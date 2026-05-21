from datetime import UTC, datetime
from decimal import Decimal

import pytest

from src.accounting import AccountingError, LedgerEventType, VirtualAccountLedger
from src.domain import OrderSide, Symbol, VirtualFill


def _now() -> datetime:
    return datetime(2026, 5, 21, 0, 0, tzinfo=UTC)


def _symbol() -> Symbol:
    return Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT")


def _ledger(initial_cash: Decimal = Decimal("1000")) -> VirtualAccountLedger:
    return VirtualAccountLedger.open(
        account_id="paper-main",
        initial_cash=initial_cash,
        opened_at=_now(),
    )


def _fill(
    *,
    side: OrderSide = OrderSide.BUY,
    quantity: Decimal = Decimal("0.01"),
    price: Decimal = Decimal("50000"),
    fee: Decimal = Decimal("0.50"),
    slippage: Decimal = Decimal("0.25"),
    fill_id: str = "fill-1",
) -> VirtualFill:
    return VirtualFill(
        fill_id=fill_id,
        order_id=f"{fill_id}-order",
        symbol=_symbol(),
        side=side,
        quantity=quantity,
        price=price,
        fee=fee,
        slippage=slippage,
        filled_at=_now(),
    )


def _marks(price: Decimal = Decimal("50000")) -> dict[Symbol, Decimal]:
    return {_symbol(): price}


def test_opens_account_with_default_virtual_cash() -> None:
    ledger = _ledger()

    assert ledger.state.account_id == "paper-main"
    assert ledger.state.cash == Decimal("1000")
    assert ledger.state.positions == ()
    assert ledger.state.equity == Decimal("1000")
    assert ledger.events[0].event_type is LedgerEventType.ACCOUNT_OPENED


def test_buy_fill_updates_cash_position_and_ledger_events() -> None:
    ledger = _ledger()

    state = ledger.apply_fill(_fill(), mark_prices=_marks())

    assert state.cash == Decimal("499.50")
    assert len(state.positions) == 1
    position = state.positions[0]
    assert position.quantity == Decimal("0.01")
    assert position.cost_basis == Decimal("500.50")
    assert position.average_entry_price == Decimal("50050")
    assert state.unrealized_pnl == Decimal("-0.50")
    assert state.equity == Decimal("999.50")
    assert [event.event_type for event in ledger.events] == [
        LedgerEventType.ACCOUNT_OPENED,
        LedgerEventType.CASH_CHANGED,
        LedgerEventType.POSITION_CHANGED,
    ]
    assert ledger.events[1].cash_delta == Decimal("-500.50")
    assert ledger.events[2].position_quantity_delta == Decimal("0.01")
    assert ledger.events[1].fee == Decimal("0.50")
    assert ledger.events[1].slippage == Decimal("0.25")


def test_second_buy_updates_average_cost() -> None:
    ledger = _ledger()
    ledger.apply_fill(_fill(fill_id="fill-1"), mark_prices=_marks())

    state = ledger.apply_fill(
        _fill(price=Decimal("40000"), fee=Decimal("0.40"), fill_id="fill-2"),
        mark_prices=_marks(Decimal("45000")),
    )

    position = state.positions[0]
    assert position.quantity == Decimal("0.02")
    assert position.cost_basis == Decimal("900.90")
    assert position.average_entry_price == Decimal("45045")


def test_partial_sell_reduces_position_and_realizes_proportional_pnl() -> None:
    ledger = _ledger()
    ledger.apply_fill(_fill(fill_id="buy-1"), mark_prices=_marks())

    state = ledger.apply_fill(
        _fill(
            side=OrderSide.SELL,
            quantity=Decimal("0.005"),
            price=Decimal("60000"),
            fee=Decimal("0.30"),
            fill_id="sell-1",
        ),
        mark_prices=_marks(Decimal("60000")),
    )

    assert state.cash == Decimal("799.20")
    assert state.positions[0].quantity == Decimal("0.005")
    assert state.positions[0].cost_basis == Decimal("250.250")
    assert state.realized_pnl == Decimal("49.450")
    assert state.unrealized_pnl == Decimal("49.750")


def test_full_sell_closes_position_without_negative_quantity() -> None:
    ledger = _ledger()
    ledger.apply_fill(_fill(fill_id="buy-1"), mark_prices=_marks())

    state = ledger.apply_fill(
        _fill(
            side=OrderSide.SELL,
            quantity=Decimal("0.01"),
            price=Decimal("60000"),
            fee=Decimal("0.60"),
            fill_id="sell-1",
        ),
        mark_prices={},
    )

    assert state.positions == ()
    assert state.cash == Decimal("1098.90")
    assert state.realized_pnl == Decimal("98.90")
    assert state.unrealized_pnl == Decimal("0")


def test_sell_cannot_create_negative_position() -> None:
    ledger = _ledger()

    with pytest.raises(AccountingError, match="position negative"):
        ledger.apply_fill(
            _fill(side=OrderSide.SELL, quantity=Decimal("0.01")),
            mark_prices=_marks(),
        )


def test_buy_cannot_create_negative_cash() -> None:
    ledger = _ledger(initial_cash=Decimal("100"))

    with pytest.raises(AccountingError, match="cash negative"):
        ledger.apply_fill(_fill(), mark_prices=_marks())


def test_rejected_order_event_does_not_change_balances() -> None:
    ledger = _ledger()
    before = ledger.state

    after = ledger.record_rejected_order(
        order_id="order-1",
        symbol=_symbol(),
        occurred_at=_now(),
        reason_codes=("BROKER_REJECTED_INSUFFICIENT_CASH",),
    )

    assert after == before
    assert ledger.events[-1].event_type is LedgerEventType.REJECTED_ORDER_RECORDED
    assert ledger.events[-1].cash_delta == Decimal("0")
    assert ledger.events[-1].position_quantity_delta == Decimal("0")


def test_snapshot_marks_unrealized_pnl_equity_peak_and_drawdown() -> None:
    ledger = _ledger()
    ledger.apply_fill(_fill(fill_id="buy-1"), mark_prices=_marks())

    high_snapshot = ledger.snapshot(
        mark_prices=_marks(Decimal("60000")),
        captured_at=_now(),
    )
    high_state = ledger.state
    low_snapshot = ledger.snapshot(
        mark_prices=_marks(Decimal("40000")),
        captured_at=_now(),
    )
    low_state = ledger.state

    assert high_snapshot.equity == Decimal("1099.50")
    assert high_state.peak_equity == Decimal("1099.50")
    assert high_state.drawdown == Decimal("0")
    assert low_snapshot.equity == Decimal("899.50")
    assert low_state.drawdown == Decimal("200.00") / Decimal("1099.50")


def test_events_are_append_only_and_exposed_as_immutable_tuple() -> None:
    ledger = _ledger()
    events_before = ledger.events
    ledger.record_rejected_order(
        order_id="order-1",
        symbol=_symbol(),
        occurred_at=_now(),
        reason_codes=("REJECTED",),
    )

    assert isinstance(events_before, tuple)
    assert len(events_before) == 1
    assert len(ledger.events) == 2


def test_missing_mark_price_for_held_symbol_is_rejected() -> None:
    ledger = _ledger()
    state_before = ledger.state
    events_before = ledger.events

    with pytest.raises(AccountingError, match="missing mark price"):
        ledger.apply_fill(_fill(), mark_prices={})

    assert ledger.state == state_before
    assert ledger.events == events_before


def test_naive_timestamps_are_rejected() -> None:
    with pytest.raises(AccountingError, match="timezone-aware UTC"):
        VirtualAccountLedger.open(
            account_id="paper-main",
            initial_cash=Decimal("1000"),
            opened_at=datetime(2026, 5, 21, 0, 0),
        )


def test_non_decimal_initial_cash_is_rejected() -> None:
    with pytest.raises(AccountingError, match="Decimal"):
        VirtualAccountLedger.open(
            account_id="paper-main",
            initial_cash=1000,  # type: ignore[arg-type]
            opened_at=_now(),
        )

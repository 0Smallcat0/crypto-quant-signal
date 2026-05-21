from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.domain import (
    DomainValidationError,
    OrderIntent,
    OrderSide,
    Position,
    RiskDecision,
    RiskDecisionStatus,
    Signal,
    Symbol,
    TargetPosition,
    VirtualFill,
    VirtualOrder,
)


def _symbol() -> Symbol:
    return Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT")


def _now() -> datetime:
    return datetime(2026, 5, 20, 0, 0, tzinfo=UTC)


def test_signal_only_supports_long_and_flat() -> None:
    assert {signal.value for signal in Signal} == {"LONG", "FLAT"}


def test_short_signal_cannot_be_represented() -> None:
    with pytest.raises(ValueError):
        Signal("SHORT")


def test_risk_decision_supports_paused_and_stopped_statuses() -> None:
    intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.25"),
        created_at=_now(),
    )

    paused = RiskDecision(
        intent=intent,
        status=RiskDecisionStatus.PAUSED,
        reason_codes=("STALE_DATA",),
        decided_at=_now(),
    )
    stopped = RiskDecision(
        intent=intent,
        status=RiskDecisionStatus.STOPPED,
        reason_codes=("ACCOUNT_STOP",),
        decided_at=_now(),
    )

    assert paused.status is RiskDecisionStatus.PAUSED
    assert stopped.status is RiskDecisionStatus.STOPPED


@pytest.mark.parametrize(
    "status",
    [RiskDecisionStatus.REJECTED, RiskDecisionStatus.PAUSED, RiskDecisionStatus.STOPPED],
)
def test_non_approved_risk_decision_requires_reason_code(status: RiskDecisionStatus) -> None:
    with pytest.raises(DomainValidationError, match="non-approved risk decision"):
        RiskDecision(
            intent=OrderIntent(
                symbol=_symbol(),
                side=OrderSide.BUY,
                quantity=Decimal("0.25"),
                created_at=_now(),
            ),
            status=status,
            reason_codes=(),
            decided_at=_now(),
        )


def test_position_quantity_cannot_be_negative() -> None:
    with pytest.raises(DomainValidationError, match="quantity"):
        Position(
            symbol=_symbol(),
            quantity=Decimal("-0.1"),
            average_entry_price=Decimal("50000"),
        )


def test_target_position_quantity_cannot_be_negative() -> None:
    with pytest.raises(DomainValidationError, match="quantity"):
        TargetPosition(symbol=_symbol(), quantity=Decimal("-0.1"))


def test_sell_below_or_equal_current_holding_is_valid() -> None:
    position = Position(
        symbol=_symbol(),
        quantity=Decimal("1.5"),
        average_entry_price=Decimal("50000"),
    )

    OrderIntent(
        symbol=_symbol(),
        side=OrderSide.SELL,
        quantity=Decimal("0.5"),
        created_at=_now(),
    ).validate_against_position(position)
    OrderIntent(
        symbol=_symbol(),
        side=OrderSide.SELL,
        quantity=Decimal("1.5"),
        created_at=_now(),
    ).validate_against_position(position)


def test_sell_greater_than_current_holding_is_rejected() -> None:
    position = Position(
        symbol=_symbol(),
        quantity=Decimal("1.5"),
        average_entry_price=Decimal("50000"),
    )
    intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.SELL,
        quantity=Decimal("1.6"),
        created_at=_now(),
    )

    with pytest.raises(DomainValidationError, match="sell quantity"):
        intent.validate_against_position(position)


def test_decimal_fields_remain_decimal_values() -> None:
    fill = VirtualFill(
        fill_id="fill-1",
        order_id="order-1",
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.25"),
        price=Decimal("50000.5"),
        fee=Decimal("1.25"),
        slippage=Decimal("0.50"),
        filled_at=_now(),
    )

    assert isinstance(fill.quantity, Decimal)
    assert isinstance(fill.price, Decimal)
    assert isinstance(fill.fee, Decimal)
    assert isinstance(fill.slippage, Decimal)


def test_virtual_order_requires_approved_matching_risk_decision() -> None:
    intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.25"),
        created_at=_now(),
    )
    approved_decision = RiskDecision(
        intent=intent,
        status=RiskDecisionStatus.APPROVED,
        reason_codes=("RISK_APPROVED",),
        decided_at=_now(),
    )

    VirtualOrder(
        order_id="order-1",
        intent=intent,
        risk_decision=approved_decision,
        approved_at=_now(),
    )


def test_virtual_order_rejects_non_approved_risk_decision() -> None:
    intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.25"),
        created_at=_now(),
    )
    rejected_decision = RiskDecision(
        intent=intent,
        status=RiskDecisionStatus.REJECTED,
        reason_codes=("MIN_NOTIONAL_NOT_MET",),
        decided_at=_now(),
    )

    with pytest.raises(DomainValidationError, match="approved risk decision"):
        VirtualOrder(
            order_id="order-1",
            intent=intent,
            risk_decision=rejected_decision,
            approved_at=_now(),
        )


def test_virtual_order_rejects_mismatched_risk_decision_intent() -> None:
    intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.25"),
        created_at=_now(),
    )
    other_intent = OrderIntent(
        symbol=_symbol(),
        side=OrderSide.BUY,
        quantity=Decimal("0.30"),
        created_at=_now(),
    )
    approved_decision = RiskDecision(
        intent=other_intent,
        status=RiskDecisionStatus.APPROVED,
        reason_codes=("RISK_APPROVED",),
        decided_at=_now(),
    )

    with pytest.raises(DomainValidationError, match="risk decision intent"):
        VirtualOrder(
            order_id="order-1",
            intent=intent,
            risk_decision=approved_decision,
            approved_at=_now(),
        )


def test_float_quantity_is_rejected() -> None:
    with pytest.raises(DomainValidationError, match="Decimal"):
        OrderIntent(
            symbol=_symbol(),
            side=OrderSide.BUY,
            quantity=0.25,  # type: ignore[arg-type]
            created_at=_now(),
        )


def test_order_side_must_be_enum_member() -> None:
    with pytest.raises(DomainValidationError, match="OrderSide"):
        OrderIntent(
            symbol=_symbol(),
            side="SELL",  # type: ignore[arg-type]
            quantity=Decimal("0.25"),
            created_at=_now(),
        )


def test_event_timestamps_must_be_timezone_aware_utc() -> None:
    with pytest.raises(DomainValidationError, match="timezone-aware UTC"):
        OrderIntent(
            symbol=_symbol(),
            side=OrderSide.BUY,
            quantity=Decimal("0.25"),
            created_at=datetime(2026, 5, 20, 0, 0),
        )

    with pytest.raises(DomainValidationError, match="timezone-aware UTC"):
        OrderIntent(
            symbol=_symbol(),
            side=OrderSide.BUY,
            quantity=Decimal("0.25"),
            created_at=datetime(2026, 5, 20, 8, 0, tzinfo=timezone(timedelta(hours=8))),
        )

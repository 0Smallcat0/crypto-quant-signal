"""Append-only virtual account ledger for Core MVP accounting."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal

from src.accounting.types import (
    AccountingError,
    AccountingPosition,
    AccountState,
    LedgerEvent,
    LedgerEventType,
)
from src.domain import OrderSide, Position, Symbol, VirtualAccountSnapshot, VirtualFill


class VirtualAccountLedger:
    """In-memory append-only virtual account ledger."""

    def __init__(
        self,
        *,
        account_id: str,
        cash: Decimal,
        positions: tuple[AccountingPosition, ...],
        realized_pnl: Decimal,
        unrealized_pnl: Decimal,
        equity: Decimal,
        peak_equity: Decimal,
        drawdown: Decimal,
        updated_at: datetime,
        events: tuple[LedgerEvent, ...],
    ) -> None:
        self._state = AccountState(
            account_id=account_id,
            cash=cash,
            positions=positions,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            equity=equity,
            peak_equity=peak_equity,
            drawdown=drawdown,
            updated_at=updated_at,
        )
        self._events = list(events)

    @classmethod
    def open(
        cls,
        *,
        account_id: str,
        initial_cash: Decimal,
        opened_at: datetime,
    ) -> VirtualAccountLedger:
        """Open a virtual account with initial cash and an audit event."""

        _require_non_negative_decimal("initial_cash", initial_cash)
        event = LedgerEvent(
            event_id="ledger-000001",
            event_type=LedgerEventType.ACCOUNT_OPENED,
            account_id=account_id,
            occurred_at=opened_at,
            reason_codes=("ACCOUNT_OPENED",),
            cash_delta=initial_cash,
        )
        return cls(
            account_id=account_id,
            cash=initial_cash,
            positions=(),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            equity=initial_cash,
            peak_equity=initial_cash,
            drawdown=Decimal("0"),
            updated_at=opened_at,
            events=(event,),
        )

    @property
    def state(self) -> AccountState:
        """Current immutable account state."""

        return self._state

    @property
    def events(self) -> tuple[LedgerEvent, ...]:
        """Immutable view of append-only ledger events."""

        return tuple(self._events)

    def apply_fill(
        self,
        fill: VirtualFill,
        *,
        mark_prices: Mapping[Symbol, Decimal],
    ) -> AccountState:
        """Apply a virtual fill and append explainable cash and position events."""

        if not isinstance(fill, VirtualFill):
            msg = "fill must be VirtualFill"
            raise AccountingError(msg)

        positions_by_symbol = {
            position.symbol.value: position for position in self._state.positions
        }
        position = positions_by_symbol.get(fill.symbol.value)
        gross_notional = fill.quantity * fill.price

        if fill.side is OrderSide.BUY:
            cash_delta = -(gross_notional + fill.fee)
            new_cash = self._state.cash + cash_delta
            if new_cash < Decimal("0"):
                msg = "fill would make cash negative"
                raise AccountingError(msg)
            new_position: AccountingPosition | None = _position_after_buy(
                position,
                fill,
                gross_notional + fill.fee,
            )
            realized_delta = Decimal("0")
            position_delta = fill.quantity
        else:
            if position is None or fill.quantity > position.quantity:
                msg = "fill would make position negative"
                raise AccountingError(msg)
            proportional_cost_basis = position.cost_basis * fill.quantity / position.quantity
            net_proceeds = gross_notional - fill.fee
            realized_delta = net_proceeds - proportional_cost_basis
            cash_delta = net_proceeds
            new_cash = self._state.cash + cash_delta
            new_position = _position_after_sell(position, fill, proportional_cost_basis)
            position_delta = -fill.quantity

        if new_position is None:
            positions_by_symbol.pop(fill.symbol.value, None)
        else:
            positions_by_symbol[fill.symbol.value] = new_position

        updated_positions = tuple(positions_by_symbol.values())
        realized_pnl = self._state.realized_pnl + realized_delta
        next_state = _marked_state(
            account_id=self._state.account_id,
            cash=new_cash,
            positions=updated_positions,
            realized_pnl=realized_pnl,
            updated_at=fill.filled_at,
            previous_peak_equity=self._state.peak_equity,
            mark_prices=mark_prices,
        )
        self._append_fill_events(
            fill=fill,
            cash_delta=cash_delta,
            position_delta=position_delta,
            realized_pnl_delta=realized_delta,
        )
        self._state = next_state
        return self._state

    def record_rejected_order(
        self,
        *,
        order_id: str | None,
        symbol: Symbol | None,
        occurred_at: datetime,
        reason_codes: tuple[str, ...],
    ) -> AccountState:
        """Append a rejected-order audit event without mutating balances."""

        self._append_event(
            event_type=LedgerEventType.REJECTED_ORDER_RECORDED,
            occurred_at=occurred_at,
            reason_codes=reason_codes,
            order_id=order_id,
            symbol=symbol,
        )
        return self._state

    def snapshot(
        self,
        *,
        mark_prices: Mapping[Symbol, Decimal],
        captured_at: datetime,
    ) -> VirtualAccountSnapshot:
        """Mark positions and return a domain account snapshot."""

        self._state = _marked_state(
            account_id=self._state.account_id,
            cash=self._state.cash,
            positions=self._state.positions,
            realized_pnl=self._state.realized_pnl,
            updated_at=captured_at,
            previous_peak_equity=self._state.peak_equity,
            mark_prices=mark_prices,
        )
        self._append_event(
            event_type=LedgerEventType.SNAPSHOT_MARKED,
            occurred_at=captured_at,
            reason_codes=("SNAPSHOT_MARKED",),
        )
        return VirtualAccountSnapshot(
            account_id=self._state.account_id,
            cash=self._state.cash,
            equity=self._state.equity,
            positions=tuple(
                Position(
                    symbol=position.symbol,
                    quantity=position.quantity,
                    average_entry_price=position.average_entry_price,
                )
                for position in self._state.positions
            ),
            captured_at=captured_at,
        )

    def _append_fill_events(
        self,
        *,
        fill: VirtualFill,
        cash_delta: Decimal,
        position_delta: Decimal,
        realized_pnl_delta: Decimal,
    ) -> None:
        self._append_event(
            event_type=LedgerEventType.CASH_CHANGED,
            occurred_at=fill.filled_at,
            reason_codes=("FILL_CASH_CHANGED",),
            order_id=fill.order_id,
            fill_id=fill.fill_id,
            symbol=fill.symbol,
            cash_delta=cash_delta,
            realized_pnl_delta=realized_pnl_delta,
            fee=fill.fee,
            slippage=fill.slippage,
        )
        self._append_event(
            event_type=LedgerEventType.POSITION_CHANGED,
            occurred_at=fill.filled_at,
            reason_codes=("FILL_POSITION_CHANGED",),
            order_id=fill.order_id,
            fill_id=fill.fill_id,
            symbol=fill.symbol,
            position_quantity_delta=position_delta,
            fee=fill.fee,
            slippage=fill.slippage,
        )

    def _append_event(
        self,
        *,
        event_type: LedgerEventType,
        occurred_at: datetime,
        reason_codes: tuple[str, ...],
        order_id: str | None = None,
        fill_id: str | None = None,
        symbol: Symbol | None = None,
        cash_delta: Decimal = Decimal("0"),
        position_quantity_delta: Decimal = Decimal("0"),
        realized_pnl_delta: Decimal = Decimal("0"),
        fee: Decimal = Decimal("0"),
        slippage: Decimal = Decimal("0"),
    ) -> None:
        event = LedgerEvent(
            event_id=f"ledger-{len(self._events) + 1:06d}",
            event_type=event_type,
            account_id=self._state.account_id,
            occurred_at=occurred_at,
            reason_codes=reason_codes,
            order_id=order_id,
            fill_id=fill_id,
            symbol=symbol,
            cash_delta=cash_delta,
            position_quantity_delta=position_quantity_delta,
            realized_pnl_delta=realized_pnl_delta,
            fee=fee,
            slippage=slippage,
        )
        self._events.append(event)


def _position_after_buy(
    position: AccountingPosition | None,
    fill: VirtualFill,
    added_cost_basis: Decimal,
) -> AccountingPosition:
    if position is None:
        quantity = fill.quantity
        cost_basis = added_cost_basis
    else:
        quantity = position.quantity + fill.quantity
        cost_basis = position.cost_basis + added_cost_basis
    return AccountingPosition(
        symbol=fill.symbol,
        quantity=quantity,
        average_entry_price=cost_basis / quantity,
        cost_basis=cost_basis,
    )


def _position_after_sell(
    position: AccountingPosition,
    fill: VirtualFill,
    removed_cost_basis: Decimal,
) -> AccountingPosition | None:
    quantity = position.quantity - fill.quantity
    if quantity < Decimal("0"):
        msg = "sell fill cannot exceed position quantity"
        raise AccountingError(msg)
    if quantity == Decimal("0"):
        return None
    cost_basis = position.cost_basis - removed_cost_basis
    return AccountingPosition(
        symbol=position.symbol,
        quantity=quantity,
        average_entry_price=cost_basis / quantity,
        cost_basis=cost_basis,
    )


def _marked_state(
    *,
    account_id: str,
    cash: Decimal,
    positions: tuple[AccountingPosition, ...],
    realized_pnl: Decimal,
    updated_at: datetime,
    previous_peak_equity: Decimal,
    mark_prices: Mapping[Symbol, Decimal],
) -> AccountState:
    unrealized_pnl = Decimal("0")
    position_value = Decimal("0")
    for position in positions:
        mark_price = _mark_price_for(mark_prices, position.symbol)
        position_mark_value = position.quantity * mark_price
        position_value += position_mark_value
        unrealized_pnl += position_mark_value - position.cost_basis
    equity = cash + position_value
    if equity < Decimal("0"):
        msg = "account equity must not be negative"
        raise AccountingError(msg)
    peak_equity = max(previous_peak_equity, equity)
    drawdown = Decimal("0")
    if peak_equity > Decimal("0") and equity < peak_equity:
        drawdown = (peak_equity - equity) / peak_equity
    return AccountState(
        account_id=account_id,
        cash=cash,
        positions=positions,
        realized_pnl=realized_pnl,
        unrealized_pnl=unrealized_pnl,
        equity=equity,
        peak_equity=peak_equity,
        drawdown=drawdown,
        updated_at=updated_at,
    )


def _mark_price_for(mark_prices: Mapping[Symbol, Decimal], symbol: Symbol) -> Decimal:
    for mark_symbol, mark_price in mark_prices.items():
        if mark_symbol == symbol:
            _require_positive_decimal("mark_price", mark_price)
            return mark_price
    msg = f"missing mark price for {symbol.value}"
    raise AccountingError(msg)


def _require_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise AccountingError(msg)


def _require_non_negative_decimal(name: str, value: Decimal) -> None:
    _require_decimal(name, value)
    if value < Decimal("0"):
        msg = f"{name} must not be negative"
        raise AccountingError(msg)


def _require_positive_decimal(name: str, value: Decimal) -> None:
    _require_decimal(name, value)
    if value <= Decimal("0"):
        msg = f"{name} must be positive"
        raise AccountingError(msg)

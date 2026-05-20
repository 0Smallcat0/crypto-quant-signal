from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.domain import (
    DomainValidationError,
    OrderIntent,
    OrderSide,
    Position,
    Signal,
    Symbol,
    TargetPosition,
    VirtualFill,
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

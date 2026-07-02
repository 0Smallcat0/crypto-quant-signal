from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Candle, Symbol, Timeframe
from src.features import (
    DAILY_TREND_WARMUP_CANDLES,
    FeaturePipelineValidationError,
    build_daily_trend_snapshots,
    daily_trend_feature_names,
)

_BASE_OPEN_TIME = datetime(2025, 1, 1, 0, 0, tzinfo=UTC)


def _symbol(value: str = "BTCUSDT", base_asset: str = "BTC") -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _daily_candle(
    index: int,
    *,
    close: str,
    symbol: Symbol | None = None,
    timeframe_value: str = "1d",
    is_closed: bool = True,
) -> Candle:
    open_time = _BASE_OPEN_TIME + timedelta(days=index)
    close_price = Decimal(close)
    return Candle(
        symbol=symbol or _symbol(),
        timeframe=Timeframe(timeframe_value),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=close_price,
        high_price=close_price + Decimal("1"),
        low_price=max(close_price - Decimal("1"), Decimal("0.01")),
        close_price=close_price,
        volume=Decimal("10"),
        is_closed=is_closed,
    )


def _constant_history(count: int, *, close: str = "100") -> tuple[Candle, ...]:
    return tuple(_daily_candle(index, close=close) for index in range(count))


def test_no_snapshot_before_the_200_close_warmup_floor() -> None:
    snapshots = build_daily_trend_snapshots(_constant_history(DAILY_TREND_WARMUP_CANDLES - 1))

    assert snapshots == ()


def test_first_snapshot_lands_exactly_on_the_200th_close() -> None:
    history = _constant_history(DAILY_TREND_WARMUP_CANDLES)

    snapshots = build_daily_trend_snapshots(history)

    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.as_of == history[-1].close_time
    assert set(snapshot.values.keys()) == set(daily_trend_feature_names())
    for name in ("sma_20", "sma_65", "sma_150", "sma_200"):
        assert snapshot.values[name] == Decimal("100")
    assert snapshot.values["close_price"] == Decimal("100")


def test_sma_values_average_only_the_lookback_window() -> None:
    history = list(_constant_history(DAILY_TREND_WARMUP_CANDLES - 1))
    history.append(_daily_candle(DAILY_TREND_WARMUP_CANDLES - 1, close="300"))

    snapshots = build_daily_trend_snapshots(tuple(history))

    snapshot = snapshots[-1]
    assert snapshot.values["close_price"] == Decimal("300")
    assert snapshot.values["sma_20"] == (Decimal("100") * 19 + Decimal("300")) / Decimal("20")
    assert snapshot.values["sma_200"] == (Decimal("100") * 199 + Decimal("300")) / Decimal("200")


def test_future_candles_do_not_change_past_snapshots() -> None:
    history = _constant_history(DAILY_TREND_WARMUP_CANDLES)
    extended = history + (
        _daily_candle(DAILY_TREND_WARMUP_CANDLES, close="999"),
        _daily_candle(DAILY_TREND_WARMUP_CANDLES + 1, close="1"),
    )

    original_first = build_daily_trend_snapshots(history)[0]
    extended_first = build_daily_trend_snapshots(extended)[0]

    assert extended_first.as_of == original_first.as_of
    assert dict(extended_first.values) == dict(original_first.values)


def test_open_candles_are_rejected() -> None:
    history = _constant_history(DAILY_TREND_WARMUP_CANDLES - 1) + (
        _daily_candle(DAILY_TREND_WARMUP_CANDLES - 1, close="100", is_closed=False),
    )

    with pytest.raises(FeaturePipelineValidationError, match="OPEN_CANDLE"):
        build_daily_trend_snapshots(history)


def test_non_daily_timeframe_is_rejected() -> None:
    candles = tuple(_daily_candle(index, close="100", timeframe_value="15m") for index in range(3))

    with pytest.raises(FeaturePipelineValidationError, match="1d"):
        build_daily_trend_snapshots(candles)


def test_mixed_symbols_are_rejected() -> None:
    history = _constant_history(DAILY_TREND_WARMUP_CANDLES - 1) + (
        _daily_candle(
            DAILY_TREND_WARMUP_CANDLES - 1,
            close="100",
            symbol=_symbol("ETHUSDT", "ETH"),
        ),
    )

    with pytest.raises(FeaturePipelineValidationError, match="one symbol"):
        build_daily_trend_snapshots(history)


def test_duplicate_open_times_are_rejected() -> None:
    history = _constant_history(DAILY_TREND_WARMUP_CANDLES) + (
        _daily_candle(DAILY_TREND_WARMUP_CANDLES - 1, close="101"),
    )

    with pytest.raises(FeaturePipelineValidationError, match="duplicate"):
        build_daily_trend_snapshots(history)


def test_empty_candles_are_rejected() -> None:
    with pytest.raises(FeaturePipelineValidationError, match="empty"):
        build_daily_trend_snapshots(())

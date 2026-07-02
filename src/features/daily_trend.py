"""Daily SMA ensemble features for the Daily Trend Ensemble strategy."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal

from src.domain import Candle
from src.features.types import (
    FeaturePipelineValidationError,
    FeatureSnapshot,
    FeatureSourceRange,
)

DAILY_TREND_TIMEFRAME = "1d"
DAILY_TREND_LOOKBACKS: tuple[int, ...] = (20, 65, 150, 200)
DAILY_TREND_WARMUP_CANDLES = max(DAILY_TREND_LOOKBACKS)


def daily_trend_feature_names() -> tuple[str, ...]:
    """Feature names produced for every daily trend snapshot."""

    return ("close_price", *(f"sma_{lookback}" for lookback in DAILY_TREND_LOOKBACKS))


def build_daily_trend_snapshots(candles: Iterable[Candle]) -> tuple[FeatureSnapshot, ...]:
    """Build point-in-time SMA ensemble snapshots from closed daily candles.

    No snapshot is produced before the 200-close warmup floor, so downstream
    strategy code can never act on insufficient history.
    """

    history = _prepare_daily_candles(candles)
    snapshots: list[FeatureSnapshot] = []
    for end_index in range(DAILY_TREND_WARMUP_CANDLES - 1, len(history)):
        current = history[end_index]
        visible = history[: end_index + 1]
        values: dict[str, Decimal] = {"close_price": current.close_price}
        for lookback in DAILY_TREND_LOOKBACKS:
            window = visible[-lookback:]
            values[f"sma_{lookback}"] = _average_close(window)
        source_window = visible[-DAILY_TREND_WARMUP_CANDLES:]
        snapshots.append(
            FeatureSnapshot(
                symbol=current.symbol,
                timeframe=current.timeframe,
                as_of=current.close_time,
                source_ranges=(
                    FeatureSourceRange(
                        symbol=current.symbol,
                        timeframe=current.timeframe,
                        start_open_time=source_window[0].open_time,
                        end_close_time=current.close_time,
                    ),
                ),
                values=values,
            )
        )
    return tuple(snapshots)


def _prepare_daily_candles(candles: Iterable[Candle]) -> tuple[Candle, ...]:
    candle_tuple = tuple(candles)
    if not candle_tuple:
        msg = "candles must not be empty"
        raise FeaturePipelineValidationError(msg)
    open_candles = [candle for candle in candle_tuple if not candle.is_closed]
    if open_candles:
        first = open_candles[0]
        msg = (
            "OPEN_CANDLE: daily trend features only accept closed candles "
            f"({first.symbol.value} {first.timeframe.value} {first.open_time.isoformat()})"
        )
        raise FeaturePipelineValidationError(msg)

    ordered = tuple(sorted(candle_tuple, key=lambda candle: candle.open_time))
    first = ordered[0]
    if first.timeframe.value != DAILY_TREND_TIMEFRAME:
        msg = f"candles must use {DAILY_TREND_TIMEFRAME} candles"
        raise FeaturePipelineValidationError(msg)
    seen_open_times: set[object] = set()
    for candle in ordered:
        if candle.symbol != first.symbol:
            msg = "candles must contain one symbol"
            raise FeaturePipelineValidationError(msg)
        if candle.timeframe != first.timeframe:
            msg = "candles must contain one timeframe"
            raise FeaturePipelineValidationError(msg)
        if candle.open_time in seen_open_times:
            msg = "candles must not contain duplicate open times"
            raise FeaturePipelineValidationError(msg)
        seen_open_times.add(candle.open_time)
    return ordered


def _average_close(window: Sequence[Candle]) -> Decimal:
    if not window:
        msg = "cannot average an empty candle window"
        raise FeaturePipelineValidationError(msg)
    total = sum((candle.close_price for candle in window), Decimal("0"))
    return total / Decimal(len(window))

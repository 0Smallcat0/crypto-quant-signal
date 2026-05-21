"""Closed-candle feature calculations for the Core MVP."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal

from src.domain import Candle
from src.features.types import (
    FeaturePipelineConfig,
    FeaturePipelineParameterValues,
    FeaturePipelineValidationError,
    FeatureSnapshot,
    FeatureSourceRange,
)


def build_feature_snapshots(
    candles: Iterable[Candle],
    *,
    btc_candles: Iterable[Candle],
    config: FeaturePipelineParameterValues | None = None,
) -> tuple[FeatureSnapshot, ...]:
    """Build point-in-time feature snapshots from closed 15m candles."""

    feature_config = _feature_pipeline_config_from(config)
    primary_candles = _prepare_candles(candles, label="candles")
    btc_history = _prepare_candles(btc_candles, label="btc_candles")
    _require_same_stream(primary_candles, label="candles")
    _require_same_stream(btc_history, label="btc_candles")

    snapshots: list[FeatureSnapshot] = []
    warmup = _required_candle_count(feature_config)
    for end_index in range(warmup - 1, len(primary_candles)):
        current = primary_candles[end_index]
        history = primary_candles[: end_index + 1]
        btc_visible_history = tuple(
            btc_candle for btc_candle in btc_history if btc_candle.close_time <= current.close_time
        )
        if len(btc_visible_history) < warmup:
            continue

        source_window = history[-warmup:]
        btc_source_window = btc_visible_history[-warmup:]
        values = _feature_values(history, feature_config)
        btc_values = _feature_values(btc_visible_history, feature_config)
        values.update(
            {
                "btc_momentum_return": btc_values["momentum_return"],
                "btc_trend_distance": btc_values["trend_distance"],
                "btc_volatility": btc_values["volatility"],
            }
        )
        snapshots.append(
            FeatureSnapshot(
                symbol=current.symbol,
                timeframe=current.timeframe,
                as_of=current.close_time,
                source_ranges=(
                    _source_range(source_window),
                    _source_range(btc_source_window),
                ),
                values=values,
            )
        )
    return tuple(snapshots)


def _feature_values(
    history: Sequence[Candle],
    config: FeaturePipelineConfig,
) -> dict[str, Decimal]:
    current = history[-1]
    momentum_base = history[-(config.momentum_lookback_candles + 1)]
    trend_window = history[-config.trend_lookback_candles :]
    breakout_window = history[-(config.breakout_lookback_candles + 1) : -1]
    volume_window = history[-(config.volume_lookback_candles + 1) : -1]
    volatility_window = history[-(config.volatility_lookback_candles + 1) :]

    previous_high = max(candle.high_price for candle in breakout_window)
    previous_low = min(candle.low_price for candle in breakout_window)
    average_volume = _average(candle.volume for candle in volume_window)
    trend_average_close = _average(candle.close_price for candle in trend_window)

    return {
        "momentum_return": _return(current.close_price, momentum_base.close_price),
        "trend_distance": _return(current.close_price, trend_average_close),
        "recent_high_distance": _return(current.close_price, previous_high),
        "recent_low_distance": _return(current.close_price, previous_low),
        "volume_ratio": _safe_ratio(current.volume, average_volume),
        "volatility": _mean_absolute_return(volatility_window),
    }


def _prepare_candles(candles: Iterable[Candle], *, label: str) -> tuple[Candle, ...]:
    candle_tuple = tuple(candles)
    if not candle_tuple:
        msg = f"{label} must not be empty"
        raise FeaturePipelineValidationError(msg)
    open_candles = [candle for candle in candle_tuple if not candle.is_closed]
    if open_candles:
        first = open_candles[0]
        msg = (
            "OPEN_CANDLE: feature pipeline only accepts closed candles "
            f"({first.symbol.value} {first.timeframe.value} {first.open_time.isoformat()})"
        )
        raise FeaturePipelineValidationError(msg)
    return tuple(sorted(candle_tuple, key=lambda candle: candle.open_time))


def _require_same_stream(candles: Sequence[Candle], *, label: str) -> None:
    first = candles[0]
    if first.timeframe.value != "15m":
        msg = f"{label} must use 15m candles"
        raise FeaturePipelineValidationError(msg)
    seen_open_times: set[object] = set()
    for candle in candles:
        if candle.symbol != first.symbol:
            msg = f"{label} must contain one symbol"
            raise FeaturePipelineValidationError(msg)
        if candle.timeframe != first.timeframe:
            msg = f"{label} must contain one timeframe"
            raise FeaturePipelineValidationError(msg)
        if candle.open_time in seen_open_times:
            msg = f"{label} must not contain duplicate open times"
            raise FeaturePipelineValidationError(msg)
        seen_open_times.add(candle.open_time)


def _required_candle_count(config: FeaturePipelineConfig) -> int:
    return max(
        config.momentum_lookback_candles + 1,
        config.trend_lookback_candles,
        config.breakout_lookback_candles + 1,
        config.volume_lookback_candles + 1,
        config.volatility_lookback_candles + 1,
    )


def _feature_pipeline_config_from(
    config: FeaturePipelineParameterValues | None,
) -> FeaturePipelineConfig:
    if config is None:
        return FeaturePipelineConfig()
    return FeaturePipelineConfig(
        momentum_lookback_candles=config.momentum_lookback_candles,
        trend_lookback_candles=config.trend_lookback_candles,
        breakout_lookback_candles=config.breakout_lookback_candles,
        volume_lookback_candles=config.volume_lookback_candles,
        volatility_lookback_candles=config.volatility_lookback_candles,
    )


def _source_range(candles: Sequence[Candle]) -> FeatureSourceRange:
    first = candles[0]
    last = candles[-1]
    return FeatureSourceRange(
        symbol=last.symbol,
        timeframe=last.timeframe,
        start_open_time=first.open_time,
        end_close_time=last.close_time,
    )


def _average(values: Iterable[Decimal]) -> Decimal:
    value_tuple = tuple(values)
    if not value_tuple:
        msg = "cannot average an empty sequence"
        raise FeaturePipelineValidationError(msg)
    return sum(value_tuple, Decimal("0")) / Decimal(len(value_tuple))


def _return(current: Decimal, base: Decimal) -> Decimal:
    return _safe_ratio(current, base) - Decimal("1")


def _safe_ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == Decimal("0"):
        return Decimal("0")
    return numerator / denominator


def _mean_absolute_return(candles: Sequence[Candle]) -> Decimal:
    returns = [
        abs(_return(current.close_price, previous.close_price))
        for previous, current in zip(candles, candles[1:])
    ]
    return _average(returns)

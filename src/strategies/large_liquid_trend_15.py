"""Large Liquid Trend 15 signal-only strategy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Protocol

from src.domain import Signal
from src.features import FeatureSnapshot
from src.strategies.types import StrategyDecision, StrategyValidationError

_MOMENTUM_WEIGHT = Decimal("0.25")
_TREND_WEIGHT = Decimal("0.25")
_BREAKOUT_WEIGHT = Decimal("0.20")
_VOLUME_WEIGHT = Decimal("0.15")
_BTC_TREND_WEIGHT = Decimal("0.15")


class LargeLiquidTrend15ParameterValues(Protocol):
    """Readable threshold values accepted by Large Liquid Trend 15."""

    @property
    def minimum_entry_score(self) -> Decimal: ...

    @property
    def exit_score(self) -> Decimal: ...


@dataclass(frozen=True, slots=True)
class LargeLiquidTrend15Parameters:
    """Signal thresholds for the first Core MVP strategy."""

    minimum_entry_score: Decimal = Decimal("0.70")
    exit_score: Decimal = Decimal("0.40")

    def __post_init__(self) -> None:
        _require_score_fraction("minimum_entry_score", self.minimum_entry_score)
        _require_score_fraction("exit_score", self.exit_score)
        if self.exit_score > self.minimum_entry_score:
            msg = "exit_score must not exceed minimum_entry_score"
            raise StrategyValidationError(msg)


def evaluate_large_liquid_trend_15(
    snapshot: FeatureSnapshot,
    *,
    parameters: LargeLiquidTrend15ParameterValues | None = None,
) -> StrategyDecision:
    """Evaluate one feature snapshot into a LONG/FLAT strategy decision."""

    if snapshot.timeframe.value != "15m":
        msg = "Large Liquid Trend 15 requires 15m feature snapshots"
        raise StrategyValidationError(msg)

    strategy_parameters = _large_liquid_trend_15_parameters_from(parameters)
    values = {
        "momentum_return": _feature_value(snapshot, "momentum_return"),
        "trend_distance": _feature_value(snapshot, "trend_distance"),
        "recent_high_distance": _feature_value(snapshot, "recent_high_distance"),
        "volume_ratio": _feature_value(snapshot, "volume_ratio"),
        "btc_momentum_return": _feature_value(snapshot, "btc_momentum_return"),
        "btc_trend_distance": _feature_value(snapshot, "btc_trend_distance"),
    }

    score = Decimal("0")
    reason_codes: list[str] = []

    if values["momentum_return"] > Decimal("0"):
        score += _MOMENTUM_WEIGHT
        reason_codes.append("MOMENTUM_POSITIVE")
    else:
        reason_codes.append("MOMENTUM_NOT_POSITIVE")

    if values["trend_distance"] > Decimal("0"):
        score += _TREND_WEIGHT
        reason_codes.append("TREND_POSITIVE")
    else:
        reason_codes.append("TREND_NOT_POSITIVE")

    if values["recent_high_distance"] > Decimal("0"):
        score += _BREAKOUT_WEIGHT
        reason_codes.append("BREAKOUT_CONFIRMED")
    else:
        reason_codes.append("BREAKOUT_NOT_CONFIRMED")

    if values["volume_ratio"] >= Decimal("1"):
        score += _VOLUME_WEIGHT
        reason_codes.append("VOLUME_CONFIRMED")
    else:
        reason_codes.append("VOLUME_NOT_CONFIRMED")

    btc_trend_supports = values["btc_momentum_return"] > Decimal("0") and values[
        "btc_trend_distance"
    ] > Decimal("0")
    if btc_trend_supports:
        score += _BTC_TREND_WEIGHT
        reason_codes.append("BTC_TREND_SUPPORTS")
    else:
        reason_codes.append("BTC_TREND_NOT_SUPPORTIVE")

    if score >= strategy_parameters.minimum_entry_score:
        signal = Signal.LONG
        reason_codes.append("ENTRY_SCORE_MET")
    else:
        signal = Signal.FLAT
        reason_codes.append("ENTRY_SCORE_NOT_MET")
        if score <= strategy_parameters.exit_score:
            reason_codes.append("EXIT_SCORE_MET")

    return StrategyDecision(
        symbol=snapshot.symbol,
        signal=signal,
        score=score,
        reason_codes=tuple(reason_codes),
        generated_at_bar_close=snapshot.as_of,
        executable_from_next_bar=snapshot.as_of + timedelta(milliseconds=1),
    )


def _feature_value(snapshot: FeatureSnapshot, name: str) -> Decimal:
    try:
        value = snapshot.values[name]
    except KeyError as exc:
        msg = f"missing required strategy feature: {name}"
        raise StrategyValidationError(msg) from exc
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise StrategyValidationError(msg)
    return value


def _large_liquid_trend_15_parameters_from(
    parameters: LargeLiquidTrend15ParameterValues | None,
) -> LargeLiquidTrend15Parameters:
    if parameters is None:
        return LargeLiquidTrend15Parameters()
    return LargeLiquidTrend15Parameters(
        minimum_entry_score=parameters.minimum_entry_score,
        exit_score=parameters.exit_score,
    )


def _require_score_fraction(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise StrategyValidationError(msg)
    if value < Decimal("0") or value > Decimal("1"):
        msg = f"{name} must be between 0 and 1"
        raise StrategyValidationError(msg)

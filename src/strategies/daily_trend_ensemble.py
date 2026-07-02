"""Daily Trend Ensemble strategy (contract: STRATEGY_DAILY_TREND_ENSEMBLE.md)."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from src.domain import Signal
from src.features import FeatureSnapshot
from src.strategies.types import (
    ALLOWED_EXPOSURE_FRACTIONS,
    DailyTrendEnsembleDecision,
    DailyTrendSubSignals,
    StrategyValidationError,
)

DAILY_TREND_ENSEMBLE_TIMEFRAME = "1d"

# Contract-fixed lookbacks, uniform across assets. Changing them is a new
# strategy variant: it must be pre-registered in the trial registry and
# reflected in the contract before any backtest runs.
DAILY_TREND_ENSEMBLE_LOOKBACKS: tuple[int, ...] = (20, 65, 150, 200)

LADDER_UP = "LADDER_UP"
LADDER_DOWN = "LADDER_DOWN"
LADDER_HOLD = "LADDER_HOLD"

_LADDER_DENOMINATOR = Decimal(len(DAILY_TREND_ENSEMBLE_LOOKBACKS))


def evaluate_daily_trend_ensemble(
    snapshot: FeatureSnapshot,
    *,
    previous_fraction: Decimal | None = None,
) -> DailyTrendEnsembleDecision:
    """Evaluate one daily feature snapshot into an exposure-ladder decision."""

    if snapshot.timeframe.value != DAILY_TREND_ENSEMBLE_TIMEFRAME:
        msg = "Daily Trend Ensemble requires 1d feature snapshots"
        raise StrategyValidationError(msg)
    baseline_fraction = _validated_previous_fraction(previous_fraction)

    close_price = _feature_value(snapshot, "close_price")
    reason_codes: list[str] = []
    above_flags: list[bool] = []
    for lookback in DAILY_TREND_ENSEMBLE_LOOKBACKS:
        sma_value = _feature_value(snapshot, f"sma_{lookback}")
        # Equality counts as NOT above: conservative by contract.
        is_above = close_price > sma_value
        above_flags.append(is_above)
        reason_codes.append(f"ABOVE_SMA_{lookback}" if is_above else f"BELOW_SMA_{lookback}")

    sub_signals = DailyTrendSubSignals(
        above_sma_20=above_flags[0],
        above_sma_65=above_flags[1],
        above_sma_150=above_flags[2],
        above_sma_200=above_flags[3],
    )
    exposure_fraction = Decimal(sub_signals.active_count) / _LADDER_DENOMINATOR

    if exposure_fraction > baseline_fraction:
        reason_codes.append(LADDER_UP)
    elif exposure_fraction < baseline_fraction:
        reason_codes.append(LADDER_DOWN)
    else:
        reason_codes.append(LADDER_HOLD)

    return DailyTrendEnsembleDecision(
        symbol=snapshot.symbol,
        signal=Signal.LONG if exposure_fraction > Decimal("0") else Signal.FLAT,
        exposure_fraction=exposure_fraction,
        sub_signals=sub_signals,
        score=exposure_fraction,
        reason_codes=tuple(reason_codes),
        generated_at_bar_close=snapshot.as_of,
        executable_from_next_bar=snapshot.as_of + timedelta(milliseconds=1),
    )


def _validated_previous_fraction(previous_fraction: Decimal | None) -> Decimal:
    if previous_fraction is None:
        return Decimal("0")
    if (
        not isinstance(previous_fraction, Decimal)
        or previous_fraction not in ALLOWED_EXPOSURE_FRACTIONS
    ):
        msg = "previous_fraction must be one of 0, 0.25, 0.5, 0.75, 1"
        raise StrategyValidationError(msg)
    return previous_fraction


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

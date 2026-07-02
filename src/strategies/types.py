"""Strategy output contracts for the Core MVP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from src.domain import Signal, Symbol


class StrategyValidationError(ValueError):
    """Raised when strategy input or output would break the Goal F contract."""


@dataclass(frozen=True, slots=True)
class StrategyDecision:
    """Signal-only strategy decision for one symbol at one closed bar."""

    symbol: Symbol
    signal: Signal
    score: Decimal
    reason_codes: tuple[str, ...]
    generated_at_bar_close: datetime
    executable_from_next_bar: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.signal, Signal):
            msg = "signal must be a Signal"
            raise StrategyValidationError(msg)
        if not isinstance(self.score, Decimal) or not self.score.is_finite():
            msg = "score must be a finite Decimal"
            raise StrategyValidationError(msg)
        if self.score < Decimal("0") or self.score > Decimal("1"):
            msg = "score must be between 0 and 1"
            raise StrategyValidationError(msg)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise StrategyValidationError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise StrategyValidationError(msg)
        _require_utc("generated_at_bar_close", self.generated_at_bar_close)
        _require_utc("executable_from_next_bar", self.executable_from_next_bar)
        if self.executable_from_next_bar <= self.generated_at_bar_close:
            msg = "executable_from_next_bar must be after generated_at_bar_close"
            raise StrategyValidationError(msg)


ALLOWED_EXPOSURE_FRACTIONS: tuple[Decimal, ...] = (
    Decimal("0"),
    Decimal("0.25"),
    Decimal("0.5"),
    Decimal("0.75"),
    Decimal("1"),
)


@dataclass(frozen=True, slots=True)
class DailyTrendSubSignals:
    """Per-lookback trend states for the Daily Trend Ensemble."""

    above_sma_20: bool
    above_sma_65: bool
    above_sma_150: bool
    above_sma_200: bool

    def __post_init__(self) -> None:
        for name in ("above_sma_20", "above_sma_65", "above_sma_150", "above_sma_200"):
            if not isinstance(getattr(self, name), bool):
                msg = f"{name} must be bool"
                raise StrategyValidationError(msg)

    @property
    def active_count(self) -> int:
        """Number of trend lines the close sits above."""

        return sum(
            (
                self.above_sma_20,
                self.above_sma_65,
                self.above_sma_150,
                self.above_sma_200,
            )
        )


@dataclass(frozen=True, slots=True)
class DailyTrendEnsembleDecision:
    """Exposure-ladder decision for one symbol at one closed daily bar."""

    symbol: Symbol
    signal: Signal
    exposure_fraction: Decimal
    sub_signals: DailyTrendSubSignals
    score: Decimal
    reason_codes: tuple[str, ...]
    generated_at_bar_close: datetime
    executable_from_next_bar: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.signal, Signal):
            msg = "signal must be a Signal"
            raise StrategyValidationError(msg)
        if not isinstance(self.sub_signals, DailyTrendSubSignals):
            msg = "sub_signals must be DailyTrendSubSignals"
            raise StrategyValidationError(msg)
        if (
            not isinstance(self.exposure_fraction, Decimal)
            or self.exposure_fraction not in ALLOWED_EXPOSURE_FRACTIONS
        ):
            msg = "exposure_fraction must be one of 0, 0.25, 0.5, 0.75, 1"
            raise StrategyValidationError(msg)
        expected_signal = Signal.LONG if self.exposure_fraction > Decimal("0") else Signal.FLAT
        if self.signal is not expected_signal:
            msg = "signal must be LONG when exposure_fraction is positive, FLAT otherwise"
            raise StrategyValidationError(msg)
        if self.score != self.exposure_fraction:
            msg = "score must equal exposure_fraction"
            raise StrategyValidationError(msg)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise StrategyValidationError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise StrategyValidationError(msg)
        _require_utc("generated_at_bar_close", self.generated_at_bar_close)
        _require_utc("executable_from_next_bar", self.executable_from_next_bar)
        if self.executable_from_next_bar <= self.generated_at_bar_close:
            msg = "executable_from_next_bar must be after generated_at_bar_close"
            raise StrategyValidationError(msg)


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise StrategyValidationError(msg)

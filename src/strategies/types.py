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


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise StrategyValidationError(msg)

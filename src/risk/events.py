"""Non-order risk events for the Core MVP (disaster notices)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from src.domain import Symbol
from src.risk.types import RiskGateError

DISASTER_SINGLE_DAY_DROP = "DISASTER_SINGLE_DAY_DROP"
REEVALUATE_REQUIRED = "REEVALUATE_REQUIRED"

DEFAULT_DISASTER_DROP_FRACTION = Decimal("0.20")


@dataclass(frozen=True, slots=True)
class RiskEvent:
    """Auditable non-order risk event emitted by the composition layer.

    A disaster notice is risk control, not a strategy parameter: it forces a
    re-evaluation notification but never mutates strategy state by itself.
    """

    symbol: Symbol
    event_type: str
    observed_fraction: Decimal
    threshold_fraction: Decimal
    occurred_at: datetime
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, Symbol):
            msg = "symbol must be Symbol"
            raise RiskGateError(msg)
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            msg = "event_type must not be empty"
            raise RiskGateError(msg)
        for name in ("observed_fraction", "threshold_fraction"):
            value = getattr(self, name)
            if not isinstance(value, Decimal) or not value.is_finite():
                msg = f"{name} must be a finite Decimal"
                raise RiskGateError(msg)
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() != UTC.utcoffset(
            self.occurred_at
        ):
            msg = "occurred_at must be timezone-aware UTC"
            raise RiskGateError(msg)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise RiskGateError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise RiskGateError(msg)


def detect_single_day_disaster(
    *,
    symbol: Symbol,
    previous_close: Decimal,
    current_close: Decimal,
    occurred_at: datetime,
    threshold_fraction: Decimal = DEFAULT_DISASTER_DROP_FRACTION,
) -> RiskEvent | None:
    """Return a disaster event when a single close-to-close drop breaches the threshold."""

    _require_positive_decimal("previous_close", previous_close)
    _require_positive_decimal("current_close", current_close)
    _require_positive_decimal("threshold_fraction", threshold_fraction)
    if threshold_fraction > Decimal("1"):
        msg = "threshold_fraction must be at most 1"
        raise RiskGateError(msg)

    drop_fraction = (previous_close - current_close) / previous_close
    if drop_fraction < threshold_fraction:
        return None
    return RiskEvent(
        symbol=symbol,
        event_type=DISASTER_SINGLE_DAY_DROP,
        observed_fraction=drop_fraction,
        threshold_fraction=threshold_fraction,
        occurred_at=occurred_at,
        reason_codes=(DISASTER_SINGLE_DAY_DROP, REEVALUATE_REQUIRED),
    )


def _require_positive_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        msg = f"{name} must be a finite Decimal"
        raise RiskGateError(msg)
    if value <= Decimal("0"):
        msg = f"{name} must be positive"
        raise RiskGateError(msg)

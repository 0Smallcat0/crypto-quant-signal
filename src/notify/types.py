"""Advisory notification events: persisted first, delivered second, never orders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Protocol, runtime_checkable

INCREASE_EXPOSURE = "INCREASE_EXPOSURE"
DECREASE_EXPOSURE = "DECREASE_EXPOSURE"

_ALLOWED_FRACTIONS = (
    Decimal("0"),
    Decimal("0.25"),
    Decimal("0.5"),
    Decimal("0.75"),
    Decimal("1"),
)


class NotificationValidationError(ValueError):
    """Raised when a notification event would be malformed or misleading."""


def ladder_notification_id(
    *,
    namespace: str,
    symbol_value: str,
    decision_time: datetime,
    previous_fraction: Decimal,
    target_fraction: Decimal,
) -> str:
    """Deterministic idempotency key: a restart can never re-send this event.

    Fractions are canonicalized so numerically equal Decimals (0.50 vs 0.5)
    can never mint two different keys for one transition.
    """

    previous = format(previous_fraction.normalize(), "f")
    target = format(target_fraction.normalize(), "f")
    return (
        f"notify:{namespace}:{symbol_value}:{decision_time.date().isoformat()}:{previous}->{target}"
    )


@dataclass(frozen=True, slots=True)
class NotificationEvent:
    """One advisory ladder-change message for the human executor.

    This is information, never an execution instruction to any exchange.
    """

    notification_id: str
    symbol_value: str
    action: str
    previous_fraction: Decimal
    target_fraction: Decimal
    delta_fraction: Decimal
    decision_price: Decimal
    decision_time: datetime
    reason_codes: tuple[str, ...]
    risk_status: str
    created_at: datetime

    def __post_init__(self) -> None:
        for name in ("notification_id", "symbol_value", "risk_status"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                msg = f"{name} must not be empty"
                raise NotificationValidationError(msg)
        if self.action not in (INCREASE_EXPOSURE, DECREASE_EXPOSURE):
            msg = "action must be INCREASE_EXPOSURE or DECREASE_EXPOSURE"
            raise NotificationValidationError(msg)
        for name in ("previous_fraction", "target_fraction"):
            value = getattr(self, name)
            if not isinstance(value, Decimal) or value not in _ALLOWED_FRACTIONS:
                msg = f"{name} must be one of 0, 0.25, 0.5, 0.75, 1"
                raise NotificationValidationError(msg)
        if self.previous_fraction == self.target_fraction:
            msg = "a notification requires a ladder change"
            raise NotificationValidationError(msg)
        expected_action = (
            INCREASE_EXPOSURE
            if self.target_fraction > self.previous_fraction
            else DECREASE_EXPOSURE
        )
        if self.action != expected_action:
            msg = "action must match the ladder direction"
            raise NotificationValidationError(msg)
        if self.delta_fraction != abs(self.target_fraction - self.previous_fraction):
            msg = "delta_fraction must equal the absolute ladder change"
            raise NotificationValidationError(msg)
        if not isinstance(self.decision_price, Decimal) or self.decision_price <= Decimal("0"):
            msg = "decision_price must be a positive Decimal"
            raise NotificationValidationError(msg)
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            msg = "reason_codes must be a non-empty tuple"
            raise NotificationValidationError(msg)
        if any(
            not isinstance(reason_code, str) or not reason_code for reason_code in self.reason_codes
        ):
            msg = "reason_codes must contain non-empty strings"
            raise NotificationValidationError(msg)
        _require_utc("decision_time", self.decision_time)
        _require_utc("created_at", self.created_at)

    def to_json_dict(self) -> dict[str, object]:
        return {
            "notification_id": self.notification_id,
            "symbol": self.symbol_value,
            "action": self.action,
            "previous_fraction": str(self.previous_fraction),
            "target_fraction": str(self.target_fraction),
            "delta_fraction": str(self.delta_fraction),
            "decision_price": str(self.decision_price),
            "decision_time": self.decision_time.isoformat(),
            "reason_codes": list(self.reason_codes),
            "risk_status": self.risk_status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class PortfolioTargetState:
    """Whole-portfolio target snapshot attached to deliveries (advisory only).

    ``weights`` are account-level target fractions (ladder fraction × risk
    budget) for every budgeted symbol, in a fixed symbol order. Riding along
    with each ladder-change message makes one push self-sufficient: a follower
    who missed earlier commands rebuilds the full position from any single
    message instead of replaying history. ``drawdown`` is the scoreboard
    drawdown fraction, used to anchor expectations during deep drawdowns.
    """

    weights: tuple[tuple[str, Decimal], ...]
    drawdown: Decimal

    def __post_init__(self) -> None:
        for symbol_value, weight in self.weights:
            if not isinstance(symbol_value, str) or not symbol_value.strip():
                msg = "portfolio weight symbols must not be empty"
                raise NotificationValidationError(msg)
            if not isinstance(weight, Decimal) or not Decimal("0") <= weight <= Decimal("1"):
                msg = "portfolio weights must be Decimals within [0, 1]"
                raise NotificationValidationError(msg)
        if not isinstance(self.drawdown, Decimal) or not (
            Decimal("0") <= self.drawdown < Decimal("1")
        ):
            msg = "drawdown must be a Decimal within [0, 1)"
            raise NotificationValidationError(msg)


@runtime_checkable
class NotificationChannel(Protocol):
    """Delivery transport for already-persisted notification events."""

    def deliver(
        self, event: NotificationEvent, *, portfolio: PortfolioTargetState | None = None
    ) -> None:
        """Deliver one ladder-change event; raising is safe (event is persisted)."""
        ...

    def send_text(self, text: str) -> None:
        """Deliver a plain out-of-band message (alerts, digests)."""
        ...


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise NotificationValidationError(msg)

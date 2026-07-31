"""Signal runtime value objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

from src.domain import VirtualFill
from src.notify import NotificationEvent


class RuntimeEngineError(ValueError):
    """Raised when the signal runtime receives unusable inputs or state."""


@dataclass(frozen=True, slots=True)
class DonchianRuntimeConfig:
    """Donchian ensemble parameters as the runtime consumes them.

    Defaults are trial 118 as registered. The runtime replays the ensemble
    from the warmup floor on every cycle rather than persisting window state,
    so these values fully determine the decision given the candle history.
    """

    windows: tuple[int, int, int, int] = (10, 20, 55, 110)
    exit_mode: str = "atr_channel"
    atr_window: int = 14
    atr_multiple: Decimal = Decimal("2")

    def __post_init__(self) -> None:
        if len(self.windows) != 4 or any(window <= 0 for window in self.windows):
            msg = "donchian windows must be four positive ints"
            raise RuntimeEngineError(msg)
        if list(self.windows) != sorted(set(self.windows)):
            msg = "donchian windows must be strictly increasing and distinct"
            raise RuntimeEngineError(msg)
        if self.atr_window <= 0:
            msg = "atr_window must be positive"
            raise RuntimeEngineError(msg)
        if self.atr_multiple <= Decimal("0"):
            msg = "atr_multiple must be positive"
            raise RuntimeEngineError(msg)


@dataclass(frozen=True, slots=True)
class RuntimeParameters:
    """Caller-adapted parameters for the daily signal runtime."""

    risk_budgets: Mapping[str, Decimal]
    initial_cash: Decimal
    account_id: str
    fee_bps: Decimal
    slippage_bps: Decimal
    quantity_step: Decimal
    price_tick: Decimal
    min_notional_usdt: Decimal
    max_drawdown_fraction: Decimal
    daily_loss_pause_fraction: Decimal
    disaster_single_day_drop_fraction: Decimal
    stale_data_max_age_seconds: int
    idempotency_namespace: str
    # Strategy selection. Defaults keep every existing caller on the incumbent
    # daily trend ensemble; only a caller that explicitly asks for the Donchian
    # ensemble changes behaviour.
    strategy_name: str = "daily_trend_ensemble"
    donchian: DonchianRuntimeConfig = field(default_factory=lambda: DonchianRuntimeConfig())

    def __post_init__(self) -> None:
        if not isinstance(self.risk_budgets, Mapping) or not self.risk_budgets:
            msg = "risk_budgets must be a non-empty mapping"
            raise RuntimeEngineError(msg)
        if self.initial_cash <= Decimal("0"):
            msg = "initial_cash must be positive"
            raise RuntimeEngineError(msg)
        if not self.account_id.strip():
            msg = "account_id must not be empty"
            raise RuntimeEngineError(msg)
        if not self.idempotency_namespace.strip():
            msg = "idempotency_namespace must not be empty"
            raise RuntimeEngineError(msg)
        if self.stale_data_max_age_seconds <= 0:
            msg = "stale_data_max_age_seconds must be positive"
            raise RuntimeEngineError(msg)
        object.__setattr__(self, "risk_budgets", MappingProxyType(dict(self.risk_budgets)))


@dataclass(frozen=True, slots=True)
class CycleResult:
    """Outcome of one runtime decision cycle."""

    processed: bool
    reason: str
    close_time: datetime | None
    notifications: tuple[NotificationEvent, ...]
    fills: tuple[VirtualFill, ...]
    rejection_reason_codes: tuple[tuple[str, tuple[str, ...]], ...]
    health_codes: tuple[str, ...]
    equity: Decimal | None

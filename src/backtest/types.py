"""Backtest value objects for the Core MVP daily replay engine."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from types import MappingProxyType

from src.domain import VirtualFill
from src.execution import BrokerAcceptedOrder, BrokerRejectedOrder
from src.risk import RiskEvent


class BacktestError(ValueError):
    """Raised when backtest inputs or invariants are violated."""


@dataclass(frozen=True, slots=True)
class BacktestParameters:
    """Caller-adapted parameters for one daily backtest run."""

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
    cost_multiplier: Decimal = Decimal("1")
    # Goal P variant selection (backtest-only; the live runtime hardcodes the
    # original ensemble and has no path to these fields).
    strategy_name: str = "daily_trend_ensemble"
    confirm_days: int = 1
    # Experiment-2 volatility-target overlay (None = off). Scales the ladder
    # fraction by min(1, target / realized_vol); a position-size modifier,
    # never a signal change.
    vol_target_annualized: Decimal | None = None
    vol_window_days: int = 20
    vol_rebalance: str = "daily"
    # Experiment-3 cross-sectional momentum family (frozen in
    # docs/research/GOALP_EXPERIMENT3_PREREGISTRATION.md). Consulted only
    # when strategy_name == "cross_sectional_momentum"; the ladder
    # strategies and the live daily runtime never read these.
    cs_top_k: int = 2
    cs_lookback_days: int = 90
    cs_rebalance_cadence: str = "weekly"
    cs_absolute_filter: bool = False
    cs_min_pool_size: int = 4
    # First allowed decision date (ISO). The pre-registration pins every
    # family member's return series to the registry window so the strict
    # alignment gate in the report can include them; without a floor the
    # lookback arms would start on different days.
    cs_decision_start: str | None = None
    # Experiment-5 directional regime gate (None = off). Multiplies cs
    # weights by 0/1 from an SMA state machine; consulted only when
    # strategy_name == "cross_sectional_momentum".
    cs_gate_sma_window: int | None = None
    cs_gate_basis: str = "btc"
    cs_gate_hysteresis: Decimal = Decimal("0")
    cs_gate_cadence: str = "daily"
    # Experiment-6 multi-horizon trend factor (empty = single-lookback
    # behavior). Selection score = equal-weight mean of trailing returns
    # over these horizons; pool eligibility keys on the longest one.
    cs_horizon_days: tuple[int, ...] = ()
    # Experiment-7 Donchian breakout ensemble (ladder path). Exactly four
    # channel windows map onto the 5-rung ladder (0, 1/4, 1/2, 3/4, 1).
    dc_windows: tuple[int, ...] = ()
    dc_exit: str = "half_low"
    # Experiment-8 engineering prerequisite: opt-in for the ladder path to
    # admit staggered listings. False (default) keeps the strict intersection-
    # aligned decision-day contract every prior family used. True switches to
    # union-of-dates + per-symbol eligibility on the ladder path (each symbol
    # participates only on days it has both a candle and a post-warmup
    # snapshot). Cross-sectional strategy is unaffected — it already uses the
    # union model natively.
    allow_staggered_listings: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.risk_budgets, Mapping) or not self.risk_budgets:
            msg = "risk_budgets must be a non-empty mapping"
            raise BacktestError(msg)
        if self.strategy_name not in (
            "daily_trend_ensemble",
            "confirmed_trend_ensemble",
            "cross_sectional_momentum",
            "donchian_breakout_ensemble",
        ):
            msg = f"unknown backtest strategy_name: {self.strategy_name}"
            raise BacktestError(msg)
        if self.strategy_name == "donchian_breakout_ensemble":
            if len(self.dc_windows) != 4:
                msg = "dc_windows must contain exactly four channel windows"
                raise BacktestError(msg)
            if any(window < 2 for window in self.dc_windows):
                msg = "dc_windows entries must each be at least 2"
                raise BacktestError(msg)
            if len(set(self.dc_windows)) != 4:
                msg = "dc_windows must not contain duplicates"
                raise BacktestError(msg)
            if self.dc_exit not in ("half_low", "mid_channel"):
                msg = "dc_exit must be 'half_low' or 'mid_channel'"
                raise BacktestError(msg)
            if self.vol_target_annualized is not None:
                msg = (
                    "vol overlay is not supported for donchian_breakout_ensemble "
                    "(experiment-7 pre-registration scope)"
                )
                raise BacktestError(msg)
        if self.confirm_days < 1:
            msg = "confirm_days must be at least 1"
            raise BacktestError(msg)
        if self.vol_target_annualized is not None and self.vol_target_annualized <= Decimal("0"):
            msg = "vol_target_annualized must be positive when set"
            raise BacktestError(msg)
        if self.vol_window_days < 2:
            msg = "vol_window_days must be at least 2"
            raise BacktestError(msg)
        if self.vol_rebalance not in ("daily", "monthly"):
            msg = "vol_rebalance must be 'daily' or 'monthly'"
            raise BacktestError(msg)
        if self.cs_top_k < 1:
            msg = "cs_top_k must be at least 1"
            raise BacktestError(msg)
        if self.cs_lookback_days < 2:
            msg = "cs_lookback_days must be at least 2"
            raise BacktestError(msg)
        if self.cs_rebalance_cadence not in ("weekly", "monthly"):
            msg = "cs_rebalance_cadence must be 'weekly' or 'monthly'"
            raise BacktestError(msg)
        if self.cs_min_pool_size < 1:
            msg = "cs_min_pool_size must be at least 1"
            raise BacktestError(msg)
        if self.cs_decision_start is not None:
            try:
                date.fromisoformat(self.cs_decision_start)
            except ValueError as exc:
                msg = "cs_decision_start must be an ISO date (YYYY-MM-DD)"
                raise BacktestError(msg) from exc
        if self.cs_gate_sma_window is not None and self.cs_gate_sma_window < 2:
            msg = "cs_gate_sma_window must be at least 2 when set"
            raise BacktestError(msg)
        if self.cs_gate_basis not in ("btc", "per_symbol"):
            msg = "cs_gate_basis must be 'btc' or 'per_symbol'"
            raise BacktestError(msg)
        if self.cs_gate_hysteresis < Decimal("0"):
            msg = "cs_gate_hysteresis must not be negative"
            raise BacktestError(msg)
        if self.cs_gate_cadence not in ("daily", "monthly"):
            msg = "cs_gate_cadence must be 'daily' or 'monthly'"
            raise BacktestError(msg)
        if any(horizon < 2 for horizon in self.cs_horizon_days):
            msg = "cs_horizon_days entries must each be at least 2"
            raise BacktestError(msg)
        if len(set(self.cs_horizon_days)) != len(self.cs_horizon_days):
            msg = "cs_horizon_days must not contain duplicates"
            raise BacktestError(msg)
        if self.strategy_name == "cross_sectional_momentum":
            if self.cs_top_k > len(self.risk_budgets):
                msg = "cs_top_k must not exceed the size of the universe"
                raise BacktestError(msg)
            # Experiment 4 lifted the earlier vol-overlay refusal: the
            # overlay resizes execution targets per symbol (de-risk only);
            # raw cross-sectional weights still drive selection state.
            if self.cs_gate_sma_window is not None and self.vol_target_annualized is not None:
                msg = (
                    "regime gate and vol overlay are mutually exclusive "
                    "(experiment-5 pre-registration scope)"
                )
                raise BacktestError(msg)
        if self.initial_cash <= Decimal("0"):
            msg = "initial_cash must be positive"
            raise BacktestError(msg)
        if not self.account_id.strip():
            msg = "account_id must not be empty"
            raise BacktestError(msg)
        if self.cost_multiplier <= Decimal("0"):
            msg = "cost_multiplier must be positive"
            raise BacktestError(msg)
        if self.stale_data_max_age_seconds <= 0:
            msg = "stale_data_max_age_seconds must be positive"
            raise BacktestError(msg)
        object.__setattr__(self, "risk_budgets", MappingProxyType(dict(self.risk_budgets)))

    @property
    def effective_fee_bps(self) -> Decimal:
        """Fee bps after the cost-stress multiplier."""

        return self.fee_bps * self.cost_multiplier

    @property
    def effective_slippage_bps(self) -> Decimal:
        """Slippage bps after the cost-stress multiplier."""

        return self.slippage_bps * self.cost_multiplier


@dataclass(frozen=True, slots=True)
class SignalLogEntry:
    """One strategy decision recorded during replay."""

    symbol: str
    as_of: datetime
    exposure_fraction: Decimal
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TargetLogEntry:
    """One portfolio target set recorded during replay."""

    as_of: datetime
    target_weights: tuple[tuple[str, Decimal], ...]
    cash_weight: Decimal
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EquityPoint:
    """One equity curve point marked at a daily close."""

    close_time: datetime
    equity: Decimal
    drawdown: Decimal
    benchmark_equity: Decimal


@dataclass(frozen=True, slots=True)
class BacktestMetrics:
    """Headline after-cost metrics for one replay."""

    final_equity: Decimal
    total_return_fraction: Decimal
    annualized_sharpe: Decimal
    max_drawdown_fraction: Decimal
    trade_count: int
    rejected_count: int
    total_fees: Decimal
    total_slippage: Decimal
    total_traded_notional: Decimal
    annualized_turnover: Decimal
    benchmark_final_equity: Decimal
    observation_days: int


@dataclass(frozen=True, slots=True)
class BacktestReport:
    """Full auditable output of one daily replay."""

    data_start: datetime
    data_end: datetime
    decision_days: int
    signals: tuple[SignalLogEntry, ...]
    targets: tuple[TargetLogEntry, ...]
    accepted_orders: tuple[BrokerAcceptedOrder, ...]
    fills: tuple[VirtualFill, ...]
    rejected_orders: tuple[BrokerRejectedOrder, ...]
    risk_rejections: tuple[tuple[str, datetime, tuple[str, ...]], ...]
    risk_events: tuple[RiskEvent, ...]
    equity_curve: tuple[EquityPoint, ...]
    metrics: BacktestMetrics
    cost_assumptions: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.data_end < self.data_start:
            msg = "data_end must not precede data_start"
            raise BacktestError(msg)
        object.__setattr__(self, "cost_assumptions", MappingProxyType(dict(self.cost_assumptions)))

    def to_json_dict(self) -> dict[str, object]:
        """JSON-serializable report for run artifacts."""

        return {
            "data_start": self.data_start.isoformat(),
            "data_end": self.data_end.isoformat(),
            "decision_days": self.decision_days,
            "signals": [
                {
                    "symbol": entry.symbol,
                    "as_of": entry.as_of.isoformat(),
                    "exposure_fraction": str(entry.exposure_fraction),
                    "reason_codes": list(entry.reason_codes),
                }
                for entry in self.signals
            ],
            "targets": [
                {
                    "as_of": entry.as_of.isoformat(),
                    "target_weights": {
                        symbol: str(weight) for symbol, weight in entry.target_weights
                    },
                    "cash_weight": str(entry.cash_weight),
                    "reason_codes": list(entry.reason_codes),
                }
                for entry in self.targets
            ],
            "accepted_orders": [
                {
                    "order_id": order.order_id,
                    "symbol": order.intent.symbol.value,
                    "side": order.intent.side.value,
                    "quantity": str(order.intent.quantity),
                    "accepted_at": order.accepted_at.isoformat(),
                }
                for order in self.accepted_orders
            ],
            "fills": [
                {
                    "fill_id": fill.fill_id,
                    "order_id": fill.order_id,
                    "symbol": fill.symbol.value,
                    "side": fill.side.value,
                    "quantity": str(fill.quantity),
                    "price": str(fill.price),
                    "fee": str(fill.fee),
                    "slippage": str(fill.slippage),
                    "filled_at": fill.filled_at.isoformat(),
                }
                for fill in self.fills
            ],
            "rejected_orders": [
                {
                    "order_id": order.order_id,
                    "symbol": order.intent.symbol.value if order.intent else None,
                    "rejected_at": order.rejected_at.isoformat(),
                    "reason_codes": list(order.reason_codes),
                }
                for order in self.rejected_orders
            ],
            "risk_rejections": [
                {
                    "symbol": symbol,
                    "decided_at": decided_at.isoformat(),
                    "reason_codes": list(reason_codes),
                }
                for symbol, decided_at, reason_codes in self.risk_rejections
            ],
            "risk_events": [
                {
                    "symbol": event.symbol.value,
                    "event_type": event.event_type,
                    "observed_fraction": str(event.observed_fraction),
                    "threshold_fraction": str(event.threshold_fraction),
                    "occurred_at": event.occurred_at.isoformat(),
                    "reason_codes": list(event.reason_codes),
                }
                for event in self.risk_events
            ],
            "equity_curve": [
                {
                    "close_time": point.close_time.isoformat(),
                    "equity": str(point.equity),
                    "drawdown": str(point.drawdown),
                    "benchmark_equity": str(point.benchmark_equity),
                }
                for point in self.equity_curve
            ],
            "metrics": {
                "final_equity": str(self.metrics.final_equity),
                "total_return_fraction": str(self.metrics.total_return_fraction),
                "annualized_sharpe": str(self.metrics.annualized_sharpe),
                "max_drawdown_fraction": str(self.metrics.max_drawdown_fraction),
                "trade_count": self.metrics.trade_count,
                "rejected_count": self.metrics.rejected_count,
                "total_fees": str(self.metrics.total_fees),
                "total_slippage": str(self.metrics.total_slippage),
                "total_traded_notional": str(self.metrics.total_traded_notional),
                "annualized_turnover": str(self.metrics.annualized_turnover),
                "benchmark_final_equity": str(self.metrics.benchmark_final_equity),
                "observation_days": self.metrics.observation_days,
            },
            "cost_assumptions": dict(self.cost_assumptions),
        }


def require_utc(name: str, value: datetime) -> None:
    """Shared UTC-awareness guard for backtest inputs."""

    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = f"{name} must be timezone-aware UTC"
        raise BacktestError(msg)

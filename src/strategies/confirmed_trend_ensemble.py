"""Confirmed Trend Ensemble (contract: STRATEGY_CONFIRMED_TREND_ENSEMBLE.md).

Backtest-only Goal P variant: the unchanged Daily Trend Ensemble behind a
symmetric N-consecutive-close confirmation filter. Pre-registered in
docs/research/GOALP_PREREGISTRATION.md; the live qualification runtime never
runs this (its contract is frozen on the original ensemble).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from src.domain import Signal
from src.features import FeatureSnapshot
from src.strategies.daily_trend_ensemble import (
    LADDER_HOLD,
    evaluate_daily_trend_ensemble,
)
from src.strategies.types import DailyTrendEnsembleDecision, StrategyValidationError

DEFAULT_CONFIRM_DAYS = 2

_LADDER_MOVE_CODES = frozenset({"LADDER_UP", "LADDER_DOWN", LADDER_HOLD})


@dataclass(frozen=True, slots=True)
class ConfirmationState:
    """Explicit cross-day confirmation state, carried by the caller.

    ``pending_fraction`` is the proposal being counted; ``pending_days`` is
    how many consecutive closes have produced it. Keeping this state explicit
    (instead of hidden inside the strategy) preserves the engine's replay
    determinism: same inputs, same outputs, always.
    """

    pending_fraction: Decimal = Decimal("0")
    pending_days: int = 0


def evaluate_confirmed_trend_ensemble(
    snapshot: FeatureSnapshot,
    *,
    previous_fraction: Decimal | None = None,
    state: ConfirmationState | None = None,
    confirm_days: int = DEFAULT_CONFIRM_DAYS,
) -> tuple[DailyTrendEnsembleDecision, ConfirmationState]:
    """One confirmed decision plus the state to carry into tomorrow.

    The raw ensemble runs unchanged; a proposal differing from the held
    fraction is adopted only after ``confirm_days`` consecutive closes with
    that same proposal. Symmetric by pre-registration: ups and downs both
    wait. The pending decision holds the previous fraction and says why.
    """

    if confirm_days < 1:
        msg = "confirm_days must be at least 1"
        raise StrategyValidationError(msg)
    held = previous_fraction if previous_fraction is not None else Decimal("0")
    raw = evaluate_daily_trend_ensemble(snapshot, previous_fraction=previous_fraction)
    proposal = raw.exposure_fraction

    if proposal == held:
        # Ensemble agrees with what we hold; nothing pends.
        return raw, ConfirmationState(pending_fraction=proposal, pending_days=0)

    current = state if state is not None else ConfirmationState()
    seen = current.pending_days + 1 if current.pending_fraction == proposal else 1
    next_state = ConfirmationState(pending_fraction=proposal, pending_days=seen)

    if seen >= confirm_days:
        confirmed = replace(
            raw,
            reason_codes=(*raw.reason_codes, f"CONFIRMED_AFTER_{confirm_days}"),
        )
        return confirmed, next_state

    # Not confirmed yet: hold yesterday's fraction, keep the sub-signal truth,
    # and replace the ladder-move code with HOLD plus the pending marker.
    held_codes = tuple(code for code in raw.reason_codes if code not in _LADDER_MOVE_CODES)
    pending_decision = replace(
        raw,
        signal=Signal.LONG if held > Decimal("0") else Signal.FLAT,
        exposure_fraction=held,
        score=held,
        reason_codes=(
            *held_codes,
            LADDER_HOLD,
            f"PENDING_CONFIRMATION_{seen}_{confirm_days}",
        ),
    )
    return pending_decision, next_state

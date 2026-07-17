from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Signal, Symbol, Timeframe
from src.features import FeatureSnapshot, FeatureSourceRange
from src.strategies import (
    ConfirmationState,
    StrategyValidationError,
    evaluate_confirmed_trend_ensemble,
)

_AS_OF = datetime(2025, 12, 31, 23, 59, 59, 999000, tzinfo=UTC)


def _snapshot(*, close: str) -> FeatureSnapshot:
    # SMAs fixed at 100: close above/below 100 moves all four rungs together,
    # which makes ladder proposals easy to steer per test day.
    return FeatureSnapshot(
        symbol=Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        timeframe=Timeframe("1d"),
        as_of=_AS_OF,
        source_ranges=(
            FeatureSourceRange(
                symbol=Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
                timeframe=Timeframe("1d"),
                start_open_time=_AS_OF - timedelta(days=200),
                end_close_time=_AS_OF,
            ),
        ),
        values={
            "close_price": Decimal(close),
            "sma_20": Decimal("100"),
            "sma_65": Decimal("100"),
            "sma_150": Decimal("100"),
            "sma_200": Decimal("100"),
        },
    )


def test_first_divergent_proposal_pends_and_holds_the_previous_fraction() -> None:
    decision, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"),  # proposal: 1.0
        previous_fraction=Decimal("0"),
        state=None,
        confirm_days=2,
    )

    assert decision.exposure_fraction == Decimal("0")
    assert decision.signal is Signal.FLAT
    assert "PENDING_CONFIRMATION_1_2" in decision.reason_codes
    assert "LADDER_HOLD" in decision.reason_codes
    # Sub-signal truth is preserved even while pending.
    assert "ABOVE_SMA_200" in decision.reason_codes
    assert state == ConfirmationState(pending_fraction=Decimal("1"), pending_days=1)


def test_second_consecutive_proposal_confirms_and_adopts() -> None:
    _, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"),
        previous_fraction=Decimal("0"),
        confirm_days=2,
    )
    decision, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"),
        previous_fraction=Decimal("0"),
        state=state,
        confirm_days=2,
    )

    assert decision.exposure_fraction == Decimal("1")
    assert decision.signal is Signal.LONG
    assert "CONFIRMED_AFTER_2" in decision.reason_codes
    assert state.pending_days == 2


def test_one_day_whipsaw_never_reaches_the_ladder() -> None:
    # Day 1: proposal jumps to 1.0 (pending). Day 2: back to 0 == held ->
    # pending resets, nothing ever executed. The exact regime the
    # pre-registered hypothesis targets.
    _, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"), previous_fraction=Decimal("0"), confirm_days=2
    )
    decision, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="90"), previous_fraction=Decimal("0"), state=state, confirm_days=2
    )

    assert decision.exposure_fraction == Decimal("0")
    assert "PENDING_CONFIRMATION" not in " ".join(decision.reason_codes)
    assert state.pending_days == 0


def test_changed_proposal_mid_count_restarts_at_one() -> None:
    _, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"),  # proposal 1.0, day 1
        previous_fraction=Decimal("0.5"),
        confirm_days=3,
    )
    decision, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="90"),  # proposal 0.0 != pending 1.0 -> restart
        previous_fraction=Decimal("0.5"),
        state=state,
        confirm_days=3,
    )

    assert decision.exposure_fraction == Decimal("0.5")
    assert "PENDING_CONFIRMATION_1_3" in decision.reason_codes
    assert state == ConfirmationState(pending_fraction=Decimal("0"), pending_days=1)


def test_symmetry_ladder_down_also_waits() -> None:
    decision, state = evaluate_confirmed_trend_ensemble(
        _snapshot(close="90"),  # proposal 0.0 vs held 1.0
        previous_fraction=Decimal("1"),
        confirm_days=2,
    )

    assert decision.exposure_fraction == Decimal("1")
    assert decision.signal is Signal.LONG
    assert "PENDING_CONFIRMATION_1_2" in decision.reason_codes

    decision, _ = evaluate_confirmed_trend_ensemble(
        _snapshot(close="90"),
        previous_fraction=Decimal("1"),
        state=state,
        confirm_days=2,
    )
    assert decision.exposure_fraction == Decimal("0")
    assert "CONFIRMED_AFTER_2" in decision.reason_codes


def test_confirm_days_one_matches_the_raw_ensemble_behavior() -> None:
    decision, _ = evaluate_confirmed_trend_ensemble(
        _snapshot(close="150"),
        previous_fraction=Decimal("0"),
        confirm_days=1,
    )

    assert decision.exposure_fraction == Decimal("1")
    assert "CONFIRMED_AFTER_1" in decision.reason_codes


def test_confirm_days_below_one_is_rejected() -> None:
    with pytest.raises(StrategyValidationError):
        evaluate_confirmed_trend_ensemble(
            _snapshot(close="150"), previous_fraction=Decimal("0"), confirm_days=0
        )

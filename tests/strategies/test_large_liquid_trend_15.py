from __future__ import annotations

from dataclasses import fields
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Signal, Symbol, Timeframe
from src.features import FeatureSnapshot, FeatureSourceRange
from src.strategies import (
    LargeLiquidTrend15Parameters,
    StrategyDecision,
    StrategyValidationError,
    evaluate_large_liquid_trend_15,
)


def _symbol() -> Symbol:
    return Symbol(value="ETHUSDT", base_asset="ETH", quote_asset="USDT")


def _timeframe() -> Timeframe:
    return Timeframe("15m")


def _snapshot(values: dict[str, Decimal]) -> FeatureSnapshot:
    as_of = datetime(2026, 5, 20, 0, 14, 59, 999000, tzinfo=UTC)
    return FeatureSnapshot(
        symbol=_symbol(),
        timeframe=_timeframe(),
        as_of=as_of,
        source_ranges=(
            FeatureSourceRange(
                symbol=_symbol(),
                timeframe=_timeframe(),
                start_open_time=as_of - timedelta(minutes=15) + timedelta(milliseconds=1),
                end_close_time=as_of,
            ),
        ),
        values=values,
    )


def _strong_values() -> dict[str, Decimal]:
    return {
        "momentum_return": Decimal("0.05"),
        "trend_distance": Decimal("0.03"),
        "recent_high_distance": Decimal("0.01"),
        "volume_ratio": Decimal("2"),
        "btc_momentum_return": Decimal("0.02"),
        "btc_trend_distance": Decimal("0.01"),
    }


def test_large_liquid_trend_15_returns_long_with_score_and_reason_codes() -> None:
    snapshot = _snapshot(_strong_values())

    decision = evaluate_large_liquid_trend_15(snapshot)

    assert decision.symbol == _symbol()
    assert decision.signal is Signal.LONG
    assert decision.score == Decimal("1.00")
    assert decision.reason_codes == (
        "MOMENTUM_POSITIVE",
        "TREND_POSITIVE",
        "BREAKOUT_CONFIRMED",
        "VOLUME_CONFIRMED",
        "BTC_TREND_SUPPORTS",
        "ENTRY_SCORE_MET",
    )
    assert decision.generated_at_bar_close == snapshot.as_of
    assert decision.executable_from_next_bar == snapshot.as_of + timedelta(milliseconds=1)


def test_large_liquid_trend_15_returns_flat_when_strength_is_missing() -> None:
    snapshot = _snapshot(
        {
            "momentum_return": Decimal("-0.01"),
            "trend_distance": Decimal("-0.01"),
            "recent_high_distance": Decimal("-0.01"),
            "volume_ratio": Decimal("0.5"),
            "btc_momentum_return": Decimal("-0.01"),
            "btc_trend_distance": Decimal("-0.01"),
        }
    )

    decision = evaluate_large_liquid_trend_15(snapshot)

    assert decision.signal is Signal.FLAT
    assert decision.score == Decimal("0")
    assert "ENTRY_SCORE_NOT_MET" in decision.reason_codes
    assert "EXIT_SCORE_MET" in decision.reason_codes


def test_entry_threshold_is_inclusive_and_does_not_require_every_reason() -> None:
    snapshot = _snapshot(
        {
            "momentum_return": Decimal("0.01"),
            "trend_distance": Decimal("0.01"),
            "recent_high_distance": Decimal("0.01"),
            "volume_ratio": Decimal("0.5"),
            "btc_momentum_return": Decimal("-0.01"),
            "btc_trend_distance": Decimal("-0.01"),
        }
    )

    decision = evaluate_large_liquid_trend_15(snapshot)

    assert decision.score == Decimal("0.70")
    assert decision.signal is Signal.LONG


def test_strategy_output_is_deterministic_for_same_input() -> None:
    snapshot = _snapshot(_strong_values())

    first = evaluate_large_liquid_trend_15(snapshot)
    second = evaluate_large_liquid_trend_15(snapshot)

    assert first == second


def test_strategy_output_has_no_order_or_sizing_fields() -> None:
    assert {field.name for field in fields(StrategyDecision)} == {
        "symbol",
        "signal",
        "score",
        "reason_codes",
        "generated_at_bar_close",
        "executable_from_next_bar",
    }


def test_missing_required_feature_is_rejected() -> None:
    values = _strong_values()
    del values["trend_distance"]

    with pytest.raises(StrategyValidationError, match="missing required strategy feature"):
        evaluate_large_liquid_trend_15(_snapshot(values))


def test_non_15m_feature_snapshot_is_rejected() -> None:
    as_of = datetime(2026, 5, 20, 0, 59, 59, 999000, tzinfo=UTC)
    snapshot = FeatureSnapshot(
        symbol=_symbol(),
        timeframe=Timeframe("1h"),
        as_of=as_of,
        source_ranges=(
            FeatureSourceRange(
                symbol=_symbol(),
                timeframe=Timeframe("1h"),
                start_open_time=as_of - timedelta(hours=1) + timedelta(milliseconds=1),
                end_close_time=as_of,
            ),
        ),
        values=_strong_values(),
    )

    with pytest.raises(StrategyValidationError, match="15m"):
        evaluate_large_liquid_trend_15(snapshot)


def test_strategy_parameters_reject_invalid_score_ordering() -> None:
    with pytest.raises(StrategyValidationError, match="exit_score"):
        LargeLiquidTrend15Parameters(
            minimum_entry_score=Decimal("0.70"),
            exit_score=Decimal("0.80"),
        )

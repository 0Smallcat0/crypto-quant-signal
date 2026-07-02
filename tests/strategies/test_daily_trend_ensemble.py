from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Signal, Symbol, Timeframe
from src.features import FeatureSnapshot, FeatureSourceRange
from src.strategies import (
    LADDER_DOWN,
    LADDER_HOLD,
    LADDER_UP,
    DailyTrendEnsembleDecision,
    DailyTrendSubSignals,
    StrategyValidationError,
    evaluate_daily_trend_ensemble,
)

_AS_OF = datetime(2025, 12, 31, 23, 59, 59, 999000, tzinfo=UTC)


def _symbol() -> Symbol:
    return Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT")


def _snapshot(
    *,
    close: str,
    sma_20: str,
    sma_65: str,
    sma_150: str,
    sma_200: str,
    timeframe_value: str = "1d",
    drop_feature: str | None = None,
) -> FeatureSnapshot:
    values = {
        "close_price": Decimal(close),
        "sma_20": Decimal(sma_20),
        "sma_65": Decimal(sma_65),
        "sma_150": Decimal(sma_150),
        "sma_200": Decimal(sma_200),
    }
    if drop_feature is not None:
        values.pop(drop_feature)
    return FeatureSnapshot(
        symbol=_symbol(),
        timeframe=Timeframe(timeframe_value),
        as_of=_AS_OF,
        source_ranges=(
            FeatureSourceRange(
                symbol=_symbol(),
                timeframe=Timeframe(timeframe_value),
                start_open_time=_AS_OF - timedelta(days=200),
                end_close_time=_AS_OF,
            ),
        ),
        values=values,
    )


def test_all_lines_reclaimed_yields_full_exposure_long() -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="110", sma_20="100", sma_65="90", sma_150="80", sma_200="70")
    )

    assert decision.signal is Signal.LONG
    assert decision.exposure_fraction == Decimal("1")
    assert decision.score == Decimal("1")
    assert decision.sub_signals.active_count == 4
    for code in ("ABOVE_SMA_20", "ABOVE_SMA_65", "ABOVE_SMA_150", "ABOVE_SMA_200"):
        assert code in decision.reason_codes


def test_all_lines_broken_yields_flat_cash() -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="60", sma_20="100", sma_65="90", sma_150="80", sma_200="70")
    )

    assert decision.signal is Signal.FLAT
    assert decision.exposure_fraction == Decimal("0")
    for code in ("BELOW_SMA_20", "BELOW_SMA_65", "BELOW_SMA_150", "BELOW_SMA_200"):
        assert code in decision.reason_codes


def test_two_lines_above_yields_half_ladder() -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="95", sma_20="100", sma_65="98", sma_150="80", sma_200="70")
    )

    assert decision.signal is Signal.LONG
    assert decision.exposure_fraction == Decimal("0.5")
    assert decision.sub_signals == DailyTrendSubSignals(
        above_sma_20=False,
        above_sma_65=False,
        above_sma_150=True,
        above_sma_200=True,
    )


def test_close_equal_to_sma_counts_as_not_above() -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="100", sma_20="100", sma_65="100", sma_150="100", sma_200="100")
    )

    assert decision.exposure_fraction == Decimal("0")
    assert decision.signal is Signal.FLAT


@pytest.mark.parametrize(
    ("previous_fraction", "expected_code"),
    (
        (None, LADDER_UP),
        (Decimal("0"), LADDER_UP),
        (Decimal("0.5"), LADDER_HOLD),
        (Decimal("1"), LADDER_DOWN),
    ),
)
def test_ladder_transition_codes_compare_against_previous_fraction(
    previous_fraction: Decimal | None, expected_code: str
) -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="95", sma_20="100", sma_65="98", sma_150="80", sma_200="70"),
        previous_fraction=previous_fraction,
    )

    assert decision.exposure_fraction == Decimal("0.5")
    assert expected_code in decision.reason_codes
    ladder_codes = {LADDER_UP, LADDER_DOWN, LADDER_HOLD}
    assert len(ladder_codes.intersection(decision.reason_codes)) == 1


def test_identical_input_produces_identical_decision() -> None:
    snapshot = _snapshot(close="110", sma_20="100", sma_65="90", sma_150="80", sma_200="70")

    first = evaluate_daily_trend_ensemble(snapshot, previous_fraction=Decimal("0.25"))
    second = evaluate_daily_trend_ensemble(snapshot, previous_fraction=Decimal("0.25"))

    assert first == second


def test_decision_is_executable_only_after_bar_close() -> None:
    decision = evaluate_daily_trend_ensemble(
        _snapshot(close="110", sma_20="100", sma_65="90", sma_150="80", sma_200="70")
    )

    assert decision.generated_at_bar_close == _AS_OF
    assert decision.executable_from_next_bar > decision.generated_at_bar_close


def test_non_daily_snapshot_is_rejected() -> None:
    with pytest.raises(StrategyValidationError, match="1d"):
        evaluate_daily_trend_ensemble(
            _snapshot(
                close="110",
                sma_20="100",
                sma_65="90",
                sma_150="80",
                sma_200="70",
                timeframe_value="15m",
            )
        )


def test_missing_required_feature_is_rejected() -> None:
    with pytest.raises(StrategyValidationError, match="sma_150"):
        evaluate_daily_trend_ensemble(
            _snapshot(
                close="110",
                sma_20="100",
                sma_65="90",
                sma_150="80",
                sma_200="70",
                drop_feature="sma_150",
            )
        )


def test_invalid_previous_fraction_is_rejected() -> None:
    with pytest.raises(StrategyValidationError, match="previous_fraction"):
        evaluate_daily_trend_ensemble(
            _snapshot(close="110", sma_20="100", sma_65="90", sma_150="80", sma_200="70"),
            previous_fraction=Decimal("0.3"),
        )


def test_decision_type_rejects_off_ladder_fractions() -> None:
    with pytest.raises(StrategyValidationError, match="exposure_fraction"):
        DailyTrendEnsembleDecision(
            symbol=_symbol(),
            signal=Signal.LONG,
            exposure_fraction=Decimal("0.3"),
            sub_signals=DailyTrendSubSignals(
                above_sma_20=True,
                above_sma_65=False,
                above_sma_150=False,
                above_sma_200=False,
            ),
            score=Decimal("0.3"),
            reason_codes=("TEST",),
            generated_at_bar_close=_AS_OF,
            executable_from_next_bar=_AS_OF + timedelta(milliseconds=1),
        )


def test_decision_type_rejects_signal_fraction_mismatch() -> None:
    with pytest.raises(StrategyValidationError, match="signal"):
        DailyTrendEnsembleDecision(
            symbol=_symbol(),
            signal=Signal.FLAT,
            exposure_fraction=Decimal("0.5"),
            sub_signals=DailyTrendSubSignals(
                above_sma_20=True,
                above_sma_65=True,
                above_sma_150=False,
                above_sma_200=False,
            ),
            score=Decimal("0.5"),
            reason_codes=("TEST",),
            generated_at_bar_close=_AS_OF,
            executable_from_next_bar=_AS_OF + timedelta(milliseconds=1),
        )

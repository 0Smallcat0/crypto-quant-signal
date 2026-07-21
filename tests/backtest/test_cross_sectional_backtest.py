"""Cross-sectional momentum engine path (experiment 3 pre-registration)."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from src.backtest import BacktestError, BacktestParameters, run_backtest
from src.backtest.engine import _cs_cadence_key
from src.domain import Candle, Symbol, Timeframe

_BASE_OPEN_TIME = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _daily_candle(symbol: Symbol, index: int, close: Decimal) -> Candle:
    open_time = _BASE_OPEN_TIME + timedelta(days=index)
    return Candle(
        symbol=symbol,
        timeframe=Timeframe("1d"),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=close,
        high_price=close + Decimal("1"),
        low_price=max(close - Decimal("1"), Decimal("0.01")),
        close_price=close,
        volume=Decimal("1000"),
        is_closed=True,
    )


def _candles_for(symbol: Symbol, prices: tuple[Decimal, ...]) -> tuple[Candle, ...]:
    return tuple(_daily_candle(symbol, index, price) for index, price in enumerate(prices))


def _linear_series(start: Decimal, step: Decimal, count: int) -> tuple[Decimal, ...]:
    return tuple(start + step * Decimal(index) for index in range(count))


def _small_universe(*, days: int = 60) -> dict[str, tuple[Candle, ...]]:
    """Four-symbol universe with easily ranked lookback returns.

    A rises fastest, B rises, C flat, D falls. At any decision day inside the
    lookback horizon, ranking is A > B > C > D.
    """

    return {
        "AUSDT": _candles_for(
            _symbol("AUSDT", "A"), _linear_series(Decimal("100"), Decimal("5"), days)
        ),
        "BUSDT": _candles_for(
            _symbol("BUSDT", "B"), _linear_series(Decimal("100"), Decimal("2"), days)
        ),
        "CUSDT": _candles_for(_symbol("CUSDT", "C"), tuple([Decimal("100")] * days)),
        "DUSDT": _candles_for(
            _symbol("DUSDT", "D"),
            _linear_series(Decimal("100"), Decimal("-1"), days),
        ),
    }


def _parameters(
    *,
    top_k: int = 2,
    lookback: int = 10,
    cadence: str = "weekly",
    absolute_filter: bool = False,
    min_pool: int = 4,
) -> BacktestParameters:
    return BacktestParameters(
        risk_budgets={
            "AUSDT": Decimal("0.25"),
            "BUSDT": Decimal("0.25"),
            "CUSDT": Decimal("0.25"),
            "DUSDT": Decimal("0.25"),
        },
        initial_cash=Decimal("10000"),
        account_id="cs-test",
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("5"),
        quantity_step=Decimal("0.000001"),
        price_tick=Decimal("0.01"),
        min_notional_usdt=Decimal("10"),
        max_drawdown_fraction=Decimal("0.50"),
        daily_loss_pause_fraction=Decimal("0.10"),
        disaster_single_day_drop_fraction=Decimal("0.20"),
        stale_data_max_age_seconds=129600,
        strategy_name="cross_sectional_momentum",
        cs_top_k=top_k,
        cs_lookback_days=lookback,
        cs_rebalance_cadence=cadence,
        cs_absolute_filter=absolute_filter,
        cs_min_pool_size=min_pool,
    )


def test_cross_sectional_requires_a_valid_top_k() -> None:
    with pytest.raises(BacktestError, match="cs_top_k must not exceed"):
        _parameters(top_k=5)


def test_cross_sectional_rejects_vol_overlay() -> None:
    with pytest.raises(BacktestError, match="vol overlay is not supported"):
        BacktestParameters(
            risk_budgets={"AUSDT": Decimal("1")},
            initial_cash=Decimal("1000"),
            account_id="cs-test",
            fee_bps=Decimal("10"),
            slippage_bps=Decimal("5"),
            quantity_step=Decimal("0.000001"),
            price_tick=Decimal("0.01"),
            min_notional_usdt=Decimal("10"),
            max_drawdown_fraction=Decimal("0.50"),
            daily_loss_pause_fraction=Decimal("0.10"),
            disaster_single_day_drop_fraction=Decimal("0.20"),
            stale_data_max_age_seconds=129600,
            strategy_name="cross_sectional_momentum",
            cs_top_k=1,
            vol_target_annualized=Decimal("0.5"),
        )


def test_cross_sectional_rejects_unknown_cadence() -> None:
    with pytest.raises(BacktestError, match="cs_rebalance_cadence"):
        _parameters(cadence="daily")


def test_cadence_key_changes_on_iso_week_boundary() -> None:
    a = datetime(2024, 1, 7, tzinfo=UTC)  # ISO week 1
    b = datetime(2024, 1, 8, tzinfo=UTC)  # ISO week 2
    assert _cs_cadence_key(a, "weekly") != _cs_cadence_key(b, "weekly")
    assert _cs_cadence_key(a, "weekly") == _cs_cadence_key(a - timedelta(days=1), "weekly")


def test_cadence_key_changes_on_month_boundary() -> None:
    a = datetime(2024, 1, 31, tzinfo=UTC)
    b = datetime(2024, 2, 1, tzinfo=UTC)
    assert _cs_cadence_key(a, "monthly") != _cs_cadence_key(b, "monthly")
    assert _cs_cadence_key(a, "monthly") == _cs_cadence_key(a - timedelta(days=30), "monthly")


def test_first_rebalance_picks_the_top_k_by_trailing_return() -> None:
    report = run_backtest(_small_universe(days=40), parameters=_parameters(top_k=2))

    first_targets = report.targets[0]
    holders = {symbol_value for symbol_value, _ in first_targets.target_weights}
    weights = dict(first_targets.target_weights)

    assert holders == {"AUSDT", "BUSDT"}
    assert weights["AUSDT"] == Decimal("0.5")
    assert weights["BUSDT"] == Decimal("0.5")
    assert "CS_REBALANCE" in first_targets.reason_codes


def test_absolute_filter_replaces_negative_lookback_symbols_with_cash() -> None:
    days = 40
    falling_universe = {
        symbol_value: _candles_for(
            _symbol(symbol_value, symbol_value[0]),
            _linear_series(Decimal("100"), Decimal("-1"), days),
        )
        for symbol_value in ("AUSDT", "BUSDT", "CUSDT", "DUSDT")
    }

    without_filter = run_backtest(
        falling_universe, parameters=_parameters(top_k=2, absolute_filter=False)
    )
    with_filter = run_backtest(
        falling_universe, parameters=_parameters(top_k=2, absolute_filter=True)
    )

    assert len(without_filter.fills) > 0
    assert len(with_filter.fills) == 0
    assert with_filter.equity_curve[-1].equity == Decimal("10000")


def test_pool_too_small_holds_cash() -> None:
    universe = {
        symbol_value: _candles_for(
            _symbol(symbol_value, symbol_value[0]),
            _linear_series(Decimal("100"), Decimal("1"), 40),
        )
        for symbol_value in ("AUSDT", "BUSDT", "CUSDT")
    }
    parameters = BacktestParameters(
        risk_budgets={
            "AUSDT": Decimal("0.33"),
            "BUSDT": Decimal("0.33"),
            "CUSDT": Decimal("0.33"),
        },
        initial_cash=Decimal("10000"),
        account_id="cs-test",
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("5"),
        quantity_step=Decimal("0.000001"),
        price_tick=Decimal("0.01"),
        min_notional_usdt=Decimal("10"),
        max_drawdown_fraction=Decimal("0.50"),
        daily_loss_pause_fraction=Decimal("0.10"),
        disaster_single_day_drop_fraction=Decimal("0.20"),
        stale_data_max_age_seconds=129600,
        strategy_name="cross_sectional_momentum",
        cs_top_k=2,
        cs_lookback_days=10,
        cs_rebalance_cadence="weekly",
        cs_min_pool_size=4,
    )

    report = run_backtest(universe, parameters=parameters)

    rebalance_targets = [t for t in report.targets if "CS_REBALANCE" in t.reason_codes]
    for target in rebalance_targets:
        assert target.target_weights == ()
        assert target.cash_weight == Decimal("1")
    assert len(report.fills) == 0


def test_monthly_cadence_fires_once_per_calendar_month() -> None:
    report = run_backtest(_small_universe(days=90), parameters=_parameters(cadence="monthly"))

    rebalance_dates = sorted(
        {target.as_of.date() for target in report.targets if "CS_REBALANCE" in target.reason_codes}
    )
    months_covered = {(date.year, date.month) for date in rebalance_dates}
    assert len(rebalance_dates) == len(months_covered), (
        "monthly cadence must fire at most once per calendar month"
    )
    assert len(months_covered) >= 2


def test_hold_days_generate_no_fills_and_carry_target_weights() -> None:
    report = run_backtest(_small_universe(days=30), parameters=_parameters(cadence="weekly"))

    hold_entries = [t for t in report.targets if "CS_HOLD" in t.reason_codes]
    assert hold_entries, "expected at least one holding day between rebalances"

    rebalance_dates = {
        target.as_of for target in report.targets if "CS_REBALANCE" in target.reason_codes
    }
    for fill in report.fills:
        latest_prior_rebalance = max(
            (date for date in rebalance_dates if date < fill.filled_at), default=None
        )
        assert latest_prior_rebalance is not None
        assert fill.filled_at == latest_prior_rebalance + timedelta(milliseconds=1)


def test_report_includes_cross_sectional_cost_assumptions() -> None:
    report = run_backtest(
        _small_universe(days=30),
        parameters=_parameters(top_k=2, lookback=10, cadence="weekly", absolute_filter=True),
    )

    assumptions = dict(report.cost_assumptions)
    assert assumptions["cs_top_k"] == "2"
    assert assumptions["cs_lookback_days"] == "10"
    assert assumptions["cs_rebalance_cadence"] == "weekly"
    assert assumptions["cs_absolute_filter"] == "True"
    assert assumptions["fill_rule"] == "next_bar_open"


def test_ladder_strategy_paths_are_untouched_by_the_dispatch() -> None:
    from tests.backtest.test_backtest_engine import (  # noqa: PLC0415  local import
        _parameters as _ladder_parameters,
    )
    from tests.backtest.test_backtest_engine import (  # noqa: PLC0415  local import
        _trend_and_crash_universe,
    )

    baseline = run_backtest(_trend_and_crash_universe(), parameters=_ladder_parameters())
    repeat = run_backtest(
        _trend_and_crash_universe(),
        parameters=replace(_ladder_parameters(), strategy_name="daily_trend_ensemble"),
    )
    assert baseline.metrics.final_equity == repeat.metrics.final_equity
    assert len(baseline.fills) == len(repeat.fills)


def test_decision_start_floor_pins_the_first_equity_point() -> None:
    unfloored = run_backtest(_small_universe(), parameters=_parameters())
    floored = run_backtest(
        _small_universe(),
        parameters=replace(_parameters(), cs_decision_start="2024-02-01"),
    )
    assert unfloored.equity_curve[0].close_time.date() < date(2024, 2, 1)
    assert floored.equity_curve[0].close_time.date() == date(2024, 2, 1)
    assert floored.equity_curve[-1].close_time == unfloored.equity_curve[-1].close_time


def test_decision_start_must_be_an_iso_date() -> None:
    with pytest.raises(BacktestError, match="cs_decision_start"):
        replace(_parameters(), cs_decision_start="not-a-date")

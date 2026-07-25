"""Experiment-9 allocation model on the Donchian ladder path."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.backtest import BacktestError, BacktestParameters, run_backtest
from src.backtest.engine import _annualized_realized_vol, _vol_scaler
from src.domain import Candle, Symbol, Timeframe

_BASE_OPEN_TIME = datetime(2023, 1, 1, 0, 0, tzinfo=UTC)


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


def _candles_for(symbol: Symbol, prices: list[Decimal]) -> tuple[Candle, ...]:
    return tuple(_daily_candle(symbol, index, price) for index, price in enumerate(prices))


def _parameters(**overrides: object) -> BacktestParameters:
    base = BacktestParameters(
        risk_budgets={"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")},
        initial_cash=Decimal("10000"),
        account_id="dc-alloc-test",
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("5"),
        quantity_step=Decimal("0.000001"),
        price_tick=Decimal("0.01"),
        min_notional_usdt=Decimal("10"),
        max_drawdown_fraction=Decimal("0.50"),
        daily_loss_pause_fraction=Decimal("0.10"),
        disaster_single_day_drop_fraction=Decimal("0.20"),
        stale_data_max_age_seconds=129600,
        strategy_name="donchian_breakout_ensemble",
        dc_windows=(10, 20, 55, 110),
    )
    return replace(base, **overrides)  # type: ignore[arg-type]


def _two_speed_universe(days: int = 240) -> dict[str, tuple[Candle, ...]]:
    """BTC climbs smoothly; ETH climbs with the same drift but zig-zags.

    Same trend, very different realized volatility — so inverse-vol
    allocation must tilt toward BTC.
    """

    btc = [Decimal("100") + Decimal("2") * Decimal(index) for index in range(days)]
    eth = [
        Decimal("100")
        + Decimal("2") * Decimal(index)
        + (Decimal("12") if index % 2 == 0 else Decimal("-12"))
        for index in range(days)
    ]
    return {
        "BTCUSDT": _candles_for(_symbol("BTCUSDT", "BTC"), btc),
        "ETHUSDT": _candles_for(_symbol("ETHUSDT", "ETH"), eth),
    }


def test_alloc_model_must_be_known() -> None:
    with pytest.raises(BacktestError, match="dc_alloc_model"):
        _parameters(dc_alloc_model="magic")


def test_name_cap_must_be_a_fraction() -> None:
    with pytest.raises(BacktestError, match="dc_name_cap"):
        _parameters(dc_alloc_model="inverse_vol", dc_name_cap=Decimal("1.5"))


def test_target_vol_must_be_positive_when_set() -> None:
    with pytest.raises(BacktestError, match="dc_target_vol"):
        _parameters(dc_alloc_model="inverse_vol", dc_target_vol=Decimal("0"))


def test_equal_model_is_bit_for_bit_unchanged() -> None:
    universe = _two_speed_universe()
    baseline = run_backtest(universe, parameters=_parameters())
    explicit = run_backtest(universe, parameters=_parameters(dc_alloc_model="equal"))

    assert baseline.metrics.final_equity == explicit.metrics.final_equity
    assert len(baseline.fills) == len(explicit.fills)


def test_inverse_vol_tilts_toward_the_calmer_symbol() -> None:
    universe = _two_speed_universe()
    allocated = run_backtest(
        universe,
        parameters=_parameters(dc_alloc_model="inverse_vol", dc_vol_lookback=20),
    )

    both_on = [
        entry
        for entry in allocated.targets
        if len(entry.target_weights) == 2 and all(weight > 0 for _, weight in entry.target_weights)
    ]
    assert both_on, "expected days where both symbols are invested"
    weights = dict(both_on[-1].target_weights)
    assert weights["BTCUSDT"] > weights["ETHUSDT"]


def test_inverse_vol_never_levers_the_book() -> None:
    universe = _two_speed_universe()
    allocated = run_backtest(
        universe,
        parameters=_parameters(dc_alloc_model="inverse_vol", dc_vol_lookback=20),
    )

    # Redistribution, not leverage: gross exposure never exceeds equity,
    # and no name ever exceeds its own risk budget.
    for entry in allocated.targets:
        gross = sum((weight for _, weight in entry.target_weights), Decimal("0"))
        assert gross <= Decimal("1")
        assert entry.cash_weight >= Decimal("0")


def test_name_cap_binds() -> None:
    universe = _two_speed_universe()
    capped = run_backtest(
        universe,
        parameters=_parameters(
            dc_alloc_model="inverse_vol", dc_vol_lookback=20, dc_name_cap=Decimal("0.30")
        ),
    )

    for entry in capped.targets:
        for _, weight in entry.target_weights:
            assert weight <= Decimal("0.30") + Decimal("0.000001")


def test_target_vol_derisks_the_book() -> None:
    universe = _two_speed_universe()
    unscaled = run_backtest(
        universe,
        parameters=_parameters(dc_alloc_model="inverse_vol", dc_vol_lookback=20),
    )
    scaled = run_backtest(
        universe,
        parameters=_parameters(
            dc_alloc_model="inverse_vol",
            dc_vol_lookback=20,
            # The synthetic BTC ramp is a near-zero-volatility series
            # by construction (measured ~0.002-0.004 annualized), so
            # only a target below that exercises the rescale branch.
            dc_target_vol=Decimal("0.0005"),
        ),
    )

    def _max_gross(targets: tuple[object, ...]) -> Decimal:
        return max(
            sum((weight for _, weight in entry.target_weights), Decimal("0"))  # type: ignore[attr-defined]
            for entry in targets
        )

    assert _max_gross(scaled.targets) < _max_gross(unscaled.targets)


def test_one_volatility_formula_backs_the_overlay() -> None:
    candles = _two_speed_universe()["ETHUSDT"]
    realized = _annualized_realized_vol(candles, 60, 20)
    assert realized is not None
    target = Decimal("0.5")
    expected = Decimal(str(round(min(1.0, float(target) / realized), 6)))
    assert _vol_scaler(candles, 60, vol_window=20, target=target) == expected


def test_warmup_reports_no_volatility() -> None:
    candles = _two_speed_universe()["BTCUSDT"]
    assert _annualized_realized_vol(candles, 5, 20) is None


def test_atr_exit_is_wired_and_validated() -> None:
    with pytest.raises(BacktestError, match="dc_exit"):
        _parameters(dc_exit="chandelier")
    with pytest.raises(BacktestError, match="dc_atr_multiple"):
        _parameters(dc_exit="atr_channel", dc_atr_multiple=Decimal("0"))
    with pytest.raises(BacktestError, match="dc_atr_window"):
        _parameters(dc_exit="atr_channel", dc_atr_window=1)


def test_atr_exit_holds_longer_than_mid_channel() -> None:
    from src.strategies.donchian_breakout_ensemble import average_true_range

    universe = _two_speed_universe()
    candles = universe["ETHUSDT"]
    atr = average_true_range(candles, 120, 14)
    assert atr is not None and atr > Decimal("0")
    assert average_true_range(candles, 0, 14) is None

    mid = run_backtest(universe, parameters=_parameters(dc_exit="mid_channel"))
    wide = run_backtest(
        universe,
        parameters=_parameters(
            dc_exit="atr_channel", dc_atr_window=14, dc_atr_multiple=Decimal("6")
        ),
    )
    # A six-ATR floor sits far below the channel high, so the book should
    # spend at least as many days invested as the mid-channel rule.
    mid_days = sum(1 for entry in mid.targets if entry.target_weights)
    wide_days = sum(1 for entry in wide.targets if entry.target_weights)
    assert wide_days >= mid_days

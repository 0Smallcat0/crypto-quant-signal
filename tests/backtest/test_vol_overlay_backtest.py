from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from src.backtest import run_backtest
from src.backtest.engine import _vol_scaler
from src.domain import Candle, Symbol
from tests.backtest.test_backtest_engine import (
    _candles_for,
    _parameters,
    _trend_and_crash_series,
)


def _universe() -> dict[str, tuple[Candle, ...]]:
    return {
        "BTCUSDT": _candles_for(
            Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
            _trend_and_crash_series(Decimal("1")),
        ),
        "ETHUSDT": _candles_for(
            Symbol(value="ETHUSDT", base_asset="ETH", quote_asset="USDT"),
            _trend_and_crash_series(Decimal("0.1")),
        ),
    }


def test_vol_scaler_warmup_and_flat_series_return_one() -> None:
    candles = _candles_for(
        Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        tuple([Decimal("100")] * 30),
    )

    # Not enough history before the index -> no scaling.
    assert _vol_scaler(candles, 5, vol_window=20, target=Decimal("0.5")) == Decimal("1")
    # Flat series has zero realized vol -> no scaling rather than divide-by-zero.
    assert _vol_scaler(candles, 25, vol_window=20, target=Decimal("0.5")) == Decimal("1")


def test_vol_scaler_shrinks_when_realized_vol_exceeds_target() -> None:
    # Alternating +/-5% daily moves: realized vol far above a 30% target.
    prices = [Decimal("100")]
    for index in range(30):
        prices.append(prices[-1] * (Decimal("1.05") if index % 2 == 0 else Decimal("0.95")))
    candles = _candles_for(
        Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"), tuple(prices)
    )

    scaler = _vol_scaler(candles, len(prices) - 1, vol_window=20, target=Decimal("0.30"))

    assert Decimal("0") < scaler < Decimal("0.5")


def test_high_target_reproduces_the_raw_backtest_bit_for_bit() -> None:
    universe = _universe()

    raw = run_backtest(universe, parameters=_parameters())
    scaled = run_backtest(
        universe,
        parameters=replace(_parameters(), vol_target_annualized=Decimal("99")),
    )

    # A target far above any realized vol must never bind.
    assert scaled.metrics.final_equity == raw.metrics.final_equity
    assert len(scaled.fills) == len(raw.fills)


def test_tight_target_cuts_exposure_and_shrinks_the_drawdown() -> None:
    universe = _universe()

    raw = run_backtest(universe, parameters=_parameters())
    scaled = run_backtest(
        universe,
        parameters=replace(
            _parameters(),
            vol_target_annualized=Decimal("0.10"),
            vol_window_days=20,
        ),
    )

    # Tight target -> smaller positions through the crash -> shallower
    # drawdown and a different equity path than raw.
    assert scaled.metrics.max_drawdown_fraction < raw.metrics.max_drawdown_fraction
    assert scaled.metrics.final_equity != raw.metrics.final_equity


def test_monthly_rebalance_freezes_the_scaler_within_a_month() -> None:
    universe = _universe()

    daily = run_backtest(
        universe,
        parameters=replace(
            _parameters(), vol_target_annualized=Decimal("0.10"), vol_rebalance="daily"
        ),
    )
    monthly = run_backtest(
        universe,
        parameters=replace(
            _parameters(), vol_target_annualized=Decimal("0.10"), vol_rebalance="monthly"
        ),
    )

    # Frozen-within-month sizing must genuinely differ from daily recompute.
    assert monthly.metrics.final_equity != daily.metrics.final_equity

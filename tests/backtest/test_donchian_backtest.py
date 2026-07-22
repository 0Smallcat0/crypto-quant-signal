"""Donchian breakout ensemble path (experiment 7 pre-registration)."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.backtest import BacktestError, BacktestParameters, run_backtest
from src.domain import Candle, Symbol, Timeframe
from src.strategies import evaluate_donchian_ensemble

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
        account_id="dc-test",
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


def test_dc_windows_must_be_exactly_four() -> None:
    with pytest.raises(BacktestError, match="exactly four"):
        _parameters(dc_windows=(10, 20, 55))


def test_dc_exit_must_be_known() -> None:
    with pytest.raises(BacktestError, match="dc_exit"):
        _parameters(dc_exit="nonsense")


def test_monotone_rise_turns_every_window_on() -> None:
    symbol = _symbol("BTCUSDT", "BTC")
    prices = [Decimal("100") + Decimal("2") * Decimal(i) for i in range(30)]
    candles = _candles_for(symbol, prices)

    fraction, codes, states = evaluate_donchian_ensemble(
        candles, 25, windows=(3, 5, 8, 13), exit_mode="half_low"
    )

    assert fraction == Decimal("1")
    assert states == (True, True, True, True)
    assert "WINDOWS_ON_4_OF_4" in codes


def test_breakdown_exits_after_the_rise() -> None:
    symbol = _symbol("BTCUSDT", "BTC")
    rise = [Decimal("100") + Decimal("5") * Decimal(i) for i in range(20)]
    fall = [rise[-1] - Decimal("8") * Decimal(i + 1) for i in range(9)]
    candles = _candles_for(symbol, rise + fall)

    states: tuple[bool, ...] | None = None
    fractions: list[Decimal] = []
    for index in range(14, len(candles)):
        fraction, _, states = evaluate_donchian_ensemble(
            candles, index, windows=(3, 5, 8, 13), exit_mode="half_low", previous_states=states
        )
        fractions.append(fraction)

    assert fractions[5] == Decimal("1")  # fully on during the rise
    assert fractions[-1] == Decimal("0")  # fully off after the breakdown


def test_engine_runs_the_donchian_ladder() -> None:
    days = 240
    universe = {
        "BTCUSDT": _candles_for(
            _symbol("BTCUSDT", "BTC"),
            [Decimal("100") + Decimal("2") * Decimal(i) for i in range(days)],
        ),
        "ETHUSDT": _candles_for(
            _symbol("ETHUSDT", "ETH"),
            [Decimal("50") + Decimal("1") * Decimal(i) for i in range(days)],
        ),
    }

    report = run_backtest(universe, parameters=_parameters())

    assert len(report.fills) > 0
    fractions = {entry.exposure_fraction for entry in report.signals}
    assert fractions <= {
        Decimal("0"),
        Decimal("0.25"),
        Decimal("0.5"),
        Decimal("0.75"),
        Decimal("1"),
    }
    assert report.metrics.final_equity > Decimal("10000")


def test_regime_gate_zeroes_the_book_in_a_bear_tape() -> None:
    days = 240
    universe = {
        "BTCUSDT": _candles_for(
            _symbol("BTCUSDT", "BTC"),
            [Decimal("500") - Decimal("1") * Decimal(i) for i in range(days)],
        ),
        "ETHUSDT": _candles_for(
            _symbol("ETHUSDT", "ETH"),
            [Decimal("50") + Decimal("1") * Decimal(i) for i in range(days)],
        ),
    }
    gated = run_backtest(
        universe,
        parameters=_parameters(
            cs_gate_sma_window=50, cs_gate_basis="btc", cs_gate_hysteresis=Decimal("0.02")
        ),
    )
    ungated = run_backtest(universe, parameters=_parameters())

    assert len(ungated.fills) > 0  # ETH breaks out even as BTC bleeds
    assert len(gated.fills) == 0  # BTC below its SMA gates the whole book

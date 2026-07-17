from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from src.backtest import BacktestParameters, run_backtest
from src.domain import Candle, Symbol
from tests.backtest.test_backtest_engine import _candles_for, _parameters


def _whipsaw_universe() -> dict[str, tuple[Candle, ...]]:
    """200 warmup days then alternating one-day spikes ending in a real trend.

    Raw ensemble ladders up on every spike day and back down the next; the
    confirmed variant should ignore every single-day spike and act once when
    the final three-day trend confirms.
    """

    spikes = (
        Decimal("150"),
        Decimal("90"),
        Decimal("150"),
        Decimal("90"),
        Decimal("150"),
        Decimal("90"),
        Decimal("150"),
        Decimal("150"),
        Decimal("151"),
        Decimal("152"),
    )
    prices = tuple([Decimal("100")] * 200) + spikes
    scaled = tuple(price * Decimal("0.1") for price in prices)
    return {
        "BTCUSDT": _candles_for(
            Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"), prices
        ),
        "ETHUSDT": _candles_for(
            Symbol(value="ETHUSDT", base_asset="ETH", quote_asset="USDT"), scaled
        ),
    }


def _confirmed_parameters() -> BacktestParameters:
    return replace(_parameters(), strategy_name="confirmed_trend_ensemble", confirm_days=2)


def test_confirmed_variant_trades_less_on_whipsaw_and_still_enters_trends() -> None:
    universe = _whipsaw_universe()

    raw = run_backtest(universe, parameters=_parameters())
    confirmed = run_backtest(universe, parameters=_confirmed_parameters())

    # The mechanism must actually fire: strictly fewer fills on whipsaw...
    assert len(confirmed.fills) < len(raw.fills)
    # ...while the confirmed three-day trend at the end still gets entered.
    assert confirmed.fills
    assert any("CONFIRMED_AFTER_2" in entry.reason_codes for entry in confirmed.signals)
    assert any("PENDING_CONFIRMATION_1_2" in entry.reason_codes for entry in confirmed.signals)


def test_default_parameters_still_run_the_original_ensemble() -> None:
    universe = _whipsaw_universe()

    raw = run_backtest(universe, parameters=_parameters())

    assert not any(
        "PENDING_CONFIRMATION" in code for entry in raw.signals for code in entry.reason_codes
    )

"""Alert-only candle sanity checks in the live paper-runtime script.

These guard the operator against a bad print from the single upstream source
becoming an executed command. They must stay alert-only: nothing here may
block or alter the decision path while the qualification run is live.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from scripts.run_paper_runtime import _candle_anomaly_lines
from src.domain import Candle, Symbol, Timeframe


def _candle(
    day: int,
    *,
    open_price: str,
    high_price: str,
    low_price: str,
    close_price: str,
) -> Candle:
    open_time = datetime(2026, 7, day, 0, 0, tzinfo=UTC)
    return Candle(
        symbol=Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        timeframe=Timeframe("1d"),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=Decimal(open_price),
        high_price=Decimal(high_price),
        low_price=Decimal(low_price),
        close_price=Decimal(close_price),
        volume=Decimal("100"),
        is_closed=True,
    )


def test_coherent_candles_produce_no_warnings() -> None:
    candles = (
        _candle(1, open_price="100", high_price="110", low_price="95", close_price="105"),
        _candle(2, open_price="105", high_price="120", low_price="100", close_price="118"),
    )

    assert _candle_anomaly_lines({"BTCUSDT": candles}) == []


def test_incoherent_ohlc_is_flagged() -> None:
    # high below low can leave the Binance parser unchallenged: the domain
    # type validates positivity only, not bracket coherence.
    candles = (_candle(1, open_price="100", high_price="90", low_price="110", close_price="100"),)

    lines = _candle_anomaly_lines({"BTCUSDT": candles})

    assert len(lines) == 1
    assert "OHLC" in lines[0]


def test_close_outside_high_low_bracket_is_flagged() -> None:
    candles = (_candle(1, open_price="100", high_price="104", low_price="98", close_price="105"),)

    lines = _candle_anomaly_lines({"BTCUSDT": candles})

    assert len(lines) == 1
    assert "OHLC" in lines[0]


def test_extreme_close_to_close_move_is_flagged() -> None:
    candles = (
        _candle(1, open_price="100", high_price="110", low_price="95", close_price="100"),
        _candle(2, open_price="100", high_price="160", low_price="99", close_price="150"),
    )

    lines = _candle_anomaly_lines({"BTCUSDT": candles})

    assert len(lines) == 1
    assert "50.0%" in lines[0]


def test_single_candle_history_skips_move_check() -> None:
    candles = (_candle(1, open_price="100", high_price="110", low_price="95", close_price="105"),)

    assert _candle_anomaly_lines({"BTCUSDT": candles}) == []

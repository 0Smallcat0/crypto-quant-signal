from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from src.domain import Candle, Symbol, Timeframe
from src.features import (
    FeaturePipelineConfig,
    FeaturePipelineValidationError,
    build_feature_snapshots,
)


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _timeframe() -> Timeframe:
    return Timeframe("15m")


def _candle(
    symbol: Symbol,
    index: int,
    *,
    close: str,
    volume: str = "10",
    is_closed: bool = True,
) -> Candle:
    open_time = datetime(2026, 5, 20, 0, 0, tzinfo=UTC) + timedelta(minutes=15 * index)
    close_price = Decimal(close)
    return Candle(
        symbol=symbol,
        timeframe=_timeframe(),
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15) - timedelta(milliseconds=1),
        open_price=close_price,
        high_price=close_price + Decimal("2"),
        low_price=close_price - Decimal("2"),
        close_price=close_price,
        volume=Decimal(volume),
        is_closed=is_closed,
    )


def _config() -> FeaturePipelineConfig:
    return FeaturePipelineConfig(
        momentum_lookback_candles=2,
        trend_lookback_candles=2,
        breakout_lookback_candles=2,
        volume_lookback_candles=2,
        volatility_lookback_candles=2,
    )


def test_feature_snapshot_contains_neutral_closed_candle_values_and_source_ranges() -> None:
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")
    eth_candles = (
        _candle(eth, 0, close="100", volume="10"),
        _candle(eth, 1, close="100", volume="20"),
        _candle(eth, 2, close="120", volume="60"),
    )
    btc_candles = (
        _candle(btc, 0, close="200", volume="10"),
        _candle(btc, 1, close="200", volume="10"),
        _candle(btc, 2, close="220", volume="20"),
    )

    (snapshot,) = build_feature_snapshots(
        eth_candles,
        btc_candles=btc_candles,
        config=_config(),
    )

    assert snapshot.symbol == eth
    assert snapshot.timeframe == _timeframe()
    assert snapshot.as_of == eth_candles[-1].close_time
    assert tuple(source.symbol.value for source in snapshot.source_ranges) == ("ETHUSDT", "BTCUSDT")
    assert snapshot.source_ranges[0].start_open_time == eth_candles[0].open_time
    assert snapshot.source_ranges[0].end_close_time == eth_candles[-1].close_time
    assert snapshot.values["momentum_return"] == Decimal("0.2")
    assert snapshot.values["recent_high_distance"] > Decimal("0")
    assert snapshot.values["volume_ratio"] == Decimal("4")
    assert snapshot.values["btc_momentum_return"] == Decimal("0.1")


def test_open_candles_are_rejected_before_feature_generation() -> None:
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")

    with pytest.raises(FeaturePipelineValidationError, match="OPEN_CANDLE"):
        build_feature_snapshots(
            (
                _candle(eth, 0, close="100"),
                _candle(eth, 1, close="100"),
                _candle(eth, 2, close="120", is_closed=False),
            ),
            btc_candles=(
                _candle(btc, 0, close="200"),
                _candle(btc, 1, close="200"),
                _candle(btc, 2, close="220"),
            ),
            config=_config(),
        )


def test_non_15m_candles_are_rejected() -> None:
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")
    eth_candles = (
        _candle(eth, 0, close="100"),
        _candle(eth, 1, close="100"),
        _candle(eth, 2, close="120"),
    )
    wrong_timeframe = tuple(
        Candle(
            symbol=candle.symbol,
            timeframe=Timeframe("1h"),
            open_time=candle.open_time,
            close_time=candle.close_time,
            open_price=candle.open_price,
            high_price=candle.high_price,
            low_price=candle.low_price,
            close_price=candle.close_price,
            volume=candle.volume,
            is_closed=candle.is_closed,
        )
        for candle in eth_candles
    )

    with pytest.raises(FeaturePipelineValidationError, match="15m"):
        build_feature_snapshots(
            wrong_timeframe,
            btc_candles=(
                _candle(btc, 0, close="200"),
                _candle(btc, 1, close="200"),
                _candle(btc, 2, close="220"),
            ),
            config=_config(),
        )


def test_future_primary_candles_do_not_change_earlier_feature_snapshots() -> None:
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")
    prefix = (
        _candle(eth, 0, close="100", volume="10"),
        _candle(eth, 1, close="100", volume="20"),
        _candle(eth, 2, close="120", volume="60"),
    )
    btc_candles = (
        _candle(btc, 0, close="200"),
        _candle(btc, 1, close="200"),
        _candle(btc, 2, close="220"),
        _candle(btc, 3, close="1000"),
    )

    baseline = build_feature_snapshots(prefix, btc_candles=btc_candles, config=_config())[0]
    with_future = build_feature_snapshots(
        (
            *prefix,
            _candle(eth, 3, close="9999", volume="9999"),
        ),
        btc_candles=btc_candles,
        config=_config(),
    )[0]

    assert with_future.as_of == baseline.as_of
    assert with_future.source_ranges == baseline.source_ranges
    assert with_future.values == baseline.values


def test_future_btc_candles_do_not_change_earlier_market_condition() -> None:
    eth = _symbol("ETHUSDT", "ETH")
    btc = _symbol("BTCUSDT", "BTC")
    eth_candles = (
        _candle(eth, 0, close="100"),
        _candle(eth, 1, close="100"),
        _candle(eth, 2, close="120"),
    )
    btc_prefix = (
        _candle(btc, 0, close="200"),
        _candle(btc, 1, close="200"),
        _candle(btc, 2, close="220"),
    )

    baseline = build_feature_snapshots(
        eth_candles,
        btc_candles=btc_prefix,
        config=_config(),
    )[0]
    with_future_btc = build_feature_snapshots(
        eth_candles,
        btc_candles=(
            *btc_prefix,
            _candle(btc, 3, close="10"),
        ),
        config=_config(),
    )[0]

    assert with_future_btc.values["btc_momentum_return"] == baseline.values["btc_momentum_return"]
    assert with_future_btc.source_ranges[1] == baseline.source_ranges[1]

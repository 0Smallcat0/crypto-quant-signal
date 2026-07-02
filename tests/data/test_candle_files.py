from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from src.data import (
    MarketDataValidationError,
    candle_file_name,
    read_candles_jsonl,
    write_candles_jsonl,
)
from src.domain import Candle, Symbol, Timeframe

_BASE_OPEN_TIME = datetime(2025, 6, 1, 0, 0, tzinfo=UTC)


def _candle(index: int, close: str = "100") -> Candle:
    open_time = _BASE_OPEN_TIME + timedelta(days=index)
    price = Decimal(close)
    return Candle(
        symbol=Symbol(value="BTCUSDT", base_asset="BTC", quote_asset="USDT"),
        timeframe=Timeframe("1d"),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=price,
        high_price=price + Decimal("5"),
        low_price=price - Decimal("5"),
        close_price=price,
        volume=Decimal("42.5"),
        is_closed=True,
    )


def test_candle_file_name_is_deterministic() -> None:
    assert candle_file_name("BTCUSDT", "1d") == "BTCUSDT_1d.jsonl"


def test_candles_round_trip_through_jsonl(tmp_path: Path) -> None:
    candles = tuple(_candle(index, close=str(100 + index)) for index in range(5))
    path = tmp_path / candle_file_name("BTCUSDT", "1d")

    write_candles_jsonl(candles, path)
    loaded = read_candles_jsonl(path)

    assert loaded == candles


def test_reading_missing_file_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(MarketDataValidationError, match="does not exist"):
        read_candles_jsonl(tmp_path / "missing.jsonl")


def test_corrupt_rows_fail_loudly(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"symbol": "BTCUSDT"}\n', encoding="utf-8")

    with pytest.raises(MarketDataValidationError, match="missing required"):
        read_candles_jsonl(path)


def test_mixed_symbols_cannot_be_written(tmp_path: Path) -> None:
    other = Candle(
        symbol=Symbol(value="ETHUSDT", base_asset="ETH", quote_asset="USDT"),
        timeframe=Timeframe("1d"),
        open_time=_BASE_OPEN_TIME + timedelta(days=1),
        close_time=_BASE_OPEN_TIME + timedelta(days=2) - timedelta(milliseconds=1),
        open_price=Decimal("10"),
        high_price=Decimal("11"),
        low_price=Decimal("9"),
        close_price=Decimal("10"),
        volume=Decimal("1"),
        is_closed=True,
    )

    with pytest.raises(MarketDataValidationError, match="one symbol"):
        write_candles_jsonl((_candle(0), other), tmp_path / "mixed.jsonl")

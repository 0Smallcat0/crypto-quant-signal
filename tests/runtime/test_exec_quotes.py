from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from src.data import BookTickerSnapshot
from src.domain import Symbol
from src.runtime import EXEC_QUOTE_KIND, JsonlEventStore, record_execution_quotes

_CLOSE_TIME = datetime(2026, 7, 2, 23, 59, 59, 999000, tzinfo=UTC)
_CAPTURED_AT = datetime(2026, 7, 3, 0, 5, 12, tzinfo=UTC)


def _symbol(value: str, base_asset: str) -> Symbol:
    return Symbol(value=value, base_asset=base_asset, quote_asset="USDT")


def _ticker(
    symbol: Symbol,
    bid: str,
    ask: str,
    *,
    captured_at: datetime = _CAPTURED_AT,
) -> BookTickerSnapshot:
    return BookTickerSnapshot(
        symbol=symbol,
        bid_price=Decimal(bid),
        bid_quantity=Decimal("2"),
        ask_price=Decimal(ask),
        ask_quantity=Decimal("3"),
        captured_at=captured_at,
    )


def test_records_one_quote_per_symbol_with_spread_bps(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")
    tickers = (
        _ticker(_symbol("BTCUSDT", "BTC"), "99.95", "100.05"),
        _ticker(_symbol("ETHUSDT", "ETH"), "1700.00", "1700.34"),
    )

    written = record_execution_quotes(store, tickers, close_time=_CLOSE_TIME)

    assert written == 2
    events = store.events_of_kind(EXEC_QUOTE_KIND)
    assert [event.key for event in events] == [
        "exec_quote:BTCUSDT:2026-07-02",
        "exec_quote:ETHUSDT:2026-07-02",
    ]
    btc = events[0].payload
    # bid 99.95 / ask 100.05 -> mid 100.00, spread 0.10 -> exactly 10 bps.
    assert btc["mid_price"] == "100.00"
    assert btc["spread_bps"] == "10.00"
    assert btc["bid_price"] == "99.95"
    assert btc["ask_price"] == "100.05"
    assert btc["trading_day"] == "2026-07-02"
    assert btc["close_time"] == _CLOSE_TIME.isoformat()
    assert btc["captured_at"] == _CAPTURED_AT.isoformat()
    assert events[0].recorded_at == _CAPTURED_AT


def test_same_day_rerun_is_a_dedup_noop(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")
    tickers = (_ticker(_symbol("BTCUSDT", "BTC"), "99.95", "100.05"),)

    assert record_execution_quotes(store, tickers, close_time=_CLOSE_TIME) == 1
    # Same decision day, fresher quote: the first snapshot must win.
    fresher = (_ticker(_symbol("BTCUSDT", "BTC"), "98.00", "98.10"),)
    assert record_execution_quotes(store, fresher, close_time=_CLOSE_TIME) == 0

    events = store.events_of_kind(EXEC_QUOTE_KIND)
    assert len(events) == 1
    assert events[0].payload["bid_price"] == "99.95"


def test_next_day_records_new_quote(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")
    tickers = (_ticker(_symbol("BTCUSDT", "BTC"), "99.95", "100.05"),)

    assert record_execution_quotes(store, tickers, close_time=_CLOSE_TIME) == 1
    next_close = datetime(2026, 7, 3, 23, 59, 59, 999000, tzinfo=UTC)
    assert record_execution_quotes(store, tickers, close_time=next_close) == 1
    assert store.count_of_kind(EXEC_QUOTE_KIND) == 2


def test_quotes_survive_store_reload_and_stay_invisible_to_other_kinds(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    store = JsonlEventStore(path)
    tickers = (_ticker(_symbol("ETHUSDT", "ETH"), "1700.00", "1700.34"),)
    record_execution_quotes(store, tickers, close_time=_CLOSE_TIME)

    # Proves the payload is JSON-round-trippable (Decimals stored as strings)
    # and that a restart replays the event without disturbing other kinds.
    reloaded = JsonlEventStore(path)
    events = reloaded.events_of_kind(EXEC_QUOTE_KIND)
    assert len(events) == 1
    assert events[0].payload["spread_bps"] == "2.00"
    assert reloaded.events_of_kind("notification") == ()
    assert reloaded.has("exec_quote:ETHUSDT:2026-07-02")

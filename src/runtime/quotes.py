"""Execution-window quote snapshots for gate 6 cost measurement.

Right after each live daily cycle — approximately when the user sees the
command — the runner captures the public best bid/ask (bookTicker) for every
decision symbol and persists it as an ``exec_quote`` event. Recording only
(AGENTS §8): these snapshots never feed decisions, fills, or notifications.
They exist so the Goal O gate can compare the 25-30bps round-trip cost
assumption against observed spreads without any private API.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from src.data import BookTickerSnapshot
from src.runtime.store import JsonlEventStore

EXEC_QUOTE_KIND = "exec_quote"

_BPS = Decimal("10000")
_BPS_PRECISION = Decimal("0.01")


def record_execution_quotes(
    store: JsonlEventStore,
    tickers: Iterable[BookTickerSnapshot],
    *,
    close_time: datetime,
) -> int:
    """Persist one ``exec_quote`` per symbol per decision day; return new rows.

    The idempotency key is (symbol, decision day), so a same-day rerun cannot
    double-record. Payload prices are strings, keeping the event JSON-safe and
    Decimal-exact like every other persisted money field.
    """

    trading_day = close_time.date().isoformat()
    written = 0
    for ticker in tickers:
        mid_price = (ticker.bid_price + ticker.ask_price) / 2
        spread_bps = (ticker.ask_price - ticker.bid_price) / mid_price * _BPS
        appended = store.append(
            kind=EXEC_QUOTE_KIND,
            key=f"{EXEC_QUOTE_KIND}:{ticker.symbol.value}:{trading_day}",
            recorded_at=ticker.captured_at,
            payload={
                "symbol": ticker.symbol.value,
                "trading_day": trading_day,
                "close_time": close_time.isoformat(),
                "bid_price": str(ticker.bid_price),
                "ask_price": str(ticker.ask_price),
                "bid_quantity": str(ticker.bid_quantity),
                "ask_quantity": str(ticker.ask_quantity),
                "mid_price": str(mid_price),
                "spread_bps": str(spread_bps.quantize(_BPS_PRECISION, rounding=ROUND_HALF_UP)),
                "captured_at": ticker.captured_at.isoformat(),
            },
        )
        if appended:
            written += 1
    return written

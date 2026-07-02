"""Replay driver: feed recorded closed daily candles through the runtime."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from src.domain import Candle
from src.runtime.engine import SignalRuntime
from src.runtime.types import CycleResult, RuntimeEngineError


@dataclass(frozen=True, slots=True)
class ReplaySummary:
    """Aggregated outcome of one recorded-candle replay."""

    cycles_processed: int
    cycles_skipped: int
    notifications: int
    fills: int
    rejections: int
    final_equity: Decimal | None


def run_replay(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    runtime: SignalRuntime,
) -> ReplaySummary:
    """Feed the recorded history one closed candle at a time."""

    if not candles_by_symbol:
        msg = "candles_by_symbol must not be empty"
        raise RuntimeEngineError(msg)
    lengths = {len(candles) for candles in candles_by_symbol.values()}
    if len(lengths) != 1:
        msg = "replay requires equal-length candle histories per symbol"
        raise RuntimeEngineError(msg)
    total_days = lengths.pop()

    ordered = {
        symbol_value: tuple(sorted(candles, key=lambda candle: candle.open_time))
        for symbol_value, candles in candles_by_symbol.items()
    }
    processed = 0
    skipped = 0
    notifications = 0
    fills = 0
    rejections = 0
    final_equity: Decimal | None = None
    for day_index in range(total_days):
        window = {
            symbol_value: candles[: day_index + 1] for symbol_value, candles in ordered.items()
        }
        result: CycleResult = runtime.process_closed_candles(window)
        if result.processed:
            processed += 1
            notifications += len(result.notifications)
            fills += len(result.fills)
            rejections += len(result.rejection_reason_codes)
            final_equity = result.equity
        else:
            skipped += 1
    return ReplaySummary(
        cycles_processed=processed,
        cycles_skipped=skipped,
        notifications=notifications,
        fills=fills,
        rejections=rejections,
        final_equity=final_equity,
    )

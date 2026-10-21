"""The live cycle fetches enough closed bars to clear the strategy's warmup."""

from __future__ import annotations

from scripts.run_paper_runtime import _LIVE_FETCH_LIMIT
from src.features import DAILY_TREND_WARMUP_CANDLES
from src.runtime import DONCHIAN_WARMUP_CANDLES


def test_live_fetch_clears_warmup_after_the_open_bar_is_dropped() -> None:
    # Binance counts today's still-open bar and closed_only drops it. A fetch
    # of exactly the warmup floor stopped every live cycle at WARMUP.
    closed_bars = _LIVE_FETCH_LIMIT - 1
    assert closed_bars >= DONCHIAN_WARMUP_CANDLES
    assert closed_bars >= DAILY_TREND_WARMUP_CANDLES

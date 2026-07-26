"""How concentrated is the benchmark's return across the universe?

Zero-cost diagnostic over local candle files: no backtest, no registry row.

Motivation. Experiment 8 (13 symbols) beat buy-and-hold in 0 of 8
configurations while experiment 7 (BTC/ETH) beat it in 8 of 8. Neither the
ratio nor the absolute return explains why. This measures the thing that
does: how much of the equal-weight benchmark's return sits in a handful of
names.

A trend rule that exits on weakness necessarily trims its biggest winners.
Where a universe's return is concentrated in two or three names, trimming
them is fatal relative to simply holding, and no parameter choice repairs
it. Where returns are evenly spread and drawdowns are severe, avoiding the
drawdowns can win.

Usage:
    python -m scripts.analyze_symbol_dispersion
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_CANDLES = Path("data/candles")
_START = date(2018, 3, 6)
_END = date(2025, 7, 1)


@dataclass(frozen=True, slots=True)
class SymbolStats:
    symbol: str
    listed: date
    bars: int
    multiple: float
    max_drawdown: float


def symbol_stats(path: Path, *, start: date, end: date) -> SymbolStats | None:
    """Buy-and-hold multiple and worst drawdown inside the window."""

    closes: list[tuple[date, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        candle = json.loads(line)
        day = date.fromisoformat(str(candle["close_time"])[:10])
        if start <= day <= end:
            closes.append((day, float(candle["close"])))
    if len(closes) < 2:
        return None
    closes.sort()

    equity = peak = 1.0
    worst = 0.0
    previous = closes[0][1]
    for _, value in closes[1:]:
        if previous > 0:
            equity *= value / previous
        previous = value
        peak = max(peak, equity)
        worst = max(worst, 1.0 - equity / peak)
    return SymbolStats(
        symbol=path.name.split("_")[0],
        listed=closes[0][0],
        bars=len(closes),
        multiple=closes[-1][1] / closes[0][1],
        max_drawdown=worst,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candles-dir", default=str(_CANDLES))
    parser.add_argument("--start", default=_START.isoformat())
    parser.add_argument("--end", default=_END.isoformat())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    rows = [
        stats
        for path in sorted(Path(args.candles_dir).glob("*_1d.jsonl"))
        if (stats := symbol_stats(path, start=start, end=end)) is not None
    ]
    if not rows:
        print("no candle files in window")
        return
    rows.sort(key=lambda item: -item.multiple)

    print(f"window {start.isoformat()} -> {end.isoformat()}  symbols={len(rows)}")
    print(f"\n{'symbol':10s}{'listed':>12}{'bars':>7}{'buy-hold':>11}{'mdd':>9}")
    for row in rows:
        print(
            f"{row.symbol:10s}{row.listed.isoformat():>12}{row.bars:7d}"
            f"{row.multiple:11.2f}{row.max_drawdown:9.2%}"
        )

    multiples = [row.multiple for row in rows]
    total = sum(multiples)
    print(f"\nmean {statistics.fmean(multiples):.2f}   median {statistics.median(multiples):.2f}")
    print(f"mildest drawdown of any name: {min(row.max_drawdown for row in rows):.2%}")
    for count in (1, 2, 3):
        share = sum(multiples[:count]) / total
        names = ", ".join(f"{row.symbol} {row.multiple:.1f}x" for row in rows[:count])
        print(f"top {count}: {share:6.1%} of summed return  ({names})")
    losers = [row.symbol for row in rows if row.multiple < 1.0]
    print(f"names that lost money holding: {len(losers)} ({', '.join(losers) or 'none'})")


if __name__ == "__main__":
    main()

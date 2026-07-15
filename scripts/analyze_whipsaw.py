"""Whipsaw diagnostic (P2-10): turning-point months vs published thresholds.

Implements the Goulding, Harvey & Mazzoleni ("Breaking Bad Trends", FAJ 2024)
turning-point definition on our own decision universe: a month whose FAST
momentum sign (1-month, and separately 2-month) disagrees with the SLOW
12-month momentum sign, sampled at month-end closes. Their cross-asset result:
years with >= 6 turning-point months have negative median static-trend
returns; >= 8 pushes median Sharpe below -1.25.

Measurement only (pre-registered diagnostic, plan P2-10): this script never
touches strategy code, parameters, or the runtime. Its output decides research
PRIORITY — whether hysteresis/confirmation experiments lead Goal P, or whether
the whipsaw budget is acceptable and effort goes to compliance measurement.

Both fast definitions are reported side by side because the paper blends
1-2 month momentum; picking one silently would be a researcher degree of
freedom, which is exactly what this repository exists to refuse.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.data import candle_file_name, read_candles_jsonl

YEARLY_WARNING_THRESHOLD = 6  # >= 6 TP months/yr: median static-trend return < 0
YEARLY_SEVERE_THRESHOLD = 8  # >= 8 TP months/yr: median Sharpe < -1.25

_SLOW_MONTHS = 12


def month_end_closes(
    closes_by_day: dict[date, Decimal],
) -> dict[tuple[int, int], Decimal]:
    """Last available daily close per COMPLETE month, keyed by (year, month).

    The trailing partial month is dropped: a mid-month "month-end" close is
    not the statistic the thresholds were computed on.
    """

    last_day_seen: dict[tuple[int, int], date] = {}
    for day in closes_by_day:
        key = (day.year, day.month)
        if key not in last_day_seen or day > last_day_seen[key]:
            last_day_seen[key] = day
    ordered = sorted(last_day_seen)
    if not ordered:
        return {}
    complete = ordered[:-1]
    final_key = ordered[-1]
    final_day = last_day_seen[final_key]
    next_day = date(
        final_day.year + (final_day.month == 12),
        final_day.month % 12 + 1,
        1,
    )
    # The final month counts only if its last candle is the true month end.
    if (next_day - final_day).days == 1:
        complete = ordered
    return {key: closes_by_day[last_day_seen[key]] for key in complete}


def turning_point_months(
    monthly_closes: dict[tuple[int, int], Decimal],
    *,
    fast_months: int,
) -> list[tuple[int, int]]:
    """Months where sign(fast momentum) != sign(slow 12M momentum).

    Zero momentum on either leg is treated as agreement (no turning point):
    the paper's turning points are sign FLIPS, and a flat leg has no sign.
    """

    keys = sorted(monthly_closes)
    points: list[tuple[int, int]] = []
    for index in range(_SLOW_MONTHS, len(keys)):
        now = monthly_closes[keys[index]]
        slow_base = monthly_closes[keys[index - _SLOW_MONTHS]]
        fast_base = monthly_closes[keys[index - fast_months]]
        slow = now - slow_base
        fast = now - fast_base
        if slow == 0 or fast == 0:
            continue
        if (slow > 0) != (fast > 0):
            points.append(keys[index])
    return points


def yearly_counts(points: list[tuple[int, int]]) -> dict[int, int]:
    counts: dict[int, int] = defaultdict(int)
    for year, _month in points:
        counts[year] += 1
    return dict(counts)


def analyze_symbol(candles_dir: Path, symbol_value: str, timeframe: str) -> dict[str, object]:
    candles = read_candles_jsonl(candles_dir / candle_file_name(symbol_value, timeframe))
    closes_by_day = {candle.close_time.date(): candle.close_price for candle in candles}
    monthly = month_end_closes(closes_by_day)
    result: dict[str, object] = {
        "symbol": symbol_value,
        "months_evaluated": max(len(monthly) - _SLOW_MONTHS, 0),
        "first_month": "-".join(map(str, min(monthly))) if monthly else None,
        "last_month": "-".join(map(str, max(monthly))) if monthly else None,
    }
    for fast_months in (1, 2):
        points = turning_point_months(monthly, fast_months=fast_months)
        by_year = yearly_counts(points)
        result[f"fast_{fast_months}m"] = {
            "turning_point_months_total": len(points),
            "by_year": {str(year): count for year, count in sorted(by_year.items())},
            "years_at_warning_6": sorted(
                year for year, count in by_year.items() if count >= YEARLY_WARNING_THRESHOLD
            ),
            "years_at_severe_8": sorted(
                year for year, count in by_year.items() if count >= YEARLY_SEVERE_THRESHOLD
            ),
        }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candles-dir", default="data/candles")
    parser.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT"])
    parser.add_argument("--timeframe", default="1d")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = [
        analyze_symbol(Path(args.candles_dir), symbol_value, args.timeframe)
        for symbol_value in args.symbols
    ]
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

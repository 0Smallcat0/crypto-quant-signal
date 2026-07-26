"""How much of the three-sleeve book is sitting in cash, and when.

Zero-cost diagnostic over already-registered reports: no backtest, no
registry row, no pre-registration needed. It measures the reports' own
`targets[].cash_weight`, which is what each sleeve actually left undeployed
on each decision day.

The question it answers: the three-sleeve book bought a 14.90% drawdown
instead of 19.73% by giving up terminal wealth (6.00x -> 3.94x). Part of
that cost is diversification and cannot be avoided. Part of it is capital
that no sleeve was using at all — a third of the book idle because gold
happened to be flat. Only the second part is potentially recoverable
without leverage, and this measures how big it is.

Usage:
    python -m scripts.analyze_idle_capital
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

_CRYPTO_REPORT = Path("docs/reports/backtests/trial-000088/report.json")
_TW_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json")
_GOLD_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json")


def deployed_by_date(path: Path) -> dict[date, float]:
    """Fraction of the sleeve's own capital that was in the market."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    report = payload.get("report", payload)
    out: dict[date, float] = {}
    for target in report["targets"]:
        day = date.fromisoformat(str(target["as_of"])[:10])
        out[day] = 1.0 - float(target["cash_weight"])
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crypto-report", default=str(_CRYPTO_REPORT))
    parser.add_argument("--tw-report", default=str(_TW_REPORT))
    parser.add_argument("--gold-report", default=str(_GOLD_REPORT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sleeves = {
        "crypto (trial 88)": deployed_by_date(Path(args.crypto_report)),
        "taiwan (trial 23)": deployed_by_date(Path(args.tw_report)),
        "gold   (trial 24)": deployed_by_date(Path(args.gold_report)),
    }

    start = max(min(series) for series in sleeves.values())
    end = min(max(series) for series in sleeves.values())
    days = sorted({day for series in sleeves.values() for day in series if start <= day <= end})
    print(f"common decision window {start.isoformat()} -> {end.isoformat()}  days={len(days)}")

    # A sleeve with no decision on a given day is closed, which is the same
    # thing as deployed 0 for the purpose of asking what the book is holding.
    print(f"\n{'sleeve':20s}{'mean deployed':>15}{'days fully flat':>18}")
    per_day: dict[str, list[float]] = {}
    for name, series in sleeves.items():
        values = [series.get(day, 0.0) for day in days]
        per_day[name] = values
        flat = sum(1 for value in values if value == 0.0)
        print(f"{name:20s}{statistics.fmean(values):15.4f}{flat / len(values):17.1%}")

    book = [
        statistics.fmean([per_day[name][index] for name in sleeves]) for index in range(len(days))
    ]
    print(f"\nthree-sleeve book mean gross exposure: {statistics.fmean(book):.4f}")
    print(f"three-sleeve book mean cash:          {1.0 - statistics.fmean(book):.4f}")

    counts = Counter(
        sum(1 for name in sleeves if per_day[name][index] > 0.0) for index in range(len(days))
    )
    print(f"\n{'sleeves long at once':24s}{'days':>8}{'share':>9}")
    for count in sorted(counts):
        print(f"{count:<24d}{counts[count]:8d}{counts[count] / len(days):9.1%}")


if __name__ == "__main__":
    main()

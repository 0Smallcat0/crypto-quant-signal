"""Does any of this beat simply holding the assets?

Zero-cost diagnostic over already-registered reports: no backtest, no
registry row. Every report already carries a `benchmark_equity` series —
buy-and-hold of the same universe over the same window — and no document in
this program has yet put the two side by side on the combination's common
window.

That is the question the whole program answers to. A trend book that
underperforms holding the assets, at any Sharpe, has not made money; it has
bought a smoother path to a smaller number, and that trade has to be checked
against the simplest possible alternative rather than against other trend
books.

Usage:
    python -m scripts.analyze_vs_buy_and_hold
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from scripts.analyze_sleeve_combination import (
    combine_monthly_rebalanced,
    common_window,
    daily_returns,
    max_drawdown,
    sharpe,
    total_multiple,
)

_REPORTS = {
    "crypto": Path("docs/reports/backtests/trial-000088/report.json"),
    "taiwan": Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json"),
    "gold": Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json"),
}


def benchmark_returns(path: Path) -> dict[date, float]:
    """Per-date buy-and-hold returns from a report's benchmark series."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    report = payload.get("report", payload)
    out: dict[date, float] = {}
    previous: float | None = None
    for point in report["equity_curve"]:
        day = date.fromisoformat(str(point["close_time"])[:10])
        equity = float(point["benchmark_equity"])
        if previous is not None and previous > 0:
            out[day] = equity / previous - 1.0
        previous = equity
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crypto-report", default=str(_REPORTS["crypto"]))
    parser.add_argument("--tw-report", default=str(_REPORTS["taiwan"]))
    parser.add_argument("--gold-report", default=str(_REPORTS["gold"]))
    return parser.parse_args()


def _print_table(title: str, books: dict[str, list[float]]) -> None:
    print(f"\n{title}")
    print(f"{'book':30s}{'sharpe':>9}{'mdd':>9}{'multiple':>10}")
    for name, series in books.items():
        print(
            f"{name:30s}{sharpe(series):9.4f}"
            f"{max_drawdown(series):9.4f}{total_multiple(series):10.2f}"
        )


def main() -> None:
    args = parse_args()
    paths = {
        "crypto": Path(args.crypto_report),
        "taiwan": Path(args.tw_report),
        "gold": Path(args.gold_report),
    }
    system = {name: daily_returns(path) for name, path in paths.items()}
    hold = {name: benchmark_returns(path) for name, path in paths.items()}

    # Each sleeve on its own full window first: that is where the honest
    # per-market verdict lives, and two of them have long histories.
    header = f"{'system':>10}{'buy-hold':>10}{'sys mdd':>10}{'bh mdd':>9}"
    print(f"{'sleeve (own full window)':38s}{header}")
    for name in paths:
        own = sorted(system[name])
        sys_series = [system[name][day] for day in own]
        bh_series = [hold[name].get(day, 0.0) for day in own]
        label = f"{name} {own[0].isoformat()}..{own[-1].isoformat()}"
        print(
            f"{label:38s}{total_multiple(sys_series):10.2f}{total_multiple(bh_series):10.2f}"
            f"{max_drawdown(sys_series):10.4f}{max_drawdown(bh_series):9.4f}"
        )

    days = common_window(list(system.values()))
    print(f"\ncommon window {days[0].isoformat()} -> {days[-1].isoformat()}  days={len(days)}")

    sleeves: dict[str, list[float]] = {}
    for name in paths:
        sleeves[f"{name} system"] = [system[name].get(day, 0.0) for day in days]
        sleeves[f"{name} buy-and-hold"] = [hold[name].get(day, 0.0) for day in days]
    _print_table("per sleeve, common window", sleeves)

    books = {
        "1/3 each, systems": combine_monthly_rebalanced(days, [system[n] for n in paths]),
        "1/3 each, buy-and-hold": combine_monthly_rebalanced(days, [hold[n] for n in paths]),
        "crypto system alone": [system["crypto"].get(day, 0.0) for day in days],
        "crypto buy-and-hold alone": [hold["crypto"].get(day, 0.0) for day in days],
    }
    _print_table("books, common window", books)

    systems = books["1/3 each, systems"]
    holds = books["1/3 each, buy-and-hold"]
    print("\nthree-sleeve system vs the same three markets simply held:")
    print(f"  return  : {total_multiple(systems):.2f}x vs {total_multiple(holds):.2f}x")
    print(f"  drawdown: {max_drawdown(systems):.2%} vs {max_drawdown(holds):.2%}")
    print(f"  sharpe  : {sharpe(systems):.4f} vs {sharpe(holds):.4f}")


if __name__ == "__main__":
    main()

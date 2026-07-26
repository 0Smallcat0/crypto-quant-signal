"""Does the timing rule add anything, once exposure is controlled for?

Zero-cost diagnostic over already-registered reports. No backtest, no
registry row.

The problem it fixes. "Beat buy-and-hold" is confounded: a system is
compared against a fully-invested benchmark while itself being invested
only part of the time, so the verdict depends on how strong that market
happened to be. Experiment 8 lost that comparison purely because its
universe rose 13.53x rather than 6.05x
(`REGISTRY_VS_BENCHMARK_2026-07-26.md`, retraction box).

The control. For each book, build a passive twin holding the SAME asset at
the system's own **average gross exposure**, continuously — no timing, no
signal, same time-in-market. If the system beats its twin, the timing
decisions added value. If it does not, the system is an expensive way to be
partially invested, and a static fraction would do the same job.

The twin is deliberately generous: it pays no trading costs even though
maintaining a constant exposure requires daily rebalancing, while the
system pays full costs. Every edge reported here is therefore conservative
for the system.

Usage:
    python -m scripts.analyze_timing_value
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

_DAYS_PER_YEAR = 365

# Declared in analyze_sleeve_combination.print_stress before this test
# existed; reused verbatim so the split cannot be chosen to flatter.
_WINDOWS = (
    ("2020 covid crash", date(2020, 2, 1), date(2020, 4, 1)),
    ("2022 bear year", date(2022, 1, 1), date(2022, 12, 31)),
    ("2018-2019", date(2018, 3, 6), date(2019, 12, 31)),
    ("2023-2025H1", date(2023, 1, 1), date(2025, 7, 1)),
)

_BOOKS = (
    ("crypto trial 88 (2 sym)", "docs/reports/backtests/trial-000088/report.json"),
    ("crypto trial 94 (13 sym)", "docs/reports/backtests/trial-000094/report.json"),
    ("taiwan trial 23", "D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json"),
    ("gold trial 24", "D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json"),
)


@dataclass(frozen=True, slots=True)
class Curve:
    sharpe: float
    max_drawdown: float
    multiple: float


def _returns(curve: list[Any], field: str) -> list[float]:
    out: list[float] = []
    previous: float | None = None
    for point in curve:
        value = float(str(point[field]))
        if previous is not None and previous > 0:
            out.append(value / previous - 1.0)
        previous = value
    return out


def summarize(returns: list[float]) -> Curve:
    equity = peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = max(worst, 1.0 - equity / peak)
    deviation = statistics.stdev(returns) if len(returns) > 1 else 0.0
    sharpe = (
        statistics.fmean(returns) / deviation * math.sqrt(_DAYS_PER_YEAR) if deviation > 0 else 0.0
    )
    return Curve(sharpe=sharpe, max_drawdown=worst, multiple=equity)


def mean_exposure(targets: list[Any]) -> float:
    """Average fraction of the book actually in the market."""

    return statistics.fmean(1.0 - float(str(target["cash_weight"])) for target in targets)


def print_subperiods(label: str, report: dict[str, Any], weight: float) -> None:
    """Is the timing edge one effect, or two crashes it happened to sit out?

    The windows are the four already declared in
    `analyze_sleeve_combination.print_stress`, not chosen here — an edge
    that lives entirely in 2018 and 2022 is "it avoided two crashes", a much
    weaker claim than "timing works".
    """

    stamped = [
        (date.fromisoformat(str(point["close_time"])[:10]), point)
        for point in report["equity_curve"]
    ]
    print(f"\n{label} by sub-period")
    print(f"{'window':22s}{'n':>6}{'system':>9}{'twin':>9}{'edge':>8}")
    for name, start, end in _WINDOWS:
        picked = [point for day, point in stamped if start <= day <= end]
        if len(picked) < 3:
            continue
        system = summarize(_returns(picked, "equity"))
        twin = summarize([weight * value for value in _returns(picked, "benchmark_equity")])
        edge = system.multiple / twin.multiple if twin.multiple > 0 else 0.0
        print(f"{name:22s}{len(picked):6d}{system.multiple:9.3f}{twin.multiple:9.3f}{edge:8.2f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="append", dest="reports", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    books = tuple((path, path) for path in args.reports) if args.reports else _BOOKS

    header = f"{'system':>9}{'twin':>9}{'edge':>8}{'sys mdd':>10}{'twin mdd':>10}{'sys sharpe':>12}"
    print(f"{'book':26s}{'expo':>7}{header}")
    for label, path in books:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        report = payload.get("report", payload)
        weight = mean_exposure(report["targets"])
        curve = report["equity_curve"]
        system = summarize(_returns(curve, "equity"))
        twin = summarize([weight * value for value in _returns(curve, "benchmark_equity")])
        edge = system.multiple / twin.multiple if twin.multiple > 0 else 0.0
        print(
            f"{label:26s}{weight:7.3f}{system.multiple:9.2f}{twin.multiple:9.2f}{edge:8.2f}"
            f"{system.max_drawdown:10.2%}{twin.max_drawdown:10.2%}{system.sharpe:12.4f}"
        )

    # Only the crypto books have a positive whole-window edge, so they are
    # the ones worth asking whether that edge is one effect or two crashes.
    for label, path in books[:2]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        report = payload.get("report", payload)
        print_subperiods(label, report, mean_exposure(report["targets"]))

    print(
        "\nedge > 1: timing beat holding the same asset for the same fraction of the time."
        "\nedge ~ 1: the signal machinery is equivalent to a static partial position."
        "\nedge < 1: timing destroyed value; a static fraction would have done better."
        "\nThe twin pays no trading costs, so every edge above is conservative."
    )


if __name__ == "__main__":
    main()

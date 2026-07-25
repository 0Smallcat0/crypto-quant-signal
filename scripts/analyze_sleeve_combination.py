"""N-sleeve combination analysis (SLEEVE3_GOLD_PREREGISTRATION.md).

Generalizes `analyze_crossmarket_combination.py` from two sleeves to any
number. That script is left untouched: it is the artifact that produced the
published two-sleeve result, and changing it would make that result
irreproducible.

Reads already-registered trial reports, builds a daily-aligned equal-weight
book rebalanced monthly, and evaluates the pre-declared criteria. Runs no
backtest and registers no trial.

Alignment: each sleeve returns on the days its own market trades and
contributes exactly 0 otherwise, which is what a held position in a closed
market does. Padding with zeros is not a distortion of the annualization —
it scales the mean by the traded fraction and the deviation by its square
root, which cancel exactly.

The two-sleeve comparison is recomputed on the three-way common window
rather than quoted from the two-sleeve result document, because that
document's window is longer and the numbers are not comparable across
different windows.

Usage:
    python -m scripts.analyze_sleeve_combination
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections.abc import Sequence
from datetime import date
from pathlib import Path

_DAYS_PER_YEAR = 365
_CRYPTO_REPORT = Path("docs/reports/backtests/trial-000088/report.json")
_TW_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json")
_GOLD_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json")

_INDEPENDENCE_LIMIT = 0.30


def daily_returns(path: Path) -> dict[date, float]:
    """Per-date returns from a report's equity curve."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    report = payload.get("report", payload)
    out: dict[date, float] = {}
    previous: float | None = None
    for point in report["equity_curve"]:
        day = date.fromisoformat(str(point["close_time"])[:10])
        equity = float(point["equity"])
        if previous is not None and previous > 0:
            out[day] = equity / previous - 1.0
        previous = equity
    return out


def sharpe(returns: Sequence[float]) -> float:
    if len(returns) < 2:
        return 0.0
    stdev = statistics.stdev(returns)
    return statistics.fmean(returns) / stdev * math.sqrt(_DAYS_PER_YEAR) if stdev > 0 else 0.0


def max_drawdown(returns: Sequence[float]) -> float:
    equity = peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = max(worst, 1.0 - equity / peak)
    return worst


def total_multiple(returns: Sequence[float]) -> float:
    equity = 1.0
    for value in returns:
        equity *= 1.0 + value
    return equity


def combine_monthly_rebalanced(
    days: Sequence[date], sleeves: Sequence[dict[date, float]]
) -> list[float]:
    """Equal weights restored at each month boundary, drifting in between.

    Rebalancing monthly rather than daily is the realistic version: a
    daily-rebalanced book would trade every sleeve every session for no
    economic reason.
    """

    count = len(sleeves)
    weight = 1.0 / count
    holdings = [weight] * count
    month = (days[0].year, days[0].month)
    combined: list[float] = []
    for day in days:
        if (day.year, day.month) != month:
            month = (day.year, day.month)
            total = sum(holdings)
            holdings = [total * weight] * count
        before = sum(holdings)
        holdings = [
            value * (1.0 + sleeve.get(day, 0.0))
            for value, sleeve in zip(holdings, sleeves, strict=True)
        ]
        after = sum(holdings)
        combined.append(after / before - 1.0 if before > 0 else 0.0)
    return combined


def common_window(sleeves: Sequence[dict[date, float]]) -> list[date]:
    start = max(min(sleeve) for sleeve in sleeves)
    end = min(max(sleeve) for sleeve in sleeves)
    seen: set[date] = set()
    for sleeve in sleeves:
        seen |= {day for day in sleeve if start <= day <= end}
    return sorted(seen)


def _row(name: str, series: Sequence[float]) -> tuple[str, float, float, float]:
    return name, sharpe(series), max_drawdown(series), total_multiple(series)


def _worst_fraction_index(series: Sequence[float], fraction: float) -> list[int]:
    """Positions of the worst ``fraction`` of days in ``series``."""

    count = max(2, int(len(series) * fraction))
    return sorted(range(len(series)), key=lambda index: series[index])[:count]


def print_stress(days: Sequence[date], series: dict[str, list[float]]) -> None:
    """Does the independence survive the days that actually hurt?

    A diversification claim that only holds in calm markets is worthless,
    since the drawdown it is supposed to cut happens in the other kind.
    """

    crypto = series["crypto sleeve (trial 88)"]
    print(f"\n{'condition':26s}{'n':>6}{'corr(gold,crypto)':>20}{'crypto':>10}{'gold':>9}{'tw':>9}")
    for label, fraction in (("crypto worst 5%", 0.05), ("crypto worst 10%", 0.10)):
        picked = _worst_fraction_index(crypto, fraction)
        left = [crypto[index] for index in picked]
        gold = [series["gold sleeve (trial 24)"][index] for index in picked]
        taiwan = [series["taiwan sleeve (trial 23)"][index] for index in picked]
        print(
            f"{label:26s}{len(picked):6d}{statistics.correlation(gold, left):+20.4f}"
            f"{statistics.fmean(left):+10.2%}{statistics.fmean(gold):+9.2%}"
            f"{statistics.fmean(taiwan):+9.2%}"
        )

    windows = (
        ("2020 covid crash", date(2020, 2, 1), date(2020, 4, 1)),
        ("2022 bear year", date(2022, 1, 1), date(2022, 12, 31)),
        ("2018-2019", date(2018, 3, 6), date(2019, 12, 31)),
        ("2023-2025H1", date(2023, 1, 1), date(2025, 7, 1)),
    )
    columns = f"{'2-sleeve mdd':>14}{'3-sleeve mdd':>14}{'3-sleeve sharpe':>17}"
    print(f"\n{'window':22s}{'n':>6}{columns}")
    for label, start, end in windows:
        picked = [index for index, day in enumerate(days) if start <= day <= end]
        if len(picked) < 2:
            continue
        sub_days = [days[index] for index in picked]
        sleeves = {
            name: {sub_days[position]: values[index] for position, index in enumerate(picked)}
            for name, values in series.items()
        }
        two = combine_monthly_rebalanced(
            sub_days, [sleeves["crypto sleeve (trial 88)"], sleeves["taiwan sleeve (trial 23)"]]
        )
        three = combine_monthly_rebalanced(sub_days, list(sleeves.values()))
        print(
            f"{label:22s}{len(picked):6d}{max_drawdown(two):14.4f}"
            f"{max_drawdown(three):14.4f}{sharpe(three):17.4f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crypto-report", default=str(_CRYPTO_REPORT))
    parser.add_argument("--tw-report", default=str(_TW_REPORT))
    parser.add_argument("--gold-report", default=str(_GOLD_REPORT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crypto = daily_returns(Path(args.crypto_report))
    taiwan = daily_returns(Path(args.tw_report))
    gold = daily_returns(Path(args.gold_report))

    gold_own = sorted(gold)
    gold_own_series = [gold[day] for day in gold_own]
    print(
        f"gold sleeve own window {gold_own[0].isoformat()} -> {gold_own[-1].isoformat()}  "
        f"sessions={len(gold_own)}  sharpe={sharpe(gold_own_series):.4f}  "
        f"mdd={max_drawdown(gold_own_series):.4f}  "
        f"multiple={total_multiple(gold_own_series):.2f}"
    )

    days = common_window([crypto, taiwan, gold])
    series = {
        "crypto sleeve (trial 88)": [crypto.get(day, 0.0) for day in days],
        "taiwan sleeve (trial 23)": [taiwan.get(day, 0.0) for day in days],
        "gold sleeve (trial 24)": [gold.get(day, 0.0) for day in days],
    }
    two_way = combine_monthly_rebalanced(days, [crypto, taiwan])
    three_way = combine_monthly_rebalanced(days, [crypto, taiwan, gold])

    print(f"\ncommon window {days[0].isoformat()} -> {days[-1].isoformat()}  days={len(days)}")
    for label, left, right in (
        ("gold vs crypto", "gold sleeve (trial 24)", "crypto sleeve (trial 88)"),
        ("gold vs taiwan", "gold sleeve (trial 24)", "taiwan sleeve (trial 23)"),
        ("crypto vs taiwan", "crypto sleeve (trial 88)", "taiwan sleeve (trial 23)"),
    ):
        value = statistics.correlation(series[left], series[right])
        print(f"daily correlation {label:18s} {value:+.4f}")

    rows = [_row(name, values) for name, values in series.items()]
    rows.append(_row("50/50 crypto+taiwan", two_way))
    rows.append(_row("1/3 each, three sleeves", three_way))
    print(f"\n{'book':28s}{'sharpe':>9}{'mdd':>9}{'multiple':>10}")
    for name, book_sharpe, book_mdd, book_multiple in rows:
        print(f"{name:28s}{book_sharpe:9.4f}{book_mdd:9.4f}{book_multiple:10.2f}")

    gold_common = series["gold sleeve (trial 24)"]
    checks = {
        "1 gold sleeve positive, own window and common": (
            sharpe(gold_own_series) > 0 and sharpe(gold_common) > 0
        ),
        "2 gold independent of both (|corr| < 0.30)": (
            abs(statistics.correlation(gold_common, series["crypto sleeve (trial 88)"]))
            < _INDEPENDENCE_LIMIT
            and abs(statistics.correlation(gold_common, series["taiwan sleeve (trial 23)"]))
            < _INDEPENDENCE_LIMIT
        ),
        "3 three-sleeve sharpe > two-sleeve, same window": sharpe(three_way) > sharpe(two_way),
        "4 three-sleeve mdd < two-sleeve, same window": (
            max_drawdown(three_way) < max_drawdown(two_way)
        ),
    }
    print()
    for label, passed in checks.items():
        print(f"{label:48s} {'PASS' if passed else 'FAIL'}")
    print(f"\nVERDICT: {'PASS' if all(checks.values()) else 'REGISTERED NEGATIVE'}")

    print_stress(days, series)


if __name__ == "__main__":
    main()

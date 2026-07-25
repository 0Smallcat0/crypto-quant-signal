"""Cross-market combination analysis (CROSSMARKET_COMBINATION_PREREGISTRATION.md).

Reads two already-registered trial reports — one per repository — builds a
daily-aligned 50/50 book rebalanced monthly, and evaluates the
pre-declared criteria. Runs no backtest and registers no trial.

Alignment: the crypto sleeve returns every calendar day; the Taiwan sleeve
returns on Taiwan trading days and contributes exactly 0 otherwise, which
is what a held position in a closed market does.

Usage:
    python -m scripts.analyze_crossmarket_combination
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import date
from pathlib import Path

_DAYS_PER_YEAR = 365
_CRYPTO_REPORT = Path("docs/reports/backtests/trial-000088/report.json")
_TW_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json")


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


def sharpe(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    stdev = statistics.stdev(returns)
    return statistics.fmean(returns) / stdev * math.sqrt(_DAYS_PER_YEAR) if stdev > 0 else 0.0


def max_drawdown(returns: list[float]) -> float:
    equity = peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = max(worst, 1.0 - equity / peak)
    return worst


def total_multiple(returns: list[float]) -> float:
    equity = 1.0
    for value in returns:
        equity *= 1.0 + value
    return equity


def combine_monthly_rebalanced(
    days: list[date], left: dict[date, float], right: dict[date, float], weight: float
) -> list[float]:
    """Fixed weights restored at each month boundary, drifting in between.

    Rebalancing monthly rather than daily is the realistic version: a
    daily-rebalanced book would trade both sleeves every session for no
    economic reason.
    """

    combined: list[float] = []
    sleeve = [weight, 1.0 - weight]
    month = (days[0].year, days[0].month)
    for day in days:
        if (day.year, day.month) != month:
            month = (day.year, day.month)
            total = sleeve[0] + sleeve[1]
            sleeve = [total * weight, total * (1.0 - weight)]
        before = sleeve[0] + sleeve[1]
        sleeve[0] *= 1.0 + left.get(day, 0.0)
        sleeve[1] *= 1.0 + right.get(day, 0.0)
        after = sleeve[0] + sleeve[1]
        combined.append(after / before - 1.0 if before > 0 else 0.0)
    return combined


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crypto-report", default=str(_CRYPTO_REPORT))
    parser.add_argument("--tw-report", default=str(_TW_REPORT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    crypto = daily_returns(Path(args.crypto_report))
    taiwan = daily_returns(Path(args.tw_report))

    start = max(min(crypto), min(taiwan))
    end = min(max(crypto), max(taiwan))
    days = sorted(day for day in set(crypto) | set(taiwan) if start <= day <= end)

    crypto_series = [crypto.get(day, 0.0) for day in days]
    taiwan_series = [taiwan.get(day, 0.0) for day in days]
    combined = combine_monthly_rebalanced(days, crypto, taiwan, 0.5)

    rows = {
        "crypto sleeve (trial 88)": crypto_series,
        "taiwan sleeve (trial 23)": taiwan_series,
        "50/50 combination": combined,
    }
    print(f"window {days[0].isoformat()} -> {days[-1].isoformat()}  days={len(days)}")
    print(f"daily correlation: {statistics.correlation(crypto_series, taiwan_series):.4f}")
    print(f"taiwan trading days in window: {sum(1 for d in days if d in taiwan)}")
    print(f"\n{'book':28s}{'sharpe':>9}{'mdd':>9}{'multiple':>10}")
    results = {}
    for name, series in rows.items():
        results[name] = (sharpe(series), max_drawdown(series), total_multiple(series))
        print(f"{name:28s}{results[name][0]:9.4f}{results[name][1]:9.4f}{results[name][2]:10.2f}")

    c_sharpe, c_mdd, _ = results["crypto sleeve (trial 88)"]
    t_sharpe, _, _ = results["taiwan sleeve (trial 23)"]
    k_sharpe, k_mdd, _ = results["50/50 combination"]
    checks = {
        "1 combined sharpe > both sleeves": k_sharpe > c_sharpe and k_sharpe > t_sharpe,
        "2 combined mdd < crypto sleeve mdd": k_mdd < c_mdd,
        "3 both sleeves positive sharpe": c_sharpe > 0 and t_sharpe > 0,
    }
    print()
    for label, passed in checks.items():
        print(f"{label:40s} {'PASS' if passed else 'FAIL'}")
    print(f"\nVERDICT: {'PASS' if all(checks.values()) else 'REGISTERED NEGATIVE'}")


if __name__ == "__main__":
    main()

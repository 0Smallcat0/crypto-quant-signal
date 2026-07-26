"""Cash-aware sleeve allocation (CASH_AWARE_ALLOCATION_PREREGISTRATION.md).

Computes the frozen rule: equal share among the sleeves that are actually
long, zero free parameters, book gross exposure never above 1.

Lookahead guard: the weight applied to day t's return uses the most recent
decision made STRICTLY BEFORE t. Weighting a return by a decision taken at
that same close would be reading the answer first, and it would flatter this
design more than any parameter could.

Registers no trial, runs no backtest.

Usage:
    python -m scripts.run_cash_aware_allocation
"""

from __future__ import annotations

import argparse
import json
from bisect import bisect_left
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

_CRYPTO_REPORT = Path("docs/reports/backtests/trial-000088/report.json")
_TW_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json")
_GOLD_REPORT = Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json")

_TWO_SLEEVE_SHARPE = 1.3437
_TWO_SLEEVE_MDD = 0.1973


def exposure_by_date(path: Path) -> dict[date, float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    report = payload.get("report", payload)
    return {
        date.fromisoformat(str(target["as_of"])[:10]): 1.0 - float(target["cash_weight"])
        for target in report["targets"]
    }


def held_during(
    exposures: dict[date, float], days: list[date], decision_days: list[date]
) -> list[float]:
    """Exposure in force during each day, from the last decision before it."""

    held: list[float] = []
    for day in days:
        position = bisect_left(decision_days, day) - 1
        held.append(exposures[decision_days[position]] if position >= 0 else 0.0)
    return held


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crypto-report", default=str(_CRYPTO_REPORT))
    parser.add_argument("--tw-report", default=str(_TW_REPORT))
    parser.add_argument("--gold-report", default=str(_GOLD_REPORT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = {
        "crypto": Path(args.crypto_report),
        "taiwan": Path(args.tw_report),
        "gold": Path(args.gold_report),
    }
    returns = {name: daily_returns(path) for name, path in paths.items()}
    exposures = {name: exposure_by_date(path) for name, path in paths.items()}
    decisions = {name: sorted(series) for name, series in exposures.items()}

    days = common_window(list(returns.values()))
    held = {name: held_during(exposures[name], days, decisions[name]) for name in paths}

    cash_aware: list[float] = []
    gross: list[float] = []
    active_days = 0
    for index, day in enumerate(days):
        live = [name for name in paths if held[name][index] > 0.0]
        if not live:
            cash_aware.append(0.0)
            gross.append(0.0)
            continue
        active_days += 1
        weight = 1.0 / len(live)
        cash_aware.append(sum(weight * returns[name].get(day, 0.0) for name in live))
        gross.append(sum(weight * held[name][index] for name in live))

    equal = combine_monthly_rebalanced(days, [returns[name] for name in paths])

    print(f"window {days[0].isoformat()} -> {days[-1].isoformat()}  days={len(days)}")
    print(f"days with at least one sleeve long: {active_days} ({active_days / len(days):.1%})")
    print(f"mean book gross: equal-weight 0.3380 -> cash-aware {sum(gross) / len(gross):.4f}")
    print(f"max book gross : {max(gross):.4f}  (must never exceed 1)")

    print(f"\n{'book':30s}{'sharpe':>9}{'mdd':>9}{'multiple':>10}")
    for name, values in (("1/3 each (published)", equal), ("equal among active", cash_aware)):
        print(
            f"{name:30s}{sharpe(values):9.4f}"
            f"{max_drawdown(values):9.4f}{total_multiple(values):10.2f}"
        )

    checks = {
        "1 terminal multiple > 3.94x": total_multiple(cash_aware) > total_multiple(equal),
        "2 max drawdown < 19.73% (two-sleeve)": max_drawdown(cash_aware) < _TWO_SLEEVE_MDD,
        "3 sharpe >= 1.3437 (two-sleeve)": sharpe(cash_aware) >= _TWO_SLEEVE_SHARPE,
    }
    print()
    for label, passed in checks.items():
        print(f"{label:40s} {'PASS' if passed else 'FAIL'}")
    print(f"\nVERDICT: {'PASS' if all(checks.values()) else 'REGISTERED NEGATIVE'}")
    print("\nUpper bound: reallocation trading costs are not modeled.")


if __name__ == "__main__":
    main()

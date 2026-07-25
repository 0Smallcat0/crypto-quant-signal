"""Adversarial diagnostics on an already-registered trial's return series.

Re-analysis only: reads durable return series under
docs/reports/research/trial_returns/ and computes stability, tail, and
combination read-outs. Runs NO backtest, registers NO trial, and therefore
costs the registry nothing (no new candidate columns, no DSR bar rise).

The point is to try to KILL the candidate: if annualized Sharpe is an
artifact of one regime, of a handful of days, or of the sample window, these
diagnostics say so.

Usage:
    python -m scripts.analyze_candidate --trial 88 --compare 4
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from datetime import date, timedelta
from pathlib import Path

_RETURNS_DIR = Path("docs/reports/research/trial_returns")
_DAYS_PER_YEAR = 365


def load_series(trial_id: int) -> tuple[list[date], list[float]]:
    path = _RETURNS_DIR / f"trial-{trial_id:06d}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    returns = [float(value) for value in payload["daily_returns"]]
    start = date.fromisoformat(str(payload["first_return_date"]))
    dates = [start + timedelta(days=index) for index in range(len(returns))]
    return dates, returns


def sharpe(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    stdev = statistics.stdev(returns)
    if stdev <= 0.0:
        return 0.0
    return statistics.fmean(returns) / stdev * math.sqrt(_DAYS_PER_YEAR)


def max_drawdown(returns: list[float]) -> float:
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = max(worst, 1.0 - equity / peak)
    return worst


def total_return(returns: list[float]) -> float:
    equity = 1.0
    for value in returns:
        equity *= 1.0 + value
    return equity - 1.0


def subperiods(
    dates: list[date], returns: list[float], boundaries: list[date]
) -> list[tuple[str, list[float]]]:
    edges = [dates[0], *boundaries, dates[-1] + timedelta(days=1)]
    blocks: list[tuple[str, list[float]]] = []
    for start, end in zip(edges, edges[1:]):
        segment = [value for day, value in zip(dates, returns) if start <= day < end]
        blocks.append((f"{start.isoformat()}..{(end - timedelta(days=1)).isoformat()}", segment))
    return blocks


def rolling_sharpe(returns: list[float], window: int) -> list[float]:
    return [
        sharpe(returns[index : index + window])
        for index in range(0, len(returns) - window + 1, window // 4 or 1)
    ]


def stationary_bootstrap(
    returns: list[float], *, samples: int, block_mean: int, seed: int
) -> list[float]:
    """Politis-Romano stationary bootstrap: preserves serial dependence.

    IID resampling would flatter a trend strategy by destroying the
    autocorrelation its drawdowns come from.
    """

    rng = random.Random(seed)
    count = len(returns)
    probability = 1.0 / block_mean
    sharpes: list[float] = []
    for _ in range(samples):
        drawn: list[float] = []
        index = rng.randrange(count)
        while len(drawn) < count:
            drawn.append(returns[index])
            if rng.random() < probability:
                index = rng.randrange(count)
            else:
                index = (index + 1) % count
        sharpes.append(sharpe(drawn))
    return sorted(sharpes)


def drop_best_days(returns: list[float], count: int) -> list[float]:
    order = sorted(range(len(returns)), key=lambda index: returns[index], reverse=True)
    dropped = set(order[:count])
    return [value for index, value in enumerate(returns) if index not in dropped]


def correlation(left: list[float], right: list[float]) -> float:
    size = min(len(left), len(right))
    left_mean = statistics.fmean(left[:size])
    right_mean = statistics.fmean(right[:size])
    covariance = sum((left[i] - left_mean) * (right[i] - right_mean) for i in range(size))
    left_var = sum((left[i] - left_mean) ** 2 for i in range(size))
    right_var = sum((right[i] - right_mean) ** 2 for i in range(size))
    if left_var <= 0.0 or right_var <= 0.0:
        return 0.0
    return covariance / math.sqrt(left_var * right_var)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=int, required=True)
    parser.add_argument("--compare", type=int, default=4)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--block-mean", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260725)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dates, returns = load_series(args.trial)
    _, other = load_series(args.compare)

    print(
        f"=== trial {args.trial}: {len(returns)} returns "
        f"{dates[0].isoformat()}..{dates[-1].isoformat()} ==="
    )
    print(f"full-window sharpe   {sharpe(returns):.4f}")
    print(f"full-window mdd      {max_drawdown(returns):.4f}")
    print(f"full-window return   {total_return(returns):.4f}")

    print("\n--- subperiod stability (does one regime carry it?) ---")
    for label, block in subperiods(
        dates,
        returns,
        [date(2021, 1, 1), date(2022, 1, 1), date(2023, 1, 1), date(2024, 1, 1)],
    ):
        if len(block) < 30:
            continue
        print(
            f"{label}  n={len(block):4d}  sharpe={sharpe(block):7.4f}  "
            f"mdd={max_drawdown(block):.4f}  return={total_return(block):8.4f}"
        )

    print("\n--- rolling 365d sharpe (quarterly steps) ---")
    rolls = rolling_sharpe(returns, 365)
    negative = sum(1 for value in rolls if value < 0)
    print(
        f"windows={len(rolls)}  min={min(rolls):.4f}  median={statistics.median(rolls):.4f}  "
        f"max={max(rolls):.4f}  negative={negative} ({negative / len(rolls):.1%})"
    )

    print(
        "\n--- stationary bootstrap CI (block mean "
        f"{args.block_mean}d, {args.bootstrap_samples} samples) ---"
    )
    boots = stationary_bootstrap(
        returns,
        samples=args.bootstrap_samples,
        block_mean=args.block_mean,
        seed=args.seed,
    )
    lower = boots[int(0.05 * len(boots))]
    upper = boots[int(0.95 * len(boots))]
    below_zero = sum(1 for value in boots if value <= 0.0) / len(boots)
    below_one = sum(1 for value in boots if value <= 1.0) / len(boots)
    print(
        f"5%={lower:.4f}  95%={upper:.4f}  P(sharpe<=0)={below_zero:.4f}  "
        f"P(sharpe<=1)={below_one:.4f}"
    )

    print("\n--- tail dependence (drop the best days) ---")
    for count in (1, 5, 10, 20):
        trimmed = drop_best_days(returns, count)
        print(
            f"drop {count:2d} best: sharpe={sharpe(trimmed):7.4f}  "
            f"return={total_return(trimmed):8.4f}"
        )

    print(f"\n--- combination with trial {args.compare} ---")
    size = min(len(returns), len(other))
    print(f"correlation={correlation(returns, other):.4f}")
    for weight in (0.25, 0.5, 0.75):
        blended = [weight * returns[i] + (1.0 - weight) * other[i] for i in range(size)]
        print(
            f"w({args.trial})={weight:.2f}  sharpe={sharpe(blended):7.4f}  "
            f"mdd={max_drawdown(blended):.4f}  return={total_return(blended):8.4f}"
        )
    print(
        f"w({args.trial})=0.00  sharpe={sharpe(other[:size]):7.4f}  "
        f"mdd={max_drawdown(other[:size]):.4f}  return={total_return(other[:size]):8.4f}"
    )


if __name__ == "__main__":
    main()

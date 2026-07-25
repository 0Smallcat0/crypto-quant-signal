"""Diagnostic: how PBO depends on what counts as a candidate.

Reads only durable return series (registers nothing, runs no backtest) and
computes CSCV/PBO over three nested column sets:

1. all-columns — every registered trial, the conservative upper bound the
   gate report already prints.
2. candidates — PRE_HOLDOUT_PROTOCOL section 1's mechanical rule, the
   gate-3 verdict input.
3. distinct-family — one representative per genuinely different strategy
   architecture, chosen by hand and listed in the result document.

**This is a diagnostic, not a gate verdict.** Gate 3's rule is frozen
until the October holdout is spent; nothing computed here changes it. The
point is to measure whether the failing PBO is telling us "the search is
overfit" or "you cannot reliably rank near-duplicates" — two very
different statements that the same number can carry.

Usage:
    python -m scripts.analyze_pbo_scope --representatives 4,7,29,56,78,96,88,118,112
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.run_gate_report import (
    CSCV_BLOCKS,
    build_performance_matrix,
    candidate_trials,
    load_return_series,
)
from src.backtest import load_trials, probability_of_backtest_overfitting

_RESEARCH_DIR = Path("docs/reports/research")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(_RESEARCH_DIR / "trial_registry.jsonl"))
    parser.add_argument("--returns-dir", default=str(_RESEARCH_DIR / "trial_returns"))
    parser.add_argument(
        "--representatives",
        required=True,
        help="Comma-separated trial ids, one per distinct strategy architecture.",
    )
    parser.add_argument(
        "--scopes",
        default="distinct_family",
        help=(
            "Comma-separated subset of all_columns,candidates,distinct_family. "
            "Defaults to distinct_family alone: the other two are already "
            "printed by every gate report, and recomputing 100+ columns of "
            "CSCV to reprint a known number costs hours for nothing."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = Path(args.registry)
    returns_dir = Path(args.returns_dir)
    trials = load_trials(registry)
    series = {trial.trial_id: load_return_series(returns_dir, trial.trial_id) for trial in trials}

    representatives = [int(value) for value in args.representatives.split(",")]
    missing = [trial_id for trial_id in representatives if trial_id not in series]
    if missing:
        raise SystemExit(f"unknown representative trial ids: {missing}")

    all_scopes = {
        "all_columns": sorted(series),
        "candidates": [trial.trial_id for trial in candidate_trials(trials)],
        "distinct_family": sorted(representatives),
    }
    wanted = [name.strip() for name in args.scopes.split(",") if name.strip()]
    unknown = [name for name in wanted if name not in all_scopes]
    if unknown:
        raise SystemExit(f"unknown scopes: {unknown}")
    scopes = {name: all_scopes[name] for name in wanted}

    report: dict[str, object] = {"registry_trials": len(trials)}
    for name, ids in scopes.items():
        matrix = build_performance_matrix({trial_id: series[trial_id] for trial_id in ids})
        result = probability_of_backtest_overfitting(matrix, block_count=CSCV_BLOCKS)
        report[name] = {
            "columns": len(ids),
            "trial_ids": ids,
            "pbo": round(result.pbo, 6),
            "combinations_evaluated": result.combinations_evaluated,
        }
        print(f"{name:16s} columns={len(ids):4d}  pbo={result.pbo:.6f}")

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

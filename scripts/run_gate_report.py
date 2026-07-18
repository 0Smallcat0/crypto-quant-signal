"""Gate 3/4 orchestration (P2-8): registry-wide PBO and per-trial DSR report.

Assembles the anti-overfitting verdict the qualification sign-off needs:
every registered trial's durable daily-return series becomes one column of a
T×N performance matrix → CSCV/PBO (S=16); each trial's DSR is deflated by the
Sharpe variance across ALL registered trials at N = the full registry count.
No trial selection, no window selection: the registry IS the input, which is
the whole point of registering everything.

Alignment is strict — every series must share the same first/last return date
and length. A mismatch aborts with the exact discrepancies instead of
silently truncating to a flattering common window.

Usage:
    python -m scripts.run_gate_report            # print report JSON
    python -m scripts.run_gate_report --write    # also persist a dated JSON
                                                 # under docs/reports/research/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from src.backtest import (
    TrialRecord,
    deflated_sharpe_ratio,
    load_trials,
    non_annualized_sharpe_variance,
    probability_of_backtest_overfitting,
)

PBO_MAX = 0.05
DSR_MIN = 0.95
DATA_FLOOR_DAYS = 1000
CSCV_BLOCKS = 16

_RESEARCH_DIR = Path("docs/reports/research")


def load_return_series(returns_dir: Path, trial_id: int) -> dict[str, object]:
    path = returns_dir / f"trial-{trial_id:06d}.json"
    if not path.exists():
        msg = (
            f"trial {trial_id} has no durable return series at {path}; "
            "re-run the backtest runner before producing a gate report"
        )
        raise SystemExit(msg)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return loaded


def candidate_trials(trials: tuple[TrialRecord, ...]) -> list[TrialRecord]:
    """Candidate columns per docs/contracts/PRE_HOLDOUT_PROTOCOL.md §1.

    Mechanical rule over registry fields only: exclude cost-stress reruns and
    holdout-spend rows; collapse identical configurations (same config hash,
    strategy name, and variant/overlay parameters) to the highest trial_id so
    audit/parity reruns count once, on the newest engine.
    """

    newest_by_key: dict[tuple[str, ...], TrialRecord] = {}
    for trial in trials:
        if str(trial.cost_assumptions.get("cost_multiplier", "1")) != "1":
            continue
        if str(trial.parameters.get("holdout_spend", "False")) == "True":
            continue
        key = (
            trial.config_hash,
            str(trial.parameters.get("strategy_name", "daily_trend_ensemble")),
            str(trial.parameters.get("confirm_days", "1")),
            str(trial.parameters.get("vol_target_annualized", "none")),
            str(trial.parameters.get("vol_window_days", "20")),
            str(trial.parameters.get("vol_rebalance", "daily")),
        )
        existing = newest_by_key.get(key)
        if existing is None or trial.trial_id > existing.trial_id:
            newest_by_key[key] = trial
    return sorted(newest_by_key.values(), key=lambda trial: trial.trial_id)


def build_performance_matrix(
    series_by_trial: dict[int, dict[str, object]],
) -> list[list[float]]:
    """Strictly aligned T×N matrix, one column per registered trial."""

    shapes = {
        trial_id: (
            str(series.get("first_return_date")),
            str(series.get("last_return_date")),
            len(list(series.get("daily_returns", []))),  # type: ignore[arg-type]
        )
        for trial_id, series in series_by_trial.items()
    }
    if len(set(shapes.values())) != 1:
        lines = "\n".join(
            f"  trial {trial_id}: {first} -> {last} ({count} returns)"
            for trial_id, (first, last, count) in sorted(shapes.items())
        )
        msg = (
            "trial return series are not aligned; refusing to build the "
            f"performance matrix on mismatched windows:\n{lines}"
        )
        raise SystemExit(msg)
    ordered = sorted(series_by_trial)
    columns = [
        [float(value) for value in list(series_by_trial[trial_id]["daily_returns"])]  # type: ignore[arg-type]
        for trial_id in ordered
    ]
    return [[column[row] for column in columns] for row in range(len(columns[0]))]


def build_report(registry_path: Path, returns_dir: Path, holdout_path: Path) -> dict[str, object]:
    trials = load_trials(registry_path)
    if len(trials) < 2:
        raise SystemExit("gate 3/4 need at least two registered trials")
    series_by_trial = {
        trial.trial_id: load_return_series(returns_dir, trial.trial_id) for trial in trials
    }
    matrix = build_performance_matrix(series_by_trial)
    observations = len(matrix)

    pbo_all = probability_of_backtest_overfitting(matrix, block_count=CSCV_BLOCKS)
    candidates = candidate_trials(trials)
    candidate_matrix = build_performance_matrix(
        {trial.trial_id: series_by_trial[trial.trial_id] for trial in candidates}
    )
    pbo_candidates = probability_of_backtest_overfitting(candidate_matrix, block_count=CSCV_BLOCKS)
    annualized = [float(trial.metrics["annualized_sharpe"]) for trial in trials]
    variance = non_annualized_sharpe_variance(annualized)
    trial_count = len(trials)

    dsr_rows = []
    for trial in trials:
        returns = [
            float(value)
            for value in list(series_by_trial[trial.trial_id]["daily_returns"])  # type: ignore[arg-type]
        ]
        result = deflated_sharpe_ratio(
            returns,
            trial_sharpe_variance=variance,
            effective_trials=trial_count,
        )
        dsr_rows.append(
            {
                "trial_id": trial.trial_id,
                "operator_note": trial.operator_note,
                "annualized_sharpe": trial.metrics["annualized_sharpe"],
                "dsr": round(result.deflated_sharpe_ratio, 6),
                "expected_max_sharpe": round(result.expected_max_sharpe, 6),
                "passes_dsr": result.deflated_sharpe_ratio >= DSR_MIN,
            }
        )

    holdout: object = None
    if holdout_path.exists():
        holdout = json.loads(holdout_path.read_text(encoding="utf-8"))

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "registry_path": str(registry_path),
        "trials_n": trial_count,
        "observations": observations,
        "gate_2_data_floor": {
            "required_days": DATA_FLOOR_DAYS,
            "observed_days": observations,
            "passes": observations >= DATA_FLOOR_DAYS,
        },
        "gate_3_pbo": {
            "threshold_max": PBO_MAX,
            # Verdict input per PRE_HOLDOUT_PROTOCOL.md §1: candidate columns.
            "pbo": round(pbo_candidates.pbo, 6),
            "candidate_trial_ids": [trial.trial_id for trial in candidates],
            "cscv_blocks": pbo_candidates.block_count,
            "combinations_evaluated": pbo_candidates.combinations_evaluated,
            "passes": pbo_candidates.pbo <= PBO_MAX,
            # Conservative upper bound over every registry column, always shown.
            "pbo_all_columns": round(pbo_all.pbo, 6),
        },
        "gate_4_dsr": {
            "threshold_min": DSR_MIN,
            "trial_sharpe_variance_deannualized": variance,
            # Conservative: raw registry count, no correlation shrinkage —
            # a larger N only raises the expected-max bar.
            "effective_trials": trial_count,
            "per_trial": dsr_rows,
        },
        "holdout_lock": holdout,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(_RESEARCH_DIR / "trial_registry.jsonl"))
    parser.add_argument("--returns-dir", default=str(_RESEARCH_DIR / "trial_returns"))
    parser.add_argument("--holdout", default=str(_RESEARCH_DIR / "holdout_lock.json"))
    parser.add_argument(
        "--write",
        action="store_true",
        help="Persist the report to docs/reports/research/gate_report_<date>.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(Path(args.registry), Path(args.returns_dir), Path(args.holdout))
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.write:
        stamp = datetime.now(UTC).date().isoformat()
        path = _RESEARCH_DIR / f"gate_report_{stamp}.json"
        path.write_text(text + "\n", encoding="utf-8")
        print(f"written: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()

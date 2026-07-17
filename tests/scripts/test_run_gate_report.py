from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.run_gate_report import build_performance_matrix, build_report


def _registry_row(trial_id: int, sharpe: str) -> dict[str, object]:
    return {
        "trial_id": trial_id,
        "recorded_at": "2026-07-01T00:00:00+00:00",
        "config_hash": f"hash-{trial_id}",
        "code_version": "abc1234",
        "strategy_id": "daily_trend_ensemble",
        "parameters": {},
        "universe": ["BTCUSDT", "ETHUSDT"],
        "data_start": "2018-03-04T23:59:59.999000+00:00",
        "data_end": "2025-07-01T23:59:59.999000+00:00",
        "cost_assumptions": {"fee_bps": "10"},
        "metrics": {"annualized_sharpe": sharpe},
        "operator_note": f"trial {trial_id}",
    }


def _series(returns: list[float]) -> dict[str, object]:
    return {
        "first_return_date": "2018-03-05",
        "last_return_date": "2025-07-01",
        "daily_returns": returns,
    }


def _write_fixture(
    tmp_path: Path, *, returns_by_trial: dict[int, dict[str, object]]
) -> tuple[Path, Path, Path]:
    registry = tmp_path / "trial_registry.jsonl"
    registry.write_text(
        "\n".join(
            json.dumps(_registry_row(trial_id, sharpe))
            for trial_id, sharpe in ((1, "1.10"), (2, "1.05"))
        )
        + "\n",
        encoding="utf-8",
    )
    returns_dir = tmp_path / "trial_returns"
    returns_dir.mkdir()
    for trial_id, series in returns_by_trial.items():
        (returns_dir / f"trial-{trial_id:06d}.json").write_text(
            json.dumps(series), encoding="utf-8"
        )
    holdout = tmp_path / "holdout_lock.json"
    holdout.write_text(json.dumps({"spent": False}), encoding="utf-8")
    return registry, returns_dir, holdout


def test_matrix_is_columns_per_trial_in_id_order() -> None:
    matrix = build_performance_matrix(
        {
            2: _series([0.3, 0.4]),
            1: _series([0.1, 0.2]),
        }
    )

    assert matrix == [[0.1, 0.3], [0.2, 0.4]]


def test_misaligned_series_abort_with_the_discrepancies() -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_performance_matrix(
            {
                1: _series([0.1, 0.2]),
                2: {
                    "first_return_date": "2019-01-01",
                    "last_return_date": "2025-07-01",
                    "daily_returns": [0.3],
                },
            }
        )

    message = str(excinfo.value)
    assert "not aligned" in message
    assert "trial 1" in message
    assert "trial 2" in message


def test_report_runs_gates_over_the_fixture_registry(tmp_path: Path) -> None:
    # 1200 alternating-sign days clear the data floor; near-identical trials
    # keep cross-trial Sharpe variance (and thus deflation) tiny.
    base = [0.01 if index % 2 == 0 else -0.004 for index in range(1200)]
    other = [value * 0.98 for value in base]
    registry, returns_dir, holdout = _write_fixture(
        tmp_path, returns_by_trial={1: _series(base), 2: _series(other)}
    )

    report = build_report(registry, returns_dir, holdout)

    assert report["trials_n"] == 2
    assert report["observations"] == 1200
    gate2 = report["gate_2_data_floor"]
    assert isinstance(gate2, dict)
    assert gate2["passes"] is True
    gate3 = report["gate_3_pbo"]
    assert isinstance(gate3, dict)
    assert gate3["cscv_blocks"] == 16
    assert 0.0 <= float(gate3["pbo"]) <= 1.0
    gate4 = report["gate_4_dsr"]
    assert isinstance(gate4, dict)
    rows = gate4["per_trial"]
    assert isinstance(rows, list)
    assert [row["trial_id"] for row in rows] == [1, 2]
    # Strongly positive, nearly identical returns: DSR must clear the gate.
    assert all(row["passes_dsr"] for row in rows)
    assert report["holdout_lock"] == {"spent": False}


def test_missing_return_series_is_a_hard_stop(tmp_path: Path) -> None:
    registry, returns_dir, holdout = _write_fixture(
        tmp_path, returns_by_trial={1: _series([0.1, 0.2])}
    )

    with pytest.raises(SystemExit) as excinfo:
        build_report(registry, returns_dir, holdout)

    assert "trial 2 has no durable return series" in str(excinfo.value)

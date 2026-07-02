"""Registered backtest entry point: holdout enforcement + trial registry + report."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from src.backtest.engine import run_backtest
from src.backtest.holdout import (
    HoldoutState,
    initialize_holdout,
    load_holdout,
    require_data_allowed,
    spend_holdout,
)
from src.backtest.registry import TrialRecord, append_trial
from src.backtest.types import BacktestError, BacktestParameters, BacktestReport
from src.domain import Candle

DEFAULT_HOLDOUT_DAYS = 365

_ENSEMBLE_PARAMETERS = {
    "lookbacks": "20,65,150,200",
    "ladder": "0,0.25,0.5,0.75,1",
    "fill_rule": "next_bar_open",
}


@dataclass(frozen=True, slots=True)
class RegisteredBacktestResult:
    """Everything one registered run produced."""

    report: BacktestReport
    trial: TrialRecord
    report_path: Path
    holdout: HoldoutState


def run_registered_backtest(
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    *,
    parameters: BacktestParameters,
    config_hash: str,
    code_version: str,
    registry_path: str | Path,
    holdout_path: str | Path,
    reports_directory: str | Path,
    recorded_at: datetime,
    operator_note: str = "",
    strategy_id: str = "daily_trend_ensemble",
    spend_holdout_single_use: bool = False,
) -> RegisteredBacktestResult:
    """Run one backtest under gate rules: lock, trim, register, report.

    Regular runs never see holdout data: on the first run the lock is created
    (most recent DEFAULT_HOLDOUT_DAYS locked) and inputs are trimmed to end
    before the holdout starts. A qualification run passes
    ``spend_holdout_single_use=True``: the spend is recorded BEFORE execution
    and can never happen twice.
    """

    if not candles_by_symbol:
        msg = "candles_by_symbol must not be empty"
        raise BacktestError(msg)
    data_end = max(candles[-1].close_time for candles in candles_by_symbol.values() if candles)
    holdout = load_holdout(holdout_path)
    if holdout is None:
        holdout = initialize_holdout(
            holdout_path,
            holdout_start=data_end - timedelta(days=DEFAULT_HOLDOUT_DAYS),
            locked_at=recorded_at,
        )

    if spend_holdout_single_use:
        holdout = spend_holdout(holdout_path, spent_at=recorded_at)
        run_candles = dict(candles_by_symbol)
    else:
        run_candles = {
            symbol_value: tuple(
                candle for candle in candles if candle.close_time < holdout.holdout_start
            )
            for symbol_value, candles in candles_by_symbol.items()
        }
        if any(not candles for candles in run_candles.values()):
            msg = (
                "no candles remain before the holdout start "
                f"({holdout.holdout_start.isoformat()}); provide more history"
            )
            raise BacktestError(msg)
        trimmed_end = max(candles[-1].close_time for candles in run_candles.values())
        require_data_allowed(holdout_path, data_end=trimmed_end)

    report = run_backtest(run_candles, parameters=parameters)

    trial = append_trial(
        registry_path,
        recorded_at=recorded_at,
        config_hash=config_hash,
        code_version=code_version,
        strategy_id=strategy_id,
        parameters={
            **_ENSEMBLE_PARAMETERS,
            "cost_multiplier": str(parameters.cost_multiplier),
            "holdout_spend": str(spend_holdout_single_use),
        },
        universe=tuple(sorted(parameters.risk_budgets)),
        data_start=report.data_start,
        data_end=report.data_end,
        cost_assumptions=dict(report.cost_assumptions),
        metrics={
            "final_equity": str(report.metrics.final_equity),
            "total_return_fraction": str(report.metrics.total_return_fraction),
            "annualized_sharpe": str(report.metrics.annualized_sharpe),
            "max_drawdown_fraction": str(report.metrics.max_drawdown_fraction),
            "trade_count": str(report.metrics.trade_count),
            "rejected_count": str(report.metrics.rejected_count),
            "benchmark_final_equity": str(report.metrics.benchmark_final_equity),
            "observation_days": str(report.metrics.observation_days),
        },
        operator_note=operator_note,
    )

    report_path = Path(reports_directory) / f"trial-{trial.trial_id:06d}" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {"trial": trial.to_json_dict(), "report": report.to_json_dict()},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return RegisteredBacktestResult(
        report=report,
        trial=trial,
        report_path=report_path,
        holdout=holdout,
    )

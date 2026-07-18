"""Goal P experiment 2: run the pre-registered 16-configuration vol family.

Executes every configuration in docs/research/GOALP_EXPERIMENT2_PREREGISTRATION.md
through the SAME registered-backtest pipeline as any other trial (lock, trim,
register, durable returns). One invocation, whole family, no selection until
the pre-declared rule is applied to the completed table.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from src.backtest import BacktestParameters, config_hash_for, run_registered_backtest
from src.config import config_snapshot, load_config
from src.data import candle_file_name, read_candles_jsonl

TARGETS = ("0.30", "0.50", "0.70", "0.90")
WINDOWS = (20, 60)
REBALANCES = ("daily", "monthly")


def _code_version() -> str:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return f"{head}-dirty" if dirty else head
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/runtime/paper_runtime.yaml")
    parser.add_argument("--candles-dir", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))
    candles_dir = Path(args.candles_dir or config.storage.candle_files_directory)
    candles_by_symbol = {}
    for symbol_value in sorted(config.portfolio.risk_budgets):
        file_path = candles_dir / candle_file_name(symbol_value, config.data_source.timeframe)
        candles_by_symbol[symbol_value] = read_candles_jsonl(file_path)

    code_version = _code_version()
    config_hash = config_hash_for(config_snapshot(config))
    rows = []
    for target in TARGETS:
        for window in WINDOWS:
            for rebalance in REBALANCES:
                parameters = BacktestParameters(
                    risk_budgets=config.portfolio.risk_budgets,
                    initial_cash=config.account.initial_cash,
                    account_id=config.account.account_id,
                    fee_bps=config.execution.fee_bps,
                    slippage_bps=config.execution.slippage_bps,
                    quantity_step=config.execution.quantity_step,
                    price_tick=config.execution.price_tick,
                    min_notional_usdt=config.risk.min_notional_usdt,
                    max_drawdown_fraction=config.risk.max_drawdown_fraction,
                    daily_loss_pause_fraction=config.risk.daily_loss_pause_fraction,
                    disaster_single_day_drop_fraction=(
                        config.risk.disaster_single_day_drop_fraction
                    ),
                    stale_data_max_age_seconds=config.risk.stale_data_max_age_seconds,
                    vol_target_annualized=Decimal(target),
                    vol_window_days=window,
                    vol_rebalance=rebalance,
                )
                result = run_registered_backtest(
                    candles_by_symbol,
                    parameters=parameters,
                    config_hash=config_hash,
                    code_version=code_version,
                    registry_path=config.storage.trial_registry_path,
                    holdout_path=config.storage.holdout_lock_path,
                    reports_directory=config.storage.backtest_reports_directory,
                    recorded_at=datetime.now(UTC),
                    operator_note=(
                        "Goal P exp 2 family member: vol overlay "
                        f"target={target} window={window} rebalance={rebalance} "
                        "(GOALP_EXPERIMENT2_PREREGISTRATION.md)"
                    ),
                )
                metrics = result.report.metrics
                rows.append(
                    {
                        "trial_id": result.trial.trial_id,
                        "target": target,
                        "window": window,
                        "rebalance": rebalance,
                        "sharpe": str(metrics.annualized_sharpe),
                        "max_drawdown": str(metrics.max_drawdown_fraction),
                        "turnover": str(metrics.annualized_turnover),
                        "final_equity": str(metrics.final_equity),
                    }
                )
                print(
                    f"trial {result.trial.trial_id}: target={target} window={window} "
                    f"rebalance={rebalance} sharpe={metrics.annualized_sharpe} "
                    f"mdd={metrics.max_drawdown_fraction} "
                    f"turnover={metrics.annualized_turnover}"
                )

    print(json.dumps({"family_size": len(rows), "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

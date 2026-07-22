"""Goal P experiment 8: run the pre-registered 8-config Donchian-13 family.

Executes every configuration in docs/research/GOALP_EXPERIMENT8_PREREGISTRATION.md
through the SAME registered-backtest pipeline as any other trial. The
13-symbol qualified universe runs in staggered-listing ladder mode
(point-in-time per-symbol eligibility, commit 7f8a0b7).
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from scripts.run_cs_family import UNIVERSE
from src.backtest import BacktestParameters, config_hash_for, run_registered_backtest
from src.config import config_snapshot, load_config
from src.data import candle_file_name, read_candles_jsonl

WINDOW_SETS = ((10, 20, 55, 110), (10, 20, 110, 220))
EXITS = ("half_low", "mid_channel")
GATES = (False, True)


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
    parser.add_argument("--candles-dir", default="data/candles_preholdout")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))
    candles_dir = Path(args.candles_dir)
    candles_by_symbol = {
        symbol_value: read_candles_jsonl(
            candles_dir / candle_file_name(symbol_value, config.data_source.timeframe)
        )
        for symbol_value in UNIVERSE
    }
    budget = Decimal("1") / Decimal(len(UNIVERSE))

    code_version = _code_version()
    config_hash = config_hash_for(config_snapshot(config))
    rows = []
    for windows in WINDOW_SETS:
        for exit_mode in EXITS:
            for gated in GATES:
                gate_kwargs: dict[str, object] = {}
                if gated:
                    gate_kwargs = {
                        "cs_gate_sma_window": 200,
                        "cs_gate_basis": "btc",
                        "cs_gate_hysteresis": Decimal("0.02"),
                        "cs_gate_cadence": "daily",
                    }
                parameters = BacktestParameters(
                    risk_budgets=dict.fromkeys(UNIVERSE, budget),
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
                    strategy_name="donchian_breakout_ensemble",
                    dc_windows=windows,
                    dc_exit=exit_mode,
                    allow_staggered_listings=True,
                    **gate_kwargs,  # type: ignore[arg-type]
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
                        "Goal P exp 8 family member: donchian-13 staggered "
                        f"windows={'+'.join(str(w) for w in windows)} exit={exit_mode} "
                        f"gate={'on' if gated else 'off'} "
                        "(GOALP_EXPERIMENT8_PREREGISTRATION.md)"
                    ),
                )
                metrics = result.report.metrics
                rows.append(
                    {
                        "trial_id": result.trial.trial_id,
                        "windows": "+".join(str(w) for w in windows),
                        "exit": exit_mode,
                        "gate": gated,
                        "sharpe": str(metrics.annualized_sharpe),
                        "max_drawdown": str(metrics.max_drawdown_fraction),
                        "turnover": str(metrics.annualized_turnover),
                        "final_equity": str(metrics.final_equity),
                    }
                )
                print(
                    f"trial {result.trial.trial_id}: "
                    f"windows={'+'.join(str(w) for w in windows)} exit={exit_mode} "
                    f"gate={gated} sharpe={metrics.annualized_sharpe} "
                    f"mdd={metrics.max_drawdown_fraction} "
                    f"turnover={metrics.annualized_turnover} "
                    f"equity={metrics.final_equity}"
                )

    print(json.dumps({"family_size": len(rows), "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

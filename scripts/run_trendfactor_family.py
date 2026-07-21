"""Goal P experiment 6: run the pre-registered 16-config trend-factor family.

Executes every configuration in docs/research/GOALP_EXPERIMENT6_PREREGISTRATION.md
through the SAME registered-backtest pipeline as any other trial. The regime
gate is FIXED (SMA 200, btc basis, 2% hysteresis, daily) — experiment 5's
MDD-bar configuration; only the selection grid varies.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from scripts.run_cs_family import DECISION_START, UNIVERSE
from src.backtest import BacktestParameters, config_hash_for, run_registered_backtest
from src.config import config_snapshot, load_config
from src.data import candle_file_name, read_candles_jsonl

HORIZON_SETS = ((28, 56), (28, 56, 112, 224))
TOP_KS = (2, 3)
CADENCES = ("weekly", "monthly")
FILTERS = (False, True)


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

    code_version = _code_version()
    config_hash = config_hash_for(config_snapshot(config))
    rows = []
    for horizons in HORIZON_SETS:
        for top_k in TOP_KS:
            for cadence in CADENCES:
                for absolute_filter in FILTERS:
                    parameters = BacktestParameters(
                        risk_budgets=dict.fromkeys(UNIVERSE, Decimal("1")),
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
                        strategy_name="cross_sectional_momentum",
                        cs_top_k=top_k,
                        cs_lookback_days=180,
                        cs_rebalance_cadence=cadence,
                        cs_absolute_filter=absolute_filter,
                        cs_min_pool_size=4,
                        cs_decision_start=DECISION_START,
                        cs_gate_sma_window=200,
                        cs_gate_basis="btc",
                        cs_gate_hysteresis=Decimal("0.02"),
                        cs_gate_cadence="daily",
                        cs_horizon_days=horizons,
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
                            "Goal P exp 6 family member: trend factor "
                            f"horizons={'+'.join(str(h) for h in horizons)} K={top_k} "
                            f"cadence={cadence} filter={'on' if absolute_filter else 'off'} "
                            "+ fixed gate sma200/btc/2%/daily "
                            "(GOALP_EXPERIMENT6_PREREGISTRATION.md)"
                        ),
                    )
                    metrics = result.report.metrics
                    rows.append(
                        {
                            "trial_id": result.trial.trial_id,
                            "horizons": "+".join(str(h) for h in horizons),
                            "top_k": top_k,
                            "cadence": cadence,
                            "filter": absolute_filter,
                            "sharpe": str(metrics.annualized_sharpe),
                            "max_drawdown": str(metrics.max_drawdown_fraction),
                            "turnover": str(metrics.annualized_turnover),
                            "final_equity": str(metrics.final_equity),
                        }
                    )
                    print(
                        f"trial {result.trial.trial_id}: "
                        f"horizons={'+'.join(str(h) for h in horizons)} K={top_k} "
                        f"cadence={cadence} filter={absolute_filter} "
                        f"sharpe={metrics.annualized_sharpe} "
                        f"mdd={metrics.max_drawdown_fraction} "
                        f"turnover={metrics.annualized_turnover} "
                        f"equity={metrics.final_equity}"
                    )

    print(json.dumps({"family_size": len(rows), "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

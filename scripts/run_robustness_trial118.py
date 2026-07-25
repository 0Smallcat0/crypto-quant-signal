"""Robustness battery on trial 118 (docs/research/ROBUSTNESS_TRIAL118_PREREGISTRATION.md).

Battery A: six perturbations around trial 118's configuration (ATR window,
ATR multiple, and channel windows).
Battery B: trial 118's exact configuration at 2x and 3x costs.

Adversarial verification, not search: per the pre-registration, no arm run
here may ever be nominated or adopted, however it scores.
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

UNIVERSE = ("BTCUSDT", "ETHUSDT")
BASE_WINDOWS = (10, 20, 55, 110)
# (label, channel windows, atr window, atr multiple)
NEIGHBOURHOOD = (
    ("A1 atr-w10", BASE_WINDOWS, 10, "2"),
    ("A2 atr-w20", BASE_WINDOWS, 20, "2"),
    ("A3 mult-1.5", BASE_WINDOWS, 14, "1.5"),
    ("A4 mult-2.5", BASE_WINDOWS, 14, "2.5"),
    ("A5 chan-20%", (8, 16, 44, 88), 14, "2"),
    ("A6 chan+20%", (12, 24, 66, 132), 14, "2"),
)
COST_MULTIPLIERS = ("2", "3")


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

    def _parameters(
        windows: tuple[int, ...],
        atr_window: int = 14,
        atr_multiple: str = "2",
        cost_multiplier: Decimal = Decimal("1"),
    ) -> BacktestParameters:
        return BacktestParameters(
            risk_budgets={"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")},
            initial_cash=config.account.initial_cash,
            account_id=config.account.account_id,
            fee_bps=config.execution.fee_bps,
            slippage_bps=config.execution.slippage_bps,
            quantity_step=config.execution.quantity_step,
            price_tick=config.execution.price_tick,
            min_notional_usdt=config.risk.min_notional_usdt,
            max_drawdown_fraction=config.risk.max_drawdown_fraction,
            daily_loss_pause_fraction=config.risk.daily_loss_pause_fraction,
            disaster_single_day_drop_fraction=config.risk.disaster_single_day_drop_fraction,
            stale_data_max_age_seconds=config.risk.stale_data_max_age_seconds,
            strategy_name="donchian_breakout_ensemble",
            dc_windows=windows,
            dc_exit="atr_channel",
            dc_atr_window=atr_window,
            dc_atr_multiple=Decimal(atr_multiple),
            cost_multiplier=cost_multiplier,
        )

    rows = []

    def _run(label: str, parameters: BacktestParameters, note: str) -> None:
        result = run_registered_backtest(
            candles_by_symbol,
            parameters=parameters,
            config_hash=config_hash,
            code_version=code_version,
            registry_path=config.storage.trial_registry_path,
            holdout_path=config.storage.holdout_lock_path,
            reports_directory=config.storage.backtest_reports_directory,
            recorded_at=datetime.now(UTC),
            operator_note=note,
        )
        metrics = result.report.metrics
        rows.append(
            {
                "label": label,
                "trial_id": result.trial.trial_id,
                "sharpe": str(metrics.annualized_sharpe),
                "max_drawdown": str(metrics.max_drawdown_fraction),
                "turnover": str(metrics.annualized_turnover),
                "final_equity": str(metrics.final_equity),
            }
        )
        print(
            f"{label:12s} trial {result.trial.trial_id}: "
            f"sharpe={metrics.annualized_sharpe} "
            f"mdd={metrics.max_drawdown_fraction} "
            f"turnover={metrics.annualized_turnover} "
            f"equity={metrics.final_equity}"
        )

    for label, windows, atr_window, atr_multiple in NEIGHBOURHOOD:
        _run(
            label,
            _parameters(windows, atr_window=atr_window, atr_multiple=atr_multiple),
            (
                "ROBUSTNESS (never nominatable): trial-118 neighbourhood "
                f"{label} windows={'+'.join(str(w) for w in windows)} "
                f"atr_window={atr_window} atr_multiple={atr_multiple} "
                "(ROBUSTNESS_TRIAL118_PREREGISTRATION.md battery A)"
            ),
        )

    for multiplier in COST_MULTIPLIERS:
        _run(
            f"B cost x{multiplier}",
            _parameters(BASE_WINDOWS, cost_multiplier=Decimal(multiplier)),
            (
                "ROBUSTNESS (never nominatable): trial-118 cost stress "
                f"multiplier={multiplier} "
                "(ROBUSTNESS_TRIAL118_PREREGISTRATION.md battery B)"
            ),
        )

    print(json.dumps({"runs": len(rows), "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

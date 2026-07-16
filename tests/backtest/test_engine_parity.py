"""Cross-engine parity: the backtest engine and the runtime engine must agree.

docs/ENGINEERING_DECISIONS.md documents two independently written engines that
were reconciled by hand to bit-identical Decimal equity once (2026-07-03).
This test turns that one-time manual audit into a standing invariant: feed the
same bundled history through both engines and require identical fills and a
bit-identical final equity. If a refactor ever makes the two paths diverge —
including any lookahead slip in the runtime's decide-then-execute sequencing —
this fails before the divergence can reach the qualification run.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from scripts.run_paper_runtime import _runtime_parameters
from src.backtest import BacktestParameters, run_backtest
from src.config import AppConfig
from src.data import candle_file_name, read_candles_jsonl
from src.domain import Candle
from src.notify import CollectingNotificationChannel
from src.runtime import JsonlEventStore, SignalRuntime, run_replay

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEMO_CANDLES_DIR = _REPO_ROOT / "demo" / "candles"
# 200-close warmup + a bull/bear stretch of decision days, kept well under the
# full bundled history so the parity check stays fast in the default test run.
_HISTORY_BARS = 400


def _shared_history(config: AppConfig) -> dict[str, tuple[Candle, ...]]:
    candles_by_symbol: dict[str, tuple[Candle, ...]] = {}
    for symbol_value in sorted(config.portfolio.risk_budgets):
        file_path = _DEMO_CANDLES_DIR / candle_file_name(symbol_value, config.data_source.timeframe)
        candles_by_symbol[symbol_value] = read_candles_jsonl(file_path)[:_HISTORY_BARS]
    return candles_by_symbol


def _backtest_parameters(config: AppConfig) -> BacktestParameters:
    return BacktestParameters(
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
        disaster_single_day_drop_fraction=config.risk.disaster_single_day_drop_fraction,
        stale_data_max_age_seconds=config.risk.stale_data_max_age_seconds,
        cost_multiplier=Decimal("1"),
    )


def test_backtest_and_runtime_replay_reconcile_on_shared_history(tmp_path: Path) -> None:
    config = AppConfig()
    candles_by_symbol = _shared_history(config)

    report = run_backtest(candles_by_symbol, parameters=_backtest_parameters(config))

    runtime = SignalRuntime(
        parameters=_runtime_parameters(config),
        store=JsonlEventStore(tmp_path / "events.jsonl"),
        channel=CollectingNotificationChannel(),
    )
    summary = run_replay(candles_by_symbol, runtime)

    assert summary.final_equity is not None
    assert report.equity_curve, "backtest produced no equity points"
    assert report.equity_curve[-1].equity == summary.final_equity
    assert len(report.fills) == summary.fills
    # The runtime folds broker rejects and risk-gate rejects into one counter;
    # the backtest keeps them in separate buckets. Same events, one total.
    assert len(report.rejected_orders) + len(report.risk_rejections) == summary.rejections

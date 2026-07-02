"""Thin CLI for the daily signal runtime (Goal L)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.config import load_config
from src.data import MarketDataValidationError, candle_file_name, read_candles_jsonl
from src.notify import (
    CollectingNotificationChannel,
    NotificationChannel,
    WebhookNotificationChannel,
)
from src.runtime import (
    JsonlEventStore,
    RuntimeEngineError,
    RuntimeParameters,
    RuntimeStoreError,
    SignalRuntime,
    run_replay,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="configs/runtime/paper_runtime.yaml",
        help="Path to the Core MVP runtime config.",
    )
    parser.add_argument(
        "--candles-dir",
        default=None,
        help="Directory with <SYMBOL>_1d.jsonl candle files (default: storage config).",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="Runtime event store path (default: storage config).",
    )
    parser.add_argument(
        "--replay-smoke",
        action="store_true",
        help="Replay the recorded candle files through the runtime and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.replay_smoke:
        print(
            "only --replay-smoke is implemented in Core MVP; "
            "the live daily loop arrives with the stability run (Goal O)",
            file=sys.stderr,
        )
        raise SystemExit(2)

    config = load_config(Path(args.config))
    candles_dir = Path(args.candles_dir or config.storage.candle_files_directory)
    store_path = Path(args.store or config.storage.runtime_events_path)

    candles_by_symbol = {}
    for symbol_value in sorted(config.portfolio.risk_budgets):
        file_path = candles_dir / candle_file_name(symbol_value, config.data_source.timeframe)
        candles_by_symbol[symbol_value] = read_candles_jsonl(file_path)

    channel = _channel_from_config(config.notifications.channel, config.notifications.webhook_url)
    runtime = SignalRuntime(
        parameters=RuntimeParameters(
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
            idempotency_namespace=config.runtime.idempotency_key_namespace,
        ),
        store=JsonlEventStore(store_path),
        channel=channel,
    )
    summary = run_replay(candles_by_symbol, runtime)

    print(
        json.dumps(
            {
                "cycles_processed": summary.cycles_processed,
                "cycles_skipped": summary.cycles_skipped,
                "notifications": summary.notifications,
                "fills": summary.fills,
                "rejections": summary.rejections,
                "final_equity": str(summary.final_equity) if summary.final_equity else None,
                "store_path": str(store_path),
                "last_processed": (
                    runtime.last_processed.isoformat() if runtime.last_processed else None
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _channel_from_config(channel: str, webhook_url: str) -> NotificationChannel:
    if channel == "webhook":
        return WebhookNotificationChannel(webhook_url)
    return CollectingNotificationChannel()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeEngineError, RuntimeStoreError, MarketDataValidationError) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from None

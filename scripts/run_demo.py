"""Two-minute offline demo: bundled candles → real engine → dashboard.

Replays the bundled BTC/ETH daily candles (demo/candles/, 2024-01 → 2026-06)
through the SAME runtime engine the live qualification run uses — warmup gate,
exposure ladder, risk gate, paper fills, idempotent event store — then serves
the read-only dashboard over the resulting scoreboard.

No API keys, no Docker, no network. The demo store lives under data/demo/ and
is rebuilt from scratch on every run; it can never touch the live runtime
store or the paper-day counter of the real qualification run.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import uvicorn

from scripts.run_paper_runtime import _runtime_parameters
from src.api import create_dashboard_app
from src.config import AppConfig
from src.data import candle_file_name, read_candles_jsonl
from src.notify import CollectingNotificationChannel
from src.runtime import JsonlEventStore, ReplaySummary, SignalRuntime, run_replay

_DEMO_CANDLES_DIR = Path("demo/candles")
_DEMO_STORE_DIR = Path("data/demo")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port",
        type=int,
        default=8010,
        help="Dashboard port (default: 8010).",
    )
    parser.add_argument(
        "--no-serve",
        action="store_true",
        help="Replay and print the scoreboard summary without serving the dashboard.",
    )
    return parser.parse_args()


def run_demo_replay(
    *,
    candles_dir: Path = _DEMO_CANDLES_DIR,
    store_dir: Path = _DEMO_STORE_DIR,
) -> tuple[ReplaySummary, Path, AppConfig]:
    """Rebuild the demo store from the bundled candles; return the summary.

    The store directory is wiped first so every demo run replays the full
    history deterministically instead of no-opping on idempotency keys.
    """

    config = AppConfig()
    if store_dir.exists():
        shutil.rmtree(store_dir)
    store_path = store_dir / "events.jsonl"

    candles_by_symbol = {}
    for symbol_value in sorted(config.portfolio.risk_budgets):
        file_path = candles_dir / candle_file_name(symbol_value, config.data_source.timeframe)
        candles_by_symbol[symbol_value] = read_candles_jsonl(file_path)

    runtime = SignalRuntime(
        parameters=_runtime_parameters(config),
        store=JsonlEventStore(store_path),
        channel=CollectingNotificationChannel(),
    )
    summary = run_replay(candles_by_symbol, runtime)
    return summary, store_path, config


def main() -> None:
    args = parse_args()
    summary, store_path, config = run_demo_replay()

    initial_cash = config.account.initial_cash
    final_equity = summary.final_equity
    print(
        json.dumps(
            {
                "cycles_processed": summary.cycles_processed,
                "notifications": summary.notifications,
                "fills": summary.fills,
                "initial_cash": str(initial_cash),
                "final_equity": str(final_equity) if final_equity is not None else None,
                "return_pct": (
                    str(round((final_equity / initial_cash - 1) * 100, 1))
                    if final_equity is not None
                    else None
                ),
                "store_path": str(store_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.no_serve:
        return

    app = create_dashboard_app(
        store_path=store_path,
        trial_registry_path=Path(config.storage.trial_registry_path),
        holdout_lock_path=Path(config.storage.holdout_lock_path),
        risk_budgets={
            symbol: str(budget) for symbol, budget in config.portfolio.risk_budgets.items()
        },
        initial_cash=str(initial_cash),
        follow_principal=str(config.notifications.follow_principal_usdt),
    )
    print(f"demo dashboard: http://127.0.0.1:{args.port}  (Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()

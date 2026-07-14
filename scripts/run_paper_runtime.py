"""Thin CLI for the daily signal runtime (Goal L replay smoke + Goal O live cycle)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import httpx

from src.config import AppConfig, load_config
from src.data import (
    BinanceSpotPublicClient,
    BookTickerSnapshot,
    MarketDataError,
    MarketDataValidationError,
    candle_file_name,
    first_passing_public_rest_base_url,
    read_candles_jsonl,
    run_public_rest_smoke,
    symbol_from_binance_native,
)
from src.domain import Candle, Timeframe
from src.notify import (
    CollectingNotificationChannel,
    DiscordBotNotificationChannel,
    NotificationChannel,
    NotificationValidationError,
    WebhookNotificationChannel,
)
from src.risk import DISASTER_SINGLE_DAY_DROP
from src.runtime import (
    CycleResult,
    JsonlEventStore,
    RuntimeEngineError,
    RuntimeParameters,
    RuntimeStoreError,
    SignalRuntime,
    record_execution_quotes,
    run_replay,
)

# 200-close warmup plus margin; Binance caps one request at 1000 anyway.
_LIVE_FETCH_LIMIT = 210
# A lock older than this is treated as a crash leftover, not a live run.
_LOCK_STALE_SECONDS = 2 * 60 * 60


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
    parser.add_argument(
        "--once",
        action="store_true",
        help=(
            "Run one LIVE daily cycle: fetch the latest closed daily candles from "
            "Binance public REST, process them, persist notifications, and exit. "
            "Idempotent: re-running on the same day is a no-op."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.replay_smoke == args.once:
        print(
            "choose exactly one mode: --replay-smoke (recorded candles) "
            "or --once (live daily cycle)",
            file=sys.stderr,
        )
        raise SystemExit(2)

    config = load_config(Path(args.config))
    store_path = Path(args.store or config.storage.runtime_events_path)
    live_store_path = Path(config.storage.runtime_events_path)
    if args.replay_smoke and store_path.resolve() == live_store_path.resolve():
        # A replay against the live store would poison the gate's paper-day
        # counter with historical cycles. Replays must name their own store.
        print(
            "refusing: --replay-smoke must not target the live runtime store "
            f"({live_store_path}); pass an explicit --store path",
            file=sys.stderr,
        )
        raise SystemExit(2)

    channel = _channel_from_config(config)
    store = JsonlEventStore(store_path, durable_fsync=args.once)
    runtime = SignalRuntime(
        parameters=_runtime_parameters(config),
        store=store,
        channel=channel,
    )

    if args.once:
        with _single_instance_lock(store_path):
            _run_live_cycle(config, runtime, store, channel)
        return

    candles_dir = Path(args.candles_dir or config.storage.candle_files_directory)
    candles_by_symbol = {}
    for symbol_value in sorted(config.portfolio.risk_budgets):
        file_path = candles_dir / candle_file_name(symbol_value, config.data_source.timeframe)
        candles_by_symbol[symbol_value] = read_candles_jsonl(file_path)
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


def _run_live_cycle(
    config: AppConfig,
    runtime: SignalRuntime,
    store: JsonlEventStore,
    channel: NotificationChannel,
) -> None:
    observed_at = datetime.now(UTC)
    rest_base_url = _resolve_rest_base_url(config)
    candles_by_symbol = asyncio.run(_fetch_latest_candles(config, observed_at, rest_base_url))
    result = runtime.process_closed_candles(candles_by_symbol, observed_at=observed_at)
    _push_disaster_alerts(channel, result)
    # Same-day reruns (ALREADY_PROCESSED) still attempt the capture so a
    # failed morning snapshot can be backfilled; the store key dedups.
    quote_close_time = result.close_time
    if quote_close_time is None and result.reason == "ALREADY_PROCESSED":
        quote_close_time = runtime.last_processed
    exec_quotes = _record_exec_quotes_best_effort(config, rest_base_url, store, quote_close_time)

    print(
        json.dumps(
            {
                "mode": "live_once",
                "observed_at": observed_at.isoformat(),
                "processed": result.processed,
                "reason": result.reason,
                "close_time": result.close_time.isoformat() if result.close_time else None,
                "equity": str(result.equity) if result.equity is not None else None,
                "health_codes": list(result.health_codes),
                "notifications": [event.to_json_dict() for event in result.notifications],
                "fills": [
                    {
                        "symbol": fill.symbol.value,
                        "side": fill.side.value,
                        "quantity": str(fill.quantity),
                        "price": str(fill.price),
                        "fee": str(fill.fee),
                    }
                    for fill in result.fills
                ],
                "rejections": [
                    {"symbol": symbol, "reason_codes": list(codes)}
                    for symbol, codes in result.rejection_reason_codes
                ],
                "exec_quotes": exec_quotes,
                "store_path": str(store.path),
            },
            indent=2,
            sort_keys=True,
        )
    )


def _resolve_rest_base_url(config: AppConfig) -> str:
    preflight_results = run_public_rest_smoke(
        config.data_source.rest_base_url_candidates,
        timeout_seconds=float(config.data_source.timeout_seconds),
    )
    rest_base_url = first_passing_public_rest_base_url(preflight_results)
    if rest_base_url is None:
        msg = "no public Binance REST base URL is reachable from this environment"
        raise MarketDataError(msg)
    return rest_base_url


async def _fetch_latest_candles(
    config: AppConfig, observed_at: datetime, rest_base_url: str
) -> dict[str, tuple[Candle, ...]]:
    timeout_seconds = float(config.data_source.timeout_seconds)
    timeframe = Timeframe(config.data_source.timeframe)
    candles_by_symbol: dict[str, tuple[Candle, ...]] = {}
    async with BinanceSpotPublicClient(
        rest_base_url=rest_base_url,
        timeout_seconds=timeout_seconds,
    ) as client:
        for symbol_value in sorted(config.portfolio.risk_budgets):
            candles_by_symbol[symbol_value] = await client.fetch_historical_candles(
                symbol=symbol_from_binance_native(symbol_value),
                timeframe=timeframe,
                limit=_LIVE_FETCH_LIMIT,
                received_at=observed_at,
                closed_only=True,
            )
    return candles_by_symbol


def _runtime_parameters(config: AppConfig) -> RuntimeParameters:
    return RuntimeParameters(
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
    )


def _channel_from_config(config: AppConfig) -> NotificationChannel:
    channel = config.notifications.channel
    if channel == "webhook":
        return WebhookNotificationChannel(config.notifications.webhook_url)
    if channel == "discord":
        token = os.environ.get("DISCORD_BOT_TOKEN", "")
        channel_id = os.environ.get("DISCORD_CHANNEL_ID", "")
        if not token or not channel_id:
            # Never let missing push credentials cost a decision day: the cycle
            # matters more than the ping. The stand-in channel RAISES on
            # deliver, so no delivered-marker is written and every pending
            # notification flushes automatically on the first run that does
            # have credentials.
            print(
                "WARNING: notifications.channel is 'discord' but DISCORD_BOT_TOKEN / "
                "DISCORD_CHANNEL_ID are not set for this process; running the cycle "
                "without push. Pending notifications stay queued and will deliver "
                "once the environment variables are available.",
                file=sys.stderr,
            )
            return _MissingCredentialsChannel()
        return DiscordBotNotificationChannel(
            token=token,
            channel_id=channel_id,
            budgets=dict(config.portfolio.risk_budgets),
            principal=config.notifications.follow_principal_usdt,
        )
    return CollectingNotificationChannel()


class _MissingCredentialsChannel:
    """Raises on delivery so pending notifications keep their retry claim."""

    def deliver(self, event: object, *, portfolio: object | None = None) -> None:
        _ = event, portfolio
        msg = "discord credentials missing; delivery deferred"
        raise NotificationValidationError(msg)

    def send_text(self, text: str) -> None:
        _ = text
        msg = "discord credentials missing; delivery deferred"
        raise NotificationValidationError(msg)


def _push_disaster_alerts(channel: NotificationChannel, result: CycleResult) -> None:
    """Best-effort push for single-day crash warnings (no-change days included).

    Ladder-change commands ride the engine's exactly-once delivery; disaster
    alerts are same-day best-effort — a missed one is still on the dashboard.
    """

    disasters = [code for code in result.health_codes if code == DISASTER_SINGLE_DAY_DROP]
    if not disasters or result.close_time is None:
        return
    try:
        channel.send_text(
            "⚠️ 單日重挫警報\n"
            f"{result.close_time.date().isoformat()} 有標的單日跌幅達警戒門檻。\n"
            "系統的長多規則會自動減碼；請留意接下來的每日指令,不要恐慌加碼。"
        )
    except Exception as exc:  # noqa: BLE001 - alerts must never break a cycle
        print(f"disaster alert delivery failed: {type(exc).__name__}", file=sys.stderr)


def _record_exec_quotes_best_effort(
    config: AppConfig,
    rest_base_url: str,
    store: JsonlEventStore,
    close_time: datetime | None,
) -> int:
    """Gate 6 cost measurement: snapshot bid/ask right after the decision.

    Best-effort by design — a capture failure must never cost a decision day,
    and a same-day rerun dedups on the (symbol, decision day) key.
    """

    if close_time is None:
        return 0
    try:
        tickers = asyncio.run(_fetch_book_tickers(config, rest_base_url))
        return record_execution_quotes(store, tickers, close_time=close_time)
    except Exception as exc:  # noqa: BLE001 - measurement must never break a cycle
        print(f"exec quote capture failed: {type(exc).__name__}", file=sys.stderr)
        return 0


async def _fetch_book_tickers(
    config: AppConfig, rest_base_url: str
) -> tuple[BookTickerSnapshot, ...]:
    async with BinanceSpotPublicClient(
        rest_base_url=rest_base_url,
        timeout_seconds=float(config.data_source.timeout_seconds),
    ) as client:
        return await client.fetch_book_tickers(sorted(config.portfolio.risk_budgets))


@contextmanager
def _single_instance_lock(store_path: Path) -> Iterator[None]:
    """Prevent overlapping live cycles (scheduled task + manual run)."""

    lock_path = store_path.with_suffix(store_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        age_seconds = time.time() - lock_path.stat().st_mtime
        if age_seconds < _LOCK_STALE_SECONDS:
            print(
                f"another live cycle appears to be running (lock {lock_path}, "
                f"age {int(age_seconds)}s); exiting without side effects",
                file=sys.stderr,
            )
            raise SystemExit(0) from None
        # A crash left a stale lock behind; replace it and continue.
        lock_path.unlink()
        handle = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(handle, str(os.getpid()).encode("ascii"))
        os.close(handle)
        yield
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except (
        RuntimeEngineError,
        RuntimeStoreError,
        MarketDataError,
        MarketDataValidationError,
        NotificationValidationError,
        httpx.HTTPError,
    ) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        raise SystemExit(1) from None

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from src.domain import Candle, Symbol, Timeframe
from src.notify import CollectingNotificationChannel
from src.runtime import (
    JsonlEventStore,
    send_weekly_digest,
    weekly_digest_key,
)

# 2026-07-04 is a Saturday; its candle is processed on Sunday morning Taipei.
_SATURDAY_CLOSE = datetime(2026, 7, 4, 23, 59, 59, 999000, tzinfo=UTC)
_SUNDAY_CLOSE = datetime(2026, 7, 5, 23, 59, 59, 999000, tzinfo=UTC)
_WEDNESDAY_CLOSE = datetime(2026, 7, 1, 23, 59, 59, 999000, tzinfo=UTC)
_OBSERVED_AT = datetime(2026, 7, 5, 0, 5, tzinfo=UTC)

_BUDGETS = {"BTCUSDT": Decimal("0.5"), "ETHUSDT": Decimal("0.5")}


def _candle(symbol_value: str, base_asset: str, day: datetime, close: Decimal) -> Candle:
    open_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
    return Candle(
        symbol=Symbol(value=symbol_value, base_asset=base_asset, quote_asset="USDT"),
        timeframe=Timeframe("1d"),
        open_time=open_time,
        close_time=open_time + timedelta(days=1) - timedelta(milliseconds=1),
        open_price=close,
        high_price=close + Decimal("1"),
        low_price=max(close - Decimal("1"), Decimal("0.01")),
        close_price=close,
        volume=Decimal("1000"),
        is_closed=True,
    )


def _candles() -> dict[str, tuple[Candle, ...]]:
    """Daily closes 06-30..07-04: BTC 100→110, ETH 10→12."""

    start = datetime(2026, 6, 30, tzinfo=UTC)
    btc_closes = [Decimal(x) for x in ("100", "102", "104", "108", "110")]
    eth_closes = [Decimal(x) for x in ("10", "10.5", "11", "11.5", "12")]
    return {
        "BTCUSDT": tuple(
            _candle("BTCUSDT", "BTC", start + timedelta(days=index), close)
            for index, close in enumerate(btc_closes)
        ),
        "ETHUSDT": tuple(
            _candle("ETHUSDT", "ETH", start + timedelta(days=index), close)
            for index, close in enumerate(eth_closes)
        ),
    }


def _seeded_store(store_path: Path) -> JsonlEventStore:
    store = JsonlEventStore(store_path)
    store.append(
        kind="cycle",
        key="cycle:2026-06-30",
        recorded_at=datetime(2026, 7, 1, 0, 5, tzinfo=UTC),
        payload={
            "close_time": "2026-06-30T23:59:59.999000+00:00",
            "account": {"equity": "1000", "drawdown": "0"},
        },
    )
    store.append(
        kind="notification",
        key="notify:paper-runtime:BTCUSDT:2026-07-02:0.25->0.5",
        recorded_at=datetime(2026, 7, 3, 0, 5, tzinfo=UTC),
        payload={
            "symbol": "BTCUSDT",
            "action": "INCREASE_EXPOSURE",
            "previous_fraction": "0.25",
            "target_fraction": "0.5",
            "decision_time": "2026-07-02T23:59:59.999000+00:00",
        },
    )
    store.append(
        kind="notification",
        key="notify:paper-runtime:ETHUSDT:2026-06-20:0.5->0.25",
        recorded_at=datetime(2026, 6, 21, 0, 5, tzinfo=UTC),
        payload={
            "symbol": "ETHUSDT",
            "action": "DECREASE_EXPOSURE",
            "previous_fraction": "0.5",
            "target_fraction": "0.25",
            "decision_time": "2026-06-20T23:59:59.999000+00:00",
        },
    )
    store.append(
        kind="cycle",
        key="cycle:2026-07-04",
        recorded_at=datetime(2026, 7, 5, 0, 5, tzinfo=UTC),
        payload={
            "close_time": "2026-07-04T23:59:59.999000+00:00",
            "account": {"equity": "1200", "drawdown": "0.05"},
        },
    )
    return store


def _send(
    store: JsonlEventStore, channel: CollectingNotificationChannel, close_time: datetime
) -> bool:
    return send_weekly_digest(
        store=store,
        channel=channel,
        budgets=_BUDGETS,
        initial_cash=Decimal("1000"),
        candles_by_symbol=_candles(),
        close_time=close_time,
        recorded_at=_OBSERVED_AT,
    )


def test_key_exists_only_for_week_ending_candles() -> None:
    assert weekly_digest_key(_WEDNESDAY_CLOSE) is None
    saturday_key = weekly_digest_key(_SATURDAY_CLOSE)
    assert saturday_key is not None
    # The Sunday candle claims the SAME week: Monday catch-up cannot double-send.
    assert weekly_digest_key(_SUNDAY_CLOSE) == saturday_key


def test_digest_summarizes_week_and_marks_the_store(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    channel = CollectingNotificationChannel()

    assert _send(store, channel, _SATURDAY_CLOSE) is True

    assert len(channel.texts) == 1
    text = channel.texts[0]
    assert "週摘要 · 06/28～07/04 · 觀察期第 3/90 天" in text
    assert "虛擬帳戶：1,200 USDT（+20%）" in text
    # Buy and hold on the same capital: 0.5x(110/100) + 0.5x(12/10) = 1.15.
    assert "vs 買入持有 1,150 USDT（+15%）" in text
    assert "目前回撤：-5%" in text
    assert "・07/02 BTCUSDT 買入 梯位 25%→50%" in text
    # Out-of-window command stays out.
    assert "06/20" not in text
    key = weekly_digest_key(_SATURDAY_CLOSE)
    assert key is not None
    assert store.has(key)


def test_second_run_of_the_same_week_is_a_noop(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    channel = CollectingNotificationChannel()

    assert _send(store, channel, _SATURDAY_CLOSE) is True
    # Same-day rerun AND the Sunday candle both dedup on the week key.
    assert _send(store, channel, _SATURDAY_CLOSE) is False
    assert _send(store, channel, _SUNDAY_CLOSE) is False

    assert len(channel.texts) == 1


def test_weekday_candle_sends_nothing(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    channel = CollectingNotificationChannel()

    assert _send(store, channel, _WEDNESDAY_CLOSE) is False

    assert channel.texts == ()


def test_failed_send_leaves_the_week_claimable(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")

    class _DeadChannel(CollectingNotificationChannel):
        def send_text(self, text: str) -> None:
            msg = "simulated outage"
            raise ConnectionError(msg)

    with pytest.raises(ConnectionError):
        _send(store, _DeadChannel(), _SATURDAY_CLOSE)

    key = weekly_digest_key(_SATURDAY_CLOSE)
    assert key is not None
    assert not store.has(key)
    # The retry (same-day rerun or Sunday catch-up) succeeds normally.
    channel = CollectingNotificationChannel()
    assert _send(store, channel, _SATURDAY_CLOSE) is True
    assert store.has(key)


def test_no_cycles_yet_means_no_digest(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")
    channel = CollectingNotificationChannel()

    assert _send(store, channel, _SATURDAY_CLOSE) is False

    assert channel.texts == ()
    key = weekly_digest_key(_SATURDAY_CLOSE)
    assert key is not None
    assert not store.has(key)


def test_missing_benchmark_anchor_omits_buy_and_hold(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    channel = CollectingNotificationChannel()

    # Candle window that no longer covers the observation start date.
    late_candles = {symbol_value: candles[-2:] for symbol_value, candles in _candles().items()}
    sent = send_weekly_digest(
        store=store,
        channel=channel,
        budgets=_BUDGETS,
        initial_cash=Decimal("1000"),
        candles_by_symbol=late_candles,
        close_time=_SATURDAY_CLOSE,
        recorded_at=_OBSERVED_AT,
    )

    assert sent is True
    text = channel.texts[0]
    assert "虛擬帳戶：1,200 USDT（+20%）" in text
    assert "買入持有" not in text

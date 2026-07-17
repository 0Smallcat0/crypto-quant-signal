from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from scripts.log_fill import (
    append_fill,
    pending_rows,
    read_logged_fills,
    summarize,
)
from src.runtime import JsonlEventStore

_DELIVERED_AT = datetime(2026, 7, 10, 0, 6, tzinfo=UTC)


def _seeded_store(store_path: Path) -> JsonlEventStore:
    store = JsonlEventStore(store_path)
    store.append(
        kind="notification",
        key="notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
        recorded_at=datetime(2026, 7, 10, 0, 5, tzinfo=UTC),
        payload={
            "notification_id": "notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
            "symbol": "BTCUSDT",
            "action": "INCREASE_EXPOSURE",
            "decision_price": "60000",
        },
    )
    store.append(
        kind="notification_delivered",
        key="delivered:notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
        recorded_at=_DELIVERED_AT,
        payload={"notification": "notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25"},
    )
    store.append(
        kind="notification",
        key="notify:paper-runtime:ETHUSDT:2026-07-12:0.5->0.25",
        recorded_at=datetime(2026, 7, 13, 0, 5, tzinfo=UTC),
        payload={
            "notification_id": "notify:paper-runtime:ETHUSDT:2026-07-12:0.5->0.25",
            "symbol": "ETHUSDT",
            "action": "DECREASE_EXPOSURE",
            "decision_price": "2000",
        },
    )
    return store


def test_pending_lists_only_unlogged_notifications(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    csv_path = tmp_path / "manual_fills.csv"

    append_fill(
        csv_path,
        notification_id="notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
        executed_at=datetime(2026, 7, 10, 0, 18, tzinfo=UTC),
        fill_price=Decimal("60120"),
        fee_usdt=Decimal("0.15"),
        recorded_at=datetime(2026, 7, 10, 0, 19, tzinfo=UTC),
    )

    pending = pending_rows(store, csv_path)
    assert [row["notification_id"] for row in pending] == [
        "notify:paper-runtime:ETHUSDT:2026-07-12:0.5->0.25"
    ]
    # Delivery time falls back to the notification's recorded_at when no
    # delivered marker exists.
    assert pending[0]["delivered_at"] == "2026-07-13T00:05:00+00:00"


def test_rows_round_trip_through_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "manual_fills.csv"

    append_fill(
        csv_path,
        notification_id="a",
        executed_at=datetime(2026, 7, 10, 0, 18, tzinfo=UTC),
        fill_price=Decimal("60120.5"),
        fee_usdt=Decimal("0.15"),
        recorded_at=datetime(2026, 7, 10, 0, 19, tzinfo=UTC),
    )
    append_fill(
        csv_path,
        notification_id="b",
        executed_at=datetime(2026, 7, 13, 1, 0, tzinfo=UTC),
        fill_price=Decimal("1990"),
        fee_usdt=Decimal("0.10"),
        recorded_at=datetime(2026, 7, 13, 1, 1, tzinfo=UTC),
    )

    rows = read_logged_fills(csv_path)
    assert set(rows) == {"a", "b"}
    assert rows["a"]["fill_price"] == "60120.5"
    assert rows["b"]["executed_at"] == "2026-07-13T01:00:00+00:00"


def test_summary_measures_delay_signed_slippage_and_compliance(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    csv_path = tmp_path / "manual_fills.csv"

    # BTC buy executed 12 minutes after delivery, 20 bps ABOVE decision price.
    append_fill(
        csv_path,
        notification_id="notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
        executed_at=datetime(2026, 7, 10, 0, 18, tzinfo=UTC),
        fill_price=Decimal("60120"),
        fee_usdt=Decimal("0.15"),
        recorded_at=datetime(2026, 7, 10, 0, 19, tzinfo=UTC),
    )
    # ETH sell executed 55 minutes after its (fallback) delivery time,
    # 50 bps BELOW decision price -> also a positive cost.
    append_fill(
        csv_path,
        notification_id="notify:paper-runtime:ETHUSDT:2026-07-12:0.5->0.25",
        executed_at=datetime(2026, 7, 13, 1, 0, tzinfo=UTC),
        fill_price=Decimal("1990"),
        fee_usdt=Decimal("0.10"),
        recorded_at=datetime(2026, 7, 13, 1, 1, tzinfo=UTC),
    )

    summary = summarize(store, csv_path)

    assert summary["notifications_total"] == 2
    assert summary["fills_logged"] == 2
    assert summary["compliance_rate"] == 1.0
    assert summary["total_fees_usdt"] == "0.25"
    delay = summary["delay_minutes"]
    assert isinstance(delay, dict)
    assert delay["mean"] == 33.5  # (12 + 55) / 2
    slippage = summary["slippage_cost_bps"]
    assert isinstance(slippage, dict)
    assert slippage["mean"] == 35.0  # (20 + 50) / 2, both signed as cost
    assert slippage["worst"] == 50.0


def test_partial_compliance_counts_unlogged_notifications(tmp_path: Path) -> None:
    store = _seeded_store(tmp_path / "events.jsonl")
    csv_path = tmp_path / "manual_fills.csv"

    append_fill(
        csv_path,
        notification_id="notify:paper-runtime:BTCUSDT:2026-07-09:0->0.25",
        executed_at=datetime(2026, 7, 10, 0, 18, tzinfo=UTC),
        fill_price=Decimal("60120"),
        fee_usdt=Decimal("0.15"),
        recorded_at=datetime(2026, 7, 10, 0, 19, tzinfo=UTC),
    )

    summary = summarize(store, csv_path)

    assert summary["fills_logged"] == 1
    assert summary["compliance_rate"] == 0.5


def test_empty_store_and_csv_yield_null_compliance(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")

    summary = summarize(store, tmp_path / "manual_fills.csv")

    assert summary["notifications_total"] == 0
    assert summary["compliance_rate"] is None

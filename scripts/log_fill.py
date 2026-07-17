"""Manual-fill log (P2-9): the world's only dataset on following this system.

Every ladder command is executed by a human. Nothing measures the gap between
the command and what actually happened — notification-to-execution delay,
realized slippage vs the decision price, and whether the command was followed
at all. No public research has these numbers for manual signal-following; the
90-day qualification window is the one chance to collect them.

Usage:
    python -m scripts.log_fill --list-pending
    python -m scripts.log_fill <notification_id> --price 65123.5 --fee 0.65
    python -m scripts.log_fill --summary

Records append to a CSV next to the runtime store (covered by the same
off-disk backup). Append-only with one row per notification: a typo is fixed
by editing the CSV by hand, never by silently overwriting evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import mean, median

from src.runtime.store import JsonlEventStore

MANUAL_FILLS_CSV = Path("data/runtime/manual_fills.csv")
_CSV_FIELDS = ("notification_id", "executed_at", "fill_price", "fee_usdt", "recorded_at")
_BPS = Decimal("10000")


def read_logged_fills(csv_path: Path) -> dict[str, dict[str, str]]:
    """Existing rows keyed by notification id (empty when no file yet)."""

    if not csv_path.exists():
        return {}
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return {row["notification_id"]: dict(row) for row in csv.DictReader(handle)}


def append_fill(
    csv_path: Path,
    *,
    notification_id: str,
    executed_at: datetime,
    fill_price: Decimal,
    fee_usdt: Decimal,
    recorded_at: datetime,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CSV_FIELDS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(
            {
                "notification_id": notification_id,
                "executed_at": executed_at.isoformat(),
                "fill_price": str(fill_price),
                "fee_usdt": str(fee_usdt),
                "recorded_at": recorded_at.isoformat(),
            }
        )


def notifications_with_delivery(
    store: JsonlEventStore,
) -> list[tuple[dict[str, object], datetime]]:
    """Every notification payload with its best-known delivery time.

    The delivered-marker's recorded_at is when the push actually went out;
    the creation time is the fallback for anything delivered before markers
    existed. Delay measured from delivery is the honest
    "user saw it -> user acted" latency.
    """

    delivered_at: dict[str, datetime] = {}
    for event in store.events_of_kind("notification_delivered"):
        target = str(event.payload.get("notification", ""))
        delivered_at[target] = event.recorded_at
    rows: list[tuple[dict[str, object], datetime]] = []
    for event in store.events_of_kind("notification"):
        rows.append((dict(event.payload), delivered_at.get(event.key, event.recorded_at)))
    return rows


def pending_rows(store: JsonlEventStore, csv_path: Path) -> list[dict[str, str]]:
    logged = read_logged_fills(csv_path)
    pending: list[dict[str, str]] = []
    for payload, delivered in notifications_with_delivery(store):
        notification_id = str(payload["notification_id"])
        if notification_id in logged:
            continue
        pending.append(
            {
                "notification_id": notification_id,
                "symbol": str(payload.get("symbol", "")),
                "action": str(payload.get("action", "")),
                "decision_price": str(payload.get("decision_price", "")),
                "delivered_at": delivered.isoformat(),
            }
        )
    return pending


def summarize(store: JsonlEventStore, csv_path: Path) -> dict[str, object]:
    """Delay, signed slippage, and compliance over everything logged so far."""

    logged = read_logged_fills(csv_path)
    delays_minutes: list[float] = []
    slippage_bps: list[float] = []
    fees = Decimal("0")
    matched = 0
    total = 0
    for payload, delivered in notifications_with_delivery(store):
        total += 1
        row = logged.get(str(payload["notification_id"]))
        if row is None:
            continue
        matched += 1
        executed_at = datetime.fromisoformat(row["executed_at"])
        delays_minutes.append((executed_at - delivered).total_seconds() / 60)
        decision_price = Decimal(str(payload["decision_price"]))
        fill_price = Decimal(row["fill_price"])
        raw_bps = (fill_price / decision_price - 1) * _BPS
        # Signed as COST: buying above or selling below the decision price is
        # positive slippage either way.
        if str(payload.get("action")) == "DECREASE_EXPOSURE":
            raw_bps = -raw_bps
        slippage_bps.append(float(raw_bps))
        fees += Decimal(row["fee_usdt"])
    summary: dict[str, object] = {
        "notifications_total": total,
        "fills_logged": matched,
        "compliance_rate": round(matched / total, 3) if total else None,
        "total_fees_usdt": str(fees),
    }
    if delays_minutes:
        summary["delay_minutes"] = {
            "mean": round(mean(delays_minutes), 1),
            "median": round(median(delays_minutes), 1),
            "max": round(max(delays_minutes), 1),
        }
        summary["slippage_cost_bps"] = {
            "mean": round(mean(slippage_bps), 2),
            "median": round(median(slippage_bps), 2),
            "worst": round(max(slippage_bps), 2),
        }
    return summary


def _parse_utc(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        msg = "executed-at must be timezone-aware ISO-8601 (e.g. 2026-07-18T08:12:00+08:00)"
        raise SystemExit(msg)
    return parsed.astimezone(UTC)


def _parse_positive_decimal(raw: str, name: str, *, allow_zero: bool) -> Decimal:
    try:
        value = Decimal(raw)
    except InvalidOperation as error:
        raise SystemExit(f"{name} is not a number: {raw}") from error
    if value < 0 or (value == 0 and not allow_zero):
        raise SystemExit(f"{name} must be {'non-negative' if allow_zero else 'positive'}")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notification_id", nargs="?", help="Notification to log a fill for.")
    parser.add_argument("--price", help="Actual fill price in USDT.")
    parser.add_argument("--fee", help="Actual fee paid in USDT.")
    parser.add_argument(
        "--executed-at",
        help="Timezone-aware ISO-8601 execution time (default: now, UTC).",
    )
    parser.add_argument("--list-pending", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--store", default="data/runtime/events.jsonl")
    parser.add_argument("--csv", default=str(MANUAL_FILLS_CSV))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    store = JsonlEventStore(args.store)
    csv_path = Path(args.csv)

    if args.list_pending:
        print(json.dumps(pending_rows(store, csv_path), indent=2))
        return
    if args.summary:
        print(json.dumps(summarize(store, csv_path), indent=2))
        return
    if not args.notification_id or args.price is None or args.fee is None:
        print(
            "usage: log_fill <notification_id> --price P --fee F (or --list-pending / --summary)",
            file=sys.stderr,
        )
        raise SystemExit(2)

    known_ids = {
        str(payload["notification_id"]) for payload, _ in notifications_with_delivery(store)
    }
    if args.notification_id not in known_ids:
        print(
            f"unknown notification id: {args.notification_id}\n"
            "run --list-pending to see loggable notifications",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if args.notification_id in read_logged_fills(csv_path):
        print(
            f"already logged: {args.notification_id}\n"
            "evidence is append-only; fix mistakes by editing the CSV by hand",
            file=sys.stderr,
        )
        raise SystemExit(2)

    executed_at = _parse_utc(args.executed_at) if args.executed_at else datetime.now(UTC)
    append_fill(
        csv_path,
        notification_id=args.notification_id,
        executed_at=executed_at,
        fill_price=_parse_positive_decimal(args.price, "price", allow_zero=False),
        fee_usdt=_parse_positive_decimal(args.fee, "fee", allow_zero=True),
        recorded_at=datetime.now(UTC),
    )
    print(json.dumps({"logged": args.notification_id, "csv": str(csv_path)}, indent=2))


if __name__ == "__main__":
    main()

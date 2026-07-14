"""Weekly digest: a rhythm of trust for a system whose correct state is silence.

A daily trend follower goes weeks without commands, and the research behind
the product plan is blunt: silence erodes compliance faster than losses do.
Once per ISO week — on the run that processes the week-ending candle — the
runner sends one summary: scoreboard equity, the same-period buy-and-hold
comparison, current drawdown against the historical expectation, observation
progress, and the week's commands. Weekly (not daily) because the dead-man
switch already covers liveness and daily heartbeats risk notification fatigue.

Delivery is send-then-mark: a failed send leaves the idempotency marker
absent so the next run retries (the Sunday candle catches up a missed
Saturday-candle run), and a success can never double-send.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from src.domain import Candle
from src.notify import (
    DRAWDOWN_NOTE_THRESHOLD,
    HISTORICAL_MAX_DRAWDOWN_TEXT,
    INCREASE_EXPOSURE,
    NotificationChannel,
)
from src.runtime.store import JsonlEventStore

WEEKLY_DIGEST_KIND = "weekly_digest"

_PAPER_TARGET_DAYS = 90
_WEEK_DAYS = 7


def weekly_digest_key(close_time: datetime) -> str | None:
    """Idempotency key when ``close_time`` ends an ISO week, else None.

    The Saturday candle (processed Sunday morning Taipei) is the normal
    trigger; the Sunday candle maps to the SAME ISO week, so a machine that
    slept through Sunday still sends on Monday's catch-up run — and the shared
    key keeps the normal path from sending twice.
    """

    close_date = close_time.date()
    if close_date.isoweekday() < 6:
        return None
    iso = close_date.isocalendar()
    return f"{WEEKLY_DIGEST_KIND}:{iso.year}-W{iso.week:02d}"


def build_weekly_digest(
    *,
    store: JsonlEventStore,
    budgets: Mapping[str, Decimal],
    initial_cash: Decimal,
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    close_time: datetime,
) -> str | None:
    """Compose the digest text from persisted events; None before any cycle."""

    cycles = store.events_of_kind("cycle")
    if not cycles:
        return None
    account = cycles[-1].payload.get("account")
    if not isinstance(account, dict):
        return None
    equity = Decimal(str(account["equity"]))
    drawdown = Decimal(str(account["drawdown"]))

    end_date = close_time.date()
    window_start = end_date - timedelta(days=_WEEK_DAYS - 1)
    observation_days = max((close_time - cycles[0].recorded_at).days, 0)
    bh_equity = _buy_and_hold_equity(
        budgets=budgets,
        initial_cash=initial_cash,
        candles_by_symbol=candles_by_symbol,
        start_date=_first_cycle_close_date(cycles[0].payload),
        end_date=end_date,
    )

    lines = [
        f"📮 週摘要 · {window_start.strftime('%m/%d')}～{end_date.strftime('%m/%d')}"
        f" · 觀察期第 {observation_days}/{_PAPER_TARGET_DAYS} 天",
        _equity_line(equity, initial_cash, bh_equity),
        f"目前回撤：-{_pct(drawdown)}%"
        f"（歷史預期最大 {HISTORICAL_MAX_DRAWDOWN_TEXT}，深回撤屬策略正常範圍）",
    ]
    if drawdown >= DRAWDOWN_NOTE_THRESHOLD:
        lines.append("規則會在回撤中自動減碼，請勿恐慌性偏離。")
    lines.extend(_command_lines(store, window_start, end_date))
    lines.append(
        f"提醒：此策略歷史最大回撤約 {HISTORICAL_MAX_DRAWDOWN_TEXT.lstrip('~')}；"
        "若無法承受這種浮虧，請把跟單本金降到能承受的水位。"
    )
    return "\n".join(lines)


def send_weekly_digest(
    *,
    store: JsonlEventStore,
    channel: NotificationChannel,
    budgets: Mapping[str, Decimal],
    initial_cash: Decimal,
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    close_time: datetime,
    recorded_at: datetime,
) -> bool:
    """Send this week's digest if due; True only when actually sent.

    Send-then-mark keeps failures retryable and successes exactly-once: the
    marker is written only after ``send_text`` returns, so an exception here
    (webhook outage, missing credentials) leaves the week claimable.
    """

    key = weekly_digest_key(close_time)
    if key is None or store.has(key):
        return False
    text = build_weekly_digest(
        store=store,
        budgets=budgets,
        initial_cash=initial_cash,
        candles_by_symbol=candles_by_symbol,
        close_time=close_time,
    )
    if text is None:
        return False
    channel.send_text(text)
    store.append(
        kind=WEEKLY_DIGEST_KIND,
        key=key,
        recorded_at=recorded_at,
        payload={"close_time": close_time.isoformat(), "characters": len(text)},
    )
    return True


def _first_cycle_close_date(payload: Mapping[str, object]) -> date | None:
    raw = payload.get("close_time")
    if raw is None:
        return None
    return datetime.fromisoformat(str(raw)).date()


def _buy_and_hold_equity(
    *,
    budgets: Mapping[str, Decimal],
    initial_cash: Decimal,
    candles_by_symbol: Mapping[str, tuple[Candle, ...]],
    start_date: date | None,
    end_date: date,
) -> Decimal | None:
    """Same-capital benchmark: budgets bought at the first cycle's close, held.

    None when any anchor price is missing (candle window slid past the start,
    or a symbol has no candle on either date) — the digest then simply omits
    the comparison instead of guessing.
    """

    if start_date is None:
        return None
    growth = Decimal("1") - sum(budgets.values())  # unbudgeted share stays cash
    for symbol_value, budget in sorted(budgets.items()):
        candles = candles_by_symbol.get(symbol_value, ())
        start_close = _close_on(candles, start_date)
        end_close = _close_on(candles, end_date)
        if start_close is None or end_close is None or start_close <= Decimal("0"):
            return None
        growth += budget * end_close / start_close
    return initial_cash * growth


def _close_on(candles: tuple[Candle, ...], day: date) -> Decimal | None:
    for candle in candles:
        if candle.close_time.date() == day:
            return candle.close_price
    return None


def _command_lines(store: JsonlEventStore, window_start: date, end_date: date) -> list[str]:
    rows: list[str] = []
    for event in store.events_of_kind("notification"):
        payload = event.payload
        decision_date = datetime.fromisoformat(str(payload["decision_time"])).date()
        if not window_start <= decision_date <= end_date:
            continue
        verb = "買入" if payload.get("action") == INCREASE_EXPOSURE else "賣出"
        previous = _pct(Decimal(str(payload["previous_fraction"])))
        target = _pct(Decimal(str(payload["target_fraction"])))
        rows.append(
            f"・{decision_date.strftime('%m/%d')} {payload.get('symbol')}"
            f" {verb} 梯位 {previous}%→{target}%"
        )
    if not rows:
        return ["本週指令：無——維持配置是趨勢系統的正常狀態"]
    return [f"本週指令 {len(rows)} 則：", *rows]


def _equity_line(equity: Decimal, initial_cash: Decimal, bh_equity: Decimal | None) -> str:
    line = f"虛擬帳戶：{_usdt(equity)} USDT（{_signed_pct(equity, initial_cash)}）"
    if bh_equity is not None:
        line += f" vs 買入持有 {_usdt(bh_equity)} USDT（{_signed_pct(bh_equity, initial_cash)}）"
    return line


def _usdt(amount: Decimal) -> str:
    whole = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return f"{whole:,}"


def _pct(fraction: Decimal) -> str:
    return format((fraction * 100).quantize(Decimal("0.1")).normalize(), "f")


def _signed_pct(value: Decimal, base: Decimal) -> str:
    change = value / base - Decimal("1")
    sign = "+" if change >= 0 else "-"
    return f"{sign}{_pct(abs(change))}%"

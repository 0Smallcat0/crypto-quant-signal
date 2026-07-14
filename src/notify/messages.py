"""Human-readable message formatting for notification events (presentation).

Pure functions on top of the notification value objects — no config, no I/O.
The same reason-code → plain-language mapping the dashboard uses, kept here so
push channels and the UI stay consistent.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from src.notify.types import INCREASE_EXPOSURE, NotificationEvent, PortfolioTargetState

_RISK_TEXT = {
    "STALE_DATA_HALT": "資料過期，已暫停加倉",
    "DRAWDOWN_PAUSE": "回撤保護中",
    "DAILY_LOSS_PAUSE": "單日虧損保護中",
}

# Behavior anchor (P1-7): the deepest follower behavior gap sits in
# high-volatility drawdowns, so once the scoreboard drawdown crosses this
# threshold every push carries a "this is within historical range" note.
# ~52% is the registered backtest's max drawdown for the active ensemble.
DRAWDOWN_NOTE_THRESHOLD = Decimal("0.20")
HISTORICAL_MAX_DRAWDOWN_TEXT = "~52%"


def _usdt(amount: Decimal) -> str:
    whole = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return f"{whole:,}"


def _pct(fraction: Decimal) -> str:
    return format((fraction * 100).quantize(Decimal("0.1")).normalize(), "f")


def _risk_note(risk_status: str) -> str:
    if not risk_status or risk_status == "OK":
        return ""
    parts = [_RISK_TEXT.get(code, code) for code in risk_status.split(",")]
    return "\n⚠ " + "、".join(parts)


def format_portfolio_target_note(
    state: PortfolioTargetState, *, principal: Decimal | None = None
) -> str:
    """Whole-portfolio target lines that make one push message self-sufficient.

    With ``principal`` each held symbol carries a USDT amount sized to the
    follow capital; without it (generic webhook, no capital context) the note
    stays percentages only. A drawdown expectation anchor is appended once the
    scoreboard drawdown crosses ``DRAWDOWN_NOTE_THRESHOLD``.
    """

    parts: list[str] = []
    for symbol_value, weight in state.weights:
        if weight == Decimal("0"):
            parts.append(f"{symbol_value} 不持有")
        elif principal is None:
            parts.append(f"{symbol_value} {_pct(weight)}%")
        else:
            parts.append(f"{symbol_value} {_pct(weight)}%（約 {_usdt(weight * principal)} USDT）")
    lines = [
        "整體目標：" + "／".join(parts) + "／其餘現金",
        "沒跟到先前指令？把持倉調整到整體目標即可，不用逐筆補做。",
    ]
    if state.drawdown >= DRAWDOWN_NOTE_THRESHOLD:
        lines.append(
            f"目前回撤 -{_pct(state.drawdown)}%，仍在策略歷史範圍內"
            f"（回測最大 {HISTORICAL_MAX_DRAWDOWN_TEXT}）；規則會自動減碼，請勿恐慌性偏離。"
        )
    return "\n".join(lines)


def format_ladder_command(
    event: NotificationEvent,
    *,
    budget: Decimal,
    principal: Decimal,
    portfolio: PortfolioTargetState | None = None,
) -> str:
    """Format one ladder-change notification as a follow-me command message.

    ``budget`` is the asset's risk-budget fraction; ``principal`` is the user's
    stated follow capital. Amounts are the tranche and the target expressed in
    that capital, so a manual follower can act without doing the arithmetic.
    When ``portfolio`` is provided the message closes with the whole-portfolio
    target, so this single push is enough to act on without the dashboard.
    """

    is_buy = event.action == INCREASE_EXPOSURE
    verb = "買入" if is_buy else "賣出"
    delta_usdt = event.delta_fraction * budget * principal
    target_usdt = event.target_fraction * budget * principal
    account_pct = event.target_fraction * budget * Decimal("100")

    above = sum(1 for code in event.reason_codes if code.startswith("ABOVE_SMA_"))
    trend = "轉強" if is_buy else "轉弱"
    move = "提高" if is_buy else "降低"
    icon = "🟢" if is_buy else "🔴"

    if event.target_fraction == Decimal("0"):
        target_line = "目標：不持有（全部轉回 USDT）"
    else:
        target_line = (
            f"目標：持有約 {_usdt(target_usdt)} USDT"
            f"（帳戶 {account_pct.quantize(Decimal('0.1'))}%）"
        )

    message = (
        f"{icon} 今日指令 · {event.symbol_value}\n"
        f"{verb}約 {_usdt(delta_usdt)} USDT\n\n"
        f"原因：收盤站上 {above} 條均線，趨勢{trend}；曝險{move}到預算的 "
        f"{(event.target_fraction * 100).quantize(Decimal('1'))}%。\n"
        f"{target_line}\n"
        f"決策價 {event.decision_price.quantize(Decimal('0.01'))} USDT · "
        f"{event.decision_time.date().isoformat()} 收盤訊號。\n"
        f"當天內執行即可；隔天以新訊號為準，不要追價。"
        f"{_risk_note(event.risk_status)}"
    )
    if portfolio is not None:
        message += "\n\n" + format_portfolio_target_note(portfolio, principal=principal)
    return message

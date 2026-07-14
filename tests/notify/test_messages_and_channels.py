from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest

from src.notify import (
    CollectingNotificationChannel,
    DiscordBotNotificationChannel,
    NotificationEvent,
    NotificationValidationError,
    PortfolioTargetState,
    WebhookNotificationChannel,
    format_ladder_command,
    format_portfolio_target_note,
    ladder_notification_id,
)

_DT = datetime(2026, 7, 2, 23, 59, 59, 999000, tzinfo=UTC)


def _event(*, previous: str, target: str, action: str, price: str = "1700") -> NotificationEvent:
    pf, tf = Decimal(previous), Decimal(target)
    reason = ["ABOVE_SMA_20"] + (
        [f"BELOW_SMA_{n}" for n in (65, 150, 200)]
        if tf < 1
        else [f"ABOVE_SMA_{n}" for n in (65, 150, 200)]
    )
    reason.append("LADDER_UP" if tf > pf else "LADDER_DOWN")
    return NotificationEvent(
        notification_id=ladder_notification_id(
            namespace="paper-runtime",
            symbol_value="ETHUSDT",
            decision_time=_DT,
            previous_fraction=pf,
            target_fraction=tf,
        ),
        symbol_value="ETHUSDT",
        action=action,
        previous_fraction=pf,
        target_fraction=tf,
        delta_fraction=abs(tf - pf),
        decision_price=Decimal(price),
        decision_time=_DT,
        reason_codes=tuple(reason),
        risk_status="OK",
        created_at=_DT,
    )


def test_command_message_sizes_tranche_to_follow_capital() -> None:
    # 0 -> 0.25 of a 0.5 budget on 1000 principal = 125 USDT tranche, 125 target.
    event = _event(previous="0", target="0.25", action="INCREASE_EXPOSURE")

    msg = format_ladder_command(event, budget=Decimal("0.5"), principal=Decimal("1000"))

    assert "買入約 125 USDT" in msg
    assert "ETHUSDT" in msg
    assert "站上 1 條均線" in msg
    assert "不要追價" in msg


def test_command_message_scales_with_principal() -> None:
    event = _event(previous="0", target="0.25", action="INCREASE_EXPOSURE")

    msg = format_ladder_command(event, budget=Decimal("0.5"), principal=Decimal("8000"))

    assert "買入約 1,000 USDT" in msg


def test_sell_to_zero_message_says_all_to_cash() -> None:
    event = _event(previous="0.5", target="0", action="DECREASE_EXPOSURE")

    msg = format_ladder_command(event, budget=Decimal("0.5"), principal=Decimal("1000"))

    assert "賣出" in msg
    assert "不持有（全部轉回 USDT）" in msg


def test_command_message_flags_risk_status() -> None:
    event = NotificationEvent(
        notification_id="notify:x",
        symbol_value="ETHUSDT",
        action="INCREASE_EXPOSURE",
        previous_fraction=Decimal("0"),
        target_fraction=Decimal("0.25"),
        delta_fraction=Decimal("0.25"),
        decision_price=Decimal("1700"),
        decision_time=_DT,
        reason_codes=("ABOVE_SMA_20", "LADDER_UP"),
        risk_status="STALE_DATA_HALT",
        created_at=_DT,
    )

    msg = format_ladder_command(event, budget=Decimal("0.5"), principal=Decimal("1000"))

    assert "資料過期" in msg


def _portfolio(*, drawdown: str = "0.05") -> PortfolioTargetState:
    return PortfolioTargetState(
        weights=(("BTCUSDT", Decimal("0.5")), ("ETHUSDT", Decimal("0.125"))),
        drawdown=Decimal(drawdown),
    )


def test_command_message_carries_whole_portfolio_target() -> None:
    event = _event(previous="0", target="0.25", action="INCREASE_EXPOSURE")

    msg = format_ladder_command(
        event, budget=Decimal("0.5"), principal=Decimal("1000"), portfolio=_portfolio()
    )

    assert "整體目標：BTCUSDT 50%（約 500 USDT）／ETHUSDT 12.5%（約 125 USDT）／其餘現金" in msg
    assert "沒跟到先前指令" in msg
    # Calm scoreboard: no drawdown anchoring noise.
    assert "回撤" not in msg


def test_command_message_anchors_expectations_in_deep_drawdown() -> None:
    event = _event(previous="0.5", target="0.25", action="DECREASE_EXPOSURE")

    msg = format_ladder_command(
        event,
        budget=Decimal("0.5"),
        principal=Decimal("1000"),
        portfolio=_portfolio(drawdown="0.23"),
    )

    assert "目前回撤 -23%" in msg
    assert "~52%" in msg
    assert "請勿恐慌性偏離" in msg


def test_portfolio_note_marks_flat_symbols_and_skips_amounts_without_principal() -> None:
    state = PortfolioTargetState(
        weights=(("BTCUSDT", Decimal("0.5")), ("ETHUSDT", Decimal("0"))),
        drawdown=Decimal("0"),
    )

    note = format_portfolio_target_note(state)

    assert "BTCUSDT 50%" in note
    assert "ETHUSDT 不持有" in note
    assert "約" not in note


def test_discord_channel_requires_credentials() -> None:
    with pytest.raises(NotificationValidationError):
        DiscordBotNotificationChannel(
            token="", channel_id="123", budgets={}, principal=Decimal("1000")
        )


def test_discord_channel_posts_bot_message(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_post(url: str, **kwargs: object) -> httpx.Response:
        captured["url"] = url
        captured["headers"] = kwargs.get("headers")
        captured["json"] = kwargs.get("json")
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", _fake_post)
    channel = DiscordBotNotificationChannel(
        token="SECRET",
        channel_id="999",
        budgets={"ETHUSDT": Decimal("0.5")},
        principal=Decimal("1000"),
    )
    channel.deliver(_event(previous="0", target="0.25", action="INCREASE_EXPOSURE"))

    assert captured["url"] == "https://discord.com/api/v10/channels/999/messages"
    # Token lives in the header, never the URL (so error/log text can't leak it).
    assert captured["headers"] == {"Authorization": "Bot SECRET"}
    assert "SECRET" not in str(captured["url"])
    content = captured["json"]["content"]  # type: ignore[index]
    assert "買入約 125 USDT" in content


def test_discord_channel_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_post(url: str, **_kwargs: object) -> httpx.Response:
        return httpx.Response(403, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", _fake_post)
    channel = DiscordBotNotificationChannel(
        token="t", channel_id="9", budgets={}, principal=Decimal("1000")
    )

    with pytest.raises(httpx.HTTPStatusError):
        channel.send_text("hi")


def test_collecting_channel_records_text_alerts() -> None:
    channel = CollectingNotificationChannel()
    channel.send_text("⚠️ 警報")
    assert channel.texts == ("⚠️ 警報",)


def test_collecting_channel_records_portfolio_context() -> None:
    channel = CollectingNotificationChannel()
    state = _portfolio()

    channel.deliver(_event(previous="0", target="0.25", action="INCREASE_EXPOSURE"))
    channel.deliver(
        _event(previous="0.25", target="0.5", action="INCREASE_EXPOSURE"), portfolio=state
    )

    assert channel.portfolios == (None, state)


def test_webhook_delivery_appends_portfolio_without_amounts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_post(url: str, **kwargs: object) -> httpx.Response:
        captured["json"] = kwargs.get("json")
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", _fake_post)
    channel = WebhookNotificationChannel("https://hook.example/x")
    channel.deliver(
        _event(previous="0", target="0.25", action="INCREASE_EXPOSURE"), portfolio=_portfolio()
    )

    content = str(captured["json"]["content"])  # type: ignore[index]
    assert "整體目標：BTCUSDT 50%／ETHUSDT 12.5%／其餘現金" in content
    # No follow-capital context on the generic webhook: percentages only.
    assert "約" not in content


def test_webhook_channel_sends_content_shaped_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def _fake_post(url: str, **kwargs: object) -> httpx.Response:
        captured["json"] = kwargs.get("json")
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", _fake_post)
    WebhookNotificationChannel("https://hook.example/x").send_text("hello")

    assert captured["json"] == {"content": "hello"}

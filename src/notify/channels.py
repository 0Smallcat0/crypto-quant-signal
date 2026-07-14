"""Notification delivery channels for the signal runtime.

Secret handling: the Discord channel takes its bot token as a constructor
argument that callers MUST load from an environment variable — never from a
tracked config file. The token rides in the Authorization header (not the URL),
so httpx errors and logs cannot leak it.
"""

from __future__ import annotations

from decimal import Decimal

import httpx

from src.notify.messages import format_ladder_command, format_portfolio_target_note
from src.notify.types import (
    INCREASE_EXPOSURE,
    NotificationEvent,
    NotificationValidationError,
    PortfolioTargetState,
)

_DISCORD_API = "https://discord.com/api/v10"
_DISCORD_MAX_CONTENT = 2000


class CollectingNotificationChannel:
    """In-memory channel: the dashboard and replay smoke read from here."""

    def __init__(self) -> None:
        self._delivered: list[NotificationEvent] = []
        self._texts: list[str] = []
        self._portfolios: list[PortfolioTargetState | None] = []

    @property
    def delivered(self) -> tuple[NotificationEvent, ...]:
        return tuple(self._delivered)

    @property
    def texts(self) -> tuple[str, ...]:
        return tuple(self._texts)

    @property
    def portfolios(self) -> tuple[PortfolioTargetState | None, ...]:
        return tuple(self._portfolios)

    def deliver(
        self, event: NotificationEvent, *, portfolio: PortfolioTargetState | None = None
    ) -> None:
        self._delivered.append(event)
        self._portfolios.append(portfolio)

    def send_text(self, text: str) -> None:
        self._texts.append(text)


class WebhookNotificationChannel:
    """Config-gated generic webhook push (Discord-webhook compatible).

    Sends ``{"content": <human text>}`` so a Discord/Slack webhook renders it as
    a message; the event is already persisted before any delivery attempt.
    """

    def __init__(self, url: str, *, timeout_seconds: float = 10.0) -> None:
        if not url.startswith("https://"):
            msg = "webhook url must use https"
            raise NotificationValidationError(msg)
        self._url = url
        self._timeout_seconds = timeout_seconds

    def deliver(
        self, event: NotificationEvent, *, portfolio: PortfolioTargetState | None = None
    ) -> None:
        # Generic webhook has no follow-capital context; send the event as a
        # readable line without USDT sizing (the Discord bot channel sizes it).
        verb = "買入" if event.action == INCREASE_EXPOSURE else "賣出"
        text = (
            f"今日指令 · {event.symbol_value} {verb}"
            f"（目標曝險 {(event.target_fraction * 100).quantize(Decimal('1'))}% 預算）"
            f" · 決策價 {event.decision_price.quantize(Decimal('0.01'))}"
        )
        if portfolio is not None:
            text += "\n" + format_portfolio_target_note(portfolio)
        self.send_text(text)

    def send_text(self, text: str) -> None:
        response = httpx.post(
            self._url, json={"content": text[:_DISCORD_MAX_CONTENT]}, timeout=self._timeout_seconds
        )
        response.raise_for_status()


class DiscordBotNotificationChannel:
    """Push follow-me commands to a Discord channel via a bot token.

    Token and channel id come from the caller (loaded from env). Ladder
    notifications are rendered as human command messages sized to the user's
    stated follow capital.
    """

    def __init__(
        self,
        *,
        token: str,
        channel_id: str,
        budgets: dict[str, Decimal],
        principal: Decimal,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not token.strip() or not channel_id.strip():
            msg = "discord token and channel_id must not be empty"
            raise NotificationValidationError(msg)
        self._token = token
        self._channel_id = channel_id
        self._budgets = dict(budgets)
        self._principal = principal
        self._timeout_seconds = timeout_seconds

    def deliver(
        self, event: NotificationEvent, *, portfolio: PortfolioTargetState | None = None
    ) -> None:
        budget = self._budgets.get(event.symbol_value, Decimal("0"))
        self.send_text(
            format_ladder_command(
                event, budget=budget, principal=self._principal, portfolio=portfolio
            )
        )

    def send_text(self, text: str) -> None:
        response = httpx.post(
            f"{_DISCORD_API}/channels/{self._channel_id}/messages",
            headers={"Authorization": f"Bot {self._token}"},
            json={"content": text[:_DISCORD_MAX_CONTENT]},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

"""Notification package entry points."""

from src.notify.channels import (
    CollectingNotificationChannel,
    DiscordBotNotificationChannel,
    WebhookNotificationChannel,
)
from src.notify.messages import (
    DRAWDOWN_NOTE_THRESHOLD,
    HISTORICAL_MAX_DRAWDOWN_TEXT,
    format_ladder_command,
    format_portfolio_target_note,
)
from src.notify.types import (
    DECREASE_EXPOSURE,
    INCREASE_EXPOSURE,
    NotificationChannel,
    NotificationEvent,
    NotificationValidationError,
    PortfolioTargetState,
    ladder_notification_id,
)

__all__ = [
    "DECREASE_EXPOSURE",
    "DRAWDOWN_NOTE_THRESHOLD",
    "HISTORICAL_MAX_DRAWDOWN_TEXT",
    "INCREASE_EXPOSURE",
    "CollectingNotificationChannel",
    "DiscordBotNotificationChannel",
    "NotificationChannel",
    "NotificationEvent",
    "NotificationValidationError",
    "PortfolioTargetState",
    "WebhookNotificationChannel",
    "format_ladder_command",
    "format_portfolio_target_note",
    "ladder_notification_id",
]

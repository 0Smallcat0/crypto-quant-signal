"""Read-only dashboard API entry points."""

from src.api.app import create_dashboard_app
from src.api.page import DASHBOARD_HTML

__all__ = [
    "DASHBOARD_HTML",
    "create_dashboard_app",
]

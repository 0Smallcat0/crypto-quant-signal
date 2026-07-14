"""Signal runtime composition layer: notify the human, keep the scoreboard honest."""

from src.runtime.digest import (
    WEEKLY_DIGEST_KIND,
    build_weekly_digest,
    send_weekly_digest,
    weekly_digest_key,
)
from src.runtime.engine import (
    STALE_DATA_HALT,
    WARMUP_INSUFFICIENT_HISTORY,
    SignalRuntime,
)
from src.runtime.quotes import EXEC_QUOTE_KIND, record_execution_quotes
from src.runtime.replay import ReplaySummary, run_replay
from src.runtime.store import JsonlEventStore, RuntimeStoreError, StoredEvent
from src.runtime.types import CycleResult, RuntimeEngineError, RuntimeParameters

__all__ = [
    "EXEC_QUOTE_KIND",
    "STALE_DATA_HALT",
    "WARMUP_INSUFFICIENT_HISTORY",
    "WEEKLY_DIGEST_KIND",
    "CycleResult",
    "JsonlEventStore",
    "ReplaySummary",
    "RuntimeEngineError",
    "RuntimeParameters",
    "RuntimeStoreError",
    "SignalRuntime",
    "StoredEvent",
    "build_weekly_digest",
    "record_execution_quotes",
    "run_replay",
    "send_weekly_digest",
    "weekly_digest_key",
]

"""Signal runtime composition layer: notify the human, keep the scoreboard honest."""

from src.runtime.engine import (
    STALE_DATA_HALT,
    WARMUP_INSUFFICIENT_HISTORY,
    SignalRuntime,
)
from src.runtime.replay import ReplaySummary, run_replay
from src.runtime.store import JsonlEventStore, RuntimeStoreError, StoredEvent
from src.runtime.types import CycleResult, RuntimeEngineError, RuntimeParameters

__all__ = [
    "STALE_DATA_HALT",
    "WARMUP_INSUFFICIENT_HISTORY",
    "CycleResult",
    "JsonlEventStore",
    "ReplaySummary",
    "RuntimeEngineError",
    "RuntimeParameters",
    "RuntimeStoreError",
    "SignalRuntime",
    "StoredEvent",
    "run_replay",
]

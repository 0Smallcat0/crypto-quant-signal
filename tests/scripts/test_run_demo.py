from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from scripts.run_demo import run_demo_replay
from src.runtime import JsonlEventStore


def test_bundled_demo_replays_offline_into_a_fresh_store(tmp_path: Path) -> None:
    store_dir = tmp_path / "demo-store"

    summary, store_path, config = run_demo_replay(store_dir=store_dir)

    # The bundled 912-candle window leaves 200 warmup closes and decides daily.
    assert summary.cycles_processed > 600
    assert summary.notifications > 0
    assert summary.fills > 0
    assert summary.final_equity is not None
    assert summary.final_equity > Decimal("0")
    store = JsonlEventStore(store_path)
    assert store.count_of_kind("cycle") == summary.cycles_processed
    assert store.count_of_kind("notification") == summary.notifications
    # Demo always targets its own store directory, never the live runtime path.
    assert store_path.parent == store_dir
    assert store_path.resolve() != Path(config.storage.runtime_events_path).resolve()


def test_demo_rerun_rebuilds_from_scratch(tmp_path: Path) -> None:
    store_dir = tmp_path / "demo-store"

    first, _, _ = run_demo_replay(store_dir=store_dir)
    second, store_path, _ = run_demo_replay(store_dir=store_dir)

    # A stale store would make every cycle an idempotent no-op; the wipe
    # guarantees the second run replays the identical full history.
    assert second.cycles_processed == first.cycles_processed
    assert second.final_equity == first.final_equity
    assert JsonlEventStore(store_path).count_of_kind("cycle") == second.cycles_processed

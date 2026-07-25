"""Forward-only shadow track for the best-evidenced candidate (trial 88).

Computes the Donchian 10/20/55/110 mid-channel ensemble on fresh BTC/ETH
daily candles and appends one row per decision day to an append-only
JSONL. Records nothing about the past: the notional equity path starts at
the track's first day, so every number this file ever reports is
out-of-sample by construction.

Boundaries this script respects:
- It NEVER touches the live runtime, its config, or its event store. The
  live qualification contract is frozen; this is a parallel observer.
- It places no orders and emits no instructions to the operator.
- Signal warmup reads prior closes (exactly as any live strategy must),
  but performance is accounted only from the track start date onward,
  which is after the sealed holdout window ends (2026-07-01). No holdout
  performance is measured, so gate 5 is untouched.

Usage:
    python -m scripts.shadow_signal            # fetch, decide, append
    python -m scripts.shadow_signal --summary  # print the track so far
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.config import load_config
from src.data import (
    BinanceSpotPublicClient,
    first_passing_public_rest_base_url,
    run_public_rest_smoke,
    symbol_from_binance_native,
)
from src.domain import Candle, Timeframe
from src.strategies import evaluate_donchian_ensemble

SYMBOLS = ("BTCUSDT", "ETHUSDT")
BUDGET = Decimal("0.5")  # both tracked configs use 0.5 per symbol
FETCH_LIMIT = 400  # > longest window + slack

# One entry per tracked configuration. Tracks are independent: adding a
# new one never disturbs an existing record, which is what keeps each
# track's forward history honest.
TRACKS: tuple[dict[str, Any], ...] = (
    {
        "name": "trial88",
        "source_trial": 88,
        "windows": (10, 20, 55, 110),
        "exit": "mid_channel",
        "atr_window": 14,
        "atr_multiple": Decimal("3"),
        "path": Path("data/runtime/shadow_trial88.jsonl"),
    },
    {
        "name": "trial118",
        "source_trial": 118,
        "windows": (10, 20, 55, 110),
        "exit": "atr_channel",
        "atr_window": 14,
        "atr_multiple": Decimal("2"),
        "path": Path("data/runtime/shadow_trial118.jsonl"),
    },
)


async def fetch_candles(config: Any, timeout_seconds: float) -> dict[str, tuple[Candle, ...]]:
    results = run_public_rest_smoke(
        config.data_source.rest_base_url_candidates,
        timeout_seconds=timeout_seconds,
    )
    base_url = first_passing_public_rest_base_url(results)
    if base_url is None:
        raise SystemExit("no reachable public REST base url; shadow track skipped")
    observed_at = datetime.now(UTC)
    out: dict[str, tuple[Candle, ...]] = {}
    async with BinanceSpotPublicClient(
        rest_base_url=base_url, timeout_seconds=timeout_seconds
    ) as client:
        for symbol_value in SYMBOLS:
            out[symbol_value] = await client.fetch_historical_candles(
                symbol=symbol_from_binance_native(symbol_value),
                timeframe=Timeframe("1d"),
                limit=FETCH_LIMIT,
                received_at=observed_at,
            )
    return out


def load_track(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def decide(
    candles: tuple[Candle, ...], track: dict[str, Any]
) -> tuple[Decimal, tuple[str, ...], tuple[bool, ...]]:
    """Replay the state machine over the fetched window to today's close.

    Replaying from the warmup floor each run keeps the decision a pure
    function of price history — no hidden state, identical output on a
    re-run, which is what makes the track auditable.
    """

    closed = tuple(candle for candle in candles if candle.is_closed)
    windows = track["windows"]
    states: tuple[bool, ...] | None = None
    fraction = Decimal("0")
    codes: tuple[str, ...] = ()
    for index in range(max(windows), len(closed)):
        fraction, codes, states = evaluate_donchian_ensemble(
            closed,
            index,
            windows=windows,
            exit_mode=track["exit"],
            previous_states=states,
            atr_window=track["atr_window"],
            atr_multiple=track["atr_multiple"],
        )
    return fraction, codes, states or (False,) * 4


def summarize(name: str, rows: list[dict[str, Any]]) -> None:
    print(f"=== {name} ===")
    if not rows:
        print("shadow track is empty")
        return
    print(f"days recorded  : {len(rows)}")
    print(f"first day      : {rows[0]['date']}")
    print(f"last day       : {rows[-1]['date']}")
    print(f"notional equity: {rows[-1]['equity']} (start 1000)")
    for symbol_value in SYMBOLS:
        exposures = [float(row["exposure"][symbol_value]) for row in rows]
        share = sum(1 for value in exposures if value > 0) / len(exposures)
        print(
            f"{symbol_value}: mean exposure {sum(exposures) / len(exposures):.3f}, "
            f"days invested {share:.1%}, latest {exposures[-1]:.2f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/runtime/paper_runtime.yaml")
    parser.add_argument("--summary", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.summary:
        for track in TRACKS:
            summarize(track["name"], load_track(track["path"]))
        return

    config = load_config(Path(args.config))
    candles_by_symbol = asyncio.run(
        fetch_candles(config, float(config.data_source.timeout_seconds))
    )
    for track in TRACKS:
        append_day(track, candles_by_symbol)


def append_day(track: dict[str, Any], candles_by_symbol: dict[str, tuple[Candle, ...]]) -> None:
    rows = load_track(track["path"])
    decisions: dict[str, Decimal] = {}
    closes: dict[str, str] = {}
    reasons: dict[str, list[str]] = {}
    decision_date = ""
    for symbol_value, candles in candles_by_symbol.items():
        closed = tuple(candle for candle in candles if candle.is_closed)
        fraction, codes, _ = decide(candles, track)
        decisions[symbol_value] = fraction
        closes[symbol_value] = str(closed[-1].close_price)
        reasons[symbol_value] = list(codes)
        decision_date = max(decision_date, closed[-1].open_time.date().isoformat())

    if rows and str(rows[-1]["date"]) >= decision_date:
        print(f"{track['name']}: already recorded through {rows[-1]['date']}")
        return

    # Notional mark-to-market: yesterday's exposure earns today's return.
    equity = Decimal(str(rows[-1]["equity"])) if rows else Decimal("1000")
    if rows:
        previous = rows[-1]
        day_return = Decimal("0")
        for symbol_value in SYMBOLS:
            prior_close = Decimal(str(previous["close"][symbol_value]))
            held = Decimal(str(previous["exposure"][symbol_value])) * BUDGET
            if prior_close > 0:
                move = Decimal(closes[symbol_value]) / prior_close - Decimal("1")
                day_return += held * move
        equity = equity * (Decimal("1") + day_return)

    row = {
        "date": decision_date,
        "recorded_at": datetime.now(UTC).isoformat(),
        "strategy": "donchian_breakout_ensemble",
        "config": {
            "windows": list(track["windows"]),
            "exit": track["exit"],
            "atr_window": track["atr_window"],
            "atr_multiple": str(track["atr_multiple"]),
            "source_trial": track["source_trial"],
        },
        "exposure": {symbol: str(value) for symbol, value in decisions.items()},
        "close": closes,
        "reason_codes": reasons,
        "equity": str(equity),
    }
    path = track["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"{track['name']}: appended {row['date']} exposure={row['exposure']}")


if __name__ == "__main__":
    main()

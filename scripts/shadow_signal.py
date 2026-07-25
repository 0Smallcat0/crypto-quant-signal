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
WINDOWS = (10, 20, 55, 110)
EXIT_MODE = "mid_channel"
BUDGET = Decimal("0.5")  # trial 88 risk budgets: 0.5 per symbol
TRACK_PATH = Path("data/runtime/shadow_trial88.jsonl")
FETCH_LIMIT = 400  # > longest window + slack


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


def load_track() -> list[dict[str, Any]]:
    if not TRACK_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in TRACK_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def decide(candles: tuple[Candle, ...]) -> tuple[Decimal, tuple[str, ...], tuple[bool, ...]]:
    """Replay the state machine over the fetched window to today's close.

    Replaying from the warmup floor each run keeps the decision a pure
    function of price history — no hidden state, identical output on a
    re-run, which is what makes the track auditable.
    """

    closed = tuple(candle for candle in candles if candle.is_closed)
    states: tuple[bool, ...] | None = None
    fraction = Decimal("0")
    codes: tuple[str, ...] = ()
    for index in range(max(WINDOWS), len(closed)):
        fraction, codes, states = evaluate_donchian_ensemble(
            closed, index, windows=WINDOWS, exit_mode=EXIT_MODE, previous_states=states
        )
    return fraction, codes, states or (False,) * 4


def summarize(rows: list[dict[str, Any]]) -> None:
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
    rows = load_track()
    if args.summary:
        summarize(rows)
        return

    config = load_config(Path(args.config))
    candles_by_symbol = asyncio.run(
        fetch_candles(config, float(config.data_source.timeout_seconds))
    )

    decisions: dict[str, Decimal] = {}
    closes: dict[str, str] = {}
    reasons: dict[str, list[str]] = {}
    decision_date = ""
    for symbol_value, candles in candles_by_symbol.items():
        closed = tuple(candle for candle in candles if candle.is_closed)
        fraction, codes, _ = decide(candles)
        decisions[symbol_value] = fraction
        closes[symbol_value] = str(closed[-1].close_price)
        reasons[symbol_value] = list(codes)
        decision_date = max(decision_date, closed[-1].open_time.date().isoformat())

    if rows and str(rows[-1]["date"]) >= decision_date:
        print(f"already recorded through {rows[-1]['date']}; nothing to append")
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
            "windows": list(WINDOWS),
            "exit": EXIT_MODE,
            "source_trial": 88,
        },
        "exposure": {symbol: str(value) for symbol, value in decisions.items()},
        "close": closes,
        "reason_codes": reasons,
        "equity": str(equity),
    }
    TRACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TRACK_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps(row, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Slice full-history candle files at the locked holdout boundary.

Reads every ``<SYMBOL>_<TF>.jsonl`` in the source directory, keeps only
candles that CLOSE strictly before the holdout_start recorded in
``docs/reports/research/holdout_lock.json`` (holdout_start is the close_time
of the first holdout candle), and writes the result into the pre-holdout
directory. Research (gates 1-4, family experiments) must only
ever read the pre-holdout directory; the full-history directory exists for
the single holdout spend and live runtime.

Usage:
    python -m scripts.slice_preholdout            # data/candles -> data/candles_preholdout
    python -m scripts.slice_preholdout --source X --dest Y --holdout Z
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from src.data import read_candles_jsonl, write_candles_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="data/candles")
    parser.add_argument("--dest", default="data/candles_preholdout")
    parser.add_argument("--holdout", default="docs/reports/research/holdout_lock.json")
    return parser.parse_args()


def holdout_start(lock_path: Path) -> datetime:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    raw = lock.get("holdout_start")
    if not isinstance(raw, str):
        raise SystemExit(f"{lock_path} has no holdout_start")
    return datetime.fromisoformat(raw)


def main() -> None:
    args = parse_args()
    boundary = holdout_start(Path(args.holdout))
    source = Path(args.source)
    dest = Path(args.dest)
    files = sorted(source.glob("*_1d.jsonl"))
    if not files:
        raise SystemExit(f"no *_1d.jsonl files under {source}")
    for file_path in files:
        candles = read_candles_jsonl(file_path)
        kept = tuple(candle for candle in candles if candle.close_time < boundary)
        if not kept:
            print(f"{file_path.name}: 0 pre-holdout candles, skipped")
            continue
        write_candles_jsonl(kept, dest / file_path.name)
        print(
            f"{file_path.name}: {len(candles)} -> {len(kept)} "
            f"(last kept {kept[-1].open_time.date().isoformat()})"
        )


if __name__ == "__main__":
    main()

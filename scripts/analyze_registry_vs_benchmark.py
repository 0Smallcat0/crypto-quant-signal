"""Across every registered trial: how many beat simply holding?

Zero-cost diagnostic. Every registry row already carries both
`final_equity` and `benchmark_final_equity` over the same window and
universe, and no document has compared them.

This is the sharpest available test of whether the crypto result is an
effect or a selection. If one configuration beats buy-and-hold and its
neighbours do not, the winner is a draw from a distribution centred below
the benchmark and the search found a tail. If most of a family beats it,
the effect survives the parameter choice and does not depend on having
picked correctly.

Reads the registry only: no backtest, no new row, no holdout contact.

Usage:
    python -m scripts.analyze_registry_vs_benchmark
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from dataclasses import dataclass
from pathlib import Path

_REGISTRY = Path("docs/reports/research/trial_registry.jsonl")

# Families are identified from the operator note, which is the only field
# that records what was actually run: the parameters block was a hardcoded
# constant until 2026-07-26.
_FAMILIES = (
    ("donchian", ("donchian",)),
    ("cross-sectional momentum", ("cs-momentum", "cross-sectional", "cs_")),
    ("volatility target", ("vol-target", "vol_target", "volatility")),
    ("regime gate", ("gate",)),
    ("trend factor", ("trendfactor", "trend-factor")),
)


@dataclass(frozen=True, slots=True)
class Row:
    trial_id: int
    note: str
    system: float
    benchmark: float
    sharpe: float
    days: int

    @property
    def ratio(self) -> float:
        return self.system / self.benchmark if self.benchmark > 0 else 0.0

    @property
    def beat(self) -> bool:
        return self.system > self.benchmark

    def family(self) -> str:
        """Family key, including the experiment that ran it.

        Grouping on the strategy name alone pooled experiment 7 (BTC/ETH,
        8 configs) with experiment 8 (13 symbols, 8 configs) and produced a
        meaningless "50% beat the benchmark": every exp-7 arm beat it and
        every exp-8 arm lost. Different universes are different families.
        """

        lowered = self.note.lower()
        match = re.search(r"\bexp (\d+)\b", lowered)
        suffix = f" exp{match.group(1)}" if match else ""
        for name, needles in _FAMILIES:
            if any(needle in lowered for needle in needles):
                return f"{name}{suffix}"
        return f"other{suffix}"


def read_rows(path: Path) -> list[Row]:
    rows: list[Row] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        metrics = payload["metrics"]
        benchmark = metrics.get("benchmark_final_equity")
        if benchmark is None:
            continue
        rows.append(
            Row(
                trial_id=int(payload["trial_id"]),
                note=str(payload.get("operator_note", "")),
                system=float(metrics["final_equity"]),
                benchmark=float(benchmark),
                sharpe=float(metrics["annualized_sharpe"]),
                days=int(float(metrics["observation_days"])),
            )
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(_REGISTRY))
    parser.add_argument("--highlight", type=int, default=88, help="Trial to locate in its family.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(Path(args.registry))
    if not rows:
        print("no registry rows carry a benchmark")
        return
    print(f"registry rows with a benchmark: {len(rows)}")

    beat = [row for row in rows if row.beat]
    ratios = [row.ratio for row in rows]
    print(f"beat buy-and-hold: {len(beat)} / {len(rows)} ({len(beat) / len(rows):.1%})")
    print(f"median system/benchmark ratio: {statistics.median(ratios):.3f}")
    print(f"mean   system/benchmark ratio: {statistics.fmean(ratios):.3f}")

    print(f"\n{'family':28s}{'n':>5}{'beat':>7}{'share':>9}{'median ratio':>14}")
    families: dict[str, list[Row]] = {}
    for row in rows:
        families.setdefault(row.family(), []).append(row)
    for name in sorted(families, key=lambda key: -len(families[key])):
        group = families[name]
        wins = sum(1 for row in group if row.beat)
        median = statistics.median(row.ratio for row in group)
        print(f"{name:28s}{len(group):5d}{wins:7d}{wins / len(group):9.1%}{median:14.3f}")

    target = next((row for row in rows if row.trial_id == args.highlight), None)
    if target is None:
        return
    peers = families.get(target.family(), [])
    ranked = sorted(peers, key=lambda row: -row.ratio)
    position = ranked.index(target) + 1
    print(
        f"\ntrial {target.trial_id} in family '{target.family()}': "
        f"ratio {target.ratio:.3f}, rank {position} of {len(ranked)}"
    )
    print(f"family ratio spread: best {ranked[0].ratio:.3f}, worst {ranked[-1].ratio:.3f}")
    beaters = sum(1 for row in peers if row.beat)
    print(f"family members beating buy-and-hold: {beaters} / {len(peers)}")


if __name__ == "__main__":
    main()

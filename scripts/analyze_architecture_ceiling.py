"""Diagnostic: the highest annualized Sharpe this engine can express at all.

Iteration 64 measured what gate 3 REQUIRES of a new parameter family — a
candidate column near annualized Sharpe 1.63 — and observed that 0 of 133
registered trials reach it. It never asked the opposite question: **is 1.63
reachable by anything this repository can build?** That is the last input
the operator needs to decide the P3 override, which iteration 64 left as
the only unblocking lever still open.

This script answers it by exhaustive hindsight search. For each strategy
architecture the engine can express, it sweeps the architecture's whole
parameter grid over the registry's own universes and window and keeps the
maximum. The maximum of a hindsight sweep is an UPPER BOUND on what any
honest family of that architecture could produce: an honest family picks
its winner without seeing the future, and cannot beat the arm picked with
full hindsight over a superset of its own grid.

**Registers nothing.** It imports ``src.backtest.engine.run_backtest``
only — never ``run_registered_backtest`` and never ``append_trial`` — so N
stays at 133, no candidate column is created, no return series is written
next to the registry, and no gate report is regenerated. Sweep output goes
to the gitignored ``data/`` tree.

**Nothing found here may be nominated.** By construction the argmax of a
hindsight sweep is the most overfit object the grid contains; its only
legitimate use is as a bound. The ``stop-condition`` mode exists to show
what that bound does against gates 3 and 4, not to propose a candidate.

Usage:
    python -m scripts.analyze_architecture_ceiling --mode validate
    python -m scripts.analyze_architecture_ceiling --mode pbo-validate
    python -m scripts.analyze_architecture_ceiling --mode sweep --grid cs-13
    python -m scripts.analyze_architecture_ceiling --mode sweep --grid donchian-btceth
    python -m scripts.analyze_architecture_ceiling --mode sweep --grid donchian-btceth-atr
    python -m scripts.analyze_architecture_ceiling --mode sweep --grid donchian-13
    python -m scripts.analyze_architecture_ceiling --mode stop-condition --grid cs-13

``validate`` and ``pbo-validate`` come first and are not optional: the
sweep's numbers mean nothing until the engine reproduces four registered
trials exactly and the vectorised PBO reproduces the recorded gate-report
values. Both are run and recorded in
``docs/research/ARCHITECTURE_CEILING_2026-09-22.md``.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import time
from collections.abc import Iterator, Mapping, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any

from scripts.run_cs_family import UNIVERSE as UNIVERSE_13
from src.backtest import BacktestParameters
from src.backtest.engine import run_backtest
from src.backtest.registry import TrialRecord
from src.backtest.validation import deflated_sharpe_ratio, non_annualized_sharpe_variance
from src.config import load_config
from src.data import candle_file_name, read_candles_jsonl
from src.domain import Candle

CONFIG_PATH = Path("configs/runtime/paper_runtime.yaml")
CANDLES_DIR = Path("data/candles_preholdout")
OUT_DIR = Path("data/research/ceiling")
RESEARCH_DIR = Path("docs/reports/research")
UNIVERSE_BTCETH = ("BTCUSDT", "ETHUSDT")

# Gate constants, copied from scripts/run_gate_report.py so this diagnostic
# cannot silently drift from the gate it is quoting.
CSCV_BLOCKS = 16
PBO_MAX = 0.05
DSR_MIN = 0.95

# --- Donchian ensemble grid -------------------------------------------------
# The channel windows are the family's only shape parameters. The engine's
# snapshot warmup is a fixed 200 closes (src/features/daily_trend.py), so the
# decision-day set — and therefore the 2676-day registry window — is identical
# for every window set, including sets longer than 200 (a window with fewer
# prior closes than its length simply stays OFF). Alignment with the registry
# is exact by construction, not by trimming.
DC_WINDOWS_FINE = (
    5,
    7,
    10,
    13,
    16,
    20,
    25,
    30,
    40,
    50,
    65,
    80,
    100,
    110,
    130,
    150,
    175,
    200,
    250,
    300,
)
DC_WINDOWS_COARSE = (5, 10, 16, 25, 40, 55, 80, 110, 150, 200, 250, 300)
DC_ATR_WINDOWS = (7, 14, 28)
DC_ATR_MULTIPLES = ("1", "1.5", "2", "3", "4", "6")
# Stage 1 is exhaustive over the window space — the family's only shape
# dimension — at a representative exit subset; stage 2 then runs the FULL
# exit/ATR grid over the stage-1 leaders, so the ATR dimension is covered
# exhaustively exactly where it could change the maximum. Splitting it this
# way costs ~76 minutes against ~215 for the full cross product, which does
# not fit one iteration.
DC_STAGE1_ATR_WINDOWS = (14, 28)
DC_STAGE1_ATR_MULTIPLES = ("2", "4")
DC_STAGE2_TOP = 250

# --- Cross-sectional momentum grid -----------------------------------------
CS_TOP_K = (1, 2, 3, 4, 5, 6, 8, 10, 13)
CS_LOOKBACKS = (20, 30, 45, 60, 90, 120, 150, 180, 240, 300, 365)
CS_CADENCES = ("daily", "weekly", "monthly")
CS_FILTERS = (False, True)
CS_GATES: tuple[int | None, ...] = (None, 50, 100, 150, 200)
CS_DECISION_START = "2018-03-05"

_WORKER_CANDLES: dict[str, tuple[Candle, ...]] = {}
_WORKER_BASE: dict[str, Any] = {}


def _load_candles(symbols: Sequence[str]) -> dict[str, tuple[Candle, ...]]:
    config = load_config(CONFIG_PATH)
    timeframe = config.data_source.timeframe
    return {
        symbol: read_candles_jsonl(CANDLES_DIR / candle_file_name(symbol, timeframe))
        for symbol in symbols
    }


def _base_kwargs(symbols: Sequence[str]) -> dict[str, Any]:
    config = load_config(CONFIG_PATH)
    budget = Decimal(1) / Decimal(len(symbols))
    return {
        "risk_budgets": dict.fromkeys(symbols, budget),
        "initial_cash": config.account.initial_cash,
        "account_id": config.account.account_id,
        "fee_bps": config.execution.fee_bps,
        "slippage_bps": config.execution.slippage_bps,
        "quantity_step": config.execution.quantity_step,
        "price_tick": config.execution.price_tick,
        "min_notional_usdt": config.risk.min_notional_usdt,
        "max_drawdown_fraction": config.risk.max_drawdown_fraction,
        "daily_loss_pause_fraction": config.risk.daily_loss_pause_fraction,
        "disaster_single_day_drop_fraction": config.risk.disaster_single_day_drop_fraction,
        "stale_data_max_age_seconds": config.risk.stale_data_max_age_seconds,
    }


def _parameters(symbols: Sequence[str], arm: Mapping[str, Any]) -> BacktestParameters:
    kwargs = dict(_base_kwargs(symbols))
    kwargs.update(_arm_to_engine_kwargs(arm))
    return BacktestParameters(**kwargs)


def _arm_to_engine_kwargs(arm: Mapping[str, Any]) -> dict[str, Any]:
    """Translate one JSON-safe arm description into engine parameters."""

    family = arm["family"]
    if family == "donchian":
        kwargs: dict[str, Any] = {
            "strategy_name": "donchian_breakout_ensemble",
            "dc_windows": tuple(arm["windows"]),
            "dc_exit": arm["exit"],
        }
        if arm["exit"] == "atr_channel":
            kwargs["dc_atr_window"] = int(arm["atr_window"])
            kwargs["dc_atr_multiple"] = Decimal(str(arm["atr_multiple"]))
        if arm.get("staggered"):
            kwargs["allow_staggered_listings"] = True
        return kwargs
    if family == "cs":
        cs_kwargs: dict[str, Any] = {
            "strategy_name": "cross_sectional_momentum",
            "cs_top_k": int(arm["top_k"]),
            "cs_lookback_days": int(arm["lookback"]),
            "cs_rebalance_cadence": arm["cadence"],
            "cs_absolute_filter": bool(arm["absolute_filter"]),
            "cs_min_pool_size": 4,
            "cs_decision_start": arm.get("decision_start"),
        }
        if arm.get("gate_sma") is not None:
            cs_kwargs["cs_gate_sma_window"] = int(arm["gate_sma"])
            cs_kwargs["cs_gate_basis"] = "btc"
            cs_kwargs["cs_gate_hysteresis"] = Decimal("0.02")
            cs_kwargs["cs_gate_cadence"] = "daily"
        return cs_kwargs
    msg = f"unknown arm family: {family}"
    raise ValueError(msg)


def _worker_init(symbols: tuple[str, ...]) -> None:
    _WORKER_CANDLES.update(_load_candles(symbols))
    _WORKER_BASE.update(_base_kwargs(symbols))


def _worker_run(arm: dict[str, Any]) -> dict[str, Any]:
    kwargs = dict(_WORKER_BASE)
    kwargs.update(_arm_to_engine_kwargs(arm))
    try:
        report = run_backtest(_WORKER_CANDLES, parameters=BacktestParameters(**kwargs))
    except Exception as error:  # noqa: BLE001 - a failing arm must not kill the sweep
        return {**arm, "error": f"{type(error).__name__}: {error}"}
    metrics = report.metrics
    return {
        **arm,
        "sharpe": float(metrics.annualized_sharpe),
        "max_drawdown": float(metrics.max_drawdown_fraction),
        "final_equity": float(metrics.final_equity),
        "trades": int(metrics.trade_count),
        "turnover": float(metrics.annualized_turnover),
        "observation_days": int(metrics.observation_days),
    }


def _donchian_variants(
    combo: Sequence[int],
    *,
    staggered: bool,
    atr_windows: Sequence[int],
    atr_multiples: Sequence[str],
) -> Iterator[dict[str, Any]]:
    for exit_mode in ("half_low", "mid_channel"):
        yield {
            "family": "donchian",
            "windows": list(combo),
            "exit": exit_mode,
            "staggered": staggered,
        }
    for atr_window in atr_windows:
        for atr_multiple in atr_multiples:
            yield {
                "family": "donchian",
                "windows": list(combo),
                "exit": "atr_channel",
                "atr_window": atr_window,
                "atr_multiple": atr_multiple,
                "staggered": staggered,
            }


def _donchian_arms(
    windows_grid: Sequence[int],
    *,
    staggered: bool,
    atr_windows: Sequence[int] = DC_ATR_WINDOWS,
    atr_multiples: Sequence[str] = DC_ATR_MULTIPLES,
) -> Iterator[dict[str, Any]]:
    for combo in itertools.combinations(sorted(windows_grid), 4):
        yield from _donchian_variants(
            combo,
            staggered=staggered,
            atr_windows=atr_windows,
            atr_multiples=atr_multiples,
        )


def _cs_arms() -> Iterator[dict[str, Any]]:
    for top_k, lookback, cadence, absolute_filter, gate in itertools.product(
        CS_TOP_K, CS_LOOKBACKS, CS_CADENCES, CS_FILTERS, CS_GATES
    ):
        yield {
            "family": "cs",
            "top_k": top_k,
            "lookback": lookback,
            "cadence": cadence,
            "absolute_filter": absolute_filter,
            "gate_sma": gate,
            "decision_start": CS_DECISION_START,
        }


GRIDS: dict[str, tuple[tuple[str, ...], str]] = {
    "donchian-btceth": (UNIVERSE_BTCETH, "donchian"),
    "donchian-btceth-atr": (UNIVERSE_BTCETH, "donchian"),
    "donchian-13": (tuple(UNIVERSE_13), "donchian"),
    "cs-13": (tuple(UNIVERSE_13), "cs"),
}


def _stage2_window_sets(stage1_path: Path, *, top: int) -> list[tuple[int, ...]]:
    """The stage-1 leaders, ranked by each window set's best arm."""

    best: dict[tuple[int, ...], float] = {}
    for line in stage1_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if "sharpe" not in row:
            continue
        key = tuple(row["windows"])
        best[key] = max(best.get(key, float("-inf")), float(row["sharpe"]))
    return [key for key, _ in sorted(best.items(), key=lambda item: -item[1])[:top]]


def _arms_for(grid: str) -> list[dict[str, Any]]:
    symbols, family = GRIDS[grid]
    if family == "cs":
        return list(_cs_arms())
    if grid == "donchian-btceth":
        return list(
            _donchian_arms(
                DC_WINDOWS_FINE,
                staggered=False,
                atr_windows=DC_STAGE1_ATR_WINDOWS,
                atr_multiples=DC_STAGE1_ATR_MULTIPLES,
            )
        )
    if grid == "donchian-btceth-atr":
        leaders = _stage2_window_sets(OUT_DIR / "sweep_donchian-btceth.jsonl", top=DC_STAGE2_TOP)
        return [
            arm
            for combo in leaders
            for arm in _donchian_variants(
                combo,
                staggered=False,
                atr_windows=DC_ATR_WINDOWS,
                atr_multiples=DC_ATR_MULTIPLES,
            )
        ]
    # Same design as the BTC/ETH stage 1: exhaustive over a (coarser) window
    # space at the representative exit subset. A complete coarse grid beats a
    # truncated prefix of a fine one, whose coverage is biased toward the
    # window sets that sort first.
    return list(
        _donchian_arms(
            DC_WINDOWS_COARSE,
            staggered=True,
            atr_windows=DC_STAGE1_ATR_WINDOWS,
            atr_multiples=DC_STAGE1_ATR_MULTIPLES,
        )
    )


def run_sweep(grid: str, *, workers: int) -> Path:
    symbols, _ = GRIDS[grid]
    arms = _arms_for(grid)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"sweep_{grid}.jsonl"
    print(f"grid {grid}: {len(arms)} arms over {len(symbols)} symbols, {workers} workers")
    started = time.time()
    done = 0
    best = float("-inf")
    with out_path.open("w", encoding="utf-8") as handle:
        with mp.Pool(workers, initializer=_worker_init, initargs=(symbols,)) as pool:
            for row in pool.imap_unordered(_worker_run, arms, chunksize=8):
                handle.write(json.dumps(row, sort_keys=True) + "\n")
                done += 1
                if "sharpe" in row and row["sharpe"] > best:
                    best = float(row["sharpe"])
                if done % 2000 == 0:
                    rate = done / max(time.time() - started, 1e-9)
                    print(f"  {done}/{len(arms)} best={best:.6f} {rate:.1f}/s", flush=True)
    print(f"grid {grid} done in {time.time() - started:.1f}s -> {out_path} best={best:.6f}")
    return out_path


def _returns_from_report(arm: Mapping[str, Any], symbols: Sequence[str]) -> list[float]:
    """Daily return series seeded from initial cash, exactly as the registry writes it."""

    parameters = _parameters(symbols, arm)
    report = run_backtest(_load_candles(symbols), parameters=parameters)
    returns: list[float] = []
    previous = parameters.initial_cash
    for point in report.equity_curve:
        if previous > Decimal("0"):
            returns.append(float(point.equity / previous) - 1.0)
        previous = point.equity
    return returns


def _load_registry() -> list[TrialRecord]:
    from src.backtest.registry import load_trials

    return list(load_trials(RESEARCH_DIR / "trial_registry.jsonl"))


def _candidate_ids() -> list[int]:
    from scripts.run_gate_report import candidate_trials

    return [trial.trial_id for trial in candidate_trials(tuple(_load_registry()))]


def _series(trial_id: int) -> list[float]:
    path = RESEARCH_DIR / "trial_returns" / f"trial-{trial_id:06d}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [float(value) for value in payload["daily_returns"]]


def fast_pbo(columns: Sequence[Sequence[float]], *, block_count: int = CSCV_BLOCKS) -> float:
    """Vectorised CSCV/PBO, identical in definition to validation.py's reference.

    The reference implementation re-slices a T x N Python matrix once per
    partition and takes ~15 minutes on 37 columns, which is unusable when the
    statistic has to be recomputed per candidate arm. This computes the same
    number from per-block sufficient statistics: with equal blocks, a subset's
    mean and sample variance are exact functions of the subset's summed
    returns and summed squares, so each of the 12 870 partitions costs one
    gather instead of a 2 672-row rebuild.

    It is NOT trusted until ``--mode pbo-validate`` reproduces the recorded
    gate-report value from the same 37 candidate columns.
    """

    import numpy as np

    data = np.asarray(columns, dtype=np.float64).T  # T x N
    observations, strategies = data.shape
    usable = observations - (observations % block_count)
    block_size = usable // block_count
    blocks = data[:usable].reshape(block_count, block_size, strategies)
    block_sum = blocks.sum(axis=1)  # S x N
    block_sq = (blocks**2).sum(axis=1)  # S x N

    half = block_count // 2
    train_sets = np.array(list(itertools.combinations(range(block_count), half)), dtype=np.int64)
    mask = np.zeros((len(train_sets), block_count), dtype=bool)
    np.put_along_axis(mask, train_sets, True, axis=1)

    def _sharpe(selected: np.ndarray) -> np.ndarray:
        count = float(half * block_size)
        total = selected @ block_sum  # C x N
        squares = selected @ block_sq
        mean = total / count
        variance = (squares - count * mean**2) / (count - 1.0)
        stdev = np.sqrt(np.maximum(variance, 0.0))
        return np.where(stdev > 0.0, mean / np.where(stdev > 0.0, stdev, 1.0), 0.0)

    train_scores = _sharpe(mask.astype(np.float64))
    test_scores = _sharpe((~mask).astype(np.float64))
    best = np.argmax(train_scores, axis=1)
    best_test = np.take_along_axis(test_scores, best[:, None], axis=1)
    rank = (test_scores <= best_test).sum(axis=1)
    return float((rank / (strategies + 1) <= 0.5).mean())


def pbo_decompose(
    columns: Sequence[Sequence[float]], *, block_count: int = CSCV_BLOCKS
) -> dict[str, float]:
    """Attribute a PBO verdict between the LAST column and the legacy pool.

    PBO is a property of the pool, not of a candidate: the recorded number is
    the frequency with which *whichever* column wins in-sample lands
    out-of-sample below the median. Iterations 64 and 66 both turned on this
    distinction, so the same decomposition is reported here — the new arm's
    in-sample win share, its failure rate on the splits it wins, the legacy
    columns' failure rate on the splits they win, and the rate the arm would
    record if it won every split.
    """

    import numpy as np

    data = np.asarray(columns, dtype=np.float64).T
    observations, strategies = data.shape
    usable = observations - (observations % block_count)
    block_size = usable // block_count
    blocks = data[:usable].reshape(block_count, block_size, strategies)
    block_sum = blocks.sum(axis=1)
    block_sq = (blocks**2).sum(axis=1)

    half = block_count // 2
    train_sets = np.array(list(itertools.combinations(range(block_count), half)), dtype=np.int64)
    mask = np.zeros((len(train_sets), block_count), dtype=bool)
    np.put_along_axis(mask, train_sets, True, axis=1)

    def _sharpe(selected: np.ndarray) -> np.ndarray:
        count = float(half * block_size)
        mean = (selected @ block_sum) / count
        variance = ((selected @ block_sq) - count * mean**2) / (count - 1.0)
        stdev = np.sqrt(np.maximum(variance, 0.0))
        return np.where(stdev > 0.0, mean / np.where(stdev > 0.0, stdev, 1.0), 0.0)

    train_scores = _sharpe(mask.astype(np.float64))
    test_scores = _sharpe((~mask).astype(np.float64))
    best = np.argmax(train_scores, axis=1)
    arm = strategies - 1

    def _fails(column: np.ndarray) -> np.ndarray:
        picked = np.take_along_axis(test_scores, column[:, None], axis=1)
        rank = (test_scores <= picked).sum(axis=1)
        return rank / (strategies + 1) <= 0.5

    fails = _fails(best)
    arm_wins = best == arm
    arm_always = _fails(np.full(len(train_sets), arm, dtype=np.int64))
    return {
        "pbo": float(fails.mean()),
        "arm_is_win_share": float(arm_wins.mean()),
        "arm_fail_rate_when_winning": float(fails[arm_wins].mean()) if arm_wins.any() else 0.0,
        "legacy_fail_rate_when_winning": (
            float(fails[~arm_wins].mean()) if (~arm_wins).any() else 0.0
        ),
        "arm_unconditional_fail_rate": float(arm_always.mean()),
    }


def pbo_validate() -> None:
    """Reproduce the recorded gate-3 candidates-PBO before the fast path is used."""

    candidate_ids = _candidate_ids()
    columns = [_series(trial_id) for trial_id in candidate_ids]
    value = fast_pbo(columns)
    recorded = json.loads(
        (RESEARCH_DIR / "gate_report_2026-07-25.json").read_text(encoding="utf-8")
    )["gate_3_pbo"]
    print(
        f"candidate columns: {len(candidate_ids)} (recorded {len(recorded['candidate_trial_ids'])})"
    )
    print(f"fast PBO {value:.6f} vs recorded {recorded['pbo']:.6f}")
    all_ids = [trial.trial_id for trial in _load_registry()]
    all_value = fast_pbo([_series(trial_id) for trial_id in all_ids])
    print(f"fast PBO all-columns {all_value:.6f} vs recorded {recorded['pbo_all_columns']:.6f}")


def stop_condition(grid: str, *, top: int) -> None:
    """Run the sweep's best arms through gates 3 and 4 without registering them."""

    symbols, _ = GRIDS[grid]
    rows = [
        json.loads(line)
        for line in (OUT_DIR / f"sweep_{grid}.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    scored = sorted((r for r in rows if "sharpe" in r), key=lambda r: -float(r["sharpe"]))
    trials = _load_registry()
    annualized = [float(trial.metrics["annualized_sharpe"]) for trial in trials]
    candidate_ids = _candidate_ids()
    candidate_columns = [_series(trial_id) for trial_id in candidate_ids]

    print(f"registry N={len(trials)} candidates={len(candidate_ids)}")
    for arm in scored[:top]:
        returns = _returns_from_report(arm, symbols)
        variance = non_annualized_sharpe_variance([*annualized, float(arm["sharpe"])])
        dsr = deflated_sharpe_ratio(
            returns,
            trial_sharpe_variance=variance,
            effective_trials=len(trials) + 1,
        )
        columns = [*candidate_columns, returns]
        parts = pbo_decompose(columns)
        pbo_value = parts["pbo"]
        print(
            json.dumps(
                {
                    "arm": {k: v for k, v in arm.items() if k != "error"},
                    "dsr": round(dsr.deflated_sharpe_ratio, 6),
                    "expected_max_sharpe": round(dsr.expected_max_sharpe, 6),
                    "passes_dsr": dsr.deflated_sharpe_ratio >= DSR_MIN,
                    "pbo_candidates_plus_arm": round(pbo_value, 6),
                    "passes_pbo": pbo_value <= PBO_MAX,
                    "columns": len(columns),
                    "decomposition": {k: round(v, 6) for k, v in parts.items() if k != "pbo"},
                },
                sort_keys=True,
            ),
            flush=True,
        )


def validate() -> None:
    """Reproduce four registered trials before any sweep number is trusted."""

    checks: list[tuple[str, tuple[str, ...], dict[str, Any], str]] = [
        (
            "trial 88",
            UNIVERSE_BTCETH,
            {"family": "donchian", "windows": [10, 20, 55, 110], "exit": "mid_channel"},
            "1.182061",
        ),
        (
            "trial 118",
            UNIVERSE_BTCETH,
            {
                "family": "donchian",
                "windows": [10, 20, 55, 110],
                "exit": "atr_channel",
                "atr_window": 14,
                "atr_multiple": "2",
            },
            "1.241113",
        ),
        (
            "trial 131",
            UNIVERSE_BTCETH,
            {
                "family": "donchian",
                "windows": [12, 24, 66, 132],
                "exit": "atr_channel",
                "atr_window": 14,
                "atr_multiple": "2",
            },
            "1.229837",
        ),
        (
            "trial 56",
            tuple(UNIVERSE_13),
            {
                "family": "cs",
                "top_k": 2,
                "lookback": 180,
                "cadence": "monthly",
                "absolute_filter": True,
                "gate_sma": 100,
                "decision_start": CS_DECISION_START,
            },
            "1.165094",
        ),
    ]
    for label, symbols, arm, recorded in checks:
        report = run_backtest(_load_candles(symbols), parameters=_parameters(symbols, arm))
        got = f"{float(report.metrics.annualized_sharpe):.6f}"
        verdict = "MATCH" if got == recorded else "MISMATCH"
        observed = report.metrics.observation_days
        print(f"{label}: recorded {recorded} got {got} obs {observed} {verdict}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("validate", "pbo-validate", "sweep", "stop-condition"),
        required=True,
    )
    parser.add_argument("--grid", choices=sorted(GRIDS), default="donchian-btceth")
    parser.add_argument("--workers", type=int, default=max(mp.cpu_count() - 2, 1))
    parser.add_argument("--top", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "validate":
        validate()
    elif args.mode == "pbo-validate":
        pbo_validate()
    elif args.mode == "sweep":
        run_sweep(args.grid, workers=args.workers)
    else:
        stop_condition(args.grid, top=args.top)


if __name__ == "__main__":
    main()

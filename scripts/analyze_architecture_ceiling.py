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
    python -m scripts.analyze_architecture_ceiling --mode gate3-currency
    python -m scripts.analyze_architecture_ceiling --mode gate3-purchasability
    python -m scripts.analyze_architecture_ceiling --mode gate3-frontier

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
from collections.abc import Callable, Iterator, Mapping, Sequence
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


# --- Gate 3 in its own currency (iteration 68) ------------------------------
# Iterations 64, 66 and 67 all priced gate 3 in annualized Sharpe by adding
# constant alpha to a base shape and bisecting until PBO crossed 0.05. Every
# base shape they used is a column already inside the candidate pool. Gate 3
# does not read Sharpe: it reads which column wins in-sample on each of the
# 12 870 partitions. This mode separates the two — the IS-win share the gate
# actually requires, and the Sharpe price of buying that share at a given
# resemblance to the incumbent pool.
NOVELTY_SEEDS = (20260924, 1, 7, 99, 2026)
NOVELTY_BASES = (131, 14, 7, 15, 85)
DOSE_MIX = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
ANNUALIZER = 365.0


def _pool() -> tuple[list[int], list[list[float]], int, int]:
    ids = _candidate_ids()
    columns = [_series(trial_id) for trial_id in ids]
    total = len(columns[0])
    usable = total - (total % CSCV_BLOCKS)
    return ids, columns, total, usable


def _padded(values: Any, total: int) -> list[float]:
    """Extend a usable-length series to the pool's length; CSCV truncates the tail."""

    import numpy as np

    column = np.zeros(total)
    column[: len(values)] = values
    return [float(value) for value in column]


def _at_sharpe(values: Any, target: float) -> Any:
    """Shift the mean so the series carries ``target`` annualized Sharpe, shape held."""

    import numpy as np

    return values - values.mean() + target / np.sqrt(ANNUALIZER) * values.std(ddof=1)


def _crossing(
    build: Callable[[float], list[float]],
    columns: Sequence[Sequence[float]],
    *,
    low: float = 0.8,
    high: float = 4.5,
    tolerance: float = 1e-4,
) -> float:
    """Lowest annualized Sharpe at which the built column takes pooled PBO to <= 0.05."""

    while high - low >= tolerance:
        middle = (low + high) / 2.0
        if fast_pbo([*columns, build(middle)]) <= PBO_MAX:
            high = middle
        else:
            low = middle
    return high


def _pool_correlation(values: Any, matrix: Any) -> tuple[float, float]:
    import numpy as np

    scores = [
        abs(float(np.corrcoef(values, matrix[:, index])[0, 1])) for index in range(matrix.shape[1])
    ]
    return max(scores), float(np.mean(scores))


def _split_sharpes(data: Any, usable: int) -> tuple[Any, Any]:
    """Per-partition IS and OOS Sharpe for every column, same definition as fast_pbo."""

    import numpy as np

    block = usable // CSCV_BLOCKS
    blocks = data[:usable].reshape(CSCV_BLOCKS, block, data.shape[1])
    block_sum = blocks.sum(axis=1)
    block_sq = (blocks**2).sum(axis=1)
    half = CSCV_BLOCKS // 2
    train_sets = np.array(list(itertools.combinations(range(CSCV_BLOCKS), half)), dtype=np.int64)
    mask = np.zeros((len(train_sets), CSCV_BLOCKS), dtype=bool)
    np.put_along_axis(mask, train_sets, True, axis=1)

    def score(selected: Any) -> Any:
        count = float(half * block)
        mean = (selected @ block_sum) / count
        variance = ((selected @ block_sq) - count * mean**2) / (count - 1.0)
        stdev = np.sqrt(np.maximum(variance, 0.0))
        return np.where(stdev > 0.0, mean / np.where(stdev > 0.0, stdev, 1.0), 0.0)

    return score(mask.astype(np.float64)), score((~mask).astype(np.float64))


def gate3_currency() -> None:
    """Measure gate 3's requirement as an IS-win share, and its price against novelty."""

    import numpy as np

    ids, columns, total, usable = _pool()
    matrix = np.asarray(columns).T[:usable]
    block = usable // CSCV_BLOCKS
    print(f"pool: {len(ids)} candidate columns, {usable} usable days, {CSCV_BLOCKS} blocks")
    print(f"recorded gate-3 candidates-PBO reproduced: {fast_pbo(columns):.6f}")

    # 1. What the incumbent pool already achieves, in the gate's own currency.
    shares: list[tuple[int, float]] = []
    for index in range(len(ids)):
        rotated = [*columns[:index], *columns[index + 1 :], columns[index]]
        shares.append((ids[index], pbo_decompose(rotated)["arm_is_win_share"]))
    shares.sort(key=lambda pair: -pair[1])
    print("\nbest IS-win shares already in the pool:")
    for trial_id, share in shares[:5]:
        print(f"  trial {trial_id:>4}  w={share:.6f}")

    # 2. Three constructions of "uncorrelated with the pool", against the
    #    incumbent-boosted construction iterations 64/66/67 used.
    from statistics import NormalDist

    normal = NormalDist()
    grid = np.array([normal.inv_cdf((i + 0.5) / block) for i in range(block)])
    grid = (grid - grid.mean()) / grid.std(ddof=0)
    legacy_sd = float(np.median(matrix.std(axis=0, ddof=1)))

    rows: list[dict[str, Any]] = []

    def record(shape: str, base: str, build: Callable[[float], list[float]]) -> None:
        crossing = _crossing(build, columns)
        decomposition = pbo_decompose([*columns, build(crossing)])
        values = np.asarray(build(crossing))[:usable]
        peak, mean = _pool_correlation(values, matrix)
        rows.append(
            {
                "shape": shape,
                "base": base,
                "crossing_annualized_sharpe": round(crossing, 6),
                "max_pool_correlation": round(peak, 4),
                "mean_pool_correlation": round(mean, 4),
                **{key: round(value, 6) for key, value in decomposition.items()},
            }
        )
        print(json.dumps(rows[-1], sort_keys=True), flush=True)

    print("\ncrossings by candidate shape:")
    record(
        "block-uniform-gaussian",
        "synthetic",
        lambda target: _padded(np.tile(_at_sharpe(legacy_sd * grid, target), CSCV_BLOCKS), total),
    )
    for trial_id in NOVELTY_BASES:
        base_series = np.asarray(_series(trial_id))[:usable]
        record(
            "incumbent-plus-constant-alpha",
            f"trial {trial_id}",
            lambda target, values=base_series: _padded(_at_sharpe(values, target), total),
        )
        for seed in NOVELTY_SEEDS:
            shuffled = base_series.copy()
            np.random.default_rng(seed).shuffle(shuffled)
            record(
                f"day-permuted-seed-{seed}",
                f"trial {trial_id}",
                lambda target, values=shuffled: _padded(_at_sharpe(values, target), total),
            )
        order = np.random.default_rng(NOVELTY_SEEDS[0]).permutation(CSCV_BLOCKS)
        reordered = base_series.reshape(CSCV_BLOCKS, block)[order].reshape(-1)
        record(
            "block-permuted",
            f"trial {trial_id}",
            lambda target, values=reordered: _padded(_at_sharpe(values, target), total),
        )

    # 3. Dose-response: interpolate one novel shape toward its incumbent twin.
    print("\ndose-response (trial 131, novel -> incumbent):")
    base_series = np.asarray(_series(131))[:usable]
    shuffled = base_series.copy()
    np.random.default_rng(NOVELTY_SEEDS[0]).shuffle(shuffled)
    standard = (base_series - base_series.mean()) / base_series.std(ddof=1)
    permuted = (shuffled - shuffled.mean()) / shuffled.std(ddof=1)
    for weight in DOSE_MIX:
        mixed = weight * standard + (1.0 - weight) * permuted
        record(
            f"mix-{weight:.2f}",
            "trial 131",
            lambda target, values=mixed: _padded(_at_sharpe(values, target), total),
        )

    # 4. Mechanism. Two competing explanations for why resemblance is cheaper,
    #    both measured rather than asserted: an inherited head start (refuted),
    #    and the variance of the margin over the legacy maximum (supported).
    train, _ = _split_sharpes(np.asarray(columns).T[:usable], usable)
    legacy_winner = train.argmax(axis=1)
    legacy_max = train[np.arange(len(train)), legacy_winner]

    head_start: list[dict[str, Any]] = []
    margin: list[dict[str, Any]] = []
    print("\nhead start (arm's IS wins that its twin already held) and margin over legacy max:")
    for row in rows:
        if row["shape"] not in ("incumbent-plus-constant-alpha",) and not row["shape"].startswith(
            "day-permuted-seed-20260924"
        ):
            continue
        trial_id = int(row["base"].split()[1])
        base_series = np.asarray(_series(trial_id))[:usable]
        if row["shape"].startswith("day-permuted"):
            base_series = base_series.copy()
            np.random.default_rng(NOVELTY_SEEDS[0]).shuffle(base_series)
        arm = _at_sharpe(base_series, row["crossing_annualized_sharpe"])
        extended = np.column_stack([np.asarray(columns).T[:usable], arm])
        arm_train, _ = _split_sharpes(extended, usable)
        wins = arm_train.argmax(axis=1) == len(ids)
        overlap = int(((legacy_winner == ids.index(trial_id)) & wins).sum())
        head_start.append(
            {
                "shape": row["shape"],
                "base": row["base"],
                "arm_is_wins": int(wins.sum()),
                "of_which_twin_already_won": overlap,
                "share": round(overlap / int(wins.sum()), 4),
            }
        )
        print(json.dumps(head_start[-1], sort_keys=True), flush=True)

    for row in [r for r in rows if r["shape"].startswith("mix-")]:
        weight = float(row["shape"].split("-")[1])
        mixed = weight * standard + (1.0 - weight) * permuted
        arm = _at_sharpe(mixed, row["crossing_annualized_sharpe"])
        arm_train, _ = _split_sharpes(arm.reshape(-1, 1), usable)
        gap = arm_train[:, 0] - legacy_max
        margin.append(
            {
                "mix": weight,
                "crossing_annualized_sharpe": row["crossing_annualized_sharpe"],
                "corr_with_legacy_max": round(
                    float(np.corrcoef(arm_train[:, 0], legacy_max)[0, 1]), 4
                ),
                "mean_margin_annualized": round(float(gap.mean()) * float(np.sqrt(ANNUALIZER)), 6),
                "sd_margin_annualized": round(
                    float(gap.std(ddof=1)) * float(np.sqrt(ANNUALIZER)), 6
                ),
            }
        )
        print(json.dumps(margin[-1], sort_keys=True), flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "gate3_currency.json"
    payload = {
        "baseline_candidates_pbo": round(fast_pbo(columns), 6),
        "pool_is_win_shares": [
            {"trial_id": trial_id, "w": round(share, 6)} for trial_id, share in shares
        ],
        "crossings": rows,
        "head_start": head_start,
        "margin_variance": margin,
    }
    path.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    print(f"\nwrote {path}")


# --- Is gate 3's verdict purchasable? (iteration 69) ------------------------
# Iteration 64 found gate 4's variance input is analyst-controllable: 39 arms
# at the registry's own mean Sharpe turn trial 88 from a gate-4 failure into a
# pass, on no new information. The mirror question was never asked of gate 3,
# which is the gate that actually refused every route iterations 66-68 closed.
# CSCV scores the in-sample winner by its OOS RANK inside the same pool
# (``rank / (N + 1) <= 0.5``), so the verdict is measured against the pool's
# own median. This mode holds the candidate fixed and changes only the pool.
#
# Every column added here is a real backtest of a real config, obtained by an
# act the contract permits (iterations 66-68: a family may be run for a
# product reason). Nothing is fabricated and nothing is hidden. That is the
# point: if the verdict moves, it moves without dishonesty.
PURCHASE_K = (1, 2, 4, 8, 16, 32, 64)
CEILING_ARM: dict[str, Any] = {
    "family": "cs",
    "top_k": 3,
    "lookback": 120,
    "cadence": "monthly",
    "absolute_filter": True,
    "gate_sma": 50,
    "decision_start": CS_DECISION_START,
}
SWEEP_METRIC_KEYS = (
    "sharpe",
    "error",
    "final_equity",
    "max_drawdown",
    "observation_days",
    "trades",
    "turnover",
)


def _sweep_rows() -> list[tuple[dict[str, Any], tuple[str, ...], float]]:
    """Every valid arm of every recorded sweep, with the universe it was run on."""

    rows: list[tuple[dict[str, Any], tuple[str, ...], float]] = []
    for grid, (symbols, _family) in GRIDS.items():
        path = OUT_DIR / f"sweep_{grid}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if "sharpe" not in row:
                continue
            arm = {key: value for key, value in row.items() if key not in SWEEP_METRIC_KEYS}
            rows.append((arm, symbols, float(row["sharpe"])))
    return rows


def _same_arm(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return all(left.get(key) == right.get(key) for key in set(left) | set(right))


def _greedy_prune(columns: Sequence[Sequence[float]]) -> list[dict[str, Any]]:
    """Price the forbidden attack: drop legacy columns until the verdict flips.

    The candidate is the last column and is never a removal candidate. This is
    silent survivor filtering and is recorded as forbidden, not proposed.
    """

    working = [list(column) for column in columns]
    labels = list(range(len(working) - 1))
    trail: list[dict[str, Any]] = []
    while len(working) > 4:
        current = fast_pbo(working)
        best_index = None
        best_value = current
        for position in range(len(labels)):
            trimmed = [column for index, column in enumerate(working) if index != position]
            value = fast_pbo(trimmed)
            if value < best_value:
                best_value = value
                best_index = position
        if best_index is None:
            break
        dropped = labels.pop(best_index)
        working = [column for index, column in enumerate(working) if index != best_index]
        trail.append(
            {"dropped_position": dropped, "columns": len(working), "pbo": round(best_value, 6)}
        )
        print(f"  prune {len(trail)}: columns={len(working)} pbo={best_value:.6f}", flush=True)
        if best_value <= PBO_MAX:
            break
    return trail


def gate3_purchasability() -> None:
    """Hold the candidate fixed, change only the pool, and watch gate 3 move."""

    ids, columns, total, _usable = _pool()
    baseline = fast_pbo(columns)
    print(f"legacy candidate columns {len(ids)} baseline candidates-PBO {baseline:.6f}")

    ceiling_returns = _returns_from_report(CEILING_ARM, tuple(UNIVERSE_13))
    ceiling = _padded(ceiling_returns, total)
    with_arm = fast_pbo([*columns, ceiling])
    arm_parts = pbo_decompose([*columns, ceiling])
    print(f"+ ceiling arm -> {with_arm:.6f} (iteration 67 recorded 0.235120)")

    rows = _sweep_rows()
    ceiling_sharpe = next(
        (sharpe for arm, _symbols, sharpe in rows if _same_arm(arm, CEILING_ARM)), 0.0
    )
    print(f"ceiling arm sharpe from sweep file: {ceiling_sharpe:.6f}")
    ranked = sorted(
        (row for row in rows if not _same_arm(row[0], CEILING_ARM)), key=lambda row: -row[2]
    )
    print(f"sweep arms available as padding: {len(ranked)}")

    largest = max(PURCHASE_K)
    sources = {"best": ranked[:largest], "worst": ranked[-largest:]}
    padding: dict[str, list[list[float]]] = {}
    for label, source in sources.items():
        padding[label] = [
            _padded(_returns_from_report(arm, symbols), total) for arm, symbols, _s in source
        ]
        print(
            f"padding[{label}] {len(padding[label])} columns, "
            f"sharpe {source[0][2]:.6f} .. {source[-1][2]:.6f}"
        )

    results: list[dict[str, Any]] = []
    for label in ("best", "worst"):
        for k in PURCHASE_K:
            pad = padding[label][:k]
            no_candidate = fast_pbo([*columns, *pad])
            full = [*columns, *pad, ceiling]
            parts = pbo_decompose(full)
            share = parts["arm_is_win_share"]
            identity = (
                share * parts["arm_fail_rate_when_winning"]
                + (1.0 - share) * parts["legacy_fail_rate_when_winning"]
            )
            row = {
                "padding": label,
                "k": k,
                "columns_without_candidate": len(columns) + k,
                "pbo_without_candidate": round(no_candidate, 6),
                "passes_without_candidate": bool(no_candidate <= PBO_MAX),
                "columns_with_candidate": len(full),
                "pbo_with_candidate": round(parts["pbo"], 6),
                "passes_with_candidate": bool(parts["pbo"] <= PBO_MAX),
                "w": round(share, 6),
                "f": round(parts["arm_fail_rate_when_winning"], 6),
                "g": round(parts["legacy_fail_rate_when_winning"], 6),
                "candidate_unconditional": round(parts["arm_unconditional_fail_rate"], 6),
                "identity_residual": round(parts["pbo"] - identity, 12),
            }
            results.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)

    print("\n-- gate 4 cost of the same padding, measured not assumed --")
    trials = _load_registry()
    annualized = [float(trial.metrics["annualized_sharpe"]) for trial in trials]
    dsr_rows: list[dict[str, Any]] = []
    for label in ("best", "worst"):
        for k in PURCHASE_K:
            added = [sharpe for _arm, _symbols, sharpe in sources[label][:k]]
            population = [*annualized, *added, ceiling_sharpe]
            variance = non_annualized_sharpe_variance(population)
            dsr = deflated_sharpe_ratio(
                ceiling_returns,
                trial_sharpe_variance=variance,
                effective_trials=len(population),
            )
            dsr_rows.append(
                {
                    "padding": label,
                    "k": k,
                    "effective_trials": len(population),
                    "sharpe_variance": float(f"{variance:.6e}"),
                    "dsr": round(dsr.deflated_sharpe_ratio, 6),
                    "passes_dsr": bool(dsr.deflated_sharpe_ratio >= DSR_MIN),
                }
            )
            print(json.dumps(dsr_rows[-1], sort_keys=True), flush=True)

    print("")
    print("-- the adversary's real problem: minimise PBO subject to DSR >= 0.95 --")
    # Junk padding buys gate 3 and loses gate 4, because the same distance from
    # the registry mean that makes a column OOS-dominated also inflates the
    # Sharpe variance gate 4 divides by. The adversary's optimum is therefore
    # padding AT the registry mean (iteration 64: 39 arms there turn trial 88
    # from a gate-4 failure into a pass). This scans Sharpe bands x K for any
    # cell where both gates pass at once.
    registry_mean = sum(annualized) / len(annualized)
    print(f"registry mean annualized sharpe {registry_mean:.6f}")
    band_rows: list[dict[str, Any]] = []
    for level in (0.0, 0.4, registry_mean, 1.2):
        nearest = sorted(ranked, key=lambda row: abs(row[2] - level))[:128]
        band_columns = [
            _padded(_returns_from_report(arm, symbols), total) for arm, symbols, _s in nearest
        ]
        for k in (8, 16, 32, 64, 128):
            pad_columns = band_columns[:k]
            pad_sharpes = [sharpe for _arm, _symbols, sharpe in nearest[:k]]
            parts = pbo_decompose([*columns, *pad_columns, ceiling])
            population = [*annualized, *pad_sharpes, ceiling_sharpe]
            variance = non_annualized_sharpe_variance(population)
            dsr = deflated_sharpe_ratio(
                ceiling_returns,
                trial_sharpe_variance=variance,
                effective_trials=len(population),
            )
            value = dsr.deflated_sharpe_ratio
            row = {
                "band_center": round(level, 6),
                "k": k,
                "pad_sharpe_span": [round(min(pad_sharpes), 6), round(max(pad_sharpes), 6)],
                "pbo": round(parts["pbo"], 6),
                "passes_pbo": bool(parts["pbo"] <= PBO_MAX),
                "sharpe_variance": float(f"{variance:.6e}"),
                "effective_trials": len(population),
                "dsr": round(value, 6),
                "passes_dsr": bool(value >= DSR_MIN),
                "passes_both": bool(parts["pbo"] <= PBO_MAX and value >= DSR_MIN),
                "w": round(parts["arm_is_win_share"], 6),
                "g": round(parts["legacy_fail_rate_when_winning"], 6),
            }
            band_rows.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    winners = [row for row in band_rows if row["passes_both"]]
    print(f"cells where BOTH gates pass: {len(winners)} of {len(band_rows)}")

    print("\n-- scale-freeness control: duplicate the candidate instead of padding --")
    duplicate: list[dict[str, Any]] = []
    for copies in (1, 2, 4, 8, 16, 32):
        full = [*columns, *([ceiling] * copies), ceiling]
        value = fast_pbo(full)
        duplicate.append({"copies": copies, "columns": len(full), "pbo": round(value, 6)})
        print(json.dumps(duplicate[-1], sort_keys=True), flush=True)

    print("\n-- the forbidden attack, priced only: greedy legacy pruning --")
    prune = _greedy_prune([*columns, ceiling])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "gate3_purchasability.json"
    path.write_text(
        json.dumps(
            {
                "baseline_candidates_pbo": round(baseline, 6),
                "candidate": {"arm": CEILING_ARM, "annualized_sharpe": ceiling_sharpe},
                "candidate_only": {
                    "pbo": round(with_arm, 6),
                    "decomposition": {key: round(value, 6) for key, value in arm_parts.items()},
                },
                "padding_sharpe_span": {
                    label: [round(source[0][2], 6), round(source[-1][2], 6)]
                    for label, source in sources.items()
                },
                "padding_sweep": results,
                "gate4_cost": dsr_rows,
                "duplicate_control": duplicate,
                "sharpe_band_scan": band_rows,
                "greedy_prune": prune,
                "pbo_max": PBO_MAX,
                "dsr_min": DSR_MIN,
            },
            indent=1,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {path}")


def gate3_frontier() -> None:
    """Push the one band that kept gate 4 while lowering gate 3 as far as it goes.

    The 20-cell scan in ``gate3-purchasability`` left the frontier minimum at
    PBO 0.095571 (band 0.4, K=128, DSR 0.969577) and the k-ladder visibly
    saturating (0.128283 -> 0.101166 -> 0.095571). Extrapolating a saturation
    is not measuring one, so this extends the same band to K=256 and K=512.
    """

    _ids, columns, total, _usable = _pool()
    ceiling_returns = _returns_from_report(CEILING_ARM, tuple(UNIVERSE_13))
    ceiling = _padded(ceiling_returns, total)
    trials = _load_registry()
    annualized = [float(trial.metrics["annualized_sharpe"]) for trial in trials]
    rows = _sweep_rows()
    ceiling_sharpe = next(
        (sharpe for arm, _symbols, sharpe in rows if _same_arm(arm, CEILING_ARM)), 0.0
    )
    ranked = [row for row in rows if not _same_arm(row[0], CEILING_ARM)]

    level = 0.4
    nearest = sorted(ranked, key=lambda row: abs(row[2] - level))[:512]
    print(
        f"band {level}: {len(nearest)} arms, sharpe span "
        f"{min(row[2] for row in nearest):.6f} .. {max(row[2] for row in nearest):.6f}"
    )
    built: list[list[float]] = []
    started = time.time()
    for index, (arm, symbols, _sharpe) in enumerate(nearest, start=1):
        built.append(_padded(_returns_from_report(arm, symbols), total))
        if index % 100 == 0:
            print(f"  {index}/{len(nearest)} engine runs, {time.time() - started:.0f}s", flush=True)

    out: list[dict[str, Any]] = []
    for k in (128, 256, 512):
        parts = pbo_decompose([*columns, *built[:k], ceiling])
        pad_sharpes = [sharpe for _arm, _symbols, sharpe in nearest[:k]]
        population = [*annualized, *pad_sharpes, ceiling_sharpe]
        variance = non_annualized_sharpe_variance(population)
        dsr = deflated_sharpe_ratio(
            ceiling_returns, trial_sharpe_variance=variance, effective_trials=len(population)
        )
        row = {
            "band_center": level,
            "k": k,
            "pad_sharpe_span": [round(min(pad_sharpes), 6), round(max(pad_sharpes), 6)],
            "pbo": round(parts["pbo"], 6),
            "passes_pbo": bool(parts["pbo"] <= PBO_MAX),
            "sharpe_variance": float(f"{variance:.6e}"),
            "effective_trials": len(population),
            "dsr": round(dsr.deflated_sharpe_ratio, 6),
            "passes_dsr": bool(dsr.deflated_sharpe_ratio >= DSR_MIN),
            "passes_both": bool(parts["pbo"] <= PBO_MAX and dsr.deflated_sharpe_ratio >= DSR_MIN),
            "w": round(parts["arm_is_win_share"], 6),
            "g": round(parts["legacy_fail_rate_when_winning"], 6),
        }
        out.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "gate3_frontier.json"
    path.write_text(json.dumps({"band_extension": out}, indent=1, sort_keys=True), encoding="utf-8")
    print(f"wrote {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=(
            "validate",
            "pbo-validate",
            "sweep",
            "stop-condition",
            "gate3-currency",
            "gate3-purchasability",
            "gate3-frontier",
        ),
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
    elif args.mode == "gate3-currency":
        gate3_currency()
    elif args.mode == "gate3-purchasability":
        gate3_purchasability()
    elif args.mode == "gate3-frontier":
        gate3_frontier()
    else:
        stop_condition(args.grid, top=args.top)


if __name__ == "__main__":
    main()

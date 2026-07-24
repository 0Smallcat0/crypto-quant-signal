# Experiment 9 engine scoping — bounded vs unbounded decision

Written 2026-07-24 during iteration 11 of the autonomous research loop, before
any engine work and before any pre-registration is written. Iteration 10
authorized this iteration to pre-register the SSRN-faithful vol-sized
Donchian family **if and only if** the engine work (allocation-model
plumbing + tests) fits inside a single iteration; else record a
consolidation switch and redirect subsequent iterations to gate-6 real-run
readiness work (`docs/RUNBOOK_*.md`, holdout lock hygiene, notifier drills).

The purpose of this document is to make that gate honestly, on the record,
before spending N. The verdict is written before any code changes so it
cannot be reverse-fit to a preferred conclusion.

## What "SSRN-faithful" means (per the source paper)

Zarattini/Pagani/Barbon SSRN 5209907 ("Catching Crypto Trends", 2025-05,
revised 2025-10) attributes its headline numbers (Sharpe 1.58, CAGR 30%,
alpha +14% vs BTC over 2015-01 → 2025-03 on a survivorship-free top-20
rotational book) to the **joint** application of:

1. A Donchian-channel breakout ensemble (multiple lookback horizons blended
   into a single signal per symbol) — this is what our experiment-7/8 already
   ran, verbatim mechanics per commit f625d87.
2. **Cross-asset volatility-based position sizing**: weights are proportional
   to `1/σ_i` (inverse realized vol), normalized across active symbols, and
   scaled so aggregate portfolio vol tracks an ex-ante target. A per-symbol
   weight cap arm is standard (Alvarez, 2026-07-24 RESEARCH_LOG line;
   Concretum Group, same date).

The two ingredients are interlocking, not additive. Applying only piece (1)
on equal-weight budgets — exactly what exp-7 and exp-8 did — leaves the
paper's causal mechanism untested. The RESEARCH_LOG line dated 2026-07-23
records this reading.

## Path A — reuse `_apply_vol_overlay` (per-symbol vol targeting)

The engine's existing `_apply_vol_overlay` (`src/backtest/engine.py:632`)
scales each symbol's exposure_fraction by `min(1, target_vol / realized_vol_i)`
using `_vol_scaler` (`src/backtest/engine.py:688`). The overlay is refused
today for `donchian_breakout_ensemble` at `src/backtest/types.py:110-115`
(the exp-7 pre-registration scope). Lifting the refusal makes the mechanism
available on the Donchian path with zero additional plumbing.

**Cost estimate** (bounded, fits one iteration):

- Remove the refusal in `types.py`; add a validation case covering
  vol_target × Donchian × cs_gate (mutually exclusive, matches exp-5).
- Confirm dispatch in the main loop already covers `_SizedDecision` (it does,
  verified at engine.py:229 — the type union already includes `_SizedDecision`).
- 3 tests: (a) parity — vol_target=∞ (or a value large enough to make scaler
  ≥1 everywhere) reproduces trial 88; (b) scaler <1 in a high-vol synthetic
  arm; (c) monthly-vs-daily rebalance differs.
- Pre-register experiment 9 grid: window pair × exit rule × vol_target ×
  vol_window × vol_rebalance.
- Runner: extend the exp-7 runner (`scripts/run_experiment_7_family.py` or
  equivalent) with the new arm dimensions.

**Problem with Path A**: this is not what SSRN describes. Per-symbol vol
targeting is what we already ran on cs momentum (experiment 4, seventh
registered negative — the vol dial swept 39% → 73% MDD and Sharpe never
cleared the deflation bar; conclusion in LOOP_LOG iteration 4). Applying the
same overlay to a different signal is not novel research; it is one more
wrapper sweep, and the N-arithmetic doc (2026-07-23) explicitly refuses
"any wrapper re-sweep, barbell variant, or ATR-on-cs-momentum family" as
strictly negative EV under current N mechanics.

Path A therefore fails the "SSRN-faithful" bar iteration 10 set, and also
fails the N-arithmetic refusal test. It is bounded but the wrong feature.

## Path B — new allocation-model dispatch (SSRN-faithful)

The engine currently commits to one allocation model: each symbol's fraction
lives on the 5-rung ladder (0, 1/4, 1/2, 3/4, 1), scaled per-symbol,
snapped by `build_ladder_targets`. The SSRN mechanism replaces this with
cross-asset weight computation on each decision day:

- For each active symbol i with Donchian signal s_i > 0, compute realized
  daily vol σ_i over a rolling lookback (Alvarez formula; SSRN uses 20-60
  day windows).
- Raw weights w_i = s_i / σ_i (SSRN inverse-vol scaling), NORMALIZED across
  active symbols to `∑ w_i = target_scale`, where `target_scale` is
  `min(1, target_vol_annualized / realized_portfolio_vol)`. This gives the
  vol-parity variant; vol-targeting adds the portfolio-vol rescale layer.
- Per-symbol weight cap arm: clip each w_i at some cap ∈ {1/N, 0.25, 0.50}
  and re-normalize (Alvarez / Concretum).
- Bypass `build_ladder_targets` in this mode; execute directly against the
  new weight vector. This is where the engine plumbing is genuinely new.

**Cost estimate** (unbounded — spans multiple iterations):

- New `BacktestParameters` fields: `allocation_model: str`, `dc_vol_target`,
  `dc_vol_window`, `dc_weight_cap`. Validation for mutual exclusion with the
  existing vol overlay and the ladder-path gate.
- New engine function `_dc_vol_target_weights(...)` computing cross-asset
  weights from `_SizedDecision`s: per-symbol vol via `_vol_scaler`-style
  logic, inverse-vol normalization, cap-and-renormalize, portfolio-vol
  rescale, cash residual.
- Rewire execution: skip `build_ladder_targets` in vol_target mode; feed the
  weight vector directly to the ladder-change loop, preserving the
  intended_notional accounting used at engine.py:433.
- Staggered-mode interaction: cross-asset normalization must operate on the
  active-symbols slice per decision day; benchmark anchoring, ledger
  padding, and gate interaction all need cases.
- Tests: parity (equal-vol universe reproduces equal-weight), inverse-vol
  correctness on a synthetic BTC-vs-DOGE spread, cap-arm behavior, target-
  vol rescale, staggered universe, no-active-signals cash case, warmup
  fallthrough. Minimum 6-8 tests to be honest.
- Runner + registry integration + per-trial return series serialization.
- Pre-registration doc, grid, and success criteria.

Honest engineering estimate: **2-3 iterations**, not one. The plumbing is
non-trivial (allocation dispatch is the first place in the engine where per-
symbol accounting is not sufficient), and the parity + staggered + gate
interactions each need dedicated tests before the family runs on a clean
committed tree per the commit-first rule.

## Verdict — UNBOUNDED

Path B is the SSRN-faithful feature iteration 10 authorized; Path A is not
what iteration 10 asked for. Path B does not fit inside one iteration by an
honest reading of the engine plumbing needed.

**Consolidation switch is engaged per the iteration-10 contingency:**

- No experiment 9 pre-registration is written this iteration.
- No new backtest family is run this iteration (registry N stays at 101).
- Subsequent autonomous iterations redirect to gate-6 real-run-readiness
  work: `docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md` verification, holdout
  lock hygiene evidence, notifier drills, and empirical cost-model
  measurement from the `exec_quote` event stream that the runtime already
  emits (`src/runtime/quotes.py`, runbook §4).
- The SSRN vol-sized Donchian family is not abandoned; it is deferred until
  the October holdout completes (or the operator explicitly authorizes the
  multi-iteration engine build ahead of the holdout). Any restart of the
  research spend requires either a passing gate-6 checkpoint OR a fresh
  operator authorization overriding the consolidation.

## Gate-6 baseline recorded this iteration

First real-money-cost datapoint from the `exec_quote` stream (21 days per
symbol, 2026-07-03 → 2026-07-23; captured post-cycle by `src/runtime/quotes.py`):

| Symbol   | n  | mean spread (bps) | median (bps) | max (bps) | round-trip estimate |
|----------|----|-------------------|--------------|-----------|---------------------|
| BTCUSDT  | 21 | 0.0000            | 0.0000       | 0.0000    | 20.00 bps           |
| ETHUSDT  | 21 | 0.0548            | 0.0500       | 0.0600    | 20.10 bps           |

Round-trip estimate = `2 × median(spread_bps) + 2 × fee_bps` at the runtime
default `fee_bps = 10`. Gate 6's calibration cap
(`VALIDATION_GATE_CONTRACT.md §6`) is `1.5 × 25–30 bps` = 37.5–45 bps
round-trip; both symbols sit at ~20 bps, well inside the cap. The cost
model is not under stress on the two live-runtime symbols so far.

Caveats worth naming (not fixed here, queued):

- 21 days is thin; 90 days is the gate-6 minimum window.
- Measurement is bid/ask spread at capture time (~5 minutes after close),
  NOT the decision→execution slippage a real order would pay. Adding a
  "decision-time vs capture-time drift" derived stat is a natural
  gate-6-work follow-up.
- Only two symbols are on the live runtime; the 13-symbol research
  universe is untouched by this measurement. If experiment 9 ever
  runs on the wider universe, altcoin cost readings would need their
  own accumulation window.

## Honesty clauses

- This document decides whether to pre-register experiment 9. It does not
  itself pre-register anything, and it does not read any holdout data
  (holdout_lock.json remains sealed, spent=false).
- The engine cost estimate is my best honest reading; the operator may
  disagree and override with an explicit multi-iteration authorization,
  in which case this document is superseded on the record via the same
  drift-guard override protocol used in iterations 4/5/6/7/9.
- Nothing here changes the statutory bars (DSR ≥ 0.95, MDD ≤ 51.93%,
  turnover ≤ 53.1). Trial 88's incumbent-frontier standing
  (DSR 0.9330, MDD 33.05%, Sharpe 1.1821) is unchanged.

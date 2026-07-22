# Goal P experiment 8 pre-registration — Donchian ensemble on the 13-symbol universe

Status: **FROZEN on commit**. Written 2026-07-22, after the iteration-8
engineering prerequisite landed (staggered-listing ladder mode, commit
7f8a0b7) and before any experiment-8 run. Hypothesis, grid, selection
rule, and success criteria may not change once the first member runs. A
failed family is a registered negative.

## Drift-guard override (recorded, not hidden)

Fifth recorded override (operator: 「continue」 after the experiment-7
read-out). Neutralized as always: **every success criterion is the
statutory bar frozen long before today** (absolute 0.95 DSR gate;
trial 4's 51.93% MDD; 3×17.69 turnover). No number first observed in
experiments 3-7 appears as a threshold.

## Hypothesis

Experiment 7 put the Donchian ensemble 0.0233 short of the deflation bar
on BTC/ETH alone, with both risk bars passed family-wide. The SSRN source
paper's headline result rests on universe BREADTH (its own abstract
credits the survivorship-bias-free wide universe), and the iteration-8
web pass confirmed point-in-time per-symbol eligibility as the standard
bias-safe way to widen. Running the same self-exiting breakout book
across 13 qualified symbols — each participating only from its own
listing day — diversifies idiosyncratic chop and is the registered route
from Sharpe 1.18 toward the ≈1.24+ the N≥101 deflation demands.

## Strategy definition (mechanical)

- Universe: the 13 qualified symbols (UNIVERSE_EXPANSION.md), pre-holdout
  candles, `allow_staggered_listings=True`: each symbol enters decisions
  only once its own history supports the strategy (per-symbol
  eligibility; no intersection collapse, no pre-listing lookthrough).
  Survivorship-bias declaration carries over from UNIVERSE_EXPANSION.md.
- Risk budgets: equal 1/13 per symbol (ladder semantics: per-symbol
  budget fraction; unfilled budgets rest in cash).
- Signal: the experiment-7 Donchian 4-window ensemble per symbol,
  unchanged (5-rung ladder; OFF→ON on a close above the prior w-day max
  close; exits per the arm's rule; explicit caller-carried state; no
  lookahead).
- Regime-gate arms reuse the experiment-5 machine (SMA 200, btc basis,
  2% hysteresis, daily) over the whole book. Experiment 7 showed the gate
  double-brakes on BTC/ETH; the 13-symbol book is a NEW test of that
  read-out (altcoin legs may need the brake BTC legs did not) — both arms
  are registered rather than assuming either way.
- No vol overlay. Costs, window, and execution identical to every
  registered trial; returns pinned to the registry window
  (2018-03-05 → 2025-07-01, 2676 obs) via the BTC-anchored decision
  start.

## Family grid (8 configurations, all registered)

- window set ∈ { {10,20,55,110} (fast — exp-7 winner shape),
  {10,20,110,220} (barbell — arxiv 2510.23150: short+long beats
  equal-band once mid horizons are redundant) }
- exit rule ∈ { half_low, mid_channel }
- regime gate ∈ { on, off }

The slow set {20,55,110,220} is dropped: it lost to fast on every
experiment-7 pairing (sequential refinement, declared here before any
experiment-8 number exists).

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 101)

1. **Winner DSR ≥ 0.95** at full deflation.
2. **Winner max drawdown ≤ 51.93%.**
3. **Winner annualized turnover ≤ 53.1.**

Anything less on any criterion → registered negative. Passing all three
does NOT trigger the loop's stop condition unless candidates-PBO ≤ 0.05
in the same report; October's holdout nominations remain fixed.

## Informative read-outs (non-gating, declared now)

- Breadth effect: winner vs trial 88's 1.1821/33.05% (did 11 more
  symbols move Sharpe toward the bar, and at what MDD cost?).
- Barbell vs fast window sets (the arxiv redundancy claim, tested).
- Gate on a diversified self-exiting book (exp-7 read-out revisited).
- Winner's correlation with trial 4 and trial 88.
- Staggered-mode audit: per-symbol first-decision dates logged against
  listing dates (point-in-time eligibility working as designed).

## Engine prerequisite

Landed and tested before this document (commit 7f8a0b7; 66 backtest
tests green; trials 1-93 bit-for-bit reproducible in default mode). No
further engine work is part of this family.

## Honesty clauses

- Registry N grows to ≥ 101; every DSR pays the larger deflation.
- Universe survivorship bias carries over; the holdout remains the single
  arbiter; October's nominations are untouched by any outcome here.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.

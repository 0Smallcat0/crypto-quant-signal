# Goal P experiment 4 pre-registration — risk-managed cross-sectional family

Status: **FROZEN on commit**. Written 2026-07-21, before any engine work or
run for this family. Hypothesis, grid, selection rule, and success criteria
may not change once the first member runs. A failed family is a registered
negative.

## Drift-guard override (recorded, not hidden)

The standing rule says the next pre-registration is written in a DIFFERENT
sitting from reading the previous results. The operator explicitly ordered
otherwise today: 「不用等下一輪，直接接著寫組合家族的 pre-registration
然後跑」. This document is therefore written in the same sitting as the
experiment-3 read-out, with the drift risk neutralized structurally
instead of temporally: **every success criterion below is anchored to
numbers frozen BEFORE today** (trial 4's live-baseline drawdown and
turnover from the pre-experiment-2 era; the absolute 0.95 DSR gate).
No criterion references any number first observed today (trial 29's
1.4109 Sharpe, 0.9621 DSR, or 75.08% MDD appear nowhere below as
thresholds). Architecture choice (which configuration to overlay) is
sequential refinement, which prior result documents already declare
legitimate; thresholds are where goalposts drift, and none moved.

## Hypothesis

Experiment 3 produced a deflation-surviving signal (cross-sectional
momentum) whose drawdown a follower cannot hold; experiment 2 produced a
sizing overlay that measurably compresses drawdown on a trend signal. The
combination — cs-momentum selection sized by a per-symbol volatility
target — retains enough of the signal's deflated Sharpe to clear the
absolute gate while pulling max drawdown to the live baseline or better.

## Strategy definition (mechanical)

- Base selection: experiment 3's winning architecture, fixed for the whole
  family — K=2, lookback 180d, monthly cadence, absolute filter ON,
  min pool 4, 13-symbol pre-holdout universe, decision floor 2018-03-05
  (`cs_decision_start`), identical costs and window to every registered
  trial.
- Overlay: each selected symbol's weight (1/K) is multiplied by
  min(1, vol_target / realized_vol_symbol) — the experiment-2 scaler
  (`_vol_scaler`: trailing `vol_window` daily log-return stdev, annualized
  √365, warmup → 1). Scaled-off weight rests in cash. Spot long-only, no
  leverage (product law): the overlay can only DE-risk.
- Overlay cadence: `vol_rebalance` daily recomputes the scaler every
  decision day (selection stays monthly); monthly freezes each symbol's
  scaler at its first decision day of the calendar month.
- Raw cs weights are never rewritten — the overlay resizes execution
  targets, the selection state machine sees raw weights (same doctrine as
  experiment 2).

## Family grid (16 configurations, all registered)

- vol_target ∈ {0.30, 0.50, 0.70, 0.90} (annualized)
- vol_window ∈ {20, 60} days
- vol_rebalance ∈ {daily, monthly}

## Selection rule (pre-declared)

Family winner = highest full-window annualized Sharpe. No post-hoc metric
switching.

## Success criteria (ALL required, same full-registry gate report, N ≥ 53)

1. **Winner DSR ≥ 0.95** — the absolute gate-4 bar, at full N≥53
   deflation. (Not "beat the previous best"; the fixed statutory line.)
2. **Winner max drawdown ≤ 51.93%** — trial 4's live-baseline MDD, the
   same anchor experiments 2 and 3 used; frozen long before today.
3. **Winner annualized turnover ≤ 53.1** — 3 × trial 4's 17.69, unchanged
   from experiment 3.

Anything less on any criterion → the family is a registered negative.
Meeting all three still does NOT trigger the loop's stop condition unless
candidates-PBO ≤ 0.05 holds in the same report; nor does it touch October
(holdout nominations are fixed; a passing winner waits for the NEXT
holdout cycle and its own paper qualification).

## Informative read-outs (non-gating, declared now)

- Overlay strength: MDD and Sharpe as functions of vol_target (does 0.30
  overshoot into cash-drag the way experiment 2's wealth trade-off did?).
- Terminal-wealth trade-off vs the unoverlaid base (experiment 2 doctrine:
  product decision, not statistics).
- Daily vs monthly scaler cadence on a monthly-selected book.
- Winner's daily-return correlation with trial 4 (diversification value,
  carried over from experiment 3's queue).

## Engine prerequisite (work item, not a degree of freedom)

`BacktestParameters` currently refuses vol overlay on
cross_sectional_momentum; that refusal predates this hypothesis and is
lifted as part of this experiment's engine work. The overlay application
in the cs path must reuse `_vol_scaler` verbatim (no second vol formula in
the codebase). Implementation and tests land BEFORE the first family run;
runs happen on a clean committed tree.

## Honesty clauses

- Registry N grows to ≥ 53; every DSR pays the larger deflation. If that
  sinks the family, the verdict stands.
- Survivorship bias of the 13-symbol universe carries over unchanged
  (UNIVERSE_EXPANSION.md); the holdout remains the arbiter.
- The §1 candidates-key folding defect documented in the experiment-3
  result applies to this family too (identical cs_* fields per row except
  the vol_* fields, which ARE in the key — so these 16 rows will NOT fold
  with each other, but their key overlap with rows 22-37 is recorded for
  October's read-out).
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it. Editing after the first run voids the family.

# Goal P pre-registration — experiment 1: two-day confirmation variant

Date registered: 2026-07-18 (BEFORE any variant backtest is run)
Basis: docs/research/WHIPSAW_DIAGNOSTIC.md verdict (2026-07-15) — hysteresis /
N-day-confirmation experiments lead the Goal P queue.
Rule: this document is written first; the backtest runs after; the numbers
land in the trial registry whatever they say. Editing this file after seeing
results voids the experiment.

## Hypothesis

The Daily Trend Ensemble's dominant cost is whipsaw: ~63 ladder changes per
symbol-year, with 2019/2023-style regimes breaching the published
turning-point thresholds. Requiring a changed ladder proposal to persist for
**2 consecutive daily closes** before adoption will:

1. cut ladder-change count (turnover) by a meaningful fraction, and
2. improve the deflated risk-adjusted result enough to matter at the gate,
3. without giving up so much entry/exit timeliness that returns collapse.

## Variant definition (exact)

`confirmed_trend_ensemble(confirm_days=2)` — a stateful wrapper around the
unchanged Daily Trend Ensemble:

- Compute the raw ensemble proposal each close (same four SMAs, same ladder).
- If the proposal equals the currently held fraction → hold; reset the
  pending counter.
- If the proposal differs → count consecutive closes with that SAME proposal;
  adopt only when the count reaches 2. A different proposal mid-count resets
  the counter to 1 for the new proposal.
- **Symmetric**: confirmation applies to ladder-ups AND ladder-downs. The
  asymmetric variant (instant exits, confirmed entries) is a SEPARATE future
  experiment; running both now doubles N for one idea. The single-day
  disaster brake (−20%) stays active in the risk layer regardless, so the
  worst crash-day exposure is unchanged.
- All other layers (portfolio budgets, risk gate, costs, universe, window)
  identical to trial 2/4.

## What runs

Exactly ONE registered trial: `confirm_days=2`, BTC+ETH, full pre-holdout
window (2018-03-04 → 2025-07-01), production backtest engine, standard costs
(10 bps fee + 5 bps slippage). No parameter scan: N is a budget, and this
experiment spends exactly 1 (registry N: 4 → 5).

## Success criteria (set before running)

The variant is considered WORTH PROMOTING to the next evidence step only if
ALL of:

1. **Turnover**: ladder changes per symbol-year fall by ≥ 25% vs trial 4
   (the mechanism must actually fire);
2. **Risk-adjusted**: annualized Sharpe ≥ trial 4's (1.02); whipsaw removal
   that costs more edge than it saves is a fail;
3. **Drawdown**: max drawdown not worse than trial 4's by more than 5pp;
4. **Gate direction**: its DSR under the registry-wide report
   (`scripts/run_gate_report.py`, N=5 after registration) is ABOVE trial 4's
   recomputed DSR in the same report — deflation-adjusted improvement, not
   raw improvement.

Anything less: the variant is recorded as a registered negative result and
the queue moves on (volatility targeting, P2-11). No re-runs with tweaked
confirm_days to rescue it — that is the researcher degree of freedom this
repository exists to refuse.

## What this experiment cannot say

- Nothing about the holdout (locked, single-use, untouched).
- Nothing about live behavior (the observation run stays on the original
  contract; variants exist only in the backtest path, and the runtime
  refuses variant strategy names by construction).
- DSR arithmetic note: adding any trial changes every trial's deflation
  (variance and N move). Criterion 4 therefore compares WITHIN the same
  N=5 report, never across reports.

# Robustness battery on trial 88 — pre-registration (NOT a search)

Status: **FROZEN on commit**. Written 2026-07-25 before any run.

## What this is, and what it is not

This is an attempt to KILL trial 88 (Donchian 10/20/55/110, mid_channel
exit, no gate, BTC/ETH — the registry's best risk-compliant trial:
Sharpe 1.1821, DSR 0.9330, MDD 33.05%). It is adversarial verification,
not search.

**Binding rule: no configuration run under this document may ever be
nominated, adopted, or reported as an improvement, even if it scores
better than trial 88.** Perturbation rows exist only to measure the
DISPERSION of trial 88's neighborhood. Reading a better neighbor as a
"finding" would be exactly the overfitting this battery is designed to
detect. Cost-stress rows carry `cost_multiplier != 1` and are already
excluded from the gate-3 candidate matrix by PRE_HOLDOUT_PROTOCOL §1.

Registry discipline is unchanged: every run is registered, N rises, and
every trial's DSR bar rises with it. That price is paid knowingly — the
question "is our best candidate a knife-edge fit?" is worth more than the
~0.002 DSR the extra rows cost.

## Battery A — parameter neighborhood (6 runs)

Same universe, exit, and gate settings as trial 88; only the window set
moves:

| Arm | Windows | Shift |
|---|---|---|
| A1 | 8, 16, 44, 88 | −20% |
| A2 | 12, 24, 66, 132 | +20% |
| A3 | 7, 14, 39, 77 | −30% |
| A4 | 13, 26, 72, 143 | +30% |
| A5 | 11, 18, 60, 100 | jitter (mixed) |
| A6 | 9, 22, 50, 120 | jitter (mixed) |

**Pre-declared stability verdict (all must hold):**

1. All six arms produce annualized Sharpe ≥ 1.00 (trial 88 is 1.1821; a
   neighborhood that collapses below 1.0 under a ±20-30% shift is a
   knife-edge fit).
2. All six arms produce MDD ≤ 51.93% (the statutory risk bar).
3. Neighborhood Sharpe spread (max − min) ≤ 0.35.

Any breach → trial 88 is recorded as parameter-fragile, and no future
pre-registration may nominate it without the fragility stated in the same
document.

## Battery B — cost stress (2 runs)

Trial 88's exact configuration at `cost_multiplier` 2 and 3 (fees and
slippage both scaled).

**Pre-declared cost verdict (both must hold):**

1. At 2× costs: Sharpe ≥ 1.00 and total return positive.
2. At 3× costs: Sharpe ≥ 0.80 and total return positive.

A strategy whose edge dies at realistic execution friction is not
tradeable regardless of its backtest Sharpe.

## Read-outs (non-gating, declared now)

- Sharpe/MDD/turnover/final equity for all eight runs.
- Whether the neighborhood's central tendency sits above or below trial
  88 (a trial 88 that is the neighborhood MAXIMUM is weaker evidence than
  one sitting mid-pack).

## Honesty clauses

- The already-completed zero-cost diagnostics (bootstrap CI, subperiod
  split, rolling-window, tail-drop, blend with trial 4 — from existing
  return series, no new trials) are reported in the result document
  alongside these runs. Their numbers were read BEFORE this document was
  written and are stated as prior context, not as criteria.
- Nothing here touches the October holdout, its fixed nominations, or the
  live contract.

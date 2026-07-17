# Strategy contract: Confirmed Trend Ensemble (backtest-only variant)

Status: registered Goal P experiment variant — **NOT eligible for the live
runtime** during the qualification run. Pre-registration:
`docs/research/GOALP_PREREGISTRATION.md`.

## Definition

A stateful confirmation wrapper around the unchanged
[Daily Trend Ensemble](STRATEGY_DAILY_TREND_ENSEMBLE.md):

- Each daily close, compute the raw ensemble proposal (same four SMAs
  20/65/150/200, same {0, 25, 50, 75, 100}% ladder, equality counts as NOT
  above).
- Adopt a proposal that differs from the held fraction only after it has
  appeared on `confirm_days` (= 2) **consecutive** closes. A different
  proposal mid-count restarts the count at 1 for the new proposal. A
  proposal equal to the held fraction resets the count.
- Confirmation is **symmetric** (applies to ups and downs). The risk layer's
  single-day disaster brake is unaffected.
- While pending, the decision holds the previous fraction and carries
  `PENDING_CONFIRMATION_<seen>_<needed>` in its reason codes; adoption adds
  `CONFIRMED_AFTER_<needed>`.

## State

The wrapper is a pure function over an explicit
`ConfirmationState(pending_fraction, pending_days)` carried by the caller
(the backtest engine). No hidden state; identical inputs give identical
outputs, preserving replay determinism.

## Boundaries

- Signals remain `LONG`/`FLAT`; fractions remain in {0, .25, .5, .75, 1}.
- The live runtime hardcodes the original ensemble and MUST reject this
  strategy name if configured; the qualification run's contract is frozen.
- Any change to `confirm_days` is a NEW variant: new registry entry, counts
  toward N.

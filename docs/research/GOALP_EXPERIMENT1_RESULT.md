# Goal P experiment 1 — result: registered negative (criteria 2 & 4 failed)

Executed: 2026-07-18 · Trial: **5** (registry N: 4 → 5)
Pre-registration: `docs/research/GOALP_PREREGISTRATION.md` (unmodified)
Variant: `confirmed_trend_ensemble(confirm_days=2)`, full pre-holdout window,
standard costs, production engine.

## Numbers vs baseline (trial 4, same window and costs)

| Metric | Trial 4 (raw) | Trial 5 (confirmed) | Δ |
|---|---:|---:|---|
| Trade count | 932 | 476 | **−48.9%** |
| Annualized turnover | 17.69 | 10.22 | **−42.2%** |
| Annualized Sharpe | 1.0230 | 1.0170 | −0.006 |
| Max drawdown | 51.9% | 51.0% | −0.9pp |
| Final equity (1000 start) | 14,221.28 | 14,424.02 | +1.4% |
| DSR (same N=5 report) | 0.8366 | 0.8322 | −0.004 |

## Verdict against the pre-registered criteria

1. Turnover −25% or better: **PASS** (−48.9% trades, −42.2% turnover — the
   mechanism fires exactly as designed).
2. Sharpe ≥ 1.02: **FAIL** (1.0170).
3. Drawdown not worse by 5pp: PASS (improved 0.9pp).
4. DSR above trial 4 within the same report: **FAIL** (0.8322 < 0.8366).

All four were required. **The variant is a registered negative result.** Per
the pre-registration: no confirm_days re-tuning to rescue it; the queue
advances to volatility targeting (P2-11).

## Honest reading

Two-day confirmation does what the whipsaw hypothesis promised mechanically
— half the trades, half the fees (527 vs 1,046 USDT), slightly higher final
equity, slightly shallower drawdown — and still fails to improve the
risk-adjusted, deflation-adjusted number the gate actually cares about. The
one-day delay on real regime changes costs roughly what the skipped whipsaws
save. "Fewer trades" was never the goal; "more edge per unit of risk after
honest deflation" was, and it did not materialize.

## Side effect that matters more than the experiment: PBO jumped to 0.88

Registry-wide gate report after registration (N=5):

- Gate 3 PBO: **0.018 (N=4) → 0.879 (N=5)** — gate 3 now FAILS.
- Gate 4 DSR: all five trials below 0.95 (expected-max Sharpe rises with N,
  as it must).

Why: CSCV treats every registry column as a competing configuration. Four of
our five columns (trial 2, its cost-stress rerun 3, its parity rerun 4, and
now variant 5) are near-duplicates of one strategy — their in-sample ranking
differences are mostly noise, so the in-sample winner mean-reverts out of
sample and PBO explodes. That is CSCV working as designed: picking the best
of five nearly identical strategies IS overfitting.

Consequence recorded for the October sign-off: the gate contract must define
BEFORE the holdout is opened which registry columns constitute the PBO
matrix (competing candidate configurations vs reruns/stress-tests of one
configuration). Deciding that rule after seeing holdout results would be
window-shopping; deciding it now, before any holdout access, is legitimate
methodology clarification. Until then, the honest headline number is the
strict all-columns PBO above.

## Provenance note

The trial was run BEFORE this change set was committed; the registry records
`code_version: 91db492-dirty`. The working tree at run time contained exactly
the variant implementation committed immediately after (same session). Future
experiments: commit first, then run — the registry's dirty flag exists to
make this ordering mistake visible, and it did.

## Not done (by rule)

- No confirm_days scan (each value would be a new N).
- No asymmetric variant this round (separate future pre-registration).
- Holdout untouched; live qualification run unaffected.

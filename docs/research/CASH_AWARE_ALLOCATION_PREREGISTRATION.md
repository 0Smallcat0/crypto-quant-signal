# Cash-aware sleeve allocation — pre-registration

Written 2026-07-26, **before the computation was run**, frozen on commit.

Goalpost-drift guard: this pre-registration is written in the same sitting
that read the diagnostic below, under the operator's standing instruction
(「你就繼續做，不用停下來」). That override is recorded here rather than
left implicit, as with the previous six.

## The measurement that motivates it

`scripts/analyze_idle_capital.py` over the three registered sleeve reports,
common decision window 2018-03-04 → 2025-07-01, 2,677 days:

| Sleeve | Mean deployed | Days fully flat |
|---|---:|---:|
| crypto (trial 88) | 0.3785 | 27.8% |
| taiwan (trial 23) | 0.3269 | 47.9% |
| gold (trial 24) | 0.3087 | 50.4% |

**Three-sleeve book mean gross exposure: 0.3380. Mean cash: 0.6620.**

| Sleeves long at once | Days | Share |
|---|---:|---:|
| 0 | 337 | 12.6% |
| 1 | 865 | 32.3% |
| 2 | 633 | 23.6% |
| 3 | 842 | 31.5% |

On **87.4% of days at least one sleeve is long**, yet the book holds an
average of 66% cash. Under fixed equal weights, a sleeve sitting flat does
not release its third of the book — that capital simply idles.

That is the honest explanation for the terminal-wealth cost recorded in
`SLEEVE3_GOLD_RESULT.md` (14.26× → 6.00× → 3.94×). It is not mostly the
arithmetic of diversification. It is a third of the book doing nothing
because gold happened to be flat.

## The rule being tested — zero free parameters

**Equal share among the sleeves that are actually long.**

    w_i(t) = 1 / n_active(t)   if sleeve i has exposure > 0 at t
           = 0                 otherwise
    book return(t) = sum of w_i(t) * R_i(t),  and 0 when n_active(t) = 0

where `R_i(t)` is sleeve i's own realized daily return from its registered
report, and exposure comes from that report's `targets[].cash_weight`.

Properties, all forced rather than chosen:

- **Gross exposure never exceeds 1.** Book gross is the mean of the active
  sleeves' own exposures, and no sleeve exposure exceeds 1. **No leverage
  is introduced**, which keeps permanent product law (spot, long-only,
  unlevered) intact. This is the property that makes the test admissible at
  all.
- **Nothing is tuned.** There is no cap parameter, no target volatility, no
  tilt, no lookback. The two designs compared are the only two natural
  endpoints: fixed equal weights (already published) and equal weights among
  the active.
- **Both designs are reported**, whatever the outcome.

## Pre-declared criteria

Evaluated on the same three-way common window, against the equal-weight
three-sleeve book recomputed identically (Sharpe 1.4108, MDD 14.90%,
3.94×):

1. **It must actually recover money.** Terminal multiple strictly greater
   than 3.94×.
2. **It must not hand back the drawdown benefit.** Max drawdown strictly
   below the two-sleeve book's 19.73% — the three-sleeve book may give up
   some of its drawdown advantage but must still beat the book it was
   introduced to improve.
3. **It must not be a Sharpe downgrade.** Sharpe at least 1.3437, the
   two-sleeve figure. A cash-aware book that concentrates into fewer sleeves
   and scores worse risk-adjusted than the simpler design has no case.

**PASS requires all three.** Failing any is a registered negative and gets
written up with the numbers that failed. In particular, if concentration
raises the drawdown materially, that is the finding: the idle cash was
buying something real.

## Declared limits, before the result

- **Trading costs of reallocation are NOT modeled.** This computation
  reweights already-computed sleeve returns; a real book would trade between
  sleeves whenever `n_active` changes, and `n_active` changes often. The
  measured result is therefore an **upper bound** on what the rule could
  deliver, and it must be reported as one. If it passes, the next step is an
  engine-level run that pays those costs — not a claim.
- **Daily reallocation is assumed.** The published equal-weight books
  rebalance monthly precisely to avoid pointless trading; this design cannot,
  because its whole mechanism is reacting to sleeve state. That asymmetry
  favours this design and is stated rather than buried.
- **It registers no trial and produces no DSR.** Portfolio-level analysis of
  existing rows, as with both previous combination results.
- **FX still not modeled** across three currencies.
- **Never nominatable** for the October holdout.
- **One window, one regime set.** 7.3 years containing one crypto cycle.

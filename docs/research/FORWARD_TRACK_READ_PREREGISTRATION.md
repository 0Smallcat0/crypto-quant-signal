# Forward-track read rule — pre-registration

Date written: 2026-07-28 · Written at **4 forward rows**, deliberately
before the data can influence the rule · Zero registry cost (no backtest
run, no trial registered).

## Why this document exists

Since 2026-07-24 three forward shadow tracks have been recording. Every
queue revision since then has said "keep the tracks recording" and
"forward evidence is the binding constraint". **No document said how the
tracks would be read.** That is the hole this closes.

Reading forward data without a rule fixed in advance is exactly the
failure the six gates exist to prevent: whoever opens the file first will
pick the metric that looks best. The tracks currently hold 4 rows, so a
rule written today cannot have been chosen to fit them. Every day of
delay makes that less true.

## The finding that forced this to be written today

The loop contract states the unblocking condition as:

> ~90 days of forward rows on all three tracks (from 2026-07-24), enough
> to say anything at all about whether the measured edge persists.

**That is wrong, by roughly a factor of eight.** Measured on the durable
return series of the two shadowed trials (`trial_returns/trial-000088.json`,
`trial-000118.json`, n=2676 each, 365-period annualization matching the
registry's own `annualized_sharpe`):

| Trial | SR (ann.) | skew | kurtosis | MinTRL 90% | MinTRL 95% |
|---:|---:|---:|---:|---:|---:|
| 88 | 1.1823 | +0.227 | 12.775 | 429 d (2027-09-26) | **706 d (2028-06-29)** |
| 118 | 1.2413 | +0.157 | 12.980 | 391 d (2027-08-19) | **644 d (2028-04-28)** |

MinTRL is Bailey & López de Prado's Minimum Track Record Length — the
same authors and the same distributional machinery as the Deflated Sharpe
Ratio this program already uses in gate 4, so adopting it introduces no
new assumption the program was not already making:

```
MinTRL = 1 + [1 - g3*SR + (g4-1)/4 * SR^2] * (Z / (SR - SR*))^2
```

with per-period SR, SR* = 0, and the series' own skew/kurtosis. The fat
tails do most of the damage: at kurtosis 12.8, MinTRL is roughly double
what a normality assumption would give.

Standard error of the forward Sharpe, same series:

| Forward N | SE (ann.) | 95% CI around 1.18 |
|---:|---:|---|
| 90 d (2026-10-22) | 2.016 | **[-2.77, +5.13]** |
| 182 d | 1.418 | [-1.60, +3.96] |
| 365 d | 1.001 | [-0.78, +3.14] |
| 730 d | 0.708 | [-0.21, +2.57] |

**At the 90-day mark the forward track cannot distinguish a Sharpe of
-2.7 from one of +5.1.** It is not weak evidence about return. It is no
evidence about return. Even a full year does not exclude zero.

This is not an argument for stopping. It is an argument for reading the
tracks for what they can actually answer, and for saying out loud that
the return question has a **2028** answer date under the current design.

## The rule, fixed as of 2026-07-28

### Read dates

- **2026-10-22** (90 d) — implementation read. Not a verdict.
- **2027-01-24** (~6 mo), **2027-07-24** (1 y) — implementation reads,
  plus the refutation checks below. Still not confirmation.
- **2028-06-29** (trial 88 MinTRL 95%) — the first date on which a
  return-based positive verdict is statistically permitted at all.

No read may be moved earlier because a number looks good. Health checks
(does the file have a new row) are unrestricted and are not reads.

### Test 1 — implementation agreement. Primary. Full power at any N.

Replay the strategy offline over the forward window and compare the
recomputed exposure path against the recorded one, per symbol, per date.

- **Pass** = exact agreement on every recorded date.
- **Any mismatch = implementation defect. Halt and fix before any other
  reading of the track.** A shadow track that does not reproduce is not
  evidence of anything.

This is deterministic, not statistical, so it has full power at 4 rows
and at 4000. It is the only test the 90-day read can actually settle,
which is precisely why it is the primary one.

### Test 2 — refutation by drawdown breach. Asymmetric, one-sided.

The backtest max drawdown is **33.05%** (trial 88) and **33.24%**
(trial 118), recorded in the registry.

- If forward drawdown **exceeds the backtest maximum** at any read date,
  that is recorded as evidence **against** the strategy generalizing, and
  it counts at any N — a tail breach does not need MinTRL, because the
  claim being refuted is about the tail, not the mean.
- Not breaching is **not** evidence in favour. It is declared here, in
  advance, as uninformative.

### Test 3 — return. Refutation-permitted, confirmation-forbidden until MinTRL.

- Before 2028-06-29: a forward Sharpe below zero may be **recorded** as
  a negative signal, but a forward Sharpe above zero may **not** be cited
  anywhere as support. Any document that does so is wrong and must be
  corrected in place the same day, under the standing correction duty.
- From 2028-06-29: the MinTRL condition is met for trial 88 at 95%
  one-sided against SR* = 0, and a return-based verdict becomes
  permissible — against SR* = 0 only, which is a weak null and must be
  described as such.

### What may not be added

No metric, sub-period, symbol subset, or alternative benchmark may be
introduced at read time. The exposure-matched twin comparison is the
program's preferred quality metric, but it is **not** part of this rule
because no twin series is being recorded forward; adding one later would
be a post-hoc metric choice. If a twin track is wanted it must start
recording now, under its own pre-registration, and it may not be
back-filled.

## Consequence the operator should see plainly

Under the current design the honest answer date for "does the crypto
timing edge survive out of sample?" is **2028**, not October 2026. Three
levers could move that date, all of them the operator's to pull, none of
them available to the loop:

1. Accept a weaker confidence level — 90% one-sided moves trial 88 to
   **2027-09-26**. Still not this year.
2. Accept the October holdout as the answer instead. It is single-use,
   nominations are fixed, and it tests a different question — whether the
   candidate survives the search history, not whether it works forward.
3. Override P3 and search for a **higher-Sharpe or higher-frequency**
   design, since MinTRL falls with the square of the Sharpe. This costs
   an N and reopens every overfitting risk the program spent 24
   iterations documenting.

Nothing here changes any recorded verdict, spends the holdout, touches
`configs/runtime/`, or proposes a new family.

## Method note

Numbers computed from `docs/reports/research/trial_returns/trial-000088.json`
and `trial-000118.json` (n=2676 each). The 365-period annualization was
not assumed — it was verified: 0.06188 * sqrt(365) = 1.1823, matching the
registry's recorded `annualized_sharpe` of 1.182061 for trial 88 exactly.
A first pass of this analysis used 252 and produced 2.80 years instead of
1.93; that pass was wrong and its number appears nowhere in this document.

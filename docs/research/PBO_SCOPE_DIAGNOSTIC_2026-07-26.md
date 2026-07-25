# PBO scope diagnostic — the gate-3 failure is not a scoping artefact

Date: 2026-07-26 · Registry N=133 · Zero registry cost (re-analysis of
existing return series; no backtest run, no trial registered).

## The question

Gate 3 fails by an order of magnitude (candidates-PBO 0.6518 against a
0.05 bar). One plausible excuse was available: CSCV over ~100 columns of
one strategy lineage measures "can you rank near-duplicates", and
near-duplicates are unrankable almost by construction. If that were the
whole story, PBO computed over genuinely DIFFERENT architectures would be
much lower, and the failing gate would be an artefact of column
composition rather than evidence about the strategies.

**It is not the whole story. The excuse is dead.**

## Measurement

One representative per distinct strategy architecture, nine columns:

| Trial | Architecture |
|---:|---|
| 4 | live daily trend ensemble (the incumbent) |
| 7 | ladder + volatility-target overlay |
| 29 | cross-sectional momentum (exp-3 winner) |
| 56 | cross-sectional momentum + SMA regime gate |
| 78 | multi-horizon trend factor under a gate |
| 96 | Donchian, 13-symbol staggered, equal weight |
| 88 | Donchian BTC/ETH, mid-channel exit |
| 112 | Donchian + inverse-vol sizing |
| 118 | Donchian + ATR channel exit (the current best) |

| Column set | Columns | PBO |
|---|---:|---:|
| all columns | 133 | 0.7326 |
| candidates (protocol §1) | ~100 | 0.6518 |
| **distinct family** | **9** | **0.7411** |

Narrowing to genuinely different architectures made PBO **worse**, not
better. Nothing about the gate-3 failure is explained by duplicate
columns.

## What this actually says

PBO is the probability that the configuration selected as best in-sample
lands below the median out-of-sample across 12,870 train/test splits.
At 0.74 across nine distinct architectures, in-sample ranking of these
strategies is **worse than a coin flip** at predicting out-of-sample
ranking inside this window.

Two honest readings, both of which matter:

1. **Selection here is unreliable, full stop.** Trial 118 clearing gate 4
   says its own deflated performance survives the search history. It does
   NOT say it will be the best of these nine out of sample — this
   diagnostic says the opposite is more likely than not. Every claim
   about trial 118 must carry that.
2. ~~**The constraint space may be too narrow to support reliable
   selection**, because all nine share 0.9+ correlated long-only crypto
   trend beta.~~ **RETRACTED 2026-07-26, same day, on measurement.**
   The pairwise correlations were asserted, not computed. Measured on the
   same nine return series: **mean 0.628, minimum 0.359, maximum 0.958**.
   These architectures are substantially more diverse than the retracted
   claim said, so "everything is the same trade" does not hold and cannot
   be used to argue that gate 3 is structurally unpassable. Any future
   document repeating that argument is repeating a refuted one.

Reading 1 stands unchanged and is the finding: selection among these
strategies does not generalize inside this window. Reading 2 was wrong.

What the measured correlations DO support is the opposite kind of
conclusion, pursued separately: if candidates are only ~0.63 correlated,
a diversified combination of them carries real variance reduction, and a
combination rule performs no selection at all — which is the textbook
response to a high PBO. That direction is being taken up under its own
pre-registration; nothing in this document evaluates it.

## What does not change

- Gate 3's rule stays frozen until the holdout is spent
  (PRE_HOLDOUT_PROTOCOL §1). This diagnostic changes no verdict and is
  not a candidate-rule proposal.
- Trial 118's gate-4 pass at N=125 and N=133 stands as recorded.
- The October holdout nominations stay fixed.
- The forward shadow tracks (trial 88, trial 118, daily since
  2026-07-24) become MORE important, not less: if in-sample ranking is
  uninformative, out-of-sample observation is the only thing that can
  discriminate, and it is the one form of evidence this project can still
  accumulate honestly.

## Method note

`scripts/analyze_pbo_scope.py`, CSCV with S=16 blocks (12,870
combinations), computed on the durable per-trial return series over the
identical 2676-day window. The representative list was chosen before the
number was computed and is recorded above in full; no alternative
representative set was tried after seeing this result, and none may be
without a pre-registration, because "search for a column set that makes
PBO look better" is precisely the behaviour the gate exists to catch.

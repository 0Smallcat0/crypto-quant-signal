# Every trial against buy-and-hold — corrected

Diagnostic, 2026-07-26. `scripts/analyze_registry_vs_benchmark.py` over all
133 registry rows. No backtest, no new row, no holdout contact.

> **Retraction, same day.** The first version of this document pooled
> experiments 7 and 8 into one "donchian family" of 16 rows and reported
> **"8 of 16 beat buy-and-hold — a coin flip"**, concluding that roughly
> half of trial 88's edge was selection. That was wrong. The two
> experiments run **different universes** — experiment 7 is BTC/ETH only,
> experiment 8 is the 13-symbol staggered book, declared as a separate test
> in experiment 7's own pre-registration (lines 101-102: *"BTC/ETH-only
> scope is declared UP FRONT; a future 13-symbol ladder needs engine work
> and its own pre-registration"*). Pooling them produced a 50% that is the
> average of 100% and 0%. The grouping key now includes the experiment
> number so the error cannot recur. Corrected numbers below.

## The corrected headline

Trial 88's actual family is **experiment 7: 8 configurations, BTC/ETH only.**

| Experiment 7 (BTC/ETH, 8 rows) | Value |
|---|---:|
| Trial 88 system/benchmark ratio | **2.381** |
| Family median ratio | 2.005 |
| Family best / **worst** | 2.381 / **1.789** |
| Members beating buy-and-hold | **8 / 8 (100%)** |

**Every member of the family beat buy-and-hold, the worst by 79%.** The
selection premium for having picked trial 88 over a random family member is
2.381 / 2.005 = **+18.8%**, not the ~50% the retracted version claimed.

Within BTC/ETH over 2018-2025, this is not a coin flip and not a tail draw.
The effect is robust to every parameter that grid varied.

## And then it dies the moment the universe changes

| Experiment 8 (13 symbols, 8 rows) | Value |
|---|---:|
| Median ratio | **0.543** |
| Best / worst | 0.695 / 0.419 |
| Members beating buy-and-hold | **0 / 8 (0%)** |

Same rule, same windows, same exits, same gate arms — eleven more symbols.
**Not one configuration beats holding the assets.** The best of eight
returns 69.5% of what buy-and-hold returned.

That is a cleanly pre-registered comparison: experiment 7 declared the
13-symbol book as a future separate test rather than folding it in
post-hoc, and experiment 8 ran it.

## Every family, universe-aware

| Family | n | Beat | Share | Median ratio |
|---|---:|---:|---:|---:|
| other exp1 | 1 | 1 | 100.0% | 2.413 |
| other exp2 | 16 | 16 | 100.0% | 2.034 |
| cross-sectional momentum exp3 | 16 | 3 | 18.8% | 0.643 |
| other exp4 | 16 | 7 | 43.8% | 0.670 |
| regime gate exp5 | 16 | 4 | 25.0% | 0.439 |
| regime gate exp6 | 16 | 3 | 18.8% | 0.729 |
| **donchian exp7 (BTC/ETH)** | **8** | **8** | **100.0%** | **2.005** |
| **donchian exp8 (13 symbols)** | **8** | **0** | **0.0%** | **0.543** |
| other exp9 | 8 | 8 | 100.0% | 1.500 |
| other exp10 | 8 | 8 | 100.0% | 2.349 |
| other (unlabelled) | 19 | 18 | 94.7% | 2.251 |
| **all rows** | **133** | **77** | **57.9%** | **1.099** |

The distribution is **bimodal, not random**. Families either beat
buy-and-hold in every arm (exp 1, 2, 7, 9, 10) or lose in most of them
(exp 3, 5, 6, 8). The overall 57.9% is the average of those two modes and
means little on its own — the same pooling mistake at a larger scale.

## What this actually establishes

**The effect within BTC/ETH is real and parameter-robust.** Eight of eight
configurations, worst case +79% over buy-and-hold. Selection explains about
19% of trial 88's margin, not half of it. The retracted claim was too harsh
and is withdrawn.

**And the effect is confined to BTC/ETH.** Every out-of-scope test lands
below the family's *worst* member:

| Test | Ratio vs buy-and-hold | Family floor was 1.789 |
|---|---:|---|
| 13-symbol crypto book (exp 8, 8 arms) | 0.419 – 0.695 | all below |
| Taiwan 0050, 21 years | 0.277 | far below |
| Gold GLD, 20 years | 0.349 | far below |

So the honest statement is narrower and more specific than either previous
version: **not "the winner was cherry-picked", and not "the rule works" —
but "the rule works on BTC/ETH in this window, robustly, and has failed
every extension tested: more crypto symbols, another equity market, and
another asset class."**

That is a statement about scope, and scope is testable going forward.

## What it does not establish

- **It does not rescue the combination.** The three-sleeve book still made
  3.94× against 5.42× for holding the same assets
  (`VS_BUY_AND_HOLD_2026-07-26.md`).
- **It does not make trial 88 safe.** Robustness to *this* grid's parameters
  is not robustness to the choice of grid, and PBO 0.7411 measured across
  distinct architectures still stands.
- **One window, one crypto cycle.** BTC/ETH 2018-2025 contains a single
  full bull-bear cycle. "Robust across 8 configurations of one window" is a
  much weaker claim than it sounds.
- **No risk adjustment.** These are return ratios; the benchmark carried an
  80.99% drawdown against trial 88's 33.05%.

## Limits of the method

- Families are inferred from `operator_note` plus the `exp N` tag, because
  the registry's parameters block was a hardcoded constant until
  2026-07-26. The unlabelled "other" bucket (19 rows) is heterogeneous.
- Rows in different experiments may span different windows and universes;
  only within-family comparisons are strictly sound. That is the whole
  lesson of the retraction above.

## Reproduce

```
python -m scripts.analyze_registry_vs_benchmark
```

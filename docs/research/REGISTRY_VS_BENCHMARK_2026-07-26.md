# The winner is the maximum of its family, and half the family loses to holding

Diagnostic, 2026-07-26. `scripts/analyze_registry_vs_benchmark.py` over all
133 registry rows. No backtest, no new row, no holdout contact. Every number
was already in the registry and had never been read.

## The headline

Trial 88 — the crypto sleeve carried into every combination result — made
**2.381×** what buy-and-hold made over the same window.

Its family made a median of **1.242×**, and **8 of its 16 members lost to
buy-and-hold outright**.

**Trial 88 ranks 1 of 16.** It is the maximum.

| Donchian family (16 rows) | Value |
|---|---:|
| Trial 88 system/benchmark ratio | **2.381** |
| Family median ratio | 1.242 |
| Family best / worst | 2.381 / 0.419 |
| Members beating buy-and-hold | 8 / 16 (50.0%) |

A coin flip decides whether a member of this family beats holding the asset,
and the configuration this program carried forward is the single best draw.
That is the textbook signature of a search finding a tail, and it is the
same conclusion the program's PBO (0.7411) reached by a different route.

## Every family

| Family | n | Beat buy-and-hold | Share | Median ratio |
|---|---:|---:|---:|---:|
| other (baseline + misc) | 68 | 58 | 85.3% | 1.971 |
| regime gate | 33 | 8 | 24.2% | 0.697 |
| donchian | 16 | 8 | 50.0% | 1.242 |
| cross-sectional momentum | 16 | 3 | 18.8% | 0.643 |
| **all rows** | **133** | **77** | **57.9%** | **1.099** |

Across the whole search, **57.9% of registered trials beat simply holding**
— barely better than a coin flip — with a median ratio of 1.099. Two whole
families (regime gate, cross-sectional momentum) lose to buy-and-hold in
about three quarters of their configurations.

## What this changes

The estimate. Not the measurement — trial 88 really did return 14.26× —
but what a person should *expect* from it going forward.

- **If the configuration were drawn at random from its family**, the
  expected ratio is 1.242, not 2.381. Roughly **half the measured edge over
  buy-and-hold is attributable to having picked the best member.**
- The out-of-market tests came in **below even the family median**: Taiwan
  0.277 (2.15× against 7.75×), gold 0.349 (2.44× against 6.99×). Selection
  plus transfer decay, in the direction this predicts.
- Combined with `SELECTION_PROVENANCE_CORRECTION_2026-07-26.md` — the
  windows and exit were themselves selected on crypto data — the honest read
  is that trial 88's advantage over buy-and-hold is **substantially, though
  probably not entirely, a selection artefact.**

Fourth independent line of evidence, all pointing the same way: PBO 0.7411,
trial 118's cross-market refutation, the buy-and-hold underperformance in
two of three markets, and now the family-rank result.

## What it does not establish

- **It is not proof the edge is zero.** The family median ratio is 1.242,
  above 1. A randomly-chosen member of this family still beat buy-and-hold
  on average over this window. The claim is that the *measured* 2.381 is
  inflated, not that the true value is 1.0.
- **The family median is not an unbiased out-of-sample estimate either.** It
  is merely less biased than the maximum. Only forward data settles it.
- **A ratio above 1 does not mean the system is preferable.** Buy-and-hold
  crypto carried an 80.99% drawdown over this window; trial 88 carried
  33.05%. Return ratio is one axis.

## Limits of the method

- **Families are inferred from `operator_note` strings**, because the
  registry's parameters block was a hardcoded constant until today. The
  "other" bucket (68 rows) is heterogeneous and its 85.3% beat rate should
  not be read as one finding.
- **Rows span different windows and universes**, so ratios are strictly
  comparable only within a family that pinned its window. Experiment 8
  pinned its window explicitly; the cross-family table is indicative.
- **No risk adjustment.** This table is return against return.

## Reproduce

```
python -m scripts.analyze_registry_vs_benchmark
```

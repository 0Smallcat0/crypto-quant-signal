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

---

## Addendum 2026-07-27 — why 13 symbols lost, and the one mechanism underneath everything

`scripts/analyze_symbol_dispersion.py` over the 13 local candle files, same
window. Buy-and-hold per name:

| Symbol | Listed | Buy-and-hold | Max drawdown |
|---|---|---:|---:|
| BNBUSDT | 2018-03-06 | **68.83×** | 76.07% |
| SOLUSDT | 2020-08-11 | **44.53×** | 96.27% |
| DOGEUSDT | 2019-07-05 | **40.77×** | 92.33% |
| LINKUSDT | 2019-01-16 | 26.35× | 90.18% |
| BTCUSDT | 2018-03-06 | 9.86× | 76.63% |
| TRXUSDT | 2018-06-11 | 5.76× | 83.11% |
| AVAXUSDT | 2020-09-22 | 3.21× | 93.49% |
| ETHUSDT | 2018-03-06 | 2.96× | 89.78% |
| XRPUSDT | 2018-05-04 | 2.44× | 84.99% |
| ADAUSDT | 2018-04-17 | 2.23× | 93.74% |
| DOTUSDT | 2020-08-18 | 1.06× | 94.14% |
| XLMUSDT | 2018-05-31 | 0.76× | 90.49% |
| LTCUSDT | 2018-03-06 | 0.42× | 88.78% |

Mean 16.09×, **median 3.21×**. Top 1 name is 32.9% of the summed return,
top 2 is 54.2%, **top 3 is 73.7%**. Two names lost money outright.
**Every single name drew down at least 76%.**

### The obvious reading, and why it is not enough

The intuitive story is skew: a trend rule exits on weakness, so it trims
exactly the names carrying the return. True as far as it goes — but
**BTC/ETH is *more* top-heavy by that measure**, not less (BTC is 76.9% of
that two-name sum against the 13-coin universe's 32.9%), and the rule *won*
there. Concentration alone does not separate the cases.

### What does separate them

| | Sleeves | Rule returned | Best constituent held | Benchmark |
|---|---:|---:|---:|---:|
| Experiment 7 | 2 | **14.26×** | 9.86× (BTC) | 6.05× |
| Experiment 8 | 13 | 9.39× (best arm) | 68.83× (BNB) | 13.53× |

On two names the rule returned **more than either constituent's own
buy-and-hold**. On thirteen it returned less than the average one.

The mechanism is already measured elsewhere in this program:
`CASH_AWARE_ALLOCATION_RESULT.md` found the three-sleeve book sits in
**66.2% cash**, because each sleeve exits independently and its share of
the book idles while it is flat. Thirteen independently-exiting sleeves
idle far more than two. Against a benchmark that rose 13.53×, idle capital
is ruinous; against one that rose 6.05× carrying an 81% drawdown, the
protection still wins.

### One mechanism, three previously separate results

| Result | Explained as |
|---|---|
| Experiment 8: 0 of 8 beat buy-and-hold | 13 sleeves ⇒ most of the book in cash ⇒ misses a benchmark that rose 13.53× |
| Three-sleeve combination: 3.94× against 5.42× held | 3 sleeves ⇒ 66.2% cash ⇒ same trade, smaller magnitude |
| Cash-aware allocation: registered negative | Deploying the idle cash restores return but re-concentrates exactly when fewest markets trend |

**The rule's advantage shrinks as the number of independently-exiting
sleeves grows.** Every sleeve added buys drawdown reduction with
compounding — one trade, not three separate findings.

### Testable consequence, and it constrains the queue

If this is right, a **fourth** sleeve should reduce return again and reduce
drawdown again. The buy-and-hold gate now in
`AUTONOMOUS_RESEARCH_LOOP.md` becomes the binding question: a candidate
sleeve must beat holding *its own* market, because otherwise it dilutes the
book toward cash for nothing.

### Limits

- **One window, one crypto cycle.** BNB, SOL and DOGE returning 40-70× is
  a fact about 2018-2025, not a law.
- **Survivorship is uncontrolled.** The 13 names come from a 2026
  eligibility screen, so coins that died are absent and every buy-and-hold
  figure here is flattered.
- **Correlational.** Sleeve count is not the only difference between
  experiments 7 and 8 — the universes differ in liquidity, listing dates
  and volatility too. The cash-share mechanism is measured; the causal
  claim across experiments is inference.

### Reproduce

```
python -m scripts.analyze_symbol_dispersion
```

# Against the simplest alternative: just holding the assets

Diagnostic, 2026-07-26. `scripts/analyze_vs_buy_and_hold.py` over three
already-registered reports. No backtest, no registry row, no
pre-registration — every number below was already sitting in the reports'
own `benchmark_equity` series and had never been read.

This is the comparison the program answers to. It was overdue.

## Each sleeve against its own market, full history

| Sleeve | Window | System | Buy-and-hold | System MDD | Hold MDD |
|---|---|---:|---:|---:|---:|
| crypto | 2018-03 → 2025-07 | **14.26×** | 6.05× | 33.05% | 80.99% |
| taiwan | 2004-04 → 2025-07 | 2.15× | **7.75×** | 30.85% | 55.75% |
| gold | 2005-09 → 2025-07 | 2.44× | **6.99×** | 25.01% | 45.56% |

**The trend rule earns its keep in exactly one of three markets.** In crypto
it more than doubles buy-and-hold's return while cutting the drawdown from
81% to 33%. In Taiwan and gold it destroys most of the return — 2.15×
against 7.75×, 2.44× against 6.99× — and buys drawdown reduction with it.

## Common window, per sleeve

2018-03-06 → 2025-07-01, 2,675 days.

| Book | Sharpe | MDD | Multiple |
|---|---:|---:|---:|
| crypto system | **1.1829** | **33.05%** | **14.26×** |
| crypto buy-and-hold | 0.7081 | 80.99% | 6.05× |
| taiwan system | **0.9816** | **14.83%** | 2.02× |
| taiwan buy-and-hold | 0.8559 | 33.96% | **3.02×** |
| gold system | 0.6432 | **13.10%** | 1.51× |
| gold buy-and-hold | **0.9012** | 22.00% | **2.46×** |

The gold sleeve is the worst case and should be named as such: it loses to
buy-and-hold gold on **both** return and Sharpe. Its only contribution is a
lower drawdown, achieved by being in cash half the time.

## The books

| Book | Sharpe | MDD | Multiple |
|---|---:|---:|---:|
| 1/3 each, systems | **1.4108** | **14.90%** | 3.94× |
| 1/3 each, buy-and-hold | 1.0455 | 40.59% | **5.42×** |
| **crypto system alone** | 1.1829 | 33.05% | **14.26×** |

**The three-sleeve book made less money than holding the same three assets
equally** — 3.94× against 5.42× — while cutting the worst drawdown from
40.59% to 14.90% and raising Sharpe from 1.05 to 1.41.

And the crypto system alone made **3.6× more money than the three-sleeve
book**, at a 33% drawdown rather than 15%.

## What this actually means

Stated without softening: **on this window, the combination is a
risk-preference product, not a return product.** Someone whose goal is the
largest number at the end was best served by the crypto sleeve alone, and
second-best by simply holding the three assets. The combination came third
on money and first on everything else.

## The counter-argument, which is not a small one

The 14.26× is **the most search-contaminated number in this program.** It is
the survivor of N=133 registered trials, and this program's own diagnostics
say that selection channel does not generalize: candidates-PBO 0.7411 across
distinct architectures, and trial 118 — the same family's best-evidenced
candidate — turned negative when run unchanged on another market.

~~The three-sleeve equal-weight book is at the opposite end: **no parameter
was chosen anywhere in it.** Same untuned rule, fixed weights declared in
advance, three markets.~~

**Corrected the same day — see
[`SELECTION_PROVENANCE_CORRECTION_2026-07-26.md`](SELECTION_PROVENANCE_CORRECTION_2026-07-26.md).**
The sentence above is false. The channel windows 10/20/55/110 are
experiment 7's winner and the `mid_channel` exit was selected from an
eight-arm grid by a maximize-Sharpe rule — both on crypto data. What was
genuinely unchosen is narrower: the **transfer** to Taiwan and gold (nothing
re-fit per market) and the **portfolio construction** (equal weights,
monthly, declared before computing). The signal rule carries crypto's search
history into every sleeve.

This makes the table above read *worse*, not better: Taiwan and gold are
out-of-sample tests of a crypto-selected rule, and in both it lost badly to
holding the asset.

So the honest comparison is not "14.26× beats 3.94×". It is:

- 14.26× is the number **most likely to shrink out of sample**, because it is
  the one the search selected.
- 5.42× (just holding) is a real, achievable, zero-search number that carries
  a 40.6% drawdown and an 81% drawdown in its crypto leg.
- 3.94× is the number **least likely to shrink**, because nothing was chosen —
  and it is measurably lower.

Which of those a person should want is a question about drawdown tolerance
and about how much weight they give this program's own overfitting warnings.
The table does not settle it.

## What it does not change

- The three-sleeve result (`SLEEVE3_GOLD_RESULT.md`) stands as measured. Its
  criteria were about combination versus combination, and it passed them.
- Nothing here is a gate verdict, a DSR, or a registry row.
- The October holdout and its fixed nominations are untouched.

## What it does change

The README headline. Publishing a Sharpe improvement without publishing that
the same book **underperformed holding the assets** would have been the exact
kind of selective reporting this repository exists to refuse. Fixed in the
same commit as this document.

## Limits

- One window, one crypto cycle. A window containing a crypto bear market
  from its start would flip several of these rows.
- Benchmarks are the engine's own buy-and-hold series over the same window
  and universe, entered at the same time. They pay entry cost but no ongoing
  cost, which slightly flatters them.
- FX is not modeled; the books are local-currency combinations.

## Reproduce

```
python -m scripts.analyze_vs_buy_and_hold
```

---

## Addendum 2026-07-27 — against the strongest naive benchmark there is

`REGISTRY_VS_BENCHMARK_2026-07-26.md` recorded that experiment 8 (the
13-symbol book) beat buy-and-hold in 0 of 8 configurations. A ratio cannot
say whether that is the system collapsing or the benchmark being enormous.
Measured directly:

| Book, 2018-03 → 2025-07 | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| **Trial 88 system (BTC/ETH)** | **1.1829** | **33.05%** | **14.26×** |
| BTC/ETH buy-and-hold | 0.7081 | 80.99% | 6.05× |
| Experiment 8 best system (13 coins) | 0.9728 | 51.54% | 9.39× |
| **13-coin equal-weight buy-and-hold** | 0.8469 | **86.22%** | **13.53×** |

**Experiment 8 did not collapse.** Its median arm still returned 7.33× and
its best 9.39×. It lost on ratio because the 13-coin benchmark returned
13.53× — 2.2× what the BTC/ETH benchmark returned. Trend-following on
altcoins made real money and still could not keep up with holding them.

### The comparison that matters most, and it is uncomfortable

**Trial 88 returned 14.26×. Buying thirteen coins in March 2018 and never
looking at them again returned 13.53×.**

A 5.4% margin, over 7.3 years, after 133 registered trials.

On return alone, this entire program bought almost nothing over the most
naive possible crypto strategy.

### What it did buy, and it is not nothing

| | Trial 88 | 13-coin hold |
|---|---:|---:|
| Worst drawdown | **33.05%** | **86.22%** |
| Sharpe | 1.1829 | 0.8469 |

An 86% drawdown is the difference between a position a person holds and one
they capitulate out of at the bottom. Almost nobody holds through 86%. The
system's product is not return — **it is the drawdown that makes the return
reachable.**

That is the same conclusion the three-sleeve combination reached, now
measured against the strongest naive alternative rather than against other
systems.

### Mechanism note

Experiment 8 traded **1,516 times against experiment 7's 396** — roughly
four times the trades, spread over 13 names — while running *lower*
annualized turnover (6.38 against 8.55) because each name holds a
thirteenth of the book. So the shortfall is not primarily cost drag. It is
that thirteen independently-exiting sleeves are rarely all invested at
once, and buy-and-hold captures every altcoin's full run while the trend
rule sits out parts of each.

That is the same flat-sleeve mechanism the combination results depend on —
here it costs money instead of saving it, because the benchmark went
straight up.

### Limits

- One window, one crypto cycle, and a 13-coin universe selected by the
  project's own eligibility screen in 2026 — **survivorship is not
  controlled**. Coins that died before the screen ran are absent from the
  benchmark, which flatters buy-and-hold's 13.53×.
- Benchmarks pay entry cost but no ongoing cost.

---

## Addendum 2026-07-28 (iteration 28) — this document contradicts itself, and the standing answer inherited the wrong half

### The contradiction

Two statements in this file describe the same strategy against different
benchmarks, and only one of them is a like-for-like comparison:

| Where | Comparison | System | Benchmark | System MDD | Benchmark MDD |
|---|---|---:|---:|---:|---:|
| line 14, line 143 | **same universe** — trial 88 vs BTC/ETH buy-and-hold | 14.26x | **6.05x** | 33.05% | **80.99%** |
| line 145, line 166 | **cross universe** — trial 88 vs 13-coin equal-weight | 14.26x | **13.53x** | 33.05% | **86.22%** |

Line 19 of this document states the first correctly: "it more than
doubles buy-and-hold's return while cutting the drawdown from 81% to
33%." Line 171 states the second as a mechanism claim: "the system's
product is not return."

**Trial 88 traded BTC and ETH only.** Its market is the 6.05x row. The
13-coin book is experiment 8's universe, where the best arm returned
9.39x against that same 13.53x (`REGISTRY_VS_BENCHMARK_2026-07-26.md`).
Pairing experiment 7's result with experiment 8's benchmark is the
identical universe-pooling error this program caught and retracted on
2026-07-26, when "8 of 16 beat buy-and-hold, a coin flip" turned out to
be 8/8 and 0/8 once the experiment number was carried in the grouping key.

### What is actually true, split by the question being asked

**As a mechanism claim — does the timing rule add value?** It must be
same-universe, and the answer is that the rule bought **both**:

- return **14.26x against 6.05x** (+136%), and
- drawdown **33.05% against 80.99%**.

The clause "the search bought drawdown, **not return**" is false in this
frame. It is also unnecessary: the exposure-matched twin measurement
(`TIMING_VALUE_2026-07-27.md`) independently scores this sleeve at 4.70x
its passive twin, which is the cleaner version of the same finding.

**As an opportunity comparison — after 133 trials, is this better than
the dumbest alternative the operator could have executed?** The
cross-universe figure is legitimate and is the more decision-relevant
one for someone whose goal is money: 14.26x against 13.53x, a **5.4%
margin**, at 33.05% drawdown against 86.22%. Two caveats already recorded
stay attached: the 13-coin universe came from a 2026 eligibility screen so
**survivorship is uncontrolled** and 13.53x is flattered, and a 5.4%
margin is not a result 133 trials can claim credit for.

Even in this frame "not return" overstates it — the correct phrasing is
**mostly drawdown, plus a slim return margin**.

### What changes

- Nothing measured. Every number above is as recorded; none is retracted.
- The standing answer in `AUTONOMOUS_RESEARCH_LOOP.md` carried the
  cross-universe sentence and is corrected the same day.
- Any future document quoting "14.26x against 13.53x" must say which
  question it is answering, and must not use it to support a claim about
  what the timing rule does.

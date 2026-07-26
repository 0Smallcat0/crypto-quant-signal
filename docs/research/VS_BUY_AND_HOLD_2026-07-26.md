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

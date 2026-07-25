# Sleeve 3 (gold) — result: PASS on all four pre-declared criteria

Executed 2026-07-26 · Pre-registration:
`D:/TW-Stock-Trading/docs/research/SLEEVE3_GOLD_PREREGISTRATION.md`
(unmodified) · Trial: TW registry #24, clean tree `5359ef4`.

The same untuned mid-channel Donchian rule (10/20/55/110), unchanged from
crypto trial 88 and Taiwan trial 23, was run once on GLD. No grid, no arms,
no parameter chosen on gold data.

## The sleeve on its own

Window 2005-09-07 → 2025-07-02, 4,986 sessions (the holdout lock trims the
last 365 days; the 2004-11-18 data start is consumed by feature warmup).

| Book | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| Gold sleeve (trial 24) | 0.6012 | 25.01% | 2.44× |
| GLD buy-and-hold, same window | 0.7717 | 45.56% | 6.96× |

**The rule loses to simply holding gold.** It halves the drawdown and gives
up nearly two-thirds of the return, and its Sharpe is *lower* than
buy-and-hold's. Read alone, this sleeve is a bad way to own gold.

That is stated first because it is the number most likely to be quietly
skipped. The case for including it is not that it is a good standalone
system — it is not — but what it does to the book, below.

## The three-sleeve combination

Common window 2018-03-06 → 2025-07-01, 2,675 days, equal weights (1/3 each)
rebalanced monthly. The two-sleeve row is **recomputed on this same
window**, not quoted from the earlier document.

| Book | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| Crypto sleeve (trial 88) | 1.1829 | 33.05% | 14.26× |
| Taiwan sleeve (trial 23) | 0.9816 | 14.83% | 2.02× |
| Gold sleeve (trial 24) | 0.6432 | 13.10% | 1.51× |
| 50/50 crypto+Taiwan | 1.3437 | 19.73% | 6.00× |
| **1/3 each, three sleeves** | **1.4108** | **14.90%** | 3.94× |

Pairwise daily correlations on the common window:

| Pair | Correlation |
|---|---:|
| gold vs crypto | +0.0767 |
| gold vs Taiwan | +0.0331 |
| crypto vs Taiwan | −0.0041 |

Pre-declared criteria:

1. **Gold sleeve individually positive** — PASS (0.6012 own window, 0.6432
   common window).
2. **Independent of both, |corr| < 0.30** — PASS (+0.0767, +0.0331).
3. **Three-sleeve Sharpe > two-sleeve Sharpe, same window** — PASS
   (1.4108 > 1.3437).
4. **Three-sleeve drawdown < two-sleeve drawdown, same window** — PASS
   (14.90% < 19.73%).

**VERDICT: PASS.**

The new script reproduces the published two-sleeve numbers exactly
(1.3437 / 19.73% / 6.00×) on this window, which is the check that it
computes the same thing the earlier one did.

## What it costs

**Terminal wealth falls again: 14.26× → 6.00× → 3.94×.** Every sleeve added
buys a smoother path with money. The gold sleeve returns 1.51× over these
seven years — barely above holding cash — so putting a third of the book in
it is expensive.

The trade being made, stated plainly:

| Book | Sharpe | Worst drawdown | Multiple over 7.3 years |
|---|---:|---:|---:|
| Crypto alone | 1.1829 | 33.05% | 14.26× |
| Three sleeves | 1.4108 | 14.90% | 3.94× |

An institution would lever the three-sleeve book back up to crypto's
volatility and keep both the return and the smoothness. **This product
cannot lever** — spot, long-only, unlevered, by permanent product law — so
the smoother path is paid for in absolute return, and no amount of Sharpe
improvement changes that.

Whether 3.94× at a 14.9% worst drawdown beats 14.26× at a 33.1% worst
drawdown is a decision about what a person can actually hold through, not a
statistical question.

## The stress test, including the part that does not help the claim

The two-sleeve result survived its sharpest objection: correlation went
*more negative* when crypto fell hardest. **Gold does not do that.**

| Condition | n | corr(gold, crypto) | crypto mean | gold mean | Taiwan mean |
|---|---:|---:|---:|---:|---:|
| Crypto worst 5% of days | 133 | **+0.1047** | −4.60% | −0.06% | +0.10% |
| Crypto worst 10% of days | 267 | +0.0503 | −3.22% | −0.07% | +0.03% |

Gold's correlation to crypto **rises** in crypto's worst days (+0.0767
baseline to +0.1047 in the tail), the opposite of the Taiwan sleeve's
behaviour. The honest reading: gold is not a hedge against crypto and is not
becoming one under stress. What it does is sit at roughly zero (−0.06% mean)
while crypto loses 4.60%, which is the flat-sleeve mechanism the
pre-registration required — not an offsetting move.

Sub-period drawdowns, two-sleeve vs three-sleeve on identical windows:

| Window | n | 2-sleeve MDD | 3-sleeve MDD | 3-sleeve Sharpe |
|---|---:|---:|---:|---:|
| 2020 covid crash | 61 | 11.78% | **9.83%** | −0.02 |
| 2022 bear year | 365 | 12.64% | **9.15%** | −0.96 |
| 2018-2019 | 666 | 16.89% | **11.90%** | +1.00 |
| 2023-2025H1 | 913 | 11.65% | **7.10%** | +1.78 |

The third sleeve lowers drawdown in **every** regime tested, including both
losing ones. The covid window is the most striking: the two-sleeve book's
Sharpe there was −3.11 in the earlier addendum, and the three-sleeve book's
is −0.02 — gold was close to flat while crypto and Taiwan both fell.

**What still hurts:** 2022 is still −0.96. A long-only trend book has no
positive-return state in a sustained decline; it can only be in cash sooner
and in fewer places at once. Diversification keeps cutting the pain and
still does not remove it. The 61-day covid window is too short to carry
weight alone.

## Deviations from the pre-registration, all recorded

1. **`min_notional` 0 → 0.01 USD.** The pre-registration declared "no lot
   minimum to clear"; the paper broker refuses a non-positive floor. 0.01 is
   the same statement in a form it accepts — one share of GLD has never been
   worth under $40, so it cannot reject a trade. Changed and committed
   (`5359ef4`) **before any result was seen**.
2. **The first invocation crashed after the backtest had already run and
   registered** (`BacktestReport.as_dict` does not exist — a defect in the
   printing block, not the run). Trial 24 was therefore **not re-run**; that
   would have duplicated the registry row. The numbers here are read from
   the report the crashed invocation had already written.

Brake check, required by the pre-registration before the result could be
reported: the report's `risk_events` is **empty**, so no disaster brake,
drawdown halt, or daily-loss pause fired. The measured result is the raw
rule.

## A registry defect found while checking this run, and fixed

Trial 24's registry row initially read `strategy_id: daily_trend_ensemble`
with `lookbacks: 20,65,150,200` — the SMA ensemble's contract, not
Donchian's. Investigation found the parameters block was a **hardcoded
constant** in `src/backtest/runner.py`, stamped onto every row regardless of
what ran.

The run itself was correct: `engine.py` dispatches on
`parameters.strategy_name == "donchian_breakout_ensemble"`, which this run
passed. Only the label was wrong.

**Trial 23 — the Taiwan sleeve already used in the published two-sleeve
result — carries the same wrong label.** The registry is append-only, so
both rows stay wrong and this document is the correction. Every row written
after commit `63e2996` records its own configuration, and a test now fails
if a Donchian run stamps SMA lookbacks.

This matters beyond bookkeeping: the registry is the artifact that makes N
auditable, and N is what every DSR in this program deflates against.

## Limits, unchanged or made worse by this sleeve

- **FX is still not modeled**, now across three currencies (USDT, TWD, USD).
  These are local-currency combinations, not an achievable portfolio return.
  A third currency makes this worse, not better. It is not fixed here.
- **No DSR, no gate verdict.** This is portfolio-level analysis of
  registered trials; it registers nothing and has no deflation statistic.
  Gate 3 remains failed in the crypto program (candidates-PBO 0.6518
  against 0.05).
- **The common window is bounded at 7.3 years** by the crypto sleeve's 2018
  start, and it contains exactly one crypto bull cycle.
- **Three sleeves is still not a diversified book.** It is one more than two.
- **Correlations are estimates from one window.** +0.0767 is not a promise.
- **No forward evidence exists for this combination.** Nothing about a
  backtested three-sleeve book has been observed out of sample.
- **Never nominatable.** Neither trial 24 nor this combination may be
  nominated for the October holdout; nominations remain fixed at N1 = live
  `daily_trend_ensemble`, N2 = trial 7.

## What this does and does not establish

It establishes that adding a third independent trend sleeve, with no
parameter chosen anywhere, improved risk-adjusted return and cut drawdown in
every regime tested — and that the improvement is arithmetic from
near-zero correlations, not a fit.

It does not establish an edge. It does not pass the six gates. It does not
change the October holdout. And it costs 34% of the two-sleeve book's
terminal wealth to buy a 24% smaller worst drawdown.

## Next step, and it is the only one that adds information

Forward tracking for the gold sleeve, matching the other two
(`CryptoShadowTrial88` daily, `TwShadow0050` weekly). Backtests cannot make
this more credible; only unseen data can.

## Reproduce

```
cd D:/TW-Stock-Trading && python -m scripts.ingest_us_etf_ohlcv
cd D:/Crypto-Trading  && python -m scripts.analyze_sleeve_combination
```

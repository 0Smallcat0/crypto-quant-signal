# Cross-market combination — result: PASS, and it is the first result here that does not rest on a parameter choice

Executed: 2026-07-26 · Pre-registration:
`docs/research/CROSSMARKET_COMBINATION_PREREGISTRATION.md` (unmodified)
Window: 2018-03-06 → 2025-07-01, 2,675 calendar days (1,779 Taiwan
trading days). No backtest run, no registry row created.

## Result

| Book | Sharpe | Max drawdown | Multiple |
|---|---:|---:|---:|
| Crypto sleeve (trial 88) | 1.1829 | 33.05% | 14.26× |
| Taiwan sleeve (trial 23) | 0.9816 | 14.83% | 2.02× |
| **50/50 combination** | **1.3437** | **19.73%** | 6.00× |

**Daily return correlation between the two sleeves: −0.0041.**
Effectively independent — the monthly estimate (0.2921) overstated the
linkage.

Pre-declared criteria:

1. Combined Sharpe strictly greater than both sleeves — **PASS**
   (1.3437 > 1.1829 and > 0.9816).
2. Combined max drawdown strictly lower than the crypto sleeve's —
   **PASS** (19.73% < 33.05%).
3. Both sleeves individually positive — **PASS** (1.1829, 0.9816).

**VERDICT: PASS.**

## Why this one is different from the 140 that came before

Every previous improvement in this program came from choosing something:
a lookback, a target, a gate, an exit multiple. Two independent
measurements say that channel does not generalize — PBO 0.7411 across
distinct architectures, and the cross-market refutation of trial 118's
2×ATR exit.

This result chooses nothing:

- **Same rule in both markets.** Mid-channel Donchian 10/20/55/110,
  identical parameters, no per-market fitting. The Taiwan sleeve is the
  configuration that was run there as a declared context arm under a
  pre-registration that forbade tuning.
- **Fixed weights, declared in advance.** 50/50, monthly rebalanced. The
  30/70 blend that scored higher in exploration was excluded by the
  pre-registration precisely because it was seen first.
- **The improvement is mechanism, not fit.** Two ~independent return
  streams of similar quality combine to a higher Sharpe by arithmetic.
  Nothing was searched for.

That is the structural difference. It does not make the result true; it
makes it the first result here that the project's own overfitting
diagnostics do not directly indict.

## What it costs — stated as plainly as what it earns

**Terminal wealth falls from 14.26× to 6.00×.** Halving the crypto sleeve
halves its compounding, and the Taiwan sleeve (2.02× over the same seven
years) cannot make that up. This is the same trade-off experiment 2
recorded: better risk-adjusted return, materially less money. An
institution would lever the combination back up to the original
volatility and keep both; **this product cannot lever** (spot, long-only,
by permanent product law), so the smoother path is paid for in absolute
return.

Whether 6.00× at a 19.7% worst drawdown beats 14.26× at a 33.05% worst
drawdown is a decision about what a person can actually hold, not a
statistical question. It should be made explicitly rather than implied by
a Sharpe ranking.

## Limits, all declared before the result

- **FX is not modeled.** The Taiwan sleeve is TWD, the crypto sleeve
  USDT. A real combined book carries currency exposure this computation
  ignores, so these numbers are a local-currency combination and not an
  achievable portfolio return.
- **The window flatters the Taiwan sleeve.** It scores 0.9816 here and
  only 0.4262 across its full 21 years, because 2018-2025 was a strong
  stretch for 0050. A longer common window would show a weaker
  combination. This is a claim about this window.
- **No DSR, no gate verdict.** This is portfolio-level analysis of two
  already-registered trials; it registers nothing and has no deflation
  statistic of its own. It inherits the crypto program's N=133 search
  history, which is not diluted by combining.
- **Correlation is an estimate.** −0.0041 over one window is not a
  guarantee of independence in the next one; crypto and equities have
  correlated sharply in past liquidity events.
- **Two sleeves is not diversification.** It is the minimum viable
  version of it.

## What this does NOT establish

It is not a certified edge. Gate 3 remains failed in the crypto program
(candidates-PBO 0.6518 against 0.05), no forward out-of-sample evidence
exists for the combination, and nothing here changes the October holdout
or its fixed nominations.

## Next step, and it is the only one that adds information

Forward tracking. The crypto sleeve already records daily
(`data/runtime/shadow_trial88.jsonl`, since 2026-07-24). The Taiwan
sleeve needs the same: a daily 0050 signal record in the TW repository,
after which the combination can be tracked as a book rather than
reconstructed from history. Backtests cannot make this result more
credible; only unseen data can.

## Provenance

Crypto sleeve: trial 88, registered 2026-07-22 on clean tree `6c99598`.
Taiwan sleeve: trial 23, registered 2026-07-26 on clean tree `892982c`
under `CROSSMARKET_DONCHIAN_PREREGISTRATION.md`, where it was declared
context for a test whose primary arm failed. Combination computed by
`scripts/analyze_crossmarket_combination.py` from both reports' equity
curves.

---

## Addendum 2026-07-26 — the independence survives stress, and the reason matters

The sharpest objection to this result is that crypto and equities correlate
sharply in liquidity events, so the diversification would vanish exactly
when it is needed and the 19.73% drawdown would be understated. Measured on
the same series, no new trials:

**Conditional correlation (crypto sleeve's own worst days)**

| Condition | n | Correlation | Crypto mean | Taiwan mean |
|---|---:|---:|---:|---:|
| Crypto worst 5% of days | 133 | **−0.1818** | −4.60% | **+0.10%** |
| Crypto worst 10% of days | 267 | −0.1741 | −3.22% | +0.03% |
| Crypto best 10% of days | 267 | +0.0298 | +3.85% | +0.05% |

Correlation goes **more negative** precisely as the crypto sleeve falls
hardest, and the Taiwan sleeve's average return on crypto's worst days is
slightly positive.

**Sub-period stability**

| Window | n | Correlation | Crypto MDD | TW MDD | Combo MDD | Combo Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| 2020 covid crash | 61 | −0.1882 | 19.9% | 2.1% | 11.9% | −3.11 |
| 2022 bear year | 365 | −0.0111 | 22.6% | 8.0% | 12.6% | −1.04 |
| 2018-2019 | 666 | −0.0536 | 29.7% | 7.2% | 16.9% | +0.94 |
| 2023-2025H1 | 913 | +0.0005 | 24.2% | 14.8% | 11.7% | +1.50 |

Across four distinct regimes the correlation never rises above +0.0005 and
the combination's drawdown is roughly half the crypto sleeve's every time.
This is not a single-window artefact.

### Name the mechanism correctly

The Taiwan sleeve is **not a hedge against crypto**. It is a trend system
that is frequently in cash — its exposure on the day this was written was
0.25 of one symbol — and *cash is uncorrelated with everything*. The
diversification benefit comes substantially from one sleeve being flat while
the other falls, not from Taiwan equities moving against crypto. Any future
sleeve added on this reasoning must be a system that also goes to cash, and
the claim being made is about **trend systems in independent markets**, not
about asset-class correlation.

### What still hurts

Both sleeves lose together in fast bear markets: combined Sharpe is −3.11
through the covid crash and −1.04 across 2022. Diversification halves the
pain; it does not remove it. A long-only trend book has no positive-return
state in a sharp decline — it can only be in cash sooner. The 61-day covid
window is also too short to carry weight on its own.

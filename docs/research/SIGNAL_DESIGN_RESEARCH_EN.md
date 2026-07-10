# Signal Design Research — English Summary

Status: condensed English edition of [`SIGNAL_DESIGN_RESEARCH.md`](SIGNAL_DESIGN_RESEARCH.md) (2026-07-02).
The Chinese original is the document of record; this summary preserves its
conclusions, evidence labels, and confidence levels without adding new claims.

Method: multi-agent deep-research workflow — fan-out search → source retrieval
→ **three-vote adversarial verification** (each surviving claim withstood three
independent refutation attempts; ≥2 refute votes kills a claim) → synthesis.
Result: **19 claims verified, 11 rejected, 0 infrastructure failures.**
Verifiers checked numbers against original PDFs where possible.

---

## 1. Research question

For a retail-scale, crypto **spot, long-only, manually executed** signal system
(public Binance data only, user places orders after a notification, no 24/7
monitoring, 25–30 bps round-trip cost assumption): which design decisions have
credible empirical support?

## 2. Executive summary

Evidence supports a credible **after-cost edge at the DAILY frequency only**:
long-only time-series trend/momentum signals on large-cap coins (BTC, ETH)
beat buy-and-hold on a risk-adjusted basis in 2014–2023 samples under
10–50 bps per-trade costs (after-cost Sharpe 1.25–1.84 vs ~0.85–1.06 B&H;
max drawdown reduced from 83–93% to 52–62%), confirmed across multiple
independent sources that survived adversarial verification.

By contrast, **no sub-hourly after-cost profitability evidence survived**
verification; small-cap short-term signals are contaminated by pump-and-dump
(+25% in seconds, reversed within an hour), and equal-weighted broad-altcoin
backtests are inflated ~62%/year by survivorship bias.

Three things must hold before real money — and none can be assumed:

1. The edge (samples mostly end 2023) has not decayed since — requires a
   non-iterated post-2023 out-of-sample test on local data.
2. The 25–30 bps cost assumption survives measured paper trading.
3. The strategy passes a strict validation gate: full trial count N recorded,
   CSCV PBO ≤ 5%, DSR ≥ 0.95, ≥1,000 daily observations, single-shot
   walk-forward.

Even then: expect **50–60% drawdowns** and negative absolute returns in bear
markets (in a verified 2022 case study, the *least overfit* strategy still
lost ~35% in two months).

## 3. Key verified findings

| # | Finding | Confidence / votes |
|---|---------|--------------------|
| 1 | Daily MA trend rules on BTC/ETH beat B&H pre-tax on all risk-adjusted metrics (BTC Sharpe 1.06→1.89; ETH 1.25→2.64; MDD 83→58% / 93→53%) | high, 3-0 (Monash CFS, verified against Exhibit 2) |
| 2 | Same rules still win after 0.1–0.5% per-trade costs (BTC Mom65: 1.84/1.78/1.69 vs B&H 1.04) | high, 3-0 (verified against Exhibits 3–4) |
| 3 | Market-level long-only TSM beats the market 8 of 10 years after 15 bps costs (Sharpe 1.51 vs 0.85; authors admit in-sample look-ahead in parameter choice) | high, 3-0 (Han, Kang & Ryu) |
| 4 | Short side loses even pre-tax → **long-only** | medium, 2-1 |
| 5 | Cross-sectional rotation is weak and fragile (5 of 21 portfolios liquidated in-sample) → no relative-strength coin picking | medium, 2-1 |
| 6 | All surviving after-cost evidence is at the **daily** frequency; nothing sub-hourly survived | high, cross-source |
| 7 | Survivorship bias inflates equal-weighted broad-altcoin backtests by ~62.19%/year | high, 3-0 (Ammann & Stöckl) |
| 8 | Pump-and-dump is routine at exchange level; small-cap breakout signals can be manipulation artifacts | high, 3-0 (Li, Shin & Wang) |
| 9 | A backtest that does not disclose trial count N is "worthless"; iterated out-of-sample is not out-of-sample | high, 3-0 (Bailey & López de Prado 2014; Arnott, Harvey & Markowitz 2019) |
| 10 | A single holdout / walk-forward is insufficient; ~20 uses of a 95%-confidence holdout make false positives expected | high, 3-0 |
| 11 | The two computable gate statistics: **PBO via CSCV** (reject > 0.05) and **DSR** (require ≥ 0.95) | high, 3-0 |
| 12 | Warning case: optimizing 4 parameters on a pure random walk yields in-sample Sharpe 1.27; CSCV correctly diagnoses PBO = 55%. MA-cross trend systems are named as a typical false-positive generator | medium |
| 13 | Gate limits: overfitting probability ranks strategies but does **not** guarantee absolute profit (least-overfit agent still −35% in 2022 crashes) | high, 3-0 |

## 4. Design decisions (as implemented)

1. **Timeframe: daily.** Signal once per day after the UTC close; hours of
   execution latency are second-order at this frequency. No 15m/1h/4h signals.
2. **Strategy class: long-only time-series trend following.** Trend up → hold;
   trend down → cash (USDT). No shorting, no cross-sectional rotation, no
   dip-buying.
3. **Signal construction: multi-lookback SMA ensemble.** Four sub-signals per
   asset (close above 20/65/150/200-day SMA), target exposure = their average
   → a {0, 25, 50, 75, 100}% ladder. The ensemble spreads single-parameter
   selection risk and keeps trial count N minimal; fixed 25% steps keep each
   notification a fixed, manually executable order size.
4. **Universe: BTC + ETH core** (half risk budget each); SOL only as a
   candidate that must independently pass the gate. Broad altcoin universes
   excluded (survivorship bias, manipulation).
5. **Exit: symmetric signal break → cash.** The only exit with after-cost
   empirical support. No trailing/ATR/time stops in v1 (no verified
   comparative evidence; they add parameters and trials). A separate
   non-strategy disaster brake exists as risk control.
6. **Regime filter: none in v1.** The long-only trend rule is itself a regime
   gate. A BTC>200-day-SMA filter for ETH/SOL is a pre-registered v1.1
   controlled experiment, counted toward N.
7. **Validation gate: six gates, all must pass** — trial registry from the
   first backtest; ≥1,000 daily observations across a full bull/bear cycle;
   CSCV (S=16, 12,870 splits) PBO ≤ 0.05; DSR ≥ 0.95; a single-use locked
   holdout (~12 most recent months); ≥3 months of paper trading with measured
   real costs within 1.5× the assumption.

Each decision in the original document carries explicit *overturn conditions* —
the evidence that would reverse it.

## 5. Realistic expectations (verified numbers, inferences labeled)

- **After-cost Sharpe**: verified full-sample range 1.25–1.84, but these embed
  in-sample parameter selection; a deflated forward-looking expectation is
  **~0.6–1.2 (inference)**. Positioning: modestly better risk-adjusted than
  B&H with much lower drawdown — not a profit machine.
- **Max drawdown**: verified historical 53–62% (vs 83–93% B&H). **50–60%
  drawdowns must still be expected.**
- **Signal frequency**: ~4–15 entries/exits per asset per year, holding weeks
  to months (inference from the ensemble design).
- **Post-2023 persistence**: supported by exactly one commercial working
  paper; treated as **unproven** until the project's own single-shot holdout
  and paper period answer it.

## 6. What was rejected

Eleven claims failed adversarial verification and were **not** used, including:
short lookbacks dominating long ones; "manipulators avoid BTC/ETH"; a 10% PBO
threshold as the practical gate (5% adopted instead); "trends persist 30–40
days"; all three out-of-sample claims of SSRN 4955617; and a "survivorship-
bias-free" data claim for a top-20 universe. The full rejection table with
votes is in the Chinese original, §7.

## 7. Open questions the project must answer itself

1. Does the BTC/ETH daily long-only trend edge still exist after 2023/8?
   (Answered only by the project's own non-iterated OOS test + holdout.)
2. What are the actual execution costs? (Measured during paper trading.)
3. What does manual execution latency actually cost? (Simulated 5min/1h/8h
   delayed fills.)
4. Marginal value of exit variants and regime filters — as pre-registered,
   N-counted controlled experiments inside the gate.

## 8. Primary sources

Monash CFS (Le & Ruthbah 2023) · Han, Kang & Ryu (SSRN 4675565) · Bailey &
López de Prado, *The Deflated Sharpe Ratio* (JPM 2014) · Bailey, Borwein,
López de Prado & Zhu, *The Probability of Backtest Overfitting* (JoCF 2015) ·
Ammann & Stöckl (SSRN 4287573) · Li, Shin & Wang (SSRN 3267041) · Zarattini,
Pagani & Barbon (SSRN 5209907) · Guan & An (arXiv 2209.05559) · Palomar,
*Portfolio Optimization* §8.3. Full URLs in the Chinese original, §8.

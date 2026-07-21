# Goal P experiment 5 — result: gate closes on the drawdown target but the winner still misses both bars

Executed: 2026-07-21 · Trials: **54-69** (registry N: 53 → 69)
Pre-registration: `docs/research/GOALP_EXPERIMENT5_PREREGISTRATION.md`
(unmodified; second same-sitting override recorded there)
Gate report: `docs/reports/research/gate_report_2026-07-21.json`
(regenerated at N=69, 2676 obs)

## Family table (16 configs; cs base fixed at K=2/180d/monthly/filter-on)

| Trial | SMA | Basis | Hyst | Gate cadence | Sharpe | MDD | Turnover | Final equity |
|---:|---:|---|---:|---|---:|---:|---:|---:|
| 54 | 100 | btc | 0 | daily | 1.0568 | 58.91% | 10.01 | 26,913 |
| 55 | 100 | btc | 0 | monthly | 0.5968 | 69.11% | 3.73 | 3,564 |
| **56** | **100** | **btc** | **2%** | **daily** | **1.1651** | **58.47%** | **4.98** | **44,397** |
| 57 | 100 | btc | 2% | monthly | 0.6697 | 69.11% | 3.13 | 4,845 |
| 58 | 100 | per_symbol | 0 | daily | 0.9099 | 61.44% | 11.73 | 15,629 |
| 59 | 100 | per_symbol | 0 | monthly | 0.7015 | 66.00% | 3.72 | 5,917 |
| 60 | 100 | per_symbol | 2% | daily | 0.8683 | 62.05% | 7.64 | 13,005 |
| 61 | 100 | per_symbol | 2% | monthly | 0.7155 | 63.75% | 3.57 | 6,308 |
| 62 | 200 | btc | 0 | daily | 0.9783 | **51.83%** | 6.66 | 18,861 |
| 63 | 200 | btc | 0 | monthly | 0.6034 | 61.75% | 3.09 | 3,750 |
| 64 | 200 | btc | 2% | daily | 0.9707 | **51.83%** | 5.10 | 18,233 |
| 65 | 200 | btc | 2% | monthly | 0.5120 | 65.33% | 2.94 | 2,605 |
| 66 | 200 | per_symbol | 0 | daily | 0.6998 | 73.37% | 6.92 | 5,613 |
| 67 | 200 | per_symbol | 0 | monthly | 0.7616 | 74.53% | 3.23 | 8,090 |
| 68 | 200 | per_symbol | 2% | daily | 0.6999 | 73.37% | 5.62 | 5,616 |
| 69 | 200 | per_symbol | 2% | monthly | 0.7598 | 73.47% | 3.20 | 7,997 |

Winner by the pre-declared rule (highest Sharpe): **trial 56 — SMA 100,
BTC basis, 2% hysteresis, daily gate**.

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR ≥ 0.95: FAIL — 0.911490** at N=69 deflation.
2. **Winner MDD ≤ 51.93%: FAIL — 58.47%**, missed by 6.54pp.
3. Winner turnover ≤ 53.1: PASS — 4.98.

**The family is a registered negative under its own pre-registration** —
the project's fifth. Stop condition remains unmet (candidates-PBO 0.8079,
all-columns 0.4971).

## Why this negative moves the search forward anyway

- **The feasible region is no longer empty.** Trials 62/64 (SMA 200, BTC
  basis, daily gate) put a cs configuration's MDD INSIDE the statutory bar
  for the first time in the lineage: **51.83% ≤ 51.93%**. Every earlier
  cs arm, overlaid or not, sat 3-23pp outside. Directional gating does
  what vol targeting could not: it removes bear-market exposure without
  amputating the high-vol bull periods the signal earns in.
- **The winner-gap trend across experiments 3 → 4 → 5: 75.08% → 63.76% →
  58.47%**, against a fixed 51.93% bar. The gate family's own spread shows
  the dial: SMA 100 keeps more Sharpe (1.17) at 58% MDD; SMA 200 buys the
  MDD bar at 0.98 Sharpe (DSR 0.794 — dead at N=69). One family, both
  bars touched — never both at once.
- **Cadence is decisive, again, in the direction practitioners predict:**
  monthly-frozen gates are the family's disaster arms (Sharpe 0.51-0.76;
  a gate that cannot exit mid-month holds through crashes AND sells the
  recovery). Daily gate evaluation with monthly selection is the only
  workable shape. The 2% hysteresis band on the winner halves turnover
  (10.0 → 4.98) and RAISES Sharpe (1.057 → 1.165) — whipsaw suppression
  is free alpha on this tape.
- **BTC as the regime proxy beats per-symbol gating** everywhere at
  SMA 200 (per-symbol arms: 73-75% MDD — idiosyncratic SMA states let
  laggards stay long through the market top).

## Also recorded

- **Trial 29 at N=69: DSR 0.980166** — third consecutive report where its
  deflated score RISES as near-duplicate columns compress cross-trial
  variance (3.64e-4 → 2.64e-4 → 2.26e-4). Mechanics, not qualification;
  it remains the only DSR-passing trial in the registry and remains the
  winner of a failed family.
- Trial 56's final equity 44,397 is the registry's new terminal-wealth
  high (4.4× initial), displacing trial 47's 25,790. Same caveat as
  always: a 58% drawdown en route means the follower likely wasn't there
  to collect it.
- Candidates-PBO climbed to 0.8079 with sixteen more distinct columns —
  in-family winner-picking stays firmly overfit, which is exactly why the
  October nominations are already fixed and none of today's trials can
  touch them.

## What happens next (sequential research, not a rescue)

The two frontier points — (Sharpe 1.165, MDD 58.5%) at SMA 100 and
(Sharpe 0.978, MDD 51.8%) at SMA 200 — bracket the statutory corner
(0.95-equivalent Sharpe ≈ 1.25+ at this N, MDD ≤ 51.93%). Closing that
corner needs either a better signal under the gate (not a better gate:
both bars have now been touched by gate arms) or acceptance that this
lineage's ceiling is below the bar. Candidate hypotheses for the NEXT
pre-registration (a later sitting unless the operator overrides again):
the multi-horizon trend factor already logged in RESEARCH_LOG (Cambridge
JFQA 2024) under the proven SMA-200/BTC/daily gate, or K/lookback
variation under that gate. The holdout stays sealed; October is
unaffected.

## Provenance

All 16 trials ran on clean tree `894056f` (commit-first rule). Registry
rows carry full cs_* + gate parameters machine-readable. Registry, return
series, the N=69 report, and this document are committed together.

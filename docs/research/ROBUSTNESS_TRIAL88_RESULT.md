# Robustness battery on trial 88 — result: it does not break

Executed: 2026-07-25 · Trials: **102-109** (registry N: 101 → 109)
Pre-registration: `docs/research/ROBUSTNESS_TRIAL88_PREREGISTRATION.md`
(unmodified). Subject: trial 88 — Donchian 10/20/55/110, mid_channel
exit, no gate, BTC/ETH. Every arm below is bound as never-nominatable.

## Battery A — parameter neighbourhood (6 runs)

| Arm | Windows | Sharpe | MDD | Turnover | Equity (1000 start) |
|---|---|---:|---:|---:|---:|
| A1 −20% | 8+16+44+88 | 1.1542 | 36.61% | 17.45 | 13,451 |
| A2 +20% | 12+24+66+132 | 1.1692 | 30.77% | 11.49 | 13,973 |
| A3 −30% | 7+14+39+77 | 1.1710 | 36.48% | 19.22 | 13,672 |
| A4 +30% | 13+26+72+143 | 1.1234 | 33.41% | 10.68 | 12,481 |
| A5 jitter | 11+18+60+100 | 1.2107 | 29.69% | 13.64 | 15,523 |
| A6 jitter | 9+22+50+120 | 1.1430 | 37.66% | 14.24 | 12,715 |
| — | **trial 88** | **1.1821** | **33.05%** | 13.92 | 14,231 |

**Stability verdict — all three criteria PASS:**

1. All six arms Sharpe ≥ 1.00: minimum is **1.1234** (A4). PASS.
2. All six arms MDD ≤ 51.93%: maximum is **37.66%** (A6). PASS.
3. Neighbourhood spread ≤ 0.35: **0.0873** (1.2107 − 1.1234). PASS with
   an order of magnitude to spare.

Read-out as pre-declared: neighbourhood mean Sharpe is **1.1619**, and
trial 88 (1.1821) is NOT the neighbourhood maximum — A5 beats it at
1.2107. A candidate sitting above the mean but below the local maximum is
the healthy shape; a candidate that is the strict maximum of its own
neighbourhood is the classic knife-edge signature, and that is not what
this is. Per the pre-registration's binding rule, A5's higher score is a
robustness read-out, not a new candidate, and is never nominatable.

Interpretation: shifting every channel window by ±30% moves annualized
Sharpe by less than 0.09 and never breaches the risk bar. The result is
not a fitted parameter artefact.

## Battery B — cost stress (2 runs)

| Arm | Sharpe | MDD | Equity | Verdict |
|---|---:|---:|---:|---|
| 2× costs (trial 108) | 1.1263 | 34.77% | 12,269 | PASS (bar: ≥1.00, positive) |
| 3× costs (trial 109) | 1.0705 | 36.87% | 10,579 | PASS (bar: ≥0.80, positive) |

At triple the modeled fees and slippage the strategy still compounds
1,000 → 10,579 over 7.3 years at Sharpe 1.07. The edge is not an
execution-cost illusion.

## Zero-cost diagnostics (run BEFORE this pre-registration, no trials)

From trial 88's already-registered return series
(`scripts/analyze_candidate.py`; registers nothing):

- **Stationary bootstrap** (2000 resamples, mean block 20d — preserves
  serial dependence): 90% CI **[0.5586, 1.8031]**;
  **P(Sharpe ≤ 0) = 0.0000**; P(Sharpe ≤ 1) = 0.317.
- **Subperiods**: 2018-2020 Sharpe 1.51 (+317%), 2021 1.61 (+108%),
  **2022 −1.17 (−19.9%)**, 2023 1.26 (+37%), 2024-2025H1 1.06 (+49%).
  The 2022 bear year is a genuine losing regime — but its drawdown was
  22.6%, i.e. the strategy loses slowly where buy-and-hold lost ~65%.
- **Rolling 365d Sharpe** (26 quarterly-stepped windows): min −1.20,
  median 1.21, max 2.68, negative in 4 windows (15.4%).
- **Tail dependence**: dropping the best 5 days of 2676 (0.19%) takes
  Sharpe 1.18 → 1.00; dropping the best 20 (0.75%) takes it to 0.57.
  Real, and typical of trend following: the payoff is convex and
  concentrated. Anyone trading this must accept that missing a handful of
  breakout days materially changes the outcome — an execution-discipline
  requirement, not a statistical defect.
- **Versus the live incumbent (trial 4), same universe**: correlation
  0.9269. Trial 88 dominates on every axis — Sharpe 1.182 vs 1.023,
  MDD 33.05% vs 51.93%, terminal wealth 13.23× vs 13.22×. Blends were
  tested at 25/50/75%: every blend is worse than pure trial 88 on both
  Sharpe and MDD. There is no diversification case for holding both; they
  are the same trade with different exit discipline.

## What this does and does not establish

**Establishes**: trial 88's in-sample edge is not a knife-edge parameter
fit, not a cost artefact, not a single-regime fluke, and not
zero-probability under resampling. On the risk axis it strictly dominates
the strategy currently under live observation.

**Does not establish**: out-of-sample validity. Every number above comes
from the same 2018-2025 pre-holdout window. Gate 3 (PBO 0.87 vs the 0.05
bar) and gate 4 (DSR at the new N, reported separately) are unchanged by
robustness evidence — those gates ask a different question, and the
sealed holdout remains the only clean test.

## Consequences recorded

- Trial 88 is entered as the project's **best-evidenced candidate**: the
  only trial with a clean robustness battery behind it.
- The October holdout's nominations remain fixed (N1 live contract, N2
  trial 7) — trial 88 cannot be adjudicated there. Its earliest clean
  out-of-sample evidence is forward-only, which is why a shadow-signal
  track starting now has standalone value.
- §1 candidate-key note: the mechanical dedupe key does not include
  `dc_windows`, so battery-A rows fold with the experiment-7 Donchian
  rows into a single candidate column. This is the same defect recorded
  in the experiment-3 result; it means the battery barely moves PBO, and
  the all-columns number stays the conservative read.

## Provenance

All 8 runs on clean tree `4604fc5` (commit-first rule). Registry rows
carry the never-nominatable marker in `operator_note`. Gate report at
N=109 committed alongside.

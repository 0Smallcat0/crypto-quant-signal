# N-arithmetic weigh-in — should the ninth family run?

Written 2026-07-23, iteration 10 (autonomous). Trigger: `LOOP_LOG.md`
iteration 9 explicit instruction — "**NEXT sitting weighs the N-arithmetic
explicitly before any ninth family (every family raises every trial's
bar)**". This document is the weigh-in. It reads existing results only; it
does NOT pre-register anything (goalpost-drift guard).

## Ground truth from the N=101 report

Source: `docs/reports/research/gate_report_2026-07-22.json` (2676 obs,
2018-03-05 → 2025-07-01, 101 trials).

| Trial | Family | SR (ann.) | MDD | DSR | Passes stop? |
|---:|---|---:|---:|---:|---|
| 29 | exp-3 cs momentum | 1.4109 | 75.08% | 0.9870 | ❌ MDD |
| 37 | exp-3 cs momentum | 1.2431 | 67.53% | 0.9532 | ❌ MDD |
| 88 | exp-7 Donchian BTC/ETH | 1.1821 | 33.05% | 0.9330 | **frontier, 0.017 short** |
| 96 | exp-8 Donchian 13-symbol | 1.0004 | 46.59% | 0.8317 | ❌ SR too low |

Trial 88 is the risk-compliant frontier. The rest either violate MDD or
sit lower on DSR. Every arithmetic decision hinges on trial 88.

## The mechanical bar for a DSR=0.95 pass

Back-solved from the N=101 report (T=2676, Emax_daily=0.032941,
trial-88 DSR z-score gives σ_effective=1.4332):

- At N=101, minimum passing annualized Sharpe = **1.2465**.
- Trial 88 gap = **+0.0644** annualized Sharpe.

## What one more family costs

E[max SR|null] scales as √(2 ln N). A 16-config family lifts N 101→117:

| N | SR bar (ann.) | Trial 88 static-projected DSR | Δ vs today |
|---:|---:|---:|---:|
| 101 | 1.2465 | 0.9330 | 0 |
| 117 | 1.2548 | 0.9305 | −0.0025 |
| 133 | 1.2619 | 0.9283 | −0.0047 |
| 149 | 1.2681 | 0.9264 | −0.0066 |
| 165 | 1.2736 | 0.9246 | −0.0084 |

**Per 16-config family, trial 88 loses ≈0.003 DSR on pure bar-rise
mechanics.** That is the fixed cost of running one more family.

## What variance compression has paid

Observed trial 88 DSR trajectory across the last two families:

- N=93 (post exp-7): DSR 0.9267.
- N=101 (post exp-8): DSR 0.9330 — **+0.0063** net after paying the
  N=93→101 bar rise.

The exp-8 winners clustered at Sharpe 0.92–1.00 (below trial 88's 1.18).
Empirically that tightened the null and paid trial 88 back
+0.0088 raw compression, net of the −0.0025 bar cost. Whether the next
family compresses similarly depends entirely on its winner distribution.

## The two productive bets left (none of them run this iteration)

1. **SSRN-faithful vol-sized Donchian** (Zarattini/Pagani/Barbon 2025).
   Their headline claim rests on Donchian ensemble × volatility-based
   sizing — we only tested the ensemble half (exp-7, exp-8). Vol sizing
   is the untested interlocking half. Requires an allocation-model
   engine feature. Plausible Sharpe range: 1.0–1.4 if the vol overlay
   damps 2021 breakout failure; equal or lower if it doesn't. **Only
   plausible route to a winner ≥ SR 1.25 at N=117 given exp-5 through
   exp-8 winner history.**
2. **Consolidation** — stop spending N, redirect iterations to gate-6
   evidence accumulation (real-money-run readiness, holdout-lock hygiene,
   deployment plumbing) until the October holdout. Trial 88 sits at
   DSR 0.9330 forever; the October holdout gets spent by the
   pre-declared nomination (trial 4) per
   `docs/contracts/PRE_HOLDOUT_PROTOCOL.md`.

Any other family (barbell variants, ATR-sized wrappers on cs momentum,
K/lookback re-sweeps) has expected winner Sharpe distributed the same as
the eight already-run families — median ~1.0, tail ~1.2 — and therefore
strictly negative EV under the arithmetic above.

## Decision recorded

- **This iteration does not pre-register any family** (drift guard —
  this iteration reads results).
- **Next iteration is authorized to pre-register the vol-sized Donchian
  family IF AND ONLY IF the engine work fits inside a single iteration**
  (allocation-model plumbing + tests; run stays in the following
  iteration under commit-first rule 6). If the engineering scope
  overflows one iteration, the honest call is consolidation — every day
  spent on multi-session engine work is a day not spent hardening the
  live paper contract for October.
- The vol-sized Donchian pre-registration must fix its grid **before**
  reading trial 88's return series (which is already in the registry —
  do not re-look, do not select windows post-hoc from the exp-7 winner).
- Statutory bars remain unchanged: DSR ≥ 0.95 AND
  candidates-PBO ≤ 0.05 AND MDD ≤ 51.93% AND turnover ≤ 53.1.

## What this document does NOT do

- Pre-register any family (drift guard).
- Recommend a specific grid (that belongs in the pre-registration).
- Peek at the October holdout (rule 2).
- Change trial 88's standing (it is not this iteration's winner — it is
  the incumbent risk-compliant frontier).

## Provenance

Numbers verified against `docs/reports/research/gate_report_2026-07-22.json`
via direct field extraction; historical DSR values quoted from
`docs/research/GOALP_EXPERIMENT7_RESULT.md` and
`docs/research/GOALP_EXPERIMENT8_RESULT.md`. σ_effective back-solved from
Bailey DSR closed form using trial 88's report row. Committed with this
iteration's LOOP_LOG entry.

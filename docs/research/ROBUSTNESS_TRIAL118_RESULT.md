# Robustness battery on trial 118 — result: it holds, and the endpoint doubt is resolved

Executed: 2026-07-25 · Trials: **126-133** (registry N: 125 → 133)
Pre-registration: `docs/research/ROBUSTNESS_TRIAL118_PREREGISTRATION.md`
(unmodified). Every arm below is bound never-nominatable.

## Battery A — parameter neighbourhood (6 runs)

| Arm | Change | Sharpe | MDD | Turnover | Equity |
|---|---|---:|---:|---:|---:|
| A1 | ATR window 10 | 1.0812 | 43.35% | 11.41 | 11,764 |
| A2 | ATR window 20 | 1.1351 | 33.24% | 11.56 | 12,266 |
| A3 | ATR multiple 1.5 | 1.1142 | 33.72% | 14.10 | 9,810 |
| A4 | ATR multiple 2.5 | 1.1316 | 40.18% | 9.21 | 15,595 |
| A5 | channels −20% | 1.1605 | 36.52% | 12.40 | 15,125 |
| A6 | channels +20% | 1.2298 | 29.93% | 10.25 | 15,004 |
| — | **trial 118** | **1.2411** | **33.24%** | 11.10 | 16,899 |

**Stability verdict — all three criteria PASS:**

1. All six arms Sharpe ≥ 1.00: minimum **1.0812** (A1). PASS.
2. All six arms MDD ≤ 51.93%: maximum **43.35%** (A1). PASS.
3. Spread ≤ 0.35: **0.1486** (1.2298 − 1.0812). PASS.

## The endpoint doubt is resolved — against the grid, in the candidate's favour

Experiment 10's winner sat at the tightest ATR multiple tested (2), and
its result document recorded that as weaker evidence: the grid had not
bracketed the mechanism. Arm A3 probes past that endpoint at multiple
1.5 and scores **1.1142 — materially worse than 2's 1.2411**.

So multiple 2 is a genuine interior optimum, not a boundary artefact:
1.5 is worse, 2.5 is worse (1.1316), 3 is worse (1.0902, experiment 10),
and it decays monotonically from there. The mechanism is bracketed. This
is exactly why the battery's arms are bound never-nominatable — the
question could be asked honestly precisely because no answer to it could
be adopted.

## The honest counterweight: trial 118 IS its neighbourhood maximum

By the same standard applied to trial 88, this is the weaker shape.
Trial 88 sat above its neighbourhood mean but BELOW its maximum (A5 beat
it) — the healthy signature. Trial 118 tops its own neighbourhood
(1.2411 vs the next-best 1.2298, mean 1.1421). A candidate that is the
best point in every direction tested is more likely to have absorbed some
sample-specific luck, and that must be carried forward wherever trial 118
is quoted.

Mitigating, and stated plainly: the margin over the runner-up is 0.011,
the spread is a tight 0.15 across ±20% channel shifts and a 3× swing in
ATR multiple, and no arm comes close to breaching the risk bar. This is a
plateau with a slight peak, not a spike.

## Battery B — cost stress (2 runs)

| Arm | Sharpe | MDD | Equity | Verdict |
|---|---:|---:|---:|---|
| 2× costs (trial 132) | 1.1967 | 34.37% | 15,006 | PASS (bar ≥1.00, positive) |
| 3× costs (trial 133) | 1.1523 | 35.47% | 13,327 | PASS (bar ≥0.80, positive) |

The strongest cost result in the project: at **triple** the modeled fees
and slippage, trial 118 still scores 1.1523 — above trial 88's 3× result
(1.0705) and above the live incumbent's UNSTRESSED Sharpe (1.0230). The
edge is not an execution-cost illusion.

## Registry consequence — the advance prediction was WRONG, measured

N moved 125 → 133. The pre-registration and the first draft of this
document both predicted trial 118's DSR would fall below 0.95 on
bar-rise mechanics alone. **It did not.** Measured at N=133
(`docs/reports/research/gate_report_2026-07-25.json`, regenerated after
the battery):

| | N=125 | N=133 |
|---|---:|---:|
| Trial 118 DSR | 0.950514 | **0.950140** |
| Cross-trial Sharpe variance | 1.6033e-4 | 1.5842e-4 |
| Candidates-PBO | 0.8451 | **0.6518** |
| All-columns PBO | 0.6967 | 0.7326 |

The bar did rise, but the eight battery arms clustered tightly around the
candidate (Sharpe 1.081–1.230), which compressed cross-trial variance
almost exactly as fast. Deflation is not monotone in N — the fifth time
this project has measured that — and the prediction failed because it
accounted for the numerator and ignored the denominator.

The record therefore reads: **trial 118 clears the gate-4 bar at both
N=125 and N=133**, by 0.0005 and 0.0001 respectively. Both margins are
inside the estimate's own noise; "at the bar" remains the honest phrase,
and the tightening margin is a reminder that any further family is
strictly negative EV for this candidate's standing.

Candidates-PBO improved from 0.845 to 0.652 — still failing the 0.05 bar
by an order of magnitude, and the all-columns number moved the other way
(0.697 → 0.733), so nothing here rescues gate 3.

## Where trial 118 now stands

- Passes its own pre-registered family criteria (experiment 10, N=125).
- Passes a full adversarial robustness battery: 6 parameter
  perturbations, 2 cost-stress levels, all 8 criteria.
- Passes zero-cost diagnostics: bootstrap P(Sharpe ≤ 0) = 0.0000, 90% CI
  [0.610, 1.864], four of five subperiods positive.
- Dominates both the live incumbent and trial 88 on Sharpe, terminal
  wealth, turnover, and 2022 behaviour, at equal drawdown.
- **Still fails the project's gate 3** (candidates-PBO 0.845 vs 0.05) and
  therefore qualifies nothing on its own.
- Cannot be adjudicated by the October holdout — nominations were fixed
  on 2026-07-19, before this lineage existed.
- Its only clean out-of-sample evidence is the forward shadow track
  started 2026-07-24.

## Provenance

All 8 runs on clean tree `5f208e2` (commit-first rule). Registry rows
carry the never-nominatable marker in `operator_note`.

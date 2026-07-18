# Goal P experiment 2 — result: family FAILS by 0.44pp; first real signal found

Executed: 2026-07-18 · Trials: **6-21** (registry N: 5 → 21)
Pre-registration: `docs/research/GOALP_EXPERIMENT2_PREREGISTRATION.md` (unmodified)
Gate report: `docs/reports/research/gate_report_2026-07-18.json` (N=21)

## Family winner (pre-declared rule: highest full-window Sharpe)

**Trial 7 — target 30%, window 20d, monthly rebalance**:

| Metric | Trial 4 (raw ladder) | Trial 7 (winner) |
|---|---:|---:|
| Annualized Sharpe | 1.0230 | **1.1270** |
| DSR (same N=21 report) | 0.8799 | **0.9273** |
| Max drawdown | 51.93% | 47.37% |
| Annualized turnover | 17.69 | 11.22 |
| Final equity (1000 start) | 14,221 | **9,280** |

## Verdict against the pre-registered family criteria

1. **Winner DSR > trial 4 DSR in the same N=21 report: PASS** —
   0.9273 vs 0.8799, after paying the full 16-way deflation (N=21,
   registry-wide variance). The first deflation-adjusted improvement in the
   project's history, and the first trial ever to approach the 0.95 gate.
2. **Winner MDD ≤ trial 4 MDD − 5pp: FAIL** — 47.37% vs the required
   ≤ 46.93%. Missed by **0.44pp**.
3. Winner turnover ≤ 2× trial 4: PASS — 11.22 vs 35.37 cap (37% BELOW
   trial 4: fewer, calmer adjustments than the raw ladder).

All three were required. **The family is a registered negative under its own
pre-registration.** The 0.44pp miss is not rounded away and the −5pp bar is
not retroactively softened — that discipline is what makes criterion 1's
PASS believable.

## The honest catch: better Sharpe, one-third less money

The winner's final equity is **9,280 vs 14,221** (−35% absolute return).
Vol targeting shrinks exposure in rich-vol regimes — which in crypto's
history were also the biggest up-years — so risk-adjusted return improves
while compounded wealth falls. Institutional vol-targeting recovers this by
LEVERING to the target; a spot-long-only product cannot lever, so it keeps
the drawdown benefit but forfeits the compensation. Any future adoption
decision must weigh "smoother path, higher DSR" against "materially less
terminal wealth" — for a follower whose failure mode is drawdown
abandonment, the smoother path may still win, but that is a product
decision, not a statistics decision.

## Informative read-outs (pre-declared as non-gating)

- **Signal existence**: most family members beat trial 4's raw Sharpe; the
  winner's DSR (0.9273) is the highest of all 21 registered trials
  (registry best before: 0.86).
- **Frequency**: monthly rebalance — the compliance-friendly arm — WON
  against its daily twin (1.1270 vs 1.0147). Vol control at monthly cadence
  costs nothing here; it helps.
- **Direction**: low target (30%) + short window (20d) dominates the grid.
- **DSR mechanics note**: trial 4's DSR rose from 0.8366 (N=5) to 0.8799
  (N=21) because sixteen similar-Sharpe trials REDUCED cross-trial variance
  faster than N raised the expected max. Deflation is not monotone in N;
  judging within one report (as pre-registered) was the right call.
- Gate 3 PBO at N=21: 0.886 (fails, expected with 21 columns of one
  lineage) — the matrix-composition rule recorded in experiment 1 remains
  the blocking methodological question for October.

## What happens next (sequential research, not a rescue)

Per the pre-registration, a failed family advances the queue — AND the
read-outs legitimately seed a NEW pre-registration (sequential refinement is
normal science; the protection is pre-declared criteria and the single-use
holdout as final arbiter). Candidates for experiment 3: the winner's exact
configuration as a single confirmatory trial with product-decision criteria
(including the terminal-wealth trade-off above), or vol-overlay × universe
interaction after expansion. Decision deferred to the next session —
deliberately: writing the next pre-registration in the same sitting as
reading these numbers is how goalposts drift.

## Provenance

All 16 trials ran on clean tree `94dfcd9` (commit-first rule applied, unlike
experiment 1). Registry rows 6-21 carry full overlay parameters
(vol_target_annualized / vol_window_days / vol_rebalance) for future
matrix-composition rules.

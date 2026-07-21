# Goal P experiment 3 — result: first DSR ≥ 0.95 in project history; family still FAILS on drawdown

Executed: 2026-07-21 · Trials: **22-37** (registry N: 21 → 37)
Pre-registration: `docs/research/GOALP_EXPERIMENT3_PREREGISTRATION.md` (unmodified)
Gate report: `docs/reports/research/gate_report_2026-07-21.json` (N=37, 2676 obs)

## Family table (16 configs, all registered; Sharpe/MDD/turnover from the run)

| Trial | K | Lookback | Cadence | Filter | Sharpe | MDD | Turnover |
|---:|---:|---:|---|---|---:|---:|---:|
| 22 | 2 | 90 | weekly | off | 0.8081 | 68.38% | 9.50 |
| 23 | 2 | 90 | weekly | on | 0.5932 | 69.59% | 2.96 |
| 24 | 2 | 90 | monthly | off | 0.9927 | 56.06% | 4.73 |
| 25 | 2 | 90 | monthly | on | 0.9004 | 51.97% | 4.42 |
| 26 | 2 | 180 | weekly | off | −0.0594 | 66.63% | 1.14 |
| 27 | 2 | 180 | weekly | on | −0.1050 | 69.35% | 0.84 |
| 28 | 2 | 180 | monthly | off | 1.0398 | 73.76% | 1.44 |
| **29** | **2** | **180** | **monthly** | **on** | **1.4109** | **75.08%** | **3.40** |
| 30 | 3 | 90 | weekly | off | 0.8725 | 61.74% | 8.66 |
| 31 | 3 | 90 | weekly | on | 0.5949 | 67.32% | 3.58 |
| 32 | 3 | 90 | monthly | off | 0.8797 | 60.38% | 3.15 |
| 33 | 3 | 90 | monthly | on | 0.7569 | 58.94% | 3.05 |
| 34 | 3 | 180 | weekly | off | 0.3821 | 75.45% | 1.98 |
| 35 | 3 | 180 | weekly | on | 0.9598 | 62.83% | 4.92 |
| 36 | 3 | 180 | monthly | off | 0.8174 | 76.05% | 1.41 |
| 37 | 3 | 180 | monthly | on | 1.2431 | 67.53% | 3.24 |

Winner by the pre-declared rule (highest Sharpe): **trial 29 — K=2,
lookback 180d, monthly, absolute filter ON**.

## Verdict against the frozen family criteria (all three required)

1. **Winner DSR > 0.9273 in the same report: PASS — 0.962102.** The first
   trial in 37 attempts to clear the 0.95 DSR gate, after paying full N=37
   deflation. For scale: the previous record holder trial 7 fell to 0.8205
   in this report (deflation is not monotone — 16 new high-dispersion
   columns raised cross-trial Sharpe variance to 3.64e-4), yet trial 29
   still clears 0.95.
2. **Winner MDD ≤ 51.93%: FAIL — 75.08%**, missed by 23.15pp. A 1000 USDT
   follower would have watched 751 USDT evaporate at the trough. Not
   rounded away, not softened.
3. Winner turnover ≤ 53.1: PASS — 3.40 (calm monthly rebalancing).

**The family is a registered negative under its own pre-registration.**
Same shape as experiment 2, amplified: the statistics improve, the risk a
human can actually sit through does not.

## Stop-condition check (autonomous loop contract)

DSR ≥ 0.95 **met** (trial 29); candidates-PBO ≤ 0.05 **not met**
(0.5834 candidates / 0.6303 all-columns). Both are required → the search
continues. No EDGE_CANDIDATE_FOUND event.

## Honest defects recorded (audit trail)

- **Registry rows 22-37 carry `cs_*` parameters only in operator_note**:
  the engine landed without extending the runner's parameter
  serialization, so machine-readable fields show None. Full configuration
  is recoverable from each row's operator_note (K/lookback/cadence/filter)
  and from this document. Forward-fixed in `src/backtest/runner.py`
  (cs fields now serialize); rows are append-only and stay as written.
- **Candidates-PBO folding**: PRE_HOLDOUT_PROTOCOL §1's dedupe key
  predates the cs family and does not include `cs_*` fields, so all 16 cs
  rows collapse to the highest trial_id (37) in the candidates matrix —
  trial 29 is not a candidates column at all. The 0.5834 candidates-PBO
  therefore measures the pre-existing lineage plus ONE cs column, not
  in-family cs winner-picking. The all-columns PBO (0.6303) includes every
  cs column separately. The protocol is frozen until the holdout spend;
  October's gate-3 read-out must weigh the all-columns number for this
  family. (The DSR table is unaffected — every trial deflates at N=37.)

## Read-outs (pre-declared as non-gating)

- Monthly beat weekly AGAIN, decisively (180d weekly arms are the two
  negative-Sharpe rows; 180d monthly arms are the two family leaders).
  Third experiment in a row where the compliance-friendly cadence wins.
- Absolute filter ON improves Sharpe at 180d (1.04→1.41 at K=2) but does
  NOT contain drawdown (75.08%) — dual momentum's advertised crash
  protection failed to materialize at this horizon on this universe.
- Concentration (K=2) beats breadth (K=3) on Sharpe at 180d.
- Diversification: trial 29's correlation with trial 4's daily returns is
  the pre-declared read-out for a future combination hypothesis; computing
  it is queued for the next iteration (registry return series are durable,
  nothing is lost by deferring).

## What happens next (sequential research, not a rescue)

The stop condition is unmet; the loop continues. The obvious next
hypothesis — pre-registrable no earlier than the NEXT session per the
goalpost-drift guard — is a risk-managed combination: cross-sectional
momentum signal (proven deflation-resistant Sharpe) under a drawdown or
volatility overlay (experiment 2's proven MDD reducer), targeting
criterion 2 without destroying criterion 1. The holdout nominations remain
frozen (N1/N2 per PRE_HOLDOUT_PROTOCOL); nothing here touches October.

## Provenance

All 16 trials ran on clean tree `6163655` (commit-first rule); runner
serialization fix committed after the run (defect section above);
registry, return series, and the N=37 gate report are committed together
with this document.

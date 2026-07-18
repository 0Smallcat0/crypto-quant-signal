# Pre-holdout protocol — fixed before anyone looks

Status: **binding once committed**. Written 2026-07-19, while the locked
holdout (2025-07-02 → 2026-07-01, per `docs/reports/research/holdout_lock.json`)
remains sealed and unread. This document removes the two remaining
researcher degrees of freedom in the October sign-off BEFORE any holdout
information exists to bias them. After the holdout is spent, editing this
file is void by the iterated-OOS doctrine; before then, only typo fixes.

## 1. Gate 3 matrix-composition rule (PBO)

Problem fixed here: the registry now holds 21 columns of one strategy
lineage (originals, an audit rerun, a cost-stress rerun, one confirmation
variant, sixteen vol-overlay family members). CSCV over ALL columns
measures "can you pick among near-duplicates" — a real question — but the
gate's question is "is the CANDIDATE selection process overfit". Both get
reported; the rule below decides which one the gate verdict uses.

**Candidate-column rule (mechanical, from registry fields only):**

A registry row is a candidate column iff:

- `cost_assumptions.cost_multiplier == "1"` (stress reruns excluded), and
- `parameters.holdout_spend != "True"` (the spend row is not a candidate), and
- among rows with identical
  `(config_hash, strategy_name, confirm_days, vol_target_annualized,
  vol_window_days, vol_rebalance)` only the HIGHEST trial_id survives
  (audit/parity reruns of the same configuration collapse to the newest
  engine's row).

The gate report computes and prints **both** PBO numbers — `all_columns`
(conservative upper bound) and `candidates` (gate verdict input). Honesty
clause: this rule exists for semantic correctness, not to rescue the
number. If candidates-PBO still exceeds 0.05, gate 3 fails and that verdict
stands: it means in-family winner-picking is unreliable — which is exactly
why holdout nominations are fixed in §2 rather than chosen after the fact.

## 2. Holdout spend protocol

**Nominations (fixed now, never extended):**

- **N1 — the live contract**: `daily_trend_ensemble`, no overlay. The Goal O
  subject.
- **N2 — the experiment-2 winner**: vol overlay `target 0.30 / window 20d /
  monthly` on the unchanged ladder (trial 7's exact configuration).

One single-use spend event evaluates BOTH nominations on the holdout
window (one unsealing, two pre-declared read-outs — not two spends). No
third configuration may be added regardless of any future backtest result;
a better future candidate waits for a new holdout to accumulate.

**Pre-declared holdout pass bar (per nomination):**

- Holdout-segment annualized Sharpe ≥ 0.5 (half the pre-holdout level —
  decay tolerance chosen blind), and
- Holdout-segment max drawdown ≤ pre-holdout max drawdown + 10pp.

**Consequences, fixed now:**

- N1 passes → Goal O proceeds to its report with gate 6's paper evidence.
- N1 fails → the strategy family returns to research per gate 5; the FAIL
  report is the product.
- N2 passes → N2 does NOT become qualified (it has no 90-day paper period);
  it becomes the pre-registered candidate for the NEXT live contract, which
  starts its own paper qualification. No shortcut exists.
- N2's wealth trade-off (experiment 2: −35% terminal wealth vs N1
  pre-holdout) is a PRODUCT decision documented in
  `docs/research/GOALP_EXPERIMENT2_RESULT.md`; holdout numbers inform it,
  the pass bar above does not decide it.

**Procedure:** the spend uses the existing single-use mechanism
(`--spend-holdout --i-understand-single-use`); the spend run's
`operator_note` must reference this protocol file. The N2 read-out runs the
same spend pipeline with the overlay parameters in the same session, before
any human interprets either result.

## 3. Why this exists

Experiment 1 (2026-07-18) showed adding near-duplicate columns explodes
all-columns PBO (0.018 → 0.879 → 0.886 at N=21); experiment 2 produced the
first deflation-surviving improvement (trial 7 DSR 0.9273) and therefore
the first temptation to steer the sign-off toward a favorite. Every rule
above was written while the holdout is still sealed, which is the only
moment such rules can be written honestly.

# Gate 3 candidate composition at N=133 — what the frozen §1 rule computes, and why no admissible reading changes the verdict

**Date:** 2026-09-01 (autonomous research loop, iteration 56)
**Status:** measurement + closed route. **No rule is changed by this document.**
`docs/contracts/PRE_HOLDOUT_PROTOCOL.md` §1 is frozen until the holdout spend
and stays exactly as written; nothing here is a proposal to amend it.

## Why this was measured

Iteration 55 recorded, as a single line of previously-known context, that none
of the three gate-4 passes (trials 29, 37, 118) is a gate-3 candidate column,
while robustness trial 131 — explicitly never-nominatable — is. That line was
correct and it was left alone, because the gate-4 addendum did not rest on it.

The loop's **stop condition** does rest on it. The only success exit in
`docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md` requires a candidate with
**DSR ≥ 0.95 AND candidates-PBO ≤ 0.05**. The second half is the number
produced by §1's candidate-column rule. Two prior documents
(`GOALP_EXPERIMENT3_RESULT.md`, `ROBUSTNESS_TRIAL88_RESULT.md`) already record
that the rule's dedupe key is incomplete, each for its own family. Nobody has
measured what the rule collapses **registry-wide at N=133**, nor how much of
the resulting verdict number is decided by the rule's own arbitrary tie-break.
This document does both.

## Method, and its validation

CSCV/PBO was recomputed with a block-sum reformulation of the program's own
`probability_of_backtest_overfitting`: because every train/test split is a
union of the S=16 contiguous blocks, each column's split Sharpe is exact from
per-block sums and sums of squares, so all 12 870 partitions evaluate without
re-scanning the 2 676-row matrix. The reformulation is **validated by exact
reproduction** of both recorded numbers in `gate_report_2026-07-25.json`:

| Quantity | Recorded in report | Recomputed here |
|---|---:|---:|
| `pbo_all_columns` (133 columns) | 0.732556 | **0.732556** |
| `pbo` — candidates (37 columns) | 0.651826 | **0.651826** |

Both to six decimal places, on the same 2 672 usable observations and the same
12 870 combinations. No new script was written (the contract's one-script
budget is untouched); no gate report was regenerated; no registry row, return
series, or recorded result was modified.

## What the frozen rule collapses at N=133

§1 excludes cost-stress reruns and holdout-spend rows, then keeps, among rows
sharing `(config_hash, strategy_name, confirm_days, vol_target_annualized,
vol_window_days, vol_rebalance)`, only the **highest trial_id**. At N=133 that
leaves **37 columns from 128 eligible rows** (5 rows excluded as cost stress:
trials 3, 108, 109, 132, 133; no holdout-spend row exists). The 37 columns
decompose as:

| Group | Members | Kept | What it merges |
|---|---:|---:|---|
| singletons | 34 rows, 1 each | 34 | one column each, as intended |
| parity pair | 2 rows: 2, 4 | 4 | trial 4 is the audit-fix parity rerun of trial 2 — **the only group where the rule does the job it was written for** |
| mega-group A | **48 rows: 22–37, 54–85** | **85** | the whole of experiment 3 (cross-sectional momentum), experiment 5 (regime-gated cs) and experiment 6 (trend factor) |
| mega-group B | **44 rows: 86–107, 110–131** | **131** | the whole of experiment 7 (Donchian ensemble), experiment 9 (inverse-vol sizing), experiment 10 (ATR-channel exit), **and both robustness batteries** |

So **92 of the 133 registered trials enter gate 3 as two columns**, and the two
survivors are decided by an index: trial 85 (an experiment-6 trend-factor arm)
and trial **131 — a row whose own operator_note reads "ROBUSTNESS (never
nominatable)"**. Trials 29, 37, 88, 106 and 118 — the three gate-4 passes and
the two trials the program actually shadow-tracks — are all absent.

### Mechanism, named exactly

`config_hash` does not vary within a family. Every family runner computes it
**once, from the base config snapshot, before the parameter sweep begins** —
e.g. `scripts/run_donchian_family.py:63`, `scripts/run_cs_family.py:85` and
`scripts/run_robustness_trial118.py:73` all call
`config_hash_for(config_snapshot(config))` outside their loops. The swept
parameters (`dc_windows`, `dc_exit`, `cs_top_k`, `cs_lookback_days`, …) never
reach the hash, and §1's key adds only `confirm_days` and the three `vol_*`
fields, none of which any of these families varies. The key therefore reads
"same base config file" where it intends "same configuration".

A second, independent defect compounds it inside mega-group A: registry rows
22–37 serialize their `cs_*` parameters only in `operator_note` (recorded in
`GOALP_EXPERIMENT3_RESULT.md`), so those 16 rows are machine-indistinguishable
**even under a full-parameter key**.

## The measurement: the verdict number is a distribution, not a value

The tie-break "highest trial_id" is arbitrary with respect to everything the
gate is asking. Holding the frozen rule's filters and grouping **exactly as
written** and varying only which member of each multi-member group represents
it, there are 2 × 44 × 48 = **4 224 admissible representative choices**. All
4 224 were evaluated.

| Reading | Representatives | candidates-PBO |
|---|---|---:|
| **as recorded** (highest trial_id) | 4, 131, 85 | **0.651826** |
| lowest trial_id | 2, 86, 22 | 0.852214 |
| highest-Sharpe member of each group | 4, 118, 29 | 0.454623 |
| forcing trial 88 (shadow-tracked) | 4, 88, 85 | 0.749728 |
| forcing trial 118 (only risk-compliant gate-4 pass) | 4, 118, 85 | 0.624553 |
| forcing trial 29 (highest DSR in the registry) | 4, 131, 29 | 0.461927 |
| minimum over all 4 224 | 2, 118, 29 | **0.454468** |
| maximum over all 4 224 | 2, 126, 28 | **0.924320** |

Distribution over the 4 224: **min 0.454468, 5th pct 0.648920, median 0.840676,
mean 0.815265, 95th pct 0.884382, max 0.924320.**

Three readings follow, and only the third is a finding about the world:

1. **The verdict input spans 0.45 to 0.92** — a factor of two — under a choice
   the rule makes on an index that carries no information about the strategies.
   `0.651826` is not a property of the registry; it is one draw from that set.
2. **The recorded draw is a favourable one.** It sits at the **5.2nd
   percentile**: only 5.2% of admissible choices produce a smaller number.
   Repairing the key toward what it intended — grouping on the full
   machine-readable parameter set, which yields **111 columns** — gives
   **0.799145**, worse than both recorded numbers.
3. **Nothing rescues gate 3.** **0 of 4 224** admissible readings reach the 0.05
   bar. The best case, 0.454468, misses it by **9.1x**; the recorded 0.651826
   by **13.0x**; the all-columns 0.732556 by **14.7x**; the repaired-key
   0.799145 by **16.0x**. Gate 3's FAIL verdict does not depend on candidate
   composition **at all**.

### One contract sentence no longer describes the numbers

§1 calls the all-columns PBO the "conservative upper bound". At N=133 it is not
an upper bound: **88.3% of the 4 224 admissible candidate readings exceed
0.732556**, and the median candidate reading (0.840676) is well above it. That
was plausibly true at N=21 when the rule was written; at N=133 the pooling is
severe enough that dropping 96 columns usually *raises* measured PBO. The
protocol is frozen and is **not edited here** — this is recorded as an
operator-attention item for the October gate-3 read-out, which under both
`GOALP_EXPERIMENT3_RESULT.md` and `ROBUSTNESS_TRIAL88_RESULT.md` was already
told to weigh the all-columns number.

## What this closes

**Route closed: candidate composition.** No future iteration may propose
re-examining, re-deriving, or re-representing gate 3's candidate columns in the
hope of a different verdict. The verdict is FAIL across every admissible
reading of the frozen rule, across the repaired key, and across all columns.
The only remaining honest use of the number is deciding *which* failing number
October cites, and that is an operator decision, not a research one.

**Third independent line saying the search is over.** Iteration 26 reached it
through gate 4's fragility at N=133; iteration 55 replaced that with the
structural disjointness of the DSR-robust and risk-compliant regions; this adds
a third: the stop condition's PBO half is missed by an order of magnitude under
every reading, and `PRE_HOLDOUT_PROTOCOL.md` §3 records that adding
near-duplicate columns drove all-columns PBO 0.018 → 0.879 → 0.886 at N=21, so
more searching moves this number the wrong way.

## Guards against over-reading

- **This is not a rule change and not a rescue.** The frozen rule stands; the
  recorded 0.651826 stands; the FAIL verdict stands and is unchanged in both
  directions. The measurement's direction happens to be unflattering.
- **PBO is a property of a selection procedure over a set of columns, not of a
  trial.** "Trial 118's PBO" is not a quantity, and nothing here licenses
  attaching 0.624553 to trial 118 as if it were one.
- **The tie-break sweep is a counterfactual, not an alternative gate.** It
  measures how much of a published number is decided by an arbitrary index. No
  reading in the table above may be cited as "the" candidates-PBO.
- **The mega-groups are not evidence that the families are near-duplicates.**
  They are near-duplicates *to the key*, which reads only the base config.

## Stop-condition check

Unchanged and negative. **DSR ≥ 0.95 AND candidates-PBO ≤ 0.05**: three trials
meet the first (29, 37, 118, of which only 118 is risk-compliant); the second
fails under all 4 224 readings, the repaired key, and all columns. **No
`EDGE_CANDIDATE_FOUND.md` event, and none is warranted.**

## What this document does not do

No gate rule modified, no frozen pre-registration or contract file edited, no
registry row touched, no return series touched, no gate report regenerated, no
result document rewritten, no prior log entry edited, no trial registered, no
backtest run, no arm run, no new script written, holdout untouched and `spent`
still `false`, no `configs/runtime/` or live-runtime file touched.

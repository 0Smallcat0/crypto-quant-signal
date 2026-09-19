# Lever 3 — what could an operator override of P3 actually buy?

Date: 2026-09-19 (iteration 64) · Registry artifacts only · Zero registry
cost (no trial registered, no backtest run, no family run, no gate report
regenerated, no new script) · **The holdout was not read and `spent` is
still `false`.** Every number below comes from
`docs/reports/research/trial_registry.jsonl`,
`docs/reports/research/trial_returns/`, and the three dated gate reports —
all pre-holdout artifacts ending 2025-07-01.

## Why this document exists

`AUTONOMOUS_RESEARCH_LOOP.md` lists three states that could unblock this
program. Two are now measured and neither decides anything: forward
validation (iterations 25, 59-62 — all three tests of the 2026-10-22 read
are mechanism checks) and the October holdout (iteration 63 — a dead
strategy clears its bar 30.91% of the time, an intact one fails 30.1%).

The third has never been measured:

> 3. An operator override of P3 that accepts the recorded cost of a new
>    family.

What exists instead is an *assertion*, carried since 2026-07-26 and
restated in iteration 63's log — that such an override "would produce an
untrustworthy winner". The assertion has a stated mechanism, in P3's own
words:

> **P3: no new single-market parameter families.** They cost N, raise
> every trial's bar, and the two diagnostics above say the winner cannot
> be trusted anyway.

That is three claims, and this document measures all three. It returns a
**quantified bar**, a **refutation of P3's stated rationale**, and a
**gate defect** — and, unlike levers 1 and 2, it does **not** close the
route.

---

## 0. Baseline reproduced before anything was computed

Nothing below is trusted until the recorded artifacts reproduce from
their own inputs.

| Recorded quantity | Source | Reproduced |
|---|---|---|
| Sharpe variance (de-annualized), N=133 | `gate_report_2026-07-25.json` `0.00015842198033849873` | **0.00015842198033849873** (exact) |
| Gate-3 candidate ids | same, 37 ids | **37 ids, list-equal** |
| candidates-PBO | same, `0.651826` | **0.651826**, 12 870 combinations (recorded 12 870) |
| DSR trial 118 | same, `0.950140` | **0.950140** |
| DSR trial 88 | same, `0.931948` | **0.931948** |
| DSR trial 29 / 37 | same, `0.986670` / `0.952424` | **0.986670** / **0.952424** |
| MinTRL trial 88 @95% vs SR\*=0 | iteration 25, `706 d` | **705.7 d** |
| Spearman(Sharpe, maxDD) | iteration 55, `-0.6789` | **-0.6789** |

The PBO reproduction is the load-bearing one: it is computed here from
block aggregates rather than by re-slicing the matrix, and it lands on the
recorded six-decimal value, so the fast path used throughout §3 is the
same statistic the gate reports.

---

## 1. The structural asymmetry — a family pays K to gate 4 and buys one column at gate 3

`config_hash` is computed **once per family run, before the sweep loop**.
This is not inferred from the data; it is visible at
`scripts/run_atr_family.py:63`, `scripts/run_alloc_family.py:64` and
`scripts/run_combo_family.py:63`, each of which computes
`config_hash_for(config_snapshot(config))` outside the loop and passes it
unchanged into every arm.

Gate 3's candidate key (`scripts/run_gate_report.py:73-80`) has six
fields: `config_hash`, `strategy_name`, `confirm_days`,
`vol_target_annualized`, `vol_window_days`, `vol_rebalance`. A family that
sweeps **only fields outside that key** — windows, exit rule, ATR window,
ATR multiple, ladder, allocation caps — collapses to exactly **one**
column, whatever its arm count.

The registry demonstrates it twice, in opposite directions:

| Group | Rows | Candidate columns | Why |
|---|---:|---:|---|
| cs-momentum (exp 3/5/6) | 48 | **1** | swept parameters outside the key |
| donchian ensemble (exp 7/9/10 + both batteries) | 44 | **1** | same |
| vol-target grid (trials 6-21) | 16 | **16** | swept `vol_target_annualized`, `vol_window_days`, `vol_rebalance` — all *inside* the key |

P3 forbids "single-market **parameter** families" — the windows/exit/ATR
kind. Those are precisely the kind that collapse. So the override's
arithmetic is fixed in advance: **K new rows on gate 4's N, one new column
on gate 3's candidate matrix.**

---

## 2. Gate 4 is not the binding constraint, and P3's stated rationale is wrong

### 2.1 The bar a family raises for its own winner

Required annualized Sharpe for DSR ≥ 0.95, holding the Sharpe variance at
the registry's recorded value and raising only N, under trial 118's own
higher-moment profile (skew 0.156784, kurtosis 12.979892, n = 2676):

| Family size K | N | E[max] | Required ann. Sharpe | vs K=0 |
|---:|---:|---:|---:|---:|
| 0 | 133 | 0.03309464 | **1.240607** | — |
| 8 | 141 | 0.03334450 | 1.245398 | +0.004791 |
| 44 | 177 | 0.03430276 | **1.263775** | **+0.023168 (+1.87%)** |
| 128 | 261 | 0.03588966 | 1.294211 | +0.053604 |
| 1024 | 1157 | 0.04148996 | 1.401658 | +0.161051 |
| 4096 | 4229 | 0.04587576 | 1.485843 | +0.245236 |

The largest parameter family this registry has ever run is 44 arms. It
would raise its own winner's bar by **1.87%**. A family sixteen times
larger than the entire search to date (K=4096) raises it by 19.8%.
**"They cost N" is true; "the cost is material to the new candidate" is
not.**

### 2.2 The premise "every family raises every trial's bar" is false, and the registry's own history refutes it

`N_ARITHMETIC_2026-07-23.md` rests on that sentence, and projects trial
88's DSR falling to 0.9283 at N=133. The projection holds the variance
fixed. The gate report recomputes it from all registry Sharpes every run,
so both inputs move — and they move in opposite directions.

| Gate report | N | Variance (de-annualized) | E[max] |
|---|---:|---:|---:|
| 2026-07-21 | 85 | 1.852337e-04 | 0.03365610 |
| 2026-07-22 | 101 | 1.689797e-04 | **0.03294135** |
| 2026-07-25 | 133 | 1.584220e-04 | 0.03309464 |

- **N=85 → 101: the bar FELL by 0.00071475.** Sixteen new trials made
  every registered trial's DSR *easier*, not harder. The sentence
  `N_ARITHMETIC_2026-07-23.md` was built on is contradicted by a gate
  report that already existed when it was written.
- **N=101 → 133:** at fixed variance E[max] would have reached
  **0.03417962**, a rise of 0.00123827. The realized rise was
  **0.00015329**. The variance channel absorbed **87.62%** of the raw-N
  cost. Trial 88's recorded DSR went 0.932985 → 0.931948, a fall of
  0.001037 against the document's projected 0.0047.

The direction of the historical N=101→133 move was right; the magnitude
was overstated by a factor of about four, and the N=85→101 move had the
wrong sign entirely.

### 2.3 At the gate-3 crossing, gate 4 is not close to binding

A candidate at the annualized Sharpe §3 shows gate 3 requires — 1.6294 —
scores DSR **0.995079** at K=44, **0.995565** at K=8, **0.995835** at
K=1 — against a 0.95 bar. Gate 4 is 0.045 of DSR away from mattering.

---

## 3. Gate 3 is the binding constraint, and its bar is an annualized Sharpe near 1.63

### 3.1 What a single added column can do

PBO counts the splits in which the in-sample-best column lands at or below
the median out-of-sample. If the new column is IS-best in **every** split
— the maximum dominance one column can have — the recorded PBO becomes
exactly that column's own OOS-below-median frequency. So a one-column
addition can move PBO anywhere in [0, 1], and the whole question is what
frequency the new column can achieve.

Measured for each of the 37 existing candidate columns, over all 12 870
CSCV splits:

| Column | P(OOS below median) | P(IS-best) today | Ann. Sharpe |
|---:|---:|---:|---:|
| trial 131 | **0.105361** | 0.345221 | 1.2298 |
| trial 14 | 0.183683 | 0.033722 | 1.0865 |
| trial 15 | 0.212199 | 0.000466 | 1.0832 |
| … | … | … | … |
| trial 1 | 0.995493 | 0.000155 | -0.3750 |

**The best column in the registry, made perfectly IS-dominant, would still
record PBO = 0.105361 — 2.11x the 0.05 bar. Zero of 37 columns reach
0.05.** Nothing shaped like anything this program has built passes gate 3,
even given free selection.

### 3.2 So how much better does the new column have to be?

Take an existing column and add a constant daily alpha δ — the friendliest
possible improvement, since it raises the mean and leaves the shape alone
— then recompute the exact 38-column PBO and bisect for PBO ≤ 0.05. Run
from five different base shapes:

| Base column | Base ann. SR | δ\* (%/yr) | Ann. SR at crossing | PBO | P(IS-best) |
|---:|---:|---:|---:|---:|---:|
| trial 131 | 1.2298 | 14.0013 | **1.6294** | 0.049961 | 0.9479 |
| trial 14 | 1.0865 | 19.5707 | **1.5814** | 0.049961 | 0.9494 |
| trial 7 | 1.1270 | 20.6343 | **1.7857** | 0.049961 | 0.9500 |
| trial 15 | 1.0832 | 22.2091 | **1.6253** | 0.049961 | 0.9500 |
| trial 85 | 0.8576 | 44.0970 | **1.6993** | 0.049961 | 0.9322 |

The required alpha varies three-fold across base shapes; the **Sharpe at
which PBO crosses 0.05 does not** — five independent shapes land in
**1.5814 to 1.7857**, median **1.6294**. The bar is a property of the
gate, not of the base.

Read directly: to pass gate 3, the new column must be OOS-above-median in
**≥ 95% of 12 870 half-sample partitions** of 2018-2025. The registry's
single best column manages 89.5%.

### 3.3 What that bar is, in this registry's own terms

| Reference | Ann. Sharpe |
|---|---:|
| **Gate-3 crossing (median of five shapes)** | **1.6294** |
| Best trial ever registered (trial 29, 75.08% drawdown) | 1.410899 |
| Live contract, trial 118 (33.24% drawdown) | 1.2411 |
| Gate-4 bar at K=44 | 1.263775 |
| Registry mean | 0.944374 |

**0 of 133 trials reach 1.5814**, the lowest of the five crossings.
Trial 29 — the highest Sharpe this program has ever produced, and
disqualified by drawdown — is **13.4% short** of the median crossing.
Three trials in 133 exceed 1.2411 at all, and two of those carry 75.08%
and 67.53% drawdown against registry-wide Spearman(Sharpe, maxDD) =
**-0.6789**.

The 1.63 figure is a **floor, not an estimate**: constant alpha is the
kindest improvement available, so a real strategy of different shape
would need at least this much.

---

## 4. A defect: gate 4 can be diluted into passing

Gate 4's variance input is the **population variance of every registry
Sharpe**, recomputed on each report. Adding arms at the pool mean shrinks
it as 133/(133+K) while E[max] scales as its square root — and that falls
faster than the Φ⁻¹(1−1/N) term grows.

Adding K arms at the registry's own mean Sharpe (0.944374), changing
nothing else:

| K | N | Variance | E[max] | DSR trial 118 | DSR trial 88 |
|---:|---:|---:|---:|---:|---:|
| 0 | 133 | 1.584220e-04 | 0.03309464 | 0.950140 | 0.931948 |
| 1 | 134 | 1.572397e-04 | 0.03300293 | **0.950626** | 0.932569 |
| 39 | 172 | 1.225007e-04 | 0.03005902 | 0.964308 | **0.950291** |
| 100 | 233 | 9.042971e-05 | 0.02676982 | 0.975749 | 0.965471 |
| 1000 | 1133 | 1.859675e-05 | 0.01418978 | 0.995639 | 0.993237 |

**Thirty-nine arms at the registry mean turn trial 88 from a gate-4
failure (0.931948) into a pass (0.950291), and simultaneously lift trial
118 to 0.964308 — with no new information of any kind.** A thousand puts
both above 0.99.

Three things must be said precisely about this.

- **It is not an allegation.** Iteration 26 already checked for
  unregistered arms and found none; all 64 cs-momentum arms and both
  robustness batteries are inside the 133. This is a property of the
  gate, not a claim about the record.
- **The math is textbook-correct.** DSR's null is the max of N trials
  drawn with Sharpe variance V. If you truly ran 39 more mediocre
  strategies, the empirical spread of your search *is* narrower. The
  defect is that **V is estimated from the same trials being graded**, so
  the input is controllable by whoever runs the search — and the
  literature's guidance on this input is entirely one-directional
  (see `RESEARCH_LOG.md`, 2026-09-19: the standard warning is against
  **undercounting** trials, never against padding with near-mean ones).
- **It completes iteration 26 rather than contradicting it.** That
  iteration measured the preserving window for a 134th trial as Sharpe
  **[0.709, 1.180]** and concluded "finding something as good as what the
  program already has would destroy the pass". Correct, and the converse
  was never stated: **finding something mediocre rescues it.** The
  headline "a margin of exactly one trial" is therefore a margin of
  exactly one *good* trial; a 134th at the registry mean raises trial
  118's DSR to 0.950626.

---

## 5. A procedural hazard: gate 3 does not see the family's winner

Within a collapsed group, the candidate rule keeps the **highest
trial_id** — the arm registered last, not the best one.

| Group | Rows | Representative | Its rank inside its own group | Group's best arm |
|---|---:|---|---:|---|
| cs-momentum | 48 | trial 85, SR 0.8576 | **26th of 48** | trial 29, SR 1.410899 |
| donchian | 44 | trial 131, SR 1.2298 | 2nd of 44 | trial 118, SR 1.2411 |

Gate 3 currently represents this registry's largest family by its
**26th-best arm**, and represents the other by a near-best arm only
because a robustness battery happened to run after trial 118.

This is a hazard, not a barrier: the candidate rule explicitly
contemplates "audit/parity reruns" counting once on the newest engine, so
re-running the winning arm last makes it the representative, at a cost of
+1 on N. But it has to be done deliberately, and no pre-registration in
this program has ever mentioned it.

---

## 6. What the lever can and cannot buy

**Can:** trip the contract's stop condition. Unlike levers 1 and 2, this
one is not closed. A new family whose representative column reaches an
annualized Sharpe of roughly 1.63 on 2018-2025 would record PBO ≤ 0.05
and DSR ≈ 0.995, which is exactly `DSR ≥ 0.95 AND candidates-PBO ≤ 0.05`.

**Cannot:** produce forward evidence any sooner. Such a winner starts its
own forward clock on its run date. Its MinTRL, computed on the crossing
profile: **377.2 days** at 95% against SR\* = 0, **783.9 days** at 95%
against gate 5's SR\* = 0.5. Faster than trial 88's 706 days because the
Sharpe is higher — but still a 2027-or-later date from a standing start,
and gates 5 and 6 remain unexecuted either way.

**Cannot:** be justified by P3's stated reasons. Two of the three are
measurably wrong. "They cost N" understates nothing and overstates much:
the cost to the new candidate is +1.87% of bar at K=44. "Raise every
trial's bar" is false — the registry's own N=85→101 step lowered it.
Only the third reason survives: PBO 0.7411 across distinct architectures
still says a selected winner does not generalize, and §3.1 is the sharpest
statement of it yet — no column this program has produced, given perfect
selection, comes within 2.1x of the bar.

**The honest summary is a reversal of emphasis.** P3 forbids new families
because of what they cost. They cost almost nothing at gate 4. What
actually stands in the way is that gate 3's bar sits **15.5% above the
best Sharpe in 133 trials and 31.3% above the live contract** — and that
the gate protecting it can be diluted into passing by arms that carry no
information at all.

---

## 7. Three options for the operator

Nothing here was repaired. All three are operator decisions; none is a
loop decision.

**(A) Leave P3 in force, and correct its rationale.** Cost: nothing
changes materially; the search stays over. Benefit: the contract stops
asserting an N-cost that measurement does not support, and the standing
answer stops resting on it. The route stays open but unused.

**(B) Override P3 with a pre-declared bar and an anti-dilution rule.**
Run one new family, pre-registering (i) that its winning arm is re-run
last so it becomes the gate-3 representative (§5), (ii) that the
gate-3-relevant target is a representative-column Sharpe ≥ 1.63 measured
before any nomination, and (iii) that the Sharpe variance used at gate 4
is frozen at its pre-family value, so the family cannot lower the bar it
is being graded against (§4). Cost: measured, a family carrying a winner at
1.6294 drops trial 118 below the DSR bar at K=1 (0.945210) and K=8
(0.948763) and only restores it at K=44 (0.961963) — and it restores it
*through the dilution channel* that rule (iii) exists to neutralise. So
the honest price of (B) is the loss of the one risk-compliant gate-4 pass
the program has, in exchange for a shot at a bar nothing in 133 trials
has come within 15% of.

**(C) Repair gate 4's variance input first, and decide afterwards.**
Declare the variance convention before recomputing anything — the same
duty iteration 27 recorded for `effective_N`, and for the same reason:
the method choice must be fixed before its effect is visible. Cost: a
sixth open choice, and the recomputation may move the one existing pass in
either direction. Benefit: it is the only option under which a future
gate-4 pass means what the gate report says it means.

This is the **sixth** operator choice now due, joining the cost omission
(iteration 59), the archive-vs-reconstruct choice and the replay-depth
specification (iteration 61), Test 2's framing (iteration 62), and the
holdout's N1 referent (iteration 63). Unlike the previous five, this one
is not dated to 2026-10-22 — it has no deadline, which is precisely why
it has gone unmeasured for eight weeks.

---

## Method note — exactly reproducible, no new script

The one-script budget is unspent; the measurement is inline and reruns
verbatim from this note. Inputs: `docs/reports/research/trial_registry.jsonl`,
`docs/reports/research/trial_returns/trial-*.json` (2676 daily returns
each, 2018-03-05..2025-07-01), and `gate_report_2026-07-{21,22,25}.json`.

- **PBO**: exactly `src/backtest/validation.py`'s CSCV — 16 contiguous
  equal blocks over the first 2672 rows, all 12 870 symmetric splits,
  `_column_sharpe` = `fmean/stdev` with sample (n−1) stdev, overfit when
  `rank/(N+1) ≤ 0.5`. Computed from per-block `Σx` and `Σx²` so any block
  subset's Sharpe is exact in closed form; verified against the recorded
  0.651826 before use.
- **New column**: `X = base + δ`, so its block aggregates are
  `Σx + nδ` and `Σx² + 2δΣx + nδ²`. Ranks recomputed over all 38 columns
  with denominator 39.
- **E[max]**: `√V · ((1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(Ne)))`, γ = Euler-
  Mascheroni, matching `deflated_sharpe_ratio()`.
- **DSR**: `Φ((SR − E[max])·√(n−1) / √(1 − g₃SR + (g₄−1)/4·SR²))` with
  per-period SR and population skew/raw kurtosis, matching the same
  function; reproduces all four recorded per-trial values.
- **Variance**: `pvariance(annualized Sharpes)/365`, matching
  `non_annualized_sharpe_variance()`.
- **MinTRL**: `1 + (1 − g₃SR + (g₄−1)/4·SR²)·(Φ⁻¹(c)/(SR − SR\*))²`;
  reproduces iteration 25's 706 days for trial 88.

## What this iteration did not do

No family was run and no arm was registered. No backtest was run, no gate
report regenerated, no registry row or return series touched, no script
added or modified, no frozen pre-registration or gate rule edited, no
nomination substituted. The holdout was not read, fetched, or unsealed;
`spent` remains `false`. No shadow file was written to or read for a
metric, no forward number computed or cited as support, no read date
moved. No file under `configs/runtime/`, `src/`, `scripts/` or any
scheduled-task definition was changed — `run_atr_family.py`,
`run_alloc_family.py`, `run_combo_family.py` and `run_gate_report.py` were
read and quoted, never written. No prior result document was rewritten;
`N_ARITHMETIC_2026-07-23.md` receives a dated append-only addendum, which
is the established pattern.

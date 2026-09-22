# The last open lever — is the gate-3 bar reachable by anything this engine can build?

Date: 2026-09-22 (iteration 67) · Backtest-only, **nothing registered** ·
The holdout was **not read, not fetched and not unsealed**; `spent` is
still `false`. Every input is a pre-holdout artifact ending 2025-07-01:
`data/candles_preholdout/`, `docs/reports/research/trial_registry.jsonl`,
`docs/reports/research/trial_returns/`, and the 2026-07-25 gate report.

Reproduce with `scripts/analyze_architecture_ceiling.py`
(`--mode validate`, `--mode pbo-validate`, `--mode sweep`,
`--mode stop-condition`). It imports `src.backtest.engine.run_backtest`
only — never `run_registered_backtest`, never `append_trial` — so N is
still **133**, no candidate column was created, no return series was
written next to the registry, and no gate report was regenerated. Sweep
output lives in the gitignored `data/research/ceiling/`.

## Why this document exists

Iteration 64 measured what gate 3 **requires** of a new parameter family
and left the P3 override as the only unblocking lever not closed:

> a family whose representative column reached ~1.63 would trip the stop
> condition … what binds is a gate-3 pass bar near annualized Sharpe
> **1.63** that 0 of 133 trials reach.

Iteration 65 finished the gates, iteration 66 finished the queue. The
question nobody had asked is the opposite one, and it is the last input
the operator needs in order to decide the override:

> **Is 1.63 reachable by anything this repository can build?**

"0 of 133 trials reach it" is a statement about what was *tried*, not
about what is *available*. This document measures what is available, by
exhaustive hindsight search over the engine's whole expressible parameter
space, and then runs the winner through the stop condition.

**The method's one honest guarantee.** The maximum of a hindsight sweep
is an upper bound on what an honest family of the same architecture can
produce: an honest family picks its winner without seeing the future and
cannot beat the arm picked with full hindsight over a superset of its own
grid. That is the only sense in which any number below is a ceiling.

**The pre-commitment, made before the sweep ran and kept.** The argmax of
a hindsight sweep is by construction the most overfit object its grid
contains. Nothing found here is nominated, registered, proposed, or
described as an edge. It is a bound.

---

## 0. Baseline reproduced before anything was computed

Nothing below is trusted until the recorded artifacts reproduce from
their own inputs under today's HEAD.

| Recorded quantity | Source | Reproduced |
|---|---|---|
| Trial 88 ann. Sharpe | registry `1.182061` | **1.182061** (obs 2676) |
| Trial 118 ann. Sharpe | registry `1.241113` | **1.241113** (obs 2676) |
| Trial 131 ann. Sharpe | registry `1.229837` | **1.229837** (obs 2676) |
| Trial 56 ann. Sharpe | registry `1.165094` | **1.165094** (obs 2676) |
| candidates-PBO | `gate_report_2026-07-25.json` `0.651826` | **0.651826** |
| all-columns PBO | same, `0.732556` | **0.732556** |
| Sharpe variance (de-annualized) | same, `1.5842198033849873e-04` | **1.58421980338499e-04** |
| Required ann. Sharpe, DSR ≥ 0.95, N=133 | iteration 64, `1.240607` | **1.240607** |
| same, N=141 / N=177 | iteration 64, `1.245398` / `1.263775` | **1.245398** / **1.263775** |

The PBO reproduction is the load-bearing one. The reference
implementation in `src/backtest/validation.py` re-slices a 2672×37 Python
matrix once per partition and takes over fifteen minutes, which is
unusable when the statistic has to be recomputed per candidate arm. The
vectorised path in `fast_pbo()` computes the same number from per-block
sufficient statistics and lands on **both** recorded six-decimal values,
so the fast path is the same statistic the gate reports.

**Window alignment is exact by construction, not by trimming.** The
engine's snapshot warmup is a fixed 200 closes
(`DAILY_TREND_LOOKBACKS`, `src/features/daily_trend.py:16-17`), so the
decision-day set does not depend on the swept parameters. Every one of
the arms below returned `observation_days = 2676` — the registry's own
window — including window sets longer than 200, where a channel with
fewer prior closes than its length simply stays OFF.

---

## 1. What was swept, and what was not

| Grid | Universe | Arms | Valid | Max ann. Sharpe | Median |
|---|---|---:|---:|---:|---:|
| `cs-13` — cross-sectional momentum | 13 coins | 2 970 | **1 980** | **1.578665** | 0.974487 |
| `donchian-btceth` stage 1 | BTC/ETH | 29 070 | 29 070 | 1.333084 | 1.062530 |
| `donchian-btceth-atr` stage 2 | BTC/ETH | 5 000 | 5 000 | 1.333084 | 1.155778 |
| `donchian-13` | 13 coins | 2 970 | 2 970 | 1.144485 | 0.929708 |
| **Total** | | **40 010** | **39 020** | **1.578665** | |

**Reported, not silently dropped: 990 of the 2 970 cs arms were rejected
by the engine's own validator** — `cs_rebalance_cadence must be 'weekly'
or 'monthly'`, so the `daily` third of that grid does not exist as a
strategy. The valid cs grid is 9 × 11 × 2 × 2 × 5 = **1 980**.

**The Donchian sweep is staged, and the stage is reported because it is a
real limitation.** The full cross product — 4 845 window sets × 3 exits ×
3 ATR windows × 6 ATR multiples — is 96 900 arms at the measured 7.5-8.1
arms/second, i.e. **215 minutes**, which does not fit one iteration.
Stage 1 is therefore **exhaustive over the window space**, the family's
only shape dimension, at a representative exit subset (`half_low`,
`mid_channel`, and `atr_channel` at ATR window 14/28 × multiple 2/4);
stage 2 then ran the **full** 3 × 6 ATR grid over the 250 leading window
sets. **Stage 2 did not move the maximum** — 1.333084 in both — which is
the evidence that stage 1's exit subset did not hide a better ATR corner.
It remains a staged search and a full cross product could in principle
find more.

**What has no ceiling to sweep.** The ladder family
(`daily_trend_ensemble`, 16 registry rows, plus trials 1-4) has **no
sweepable signal parameter**: its lookbacks are the module constant
`(20, 65, 150, 200)` at `src/features/daily_trend.py:16`, not a
`BacktestParameters` field. Its only parameter family is the 16-arm
volatility overlay of experiment 2, whose registered maximum is
**1.127022** (trial 7). The swept architectures generate **112 of the 133
registry rows** (64 cross-sectional + 48 Donchian); the remaining 21 are
the ladder family, `confirmed_trend_ensemble` (1 row), and the four
un-named early trials.

**Scope, stated plainly.** This is the ceiling of the parameter space
**this engine can express today**, which is exactly what P3 governs — P3
forbids "new single-market **parameter** families". A new *architecture*
requires new code and is not measured here.

---

## 2. The ceiling: annualized Sharpe 1.578665

The best arm the engine can express, over **39 020** valid arms and its own
registry window:

| Property | Value |
|---|---|
| Architecture | `cross_sectional_momentum`, 13-coin universe |
| Parameters | `cs_top_k=3`, `cs_lookback_days=120`, `cs_rebalance_cadence=monthly`, `cs_absolute_filter=True`, regime gate `sma=50` / basis `btc` / hysteresis `0.02` / cadence `daily` |
| Annualized Sharpe | **1.578665** |
| Max drawdown | **38.4135 %** |
| Terminal wealth | **60.25x** |
| Trades / annualized turnover | 132 / 6.197245 |
| Observation days | 2676 (registry window, exact) |

**It is not a registered trial, and it is outside the registry on two
dimensions at once.** Across the 64 registered cross-sectional rows the
only gate windows ever run are `None` (32 rows), **100** (8) and **200**
(24) — SMA **50** never; and the only lookbacks ever run are **90** and
**180** — **120** never. Both were read out of the registry, not assumed.

Where 1.578665 sits:

| Reference | Ann. Sharpe |
|---|---:|
| **Ceiling, hindsight argmax over 39 020 arms** | **1.578665** |
| Gate-3 crossing, lowest of iteration 64's five shapes | 1.5814 |
| Gate-3 crossing, median of five shapes | 1.6294 |
| Gate-3 crossing, sixth shape (iteration 66, sleeve book) | 1.6905 |
| Best trial ever registered (trial 29, 75.08 % drawdown) | 1.410899 |
| Live contract, trial 118 | 1.241113 |
| Gate-4 bar at N=133 | 1.240607 |

**The raw margin is not the finding.** The ceiling is **0.173 % below**
the lowest crossing and 3.114 % below the median. A 0.17 % shortfall is
not a decisive margin and this document does not rest on it. What is
decisive is what happens when the ceiling arm is actually put through the
stop condition.

---

## 3. The ceiling arm against the stop condition

The mission's only success exit is **DSR ≥ 0.95 AND candidates-PBO ≤
0.05**. Both halves, measured on the ceiling arm as a 38th candidate
column, with the Sharpe variance recomputed across all 134 rows
(**1.654042e-04** against the recorded 133-row **1.584220e-04**):

| Gate | Bar | Ceiling arm | Verdict |
|---|---|---:|---|
| 4 — DSR at N=134 | ≥ 0.95 | **0.994802** (E[max] 0.033849) | **PASS** |
| 3 — candidates-PBO, 37 + 1 columns | ≤ 0.05 | **0.235120** | **FAIL, 4.70x the bar** |

**The stop condition is not reached at the ceiling.** No
`EDGE_CANDIDATE_FOUND.md` is written and none is warranted.

### 3.1 Gate 4 — and the self-referential closure

Holding the recomputed variance fixed and raising N, the ceiling arm
**survives to N = 17 113** and fails at 17 114:

| N | Meaning | DSR | Verdict |
|---:|---|---:|---|
| 134 | one new trial | **0.994802** | PASS |
| 2 113 | its own 1 980-arm grid | **0.977331** | PASS |
| 17 113 | last N it survives | **0.950000** | PASS |
| 17 114 | first N it fails | **0.949999** | FAIL |
| 18 931 | arms swept at the time of measurement | **0.948313** | FAIL |
| 39 153 | 133 + every valid arm swept today | **0.935112** | FAIL |

**The search that locates the ceiling is larger than the ceiling can
carry.** Finding the argmax of the engine's parameter space requires
searching that space, and the search costs more deflation than the argmax
is worth — **39 020** arms against a survivable **17 113**.

Stated fairly and against this loop's own interest: **this does not bind a
single lucky family.** An operator who ran only the 1 980-arm
cross-sectional grid would keep the gate-4 pass (0.977331), and one who
ran an eight-arm family that happened to contain this arm would keep it
easily. The N-argument binds the *program's total search*, not any one
family, and it is gate 3 — which does not depend on N at all — that
refuses the arm unconditionally.

### 3.2 Gate 3 — and the fourth recorded defect

The recorded 0.235120 decomposes over all 12 870 CSCV partitions:

| Quantity | Value |
|---|---:|
| Splits the ceiling arm wins in-sample | **0.759751** |
| Its OOS-below-median rate **on the splits it wins** | **0.063714** |
| Legacy 37 columns' OOS-below-median rate on the 0.240249 they win | **0.777167** |
| **The arm's own unconditional rate** | **0.048407** |
| Recorded verdict | **0.235120** |

Arithmetic check: 0.759751 × 0.063714 + 0.240249 × 0.777167 =
**0.235120**, to six decimals.

**The arm's own overfit rate is 0.048407 — below the 0.05 bar — and
0.186714 of the recorded 0.235120, i.e. **79.41 %** of the verdict, belongs to
37 columns the arm has nothing to do with.** This is the same structure
iteration 66 found for the sleeve book (own rate 0.020513, recorded
0.294794), reproduced here on the highest-Sharpe object the engine can
express, and it is the **fourth recorded gate-3 defect**. Today's
instance is the sharpest available: the pooled statistic and the
candidate's own statistic fall on **opposite sides of the bar**.

Two things must be said about that in the same breath.

**First, this loop declines the rule change.** Gate 3 is frozen until the
holdout is spent. Re-reading it on its candidate-only rate would convert
a fail into a pass in the one case where doing so favours the program,
which is precisely the move the mission forbids. Iteration 66 refused
exactly this and the refusal is repeated, on a stronger temptation.

**Second, the object is not an edge and must not be read as one.** It is
the argmax of a 39 020-arm hindsight sweep, selected on the same
2018-2025 window its 0.048407 is measured on; it has **zero forward
rows**; it carries **38.41 % drawdown**; it is 100 % in-sample; and its
own rate is itself pool-dependent — it is the rate the arm would record
against *this* 38-column pool, not an intrinsic property.

### 3.3 A corroboration of iteration 64, measured rather than assumed

Iteration 64 derived the ~1.63 crossing by adding a **constant daily
alpha** to five base shapes and called the result "a floor, not an
estimate", on the reasoning that constant alpha is the friendliest
possible improvement and a real strategy of different shape would need
at least that much. That caveat had never been tested against a real
arm. It is now: a real arm at **1.578665** records PBO **0.235120**,
where a constant-alpha arm near that Sharpe records close to 0.05. The
floor reading was correct, and the gap between the two is the cost of
changing shape rather than adding a constant.

---

## 4. Two secondary measurements, recorded because they were free

**The live contract is not the peak of its own architecture, and the peak
is close.** Within the 34 070 swept Donchian BTC/ETH arms, trial 118
sits at the **95.49th percentile**, trial 131 at the 93.91st, trial 88 at
the **85.01st**; **773** arms beat trial 118. The best is **1.333084**
(windows 20/25/30/130, `atr_channel`, ATR window 14, multiple 2, 29.87 %
drawdown), only **+7.41 %** over trial 118. This corroborates iterations
19-20's +14.2 % selection premium over the family median from a grid
four hundred times larger, and in the reassuring direction: the live
contract's parameters are not a lucky corner of their own space.

**The 13-coin Donchian architecture is nowhere near the bar.** Its 2 970
arms top out at **1.144485** (windows 5/10/16/25, `half_low`, 37.75 %
drawdown, 10.09x), with **0** arms at or above any crossing — below the
registry's own best and below every other grid swept today.

---

## 5. What this closes

**Route closed: no proposal may treat a new single-market parameter
family as a path to the stop condition.** The bound is the engine's own
expressible space, searched exhaustively over the cross-sectional grid
and the Donchian window space, and the best object it contains fails
gate 3 at 4.70x the bar while passing gate 4.

With this, **all three unblocking states named in
`AUTONOMOUS_RESEARCH_LOOP.md` are measured and none of them decides**:
forward validation (iterations 25, 59-62 — every October test is a
mechanism check), the holdout spend (iteration 63 — a near-coin-flip
whose subject changed on 2026-07-31), and the P3 override (today).

**What is NOT closed, and must not be confused with what is.** A new
*architecture* — new signal code, not a new parameter family — is outside
both P3 and this measurement. Nothing here says such a thing cannot
exist; it says the current engine cannot express it.

---

## 6. The three options this hands the operator

This is the **ninth** operator choice now due, and the fourth with no
deadline.

**Option A — accept the closure and stop searching.** All three levers
are measured and none can reach the stop condition. The program's
remaining honest activity is P1 maintenance and the accumulation of
forward rows toward 2028-06-29. Cost: the search ends without a
qualified candidate. This is the reading the loop recommends, and it is
the one the mission's own framing calls a valid outcome — "a registered
negative is a valid, publishable outcome".

**Option B — declare a candidate-only gate-3 reading, in advance, and
re-run every gate under it.** The fourth recorded defect is real: a
candidate whose own rate is 0.048407 is failed at 0.235120 for other
columns' behaviour. If the operator believes the pooled statistic is the
wrong instrument, the honest form is a **pre-declared rule change applied
to the whole registry at once**, before any candidate is scored under it,
with the 2026-07-25 report retained unchanged for comparison. Cost: it is
a rule change made after seeing which way it cuts, and this loop will not
make it. The only reason it is listed is that refusing to *tell* the
operator about a measured defect would be worse than refusing to act on
it.

**Option C — grant the P3 override anyway, for a product reason rather
than a search reason.** Nothing forbids running a new family to get a
better book; iteration 66 said the same of a fourth sleeve. The operator
should know it cannot reach the stop condition, that its winner would
carry the full selection premium of its grid, and that it adds K rows to
every future gate report's N. Cost: N, and a result that cannot qualify.

---

## 7. What this iteration did not do

No trial was registered and no arm nominated. **No backtest output was
written next to the registry**; the sweep lives entirely in the
gitignored `data/` tree. The holdout was **not read, not fetched and not
unsealed**; `spent` is still `false`. No gate rule was modified — in
particular **gate 3 was not repaired, re-read, or re-scored on its
candidate-only rate**, in the case where doing so would have converted
the program's best measured object from a fail into a pass. No frozen
pre-registration or contract clause was edited. No file under
`configs/runtime/`, `src/`, or any scheduled-task definition was touched.
No forward metric was computed and no forward number cited. Nothing in
this document may be cited as evidence that an edge exists.

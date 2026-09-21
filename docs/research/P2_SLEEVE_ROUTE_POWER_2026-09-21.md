# The P2 sleeve route cannot reach the stop condition — and the object it produces is the best thing this program has ever built, clears gate 4 at N=1195, and is scored by gate 3 for failures that are not its own — 2026-09-21 (iteration 66)

## 0. Why this measurement, and why now

Iterations 25 and 59-62 characterised the forward-validation lever, 63 the
October holdout, 64 the P3 override; iteration 65 completed the gates —
all six now measured. What that sequence never touched is the **queue**.

The loop's own queue (`AUTONOMOUS_RESEARCH_LOOP.md` step 3) has three
standing items: **P1** keep the forward tracks recording, **P2** a fourth
sleeve is permitted under the buy-and-hold and market-shopping guards, and
**P3** no new single-market parameter families. P1 is maintenance and P3
was measured on 2026-09-19. **P2 is the only queue item that is an action,
is permitted, is unmeasured, and has never been asked the one question the
mission turns on: can it reach the stop condition?**

That question has a precise form. The stop condition
(`AUTONOMOUS_RESEARCH_LOOP.md`, "Stop condition") is:

> a **full-registry gate report** shows a candidate with **DSR ≥ 0.95 AND
> candidates-PBO ≤ 0.05**

So P2 reaches it only if a sleeve book can (a) become a row of the trial
registry with a durable return series, and (b) clear both bars there.
Nobody has checked either. Note the asymmetry this document had to guard
against from the first line: unlike iterations 59-65, whose findings were
all defects, **this one had a live chance of producing a positive**, and a
quietly-rescued positive is the single forbidden result of an iteration.
Every number below is therefore reported with the objection that weakens
it, computed rather than acknowledged.

## 1. The answer to (a): the object is unregistrable, by construction

Four facts, each read from source today.

**1.1 There is exactly one production path into the registry.**
`append_trial` (`src/backtest/registry.py:89`) has **one** non-test caller
in the entire repository — `src/backtest/runner.py:129`, inside
`run_registered_backtest`. That function's signature
(`src/backtest/runner.py:45`) takes `candles_by_symbol` and
`parameters: BacktestParameters`; it runs **one** engine over **one**
universe and writes the return series from its own `report.equity_curve`
(`_write_trial_returns`, `src/backtest/runner.py:264`, called at `:188`).
**No code path accepts an externally computed equity curve.**

**1.2 The sleeve analyser says so itself.** `analyze_sleeve_combination.py`
states it in its docstring: *"Reads already-registered trial reports,
builds a daily-aligned equal-weight book rebalanced monthly, and evaluates
the pre-declared criteria. **Runs no backtest and registers no trial.**"*

**1.3 The registry is crypto-only, and two of the three sleeves live in a
different repository.** All **133** rows carry a crypto universe — **72**
rows on the 13-coin universe, **61** on `(BTCUSDT, ETHUSDT)` — across
**132** `daily_trend_ensemble` and **1** `confirmed_trend_ensemble`. The
Taiwan and gold sleeves are trials **23** and **24** of
`D:/TW-Stock-Trading/docs/reports/research/trial_registry.jsonl`, a
separate **24**-row registry (0050 Sharpe **0.426168** / mdd **0.3085**;
GLD **0.498551** / **0.2501**).

**1.4 Registering it as-is would not fail the gate — it would abort the
gate report.** `build_performance_matrix` (`scripts/run_gate_report.py:87`)
requires every series to share `(first_return_date, last_return_date,
length)` and raises `SystemExit` listing the discrepancies otherwise; the
docstring is explicit that this is deliberate ("A mismatch aborts with the
exact discrepancies instead of silently truncating to a flattering common
window"). The registry's 133 series are all **2018-03-05 → 2025-07-01,
2676** returns (verified: consecutive calendar days). The three-sleeve
book's common window is **2018-03-06 → 2025-07-01, 2675** days (also
consecutive) — **exactly one day short**, because the gold and Taiwan
series start a day later. A naive registration therefore breaks **every
future gate report**, for all 134 rows, until removed.

**Conclusion on (a): P2 produces an object that no gate report in this
repository can ever see.** Not because it is bad — because nothing
connects it to the registry. This alone closes P2 against the stop
condition as the machinery stands.

## 2. The answer to (b), computed anyway — because (a) is a 20-line fix

An operator could obviously write the missing path, so "unregistrable"
would be a cheap closure to stop at. The rest of this document answers
what the gates would say if it were registered. The alignment used
throughout is the only honest one available: the registry columns are
truncated by their **first** row (2018-03-05), giving 2675 rows that match
the book's window exactly, date for date.

**Method validation, first.** Every PBO below comes from a vectorised
reimplementation of `probability_of_backtest_overfitting`. On the recorded
inputs it reproduces the 2026-07-25 gate report **exactly**: candidates
**0.651826** and all-columns **0.732556**, both to six decimals, at
12 870 combinations and 2672 usable rows. The candidate set it builds is
identical to the recorded `candidate_trial_ids` (**37** columns). DSR
values come from `src.backtest.deflated_sharpe_ratio` unmodified.

### 2.1 The book itself

| | Sharpe (ann.) | max drawdown | multiple |
|---|---:|---:|---:|
| three-sleeve book, 1/3 each, monthly | **1.410785** | **14.8988%** | 3.9396× |
| registry best ever (trial 29) | **1.410899** | **75.08%** | — |
| trial 37 | 1.243142 | 67.53% | — |
| trial 118 (live contract) | 1.241113 | 33.24% | — |
| trial 88 (crypto sleeve alone, this window) | 1.182927 | 33.05% | 14.26× |

Reproduced from `python -m scripts.analyze_sleeve_combination` (Sharpe
1.4108, mdd 0.1490, 3.94× — matching `SLEEVE3_GOLD_RESULT.md` and the
contract's standing answer), then recomputed at full precision.

**The book is the second-highest Sharpe this program has ever produced,
short of the best by 0.000114 — 0.0081% — at one fifth of its drawdown.**
That near-tie is a coincidence of two unrelated computations and is
reported as such; what is not coincidence is the drawdown column.

### 2.2 Gate 4 (DSR ≥ 0.95): **PASS**, and robustly

Computed the way `run_gate_report.py` would: the book's annualized Sharpe
is appended to the 133 registry Sharpes, the variance is recomputed across
all 134 (**1.616543e-04**, against the recorded **1.584220e-04** at
N=133), and `effective_trials` becomes **134**.

- **DSR = 0.981583**, E[max Sharpe] = 0.033463, on 2675 observations.
- Holding that variance fixed and raising N by iteration 55's method, the
  book **survives to N = 1195** and fails at **1196**.

Against the three recorded gate-4 passes:

| | DSR | ann. Sharpe | max drawdown | survives to N |
|---|---:|---:|---:|---:|
| trial 29 | 0.986670 | 1.410899 | 75.08% | 2130 |
| **sleeve book** | **0.981583** | **1.410785** | **14.90%** | **1195** |
| trial 37 | 0.952424 | 1.243142 | 67.53% | 149 |
| trial 118 | 0.950140 | 1.241113 | 33.24% | 134 |

Iteration 55's structural finding was that *"the statistically robust part
of this registry is the part no human could sit through, and the part a
human could sit through sits at or below the DSR bar."* **The sleeve book
is the first object measured in this program that breaks that trade-off:**
nine times the registry's N of statistical robustness at the **lowest**
drawdown of anything listed.

**The N objection, computed rather than waved.** The book's crypto sleeve
*is* trial 88 — itself the survivor of a 133-trial search — and its other
two sleeves were selected inside a separate 24-row registry, so N=134
understates the search behind it. Measured across the range:

| effective N | rationale | DSR | |
|---|---|---:|---|
| 134 | registry + this column | 0.981583 | PASS |
| **157** | **every registered row behind all three sleeves (133 + 24)** | **0.979936** | **PASS** |
| 500 | arbitrary stress | 0.964940 | PASS |
| 1195 / 1196 | the breaking point | 0.950004 / 0.949988 | PASS / FAIL |
| 3192 | multiplicative view (133 × 24) | 0.929199 | FAIL |
| 10000 | — | 0.899717 | FAIL |

So gate 4's verdict survives every additive accounting of the real search
and fails only under the multiplicative one. **Which is correct is a
judgement this loop does not get to make** — it is an `effective_N` method
choice, and iteration 27 already established that the operator must
declare such a method **before** it is computed. Recorded here as an open
question, not resolved in the direction that flatters.

### 2.3 Gate 3 (candidates-PBO ≤ 0.05): **FAIL** — and not for the book's reasons

- **PBO with 38 columns (37 candidates + the book) = 0.294794**, against a
  bar of 0.05. **FAIL, by 5.90×.**
- Control, the same 37 candidates alone on the same 2675-row window:
  **0.629526** (the recorded 0.651826 is the same 37 columns on 2676).

So adding the book **more than halves the registry's recorded overfit
probability** — and still fails. Decomposing all 12 870 splits by who wins
in sample:

| | splits | share | of those, OOS-below-median |
|---|---:|---:|---:|
| the book is the in-sample winner | 8 019 | 62.31% | **264 → 3.2922%** |
| a legacy column is the winner | 4 851 | 37.69% | 3 530 → **72.7685%** |
| **total** | 12 870 | | **0.294794** |

And the book's **own** unconditional rate — iteration 64's
"maximally-dominant column" quantity, the OOS-below-median frequency it
would record if it were the in-sample winner in every split — is
**0.020513**. **Below the bar.**

**This is a third recorded defect of gate 3, and it is the mirror image of
iteration 64's.** PBO is a property of the **selection process over the
whole matrix**, not of a candidate; a candidate whose own overfit rate is
**0.020513** is recorded as **0.294794** because of 37 columns it has
nothing to do with, and no amount of improvement in the candidate can
retire more than its in-sample-win share of the pool's 72.77%. Iteration
64 found that gate 3 hands a verdict to a family's *last-registered* arm
rather than its best; this is the same failure of attribution one level
up. Both are recorded. **Neither may be repaired by this loop** — changing
gate 3 after seeing a result it produced is the exact move the contract
refuses by design, and it is refused here in the one case where the change
would be favourable.

### 2.4 How much better would it have to be?

By iteration 64's own method — bisect a constant per-day alpha added to
the series and recompute the full 38-column PBO at each step — the
crossing for **this** shape is:

- alpha **0.00010693/day**, i.e. annualized Sharpe **1.6905**, where
  PBO = **0.049728** and the book becomes the in-sample winner in
  **94.61%** of splits.

Iteration 64 measured the same crossing for five other base shapes at
**1.5814 / 1.6253 / 1.6294 / 1.6993 / 1.7857** (median 1.6294). **The
sleeve-book shape is the sixth and it lands inside that range**, just
above the median — so this route does **not** escape the ~1.63 bar; it
corroborates it from a new direction. The book is short by **0.2797** of
annualized Sharpe, and **0 of 133** registered trials reach even 1.5814.

### 2.5 The version that is admissible under the current rule

The three-sleeve book contains a sleeve the program's **own** P2 rule
would now refuse. P2 requires a sleeve to "beat buy-and-hold in its own
market on at least one of return or Sharpe", and on the common window
(`VS_BUY_AND_HOLD_2026-07-26.md:27-34`) the gold sleeve returns **1.51×**
against buy-and-hold gold's **2.46×** at Sharpe **0.6432** against
**0.9012** — it loses **both**. Taiwan passes, on Sharpe (**0.9816** vs
**0.8559**) though not on return. **So the best object this program has
ever built contains a component its current admission rule forbids**, and
the rule postdates the build.

The admissible two-sleeve book (crypto + Taiwan) was therefore measured
too, and the finding is **not** confined to the inadmissible object:

| | ann. Sharpe | mdd | DSR (N=134) | survives to N | PBO (38 cols) | IS-win share |
|---|---:|---:|---:|---:|---:|---:|
| 3-sleeve | 1.410785 | 14.90% | **0.981583** | 1195 | 0.294794 | 62.31% |
| **2-sleeve (P2-admissible)** | 1.343746 | 19.73% | **0.972597** | **497** | 0.379565 | 50.92% |

Same verdict, same structure, one third the N-robustness: **gate 4 passes,
gate 3 fails on the pool.**

## 3. What this does and does not establish

**Established.**

1. **P2 cannot reach the stop condition.** Its output is unregistrable by
   every production path in this repository (§1), and if registered it
   fails gate 3 at **0.294794** (§2.3), 5.90× the bar.
2. **The failure is not attributable to the object.** The book's own
   overfit rate is **0.020513**; **72.7685%** of the recorded failure
   belongs to the 37 legacy columns, in the 37.69% of splits where one of
   them wins.
3. **Gate 4 is passed, at the lowest drawdown in the program**, and under
   every additive accounting of the real search (N=157 → **0.979936**).
4. **The ~1.63 gate-3 crossing survives a sixth, structurally different
   base shape** (**1.6905**), so it is a property of this matrix rather
   than of the five shapes iteration 64 happened to pick.

**Not established, and explicitly not claimed.**

5. **This is not an edge, and nothing here is forward evidence.** The book
   has **zero** forward rows: no sleeve-book shadow track exists — the four
   recording tracks are trial 88, trial 118 (crypto, daily) and 0050, GLD
   (weekly), none of which is the combined book. Its MinTRL against
   SR* = 0 at 95% one-sided, on its own moments (daily SR 0.073844,
   skew 0.1898, kurtosis 11.6409), is **497.4 days** — so even a track
   started today could not speak to return before **2028-01**.
6. **The DSR pass may be an artifact of additive N.** §2.2 records the
   multiplicative accounting that fails (0.929199) and does not choose
   between them. The choice is the operator's, declared before computing.
7. **The book is 100% in-sample**, over the same 2018-2025 window as
   everything else, and its crypto sleeve carries trial 88's full
   selection premium.
8. **Nothing here contradicts the standing answer's headline.** Timing
   still adds value in crypto only; the sleeve book's 3.94× is still
   **less money** than holding the same three assets equally (5.42×,
   `VS_BUY_AND_HOLD_2026-07-26.md:44-45`). What it buys is drawdown and
   Sharpe, which is exactly what iteration 18 concluded and what §2.1
   re-measures at higher precision.

**Nothing was repaired and nothing frozen was edited.** No registration
path was written, no gate rule modified, no sleeve registered, no
pre-registration authored, no trial run, no gate report regenerated, no
holdout touched, no forward file written or read for a metric, no new
script created.

## 4. Three options for the operator

**(A) Leave P2 as it is, and record that it is decorative.** The queue
keeps recommending an action that cannot reach the mission's only success
exit. Cost: the next iteration that follows the queue honestly spends
itself building a fourth sleeve whose gate verdict is already known —
**0.294794 on a pool it cannot influence**, no matter how good the sleeve
is. Benefit: nothing frozen changes, and the queue's provenance stays
intact.

**(B) Write the missing registration path for combined books.** The gap is
small — accept an externally computed, date-stamped equity curve, write
the `trial_returns` series, append the registry row — and it would let the
program's best risk-adjusted object be graded at all. Cost, and it is the
real one: **the book's window is one day short of the registry's**, so
either the book is recomputed on 2018-03-05 (it cannot be — the gold and
Taiwan series do not start until 2018-03-06) or the registry's alignment
rule is relaxed, and relaxing it is a change to the input of every gate
report ever produced. This is a **rule change and must be declared before
the object it governs is registered**, per iteration 27's `effective_N`
precedent and iteration 64's anti-dilution precedent.

**(C) Accept that gate 3 cannot score a candidate, and declare what
replaces it — before computing anything.** The defect in §2.3 is not
repairable by tuning: a clean candidate inherits the pool's failure by the
statistic's own definition. The honest alternatives are to score the
candidate's **own** OOS-below-median rate (the book: **0.020513**), or to
fix the pool (iteration 56 measured that repairing the candidate key to
the full 111-column parameter set gives **0.799145** — worse), or to state
that gate 3 measures the registry and not the candidate and stop reading
it as a verdict on a trial. **All three are rule changes, and declaring
one after reading this document is the change-the-rules-after-seeing-
results failure the gate contract forbids.** It is named here precisely so
that the operator can see the loop declining to make the change that would
favour it.

Nothing here is a recommendation the loop may act on. All three require
the operator. **(A) has no deadline; (B) and (C) are rule changes and must
precede any registration or any re-reading of gate 3.**

## Appendix — reproducing every number

No new script was written (the one-script budget is unspent for the sixth
iteration running). The measurement is this, run from the repository root
against the committed tree:

```python
import json
from itertools import combinations
from pathlib import Path
import numpy as np
from src.backtest import (load_trials, deflated_sharpe_ratio,
                          non_annualized_sharpe_variance)
import scripts.run_gate_report as gr
from scripts.analyze_sleeve_combination import (
    daily_returns, common_window, combine_monthly_rebalanced, sharpe, max_drawdown)

def pbo_np(M, block_count=16):
    """Vectorised equivalent of probability_of_backtest_overfitting.
    Validated: reproduces the 2026-07-25 gate report's 0.651826 (candidates)
    and 0.732556 (all columns) exactly."""
    T, N = M.shape
    usable = T - (T % block_count); bs = usable // block_count
    X = M[:usable].reshape(block_count, bs, N)
    S1, S2 = X.sum(1), (X ** 2).sum(1)
    tot1, tot2 = S1.sum(0), S2.sum(0); n = usable // 2
    over = wins = cond = 0
    combos = list(combinations(range(block_count), block_count // 2))
    for tr in combos:
        i = list(tr)
        a1, a2 = S1[i].sum(0), S2[i].sum(0); b1, b2 = tot1 - a1, tot2 - a2
        def sh(s1, s2):
            m = s1 / n; v = (s2 - n * m * m) / (n - 1)
            sd = np.sqrt(np.maximum(v, 0.0))
            return np.where(sd > 0, m / np.where(sd > 0, sd, 1.0), 0.0)
        ts, es = sh(a1, a2), sh(b1, b2)
        b = int(np.argmax(ts))
        bad = int((es <= es[b]).sum()) / (N + 1) <= 0.5
        if b == N - 1: wins += 1; cond += bad
        over += bad
    return over / len(combos), wins / len(combos), cond / max(wins, 1)

crypto = daily_returns(Path("docs/reports/backtests/trial-000088/report.json"))
tw     = daily_returns(Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000023/report.json"))
gold   = daily_returns(Path("D:/TW-Stock-Trading/docs/reports/backtests/trial-000024/report.json"))
days   = common_window([crypto, tw, gold])                      # 2018-03-06..2025-07-01, 2675
book   = np.asarray(combine_monthly_rebalanced(days, [crypto, tw, gold]), float)

trials = load_trials(Path("docs/reports/research/trial_registry.jsonl"))
cands  = gr.candidate_trials(trials)                            # 37, == recorded ids
ser = lambda t: np.asarray(json.load(open(
    f"docs/reports/research/trial_returns/trial-{t:06d}.json"))["daily_returns"], float)
C = np.column_stack([ser(t.trial_id)[1:] for t in cands])       # drop 2018-03-05 -> 2675 rows

print(pbo_np(C)[0])                                # 0.629526  (control)
print(pbo_np(np.column_stack([C, book])))          # 0.294794, 0.623077, 0.032922

ann  = [float(t.metrics["annualized_sharpe"]) for t in trials]
var  = non_annualized_sharpe_variance(ann + [float(sharpe(list(book)))])   # 1.616543e-04
print(deflated_sharpe_ratio(list(book), trial_sharpe_variance=var,
                            effective_trials=134).deflated_sharpe_ratio)   # 0.981583
```

The §2.4 crossing is a 14-step bisection of `alpha` in `[0, 0.004]` on
`pbo_np(np.column_stack([C, book + alpha]))` against 0.05; the §2.3
unconditional rate replaces `int(np.argmax(ts))` with the book's own
column index; the §2.2 N-sweep bisects `effective_trials` at fixed `var`.

## Sources consulted (iteration 66, recorded in `RESEARCH_LOG.md`)

- **vinilpolepalli/quantfirm PR #75** — an independent campaign whose
  round-2 sleeve scored standalone Sharpe **1.028**, correlation
  **−0.156** to its core book, blend Sharpe **1.694**, P(blend beats core)
  **0.947**, and was still refused by a trial-level deflated Sharpe of
  **0.695** against a 0.95 bar. The same asymmetry as §2.3, reached from
  the opposite side. Used for **corroboration of structure only**; no
  number imported.
- **yuyank-code/bitcoin-ml-trading issue #54** — a **negative** external
  result: the most complete external DSR/PBO/SPA/MinTRL gate specification
  the search returned states **no numeric thresholds** and contains **no
  language about applying these gates to combinations**, which is exactly
  the gap §1 measures here.
- **Wataru1987/gmo-coin-trend-lab** — a product-law-compliant near-miss
  (daily, spot, long-only, 5 bp/side) rejected as **already registered**:
  its mechanism is trial 118's, and its honest walk-forward OOS Sharpe
  **0.85** is below both this registry's best (1.410899) and §2.4's
  crossing (1.6905).
- **arXiv 2201.06635**, Valeyre, 2022-01-17 — fetched for an external
  sleeve-scaling anchor; the abstract carries none and the PDF returned
  binary. **No number imported**, and §2.4's crossing is therefore
  measured locally with no outside corroboration.

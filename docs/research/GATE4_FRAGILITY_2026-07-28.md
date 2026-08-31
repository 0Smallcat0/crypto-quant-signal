# Gate 4's only pass exists only if the search stops

Date: 2026-07-28 (iteration 26) · Registry N=133 · Zero registry cost
(re-analysis of existing return series; no backtest run, no trial
registered).

## The question

Trial 118 is the program's single gate-4 pass, at DSR **0.950140**
against a 0.95 bar — a margin of 0.00014. A margin that thin is either a
technicality worth ignoring or a structural fact worth acting on. This
measures which.

## Two hypotheses tested first, both refuted

Before drawing any conclusion from the margin, the two ways it could be
**dishonest** were checked. Neither holds.

**H1 — the true trial count is higher than 133, because arms were
evaluated but never registered.** Refuted. Registry composition by
experiment: exp-1 1, exp-2 through exp-6 16 each, exp-7 through exp-10
8 each, 20 unlabelled early rows, total 133. `LOOP_LOG.md:126` records
"64 **registered** cs-momentum arms", which is exactly exp-3 through
exp-6 at 16 apiece. Both robustness batteries are registered too —
trials 102-109 (trial 88) and 126-133 (trial 118), marked
never-nominatable. **No evaluated configuration is missing from the
count.**

**H2 — the pass is an artefact of trial 118's own robustness battery
compressing cross-trial variance.** This was the stated reason an
advance prediction failed on 2026-07-25 ("the clustered battery arms
compressed cross-trial variance as fast as the bar rose"), so it was a
live suspicion that the winner had been rescued by arms run on the
winner. Refuted, and in the opposite direction:

| Registry used | N | variance | trial 118 DSR | |
|---|---:|---:|---:|---|
| as recorded | 133 | 0.00015842 | 0.950140 | PASS |
| minus trial 118's own battery (126-133) | 125 | 0.00016033 | **0.950514** | PASS |
| minus trial 88's battery (102-109) | 125 | 0.00016071 | 0.950304 | PASS |
| minus both batteries | 117 | 0.00016177 | **0.951257** | PASS |

Removing the batteries makes trial 118 score **higher**, not lower. The
N reduction outweighs the variance increase. **The pass is not
self-served. It is honest.**

## What the margin actually is

It is one trial.

| N | trial 118 DSR | |
|---:|---:|---|
| 133 | 0.950140 | PASS |
| **134** | **0.949969** | **FAIL** |
| 140 | 0.948963 | FAIL |
| 200 | 0.940346 | FAIL |
| 400 | 0.921482 | FAIL |

A 134th trial does not only raise N; it also shifts the cross-trial
Sharpe variance, and that can cut either way. So the honest question is
not "does one more trial break it" but **"is there any 134th trial that
does not break it"**. Sweeping the new trial's annualized Sharpe:

| 134th trial's Sharpe | trial 118 DSR | |
|---:|---:|---|
| -1.00 | 0.899062 | FAIL |
| 0.00 | 0.940088 | FAIL |
| 0.50 | 0.948382 | FAIL |
| **0.95** (registry mean 0.9444) | **0.950626** | **PASS** |
| 1.00 | 0.950591 | PASS |
| 1.1823 (= trial 88's Sharpe) | 0.949988 | FAIL |
| 1.2413 (= trial 118's own Sharpe) | 0.949630 | FAIL |
| 2.00 | 0.937298 | FAIL |

**The surviving window is Sharpe in [0.709, 1.180], width 0.471.** The
registry's own Sharpe mean, 0.9444, sits inside it. **Trial 118's Sharpe
of 1.2413 does not. Trial 88's 1.1823 does not.**

## The statement that follows

**If the next experiment discovered a strategy as good as either of the
two the program already shadows, trial 118's gate-4 pass would be
destroyed by the discovery.** So would a strategy notably worse
(Sharpe <= 0.708). Only a 134th trial that lands close to the registry
average preserves the pass.

**This is not a defect in the Deflated Sharpe Ratio.** DSR asks whether
the best of N searched configurations beats what the best of N noise
draws would produce. More search, and more spread among what was
searched, legitimately raises that bar. The arithmetic above is DSR
working exactly as intended.

**The defect is in how this program has been reading it.** "Trial 118
passes gate 4" has been recorded and quoted as a durable property of
trial 118. It is not. It is a property of **the search that produced
it**, and it holds only while that search stays at 133 trials. Restated
correctly:

> Trial 118 clears gate 4 **with respect to a search of 133
> configurations that has stopped.** The pass does not survive the search
> continuing, except in the narrow case where the next thing found is
> mediocre.

## The decision this forces on the operator

The standing order governing this program is **"沒有找到 edge 不准停"**
— do not stop until an edge is found. The queue's standing decision since
2026-07-25 is **"no new families,"** adopted because "the margin (0.0001
at N=133) cannot absorb one."

Those were treated as a pause. They are not a pause. Measured, they are
**mutually exclusive**:

- **Keep the gate-4 pass** => the crypto registry is frozen at 133
  forever. No exp-11, no new family, no new arm. The search is not
  paused, it is **over**, and what the program has is one candidate that
  passed a stopped search and has zero forward validation until
  2028-06-29 (`FORWARD_TRACK_READ_PREREGISTRATION.md`).
- **Keep searching** => accept in advance that trial 118's gate-4 pass is
  forfeit the moment anything interesting is registered, and that gate 4
  will then have **zero** passing risk-compliant trials, exactly as it
  did for the first 117.

### A third option exists, and this program has refused it in advance

The result above is exactly true **under this program's own N
convention**, which is the raw registry count.
`scripts/run_gate_report.py:188` states it deliberately: "Conservative:
raw registry count, no correlation shrinkage — a larger N only raises
the expected-max bar."

The DSR literature does not prescribe that convention. Bailey and López
de Prado's variable is the number of **independent** trials, and the
standard caution is that a raw backtest count **overstates** the breadth
of a search, because the variations executed are highly correlated with
one another. This registry is a textbook case: nine distinct
architectures measured at mean pairwise correlation **0.628**
(`PBO_SCOPE_DIAGNOSTIC_2026-07-26.md`), and 64 of the 133 rows are arms
of a single cs-momentum lineage.

So a correlation-adjusted effective N would be **materially below 133**,
trial 118's DSR would be **higher** than 0.950140, and the one-trial
margin would be looser than measured here. That is a genuine counterweight
and it is recorded as such: **the fragility above is a property of the
conservative convention, not only of the strategy.**

It is nonetheless **not available as a fix**. Switching to
correlation-adjusted N now would be changing a gate's input after seeing
that the current input produces an inconvenient answer — the identical
move the program refused over gate 3 when PBO was found to misrank
(`AUTONOMOUS_RESEARCH_LOOP.md`, exhausted-state table, "Revising gate 3
after finding it misranks ... Refused by design, even though the defect
is real and recorded"). The same refusal applies here, and applies more
strongly because the change would be self-serving in a measurable
direction.

If the operator wants that convention, the honest route is to declare it
**before** the October holdout is spent and to state plainly that it
loosens the bar, not to adopt it silently because it rescues a margin.

Setting that aside: there is no option in which the program both
continues to search in crypto under the frozen convention and keeps its
one gate-4 pass, unless every future trial is mediocre.

**This document does not choose.** Gate rules stay frozen until the
holdout is spent (`PRE_HOLDOUT_PROTOCOL.md` section 1), and choosing
between these is the operator's call, not the loop's. What the loop can
say is that the choice exists, is forced, and has until now been
invisible because the margin was described as "thin" rather than counted.

## Addendum 2026-07-28 (iteration 27) — correction to this document, and a gate audit

### Correction: the effective-N adjustment is mandated, not a rule change

The section above says adopting correlation-adjusted N "would be changing
a gate's input after seeing that the current input produces an
inconvenient answer." **That framing is wrong, and it is corrected here
the same day.**

`VALIDATION_GATE_CONTRACT.md` — frozen, written before any of these
results — already requires it. Gate 1, line 44:

> `effective_N` for DSR **should account for correlation between trials**
> (near-identical variants do not count as fully independent); **the
> method used must be recorded alongside the number.**

and line 75 lists gate 4's inputs as the Sharpe variance across
registered trials **and `effective_N`** — not the raw count.

So correlation adjustment is not a post-hoc loosening. It is the frozen
contract's own specification, and `scripts/run_gate_report.py:190`
passing `trial_count = len(trials)` is a **deviation from the contract**,
conservative on the N axis and undocumented as to method. The report
records `effective_trials: 133` and no method, which does not satisfy
"the method used must be recorded alongside the number."

**Consequence for trial 118, stated carefully:** its gate-4 pass was
earned under a bar at least as strict as the contract requires, and
probably stricter. That is a point in its favour, not against it.

### What is genuinely post-hoc is the method, and the direction is unknown

Three standard methods exist for the effective count — ONC clustering,
hierarchical clustering, and spectral/eigenvalue treatment of the
correlation matrix. Choosing among them **now**, knowing trial 118 sits
at 0.950140, is where the post-hoc risk actually lives.

More importantly, proper compliance is **not** simply "use a smaller N".
The prescribed procedure clusters correlated trials into K independent
groups, forms an aggregate Sharpe per cluster, and takes the variance
across **those K Sharpes** — so it changes *both* gate-4 inputs, and a
variance computed across K cluster aggregates can be larger or smaller
than the variance across 133 individual trials. **The net effect on
trial 118 is therefore unknown and must not be assumed favourable.**
This document does not compute it, because computing it requires picking
a method, and picking a method after seeing the margin is the one move
that would make the answer untrustworthy.

**The clean route** is for the operator to declare the method before it is
computed, and to record it, as gate 1 already demands. Until then the
raw count stands, and the one-trial margin measured above stands with it.

### Gate audit: which gates have ever adjudicated anything

Prompted by the above, all six were checked against the latest report
(`gate_report_2026-07-25.json`, N=133) and the contract:

| Gate | What it is | Has it ever decided a candidate? |
|---|---|---|
| 1 Trial registry | Process discipline — append-only, `effective_N` method recorded | No. It is a precondition. **And it is currently not fully satisfied** — no method is recorded. |
| 2 Data floor | >= 1000 daily observations | **No, and it cannot.** Every trial shares one 2676-day window, so it returns `passes: true` for all 133 by construction. Cleared 2.7x over before trial 1. |
| 3 PBO <= 0.05 | CSCV over candidate columns | **Yes — it rejects everything.** 0.6518 candidates / 0.7326 all-columns. |
| 4 DSR >= 0.95 | Deflated Sharpe | **Yes — one passer** (trial 118), on the margin measured above. |
| 5 Single-use holdout | Operator-only, single-use | No. Never executed; nominations fixed for October. |
| 6 Paper trading >= 3 months | Live signal runtime | No. `GATE6_BASELINE_2026-07-25.md` checklist item "Paper period >= 3 calendar months completed" is **unchecked**. |

**Of six gates, two have ever produced a verdict on a candidate.** Gates
1 and 2 are preconditions rather than filters; gates 5 and 6 lie ahead,
not behind. That is not a defect on its own — a pipeline whose later
stages have not run is normal. What matters is the combination with what
is already recorded:

- **Gate 3, the only gate that has ever rejected anything, misranks.**
  It would call exp-3 (2 of 8 members with any edge) safer than exp-7
  (8 of 8), because PBO tracks dispersion rather than edge
  (`PBO_SCOPE_DIAGNOSTIC_2026-07-26.md`, iteration 22).
- **Gate 4, the only gate that has ever passed anything, holds only for a
  search that has stopped** (this document, iteration 26).

**So the entire discriminating power exercised in 133 trials rests on two
gates, and both have documented defects.** Neither defect is being fixed,
correctly — rules stay frozen until the holdout is spent. But no document
should describe this program as having "survived six gates". Nothing has
survived them: gate 3 fails, and gates 5 and 6 have not been attempted.

## Relation to the gate-3 finding

Iteration 22 recorded that gate 3 (PBO) **misranks**: it would call
exp-3, where only 2 of 8 members have any edge, safer than exp-7, where
all 8 do, because PBO measures dispersion rather than edge. This is a
second gate whose output moves for reasons unrelated to whether the
strategy works — here, gate 4's verdict on an existing candidate is
changed by what gets searched **afterwards**.

Both findings are recorded, neither changes a frozen rule, and both
belong in front of the operator before the October holdout is spent.

## What does not change

- No gate rule is modified. Gate 3 and gate 4 stay frozen.
- Trial 118's recorded gate-4 pass at N=125 and N=133 stands exactly as
  registered. Nothing here retracts it; it qualifies what it means.
- The holdout is untouched, nominations stay fixed.
- No trial registered, no backtest run, no `configs/runtime/` touched.

## Method note

Computed with the program's own `deflated_sharpe_ratio` and
`non_annualized_sharpe_variance` (imported, not reimplemented), against
`docs/reports/research/trial_registry.jsonl` (133 rows) and
`trial_returns/trial-000118.json` (n=2676). The hypothetical-134th-trial
sweep varies only the new trial's annualized Sharpe, which is the only
input a new row contributes to gate 4 besides the count itself.

---

## Addendum 2026-08-31 (iteration 55) — this document's own premise is wrong: gate 4 passes three trials, not one, and the robust pass is not fragile at all

Zero registry cost (re-analysis of existing return series with the
program's own functions; no backtest run, no trial registered, no gate
rule touched).

### The correction

This document's title and its opening sentence — "Trial 118 is the
program's single gate-4 pass" — are **false against the very report they
cite**. `docs/reports/research/gate_report_2026-07-25.json` (N=133, the
latest report, unchanged since) marks `passes_dsr: true` on **three**
trials:

| Trial | Annualized Sharpe | DSR at N=133 | Max drawdown | Family verdict |
|---:|---:|---:|---:|---|
| 29 | 1.410899 | **0.986670** | **75.08%** | exp-3 winner; family MDD bar 51.93%, missed by 23.15pp |
| 37 | 1.243142 | **0.952424** | **67.53%** | exp-3 member; same bar, missed by 15.60pp |
| 118 | 1.241113 | **0.950140** | 33.24% | exp-10 winner; **all three frozen criteria pass** |

The correct sentence is the one `GOALP_EXPERIMENT10_RESULT.md` already
wrote on 2026-07-25, three days before this document: trial 118 is "the
first trial in the registry's history to clear the gate-4 deflation bar
while ALSO being risk-compliant (trials 29 and 37 clear DSR at 75.1% and
67.5% drawdown, which fails the risk bar by 23pp and 16pp; they qualify
nothing)". `LOOP_LOG.md` recorded the same thing even earlier, at
iteration 9: "trial 37 became the registry's SECOND gate-4 pass".

So nothing about the registry was ever unknown. What happened is a
**documentation regression**: a correct, qualified statement lost its
qualifier when it was carried into this document, and the unqualified
version then propagated into roughly twenty `LOOP_LOG.md` entries and
into the standing answer's iteration-27 refinement ("gate 4 passes one
trial"). Same failure mode as the pooling error retracted on 2026-07-26
and again on 2026-07-28 — an inherited half-sentence, not a bad
measurement.

The original text above is **not rewritten**; it is corrected here, as
the loop contract requires.

### What the correction changes — the fragility is trial-118-specific, not gate-4-specific

Applying this document's own method (registry Sharpe variance held at the
recorded `0.00015842198033849873`, N raised, everything else fixed) to
all three passes gives the number nobody had computed:

| Trial | Highest N that still passes | DSR there | First N that fails | DSR there | Headroom vs today's N=133 |
|---:|---:|---:|---:|---:|---:|
| 29 | **2130** | 0.950008 | 2131 | 0.949999 | **16.0x** |
| 37 | **148** | 0.950018 | 149 | 0.949864 | 1.11x |
| 118 | **133** | 0.950140 | 134 | 0.949969 | **1.00x** |

Method identical to the table in "What the margin actually is" above, and
it reproduces that table to the digit (N=140 → 0.948963, N=200 →
0.940346, N=400 → 0.921482).

Therefore this document's headline — "gate 4's only pass exists only if
the search stops" — **cannot stand as a statement about gate 4**. Gate 4
holds a pass that would survive roughly **two thousand** trials: about
sixteen times the entire search to date. What is one-trial fragile is
specifically **the only pass the program would be willing to trade**.

### The sharper statement that replaces it

The binding constraint was never gate 4 alone. It is the **conjunction**
of gate 4 and the families' own frozen drawdown bars, and in this
registry those two are pulling in opposite directions at the top of the
ranking:

- The DSR-robust region (trials 29 and 37, DSR headroom 16.0x and 1.11x)
  is **entirely outside** the risk-compliant region — 75.08% and 67.53%
  drawdown against a 51.93% bar.
- The risk-compliant frontier (trials 118 at 33.24%, 131 at 29.93%, 106
  at 29.69%, 88 at 33.05%) sits **at or below** the DSR bar, with 118 at
  it by 0.00014 and the rest under it.

So "the search is over" survives the correction, but its reason changes
from a statistical near-miss at N=133 to something structural: **the part
of this registry that is statistically robust is the part a human could
not sit through, and the part a human could sit through is not
statistically robust.** That is a stronger claim than the original and it
does not depend on the exact value of N.

### Guard against the over-reading this invites

The pattern above is **local to the top of the ranking and must not be
generalized into "DSR rewards risk"**. Measured across all 133 registered
trials, annualized Sharpe and maximum drawdown are **negatively**
correlated — Pearson **-0.4276**, Spearman **-0.6789** — i.e. registry-wide,
higher Sharpe generally comes with *lower* drawdown, the opposite
direction. The inversion is confined to the two exp-3 cross-sectional
momentum arms, which bought their Sharpe with drawdown no other family
tolerated. Anyone citing this addendum as evidence that the deflated
Sharpe ratio systematically favours risky strategies would be citing it
against its own numbers.

One further observation, recorded as previously-known rather than new:
none of the three gate-4 passes is a **gate-3 candidate column** in the
same report, while robustness trial 131 (explicitly never-nominatable) is.
That follows from the incomplete `PRE_HOLDOUT_PROTOCOL.md` §1 dedupe key
already recorded as a defect in `GOALP_EXPERIMENT3_RESULT.md`; it is not
a new finding and nothing here rests on it.

### Stop-condition check

Unchanged and negative. The loop's stop condition requires **DSR ≥ 0.95
AND candidates-PBO ≤ 0.05**. Three trials now visibly meet the first;
candidates-PBO is **0.651826** (all-columns 0.732556), so the second
fails by an order of magnitude. **No `EDGE_CANDIDATE_FOUND.md` event.**

### What this addendum does not do

No gate rule modified, no frozen pre-registration edited, no registry row
touched, no result document rewritten, no trial registered, no backtest
run, no gate report regenerated, holdout untouched, no new script written.
Trial 118's recorded pass at N=125 and N=133 stands exactly as registered.

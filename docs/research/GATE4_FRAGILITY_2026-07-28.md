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

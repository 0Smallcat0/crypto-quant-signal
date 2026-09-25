# Is gate 3's verdict purchasable? — iteration 69, 2026-09-25

**Status: measurement, complete. Nothing registered, nothing repaired, nothing
frozen edited.** N is still 133, no gate report was regenerated, and the
attack this document prices is **refused** — for the sixth consecutive
iteration in which taking it would have converted this program's best measured
object from a fail into a pass.

## Why this was asked

Iteration 64 found that **gate 4's input is analyst-controllable**: 39 arms at
the registry's own mean Sharpe (0.944374) turn trial 88 from a gate-4 failure
(0.931948) into a pass (0.950291), on no new information. It recorded that as
a property of the gate, not an allegation.

The mirror question was never asked of **gate 3** — and gate 3 is the gate that
actually did the refusing in every route iterations 66, 67 and 68 closed. It
matters because of how CSCV decides. The fail test is a **rank inside the pool**
(`rank / (N + 1) <= 0.5`, `fast_pbo` in
`scripts/analyze_architecture_ceiling.py`, matching
`src/backtest/validation.py`), so the verdict is measured against the pool's own
median rather than against any absolute standard. That makes it a candidate for
the same defect: hold the candidate fixed, change only the pool, and see whether
the verdict moves.

If it moves, the stop condition — this loop's only success exit — is reachable
without information, and "no route reaches the stop condition" would have to be
reread as a statement about pool composition rather than about an edge. If it
does not, iterations 67 and 68's closures are stronger than they were stated.

**Every column added below is a real backtest of a real config**, obtained by an
act this contract permits (iterations 66-68: a family may be run for a *product*
reason). Nothing is fabricated and nothing is withheld. That is the point of the
exercise: if the verdict moves, it moves **without dishonesty**.

## Instrument, validated before use

Existing script, two new modes, **no new script** (twelfth iteration in
thirteen to add none):
`python -m scripts.analyze_architecture_ceiling --mode gate3-purchasability`
and `--mode gate3-frontier`.

| Check | Recorded | Reproduced here |
|---|---|---|
| candidates-PBO, 37 legacy columns | 0.651826 (`gate_report_2026-07-25.json`) | **0.651826** |
| all-columns PBO, 133 rows | 0.732556 (same report) | **0.732556** |
| ceiling arm + 37 columns | 0.235120 (iteration 67) | **0.235120** |
| ceiling arm decomposition | w 0.759751, f 0.063714, g 0.777167, own rate 0.048407 | **identical to 6 dp** |
| registry mean annualized Sharpe | 0.944374 (iteration 64) | **0.944374** |
| engine ceiling | 1.578665 (iteration 67) | **1.578665** |

Iteration 68's identity **PBO = w·f + (1 − w)·g** holds with residual **0.0**
(below 1e-12) in all 14 ladder rows, so the decomposition is arithmetic, not a
fit.

Fixed candidate throughout: iteration 67's ceiling arm — cross-sectional
momentum, K=3, lookback 120, monthly, absolute filter on, regime gate SMA 50,
annualized Sharpe **1.578665** at 38.41 % drawdown. It is the best object this
engine can express and the one whose fail→pass conversion matters.

## Finding 1 — gate 3 alone IS purchasable, and cheaply

Padding with the 64 lowest-Sharpe valid sweep arms (span **−0.053085** to
**−0.759738**), candidate held fixed:

| K junk columns | candidates-PBO | gate 3 | w | f | g |
|---|---|---|---|---|---|
| 0 | 0.235120 | fail | 0.759751 | 0.063714 | 0.777167 |
| 1 | **0.235120** | fail | 0.759751 | 0.063714 | 0.777167 |
| 2 | 0.195726 | fail | 0.759751 | 0.017591 | 0.759056 |
| 4 | 0.188733 | fail | 0.759751 | 0.013909 | 0.741591 |
| 8 | 0.172727 | fail | 0.759751 | 0.008488 | 0.692109 |
| 16 | 0.144056 | fail | 0.759751 | 0.003170 | 0.589586 |
| 32 | **0.023776** | **PASS** | 0.759674 | 0.000307 | 0.097963 |
| 64 | **0.005594** | **PASS** | 0.759596 | 0.000102 | 0.022948 |

**Thirty-two deliberately bad registered arms take the program's best object
from 4.70x the bar to below it.** Stronger: with **no new candidate at all**,
64 junk columns take the 37-column legacy pool from **0.651826 to 0.028749** —
also a pass. Gate 3's `passes` flag is a report-level field
(`gate_3_pbo.passes`), and three trials (29, 37, 118) already carry
`passes_dsr: true` in the same recorded report, so on the stop condition's
literal wording that is enough to trip it.

**The one-column step is exactly inert, and that is arithmetic.** K=1 leaves
PBO at 0.235120 and w/f/g unchanged to six decimals, because the fail
threshold is `floor(0.5·(N + 1))` and adding one uniformly OOS-dominated
column advances the winner's rank and the threshold by exactly 1 each. Extended:
after j such columns the test is `rank ≤ floor(0.5·(38 + j + 1)) − j`, which
tightens as j grows and becomes unsatisfiable near j = 64. The observed decline
is that arithmetic, blunted only because a negative-Sharpe arm can outscore the
winner on an individual half-sample.

**This is the sixth recorded gate-3 defect, and the first whose direction is
unexpected: the gate rewards registering junk.** Defects 1-5 (iterations 56,
64, 66, 67, 68) all say gate 3 mis-attributes or overcharges. This one says the
rank test is **not scale-free** — so full, honest disclosure of bad arms and a
lower PBO are the *same act*.

## Finding 2 — the stop condition is NOT purchasable, and this is why

Gate 3 is one half of an `AND`. Measured over **36 distinct (padding-shape, K)
cells** — 14 in the two extreme ladders, 20 in a Sharpe-band scan, 2 frontier
extension points — **0 pass both gates.**

The junk that buys gate 3 destroys gate 4, on the same columns:

| K junk columns | PBO | gate 3 | Sharpe variance | DSR | gate 4 |
|---|---|---|---|---|---|
| 8 | 0.172727 | fail | 3.037061e-04 | 0.972130 | pass |
| 16 | 0.144056 | fail | 4.153607e-04 | 0.930822 | **fail** |
| 32 | **0.023776** | **PASS** | 5.808302e-04 | 0.820492 | **fail** |
| 64 | **0.005594** | **PASS** | 8.549405e-04 | 0.539019 | **fail** |

And the padding that protects gate 4 destroys gate 3. Padding **at** the
registry mean — iteration 64's own dilution attack, the DSR optimum — drives the
Sharpe variance *down* from 1.584220e-04 to **8.461149e-05** at K=128 and DSR
*up* to **0.998472**, while PBO **rises to 0.258353**, worse than the unpadded
0.235120.

**Mechanism, measured rather than asserted:** the pool's own failure rate
`g` — the term that has to be small, since PBO ≤ 0.05 requires
(1 − w)·g ≤ 0.05 — is monotone in how good the padding is.

| Padding band centre | g at K=64 | PBO at K=64 | DSR at K=64 |
|---|---|---|---|
| 0.0 | 0.037013 | 0.009013 | 0.701279 |
| 0.4 | 0.387743 | 0.101166 | 0.968748 |
| 0.944374 (registry mean) | 0.745297 | 0.242657 | 0.997485 |
| 1.2 | 0.993754 | 0.478788 | 0.994844 |

A column is OOS-dominated (which lowers PBO) exactly to the extent its Sharpe
is far below the candidate's; and its distance from the registry mean is what
inflates the variance gate 4 divides by. **The two gates read the same distance
with opposite signs.** There is no third direction available: a column's OOS
rank and its full-sample Sharpe are the same quantity measured on overlapping
data.

## Finding 3 — the frontier, and it is an interior minimum

Minimum candidates-PBO achievable subject to DSR ≥ 0.95, over all 36 cells:

**0.095571** — padding band 0.4, K=128, DSR **0.969577**, w 0.735354,
g 0.361127. That is **1.9114x the 0.05 bar**.

Extended so saturation is measured and not extrapolated (`--mode
gate3-frontier`, 512 further engine runs on the same band):

| K | PBO | DSR |
|---|---|---|
| 128 | **0.095571** | 0.969577 |
| 256 | 0.098601 | 0.983973 |
| 512 | 0.144522 | 0.993604 |

The minimum is interior — PBO **rises** past K=128 as the band's own arms start
winning splits (w falls 0.735354 → 0.729759 → 0.706138). **Independent
corroboration:** 0.095571 sits **10.2 %** from iteration 64's separately
measured 0.105361, the best any of the 37 existing columns would record. Two
different questions, one magnitude.

## Controls — both negative, which is what makes finding 2 load-bearing

- **Duplication does not work.** 1 to 32 extra copies of the candidate itself
  leave PBO in **[0.205128, 0.240249]**, every one a fail. So the attack is
  specific to *dominated* columns, and today's finding is a different mechanism
  from iteration 68's resemblance premium, not a restatement of it.
- **Padding with good arms does not work.** The 64 highest-Sharpe arms
  (1.470270 to 1.331424) raise PBO monotonically to **0.828283** at K=64, while
  w collapses 0.759751 → 0.276923: they compete for the in-sample wins.
- **The forbidden attack does not work either.** Greedy removal of legacy
  columns — silent survivor filtering, which the outside literature explicitly
  forbids and this program would not do — saturates after **14 drops** at
  **0.094406** with **24 of 37** columns left, and no further single removal
  lowers it. Two unrelated attacks land on **0.094406** and **0.095571**.

## Scope limit, stated rather than buried

Padding is drawn from the **39 020 valid arms this engine can express**
(iteration 67's sweep). So the claim is *"not purchasable with anything this
repository can build"* — the same framing as iteration 67's ceiling — and **not**
a proof over all mathematically possible columns. A column that is reliably
OOS-last while carrying registry-mean full-sample Sharpe would break the
trade-off; no such object exists in this engine's expressible space, and the
mechanism above says why one is hard to construct anywhere.

## Outside literature: a prediction refuted in this configuration

Francis Dube, MQL5, **2023-11-21** — "Combinatorially Symmetric Cross
Validation In MQL5": *"using fewer parameter variations can lead to the under
estimation of overfitting, at the same time including a large number of
unrealistic parameter combinations can produce over estimates"*, and the same
EA records PBO from **0.2 to 0.8888** across timeframes on identical settings.

Measured here with the **candidate held fixed**, junk padding moves PBO the
**opposite** way — 0.235120 down to 0.005594. Both statements are true and the
scope is the difference: Dube's pool is the one the winner is *selected from*,
so junk pollutes the selection; here the winner is fixed and the pool only
supplies the OOS median, so junk lowers the median. **A gate that quotes Dube's
direction as reassurance would be quoting it out of scope.**

## Decision

1. **The attack is refused.** No proposal may register arms for the purpose of
   moving a gate-3 verdict, and no document may cite a PBO improvement obtained
   by growing the pool. Sixth consecutive refusal of a rule change or act that
   would convert this program's best measured object from a fail into a pass.
2. **Route closed:** no proposal may treat pool composition as a path to the
   stop condition. It fails on gate 4 at every measured point.
3. **Iterations 67 and 68 are strengthened, not weakened.** The ceiling arm's
   0.235120 cannot be padded away while gate 4 holds, so "the engine's ceiling
   fails gate 3" is not an artifact of who else is in the pool.
4. **First defence of the framework in this program's record.** Gate 4 is
   individually manipulable (iteration 64) and gate 3 is individually
   purchasable (today). The **conjunction** resisted 36 of 36 measured attacks,
   because the two gates respond to pool padding with opposite signs. This is
   the one structural property of the six-gate framework that works in the
   program's favour, and it is now measured.
5. **Still true, and unchanged by any of it:** nothing here is an edge. The
   candidate is a hindsight argmax that may never be nominated, and the honest
   reading of the stop condition is still that nothing this engine can build
   reaches it.

## Operator options

- **A — accept (default, no action).** Gate 3 stays as written, pool-size
  dependence recorded as defect 6, the attack recorded as refused. Cost: the
  recorded candidates-PBO of any future report remains uncomparable across
  reports with different N, and nothing in the contract says so.
- **B — declare a scale rule before the next gate report.** Fix the candidate
  matrix's composition (for example: candidates only, one column per
  architecture, or a fixed N) so PBO is comparable across reports. This is a
  rule change and must be declared before the report it governs, not after.
- **C — require the candidate-only rate to be reported beside the pooled one.**
  Does not change any verdict; makes defects 4, 5 and 6 visible in the report
  rather than in this document tree. Refused here as a repair of gate 3 (it
  would favour the ceiling arm, 0.048407 against 0.235120) but it is the
  operator's to grant.

Sources for every number: `data/research/ceiling/gate3_purchasability.json`,
`data/research/ceiling/gate3_frontier.json`,
`docs/reports/research/gate_report_2026-07-25.json`.

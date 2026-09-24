# The last open route — gate 3 does not price Sharpe, it prices resemblance

Date: 2026-09-24 (iteration 68) · Backtest-only, **nothing registered** ·
The holdout was **not read, not fetched and not unsealed**; `spent` is
still `false`. Every input is a pre-holdout artifact ending 2025-07-01:
`docs/reports/research/trial_registry.jsonl`,
`docs/reports/research/trial_returns/`, and the 2026-07-25 gate report.
No backtest was run for the headline result — it is computed from the 37
recorded candidate return series alone.

Reproduce with
`python -m scripts.analyze_architecture_ceiling --mode gate3-currency`.
This is a **new mode on iteration 67's existing script**, not a twelfth
`analyze_*` script; it imports no registration path, so N is still
**133**, no candidate column was created, no return series was written
next to the registry, and no gate report was regenerated. Canonical
output: `data/research/ceiling/gate3_currency.json` (gitignored), whose
five keys carry **every** number published below —
`baseline_candidates_pbo`, `pool_is_win_shares` (37), `crossings` (43),
`head_start` (10) and `margin_variance` (7).

## Why this document exists

Iteration 67 closed the parameter-family route by measuring what this
engine can build, and left exactly one route open:

> Explicitly NOT closed and not to be confused with it: a new
> *architecture* — new signal code rather than a new parameter family —
> is outside both P3 and this measurement.

That route cannot be closed by enumeration: you cannot sweep the space of
strategies nobody has written. But it does not have to be. **Gate 3's bar
is a property of the incumbent pool, and every new architecture faces the
same pool.** So the bar can be characterised without knowing what the
architecture is — provided it is measured in the currency the gate
actually reads.

Three iterations have priced gate 3 in annualized Sharpe:

| Iteration | Method | Result |
|---|---|---|
| 64 | constant alpha added to five base shapes, bisect to PBO = 0.05 | 1.5814–1.7857, median **1.6294** |
| 66 | the same, sixth base shape (the three-sleeve book) | **1.6905** |
| 67 | observed a real arm at 1.578665 records 0.235120 | "the floor reading was right" |

All six base shapes are **columns already inside the candidate pool**.
Iteration 64's five are trials 131, 14, 7, 15 and 85; four of them are
among the pool's top IS-winners. Nobody checked whether that mattered.

It matters, and it inverts the conclusion's direction for the one route
still open.

## 0. Baseline reproduced before anything was computed

The fast CSCV path is iteration 67's, already validated there. It was
re-validated here before use:

```
pool: 37 candidate columns, 2672 usable days, 16 blocks
recorded gate-3 candidates-PBO reproduced: 0.651826
```

Exact against the recorded `gate_3_pbo.pbo` in
`docs/reports/research/gate_report_2026-07-25.json`. Iteration 67's
decomposition of the ceiling arm was re-run and reproduces to six
decimals — PBO **0.235120**, IS-win share **0.759751**, own failure rate
**0.063714**, legacy failure rate **0.777167**, unconditional
**0.048407** — so this document and iteration 67's are measuring the same
object with the same instrument.

**One deviation is disclosed rather than buried.** Re-measured here,
iteration 64's five incumbent crossings come out at 1.630716 / 1.586848 /
1.790999 / 1.630490 / 1.698070 against its recorded 1.6294 / 1.5814 /
1.7857 / 1.6253 / 1.6993 — agreeing in rank and magnitude, but only to
**+0.34% at worst**, not to six decimals as the decomposition above does.
The bisection tolerance here is 1e-4 and iteration 64's is not recorded,
so the gap is consistent with tolerance and search bracket rather than
with a different quantity. **Nothing in this document turns on the
difference** — the finding is a *ratio* between two crossings measured
by the same instrument in the same run, and the incumbent leg is the
one that would have to move by more than 15% to overturn it.

## 1. The gate's own currency

CSCV/PBO is computed over C(16,8) = **12 870** partitions. On each one,
whichever column has the highest in-sample Sharpe is selected, and the
verdict counts how often that selection lands out-of-sample below the
median. Write **w** for a candidate's in-sample win share, **f** for its
own failure rate on the splits it wins, and **g** for the legacy pool's
failure rate on the splits it keeps. Then, exactly:

> PBO = w·f + (1 − w)·g

Because f ≥ 0, **PBO ≤ 0.05 requires (1 − w)·g ≤ 0.05.** This is
arithmetic, not an estimate. The gate never reads Sharpe; Sharpe only
enters through w.

Measured at the crossing across all 43 rows computed here — five
construction families over five base shapes, five seeds and seven
resemblance levels — the required win share is **essentially
constant**. Two of the 43 are exact duplicates by construction
(`mix-0.00` reproduces trial 131's day-permuted row and `mix-1.00` its
incumbent row, because the mix is standardised before rescaling), so 41
are independent; the three statistics below are identical either way:

| | min | median | max |
|---|---|---|---|
| **w required at PBO = 0.05** (43 rows) | 0.932246 | **0.949495** | 0.956410 |
| w required, novel shapes only (31 rows) | 0.942890 | **0.950039** | 0.956410 |

**Gate 3's actual requirement is: win the in-sample Sharpe comparison in
~95% of 12 870 split geometries against 37 fixed incumbent columns.**
That number is shape-independent. Everything the previous three
iterations measured was not the bar — it was the *Sharpe price of buying
that win share*, for one particular kind of candidate.

What the program has ever achieved in this currency:

| Object | w |
|---|---|
| best incumbent column (trial 131) | 0.345221 |
| second (trial 7) | 0.329681 |
| third (trial 47) | 0.131546 |
| **the engine's ceiling arm (iteration 67)** | **0.759751** |
| **required** | **≈ 0.95** |

## 2. The price of that win share depends on resemblance

Same requirement, four constructions of a candidate, each bisected to the
crossing. "Novel" here means *uncorrelated with the incumbent pool*, which
is what a new architecture is:

| Construction | n | min | median | max | max pool corr |
|---|---|---|---|---|---|
| incumbent + constant alpha (iterations 64/66/67's method) | 5 | 1.586848 | **1.630716** | 1.790999 | 1.0000 |
| day-permuted real shape (5 bases × 5 seeds) | 25 | 1.886356 | 2.084465 | 2.355461 | 0.013–0.0462 |
| block-permuted real shape | 5 | 2.066681 | 2.198848 | 2.263266 | 0.15–0.28 |
| block-uniform Gaussian (maximum uniformity) | 1 | — | **1.908769** | — | 0.0305 |
| **all novel constructions** | **31** | **1.886356** | **2.105693** | **2.355461** | |

Every one of the 43 rows lands at a pooled PBO inside
[0.049883, 0.049961], so these are crossings, not approximations.

Paired against its own base shape at a common seed, the penalty for being
novel rather than being a boosted incumbent:

| Base | incumbent + alpha | day-permuted | penalty |
|---|---|---|---|
| trial 131 | 1.630716 | 1.886356 | **+15.68%** |
| trial 14 | 1.586848 | 2.050139 | **+29.20%** |
| trial 7 | 1.790999 | 1.980640 | **+10.59%** |
| trial 15 | 1.630490 | 1.991649 | **+22.15%** |
| trial 85 | 1.698070 | 2.198566 | **+29.47%** |
| | | **median** | **+22.15%** |

The day-permutation preserves the base's exact marginal return
distribution — its fat tails, its skew, its volatility — and destroys only
its alignment with the pool. It also destroys serial dependence, which is
a fair objection; the **block-permutation** control answers it by
preserving within-block structure and permuting whole 167-day blocks, and
it lands **higher still** (2.066681–2.263266). Permutation is not
flattering the penalty. Three structurally independent constructions of
"uncorrelated" — day-permuted, block-permuted, and a synthetic Gaussian
with no relation to any traded series — agree.

## 3. The dose-response, and the mechanism

Interpolating one novel shape toward its incumbent twin,
`a·incumbent + (1−a)·permuted`, rescaled to each target Sharpe:

| a | max pool corr | crossing | w at crossing |
|---|---|---|---|
| 0.00 | 0.0312 | 1.886356 | 0.945532 |
| 0.10 | 0.1398 | 1.849376 | 0.944678 |
| 0.25 | 0.3416 | 1.808839 | 0.943512 |
| 0.50 | 0.7176 | 1.738776 | 0.943978 |
| 0.75 | 0.9497 | 1.668599 | 0.946698 |
| 0.90 | 0.9939 | 1.640370 | 0.947552 |
| 1.00 | 1.0000 | 1.630716 | 0.947863 |

Monotone across the whole range, **+15.68%** end to end, while the
required w never leaves [0.9435, 0.9479]. One requirement, priced
differently.

**A hypothesis was tested first and refuted.** The obvious explanation is
a head start — a boosted copy of trial 131 inherits the splits its twin
already won. Measured at each shape's own crossing, the overlap between
the arm's win set and its twin's original win set is **the same for both
constructions** (trial 131: 0.3642 incumbent vs 0.3645 permuted; trial 14:
0.0355 vs 0.0301; trial 7: 0.3470 vs 0.3105; trial 15: 0.0005 vs 0.0005;
trial 85: 0.0313 vs 0.0306). The advantage is not inherited splits.

**The mechanism is the variance of the margin.** A candidate must keep
(its IS Sharpe − the legacy max IS Sharpe) positive on ~95% of splits
(0.9435–0.9479 across these seven rows).
Correlation with the pool makes that difference *less variable*, so a
smaller mean margin suffices (annualized, at each row's own crossing):

| a | corr(candidate IS Sharpe, legacy max) | mean margin | sd of margin |
|---|---|---|---|
| 0.00 | 0.4658 | 0.558903 | 0.349773 |
| 0.10 | 0.5785 | 0.521329 | 0.321398 |
| 0.25 | 0.7009 | 0.477458 | 0.283791 |
| 0.50 | 0.8255 | 0.393207 | 0.228129 |
| 0.75 | 0.8979 | 0.316049 | 0.170904 |
| 0.90 | 0.9211 | 0.289611 | 0.152087 |
| 1.00 | 0.9288 | 0.281946 | 0.148776 |

The sd of the margin falls **57.5%** across the range while the required
mean margin falls **49.6%** — so the variance channel accounts for most,
but not all, of the pricing difference; the margin distribution's shape
changes too. Stated as measured, not as a clean Gaussian story.

## 4. Fifth recorded gate-3 defect

Iterations 56, 64, 66 and 67 each recorded a distinct defect in gate 3.
This is the fifth, and it is the first that is directional against the
program's stated goal:

> **At equal statistical quality, gate 3 is cheaper to pass by resembling
> what is already in the registry than by bringing something new.** A
> duplicate of trial 131 plus constant alpha crosses at **1.630716**; a
> candidate with trial 131's identical return distribution and no
> relationship to the pool crosses at **1.886356** — **+15.68%** on the
> same base, **+22.15%** at the median of five bases.

This compounds the fourth defect rather than restating it. Iteration 67
found that the recorded verdict is **79.41%** attributable to columns the
candidate has nothing to do with. Today's finding is that the same pooling
also sets the *entry price*, and sets it lower for candidates that
duplicate the pool. A gate meant to punish overfitting charges a
**novelty premium**.

**The loop declines the rule change, for the fifth time.** Gate 3 is
frozen until the October holdout is spent. This document does not re-read,
re-score or repair it, and no number here is offered as a substitute
verdict.

## 5. What this closes

Iteration 67 put the engine's expressible ceiling at annualized Sharpe
**1.578665** (that arm's own return series scores **1.584529** when the
Sharpe is recomputed from the equity curve rather than read off the
engine's metric; both are quoted, and the conclusion is identical under
either). Against it:

| | crossing | vs ceiling 1.578665 |
|---|---|---|
| iteration 64's median (incumbent-priced) | 1.629400 | +3.21% |
| **lowest novel crossing measured** | **1.886356** | **+19.49%** |
| median novel crossing | 2.105693 | +33.38% |
| highest novel crossing | 2.355461 | +49.21% |

Iteration 67 closed the parameter-family route on a **+3.21%** shortfall —
close enough that "the bar is nearly reachable" was a defensible reading.
For the route it left open, the shortfall is **+19.49% at its most
favourable measured point**, and that point is **not** an idealisation. The lowest
novel crossing, 1.886356, belongs to a **day-permuted copy of trial 131** —
an object carrying a registered strategy's exact marginal return
distribution with only its alignment to the pool removed. The
maximally-uniform synthetic object, which no traded strategy produces, is
**more** expensive still at 1.908769.

**Route closed: no proposal may treat a new architecture as a path to the
stop condition.** The reason is not that new architectures are bad — it is
that gate 3, as frozen, charges novelty a premium of 10.59% to 29.47% over
the price it charges a duplicate, and the program's best measured object
already falls short at the duplicate price.

This closure needs no enumeration of architectures. It rests on one
property: a new architecture is, by definition, not already in the pool.

**What it does not close.** A new architecture may still be built for a
**product** reason — exactly as iteration 66 said of a fourth sleeve and
iteration 67 of a parameter family. Nothing here says a better strategy
cannot exist; it says gate 3 as frozen would not certify one. And nothing
here is evidence about whether the existing edge works forward: that
question still has a 2028-06-29 date.

## 6. The three options this hands the operator

**A. Accept the closure and stop searching.** All three unblocking levers
are measured, all six gates are characterised, the engine's ceiling is
measured, and the last open route is now priced. There is no route from
here to the stop condition that this loop may take without an operator
rule change. Consistent with iteration 26's finding that the one
risk-compliant gate-4 pass exists only if the search stops.

**B. Declare an anti-resemblance rule before any new candidate is run.**
Gate 3's pooling is what produces both the fourth defect (79.41% foreign
attribution) and the fifth (the novelty premium). A candidate-only PBO —
the arm's own unconditional failure rate — would fix both. It is recorded
here that this change would convert the engine's ceiling arm from a fail
(0.235120) to a pass (0.048407), which is precisely why this loop refuses
to make it. **If the operator makes it, it must be declared before the
candidate it will grade exists**, in a contract rather than a research
document, and `PRE_HOLDOUT_PROTOCOL.md` §1 must be amended in the same
act.

**C. Change nothing and let the October reads happen.** Defensible, and it
costs nothing, but iterations 62 and 63 already established that neither
the forward read nor the holdout spend can decide whether the edge works.
This option should be chosen knowing it produces no verdict.

This is the **tenth** operator choice now due, and the **fifth with no
deadline**.

## 7. What this iteration did not do

No trial was registered and no arm nominated; N is still **133**. No
backtest output was written next to the registry — the one backtest run
(iteration 67's ceiling arm, re-run only to confirm the instrument agrees)
went nowhere durable. The holdout was **not read, not fetched and not
unsealed**. No gate rule was modified; **gate 3 was not repaired, re-read,
or re-scored on its candidate-only rate**, in the second consecutive
iteration where doing so would have converted the program's best measured
object from a fail into a pass. No frozen pre-registration was edited. No
registry row or return series was touched, no shadow file was written to
or read for a metric, no prior result document was rewritten, no prior log
entry was edited, no gate report was regenerated, and **no file under
`configs/runtime/`, `src/` or any scheduled-task definition was touched**.
No new script was created: iteration 67's `analyze_architecture_ceiling.py`
gained a `gate3-currency` mode.

Iterations 64, 66 and 67 are **not retracted**. Their numbers are correct
for what they measured — the Sharpe price of gate 3 for a boosted
incumbent. What is corrected is the reading that those numbers are the
bar. They are the bar's *lowest* price, available only to a candidate that
duplicates the pool.

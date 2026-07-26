# PBO scope diagnostic — the gate-3 failure is not a scoping artefact

Date: 2026-07-26 · Registry N=133 · Zero registry cost (re-analysis of
existing return series; no backtest run, no trial registered).

## The question

Gate 3 fails by an order of magnitude (candidates-PBO 0.6518 against a
0.05 bar). One plausible excuse was available: CSCV over ~100 columns of
one strategy lineage measures "can you rank near-duplicates", and
near-duplicates are unrankable almost by construction. If that were the
whole story, PBO computed over genuinely DIFFERENT architectures would be
much lower, and the failing gate would be an artefact of column
composition rather than evidence about the strategies.

**It is not the whole story. The excuse is dead.**

## Measurement

> **Addendum 2026-07-27 — what PBO is actually measuring here.** Computed
> per family, eight columns each, PBO ranges over **15×**: exp-7 donchian
> BTC/ETH **0.7415**, exp-8 donchian-13 **0.6830**, exp-3 cs-momentum
> **0.2789**, exp-5 regime gate **0.0482**. It is not degenerate.
>
> But it runs **opposite** to measured quality. Against exposure-matched
> passive twins (`TIMING_VALUE_2026-07-27.md`), exp-7's eight members score
> 3.84–4.70 — **all positive, tightly clustered**. A four-member sample of
> exp-5 scores 3.70 / 5.96 / 2.31 / 1.85 — **also all positive, spread
> 3.2×**.
>
> **Both families have a real edge in every member measured. Their PBOs
> differ by 15×.** What separates them is *dispersion*: when members are
> nearly indistinguishable the in-sample best is close to a coin flip out
> of sample (high PBO); when they differ a lot the ranking is stable (low
> PBO).
>
> So PBO answers "can I trust that I picked the best member?" — a real
> question — and says **nothing about whether the family has an edge.**
> Used as a gate on edge existence it **penalises parameter-robust
> families and rewards parameter-sensitive ones**, which is backwards. The
> weakest family by this program's own buy-and-hold table (exp-5, median
> ratio 0.439) is the only one here that would **pass** gate 3's 0.05 bar.
>
> **Correction to this iteration's own framing:** exp-5 was chosen as a
> "known weak" control on the strength of its buy-and-hold ratio. On the
> exposure-matched metric it is not weak. That is the same confound
> iteration 17 identified — judging a partly-invested system against a
> fully-invested benchmark — biting again inside one session.

> **Addendum 2026-07-27 (iteration 22) — all four families measured.** The
> claim above rested on two families. The other two were measured to test
> it, since either could have refuted it:
>
> | Family | PBO | Twin edges | Spread | Members with edge |
> |---|---:|---|---:|---:|
> | exp-7 donchian BTC/ETH | **0.7415** | 3.84–4.70 | 1.22× | **8/8** |
> | exp-8 donchian-13 | **0.6830** | 2.33–2.92 | 1.25× | **8/8** |
> | exp-3 cs-momentum | 0.2789 | 0.04–20.22 | **505×** | **2/8** |
> | exp-5 regime gate | 0.0482 | 1.85–5.96 | 3.2× | 4/4 measured |
>
> **The grouping holds: both tight families have high PBO (0.68, 0.74) and
> both dispersed families have low PBO (0.05, 0.28).** The fine ordering
> does not — exp-3 is 150× more dispersed than exp-5 yet scores a higher
> PBO. Dispersion explains the split, not the ranking, and n = 4.
>
> **The decision-relevant statement is now sharper and rests on four
> families rather than two:**
>
> - The two families where **every measured member has a real
>   exposure-adjusted edge** (exp-7 and exp-8, 8/8 each) are the two with
>   the **worst** PBO.
> - The family where **only 2 of 8 members have any edge** (exp-3 — six
>   members score between 0.04 and 1.00) scores a **better** PBO than both.
>
> **Gate 3 would therefore rank exp-3 as safer than exp-7.** PBO is a valid
> statement about whether a *pick* can be trusted; it is not a statement
> about whether the family works, and this program has been reading it as
> the latter.
>
> **Method note:** the first exp-8 run exited 1. The cause was mine — a
> PowerShell format string emitting `trial-0000100` instead of
> `trial-000100` for the two three-digit ids. Fixed and rerun to exit 0
> before any number here was used.
>
> **Still untested:** four of exp-5's eight members.

One representative per distinct strategy architecture, nine columns:

| Trial | Architecture |
|---:|---|
| 4 | live daily trend ensemble (the incumbent) |
| 7 | ladder + volatility-target overlay |
| 29 | cross-sectional momentum (exp-3 winner) |
| 56 | cross-sectional momentum + SMA regime gate |
| 78 | multi-horizon trend factor under a gate |
| 96 | Donchian, 13-symbol staggered, equal weight |
| 88 | Donchian BTC/ETH, mid-channel exit |
| 112 | Donchian + inverse-vol sizing |
| 118 | Donchian + ATR channel exit (the current best) |

| Column set | Columns | PBO |
|---|---:|---:|
| all columns | 133 | 0.7326 |
| candidates (protocol §1) | ~100 | 0.6518 |
| **distinct family** | **9** | **0.7411** |

Narrowing to genuinely different architectures made PBO **worse**, not
better. Nothing about the gate-3 failure is explained by duplicate
columns.

## What this actually says

PBO is the probability that the configuration selected as best in-sample
lands below the median out-of-sample across 12,870 train/test splits.
At 0.74 across nine distinct architectures, in-sample ranking of these
strategies is **worse than a coin flip** at predicting out-of-sample
ranking inside this window.

Two honest readings, both of which matter:

1. **Selection here is unreliable, full stop.** Trial 118 clearing gate 4
   says its own deflated performance survives the search history. It does
   NOT say it will be the best of these nine out of sample — this
   diagnostic says the opposite is more likely than not. Every claim
   about trial 118 must carry that.
2. ~~**The constraint space may be too narrow to support reliable
   selection**, because all nine share 0.9+ correlated long-only crypto
   trend beta.~~ **RETRACTED 2026-07-26, same day, on measurement.**
   The pairwise correlations were asserted, not computed. Measured on the
   same nine return series: **mean 0.628, minimum 0.359, maximum 0.958**.
   These architectures are substantially more diverse than the retracted
   claim said, so "everything is the same trade" does not hold and cannot
   be used to argue that gate 3 is structurally unpassable. Any future
   document repeating that argument is repeating a refuted one.

Reading 1 stands unchanged and is the finding: selection among these
strategies does not generalize inside this window. Reading 2 was wrong.

What the measured correlations DO support is the opposite kind of
conclusion, pursued separately: if candidates are only ~0.63 correlated,
a diversified combination of them carries real variance reduction, and a
combination rule performs no selection at all — which is the textbook
response to a high PBO. That direction is being taken up under its own
pre-registration; nothing in this document evaluates it.

## What does not change

- Gate 3's rule stays frozen until the holdout is spent
  (PRE_HOLDOUT_PROTOCOL §1). This diagnostic changes no verdict and is
  not a candidate-rule proposal.
- Trial 118's gate-4 pass at N=125 and N=133 stands as recorded.
- The October holdout nominations stay fixed.
- The forward shadow tracks (trial 88, trial 118, daily since
  2026-07-24) become MORE important, not less: if in-sample ranking is
  uninformative, out-of-sample observation is the only thing that can
  discriminate, and it is the one form of evidence this project can still
  accumulate honestly.

## Method note

`scripts/analyze_pbo_scope.py`, CSCV with S=16 blocks (12,870
combinations), computed on the durable per-trial return series over the
identical 2676-day window. The representative list was chosen before the
number was computed and is recorded above in full; no alternative
representative set was tried after seeing this result, and none may be
without a pre-registration, because "search for a column set that makes
PBO look better" is precisely the behaviour the gate exists to catch.

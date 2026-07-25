# Goal P experiment 11 pre-registration — combination instead of selection

Status: **FROZEN on commit**. Written 2026-07-26, before any
experiment-11 run and before any engine work for it.

## Why this family exists

The 2026-07-26 PBO scope diagnostic measured that in-sample ranking of
this project's strategies does not generalize (distinct-family PBO
0.7411 — worse than a coin flip). The textbook response to a high PBO is
not to rank better; it is **not to rank at all**. A combination rule
performs no selection, so the failure mode PBO measures does not apply
to it.

The same diagnostic also measured what makes combination worth trying:
pairwise correlations among distinct architectures are **mean 0.628,
minimum 0.359** — not the 0.9+ that was wrongly asserted and has been
retracted. At that correlation level, equal weighting nine series buys
roughly a 20% variance reduction, which is real.

## The contaminated number that motivated this, disclosed up front

An exploratory blend of nine hand-picked architectures scored Sharpe
1.4533 / MDD 34.77% / 27.2× on the pre-holdout window. **That number is
not evidence and is not a criterion.** The nine were chosen by the
author after seeing every result, which is exactly the hindsight channel
this project exists to block. Two hindsight-free blends computed at the
same time scored materially lower — all 133 registered columns: Sharpe
1.2017 / MDD 39.22%; all protocol-§1 candidates: Sharpe 1.1147 /
MDD 44.96%. The gap between 1.45 and 1.11–1.20 is the size of the
hindsight. This family exists to find out what a MECHANICAL rule scores.

## Member rule (mechanical, fixed now, no judgement)

Members are, exactly:

- **trial 4** — the live baseline, the only non-family member, included
  because it is the incumbent every candidate must beat.
- **the pre-declared winner of every frozen family pre-registration**,
  as recorded in that family's own result document at the time, before
  this idea existed: trial 5 (exp 1), 7 (exp 2), 29 (exp 3), 47 (exp 4),
  56 (exp 5), 78 (exp 6, lowest id of the recorded tie), 88 (exp 7),
  96 (exp 8), 112 (exp 9), 118 (exp 10).

Eleven members. **No member may be dropped for performing badly** — that
includes trial 5 and trial 47, which the exploratory blend omitted and
this rule restores. Failed-family winners are members: the rule keys on
"was pre-declared the winner of a registered family", not on "did well".

Never-nominatable robustness arms and cost-stress rows are excluded, as
they are excluded everywhere.

## Weighting arms (2 configurations)

- **W1 equal weight**: 1/11 of the risk budget to each member.
- **W2 inverse realized volatility**: weights ∝ 1/σ of each member's
  own trailing 60-day realized return volatility, renormalized to the
  same gross as W1, recomputed monthly.

Both are mechanical. **Weight optimization of any kind is forbidden** —
fitting weights to the sample is selection through the back door and
would reintroduce exactly what this family is designed to avoid.

## Success criteria (ALL required, same full-registry gate report)

1. **Winner DSR ≥ 0.95** at full deflation.
2. **Winner max drawdown ≤ 51.93%.**
3. **Winner annualized turnover ≤ 53.1.**

Selection rule between W1 and W2: higher full-window annualized Sharpe.

Anything less on any criterion → registered negative. Passing does not
trigger the loop's stop condition unless candidates-PBO ≤ 0.05 in the
same report.

## Informative read-outs (non-gating, declared now)

- W1 versus the exploratory hand-picked 1.4533: the difference is a
  direct measurement of this project's hindsight premium, and is worth
  recording whichever way it falls.
- W1 versus trial 118 alone (Sharpe 1.2411 / MDD 33.24%): does declining
  to choose beat choosing?
- Realized turnover versus the sum of member turnovers: a combined book
  nets offsetting trades across sleeves, so the engine result should
  come in BELOW naive return-series averaging, which over-counts costs.

## Engine prerequisite

A combination path that, on each decision day, evaluates every member
configuration and averages their target weights into one book, then
executes that book once (netting offsetting trades). Return-series
averaging is NOT acceptable as the registered result — it ignores
netting and therefore misstates costs — though it may be reported
alongside as the conservative bound. Implementation plus tests land
before the first run, on a clean committed tree.

## Honesty clauses

- Registry N grows; every DSR pays the larger deflation, including
  trial 118's. That cost is accepted because a combination rule is the
  direct answer to the measured selection failure, not another sweep.
- A combination inherits no member's robustness battery. It needs its
  own before any nomination.
- The October holdout, its fixed nominations, and the live contract are
  untouched by any outcome here.
- The autonomous loop may EXECUTE this pre-registration but may not EDIT
  it.

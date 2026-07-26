# Correction: the sleeve rule is not "untuned". It is a crypto search winner.

Written 2026-07-26, same day as the claims it corrects.

## The claim that was wrong

Several documents in this program, including one written earlier today,
describe the sleeve rule as **untuned** and the three-sleeve combination as
having **"no parameter chosen anywhere in it."**

That second phrasing is false, and I wrote it.

## What the record actually says

Trial 88 is an **experiment 7** row (`operator_note`: *"Goal P exp 7 family
member: donchian ensemble windows=10+20+55+110 exit=mid_channel gate=off"*).
Its own frozen pre-registration,
`docs/research/GOALP_EXPERIMENT7_PREREGISTRATION.md`:

- line 54 — `## Family grid (8 configurations, all registered)`
- line 56 — `window set ∈ { {10,20,55,110}, {20,55,110,220} }`
- line 57 — `exit rule ∈ { half_low, mid_channel }`
- line 65 — `Family winner = highest full-window annualized Sharpe.`

So the configuration carried into every sleeve — Donchian 10/20/55/110 with
a mid-channel exit, gate off — was **selected as the maximum-Sharpe member
of an eight-configuration grid, on crypto data**, and experiment 8 then
inherited it (its line 54 calls `{10,20,55,110}` the *"exp-7 winner
shape"*), carrying the choice forward a second time.

> **Correction, 2026-07-26.** An earlier version of this section attributed
> the grid to experiment 8. Experiment 8 is the 13-symbol book; trial 88 is
> an experiment 7 row on BTC/ETH. The substance is unchanged and is now
> better sourced — a max-Sharpe pick from an 8-arm grid on crypto data —
> but the experiment number was wrong and is fixed here.
>
> A second correction belongs here too: this document said the Taiwan and
> gold failures showed the rule "does not generalize", implying the crypto
> result was itself fragile. `REGISTRY_VS_BENCHMARK_2026-07-26.md` measured
> that directly — **all 8 experiment-7 configurations beat buy-and-hold,
> the worst by 79%** — so within BTC/ETH the effect is parameter-robust and
> the selection premium is only +18.8%. The failures are about **scope**,
> not about the winner being a lucky draw.

## What is still true, stated precisely

The distinction that matters is **where** the selection happened:

| Component | Chosen? | Where |
|---|---|---|
| Channel windows 10/20/55/110 | **Yes** | crypto, experiment 7 |
| Exit rule `mid_channel` | **Yes** | crypto, experiment 8 grid |
| Applying it to Taiwan | No | nothing re-fit on 0050 |
| Applying it to gold | No | nothing re-fit on GLD |
| Sleeve weights (equal) | No | declared before computing |
| Rebalance cadence (monthly) | No | declared before computing |

So the **transfer** was genuinely untuned, and the **portfolio construction**
genuinely chose nothing. The **signal rule itself was not untuned** — it
carries crypto's full search history into every market it is run in.

Correct wording going forward: *"the same rule, selected in crypto, applied
unchanged elsewhere."* Not *"an untuned rule."*

## Why this matters, and it cuts against the program

Under the corrected reading, the Taiwan and gold sleeves are **out-of-sample
tests of a crypto-selected rule** — and today's benchmark comparison
(`VS_BUY_AND_HOLD_2026-07-26.md`) shows what those tests returned:

| Market | Rule | Buy-and-hold |
|---|---:|---:|
| Taiwan 0050, 21 years | 2.15× | **7.75×** |
| Gold GLD, 20 years | 2.44× | **6.99×** |

**In both markets where the rule was not selected, it badly underperformed
holding the asset.** That is the same direction as the two other independent
warnings this program has recorded: candidates-PBO 0.7411 across distinct
architectures, and trial 118 turning negative on 0050.

Three separate lines of evidence now say the crypto result does not
generalize. The combination's Sharpe and drawdown improvements are still
real and still come from near-zero correlation — that part does not depend on
the rule being good, only on the sleeves being independent and not
catastrophic. But the story "an untuned rule that works in three markets" is
not supported. The supportable story is narrower: **"a crypto-selected rule
that transfers poorly, combined with declared equal weights, produces a
smoother book than any of its parts."**

## Documents affected

- `README.md` — the phrase "nothing was chosen at all" is corrected in the
  same commit as this file.
- `VS_BUY_AND_HOLD_2026-07-26.md` — written hours earlier today; its
  counter-argument section overstates the combination's freedom from
  selection. Corrected in place with a pointer here.
- `CROSSMARKET_COMBINATION_RESULT.md` and `SLEEVE3_GOLD_RESULT.md` are frozen
  result documents and are **not edited**; this file is their correction.
  Their measured numbers are unaffected — no computation changes, only the
  interpretation of what those numbers license.

## What does not change

- Every measured value in every result document. Nothing here is a
  recomputation.
- The pre-registrations, which were honest: experiment 8 declared its grid
  and its selection rule in advance. The failure was later prose describing
  the winner as if it had never been selected.
- The October holdout and its fixed nominations.

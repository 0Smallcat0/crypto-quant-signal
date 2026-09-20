# Autonomous research loop — standing contract

Authorized by the operator on 2026-07-21 ("開啟一個長時間的自我運行模式",
full autonomy, stop when a gate-passing candidate is found, universe
expansion first). A scheduled task runs one loop iteration per day via
`scripts/run_research_loop.ps1`. This file IS the loop's instruction set:
each iteration reads it top to bottom and executes ONE iteration honestly.

## Mission

Search for a tradeable edge — systematically, at maximum honest intensity —
inside the six-gate anti-overfitting framework. The mission is search
intensity, not a guaranteed find. A registered negative is a valid,
publishable outcome of an iteration; a fabricated or quietly-rescued
positive is the only forbidden result.

## Iron rules (violating any of these voids the iteration)

1. NEVER touch the live paper contract, `configs/runtime/`, or anything the
   daily 08:05 runtime reads. Research is backtest-only.
2. NEVER spend or peek at the holdout (`--spend-holdout` is operator-only;
   holdout nominations are fixed in `docs/contracts/PRE_HOLDOUT_PROTOCOL.md`).
3. NEVER edit a frozen pre-registration, the trial registry, or recorded
   results. Append-only science.
4. NEVER place real orders, use private APIs, or handle keys (product law,
   AGENTS.md §2).
5. Every number written into a document must be verified against its source
   file first (registry, gate report, backtest output).
6. Commit-first rule: family runs happen on a clean committed tree.
7. Run verification bare (no `| tail` pipes): `ruff check`, `ruff format
   --check`, `mypy --strict src/`, `lint-imports`, `pytest -m "not network"`.

## Step 0 — convergence check (operator order 2026-07-27, do this FIRST)

「記得每次loop都要先檢查不能越做越發散」. On 2026-07-27 the loop had
produced **10 `analyze_*` scripts, 45 files in `docs/research/`, and 24
commits in two days** while the operator's actual question went unmoved.
Diagnostics are cheap to generate and feel like progress. They are not.

Before doing anything else, write these three lines into the iteration:

1. **Current answer.** State, in one sentence, the best present answer to
   "does this make money?" — copied from the standing answer below and
   updated only when a measurement changed it.
2. **What this iteration moves.** Name the specific decision it advances or
   the specific route it closes. "Measure X" is not an answer; "decide
   whether the gold sleeve can be replaced by a static holding" is.
3. **Why it is not sprawl.** If the honest answer is "this adds a
   diagnostic but does not change the current answer or close a route",
   **do not run it.** Pick something that does, or do maintenance (P1) and
   stop.

Hard limits, binding:

- **At most one new script per iteration**, and only after checking that
  none of the existing ten can be extended instead:
  `analyze_candidate`, `analyze_crossmarket_combination`,
  `analyze_idle_capital`, `analyze_pbo_scope`,
  `analyze_registry_vs_benchmark`, `analyze_sleeve_combination`,
  `analyze_symbol_dispersion`, `analyze_timing_value`,
  `analyze_vs_buy_and_hold`, `analyze_whipsaw`.
- **No new research document** unless it records a decision or a closed
  route. Findings that only refine an existing document go into that
  document as a dated addendum.
- **End every iteration by restating line 1**, changed or unchanged. An
  iteration that cannot change it should have been P1 maintenance.

### Standing answer (update in place; this is the convergence anchor)

> As of 2026-07-27, measured on 2018-2025 and not forward-validated:
> the timing rule adds real value **in crypto only** — 4.70x and 2.77x
> its exposure-matched passive twin — and **none** in Taiwan (0.73x) or
> gold (1.00x). The best backtested book returned **14.26x against 13.53x
> for simply holding thirteen coins**, so the search bought **drawdown
> (33% vs 86%), not return**. [**CORRECTED 2026-07-28, iteration 28 —
> this clause pools two universes; see the correction block at the end of
> this standing answer. Trial 88 traded BTC/ETH, whose benchmark is 6.05x
> at 80.99%, not 13.53x at 86.22%.**] No forward evidence exists; three shadow
> tracks began 2026-07-24. **Nothing here is an edge that passes the six
> gates.**
>
> Refinement 2026-07-27 (iteration 18): *standalone* timing value and
> *portfolio* timing value are different quantities. Replacing the Taiwan
> and gold sleeves with static holdings at the same average exposure makes
> the book **worse** (Sharpe 1.3870 vs 1.4108, drawdown 16.74% vs 14.90%,
> 3.74× vs 3.94×) even though the twins pay no trading costs. Those sleeves
> earn their place by **being flat at moments uncorrelated with crypto's
> drawdowns**, not by their own returns. Route closed: do not propose
> static substitution again.
>
> Refinement 2026-07-27 (iterations 19-20): the BTC/ETH timing edge is
> **positive in all four pre-declared sub-periods** and **in all eight
> members of its experiment-7 family** (edge 3.84 to 4.70, median 4.115).
> Trial 88's selection premium is only **+14.2%** over the family median,
> so selection chose the edge's size, not its existence. This does NOT
> dispose of PBO 0.7411 — the eight are a 2x2x2 grid on the same two
> assets over the same window, not eight independent tests. On 13
> symbols the same edge fails both bear windows.
>
> Refinement 2026-07-28 (iteration 25): **the forward-validation plan's
> own timetable was wrong.** MinTRL on trial 88 is 706 days (2028-06-29,
> 95% one-sided vs SR* = 0), not the ~90 days the contract asserted; at
> 90 days the forward Sharpe's 95% interval is [-2.77, +5.13]. So the
> answer to "does it work forward?" has a **2028** date under the current
> design, and the 2026-10-22 read can only test **implementation
> agreement**, never return. Read rule frozen in advance at 4 rows:
> `docs/research/FORWARD_TRACK_READ_PREREGISTRATION.md`.
>
> Refinement 2026-07-28 (iteration 26): **the one gate-4 pass exists only
> if the search stops.** Trial 118's DSR is 0.950140 at N=133 and
> **0.949969 at N=134** — a margin of exactly one trial. Sweeping what a
> 134th trial could be, the only ones that preserve the pass have Sharpe
> in **[0.709, 1.180]**; trial 118's own 1.2413 and trial 88's 1.1823 are
> both **outside** it, so *finding something as good as what the program
> already has would destroy the pass*. Two dishonesty hypotheses were
> tested and refuted first: no unregistered arms exist (64 cs-momentum
> arms and both robustness batteries are all inside the 133), and
> dropping the batteries **raises** trial 118's DSR, so the pass is not
> self-served. This is DSR working correctly; the error was reading a
> pass as a durable property of a trial rather than of a stopped search.
> **"No new families" is therefore not a pause — it is the search being
> over.** Full measurement and the forced operator choice:
> `docs/research/GATE4_FRAGILITY_2026-07-28.md`.
>
> Refinement 2026-07-28 (iteration 27): **of six gates, two have ever
> decided a candidate.** Gate 2 cannot bind — all 133 trials share one
> 2676-day window against a 1000-day floor, so it returns pass by
> construction; gate 1 is process discipline; gates 5 and 6 have never
> been executed (gate 6's "paper period >= 3 months" checkbox is still
> unchecked). Gate 3 rejects everything and **misranks**; gate 4 passes
> one trial and **only for a stopped search**. **The whole discriminating
> power rests on two gates, both with recorded defects — so no document
> may say this program "survived six gates".** Also corrected in place:
> iteration 26 called correlation-adjusted `effective_N` a post-hoc rule
> change. It is not — `VALIDATION_GATE_CONTRACT.md` gate 1 line 44 already
> mandates it and requires the method be recorded, so the raw count in
> `run_gate_report.py:190` is a conservative **deviation from contract**.
> What is post-hoc is the *method choice*, and since proper compliance
> also recomputes the variance across K cluster aggregates, its net effect
> on trial 118 is **unknown, not favourable**. The operator must declare a
> method before it is computed.
>
> Refinement 2026-07-28 (iteration 28) — **correction to this standing
> answer's own headline sentence.** "Best book 14.26x against 13.53x for
> holding thirteen coins, so the search bought drawdown (33% vs 86%), not
> return" **pools two universes.** Trial 88 traded BTC/ETH only; its
> market is **6.05x at 80.99% drawdown**. The 13.53x / 86.22% pair is
> experiment 8's 13-coin universe, where the best arm returned 9.39x.
> This is the same pooling error caught and retracted on 2026-07-26.
> Split by question:
>
> - **Does the timing rule add value?** Same-universe only. The rule
>   bought **both** — return **14.26x vs 6.05x (+136%)** and drawdown
>   **33.05% vs 80.99%**. "Not return" is **false** here. Independently
>   corroborated by the exposure-matched twin score of 4.70x.
> - **Was 133 trials of work better than the dumbest alternative?**
>   Cross-universe is legitimate for this and is the money question:
>   **14.26x vs 13.53x, a 5.4% margin**, at 33.05% vs 86.22%. Caveats
>   stand — the 13-coin universe is survivorship-uncontrolled so 13.53x
>   is flattered, and 5.4% is not a margin 133 trials can claim credit
>   for. Even here "not return" overstates; it is **mostly drawdown plus
>   a slim return margin**.
>
> `VS_BUY_AND_HOLD_2026-07-26.md` stated the correct same-universe
> reading at its line 19 and the pooled one at its line 171; the standing
> answer inherited the wrong half. Full addendum in that document.
>
> Refinement 2026-08-31 (iteration 55) — **correction to the iteration-27
> clause "gate 4 passes one trial".** It passes **three**. The latest gate
> report (2026-07-25, N=133, unchanged since) marks `passes_dsr: true` on
> trial **29** (DSR 0.986670, drawdown 75.08%), trial **37** (0.952424,
> 67.53%) and trial **118** (0.950140, 33.24%). The first two are
> disqualified by their own family's frozen 51.93% drawdown bar, which
> `GOALP_EXPERIMENT10_RESULT.md` stated correctly on 2026-07-25 — the
> qualifier was lost when the sentence was carried into
> `GATE4_FRAGILITY_2026-07-28.md`, and the unqualified version then
> propagated. Correct wording: **the only gate-4 pass that is also
> risk-compliant.** Consequence, newly measured with the fragility
> document's own method: the one-trial fragility is
> **trial-118-specific, not gate-4-specific.** Holding the recorded
> Sharpe variance fixed and raising N, trial 118 fails at N=**134**,
> trial 37 at N=**149**, and trial 29 survives to N=**2130** — sixteen
> times the whole search. So "the search is over" stands, but for a
> structural reason rather than a near-miss at N=133: **the
> statistically robust part of this registry is the part no human could
> sit through (75.08% and 67.53% drawdown), and the part a human could
> sit through sits at or below the DSR bar.** Not to be over-read —
> registry-wide, Sharpe and drawdown are *negatively* rank-correlated
> (Spearman **-0.6789**, n=133), so this is a top-of-ranking inversion,
> not a claim that DSR rewards risk. Full addendum in
> `docs/research/GATE4_FRAGILITY_2026-07-28.md`.
>
> Refinement 2026-09-01 (iteration 56) — **gate 3's verdict number is a
> distribution, and no reading of it changes the verdict.** The stop
> condition's second half is `PRE_HOLDOUT_PROTOCOL.md` §1's
> candidates-PBO. At N=133 that rule collapses **92 of 133 trials into
> two columns** — 48 rows (experiments 3, 5, 6) represented by trial 85
> and 44 rows (experiments 7, 9, 10 plus both robustness batteries)
> represented by trial **131, a row marked "never nominatable"** —
> because `config_hash` is computed once per family run from the base
> config snapshot, before the sweep loop, so it does not vary across a
> family's arms. All three gate-4 passes are therefore absent from the
> candidate set. Varying only the rule's arbitrary "highest trial_id"
> tie-break gives **4 224 admissible readings spanning 0.454468 to
> 0.924320** (median 0.840676); the recorded **0.651826 sits at the 5.2nd
> percentile**, and repairing the key to the full machine-readable
> parameter set (111 columns) gives **0.799145**. **0 of 4 224 reach the
> 0.05 bar** — best case misses by 9.1x. So gate 3 fails independently of
> candidate composition, the route is closed, and §1's description of the
> all-columns number as a "conservative upper bound" no longer holds at
> N=133 (**88.3%** of admissible candidate readings exceed it). The
> frozen rule is unchanged and unedited. Full measurement in
> `docs/research/GATE3_CANDIDATE_COMPOSITION_2026-09-01.md`.
>
> Refinement 2026-09-06 (iteration 59) — **the forward evidence stream is
> costless, and the read rule's only full-power test cannot see it.** All
> four shadow tracks reproduce their recorded equity exactly under a
> *costless*, correctly-lagged model (max residual 8.140e-28 on trial 88,
> 8.973e-28 on trial 118, over 99 transitions), while the same-day-weight
> model fails on every turnover day. Two consequences, opposite in sign.
> **PASS:** there is no look-ahead — the recorder's own comment is now a
> measured property of the data, not a claim about the code. **DEFECT:**
> no fee, slippage or spread is charged on any turnover day, while the
> backtest these tracks validate charges **15 bps per fill**
> (`fee_bps 10 + slippage_bps 5`, registry rows 88 and 118). Uncharged
> drag is **2.607 %/yr** on trial 88 (turnover 17.381/yr) and
> **1.304 %/yr** on trial 118, worth **4.981 %** and **2.289 %** of equity
> by their MinTRL dates. The bias is **one-signed** — it can only flatter.
> Test 1 compares the exposure path only, so it **passes while the defect
> is present**; Test 2's drawdown breach becomes less likely to fire
> (currently immaterial: 3.4094 % vs 3.4456 % against a 33.05 % bar); and
> the 2028-06-29 date was derived from a **cost-inclusive** SR of 1.1823
> while the series measured on it will be **cost-exclusive**. Nothing was
> repaired: fixing the recorder mid-track splices two accounting regimes
> into one append-only series, and a read-time adjustment is a post-hoc
> metric change the frozen rule forbids. **The operator must choose, and
> before 2026-10-22.** Full measurement and the three options:
> `docs/research/FORWARD_TRACK_COST_OMISSION_2026-09-06.md`.
>
> Refinement 2026-09-16 (iteration 61) — **Test 1 is well defined, is not
> offline, and is narrower than its own wording.** Three answers to the
> question iterations 57-58 asked of gate 6, now asked of the forward
> read's primary test. **PASS:** the recorder re-seeds a fresh all-OFF
> state every run at index 110 of a *rolling* 400-bar window while an
> offline replay seeds once, and Test 1 demands exact agreement — but over
> **12 524 seed-runs** on 2017-2026 history the worst-case state burn-in
> is **96 bars** against the recorder's **290** (trial 88 96/68, trial 118
> 29/28 on BTC/ETH; median 0; **zero** seeds needed more than 290). Route
> closed; the mechanism (a late seed can never be ON while an early one is
> OFF, and the two re-converge on the first close outside
> `[exit_level, max(prior closes)]`) predicts the atr_channel track
> converges faster, and it does. **MISSING SPECIFICATION:** the rule states
> no replay depth, so a replay seeded at the 110-bar channel floor can
> disagree by up to 96 bars of state while the rule's verdict for any
> mismatch is *"implementation defect. Halt and fix."* — **as written it
> can manufacture a false halt on a correct recorder.** Required depth
> ≥ **206** bars; the recorder's own 400 is safe and adds no new number.
> **DEFECT:** the rule says "offline" and **there is no offline input.**
> The local candle store ends **2026-07-02**, the forward window opens
> **2026-07-24**, shadow rows record `close` only (no open/high/low, which
> trial 118's ATR exit consumes), and `shadow_runs/` holds 88 stdout logs
> and no candle. Test 1 on 2026-10-22 must **re-fetch 112 bars per
> symbol** — 21 warmup, 91 forward — that exist in no local file,
> unverifiable against what the recorder saw except through the ~90
> recorded closes. So the October read is bounded on three sides: it
> cannot see cost (iteration 59), cannot see a signal-math error (recorder,
> backtest engine and live runtime all import the same
> `evaluate_donchian_ensemble`), and cannot be run against an archived
> input. **It remains a real harness check, and archiving is forward-only
> — every deferred day is provenance that cannot be recovered.** Nothing
> was repaired and nothing frozen was edited. Full measurement and the
> three options:
> `docs/research/FORWARD_TRACK_REPLAYABILITY_2026-09-16.md`.
>
> Refinement 2026-09-17 (iteration 62) — **the read rule's one refutation
> test cannot fire, and with it the last uncharacterised part of the
> October read closes.** The rule quantifies Test 3's power in detail
> (SE 2.016, interval [-2.77, +5.13]) and never quantified **Test 2's**,
> whose "counts at any N" is a statement about admissibility that has been
> reading as one about power. **PASS:** Test 2's in-sample false-positive
> rate is exactly **zero at every horizon**, and by construction — the bar
> is the *maximum of the same series*, and a window whose peak resets at
> its first bar can never exceed a full-sample peak that includes
> everything before it. Checked, not asserted: a naive comparison reports
> 78/141/194 "breaches" at L=706/1000/1338 and **all of them vanish at a
> 1e-12 tolerance** (excesses 7.216e-14 to 1.776e-13 pp); an earlier pass
> of this measurement reported those artifacts as findings and is
> retracted inside the result document. **DEFECT of framing:** maxima grow
> with the window, and the bar is a 2676-day maximum applied on 2026-10-22
> to a **90**-day one. The worst 90-day stretch in the strategy's whole
> history is **26.2856%** (trial 88) and **23.4776%** (trial 118) against
> bars of 33.0478% and 33.2402% — the bar is **1.2573x** and **1.4158x**
> the worst thing ever recorded, and stops being an over-reach only at
> **706 days**, the MinTRL date reached by an independent route. Power,
> from two crude models of opposite shape agreeing on magnitude: an even
> chance of firing at 90 days needs an extra **0.4136 pp/day (-77.97 %/yr)**
> bleed or a 3.4393x severity multiple (trial 88), and the gentlest
> uniform breaching path is **0.4448 %/day for 90 consecutive days**. A
> strategy whose edge had vanished entirely and merely held BTC/ETH
> through a bad quarter would **not** trip it. The bar is not unreachable
> in principle — a 50/50 BTC/ETH benchmark's worst 90-day drawdown is
> **65.9505 %**, twice it — so what Test 2 detects is the **exit mechanism
> failing**, placing it beside Test 1 rather than beside Test 3.
> **Consequence: all three tests of the 2026-10-22 read are now
> characterised, and not one of them can speak to whether the edge works.**
> Route closed: no proposal may claim the October read produces evidence
> about the edge, in any form. Nothing was repaired and nothing frozen was
> edited; this is the **fourth** operator choice due before 2026-10-22.
> Full measurement and the three options:
> `docs/research/FORWARD_TRACK_TEST2_POWER_2026-09-17.md`.
>
> Refinement 2026-09-18 (iteration 63) — **the second unblocking lever is
> now characterised too, and the October holdout cannot decide anything
> either.** Iterations 25 and 59-62 exhausted lever 1; lever 2 had never
> been measured, and `HOLDOUT_INTEGRITY_2026-07-28.md` deliberately
> measured only its *cleanliness*, which is a different property from
> power. **DEFECT of reference:** `PRE_HOLDOUT_PROTOCOL.md` §2 was sealed
> **2026-07-19** and fixes N2 by trial id but N1 by *role* — "the live
> contract, `daily_trend_ensemble`, no overlay". On **2026-07-31**, twelve
> days later, commit `2423bf6` moved that role to trial 118, and
> `paper_runtime.yaml` says so in its own comment. The sealed text settles
> its own ambiguity on internal evidence: the bar reads "Sharpe ≥ 0.5
> (half the pre-holdout level)", and half of trial 4's **1.0230** is
> **0.5115** while half of trial 118's **1.2411** would be **0.6206**, so
> **N1 as sealed is trial 4** — which has not been live for seven weeks.
> Both resolutions cost something and neither act was improper on its own;
> what went unrecorded for **49 days** is the interaction. **DEFECT of
> power, three-fold.** At the holdout's archived L=**366** days the pass
> bar is a point estimate with SE **1.0034**, so a **completely dead**
> strategy clears it **30.91 %** of the time while a **fully intact** one
> fails **30.1 %** — on a single-use, irreversible test. Empirically over
> 2311 rolling 366-day windows N1-A clears 0.5 in **68.07 %** of them and
> the registry's **own** benchmark — a no-rebalance 50/50 BTC/ETH hold,
> provenance confirmed by reconstructing it to **5.9764x** against the
> recorded `benchmark_final_equity` — clears the same bar in **68.15 %**,
> so at today's horizon the sealed nomination scores **-0.08 pp against
> doing nothing** (the gap reverses to +7.73 pp at L=478, stated in both
> directions). And the drawdown half repeats iteration 62's Test 2 defect
> exactly: a 2676-day maximum applied to a 366-day window plus 10 pp of
> slack, giving a bar **1.2801x** the worst year the strategy ever had and
> **0 of 2311** in-sample breaches, structurally rather than by luck.
> **The gate's own arithmetic agrees:** MinTRL against gate 5's SR\* = 0.5
> is **2 207.8 days (2031-07-19)** at 90 % for the sealed nomination
> against the **366** the window holds — short by **6.0x**, and by
> **9.9x** at 95 %. Even substituting trial 118 lands on **2028-07-01**,
> one day after the forward track's independently derived MinTRL date.
> Route closed: **no proposal may treat the October holdout spend as
> evidence that decides whether the edge works.** It remains a legitimate
> single-use out-of-sample read; it is not a verdict. **Two of the three
> unblocking states named below are now measured and neither decides
> anything.** Nothing was repaired and nothing frozen was edited; this is
> the **fifth** operator choice due before 2026-10-22. Full measurement
> and the three options:
> `docs/research/GATE5_HOLDOUT_POWER_2026-09-18.md`.
>
> Refinement 2026-09-19 (iteration 64) — **the third and last unblocking
> lever is measured, and it is the only one that is NOT closed — but the
> reason this contract refuses it is measurably wrong.** P3's stated
> mechanism is "they cost N, raise every trial's bar". **DEFECT of
> premise:** `run_gate_report.py` recomputes the Sharpe variance from all
> registry rows every run, and E[max] scales as its square root while N
> enters only through Phi-inverse(1 - 1/N), so the two inputs move in
> opposite directions. Read out of this program's own three dated reports,
> variance fell **1.852337e-04 -> 1.689797e-04 -> 1.584220e-04** across
> N = 85 -> 101 -> 133 and **the N=85 -> 101 step LOWERED every trial's
> bar by 0.00071475** — sixteen new trials made gate 4 *easier*, in a
> report generated 2026-07-21T16:00:42Z, before
> `N_ARITHMETIC_2026-07-23.md` stated the premise. Across N=101 -> 133 the
> variance channel absorbed **87.62%** of the raw-N cost (realized
> +0.00015329 against +0.00123827 at fixed variance). **Gate 4 does not
> bind a new family:** a 44-arm family — the largest ever run here —
> raises its own winner's required Sharpe from **1.240607** to
> **1.263775**, **+1.87%**, and at the Sharpe gate 3 requires the same
> candidate scores DSR **0.995079**. **Gate 3 binds, and its bar is
> quantified for the first time.** A new parameter family adds K rows to N
> but exactly **one** column to the candidate matrix (`config_hash` is
> computed once per family run — `run_atr_family.py:63` — and no swept
> parameter is in the six-field candidate key; demonstrated twice, 48 rows
> -> 1 column and 44 rows -> 1 column). One maximally-dominant column
> drives PBO to its own OOS-below-median frequency, and measured over all
> 12 870 splits **the best of the 37 existing columns would still record
> 0.105361 — 2.11x the bar — with 0 of 37 reaching 0.05.** Bisecting a
> constant-alpha improvement from five base shapes puts the PBO=0.05
> crossing at annualized Sharpe **1.5814 / 1.6253 / 1.6294 / 1.6993 /
> 1.7857** (median **1.6294**), a floor rather than an estimate. **0 of
> 133 trials reach even 1.5814**; the best ever registered is **1.410899**
> (disqualified at 75.08% drawdown). **DEFECT of gate 4, newly found:** its
> variance input is analyst-controllable — **39 arms at the registry's own
> mean Sharpe (0.944374) turn trial 88 from a gate-4 failure (0.931948)
> into a pass (0.950291)** and lift trial 118 to 0.964308, on no new
> information. This is a property of the gate, not an allegation
> (iteration 26 verified no unregistered arms exist), and it completes
> iteration 26's [0.709, 1.180] window rather than contradicting it: a
> 134th trial at the registry mean *raises* trial 118's DSR to 0.950626,
> so "a margin of exactly one trial" is a margin of exactly one **good**
> trial. **Route explicitly NOT closed** — a family whose representative
> column reached ~1.63 would trip the stop condition — but no proposal may
> justify or refuse a new family by its N-cost, and any override must
> pre-declare an anti-dilution rule and the fact that gate 3 sees a
> family's **last-registered** arm, not its best (the 48-arm group is
> represented by trial 85, ranked 26th of 48). Nothing was repaired and
> nothing frozen was edited; `N_ARITHMETIC_2026-07-23.md` has an
> append-only dated addendum. This is the **sixth** operator choice now
> due and the first with **no deadline**. Full measurement and the three
> options: `docs/research/P3_OVERRIDE_POWER_2026-09-19.md`.
>
> Refinement 2026-09-20 (iteration 65) — **the sixth and last gate is
> characterised, and it cannot fail.** Iteration 27 measured gates 1 and
> 2, 56 and 64 gate 3, 26/55/64 gate 4, 63 gate 5; **gate 6 had never been
> measured at all**, and it is the only gate with a live deadline
> (`GATE6_BASELINE_2026-07-25.md` §3.1's first checkbox becomes
> date-eligible **2026-10-03**; the dashboard bar reaches 100 % on
> **2026-10-01**). Gate 6 (`VALIDATION_GATE_CONTRACT.md:92-101`)
> decomposes into ten clauses. **Four cannot fail under any
> circumstances:** "0 real order attempts" (the only broker is
> `PaperBroker`, `src/execution/broker.py:34`; the only POSTs in `src/`
> are Discord, `src/notify/channels.py:87,130`), "0 private API usage"
> (`src/config/models.py:129-133` raises at config load, `:30-34`), "no
> duplicate notifications/orders" (`src/runtime/store.py:111-112` refuses
> duplicate keys, as its own docstring states), and **"ledger
> reconciliation passes", which has no implementation and whose absence is
> a recorded design decision** — `docs/ENGINEERING_DECISIONS.md:41` chose
> "a two-level recovery lattice **with no reconciliation pass**" on
> **2026-07-03**, the day the paper period began. **Four more are strictly
> easier to pass when dead:** "0 critical crashes" is impossible to fail
> because `src/runtime/engine.py:202` returns before every downstream
> path; "every fill has fee/slippage" (**9/9**) and "every reject has a
> reason code" (**1/1**) are frozen, where measured rates of **0.3214
> fills/day** and **0.0357 rejections/day** over the 28 decision days mean
> a live 93-day window would have graded ~**29.9** and ~**3.3**; and the
> cost-recalibration trigger needs a per-side spread above **12.5 bps**
> against a frozen BTC median of **0.0000** and ETH median **0.0500**
> (round-trip **20.00** / **20.10 bps**, i.e. **250x** the ETH median
> away), on a sample that cannot grow because zero `exec_quote` events
> have been emitted in **51 days**. **One clause is activity-independent**
> (">= 3 calendar months"). **One — "measure actual costs" — is the only
> clause a dead runtime fails, and gate 6 attaches no bar to it.** So nine
> clauses carry a verdict, **not one of them can be failed by a runtime
> emitting nothing**, and gate 6's pass probability for such a subject is
> **1.0 by construction** — not a near-coin-flip like gate 5, a certainty.
> The window it will grade holds **28 deciding days of 93 (30.11 %)**.
> Stated fairly, three of the four unfailable clauses are unfailable
> because product law and idempotency are enforced in **types and
> validators** rather than by discipline — good engineering; the defect is
> that gate 6 **credits them as three months of accumulated evidence**.
> The one instrument that would catch a dead paper period — §3.1's ">= 60
> quote days", observed **28**, frozen **52** days — lives in an
> **unfrozen research document**, not a contract. Route closed: **no
> document may treat a gate-6 pass as evidence that the paper period
> validated the runtime** unless the window's deciding-day count is
> reported with it. **All six gates are now characterised: gate 2 cannot
> bind, gate 6 cannot fail, gate 5 is a near-coin-flip, gates 3 and 4 are
> the only two that ever decided anything and both carry recorded defects,
> gate 1 is process discipline.** Nothing was repaired and nothing frozen
> was edited. This is the **seventh** operator choice due and the second
> with an October date (**2026-10-03** for option C, which is a rule
> change and must be declared before the window it governs). Full
> measurement and the three options:
> `docs/research/GATE6_POWER_2026-09-20.md`.

### When the analytical routes are exhausted (reached 2026-07-27, iter 23)

Step 0 was applied honestly and returned **nothing to do**. Every remaining
lever is blocked, and the block is structural rather than temporary:

| Lever | Why it is blocked |
|---|---|
| Forward validation | Needs **time**. Crypto gains one row/day at 08:20; Taiwan and gold one row/week. Analysis cannot accelerate it. |
| October holdout | **Operator-only**, single-use, nominations fixed. |
| A new parameter family | **P3 refuses it**, and the PBO/family measurements say the winner would not be trustworthy anyway. **QUALIFIED 2026-09-19 (iteration 64): this is the one lever that is not structurally blocked — it can trip the stop condition. P3's N-cost rationale is refuted (+1.87% at K=44; the N=85->101 report shows the bar falling); what binds is a gate-3 pass bar near annualized Sharpe 1.63 that 0 of 133 trials reach. See item 3 below.** |
| Revising gate 3 after finding it misranks | Changing the rules after seeing results. Refused by design, even though the defect is real and recorded. |
| More diagnostics | Would not change the standing answer. Step 0 forbids running them. |

**So the correct behaviour of an iteration that reaches this point is: do
P1 maintenance, confirm the three tracks are gaining rows, and stop.** Do
not manufacture a diagnostic in order to have something to commit.
Twenty-three iterations produced the standing answer; the twenty-fourth
cannot improve it without data that does not exist yet.

**The state that would unblock this**, in order of when it can arrive:

1. ~~~90 days of forward rows on all three tracks (from 2026-07-24), enough
   to say anything at all about whether the measured edge persists.~~
   **CORRECTED 2026-07-28 (iteration 25) on measurement — this was wrong
   by about a factor of eight.** MinTRL on trial 88's own return series
   (SR 1.1823, skew +0.227, kurtosis 12.775) is **706 days, i.e.
   2028-06-29** at 95% one-sided against SR* = 0; 429 days (2027-09-26)
   at 90%. At 90 days the standard error of the forward Sharpe is 2.016
   annualized, a 95% interval of **[-2.77, +5.13]** — no evidence about
   return whatsoever. The 90-day read is an **implementation** read only.
   Rule fixed in advance in
   `docs/research/FORWARD_TRACK_READ_PREREGISTRATION.md`; no read may be
   moved earlier, and a positive forward Sharpe may not be cited as
   support before the MinTRL date.
2. ~~The October holdout spend, per `PRE_HOLDOUT_PROTOCOL.md`,
   operator-run.~~ **CORRECTED 2026-09-18 (iteration 63) on measurement —
   this lever does not unblock anything either.** The spend is still
   available and still clean (`spent: false`, no trial ever crossed the
   boundary), but it cannot decide: at the holdout's 366 days a dead
   strategy clears the SR ≥ 0.5 bar **30.91%** of the time while an
   intact one fails **30.1%**; a passive 50/50 BTC/ETH hold clears the
   same bar at **68.15%** against the sealed nomination's **68.07%**; the
   drawdown half is **1.2801x** the worst year on record and breaches in
   **0 of 2311** in-sample windows; and MinTRL against the gate's own
   SR* = 0.5 is **2 207.8 days (2031-07-19)** at 90%, short by **6.0x**.
   Separately, §2's N1 has not named the live contract since
   **2026-07-31**. No proposal may treat this spend as evidence that
   decides whether the edge works.
   `docs/research/GATE5_HOLDOUT_POWER_2026-09-18.md`.
3. ~~An operator override of P3 that accepts the recorded cost of a new
   family.~~ **CORRECTED 2026-09-19 (iteration 64) on measurement — this
   is the only one of the three that still works, and "the recorded cost"
   is not what this contract says it is.** The N-cost is **+1.87%** of
   required Sharpe at K=44 and the premise that every family raises every
   trial's bar is refuted by this program's own 2026-07-21 gate report,
   which shows the bar **falling** as N went 85 -> 101. What binds is
   **gate 3**: a parameter family buys exactly one candidate column, one
   maximally-dominant column sets PBO to its own OOS-below-median rate,
   and the best of the 37 existing columns would still record **0.105361**
   against a 0.05 bar. The crossing sits at annualized Sharpe **~1.63**
   (five base shapes, 1.5814-1.7857), which **0 of 133 trials reach**.
   Gate 4's variance input is separately **diluteable** — 39 arms at the
   registry mean convert trial 88 from failure to pass. So the lever can
   trip the stop condition, cannot produce forward evidence sooner
   (winner's own MinTRL 377.2 d at 95% vs SR* = 0), and must not be
   refused or granted on N-cost grounds.
   `docs/research/P3_OVERRIDE_POWER_2026-09-19.md`.

## One iteration, in order

1. **Read state** (~5 min): `docs/research/LOOP_LOG.md` (last entry),
   `docs/research/GOALP_EXPERIMENT3_PREREGISTRATION.md`, latest gate report
   under `docs/reports/research/`. Decide today's step from the queue below.
2. **Web research** (15–30 min): search recent literature/practitioner
   sources for edge hypotheses fitting product law (spot, long-only, daily,
   two-sided costs). Append 3–5 dated lines to
   `docs/research/RESEARCH_LOG.md` — source, claim, testable-here yes/no.
   Never skip this step; training-data-only reasoning is not research.
3. **Advance the queue** (the bulk of the iteration).

   **Queue as of 2026-07-26 (latest) — a sleeve must beat buy-and-hold
   in its own market before it may be added**

   Two measurements taken after the queue below was written change what
   a sleeve has to prove.

   1. `VS_BUY_AND_HOLD_2026-07-26.md`: the trend rule beats simply
      holding the asset in **one** of three markets. Taiwan 2.15x
      against 7.75x, gold 2.44x against 6.99x, and the gold sleeve
      loses on Sharpe as well. The three-sleeve book made 3.94x against
      5.42x for holding the same three assets equally — it wins on
      drawdown (14.90% against 40.59%) and Sharpe, and loses on money.
   2. `SELECTION_PROVENANCE_CORRECTION_2026-07-26.md`: the rule is not
      untuned. Windows 10/20/55/110 are experiment 7's winner and
      `mid_channel` was selected from an eight-arm grid by a
      maximize-Sharpe rule, both on crypto data. Taiwan and gold are
      therefore out-of-sample tests of a crypto-selected rule, and it
      lost both.

   - **P1 (unchanged, still first): keep all three forward tracks
     recording.** They are the only unbiased evidence this program can
     still generate.
   - **P2 (tightened): a fourth sleeve must clear a buy-and-hold gate
     BEFORE it is proposed.** Pre-register it, run it once, and require
     that the sleeve beat buy-and-hold **in its own market on at least
     one of return or Sharpe**. A sleeve that loses on both is buying
     drawdown reduction the operator could buy more cheaply by simply
     holding less of everything, and it must not be added on a
     portfolio-level Sharpe improvement alone. The market-shopping
     guard in `SLEEVE3_GOLD_PREREGISTRATION.md` still binds: every
     market tried is reported, not only the survivor.
   - **P3 (unchanged): no new single-market parameter families**, and
     no re-opening the cash-aware allocation route with a cap parameter
     or a tilt.
   - **Standing correction duty:** three independent lines now say the
     crypto result does not generalize — PBO 0.7411, trial 118's
     cross-market refutation, and the buy-and-hold comparison above.
     Any document written from here that describes the rule as
     "untuned", or the combination as choosing nothing, is wrong and
     must be corrected in place the same day.
   - Superseded queue (kept for provenance):

   **Queue as of 2026-07-26 (later) — three sleeves exist; forward
   evidence is now the binding constraint**

   Sleeve 3 (gold, GLD) was built and run the same day the queue below
   was written. Result: `docs/research/SLEEVE3_GOLD_RESULT.md`, PASS on
   all four pre-declared criteria. Three sleeves, equal weight, monthly
   rebalanced, common window 2018-03-06..2025-07-01: Sharpe 1.4108
   (from 1.3437), max drawdown 14.90% (from 19.73%), and lower drawdown
   in every one of four sub-period regimes tested. Cost: terminal
   wealth 6.00x -> 3.94x.

   - **P1: keep all three forward tracks recording.** Crypto daily 08:20
     (`CryptoShadowTrial88`), Taiwan + gold weekly Saturday 09:40
     (`TwShadow0050`, which now refreshes both series and writes
     `shadow_tw0050.jsonl` and `shadow_gld.jsonl`). If any stops gaining
     rows, fix it before anything else. Every result document since the
     two-sleeve combination has ended with the same sentence: backtests
     cannot make this more credible, only unseen data can. Act like that
     is true.
   - **P2: a fourth sleeve is permitted, under the market-shopping
     guard.** `SLEEVE3_GOLD_PREREGISTRATION.md` binds: pre-register the
     market by name with reasons written before any run, run it once,
     and report it **whether it passes or fails** — never try several
     and publish the survivor. The mechanism constraint still holds: the
     candidate must be a system that exits to cash. Weigh it against the
     measured cost — each sleeve so far cut terminal wealth (14.26x,
     6.00x, 3.94x) to buy a smaller drawdown, and a fourth will do it
     again. A sleeve that is not close to independent is not worth that.
   - **P3: no new single-market parameter families.** Unchanged, and
     reinforced: PBO 0.7411 across distinct architectures, and trial
     118's distinguishing parameter turned negative out of market.
   - Superseded queue (kept for provenance):

   **Queue as of 2026-07-26 — combination over selection, sleeve by sleeve**

   The 2026-07-26 measurements changed what is worth doing. Selection
   does not generalize here: PBO 0.7411 across distinct architectures,
   and trial 118's distinguishing parameter turned NEGATIVE on Taiwan
   0050 when run unchanged. What did work was combining the SAME untuned
   rule across independent markets — crypto + 0050, daily correlation
   −0.0041, combined Sharpe 1.3437 at 19.73% drawdown, all three
   pre-declared criteria passed, and the independence measured STRONGER
   in stress (−0.18 on crypto's worst 5% of days).

   - **P1 (highest value): add independent-market trend sleeves.** Same
     untuned mid-channel Donchian rule, new market, fixed equal weights,
     no per-market tuning — a new sleeve is a data-source task, not a
     search. **Binding mechanism constraint** from
     `CROSSMARKET_COMBINATION_RESULT.md`: the benefit comes from a sleeve
     being IN CASH while another falls, not from asset-class hedging, so
     every candidate sleeve must be a system that exits to cash. Cheapest
     next sources: a public daily CSV feed (US index ETF, gold) with its
     own ingestion, quality gate, and pre-registration before any run.
   - **P2: keep both existing sleeves recording.** Crypto shadow daily
     08:20 (`CryptoShadowTrial88`), Taiwan weekly Saturday 09:40
     (`TwShadow0050`). If either stops gaining rows, fix it first —
     forward evidence is the only kind this project can still add.
   - **P3: no new single-market parameter families.** They cost N, raise
     every trial's bar, and the two diagnostics above say the winner
     cannot be trusted anyway. Refuse them unless the operator overrides.
   - Superseded queue (kept for provenance):

   **Queue as of 2026-07-25 — consolidation LIFTED by operator order**
   (「你真正該做的應該是想盡辦法，做盡測試」). The iteration-11
   consolidation switch is revoked; the multi-iteration budget the
   scoping doc said experiment 9 needs is granted. The N-arithmetic of
   `docs/research/N_ARITHMETIC_2026-07-23.md` still governs WHICH family
   is worth running — it rules out wrapper re-sweeps, not this one.

   - Q1 (2-3 iterations, engine): SSRN-faithful allocation model for the
     Donchian book per `docs/research/EXPERIMENT9_SCOPING_2026-07-24.md`
     path B — cross-asset inverse-vol weights, per-name cap arm,
     portfolio-vol rescale, new `BacktestParameters` fields, execution
     rewire, staggered-mode interaction, ≥6 tests. Leave the tree green
     and committed at every stop; never rush a half-verified engine out.
   - Q2: pre-register the experiment-9 family (frozen on commit) with
     statutory bars only, then run it, then gate report + result doc.
   - Q3: adversarial robustness battery on any candidate that ends up
     better-evidenced than trial 88, following the pattern in
     `docs/research/ROBUSTNESS_TRIAL88_PREREGISTRATION.md` (arms bound as
     never-nominatable; a better neighbour is a fragility signal).
   - Q4: keep the trial-88 shadow track healthy — if
     `data/runtime/shadow_trial88.jsonl` has not gained a row in 48h,
     diagnose and fix it. Forward-only evidence is the only clean
     out-of-sample data this project can accumulate before October.
   - Standing: an iteration that READS results does not WRITE the next
     pre-registration (goalpost-drift guard) unless the operator has
     ordered otherwise in that sitting.
4. **Verify** (rule 7), fix what breaks, or revert and log the failure.
5. **Record + publish**: append a dated LOOP_LOG.md entry — what ran, what
   resulted, exact numbers, next step. Commit everything meaningful with a
   decision-record message; `git push`.

## Stop condition (the only success exit)

If a full-registry gate report shows a candidate with **DSR ≥ 0.95 AND
candidates-PBO ≤ 0.05**: write `docs/research/EDGE_CANDIDATE_FOUND.md`
(config, numbers, report path), commit, push, send the operator a Discord
notification via the runtime notifier if reachable, and STOP starting new
experiments. Subsequent iterations only maintain/verify until the operator
responds. Everything below that bar: log and continue.

## Budget discipline

One iteration ≈ one focused working session. Unfinished queue items carry
over via LOOP_LOG.md — never rush a half-verified result out the door to
"finish". If the tree cannot be left green, revert to the last green state
and log why.

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

### When the analytical routes are exhausted (reached 2026-07-27, iter 23)

Step 0 was applied honestly and returned **nothing to do**. Every remaining
lever is blocked, and the block is structural rather than temporary:

| Lever | Why it is blocked |
|---|---|
| Forward validation | Needs **time**. Crypto gains one row/day at 08:20; Taiwan and gold one row/week. Analysis cannot accelerate it. |
| October holdout | **Operator-only**, single-use, nominations fixed. |
| A new parameter family | **P3 refuses it**, and the PBO/family measurements say the winner would not be trustworthy anyway. |
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
2. The October holdout spend, per `PRE_HOLDOUT_PROTOCOL.md`, operator-run.
3. An operator override of P3 that accepts the recorded cost of a new
   family.

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

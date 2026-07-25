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

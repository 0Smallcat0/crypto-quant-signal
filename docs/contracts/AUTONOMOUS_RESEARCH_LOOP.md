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
3. **Advance the queue** (the bulk of the iteration):
   - Q1: cross-sectional allocator engine path (`cross_sectional_momentum`
     in BacktestParameters) + tests, per the experiment-3 pre-registration.
     Multi-session work: leave the tree green and committed at every stop.
   - Q2: run the 16-config experiment-3 family (registry rows + durable
     return series), commit.
   - Q3: full gate report at the new N; write
     `docs/research/GOALP_EXPERIMENT3_RESULT.md` with the pre-declared
     verdict. An iteration that READS results does not WRITE the next
     pre-registration (goalpost-drift guard) — queue it for the next one.
   - Q4: next family pre-registration (frozen on commit), drawing on
     RESEARCH_LOG hypotheses. Then its engine work, run, result — repeat.
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

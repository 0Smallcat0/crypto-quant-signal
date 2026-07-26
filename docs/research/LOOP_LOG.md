# Autonomous research loop — iteration log (append-only)

## 2026-07-21 — iteration 0 (sprint session, human-supervised)

- Universe expanded 2 → 13 qualified symbols; quality gate 13/13 PASS
  (`docs/research/UNIVERSE_EXPANSION.md`, commit 71063e7).
- Experiment 3 pre-registered and FROZEN: cross-sectional momentum,
  16 configs (commit 972c44d).
- Daily loop scheduled: task `CryptoResearchLoop`, 21:37 local,
  runs `scripts/run_research_loop.ps1`.
- **Next step (Q1): implement the `cross_sectional_momentum` engine path +
  tests. Nothing has run yet; registry N is still 21.**

## 2026-07-21 — iteration 1 (Q1, autonomous)

- Research log appended (4 dated lines): Springer FMPM 2025 XS-momentum
  fragility warning, Cambridge JFQA 2024 trend-factor result parked for a
  future family, Trakx practitioner cost-drag confirmation, ACFR AUT
  homogeneous-universe read-out — all mapped to the pre-registered grid
  arms in `docs/research/RESEARCH_LOG.md`.
- `BacktestParameters` extended with `cs_top_k`, `cs_lookback_days`,
  `cs_rebalance_cadence`, `cs_absolute_filter`, `cs_min_pool_size`
  (`src/backtest/types.py`). Strategy whitelist now allows
  `"cross_sectional_momentum"`; the vol overlay is refused for it because
  cross-sectional weights are already normalized.
- Engine dispatch added at the top of `run_backtest` in
  `src/backtest/engine.py`; ladder path untouched. New
  `_run_cross_sectional_backtest` implements the mechanical spec: union of
  candle dates, per-decision lookback ranking, top-K equal-weight snap,
  absolute-filter arm, cadence-driven weekly/monthly rebalance, next-bar-open
  execution reusing `_execute_ladder_change` for order plumbing.
- 12 new tests in `tests/backtest/test_cross_sectional_backtest.py` cover
  validation errors, cadence key semantics, top-K selection, absolute filter,
  min-pool-size gate, monthly cadence firing, hold-day fill absence, cost
  assumptions surfacing, and ladder-strategy non-regression.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check` PASS;
  `mypy --strict src/` PASS (57 files, 0 issues after installing missing
  `websockets` and `types-PyYAML` env deps that pre-dated this iteration);
  `lint-imports` 13/13 KEPT; `pytest -m "not network"` 349 passed in 109.57s.
- Registry N unchanged at 21. Family runs are Q2 work, deferred to a future
  iteration per the multi-session split allowed by the contract.
- **Next step (Q2): run the 16-config experiment-3 family through
  `run_registered_backtest`, register 16 new trials (N: 21 → 37), commit
  registry rows and per-trial return series.**

## 2026-07-21 — iteration 2 (Q2+Q3, operator-triggered "直接接著跑")

- Alignment bug caught BEFORE running: cs decision times started at the
  lookback floor, so 90d/180d arms would have produced misaligned return
  series and the gate report would abort. Fixed with
  `cs_decision_start` (engine floor + validation + 2 tests), pinning all
  family series to the registry window (2676 returns,
  2018-03-05 → 2025-07-01). Commit 6163655.
- Family ran clean (trials 22-37). Winner trial 29 (K=2/180d/monthly/
  filter-on): Sharpe 1.4109, **DSR 0.962102 — first ≥ 0.95 in project
  history** — but MDD 75.08% fails criterion 2 by 23.15pp.
  **Family = registered negative.** Full table + verdict in
  `docs/research/GOALP_EXPERIMENT3_RESULT.md`.
- Stop condition NOT met: candidates-PBO 0.5834 > 0.05 (and the cs family
  folds to one candidates column — defect documented in the result file;
  runner serialization forward-fixed).
- **Next step (Q4, NEXT session per drift guard): pre-register the
  risk-managed combination family (cs momentum signal × drawdown/vol
  overlay) targeting MDD without killing the deflation-surviving Sharpe.
  Also compute trial 29 × trial 4 return correlation (queued read-out).**

## 2026-07-21 — iteration 4 (experiment 4, operator-triggered same-sitting)

- Drift-guard override by explicit operator order, recorded in the
  pre-registration; thresholds all anchored to pre-today numbers.
- Engine: cs vol-overlay refusal lifted; `_cs_vol_scaled_weights` reuses
  `_vol_scaler` verbatim; execution now fires on any effective-vs-held
  drift (daily scaler resizes between monthly selections). Commit 7e50bc8.
- Family ran (trials 38-53, N: 37 → 53). Winner trial 47 (70%/20d/monthly):
  Sharpe 1.0338, DSR 0.8114, MDD 63.76% — **criteria 1 AND 2 fail; fourth
  registered negative.** Full table + structural finding in
  `docs/research/GOALP_EXPERIMENT4_RESULT.md`.
- Structural conclusion: the vol dial sweeps 39%→73% MDD and Sharpe never
  clears the deflation bar anywhere on the dial — volatility is the wrong
  conditioning variable for cs momentum (profits live IN high-vol regimes).
- Trial 29 at N=53: DSR 0.9765 (non-monotonic deflation, third case).
- Scheduled iteration 3 (21:37 headless) ran during this window and
  surfaced the regime-gate hypothesis (BTC 200d-SMA) in RESEARCH_LOG.
- **Next step (Q4, NEXT sitting, drift guard back in force): pre-register
  experiment 5 — directional regime gate (BTC close > 200d SMA) over the
  fixed cs architecture; grid over gate window/hysteresis arms; criteria
  anchored to the same statutory bars (DSR ≥ 0.95, MDD ≤ 51.93%,
  turnover ≤ 53.1).**

## 2026-07-21 — iteration 5 (experiment 5, operator-triggered same-sitting)

- Second recorded drift-guard override; thresholds statutory as before.
- Engine: cs_gate_* parameters + prefix-sum SMA state machine with
  hysteresis (btc-proxy or per-symbol basis, daily or monthly-frozen
  cadence), mutually exclusive with the vol overlay. Commit 273b9d7.
- Family ran (trials 54-69, N: 53 → 69). Winner trial 56 (SMA100/btc/2%/
  daily): Sharpe 1.1651, DSR 0.9115, MDD 58.47% — criteria 1 and 2 fail;
  **fifth registered negative.** Full table + frontier analysis in
  `docs/research/GOALP_EXPERIMENT5_RESULT.md`.
- Breakthrough inside the negative: trials 62/64 (SMA200/btc/daily) put
  cs MDD INSIDE the statutory bar for the first time (51.83% ≤ 51.93%) at
  Sharpe 0.978 — the feasible region exists; the statutory corner
  (both bars at once) is still open.
- Winner-gap trend exp 3→4→5: 75.08% → 63.76% → 58.47% MDD. Directional
  gating works where vol targeting failed. Monthly-frozen gates are
  disaster arms; daily gate + 2% hysteresis halves turnover and raises
  Sharpe. Trial 29 at N=69: DSR 0.9802 (fourth non-monotone rise).
- **Next step (Q4, NEXT sitting unless operator overrides): pre-register
  experiment 6 — multi-horizon trend-factor selection (Cambridge JFQA
  2024, already in RESEARCH_LOG) under the proven SMA200/btc/daily gate;
  or K/lookback variation under that gate. Statutory bars unchanged.**

## 2026-07-21/22 — iteration 6 (experiment 6, operator-triggered "continue")

- Third recorded drift-guard override; thresholds statutory as before.
- Engine: cs_horizon_days multi-horizon score (+ decision-floor semantics
  fix so short/long-horizon arms share the 2676-return window). Commit
  2e9142f.
- Family ran (trials 70-85, N: 69 → 85). Winner trials 78/79 (exact tie,
  filter arm never triggered — grid design lesson recorded): blend
  28+56+112+224, K=2, weekly. Sharpe 0.9855, DSR 0.8345, MDD 53.49% —
  criteria 1 and 2 fail; **sixth registered negative.** Full table in
  `docs/research/GOALP_EXPERIMENT6_RESULT.md`.
- **Lineage closed**: JFQA multi-horizon did not replicate (blend ≈
  exp-5's single lookback); four arms now inside the MDD bar but best
  in-bar Sharpe 0.917 vs the ~1.3 the N=85 deflation demands. 64
  registered cs-momentum arms cannot satisfy both statutory bars at once.
- Trial 29 at N=85: DSR 0.9856 (fourth consecutive non-monotone rise);
  trial 37 at 0.9494. PBO candidates 0.8241.
- **Next step (Q4, NEXT sitting unless operator overrides): pick the fork
  recorded in the result file — (1) Donchian breakout ensemble
  pre-registration (new signal space, SSRN 2025 in RESEARCH_LOG), or
  (2) consolidate: stop spending N, redirect iterations to gate-6
  evidence until the October holdout. One choice, pre-registered.**

## 2026-07-22 — iteration 7 (experiment 7, operator-triggered "繼續找")

- Fork resolved by operator order: new signal space. Fourth recorded
  override; thresholds statutory as always.
- Engine: donchian_breakout_ensemble strategy module on the ladder path
  (4-window state machines → 5-rung ladder), _SizedDecision gained
  generated_at_bar_close, ladder path gained the exp-5 regime gate.
  Commit f625d87.
- Family ran (trials 86-93, N: 85 → 93). Winner trial 88 (10+20+55+110/
  mid_channel/no gate): Sharpe 1.1821, **DSR 0.9267 — missed by 0.0233,
  the closest any winner has come** — MDD 33.05% and turnover both PASS.
  **Seventh registered negative, but the first with both risk bars passed
  family-wide.** Full table in `docs/research/GOALP_EXPERIMENT7_RESULT.md`.
- Signal space > wrapper: Donchian's WORST arm beats every MDD-compliant
  cs arm on both axes. Gate on a self-exiting signal double-brakes
  (lowers Sharpe in 3 of 4 pairings) — lesson recorded.
- vs incumbent trial 4 (same universe): equal terminal wealth, MDD
  33% vs 52%.
- Trial 29 at N=93: DSR 0.9852 (plateau). PBO candidates 0.8705.
- **Next step (Q4, NEXT sitting unless operator overrides): experiment 8
  — Donchian on the 13-symbol universe. Engineering prerequisite first:
  ladder engine must admit staggered listings (per-symbol decision
  eligibility instead of intersection alignment) with tests; then the
  family pre-registration. Statutory bars unchanged.**

## 2026-07-22 — iteration 9 (experiment 8, operator-triggered "continue")

- Fifth recorded override; thresholds statutory. Iteration-8 engine
  prerequisite verified green (66 tests) and its unpushed commit 7f8a0b7
  pushed first.
- Family ran (trials 94-101, N: 93 → 101) on the staggered 13-symbol
  universe, 1/13 budgets. Winner trial 96 (fast/mid_channel/no gate —
  exp-7 winner architecture widened): Sharpe 1.0004, DSR 0.8317,
  MDD 46.59% — criterion 1 fails; **eighth registered negative.**
- **Breadth hypothesis falsified in all eight pairings** (winner −0.18
  Sharpe vs trial 88): cash drag from idle pre-listing budgets + altcoin
  false breakouts. Barbell windows underperformed fast. Gate verdict
  FLIPPED on the diversified book (improves MDD, Sharpe-neutral) — the
  exp-7 double-brake was BTC/ETH-specific.
- Deflation mechanics: trial 37 became the registry's SECOND gate-4 pass
  (0.9532) on variance compression alone — MDD 67.5% keeps it
  disqualified; trial 88 GAINED to 0.9330 and remains the risk-compliant
  frontier (0.017 short). Trial 29: 0.9870.
- Hypothesis pool (not auto-run): SSRN-faithful vol-based sizing on the
  Donchian book (new allocation-model engine feature); barbell variants
  parked. Full table in `docs/research/GOALP_EXPERIMENT8_RESULT.md`.
- **Next step: NEXT sitting weighs the N-arithmetic explicitly before
  any ninth family (every family raises every trial's bar); October
  holdout untouched; gate-6 evidence accumulation continues in the
  background.**

## 2026-07-22 — iteration 8 (Q1 for experiment 8, autonomous)

- Research log appended (4 dated lines): arxiv 2510.23150 (2025-10-28)
  "medium-term horizon is redundant when short and long are present —
  barbell beats equal-weight" (parked as follow-up family, not this
  iteration); CoinAPI/Concretum/StratBase practitioner notes on survivor-
  ship bias and point-in-time universe construction (load-bearing for
  exp-8); Zarattini/Pagani/Barbon SSRN 2025 revisited (their headline
  rests on a survivorship-bias-free wide universe — universe size is
  central to the claim). All mapped to the exp-8 lineage.
- `BacktestParameters.allow_staggered_listings: bool = False` added
  (`src/backtest/types.py`) — additive optional field; every existing
  call site defaults to intersection mode, so the entire pre-exp-8
  registry (trials 1..93) is bit-for-bit reproducible.
- Engine gained `_ladder_decision_times(...)` (union or intersection),
  `_partial_execution_candles(...)` (per-symbol next-bar slice), and a
  staggered-mode branch in the main ladder loop (`src/backtest/engine.py`):
  active-symbol filter per decision day, subset ladder targets, per-symbol
  benchmark anchor (reuses `_cs_benchmark_equity`), padded ledger marks
  (reuses `_cs_equity_at_marked`). The cs path is untouched — it already
  uses the union-of-dates model natively.
- 3 new tests in `tests/backtest/test_backtest_engine.py`:
  (1) intersection mode STILL rejects a staggered universe (contract
      preserved for every pre-exp-8 family);
  (2) staggered mode: BTC lists day 0, ETH day 100; ETH's first signal is
      strictly later than BTC's, union has strictly more BTC decision days
      than ETH, both symbols fill from their respective listing days;
  (3) parity — turning the flag on with an aligned universe reproduces the
      intersection result bit-for-bit (metrics, trade count, signals).
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check` PASS
  (2 files reformatted, re-checked green); `mypy --strict src/` PASS
  (58 files, 0 issues); `lint-imports` 13/13 KEPT; `pytest -m "not network"`
  366 passed in 50.21s (was 349 at iteration 1 — deltas across intervening
  iterations plus the 3 new engine tests this iteration).
- Registry N unchanged at 93. Family run (Q2) and pre-registration (Q4)
  are deferred to the next iteration per the multi-session split the
  contract allows and the drift-guard scheduling.
- **Next step (Q4, NEXT sitting unless operator overrides): pre-register
  experiment 8 — Donchian breakout ensemble on the 13-symbol qualified
  universe with `allow_staggered_listings=True`, grid drawn from the
  exp-7 family (best fast/slow window pair × exit rule × gate off/on),
  criteria anchored to the same statutory bars (DSR ≥ 0.95,
  MDD ≤ 51.93%, turnover ≤ 53.1).**

## 2026-07-23 — iteration 10 (N-arithmetic weigh-in, autonomous)

- Research log appended (4 dated lines): Lopez de Prado/Fabozzi SSRN
  2026-03 on FDR-in-finance validates "every family raises the bar"
  arithmetic; Quanterlab DSR foundations for the √(2·ln N) growth law;
  Zarattini/Pagani/Barbon SSRN 2025 mechanism read — Donchian ensemble ×
  **vol-based position sizing** is the interlocking half we never tested;
  Poluri SSRN 2025 ATR-scaled Donchian as sibling spec for a
  vol-sized-Donchian family grid.
- N-arithmetic recorded in `docs/research/N_ARITHMETIC_2026-07-23.md`
  (numbers verified against gate_report_2026-07-22.json only):
  σ_effective back-solved from trial 88's DSR row = 1.4332; at N=101 the
  DSR ≥ 0.95 bar is SR_ann=**1.2465** and trial 88's gap is **+0.0644**;
  each 16-config family lifts the bar to SR_ann≈1.255 (N=117) and costs
  trial 88 ≈0.003 DSR on pure bar-rise mechanics; net observed exp-8 gain
  was +0.0063 DSR (+0.0088 raw compression, exp-8 winners clustered
  0.92–1.00 below trial 88's 1.18).
- Decision recorded (does NOT pre-register anything — drift guard):
  next iteration is authorized to pre-register the SSRN-faithful
  vol-sized Donchian family IF AND ONLY IF the engine work
  (allocation-model plumbing + tests) fits inside a single iteration;
  else consolidate to gate-6 evidence accumulation until the October
  holdout. Any wrapper re-sweep, barbell variant, or ATR-on-cs-momentum
  family is strictly negative EV under the arithmetic and is refused.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (111 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT; `python -m pytest -m "not network"` 366
  passed in 49.42s. Registry N unchanged at 101. Tree remained clean
  through the iteration (docs-only edits).
- Trial 88 standing unchanged: DSR 0.9330, MDD 33.05%, Sharpe 1.1821 —
  incumbent risk-compliant frontier. Trial 29 sealed off from October per
  holdout protocol; October holdout untouched.
- **Next step (Q1+Q4, NEXT sitting): scope the SSRN-faithful vol-sized
  Donchian allocation-model engine feature (target-vol weights over the
  Donchian ladder). If bounded to one session (spec + tests + green
  tree), land it and pre-register experiment 9 with a frozen grid
  (window sets × vol target × cap arm). If unbounded, log a
  consolidation switch: stop spending N, redirect subsequent iterations
  to gate-6 real-run-readiness work (`docs/runbooks/`, holdout lock
  hygiene, notifier drills) until 2026-10.**

## 2026-07-24 — iteration 11 (experiment-9 scoping, consolidation switch, autonomous)

- Research log appended (4 dated lines): Zarattini/Pagani/Barbon SSRN
  5209907 mechanism re-read on the Concretum Group companion page
  (Sharpe 1.58, alpha +14% vs BTC 2015-01→2025-03 attributed **jointly**
  to Donchian ensemble AND cross-asset vol-based sizing — not per-symbol
  overlay); Concretum "Position Sizing in Trend-Following" naming
  vol-targeting vs vol-parity vs pyramiding as three distinct
  allocation models; Alvarez Quant Trading inverse-vol formula with
  25%-per-name cap as the standard baseline; Bloomberg Cryptocurrency
  Vol Target Indices spec (2025-08-05) anchoring 10/15/25% target-vol
  values in institutional use.
- Iteration-10's gate honored: engine work scoped honestly BEFORE any
  code changes. Path A (reuse `_apply_vol_overlay` for Donchian by
  lifting the exp-7 refusal in `types.py:110-115`) is bounded to one
  iteration but is NOT SSRN-faithful (per-symbol overlay, not cross-
  asset inverse-vol) and is explicitly refused by the 2026-07-23
  N-arithmetic doc as a wrapper re-sweep. Path B (SSRN-faithful:
  new allocation-model dispatch, cross-asset weight normalization,
  cap arm, portfolio-vol rescale) requires new `BacktestParameters`
  fields, new `_dc_vol_target_weights(...)`, execution rewire skipping
  `build_ladder_targets`, staggered-mode interaction, ≥6-8 tests, plus
  runner + registry + pre-registration — honest estimate 2-3
  iterations, not one. Full scoping in
  `docs/research/EXPERIMENT9_SCOPING_2026-07-24.md`.
- **Verdict: UNBOUNDED**. Consolidation switch engaged per iteration-10
  contingency. No exp-9 pre-registration written. No family run.
  Registry N unchanged at 101. Trial 88 incumbent-frontier unchanged
  (DSR 0.9330, MDD 33.05%, Sharpe 1.1821). The SSRN vol-sized
  Donchian family is deferred until October holdout completes OR an
  explicit operator authorization overrides the consolidation.
- First gate-6 baseline recorded from the live `exec_quote` stream
  (`data/runtime/events.jsonl` 42 events, 2026-07-03 → 2026-07-23,
  21 days × 2 symbols): BTCUSDT median spread 0.00 bps, ETHUSDT
  median 0.05 bps; round-trip estimate `2 × spread_median + 2 × fee_bps`
  = 20.00 / 20.10 bps respectively vs the gate-6 cap of 37.5-45 bps
  (`VALIDATION_GATE_CONTRACT.md §6`). Cost model comfortably inside
  the calibration bar on the two live symbols so far; 90-day window
  and decision→capture drift stat remain queued. Baseline table in
  the scoping doc.
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (111 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT (via `.venv/Scripts/lint-imports.exe` —
  `python -m lint_imports` is not the entry point on Windows; noted
  for future iterations); `python -m pytest -m "not network"` 366
  passed in 50.48s. Registry N unchanged at 101; tree docs-only.
- Holdout hygiene: `docs/reports/research/holdout_lock.json`
  `spent=false`, `holdout_start=2025-07-02T23:59:59.999000+00:00`,
  `locked_at=2026-07-03T02:44:47.633808+00:00` — sealed and untouched
  this iteration.
- **Next step: NEXT sitting continues consolidation work — likely
  targets are (a) adding a decision→capture drift stat to
  `src/runtime/quotes.py` outputs so gate-6 measurement covers
  slippage in addition to spread, (b) drafting an operator-facing
  holdout spend rehearsal note against `PRE_HOLDOUT_PROTOCOL.md`, or
  (c) auditing the daily-cycle runbook against the actual harden
  script output. Any exp-9 resumption requires an explicit operator
  override recorded per drift-guard protocol.**

## 2026-07-25 — operator sprint (robustness, exp 9, exp 10; consolidation lifted)

- Operator lifted the iteration-11 consolidation and granted an unbounded
  budget (「想盡辦法，做盡測試」/「預算很充足，你可以一直跑」).
- **Robustness battery on trial 88** (trials 102-109, never-nominatable):
  all eight pre-declared criteria PASS — six window perturbations hold
  Sharpe 1.123-1.211 / MDD 29.7-37.7% (spread 0.087 vs a 0.35 bar), cost
  stress 1.126 at 2x and 1.071 at 3x. Zero-cost diagnostics:
  P(Sharpe<=0)=0.0000, 2022 is a real losing year at 22.6% drawdown,
  correlation 0.927 with the live incumbent which it dominates on every
  axis. `docs/research/ROBUSTNESS_TRIAL88_RESULT.md`.
- **Shadow track** started (commit 58f7af6) and later doubled: trial 88
  and trial 118 each accumulate forward-only records daily at 08:20
  (task CryptoShadowTrial88). First rows 2026-07-24; the two configs
  already disagree materially, which is what a forward record is for.
- **Experiment 9** (trials 110-117, SSRN-faithful inverse-vol sizing):
  winner trial 112 DSR 0.9153 — **ninth negative**. All eight arms score
  below equal-weighted trial 88. Third family across two signal spaces to
  confirm that volatility targeting on an unleverable spot book can only
  de-risk. Sizing is closed.
- **Experiment 10** (trials 118-125, ATR-scaled channel exits):
  **first family in ten to pass all three of its own criteria.**
  Winner trial 118 (ATR 14 / multiple 2): Sharpe 1.2411,
  **DSR 0.950514 PASS**, MDD 33.24% PASS, turnover 11.10 PASS. It is the
  first risk-compliant trial ever to clear gate 4.
- Honest limits recorded in the result doc: the DSR margin is 0.0005 (at
  the bar, not above it); the winner sits at a grid endpoint; gate 3 PBO
  is 0.8451 so the loop stop condition is NOT met and the search does not
  halt; and one more 8-arm family would push trial 118 back under 0.95 on
  bar-rise mechanics alone.
- **Next step: robustness battery on trial 118 (its own, per experiment
  10's honesty clause) — parameter neighbourhood plus 2x/3x cost stress,
  all arms never-nominatable. After that, no new families without an
  explicit N-arithmetic weigh-in, because the margin cannot absorb one.**

## 2026-07-25 (late) — trial-118 battery + final N=133 report

- Battery (trials 126-133, never-nominatable): all eight criteria PASS.
  Perturbations Sharpe 1.081-1.230 / MDD 29.9-43.4% (spread 0.149);
  cost stress 1.197 at 2x and 1.152 at 3x — the project's strongest.
- **Endpoint doubt resolved**: arm A3 at ATR multiple 1.5 scores 1.114,
  below multiple 2's 1.241, so experiment 10's boundary winner is a
  genuine interior optimum after all.
- **Honest counterweight**: trial 118 IS its own neighbourhood maximum
  (trial 88 was not) — the weaker signature, recorded to travel with
  every future quote.
- **Advance prediction WRONG, corrected in the result doc**: DSR was
  predicted to fall under 0.95 at N=133; measured 0.950140, still
  passing, because the clustered battery arms compressed cross-trial
  variance as fast as the bar rose. Fifth measured case of non-monotone
  deflation.
- Final report N=133: gate 2 PASS; gate 3 candidates-PBO 0.6518 (down
  from 0.8451) and all-columns 0.7326 — still FAIL by an order of
  magnitude; gate 4 passing trials [29, 37, 118], of which only 118 is
  risk-compliant.
- **Standing decision: no new families.** The margin (0.0001 at N=133)
  cannot absorb one, and every closed lineage is documented. Loop work
  returns to: shadow-track health (trial 88 + trial 118, daily 08:20),
  gate-6 evidence, and the October holdout per PRE_HOLDOUT_PROTOCOL.

## 2026-07-25 — iteration 12 (gate-6 evidence + holdout rehearsal, autonomous)

- Research log appended (4 dated lines): Bybit Q1 2026 spot slippage
  publication (institutional 0.01-0.06 bps band on US$10k BTC orders —
  our recorded 0.00/0.05 bps sits inside the same order of magnitude);
  QuantMedia slippage/latency modeling reference (mid-quote fills
  overstate Sharpe by 0.5-1.0 vs a decision-to-fill model);
  Turbine blog on backtest/live divergence (reinforces
  no-new-families standing at margin 0.0001); VARRD one-shot OOS
  restatement (external anchor for the holdout rehearsal note).
- Standing decision honored: **no new families**, no new
  pre-registrations, no trial IDs reserved. Registry `N` unchanged
  at 133; trial 118 remains the sole risk-compliant gate-4 pass;
  trial 88 remains the incumbent-frontier shadow. Holdout untouched
  (`spent=false`, `locked_at=2026-07-03T02:44:47.633808+00:00`).
- Shadow-track health: `data/runtime/shadow_trial88.jsonl` and
  `data/runtime/shadow_trial118.jsonl` each hold 1 row, first record
  2026-07-24 (recorded 2026-07-25 morning by task
  CryptoShadowTrial88). Both healthy — new files, first row within
  contract 48h rule; next 48h check is 2026-07-27. No diagnosis or
  fix needed.
- Gate-6 evidence: refreshed baseline snapshot from
  `data/runtime/events.jsonl` (44 exec_quote events, +2 vs
  iteration 11's 42) into a new consolidated doc
  `docs/research/GATE6_BASELINE_2026-07-25.md`. Numbers unchanged
  from iteration 11: BTCUSDT median 0.00 bps, ETHUSDT median 0.05
  bps, both round-trip estimates 20.00 / 20.10 bps vs the 37.5-45
  bps cap. Sample still short of the 90-day §6 requirement.
- Iteration-11 queued gate-6 stat delivered: decision→capture drift
  computed post-hoc from already-recorded `close_time` and
  `captured_at` fields (no runtime change — iron rule 1 preserved).
  Median 308.4 s (~5m 08s, matches the 08:05 Taipei daily cycle);
  two catch-up outliers (2026-07-06 ~3.4 h, 2026-07-11 ~19.8 h)
  pulled the mean to 4099.7 s. Tail is bounded by the daily
  re-fire; asymmetry documented, no recalibration required at
  N=44; next re-check at N ≥ 60.
- Operator-facing holdout spend rehearsal note included in the
  same file — command sequence for the single-use spend, both
  pre-declared nominations (N1 daily_trend_ensemble no-overlay,
  N2 trial-7 overlay config), pass bars, consequence table, and
  the explicit forbid list (no third nomination, no re-runs, no
  post-hoc parameter tweaks). Doc-only; no CLI flag verified today
  (called out in the doc so the operator re-checks `--help` before
  the October session).
- Verification bare (rule 7): `ruff check` PASS; `ruff format --check`
  PASS (118 files); `mypy --strict src/` PASS (58 files, 0 issues);
  `lint-imports` 13/13 KEPT (via `.venv/Scripts/lint-imports.exe`);
  `python -m pytest -m "not network"` 378 passed in 50.00s. Tree
  docs-only (2 files); registry N unchanged at 133.
- **Next step: NEXT sitting continues consolidation work — likely
  targets are (a) 48h shadow-track diff read-out (trial 88 vs
  trial 118 exposure disagreement) once both files have ≥ 3 rows,
  (b) audit of `RUNBOOK_DAILY_CYCLE_RELIABILITY.md` against the
  observed 9% catch-up rate (2 late captures in 22 runs), or
  (c) survey of `configs/costs/` vs the refreshed baseline to
  confirm no calibration drift has crept in. No family resumption
  without an explicit operator override recorded per drift-guard
  protocol; October holdout untouched.**

## 2026-07-26 — PBO scope diagnostic (zero registry cost)

- Tested the one available excuse for gate 3's failure: that CSCV over
  ~100 near-duplicate columns measures unrankable twins rather than
  overfitting. Computed PBO over nine DISTINCT architectures (trials
  4, 7, 29, 56, 78, 88, 96, 112, 118).
- **Hypothesis refuted, in the worse direction**: distinct-family PBO is
  **0.7411**, higher than candidates (0.6518) and all-columns (0.7326).
  The gate-3 failure is not a column-composition artefact.
- Consequences recorded in
  `docs/research/PBO_SCOPE_DIAGNOSTIC_2026-07-26.md`: in-sample ranking
  of these strategies is worse than a coin flip out of sample; trial
  118's gate-4 pass does NOT imply it is the best of the nine; and since
  all nine share 0.9+ correlated long-only crypto trend beta, **gate 3
  may be unpassable for any strategy this product is legally allowed to
  run**. October's report should state that as a finding, not discover it.
- No rule changed, no verdict moved, no alternative representative set
  tried after seeing the number (that search is exactly what the gate
  exists to catch).
- Forward shadow tracks are now the highest-value evidence stream: if
  in-sample ranking is uninformative, only out-of-sample observation can
  discriminate.

## 2026-07-26 (later) — correlation retraction + combination pre-registered

- **Retraction**: the PBO diagnostic asserted the nine architectures
  correlate at 0.9+. Measured: mean 0.628, min 0.359, max 0.958. Reading
  2 of that document ("the constraint space is too narrow, gate 3 may be
  structurally unpassable") is RETRACTED in place — it rested on the
  wrong number. Reading 1 (selection does not generalize) stands.
- The measured correlations point the other way: at ~0.63, combining
  candidates buys real variance reduction, and a combination rule
  performs no selection at all — the textbook answer to a high PBO.
- Exploratory blends (zero registry cost, from existing return series):
  nine hand-picked architectures Sharpe 1.4533 / MDD 34.77% / 27.2x;
  **all 133 registered columns 1.2017 / 39.22%; all protocol candidates
  1.1147 / 44.96%.** The gap between 1.45 and 1.11-1.20 IS the hindsight
  premium, disclosed rather than banked.
- **Experiment 11 pre-registered** (`GOALP_EXPERIMENT11_PREREGISTRATION.md`):
  combination instead of selection, members fixed by a mechanical rule
  (trial 4 plus every family's own pre-declared winner, including the
  bad ones — trials 5 and 47 are restored), two weighting arms (equal,
  inverse-vol), weight optimization forbidden, statutory bars.
- Engine prerequisite declared: a real combination path that nets
  offsetting trades across sleeves. Return-series averaging is the
  conservative bound only, never the registered result.

## 2026-07-26 (cross-market) — trial 118 tested in Taiwan, unchanged: it did not transfer

- Ported the Donchian+ATR strategy into `D:\TW-Stock-Trading` (376 tests
  green, existing paths untouched) under a frozen pre-registration
  allowing ONE configuration and forbidding any tuning on TW data.
- 0050 adjusted, 2004-2025, TW cost model unchanged: trial 118's config
  scores **Sharpe -0.3055, MDD 40.48%, 100k TWD to 66,330** against
  buy-and-hold's 0.7159 / 55.75% / 787,034. **DID NOT TRANSFER.**
- Not a broken port: mean exposure 0.384 over 5,218 days, all five rungs
  used, 165 trades.
- Mechanism: the declared context arm (trial 88's mid-channel exit)
  scores +0.4262 on identical data. One parameter — the exit rule — is
  worth +0.06 Sharpe in crypto and -0.73 in Taiwan. The crypto-optimal
  exit is the Taiwan-worst exit.
- Consequence appended to the experiment-10 result (verdict unchanged):
  trial 118's distinguishing choice is crypto-specific. Direct
  cross-market confirmation of what PBO 0.7411 implied statistically.
- **Standing guidance for any future work: a candidate's standing in this
  program now requires cross-market evidence before it can be described
  as an edge rather than a fit.**

## 2026-07-26 (cross-market combination) — PASS

- Pre-registered before computing: same untuned mid-channel Donchian rule
  in crypto and on 0050, fixed 50/50 monthly rebalanced, daily
  resolution, criteria and limitations frozen (the higher-scoring 30/70
  blend seen in exploration was excluded by design).
- Result over 2018-03-06 → 2025-07-01: crypto sleeve Sharpe 1.1829 /
  MDD 33.05% / 14.26x; Taiwan sleeve 0.9816 / 14.83% / 2.02x;
  **50/50 combination 1.3437 / 19.73% / 6.00x**. Daily correlation
  **-0.0041** — effectively independent.
- All three pre-declared criteria PASS.
- **Why it matters**: it chooses nothing. Same rule both markets, weights
  fixed in advance, improvement from diversification arithmetic rather
  than from a fitted parameter — the one channel PBO 0.7411 and the
  trial-118 cross-market refutation do not indict.
- **What it costs**: terminal wealth 14.26x to 6.00x. Better path, less
  money, and product law forbids levering it back. That is a decision
  about what a person can hold, recorded as such.
- Limits declared in advance: FX unmodeled, the window flatters the
  Taiwan sleeve (0.98 here vs 0.43 over its full 21 years), no DSR, one
  correlation estimate, two sleeves only.
- **Next: forward tracking of the Taiwan sleeve so the combination can be
  observed as a book. Backtests cannot strengthen this; only unseen data
  can.**

## 2026-07-26 (documentation + a blocked forward track)

- README updated in both repositories with the honest search log: 133
  trials, ten registered negatives, the trial-118 cross-market
  refutation, and the combination result with its wealth cost stated.
- second_brain project note updated to the current state.
- **Blocked, filed rather than worked around**: the TW forward shadow
  track cannot start yet. `scripts.ingest_public_ohlcv` completed but
  wrote through 2026-07-03 while reporting 5,675 known days against
  5,661 written — roughly 14 sessions fetched and not persisted. The
  shadow script's staleness guard refused to record rather than repeat a
  22-day-old signal into a forward record, which is the correct
  behaviour. **Next concrete task: find why the writer stops short of
  TWSE's coverage, fix it, then start the TW track.** Until then the
  cross-market combination has forward evidence on the crypto sleeve
  only.

## 2026-07-26 (later) — sleeve 3: gold, built and run the same day

- **Data source found and gated.** Stooq is behind a JavaScript
  proof-of-work bot wall and was not worked around. Yahoo's chart
  endpoint plus FinMind's `USStockPrice` are two independent providers
  for GLD; both were fetched. `range=max` silently downsamples 1d to
  monthly (261 rows instead of 5,453), so an explicit epoch window is
  used. Ingestion gate: 5,452 bars 2004-11-18..2026-07-23, **both
  providers agreeing on every one of them**, worst close disagreement
  6e-8, zero bars where adjusted close differs from raw, no gap over 10
  days. Yahoo's 2026-07-24 row was holed and was dropped rather than
  patched — the reason two providers are fetched at all.
- **Pre-registration frozen before the run**
  (`SLEEVE3_GOLD_PREREGISTRATION.md`, TW repo) with GLD chosen a priori,
  SPY and TLT rejected in writing, four criteria, a cost model harsher
  than US retail, brakes set so they cannot bind, and a binding
  market-shopping guard.
- **Result: PASS on all four** (`SLEEVE3_GOLD_RESULT.md`). TW trial 24.
  Three sleeves, one third each, monthly rebalanced,
  2018-03-06..2025-07-01: Sharpe 1.3437 to **1.4108**, max drawdown
  19.73% to **14.90%**, correlations gold/crypto +0.0767 and
  gold/Taiwan +0.0331. Lower drawdown in all four sub-periods;
  covid-window Sharpe −3.11 to −0.02.
- **Recorded against it:** terminal wealth 6.00x to 3.94x; the gold
  sleeve loses to holding gold (2.44x vs 6.96x, at a lower Sharpe); and
  its correlation to crypto **rises** in crypto's worst 5% of days
  (+0.077 to +0.105), unlike Taiwan's. Gold is not a hedge; it is flat.
- **Registry defect found and fixed.** Every row was stamping the SMA
  ensemble's lookbacks regardless of what ran, so trials 23 and 24 are
  on record naming a strategy they did not execute. Rows are
  append-only; both stay wrong, the result document is the correction,
  and rows after `63e2996` describe their own run. A test now fails if a
  Donchian run stamps SMA lookbacks.
- **Both non-crypto sleeves now record forward.** `shadow_signal_tw` was
  generalized to a TRACKS tuple; first GLD row 2026-07-23, exposure 0.0.
- **Next: P1 is keeping all three tracks alive.** A fourth sleeve is
  permitted only under the market-shopping guard, and must be weighed
  against the measured cost — every sleeve so far bought a smaller
  drawdown with terminal wealth.

## 2026-07-26 (later still) — where the money goes, and a closed route

- **Diagnostic** (`analyze_idle_capital.py`, no registry cost): the
  three-sleeve book holds **66.2% cash on average**, mean gross exposure
  0.3380, while at least one sleeve is long on 87.4% of days. The
  terminal-wealth cost of combining is mostly idle capital, not the
  arithmetic of diversification.
- **Pre-registered and run the same sitting** (operator override
  recorded): equal share among the sleeves actually long, zero free
  parameters, gross provably never above 1.
- **REGISTERED NEGATIVE** (`CASH_AWARE_ALLOCATION_RESULT.md`).
  Deployment 0.3380 to 0.5557 and multiple 3.94x to 4.39x, but drawdown
  14.90% to **23.49%** and Sharpe 1.4108 to **1.3027**. Two of three
  criteria fail. The pre-registration had already written what this
  would mean: the idle cash was buying something real.
- **Route closed with a mechanism**: within product law (spot,
  long-only, unlevered) the smoother path and the smaller multiple are
  the same fact, and reallocating idle capital does not separate them.
  The rule concentrates hardest exactly when fewest markets trend. This
  is an upper bound — reallocation costs are unmodelled and would only
  make it worse.
- **Do not re-open this by adding a cap parameter or a tilt.** That is a
  parameter family on a portfolio rule, and P3 refuses those for the
  same reason it refuses them on signals.

## 2026-07-26 (last) — the comparison the program answers to, and a correction

- **Against buy-and-hold** (`VS_BUY_AND_HOLD_2026-07-26.md`). Every
  report already carried a `benchmark_equity` series and no document had
  ever read it. The trend rule beats holding the asset in **one of three
  markets**: crypto 14.26x vs 6.05x (and 33% drawdown vs 81%), but
  Taiwan 2.15x vs **7.75x** and gold 2.44x vs **6.99x** — gold loses on
  Sharpe too. The three-sleeve book: 3.94x vs **5.42x** for holding the
  same three assets equally, winning on drawdown (14.90% vs 40.59%) and
  Sharpe (1.41 vs 1.05). **It is a risk-preference result, not a return
  result**, and the README now says so.
- **Correction, same day**
  (`SELECTION_PROVENANCE_CORRECTION_2026-07-26.md`). Calling the sleeve
  rule "untuned" was false and I had written it hours earlier.
  Experiment 8's frozen pre-registration names {10,20,55,110} as
  experiment 7's winner (line 54), lists `mid_channel` as one of two
  exit arms (line 57), and declares the winner as highest full-window
  Sharpe (line 66). Two rounds of selection, both on crypto.
- **Precise survivor:** the *transfer* to Taiwan and gold was untuned and
  the *portfolio construction* chose nothing. The *signal rule* carries
  crypto's search history everywhere it goes. Frozen result docs were
  not edited; the README and today's diagnostic were corrected in place.
- **This is the third independent line** saying the crypto result does
  not generalize, alongside PBO 0.7411 and trial 118's cross-market
  refutation.
- **Queue tightened:** a fourth sleeve must now beat buy-and-hold in its
  own market on return or Sharpe **before** it can be proposed. Adding a
  leg that loses on both, purely for a portfolio-level Sharpe bump, is
  buying drawdown reduction that holding less would buy more cheaply.

## 2026-07-26 (final) — the winner is the maximum of its family

- **Registry-wide benchmark comparison**
  (`REGISTRY_VS_BENCHMARK_2026-07-26.md`). All 133 rows already carried
  `benchmark_final_equity`; nothing had ever read that column.
- ~~**Trial 88 ranks 1 of 16 in its own family.** Its system/benchmark
  ratio is 2.381; the family median is 1.242; the spread runs 2.381 down
  to 0.419; and 8 of 16 members lose to buy-and-hold outright. A coin
  flip decides whether a family member beats holding the asset.~~
  **Retracted same day — the 16 rows are two different universes.**
  Experiment 7 is BTC/ETH only (8 rows) and experiment 8 is the
  13-symbol book (8 rows), declared as a separate test in exp 7's own
  pre-registration. Pooling them averaged 100% and 0% into a fake 50%.
- **Corrected: trial 88 ranks 1 of 8, and all 8 beat buy-and-hold.**
  Family median 2.005, floor **1.789** — the worst member still beat
  holding by 79%. Selection premium is 2.381/2.005 = **+18.8%**, not the
  ~50% first claimed. Within BTC/ETH the effect is parameter-robust.
- **But experiment 8 — the same rule on 13 symbols — beat buy-and-hold
  in 0 of 8 configurations**, median ratio 0.543. The rule does not
  survive universe expansion inside its own asset class.
- **Distribution is bimodal, not random.** Families either win every arm
  (exp 1, 2, 7, 9, 10) or lose most (exp 3, 5, 6, 8). The overall 57.9%
  is the average of two modes and means little alone.
- **Across the whole search: 77/133 (57.9%) beat buy-and-hold**, median
  ratio 1.099. Regime gate 8/33 (median 0.697), cross-sectional
  momentum 3/16 (median 0.643) — both lose in about three quarters of
  their configurations.
- **The real finding is scope, not selection.** Every out-of-scope test
  lands below the exp-7 family's *worst* member (floor 1.789): the
  13-symbol crypto book 0.419-0.695, Taiwan 0.277, gold 0.349. So the
  supportable statement is **"the rule works on BTC/ETH in this window,
  robustly across 8 configurations, and has failed every extension
  tested — more crypto symbols, another equity market, another asset
  class."** Scope is testable going forward; a cherry-picking story is
  not what the data says.
- **Fourth independent line** saying the result does not generalize:
  PBO 0.7411, trial 118's cross-market refutation, losing to
  buy-and-hold in two of three markets, and now 0/8 on universe
  expansion.
- **Lesson recorded in the tool, not just the prose.** The grouping key
  now carries the experiment number so two universes can never be
  averaged together again. I made that mistake and published it before
  catching it the same day.
- **Correction duty executed**, not just declared: the word "untuned"
  removed from README and from the TW repo's `shadow_signal_tw.py`
  docstring. Frozen result documents keep their wording and are covered
  by the correction file.

## 2026-07-26 (iteration 13, autonomous) — tracks alive, external evidence recorded, no new writes

- **All three forward tracks alive.** Crypto
  `data/runtime/shadow_trial88.jsonl` last row date 2026-07-25 recorded
  2026-07-26T00:20:06Z (daily 08:20 local) with `WINDOWS_ON_0_OF_4` for
  BTCUSDT and `WINDOWS_ON_1_OF_4` for ETHUSDT, exposure 0/0.25 —
  ensemble ran, ETH held a single window's long. TW repo
  `shadow_tw0050.jsonl` last row 2026-07-24 recorded 2026-07-25T18:09Z,
  exposure 0.25; `shadow_gld.jsonl` last row 2026-07-23 recorded
  2026-07-25T20:19Z, exposure 0. Both are ahead of today's Saturday
  09:40 schedule tick; healthy, no fix needed.
- **Web research pass (five dated lines)** appended to `RESEARCH_LOG.md`
  under `## 2026-07-26 (iteration 13)`. Two of the five directly harden
  the sleeve programme:
  1. Man Group "Cash (Equities) Is King" — directional univariate
     sector trend keeps ~0.81 rolling-24m correlation to equity-index
     trend over 21 years; cross-sectional trend is the diversifier,
     not univariate. Reads onto our three univariate sleeves as a
     warning against assuming a fourth is independent.
  2. arXiv 2510.23150 "When Diversification Hides Redundancy" —
     principal-components decomposition of multi-market trend books
     shows effective-N materially below nominal N. Points at a
     read-only diagnostic on our recorded sleeve returns.
- **Queue action taken: none of P1/P2/P3 required a write this
  iteration.** P1 was verified alive (above). P2 needs a fourth sleeve's
  market pre-checked against buy-and-hold **before** pre-registration;
  the standing goalpost-drift guard says an iteration that reads
  results does not write the next pre-registration. P3 remains refused.
  No code, no configs, no new pre-registration touched.
- **Next-iteration candidate (recorded, not committed to)**: read-only
  PCA / effective-N diagnostic on the three-sleeve daily return series
  (crypto trial 88 curve, TW trial 23 curve, TW trial 24 curve) to put
  a number on the arXiv 2510.23150 claim as it applies to this book.
  Belongs alongside `analyze_idle_capital.py`, does not use holdout,
  does not add a family, does not require a pre-registration.
- **Verify (rule 7, bare)**: `ruff check` all-clear; `ruff format
  --check` 125 files already formatted; `lint-imports` 13 contracts
  kept / 0 broken; `mypy --strict src/` 58 files, no issues;
  `pytest -m "not network"` 378 passed. Tree left green.

## 2026-07-27 — iteration 14 (loop, self-paced)

- **P1 checked first: all three tracks healthy.** Crypto shadow last ran
  2026-07-26 08:20 (result 0), track at 2 rows through 2026-07-25. The
  one-day lag is by design, not a defect: the script records the last
  fully closed daily candle. Next fire 2026-07-27 08:20.
- **Resolved the exp-8 confound.** Yesterday's "0 of 8 beat buy-and-hold"
  could not distinguish a collapsing system from an enormous benchmark.
  Measured: exp 8's median arm returned 7.33x and its best 9.39x, while
  the 13-coin benchmark returned **13.53x** — 2.2x the BTC/ETH
  benchmark's 6.05x. The system made real money and still lost.
- **The comparison this program had never made.** Trial 88 returned
  **14.26x**; buying thirteen coins in March 2018 and never looking again
  returned **13.53x**. A 5.4% margin after 133 registered trials.
- **What the search actually bought: drawdown, not return.** 33.05%
  against 86.22%, Sharpe 1.1829 against 0.8469. An 86% drawdown is the
  difference between a position a person holds and one they capitulate
  out of. Same conclusion as the combination results, now measured
  against the strongest naive alternative rather than against other
  systems.
- **Mechanism, not cost drag.** Exp 8 traded 1,516 times against exp 7's
  396 while running *lower* turnover (6.38 against 8.55) — thirteen
  independently-exiting sleeves are rarely all invested at once, and
  buy-and-hold captures every altcoin's full run.
- **Limit recorded against the finding:** the 13-coin universe came from
  a 2026 eligibility screen, so **survivorship is uncontrolled** and the
  13.53x benchmark is flattered by coins that never died.
- Written into `VS_BUY_AND_HOLD_2026-07-26.md` as a dated addendum.
- **Next: P1 stays P1.** No new family. The open scope question is
  whether the BTC/ETH effect is a two-asset phenomenon or a
  large-cap-only one; a fourth sleeve must still clear the buy-and-hold
  gate before being proposed.

## 2026-07-27 — iteration 15 (loop, self-paced)

- Answered the scope question left open by iteration 14. New tool:
  `scripts/analyze_symbol_dispersion.py` (zero registry cost, reads local
  candles only).
- **Per-name buy-and-hold across the 13-coin universe is violently
  skewed**: mean 16.09x, median 3.21x. Top 1 name is 32.9% of summed
  return, top 2 is 54.2%, top 3 is **73.7%** (BNB 68.8x, SOL 44.5x, DOGE
  40.8x). Two names lost money outright. **Every name drew down at least
  76%.**
- **The skew story alone does not survive contact with the data.**
  BTC/ETH is MORE top-heavy by top-1 share (BTC 76.9% of that two-name
  sum vs 32.9%), and the rule won there. Concentration does not separate
  the cases.
- **What does: sleeve count.** On 2 names the rule returned 14.26x —
  more than either constituent's own buy-and-hold (9.86x, 2.96x). On 13
  names the best arm returned 9.39x, below the average constituent. The
  measured cause is already on record: independently-exiting sleeves idle
  their share of the book, and the three-sleeve combination sits in 66.2%
  cash (`CASH_AWARE_ALLOCATION_RESULT.md`). Thirteen idle far more.
- **One mechanism now explains three previously separate results**:
  exp 8's 0-of-8, the combination's 3.94x against 5.42x held, and the
  cash-aware refutation. The rule's advantage shrinks as the number of
  independently-exiting sleeves grows — every sleeve buys drawdown
  reduction with compounding. One trade, not three findings.
- **Testable consequence**: a fourth sleeve should cut return again and
  cut drawdown again, which makes the buy-and-hold gate already in the
  contract the binding question rather than a formality.
- Limits recorded: one window; survivorship uncontrolled (2026
  eligibility screen, dead coins absent, benchmarks flattered); and the
  cross-experiment causal claim is inference, since exp 7 and exp 8
  differ in more than sleeve count.
- Written into `REGISTRY_VS_BENCHMARK_2026-07-26.md` as a dated addendum.
- **Next: P1 unchanged.** No new family. If a fourth sleeve is ever
  proposed, this addendum is the prior it has to beat.

## 2026-07-27 — iteration 16 (loop, self-paced): iteration 15 retracted

- Iteration 15 labelled its own central claim "inference, not
  measurement". This iteration measured it. **It failed.**
- **Deployment, measured from `targets[].cash_weight`:** trial 88
  (2 symbols) mean gross **0.3785**; trial 94 (13 symbols) **0.3011**;
  trial 96 (13 symbols, mid-channel) **0.2631**. The gap is real but only
  ~20% relative — it cannot explain a 3.4x swing in benchmark-relative
  performance. **The sleeve-count synthesis is retracted.**
- **Backup hypothesis also refuted.** "Buy-and-hold wins by letting BNB
  and SOL drift to dominate while the ladder re-snaps to equal budgets"
  predicts drift >> rebalanced. Measured across all 13: drift **16.09x**,
  daily-rebalanced equal weight **17.51x**. A wash.
- **A bug was caught before publication.** The first rebalancing
  computation returned 176.27x against a constituent mean of 16.09x.
  Implausible on its face; the loop double-counted cash for unlisted
  names. Rewritten with a sanity check on the six full-history names
  (drift 14.46x, rebalanced 9.04x — sensible) before any number was used.
  **Not reported as a finding at any point.**
- **Corrected reading, simpler and less flattering to the analysis:**
  both books add real timing value over their own exposure. Trial 88
  turned a 6.05x benchmark into 14.26x at 37.9% average exposure; trial
  94 turned a 13.53x benchmark into 9.39x at 30.1%. **Experiment 8 did
  not collapse — its benchmark was 2.2x stronger**, and a
  benchmark-relative test penalises operating in a market that rose more.
- **Methodological consequence for the contract's buy-and-hold gate:** it
  remains the right test for "hold this instead of the asset?", but it is
  NOT a measure of strategy quality across markets. A sleeve can fail the
  gate purely because its market went up a lot. That distinction now
  belongs in any fourth-sleeve pre-registration.
- Second self-retraction in two days, both caught by my own follow-up
  measurement rather than by a reader.
- **Next: P1 unchanged.** No new family.

## 2026-07-27 — iteration 17 (loop, self-paced): the confound-free control

- Iteration 16 identified that "beat buy-and-hold" is confounded by how
  strong the benchmark was. This iteration built the control that removes
  it: `scripts/analyze_timing_value.py` compares each system against a
  **passive twin holding the same asset at the system's own average
  gross exposure** — same time in market, no signal. The twin pays no
  trading costs, so every edge is conservative for the system.

| Book | Expo | System | Twin | Edge | Sys MDD | Twin MDD |
|---|---:|---:|---:|---:|---:|---:|
| crypto t88 (2 sym) | 0.379 | 14.26x | 3.03x | **4.70** | 33.05% | 43.60% |
| crypto t94 (13 sym) | 0.301 | 9.39x | 3.39x | **2.77** | 51.54% | 36.73% |
| taiwan t23 | 0.477 | 2.15x | 2.95x | **0.73** | 30.85% | 30.96% |
| gold t24 | 0.419 | 2.44x | 2.44x | **1.00** | 25.01% | 21.17% |

- **Crypto timing works, in both universes.** 4.70x and 2.77x the twin.
  This **vindicates experiment 8**: it did not fail, it beat its
  exposure-matched twin and only lost the raw comparison because its
  market rose 2.2x more. Iteration 16's correction is confirmed by a
  proper control rather than by argument.
- **Asymmetry not in the system's favour**: on BTC/ETH timing improved
  return AND drawdown; on 13 symbols it improved return but **worsened**
  drawdown (51.54% against 36.73%).
- **Taiwan: timing destroyed value.** 0.73x, at the same drawdown.
  Strictly dominated by holding 47.7% of 0050 continuously.
- **Gold: timing did exactly nothing.** 1.00x, and the twin's drawdown is
  LOWER (21.17% against 25.01%). The sleeve's signal machinery is
  overhead.
- **Consequence for the combination:** it is not one rule working in
  three markets. It is one market where timing works plus two legs
  equivalent to or worse than static partial positions.
- **Free testable prediction, and it is the next step**: replace the gold
  and Taiwan sleeves with static 41.9% GLD and 47.7% 0050 holdings. If
  the three-sleeve result holds or improves, the diversification benefit
  was never about trend-following in those markets — it was about holding
  partially uncorrelated assets, which needs no signal.
- Written up in `TIMING_VALUE_2026-07-27.md`.
- **Next: run that substitution test.** P1 unchanged.

## 2026-07-27 — iteration 18 (loop, first under the step-0 convergence check)

- **Step 0 recorded.** Current answer: timing works in crypto only
  (4.70x/2.77x vs exposure-matched twin), nothing in Taiwan (0.73x) or
  gold (1.00x); best book 14.26x against 13.53x for holding thirteen
  coins, so the search bought drawdown not return; no forward evidence.
  This iteration moves: whether the non-crypto sleeves need their signal
  at all. Not sprawl: closes a route, no new script (extended
  `analyze_sleeve_combination`), no new document (addendum).
- **Prediction from iteration 17 was REFUTED by its own test.** It said
  substituting static holdings "should produce the same or better"
  three-sleeve result. Measured: Sharpe **1.3870 vs 1.4108**, drawdown
  **16.74% vs 14.90%**, multiple **3.74x vs 3.94x**. Worse on all three.
- **The test was biased against the signal and the signal still won**:
  static twins pay no trading costs, the sleeves pay full costs.
- **Both results are true at once.** A sleeve can be worthless standalone
  (Taiwan 0.73x) and still contribute to a book, because a static holding
  is exposed all the time while a trend sleeve is **flat at moments
  uncorrelated with crypto's drawdowns**. That is exactly the mechanism
  `CROSSMARKET_COMBINATION_RESULT.md` named. Static exposure cannot
  reproduce it by construction.
- **Honest size: small.** Sharpe +1.7%, drawdown -11%, wealth +5% against
  the static substitute.
- **Route closed**: "replace the non-crypto sleeves with static holdings"
  is worse; the sleeves stay as systems. Recorded in the contract's
  standing answer so it is not proposed again.
- **Standing answer restated (refined, not overturned):** timing value in
  crypto only, the search bought drawdown rather than return, nothing is
  forward-validated — **and standalone timing value is not the same
  quantity as portfolio timing value**, which this program had been
  conflating.

## 2026-07-27 — iteration 19 (loop, step-0 check passed)

- **Step 0.** Current answer unchanged going in. This iteration moves:
  whether the program's ONLY positive finding (crypto timing edge 4.70x)
  is a stable effect or an artifact of one or two crash episodes. Not
  sprawl: no new script (extended `analyze_timing_value`), no new
  document (addendum), and it attacks the central clause of the standing
  answer.
- **Split uses the four windows already declared** in
  `analyze_sleeve_combination.print_stress`, reused verbatim so the split
  could not be chosen after seeing results.
- **Trial 88 (BTC/ETH): edge > 1 in all four windows** — covid 1.14,
  2022 bear 1.14, 2018-2019 1.91, 2023-2025H1 1.10. Bull, bear, crash and
  mixed. **Not a single-episode artifact.** This is the strongest
  statement this program has made about any finding.
- **Trial 94 (13 symbols): fails both bear windows** — covid 0.98, 2022
  **0.90**, 2018-2019 1.21, 2023-2025H1 1.29. Its whole-window 2.77x is
  regime-dependent: it earns in rising markets and loses to a static
  position in falling ones, which is the opposite of what a trend system
  is for.
- **Gap stated plainly:** the four windows cover 2,005 of 2,676 days
  (74.9%). They do not tile the sample — roughly 671 days from 2020-04 to
  2021-12 are excluded, and that is the largest bull run in it. The
  sub-period edges therefore do not multiply to 4.70x. Extending the
  split would mean picking boundaries after seeing results, which this
  program refuses.
- **Standing answer restated, now with a robustness clause:** timing
  works in crypto only; on BTC/ETH that edge is **positive in all four
  pre-declared sub-periods**, on 13 symbols it is not; the search bought
  drawdown rather than return; standalone and portfolio timing value are
  different quantities; **nothing is forward-validated.**

## 2026-07-27 — iteration 20 (loop, step-0 check passed)

- **Step 0.** Moves the biggest remaining doubt about the only positive
  finding: trial 88 is the MAXIMUM of its 8-member family and PBO is
  0.7411, but the exposure-matched twin had only ever been run on the
  winner. Not sprawl: **zero code change** (`--report` already existed),
  no new script, no new document.
- **Eight of eight family members beat their exposure-matched twin.**
  Edges 3.88 / 4.17 / **4.70 (trial 88)** / 4.15 / 3.84 / 4.16 / 4.08 /
  3.95. Range 3.84-4.70, median **4.115**. The family FLOOR beats its
  twin by 3.84x.
- **Trial 88's selection premium is +14.2%** over a randomly-drawn family
  member. **Selection chose the edge's size, not its existence.**
- **Regime robustness is not unique to the winner either.** Non-winners
  86 and 93, same pre-declared windows: 1.09/1.08/1.89/1.06 and
  1.06/1.37/1.71/1.03 — both positive in all four.
- **Stated against the finding:** the eight are NOT eight independent
  tests. They are a 2x2x2 grid (window set x exit x gate) on the same two
  assets over the same window. "Eight of eight" means no parameter choice
  inside that grid destroys the edge, not that it survived eight separate
  chances to fail. **PBO 0.7411 was measured across distinct
  architectures on Sharpe rankings and remains unanswered.**
- **Method note:** the first run printed correct numbers while returning
  exit code 255. Rerun bare it exits 0 — PowerShell's `Select-Object
  -First` closed the pipe. Numbers were used only after that check. This
  project has been bitten twice by pipes masking exit codes.
- **Standing answer restated:** timing works in crypto only; on BTC/ETH
  the edge is positive in all four pre-declared sub-periods AND all eight
  family members, with a selection premium of only +14.2%; on 13 symbols
  it fails both bear windows; the search bought drawdown rather than
  return; standalone and portfolio timing value differ; **nothing is
  forward-validated and PBO remains unanswered.**

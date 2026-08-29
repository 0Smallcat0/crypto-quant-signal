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

## 2026-07-27 — iteration 21 (loop, step-0 check passed)

- **Step 0.** PBO was the last analytically-addressable item in the
  standing answer. Not sprawl: zero code change (`--representatives`
  already takes an arbitrary trial list), no new script, no new document.
- **PBO per family, eight columns each** — it is NOT degenerate, it
  ranges over 15x:

| Family | PBO |
|---|---:|
| exp-7 donchian BTC/ETH | **0.7415** |
| exp-8 donchian-13 | 0.6830 |
| exp-3 cs-momentum | 0.2789 |
| exp-5 regime gate | **0.0482** |

- **It runs opposite to measured quality.** exp-7's eight members score
  3.84-4.70 against exposure-matched twins — all positive, tightly
  clustered. A four-member sample of exp-5 scores 3.70 / 5.96 / 2.31 /
  1.85 — also all positive, spread 3.2x.
- **Both families have a real edge in every member measured; their PBOs
  differ by 15x.** The separator is dispersion: near-identical members
  make the in-sample best a near coin flip out of sample (high PBO);
  dispersed members make ranking stable (low PBO).
- **So PBO answers "can I trust that I picked the best member?" and says
  nothing about whether the family has an edge.** Used as a gate on edge
  existence it penalises parameter-robust families and rewards
  parameter-sensitive ones. The weakest family by this program's own
  buy-and-hold table is the only one that would PASS gate 3.
- **Self-correction inside the iteration:** exp-5 was picked as a "known
  weak" control from its buy-and-hold ratio. On the exposure-matched
  metric it is not weak. That is the exact confound iteration 17
  identified, biting again in the same session. Recorded rather than
  quietly fixed.
- **Untested, stated:** only 4 of exp-5's 8 members measured on the twin
  metric; exp-3's twin edges not measured at all.
- **Standing answer restated, with PBO now interpreted rather than
  outstanding:** timing works in crypto only; the BTC/ETH edge is
  positive in all four pre-declared sub-periods and all eight family
  members with a +14.2% selection premium; the search bought drawdown
  rather than return; **PBO 0.7415 for that family reflects members being
  indistinguishable, not absence of edge**; **nothing is
  forward-validated**, which is now the only unresolved item.

## 2026-07-27 — iteration 22 (loop, step-0 check passed)

- **Step 0.** Iteration 21 published "PBO tracks dispersion, not edge" on
  only two families. This iteration measured the other two, which could
  have refuted it. Not sprawl: no new script, no new document, tests a
  claim published one iteration earlier.
- **All four families now measured on the same exposure-matched metric:**

| Family | PBO | Twin edges | Spread | Members with edge |
|---|---:|---|---:|---:|
| exp-7 donchian BTC/ETH | **0.7415** | 3.84-4.70 | 1.22x | **8/8** |
| exp-8 donchian-13 | **0.6830** | 2.33-2.92 | 1.25x | **8/8** |
| exp-3 cs-momentum | 0.2789 | 0.04-20.22 | **505x** | **2/8** |
| exp-5 regime gate | 0.0482 | 1.85-5.96 | 3.2x | 4/4 measured |

- **Grouping confirmed, ranking not.** Both tight families have high PBO
  (0.68, 0.74); both dispersed families have low PBO (0.05, 0.28). But
  exp-3 is 150x more dispersed than exp-5 and still scores higher PBO, so
  dispersion explains the split and not the order. n = 4.
- **Sharpest form of the finding:** the two families where EVERY measured
  member has a real exposure-adjusted edge are the two with the WORST
  PBO. The family where only 2 of 8 members have any edge scores BETTER
  than both. **Gate 3 would rank exp-3 as safer than exp-7.**
- **exp-8 clarification:** all 8 members are positive whole-window
  (2.33-2.92) even though iteration 19 found it fails both bear
  sub-windows. Both are true and neither was retracted.
- **My own bug, recorded:** the first exp-8 run exited 1 because a
  PowerShell format string emitted `trial-0000100` instead of
  `trial-000100`. Caught by the exit code, fixed, rerun to exit 0 before
  any number was used.
- **Standing answer unchanged.** Forward validation remains the only
  unresolved item, and it needs time rather than analysis.

## 2026-07-27 — iteration 23 (loop): analytical routes exhausted

- **Step 0 returned "nothing to do", and that is the finding.** Every
  remaining lever is structurally blocked: forward validation needs time,
  the October holdout is operator-only, a new parameter family is refused
  by P3, revising gate 3 after discovering it misranks would be changing
  the rules after seeing results, and further diagnostics would not move
  the standing answer.
- **P1 verified, all three tracks healthy:**
  - `CryptoShadowTrial88` last ran 2026-07-26 08:20:01 result 0, next
    2026-07-27 08:20. Track at 2 rows through 2026-07-25 (one-day lag by
    design — it records the last CLOSED daily candle).
  - `TwShadow0050` shows last=1999-11-30 result=267011, which is
    `SCHED_S_TASK_HAS_NOT_RUN`, not a failure: it was registered on a
    Sunday and its first Saturday is 2026-08-01. 0050 at 1 row, GLD at 1
    row, both written by the manual runs that created them.
  - `CryptoResearchLoop` last ran 2026-07-26 21:37:01 result 0.
- **Contract updated** with a "when the analytical routes are exhausted"
  section, so a fresh-context iteration does not restart the diagnostic
  treadmill. It names the three states that would unblock the work: ~90
  days of forward rows, the October holdout spend, or an operator
  override of P3.
- **Standing answer unchanged**, and this iteration deliberately did not
  try to change it.

## 2026-07-27 — iteration 24 (loop, exhausted state, P1 maintenance)

- **Step 0.** Current answer unchanged from iteration 23 (see standing
  answer). What this iteration moves: nothing analytical — it confirms
  the three forward tracks are still gaining rows and adds two dated
  research-log entries whose only purpose is a calendar anchor for when
  the shadow tracks can first speak. Why not sprawl: **zero new
  scripts, zero new research documents, zero new pre-registrations, and
  no attempt to invent an experiment.** The contract's "when the
  analytical routes are exhausted" clause governs, and its instruction
  is "do P1 maintenance, confirm the three tracks are gaining rows, and
  stop."
- **P1 status, all three tracks:**
  - `CryptoShadowTrial88` — last 2026-07-27 08:20:01 result 0, next
    2026-07-28 08:20. `shadow_trial88.jsonl` at **3 rows** (up from 2 at
    iteration 23), most recent row `date=2026-07-26 close BTC 65399.99
    ETH 1954.72 equity 1006.230318 exposure BTC 0 / ETH 0.5`. New row
    written 2026-07-27 00:20:06 UTC. Track is healthy.
  - `TwShadow0050` — last=1999-11-30 result=267011
    (`SCHED_S_TASK_HAS_NOT_RUN`, per iteration 23 analysis), next
    2026-08-01 09:40 (Saturday). `shadow_tw0050.jsonl` still at 1 row
    and `shadow_gld.jsonl` still at 1 row, both from the manual seeds.
    First scheduled fire has not arrived; nothing to fix.
  - `CryptoResearchLoop` — currently Running (this iteration), previous
    run 2026-07-27 21:37:01 result 0, next 2026-07-28 21:37. Healthy.
- **Web research (contract step 2).** Two dated entries appended to
  `RESEARCH_LOG.md`:
  1. Coin Bureau's 2-4 weeks paper-trading threshold — places a first
     honest read on the shadow tracks no earlier than 2026-08-07, real
     read closer to 2026-08-21.
  2. Multiple aggregator repostings of a 55-day Donchian mid-line
     filter raising BTC daily long-signal win rate ~50% to ~55% — a
     prior consistent with trial 88's mechanism, not testable-here as
     a new experiment (P3 refuses).
- **What was deliberately NOT done, and why:**
  - Did not run any `analyze_*` script — every one would only refine
    an existing document, and Step 0 forbids that.
  - Did not open a new pre-registration — no sleeve candidate has
    passed the P2 buy-and-hold pre-gate on paper, so a pre-reg would
    be premature and would cost an N.
  - Did not touch `configs/runtime/`, the trial registry, or any frozen
    pre-registration.
  - Did not attempt to move the standing answer — it can only be moved
    by data that does not exist yet (~90 days of forward rows, or the
    October holdout, or an operator override of P3).
- **Standing answer restated, unchanged:** timing works in crypto only;
  BTC/ETH edge positive in all four pre-declared sub-periods and all
  eight family members with +14.2% selection premium; PBO 0.7415 for
  that family reflects members being indistinguishable rather than
  absence of edge; on 13 symbols the same edge fails both bear windows;
  the search bought drawdown rather than return; **nothing is
  forward-validated**, and forward validation remains the only
  unresolved item — it needs time rather than analysis.

## 2026-07-28 — iteration 25 (loop, exhausted state broken by a correction)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 24. What this iteration moves: it closes a real hole —
  **the forward tracks were recording with no rule for how they would
  be read** — and, in writing that rule, it found and corrected a
  wrong number in the contract's own roadmap. Why not sprawl: **zero
  new scripts** (all computation done inline against durable return
  series), **one new document, which is a pre-registration and
  therefore records a decision**, and two in-place corrections rather
  than new documents.
- **The hole.** Every queue revision since 2026-07-24 says "keep the
  three forward tracks recording" and "forward evidence is the binding
  constraint". Searching `docs/research/*PRE*` and `docs/contracts/`
  found **no document stating how the tracks would be read**. Reading
  forward data without a pre-declared rule is the exact failure the six
  gates exist to prevent. Written today at **4 rows**, so the data
  cannot have shaped the rule; every day of delay would have made that
  less true.
- **The correction, which is the substantive finding.** The contract
  asserted ~90 days of forward rows would be "enough to say anything at
  all". Measured with MinTRL (Bailey & Lopez de Prado, the same
  machinery as the gate-4 DSR) on the shadowed trials' own durable
  return series:

  | Trial | n | SR_ann | skew | kurtosis | MinTRL 90% | MinTRL 95% |
  |---:|---:|---:|---:|---:|---:|---:|
  | 88 | 2676 | 1.1823 | +0.227 | 12.775 | 429 d (2027-09-26) | **706 d (2028-06-29)** |
  | 118 | 2676 | 1.2413 | +0.157 | 12.980 | 391 d (2027-08-19) | **644 d (2028-04-28)** |

  Forward Sharpe standard error: **N=90 -> 2.016 annualized, 95%
  interval [-2.77, +5.13]**; N=365 -> 1.001, [-0.78, +3.14]. At the
  90-day mark the track cannot distinguish Sharpe -2.7 from +5.1. The
  contract was wrong by roughly a factor of eight and is corrected in
  place.
- **Method self-correction inside the iteration.** The first pass
  annualized with 252 and produced 706 days = 2.80 years. Checking
  against the registry's own recorded `annualized_sharpe` of 1.182061
  showed the program annualizes with **365** (crypto trades every day):
  0.06188 * sqrt(365) = 1.1823, exact match. Redone; 706 days is
  **1.93 years**, not 2.80. The 252 numbers appear in no document.
- **The rule now frozen** (`FORWARD_TRACK_READ_PREREGISTRATION.md`):
  read dates 2026-10-22 / 2027-01-24 / 2027-07-24 / 2028-06-29, none
  movable earlier; **Test 1 implementation agreement** (deterministic,
  full power at any N, and the only thing the 90-day read can settle);
  **Test 2 drawdown breach** as one-sided refutation against the
  recorded 33.05% / 33.24% backtest maxima, with non-breach declared in
  advance as uninformative; **Test 3 return**, refutation permitted but
  **confirmation forbidden until 2028-06-29**. No metric may be added at
  read time.
- **P1 status, all tracks healthy:**
  - `CryptoShadowTrial88` — last 2026-07-28 08:20:01 result 0, next
    2026-07-29 08:20. `shadow_trial88.jsonl` **4 rows** (up from 3),
    latest `date=2026-07-27 close BTC 63755.86 ETH 1892.53 equity
    998.2269 exposure BTC 0 / ETH 0.25`. `shadow_trial118.jsonl` also
    4 rows, equity 1002.9011, exposure 0.5 / 0.5.
  - `TwShadow0050` — next 2026-08-01 09:40, first scheduled fire still
    ahead; `shadow_tw0050.jsonl` and `shadow_gld.jsonl` at 1 row each
    from the manual seeds, as expected. Nothing to fix.
  - `CryptoResearchLoop` — previous run 2026-07-27 21:37:01 result 0,
    next 2026-07-28 21:37. Healthy.
- **What this does NOT do:** no trial registered, no backtest run, no
  holdout touched, no `configs/runtime/` touched, no new family
  proposed, no frozen pre-registration edited, no recorded verdict
  changed.
- **Standing answer, updated:** timing works in crypto only; the BTC/ETH
  edge is positive in all four pre-declared sub-periods and all eight
  family members; the search bought drawdown rather than return;
  nothing is forward-validated — **and the date at which forward
  validation could first return a positive verdict is 2028-06-29, not
  October 2026.** The 2026-10-22 read tests implementation only. The
  operator's levers to move that date are: accept 90% confidence
  (2027-09-26), accept the October holdout as a different question, or
  override P3 to search for a higher-Sharpe design, since MinTRL falls
  with the square of the Sharpe.

## 2026-07-28 — iteration 26 (loop, gate-4 fragility measured)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 25. What this iteration moves: it audits the program's
  single claimed achievement — trial 118's gate-4 pass at DSR 0.950140,
  margin 0.00014 — and converts "thin margin" from an adjective into a
  count. Why not sprawl: **zero new scripts** (imported the program's
  own `deflated_sharpe_ratio` and `non_annualized_sharpe_variance`
  rather than reimplementing), one new document that records a forced
  operator decision and two closed routes, one in-place contract
  refinement.
- **Two dishonesty hypotheses tested FIRST, both refuted.** Neither
  finding was allowed to rest on the margin until the margin was shown
  to be honest.
  - **H1: unregistered arms inflate the true N.** Refuted. Registry by
    experiment: exp-1 1, exp-2..exp-6 16 each, exp-7..exp-10 8 each, 20
    unlabelled early rows = 133. `LOOP_LOG.md:126` says "64 **registered**
    cs-momentum arms" = exp-3..exp-6 at 16 apiece, exactly. Both
    robustness batteries are registered (trials 102-109, 126-133).
    Nothing evaluated is missing from the count.
  - **H2: the pass is an artefact of trial 118's own battery
    compressing cross-trial variance** — a live suspicion, since that
    was the stated reason a 2026-07-25 advance prediction failed.
    Refuted, and backwards: dropping trial 118's own battery gives
    **0.950514**, dropping both batteries gives **0.951257**, both
    higher than the recorded 0.950140. The N reduction outweighs the
    variance increase. **The pass is honest.**
- **The margin, counted:** N=133 -> 0.950140 PASS; **N=134 -> 0.949969
  FAIL**. Because a 134th row shifts the variance as well as the count,
  the real question is whether *any* 134th trial preserves the pass.
  Sweeping its Sharpe: the surviving window is **[0.709, 1.180]**.

  | 134th trial Sharpe | trial 118 DSR | |
  |---:|---:|---|
  | 0.00 | 0.940088 | FAIL |
  | 0.95 (registry mean 0.9444) | 0.950626 | PASS |
  | 1.1823 (trial 88's own) | 0.949988 | FAIL |
  | 1.2413 (trial 118's own) | 0.949630 | FAIL |
  | 2.00 | 0.937298 | FAIL |

  **Finding something as good as what the program already has would
  destroy the pass.** So would something notably worse. Only a mediocre
  134th trial preserves it.
- **This is not a DSR defect.** More search, and more spread among what
  was searched, legitimately raises the bar. The error was this
  program's: "trial 118 passes gate 4" has been quoted as a durable
  property of trial 118, when it is a property of **a search of 133
  configurations that has stopped**.
- **Consequence, and it is a forced choice for the operator.** The
  standing order is 「沒有找到 edge 不准停」. The standing decision since
  2026-07-25 is "no new families" because "the margin cannot absorb
  one." Those were treated as a pause; measured, they are **mutually
  exclusive**. Keep the pass => the crypto registry is frozen at 133 and
  the search is over, not paused. Keep searching => the pass is forfeit
  the moment anything interesting registers, and gate 4 returns to zero
  risk-compliant passers.
- **Counterweight recorded against our own finding** (contract step 2
  web research): the DSR literature's variable is the number of
  **independent** trials, and a raw backtest count overstates search
  breadth because variations are correlated. This program uses the raw
  count by deliberate choice (`run_gate_report.py:188`). Its rows are
  heavily correlated — mean pairwise 0.628, and 64 of 133 are one
  lineage — so a correlation-adjusted N would be below 133 and would
  give trial 118 more margin. **Recorded as a genuine counterweight and
  as a fix that is refused**: adopting it now is changing a gate input
  after seeing the answer it produces, the same move already refused
  over gate 3, and self-serving in a measurable direction.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no holdout touched, no `configs/runtime/` touched,
  trial 118's recorded pass at N=125 and N=133 not retracted — only
  qualified.
- **Standing answer restated, extended:** timing works in crypto only;
  the BTC/ETH edge is positive in all four pre-declared sub-periods and
  all eight family members; the search bought drawdown rather than
  return; nothing is forward-validated and the earliest possible
  forward verdict is **2028-06-29**; **and the single gate-4 pass holds
  only for a search that has stopped — under the frozen N convention
  the program cannot both keep searching in crypto and keep it.**

## 2026-07-28 — iteration 27 (loop, gate audit + same-day correction of iteration 26)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 26. What this iteration moves: it audits the phrase used in
  nearly every document this program has produced — "six-gate
  anti-overfitting framework" — by asking which gates have ever decided
  anything; and in doing so it found that **iteration 26's own reasoning
  was wrong** and corrected it the same day. Why not sprawl: **zero new
  scripts, zero new documents** — the findings are a dated addendum to
  `GATE4_FRAGILITY_2026-07-28.md` plus two in-place contract
  refinements.
- **Correction to iteration 26, in place.** Iteration 26 said adopting
  correlation-adjusted `effective_N` "would be changing a gate's input
  after seeing the answer it produces" and refused it on that basis.
  **Wrong.** `VALIDATION_GATE_CONTRACT.md` — frozen, written before any
  of these results — mandates it at gate 1 line 44: "`effective_N` for
  DSR should account for correlation between trials ... the method used
  must be recorded alongside the number", and line 75 lists `effective_N`
  as a gate-4 input. So `run_gate_report.py:190` passing
  `trial_count = len(trials)` is a **deviation from the contract**,
  conservative on the N axis, with no method recorded — which also means
  gate 1 is not currently fully satisfied.
- **What is actually post-hoc, and why it was still not computed.** Three
  standard methods exist (ONC, hierarchical, spectral). Proper compliance
  clusters trials into K groups, forms an aggregate Sharpe per cluster,
  and takes the variance across **those K Sharpes** — changing *both*
  gate-4 inputs. The variance across K aggregates can be larger or
  smaller than across 133 individual trials, so **the net effect on trial
  118 is unknown, not favourable.** Choosing a method after seeing the
  0.950140 margin is the move that would void the answer, so it was left
  for the operator to declare first. Meanwhile trial 118's pass stands as
  earned under a bar at least as strict as the contract requires.
- **Gate audit — which gates have ever decided a candidate:**

  | Gate | Ever decided a candidate? |
  |---|---|
  | 1 trial registry | No — precondition, and **not currently satisfied** (no `effective_N` method recorded) |
  | 2 data floor >= 1000 days | **No, and cannot** — all 133 trials share one 2676-day window, so `passes: true` by construction |
  | 3 PBO <= 0.05 | **Yes — rejects everything** (0.6518 candidates, 0.7326 all-columns) |
  | 4 DSR >= 0.95 | **Yes — one passer**, trial 118, on a one-trial margin |
  | 5 single-use holdout | No — never executed, nominations fixed |
  | 6 paper trading >= 3 months | No — `GATE6_BASELINE_2026-07-25.md` checkbox still unchecked |

- **The synthesis, which is the finding.** Gates 5 and 6 lying ahead is
  normal and not a defect. What matters is that the two gates which have
  actually exercised judgement over 133 trials **both have recorded
  defects**: gate 3 misranks (iteration 22 — it would call exp-3 with
  2/8 members having edge safer than exp-7 with 8/8), and gate 4 holds
  only for a stopped search (iteration 26). **No document may describe
  this program as having "survived six gates".** Nothing has: gate 3
  fails, and gates 5 and 6 have not been attempted.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, no holdout touched, no
  `configs/runtime/` touched. The contract deviation is **recorded, not
  fixed** — fixing it requires an operator-declared method.
- **Standing answer restated, extended:** timing works in crypto only;
  the BTC/ETH edge is positive in all four pre-declared sub-periods and
  all eight family members; the search bought drawdown rather than
  return; nothing is forward-validated and the earliest possible forward
  verdict is 2028-06-29; the single gate-4 pass holds only for a stopped
  search; **and the framework that produced all of this has exercised
  exactly two gates, both of which are known to be defective in recorded
  ways.**

## 2026-07-28 — iteration 28 (loop, the standing answer's headline sentence was pooling two universes)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 27. What this iteration moves: it audits the single sentence
  this program restates verbatim every iteration — its convergence
  anchor — and finds it compares experiment 7's result against
  experiment 8's benchmark. Why not sprawl: **zero new scripts, zero new
  documents**; a dated addendum to the existing result document plus two
  in-place contract corrections.
- **The defect.** The standing answer reads: "best book 14.26x against
  13.53x for holding thirteen coins, so the search bought drawdown (33%
  vs 86%), not return." **Trial 88 traded BTC and ETH only.** Verified
  against `VS_BUY_AND_HOLD_2026-07-26.md`:

  | Row | System | Benchmark | System MDD | Benchmark MDD |
  |---|---:|---:|---:|---:|
  | line 14 / 143 — **BTC/ETH buy-and-hold** (same universe) | 14.26x | **6.05x** | 33.05% | **80.99%** |
  | line 145 / 166 — **13-coin equal-weight** (cross universe) | 14.26x | 13.53x | 33.05% | 86.22% |

  The 13.53x / 86.22% pair belongs to experiment 8, whose best arm
  returned 9.39x against it. **This is the identical universe-pooling
  error caught and retracted on 2026-07-26**, when "8 of 16 beat
  buy-and-hold, a coin flip" turned out to be 8/8 and 0/8 once the
  experiment number entered the grouping key.
- **The source document contradicts itself and the standing answer
  inherited the wrong half.** `VS_BUY_AND_HOLD_2026-07-26.md` line 19
  states it correctly — "more than doubles buy-and-hold's return while
  cutting the drawdown from 81% to 33%" — and line 171 states the pooled
  version as a mechanism claim, "the system's product is not return."
- **Corrected, split by the question being asked:**
  - **Does the timing rule add value?** Same-universe only. It bought
    **both**: return **14.26x vs 6.05x (+136%)** and drawdown **33.05%
    vs 80.99%**. **"Not return" is false here**, and unnecessary — the
    exposure-matched twin already scores this sleeve 4.70x independently.
  - **Was 133 trials better than the dumbest alternative?**
    Cross-universe is legitimate for this and is the operator's money
    question: **14.26x vs 13.53x, a 5.4% margin**, at 33.05% vs 86.22%.
    Caveats stay attached — the 13-coin universe is
    survivorship-uncontrolled so 13.53x is flattered, and 5.4% is not a
    margin 133 trials can claim credit for. Even here "not return"
    overstates: **mostly drawdown plus a slim return margin**.
- **Web research (contract step 2)** supplied the standard this convicts
  the sentence against: a benchmark must be **appropriate to the
  portfolio's actual universe** and **specified in advance**. The 13-coin
  benchmark for a BTC/ETH strategy fails both.
- **Note on direction.** This correction makes the program look
  **better** than the record said, so it was held to the stricter
  standard: every number was read from the result document's own tables
  rather than from LOOP_LOG prose, and nothing is retracted — only the
  pairing is.
- **What this does NOT do:** no gate rule modified, no frozen
  pre-registration edited, no measured number changed or retracted, no
  trial registered, no backtest run, no holdout touched, no
  `configs/runtime/` touched.
- **Standing answer restated, corrected:** timing works in crypto only,
  and **in its own universe it bought both return and drawdown (14.26x
  vs 6.05x, 33.05% vs 80.99%)**; against the naive 13-coin alternative
  the margin is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails (exp-8 best arm 9.39x vs 13.53x); nothing is
  forward-validated and the earliest possible forward verdict is
  2028-06-29; the single gate-4 pass holds only for a stopped search;
  and the framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 29 (loop, audited the headline metric; it survives)

- **Step 0.** Current answer entering the iteration: as corrected in
  iteration 28. What this iteration moves: it closes two open attacks on
  the **exposure-matched twin**, the metric that replaced the discredited
  buy-and-hold comparison on 2026-07-27 and became the headline number
  ("4.70x") within a single iteration without ever being audited itself.
  Why not sprawl: **zero new scripts, zero new documents** — one dated
  addendum to the existing metric document.
- **Attack 1 — volatility drag.** The twin is built as `w *
  benchmark_return` compounded (`analyze_timing_value.py:139`), i.e. a
  continuously-rebalanced constant mix, which carries a drag the system
  does not. **Refuted.** `log(1 + w*r) > w * log(1 + r)` for both signs
  of r, so partial exposure suffers *less* drag than the asset it tracks
  — the twin is a harder benchmark, not an easier one. Quantified against
  the alternative construction (buy w once, never rebalance, cash
  remainder):

  | Twin construction | Twin multiple | Edge |
  |---|---:|---:|
  | constant-mix, daily rebalanced (**as used**) | 3.03x | **4.71** |
  | un-rebalanced fraction | 2.9121x | 4.90 |

  **4.1% apart, and the one in use is the more conservative.** The
  headline is not a rebalancing artefact.
- **Attack 2 — is it asset selection, not timing?** The twin matches
  time-in-market but not asset mix, and BTC returned 9.86x against the
  equal-weight benchmark's 6.05x, so a rule that merely favoured BTC
  would masquerade as timing value. **Refuted decisively.** Mean
  per-symbol target weight over all 2,677 decision days, from
  `trial-000088/report.json`: **BTC 0.2006, ETH 0.1780** — total 0.3785,
  reproducing the recorded mean exposure 0.379 exactly, and a **53/47
  split against a 50/50 benchmark**. A three percentage point tilt cannot
  produce a 4.70x edge.
- **Route closed.** The twin metric survives audit on both the
  construction it uses and the composition it ignores. Neither question
  may be re-opened without new evidence. Limits unchanged and still
  attached: the twin pays no trading costs while the system pays full
  ones; the twin has no drawdown control (43.60% against 33.05%); and
  none of it is forward evidence.
- **Honest note on iteration value.** This iteration produced no new
  claim — it removed two ways the existing claim could have been wrong.
  That is the intended outcome of an audit, and it is recorded as such
  rather than dressed up as a discovery.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` touched.
- **Standing answer restated, unchanged from iteration 28:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%), **now with the 4.70x twin edge
  audited and robust to +-4% on twin construction and to asset mix**;
  against the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated and the earliest permitted forward verdict is
  2028-06-29; the single gate-4 pass holds only for a stopped search; and
  the framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 30 (loop, look-ahead ruled out; execution latency found unmodelled)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 29. What this iteration moves: five audits had not touched
  the most consequential correctness question in any backtest —
  **look-ahead between signal and fill**. It closes that question and, in
  doing so, exposes a quantified assumption nobody had written down. Why
  not sprawl: **zero new scripts, zero new documents** — one dated
  addendum to the gate-6 document, which is where execution realism
  belongs.
- **Look-ahead: ruled out, and verified empirically rather than from
  code intent.** `src/backtest/engine.py` carries
  `generated_at_bar_close` and `executable_from_next_bar` and executes at
  the next bar's `open_price`. Traced end to end on trial 88's first
  trade: signal `as_of` 2018-03-04T23:59:59.999Z, order `accepted_at`
  2018-03-05T00:00:00Z, fill price **11520.76**. Source candles give
  2018-03-04 close **11515.00** and 2018-03-05 open **11515.00**, and
  `11515.00 x 1.0005 = 11520.7575` — the next bar's open plus exactly the
  modelled 5 bps. **The decision uses nothing after its own bar close.
  Route closed.**
- **The gap the acquittal exposes.** Because crypto is continuous,
  `open[t+1] == close[t]`, so the one-bar lag gives **no price
  protection** — the system fills at the price it decided on. That
  encodes **zero decision-to-execution latency**. The live system is not
  instantaneous: paper runtime 08:05 Taipei = **~5 min** after the 00:00
  UTC bar close; shadow recorder 08:20 Taipei = **~20 min** (confirmed
  from `recorded_at` 2026-07-28T00:20:07Z against `date` 2026-07-27).
- **Quantified.** BTC daily sigma over the backtest window
  (2018-03-05..2025-07-01, n=2675) is **3.4068%**. Scaled by sqrt(t):

  | Horizon | E abs move | vs modelled 5 bps |
  |---|---:|---:|
  | 5 min (runtime) | **16.0 bps** | **3.2x** |
  | 20 min (shadow) | **32.0 bps** | **6.4x** |
  | 60 min | 55.5 bps | 11.1x |

- **Stated honestly, with its limit.** This is **dispersion, not cost** —
  a delay is symmetric in expectation unless the signal correlates with
  the move that follows. The adverse fraction **cannot be measured from
  daily candles**, so no cost number is claimed. But trial 88 is a
  breakout rule, firing exactly when a level has just broken, and the
  transaction-cost literature names breakout and momentum systems as the
  case where delay cost is directional against you. The trial-118
  robustness battery held at 3x cost (~60 bps round-trip); a
  half-adverse 20-minute gap would add ~32 bps round-trip on top,
  pushing toward the edge of what was tested. **The cost model's headroom
  is smaller than the 3x stress suggests, by an amount this program
  cannot currently measure.**
- **This is gate 6's declared job and gate 6 has not run.** Its contract
  requires measuring "notification->execution delay (simulated or
  journaled)"; its "paper period >= 3 months" checkbox is still
  unchecked. This converts a checklist line into a quantified reason to
  run it.
- **Closing it is an operator decision, not a loop action.** Either
  ingest 1m/5m candles and measure the signed drift conditioned on a
  signal firing, or add a bar-close-price and execution-price field to
  the shadow tracks. The second touches a live recording track, so it is
  the operator's call — and if done **now** rather than at a read it
  strengthens Test 1 of `FORWARD_TRACK_READ_PREREGISTRATION.md` instead
  of adding a read-time metric.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` or shadow script touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown (14.26x vs 6.05x,
  33.05% vs 80.99%), with the 4.70x twin edge audited and robust;
  **the engine is free of look-ahead, verified to the cent**; but the
  backtest assumes zero execution latency while the live system runs 5 to
  20 minutes late, a window whose price dispersion is 3 to 6 times the
  modelled slippage and whose adverse component is unmeasured; against
  the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated before 2028-06-29; the single gate-4 pass holds only
  for a stopped search; and the framework has exercised exactly two
  gates, both defective.

## 2026-07-28 — iteration 31 (loop, measured the delay cost iteration 30 called unmeasurable)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 30. What this iteration moves: iteration 30 left the
  execution-latency question as a bound and declared the adverse
  component "unmeasurable from daily candles". **That was wrong**, and
  this iteration measures it. Why not sprawl: **zero new scripts, zero
  new documents** — one dated addendum to the same gate-6 document, using
  data already on disk.
- **The test.** Daily candles carry one usable signal about intraday
  direction: where the **open** sits inside that day's high-low range. If
  price rose after the open, the open sits low in the range, and a
  delayed BUY pays more. All 669 fills were matched to their
  execution-day candle:

  | Group | n | mean open-in-range | delta vs baseline | t | implied drift |
  |---|---:|---:|---:|---:|---:|
  | BUY fill days | 331 | 0.4910 | **-0.0167** | **-0.99** | **-8.8 bps** |
  | SELL fill days | 338 | 0.5038 | -0.0040 | -0.25 | -2.4 bps |
  | all days baseline | 6484 | 0.5077 | — | — | — |

- **Result: the predicted signature is there on buys, and it is not
  significant.** BUY-day opens sit 1.67pp lower in range than typical —
  the breakout continuation signature — at **t = -0.99**. And **SELL days
  lean the favourable way**: an open low in the range means a delayed
  sell gets a *better* price, worth +2.4 bps. **Net round-trip point
  estimate about -6.4 bps**, against 10 bps of modelled round-trip
  slippage and ~40 bps of headroom the trial-118 battery demonstrated at
  3x cost. **Inside what was already stress-tested.**
- **Second correction to iteration 30.** Its sqrt(t) scaling assumed
  uniform intraday volatility. Crypto volatility peaks at **14:00-16:00
  UTC** and declines after **20:00 UTC**; the execution window is
  **00:00-00:20 UTC**, the quiet part of the day. So the 16 bps and
  32 bps dispersion figures are **overestimates**, not neutral scalings.
- **What this does not establish, stated plainly.** With sd 0.3070 and
  n=331 the 95% detectable deviation for buys is **~17.4 bps**, so this
  rules out adverse drifts larger than that and **cannot resolve the
  measured -8.8 bps from zero**. And open-in-range describes a 24-hour
  bar, not the first 5-20 minutes — it is evidence about direction, not a
  substitute for intraday data. **The concern is narrowed to "under 17
  bps and probably much less", not closed.**
- **Method note against self-flattery.** This iteration's result makes
  the program look better than iteration 30 implied, so the limits above
  are stated in the same breath as the numbers, and the "narrowed, not
  closed" verdict is the one that goes into the standing answer.
- **What this does NOT do:** no gate rule modified, no trial registered,
  no backtest run, no number retracted, no holdout touched, no
  `configs/runtime/` or shadow script touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown (14.26x vs 6.05x,
  33.05% vs 80.99%), with the 4.70x twin edge audited and robust; the
  engine is free of look-ahead, verified to the cent; **the execution-
  latency gap iteration 30 raised is now measured at about -6.4 bps
  round-trip point estimate, bounded above by ~17 bps, and inside the
  cost headroom already stress-tested** — narrowed, not closed, and gate
  6 remains the way to close it; against the naive 13-coin alternative
  the margin is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; nothing is forward-validated before 2028-06-29;
  the single gate-4 pass holds only for a stopped search; and the
  framework has exercised exactly two gates, both defective.

## 2026-07-28 — iteration 32 (loop, holdout integrity verified; one hazard found)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 31. What this iteration moves: seven audits had not touched
  **gate 5**, and the October holdout is the one clean evidence this
  program has reserved. If it were already contaminated it would be
  worthless before being spent, and nobody had checked. Why not sprawl:
  **zero new scripts**; one new document, justified because it records a
  verification the operator needs before spending the holdout and has no
  existing home (`PRE_HOLDOUT_PROTOCOL.md` is frozen and was not edited).
- **Verified clean at the trial level.** `data/candles` runs to
  2026-07-02 (3242 rows); `data/candles_preholdout` stops at 2025-07-01
  (2876 rows), exactly one day before `holdout_start`
  2025-07-02T23:59:59.999Z. The decisive check is the registry, not
  script intent: **all 133 registered trials have `data_end` =
  2025-07-01, and zero cross the boundary.** About 366 days of holdout
  exist to spend and `spent` is still `false`. **Gate 5 is intact as
  written.**
- **Hazard: the lock is convention, not mechanism.** All ten
  trial-registering scripts (`run_alloc_family`, `run_atr_family`,
  `run_combo_family`, `run_cs_family`, `run_donchian13_family`,
  `run_donchian_family`, `run_gate_family`, `run_robustness_trial88`,
  `run_robustness_trial118`, `run_trendfactor_family`) default to
  `data/candles_preholdout` — but nothing *prevents* passing
  `--candles-dir data/candles`. The guarantee rests on ten argparse
  defaults staying correct, not on the engine refusing to read past
  `holdout_start`.
- **Soft contamination found and recorded before October, not after.**
  `analyze_symbol_dispersion.py:30` and `analyze_whipsaw.py:129` default
  to the **full** series, and `WHIPSAW_DIAGNOSTIC.md:84` documents a run
  over candles spanning 2024-01 to 2026-06 — crossing the boundary. That
  diagnostic's verdict placed the hysteresis experiment first in Goal P.
  **This is not a gate-5 violation** (gate 5 binds trials, and no trial
  read it), but the adaptive-data-analysis literature is explicit that a
  researcher merely *considering* a result computed on reserved data
  creates a formal dependency the classical theory does not cover.
- **Magnitude, not minimised.** The whipsaw statistic is signal churn
  frequency, **not** strategy P&L, so it cannot reveal whether trial 88
  or 118 made money after 2025-07-01 and cannot have tuned them toward
  holdout returns. What it could do — and did — is nudge **research
  priority**. Weak channel, real channel, and it belongs on the record
  now rather than surfacing after the October result, when it would read
  as an excuse.
- **Three operator decisions named:** carry this caveat into the October
  result document; optionally make the lock mechanical (engine refuses
  `open_time >= holdout_start` without an explicit `--spend-holdout`);
  and repoint the two diagnostics at `candles_preholdout` by default,
  which costs nothing and closes the channel for future work.
- **What this does NOT do:** the holdout was **not read** — only
  `holdout_lock.json` metadata, row counts and date boundaries were
  inspected. No gate rule modified, no frozen contract edited, no trial
  registered, no backtest run, nominations unchanged, `spent` still
  `false`, no `configs/runtime/` touched.
- **Standing answer restated, extended:** timing works in crypto only and
  in its own universe bought both return and drawdown; the 4.70x twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is measured at about -6.4 bps
  round-trip point estimate, bounded above by ~17 bps, inside tested
  headroom; **the October holdout is verified unread by any trial and
  still has ~366 days available, with one soft-contamination channel now
  on the record**; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails; nothing is forward-validated before 2028-06-29; the single
  gate-4 pass holds only for a stopped search; and the framework has
  exercised exactly two gates, both defective.

## 2026-07-28 — iteration 33 (loop, first code change in nine iterations: holdout channel closed)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 32. What this iteration moves: eight consecutive iterations
  produced observations. Iteration 32 found a live hazard and named three
  fixes, one of which is purely protective — and I filed it under
  "operator decides", which on re-reading was **over-cautious**. It
  touches no runtime, no engine, no contract, no registry, and can only
  *reduce* holdout exposure. Why not sprawl: **zero new scripts** — one
  default changed, one test added.
- **Correction to iteration 32, in place.** That entry listed
  `analyze_symbol_dispersion.py` and `analyze_whipsaw.py` together as
  reading the full series. **Wrong for the first.**
  `analyze_symbol_dispersion` defaults `--end` to `_END = date(2025, 7, 1)`
  — exactly the holdout boundary — so it reads `data/candles` but
  truncates before `holdout_start` and was **safe all along**. Only
  `analyze_whipsaw` was genuinely unbounded: it has no date argument, so
  its `--candles-dir` default was the entire exposure.
- **Fix.** `scripts/analyze_whipsaw.py` now defaults to
  `data/candles_preholdout`, with the reason written at the argument.
  `first_month`/`last_month` were already emitted, so a future run that
  widens the window explicitly still records what it read. Locked in by
  `tests/scripts/test_analyze_whipsaw.py::test_default_candles_dir_is_the_preholdout_slice`
  so it cannot regress silently.
- **Verification, run bare.** ruff check 0, ruff format --check 0
  (127 files), mypy --strict 0 (58 source files), lint-imports 0
  (13 contracts kept), **pytest -m "not network": 379 passed**. The
  trailing `PermissionError` in the pytest output is its own Windows
  temp-directory cleanup at interpreter exit, after the run completed —
  not a test failure.
- **What is not undone.** The whipsaw verdict that placed hysteresis
  first in Goal P was formed on a window crossing the boundary. Changing
  the default prevents recurrence; it does not retract history. **That
  caveat still travels to October.**
- **Operator decisions 1 and 2 remain open** — carry the caveat into the
  October result document, and optionally make the lock mechanical in the
  engine. A literature search for programmatic holdout-enforcement
  patterns returned little of substance (mostly LLM guardrail tooling),
  so decision 2 would be a from-scratch design rather than adopting a
  known pattern. Empty search result recorded rather than padded.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read,
  nominations unchanged, `spent` still `false`, no `configs/runtime/`
  and no family runner touched.
- **Standing answer restated, unchanged in substance from iteration 32:**
  timing works in crypto only and in its own universe bought both return
  and drawdown; the 4.70x twin edge is audited and robust; the engine is
  free of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip point estimate, bounded above by ~17 bps,
  inside tested headroom; the October holdout is verified unread by any
  trial with ~366 days available, **its one soft-contamination channel is
  now closed at the source though the historical caveat stands**; against
  the naive 13-coin alternative the margin is only 5.4% and that
  benchmark is survivorship-flattered; breadth still fails; nothing is
  forward-validated before 2028-06-29; the single gate-4 pass holds only
  for a stopped search; and the framework has exercised exactly two
  gates, both defective.

## 2026-07-28 — iteration 34 (loop, iteration 32's central claim retracted)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 33. What this iteration moves: nine audits asked whether the
  holdout is clean; none asked whether the code that **spends** it works.
  October is a one-shot irreversible operation that has never executed.
  Why not sprawl: **zero new scripts, zero new documents** — one dated
  addendum, and it is mostly a retraction of my own earlier work.
- **Hypothesis tested and refuted.** Suspected an irreversible-loss bug:
  if the lock is marked spent **before** the run, a crash burns the
  single-use holdout for nothing. It is not a bug — `spend_holdout`'s
  docstring states the design outright: "The spend is recorded BEFORE the
  qualification run executes: if the run crashes, the holdout stays spent
  (conservative by doctrine)." Deliberate and documented.
- **RETRACTION: iteration 32's central claim was wrong.** That entry said
  "the lock is convention, not mechanism ... the guarantee rests on ten
  defaults staying correct, not on the engine refusing to read past
  `holdout_start`." **False.** `src/backtest/runner.py` — the single
  registered entry point every family runner uses — trims
  unconditionally:

  ```python
  run_candles = {
      symbol_value: tuple(
          candle for candle in candles if candle.close_time < holdout.holdout_start
      )
  ```

  **Passing `--candles-dir data/candles` to a family runner would not
  leak the holdout.** The reason all 133 trials carry `data_end` =
  2025-07-01 is this trim, not luck with argparse. This is exactly the
  framework-level enforcement the leakage literature prescribes —
  "architectural level rather than relying on manual implementation".
  **Operator decision 2 from iteration 32 ("make the lock mechanical") is
  VOID: it already is.**
- **The October procedure is covered by six tests**, including the trim
  itself (`test_registered_run_locks_holdout_trims_data_and_registers_trials`),
  double-spend rejection, future-dated candles being unable to anchor
  `holdout_start` years ahead, isolated holdout-segment metrics, and the
  boundary-day move not being dropped.
- **What survives, and it matters.** Iteration 33's fix was the real
  hole: diagnostics like `analyze_whipsaw` read candle files **directly**
  and never call `run_registered_backtest`, so the trim never protected
  them. **Trials were mechanically safe all along; diagnostics were
  not.** The soft-contamination history — the whipsaw verdict that placed
  hysteresis first in Goal P — is untouched by this correction and still
  travels to October.
- **How iteration 32 went wrong, named plainly.** It inferred a mechanism
  claim from **ten argparse defaults without reading the runner they feed
  into**. That is asserting instead of measuring, the same failure this
  program has caught in itself before (the retracted 0.9+ correlation
  claim, the retracted sleeve-count synthesis, the pooled-universe
  headline). Three of iteration 32's statements have now needed
  correction across two iterations.
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read,
  nominations unchanged, `spent` still `false`, no code changed this
  iteration.
- **Standing answer restated, one clause strengthened:** timing works in
  crypto only and in its own universe bought both return and drawdown;
  the 4.70x twin edge is audited and robust; the engine is free of
  look-ahead, verified to the cent; execution-latency cost is about
  -6.4 bps round-trip, bounded above by ~17 bps, inside tested headroom;
  **the October holdout is protected mechanically by the runner's trim,
  not by convention, and its spend path is covered by six tests** —
  ~366 days remain, `spent` is false, and the one real leak channel
  (diagnostics) was closed in iteration 33 though its historical caveat
  stands; against the naive 13-coin alternative the margin is only 5.4%
  and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 35 (loop, Taiwan verdict closed; audit route declared converged)

- **Step 0, with a warning raised rather than buried.** Two of the
  previous three iterations corrected **my own recent work** rather than
  finding anything new (32 was wrong, 34 retracted it). That is precisely
  the diminishing-returns signal Step 0 exists to detect. This iteration
  targets the last substantive standing-answer claim never checked at
  source, then reports honestly on whether the route should continue.
  Zero new scripts, zero new documents.
- **Hypothesis: the Taiwan verdict is a dividend artefact.** 0050 pays
  ~3-4% a year; over 2018-03 to 2025-07 that compounds ~30%, enough to
  overturn "timing adds none in Taiwan (0.73x)" if the system and its
  benchmark treated dividends differently.
- **Refuted structurally.** The Taiwan `src/backtest/engine.py` derives
  the benchmark from the same candles the system trades:
  `benchmark_open_prices = dict(open_prices)` taken from
  `execution_candles`, then
  `growth += budget * close_prices[s] / benchmark_open_prices[s]`.
  One series feeds both sides, so adjusted-versus-raw shifts them
  **together** and no relative distortion is possible. This iteration
  deliberately did **not** resolve which series is used, because the
  conclusion does not depend on it.
- **Any residual error is conservative.** The system is ~30% invested
  against a 100%-invested benchmark, so missing dividends would
  understate the **benchmark** more, making the Taiwan loss look
  *smaller* than truth. The recorded verdict is correct or too kind, not
  an artefact. **Route closed.**
- **P1 status: nothing due, nothing missing.** `shadow_trial88` 4 rows,
  `shadow_trial118` 4 rows, next fire 2026-07-29 08:20; `shadow_tw0050`
  and `shadow_gld` 1 row each, first scheduled fire 2026-08-01.
- **Convergence declaration: the audit route opened at iteration 25 is
  converged.**

  | Iteration | Outcome |
  |---:|---|
  | 25 | **Finding** — forward-validation timetable wrong by ~8x; MinTRL 2028-06-29 |
  | 26 | **Finding** — the gate-4 pass survives only a stopped search |
  | 27 | **Finding** — only 2 of 6 gates ever adjudicated, both defective |
  | 28 | **Finding** — the headline sentence pooled two universes |
  | 29 | Refuted two attacks; metric survived |
  | 30 | Acquittal on look-ahead, plus one new gap |
  | 31 | **Finding** — that gap measured and de-escalated |
  | 32 | **Partly wrong** |
  | 33 | Fix (the one real hole) |
  | 34 | **Retraction of 32** |
  | 35 | Refuted; route closed |

  The last genuinely new finding was iteration 31. Four of the last five
  iterations produced refutations, fixes, or corrections of my own work.
  By Step 0's own criterion the route is worked out.
- **What the loop should do next.** None of the three unblocking states is
  reachable by analysis: forward rows need time (2028-06-29 for a return
  verdict), the October holdout is operator-only, and P3 refuses new
  families. The remaining mode is **P1 maintenance** — confirm the four
  tracks gain rows, correct anything found wrong, and stop manufacturing
  work. Two operator items remain, both narrowed by iteration 34: carry
  the whipsaw soft-contamination caveat into the October result, and
  optionally repoint `analyze_symbol_dispersion` for tidiness (it is
  already date-bounded, so this is cosmetic, not protective).
- **What this does NOT do:** no gate rule modified, no frozen contract
  edited, no trial registered, no backtest run, holdout not read, no code
  changed, nominations unchanged.
- **Standing answer restated, unchanged in substance:** timing works in
  crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is audited and
  robust; the engine is free of look-ahead, verified to the cent;
  execution-latency cost is about -6.4 bps round-trip, bounded above by
  ~17 bps, inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; **the Taiwan
  and gold negatives are robust to dividend treatment and if anything
  understated**; against the naive 13-coin alternative the margin is only
  5.4% and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 36 (loop, P1 maintenance only — first post-convergence iteration)

- **Step 0.** Current answer entering the iteration: unchanged from
  iteration 35. What this iteration moves: **it advances nothing new by
  design.** Iteration 35 declared the audit route converged; the
  contract's own guidance (line 182) is "do P1 maintenance, confirm the
  three tracks are gaining rows, and stop. Do not manufacture a
  diagnostic in order to have something to commit." This iteration tests
  whether the loop will honour that instruction rather than drift back
  into diagnostic-generation. Zero new scripts, zero new documents, one
  dated addendum to `RESEARCH_LOG.md`.
- **P1 status — all four tracks green.** Verified by direct read of the
  jsonl files and today's shadow-run log:

  | Track | Rows | Last date | Next fire | Today's run |
  |---|---:|---|---|---|
  | `shadow_trial88` (crypto BTC/ETH, source trial 88) | 4 | 2026-07-27 | 2026-07-29 08:20 | exit=0 at 08:20:07+08 |
  | `shadow_trial118` (crypto BTC/ETH, source trial 118) | 4 | 2026-07-27 | 2026-07-29 08:20 | exit=0 at 08:20:07+08 |
  | `shadow_tw0050` (Taiwan 0050, source trial 23) | 1 | 2026-07-24 | 2026-08-01 09:40 (weekly Sat) | not scheduled today |
  | `shadow_gld` (US GLD, source trial 24) | 1 | 2026-07-23 | 2026-08-01 09:40 (weekly Sat) | not scheduled today |

  Nothing broken, nothing due. The two weekly tracks are three days from
  their first non-seed row; if that fire fails on Saturday it becomes
  P1 obligation of iteration 37 or 38.
- **Step 2 (web research) done and recorded** — three passes, two
  actionable-adjacent papers (Han/Kang/Ryu SSRN 4675565 on crypto
  momentum under realistic assumptions, Huang/Sangiorgi/Urquhart SSRN
  4825389 on volume-weighted TSMOM). Both are blocked by P3 (no new
  single-market families). Filed in `RESEARCH_LOG.md` so the same
  searches are not re-issued. Third consecutive iteration with no
  directly-actionable literature under the P1-only constraint.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract edited, no trial registered, no backtest run, holdout not
  read, `spent` still `false`, no code changed, no diagnostic script
  written, no research document created. Verification (rule 7) not run
  because no source file changed — consistent with iterations 34-35.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is audited and
  robust; the engine is free of look-ahead, verified to the cent;
  execution-latency cost is about -6.4 bps round-trip, bounded above by
  ~17 bps, inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; the Taiwan
  and gold negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin is only
  5.4% and that benchmark is survivorship-flattered; breadth still fails;
  nothing is forward-validated before 2028-06-29; the single gate-4 pass
  holds only for a stopped search; and the framework has exercised
  exactly two gates, both defective.

## 2026-07-28 — iteration 37 (session loop, handoff verification and shutdown)

- **Purpose: verify the unattended mechanism, then hand off.** Iteration
  35 declared the audit route converged; iteration 36 (this session)
  deliberately committed nothing so the nightly headless run could own
  that number cleanly. This iteration checks whether it did.
- **Verified, end to end and correct.** `CryptoResearchLoop` fired
  2026-07-28 21:37:01, exit 0, finished 21:41:24 (~4 minutes),
  `docs/research/loop_runs/run_20260728_213701.log`. It:
  - numbered itself **iteration 36**, with no collision;
  - read the convergence declaration and did **P1 maintenance only**,
    recording the standing answer "unchanged in every clause";
  - performed contract step 2 independently, surfacing SSRN 4675565
    (crypto momentum under realistic assumptions) and SSRN 4825389
    (volume-weighted TSMOM), and **correctly judged both blocked by P3**;
  - named its own next P1 obligation — confirm the 2026-08-01 Saturday
    fire appends a second row to the TW and GLD tracks;
  - committed `de0cb9d` and pushed. `origin/main` and local are both at
    `de0cb9d`, 0 ahead / 0 behind.
- **Operator decision, 2026-07-28: the session loop is stopped.** The
  reason is not fatigue and not diminishing returns in the abstract — it
  is that the free nightly mechanism was demonstrated tonight to do the
  same job correctly, so a paid session loop iterating the same contract
  on a converged route is strictly redundant. Research does not stop; it
  moves to the leg that costs nothing.
- **What continues unattended:**
  - `CryptoResearchLoop` — daily 21:37, one contract iteration.
  - `CryptoShadowTrial88` — daily 08:20, writes `shadow_trial88.jsonl`
    and `shadow_trial118.jsonl` (4 rows each).
  - `TwShadow0050` — Saturdays 09:40, first fire **2026-08-01**; both
    `shadow_tw0050.jsonl` and `shadow_gld.jsonl` still at their 1-row
    manual seeds, which is expected, not a fault.
- **Open items that need the operator, not the loop:**
  1. Carry the whipsaw soft-contamination caveat into the October
     holdout result document (`HOLDOUT_INTEGRITY_2026-07-28.md`).
  2. If an earlier answer date than 2028-06-29 is wanted, the only lever
     is a P3 override toward a higher-Sharpe design — MinTRL falls with
     the square of the Sharpe. The cost is trial 118's gate-4 pass, which
     fails at N=134 (`GATE4_FRAGILITY_2026-07-28.md`).
  3. Optionally repoint `analyze_symbol_dispersion` at the pre-holdout
     slice. Cosmetic only — it is already date-bounded to 2025-07-01.
- **Standing answer at handoff, unchanged:** timing works in crypto only
  and in its own universe bought both return and drawdown (14.26x vs
  6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin edge is
  audited and robust to twin construction and asset mix; the engine is
  free of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside tested
  headroom; the October holdout is protected mechanically by the runner's
  trim, unread by all 133 trials, with ~366 days available and its spend
  path covered by six tests; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth fails;
  **nothing is forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**; the single gate-4 pass
  holds only for a stopped search; and the six-gate framework has
  exercised exactly two gates, both with recorded defects.

## 2026-07-30 — iteration 38 (nightly headless, P1 maintenance)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iteration 37 handoff: timing
     works in crypto only; in its own universe it bought both return
     (14.26x vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no forward-based
     return verdict is statistically permitted before **2028-06-29**;
     the single gate-4 pass on trial 118 holds only for a stopped
     search; the six-gate framework has exercised only gates 3 and 4,
     both with recorded defects; the audit route is declared
     converged (iteration 35).
  2. **What this iteration moves.** Confirms the three continuing
     unattended tracks (crypto x2, weekly TW+GLD) are still gaining
     rows on schedule, and records that yesterday's nightly loop
     (2026-07-29 21:37) crashed with an upstream API
     `ConnectionRefused` before it could number itself as an
     iteration. Names no new decision; closes no route.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable to "confirm rows"), no new document,
     no gate rerun, no trial registered. Under contract's
     analytical-routes-exhausted clause the correct behaviour is
     "do P1 maintenance, confirm three tracks are gaining rows,
     and stop" — this iteration does exactly that.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Last date | Next fire | Today |
  |---|---|---:|---|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 6 (5 real + seed) | 2026-07-29 | 2026-07-31 08:20 | wrote 2026-07-30 at 08:20:07+00 (equity 999.44) |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 6 (5 real + seed) | 2026-07-29 | 2026-07-31 08:20 | wrote 2026-07-30 at 08:20:07+00 (equity 1006.23) |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed) | 2026-07-26 | 2026-08-01 09:40 (Sat) | not scheduled today |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 1 (seed) | 2026-07-26 | 2026-08-01 09:40 (Sat) | not scheduled today |

  Nothing broken, nothing due. The two weekly tracks are still
  two days from their first non-seed row; if Saturday's fire
  misses, that becomes P1 obligation of iteration 39 or 40.
  Iteration 36's own next-P1 obligation ("confirm 2026-08-01
  Saturday fire appends a second row to TW and GLD") is carried
  forward unchanged.
- **Nightly loop failure recorded, not fixed here.** The
  `CryptoResearchLoop` scheduled task fired 2026-07-29 21:37:01,
  ran ~3 minutes, and exited 1 —
  `docs/research/loop_runs/run_20260729_213701.log` contains a
  single line: `API Error: Unable to connect to API
  (ConnectionRefused)`. No LOOP_LOG entry was written, no
  iteration was numbered, and no source file changed, so the
  research state is uncorrupted. This is a transient upstream
  outage (Claude API), not a repo defect; iteration 37 explicitly
  named this exact failure mode as an acceptable one because a
  missed nightly does not touch the frozen artefacts. Not
  escalating unless it recurs — a second consecutive miss would
  need operator attention on the scheduled task's Claude
  invocation.
- **Step 2 (web research) done and recorded.** Three passes,
  one new-looking finding (arXiv 2602.11708 — adaptive-allocator
  trend-following on 150+ crypto pairs, headline SR 2.41) which
  P3 refuses because it is a simultaneous universe-and-family
  expansion; two other passes returned DSR restatements and
  practitioner blog posts already known. Filed in
  `RESEARCH_LOG.md` under iteration 38. **Fourth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint — signal that the binding constraint is
  forward rows, not literature.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed, no
  diagnostic script written, no research document created,
  no pre-registration touched. Verification (rule 7) not run
  because no source file changed — consistent with iterations
  34-37.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought
  both return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%);
  the 4.70x twin edge is audited and robust; the engine is free
  of look-ahead, verified to the cent; execution-latency cost
  is about -6.4 bps round-trip, bounded above by ~17 bps,
  inside tested headroom; the October holdout is protected
  mechanically and its spend path is covered by six tests; the
  Taiwan and gold negatives are robust to dividend treatment
  and if anything understated; against the naive 13-coin
  alternative the margin is only 5.4% and that benchmark is
  survivorship-flattered; breadth still fails; **nothing is
  forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**; the single
  gate-4 pass holds only for a stopped search; and the
  framework has exercised exactly two gates, both defective.

## 2026-07-31 — iteration 39 (P1 maintenance, on-chain route awaits operator hypothesis lock)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iteration 38. Timing works
     in crypto only; own universe bought both return (14.26x vs
     6.05x) and drawdown (33.05% vs 80.99%); the 4.70x exposure-
     matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; audit route declared converged (iteration 35).
  2. **What this iteration moves.** Declares in one place what the
     unnumbered `ba0b99f` ("Open the on-chain route: source
     inventory, no strategy", 2026-07-30 22:39) opened but did not
     close: the on-chain route is now standing, no hypothesis lock
     exists, and the contract's own queue block ("Queue as of
     2026-07-26 (latest)") does not yet mention it. Records that
     iteration 39 will NOT write an on-chain pre-registration
     unilaterally — that is a substantive hypothesis choice and
     needs an operator order. Route remains open; next actionable
     step is operator-scoped, not Claude-scoped.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable), no new research document, no gate rerun,
     no trial registered, no edit to `AUTONOMOUS_RESEARCH_LOOP.md`
     or any frozen contract. The LOOP_LOG entry records a
     decision (defer the on-chain pre-reg to operator hypothesis
     order); under Step 0's document rule "no new research
     document unless it records a decision or a closed route", a
     LOOP_LOG entry that records a defer-decision is inside the
     rule, not outside it. Under contract's analytical-routes-
     exhausted clause the correct behaviour absent an operator
     order is P1 maintenance — this iteration does exactly that.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Dates covered | Today's fire |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 7 (6 real + seed) | 2026-07-24 .. 2026-07-30 | wrote 2026-07-30 row at 01:31:46 UTC = 09:31 local, equity 999.9328, exposure `{BTC: 0, ETH: 0.25}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 7 (6 real + seed) | 2026-07-24 .. 2026-07-30 | wrote 2026-07-30 row at 01:31:46 UTC = 09:31 local, equity 1010.3542, exposure `{BTC: 0.5, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed) | 2026-07-24 (seed) | not scheduled today; next fire 2026-08-01 09:40 Sat |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 1 (seed) | 2026-07-23 (seed) | not scheduled today; next fire 2026-08-01 09:40 Sat |

  Two accounting corrections to iteration 38's own numbers,
  read directly from the jsonl:

  - Iteration 38 said trial88 wrote a 2026-07-30 row at
    08:20:07+00 UTC with equity 999.44. The jsonl shows the
    999.4365 equity attaches to the row for **date 2026-07-29**
    written at UTC 2026-07-30 00:20:07; the row for **date
    2026-07-30** was written today at UTC 01:31:46 with equity
    999.9328. Same-shift, off-by-one date label in iteration 38.
  - Same off-by-one for trial118: 1006.226 is the 2026-07-29 row
    (not 2026-07-30 as iteration 38 said); the 2026-07-30 row
    was written today at UTC 01:31:46 with equity 1010.3542.

  Two schedule observations for the record, not acted on:

  - Today's crypto shadow fire ran at 09:31 local (01:31 UTC),
    not the previous 08:20 local (00:20 UTC) documented in six
    prior `shadow_runs/shadow_YYYYMMDD_082001.log` files. The
    schedule shifted between 2026-07-30 08:20 local and today.
    No `.log` from 08:20 today exists, so the earlier scheduled
    task either did not fire or was replaced. Either way the row
    was written before any decision would consume it. Not a
    defect; recording so a future missed fire is diagnosed
    correctly.
  - `shadow_tw0050` last row is dated 2026-07-24 (seed) and
    `shadow_gld` last row is dated 2026-07-23 (seed). Both are
    still at their iteration-38 state. Iteration 36's carried-
    forward obligation ("confirm 2026-08-01 Saturday fire
    appends a second row to TW and GLD") lands on iteration 40
    or 41 depending on when the nightly loop fires next.
- **On-chain route: standing but unadvanced today, and why.**
  `ONCHAIN_SOURCE_INVENTORY_2026-07-29.md` opened the route with
  four decisions locked before any fit: keyless Coin Metrics
  community API is the source; genuinely non-price metrics are
  the ten listed (`AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`,
  `TxTfrCnt`, `FeeTotNtv`, `IssTotNtv`, `HashRate`, `FlowInExNtv`,
  `FlowOutExNtv`, `SplyExNtv`); every on-chain input lags D-1
  because completion is 3.02-3.18 h after UTC day close;
  validation moves from level agreement (unusable, median ratio
  1.391) to daily-change correlation ≥ some floor (measured
  +0.8729 on `AdrActCnt` vs blockchain.com over 1337 days).
  What the inventory explicitly did not decide: which metric or
  metric-combination to test, in which direction, against what
  passing threshold, with what N-budget cost against the gate-4
  fragility (a 134th trial would break trial 118's DSR pass unless
  its Sharpe fell inside [0.709, 1.180], per
  `GATE4_FRAGILITY_2026-07-28.md`). Writing that pre-registration
  is a substantive hypothesis choice, and the standing goalpost-
  drift guard at contract line 344-347 restricts Claude from
  authoring a next pre-registration in an iteration that reads
  prior state absent explicit operator order in the same sitting.
  No such order exists in today's input. **Iteration 39 therefore
  does not touch the on-chain route.** Options for iteration 40+
  when the operator decides: (a) close by refusing to spend
  registry N; (b) issue a hypothesis-scope order (which metric,
  which direction, which pass criterion) and let a subsequent
  iteration write the pre-reg; (c) hand the pre-reg authorship
  to a human. All three are legitimate under the contract; the
  ambiguity is not.
- **Step 2 (web research) done and recorded.** Three passes:
  practitioner exchange-netflow narratives (accumulation vs
  distribution language, no peer-reviewed backtest with realistic
  costs); active-address predictive signal (one MDPI 2026 paper
  using ML crisis-period features — P3 refuses on parameter-
  family grounds); MVRV backtest search — TradingView scripts and
  Coin Bureau guide, one useful negative line ("neither MVRV nor
  other popular indicators has survived a rigorous backtest
  across all historical cycles as a reliable standalone signal")
  which corroborates the standing answer. Filed in
  `RESEARCH_LOG.md` under iteration 39. **Fifth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint. The web-research signal is consistent —
  the binding constraint is forward rows plus operator hypothesis
  authority, not literature.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed, no
  diagnostic script written, no research document created, no
  pre-registration touched, on-chain ingestion not started.
  Verification (rule 7) not run because no source file under
  version control changed except this log entry itself and
  `RESEARCH_LOG.md` — consistent with iterations 34-38.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought
  both return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%);
  the 4.70x twin edge is audited and robust; the engine is free
  of look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside
  tested headroom; the October holdout is protected mechanically
  and its spend path is covered by six tests; the Taiwan and gold
  negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; **nothing is forward-validated and no
  return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped
  search; and the framework has exercised exactly two gates,
  both defective. New line, dated 2026-07-31: the on-chain route
  is opened but unadvanced — inventory locked, pre-registration
  awaits operator hypothesis order.

## 2026-08-03 — iteration 40 (P1 maintenance, TW shadow broken, two research-loop misses recorded)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-39. Timing works
     in crypto only; own universe bought both return (14.26x vs 6.05x)
     and drawdown (33.05% vs 80.99%); the 4.70x exposure-matched twin
     edge is audited and robust; no return-based forward verdict is
     statistically permitted before **2028-06-29**; trial 118's gate-4
     pass holds only for a stopped search; the six-gate framework has
     exercised only gates 3 and 4, both with recorded defects; audit
     route declared converged (iteration 35); on-chain route open but
     unadvanced pending operator hypothesis lock.
  2. **What this iteration moves.** Records four facts read directly
     from source files, none changing the standing answer: (a) the TW
     0050 shadow is BROKEN — still at 1 seed row from 2026-07-24
     because the Saturday 2026-08-01 09:40 fire hit a TWSE
     `STOCK_DAY` ingest error and never reached the 0050 append step;
     (b) the GLD shadow gained its first non-seed row (2026-07-31,
     close 371.54, exposure 0) on 2026-08-01 09:55 local — one branch
     of the Sat fire worked, the other did not; (c) the daily crypto
     shadow missed its 2026-08-02 08:20 fire, caught up today at
     00:53 local writing the 2026-08-01 row late — no dates dropped
     but the schedule is drifting; (d) the nightly research loop
     missed BOTH 2026-08-01 21:37 and 2026-08-02 21:37 firings —
     iteration 39 named a second consecutive miss as the point that
     needs operator attention, so this is now flagged. This iteration
     is 00:53 local, i.e. today's recovery firing.
  3. **Why it is not sprawl.** No new script (checked the ten:
     none applicable — the TW ingest bug lives in `D:/TW-Stock-Trading`,
     a separate repo, and this loop's iron rule 1 forbids touching
     the live runtime side); no new research document; no gate rerun;
     no trial registered; no edit to any frozen contract; the LOOP_LOG
     entry records observations and one P1 escalation
     (operator-attention flag on TW shadow + research-loop scheduler),
     which is inside Step 0's rule "no new document unless it records
     a decision or a closed route" because the escalation IS a
     decision — defer fix to operator since the fix lives outside
     this repo's boundary. Under contract's analytical-routes-
     exhausted clause the correct behaviour is P1 maintenance; that
     is exactly what this iteration does.
- **Track state, verified from source files, not memory.**

  | Track | Path | Rows | Dates covered | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 9 (8 real + seed) | 2026-07-24 .. 2026-08-01 | OK — today's 00:53 local fire wrote 2026-08-01 row late (recorded_at 2026-08-02T16:53:28+00:00), equity 996.30, exposure `{BTC: 0, ETH: 0}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 9 (8 real + seed) | 2026-07-24 .. 2026-08-01 | OK — same fire wrote 2026-08-01 row, equity 993.28, exposure `{BTC: 0, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 1 (seed only) | 2026-07-24 (seed) | **BROKEN** — 2026-08-01 09:40 Sat fire failed at TWSE `STOCK_DAY` step; log at `tw_shadow_20260801_094000.log` shows `python.exe : backfill failed: STOCK_DAY returned stat = '...'` (Chinese error garbled by PowerShell encoding). Corporate-actions and calendar refreshed 19063 events, TWSE month sweep began but the 0050 append never ran. Next scheduled Sat 2026-08-08 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 2 (1 real + seed) | 2026-07-23 (seed), 2026-07-31 (real) | OK — 2026-08-01 09:55 local wrote 2026-07-31 row, close 371.54, exposure 0, `WINDOWS_ON_0_OF_4` |

  Iteration 39's carried obligation — "confirm 2026-08-01 Saturday
  fire appends a second row to TW and GLD" — is resolved as **half
  pass, half fail.** GLD passed. TW failed and needs operator repair
  in the sibling repo before the next Sat fire is meaningful.
- **Nightly research loop schedule state.** `docs/research/loop_runs/`
  is missing files for 2026-08-01 21:37 and 2026-08-02 21:37 —
  contiguous with `run_20260731_213701.log` (last successful) and
  `run_20260803_005325.log` (this iteration). Two consecutive misses
  crosses iteration 39's escalation threshold. This is a scheduler
  problem, not a Claude API outage: the 2026-07-29 miss (recorded in
  iteration 38) had a `ConnectionRefused` line inside its log file;
  the 08-01/08-02 slots produced no log file at all, meaning the
  scheduled task itself did not fire. Not fixing here — the task is
  registered under Windows Task Scheduler outside this repo's
  operational boundary (`data/runtime/shadow_runs/task_registered.txt`
  references it) and operator attention is the correct next step.
- **Runtime-side commits noted, not touched.** Commits `8d9ce67`
  (2026-07-31, "Wire the Donchian ensemble into the live runtime")
  and `2423bf6` (2026-07-31, "Switch the live signal to trial 118")
  landed on main between iteration 39 and today. Iron rule 1 forbids
  iterations from touching the live paper contract; these commits
  are operator-attributed and inside the runtime side, so they do
  not violate the rule. Recorded here so a future audit can see that
  the shadow tracks now read from a live runtime that itself has
  been switched to the trial-118 configuration (`atr_multiple: 2`,
  `exit: atr_channel`) — the shadow trial88 file continues to write
  its own trial-88 numbers (`atr_multiple: 3`, `exit: mid_channel`),
  so the two are still parallel unbiased signals as long as the
  daily shadow driver stays configured against both trials. Verified
  from the shadow rows above that both configs are being written
  side-by-side.
- **Step 2 (web research) done and recorded.** Three passes filed in
  `RESEARCH_LOG.md` under iteration 40: (i) arXiv 2209.05559 (crypto
  DRL overfitting, 2022 crash cohort) — corroborates PBO framework
  but adds no directly-testable rule; (ii) exchange-flow predictive
  research (arXiv 2411.06327 + practitioner data ~48,500 BTC net
  outflow in the 30 days ending early April 2026) — directly relevant
  to on-chain route but P3-blocked until operator locks a hypothesis
  (metric/direction/threshold); (iii) MinTRL and walk-forward
  literature — corroborates the 706-day MinTRL number on trial 88
  and Quantpedia's 33%/44% Sharpe degradation OOS finding, both
  already inside the standing answer's caveats. **Sixth consecutive
  iteration** with no directly-actionable literature under the
  P1-only constraint. Consistent with iterations 35/37/38/39.
- **What this iteration does NOT do:** no gate rule modified, no
  frozen contract edited, no trial registered, no backtest run,
  holdout not read, `spent` still `false`, no code changed in either
  repo, no diagnostic script written, no research document created,
  no pre-registration touched, on-chain ingestion not started, TW
  shadow bug not fixed (operator boundary). Verification (rule 7)
  not run because no source file under version control changed
  except this log entry and `RESEARCH_LOG.md` — consistent with
  iterations 34-39.
- **Standing answer restated, unchanged in every clause:**
  timing works in crypto only and in its own universe bought both
  return and drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the
  4.70x twin edge is audited and robust; the engine is free of
  look-ahead, verified to the cent; execution-latency cost is
  about -6.4 bps round-trip, bounded above by ~17 bps, inside
  tested headroom; the October holdout is protected mechanically
  and its spend path is covered by six tests; the Taiwan and gold
  negatives are robust to dividend treatment and if anything
  understated; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails; **nothing is forward-validated and no
  return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped
  search; and the framework has exercised exactly two gates, both
  defective. On-chain route open but unadvanced. New operator-
  attention items, dated 2026-08-03: (a) TW 0050 shadow ingest
  broken since 2026-08-01, needs operator repair in
  `D:/TW-Stock-Trading` before Sat 2026-08-08 fire; (b) nightly
  research loop scheduled task missed 2026-08-01 and 2026-08-02
  slots with no log emission, indicating Task Scheduler misfire
  rather than in-process outage.

## 2026-08-15 — iteration 42 (P1 maintenance after an 11-night loop outage; iteration 40's root cause corrected)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-40. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** It closes the question "why has
     this loop produced nothing since 2026-08-03?" with a root cause
     read from log files rather than inferred, and it **corrects
     iteration 40's answer to that same question**, which named the
     wrong cause. It also resolves iteration 40's open obligation on
     the Taiwan track, records a permanent hole in the crypto forward
     record with the arithmetic needed to bound its damage, and repairs
     two verification defects that made contract rule 7 unrunnable as
     written.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a scheduler-auth outage or to a jsonl gap). No new
     research document. No gate rerun, no trial registered, no
     pre-registration touched, no frozen contract edited. Two config
     lines changed in `pyproject.toml`, both purely to make the
     contract's own verification command execute; no source or research
     content altered. Under the analytical-routes-exhausted clause the
     prescribed behaviour is P1 maintenance, and every item here is P1.
- **Root cause of the outage, and a correction to iteration 40.** The
  nightly `CryptoResearchLoop` task (registered 2026-07-21, daily
  21:37) **did fire** on 2026-08-04, 08-05, 08-06, 08-07, 08-09, 08-11,
  08-12 (21:53), 08-13 and 08-14. Every one of those runs is a 480-byte
  log containing exactly one error and an exit code:

  ```
  Failed to authenticate. API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"OAuth access token has expired. Re-authenticate to continue."},"request_id":null}
  exit=1
  ```

  Four extra daytime retries (2026-08-11 09:48 and 15:19, 08-12 17:53,
  08-13 09:58) failed identically. The 2026-08-03 21:37 and 2026-08-08
  21:37 logs are 0 bytes; the 2026-08-10 21:37 slot produced no file at
  all. **Net: zero completed iterations from 2026-08-04 to 2026-08-14,
  eleven nights.** Iteration 40 recorded the cause as "Task Scheduler
  misfire rather than in-process outage". For the outage that followed
  **that is wrong** — the task fires reliably and the agent cannot
  authenticate. Corrected here per the standing correction duty. The
  2026-08-01 and 2026-08-02 slots remain fileless and therefore still
  unexplained; they are a separate, earlier symptom and are not
  evidence for the auth diagnosis.
- **Orphaned iteration 41, committed unedited.** `RESEARCH_LOG.md`
  carried an uncommitted `## 2026-08-03 — iteration 41` block (four
  sources: arXiv 2602.11708, arXiv 2510.23150, arXiv 2603.20319, and
  the DSR literature) with **no** LOOP_LOG entry and no commit. That
  iteration completed step 2 and died before step 5 — consistent with
  the 0-byte 2026-08-03 21:37 log. It is committed today exactly as
  written, keeps the number 41, and today's work is numbered 42, so the
  numbering stays auditable rather than being silently reused.
- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Dates covered | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 21 (20 real + seed) | 2026-07-24 .. 2026-08-14, **2026-08-09 missing** | OK — last row 2026-08-14 written 2026-08-15T00:20:05.804828+00:00, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0}` |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 21 (20 real + seed) | 2026-07-24 .. 2026-08-14, **2026-08-09 missing** | OK — last row 2026-08-14 written 2026-08-15T00:20:05.836265+00:00, equity 994.7655928691401162549420727, exposure `{BTC: 0.25, ETH: 0.5}` |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-07-24 (seed), 08-07, 08-11, 08-12, 08-14 | **REPAIRED** — last row 2026-08-14 written 2026-08-15T01:49:32.325851+00:00, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-07-23 (seed), 07-31, 08-07, 08-10, 08-11, 08-14 | OK — last row 2026-08-14 written 2026-08-15T01:49:32.462409+00:00, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 |

  Iteration 40's operator-attention item (a) — the Taiwan 0050 ingest
  broken since 2026-08-01 — is **resolved**. The Saturday fires of
  2026-08-08 and 2026-08-15 both appended (01:49 UTC = 09:49 local),
  and two extra runs on 08-11 and 08-12 added rows as well. **Forward
  evidence accumulated normally throughout the loop outage**: the
  shadow drivers are separate scheduled tasks and never depended on the
  research agent.
- **One permanently lost forward row, and what it cost.** No
  `shadow_20260810_0820*.log` exists, so the 2026-08-10 08:20 fire did
  not run and the **2026-08-09** row was never written; the next run
  (2026-08-11 09:48 local) wrote the 2026-08-10 row and did **not**
  backfill. The gap is left as-is: fabricating a row after the fact
  would corrupt an append-only forward record, which is the one clean
  evidence stream this project still has. Damage bounded by arithmetic
  on trial 118, the only track that was exposed. From the 2026-08-08
  row (equity 1002.9901337, BTC 64962.60, ETH 1916.74) to the
  2026-08-10 row (BTC 63970.01, ETH 1873.16): BTC -1.5279%, ETH
  -2.2737%; at the driver's per-symbol weighting (exposure divided by
  the two symbols) the two-day portfolio return is **-0.759406%**,
  predicting equity **995.373370** against **995.373372** recorded. So
  the driver compounds from the last recorded close and the missing day
  **did not distort the equity path**. What was lost is at most one
  exposure update dated 2026-08-09, and it is unrecoverable.
- **Verification (rule 7) run bare, and two defects repaired to make it
  runnable.** `ruff format --check` failed on
  `docs/research/VS_BUY_AND_HOLD_2026-07-26.md:271` because **ruff
  0.16.2 now formats Python blocks inside Markdown** and wanted to
  restyle a source excerpt quoted verbatim in a recorded result
  document. Editing that document to satisfy a formatter would violate
  iron rule 3, so `*.md` was added to `[tool.ruff] exclude` instead — a
  formatter must never rewrite append-only records. Separately,
  `pytest -m "not network"` failed collection in **36 modules** with
  `ModuleNotFoundError: No module named 'src'`, because bare `pytest`
  resolves to the system Python 3.12 on PATH, which has neither the
  editable install nor the repo root on `sys.path`; `pythonpath = ["."]`
  was added to `[tool.pytest.ini_options]` so the command in rule 7
  works as written under any interpreter. Results after both fixes, all
  run bare: `ruff check` **All checks passed!**; `ruff format --check`
  **128 files already formatted** (exactly the 128 tracked `.py`
  files); `mypy --strict src/` **Success: no issues found in 58 source
  files**; `lint-imports` **Contracts: 13 kept, 0 broken** over 81 files
  and 325 dependencies; `pytest -m "not network"` **383 passed** in
  125.10s. Tree green.
- **Step 2 (web research) done and recorded.** Three passes filed in
  `RESEARCH_LOG.md` under iteration 42: (i) arXiv **2607.19453**
  (Jadouli, 2026-07-21) — the closest external match to this project's
  product law yet found (Binance **spot**, daily and 4h candles,
  **long-only**, costs charged at 31 bps per cycle) and a registered
  **negative**: "every operational decision remains NO_TRADE", ten-pair
  daily selector -6.72% over 19 cycles, ROC AUC 0.874-0.896 against
  average precision 0.116-0.134. Recorded as an external base rate, not
  as a strategy; (ii) *Order flow and cryptocurrency returns* (J. Emp.
  Fin., S1386418126000029, 2026-01) — order flow claimed to have
  out-of-sample predictive power surviving short-sale constraints and
  high costs; adjacent to but **not** the same as the open on-chain
  route (exchange order flow, not on-chain netflow), and its numbers
  are **unverified at source** (publisher 403, working-paper PDF TLS
  failure) so they may not be quoted in a result document yet; (iii)
  e-values / anytime-valid inference — **pre-refused** as a route to
  reading the forward tracks before 2028-06-29, because
  anytime-validity buys permission to look, not evidence, and is
  strictly less powerful than the fixed-sample test at the same date.
  **Eighth consecutive iteration** with no directly-actionable
  literature under the P1-only constraint.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no runtime or `configs/runtime/` file touched, no shadow row
  fabricated or backfilled, on-chain ingestion not started.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-15: (a) **the
  nightly research loop cannot authenticate** — every scheduled run
  from 2026-08-04 to 2026-08-14 exited 1 on an expired OAuth token, and
  it will keep doing so until the credential is refreshed on the
  machine that runs the task; there is no in-repo fix; (b) the
  2026-08-10 08:20 crypto shadow fire never ran, costing the 2026-08-09
  row permanently — if that slot misses again the driver's scheduling
  needs operator inspection; (c) iteration 40's item (a), the Taiwan
  ingest break, is closed.

## 2026-08-16 — iteration 43 (P1: the shadow track's scheduling defect found, fixed, and one missed row recovered inside its 24h window)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-42. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** It closes iteration 42's open
     operator-attention item (b) — "the 2026-08-10 08:20 crypto shadow
     fire never ran; if that slot misses again the driver's scheduling
     needs operator inspection". It missed again on 2026-08-16. The
     cause is now identified from the task definition rather than
     inferred, **fixed at its source in this repo**, and the row that
     the miss would have destroyed was recovered before it became
     unrecoverable. Forward rows are the only evidence this program can
     still add, so a defect that silently deletes them is the highest
     P1 item there is.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a Task Scheduler settings defect). No new research
     document. No gate rerun, no trial registered, no backtest, no
     pre-registration or frozen contract touched. Two registration
     scripts changed, both to make an existing scheduled task actually
     fire. Under the analytical-routes-exhausted clause the prescribed
     behaviour is P1 maintenance; every item here is P1.
- **The miss, from the task itself.** Before any change,
  `Get-ScheduledTaskInfo CryptoShadowTrial88` reported `LastRunTime
  2026-08-15 08:20:01`, `LastTaskResult 0`, **`NumberOfMissedRuns 1`**
  and `NextRunTime 2026-08-17 08:20`. No `shadow_20260816_*.log` exists
  in `data/runtime/shadow_runs/`. So the 2026-08-16 08:20 slot was
  **dropped by the scheduler, not failed by the driver** — the same
  signature as 2026-08-10.
- **Root cause, and it was in this repo all along.**
  `scripts/register_shadow_task.ps1` built the task with a bare
  `New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit
  20m`. That cmdlet's **defaults** are `WakeToRun=$false`,
  `DisallowStartIfOnBatteries=$true`, `StopIfGoingOnBatteries=$true`,
  and the task was registered with a single daily trigger. Verified on
  the live task before the fix: `StartWhenAvailable True, WakeToRun
  False, DisallowStartIfOnBatteries True, StopIfGoingOnBatteries True,
  ExecutionTimeLimit PT20M, triggers 1`. This machine is a laptop
  (`Win32_Battery` reports device `L23M4PK4`, 76% charge), so any 08:20
  where the machine is asleep or on battery is dropped, and the
  `StartWhenAvailable` catch-up is itself blocked while on battery.
  **The live 08:05 runtime task hit exactly this failure on 2026-07-07
  and was fixed then** — `scripts/harden_daily_task.ps1` and
  `docs/RUNBOOK_DAILY_CYCLE_RELIABILITY.md`. Confirmed by comparison:
  `CryptoQuantDailySignalCycle` today has `WakeToRun True,
  DisallowStartIfOnBatteries False`, and it caught its own missed 08:05
  up at 12:32:04 on 2026-08-16, on the same machine, on the same
  morning the shadow task was dropped. The hardening was simply never
  applied to the two research-side tasks.
- **Evidence quality, stated honestly.** The mechanism above is read
  from task settings plus `System` power events (kernel power manager
  shutdown transitions at 00:20:06, 05:31:06 and 05:32:05 on 2026-08-16,
  then no system activity recorded until 12:30:17 — the 08:20 slot falls
  inside that gap). It is **not** read from a per-launch record, because
  `Microsoft-Windows-TaskScheduler/Operational` is **disabled** on this
  machine (`IsEnabled False`), so no "did not launch because ..." event
  exists for either miss. The settings defect is certain; which of
  asleep-versus-on-battery applied on a given morning is inference.
- **The row was recovered, and the recovery window is 24 hours.**
  `scripts/run_shadow_track.ps1` was run manually at 2026-08-16 21:42:04
  local (`shadow_20260816_214200.log`, `exit=0`) and appended the
  **2026-08-15** row to both tracks — 22 rows each now. It could do this
  only because `scripts/shadow_signal.py` appends the latest *closed*
  daily candle, and at 13:42 UTC on 08-16 that candle was still 08-15.
  Had the fix waited until after tomorrow's 08:20 fire, the 08-15 row
  would have been lost exactly the way the **2026-08-09** row was lost
  (iteration 42): the driver appends one day and never backfills.
  **A missed slot is therefore recoverable for about 24 hours and
  permanently lost after that** — worth knowing before the next miss.
- **The recovered row, verified against its source.** trial 88:
  `date 2026-08-15`, exposure `{BTCUSDT: 0, ETHUSDT: 0}`, equity
  `993.7564267590065144761572415` — unchanged, correctly, because the
  08-14 exposure was zero. trial 118: exposure `{BTCUSDT: 0.25,
  ETHUSDT: 0.5}`, closes `BTCUSDT 63086.01`, `ETHUSDT 1882.64`, equity
  `994.9074566318213201893273399`. Recomputed independently from the
  08-14 row (equity `994.7655928691401162549420727`, closes
  `63043.56` / `1882.20`) at the driver's per-symbol budget of 0.5:
  day return `0.000142610242752802864757661375`, predicted equity
  `994.9074566318213201893273399`, **difference 0E-25**. The equity
  path is intact across the miss.
- **Fix applied, and deliberately not applied uniformly.**
  `scripts/register_shadow_task.ps1` now registers the task with
  `-WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries`
  plus at-logon and on-unlock catch-up triggers (2-minute delay each),
  mirroring the runbook's three lines of defense. The unlock trigger is
  safe here **because the driver is idempotent** — `append_day` returns
  early when the last recorded date is already >= the latest closed
  candle — so an extra fire is a no-op. The script was re-run and the
  live task verified: `StartWhenAvailable True, WakeToRun True,
  DisallowStartIfOnBatteries False, StopIfGoingOnBatteries False,
  ExecutionTimeLimit PT20M, MultipleInstances IgnoreNew`, three triggers
  (daily 08:20, logon +2m, session-unlock +2m), `NextRunTime
  2026-08-17 08:20`. The OS-level gate `WakeToRun` depends on is already
  on from 2026-07-07: `powercfg` reports allow-wake-timers `0x00000001`
  on both AC and DC. **`RestartCount` was considered and refused** —
  `run_shadow_track.ps1` always exits 0 (it logs Python's exit code
  instead of propagating it), so a restart-on-failure setting could
  never fire.
- **`scripts/register_research_loop_task.ps1` carried the identical
  defect and is fixed the same way, minus the catch-up triggers.**
  `CryptoResearchLoop` also had `WakeToRun False,
  DisallowStartIfOnBatteries True, StopIfGoingOnBatteries True`. This is
  a **consistent explanation for the 2026-08-01 and 2026-08-02 fileless
  21:37 slots that iteration 42 left unexplained** — not a proven one,
  for the same reason as above (operational log disabled). Logon and
  unlock triggers were **not** added to this task: the shadow driver is
  idempotent but a research iteration is not — every fire writes a
  LOOP_LOG entry and consumes a working session, so unlock-triggered
  catch-up would manufacture duplicate iterations. One fire per day.
  The task's live settings are updated after this entry is committed,
  because the task is *currently running this iteration* and a
  definition rewrite mid-run risks killing it before step 5 completes —
  which is precisely how iteration 41 was orphaned.
- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 22 (21 real + seed) | 2026-08-15, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0}` | OK — 2026-08-09 still permanently missing (iteration 42) |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 22 (21 real + seed) | 2026-08-15, equity 994.9074566318213201893273399, exposure `{BTC: 0.25, ETH: 0.5}` | OK — same single 2026-08-09 hole |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-08-14, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 | OK — weekly; `TwShadow0050` next fire 2026-08-22 09:40, last result 0, missed 0 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-08-14, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 | OK — same weekly task |

- **Loop health.** `docs/research/loop_runs/run_20260815_213702.log` is
  3230 bytes (iteration 42, successful) and today's
  `run_20260816_213701.log` is this run. The OAuth expiry that killed
  eleven consecutive nights (2026-08-04 .. 2026-08-14, iteration 42) is
  resolved on the operator's side; this is the **second consecutive**
  successful scheduled fire.
- **Step 2 (web research) done and recorded.** Four passes filed in
  `RESEARCH_LOG.md` under iteration 43: (i) Li, Zhang and Zhou, *J.
  Futures Markets* 37(12) 2017 — trend rules beat buy-and-hold in
  Chinese commodity **futures**, robust to costs, with the authors'
  own data-snooping caveat; out of product law (futures), filed only as
  the closest external analogue to this project's own P2
  beat-buy-and-hold gate; (ii) **a widely-repeated Bitcoin volatility
  statistic that failed source verification** — "daily standard
  deviation ~5.3% in 2021 falling to ~2.1% in 2024-2025", attributed to
  State Street; the SSGA page (published 2026-02-03) was fetched and
  contains **no such numbers**, only a qualitative downward-trend claim
  on two-year rolling weekly returns, and the S&P Global piece returned
  HTTP 403. The pair is now **banned from this project's documents**.
  The underlying question — whether the 2018-2025 measurement came from
  a volatility regime that no longer exists — is real and testable here,
  and is deliberately **not** run, because under Step 0 it would be a
  diagnostic with no decision attached; (iii) arXiv 2602.11708 resurfaced
  and is **not** re-filed (already logged in iteration 41; its H6
  rebalance is outside the daily product law); (iv) practitioner claims
  that daily rebalancing is cost-dominated — inapplicable, since this
  book makes a daily *decision*, not a daily *rebalance*. **Ninth
  consecutive iteration** with no directly-actionable literature under
  the P1-only constraint.
- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed** in 50.05s.
- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no `configs/runtime/` or live-runtime file touched, **the live 08:05
  task's definition not touched** (iron rule 1 — only the two
  research-side tasks were changed), no shadow row fabricated, and the
  2026-08-09 hole left as a hole.
- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-16: (a)
  iteration 42's item (b) is **closed** — cause found, fixed in
  `scripts/register_shadow_task.ps1`, task re-registered, and the row
  it cost recovered; (b) iteration 42's item (a), the loop's OAuth
  expiry, is **closed** — two consecutive successful nightly fires;
  (c) **new, low priority:** `Microsoft-Windows-TaskScheduler/Operational`
  is disabled on this machine, which is why both shadow misses had to be
  diagnosed by inference; enabling it would make the next scheduling
  failure self-documenting.

## 2026-08-19 — iteration 44 (P1: both missed slots explained from evidence; the loop's own log made self-documenting)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-43. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** Two scheduled iterations, 2026-08-17
     and 2026-08-18, produced no LOOP_LOG entry and no commit. This
     iteration gives each a **verified cause** rather than a
     hypothesis, and then closes the class: the loop's own log now
     distinguishes "killed mid-run" from "never started" without
     forensic work, and the Task Scheduler Operational channel — open
     as operator-attention item (c) since iteration 43 — is enabled, so
     the next scheduling failure documents itself. Three consecutive
     iterations have now had to diagnose a miss by inference from
     indirect evidence; this one removes the need.
  3. **Why it is not sprawl.** No new script (the ten were checked;
     none applies to a logging or event-channel defect). No new
     research document. No gate rerun, no trial registered, no
     backtest, no pre-registration or frozen contract touched. One
     existing script gained a start marker and an append redirect; one
     OS event channel was enabled. Under the analytical-routes-
     exhausted clause the prescribed behaviour is P1 maintenance, and
     every item here is P1.

- **2026-08-17: refused at the door, not killed.**
  `docs/research/loop_runs/run_20260817_213701.log` is **218 bytes** and
  reads, in full, that the account had hit its weekly usage limit
  (resetting 8am Asia/Taipei), followed by `exit=1
  finished=2026-08-17T21:37:19.1612042+08:00`. The iteration therefore
  started at 21:37:01 and died **18 seconds later** on an account usage
  limit. This is operator-side and outside the loop's control; the same
  class as the eleven-night OAuth outage of iteration 42, but a
  different mechanism (quota, not authentication). No repo change can
  prevent it.

- **2026-08-18: a working iteration killed by an operator reboot.**
  `run_20260818_213702.log` is **0 bytes with no `exit=` line at all**,
  which under the old script means the redirect created the file and
  the process died before anything was flushed *and* before the
  trailing status line could be appended. The Windows **System** log
  supplies the mechanism directly:

  | Time | Event | Content |
  |---|---|---|
  | 2026-08-18 21:37:02 | (log file created) | iteration starts |
  | 2026-08-18 21:52:48 | `User32` **1074** | `StartMenuExperienceHost.exe (SMALLCAT)` initiated the **restart** of computer SMALLCAT **on behalf of user** `smallcat\Administrator`, reason `其他 (不在計劃之中)` |
  | 2026-08-18 21:52:57 | `Kernel-Power` **109** | kernel power manager initiated a shutdown transition |
  | 2026-08-18 21:53:09 | `Hyper-V-Hypervisor` **1** | hypervisor started (machine back up) |

  The iteration ran **15 minutes 46 seconds** and was then terminated
  by an operator-initiated restart from the Start menu. **This is the
  same failure mode that orphaned iteration 41**, and it is not a
  defect: the operator may reboot their own machine whenever they like.
  What was defective was that the evidence had to be reconstructed from
  a system log at all.

  **Two hypotheses were considered and are refuted, not merely
  unfavoured.** (i) *Scheduler settings*, the cause found in iteration
  43 for the shadow task — refuted by inspecting the live task, which
  already carries iteration 43's hardening: `WakeToRun True`,
  `StartWhenAvailable True`, `DisallowStartIfOnBatteries False`,
  `StopIfGoingOnBatteries False`. So iteration 43's fix **was**
  applied to the live `CryptoResearchLoop`, and it is not the
  explanation here. (ii) *`ExecutionTimeLimit` expiry* — the limit is
  `PT6H`, which from a 21:37 start expires at 03:37, long after the
  21:52 shutdown. Task state today: one daily trigger at 21:37,
  `RestartCount 0`, `NextRunTime 2026-08-20 21:37`,
  `NumberOfMissedRuns 0`.

- **Fix: the loop's log now says which of the two happened.**
  `scripts/run_research_loop.ps1` writes `started=<ISO-8601>` before
  invoking the agent and appends the agent's output with `*>>` instead
  of truncating with `*>`. From the next fire onward the three
  signatures are distinct and need no event log: a file with
  **neither** marker means the task never launched; **`started=` with
  no `exit=`** means an interrupted iteration; **both** means it ran to
  completion and the exit code says how it ended. The rewritten script
  was parse-checked (`PSParser.Tokenize`, zero errors) but deliberately
  **not** executed — running it would launch a second concurrent
  iteration on top of this one. It takes effect at the 2026-08-20
  21:37 fire.

- **Operator-attention item (c) from iteration 43 closed.**
  `Microsoft-Windows-TaskScheduler/Operational` was still
  `IsEnabled=False`, which is why the 2026-08-09, 2026-08-16 and
  2026-08-18 misses all had to be diagnosed indirectly. It is now
  **enabled** (`wevtutil sl ... /e:true`, exit 0; verified
  `IsEnabled=True`, `MaximumSizeInBytes=10485760`, `LogMode=Circular`).
  Circular at 10 MB, so it self-trims and cannot fill the disk. This is
  a diagnostic channel on the operator's machine, not a change to the
  trading system, and it is reversible with `/e:false`.

- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 25 (24 real + seed) | 2026-08-18, equity 993.7564267590065144761572415, exposure `{BTC: 0, ETH: 0.25}`, closes 64725.42 / 1917.85 | OK — +3 rows since iteration 43 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 25 (24 real + seed) | 2026-08-18, equity 1002.796755227646803154754684, exposure `{BTC: 0.25, ETH: 0.5}` | OK — +3 rows since iteration 43 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-08-14, close 106.40, exposure 0.75, equity 1015.741494790171164002006047 | OK — weekly; next fire 2026-08-22 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-08-14, close 401.480011, exposure 0.5, equity 1003.784962641249894625805519 | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-18 with **exactly one
  date gap, 2026-08-08 to 2026-08-10** — the permanently lost
  2026-08-09 row from iteration 42. No new holes opened during the two
  missed research iterations, which is the point: the shadow driver and
  the research loop are separate tasks, and the research loop failing
  does not cost forward rows. `TwShadow0050` last result 0, missed 0.

- **Iteration 43's catch-up trigger observed working, and harmless.**
  `CryptoShadowTrial88` shows `LastRunTime 2026-08-19 15:58:13` with
  result 0 — that is the session-unlock trigger added in iteration 43,
  not the 08:20 daily fire. It wrote nothing, exactly as designed: the
  2026-08-18 row was already recorded at `2026-08-19T00:20:05Z` by the
  daily fire, and `append_day` returns early when the last recorded
  date is already current. The idempotence argument used to justify
  that trigger now has a live confirmation.

- **Step 2 (web research) done and recorded.** Five items filed in
  `RESEARCH_LOG.md` under iteration 44. The one that matters: **Gueta
  Quant's pre-registered funnel of 13 simple strategies on EURUSD
  daily (2020-2025, OOS 2024-2025) returned 13 to 0** — 8 passed their
  gate 1, 7 their gate 2, and **zero** passed either DSR >= 0.95 or
  PBO, with their Breakout Channel arm scoring **DSR 0.062** despite
  +1.52% OOS and +16.05% walk-forward return; their PBO was 0.5639
  (CSCV, 16 blocks, 12,870 combinations, family N=14). Source-verified
  by fetching the page, per the iteration-43 lesson. Out of product law
  (FX, not spot crypto), so **not testable here** and no trial follows
  from it — but it is the first outside evidence about how this
  project's own two deciding gates behave in independent hands, and it
  points the same way iteration 26's fragility measurement does. Also
  filed: a second independent arrival at the momentum-regime-decay
  question (flagged — a third should trigger asking the operator
  whether to attach a decision to it); a practitioner "100 trades makes
  a forward test valid" rule **explicitly refused** as a goalpost move
  against `FORWARD_TRACK_READ_PREREGISTRATION.md`; and arXiv 2512.22476
  (AutoQuant) disposed of as perpetual futures. Tenth consecutive pass
  with nothing directly actionable under P1-only.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed**, 1 warning, in 102.52s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false` (`holdout_lock.json` verified), no research document created,
  no diagnostic script written, no `configs/runtime/` or live-runtime
  file touched, the live 08:05 task's definition not touched, no shadow
  row fabricated, and the 2026-08-09 hole left as a hole. The Gueta
  result was **not** used to adjust any gate threshold or to reinterpret
  trial 118's DSR — reading someone else's failure as license to move
  one's own bar is the error this program most needs to avoid.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about -6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-19: (a)
  iteration 43's item (c) is **closed** — the Task Scheduler
  Operational channel is enabled; (b) **new, informational only:** the
  2026-08-17 slot was lost to a weekly account usage limit, which no
  repo change can prevent — if nightly iterations matter more than
  other usage, the operator controls that trade-off, not the loop;
  (c) **new, informational only:** the 2026-08-18 slot was lost to an
  operator-initiated restart 15m46s into the run. Reboots are the
  operator's prerogative; noted only so the two blank logs are not
  mistaken for a recurring defect.

## 2026-08-21 — iteration 45 (P1: the 08-20 miss self-documented on the first try; three outside measurements of backtest-to-live transfer)

- **Numbering note.** The 2026-08-20 slot started an agent and was
  killed 2m04s in without writing to the repository (`git status`
  clean at 8a92b3b, no commit, no draft file), so it is counted as a
  **lost slot**, not an iteration — the same treatment iteration 44
  gave 2026-08-17 and 2026-08-18. The 2026-08-03 orphan was
  retroactively called "iteration 41" in a later entry; that precedent
  is deliberately not followed here. The difference is bookkeeping
  only and changes no measurement.

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-44. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; no return-based
     forward verdict is statistically permitted before **2028-06-29**;
     trial 118's gate-4 pass holds only for a stopped search; the
     six-gate framework has exercised only gates 3 and 4, both with
     recorded defects; the audit route is converged (iteration 35); the
     on-chain route is open but unadvanced pending an operator
     hypothesis lock.
  2. **What this iteration moves.** It closes the 2026-08-20 miss with
     a **verified mechanism and exit code** instead of an inference,
     and in doing so it settles a question iteration 44 could only
     assert: whether the instrumentation built that night actually
     removes forensic work from the next failure. It did — the answer
     came from two log queries and no System-event reconstruction. It
     also converts a five-slot run of failures into a stated
     reliability figure with a decision handed to the operator rather
     than taken unilaterally.
  3. **Why it is not sprawl.** No new script, no new research document,
     no new instrumentation — see the explicit refusal below. No gate
     rerun, no trial registered, no backtest, no pre-registration or
     frozen contract touched. Under the analytical-routes-exhausted
     clause the prescribed behaviour is P1 maintenance, and every item
     here is P1.

- **2026-08-20 diagnosed: a console-control kill, a third distinct
  mechanism.** `run_20260820_213701.log` is **43 bytes** and contains
  exactly `started=2026-08-20T21:37:01.5149033+08:00` with no `exit=`
  line — which under iteration 44's scheme means *interrupted mid-run*,
  not *never launched*. The Task Scheduler Operational channel, enabled
  by iteration 44, supplies the rest directly:

  | Time | Event | Content |
  |---|---|---|
  | 2026-08-20 21:37:01 | `107` / `100` / `200` | task launched by time trigger, instance `{3e44ad1f-...}`, action `powershell.exe`, PID 35720 |
  | 2026-08-20 21:39:05 | `201` | action completed **with return code 3221225786** |
  | 2026-08-20 21:39:05 | `102` | instance finished |

  **3221225786 = 0xC000013A = `STATUS_CONTROL_C_EXIT`** — the process
  was terminated by a console control event (Ctrl+C or window close),
  **2 minutes 4 seconds** after starting. Three competing explanations
  are refuted from evidence, not merely disfavoured:

  - *Reboot or power transition,* the 2026-08-18 cause — refuted: the
    **System log holds zero events** between 21:30 and 22:30 that
    night. The machine stayed up.
  - *Logoff or session teardown* — refuted: the TerminalServices
    LocalSessionManager channel records no session event between 20:00
    and 02:00; its only nearby entry is an unrelated `59` at
    2026-08-21 00:59:30.
  - *Quota or authentication failure,* the 2026-08-17 and iteration-42
    causes — refuted: the agent transcript for that run
    (`c140db9a-...jsonl`, 133 entries, 537 KB) shows a **healthy
    iteration in mid-flight**, executing step 2 web research with tool
    results returning normally at 13:39:01Z, four seconds before the
    kill. Nothing failed; something outside stopped it.

  The task runs `LogonType=Interactive`, `Hidden=False`, so it owns a
  **visible console window on the operator's desktop**, and that window
  is the only ordinary source of a console control event.

- **No new instrumentation was added, on purpose.** The obvious move —
  a `try/finally` in `run_research_loop.ps1` that appends a `killed=`
  marker so Ctrl+C is distinguishable from a hard kill without touching
  the event log — was considered and **refused**. Step 0's test is
  whether a change moves a decision or closes a route; this one closes
  nothing, because the existing chain answered the question in about a
  minute on its first live use. The circular 10 MB event channel is the
  only durable weakness in that chain, and at one iteration per day the
  events are always days fresh when read. Adding a fourth log signature
  would be a diagnostic that feels like progress and is not.

- **Slot reliability, stated rather than implied.** Of the five nightly
  21:37 slots from 2026-08-17 to 2026-08-21: **one completed**
  (08-19, iteration 44, `exit=0`), **three were lost** (08-17 weekly
  usage limit, `exit=1`, 218 bytes; 08-18 operator restart, 0 bytes;
  08-20 console-control kill, 43 bytes), and one is this iteration.
  All three losses are **operator-side** and none is a repo defect —
  but they are no longer independent one-offs, and their union is a
  **60% loss rate over that window**. What follows is a choice, not a
  fix, and it is the operator's:

  - **Operator-attention item (a), new.** If the 08-20 window closure
    was **accidental**, the loop can be made unclosable by adding
    `-WindowStyle Hidden` to the task action, which keeps
    `LogonType=Interactive` and therefore keeps the credential and
    OAuth path that iteration 42 proved fragile. If it was
    **deliberate** — the operator wanting the machine back — then
    hiding the window would remove the only convenient way to stop a
    running iteration, and **nothing should change**. The loop cannot
    tell these apart from evidence and must not guess, so it does
    neither and asks.
  - **Operator-attention items from iteration 44 carry forward
    unchanged:** the weekly usage limit is an account-level trade-off
    only the operator controls, and reboots are the operator's
    prerogative.

- **Track state, verified from the files themselves.**

  | Track | Path | Rows | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 27 (26 real + seed) | 2026-08-20, equity 1048.230780896974809913646460, exposure `{BTC: 0.75, ETH: 0.75}`, closes 73025.15 / 2326.82 | OK — +2 rows since iteration 44 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 27 (26 real + seed) | 2026-08-20, equity 1089.580341451188033215394260, exposure `{BTC: 0.75, ETH: 0.75}` | OK — +2 rows since iteration 44 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 5 (4 real + seed) | 2026-08-14, close 106.40, exposure 0.75 | OK — weekly; last fire 2026-08-15 result 0, next 2026-08-22 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 6 (5 real + seed) | 2026-08-14, close 401.480011, exposure 0.5 | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-20 with **exactly one
  date gap, 2026-08-09** — the permanently lost row from iteration 42,
  unchanged. `CryptoShadowTrial88` last ran 2026-08-21 08:20:01 with
  result 0, next 2026-08-22 08:20; `TwShadow0050` last ran 2026-08-15
  09:40 with result 0, next 2026-08-22 09:40; both `Ready`, both with
  `NumberOfMissedRuns 0`. **The three lost research slots cost zero
  forward rows**, which is the point of keeping the shadow drivers on
  separate tasks.

- **Step 2 (web research) done, source-verified, and unusually
  convergent.** Five items filed in `RESEARCH_LOG.md` under iteration
  45; every number below was read out of the source document, not out
  of a search summary. Three independent measurements of
  **backtest-to-live transfer** arrived in one pass:

  - **Liu (arXiv 2604.18821, 20 Apr 2026)** — 1,726 commercially
    distributed structured strategies, ten institutions, 2009-2025.
    Pro-forma 12-month volatility-adjusted return **4.1% p.a. against
    1.0% live** (−3.1pp, p<0.01). Regression of live on pro-forma:
    **beta 0.137, R² = 0.148** raw, collapsing to **0.025 (R² = 0.032)**
    against an external index and **0.034 (R² = 0.054)** against a
    leave-one-out peer average — **81% and 75% reductions**. 59% of
    strategies are negative against both benchmarks.
  - **Mroziewicz and Slepaczuk (arXiv 2602.10785, 11 Feb 2026)** —
    spot BTC/ETH/BNB, walk-forward-optimized EMA crossover, unseen
    out-of-sample 2019-11-07..2021-08-22. Sharpe against buy-and-hold:
    BTC **1.1064 vs 1.1281**, ETH **1.3371 vs 1.5365**, BNB **1.1982
    vs 1.4644**. Their own sentence: *"No strategy surpassed the
    respective asset's Buy-and-Hold performance in terms of Sharpe
    ratio."* Annualized returns of 90.91%, 137.27% and 140.30% did not
    save it.
  - **Wiecki et al. (SSRN 2745220)** — 888 algorithms with at least six
    months out-of-sample. In-sample Sharpe predicts out-of-sample
    Sharpe at **Pearson R² = 0.02**, while **annual volatility
    transfers at R² = 0.67 and maximum drawdown at R² = 0.34**.

  **What this does and does not do to the standing answer.** It changes
  no clause. It hardens two: that a backtest must be read against a
  benchmark, and that of this program's two headline numbers the
  **drawdown** result is the more likely to travel and the **5.4%
  return margin** the less. The Wiecki limit is stated precisely in
  `RESEARCH_LOG.md` — drawdown *character* persists for an algorithm;
  a drawdown *advantage over a benchmark* is a different quantity he
  did not measure. Liu's regime-timing result was **not** used to
  license an era-extremity diagnostic on the 2026-07-24 launch date,
  and no forward read moves: `FORWARD_TRACK_READ_PREREGISTRATION.md`
  stands as frozen, 2028-06-29 for return. Eleventh consecutive
  research pass with nothing directly actionable under P1-only. Also
  recorded: none of these is the **third** arrival at the
  momentum-regime-decay question — that trigger is about crypto
  momentum compressing post-2021 and remains at two.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed** in 48.66s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false` (`docs/reports/research/holdout_lock.json` verified), no
  research document created, no diagnostic script written, no new
  logging added, no scheduled-task definition altered — including the
  research loop's own, whose window exposure is reported to the
  operator rather than silently changed — no `configs/runtime/` or
  live-runtime file touched, no shadow row fabricated, and the
  2026-08-09 hole left as a hole. Three outside papers reporting that
  backtests do not transfer were **not** used to discount, reinterpret
  or re-weight any recorded number of this program's own; they are
  filed as priors and corroboration, and the measurements stand as
  measured.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about −6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**; the
  single gate-4 pass holds only for a stopped search; the framework has
  exercised exactly two gates, both defective. On-chain route open but
  unadvanced. Operator-attention items, dated 2026-08-21: (a)
  **new** — the 2026-08-20 slot was lost to a console-control kill of
  the loop's visible console window; hiding that window is a one-line
  task change the loop declines to make unilaterally, because the same
  window is the operator's only convenient stop control; (b) carried
  forward — the weekly account usage limit that cost 2026-08-17 is an
  account-level trade-off only the operator controls; (c) carried
  forward — reboots such as the one that cost 2026-08-18 are the
  operator's prerogative, noted only so the blank logs are not
  mistaken for a recurring defect.

## 2026-08-22 — iteration 46 (P1: first clean slot in six; all four tracks recording; a redundancy question opened at two arrivals)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-45. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; against the naive
     13-coin alternative the margin is only 5.4% and that benchmark is
     survivorship-flattered; no return-based forward verdict is
     statistically permitted before **2028-06-29**; trial 118's gate-4
     pass holds only for a stopped search; the six-gate framework has
     exercised only gates 3 and 4, both with recorded defects; the audit
     route is converged (iteration 35); the on-chain route is open but
     unadvanced pending an operator hypothesis lock.
  2. **What this iteration moves.** Little, and that is the correct
     output under the contract's "routes exhausted" clause. Concretely
     it (a) confirms from the files that **all four forward tracks
     gained rows**, including the weekly Taiwan and gold task firing
     this morning, so P1 is intact; (b) records the **first scheduled
     slot since 2026-08-16 that ran without a miss, kill or auth
     failure** [**CORRECTED 2026-08-24, iteration 48 — wrong as
     written. `run_20260819_213701.log` ends `exit=0 finished=
     2026-08-19T21:46:41.2533077+08:00` and `run_20260821_213702.log`
     ends `exit=0 finished=2026-08-21T21:51:18.4578567+08:00`, and
     iteration 45's own entry already counted 08-19 as completed. The
     08-22 slot was therefore the third clean slot since 08-16, not the
     first. Nothing in the record explains excluding 08-19 and 08-21,
     so the sentence is corrected rather than reinterpreted.**], which
     is the evidence the operator needs to judge
     whether the five-slot failure run was a phase or a defect; and
     (c) opens one tracked question — whether the ensemble's four
     windows are four bets or effectively two — at **two arrivals**,
     with nothing run and nothing decided.
  3. **Why it is not sprawl.** No new script, no new research document,
     no new diagnostic, no trial. The web pass is contract-mandated and
     its output is five lines in `RESEARCH_LOG.md`. The one new
     question is filed under the existing arrival-counting rule rather
     than acted on, which is the mechanism that stops an interesting
     paper from becoming an unplanned family.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 28 (27 real + seed) | 2026-08-21, equity 1108.839671324292607997147552, exposure `{BTC: 0.75, ETH: 1}`, closes 78338.03 / 2516.30 | OK — +1 row since iteration 45 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 28 (27 real + seed) | 2026-08-21, equity 1152.580070833553048227738291, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 45 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5 | OK — weekly task fired 2026-08-22 09:40, result 0 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75 | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-21 with **exactly one
  date gap, 2026-08-09** — the permanently lost row from iteration 42,
  unchanged and still left as a hole. Task state read from the
  scheduler at 21:37 today: `CryptoShadowTrial88` last ran 2026-08-22
  08:20:01 result 0, next 2026-08-23 08:20; `TwShadow0050` last ran
  2026-08-22 09:40:00 result 0, next 2026-08-29 09:40; both `Ready`,
  both `NumberOfMissedRuns 0`. `CryptoQuantDailySignalCycle` (the live
  08:05 runtime, not touched by research) last ran 2026-08-22 08:05:01
  result 0. Both ETH sleeves moved from 3-of-4 to **4-of-4 windows on**
  on 2026-08-21; that is the recorded signal state, not a result.

- **The loop's own reliability, stated plainly.** `CryptoResearchLoop`
  fired on time at 2026-08-22 21:37:01 and this iteration ran to
  completion — the **first uninterrupted research slot since
  2026-08-16**. The five slots in between were: 08-17 weekly account
  usage limit, 08-18 reboot, 08-19 ran (iteration 44), 08-20 console
  kill, 08-21 ran (iteration 45). Counting only slots the loop itself
  could control, the failure run is over; counting all slots, six of
  the last ten produced an iteration. [**CORRECTED 2026-08-23,
  iteration 47 — five, not six.** The ten scheduled 21:37 slots ending
  2026-08-22 are 08-13..08-22, and their run logs classify as: 08-13
  auth 401, 08-14 auth 401, 08-15 ran, 08-16 ran, 08-17 weekly account
  limit, 08-18 zero-byte reboot, 08-19 ran, 08-20 `started=`-only
  console kill, 08-21 ran, 08-22 ran — **five** completed. The two
  off-schedule runs in the same stretch (08-12 17:53 and 08-13 09:58)
  were also auth-401 failures, so including them cannot raise the
  count. The sentence's other clauses stand unchanged.] The instrumentation added in
  iteration 44 is now confirmed working twice: today's log opened with
  `started=` and will close with `exit=`, and no System-event
  reconstruction was needed for anything in this entry.

- **Operator-attention items, carried forward unchanged, none acted on
  unilaterally.** (a) The research loop still runs in a **visible
  console window**; hiding it with `-WindowStyle Hidden` would have
  prevented the 08-20 kill but would also remove the operator's only
  convenient way to stop a running iteration. The loop cannot tell an
  accidental close from a deliberate one and does not guess, so the
  task definition is **unchanged** and the choice stays with the
  operator. (b) The weekly account usage limit that cost 08-17 is an
  account-level trade-off only the operator controls. (c) Reboots such
  as the one that cost 08-18 are the operator's prerogative, noted only
  so blank logs are not mistaken for a recurring defect.

- **Step 2 (web research) done and source-verified, with one number
  retracted mid-pass.** Five items filed in `RESEARCH_LOG.md` under
  iteration 46. Two are new: **arXiv 2607.19497** (Sepp and Lucic,
  21 Jul 2026), which derives trend P&L as a Poisson-kernel reading of
  the return spectrum — "trend-following alpha is excess spectral mass
  at low frequencies" — gives a closed-form net Sharpe and cost-optimal
  span under costs, shows positive skewness of trend returns is
  structural and peaks near half the filter span, and reports that all
  trend systems on liquid contracts are strongly correlated; and
  **arXiv 2510.23150v2** (Etienne et al., 28 Oct 2025), which reports
  standalone Sharpe of **0.20 / 0.21 / 0.21 / 0.42 / 0.47** for the
  20 / 60 / 125 / 250 / 500-day horizons against an all-horizons
  baseline of **0.36**, with pairwise correlations up to **90%**
  (250d-500d) and **84%** (125d-250d), and concludes that the medium
  band adds little once short and long are present. **A number was
  retracted before it was written anywhere durable:** the first read of
  that paper reported "excluding 125d lifts Sharpe from 0.36 to about
  0.40"; a second targeted read found no such figure in the document,
  so it is not recorded. Also filed: an Amberdata 2026 outlook whose
  search-summary claims about realized volatility and trend-strategy
  decay **did not survive fetching the page** and are therefore not
  recorded, and arXiv 2602.11708 re-encountered a third time and left
  disposed. Twelfth consecutive pass with nothing directly actionable.

- **The one thing the papers point at, and why it stays unrun.** Both
  new sources bear on the same untested place: whether the ensemble's
  **10/20/55/110** windows are four independent bets or effectively
  two. The direct test is a leave-one-window-out ablation, and it is
  **refused**, on two independent grounds. Procedurally it is an arm of
  the experiment-7 family and P3 forbids new single-market parameter
  families. Arithmetically it is worse than procedural: iteration 26
  measured that a 134th trial preserves trial 118's gate-4 pass only
  if its Sharpe falls in **[0.709, 1.180]**, and an ablation arm
  behaving like the current ensemble (trial 88 at 1.1823, trial 118 at
  1.2413) would sit at or above that ceiling and destroy the pass. So
  the honest position is recorded rather than tested: the ensemble's
  effective breadth is **unmeasured**, no document may claim its four
  windows are four independent bets, and the question waits for a third
  independent arrival before the operator is even asked.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed**, 1 warning, in 52.67s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false` (`docs/reports/research/holdout_lock.json` verified today),
  no research document created, no diagnostic script written, no
  window-ablation arm run, no scheduled-task definition altered —
  including the research loop's own console-window setting — no
  `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. One external
  number was dropped rather than rounded into the record, and one
  search summary was refused because the page behind it did not
  contain the claim.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x twin edge is
  audited and robust; the engine is free of look-ahead, verified to the
  cent; execution-latency cost is about −6.4 bps round-trip, bounded
  above by ~17 bps, inside tested headroom; the October holdout is
  protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin
  is only 5.4% and that benchmark is survivorship-flattered; breadth
  still fails, and as of today the ensemble's **internal** breadth is
  additionally unmeasured; **nothing is forward-validated and no
  return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped search;
  the framework has exercised exactly two gates, both defective.
  On-chain route open but unadvanced. Operator-attention items dated
  2026-08-22 are the three carried forward above, all unchanged.

## 2026-08-23 — iteration 47 (P1: second clean slot running; the redundancy question hits its third arrival and goes to the operator; one prior tally corrected)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-46. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; against the naive
     13-coin alternative the margin is only 5.4% and that benchmark is
     survivorship-flattered; no return-based forward verdict is
     statistically permitted before **2028-06-29**; trial 118's gate-4
     pass holds only for a stopped search; the six-gate framework has
     exercised only gates 3 and 4, both with recorded defects; the audit
     route is converged (iteration 35); the on-chain route is open but
     unadvanced pending an operator hypothesis lock.
  2. **What this iteration moves.** One tracked question crosses the
     threshold its own rule fixed in advance. The ensemble-breadth
     question opened at two arrivals in iteration 46 received its
     **third independent arrival** today (Valeyre, arXiv 2504.10914v15,
     12 Aug 2026), so under the arrival-counting rule it stops
     accumulating citations and goes to the operator as a question.
     Nothing was run to reach that state, and nothing is run because of
     it. Secondarily the iteration (a) confirms all four forward tracks
     are healthy, (b) records the second consecutive uninterrupted
     scheduled slot, and (c) **corrects a number in iteration 46's own
     entry** — the slot tally was five, not six.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial, no backtest, no gate report, no arm run. The web pass is
     contract-mandated. The one measurement taken (cross-track exposure
     agreement, below) reads rows already on disk, computes no
     performance quantity, and is flagged as borderline to the operator
     rather than quietly kept.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 29 (28 real + seed) | 2026-08-22, equity 1081.490141410677996921596055, exposure `{BTC: 0.75, ETH: 1}`, closes 77074.93 / 2422.60 | OK — +1 row since iteration 46 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 29 (28 real + seed) | 2026-08-22, equity 1124.151683988905973274222590, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 46 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly, not due until 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-22 with **exactly one date
  gap, 2026-08-09** — the permanently lost row from iteration 42,
  unchanged and still left as a hole. Task state read from the scheduler
  at 21:37 today: `CryptoShadowTrial88` last ran 2026-08-23 08:20:01
  result 0, next 2026-08-24 08:20; `TwShadow0050` last ran 2026-08-22
  09:40:00 result 0, next 2026-08-29 09:40; both `Ready`, both
  `NumberOfMissedRuns 0`. `CryptoQuantDailySignalCycle` (the live 08:05
  runtime, not touched by research) last ran 2026-08-23 08:05:01 result
  0. `docs/reports/research/holdout_lock.json` re-verified: `spent`
  still `false`.

- **An arithmetic health check on the recorder, which passes.** On
  2026-08-22 BTC closed **-1.6124%** and ETH **-3.7237%** against the
  previous row, and both shadow books moved **-2.4665%**. Equal weight
  across the two symbols at the recorded exposures gives
  `0.5*(0.75*-1.6124) + 0.5*(1*-3.7237) = -2.4666%`, matching the
  recorded equity change to the fourth decimal. That is a consistency
  check of the recorder against its own inputs, not a performance
  statement.

- **Cross-track exposure agreement, measured — and self-flagged as
  borderline.** Over the 29 common dates the two crypto shadow
  configurations held **identical exposures on only 4 dates and
  differed on 25**, with all four agreements falling in the last four
  days (2026-08-19..08-22). Before that they diverged persistently:
  trial 88 sat flat in BTC for the first fourteen rows while trial 118
  held 0.5, and trial 88 was entirely in cash for 2026-08-11..08-17
  while trial 118 held `{BTC: 0.25, ETH: 0.5}` throughout. So the two
  tracks are **carrying distinct information, not duplicating one
  observation** — which matters because today's identical daily return
  is a four-day-old convergence, not a structural property, and a
  future entry must not infer redundancy from it. **What this is not:**
  it is not Test 1, 2 or 3 of
  `FORWARD_TRACK_READ_PREREGISTRATION.md`, it computes no Sharpe,
  return, drawdown or benchmark, and **no comparison between the two
  trials may be drawn from the two equity figures quoted in the table
  above** — a positive forward number may not be cited as support
  before 2028-06-29 under that rule, and neither may a relative one.
  **The borderline, disclosed rather than hidden:** the read
  pre-registration permits unrestricted health checks and restricts
  reads, and a cross-track structural comparison was not contemplated
  when it was written. This iteration judged it a health check because
  it introduces no metric, but the judgement is the loop's own and the
  operator may disagree. It is raised as item (d) below.

- **The third arrival, and why it still runs nothing.** Today's web
  pass found **arXiv 2504.10914v15** (Sebastien Valeyre, v15 submitted
  12 Aug 2026), *"Breaking the Trend: How to Avoid Cherry-Picked
  Signals"*: 70 futures instruments, 25 May 1990 to 7 Dec 2023, daily.
  Verified in two passes — abstract page, then a targeted second read
  of the full text for every body number. The abstract states verbatim
  that *"using only one simple EMA, appears optimal to capture the
  trend"* and that a *"complex basket of different complex indicators
  as signal ... exposes to the risk of cherry-picking"*; the body gives
  *"ARP(80) is correlated to ARP(150) with a coefficient of 0.96"* and
  *"the parameter of 112±10 business days ... is the optimal parameter
  to get the optimal Sharpe ratio"*. That is the **third independent
  arrival** at the question opened in iteration 46 — three groups
  (Sepp and Lucic; Etienne et al.; Valeyre), three methods, three
  samples, one conclusion that adjacent trend horizons are
  near-duplicates. **Three limits are recorded with it.** First, all
  three are liquid-futures studies and **none is crypto**, so they are
  three arrivals in the bookkeeping sense and not three tests of this
  program's ensemble; this program already measured that a
  crypto-selected rule failed to transfer to Taiwan and gold, and the
  reverse transfer is equally unestablished. Second, the near-match
  between Valeyre's 112±10 days and this program's longest window of
  110 is a **coincidence of different indicators on different
  universes** and must never be cited as corroboration. Third, the two
  standing refusals are unchanged: a leave-one-window-out ablation is
  an arm of the experiment-7 family and P3 forbids new single-market
  parameter families, and iteration 26's arithmetic says a 134th trial
  preserves trial 118's gate-4 pass only if its Sharpe lands in
  **[0.709, 1.180]**, which an ablation behaving like the current
  ensemble (trial 88 at 1.1823, trial 118 at 1.2413) would not. **So
  the loop does not decide it.** The operator must, because the
  decision is a measurement priced against a recorded gate-4 cost.

- **Step 2 (web research) done and source-verified, with one prior-read
  slip corrected and one search direction closed.** Five items filed in
  `RESEARCH_LOG.md` under iteration 47. Besides Valeyre: **arXiv
  2604.26747** (Huang, Fan, Hu, Ye, 29 Apr 2026), an LLM-agent crypto
  factor program built on an append-only experiment trace with a
  deterministic gate engine — structurally this program's own idea —
  reporting **44.55% annualized and Sharpe 1.55** out of sample
  (train 2020-2022, validate 2023, test 2024 onward, daily, 5 bps
  one-way, max drawdown -0.236, 25 factors over five search rounds) and
  applying **no multiple-testing correction of any kind** after an
  explicitly searched factor set; it is long-short, so outside product
  law and not testable here. And **BATP Vol. 33** (Gbadebo, 9 Jun 2026)
  on eight coins 2020-01-01..2025-10-31, reporting time-series momentum
  at **31.96% annual return** and cross-sectional max drawdown
  **55.0%** — with **no buy-and-hold comparison stated anywhere in the
  abstract**, the exact defect `VS_BUY_AND_HOLD_2026-07-26.md` exists
  to correct; that absence is recorded as a verified absence and **no
  estimate of what the passive twin would have returned is made here**.
  A first-read slip on Valeyre's sample start (29 May 1990) was
  corrected against the paper's own sentence (25 May 1990) before being
  recorded. A targeted search for post-ETF momentum decay returned only
  flow journalism — no measurement of any trend strategy — so it is
  **not** an arrival and the momentum-regime-decay question stays at
  **two**; the two questions are not pooled. Thirteenth consecutive
  pass with nothing directly actionable.

- **A number in iteration 46's own entry, corrected in place.** That
  entry said "six of the last ten produced an iteration". The ten
  scheduled 21:37 slots ending 2026-08-22 are 08-13..08-22, and their
  run logs classify as 08-13 auth 401, 08-14 auth 401, 08-15 ran,
  08-16 ran, 08-17 weekly account limit, 08-18 zero-byte reboot, 08-19
  ran, 08-20 `started=`-only console kill, 08-21 ran, 08-22 ran —
  **five**, not six. The two off-schedule runs in the same stretch
  (08-12 17:53, 08-13 09:58) were also auth-401 failures, so including
  them cannot raise the count. The correction is inserted as a
  bracketed marker beside the original sentence rather than replacing
  it, following the standing answer's own convention; nothing was
  deleted.

- **The loop's own reliability, stated plainly.** `CryptoResearchLoop`
  fired on time at 2026-08-23 21:37:01, its log opened with
  `started=2026-08-23T21:37:01.8644098+08:00`, and the task reports
  `Running` with `LastTaskResult 267009` (`STILL_ACTIVE`) — this
  iteration in flight, the **second consecutive uninterrupted slot**
  after 08-22 [**CORRECTED 2026-08-24, iteration 48 — the third, not
  the second. The streak runs 08-21, 08-22, 08-23, each with `exit=0`
  in its own run log; this entry inherited iteration 46's undercount,
  corrected above.**]. `NumberOfMissedRuns` is 0 and the next slot is
  2026-08-24 21:37. Counting completed iterations over the eleven
  scheduled slots 08-13..08-23, six including today.

- **Operator-attention items.** (a) **New, and the substantive one:**
  the ensemble-breadth question has reached three independent arrivals
  and now needs a decision the loop is not permitted to take — *should
  a leave-one-window-out ablation of 10/20/55/110 be run, knowing it
  costs an N, is a P3-forbidden family arm, and would very likely
  destroy trial 118's single gate-4 pass?* Declining is a legitimate
  answer; the recorded consequence of declining is that the ensemble's
  internal breadth stays **unmeasured** and no document may describe
  its four windows as four independent bets. (b) The research loop
  still runs in a **visible console window**; hiding it would have
  prevented the 08-20 kill but would remove the operator's only
  convenient way to stop a running iteration, so the task definition is
  **unchanged** and the choice stays with the operator. (c) The weekly
  account usage limit that cost 08-17 and the auth expiries that cost
  08-13 and 08-14 are account-level matters only the operator controls.
  (d) **New, procedural:** should cross-track structural comparisons of
  the shadow files be brought explicitly under
  `FORWARD_TRACK_READ_PREREGISTRATION.md`, either as permitted health
  checks or as restricted reads? Today's comparison was judged a health
  check by the loop; a rule the loop did not write would be better.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over
  81 files and 325 dependencies; `pytest -m "not network"` **383
  passed**, 1 warning, in 113.49s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no window-ablation arm run, no scheduled-task definition altered
  — including the research loop's own console-window setting — no
  `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. One prior tally
  was corrected downward rather than left flattering, one first-read
  date was corrected against the source before it was recorded, and one
  search direction was refused as journalism rather than counted as an
  arrival.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and
  drawdown (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x
  exposure-matched twin edge is audited and robust; the engine is free
  of look-ahead, verified to the cent; execution-latency cost is about
  −6.4 bps round-trip, bounded above by ~17 bps, inside tested headroom;
  the October holdout is protected mechanically; the Taiwan and gold
  negatives are robust to dividend treatment; against the naive 13-coin
  alternative the margin is only 5.4% and that benchmark is
  survivorship-flattered; breadth still fails, and the ensemble's
  **internal** breadth remains **unmeasured** — now with three outside
  arrivals pointing at it and an operator decision pending, which
  changes the question's status and not its answer; **nothing is
  forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**; the single gate-4 pass
  holds only for a stopped search; the framework has exercised exactly
  two gates, both defective. On-chain route open but unadvanced.
  Operator-attention items dated 2026-08-23 are the four above.
## 2026-08-24 — iteration 48 (P1: fourth consecutive clean slot; two prior slot-streak claims corrected upward against their own logs; the closest crypto relative of this rule does not hand over the redundancy number)

- **Step 0 convergence check.**
  1. **Current answer** — unchanged from iterations 27-47. Timing works
     in crypto only; in its own universe it bought both return (14.26x
     vs 6.05x) and drawdown (33.05% vs 80.99%); the 4.70x
     exposure-matched twin edge is audited and robust; against the naive
     13-coin alternative the margin is only 5.4% and that benchmark is
     survivorship-flattered; no return-based forward verdict is
     statistically permitted before **2028-06-29**; trial 118's gate-4
     pass holds only for a stopped search; the six-gate framework has
     exercised only gates 3 and 4, both with recorded defects; the audit
     route is converged (iteration 35); the on-chain route is open but
     unadvanced pending an operator hypothesis lock.
  2. **What this iteration moves.** Three things, none of them a new
     measurement of the strategy. (a) P1 is confirmed from the files:
     both crypto tracks gained a row and the recorder reproduces its own
     equity change to eight decimal places. (b) **Two claims about the
     loop's own reliability, in iterations 46 and 47, are corrected in
     place against the run logs** — and the correction runs in the
     *flattering* direction, which is why it is evidenced line by line
     rather than asserted. (c) The web pass locates the closest
     published relative of this program's own rule — a crypto Donchian
     **ensemble** built from several lookbacks — and records that
     neither authors' page states a between-window redundancy
     measurement. That is a **failure to find**, and it sharpens the
     question already sitting with the operator: the literature does not
     appear to offer a substitute for running the ablation.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial, no backtest, no gate report, no arm run, no
     pre-registration written or touched. The web pass is
     contract-mandated. The only computation performed is the recorder
     consistency check, which reads two rows already on disk and
     produces no performance quantity.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 30 (29 real + seed) | 2026-08-23, equity 1094.067228255416991520871868, exposure `{BTC: 0.75, ETH: 1}`, closes 77734.00 / 2463.41 | OK — +1 row since iteration 47 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 30 (29 real + seed) | 2026-08-23, equity 1137.224899189689921012190864, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 47 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly; unchanged is correct, next run 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-23 with **exactly one date
  gap, 2026-08-09** — the permanently lost row from iteration 42,
  unchanged and still left as a hole. Task state read from the scheduler
  during this iteration: `CryptoShadowTrial88` last ran 2026-08-24
  08:20:01 result 0, next 2026-08-25 08:20; `TwShadow0050` last ran
  2026-08-22 09:40:00 result 0, next 2026-08-29 09:40; both `Ready`,
  both `NumberOfMissedRuns 0`. `CryptoQuantDailySignalCycle` (the live
  08:05 runtime, not touched by research) last ran 2026-08-24 08:05:01
  result 0, next 2026-08-25 08:05.
  `docs/reports/research/holdout_lock.json` re-verified: `spent` still
  `false`.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-22 to 2026-08-23 BTC closed **+0.8551%** (77074.93 to
  77734.00) and ETH **+1.6846%** (2422.60 to 2463.41). Applying the
  exposures recorded on the 08-22 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — gives a predicted book move of
  **+1.162940%**, and both books moved **+1.162940%**, a difference of
  **0.00000000pp**. This is a check of the recorder against its own
  inputs, not a performance statement. The two books moved identically
  because they held identical exposures on 08-22; **no further
  cross-track structural statistic is computed today**, because
  iteration 47 flagged exactly that class of comparison as possibly
  belonging under `FORWARD_TRACK_READ_PREREGISTRATION.md` and the
  operator has not yet ruled. Pending a rule, the loop does less rather
  than more.

- **Two prior claims about the loop's own reliability, corrected in
  place — upward, and therefore evidenced.** Iteration 46 called the
  2026-08-22 slot "the first scheduled slot since 2026-08-16 that ran
  without a miss, kill or auth failure", and iteration 47 inherited that
  framing as "the second consecutive uninterrupted slot". Against the
  run logs both are wrong: `run_20260819_213701.log` ends `exit=0
  finished=2026-08-19T21:46:41.2533077+08:00`, `run_20260821_213702.log`
  opens `started=2026-08-21T21:37:02.1986625+08:00` and ends `exit=0
  finished=2026-08-21T21:51:18.4578567+08:00`, and iteration 45's own
  entry already recorded 08-19 as completed. So 08-22 was the **third**
  clean slot since 08-16, 08-23 the **third consecutive**, and with
  today's slot in flight the streak is **four** (08-21, 08-22, 08-23,
  08-24). A correction that makes the loop look better carries a higher
  bar than one that makes it look worse, so the marker inserted into
  each entry quotes the exit lines rather than restating a count, and
  neither original sentence was deleted.

- **Slot ledger over the eleven scheduled 21:37 slots 08-14..08-24, each
  classified from its own log:** 08-14 `exit=1` at 21:37:14 (auth), 08-15
  `exit=0`, 08-16 `exit=0`, 08-17 `exit=1` at 21:37:19 (weekly account
  usage limit, 218 bytes), 08-18 zero bytes (operator restart), 08-19
  `exit=0`, 08-20 `started=` only with no `exit=` (console-control kill,
  43 bytes), 08-21 `exit=0`, 08-22 `exit=0`, 08-23 `exit=0`, 08-24
  `started=2026-08-24T21:37:02.7855238+08:00` and still running. That is
  **seven completed iterations out of eleven slots**, all four losses
  operator-side, and none of them a repo defect.

- **Step 2 (web research) done and source-verified; one item is a
  failure to find and is labelled as one.** Five items filed in
  `RESEARCH_LOG.md` under iteration 48. The substantive one is
  **Zarattini, Pagani and Barbon, "Catching Crypto Trends" (SSRN
  5209907)** — a Donchian **ensemble of several lookback periods**, on a
  survivorship-bias-free crypto dataset since 2015, rotational top-20,
  Sharpe above 1.5 and annualized alpha 10.8% versus Bitcoin. SSRN
  returned **HTTP 403** for both the abstract page and the PDF, so the
  full text was **not read**; everything above comes from the authors'
  own pages. Neither page states a **between-window redundancy**
  measurement, nor the lookback periods, costs, direction, instrument or
  benchmark levels. That is recorded as a **failure to locate, not a
  verified absence** — no claim is made about the paper's tables.
  Consequence for the pending operator question: the ensemble-breadth
  question stays at **three arrivals, all liquid-futures**, and the
  search found no crypto substitute for measuring 10/20/55/110
  directly. Also filed: **arXiv 2602.11708** (Bui, Nguyen, 12 Feb 2026),
  verified from the HTML full text — Binance **perpetual swaps**, 150+
  contracts, **6-hour** bars, long-short 70/30, 4 bps taker fee, Sharpe
  2.41 and MDD -12.7% out of sample 2022-2024 against its own quoted BTC
  buy-and-hold (12.6% return, Sharpe 0.17, MDD -64.1%), with parameters
  re-optimized **monthly by grid search** and **no multiple-testing
  correction of any kind**; outside product law on three counts, so not
  testable here. And **QuantPedia's 355-strategy in-sample/out-of-sample
  study** (2 Jun 2023): Sharpe decays **33% on average** and **43.90% at
  the median** — a *fourth* arrival on the transfer question that
  already hit its threshold at three on 08-21, so it is filed as one
  line and opens nothing. A search for recent-regime crypto trend
  performance returned only outlook journalism for the second
  consecutive pass, so the momentum-decay question stays at **two
  arrivals**; the two questions are not pooled.

- **Operator-attention items.** All carried forward unchanged; **no new
  one is added today.** (a) The ensemble-breadth question is still with
  the operator: *should a leave-one-window-out ablation of 10/20/55/110
  be run, knowing it costs an N, is a P3-forbidden family arm, and would
  very likely destroy trial 118's single gate-4 pass?* Today adds one
  fact to that choice and no pressure: the closest published crypto
  ensemble does not appear to supply the number, so declining means the
  ensemble's internal breadth stays **unmeasured** with no citation able
  to stand in. (b) The research loop still runs in a **visible console
  window**; the task definition is unchanged and the choice stays with
  the operator. (c) The weekly account usage limit and the auth expiries
  are account-level matters only the operator controls. (d) Should
  cross-track structural comparisons of the shadow files be brought
  explicitly under `FORWARD_TRACK_READ_PREREGISTRATION.md`? Still
  unanswered; today the loop **abstained** from that class of comparison
  rather than repeating it.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over 81
  files and 325 dependencies; `pytest -m "not network"` **383 passed** in
  49.01s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no window-ablation arm run, no cross-track structural statistic
  computed while item (d) is open, no scheduled-task definition altered,
  no `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. Two prior
  statements were corrected **upward** and each correction quotes the log
  line that forces it; one literature item was labelled a failure to find
  rather than an absence; one search direction was refused as journalism
  for the second time rather than counted as an arrival.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by ~17 bps, inside tested headroom; the October holdout
  is protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails, and the ensemble's **internal** breadth remains **unmeasured**,
  with three outside arrivals pointing at it, an operator decision
  pending, and — new today — no published crypto measurement located
  that could answer it without running it; **nothing is forward-validated
  and no return-based forward verdict is statistically permitted before
  2028-06-29**; the single gate-4 pass holds only for a stopped search;
  the framework has exercised exactly two gates, both defective.
  On-chain route open but unadvanced. Operator-attention items dated
  2026-08-24 are the four above, all carried forward.

## 2026-08-25 — iteration 49 (P1: fifth slot in the streak; the ensemble-breadth ablation is found already published, and its own tables argue against running ours)

- **Step 0 convergence check, done first and in writing.**
  1. **Current answer, unchanged:** measured on 2018-2025 and not
     forward-validated, the timing rule adds real value **in crypto
     only** — 4.70x its exposure-matched passive twin, and in its own
     BTC/ETH universe it bought **both** return (14.26x vs 6.05x) and
     drawdown (33.05% vs 80.99%). Against the naive thirteen-coin
     alternative the margin is only **5.4%** and that benchmark is
     survivorship-flattered. **Nothing here passes the six gates**, and
     the one gate-4 pass exists only for a stopped search.
  2. **What this iteration moves.** It does not run anything. It changes
     the **inputs to the one decision sitting with the operator** — the
     ensemble-breadth question — by locating the experiment they were
     asked to authorize **already performed and published**, with its
     numbers, on 23 liquid futures over 2005-2025. The finding that
     matters is not the paper's conclusion but its **precision**: the
     best of five leave-one-out arms wins by **+0.03 full-sample Sharpe**
     (0.74 to 0.77) while **losing in two of four subperiods**, with
     **no multiple-testing correction anywhere in the text**. That is a
     prior on what running our own ablation could yield, and it points
     the same way as the N cost.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial, no backtest, no gate report, no arm run, no
     pre-registration written or touched, no window family opened. The
     web pass is contract-mandated (step 2, "never skip"). The only
     computation performed is the recorder consistency check on today's
     new row, which reads two rows already on disk and produces no
     performance quantity.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 31 (30 real + seed) | 2026-08-24, equity 1104.907833794170722816361255, exposure `{BTC: 0.75, ETH: 1}`, closes 78992.75 / 2482.31 | OK — +1 row since iteration 48 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 31 (30 real + seed) | 2026-08-24, equity 1148.493134104853934685558048, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 48 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly; unchanged is correct, next run 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series now span 2026-07-24..2026-08-24 with **exactly one
  date gap**: the pair 2026-08-08 to 2026-08-10, i.e. the missing date is
  **2026-08-09** — the permanently lost row from iteration 42, unchanged
  and still left as a hole. Scheduler state read during this iteration:
  `CryptoShadowTrial88` last ran 2026-08-25 08:20:01 result 0, next
  2026-08-26 08:20; `TwShadow0050` last ran 2026-08-22 09:40:00 result 0,
  next 2026-08-29 09:40; both `Ready`, both `NumberOfMissedRuns 0`.
  `CryptoQuantDailySignalCycle` (the live 08:05 runtime, not touched by
  research) last ran 2026-08-25 08:05:01 result 0, next 2026-08-26 08:05.
  `docs/reports/research/holdout_lock.json` re-verified: `spent` still
  `false`.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-23 to 2026-08-24 BTC closed **+1.619304%** (77734.00 to
  78992.75) and ETH **+0.767229%** (2463.41 to 2482.31). Applying the
  exposures recorded on the 08-23 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — gives a predicted book move of **+0.990854%**,
  and both books moved **+0.990854%**, a difference of **0.0000000000pp**.
  This is a check of the recorder against its own inputs, not a
  performance statement. The two books moved identically because they
  held identical exposures on 08-23; **no cross-track structural
  statistic is computed today**, because operator-attention item (d)
  below is still open and, pending a rule, the loop does less rather than
  more.

- **Slot ledger over the twelve scheduled 21:37 slots 08-14..08-25, each
  classified from its own log.** 08-14 `exit=1` (auth), 08-15 `exit=0`,
  08-16 `exit=0`, 08-17 `exit=1` (weekly account usage limit, 218 bytes),
  08-18 zero bytes (operator restart), 08-19 `exit=0`, 08-20 `started=`
  only with no `exit=` (console-control kill, 43 bytes), 08-21 `exit=0
  finished=2026-08-21T21:51:18.4578567+08:00`, 08-22 `exit=0
  finished=2026-08-22T21:46:05.3708545+08:00`, 08-23 `exit=0
  finished=2026-08-23T21:49:07.8944932+08:00`, 08-24 `exit=0
  finished=2026-08-24T21:49:41.3381394+08:00`, 08-25
  `started=2026-08-25T21:37:02.2626518+08:00` and still running. Iteration
  48 recorded the streak as **four with today's slot in flight**; 08-24's
  exit line now confirms it, so the completed streak is **four (08-21,
  08-22, 08-23, 08-24)** and today is the fifth in flight. That is **eight
  completed iterations out of twelve slots**, all four losses
  operator-side, none of them a repo defect.

- **Step 2 (web research): the pending operator question's experiment
  turns out to already exist in print, and its own tables are the
  finding.** Five items filed in `RESEARCH_LOG.md` under iteration 49.
  The substantive one is **Etienne, Ohana, Benhamou, Guez, Setrouk and
  Jacquot, "Revisiting the Structure of Trend Premia: When Diversification
  Hides Redundancy" (arXiv 2510.23150v2, 27-28 Oct 2025)**, read from the
  **arXiv HTML full text** — not an abstract-only read, unlike the
  SSRN item iteration 48 had to label a failure to locate. It runs an
  explicit **leave-one-horizon-out ablation** over
  H = {20, 60, 125, 250, 500} trading days on **23 liquid futures**
  (commodities, equities, fixed income, FX), long-short, with transaction
  2 bps, roll 2-15 bps and a 50 bps management fee, benchmarked to
  **NEIXCTAT**, tables spanning **2005-2025**. Three numbers matter here:

  - **Adjacent-horizon correlations (Table 5, 2015-2025)** — 20d/60d
    **83%**, 60d/125d **81%**, 125d/250d **84%**, 250d/500d **90%**; the
    most distant pair 20d/500d is **35-44%**. This is precisely the class
    of measurement this program does **not** have for its own 10/20/55/110
    ensemble.
  - **The ablation result** — best arm is `No 125` (Z-score +0.80), worst
    is `No 500` (**-1.12**); dropping the short 20d sleeve also hurts
    (-0.38). Sharpe by period, All Horizons vs No 125: 0.91/**0.90**,
    1.37/**1.41**, 0.43/**0.42**, 0.35/**0.44**, full sample
    0.74/**0.77**.
  - **What is wrong with it**, verified against the paper's own text. Its
    prose says excluding 125d "consistently improves Sharpe ratios" and
    claims the improvement holds "in three of the four subperiods", then
    enumerates only **two** subperiods plus the full-sample average —
    Table 8 in fact shows it **worse in two of four**. And a full-text
    search for `deflated`, `multiple test`, `bootstrap`, `reality check`
    and `PBO` returns **zero** occurrences: overfitting is handled only by
    a persistence-filtering heuristic. So the published winner is the
    **maximum of five arms, uncorrected, winning by +0.03 Sharpe**.

  Also filed: a **structural observation** that this program's four
  windows (10/20/55/110) all sit **at or below** the paper's 125d medium
  band, with **no member near the 250d/500d long end the paper finds
  indispensable** — recorded with its transfer caveats (spot vs futures,
  long-only vs long-short, crypto vs traditional, 2018-2025 vs 2005-2025,
  absolute return vs index replication) and **not** as a claim about this
  program, since it is untestable here under P3. Also filed: **arXiv
  2510.14435v4** (Borri, Liu, Tsyvinski, Wu, 21 Mar 2026) as **located,
  abstract only, not read, not an arrival**. And a **third consecutive
  empty pass** on recent-regime crypto trend versus buy-and-hold —
  outlook journalism only — so that direction is now recorded as a
  channel that is not producing measurements, and the momentum-decay
  question stays at **two arrivals**, still not pooled with the
  redundancy question.

- **Operator-attention items.** All four carried forward; **no new one is
  added today**, but item (a) has materially better inputs than it had
  yesterday. (a) The ensemble-breadth question is still with the operator:
  *should a leave-one-window-out ablation of 10/20/55/110 be run, knowing
  it costs an N, is a P3-forbidden family arm, and would very likely
  destroy trial 118's single gate-4 pass?* Yesterday the loop reported it
  could find no published crypto measurement to stand in. Today it found
  the **experiment itself**, in the closest available non-crypto setting,
  and the honest reading is that **it does not answer our question and
  suggests ours would not answer it either**: twenty years and 23 markets
  bought a +0.03 Sharpe margin that fails in half its subperiods, with no
  correction applied. Our version would have less data, five fewer years,
  one market, and a machinery obliged to discount the result — while
  paying an N that is already known to be fatal to the gate-4 pass. This
  is offered as an input, not a recommendation; the decision remains the
  operator's. (b) The research loop still runs in a **visible console
  window**; task definition unchanged, choice stays with the operator.
  (c) The weekly account usage limit and the auth expiries are
  account-level matters only the operator controls. (d) Should
  cross-track structural comparisons of the shadow files be brought
  explicitly under `FORWARD_TRACK_READ_PREREGISTRATION.md`? Still
  unanswered; today the loop **abstained** from that class of comparison
  for the second consecutive iteration.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over 81
  files and 325 dependencies; `pytest -m "not network"` **383 passed** in
  104.25s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written, no
  window-ablation arm run, no long-window family opened despite today's
  finding pointing at one, no cross-track structural statistic computed
  while item (d) is open, no scheduled-task definition altered, no
  `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. The paper's finding
  was **not** adopted as a fact about this program; its transfer caveats
  are recorded alongside it, and the two flaws found in it are recorded
  even though they weaken an item that would otherwise have looked like
  the strongest external result this loop has found.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by ~17 bps, inside tested headroom; the October holdout
  is protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails, and the ensemble's **internal** breadth remains **unmeasured** —
  now with **four** outside arrivals pointing at it, the fourth being the
  ablation itself performed elsewhere, [**CORRECTED 2026-08-27, iteration 51 — three, not four. The "fourth" is arXiv 2510.23150v2 counted a second time: it was already logged from its abstract in iteration 46 as one of the two opening arrivals, then re-logged in iteration 49 after being read in full. Reading a paper twice is not two arrivals. Iteration 49's own body text said "three arrivals, all liquid-futures" and this closing paragraph contradicted it. Distinct sources: arXiv 2607.19497 (Sepp and Lucic), arXiv 2510.23150v2 (Etienne et al., Ai For Alpha), arXiv 2504.10914v15 (Valeyre). Three groups, which is exactly the escalation threshold, not one above it. The escalation stands; only the evidence behind it shrinks.**] and an operator decision still
  pending; **nothing is forward-validated and no return-based forward
  verdict is statistically permitted before 2028-06-29**; the single
  gate-4 pass holds only for a stopped search; the framework has exercised
  exactly two gates, both defective. On-chain route open but unadvanced.
  Operator-attention items dated 2026-08-25 are the four above, all
  carried forward.

## 2026-08-26 — iteration 50 (P1: sixth slot in the streak; iteration 48's "failure to locate" becomes a partial locate, and one search channel is closed for good)

- **Step 0 convergence check, done first and in writing.**
  1. **Current answer, unchanged:** measured on 2018-2025 and not
     forward-validated, the timing rule adds real value **in crypto
     only** — 4.70x its exposure-matched passive twin, and in its own
     BTC/ETH universe it bought **both** return (14.26x vs 6.05x) and
     drawdown (33.05% vs 80.99%). Against the naive thirteen-coin
     alternative the margin is only **5.4%** and that benchmark is
     survivorship-flattered. **Nothing here passes the six gates**, and
     the one gate-4 pass exists only for a stopped search.
  2. **What this iteration moves.** Two things, both of which shrink the
     search rather than grow it. First, it **closes a search channel**:
     recent-regime crypto trend versus buy-and-hold returned nothing on
     three consecutive passes, so today it was **not queried at all** and
     is retired with a reopen condition written down in advance. Second,
     it converts iteration 48's recorded **failure to locate** into a
     **partial locate** — the closest published crypto relative of this
     program's rule now has its lookback set, direction, sample and cost
     grid on the record, obtained from RePEc and a third-party review
     because SSRN returned **HTTP 403 for the second consecutive
     iteration**. That partial locate says something about **structure**
     and, importantly, still says **nothing** about redundancy.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial, no backtest, no gate report, no arm run, no
     pre-registration written or touched, no window family opened. The
     web pass is contract-mandated (step 2, "never skip"). The only
     computation performed is the recorder consistency check on today's
     new row plus one division against the MinTRL horizon, both of which
     read numbers already on disk and neither of which produces a
     performance quantity.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 32 (31 real + seed) | 2026-08-25, equity 1093.699703181384896489564028, exposure `{BTC: 0.75, ETH: 1}`, closes 78539.14 / 2442.64 | OK — +1 row since iteration 49 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 32 (31 real + seed) | 2026-08-25, equity 1136.842876353732844457158380, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 49 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly; unchanged is correct, next run 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series now span 2026-07-24..2026-08-25 with **exactly one
  date gap**, the pair 2026-08-08 to 2026-08-10, i.e. the missing date is
  **2026-08-09** — the permanently lost row from iteration 42, unchanged
  and still left as a hole. Scheduler state read during this iteration:
  `CryptoShadowTrial88` last ran **2026-08-26 20:53:47** result 0, next
  2026-08-27 08:20; `TwShadow0050` last ran 2026-08-22 09:40:00 result 0,
  next 2026-08-29 09:40; both `Ready`, both `NumberOfMissedRuns 0`.
  `CryptoQuantDailySignalCycle` (the live 08:05 runtime, read but not
  touched by research) last ran 2026-08-26 20:53:47 result 0, next
  2026-08-27 08:05. `docs/reports/research/holdout_lock.json` re-verified:
  `spent` still `false`.

- **A real duplicate invocation happened today, and the recorder refused
  it — the first time this loop has been able to say so from a same-day
  log.** The **08:20 scheduled** run appended the 2026-08-25 rows
  (`data/runtime/shadow_runs/shadow_20260826_082001.log`: "trial88:
  appended 2026-08-25", "trial118: appended 2026-08-25", `exit=0
  finished=2026-08-26T08:20:05.3640268+08:00`). Then at **20:53** the
  task fired **again** — `Get-ScheduledTask` confirms
  `CryptoShadowTrial88` carries a daily trigger **plus**
  `MSFT_TaskLogonTrigger` and `MSFT_TaskSessionStateChangeTrigger` with
  `StartWhenAvailable=True`, the belt-and-braces set added by iteration
  43 — and the second run wrote **no row**:
  `shadow_20260826_205348.log` reads "trial88: already recorded through
  2026-08-25", "trial118: already recorded through 2026-08-25", `exit=0`.
  Line counts confirm it: 32 and 32, not 33. The idempotence argument
  iteration 43 used to justify those extra triggers is therefore
  **observed working against a real duplicate fire**, not merely asserted.
  Note what this does **not** license: the same triggers on
  `CryptoResearchLoop` would still be unsafe, because a research
  iteration is not idempotent — that distinction, drawn in iteration 43,
  stands unchanged.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-24 to 2026-08-25 BTC closed **-0.574243%** (78992.75 to
  78539.14) and ETH **-1.598108%** (2482.31 to 2442.64). Applying the
  exposures recorded on the 08-24 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — gives a predicted book move of
  **-1.014395071695523%**; trial 88 moved **-1.014395071695523%** and
  trial 118 moved **-1.014395071695523%**, agreeing with the prediction
  to **-4.7e-27 pp** and **+2.3e-26 pp** respectively. This is a check of
  the recorder against its own inputs, not a performance statement. The
  two books moved identically because they held identical exposures on
  08-24; **no cross-track structural statistic is computed today**,
  because operator-attention item (d) below is still open and, pending a
  rule, the loop does less rather than more. That is now the **third**
  consecutive iteration of abstention.

- **Where the only unbiased evidence actually stands, stated as a
  fraction for once.** The crypto tracks hold **31 real forward rows**
  against the **706-day** MinTRL fixed in iteration 25 — **4.39%** of the
  way to the date at which a return-based forward verdict first becomes
  statistically permissible (**2028-06-29**). This is arithmetic on rows
  already counted above, and it is recorded because it is the honest
  scale of the wait: at one row per day, the remaining 675 rows are the
  binding constraint on this entire program, and no amount of analysis
  shortens them.

- **Slot ledger over the thirteen scheduled 21:37 slots 08-14..08-26,
  each classified from its own log.** Confirmed complete (`exit=0`),
  **eight**: 08-15, 08-16, 08-19, 08-21, 08-22, 08-23, 08-24, and 08-25
  (`exit=0 finished=2026-08-25T21:49:00.6718758+08:00`, which converts
  iteration 49's in-flight fifth into a confirmed one). Losses, **four**,
  all operator-side and none a repo defect: 08-14 `exit=1` (auth), 08-17
  `exit=1` (weekly account usage limit, 218 bytes), 08-18 zero bytes
  (operator restart), 08-20 `started=` with no `exit=` (console-control
  kill, 43 bytes). In flight, **one**: 08-26, `started=2026-08-26T21:37:
  02.0330289+08:00`, 43 bytes. That makes the completed streak **five
  (08-21..08-25)** with today the sixth in flight. **A reading caution
  for whoever audits this next:** today's in-flight log and the 08-20
  killed log are **both 43 bytes and both "started= with no exit="** —
  the start marker distinguishes *started* from *never started*, but it
  does **not** by itself distinguish *interrupted* from *still running*.
  Only the file's age relative to the reading time does. Do not classify
  08-26 from size alone.

- **Step 2 (web research): the closest crypto relative gives up its
  design, not its results, and one channel is retired.** Nine items filed
  in `RESEARCH_LOG.md` under iteration 50. The substantive ones:

  - **Zarattini, Pagani and Barbon, "Catching Crypto Trends" — partially
    located.** SSRN 403 again (second consecutive iteration), so the full
    text is **still unread**. Reachable instead: **RePEc/IDEAS
    `chf/rpseri/rp2580`**, which supplies the verbatim abstract and the
    identifier **Swiss Finance Institute Research Paper 25-80**; and
    **CXO Advisory's review**, whose free portion states the design and
    then paywalls every result. Design as that review states it: Donchian
    lookbacks of **5, 10, 20, 30, 60, 90, 150, 250 or 360 days**,
    **long-only**, **January 2010 to mid-March 2025**, **21,616**
    crypto-assets, costs tested at **0.10% / 0.25% / 0.50%**, sizing to
    **25% target annualized volatility** capped at **200%** leverage.
    All second-hand, none verified against the paper.
  - **The redundancy question is not advanced by it, and is not recorded
    as if it were.** The abstract's correlation clause is "correlations
    between crypto-focused trend-following strategies and those applied
    to traditional asset classes" — **cross-asset-class**, not
    **between-lookback**. So the ensemble-breadth question stays at
    **four arrivals**, unchanged from 2026-08-25, and today's item is
    **explicitly not counted as a fifth**. [**CORRECTED 2026-08-27,
    iteration 51 — the count inherited here is three, not four; see the
    correction marker in iteration 49's closing paragraph. Today's
    abstention from counting a fifth was correct for its own reason and
    is unaffected.**]
  - **What it does advance is the structural observation, now
    corroborated inside this program's own asset class and direction.**
    This program's windows are **10, 20, 55, 110** (verified today from
    `config.windows` on the live rows, not from memory). The closest
    crypto, long-only, Donchian-ensemble relative uses **nine** lookbacks
    from **5 to 360 days** — one faster than our fastest and **three
    (150, 250, 360) longer than our longest**; span **11x here against
    72x there**. Iteration 49's liquid-futures observation pointed the
    same way. Two independent structural datapoints now say this
    ensemble sits at the **narrow, short end** of what the literature
    builds. Recorded as **structure only**: not a performance claim, not
    evidence a longer window would help here, and **not testable** under
    P3.
  - **A discrepancy left standing rather than smoothed:** the abstract
    says "all cryptocurrencies traded since **2015**", the review says
    the sample starts **January 2010**. Both quoted as their sources
    state them; neither adopted.
  - **Two further outside crypto results, both filed with their
    selection language intact.** Bysik and Ślepaczuk (arXiv
    **2606.00060**, 2026-05-19): hourly BTC-USDT, 2018-2026, 27-fold
    walk-forward; naive sign strategies **fail at 10 bps**, a
    cost-magnitude threshold restores profitability "in selected
    configurations", best long-only arm >**65%** annualized at Sharpe
    >**1**. Bui and Nguyen (arXiv **2602.11708**, 2026-02-12):
    6-hour bars, long-short 70/30, 150+ pairs, 2022-2024, Sharpe
    **2.41**, drawdown **-12.7%**, Calmar **3.18**. **Both
    testable-here: no** — hourly/6-hour and, for the second, long-short,
    all outside product law. Neither abstract mentions a deflated
    Sharpe, a multiple-testing correction or a PBO, so both headlines
    are **selected maxima until shown otherwise**.
  - **Mackic (2023), the 0.17 fast-versus-slow correlation, traced but
    not read.** It is citation `bib.bib14` of the liquid-futures paper;
    a search points to **Adi Mackic (Man AHL), "High-Level Statistics of
    Trend-Following Speeds", 2023**, on Man Group data 1995-01 to
    2022-08. **The number was not found in any primary source today**, so
    it is filed as a **pointer, not an arrival**, and may not be cited as
    a measurement.
  - **Channel closed: recent-regime crypto trend versus buy-and-hold.**
    Three consecutive empty passes; today it was **not queried**.
    **Reopen condition fixed in advance:** a named source measuring a
    trend rule against its own passive twin on a **stated sample with
    stated costs** — a citable measurement, not an outlook or a price
    forecast.

- **Operator-attention items.** All four carried forward; **no new one is
  added today**. (a) The ensemble-breadth question is still with the
  operator: *should a leave-one-window-out ablation of 10/20/55/110 be
  run, knowing it costs an N, is a P3-forbidden family arm, and would
  very likely destroy trial 118's single gate-4 pass?* Today's material
  does not change the recommendation-free framing, but it sharpens one
  side of it: the **redundancy** number is still nowhere in the
  literature for a crypto ensemble, while the **structural** point that
  this ensemble is short and narrow now has a second, crypto-native
  corroboration. Those pull in opposite directions — the first says our
  ablation cannot be replaced by a citation, the second says the
  interesting arm might be a **longer** window rather than a dropped one,
  and that is a *new family*, which P3 forbids outright. The decision
  remains the operator's; the loop proposes nothing. (b) The research
  loop still runs in a **visible console window**; task definition
  unchanged, choice stays with the operator. (c) The weekly account usage
  limit and the auth expiries are account-level matters only the operator
  controls. (d) Should cross-track structural comparisons of the shadow
  files be brought explicitly under
  `FORWARD_TRACK_READ_PREREGISTRATION.md`? Still unanswered; today the
  loop **abstained** from that class of comparison for the third
  consecutive iteration.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken** over 81
  files and 325 dependencies; `pytest -m "not network"` **383 passed** in
  49.82s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written, no
  window-ablation arm run, no long-window family opened despite today's
  structural finding pointing at one, no cross-track structural statistic
  computed while item (d) is open, no scheduled-task definition altered,
  no `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. The CXO Advisory
  design figures were **not** adopted as facts about the Zarattini paper
  — they are labelled second-hand at every point of use — and the
  2010-versus-2015 discrepancy inside them was recorded rather than
  resolved by preference.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by ~17 bps, inside tested headroom; the October holdout
  is protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails, and the ensemble's **internal** breadth remains **unmeasured** —
  four outside arrivals point at it [**CORRECTED 2026-08-27, iteration 51 —
  three distinct sources from three groups; the tally double-counted arXiv
  2510.23150v2.**], none of them crypto, and the closest
  crypto relative is now known **not** to contain the measurement, so if
  the operator wants that number it must be run rather than cited;
  **nothing is forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**, a date the tracks are
  **4.39%** of the way to; the single gate-4 pass holds only for a
  stopped search; the framework has exercised exactly two gates, both
  defective. On-chain route open but unadvanced. Operator-attention items
  dated 2026-08-26 are the four above, all carried forward.

## 2026-08-27 — iteration 51 (P1: seventh slot in flight; two "new" sources on the open operator question are the same authors as an existing one, and the arrival tally is corrected downward)

- **Step 0 convergence check, done first and in writing.**
  1. **Current answer, unchanged:** measured on 2018-2025 and not
     forward-validated, the timing rule adds real value **in crypto
     only** — 4.70x its exposure-matched passive twin, and in its own
     BTC/ETH universe it bought **both** return (14.26x vs 6.05x) and
     drawdown (33.05% vs 80.99%). Against the naive thirteen-coin
     alternative the margin is only **5.4%** and that benchmark is
     survivorship-flattered. **Nothing here passes the six gates**, and
     the one gate-4 pass exists only for a stopped search.
  2. **What this iteration moves.** It shrinks the evidence base under
     the one decision sitting with the operator, and does so in two
     independent ways. First, the two sources found today — arXiv
     **2507.15876** and the CFA Institute post of 28 Jan 2026 — would
     naively have been logged as a fifth and sixth arrival on the
     ensemble-breadth question. They are by the **same six authors**
     (Ai For Alpha) as arXiv **2510.23150v2**, which is already an
     arrival, and the CFA post reuses that paper's exact horizon set
     {20, 60, 125, 250, 500}. Independence added: **zero**. Second, and
     larger, the standing tally of **four** arrivals is itself an
     **overcount**: the "fourth" is arXiv 2510.23150v2 counted a second
     time, once from its abstract in iteration 46 and again after being
     read in full in iteration 49. **Corrected to three distinct sources
     from three groups**, in place, in both iterations that carry the
     wrong number. The escalation to the operator stands — three was
     always its trigger — but the operator was told the question had one
     more independent source behind it than it does.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial, no backtest, no gate report, no arm run, no
     pre-registration written or touched, no window family opened. The
     web pass is contract-mandated (step 2, "never skip"). The only
     computation performed is the recorder consistency check on today's
     new row plus one division against the MinTRL horizon, both of which
     read numbers already on disk and neither of which produces a
     performance quantity. The three edits to prior entries are
     **corrections of this program's own bookkeeping**, in the
     bracketed in-place form iteration 48 established, and every one of
     them makes a claim smaller.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 33 (32 real + seed) | 2026-08-26, equity 1110.589816469934375057190868, exposure `{BTC: 0.75, ETH: 1}`, closes 79023.75 / 2506.78 | OK — +1 row since iteration 50 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 33 (32 real + seed) | 2026-08-26, equity 1154.399253956324671407399122, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 50 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly; unchanged is correct, next run 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series now span 2026-07-24..2026-08-26 with **exactly one
  date gap**, the pair 2026-08-08 to 2026-08-10, i.e. the missing date is
  **2026-08-09** — the permanently lost row from iteration 42, unchanged
  and still left as a hole. Scheduler state read during this iteration:
  `CryptoShadowTrial88` last ran **2026-08-27 15:19:37** result 0, next
  2026-08-28 08:20; `TwShadow0050` last ran 2026-08-22 09:40:00 result 0,
  next 2026-08-29 09:40; both `Ready`, both `NumberOfMissedRuns 0`.
  `CryptoQuantDailySignalCycle` (the live 08:05 runtime, read but not
  touched by research) last ran 2026-08-27 15:19:37 result 0, next
  2026-08-28 08:05. `CryptoResearchLoop` reports `Running` with
  `LastTaskResult 267009` (`STILL_ACTIVE`) — this iteration in flight.
  `docs/reports/research/holdout_lock.json` re-verified: `spent` still
  `false`. At 32 real rows the tracks are **4.53%** of the way to the
  706-row MinTRL horizon of 2028-06-29.

- **A duplicate invocation was refused again today — the second
  consecutive day this can be shown from same-day logs.** The **08:20**
  scheduled run appended the 2026-08-26 rows
  (`data/runtime/shadow_runs/shadow_20260827_082001.log`: "trial88:
  appended 2026-08-26", "trial118: appended 2026-08-26", `exit=0
  finished=2026-08-27T08:20:04.7182205+08:00`). At **15:19** the task
  fired again — the `MSFT_TaskSessionStateChangeTrigger` set added by
  iteration 43 — and wrote **no row**: `shadow_20260827_151937.log`
  reads "trial88: already recorded through 2026-08-26", "trial118:
  already recorded through 2026-08-26", `exit=0
  finished=2026-08-27T15:19:42.4131561+08:00`. Line counts confirm it:
  33 and 33, not 34. Two observed refusals on two consecutive days is
  weak evidence but it is evidence, and it is the kind iteration 43's
  argument needed. The distinction drawn there still stands: the same
  triggers on `CryptoResearchLoop` would remain unsafe, because a
  research iteration is not idempotent.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-25 to 2026-08-26 BTC closed **+0.617030%** (78539.14 to
  79023.75) and ETH **+2.625847%** (2442.64 to 2506.78). Applying the
  exposures recorded on the 08-25 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — gives a predicted book move of **+1.544310%**,
  and both books moved **+1.544310%**, a difference of **0.0000000000pp**.
  This is a check of the recorder against its own inputs, not a
  performance statement. The two books moved identically because they
  held identical exposures on 08-25; **no cross-track structural
  statistic is computed today**, because operator-attention item (d)
  below is still open and, pending a rule, the loop does less rather than
  more.

- **Slot ledger over the fourteen scheduled 21:37 slots 08-14..08-27,
  every one re-classified today from its own log rather than carried.**
  Confirmed complete (`exit=0`), **nine**: 08-15, 08-16, 08-19, 08-21,
  08-22, 08-23, 08-24, 08-25 and 08-26
  (`exit=0 finished=2026-08-26T21:48:45.0118775+08:00`, 5960 bytes,
  which converts iteration 50's in-flight sixth into a confirmed one).
  Losses, **four**, all operator-side and none a repo defect: 08-14
  `exit=1` (auth), 08-17 `exit=1` (weekly account usage limit, 218
  bytes), 08-18 zero bytes (operator restart), 08-20 `started=` with no
  `exit=` (console-control kill, 43 bytes). In flight, **one**: 08-27,
  `started=2026-08-27T21:37:02.2347665+08:00`, 43 bytes. The completed
  streak is therefore **six (08-21..08-26)** with today the seventh in
  flight. Iteration 50's reading caution applies again and was applied:
  today's in-flight log and the 08-20 killed log are both 43 bytes and
  both `started=` with no `exit=`, and only the file's age relative to
  the reading time separates them.

- **Step 2 (web research): the two most promising unread leads were
  read, and both collapsed into a source already on the record.** Six
  items filed in `RESEARCH_LOG.md` under iteration 51. The substantive
  ones:

  - **arXiv 2507.15876 (Benhamou, Ohana, Etienne, Guez, Setrouk,
    Jacquot; 17 Jul 2025) read in full from the arXiv HTML.** Short-term
    trend on lookbacks **{10, 20, 40, 60}** days, long-term trend on
    **500** days, sample **Jan 2010 – Jun 2025**. Table 3 Sharpe row as
    printed: **LTT 0.39, MKT 0.40, STT+LTT 0.40, STT 0.20,
    MKT+STT+LTT 0.45, MKT+STT 0.49, SG CTAT 0.03**. Read plainly:
    adding an entire fast band on top of a 500-day slow model moved
    Sharpe **0.39 to 0.40**, and plain market beta alone also scored
    0.40; the paper's case for the blend rests on **Sharpe/MaxDD =
    2.37**, quoted verbatim, not on Sharpe. This is the **second**
    measurement this loop holds of what a horizon band is worth on top
    of an existing ensemble — the first being iteration 49's
    leave-one-out arm at **+0.03** full-sample Sharpe while losing in
    two of four subperiods. **Both are in the hundredths.**
  - **The between-horizon correlation is absent here too.** The paper
    reports correlation *to the SG CTA benchmark* (STT 0.65, LTT 0.81,
    blend 0.84), not between the factors. A summarizing first read
    offered a "0.24-0.50 overlap" figure; a targeted second read found
    no such printed number, so it is **discarded, not recorded** — the
    same handling iteration 46 gave its retracted 0.36-to-0.40 figure.
  - **CFA Institute, "Decoding CTA Allocations by Trend Horizon" (28
    Jan 2026) read.** Five mono-horizon sleeves at **20, 60, 125, 250,
    500** trading days; sample stated only as "the last five years"
    with **no start date**; correlations given are sleeve-to-index
    (125d and 250d ~82%, 20d ~66%), not sleeve-to-sleeve.
  - **Why both are subtractions rather than additions.** Byline check:
    arXiv 2510.23150v2 is **Etienne, Ohana, Benhamou, Guez, Setrouk,
    Jacquot**; arXiv 2507.15876 is the **same six names**; the CFA post
    is **four of those six** (Benhamou, Ohana, Guez, Jacquot).
    Affiliation **Ai For Alpha** (Alban Etienne), with Benhamou also at
    Université Paris Dauphine-PSL. The CFA post's horizon set is
    **identical** to arXiv 2510.23150v2's. One group, three
    publications — filed as corroboration inside an existing arrival,
    **not** as new arrivals.
  - **Tally corrected in place, downward, in both entries that carry
    it.** Distinct sources on the ensemble-breadth question are
    **three**: arXiv **2607.19497** (Sepp and Lucic, 21 Jul 2026),
    arXiv **2510.23150v2** (Etienne et al., Ai For Alpha, 28 Oct 2025),
    arXiv **2504.10914v15** (Valeyre, 12 Aug 2026). The "fourth" in
    iteration 49's closing paragraph is source two counted twice —
    logged from its abstract in iteration 46, re-logged after a full
    read in iteration 49. **Iteration 49's own body text had it right**
    ("three arrivals, all liquid-futures") and its closing paragraph
    contradicted it; iteration 50 inherited the closing paragraph.
  - **Structural position, restated without inflation.** Our windows
    **10, 20, 55, 110** sit at or below Ai For Alpha's 125-day sleeve
    and below the median lookback of the 5-to-360 crypto relative from
    iteration 50. That remains **two** independent structural
    datapoints, the same two iteration 50 claimed — today's material
    does **not** make it three. Structure only: not a performance
    claim, not evidence a longer window would help here, and pointing
    at a longer-window family that **P3 forbids outright**.
  - **The closed channel stayed closed.** Recent-regime crypto trend
    versus buy-and-hold was **not queried**, per the reopen condition
    fixed in iteration 50. SSRN was not retried today either; the
    Zarattini paper remains second-hand and unread, unchanged.

- **Operator-attention items.** All four carried forward; **no new one
  is added today**, but item (a) is **restated with a corrected
  number**. (a) The ensemble-breadth question is still with the
  operator: *should a leave-one-window-out ablation of 10/20/55/110 be
  run, knowing it costs an N, is a P3-forbidden family arm, and would
  very likely destroy trial 118's single gate-4 pass?* The correction
  that matters for the decision: it rests on **three** outside sources
  from **three** groups, not four, and the strand that looks deepest —
  three Ai For Alpha publications — is **one** group, so its apparent
  weight must not be read as replication. Against that, the second
  incremental-value number arrived today and points the same way as the
  first: **+0.01 and +0.03 Sharpe**, both from adding or removing a
  horizon band, both in the hundredths, both without multiple-testing
  correction. The loop still proposes nothing and recommends nothing.
  (b) The research loop still runs in a **visible console window**; task
  definition unchanged, choice stays with the operator. (c) The weekly
  account usage limit and the auth expiries are account-level matters
  only the operator controls. (d) Should cross-track structural
  comparisons of the shadow files be brought explicitly under
  `FORWARD_TRACK_READ_PREREGISTRATION.md`? Still unanswered; today the
  loop **abstained** from that class of comparison for the fourth
  consecutive iteration.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken**;
  `pytest -m "not network"` **383 passed**, 1 warning, in 108.57s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no diagnostic script written,
  no window-ablation arm run, no long-window family opened despite the
  structural finding pointing at one, no cross-track structural
  statistic computed while item (d) is open, no scheduled-task
  definition altered, no `configs/runtime/` or live-runtime file
  touched, no shadow row fabricated, and the 2026-08-09 hole left as a
  hole. The "0.24-0.50 overlap" figure surfaced by a summarizing fetch
  was **not** recorded, because a targeted re-read did not find it
  printed. The three edits to prior LOOP_LOG entries are bracketed
  in-place corrections of this program's own arrival tally, in the form
  iteration 48 established; **no recorded measurement, registry row or
  gate output was altered.**

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by ~17 bps, inside tested headroom; the October holdout
  is protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails, and the ensemble's **internal** breadth remains **unmeasured** —
  **three** outside sources from three groups point at it, none of them
  crypto, one group now three publications deep, and the closest crypto
  relative is known **not** to contain the measurement, so if the
  operator wants that number it must be run rather than cited;
  **nothing is forward-validated and no return-based forward verdict is
  statistically permitted before 2028-06-29**, a date the tracks are
  **4.53%** of the way to; the single gate-4 pass holds only for a
  stopped search; the framework has exercised exactly two gates, both
  defective. On-chain route open but unadvanced. Operator-attention items
  dated 2026-08-27 are the four above, all carried forward.

## 2026-08-28 — iteration 52 (P1: eighth slot in flight; the number the operator was asked to buy an N for turns out to be half-answered inside the registry, at zero N)

- **Step 0 convergence check, done first and in writing.**
  1. **Current answer, unchanged:** measured on 2018-2025 and not
     forward-validated, the timing rule adds real value **in crypto
     only** — 4.70x its exposure-matched passive twin, and in its own
     BTC/ETH universe it bought **both** return (14.26x vs 6.05x) and
     drawdown (33.05% vs 80.99%). Against the naive thirteen-coin
     alternative the margin is only **5.4%** and that benchmark is
     survivorship-flattered. **Nothing here passes the six gates**, and
     the one gate-4 pass exists only for a stopped search.
  2. **What this iteration moves.** It changes the terms of the one
     decision sitting with the operator. Since iteration 47 that
     decision has been posed as: *spend an N on a P3-forbidden
     leave-one-window-out arm, on the strength of three outside sources,
     because this program holds no internal measurement of what one
     horizon is worth.* The last clause is **false**. Experiment 7
     pre-registered a window-set axis and ran it — trials **86-93**,
     registered 2026-07-22 — and the two sets share 20/55/110, so the
     four matched pairs are a **single-window swap of 10 against 220**
     with **exactly one differing parameter key**. The operator can be
     handed a same-universe, same-code, already-paid-for number today
     instead of being asked to authorize a purchase.
  3. **Why it is not sprawl.** No new script, no new research document,
     no trial registered, no backtest run, no gate report regenerated,
     no arm run, no pre-registration written or touched, no result
     document edited, no window family opened. The web pass is
     contract-mandated (step 2, "never skip"). The only computation is
     subtraction between rows already published in
     `trial_registry.jsonl` on 2026-07-22, plus the standing recorder
     consistency check. **Subtracting two published rows does not create
     a trial and does not spend an N** — the eight trials were counted
     in N=93 at the time they ran.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 34 (33 real + seed) | 2026-08-27, equity 1117.971700642271436870919469, exposure `{BTC: 0.75, ETH: 1}`, closes 80249.58 / 2510.94 | OK — +1 row since iteration 51 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 34 (33 real + seed) | 2026-08-27, equity 1162.072331320228810216546166, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 51 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 6 (5 real + seed) | 2026-08-21, close 104.65, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — weekly; unchanged is correct, next run 2026-08-29 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 7 (6 real + seed) | 2026-08-21, close 423.359985, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — same weekly task |

  Both crypto series span 2026-07-24..2026-08-27 with **exactly one date
  gap**, the pair 2026-08-08 to 2026-08-10, i.e. the missing date is
  **2026-08-09** — the permanently lost row from iteration 42, unchanged
  and still left as a hole. Scheduler state read during this iteration:
  `CryptoShadowTrial88` last ran **2026-08-28 08:20:01** result 0, next
  2026-08-29 08:20; `TwShadow0050` last ran 2026-08-22 09:40:00 result 0,
  next 2026-08-29 09:40; both `Ready`, both `NumberOfMissedRuns 0`.
  `CryptoResearchLoop` reports `Running` with `LastTaskResult 267009`
  (`STILL_ACTIVE`) — this iteration in flight.
  `docs/reports/research/holdout_lock.json` re-verified: `spent` still
  **`false`**. At 33 real rows the tracks are **4.67%** of the way to the
  706-row MinTRL horizon of 2028-06-29.

- **Slot ledger, fifteen scheduled 21:37 slots 08-14..08-28.** The
  2026-08-27 slot, in flight when iteration 51 read it, is now confirmed
  complete: `exit=0 finished=2026-08-27T21:51:33.5481676+08:00`, 3794
  bytes. That makes **ten** confirmed complete (08-15, 08-16, 08-19,
  08-21 through 08-27), **four** losses all operator-side and none a
  repo defect (08-14 `exit=1` auth, 08-17 `exit=1` weekly account usage
  limit, 08-18 zero bytes operator restart, 08-20 `started=` with no
  `exit=` console-control kill), and **one** in flight: today's
  `run_20260828_213702.log`, `started=2026-08-28T21:37:02.2647051+08:00`,
  43 bytes. **The completed streak is seven (08-21..08-27)**, with today
  the eighth in flight. Iteration 50's reading caution applies again and
  was applied: today's in-flight log and the 08-20 killed log are both
  43 bytes and both `started=` with no `exit=`; only file age relative to
  reading time separates them.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-26 to 2026-08-27 BTC closed **+1.551217%** (79023.75 to
  80249.58) and ETH **+0.165950%** (2506.78 to 2510.94). Applying the
  exposures recorded on the 08-26 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — predicts a book move of **+0.664681%**, and
  both books moved **+0.664681%**, a difference of **0.0000000000pp**.
  This is a check of the recorder against its own inputs, not a
  performance statement. The two books moved identically because they
  held identical exposures on 08-26; **no cross-track structural
  statistic is computed today**, because operator-attention item (d)
  remains open and, pending a rule, the loop does less rather than more.

- **The substantive finding: experiment 7 already contains a controlled
  single-window contrast, and nobody in this loop had subtracted it.**
  `GOALP_EXPERIMENT7_PREREGISTRATION.md` line 56 declares
  `window set ∈ { {10,20,55,110}, {20,55,110,220} }` and line 80 names
  the axis "Fast (10-110) vs slow (20-220) window sets". Trials 86-93
  ran it as a 2x2x2 grid on 2026-07-22. Verified against
  `docs/reports/research/trial_registry.jsonl`: each of the four
  fast/slow pairs differs in **exactly one parameter key, `dc_windows`**
  — same BTC/ETH universe, same 2018-03-04..2025-07-01 window, same code
  version `6c99598`, identical costs (fee 10 bps, slippage 5 bps,
  `next_bar_open`). The two sets **share 20/55/110**, so the contrast is
  a **single-window swap, 10 against 220**.

  | Exit | Gate | Fast | Slow | ΔSharpe | ΔMDD | equity ratio | trades ratio |
  |---|---|---:|---:|---:|---:|---:|---:|
  | half_low | off | T86 1.091622 | T90 1.066666 | **+0.024956** | −7.2714pp | 0.9928 | 2.1015 |
  | half_low | on | T87 1.122056 | T91 1.096663 | **+0.025393** | −6.9008pp | 0.9274 | 1.8145 |
  | mid_channel | off | T88 1.182061 | T92 1.093639 | **+0.088422** | −14.5784pp | 1.1624 | 1.9335 |
  | mid_channel | on | T89 1.136883 | T93 1.076638 | **+0.060245** | −12.2753pp | 0.9850 | 1.7259 |

  Mean ΔSharpe **+0.049754** (range +0.024956 to +0.088422), positive in
  **4 of 4**. Mean ΔMDD **−10.2565pp**, favourable in **4 of 4**.
  Terminal money is a **wash**: the fast set wins **1 of 4**, mean equity
  ratio **1.0169** — and it pays for that with **1.8939x** the mean trade
  count. So the single window that differs bought **drawdown, and a
  hair of Sharpe, at nearly double the trading** — the same shape as the
  program's headline result, one level down.

- **What the finding is not, stated before it can be over-read.** It is
  **not** the leave-one-out the operator was asked to authorize: both
  arms carry four windows, so it prices one window **against another
  window**, never **against nothing**. A window worth +0.05 against a
  220-day alternative could still be worth more, or less, against its
  own absence. It is also four cells of a single 2x2 grid on two assets
  over one window — the same non-independence iteration 20 recorded when
  it refused to read the eight-member family as eight tests — so
  **"4 of 4" is a sign count, not four independent tests**, and no
  p-value is claimed. And the qualitative half of it was already
  published: `GOALP_EXPERIMENT7_RESULT.md` states under "Also recorded"
  that *"Fast windows beat slow on Sharpe everywhere"*. **That document
  is not wrong and is not edited today.** What was missing was the
  **paired magnitude** and its placement on the same scale as the
  outside literature.

- **Why the magnitude matters more than the direction.** The loop now
  holds **three** measurements of what one horizon band is worth, from
  three sources, and they agree on order of magnitude: **+0.01** (arXiv
  2507.15876, adding an entire fast band of four lookbacks on top of a
  500-day model, Sharpe 0.39 to 0.40), **+0.03** (arXiv 2510.23150v2's
  leave-one-out, full-sample, while losing in two of four subperiods),
  and now **+0.0498** (this program's own single-window swap). All three
  are in the **hundredths**. None carries a multiple-testing correction.
  Against that, the arm the operator was asked about costs an **N**, is a
  **P3-forbidden family arm**, and by iteration 26's arithmetic would
  very likely destroy trial 118's single gate-4 pass — a pass whose
  margin is exactly one trial.

- **Step 2 (web research): four candidates examined, four negatives,
  arrival tally unchanged at three.** Full detail filed in
  `RESEARCH_LOG.md` under iteration 52. Panjabi and Robertson (Man
  Group, AIMA, 17 Jun 2024) print **no** lookback windows, **no**
  single-versus-ensemble Sharpe, **no** between-sleeve correlation and
  run **no** ablation. Tzotchev (QuantPedia, 17 Jul 2024) names only
  2d/32d/1y and prints none of the four either. McClain (LPL Research,
  13 Aug 2026) names horizons "20 days at the fast end to 250 days at
  the slow end" but prints Sharpe by horizon **not at all**. The one
  genuinely interesting item, **arXiv 2602.11708v1 (Bui and Nguyen,
  Talyxion Research, 12 Feb 2026)**, is the first **crypto** trend paper
  this loop has found that prints a component ablation table — Full 2.41
  Sharpe / −12.7% MDD down to 1.34 / −28.6% without monthly
  re-optimization — and **no row of it removes a lookback**, because its
  momentum lookback is a single scalar re-chosen monthly by grid search,
  so there is no horizon ensemble to ablate. It is also **long/short on
  Binance perpetual futures**, outside product law, with a headline
  Sharpe from monthly re-optimization over 36 months and no stated
  multiple-testing correction. Byline check per iteration 51's
  discipline: the Sepp and Lucic `TrendFollowingSystems` repository
  (SSRN 3167787) also surfaced and is the **same authors** as arrival
  (1), filed as corroboration, **not** a new arrival. **Independence
  added today: zero.**

- **Operator-attention items.** Four carried forward, and item (a) is
  **materially restated** for the second consecutive day, this time
  because the loop found evidence it already owned. (a) The
  ensemble-breadth question goes back to the operator **with its terms
  changed**: it was posed as a purchase decision on the premise that no
  internal measurement existed, and an internal one does — experiment
  7's registered single-window swap, mean **+0.0498** Sharpe, **zero
  additional N**. The leave-one-out itself is still unmeasured and still
  P3-forbidden, so the question does not close; but the operator should
  decide knowing that the nearest available number is already paid for
  and agrees with the two outside numbers. **The loop still proposes
  nothing and recommends nothing.** (b) The research loop still runs in a
  **visible console window**; task definition unchanged, choice stays
  with the operator. (c) The weekly account usage limit and the auth
  expiries are account-level matters only the operator controls. (d)
  Should cross-track structural comparisons of the shadow files be
  brought explicitly under `FORWARD_TRACK_READ_PREREGISTRATION.md`?
  Still unanswered; today the loop **abstained** from that class of
  comparison for the fifth consecutive iteration.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken**;
  `pytest -m "not network"` **383 passed**, 1 warning, in 51.19s.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no result document edited —
  including `GOALP_EXPERIMENT7_RESULT.md`, which is correct as written —
  no diagnostic script written, no window-ablation arm run, no
  long-window family opened, no cross-track structural statistic
  computed while item (d) is open, no scheduled-task definition altered,
  no `configs/runtime/` or live-runtime file touched, no shadow row
  fabricated, and the 2026-08-09 hole left as a hole. **No prior entry
  is edited today** — the arrival tally corrected in iteration 51 stands
  at three and today's four candidates add none.

- **Standing answer restated, unchanged in every clause:** timing works
  in crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by ~17 bps, inside tested headroom; the October holdout
  is protected mechanically; the Taiwan and gold negatives are robust to
  dividend treatment; against the naive 13-coin alternative the margin is
  only 5.4% and that benchmark is survivorship-flattered; breadth still
  fails, and the ensemble's **internal** breadth remains **unmeasured in
  the leave-one-out sense** — but it is **no longer wholly unmeasured**,
  because experiment 7's registered single-window swap prices 10 against
  220 at **+0.0498** mean Sharpe, **4 of 4** in sign, at **1.89x** the
  trades, on this program's own data at zero additional N, and it lands
  in the same **hundredths** as the two outside numbers; **nothing is
  forward-validated and no return-based forward verdict is statistically
  permitted before 2028-06-29**, a date the tracks are **4.67%** of the
  way to; the single gate-4 pass holds only for a stopped search; the
  framework has exercised exactly two gates, both defective. On-chain
  route open but unadvanced. Operator-attention items dated 2026-08-28
  are the four above, all carried forward, with (a) restated.

## 2026-08-29 — iteration 53 (P1: ninth slot in flight; the registry holds a *second* single-window swap, it disagrees with yesterday's on the thing that matters, and the zero-N channel is now exhaustively closed)

- **Step 0 convergence check, done first and in writing.**
  1. **Current answer, unchanged:** measured on 2018-2025 and not
     forward-validated, the timing rule adds real value **in crypto
     only** — 4.70x its exposure-matched passive twin, and in its own
     BTC/ETH universe it bought **both** return (14.26x vs 6.05x) and
     drawdown (33.05% vs 80.99%). Against the naive thirteen-coin
     alternative the margin is only **5.4%** and that benchmark is
     survivorship-flattered. **Nothing here passes the six gates**, and
     the one gate-4 pass exists only for a stopped search.
  2. **What this iteration moves.** It corrects yesterday and then closes
     a channel. Iteration 52 handed the operator **one** internal price
     for a window — experiment 7's swap of 10 against 220, mean
     **+0.0498** Sharpe, 4 of 4 in sign, and reported it as *the* nearest
     available number. There is a **second** one. Experiment 8 ran the
     same 2x2 exit-by-gate grid with `{10,20,55,110}` against
     `{10,20,110,220}`, which share **{10,20,110}** — a single-window swap
     of **55 against 220** — and it prices the swap at **+0.0272** mean
     Sharpe, **3 of 4** in sign, with drawdown moving **against** the
     shorter set in **4 of 4**. Yesterday's characterization "one
     internal, all pointing the same way" is therefore wrong on both
     counts, and is corrected here. Then the channel is closed: **all 133
     registered trials carry exactly four windows**, so no further reading
     of the registry can ever produce the leave-one-out itself.
  3. **Why it is not sprawl.** No new script, no new research document, no
     trial registered, no backtest run, no gate report regenerated, no arm
     run, no pre-registration written or touched, no result document
     edited. The web pass is contract-mandated (step 2, "never skip"). The
     only computation is subtraction between rows published in
     `trial_registry.jsonl` on 2026-07-22, an exhaustive count of a field
     already in that file, and the standing recorder consistency check.
     **Subtracting two published rows does not create a trial and does not
     spend an N** — trials 94-101 were counted in N at the time they ran.

- **P1 track state, verified from the files themselves.**

  | Track | Path | Lines | Last row | Health |
  |---|---|---:|---|---|
  | `shadow_trial88` | `data/runtime/shadow_trial88.jsonl` | 35 (34 real + seed) | 2026-08-28, equity 1090.244915564835404897822208, exposure `{BTC: 0.75, ETH: 1}`, closes 77845.87 / 2442.80 | OK — +1 row since iteration 52 |
  | `shadow_trial118` | `data/runtime/shadow_trial118.jsonl` | 35 (34 real + seed) | 2026-08-28, equity 1133.251807726974686274738578, exposure `{BTC: 0.75, ETH: 1}` | OK — +1 row since iteration 52 |
  | `shadow_tw0050` | `D:/TW-Stock-Trading/data/runtime/shadow_tw0050.jsonl` | 7 (6 real + seed) | 2026-08-28, close 106.95, exposure 0.75, `WINDOWS_ON_3_OF_4` | OK — **+1 row**, weekly task fired 2026-08-29 09:40 |
  | `shadow_gld` | `D:/TW-Stock-Trading/data/runtime/shadow_gld.jsonl` | 8 (7 real + seed) | 2026-08-28, close 408.890015, exposure 0.5, `WINDOWS_ON_2_OF_4` | OK — **+1 row**, same weekly task |

  All four tracks gained a row this iteration; the weekly pair had been
  static since 2026-08-21 and refreshed on schedule this morning. Both
  crypto series carry the seed at 2026-07-24 and real rows
  2026-07-25..2026-08-28 with **exactly one date gap**, the missing
  **2026-08-09** — the permanently lost row from iteration 42, unchanged
  and still left as a hole. Scheduler state read during this iteration:
  `CryptoShadowTrial88` last ran **2026-08-29 08:20:01** result 0, next
  2026-08-30 08:20; `TwShadow0050` last ran **2026-08-29 09:40:00**
  result 0, next 2026-09-05 09:40; both `Ready`, both
  `NumberOfMissedRuns 0`. `CryptoResearchLoop` reports `Running` with
  `LastTaskResult 267009` (`STILL_ACTIVE`) — this iteration in flight.
  `docs/reports/research/holdout_lock.json` re-verified: `spent` still
  **`false`**. At **34** real rows the tracks are **4.82%** of the way to
  the 706-row MinTRL horizon of 2028-06-29.

- **Slot ledger, sixteen scheduled 21:37 slots 08-14..08-29.** The
  2026-08-28 slot, in flight when iteration 52 read it, is now confirmed
  complete: `exit=0 finished=2026-08-28T21:49:57.0850632+08:00`, 6868
  bytes. That makes **eleven** confirmed complete (08-15, 08-16, 08-19,
  08-21 through 08-28), **four** losses all operator-side and none a repo
  defect (08-14 `exit=1` auth, 08-17 `exit=1` weekly account usage limit,
  08-18 zero bytes operator restart, 08-20 `started=` with no `exit=`
  console-control kill), and **one** in flight: today's
  `run_20260829_213701.log`, `started=2026-08-29T21:37:01.3082286+08:00`,
  43 bytes. **The completed streak is eight (08-21..08-28)**, with today
  the ninth in flight. Iteration 50's reading caution applies again and
  was applied: today's in-flight log and the 08-20 killed log are both
  43 bytes and both `started=` with no `exit=`; only file age relative to
  reading time separates them.

- **Recorder consistency check on the new row, which passes exactly.**
  From 2026-08-27 to 2026-08-28 BTC closed **-2.995293%** (80249.58 to
  77845.87) and ETH **-2.713725%** (2510.94 to 2442.80). Applying the
  exposures recorded on the 08-27 row — BTC 0.75, ETH 1.00, equal weight
  across the two symbols — predicts a book move of **-2.480097%**, and
  both books moved **-2.480097%**, agreeing to within decimal-division
  dust below 1e-25 pp. This is a check of the recorder against its own
  inputs, not a performance statement. The two books moved identically
  because they held identical exposures on 08-27; **no cross-track
  structural statistic is computed today**, because operator-attention
  item (d) remains open and, pending a rule, the loop does less rather
  than more.

- **The substantive finding: the registry holds two single-window swaps,
  not one, and the second one disagrees.** Iteration 52 found experiment
  7's fast/slow window axis and read it correctly as a single-window swap
  of **10 against 220** (the sets `{10,20,55,110}` and `{20,55,110,220}`
  share 20/55/110). What it did not do was ask whether any *other*
  registered pair has the same property. One does. Experiment 8, declared
  at `GOALP_EXPERIMENT8_PREREGISTRATION.md` line 54-55 as
  `window set in { {10,20,55,110} (fast), {10,20,110,220} (barbell) }`,
  ran trials **94-101** on 2026-07-22 as the same 2x2 exit-by-gate grid.
  Those two sets share **{10,20,110}**, so the contrast is a single-window
  swap of **55 against 220**. Verified against
  `docs/reports/research/trial_registry.jsonl`: each of the four pairs
  differs in **exactly one parameter key, `dc_windows`**, with identical
  universe, identical 2018-03-04..2025-07-01 window, identical code
  version `5e2d50e`, identical strategy id and identical costs (fee 10
  bps, slippage 5 bps, `next_bar_open`), 2676 observation days on both
  sides.

  | Exit | Gate | Shorter `{10,20,55,110}` | Barbell `{10,20,110,220}` | dSharpe | dMDD | equity ratio | trades ratio |
  |---|---|---:|---:|---:|---:|---:|---:|
  | half_low | off | T94 0.972534 | T98 0.920546 | **+0.051988** | +0.2451pp | 1.0713 | 1.0625 |
  | half_low | on | T95 0.954871 | T99 0.924608 | **+0.030263** | +0.2126pp | 1.0431 | 1.0394 |
  | mid_channel | off | T96 1.000378 | T100 0.945654 | **+0.054724** | +0.2120pp | 1.0555 | 1.0558 |
  | mid_channel | on | T97 0.921164 | T101 0.949161 | **-0.027997** | +0.4416pp | 0.8194 | 1.0419 |

  Mean dSharpe **+0.027245**, positive in **3 of 4**. Mean dMDD
  **+0.2778pp**, favourable to the shorter set in **0 of 4**. Mean equity
  ratio **0.9973**, shorter set ahead in 3 of 4. Mean trades ratio
  **1.0499**.

- **Side by side with yesterday, and what changes.**

  | | Exp 7 (BTC/ETH, `6c99598`) | Exp 8 (13 coins, `5e2d50e`) |
  |---|---|---|
  | Window swapped | 10 against 220 | 55 against 220 |
  | Held fixed | 20, 55, 110 | 10, 20, 110 |
  | Mean dSharpe | **+0.049754** | **+0.027245** |
  | Sign count | 4 of 4 | **3 of 4** |
  | Mean dMDD | **-10.2565pp** (favourable 4 of 4) | **+0.2778pp** (favourable **0 of 4**) |
  | Mean trades ratio | **1.8939** | **1.0499** |

  Three consequences, none of which favours buying the arm. (1) **The
  price is not stable**: +0.0498 and +0.0272 differ by nearly two to one,
  so yesterday's figure is one of two prices rather than *the* price.
  (2) **The drawdown story reverses.** Experiment 7's swap bought
  **-10.26pp** of drawdown in 4 of 4; experiment 8's swap pays **+0.28pp**
  against in 4 of 4. Drawdown is the thing this program's headline result
  actually purchased, so a reversal there weighs more than the Sharpe
  agreement. (3) **The turnover is attributable to the fast window
  itself.** Experiment 7's near-doubling of trades arrived with the **10**
  entering, not with the **220** leaving — because swapping 55 for 220
  while holding the 10 fixed leaves trade count essentially unchanged at
  1.05x.

- **What the finding is not, stated before it can be over-read.** The two
  swaps differ in **universe (2 coins against 13), code version, execution
  mode (plain against staggered) and which window moved — all at once**,
  so the gap between +0.0498 and +0.0272 **cannot** be attributed to the
  window position. Each number is valid **inside its own experiment
  only**; reading the pair as a controlled comparison would repeat exactly
  the universe-pooling error retracted on 2026-07-26 and again on
  2026-07-28. Neither is the leave-one-out: both arms in both experiments
  carry four windows, so both price a window **against another window**,
  never **against nothing**. And each is four cells of one 2x2 grid, so
  "3 of 4" and "4 of 4" are sign counts, not tests; **no p-value is
  claimed for either.** The qualitative half of today's finding was
  already published — `GOALP_EXPERIMENT8_RESULT.md` records that "the
  barbell window set (arxiv 2510.23150) also underperformed fast in 3 of 4
  pairings". **That document is correct as written and is not edited
  today.** What was missing was the paired magnitude, the drawdown
  direction and the turnover attribution.

- **The zero-N channel is now closed, by enumeration rather than by
  assertion.** Every one of the **133** registered trials carries
  **exactly four windows** — 48 with a `dc_windows` set, all 133 with a
  four-entry `lookbacks` string, and zero trials anywhere with three. So
  the leave-one-out the operator was asked to authorize **cannot be
  answered by any further reading of the registry at any price**. The
  registry contains exactly **two** window-against-window swaps and
  **zero** window-against-nothing ablations, and this iteration enumerated
  both. "Look harder inside what is already paid for" is no longer a
  route; the decision in front of the operator is a genuine purchase
  decision again, but now with **two** internal prices attached instead of
  one, and with the disagreement between them on the record.

- **Correction owed and paid, same day.** Iteration 52's RESEARCH_LOG
  entry ended "Three measurements, three sources, **one internal**, all in
  the hundredths, **all pointing the same way**." There are **two**
  internal measurements, and they do **not** all point the same way — they
  agree that the effect lives in the hundredths of Sharpe and disagree on
  drawdown, in opposite directions, 4 of 4 each way. Both clauses are
  corrected in today's RESEARCH_LOG entry. Per the loop's practice since
  iteration 51, the correction is recorded in a new entry; **no prior
  entry is edited.**

- **Step 2 (web research): five candidates examined, five negatives,
  arrival tally unchanged at three.** Full detail filed in
  `RESEARCH_LOG.md` under iteration 53. The Beyond Passive Investing
  Substack piece (2026-06-07) that the search engine credited with a
  20 / 60-125 / 500-day leave-one-out **contains no such table** — the
  bands are almost certainly arXiv 2507.15876's, already held; the piece
  is long/short futures, explicitly **gross of costs**, and its author
  disclaims any out-of-sample claim. arXiv 2512.08124 (Yang, 2025-12-09)
  is genuinely **long-only, crypto, daily** but is a neural ranking net
  with no ablation and no DSR/PBO. arXiv 2604.26747 (Huang et al.,
  2026-04-29) is **long-short**, and searched 25 candidate factors with
  **no multiple-testing correction of any kind**. Suominen and Hjalmarsson
  (Financial Management, 2026-07-06) build a **25-strategy** 1-to-12-month
  horizon ensemble and then **never break out a single horizon** — costs
  not deducted at all. The heavyweight, **Moskowitz, Sabbatucci, Tamoni
  and Uhl (2025-12-10)**, mentions "lookback" 122 times and "Sharpe" 143
  times across 66 pages and still does not answer the question: the word
  **"ensemble" appears zero times**, its contribution is a nonlinear
  weighting function rather than horizon breadth, its universe is 53
  futures with **zero crypto and zero spot**, it is **long/short**, and
  "transaction cost" appears **once** as an argument, "deflated" and
  "multiple testing" **zero** times. Byline check per iteration 51's
  discipline: that group is genuinely new and unrelated to Sepp and Lucic,
  Ai For Alpha or Valeyre — but a new group publishing a **negative** adds
  no independence. **Independence added today: zero.**

- **Operator-attention items.** Four carried forward, and item (a) is
  **materially restated for the third consecutive day** — this time
  against yesterday's own restatement. (a) The ensemble-breadth question
  goes back to the operator with **two** internal prices rather than one:
  **+0.0498** (exp 7, 10 against 220, BTC/ETH, 4 of 4, drawdown
  **favourable** 4 of 4, at 1.89x trades) and **+0.0272** (exp 8, 55
  against 220, 13 coins, 3 of 4, drawdown **unfavourable** 4 of 4, at
  1.05x trades). Both are already paid for at **zero additional N**; the
  leave-one-out itself is still unmeasured, still P3-forbidden, and now
  provably **unobtainable from the registry** since no registered trial
  anywhere carries fewer than four windows. **The loop still proposes
  nothing and recommends nothing.** (b) The research loop still runs in a
  **visible console window**; task definition unchanged, choice stays with
  the operator. (c) The weekly account usage limit and the auth expiries
  are account-level matters only the operator controls. (d) Should
  cross-track structural comparisons of the shadow files be brought
  explicitly under `FORWARD_TRACK_READ_PREREGISTRATION.md`? Still
  unanswered; today the loop **abstained** from that class of comparison
  for the sixth consecutive iteration.

- **Verification (rule 7), run bare, all green.** `ruff check` **All
  checks passed!**; `ruff format --check` **128 files already
  formatted**; `mypy --strict src/` **Success: no issues found in 58
  source files**; `lint-imports` **Contracts: 13 kept, 0 broken**;
  `pytest -m "not network"` **383 passed**, 1 warning.

- **What this iteration does NOT do:** no gate rule modified, no frozen
  contract or pre-registration edited, no trial registered, no backtest
  run, no gate report regenerated, holdout untouched and `spent` still
  `false`, no research document created, no result document edited —
  including `GOALP_EXPERIMENT8_RESULT.md`, whose 3-of-4 sign count is
  correct as written — no diagnostic script written, no window-ablation
  arm run, no long-window family opened, no cross-track structural
  statistic computed while item (d) is open, no scheduled-task definition
  altered, no `configs/runtime/` or live-runtime file touched, no shadow
  row fabricated, and the 2026-08-09 hole left as a hole. **No prior entry
  is edited today** — iteration 52's two wrong clauses are corrected by
  new text, not by rewriting the old.

- **Standing answer restated, unchanged in every clause:** timing works in
  crypto only and in its own universe bought both return and drawdown
  (14.26x vs 6.05x, 33.05% vs 80.99%); the 4.70x exposure-matched twin
  edge is audited and robust; the engine is free of look-ahead, verified
  to the cent; execution-latency cost is about -6.4 bps round-trip,
  bounded above by about 17 bps, inside tested headroom; the October
  holdout is protected mechanically; the Taiwan and gold negatives are
  robust to dividend treatment; against the naive 13-coin alternative the
  margin is only 5.4% and that benchmark is survivorship-flattered;
  breadth still fails, and the ensemble's **internal** breadth remains
  **unmeasured in the leave-one-out sense** and is now known to be
  **unmeasurable from the registry at any price** — but it is **not
  wholly unpriced**, because the registry holds **two** registered
  single-window swaps, **+0.0498** and **+0.0272** mean Sharpe, which
  agree in order of magnitude with the two outside numbers and
  **disagree with each other on drawdown, 4 of 4 in opposite
  directions**; **nothing is forward-validated and no return-based
  forward verdict is statistically permitted before 2028-06-29**, a date
  the tracks are **4.82%** of the way to; the single gate-4 pass holds
  only for a stopped search; the framework has exercised exactly two
  gates, both defective. On-chain route open but unadvanced.
  Operator-attention items dated 2026-08-29 are the four above, all
  carried forward, with (a) restated.

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

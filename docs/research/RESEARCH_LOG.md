# External research log (append-only)

Per `docs/contracts/AUTONOMOUS_RESEARCH_LOOP.md` step 2: every iteration
appends 3–5 dated lines — source, claim, testable-here yes/no. Seeded from
`docs/research/EXTERNAL_EVIDENCE_2026-07.md` (2026-07 review): vol-managed
momentum strongest (tested, exp 2); carry dead and product-excluded;
cross-sectional momentum untested here → experiment 3.

## 2026-07-21 — iteration 1 web pass (experiment-3 engine work)

- 2026-07-21 — Springer FMPM 2025 ("Cryptocurrency momentum has (not) its
  moments", link.springer.com/article/10.1007/s11408-025-00474-9): claims
  crypto XS-momentum profits concentrate in high-volatility regimes and are
  fragile to costs; long-short Sharpe > 1 in-sample. Testable-here: **no**
  (long-short excluded by product law), but the fragility warning maps onto
  our absolute-filter arm and cost-sensitivity read-out.
- 2026-07-21 — Cambridge JFQA 2024 ("A Trend Factor for the Cross Section of
  Cryptocurrency Returns"): trend factor from multiple horizons subsumes
  single-lookback XS-momentum; 4-week and 8-week short-horizon trends carry
  most of the OOS explanatory power. Testable-here: **yes as a follow-up
  family** (would need multi-horizon signal engine — parked for post-exp-3
  RESEARCH_LOG hypothesis pool, not this iteration).
- 2026-07-21 — Trakx practitioner note (trakx.io/resources/insights/
  momentum-trading-in-cryptocurrencies-guide): large-cap crypto momentum
  usually rebalanced monthly, 50–200% annual turnover typical; weekly on a
  small universe magnifies cost drag. Testable-here: **yes** — the family's
  weekly-vs-monthly arm directly measures this, and our ≤ 53.1 turnover cap
  in the pre-registration lines up with the practitioner range.
- 2026-07-21 — ACFR AUT working paper ("Time-Series and Cross-Sectional
  Momentum in the Cryptocurrency Market"): TS and XS momentum are correlated
  but XS wins when the universe is homogeneous large-cap USDT pairs.
  Testable-here: **yes indirectly** — winner's return correlation with
  trial 4 (TS ensemble) is already the pre-declared diversification
  read-out; nothing new to add to the grid.

## 2026-07-21 — iteration 3 web pass (experiment-4 result read-out)

- 2026-07-21 — Ali Azary Medium 2025-04 ("Regime-filtered risk-adjusted
  momentum strategy with inverse-volatility weighting") aliazary.medium.com/
  regime-filtered-risk-adjusted-momentum-strategy-with-inverse-volatility-
  weighting-12-to-655-b145d64d8cf9: combines (a) market-regime filter that
  gates trading to bullish trend, (b) risk-adjusted momentum selection,
  (c) inverse-volatility weights, (d) trailing stop-loss for tail control.
  Testable-here: **yes** — item (a) is the natural next lever to try after
  exp-4 confirmed vol-target overlay alone cannot compress MDD without
  destroying Sharpe. Candidate as experiment-5 pre-registration:
  BTC-200d-SMA regime gate applied to trial 29's architecture.
- 2026-07-21 — glassnode / bitcoinmagazinepro dashboards on 200-DMA regime
  use: 200-day SMA is the most commonly cited macro-regime marker; positions
  entered only above 200-DMA "reduce exposure to prolonged bear markets"
  (search corroboration, not a formal paper). Testable-here: **yes as gate,
  not as signal** — implementation is one boolean per decision day
  (BTC close_t > SMA200_t on the decision bar), which fits the cs decision
  cadence and reuses candle data already loaded.
- 2026-07-21 — Zarattini/Pagani/Barbon SSRN 2025 ("Catching Crypto Trends:
  A Tactical Approach for Bitcoin and Altcoins", papers.ssrn.com/sol3/
  Delivery.cfm/5209907.pdf): daily-rebalanced Donchian breakout ensemble
  with vol-based position sizing on a BTC+altcoin universe reports
  material MDD reduction vs. buy-and-hold. Testable-here: **partially** —
  Donchian is a different SIGNAL, not a wrap on the cs book; parked as an
  alternative architecture for a later family, not the immediate next step.
- 2026-07-21 — arxiv 2601.05716 ("When the Rules Change: Adaptive Signal
  Extraction via Kalman Filtering and Markov-Switching Regimes"): argues
  crypto strategies must be regime-adaptive because parameter stability
  breaks across cycles. Testable-here: **not directly this project**
  (Markov-switching classifier is an engine-scale addition; premature
  before we have exhausted the simpler regime-gate hypothesis).

## 2026-07-22 — iteration 8 web pass (experiment-8 engineering prerequisite)

- 2026-07-22 — arxiv 2510.23150 ("Revisiting the Structure of Trend Premia:
  When Diversification Hides Redundancy", 2025-10-28): dynamic per-asset
  weighting across trend horizons via Bayesian optimization; medium-term
  band (~125d) contributes little incremental performance or diversification
  once short and long are included; a barbell of short+long trends beats
  equal-weight three-band on Sharpe and drawdown while retaining benchmark
  correlation. Testable-here: **yes as a follow-up family** — our Donchian
  ensemble already spans 10/20/55/110 (short + medium) and 20/55/110/220
  (medium + long); a barbell arm (e.g. 10+20+110+220) is a natural addition
  once the wider universe is running. Not this iteration's scope.
- 2026-07-22 — CoinAPI + Concretum practitioner notes on survivorship bias
  (coinapi.io/blog/how-to-eliminate-survivorship-bias-in-crypto-backtesting,
  concretumgroup.com/building-a-survivorship-bias-free-crypto-dataset-with-
  coinmarketcap-api/): point-in-time universe construction (include symbols
  as of the historical decision date, not the terminal snapshot) is the
  standard fix; naive "all symbols traded today" datasets inflate returns
  200–400% in crypto. Testable-here: **yes and load-bearing for exp-8** —
  UNIVERSE_EXPANSION.md already qualifies 13 symbols with staggered listing
  dates; the engine change this iteration is the mechanical prerequisite so
  each symbol participates only from its own listing day onward (no
  look-back through the pre-listing window into future returns).
- 2026-07-22 — StratBase.ai note on delisting exposure: even a qualified
  universe carries survivorship risk if the strategy silently averages over
  the intersection of dates instead of using per-symbol eligibility.
  Testable-here: **directly** — this is what the ladder-path change fixes;
  the cross-sectional path already uses the union-of-dates model.
- 2026-07-22 — Zarattini/Pagani/Barbon SSRN 2025 revisited: the paper's
  headline result rests on a survivorship-bias-free dataset covering all
  cryptocurrencies traded since 2015 (per the SSRN abstract) — the SIZE of
  the universe is central to their claim, not incidental. Testable-here:
  **yes** — our 13-symbol qualified universe is the largest exp-8 can start
  with under gate 1, and per the pre-registration will be the test corpus.

## 2026-07-23 — iteration 10 web pass (N-arithmetic weigh-in)

- 2026-07-23 — Lopez de Prado & Fabozzi SSRN 2026-03 ("The False Discovery
  Rate in Finance: Identification Failure and Search-Adjusted Estimation",
  dx.doi.org/10.2139/ssrn.6450418): argues that in strategy search, FDR
  control (not FWER/DSR alone) is the correct target once the search
  budget grows large, because DSR is a per-test null-rejection rate that
  gets more punishing with N regardless of independence structure.
  Testable-here: **partially** — our current stop condition is DSR ≥ 0.95
  AND candidates-PBO ≤ 0.05; PBO is already an FDR-adjacent measure. Load-
  bearing for THIS iteration: it validates the "every family raises every
  trial's bar" arithmetic — spending N without expected-Sharpe headroom is
  strictly negative EV under both frameworks.
- 2026-07-23 — Quanterlab foundations note on DSR (quanterlab.com/articles/
  foundations-dsr): E[max SR|null] grows as √(2·ln N) times cross-trial
  Sharpe std; for our N=101→117 step that's a ~1.5% expected-max lift
  which raises the pass bar by ~0.007 annualized Sharpe. Testable-here:
  **yes** — plugged into the arithmetic doc this iteration.
- 2026-07-23 — Zarattini/Pagani/Barbon SSRN 2025 headline mechanism
  (papers.ssrn.com/sol3/Delivery.cfm/5209907.pdf): the paper combines a
  Donchian breakout ENSEMBLE with a **volatility-based position sizing**
  step (inverse-vol / target-vol weights) — the two ingredients are
  interlocking, not additive. Testable-here: **yes** — our exp-7/exp-8 ran
  the ensemble on equal budgets; the vol-sizing arm is the untested half of
  the paper's claim and remains the only registered-evidence route left in
  the Donchian lineage. Queued to Q4 (next iteration under drift guard).
- 2026-07-23 — Poluri SSRN 2025 ("Evaluating the Performance of a Donchian
  Channel Breakout Strategy with ATR-Based Risk Management",
  papers.ssrn.com/sol3/papers.cfm?abstract_id=6272239): ATR-scaled sizing
  on Donchian entries on BTC daily materially reduces drawdown vs
  fixed-size; the mechanism is roughly "smaller risk when the channel
  itself is wide". Testable-here: **yes** as a sibling / spec of the
  SSRN-2025 vol-sizing arm — if we add a vol-sized Donchian family,
  ATR-based and realized-vol-based both belong in the same pre-registered
  grid so the family is pre-registered before it runs.

## 2026-07-24 — iteration 11 web pass (experiment-9 scoping, gate-6 pivot)

- 2026-07-24 — Zarattini/Pagani/Barbon SSRN 5209907 revisited on the
  concretumgroup.com companion page ("Catching Crypto Trends"): the
  paper's headline (Sharpe 1.58, CAGR 30%, alpha +14% vs BTC over
  Jan-2015–Mar-2025 on a survivorship-free top-20 rotational book) is
  **jointly** attributed to the Donchian ensemble AND cross-asset
  volatility-based position sizing — the mechanism is inverse-vol
  weighting scaled to a portfolio vol target, NOT per-symbol vol
  overlay. Testable-here: **yes, but the engine feature is a genuinely
  new allocation model** — cross-asset weight normalization and cap
  arm — not a reuse of the per-symbol `_apply_vol_overlay` we already
  have. Load-bearing for the exp-9 scoping verdict this iteration.
- 2026-07-24 — Concretum Group "Position Sizing in Trend-Following:
  Comparing Volatility Targeting, Volatility Parity, and Pyramiding"
  (concretumgroup.com/position-sizing-in-trend-following-...): three
  named methods differ in whether normalization is per-symbol vs
  cross-asset and whether pyramiding is allowed; the trend-following
  results the paper cites (60% monthly hit rate, healthy Sharpe over
  1980–2024) use vol-targeting = cross-asset scale-to-portfolio-vol,
  which matches SSRN 5209907's arm. Testable-here: **yes** — if
  experiment 9 lands, the grid must pre-register vol-parity vs
  vol-targeting explicitly (they are distinct research questions).
- 2026-07-24 — Alvarez Quant Trading "Inverse Volatility Position
  Sizing" (alvarezquanttrading.com/blog/inverse-volatility-position-
  sizing/): concrete formula = per-asset weight ∝ 1/σ_i normalized so
  ∑w = 1; cap arm typically 25% per asset. Testable-here: **yes**;
  the SSRN top-20 book keeps ~5% per name under this rule, but our
  13-symbol universe needs a cap in {1/N, 0.25, 0.50} to stop BTC
  from dominating when altcoin vols spike. Belongs in the exp-9 grid.
- 2026-07-24 — Bloomberg "Cryptocurrency Volatility Target Indices"
  spec (assets.bbhub.io/professional/sites/10/Bloomberg-Vol-Target-
  Specs_Crypto.pdf, 2025-08-05): institutional cash-vs-crypto vol
  target indices; the mechanism scales to underlying-only for
  long-only mandates, matching our product law. Testable-here:
  **not directly** — index construction rules add rebalance bands and
  fee accruals we would not want to import — but the vol targets in
  common use (10% / 15% / 25%) anchor a reasonable grid range for
  our exp-9 target-vol arm.

## 2026-07-25 — iteration 12 web pass (gate-6 evidence + holdout hygiene)

- 2026-07-25 — Bybit Q1 2026 spot execution analysis via TradingView
  news feed (tradingview.com/news/chainwire:ee08acbdf094b:0-...):
  reference-order US$10k BTC spot slippage measured 0.01 bps on Bybit
  vs 0.02–0.06 bps on peer venues, with the RPI mechanism accounting
  for the improvement. Testable-here: **yes as a sanity anchor** —
  our current gate-6 baseline of median 0.00 bps BTCUSDT / 0.05 bps
  ETHUSDT (`data/runtime/events.jsonl`) is inside the same
  order-of-magnitude band as an institutional publication, i.e. our
  spread capture is not obviously miscalibrated; nothing to add to
  a family grid, everything to add to the gate-6 rehearsal note.
- 2026-07-25 — QuantMedia "Slippage and Latency Modeling: Realistic
  Backtesting in Python" (quantmedia.io/paper-slippage-latency-
  modeling.html): backtest engines that use mid-quote fills overstate
  Sharpe by 0.5–1.0 versus a decision-to-fill model that includes
  spread crossing + market-impact (square-root law) + stochastic drift
  during the latency window. Testable-here: **yes, defensively** —
  the specific number our `configs/costs/` cost model already books
  (~20 bps round-trip vs a 37.5–45 bps gate-6 cap) implicitly assumes
  the drift term is small; already-recorded `exec_quote` events make
  the arithmetic a query away, not a new family. Belongs in gate-6,
  not in trials.
- 2026-07-25 — Turbine blog "Why Your Backtest Said +20% But Live
  Trading Lost Money" (turbinefi.com/blog/why-backtests-lie-prediction-
  market-overfitting-2026): argues live-vs-backtest divergence on
  paper-trading books is dominated by (a) stale-side fills the backtest
  assumes are mid, and (b) selection bias from picking the "best"
  backtest out of many. Testable-here: **yes and both are already
  gated** — (a) is what decision→capture drift in the runtime quote
  stream is for (queued gate-6 work), (b) is exactly what the DSR
  deflation + PBO framework corrects for. Reinforces the
  no-new-families standing decision at margin 0.0001.
- 2026-07-25 — VARRD "Out-of-Sample Testing in Trading — The Sacred
  One-Shot" (varrd.com/guides/out-of-sample-testing.html): explicit
  restatement of the one-shot protocol — a holdout that gets peeked
  at, tweaked against, or re-tested is not a holdout. Testable-here:
  **yes, procedurally** — matches `PRE_HOLDOUT_PROTOCOL.md` exactly;
  useful as an external anchor for the operator-facing holdout
  rehearsal note this iteration produces (nomination → freeze →
  single `--spend-holdout` run → publish, no re-runs, no
  post-hoc grid searches).

## 2026-07-26 (iteration 13) — sleeve-independence external evidence

- 2026-07-26 — Man Group "A Trend Following Deep Dive: Cash (Equities)
  Is King" (man.com/insights/trend-following-cash-is-king): directional,
  time-series sector trend following retains a rolling-24-month
  correlation of ~0.81 to equity-index trend over a 21-year sample.
  Cross-sectional sector trend delivers the diversification; univariate
  sector trend does not. Testable-here: **yes, defensively** — our
  crypto/Taiwan/gold sleeves are univariate trend on three markets,
  which this paper says will remain highly correlated in the tails; a
  fourth univariate sleeve is not safely assumed to be independent.
  Reinforces the P2 buy-and-hold gate before any fourth sleeve.
- 2026-07-26 — arXiv 2510.23150 "Revisiting the Structure of Trend
  Premia: When Diversification Hides Redundancy": principal-components
  decomposition of multi-market trend books shows the effective number
  of independent bets is materially lower than the number of sleeves;
  most of the risk sits on a small set of common factors. Testable-here:
  **yes, as a read-only diagnostic on the three-sleeve book** — compute
  PCA on the daily sleeve returns already recorded and report
  effective-N vs nominal N=3. Belongs in a diagnostic doc, not a new
  family.
- 2026-07-26 — Man Group "A Trend Following Deep Dive: The Dynamics of
  Dispersion" (man.com/insights/deep-dive-trend-following): 2020-2025
  window, {20d, 60d, 125d, 250d, 500d} CTA horizons — only 20d and 500d
  reached ~160 cumulative index; 60d and 125d stalled at ~120; the gap
  widened after 2022 dispersion regime. Testable-here: **yes,
  interpretively** — our Donchian ensemble is {10, 20, 55, 110} bars
  daily, straddling the underperforming 60/125-day middle. Not
  actionable as a new family (P3 refuses), but useful when the operator
  weighs a fourth sleeve at a very different horizon.
- 2026-07-26 — QuantInsti "Donchian Channels: How to Turn a Simple Idea
  Into Working Strategies" (blog.quantinsti.com/donchian-channel-
  strategy/): explicit finding that a Donchian rule tuned on one date
  range typically degrades on the next, and that the in-sample /
  out-of-sample gap is a stronger robustness signal than any single
  backtest number. Testable-here: **yes as prior anchor** — matches our
  own PBO 0.7411 and trial 118's cross-market refutation; useful to
  cite when the operator asks whether the crypto search history really
  contaminates the Taiwan/gold transfer (it does; this is an
  independent voice saying so).
- 2026-07-26 — etfdb "Alternatives ETFs Punching Above Their Weight in
  2026" (etfdb.com/equity-etf-content-hub/alternatives-etfs-punch-
  above-weight/): DBMF and CTA managed-futures ETFs took large 2026
  inflows as bond-heavy allocators diversified. Testable-here: **no,
  directly** — those are levered multi-asset futures books, not a
  spot/long-only sleeve within product law. Useful only as a market
  context note: institutional demand for trend diversification is not
  evidence that a univariate long-only spot trend rule generalizes to
  a new market, which is what our P2 gate exists to check.
- 2026-07-27 — Coin Bureau "How to Backtest a Crypto Strategy in 2026"
  (coinbureau.com/guides/how-to-backtest-your-crypto-trading-strategy):
  claim that **2-4 weeks of paper/shadow trading** is a typical
  practitioner threshold to separate a backtest survivor from live
  failure, and that walk-forward re-optimisation should not be
  substituted for it. Testable-here: **no, directly** — three shadow
  tracks began 2026-07-24 and are ~3 days in; the claim places a first
  honest read no earlier than 2026-08-07 and a real read closer to
  2026-08-21. Useful as a **calendar anchor** for when to stop asking
  "does the shadow track say anything yet" (answer: not before ~Aug 21).
- 2026-07-27 — QuantInsti/Altrady/LuxAlgo/PyQuantLab Donchian repostings
  (quantzee.com/crypto-trading-indicators; altrady.com/blog/crypto-
  trading-strategies/donchian-channel-strategy; luxalgo.com/blog/
  donchian-channels-breakout-and-trend-following-strategy):
  consistently reported that a 55-day Donchian mid-line trend filter
  raises BTC daily long-signal win rate from ~50% to ~55%, and that
  mid-channel exits systematically outperform reversal-band exits for
  capital preservation across BTC, gold, and equity indices.
  Testable-here: **partially, as a prior** — trial 88 already uses
  mid_channel exit and windows straddling 55, so the reported filter
  uplift matches its mechanism claim. Not a new experiment (would need
  a new family, which P3 refuses), but supports the standing answer's
  mechanism claim that the crypto edge is real even if it does not
  generalize to Taiwan or gold.


## 2026-07-28 (iteration 25)

- **Bailey & López de Prado, Minimum Track Record Length (MinTRL)** —
  via `portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-bias-
  adjustment-confidence-intervals-hypothesis-testing-and-minimum-track-
  record-length/`, `papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643`
  ("The Sharpe Ratio Efficient Frontier"), and the CRAN
  `PerformanceAnalytics::MinTrackRecord` reference
  (`rdrr.io/cran/PerformanceAnalytics/man/MinTrackRecord.html`).
  Claim: the track length needed to reject "measured Sharpe is below a
  threshold" at a given confidence, explicitly incorporating skewness,
  kurtosis and sample length. Same authors and same distributional
  machinery as the Deflated Sharpe Ratio already used in gate 4.
  Testable-here: **yes, and tested this iteration.** Applied to trial
  88's own return series (n=2676, SR_ann 1.1823, skew +0.227, kurtosis
  12.775): **MinTRL = 706 days = 2028-06-29** at 95% one-sided against
  SR* = 0; 429 days (2027-09-26) at 90%. Trial 118: 644 / 391 days.
- **Consequence, recorded as a correction rather than a finding:** the
  loop contract's stated unblock condition ("~90 days of forward rows
  ... enough to say anything at all") is wrong by roughly 8x. At 90
  forward days the annualized Sharpe standard error is 2.016, a 95%
  interval of [-2.77, +5.13]. Corrected in place in
  `AUTONOMOUS_RESEARCH_LOOP.md` the same day, per the standing
  correction duty.
- **Sources consulted and rejected as not testable-here:**
  `arxiv.org/pdf/2605.17628` (quantum-annealer portfolio optimization —
  no bearing on a long-only daily spot rule),
  `en.wikipedia.org/wiki/Deflated_Sharpe_ratio` (already implemented in
  gate 4; nothing new).

## 2026-07-28 (iteration 26)

- **Bailey & Lopez de Prado, Deflated Sharpe Ratio — the "number of
  trials" variable** — `papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551`,
  `davidhbailey.com/dhbpapers/deflated-sharpe.pdf`,
  `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`. Claim: DSR integrates
  five inputs — track length, skewness, kurtosis, the variance across
  the Sharpe ratios of all trials, and **the number of INDEPENDENT
  trials**. The standard caution is that a raw backtest count
  **overstates** search breadth, because optimizers run highly
  correlated variations of one core strategy; determining the true
  independent count requires precise recording of all historical
  backtests. Testable-here: **yes, and used this iteration as a
  counterweight against our own finding.** This program uses the raw
  registry count by deliberate choice (`run_gate_report.py:188`,
  "Conservative: raw registry count, no correlation shrinkage"). Its 133
  rows are heavily correlated — mean pairwise 0.628 across nine distinct
  architectures, and 64 of 133 are one cs-momentum lineage — so a
  correlation-adjusted N would be materially below 133 and would give
  trial 118 more margin than the one-trial figure measured today.
  Recorded in `GATE4_FRAGILITY_2026-07-28.md` as a real counterweight
  **and** as a fix that is refused, because adopting it now would be
  changing a gate input after seeing the answer it produces — the same
  move already refused over gate 3.
- **Consulted, not usable here:** `arxiv.org/pdf/2603.20319`
  ("Implementation Risk in Portfolio Backtesting") — quantifies error
  from implementation choices rather than selection bias; relevant to
  Test 1 of the forward-track read rule but not to the trial count.

## 2026-07-28 (iteration 27)

- **Lopez de Prado, methods for the effective number of independent
  trials** — `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`,
  `risklab.ai/research/backtesting/testing_set_overfitting`,
  `paperswithbacktest.com/course/deflated-sharpe-ratio`. Claim: three
  named techniques cluster correlated strategies to recover K
  independent trials — **ONC (optimal number of clusters)**,
  **hierarchical clustering** (a conservative lower bound for N), and
  **spectral methods** on the correlation matrix eigenvalue
  distribution. The full procedure does not stop at a smaller N: it
  forms inverse-variance-weighted aggregate returns per cluster,
  computes an aggregate Sharpe for each of the K independent trials, and
  takes **the variance across those K Sharpes**. Testable-here:
  **yes in principle, deliberately NOT run.** Both gate-4 inputs would
  change and the variance across K cluster aggregates can be larger or
  smaller than across 133 individual trials, so the net effect on trial
  118's 0.950140 is unknown — and choosing among three methods after
  seeing that margin is exactly the post-hoc move that would void the
  answer. Recorded in `GATE4_FRAGILITY_2026-07-28.md` as an
  operator-declares-first item.
- **Consequence found in our own frozen contract, not in the
  literature:** `VALIDATION_GATE_CONTRACT.md` gate 1 line 44 already
  mandates correlation-adjusted `effective_N` with the method recorded,
  and line 75 lists `effective_N` as a gate-4 input. The implementation
  passes the raw count (`run_gate_report.py:190`). This corrects
  iteration 26's claim that adopting effective-N would be a rule change
  — it is the frozen rule; the raw count is a conservative deviation
  from it.

## 2026-07-28 (iteration 28)

- **Benchmark appropriateness criteria** —
  `auroratrainingadvantage.com/finance/investment-management/performance-measurement-benchmarks/`,
  `m1.com/blog/benchmarks-why-choosing-the-right-one-matters/`,
  `assetvantage.com/blogs/portfolio-comparison-against-benchmark/`.
  Claim: a valid benchmark must be measurable, investable,
  **appropriate** (aligned with the portfolio's actual investment
  universe, strategy and constraints), reflective of current investment
  opinion, and **specified in advance**. A frequent error is choosing a
  benchmark by convenience rather than appropriateness — the cited
  example is judging a US large-cap portfolio against a global index.
  Outperformance against a mismatched benchmark reflects universe
  differences, not skill. Testable-here: **yes, and it convicts this
  program's own headline sentence.** Trial 88 trades BTC/ETH; the
  13-coin equal-weight benchmark is neither appropriate to its universe
  nor specified in advance for it. Corrected in
  `VS_BUY_AND_HOLD_2026-07-26.md` and in the contract standing answer.
- **Survivorship, look-ahead and data-snooping from narrow universes** —
  `arxiv.org/html/2505.07750v1` ("The Pitfalls of Benchmarking in
  Algorithm Selection"). Claim: short horizons and narrow universes
  produce survivorship, look-ahead and data-snooping bias that undermine
  claimed improvements. Testable-here: **already recorded** — the
  13-coin universe came from a 2026 eligibility screen, so its 13.53x is
  survivorship-flattered; that caveat now travels with the corrected
  opportunity comparison rather than being a footnote.

## 2026-07-28 (iteration 29)

- **Constant-mix vs buy-and-hold, and where volatility drag comes from** —
  `aqr.com/-/media/AQR/Documents/Whitepapers/AQR_Portfolio-Rebalancing_Common-Misconceptions.pdf`,
  `returnstacked.com/the-rebalance-drag-myth-in-leveraged-etfs-what-advisors-need-to-know/`,
  `en.wikipedia.org/wiki/Rebalancing_investments`,
  `caia.org/sites/default/files/dynamic_strategies_for_asset_allocation.pdf`.
  Claim: constant-mix is a **concave** strategy that outperforms in
  oscillating markets and underperforms buy-and-hold in trending ones;
  the drag itself "arises from the interplay of volatility and
  compounding, not from rebalancing", and rebalancing changes expected
  growth only through its effect on portfolio variance. Testable-here:
  **yes, and used to audit our own headline metric.** The
  exposure-matched twin in `analyze_timing_value.py:139` is a
  continuously-rebalanced constant mix. This window trended (benchmark
  6.0510x), so the literature predicts the constant-mix twin should lose
  to an un-rebalanced fraction twin — measured, it is the other way by
  4.1% (3.03x against 2.9121x), which makes the twin actually used the
  **more conservative** of the two. Either way the edge is 4.71 or 4.90,
  so the headline is not a rebalancing artefact.
- **Consequence recorded in `TIMING_VALUE_2026-07-27.md`** as a closed
  route, together with a second refuted attack: per-symbol mean weights
  read from the trial-88 report are BTC 0.2006 / ETH 0.1780, a 53/47
  split against an equal-weight 50/50 benchmark, so the edge is not
  BTC-over-ETH selection.

## 2026-07-28 (iteration 30)

- **Implementation shortfall and why delay is directional for breakout
  systems** — `cube.exchange/what-is/implementation-shortfall`,
  `quantitativebrokers.com/blog/a-brief-history-of-implementation-shortfall`,
  `ryanoconnellfinance.com/implementation-shortfall/`,
  `markets4you.com/en/blog/market-analysis/how-to-measure-slippage-spread-and-market-impact-before-they-erode-a-winning-strategy/`.
  Claim: implementation shortfall is the gap between the **decision
  price** and the realised execution price, covering market impact plus
  delay cost. It is called out as "particularly dangerous for breakout
  traders and momentum systems", because a breakout entry is identified
  at a level and by the time the order reaches the market liquidity has
  shifted and the fill lands worse. The urgency dilemma: trading fast
  costs impact, trading slow costs delay. Testable-here: **partially,
  and it convicts an unmodelled assumption.** Trial 88 is a Donchian
  breakout whose backtest fills at the next bar's open, which in 24/7
  crypto equals the decision-bar close — i.e. **zero assumed latency**.
  Live lag is ~5 min (paper runtime) to ~20 min (shadow recorder), across
  which BTC's expected absolute move is **16.0 / 32.0 bps** against a
  modelled 5 bps slippage. The adverse *fraction* is not measurable from
  daily candles, so no cost figure is claimed — but the literature says
  the sign is against a breakout system rather than neutral. Recorded in
  `GATE6_BASELINE_2026-07-25.md`.

## 2026-07-28 (iteration 31)

- **Bitcoin intraday volatility and volume seasonality** —
  `sciencedirect.com/science/article/pii/S1059056024006506` ("Intraday
  and daily dynamics of cryptocurrency"),
  `researchgate.net/publication/334727071` ("Time-of-Day Periodicities of
  Trading Volume and Volatility in Bitcoin Exchange"),
  `quantpedia.com/strategies/intraday-seasonality-in-bitcoin`,
  `blog.paperswithbacktest.com/p/bitcoin-never-sleeps-exploiting-seasonality`.
  Claim: crypto volume and volatility are **not uniform across the day**
  — they peak during the LSE/NYSE overlap (**14:00-16:00 UTC**) and
  decline after **20:00 UTC**; the 21:00-23:00 UTC window carries the
  highest average returns. Testable-here: **yes, and it corrects our own
  previous estimate.** Iteration 30 scaled the execution-delay dispersion
  from daily sigma by sqrt(t), implicitly assuming uniform intraday
  volatility. The execution window is **00:00-00:20 UTC**, which this
  literature places in the **quiet** part of the day, so the 16 bps and
  32 bps figures are **overestimates** rather than neutral scalings.
  Recorded in `GATE6_BASELINE_2026-07-25.md`.

## 2026-07-28 (iteration 32)

- **Adaptive data analysis and indirect holdout contamination** —
  `research.google/blog/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis/`,
  `mlbenchmarks.org/04-holdout-method.html`,
  `arxiv.org/pdf/1905.12580` ("Model Similarity Mitigates Test Set
  Overuse"). Claim: the holdout's statistical guarantee assumes the k
  models were chosen **independently** of the test data; in practice
  analysts choose guided by earlier results, and "the moment a scientist
  considers a prior result on a benchmark dataset, the new model now has
  some formal dependency on the test data that invalidates the classical
  theory." The failure mode is **adaptivity** — a feedback loop between
  analyst and data — not only direct fitting. Testable-here: **yes, and
  it names a channel this program had not recorded.** No trial read the
  holdout (verified: all 133 have `data_end` 2025-07-01), but
  `analyze_whipsaw` defaults to the full series and its documented run
  spanned 2024-01 to 2026-06, crossing `holdout_start`; its verdict set
  research priority. Recorded in `HOLDOUT_INTEGRITY_2026-07-28.md` as a
  caveat that must travel with the October result rather than be
  discovered after it.

## 2026-07-28 (iteration 33)

- **Programmatic holdout enforcement — search largely unproductive, recorded
  as such.** Queried for guard-rail patterns that prevent accidental test-set
  access in data pipelines. Results were dominated by LLM guardrail tooling
  (`invariantlabs.ai/blog/guardrails`, `budecosystem.com/llm-guardrails-...`,
  AWS Control Tower) rather than ML data governance. The one on-topic hit,
  `mlbenchmarks.org/pdf/04-holdout-method.pdf`, restates that in theory a
  test set is used once and in practice that is "only sometimes the case",
  and that repeated exposure degrades the generalisation estimate.
  Testable-here: **no established pattern to copy.** Recorded so that the
  engine-level holdout guard (operator decision 2 in
  `HOLDOUT_INTEGRITY_2026-07-28.md`) is known to be a from-scratch design
  rather than an adoption. Reporting the empty result rather than padding it.

## 2026-07-28 (iteration 34)

- **Framework-level enforcement of train/test boundaries** —
  `medium.com/balaena-quant-insights/train-test-split-cross-validation-and-walk-forward-testing-for-on-chain-factors-b5fcf01572e2`,
  `insightbig.com/post/traditional-backtesting-is-outdated-use-cpcv-instead`,
  `research.mental-momentum.ai/r/backtesting-frameworks-llm-trading-bias-l1dnl5`,
  `quantstrategy.io/blog/backtesting-ai-powered-trading-systems-ensuring-robustness/`.
  Claim: leakage prevention should be enforced **at the framework level**,
  "at the architectural level rather than relying on manual
  implementation"; chronological forward-chaining splits ensure the model
  never observes future data; **purging** removes observations adjacent to
  the split boundary. Testable-here: **yes, and it vindicates the codebase
  against our own iteration-32 claim.** `run_registered_backtest` trims
  every non-spend run to `close_time < holdout_start` before the engine
  sees a candle — architectural enforcement, exactly the recommended
  pattern. Purging is not applicable here: this is a chronological
  walk-forward boundary, not a cross-validation split, and the
  qualification run deliberately keeps pre-holdout history so indicators
  with up to 110-day lookbacks are computable at the holdout's first day.
  CPCV purging is already used separately in gate 3.

## 2026-07-28 (iteration 35)

- **Stopping rules for a research programme — search largely off-target,
  recorded as such.** Queried for when to stop a quantitative research
  programme on diminishing returns. Results were dominated by stop-loss
  literature (`sciencedirect.com/science/article/abs/pii/S138641811300030X`,
  `arxiv.org/pdf/1609.00869`), which answers a different question. The one
  on-point line, from
  `kevinrodonnell.com/leveraging-quantitative-market-research-to-avoid-diminishing-returns-in-product-development/`,
  is generic: diminishing returns arrive when further effort yields smaller
  increments of value and additional investment no longer justifies the
  gains. Testable-here: **no external stopping rule found to adopt**, so
  the convergence judgement in this iteration rests on the loop's own
  Step 0 criterion rather than borrowed authority. Second consecutive
  search returning little of substance; recorded rather than padded.

## 2026-07-28 (iteration 36, P1 maintenance)

- `papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565` — Han, Kang, Ryu,
  "Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market:
  A Comprehensive Analysis under Realistic Assumptions". Claim: momentum
  effects in crypto shrink materially once realistic trading assumptions
  (costs, borrowing constraints, execution frictions) are applied.
  Testable-here: **not actionable this iteration** — the queue is P1-only
  (route declared converged iteration 35). Filed for the next family
  window if the operator ever opens P3; would inform any experiment 9
  successor about cost sensitivity, not the existing frozen 133.
- `papers.ssrn.com/sol3/papers.cfm?abstract_id=4825389` — Huang,
  Sangiorgi, Urquhart, "Cryptocurrency Volume-Weighted Time Series
  Momentum". Claim: volume-weighted TSMOM in crypto shows significant
  positive returns using volume-weighted market returns. Testable-here:
  **no** — introduces a volume-weighting parameter that would be a new
  single-market family (P3-refused). Recorded so the same idea is not
  re-searched next iteration.
- Third pass on "trend/momentum in crypto forward-validated 2026" and
  "MinTRL small-sample corrections". Returned only Bailey/Lopez de Prado
  restatements already codified in the standing answer (MinTRL on trial
  88 is 706 days at 95% one-sided vs SR* = 0 = 2028-06-29, per iteration
  25). Testable-here: **already implemented**; nothing new to lift.
- **Meta-observation, recorded rather than acted on.** Three consecutive
  external-research passes have returned no directly-actionable finding
  under this repo's P1-only constraint. Same diminishing-returns pattern
  iteration 35 noted internally. Not a reason to stop Step 2 (which is
  contract-mandated), but another signal that the binding constraint is
  now forward rows, not literature.

## 2026-07-30 (iteration 38, P1 maintenance)

- `arxiv.org/abs/2602.11708` — "Systematic Trend-Following with Adaptive
  Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency
  Markets", claim: 36-month OOS on 150+ crypto pairs yields SR 2.41,
  max DD 12.7%, Calmar 3.18 via an adaptive weighting scheme.
  Testable-here: **no** — 150+ pairs is a universe expansion plus an
  adaptive allocator, i.e. simultaneously a new symbol set and a new
  parameter family. P3 refuses it, and PBO 0.7411 across four existing
  architectures says the winner of such a search would not be trustworthy
  regardless. Filed for provenance so this SR-2.41 headline is not
  chased again next iteration.
- `en.wikipedia.org/wiki/Deflated_Sharpe_ratio` + `quanterlab.com/articles/foundations-dsr`
  — DSR restatement, "DSR > 0.95 = real edge after search". No content
  beyond Bailey/Lopez de Prado 2014 already codified in the gate
  contract; specifically nothing on the fragility question raised in
  iteration 26 ("DSR pass is a property of a stopped search, not of a
  trial"). Testable-here: **already implemented**.
- Third pass on "forward validation of crypto trend rules under realistic
  costs 2026". Returned aggregator/practitioner posts (Coin Bureau,
  Vantixs, Medium/Coinmonks) and the older arXiv 2009.12155 already
  known. No new peer-reviewed finding that would displace the standing
  answer's MinTRL = 706 days on trial 88. Fourth consecutive iteration
  in which external literature returns nothing directly actionable under
  the P1-only queue — recording, not stopping.

## 2026-07-29 — new route opened: on-chain data

- **Coin Metrics community API** (`community-api.coinmetrics.io/v4/`) —
  **verified keyless by direct query**, no account, no bot wall. Daily
  BTC and ETH metrics covering the full backtest window: network activity
  (`AdrActCnt`, `AdrBalCnt`, `BlkCnt`, `TxCnt`, `TxTfrCnt`), exchange
  flows (`FlowInExNtv`, `FlowOutExNtv`, `SplyExNtv`), miner/issuance
  (`FeeTotNtv`, `IssTotNtv`, `HashRate`), valuation (`CapMVRVCur`). BTC
  from 2009-2011, ETH from 2015. Testable-here: **yes — this is the first
  genuinely non-price information source available to the programme.**
- **Constraint discovered before any design, not after:**
  `AssetEODCompletionTime` shows each day's metrics finalize **~3.1 h
  after the UTC day closes** (BTC 3.18 h, ETH 3.02 h). The engine decides
  and fills at 00:00 UTC, so using day D's on-chain data for a day-D
  decision would be **look-ahead**. Every on-chain input must be lagged
  one full day, or execution moved past 04:00 UTC.
- **The programme's dual-source gate does not transfer.** Against
  `api.blockchain.info/charts/n-unique-addresses` (free, keyless, BTC
  only) over 1337 overlapping days: level ratio median **1.391** (range
  1.141-2.548) but daily-change correlation **+0.8729**. On-chain metrics
  are provider-specific constructions, so validation must move to change
  correlation plus recorded definitions. ETH would be single-source, and
  exchange flows cannot be cross-validated at all — every provider uses
  its own private exchange-address labelling.
- Full inventory: `ONCHAIN_SOURCE_INVENTORY_2026-07-29.md`. No strategy,
  no pre-registration, no trial, no ingestion script yet.

## 2026-07-31 (iteration 39, P1 maintenance)

- `deepbluealpha.io/research/bitcoin-bottom-signals-2026-on-chain`,
  `zipmex.com/blog/how-to-use-on-chain-analytics-for-crypto-trading/`,
  `theledgermind.com/on-chain-metrics-bitcoin/`,
  `axeladlerjr.com/charts/bitcoin-exchange-netflow/` — practitioner
  exchange-netflow narratives: negative netflow = accumulation,
  positive = distribution; divergence-based interpretation. Cited
  headline stat: ~48,500 BTC net outflow in the 30 days ending early
  April 2026, single-day 32,000 BTC withdrawal 2026-03-07.
  Testable-here: **partially.** The metric class (`FlowInExNtv`,
  `FlowOutExNtv`, `SplyExNtv`) is in the on-chain inventory as
  genuinely non-price and single-source-only (cannot cross-validate,
  every provider uses private exchange labelling). Any hypothesis
  lock the operator issues on netflow must specify (a) which side,
  (b) which threshold, (c) how to trade the signal (long-only spot,
  no shorting), (d) the D-1 lag rule. No peer-reviewed backtest with
  realistic two-sided costs found; practitioner sources are all
  narrative.
- `mdpi.com/2227-9091/14/3/51` — "Enhancing Bitcoin Trading Signal
  Prediction in Crisis Periods Using an Improved Machine Learning
  Approach" (Risks 2026, vol. 14 iss. 3). Uses ML on crisis-period
  features to predict entry/exit. Testable-here: **no** — an ML
  approach is a parameter family expansion (P3 refuses), the paper's
  own scope-of-validity is crisis periods (a regime-selected sample,
  not out-of-sample), and no realistic two-sided cost audit is
  reported. Adds nothing directly usable.
- `arxiv.org/pdf/2606.00071` — "Bitcoin Price Prediction: Peer-
  Reviewed Evidence and Social Media Discourse" (June 2026 arXiv).
  Cited multi-regime finding: no model survives across multiple
  regimes; independent replications with different model families
  are needed. Testable-here: **no**, but useful as external
  corroboration of the standing answer's PBO/multi-family findings.
- `coinbureau.com/guides/how-to-backtest-your-crypto-trading-strategy`,
  `theledgermind.com/bitcoin-mvrv-ratio-analysis/`,
  `tradingview.com/script/czUjU1Zi-Crypto-MVRV-ZScore-Strategy-PresentTrading/`
  — MVRV Z-score backtest guides. One useful negative line from the
  Coin Bureau piece: "MVRV has only been tested across three bear
  markets, and neither MVRV nor other popular indicators has survived
  a rigorous backtest across all historical cycles as a reliable
  standalone signal." Testable-here: **partial** — MVRV
  (`CapMVRVCur`) is in the on-chain inventory but flagged as
  partly-price-derived (price sits in the numerator of market cap
  over realized cap), so any use of it must be labelled accordingly.
  No independent peer-reviewed OOS backtest found.
- **Meta-observation.** Fifth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint.
  Consistent with iterations 35/37/38's same observation. The binding
  constraint remains forward rows plus operator hypothesis authority,
  not literature.

## 2026-08-03 — iteration 40 (P1 maintenance pass)

- `arxiv.org/pdf/2209.05559` — "Deep Reinforcement Learning for
  Cryptocurrency Trading: Practical Approach to Address Backtest
  Overfitting" (10-coin test, 2022-05-01..2022-06-27 cohort spanning
  two crashes). Reported finding: less-overfit DRL agents (measured
  by their PBO-like discipline) delivered HIGHER out-of-sample return
  than more-overfit peers. Testable-here: **no** — a DRL policy is a
  parameter-family expansion and P3 refuses. Value is corroborative:
  an independent methodology confirms the standing answer's PBO
  framework as OOS-predictive rather than a formality.
- `arxiv.org/pdf/2411.06327` — "Return and Volatility Forecasting
  Using On-Chain Flows in Cryptocurrency Markets". Reported finding:
  USDT flowing INTO exchanges positively predicts BTC and ETH returns
  at multiple horizons, and negatively predicts ETH volatility at
  multiple horizons and BTC volatility at 6h. Practitioner
  corroboration: ~48,500 BTC net outflow across major exchanges in
  the 30 days ending early April 2026 (single-day 32,000 BTC
  withdrawal on 2026-03-07). Testable-here: **partially, and only
  after operator hypothesis lock.** The metric class (`FlowInExNtv`,
  `FlowOutExNtv`) is already in the on-chain inventory as genuinely
  non-price and single-source-only; the literature adds a directional
  prior (INflow positively predicts return — counterintuitive vs the
  retail "coins leave exchanges = bullish" narrative) but does not
  fix N-budget, threshold, or cost-audit path. P3-blocked pending
  operator scope.
- `portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-*` and
  `stratbase.ai/en/blog/walk-forward-analysis-guide` — MinTRL and
  walk-forward canonical references. Two lines relevant to the
  standing answer: (i) MinTRL is defined against a specific null
  Sharpe and confidence — the 706-day figure for trial 88 at SR* = 0,
  95% one-sided is the textbook computation, not a bespoke bar;
  (ii) Quantpedia-cited OOS gap across published strategies is ~33%
  mean / ~44% median Sharpe degradation, corroborating the standing
  answer's caveat that the 5.4% margin over the naive benchmark is
  not enough. Neither line changes the standing answer; both belong
  on file so a future audit sees the numbers are aligned with
  external norms.
- **Meta-observation.** Sixth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint.
  Consistent with iterations 35/37/38/39. Item (ii) is the first
  literature-side entry with a genuine testable prior for the
  on-chain route (directional exchange-flow) — recording it here so
  that when the operator issues a hypothesis lock, the pre-reg has an
  external reference rather than being invented from scratch.

## 2026-08-03 — iteration 41 (P1 maintenance, TW ingest root cause)

- arXiv **2602.11708**, "Systematic Trend-Following with Adaptive
  Portfolio Construction: Enhancing Risk-Adjusted Alpha in
  Cryptocurrency Markets" (AdaptiveTrend). Claim: rule-based
  trend-following on crypto **perpetual futures**, 150+ pairs,
  36-month out-of-sample window 2022-2024, annualized Sharpe 2.41,
  max drawdown -12.7%, Calmar 3.18, beating TSMOM and equal-weight
  buy-and-hold; robustness section covers parameter sensitivity,
  transaction costs and regime decomposition. Testable-here:
  **no.** Product law binds this project to spot, long-only, daily,
  two-sided costs; perpetual futures bring leverage, shorting and
  funding-rate carry, none of which this engine models or is
  permitted to trade. Recorded because a 2.41 headline on a market
  this project cannot access is exactly the kind of number that
  invites goalpost drift — it is not comparable to trial 88's 1.1823
  and must never be cited as evidence about this program.
- arXiv **2510.23150** / SSRN 5665752, Etienne, Ohana, Benhamou et al.,
  "Revisiting the Structure of Trend Premia: When Diversification
  Hides Redundancy". Claim: equal-weighting trend horizons assumes
  every asset benefits equally from every horizon, which is
  empirically suboptimal; the medium-term (~125-day) horizon "adds
  little distinct information" and overlaps its neighbours; a
  **barbell** of short- plus long-term horizons captures most of the
  performance, and dropping the mid horizon modestly **lifts** Sharpe
  and improves drawdown. Testable-here: **mechanically yes, and
  refused.** This project's ensemble is a four-window equal-weight
  Donchian at windows 10/20/55/110 — close to the structure the paper
  says carries redundancy, and "drop 55" is a one-line arm. It is
  refused on two independent grounds: (a) queue **P3** bars new
  single-market parameter families, and this is a wrapper re-sweep of
  the kind `N_ARITHMETIC_2026-07-23.md` already ruled out; (b)
  `GATE4_FRAGILITY_2026-07-28.md` measured that a 134th trial
  preserves trial 118's DSR pass only if its Sharpe lands inside
  **[0.709, 1.180]**, so an arm that *worked* as the paper predicts
  would land above that band and **destroy the only gate-4 pass the
  program has**. Filed as a named, deliberately-unrun hypothesis so a
  future audit sees the refusal was priced, not overlooked.
- arXiv **2603.20319** / SSRN 6443898, Yin, Miki, Lesnichenko, Gural,
  "Implementation Risk in Portfolio Backtesting: A Previously
  Unquantified Source of Error" (2026-03-19). Claim: the same logical
  strategy run through five independent open-source engines diverges
  purely from implementation; 15 strategies x 30 stratified buckets
  (180 S&P 500 names) x 4 cost regimes. Key result: **at zero cost
  all five engines agreed exactly (max divergence 0.000%)**, isolating
  **transaction-cost implementation** as the sole source of
  disagreement; the authors propose engine sensitivity, an
  implementation-uncertainty interval, a divergence amplification
  factor and a conclusion stability index, and conclude multi-engine
  comparison is the most effective diagnostic. Testable-here:
  **no under P1**, but it names an uncertainty this program has never
  measured. Every headline number here (14.26x, Sharpe 1.1823/1.2413,
  the 4.70x twin edge) comes from **one** engine, and this is a
  cost-intensive daily strategy with two-sided costs — the exact
  regime where the paper finds divergence is material. Honest status:
  a **known-unquantified** error source, added to the caveat list.
  It cannot manufacture an edge, only widen the interval around one,
  so it does not change the standing answer's direction.
- `en.wikipedia.org/wiki/Deflated_Sharpe_ratio`, Bailey & López de
  Prado (SSRN 2460551), and secondary explainers. Claim: DSR adjusts
  the rejection threshold by trial count, skew and kurtosis; "the
  more configurations you tried, the higher the bar the winner has to
  clear", and the expected maximum Sharpe across many zero-edge
  trials is well above zero. Testable-here: **already applied.**
  Recorded as external corroboration that iteration 26's finding is
  **DSR working as designed, not a defect of this implementation** —
  a pass that survives only while the search is stopped is the
  textbook property of the statistic. Removes any temptation to treat
  the one-trial margin (0.950140 at N=133, 0.949969 at N=134) as an
  artefact to be engineered around.
- **Meta-observation.** Seventh consecutive external-research pass
  with no *actionable* finding under P1-only — but the first in that
  run to change the **caveat list** rather than only corroborate it:
  2603.20319 adds single-engine implementation risk as a named
  unquantified error source, and 2510.23150 supplies a concrete,
  priced-and-refused hypothesis (drop the mid horizon) rather than
  the usual "no directly testable rule". Both are facts about
  measurement quality; neither is evidence of an edge.

## 2026-08-15 — iteration 42 (P1 maintenance after an 11-night loop outage)

- arXiv **2607.19453**, Ayoub Jadouli, "Predictive Extrema,
  Unprofitable Policies: An AI-Assisted Audit of Candle-Based Binance
  Spot Timing Models" (submitted 2026-07-21). Claim: machine-learning
  models that predict price extrema on **Binance Spot**, daily and
  4-hour candles, **long-only**, produce **no** profitable policy once
  costs are charged — "every operational decision remains NO_TRADE" at
  **31 bps per completed cycle** (21 bps stress threshold). Recorded
  numbers: a ten-pair daily selector lost **6.72% over 19 cycles**
  (3 wins, 16 losses); a local-minimum policy returned **-1.79%**
  against an **11.11 bps** gross advantage; a local-maximum policy
  underperformed holding by **2.80%** despite a **12.21 bps**
  theoretical edge; a Gurgul-inspired model lost **44.30%** over seven
  cycles against **-41.20%** for buy-and-hold. Classification quality
  was good and useless at once — ROC AUC **0.874-0.896** with average
  precision only **0.116-0.134**. Testable-here: **not as a strategy**
  (different signal family, and P3 bars new single-market families),
  but it is the **closest external match to this project's own product
  law** yet found — same exchange, same spot venue, same long-only
  daily bar, same two-sided cost discipline — and it is a registered
  negative. Its value here is as a base rate: an independent,
  cost-honest audit of daily Binance spot timing found nothing, which
  is the prior against which this program's single gate-4 pass should
  be read. Numbers verified at arxiv.org/abs/2607.19453.
- **"Order flow and cryptocurrency returns"**, Journal of Empirical
  Finance, ScienceDirect **S1386418126000029** (online 2026-01);
  working-paper version presented at EFMA 2025. Claim: exchange
  **order flow** has economically valuable **out-of-sample**
  predictive power for crypto returns, with non-linear ML conditioned
  on order flow beating both fundamentals-conditioned ML and leading
  ML benchmarks without it; a one-standard-deviation rise in lagged
  world order flow is associated with **+0.2% daily** and **+0.9%
  weekly** returns, and the authors state the result survives
  short-selling constraints and high transaction costs — the two
  restrictions that usually kill a crypto result under this project's
  product law. Testable-here: **not yet, and not without an operator
  hypothesis lock.** It is adjacent to, but not the same as, the open
  on-chain route: this is *exchange* order flow (trades and book), not
  *on-chain* exchange netflow, and conflating the two would repeat the
  pooling error of 2026-07-26 and 2026-07-28. The data is not
  ingested here. Filed as the strongest external support so far for
  the flow family being worth an eventual hypothesis lock, **and** as
  a reminder that the lock must name which flow. **Source-access
  caveat, recorded deliberately:** the publisher page returned HTTP
  403 and the EFMA working-paper PDF failed TLS verification, so the
  numbers above come from the publisher-side abstract summary and are
  **not** verified against the paper itself. They must not be quoted
  in a result document until someone reads the PDF.
- **E-values / anytime-valid sequential inference** (Ramdas and Wang,
  *Hypothesis Testing with E-values*; Johari et al., arXiv 1512.04922
  "Always Valid Inference"; group-sequential comparisons from
  practitioner sources). Claim: e-values and always-valid p-values
  control Type I error **at any data-dependent stopping time**, so a
  monitor may look at an accumulating record continuously without
  inflating alpha. Testable-here: **relevant, and refused as a way to
  read the forward tracks early.** This is the obvious next idea once
  a 706-day MinTRL is on the books (iteration 25), so it is priced
  here before anyone proposes it: anytime-validity buys *permission to
  look*, not *evidence*. It does not reduce the data needed to
  separate SR = 1.1823 from SR = 0; against a fixed-sample test at the
  same date it is strictly **less** powerful, because the flexibility
  is paid for in power. Adopting it would move the honest verdict date
  **later than 2028-06-29, not earlier**. What it could legitimately
  buy is the right to monitor the three shadow tracks continuously
  without the alpha-spending problem that
  `FORWARD_TRACK_READ_PREREGISTRATION.md` currently solves by freezing
  the read to four rows — a governance simplification, not a
  scientific shortcut, and one that would itself have to be
  pre-registered before any row is read under it.
- **Meta-observation.** Eighth consecutive external-research pass with
  no actionable finding under P1-only. This one is the first to supply
  an external **base rate** (2607.19453: an independent cost-honest
  audit of daily long-only Binance spot timing found nothing
  tradeable) rather than only method caveats, and the first to
  pre-refuse a shortcut around the 2028 verdict date. Neither is
  evidence of an edge; both narrow what a future iteration may claim.

## 2026-08-16 — iteration 43 (P1 maintenance, shadow-task scheduling defect)

- **"Do trend following strategies work in Chinese futures markets?"**
  (Li, Zhang and Zhou, *Journal of Futures Markets* 37(12), 2017,
  pp. 1226-1254; abstract read at RePEc, ideas.repec.org). Claim:
  trend-following technical trading rules "yield better performance
  than the buy and hold strategy on both individual contracts and
  sorted portfolios", and the outperformance is "robust to transaction
  costs, data frequency, sub-prime crisis, shorting constraint,
  delayed execution, liquidity and parameters". The authors themselves
  add that "the profitability of the trend following strategy may be
  subject to data snooping bias". Testable-here: **no, and it is the
  wrong market anyway** — Chinese commodity *futures*, which the
  product law excludes (spot only, long-only, no leverage). Filed for
  one reason: it is the closest external analogue to this project's
  own P2 gate, which requires a candidate sleeve to beat buy-and-hold
  **in its own market**. A 2017 futures result cannot license a spot
  sleeve, and the paper's own data-snooping caveat is the same defect
  PBO 0.7411 measures here.
- **Bitcoin volatility-regime claim — checked and NOT verified.** A
  search summary attributed to State Street Global Advisors the figures
  "daily standard deviation roughly halving from approximately 5.3% in
  2021 to about 2.1% in 2024-2025". The SSGA source
  (ssga.com, *Bitcoin volatility and liquidity: key trends for
  investors*, published 2026-02-03) was fetched and **contains no such
  numbers**: it reports two-year rolling windows of weekly returns and
  states only, qualitatively, that "BTC volatility has evolved since
  its inception and has been trending downward over time". The S&P
  Global piece that may carry the figures returned HTTP 403.
  **Therefore the 5.3%/2.1% pair must not be quoted anywhere in this
  project.** Recorded because the underlying question is real and
  directly relevant: this program's entire measured edge comes from
  2018-2025, and a Donchian breakout rule's value depends on the
  volatility and trend-persistence regime it is run in. Testable-here:
  **yes in principle** (the repo holds the daily candles), but not run
  — under the Step 0 hard limits a realized-volatility-by-era chart
  would be a diagnostic that does not change the standing answer or
  close a route. It is filed as a candidate for the first iteration
  that has a decision attached to it, e.g. an operator question about
  whether the 2018-2025 measurement should be re-weighted.
- **AdaptiveTrend (arXiv 2602.11708) re-encountered, not re-filed.**
  It surfaced again as the top result for crypto time-series momentum
  net of costs. Already recorded under iteration 41; the H6
  (six-hourly) rebalance at the core of its Sharpe 2.41 is outside the
  product law's daily frequency, so nothing changes. Noted only so a
  future reader does not count it twice.
- **Practitioner claim that daily rebalancing is cost-dominated.**
  Several 2026 practitioner sources assert weekly or threshold-based
  rebalancing beats daily for long-only crypto books because daily
  turnover costs exceed the benefit. Testable-here: **already
  answered internally and in the opposite direction for this rule** —
  the Donchian ensemble is not a daily *rebalance*, it is a daily
  *decision* that changes exposure only on channel events, and the
  measured execution-latency and cost work (about -6.4 bps round trip,
  bounded above by ~17 bps) is inside tested headroom. Filed as a
  reminder that "daily" in practitioner writing usually means daily
  turnover, which this book does not do. No action.
- **Meta-observation.** Ninth consecutive external-research pass with
  no actionable finding under P1-only. The one genuinely new thing this
  pass produced is negative and about method: a widely-repeated
  Bitcoin volatility statistic failed source verification, and is now
  banned from this project's documents rather than absorbed into them.

## 2026-08-19 — iteration 44 (P1 maintenance, two missed slots explained)

- **Gueta Quant, "Gueta Research #001", pre-registered funnel of 13
  simple strategies on EURUSD daily, 2020-01..2025-12 (in-sample
  2020-2023, out-of-sample 2024-2025).** Headline: **13 -> 0**. Eight
  passed gate 1 (OOS return > 0 and Sharpe > 0 at 2 pips), seven passed
  gate 2 (walk-forward cumulative return > 0), and **zero** passed gate
  3 (Deflated Sharpe Ratio >= 0.95) or gate 4 (PBO). Their PBO came out
  at 0.5639 via CSCV with 16 blocks and 12,870 combinations, family
  N=14. Their **Breakout Channel** arm returned +1.52% OOS and +16.05%
  walk-forward and still scored **DSR 0.062**. Testable-here: **no** —
  EURUSD spot FX is outside this project's product law. Filed anyway
  because it is the closest external analogue yet found to this
  program's own apparatus: an independent group, pre-registering, using
  the **same two deciding gates at the same DSR >= 0.95 threshold**, on
  a different market, rejected every candidate. That is independent
  corroboration of iteration 27's finding that gates 3 and 4 reject
  nearly everything, and it makes this project's single pass — trial
  118 at DSR 0.950140, a margin of exactly one trial (iteration 26) —
  look more like a property of a stopped search than less. It does not
  change the standing answer; it hardens one clause of it.
- **Momentum-decay literature, second look, still not actionable.**
  Several 2025-2026 sources (a comparative time-series vs
  cross-sectional momentum study in crypto; Grayscale's 2026 digital
  asset outlook; Springer's *Cryptocurrency momentum has (not) its
  moments*) converge on a qualitative claim: time-series and
  cross-sectional crypto momentum have **compressed toward similar,
  modest positive returns** as the market institutionalized post-2021,
  with BTC/ETH trading more as macro-sensitive instruments than as
  reflexive crypto assets. Testable-here: **yes in principle** — it is
  the same regime question raised in iteration 43 by the failed State
  Street volatility claim, and it bears directly on whether a
  2018-2025 measurement transfers. Still **not run**, for the same
  Step 0 reason: an era-split of the backtest is a diagnostic with no
  decision attached to it, and P3 forbids the family re-run that would
  give it teeth. Recorded now as the **second independent arrival** at
  the same question; a third should be treated as a signal that the
  operator ought to be asked whether to attach a decision to it.
- **Minimum-track-record-length sources re-checked; iteration 25's
  arithmetic stands.** Bailey and Lopez de Prado's DSR/PSR framework —
  and the Portfolio Optimizer write-ups of MinTRL — restate that the
  required track length "can substantially exceed typical evaluation
  windows", which is exactly the 706-day (2028-06-29) figure this
  project computed for trial 88. Also encountered: a practitioner rule
  that a forward test "is statistically valid when it reaches at least
  100 trades with no rule changes". **Not adopted.** A trade count is
  not a substitute for MinTRL — it ignores Sharpe, skew and kurtosis,
  all three of which drive this book's 706 days (SR 1.1823, skew
  +0.227, kurtosis 12.775) — and adopting a laxer forward-read rule
  after freezing a stricter one is precisely the goalpost move
  `FORWARD_TRACK_READ_PREREGISTRATION.md` exists to prevent. Logged so
  that a future iteration meeting the 100-trade rule cannot mistake it
  for permission to read return early.
- **arXiv 2512.22476 (AutoQuant) surfaced, not filed.** Auto-tuning
  under execution constraints for crypto **perpetual futures** — out of
  product law (spot, long-only), same disposal as AdaptiveTrend.
- **Meta-observation.** Tenth consecutive external-research pass with
  no directly-actionable finding under the P1-only constraint. Unlike
  the previous nine, this one produced a result that touches an
  existing conclusion: the Gueta funnel is the first outside evidence
  about how the DSR-plus-PBO pair behaves when someone else runs it
  honestly, and it points the same way this program's own gate-4
  fragility measurement does.

## 2026-08-21 — iteration 45 (P1 maintenance, backtest-to-live transfer measured by outsiders)

- **Liu (2026), "Evaluating Structured Strategy Backtests: Peer
  Benchmarks, Regime Timing, and Live Performance", arXiv 2604.18821,
  20 Apr 2026 — the largest measurement yet of the exact transfer this
  program cannot make.** 1,726 commercially distributed structured
  strategies from ten global institutions, 2009-2025, each with a
  marketed pro-forma record and a subsequent live record. Verified by
  extracting the PDF text, not from the search summary. Numbers: mean
  volatility-adjusted return over the twelve months **before** launch
  is 4.1% p.a. against **1.0%** live, a decay of −3.1pp (p<0.01); at
  six months 3.6% against 1.5%, −2.1pp (p<0.01). The regression of
  live on pro-forma performance gives **β̂ = 0.137 (R² = 0.148,
  N = 1694)** in raw returns, but **0.025 (R² = 0.032)** once the
  dependent variable is Jensen α against an external Bloomberg index
  and **0.034 (R² = 0.054)** against a leave-one-out peer average —
  reductions of about **81% and 75%**. Median live underperformance is
  0.8pp p.a. against LOO peers and 3.0pp against the external index at
  twelve months, with **59% of strategies negative** on both. The
  authors' reading: marketed backtests "predominantly reflect the
  common factor regime present before launch rather than strategy-
  specific skill", and the discount should grow when launch follows an
  extreme factor run. **Testable-here: no** — it is not a strategy
  hypothesis and nothing here can be traded. It is evidence, and it
  bears on two clauses this program already holds: that a backtest
  must be judged against a benchmark (which is why
  `VS_BUY_AND_HOLD_2026-07-26.md` exists), and that raw pro-forma
  numbers such as 14.26x carry far less information about live
  behaviour than their size suggests. **No goalpost moves from this**:
  the forward read rule stays exactly as frozen in
  `FORWARD_TRACK_READ_PREREGISTRATION.md`, and Liu's regime-timing
  finding is recorded as a prior, not as a reason to run an
  era-extremity diagnostic on the 2026-07-24 launch date.
- **Mroziewicz and Ślepaczuk (2026), arXiv 2602.10785, 11 Feb 2026 —
  an independent walk-forward crypto study whose own headline table
  loses to buy-and-hold.** University of Warsaw; **spot** BTC, ETH and
  BNB; EMA-crossover, long-short, intraday bars (1 to 60 minutes);
  0.1% per transaction with sensitivity from 0.05% to 0.50%; training
  2018-02-08..2019-09-01, unseen out-of-sample 2019-11-07..2021-08-22;
  81 training/testing window pairs optimized by walk-forward, with the
  top two carried to a single unseen evaluation. Unseen-period Sharpe,
  strategy against buy-and-hold: BTC **1.1064 vs 1.1281**, ETH
  **1.3371 vs 1.5365**, BNB **1.1982 vs 1.4644** — the benchmark wins
  all three, despite annualized returns of 90.91%, 137.27% and 140.30%
  that look spectacular in isolation. The paper's own sentence,
  verbatim: **"No strategy surpassed the respective asset's
  Buy-and-Hold performance in terms of Sharpe ratio."** **Testable-
  here: no** — long-short and intraday both fall outside product law
  (spot, long-only, daily), so no trial follows. Filed because it is
  an independent, published, walk-forward-validated instance of the
  failure mode this program measured for Taiwan and gold: an optimized
  trend rule that produces large absolute returns and still loses to
  simply holding the asset.
- **Wiecki, Campbell, Lent and Stauth (Quantopian), "All that glitters
  is not gold", SSRN 2745220 — what survives a backtest is drawdown
  character, not Sharpe.** 888 US-equities algorithms with at least six
  months of out-of-sample performance. Verified from the PDF: the
  abstract states Sharpe ratio and similar metrics "offer little value
  in predicting out of sample performance (**R² < 0.025**)", with the
  in-sample/out-of-sample Sharpe correlation at **Pearson R² = 0.02**,
  while **annual volatility reaches R² = 0.67 and maximum drawdown
  R² = 0.34**; a non-linear model on the full feature set gets to
  R² = 0.17 on hold-out data. **Testable-here: no** (equities, and the
  finding is about metrics, not a rule). Recorded because it puts a
  number on which half of this program's own result should be expected
  to travel: **drawdown character is among the most persistent
  properties of a backtest and Sharpe rank is nearly the least.** The
  precise claim is that an algorithm's own drawdown level persists
  in-sample to out-of-sample — **not** that a drawdown advantage over a
  benchmark persists, which is a different quantity and is not what
  Wiecki measured. Under that limit it supports the clause of the
  standing answer that treats the 33.05%-against-80.99% drawdown result
  as the more durable half, and it argues against leaning on the 5.4%
  return margin.
- **ETF- and on-chain-flow commentary surveyed, nothing adoptable.**
  The 2026 market-commentary corpus (Amberdata, VanEck and similar)
  offers claims of the form "five or more consecutive ETF inflow days
  marked durable bottoms in 2026". No sample definition, no
  out-of-sample split, no cost treatment, and no paper behind it. The
  on-chain route opened in iteration 39 remains open and unadvanced;
  it still awaits an operator hypothesis lock, and this class of claim
  is not one a hypothesis could honestly be locked from.
- **arXiv 2602.11708 (AdaptiveTrend) resurfaced and stays disposed.**
  Same paper already refused in an earlier pass: 6-hour bars,
  long-short, asymmetric 70/30 allocation. Re-encountering a disposed
  source is not new evidence, and it is logged only so a later
  iteration does not count it twice.
- **Meta-observation.** Eleventh consecutive external-research pass
  with nothing directly actionable under the P1-only constraint. Like
  iteration 44's, this one still touched existing conclusions rather
  than adding routes: three independent sources — 1,726 institutional
  strategies, 888 retail algorithms, and one walk-forward crypto study
  — all say the same thing from different directions, that the part of
  a backtest that survives contact with live markets is small and is
  not the part that looks best on the page. **None of these is the
  third arrival at the momentum-regime-decay question** flagged in
  iteration 44; that trigger concerns crypto momentum compressing
  post-2021 and remains at two arrivals. Conflating the two questions
  would be exactly the loose bookkeeping the trigger exists to prevent.

## 2026-08-22 — iteration 46 web pass (P1-only; horizon redundancy inside a trend ensemble)

- **arXiv 2607.19497 (Sepp and Lucic, 21 Jul 2026), "The Science and
  Practice of Trend-Following Systems" — a closed-form theory of what a
  trend system earns, and one sentence that touches this program.**
  Verified by fetching the abstract page. The paper classifies trend
  systems into European, American and time-series-momentum types and
  derives, for the European class, an exact relationship between P&L,
  autocorrelation and drift in volatility-normalized returns; in the
  frequency domain the expected return is a Poisson-kernel reading of
  the return spectrum, so that **"trend-following alpha is excess
  spectral mass at low frequencies"** and the system profits at zero
  drift when the kernel-weighted spectral mass exceeds one. It also
  derives a closed-form Sharpe ratio, a **net** Sharpe and a
  **cost-optimal span** under trading costs, and shows the positive
  skewness of aggregated trend returns is **structural**, positive at
  every horizon and peaking near half the filter span. Empirically it
  reports that **"all TF systems are strongly correlated"** on liquid
  contracts. **Testable-here: no, and deliberately not.** The
  cost-optimal-span formula is a design rule, and using it to pick or
  re-pick a lookback would be a new single-market parameter family,
  which P3 refuses. Two things it does do without any run: it gives a
  structural explanation for the **+0.227 skew** already measured on
  trial 88's return series (a property, not a result), and its
  strong-correlation finding is about systems on a shared contract set,
  which is a **different quantity** from this program's cross-market
  sleeve correlation of −0.0041 — the two must not be conflated.
- **arXiv 2510.23150v2 (Etienne, Ohana, Benhamou, Guez, Setrouk,
  Jacquot, 28 Oct 2025), "Revisiting the Structure of Trend Premia:
  When Diversification Hides Redundancy" — layering horizons can hide
  redundancy rather than add diversification.** Universe 20 liquid
  futures across commodities, equities, rates and FX; horizons 20, 60,
  125, 250, 500 trading days; sample 2013-2025 with the formal backtest
  2015-2025; Bayesian reallocation across horizons on rolling 8-year
  training windows. Numbers below were read twice from the paper's own
  tables. Standalone Sharpe (Table 6): **20d 0.20, 60d 0.21, 125d 0.21,
  250d 0.42, 500d 0.47, all-horizons baseline 0.36**. Pairwise
  correlations (Table 5): **20d-60d 83%, 20d-125d 59%, 20d-250d 59%,
  20d-500d 44%, 60d-125d 81%, 60d-250d 60%, 60d-500d 44%, 125d-250d
  84%, 125d-500d 67%, 250d-500d 90%**. The claim is that the medium
  band adds little once short and long are included, and that optimal
  weight goes barbell rather than ladder. **A number was retracted
  during verification:** the first read reported "excluding 125d lifts
  Sharpe from 0.36 to about 0.40"; the second, targeted read found no
  such figure in the document, so it is **not recorded** and must not
  be cited later. **Testable-here: mechanically yes, and refused.**
  This program's ensemble votes over windows **10/20/55/110**, so a
  leave-one-window-out ablation is the direct analogue — but it is an
  arm of the experiment-7 family, and P3 forbids new single-market
  parameter families. Iteration 26's arithmetic makes the refusal
  sharper rather than merely procedural: a 134th trial preserves trial
  118's gate-4 pass only if its Sharpe lands in **[0.709, 1.180]**, and
  an ablation arm that behaved like the existing ensemble (trial 88 at
  1.1823, trial 118 at 1.2413) would land at or above the top edge and
  destroy the pass. Recorded as evidence, not as a route.
- **Amberdata "2026 Outlook: The End of the Four-Year Cycle" (Michael
  Marshall, 20 Jan 2026) — search summary refused after source check.**
  A search result attributed to this piece a claim that Bitcoin's
  30-day realized volatility sits at 20-30% and that the ETF-flow
  regime is eroding trend-strategy efficacy. Fetching the page found
  **no realized-volatility figure, no dated measurement and no
  statement about momentum or trend-strategy performance** — the
  nearest text is the qualitative "Volatility compresses. Interest
  fades. Then something changes." The numbers are therefore not
  recorded, and this is **not** an arrival at the momentum-regime-decay
  question, which stays at **two**. Logged as a worked example of the
  iteration-43 lesson: a search summary is not a source.
- **arXiv 2602.11708 (AdaptiveTrend) re-encountered a third time and
  stays disposed.** 150+ pairs, 6-hour bars, long-short with asymmetric
  70/30 allocation, 2022-2024, reported Sharpe 2.41 and max drawdown
  −12.7%. Outside product law on two counts. Logged only so repeated
  encounters are never counted as accumulating evidence.
- **Meta-observation — twelfth consecutive pass with nothing actionable
  under P1-only, and a new question opened at two arrivals.** Both new
  sources point at the same unexamined place, from opposite directions:
  Sepp and Lucic say trend systems are strongly correlated with one
  another, and Etienne et al. say adjacent horizons inside one ensemble
  can be near-duplicates carrying real cost. Applied here the question
  is whether **10/20/55/110 is four bets or effectively two**. It is
  tracked at **two arrivals**, on the same bookkeeping rule as the
  momentum-regime-decay question — a third independent arrival triggers
  asking the operator whether to attach a decision to it, and until
  then nothing runs. The two questions are distinct and must not be
  pooled to reach a threshold faster.

## 2026-08-23 — iteration 47 web pass (P1-only; the redundancy question reaches its third arrival)

- **arXiv 2504.10914v15 (Sebastien Valeyre, v15 submitted 12 Aug 2026),
  "Breaking the Trend: How to Avoid Cherry-Picked Signals" — the THIRD
  independent arrival at the ensemble-breadth question opened in
  iteration 46.** Verified in two passes: the abstract page first, then
  a targeted second read of the v15 full text for each body number.
  From the abstract, verbatim: *"using only one simple EMA, appears
  optimal to capture the trend. As a consequence, using a complex basket
  of different complex indicators as signal, does not seem to be so
  rational or optimal and exposes to the risk of cherry-picking."* From
  the body, each quoted back on the second read: *"ARP(80) is correlated
  to ARP(150) with a coefficient of 0.96"*; *"the parameter of 112±10
  business days (equivalent to a half-life period of 78 business days)
  for simple EMA is the optimal parameter to get the optimal Sharpe
  ratio"*; universe *"70 futures instruments in stock indices, bonds, FX
  and commodities futures"* over *"25th of May 1990 ... 7th of December
  2023"*. Reported Sharpe ratios for the single-EMA arms: ARP(100) 1.25,
  ARP(120) 1.24, ARP(150) 1.21, MACD(20,120,0.4x400) 1.18. **A first-read
  slip is corrected here rather than carried:** the initial read gave the
  sample start as 29 May 1990; the paper's own sentence says 25 May 1990,
  and that is what is recorded. **No multiple-testing correction is
  applied in the paper** — it uses a bootstrap interval [1/223, 1/157]
  and an R^2 = 0.98 fit to the Grebenkov-Serror Sharpe formula, not a
  deflated Sharpe or an FDR control. **Testable-here: mechanically yes,
  and still refused** — see the disposition line below.
- **Why this is a genuine third arrival, and what it is NOT.** It is
  independent of the two iteration-46 arrivals in author, method and
  sample: Sepp and Lucic (arXiv 2607.19497) argue spectrally that trend
  systems are strongly correlated with one another; Etienne et al.
  (arXiv 2510.23150v2) measure 125d-250d at 84% and 250d-500d at 90%
  on 20 futures 2013-2025; Valeyre measures 0.96 between ARP(80) and
  ARP(150) on 70 futures 1990-2023 and concludes a single scale suffices.
  Three groups, three methods, three samples, one conclusion. **But all
  three are liquid-futures studies and none is crypto.** They are three
  independent arrivals in the bookkeeping sense and **not** three
  independent tests of this program's ensemble. This program already
  holds direct measured evidence that a rule selected on crypto did not
  transfer to Taiwan or gold; the reverse transfer — a futures-derived
  redundancy finding into BTC/ETH spot — is equally unestablished, and
  no document may treat these three papers as if they had measured
  10/20/55/110 on crypto. The near-match between Valeyre's 112±10 and
  this program's longest window of 110 is a **coincidence of different
  indicators on different universes** (EMA on futures vs Donchian on
  BTC/ETH) and must never be cited as corroboration.
- **Disposition: the arrival threshold is reached, so the operator is
  asked and nothing is run.** The arrival-counting rule says a third
  independent arrival triggers asking the operator whether to attach a
  decision, and until then nothing runs. The question is put to the
  operator in today's LOOP_LOG entry, unchanged in substance: are
  10/20/55/110 four bets or effectively two? The two standing refusals
  are unaltered while the operator considers it — procedurally a
  leave-one-window-out ablation is an arm of the experiment-7 family and
  P3 forbids new single-market parameter families; arithmetically
  iteration 26 measured that a 134th trial preserves trial 118's gate-4
  pass only if its Sharpe lands in [0.709, 1.180], and an ablation arm
  behaving like the current ensemble (trial 88 at 1.1823, trial 118 at
  1.2413) would sit at or above that ceiling and destroy the pass. The
  operator's answer must therefore price a measurement against a
  recorded gate-4 cost, which is exactly why the loop does not decide it.
- **arXiv 2604.26747 (Yikuan Huang, Zheqi Fan, Kaiqi Hu, Yifan Ye,
  29 Apr 2026), "From Hypotheses to Factors: Constrained LLM Agents in
  Cryptocurrency Markets" — an outside program with this one's audit
  discipline and none of its statistical discipline.** Abstract verified
  on the listing page, details on the v1 full text. Design: an agent
  reads an *append-only experiment trace*, proposes falsifiable factor
  hypotheses, and a deterministic engine enforces fixed splits, selection
  gates and transaction costs, with successful and failed hypotheses
  both auditable — structurally the same idea as this program's trial
  registry. Reported: a ridge-combined **equal-weight long-short**
  portfolio trained on 2020-2022, validated on 2023, tested 2024 onward,
  daily CoinMarketCap data with a one-day execution lag and one-day
  holding period, **44.55% annualized return and Sharpe 1.55** out of
  sample after **5 bps one-way** costs, max drawdown **-0.236**; 25
  single factors generated across five search rounds. **Testable-here:
  no** — long-short violates product law's long-only constraint, and the
  factor DSL is a different mechanism from a channel-breakout timing
  rule. **Recorded for one reason only:** the paper reports **no
  multiple-testing correction of any kind** — no deflated Sharpe, no PBO,
  no family-wise control — after an explicitly *searched* factor set.
  This program's DSR/PBO bookkeeping is therefore not excess caution
  relative to the published literature; it is a discipline the published
  literature here does not apply. That observation changes nothing about
  whether this program has an edge.
- **Buhalterines apskaitos teorija ir praktika Vol. 33 (Adedeji Daniel
  Gbadebo, published 9 Jun 2026), "Momentum Trading in Cryptocurrencies:
  A Comparative Study of Time-Series and Cross-Sectional Strategies" —
  a headline crypto-momentum return published without its buy-and-hold
  twin.** Verified from the journal's own article page, not from a search
  summary. Universe eight coins (BTC, ETH, LTC, XRP, BNB, ADA, DOGE, SOL),
  period **1 January 2020 to 31 October 2025**, multi-horizon EMA signals
  with volatility normalization, two structures compared. Reported:
  time-series momentum **31.96% annual return**, said to outperform
  cross-sectional on a risk-adjusted basis; cross-sectional max drawdown
  **55.0%**. **Not stated anywhere in the abstract: long-only or
  long-short, transaction cost assumptions, Sharpe ratios, and — the
  point — any buy-and-hold comparison.** This is the exact defect
  `VS_BUY_AND_HOLD_2026-07-26.md` was written to correct in this
  program's own record: over a window containing 2020-2021 and 2023-2024,
  a crypto momentum return is uninterpretable without the passive twin
  it must beat. **Testable-here: no.** The absence recorded above is a
  verified absence, not an estimate; this log makes **no claim** about
  whether 31.96% would or would not beat holding those eight coins,
  because that number was not measured here and must not be guessed.
- **Momentum-regime-decay question: no arrival this pass, and a search
  direction closed.** A targeted search for post-ETF decay in Bitcoin
  trend performance returned only flow journalism — spot-ETF net buying
  falling from a cited $23.72bn peak, ten straight outflow days
  15-29 May 2026 totalling $2.9623bn, and price commentary. **None of
  it measures a trend or momentum strategy's performance**, so none of it
  is an arrival; ETF flow is a market-structure fact, not a strategy
  measurement, and conflating the two would manufacture a third arrival
  out of newspaper copy. The question stays at **two arrivals**. It also
  stays strictly separate from the redundancy question that reached
  three today; the two must never be pooled.
- **Meta-observation — thirteenth consecutive pass with nothing directly
  actionable under P1-only, and the first pass to move a tracked question
  to its trigger.** Nothing was run, no arm was tested, and the standing
  answer is unchanged. What changed is procedural and small: one open
  question crossed the threshold its own rule set in advance, so it goes
  to the operator instead of quietly accumulating more citations.

## 2026-08-24 — iteration 48 (P1 maintenance; the closest published relative of this program's own rule, and what it does not measure)

- **Zarattini, Pagani and Barbon, "Catching Crypto Trends: A Tactical
  Approach for Bitcoin and Altcoins" (SSRN 5209907, author page last
  revised 2025-04-09) — the closest published relative of this program's
  own rule, and it does not settle the question the operator is
  currently being asked.** Verified from the authors' own pages
  (`abarbon.com/papers/catching-crypto-trends` and Concretum Group's
  paper page), because SSRN returned **HTTP 403** for both the abstract
  page and the delivery PDF, so the full text was **not read here**.
  What those pages state: an "ensemble of Donchian channel-based trend
  models, each calibrated with a different lookback period", aggregated
  into a single signal, with volatility-based position sizing; applied
  to a rotational portfolio of the "top 20 most liquid coins"; on a
  "survivorship bias-free dataset covering all cryptocurrencies traded
  since 2015"; Sharpe **above 1.5** and annualized alpha of **10.8%**
  versus Bitcoin, described as net of fees. **Testable-here: no.** The
  mechanism matches this program's (Donchian ensemble, crypto), but
  rotational top-20 selection with volatility sizing is a different
  portfolio construction from equal-weight BTC/ETH, and P3 forbids new
  single-market parameter families in any case.
- **The reason that paper is filed is a failure to find, and it bears
  directly on the pending operator decision.** This is precisely where
  a crypto measurement of **between-window redundancy** would live —
  a Donchian ensemble, on crypto, by authors who built it deliberately
  out of several lookbacks — and neither authors' page states one.
  Also not stated on either page: the lookback periods themselves, the
  sample end date, long-only versus long-short, spot versus futures,
  the transaction-cost number, Bitcoin's own return/Sharpe/drawdown,
  and any out-of-sample split or multiple-testing correction. This is
  recorded as a **failure to locate**, **not** as a verified absence
  from the paper — the full text was not retrievable, so no claim is
  made about what its tables contain. Consequence: the ensemble-breadth
  question stays at **three arrivals, all liquid-futures**, exactly as
  it stood on 2026-08-23, and the literature search has produced **no
  substitute** for measuring 10/20/55/110 directly. If the operator
  wants that number, it appears it must be run rather than cited.
  One point of discipline worth noting in the paper's favour: its
  headline is stated **relative to Bitcoin** (alpha 10.8%), unlike the
  BATP paper filed on 2026-08-23 — though regression alpha against
  Bitcoin is **not** the same test as beating buy-and-hold on return or
  Sharpe, which is what `VS_BUY_AND_HOLD_2026-07-26.md` requires, and
  the two must not be treated as interchangeable.
- **arXiv 2602.11708 (Duc Bui, Thanh Nguyen, 12 Feb 2026), "Systematic
  Trend-Following with Adaptive Portfolio Construction: Enhancing
  Risk-Adjusted Alpha in Cryptocurrency Markets" — verified from the
  HTML full text, not from a search summary.** Data: "historical data
  from Binance Futures, covering 150+ perpetual swap contracts with
  6-hour OHLCV bars from January 2021 to December 2024"; long-short
  with an asymmetric 70/30 allocation. Costs: "a taker fee of 4 bps per
  trade", volume-scaled slippage, and funding "incorporated as a
  rolling 8-hour charge/rebate", with robustness at 0, 4, 8 and 12 bps.
  Out-of-sample 36 months (2022-2024): Sharpe **2.41**, max drawdown
  **-12.7%**, Calmar **3.18**. Its own Table 1 benchmarks, quoted:
  BTC buy-and-hold "Ann. Ret. 12.6%, Ann. Vol. 48.7%, Sharpe 0.17,
  MDD -64.1%"; equal-weight buy-and-hold "Ann. Ret. 8.3%, Ann. Vol.
  52.1%, Sharpe 0.07, MDD -72.4%". Parameters (theta_entry, alpha, L)
  are re-optimized **monthly by grid search on the preceding month**.
  **Multiple-testing correction: absent from the full text** — no
  deflated Sharpe, no PBO, no White reality check, no family-wise
  control, after an explicitly searched parameter set. **Testable-here:
  no** — perpetual futures and long-short both violate product law, and
  6-hour bars violate the daily constraint. Filed for two reasons: it
  **does** report its passive twins with numbers, which is the
  discipline the 2026-08-23 BATP entry found missing; and it is the
  second consecutive pass to find a searched parameter set published
  with no multiple-testing correction. That is a pattern in what this
  program reads and it changes nothing about whether this program has
  an edge.
- **QuantPedia, "In-Sample vs. Out-Of-Sample Analysis of Trading
  Strategies" (2 Jun 2023) — a fourth arrival on a question that
  already reached its threshold, so it is one line and no more.**
  "355 strategies for further analysis" retained from an initial 868;
  in-sample defined as running to the source paper's backtest end and
  out-of-sample from there to the end of QuantPedia's own backtest;
  Sharpe "deteriorated by 33% (on average)" with delta **-0.525**, and
  a median decline of **43.90%** with delta **-0.518**. What fraction
  of strategies stayed profitable out of sample: **not stated**.
  **Testable-here: no.** The backtest-to-live transfer question reached
  three arrivals on 2026-08-21 (Liu's 1,726 structured strategies,
  Mroziewicz and Slepaczuk's walk-forward crypto study, Quantopian's
  888 algorithms), so this is bookkeeping only: it opens nothing,
  strengthens nothing, and is **not** forward evidence about this
  program's own rule.
- **Search direction closed for the second consecutive pass: recent-
  regime crypto trend performance.** A targeted search for measurements
  of trend-following against buy-and-hold in the 2025-2026 regime
  returned market-outlook publications (Kraken, Coinbase Institutional,
  Trakx, Motley Fool) plus the AdaptiveTrend paper already filed above.
  **None measures a trend strategy's recent performance against its
  passive twin on a stated sample**, so none is an arrival. The
  momentum-regime-decay question stays at **two arrivals**, unchanged
  from 2026-08-23, and stays strictly separate from the redundancy
  question; the two are not pooled.
- **Meta-observation — fourteenth consecutive pass with nothing
  directly actionable under P1-only.** Nothing was run, no arm was
  tested, and the standing answer is unchanged. The one thing this pass
  adds is negative and useful: the most closely matched published work
  does not appear to hand the operator the redundancy number for free.

## 2026-08-25 — iteration 49 (P1 maintenance; the ablation the operator was asked to authorize, already published — and already unreliable)

- **Etienne, Ohana, Benhamou, Guez, Setrouk and Jacquot, "Revisiting the
  Structure of Trend Premia: When Diversification Hides Redundancy"
  (arXiv 2510.23150v2, submitted 27 Oct 2025, revised 28 Oct 2025;
  q-fin.PR / q-fin.PM / q-fin.RM / q-fin.TR / stat.ML; no journal
  reference).** Read from the arXiv HTML full text, not from the abstract
  page — every number below was extracted from the rendered tables and is
  quoted as the paper prints it. **This is the pending operator
  question's experiment, already run and published by someone else.** The
  paper performs an explicit **leave-one-horizon-out ablation** on a
  five-horizon trend ensemble.

  *Setup.* Universe **23 liquid futures** across four asset classes —
  commodities GC, CL, NG, CO, HG; equities ES, NQ, NK, SX, Z, EM; fixed
  income TU, TY, SZ, RX, G, JGB, XM; FX EUR, JPY, GBP, AUD, CAD.
  Horizons **H = {20, 60, 125, 250, 500} trading days**. Costs modelled in
  three layers: transaction 2 bps round-turn, roll cost 2–15 bps by asset
  class (2000–2025 average front-to-next spread), management fee 50 bps
  per annum. Benchmark is the **NEIXCTAT** CTA index; the object is CTA
  *replication*, not absolute return. Long–short futures. Tables span
  2005–2025 with four subperiods; Tables 5–6 cover 2015-08-31 to
  2025-08-29. **No cryptocurrency in the universe.**

  *Cross-horizon correlation (Table 5, 2015–2025), the number this program
  does not have for its own ensemble.* Adjacent pairs: 20d/60d **83%**,
  60d/125d **81%**, 125d/250d **84%**, 250d/500d **90%**. Most distant
  pair 20d/500d **35–44%** (the printed matrix is asymmetric at that cell:
  44% in the 20d row, 35% in the 500d row). Single-horizon Sharpe over the
  same decade (Table 6): 20d **0.20**, 125d **0.21**, 250d **0.42**, 500d
  **0.47**; annual returns 4.2% / 4.4% / 4.5% / 6.7% / 7.2% for
  20d/60d/125d/250d/500d, vol 10.0–10.9%.

  *The ablation itself (Tables 7–10).* Z-score ranking (Table 7): the best
  leave-one-out arm is **No 125 (+0.80)**, then No 60 (+0.37), then No
  250, No 20 (**−0.38**), No 500 (**−1.12**). Sharpe by period (Table 8),
  All Horizons versus No 125: 2005–2010 **0.91 vs 0.90**, 2010–2015
  **1.37 vs 1.41**, 2015–2020 **0.43 vs 0.42**, 2020–2025 **0.35 vs
  0.44**, full sample **0.74 vs 0.77**. Return/MaxDD (Table 9), same
  pairing: 1.12 vs 1.13, 1.39 vs 1.75, 0.48 vs 0.45, 0.32 vs 0.39, full
  sample **0.48 vs 0.52**. Correlation to NEIXCTAT (Table 10) full sample
  **0.83 vs 0.84**. Conditional (crisis) Sharpe across all leave-one-out
  arms ranges **0.61 to 0.65**; All Horizons 0.65, No 125 **0.63** — i.e.
  removing the medium band very slightly *reduces* crisis performance.
  Removing **500d** is the worst arm on every axis (Sharpe 0.74 to
  **0.67**, Return/MaxDD 0.48 to **0.44**, correlation 0.84 to **0.81**).

  *Two problems with the paper, both verified against its own text, and
  they are the reason this does not settle anything.* (1) **Its prose
  overstates its tables.** The abstract and the introduction say excluding
  the 125d layer "consistently improves Sharpe ratios"; Table 8 shows No
  125 **worse in two of the four subperiods** (2005–2010 0.90 vs 0.91,
  2015–2020 0.42 vs 0.43). The body text at that table claims the Sharpe
  "exceeds ... in three of the four subperiods" and then enumerates only
  **two** subperiods plus the full-sample average — the third named item
  is not a subperiod. (2) **No multiple-testing correction of any kind.**
  Searching the full text for `deflated`, `multiple test`, `bootstrap`,
  `reality check` and `PBO` returns **zero** occurrences. Overfitting is
  addressed only by a "persistence filtering" heuristic on the weight
  series (section 4.3). So the reported winner is the **maximum of five
  leave-one-out arms**, selected without any correction, and its
  full-sample Sharpe margin over the baseline is **+0.03** (0.74 to 0.77).
  That is the third consecutive pass in which a searched configuration is
  published with no multiple-testing control.

  **Testable-here: no**, on three counts — long–short, futures with roll
  costs, and no crypto. **Consequence for the pending operator decision,
  stated without pressure:** the ensemble-breadth question now has a
  **fourth arrival**, and this one differs in kind from the first three
  because it actually ran the ablation and printed the numbers. What it
  supplies is not the answer for 10/20/55/110 — it is a prior on what
  running that ablation *could yield*: in the most favourable published
  setting available (20 years, 23 markets, five horizons), the best
  leave-one-out arm wins by **+0.03 Sharpe full-sample while losing in
  half the subperiods**, with no correction applied. A margin that size is
  inside what selection over five arms manufactures. This program's own
  machinery would be obliged to discount it, and the arm would still cost
  an N that `docs/research/GATE4_FRAGILITY_2026-07-28.md` shows destroys
  trial 118's single gate-4 pass. The decision stays with the operator;
  this entry adds the missing prior and nothing else.

- **A structural observation about this program's own ensemble, filed as
  an observation and not as a claim.** The paper's finding is that the
  trend spectrum is **bimodal** — the short end (20d) and the long end
  (250d/500d) carry the value, the middle (60–125d) is the drag, and
  removing 500d is the single most damaging ablation of the five. This
  program's ensemble is **10 / 20 / 55 / 110** days. Every one of its four
  windows sits **at or below the paper's 125d medium band**, and it has
  **no member anywhere near the 250d/500d long end the paper calls
  indispensable**. If the paper's structure transferred, this program
  would be holding the short-plus-middle cluster and none of the long
  anchor. **Transfer is not established and is not assumed**: different
  instrument (spot versus futures), different direction (long-only versus
  long–short), different asset class (crypto versus 23 traditional
  futures), different era (2018–2025 versus 2005–2025), and a different
  objective (absolute return versus index replication). It is also **not
  testable here** — P3 forbids a new single-market parameter family, and a
  long-window arm would be exactly that. Recorded so the fact is on the
  record rather than rediscovered later, with the caveat attached.

- **Borri, Liu, Tsyvinski and Wu, "Cryptocurrency as an Investable Asset
  Class: Coming of Age" (arXiv 2510.14435v4, 21 Mar 2026, q-fin.GN) —
  located, abstract only, not an arrival.** Organizes crypto empirical
  regularities into seven stylized facts, reports that "risk-adjusted
  performance so far is broadly comparable" to traditional markets and
  that the cross-section reduces to a small factor set, and discusses
  "potential data quality issues". **The abstract states no return,
  Sharpe, drawdown or sample period, and the full text was not read**, so
  nothing here bears on the survivorship-flattered 13-coin benchmark in
  the standing answer. Filed as **located but unverified**, not as a
  finding. **Testable-here: no** (survey).

- **Search direction closed for the third consecutive pass: recent-regime
  crypto trend performance versus buy-and-hold.** A targeted query for
  2025–2026 measurements returned price-prediction and outlook
  publications only (Motley Fool, CoinLore, Phemex, CoinDCX, UEEx, Tiger,
  Yahoo Finance) — none measures a trend rule against its passive twin on
  a stated sample. **No arrival.** The momentum-regime-decay question
  stays at **two arrivals**, unchanged since 2026-08-23, and remains
  strictly separate from the redundancy question; the two are not pooled.
  Three consecutive empty passes is now itself evidence about the channel:
  this direction is not producing measurements and should not be re-run
  every night.

- **Meta-observation — fifteenth consecutive pass with nothing runnable
  under P1-only, but the first in six passes that changed a pending
  decision's inputs.** Nothing was run, no arm was tested, no trial
  registered, and the standing answer is unchanged in every clause. What
  changed is the evidence available to the operator on the one open
  research question: the experiment they were asked to authorize has a
  published precedent, and that precedent's own numbers argue it cannot
  deliver a trustworthy answer.

## 2026-08-26 — iteration 50 (P1 maintenance; iteration 48's failure to locate becomes a partial locate, through a third party rather than the paper)

- **Zarattini, Pagani and Barbon, "Catching Crypto Trends; A Tactical
  Approach for Bitcoin and Altcoins" — the lookback set is now on the
  record, obtained from a review rather than from the paper.** SSRN
  returned **HTTP 403** again today, for both the abstract page and the
  `Delivery.cfm/5209907.pdf` link, so this is the **second consecutive
  iteration** in which the full text was not retrievable and the second
  time no claim is made about its tables. Two new sources were reachable.
  (1) **RePEc/IDEAS `chf/rpseri/rp2580`** gives the verbatim abstract and
  identifies it as **Swiss Finance Institute Research Paper 25-80**,
  2025. (2) **CXO Advisory's review**
  (`cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies`),
  whose free portion covers the method but stops at "Subscribe to Keep
  Reading" before any result, states the design: Donchian lookbacks of
  **5, 10, 20, 30, 60, 90, 150, 250 or 360 days**; **long-only**; sample
  **January 2010 through mid-March 2025** over **21,616 individual
  crypto-assets**; transaction costs tested at **0.10%, 0.25% and
  0.50%**; position sizing to a **25% target annualized volatility** with
  leverage capped at **200%**. Everything in this item is **second-hand
  and unverified against the paper's own text**, and the Sharpe, drawdown
  and Bitcoin comparison remain unread — the review paywalls exactly the
  numbers that would matter. **Testable-here: no.** Rotational top-20
  selection, volatility targeting and 2x leverage are a different
  portfolio construction from this program's unlevered equal-weight
  BTC/ETH book, and P3 forbids a new single-market parameter family
  regardless.

- **A discrepancy inside that item, recorded rather than smoothed.** The
  abstract says the dataset covers "all cryptocurrencies traded **since
  2015**"; the review says the sample begins **January 2010**. Both are
  quoted above as their sources state them. Nothing here resolves which
  is right, and no number downstream should be taken as resting on either
  date until the paper itself is read.

- **What the paper's own abstract says about correlation, which is not
  what this program needs.** The verbatim abstract's correlation clause
  is "we investigate correlations between **crypto-focused
  trend-following strategies and those applied to traditional asset
  classes**". That is a cross-asset-class comparison, not a
  **between-lookback** one. So even with today's partial locate, the
  crypto measurement of internal ensemble redundancy is **still not shown
  to exist in that paper**, and the ensemble-breadth question stays at
  **four arrivals**, unchanged from 2026-08-25. This item is **not**
  counted as a fifth arrival: it supplies structure, not a redundancy
  number, and the two must not be pooled.

- **A structural observation, now with a crypto-native and long-only
  corroboration.** Iteration 49 recorded that this program's windows —
  **10, 20, 55, 110**, verified today from the `config.windows` field of
  the live rows in `data/runtime/shadow_trial88.jsonl` — all sit at or
  below the 125d medium band of the liquid-futures ablation paper, with
  no member near the 250d/500d long end that paper finds indispensable.
  The closest **crypto**, **long-only**, **Donchian-ensemble** relative
  reported above uses **nine** lookbacks spanning **5 to 360 days**: one
  member faster than this program's fastest, and **three (150, 250, 360)
  longer than its longest**. Span ratio **11x here against 72x there**.
  This is the second independent structural datapoint pointing the same
  way, and unlike the first it is in this program's own asset class and
  direction. It is recorded as **structure only** — it is not evidence
  that a longer window would help here, it is not a performance claim,
  the surrounding construction differs in several ways at once, and it is
  **not testable here** under P3.

- **Bysik and Ślepaczuk, "Machine Learning-Based Bitcoin Trading Under
  Transaction Costs: Evidence From Walk-Forward Forecasting" (arXiv
  2606.00060, submitted 2026-05-19) — read from the arXiv abstract
  page.** About **70,000 hourly** BTC-USDT observations, **2018-2026**,
  XGBoost, LSTM and iTransformer in a **27-fold walk-forward** protocol.
  Reported: all three models are positive gross "in selected
  configurations"; naive sign-based strategies **fail once 10 bps costs
  are imposed**; a cost-aware filter that trades only when forecast
  magnitude exceeds a cost-based threshold "sharply reduces turnover and
  restores profitability in selected configurations", the strongest
  long-only XGBoost arm giving annualized returns above **65%** at Sharpe
  above **one**. **Testable-here: no** — hourly, machine-learned, and a
  new family under P3. Filed for one reason only: it is an outside
  measurement that a cost-magnitude threshold is what separates a
  gross-positive signal from a net-positive one, which is the same
  mechanism this program prices at about -6.4 bps round-trip. Note the
  selection language: "in selected configurations" appears twice, and the
  abstract states no multiple-testing correction, so the 65% figure is a
  **maximum over configurations**, not an expectation.

- **Bui and Nguyen, "Systematic Trend-Following with Adaptive Portfolio
  Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets"
  (arXiv 2602.11708, submitted 2026-02-12) — read from the arXiv abstract
  page.** "AdaptiveTrend": trend-following on **6-hour** intervals with
  monthly adaptive portfolio construction and asymmetric **long-short
  70/30** allocation, spot, **150+ pairs**, a **36-month** window
  **2022-2024**. Reported annualized Sharpe **2.41**, max drawdown
  **-12.7%**, Calmar **3.18**, benchmarked against TSMOM and
  equal-weighted buy-and-hold. Transaction-cost modelling is mentioned
  inside robustness analyses with **no level stated in the abstract**.
  **Testable-here: no** — 6-hour bars and long-short are both outside
  product law. Recorded with the same skepticism this loop applies to its
  own numbers: a Sharpe of 2.41 over a 36-month window that contains one
  bear and one recovery, with **no deflated Sharpe, no multiple-testing
  correction and no PBO mentioned in the abstract**, is a selected
  maximum until shown otherwise.

- **Mackic (2023) traced one level, still not read.** The "correlation of
  only 0.17 between very fast and very slow trend models" quoted in the
  liquid-futures ablation paper is its citation `bib.bib14`; a search
  points to **Adi Mackic (Man AHL), "High-Level Statistics of
  Trend-Following Speeds", 2023**, on Man Group data **January 1995 to
  August 2022**. The **0.17 figure was not found in any primary source
  today** — it exists here only as a secondary citation inside a paper
  this loop has already read. Filed as a **pointer, not an arrival**, and
  it must not be cited as a measurement until the primary is read. Two
  further leads located and **not read**: CFA Institute, "Decoding CTA
  Allocations by Trend Horizon" (2026-01-28), and arXiv **2507.15876**,
  "Re-evaluating Short- and Long-Term Trend Factors in CTA Replication: A
  Bayesian Graphical Approach".

- **Search channel formally closed: recent-regime crypto trend versus
  buy-and-hold.** Iteration 49 recorded a third consecutive empty pass on
  this direction and wrote that it "should not be re-run every night".
  Today the loop acted on that instead of restating it: the direction was
  **not queried**, and it is now closed. **Reopen condition, fixed here in
  advance so the decision is not made after seeing a result:** it reopens
  only on a named source that measures a trend rule against its own
  passive twin on a **stated sample with stated costs** — a dated,
  citable measurement, not an outlook, forecast or price-prediction
  article. Three consecutive empty passes cost real search budget;
  closing the channel is the finding.

- **Meta-observation — sixteenth consecutive pass with nothing runnable
  under P1-only.** Nothing was run, no arm tested, no trial registered,
  and the standing answer is unchanged in every clause. Two things did
  change: a fact that iteration 48 had to file as a **failure to locate**
  is now **partially located**, and one search channel is **closed** with
  its reopen condition written down. Both are the kind of change the
  convergence rule asks for — they shrink the search rather than grow it.

## 2026-08-27 — iteration 51 (P1 maintenance; two "new" sources on the open operator question turn out to be the same authors, and the arrival tally is an overcount)

- **Benhamou, Ohana, Etienne, Guez, Setrouk and Jacquot,
  "Re-evaluating Short- and Long-Term Trend Factors in CTA Replication:
  A Bayesian Graphical Approach" (arXiv 2507.15876, submitted 17 July
  2025).** Read from the arXiv HTML full text. Setup: short-term trend
  (STT) built on lookbacks **n ∈ {10, 20, 40, 60}** days, long-term
  trend (LTT) on **n = 500** days, decomposed against a market beta
  factor with a Bayesian graphical model; primary sample **January 2010
  to June 2025**, with robustness windows June 2020–June 2025, January
  2010–December 2015 and January 2016–December 2020. Table 3 (daily
  sampling), Sharpe ratio row as printed: **LTT 0.39, MKT 0.40, STT+LTT
  0.40, STT 0.20, MKT+STT+LTT 0.45, MKT+STT 0.49, SG CTAT 0.03**.
  Verbatim: *"Combining STT and LTT raises the Sharpe/MaxDD efficiency
  to 2.37, reflecting the asymmetric payoff benefits of mixing fast and
  slow trend signals."*

  **What that table is, read plainly.** Adding an entire fast band
  (four lookbacks, 10 to 60 days) on top of a 500-day slow model moved
  the Sharpe from **0.39 to 0.40** — **+0.01** — and plain market beta
  alone scored **0.40** as well. The paper's own case for the blend
  therefore rests on the **Sharpe/MaxDD** ratio (2.37), not on Sharpe.
  This is the second measurement of *what a horizon band is worth on top
  of an existing ensemble* that this loop has obtained; the first was
  iteration 49's leave-one-out arm at **+0.03** full-sample Sharpe (0.74
  to 0.77) while losing in two of four subperiods. Both are in the
  hundredths. **Testable-here: no** — multi-asset liquid futures,
  long-short, CTA replication rather than absolute return, no crypto in
  the universe.

  **The correlation this loop wanted is not in this paper either.** It
  does **not** print the correlation between the STT and LTT factors
  themselves. What it prints (Table 2) is correlation *to the SG CTA
  benchmark*: **STT 0.65, LTT 0.81, STT+LTT 0.84**. **A number was
  discarded before it was written anywhere durable:** a first
  summarizing read offered "low overlap, 0.24–0.50 between individual
  factor strategies"; a second targeted read found no such printed
  figure, so it is **not recorded** — the same discipline applied to the
  retracted 0.36→0.40 figure in iteration 46.

- **CFA Institute, Enterprising Investor, "Decoding CTA Allocations by
  Trend Horizon" (28 January 2026).** Read. Byline verbatim: **"Eric
  Benhamou, PhD", "Jean-Jacques Ohana, CFA", "Béatrice Guez", "Thomas
  Jacquot, CFA"**. Five mono-horizon sleeves at **20, 60, 125, 250 and
  500 trading days**, grouped fast (20–60), medium (~125) and slow
  (250–500); sample stated only as "the last five years" against the SG
  CTA Trend Index, i.e. roughly 2021–2026, with **no start date given**.
  Correlations reported are to the index, not between sleeves: verbatim,
  *"The 125-day and 250-day sleeves have the highest correlations with
  the index (around 82%). The 20-day sleeve is the least correlated,
  with a correlation of about 66%."* On overlap, verbatim: *"Fast and
  slow horizons contribute complementary information: Fast trend helps
  capture sharp reversals and shorter-lived regimes. Slow trend anchors
  the portfolio to longer-term drifts and tends to stabilize drawdown
  behavior."* **Testable-here: no.**

- **The finding of the day, and it is a subtraction.** Both items above
  are by **the same research group as an arrival already on this
  program's record**. arXiv 2510.23150v2 — the leave-one-horizon-out
  ablation read in full in iteration 49 — is authored by **Etienne,
  Ohana, Benhamou, Guez, Setrouk and Jacquot**; arXiv 2507.15876 is
  **Benhamou, Ohana, Etienne, Guez, Setrouk and Jacquot**, the same six
  names; and the CFA Institute post is four of those six. Affiliation
  confirms it: **Ai For Alpha** (Alban Etienne), with Eric Benhamou also
  at Université Paris Dauphine-PSL. The CFA post uses **exactly** the
  horizon set H = {20, 60, 125, 250, 500} of arXiv 2510.23150. So
  today's two sources are **not two new arrivals** on the ensemble-breadth
  question — they are the same strand, one publication earlier and one
  practitioner restatement. **Independence added today: zero.** They are
  filed as corroboration inside an existing arrival.

- **Correction to this program's own tally, made in place.** The
  ensemble-breadth question has been described since iteration 49's
  closing paragraph, and throughout iteration 50, as having **four**
  outside arrivals. **That is an overcount, and iteration 49's own body
  text said so correctly before its own closing paragraph contradicted
  it** ("stays at three arrivals, all liquid-futures"). The distinct
  sources are three: (1) **arXiv 2607.19497**, Sepp and Lucic, 21 Jul
  2026; (2) **arXiv 2510.23150v2**, Etienne et al. (Ai For Alpha), 28
  Oct 2025; (3) **arXiv 2504.10914v15**, Valeyre, 12 Aug 2026. The
  "fourth" counted in iteration 49's closing line — "the ablation itself
  performed elsewhere" — **is source (2) again**, first logged from its
  abstract in iteration 46 and then re-logged after being read in full.
  Reading a paper twice is not two arrivals. **Corrected count: three
  distinct sources from three groups**, which is exactly the escalation
  threshold rather than one above it. The escalation itself stands
  unchanged — three was always the trigger — so the operator decision
  does not move; only the size of the evidence behind it does, and it
  moves **down**.

- **Structural position, restated and not inflated.** This program's
  windows are **10, 20, 55, 110**. Ai For Alpha's ensemble spans
  **20 to 500** days and its own fast band stops at **60**; the closest
  published crypto relative (iteration 50, second-hand via CXO Advisory)
  spans **5 to 360**. Our entire ensemble sits at or below the 125-day
  sleeve of the first and below the median lookback of the second. That
  is **two** independent structural datapoints, the same two iteration
  50 claimed — today's additions do not make it three, because they are
  the same group. Recorded as **structure only**: not a performance
  claim, not evidence a longer window would help here, and pointing at a
  **longer-window family**, which **P3 forbids outright**.

- **Meta-observation — seventeenth consecutive pass with nothing
  runnable under P1-only.** Nothing was run, no arm tested, no trial
  registered, and the standing answer is unchanged in every clause. What
  changed is the record's honesty about its own evidence: one tally
  corrected downward, one apparent pair of new arrivals reclassified to
  zero, and one summarizing-fetch number discarded rather than kept.

## 2026-08-28 — iteration 52 (P1 maintenance; four candidate sources examined, zero arrivals — and the measurement the operator question needed turns out to be inside this repo)

- **Four outside items were examined today on the ensemble-breadth
  question. All four are negatives, and the arrival tally stays at
  three.** Listed with what each does and does not print, because a
  failure to locate is worth as much on the record as a locate:

  - **Panjabi and Robertson (Man Group), "Honey, I Shrunk the
    Trend-Following", AIMA, 17 June 2024.** Sample stated as 1 January
    1900 – 31 December 2023 for its long figure and January 1995 –
    December 2023 for the primary analysis. Lookback windows: **not
    printed**. Single-horizon versus multi-horizon Sharpe comparison:
    **not printed**. Between-sleeve correlations: **not printed**.
    Leave-one-out or ablation: **not performed**. Testable-here: **no** —
    it carries no number this program can use.
  - **Tzotchev, "Designing a Robust Trend-Following System",
    QuantPedia, 17 July 2024.** Lookbacks named only as **2 days, 32
    days and 1 year**; sample period **not printed**; ensemble-versus-
    single comparison **not printed**; between-sleeve correlation **not
    printed**; ablation **not printed**. Testable-here: **no**.
  - **McClain (LPL Research), "A Tale of Two CTAs", 13 August 2026.**
    Horizons named — **"20 days at the fast end to 250 days at the slow
    end"**, plus "50, 100, or 200 days" and "6- or 12-month return".
    Sharpe broken out by horizon: **not printed**. Between-sleeve
    correlation: **not printed**. Ablation: **not printed**. It gives
    index-level performance (SG Trend Index +7.9% through August against
    the Short-Term Index +3.2%) which is a horizon *dispersion*
    observation, not an incremental-value one. Testable-here: **no**.
  - **Bui and Nguyen (Talyxion Research, Hanoi), "Systematic
    Trend-Following with Adaptive Portfolio Construction: Enhancing
    Risk-Adjusted Alpha in Cryptocurrency Markets" (arXiv 2602.11708v1,
    12 February 2026).** This is the first **crypto** trend paper this
    loop has found that prints a **component ablation table**, and it is
    worth recording precisely why it still does not answer the question.
    Universe "150+ cryptocurrency pairs", sample **January 2022 –
    December 2024** (36 months). Table 3 as printed — Full AdaptiveTrend
    **Sharpe 2.41 / MDD −12.7%**; w/o Dynamic Trailing Stop **1.68 /
    −22.4%**; w/o Market Cap Filter **2.05 / −17.8%**; w/o Sharpe Ratio
    Selection **1.92 / −19.1%**; w/o Asymmetric Allocation **2.12 /
    −14.3%**; Fixed Parameters (no opt.) **1.34 / −28.6%**. **No row
    removes a lookback.** The momentum lookback is a single scalar `L`
    re-chosen **monthly by grid search**, so the paper has no horizon
    ensemble to ablate in the first place. Two further disqualifications
    under product law: it is **long/short on Binance perpetual futures**,
    not spot long-only, and its headline Sharpe is produced by monthly
    re-optimization over a 36-month window with **no multiple-testing
    correction stated**. Testable-here: **no**, on all three counts.

- **Byline check, per the discipline iteration 51 had to install.** The
  search also surfaced the **Sepp and Lucic `TrendFollowingSystems`
  repository, companion to SSRN 3167787**. Sepp and Lucic are already
  arrival (1) via arXiv 2607.19497. Same authors, different paper —
  filed as **corroboration inside an existing arrival, not a new
  arrival**, exactly as the three Ai For Alpha publications were. The
  Talyxion authors are a genuinely new group, but their paper is a
  negative, so **independence added today: zero**. Distinct sources on
  the ensemble-breadth question remain **three**: arXiv 2607.19497
  (Sepp and Lucic), arXiv 2510.23150v2 (Etienne et al., Ai For Alpha),
  arXiv 2504.10914v15 (Valeyre).

- **The internal measurement, which is the substantive item today.**
  Every source above was being sought because the loop believed it held
  **no** internal number on what one horizon is worth. That belief was
  wrong. **Experiment 7 pre-registered a window-set axis** — line 56 of
  `GOALP_EXPERIMENT7_PREREGISTRATION.md` declares
  `window set ∈ { {10,20,55,110}, {20,55,110,220} }` and line 80 names
  it "Fast (10-110) vs slow (20-220) window sets" — and ran it as a
  full 2x2x2 grid, trials **86-93**, registered 2026-07-22. Read from
  `docs/reports/research/trial_registry.jsonl`, the four pairs differ in
  **exactly one parameter key, `dc_windows`**, on the same BTC/ETH
  universe, the same 2018-03-04..2025-07-01 window, the same code
  version `6c99598` and identical cost assumptions (10 bps fee, 5 bps
  slippage, next-bar-open fill). And because the two sets **share
  20/55/110**, the contrast is a **single-window swap: 10 against 220**.

  | Exit | Gate | Fast (T) | Slow (T) | ΔSharpe | ΔMDD | equity ratio | trades ratio |
  |---|---|---:|---:|---:|---:|---:|---:|
  | half_low | off | 86 (1.091622) | 90 (1.066666) | **+0.024956** | −7.2714pp | 0.9928 | 2.1015 |
  | half_low | on | 87 (1.122056) | 91 (1.096663) | **+0.025393** | −6.9008pp | 0.9274 | 1.8145 |
  | mid_channel | off | 88 (1.182061) | 92 (1.093639) | **+0.088422** | −14.5784pp | 1.1624 | 1.9335 |
  | mid_channel | on | 89 (1.136883) | 93 (1.076638) | **+0.060245** | −12.2753pp | 0.9850 | 1.7259 |

  Mean ΔSharpe **+0.049754**, range **+0.024956 to +0.088422**, sign
  positive in **4 of 4**; mean ΔMDD **−10.2565pp**, favourable in **4 of
  4**; terminal money a **wash** — the fast set wins **1 of 4** with a
  mean equity ratio of **1.0169** — bought at a mean **1.8939x** the
  trade count. Testable-here: **already tested**, on this program's own
  data, at **zero additional N**, because all eight trials were
  registered on 2026-07-22 and no new trial is created by subtracting
  two published rows.

- **What it does and does not license.** It is **not** the leave-one-out
  the operator was asked to authorize: both arms carry four windows, so
  it measures one window **against another window**, never **against
  nothing**. It is also four cells of one 2x2 grid on two assets over
  one window — the same non-independence iteration 20 recorded for the
  eight-member family, so "4 of 4" is a sign count, not four tests. What
  it does establish is the **scale**: on this program's own rule, its
  own windows and its own universe, swapping a single window moves
  Sharpe by **hundredths** — mean **+0.0498** — which is the same order
  as the two outside numbers already on the record, **+0.01** (arXiv
  2507.15876, adding a whole fast band to a 500-day model) and **+0.03**
  (arXiv 2510.23150v2's leave-one-out). Three measurements, three
  sources, one internal, all in the hundredths, all pointing the same
  way.

## 2026-08-29 — iteration 53 (P1 maintenance; five candidate sources examined, zero arrivals — and the repo turns out to hold a *second* window swap that disagrees with the first)

- **2026-08-29 — "What Trend Following Actually Adds to a Risk-Premia Core",
  Beyond Passive Investing (Substack), published 2026-06-07, no individual
  byline.** Surfaced at the top of the search for lookback ablations, and the
  search engine's own summary attributed a leave-one-out over 20 / 60-125 /
  500-day bands to it. **Fetched and checked: the article contains no such
  table.** It names no lookback bands and prints no per-horizon Sharpe. It is
  a 50/50 blend study — risk-premia core (SPY/TLT/GLD) plus a 62-market
  futures trend replica, long and short, refit on a rolling walk-forward —
  reporting core Sharpe about 1.1, standalone trend replica about the same,
  blended **1.49** with drawdown 17% to 13% over 1995-2026. Explicitly
  **gross of costs**: "no commissions, no slippage, no bid-ask, no management
  fee". No multiple-testing correction; the author states "I make no
  out-of-sample claim". The band figures in the search summary are almost
  certainly arXiv 2507.15876's, which this loop already holds. Testable here:
  **no** — long/short futures, gross of costs, and no horizon decomposition at
  all. **Lesson repeated from iteration 50: a search-engine summary is not a
  source.** The attributed table did not exist.

- **2026-08-29 — arXiv 2512.08124, "Long-only cryptocurrency portfolio
  management by ranking the assets: a neural network approach", Zijiang Yang,
  submitted 2025-12-09.** The rare candidate that is genuinely **long-only,
  crypto, and daily-rebalanced** — three of four product-law conditions. But
  the signal is a neural ranking net, not a horizon ensemble: **no
  per-lookback table, no ablation of any component**, and **no deflated
  Sharpe, PBO, or multiple-testing correction**. Headline Sharpe **1.01**,
  annualized return 64.26%, over May 2020 to November 2023. Transaction costs
  are only qualitatively stress-tested ("robustness to the increase of
  transaction fee"), never stated as a number in the abstract. Testable here:
  **no** on the open question — it hands over nothing about what one horizon
  is worth.

- **2026-08-29 — arXiv 2604.26747, "From Hypotheses to Factors: Constrained
  LLM Agents in Cryptocurrency Markets", Huang, Fan, Hu and Ye (HKUST,
  Rutgers, BNU-HKBU), submitted 2026-04-29.** Crypto, daily rebalance,
  one-day execution lag, **5 bps one-way** costs — and a headline of
  **44.55%** annualized at Sharpe **1.55** on a 2024-2026 out-of-sample
  window. Fails product law at the first hurdle: the portfolio is
  **long-short** equal-weighted quintile sorting, top against bottom. It also
  reports the agent ran **five search rounds generating 25 candidate factors**
  with **no deflated Sharpe, no PBO, and no multiple-testing adjustment** —
  the exact failure this program's gate 4 exists to price. No ablation over
  horizons. Testable here: **no**.

- **2026-08-29 — "Boundaries of Time-Series Momentum", Matti Suominen (Aalto)
  and Erik Hjalmarsson (Gothenburg), Financial Management, Early View, first
  published 2026-07-06, DOI 10.1111/fima.70055.** Uses **25 time-series
  momentum strategies with lookback and holding horizons from 1 to 12 months**
  — exactly the ensemble shape the open question is about — and then
  **collapses them into a single equally weighted index**. No individual
  horizon is ever broken out: no per-lookback Sharpe, no leave-one-out. Equity
  index cash positions across the US and 20 countries, **long/short** against
  the risk-free rate, **monthly**, and **transaction costs are not discussed
  or deducted**. Newey-West and IVX robustness, but **no Bonferroni, no
  deflated Sharpe, no PBO**. Testable here: **no**. Filed because it is the
  cleanest recent example of the thing this loop keeps hitting — an ensemble
  is built, its breadth is never priced.

- **2026-08-29 — "Nonlinear Time Series Momentum", Tobias J. Moskowitz (Yale
  and AQR), Riccardo Sabbatucci (SSE), Andrea Tamoni (Notre Dame), Bjorn Uhl
  (Hamburg), dated 2025-12-10, FoFI 2026 working paper.** The most serious
  candidate today by pedigree, and the one that needed real work to read — the
  fetch returned raw PDF object streams and the byline had to be recovered by
  local text extraction rather than guessed. 66 pages, **122 occurrences of
  "lookback" and 143 of "Sharpe"**, and it still does not answer the question:
  the word **"ensemble" appears zero times**, lookbacks are studied one at a
  time, and the paper's contribution is a **nonlinear weighting function of
  the trend**, not horizon breadth. Universe is **8 equity index, 24 commodity
  and 21 rates/FX futures** — **zero crypto, zero spot** — and the strategy is
  sign-based **long/short**. Occurrences of "transaction cost": **1**, and it
  is an argument rather than a measurement ("likely to improve after
  accounting for transactions costs"). Occurrences of "deflated": **0**.
  "Multiple testing": **0**. Testable here: **no**.
  **Byline check per iteration 51's discipline:** Moskowitz, Sabbatucci,
  Tamoni and Uhl are a genuinely new group, unrelated to Sepp and Lucic, to
  Ai For Alpha, or to Valeyre. But a new group publishing a **negative** for
  this question adds no independence. **Arrivals added today: zero.** Distinct
  sources on the ensemble-breadth question remain **three**: arXiv 2607.19497
  (Sepp and Lucic), arXiv 2510.23150v2 (Etienne et al., Ai For Alpha),
  arXiv 2504.10914v15 (Valeyre).

- **The internal item, and a correction to iteration 52.** Yesterday's entry
  closed with "Three measurements, three sources, **one internal**, all in the
  hundredths, **all pointing the same way**." Both emphasized clauses are
  wrong. Searching `dc_windows` across all 133 registered trials shows
  **experiment 8 contains a second matched single-window swap**: trials
  **94-97** ran `{10,20,55,110}` and trials **98-101** ran `{10,20,110,220}`
  on the same 13-coin universe, the same 2018-03-04..2025-07-01 window, the
  same code version `5e2d50e`, the same staggered mode and identical cost
  assumptions (10 bps fee, 5 bps slippage, next-bar-open fill). The two sets
  share **{10, 20, 110}**, so the contrast is a single-window swap of **55
  against 220** — a *different* window from experiment 7's **10 against 220**.
  Each of the four exit-by-gate pairs was verified to differ in **exactly one
  parameter key, `dc_windows`**.

  | Exit | Gate | {10,20,55,110} | {10,20,110,220} | dSharpe | dMDD | equity ratio | trades ratio |
  |---|---|---:|---:|---:|---:|---:|---:|
  | half_low | off | T94 0.972534 | T98 0.920546 | **+0.051988** | +0.2451pp | 1.0713 | 1.0625 |
  | half_low | on | T95 0.954871 | T99 0.924608 | **+0.030263** | +0.2126pp | 1.0431 | 1.0394 |
  | mid_channel | off | T96 1.000378 | T100 0.945654 | **+0.054724** | +0.2120pp | 1.0555 | 1.0558 |
  | mid_channel | on | T97 0.921164 | T101 0.949161 | **-0.027997** | +0.4416pp | 0.8194 | 1.0419 |

  Mean dSharpe **+0.027245**, positive in **3 of 4** — not 4 of 4. Mean dMDD
  **+0.2778pp**, i.e. favourable to the shorter set in **0 of 4**. Mean trades
  ratio **1.0499**, against experiment 7's **1.8939**.

- **What the second swap changes.** Three things, and none of them favour
  buying the arm. (1) **Magnitude is not stable across the registry**:
  +0.0498 and +0.0272 differ by nearly two-to-one, so yesterday's number is
  one of two prices, not *the* price. (2) **The drawdown story reverses.**
  Experiment 7's swap bought -10.2565pp of drawdown in 4 of 4; experiment 8's
  bought **+0.2778pp against** in 4 of 4. Since drawdown is the thing this
  program's headline result actually purchased, that reversal matters more
  than the Sharpe agreement. (3) **The turnover cost is attributable.**
  Experiment 7's near-doubling of trades came with the **10** entering, not
  with the **220** leaving — because swapping 55 for 220 while holding the 10
  fixed leaves trade count almost unchanged at **1.05x**.

- **The confound, stated before it can be over-read.** The two swaps differ in
  **universe (2 coins against 13), code version (`6c99598` against
  `5e2d50e`), execution mode (plain against staggered) and which window moved
  — all at once.** The difference between +0.0498 and +0.0272 therefore
  **cannot** be attributed to the window position. Each number is valid
  **inside its own experiment only**; putting them side by side is
  descriptive, and treating the pair as a controlled comparison would repeat
  the universe-pooling error retracted on 2026-07-26 and again on 2026-07-28.
  The published sign count in `GOALP_EXPERIMENT8_RESULT.md` — "the barbell
  window set also underperformed fast in 3 of 4 pairings" — is **correct as
  written and is not edited**; what was missing was the paired magnitude, the
  drawdown direction and the turnover attribution.

- **And the channel is now closed.** Across all **133** registered trials,
  **every single one carries exactly four windows** — 48 carrying a
  `dc_windows` set and all 133 carrying a four-entry `lookbacks` string.
  There is **no trial anywhere in the registry that ran three windows**, so
  the leave-one-out the operator was asked to authorize **cannot be answered
  at zero N by any further reading of the registry**. Searching harder is no
  longer a route. The registry holds exactly **two** window-against-window
  swaps and **zero** window-against-nothing ablations, and today's pass
  enumerated both.

## 2026-08-30 — iteration 54 (P1 maintenance; five candidate sources examined, and a fourth author group — missed by eighteen prior passes — finally prices horizon breadth with the architecture held fixed)

- **arXiv 2406.08742v1, Joel Ong and Dorien Herremans, "DeepUnifiedMom:
  Unified Time-series Momentum Portfolios with Multi-Task Learning"
  (submitted 13 June 2024, q-fin.CP, 21 pages).** Read from the arXiv HTML
  full text. Universe: **49 futures contracts** across "equity indexes,
  fixed income, foreign exchange, and commodities"; **no cryptocurrency**.
  Direction: **long-short** — verbatim, "establishing long positions during
  uptrends and short positions during downtrends". Daily data from January
  1990, out-of-sample backtest **January 2000 to December 2023**. Table 2
  caption verbatim: *"Backtest results (net) for the period from January
  2000 to December 2023, with transaction costs set at 3 basis points."*
  The Sharpe annualization convention is **not stated anywhere in the
  paper**; the ratios below are therefore internally comparable but not
  comparable to this program's 365-period figures. No deflated Sharpe
  ratio, no PBO, no multiple-testing correction of any kind.
  **Testable-here: no** — long-short liquid futures, one-way 3 bps, no
  spot and no crypto.

  Table 2 Sharpe column, as printed:

  | Portfolio | Sharpe |
  |---|---:|
  | TSMOM(1) | 0.73 |
  | TSMOM(3) | 0.80 |
  | TSMOM(6) | 0.82 |
  | TSMOM(12) | 1.01 |
  | TSMOM(1,4) | 1.00 |
  | TSMOM(5,8) | 0.87 |
  | TSMOM(9,12) | 1.00 |
  | TSMOM(1,12) | 1.07 |
  | DeepUnifiedMom(Fast) | 1.34 |
  | DeepUnifiedMom(Medium) | 0.99 |
  | DeepUnifiedMom(Slow) | 1.54 |
  | DeepUnifiedMom(CAN) | 2.33 |
  | DeepUnifiedMom(EQWT) | 2.31 |
  | DeepUnifiedMom(MVO) | 1.72 |

  Notation verified against the paper's own definitions before any
  subtraction was performed. TSMOM(n) is "based on the past n month's
  returns"; TSMOM(a,b) is "An equal-weighted combination of the a ... to
  b-month TSMOMs", so **TSMOM(1,12) is a twelve-signal equal-weighted
  ensemble and TSMOM(12) is a single signal**. Fast, Medium and Slow are
  each trained on a **single** horizon — "20 trading days for
  DeepUnifiedMom(Fast), 60 trading days for DeepUnifiedMom(Medium), and
  120 trading days for DeepUnifiedMom(Slow)" — and **CAN** is the
  "Capital Allocation Network", whose "output ... serves as a set of
  weights assigned to the fast, medium, and slow momentum portfolios".

- **The finding of the day: the first architecture-matched, naive-rule
  price for horizon breadth, and it is in the hundredths.** Inside Table 2,
  with no neural network anywhere in either arm, going from **one** horizon
  to **twelve** moves the Sharpe from **1.01 to 1.07 — plus 0.06**, net of
  3 bps. That is a subtraction between two printed rows and nothing more:
  no standard error is given for either, one universe, one period, so it
  is a **sign and a magnitude, not a test**. It is now the fifth
  measurement of what horizon breadth is worth that this loop holds, and
  **all five land in the hundredths**:

  | Source | What was priced | Sharpe delta |
  |---|---|---:|
  | arXiv 2510.23150v2 (Ai For Alpha), iteration 49 | leave-one-horizon-out | **+0.03** (0.74 to 0.77) |
  | arXiv 2507.15876 (Ai For Alpha), iteration 51 | whole fast band onto a slow model | **+0.01** (0.39 to 0.40) |
  | this repo, experiment 7, iteration 52 | one window swapped (10 against 220) | **+0.0498** |
  | this repo, experiment 8, iteration 53 | one window swapped (55 against 220) | **+0.0272** |
  | arXiv 2406.08742 Table 2, **today** | **one horizon against twelve** | **+0.06** |

  The five are **not** commensurable and no arithmetic may be done across
  them — different asset classes, directions, cost models, periods and
  architectures, and above all different amounts of breadth. What can be
  said is weaker and still worth saying: **nobody who has published a
  number on this question has found one outside the hundredths**, and the
  largest of the five buys eleven extra horizons for it.

- **Non-monotone inside the same table, and it points at span rather than
  count.** TSMOM(9,12) — a four-signal band around the best single horizon
  — scores **1.00**, *below* TSMOM(12)'s **1.01**; TSMOM(1,4) also scores
  **1.00**. Only the full twelve-month span beats the best single, and by
  0.06. So in this source, adding **neighbouring** horizons bought nothing
  or slightly less than nothing, and the entire gain came from **spanning
  distant** horizons. Recorded as **structure only** — this program's own
  windows span 10 to 110, a factor of 11, against 1-to-12 months, a factor
  of 12, and that resemblance is not evidence about anything here.

- **The large breadth number in the same table is not a breadth number,
  stated before it can be over-read.** Best single-horizon *neural* model
  (Slow, **1.54**) against the three-horizon equal-weight combination
  (EQWT, **2.31**) is **+0.77** — more than ten times the naive figure.
  It is **not** attributable to breadth: the three task-specific networks
  are **jointly trained** inside one multi-task-learning framework, so the
  gap confounds joint training and the mixture-of-experts architecture with
  horizon count. This program's rule is naive, so **the applicable branch
  is +0.06, not +0.77** — and a document that cited the larger number as
  the price of breadth would be wrong.

- **Outside corroboration for a route this program closed on its own
  evidence.** In the same table, the learned Capital Allocation Network
  (**2.33**) beats naive equal weighting over the identical three
  portfolios (**2.31**) by **+0.02**, and mean-variance optimization
  (**1.72**) *loses* to equal weighting by **-0.59**. An independent group
  carrying a full deep-learning allocator therefore measures sophisticated
  allocation at roughly **one percent** of Sharpe over doing nothing
  clever, and measures MVO as actively destructive. This program uses fixed
  equal sleeve weights, refused per-market tuning, and P3 forbids
  reopening the cash-aware allocation route with a cap parameter or a tilt.
  **Same direction, from outside, net of costs.** It is corroboration, not
  proof: different asset class, different allocator, no crypto.

- **Byline check per iteration 51's discipline, and this one passes.**
  **Joel Ong** and **Dorien Herremans** appear in none of the three
  arrivals already on record — (1) **Sepp and Lucic**, arXiv 2607.19497;
  (2) **Etienne, Ohana, Benhamou, Guez, Setrouk and Jacquot** (Ai For
  Alpha), arXiv 2510.23150v2; (3) **Valeyre**, arXiv 2504.10914v15.
  Institutional affiliations are **not printed on the arXiv abstract page**
  and are therefore not recorded here; the independence claim rests on the
  name check alone, which is the check that matters. **Arrival tally moves
  three to four** — the first increase since iteration 49, and the exact
  mirror of iteration 51, where two apparent arrivals collapsed into one
  because the names repeated.

- **Honesty about what kind of event this is: a search failure corrected,
  not new literature.** arXiv 2406.08742 was submitted **13 June 2024** —
  older than every one of the three existing arrivals — and **eighteen
  consecutive external-research passes missed it**. Nothing arrived today;
  something that had been sitting in the open for fourteen months was
  finally found. Same class as iteration 50's failure-to-locate becoming a
  locate, and it should lower rather than raise confidence in the
  completeness of every prior pass.

- **Primary-source read of the closest crypto relative, and a prior loop
  statement narrowed.** Iteration 50 recorded the Concretum paper
  second-hand through CXO Advisory, whose free portion "paywalls exactly
  the numbers that would matter". The **primary source** was read directly
  today (`concretumgroup.com/catching-crypto-trends-a-tactical-approach-for-bitcoin-and-altcoins/`)
  and it prints two of them in the open: **"Sharpe ratio above 1.5"** and
  **"annualized alpha of 10.8% relative to Bitcoin"**. So the paywall was
  never the obstacle for those two. It is the obstacle for nothing else
  either, because the number iteration 48 actually wanted — **the ensemble
  priced against a single lookback window** — is **not present on the
  primary page at all**, alongside no drawdown figure, no sample dates, no
  window list and no cost levels. **Iteration 48's conclusion therefore
  stands unchanged** — the closest published crypto relative of this
  program's own rule does not hand over the redundancy number — but it now
  rests on a direct read rather than on an assumption about what a paywall
  was hiding. Authorship, newly recorded: **Carlo Zarattini, Alberto Pagani
  and Andrea Barbon**, SSRN abstract 5209907. The paper itself remains
  **unread**: SSRN returns HTTP 403 to this loop's fetcher, and the
  publisher's own papers index carries only a four-sentence blurb.

- **A search-engine attribution examined and rejected, for the second
  consecutive iteration.** The engine credited that same source with a
  "net-of-fees Sharpe ratio of 1.57" and "a maximum drawdown of only 11%".
  The primary page prints **"above 1.5"** and **no drawdown figure
  whatsoever**. Neither **1.57** nor **11%** is recorded anywhere, under
  the same discipline that discarded the unfound 0.24-0.50 correlation
  range in iteration 51 and the non-existent Substack leave-one-out table
  in iteration 53. Three iterations, three engine-supplied figures that the
  cited source does not print. **Treat summarizer output as a pointer to a
  document, never as a reading of it.**

- **arXiv 2606.27670, Yu Peng, Matloob Khushi and Josiah Poon, "CryptoGAT"
  (26 June 2026).** Abstract read. Graph-attention **price forecasting**
  for cryptocurrency, arguing that "time series models have difficulty
  learning effective information" in crypto. No transaction costs, no
  strategy, no Sharpe, no deflated Sharpe or PBO in the abstract.
  **Testable-here: no** — a forecasting-accuracy result is not a costed
  long-only spot rule, and this program has no route from one to the other.

- **Beckmeyer and Wiedemann, "All Days Are Not Created Equal:
  Understanding Momentum by Learning to Weight Past Returns", Journal of
  Banking & Finance vol. 181 (2025).** Abstract read via RePEc;
  ScienceDirect and SSRN both return HTTP 403 to this loop's fetcher, so
  the full text is **unread**. Verbatim from the abstract: "By flexibly
  weighting the information contained in past realized returns, we
  construct a momentum strategy that outperforms and subsumes the
  performance of traditional stock momentum" and "We find that the response
  to earnings announcements, market-wide jumps and large individual returns
  realized in the formation period are most informative about future stock
  returns." **Adjacent to the open question but not the same question**: it
  weights past *days inside one formation window*, not *horizons across an
  ensemble*, and it is cross-sectional long-short **stock** momentum with
  no crypto, no cost figure and no multiple-testing correction visible.
  **Testable-here: no.** The byline is a distinct group, but a source that
  does not address ensemble breadth adds nothing to that tally.

- **Frontiers in Blockchain 10.3389/fbloc.2026.1811716 ("Microstructure
  alpha: hierarchical learning and cross-asset transfer in cryptocurrency
  markets") — not read.** The fetch failed with `ECONNREFUSED`. It is
  recorded here as **attempted and unread**, not as a negative, so that a
  future pass does not mistake it for an examined source. A search-result
  snippet suggested it computes round-trip costs on Binance's spot
  schedule, which would make it worth a retry.

- **Meta-observation — twentieth consecutive pass with nothing runnable
  under P1-only, and the first in six with a genuine change to the
  evidence base.** Nothing was run, no arm tested, no trial registered, no
  script written, and the standing answer is unchanged in every clause.
  What changed is that the ensemble-breadth question the operator has been
  sitting on since iteration 49 now has **four** independent groups behind
  it instead of three, an **architecture-matched naive price** (+0.06 for
  one horizon against twelve) instead of only learned-model and
  cross-experiment prices, and an explicit statement of which branch of
  that source applies here. The operator's decision does not move — the
  leave-one-out itself is still unmeasured, still P3-forbidden, and still
  unobtainable from the registry at any price — but the evidence behind it
  is larger and, for the first time in this thread, not dominated by a
  single research group.

## 2026-08-31 — iteration 55 (P1 maintenance; four candidate sources examined, one arrival — and the closest published cousin of this rule reports its numbers on the protected holdout window)

- **coinquant.ai, "Donchian Channel Breakout on Crypto: Backtest vs
  Keltner" (published 3 August 2026, author not shown).** Read by direct
  fetch of the page. This is the closest published cousin of this
  program's rule the loop has located: **long-only, spot BTCUSDT, daily
  bars, no leverage**, a 20-period Donchian channel entering on a close
  above the upper band and exiting below the lower band, with **Binance
  standard 0.1% taker fees included and slippage explicitly 0%**. Window
  **January 2022 to June 2026**. Numbers as printed: total return
  **+36.50%**, max drawdown **38.52%**, **Sharpe 0.38**, **25 trades**,
  win rate **36.0% (9W / 16L)**, profit factor **1.28**. No deflated
  Sharpe, no PBO, no multiple-testing correction, no confidence interval,
  and a single asset over a single window — so it is one uncontrolled
  observation, not a test.
  **Testable-here: no, and for a reason worth recording.** The window it
  covers (2022-01 to 2026-06) overlaps this program's protected data.
  Registry trials end **2025-07-01**; everything after that is either the
  October holdout or shadow-track territory. Reproducing this source's
  window inside the repo would **spend the holdout**, which is
  operator-only under `PRE_HOLDOUT_PROTOCOL.md` and forbidden to the loop
  by iron rule 2. Recorded so that a later pass does not mistake an
  attractive outside comparison for a cheap one.
  Read against it without arithmetic: this program's own BTC/ETH rule
  scores Sharpe **1.1823** (trial 88) on **2018-03-04..2025-07-01**. The
  two are **not commensurable** — different asset count, different exit
  rule, different window, different slippage model, different ensemble
  breadth — and no comparison is claimed. What can be said is narrow:
  a naive single-window Donchian on spot BTC alone, net of taker fees,
  produced a **low** Sharpe over a window this program has never tested.

- **arXiv 2601.20336 — engine-supplied title and actual title do not
  match, for the fourth consecutive iteration.** The search engine listed
  it as "Do Whitepaper Claims Predict Market Behavior? Evidence from
  Cryptocurrency Factor Analysis". The arXiv abstract page reads **"Are
  Whitepaper Claims Reflected in Market Structure? A Contamination-Aware
  Pipeline and a Power-Limited Null"** (Murad Farzulla, v1 28 January
  2026, v6 11 July 2026). It is **not a trading-strategy paper at all**:
  43 whitepapers across 10 semantic categories against seven
  market-structure statistics on hourly 2023-2024 data, reporting a
  **non-significant** alignment (φ = 0.303 dimension-matched, φ = 0.223
  zero-padded). No strategy, no costs, no Sharpe, no drawdown.
  **Testable-here: no.** The engine's "factor analysis" framing was
  invented. Standing rule holds: **summarizer output is a pointer to a
  document, never a reading of it.**

- **A second engine-vs-primary mismatch, in the same pass.** The search
  engine reported the Donchian source above as having a **"45% win
  rate"**. The page prints **"36.0% (9W / 16L)"**, which is internally
  consistent (9/25 = 36.0%). Only the primary figure is recorded. Two
  mismatches in one iteration, five across the last four.

- **arXiv 2508.16378, Qizhao Chen, "Sentiment-Aware Mean-Variance
  Portfolio Optimization for Cryptocurrencies" (v1 22 August 2025, v2 4
  March 2026).** Read from the arXiv abstract page. Combines 14-day RSI
  and SMA with VADER and Google Gemini news sentiment inside a
  "constrained mean-variance optimization framework", compared against a
  momentum strategy, a Bitcoin long-short strategy and an equal-weighted
  portfolio. The abstract states "stronger risk-adjusted returns" but
  prints **no Sharpe ratio, no drawdown percentage, no rebalance
  frequency and no transaction-cost assumption**; long-only vs long-short
  and spot vs derivatives are not stated either. No multiple-testing
  correction. **Testable-here: no** — it requires a news-sentiment feed
  this product does not have, and its architecture is mean-variance
  optimization, the route this program closed on its own evidence (P3)
  and which iteration 54's outside source priced at **-0.59** Sharpe
  against naive equal weighting.

- **arXiv 2602.11708 (AdaptiveTrend) re-encountered for at least the
  fifth time and stays disposed;** arXiv 2603.20319 (implementation risk
  in portfolio backtesting) is already filed three times. Neither is a
  new arrival. **Independence added today: one** (the Donchian cousin),
  and it arrives already blocked by the holdout protocol.

## 2026-09-01 — iteration 56 (P1 maintenance; four candidate sources examined, two arrivals — and the sentence everyone quotes about PBO cannot be verified from its primary source)

- **coinquant.ai, "Best Crypto Trading Strategy in 2026: Backtested and
  Ranked" (published 17 August 2026, author not shown).** Read by direct
  fetch of the page. **A second, different page from the same site as
  iteration 55's Donchian arrival**, and more useful than it: five
  distinct daily rule families on the **same asset, same window, same fee
  assumption**, which is the like-for-like comparison the loop has never
  been able to buy. All are **BTCUSDT, daily candles, January 2021 to
  August 2026, Binance standard taker fees 0.1%**; slippage is not stated
  on this page. As printed:

  | Rank | Strategy | Return | Max DD | Sharpe | Profit factor | Win rate | Trades |
  |---:|---|---:|---:|---:|---:|---:|---:|
  | 1 | BTC Breakout 1D | +118.4% | 48.6% | **0.54** | 1.45 | 50.0% | 24 |
  | 2 | BTC Trend Following 1D | +82.8% | 37.6% | **0.49** | 2.02 | 20.0% | 25 |
  | 3 | BTC EMA Crossover 20/50 1D | +79.2% | 51.6% | **0.48** | 1.55 | 37.5% | 16 |
  | 4 | BTC Mean Reversion 1D | +39.3% | 24.6% | **0.35** | 2.12 | 57.1% | 14 |
  | 5 | BTC Bollinger Mean Reversion 1D | +10.4% | 52.7% | **0.22** | 1.07 | 65.7% | 35 |

  **Testable-here: no**, and for the same reason as iteration 55's arrival —
  the window runs to **August 2026**, past the registry's 2025-07-01
  boundary, so reproducing it in-repo would spend the holdout (iron rule 2).
  What can be read without arithmetic, and is worth recording: across five
  daily BTC rule families on one identical window net of taker fees, the
  **entire Sharpe spread is 0.22 to 0.54**. That is an outside prior on how
  much daily-timeframe *rule selection* on BTC is worth — a third of a
  Sharpe point between the best and worst family — and it is **not
  commensurable** with this program's trial 88 (Sharpe 1.1823, two assets,
  ensemble of four windows, 2018-03-04..2025-07-01, two-sided costs). No
  comparison is claimed. Note also that the same site's 3 August page put a
  20-period Donchian on BTC at **Sharpe 0.38** over Jan 2022–Jun 2026, and
  this page's "BTC Breakout 1D" at **0.54** over Jan 2021–Aug 2026; the two
  are different windows and possibly different rules, and the site does not
  reconcile them.

- **Frontiers in Blockchain, Edson Pindza, "Microstructure alpha:
  hierarchical learning and cross-asset transfer in cryptocurrency markets"
  (published 11 June 2026).** Read by direct fetch of the full article.
  **New arrival.** Minute-level bars, **August 2025 – February 2026**, six
  coins (BTC, ETH, SOL, AVAX, LINK, DOT), both Binance spot and perpetual
  futures, **long-short**, **5-minute rebalancing**, turnover **124–204x
  notional**. Costs are Binance VIP-0: 10 bps per side spot (20 bps
  round-trip), 2 bps maker / 5 bps taker on perps, plus Corwin-Schultz
  half-spread slippage. Its own headline table, as printed:

  | Model | Gross Sharpe | Net Sharpe (spot) | Net Sharpe (futures) |
  |---|---:|---:|---:|
  | AR(1) | 0.43 | **−31.29** | **−10.68** |
  | Momentum (5 min) | 0.43 | −31.29 | −10.68 |
  | OLS (microstructure) | −0.31 | −52.05 | −18.42 |
  | LightGBM | **0.96** | **−50.30** | **−16.98** |

  Max drawdown is **not reported**. **Testable-here: no** — minute bars, a
  long-short book, perpetual futures and a window inside the protected
  holdout are each independently disqualifying under product law and iron
  rule 2. The value is as an outside price on turnover: the **best gross
  signal in the paper (0.96) becomes the worst net one (−50.30)**, i.e. at
  5-minute rebalancing, retail fees consume roughly fifty Sharpe points.
  This is corroboration from outside the program that the daily,
  low-turnover, two-sided-cost design is not a limitation of ambition; it
  is where the arithmetic still permits a positive number. It says nothing
  about whether any daily edge exists.

- **Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest
  Overfitting" (Journal of Computational Finance / JFQA, 2017) —
  retrieved primary, and the sentence the loop wanted is NOT in it.**
  Search engines returned, twice in one pass and in confident phrasing,
  "under CSCV, PBO approaches 1 as N grows, regardless of whether any
  individual configuration has genuine predictive power". That claim bears
  directly on this program's standing conclusion that more searching makes
  gate 3 worse, so it was checked. The **primary abstract**, fetched from
  the publisher's institutional record, reads in full: *"Many investment
  firms and portfolio managers rely on backtests… Standard statistical
  techniques designed to prevent regression overfitting, such as hold-out,
  tend to be unreliable and inaccurate in the context of investment
  backtests. We propose a general framework to assess the probability of
  backtest overfitting (PBO). We illustrate this framework with specific
  generic, model-free and nonparametric implementations… we call these
  implementations combinatorially symmetric cross-validation (CSCV). We
  show that CSCV produces reasonable estimates of PBO for several useful
  examples."* **No claim about N, and no guidance on how the N columns
  should be composed.** The author-hosted full-text PDF is a scanned/binary
  layout the fetch tool cannot read, so the sentence remains **unverified
  against primary** and is **not** recorded as a finding, cited, or used to
  support today's gate-3 measurement. Where this program needs "more
  columns move PBO the wrong way", it uses **its own** experiment-1
  measurement (0.018 → 0.879 → 0.886 at N=21, `PRE_HOLDOUT_PROTOCOL.md`
  §3), not the literature. **This is the sixth engine-vs-primary caution in
  five iterations** — the first five were wrong titles and wrong figures;
  this one is a plausible, widely-repeated sentence that the primary
  source does not contain where the engine implied it does. The standing
  rule tightens by one word: **summarizer output is a pointer to a
  document, never a reading of it, and never a quotation from it.**

- **arXiv 2602.11708 (AdaptiveTrend) re-encountered for at least the sixth
  time and stays disposed**; the Bailey PBO paper is a method reference,
  not a strategy arrival. **Independent arrivals added today: two** (the
  coinquant ranked page and the Frontiers microstructure paper), and both
  arrive blocked — the first by the holdout boundary, the second by product
  law on three separate counts.

## 2026-09-04 — iteration 57 (four candidate sources examined, zero strategy arrivals — and the two most useful sources this pass are about operations, because that is where today's finding landed)

- **Bui & Nguyen, "Systematic Trend-Following with Adaptive Portfolio
  Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets",
  arXiv 2602.11708, submitted 12 February 2026 — seventh re-encounter,
  disposition unchanged.** Abstract re-fetched from the primary arXiv
  record rather than taken from the search summary, per the standing rule.
  As printed: "high-frequency trend-following on **6-hour intervals**",
  "**asymmetric 70/30 long-short** allocation", "monthly adaptive portfolio
  construction", 150+ pairs over 2022-2024, "annualized Sharpe ratio of
  **2.41**, a maximum drawdown of **-12.7%**, and a Calmar ratio of 3.18".
  **Testable-here: no**, on two independent counts of product law —
  6-hour bars are not daily, and a long-short book is not spot long-only.
  Recorded again only so the count of re-encounters stays honest; it is
  the single most persistent search result for this query and it has never
  been admissible.

- **"Exit 0 Is Not Success: Automation Assurance That Verifies Outcomes",
  tonsofskills.com, 13 July 2026 (author not shown) — fetched and read,
  and it describes this program's own live runtime exactly.** As printed:
  a process can "exit zero and produce nothing", which is "a silent
  failure wearing a green badge"; schedulers answer only "did the process
  start and did it return 0?"; the named examples include a heartbeat
  file lacking "a fresh timestamp" and an export writing an "empty stub".
  Its rule, stated explicitly: "An exit code of 0 is **not** business
  success." Its remedy is "independent outcome verification" — register
  the expected output, check the artifact exists and is plausible from
  *outside* the job, and run a "watchdog + watchdog-of-watchdog".
  **Testable-here: not a strategy hypothesis, so it buys no edge**, but it
  is the closest published description of the defect this iteration found
  in `data/runtime/events.jsonl`, where `scripts/run_daily_cycle.cmd`
  has pinged the dead-man switch on the success branch for **36
  consecutive days** while the runtime emitted nothing but a health row.

- **DRo, "Cross-Backtesting Pitfalls", backtrader articles (undated on the
  page) — fetched, and it is a Donchian off-by-one, though not this
  one.** As printed: with `lookback=-1` "the bars to consider will start 1
  bar in the past and the current high/low may break through the channel";
  with `lookback=0` "the current prices will be considered for the
  Donchian Channel. This means that the price will **NEVER** break through
  the upper/lower channel bands." StockCharts and IncredibleCharts exclude
  the current bar; TradingView includes it. **Testable-here: no as an
  edge; yes as a check**, and the check was run — this program's engine
  and `scripts/shadow_signal.py` were already proved equivalent on 138 of
  138 historical windows (commit `2423bf6`), so the channel-indexing
  variant of the bug is not present. Today's defect is a *different*
  off-by-one, one layer up: how many closed candles the live fetch
  returns versus how many the warmup floor demands.

- **"Your CI is green and your pipeline produced nothing" (dev.to) —
  pointer only, not fetched, no claim recorded from it.** Listed so the
  pass is fully enumerated. Under the standing rule the search engine's
  paraphrase of it is not a reading of it, and nothing in this iteration
  rests on it.

- **Arrivals: zero.** Four sources examined, none admissible as a strategy
  hypothesis under product law. Two were nonetheless the most valuable
  sources this loop has fetched in several iterations, because the
  iteration's finding was operational rather than statistical.

## 2026-09-05 — iteration 58 (four candidate sources fetched, two of them new; zero strategy arrivals, and the closest external cousin of this program's own architecture publishes none of the numbers that would decide admissibility)

- **arXiv 2512.08124, "Long-only cryptocurrency portfolio management by
  ranking the assets: a neural network approach", Zijiang Yang, submitted
  2025-12-09 — second encounter (first logged 2026-08-29), disposition
  unchanged.** Abstract re-fetched from the primary arXiv record rather
  than taken from the search summary, per the standing rule. As printed:
  "in each time step, we utilize the neural network to predict the rank of
  the future return of the managed cryptocurrencies and place weights
  accordingly"; backtested on "real daily cryptocurrency market data from
  May, 2020 to Nov, 2023"; "a Sharpe ratio of 1.01 and annualized return
  of 64.26%"; "robust to the increase of transaction fee". Long-only and
  daily are two of four product-law conditions; spot vs derivatives is
  still not stated anywhere in the abstract. No deflated Sharpe, no PBO,
  no multiple-testing correction. **Testable-here: no** — a neural ranking
  family is a new single-market parameter family, which P3 refuses.

- **Buhalterinės apskaitos teorija ir praktika (Accounting Theory and
  Practice), Vol. 33 (2026), Adedeji Daniel Gbadebo, "Momentum Trading in
  Cryptocurrencies: A Comparative Study of Time-Series and Cross-Sectional
  Strategies", published 2026-06-09 — new, and admissibility could not be
  established.** The publisher's landing page was fetched and yields:
  a "multi-horizon exponential moving average (EMA) framework" with
  volatility normalisation, two portfolio structures (time-series and
  cross-sectional), eight major cryptocurrencies, 2020-01-01 to
  2025-10-31. The landing page discloses **none** of the four facts that
  decide admissibility here — long-only vs long-short, spot vs futures,
  rebalancing frequency, transaction-cost assumptions. The full-text PDF
  returned undecodable bytes to the fetch tool and no PDF extractor is
  installed in `.venv`, so the full text was not read. **A "31.96% versus
  14.59%" annual-return pair appeared in the search engine's summary and
  is deliberately NOT recorded as verified** — under the standing rule a
  summariser's paraphrase is not a reading of the source.
  **Testable-here: undetermined**, pending a readable full text.

- **Concretum Group, Carlo Zarattini, Alberto Pagani and Andrea Barbon,
  "Catching Crypto Trends; A Tactical Approach for Bitcoin and Altcoins"
  (2026 per the page footer) — new, and the closest external instance of
  this program's own architecture found in 58 iterations.** Fetched. As
  printed: "Donchian channel-based trend models" with "different lookback
  periods", applied as a rotational portfolio over the "top 20 most liquid
  cryptocurrencies", plus "a simple yet effective portfolio construction
  technique designed to reduce trading costs". Headline: "Sharpe ratio
  above 1.5" and "annualized alpha of 10.8% relative to Bitcoin". Two
  things are worth recording. First, an independent author group reaches
  for the **same architecture this registry runs** — a Donchian ensemble
  across lookbacks on a multi-coin crypto universe — and, second, it
  independently adopts **alpha relative to Bitcoin** as the reporting
  frame, the same move `VS_BUY_AND_HOLD_2026-07-26.md` made when it
  stopped quoting absolute multiples. **No numeric comparison is drawn
  between their 10.8% and this program's 5.4% margin**: the fetched page
  states no sample period, no cost numbers, no bar frequency, no
  long-only/long-short declaration, no drawdown, and no data-snooping or
  multiple-testing caveat, so the two are not commensurable and it would
  be dishonest to line them up. **Testable-here: no** — a 20-coin Donchian
  family is precisely what P3 refuses, and product-law admissibility is
  undetermined from the fetched record. Flagged for the operator only:
  an SSRN version with full method detail may exist; not chased this
  iteration.

- **Streamkap, "Data Freshness Monitoring: How to Know Your Real-Time
  Pipeline Is Actually Real-Time", published 2026-02-25 — fetched, and it
  states today's finding as a general principle.** As printed: "A
  dashboard showing 'real-time' data that is actually 30 minutes old is
  worse than a dashboard that honestly says 'updated hourly.'"; "A
  pipeline can be running, producing events, and writing to a destination,
  yet the data visible to analysts and applications might be minutes or
  even hours behind reality."; and the heartbeat pattern — "a dedicated
  table in your source database that receives a timestamped row at a fixed
  interval… You then measure how long that heartbeat takes to appear at
  the destination." **Testable-here: not a strategy hypothesis, so it buys
  no edge.** Recorded because this repository's dashboard is the first
  case exactly: `/api/gate` reports `days` from wall clock while `cycles`
  has been frozen at 29 for 36 days, and `src/api/page.py` renders the
  first and hides the second. Recorded honestly: the page does **not**
  discuss jobs that exit cleanly while producing nothing, and never uses
  the term dead-man switch — those remain the 2026-07-13 tonsofskills
  source's contribution, not this one's.

- **Pointers not fetched, enumerated so the pass is complete.** (a) Monash
  working paper, Trinh Le and Ummul Ruthbah, "Trend-following Strategies
  for Crypto Investors" — the PDF returned **HTTP 403 Forbidden**; no
  claim is recorded from it and nothing in this iteration rests on it.
  (b) pipecode.ai, "Data Freshness & SLA Monitoring" — the fetch returned
  the page title only, no body; no claim recorded.

- **Arrivals: zero.** Four sources fetched, two of them new to this log,
  none admissible as a strategy hypothesis under product law. The most
  significant of the four is the Concretum piece, and its significance is
  **not** its numbers — which are unusable as published — but that an
  independent group has converged on this program's architecture and its
  benchmark framing without publishing a single one of the six-gate
  quantities.

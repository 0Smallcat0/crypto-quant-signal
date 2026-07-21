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


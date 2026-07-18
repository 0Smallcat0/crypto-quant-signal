# External evidence check — 2026-07-18 web review

Trigger: operator challenge — experiment design had been running on the
2026-07-02 research report alone, with zero fresh external evidence since.
This note records a same-day web review and how it re-orders the Goal P
queue. Search-level evidence only (two key papers are paywalled); each item
is tagged with how solid it looks. This is a research-direction document,
not a pre-registration.

## 1. Funding-rate carry: real edge, dying, and off-limits to this product

- BIS WP 1087 and 2025-26 follow-ups: crypto carry Sharpe ~6.45 (2020-2025
  full sample) fell to ~4.06 in 2024 and **turned negative in 2025**; spot
  ETF introduction compressed carry by ~36% (all venues) to ~97% (CME).
  A 2026 high-frequency panel (26 exchanges, 749 symbols) finds only ~40% of
  top funding-rate opportunities survive costs and spread reversal.
- Product verdict: carry requires perpetual futures — **permanently excluded
  by AGENTS §2.2**. Recorded so nobody re-litigates it: the edge existed,
  is compressing fast, and is structurally unavailable to a spot-long-only
  product. Not a research candidate.

## 2. Volatility-managed exposure: the strongest available hypothesis

- Original evidence (SSRN 3175538, in the 07-02 report): vol targeting cuts
  left tails across 60+ assets; Sharpe gains concentrated in risk assets.
- New in this review: 2024-25 crypto-specific results, including a dynamic
  volatility-managed study with 438 daily-rebalanced OOS days (2024-08 →
  2025-10) reporting Sharpe ≈ 2.08 — methodology-heavy (ML), treat the
  number as directional, not transferable.
- Queue action: **vol-targeted overlay is Goal P experiment 2** (was already
  P2-11; external evidence now corroborates). Spot-compatible: it only
  scales the exposure fraction we already ladder. Monthly-frequency variant
  first (manual-execution compliance), per the original plan.

## 3. Time-series momentum in the ETF era: weaker, not dead

- Multiple 2025-26 sources agree the institutional/ETF era (post 2024-01)
  reduced BTC volatility and trend persistence; the post-halving rally
  (~100% to the 2025-10 ATH) was roughly half of prior cycles.
- Consistent with our own registry: DSR stuck near 0.83-0.86 on a strategy
  family whose evidence base is mostly pre-ETF. The struggle is structural,
  not an implementation bug.
- Grayscale institutional research still endorses momentum signals for
  MANAGING volatility (not for raw alpha) — supporting trend × vol-managed
  composites rather than faster/denser trend rules.

## 4. Cross-sectional momentum: real hypothesis space, needs a bigger universe

- JFQA trend-factor paper and 3,900-coin factor studies: cross-sectional
  momentum/trend factors price the crypto cross-section; three factors
  (market, size, momentum) span most anomalies.
- Blocked on universe size: a two-asset universe (BTC, ETH) has no
  cross-section. Requires the universe-expansion gate (SOL+ candidates each
  passing data-quality and validation) — a mid-term project, queued behind
  experiments 2-3, not before.

## Re-ordered Goal P queue (decision)

1. **Experiment 2 — monthly vol-targeted overlay** on the existing ladder
   (pre-register next; strongest combined internal + external evidence).
2. Experiment 3 candidate — trend × vol-managed composite (design depends on
   experiment 2's result; do NOT pre-commit).
3. Mid-term — universe expansion, then cross-sectional trend factor.
4. Dead ends recorded: carry (structural exclusion), faster/denser MA rules
   (algebraic equivalence + our own trial 5), naive N-day confirmation
   (trial 5 registered negative).

## Sources

- [BIS Working Paper 1087 — Crypto carry](https://www.bis.org/publ/work1087.pdf)
- [CEPR VoxEU — Crypto carry: market segmentation and price distortions](https://cepr.org/voxeu/columns/crypto-carry-market-segmentation-and-price-distortions-digital-asset-markets)
- [MDPI 2026 — Two-tiered structure of funding-rate markets](https://www.mdpi.com/2227-7390/14/2/346)
- [ScienceDirect 2025 — Funding-rate arbitrage risk/return on CEX and DEX](https://www.sciencedirect.com/science/article/pii/S2096720925000818)
- [arXiv 2510.14435 — Cryptocurrency as an investable asset class](https://arxiv.org/html/2510.14435v2)
- [Springer 2026 — Time-series momentum and market timing in Bitcoin](https://link.springer.com/article/10.1057/s41283-026-00234-7) (paywalled; abstract-level only)
- [Grayscale Research — The trend is your friend](https://research.grayscale.com/reports/the-trend-is-your-friend-managing-bitcoins-volatility-with-momentum-signals) (fetch blocked; summary-level only)
- [JFQA — A trend factor for the cross-section of cryptocurrency returns](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC24379148178)
- [Quantitative Finance — Cryptocurrency factor momentum](https://www.tandfonline.com/doi/abs/10.1080/14697688.2023.2269999)
- [AUT working paper — Time-series and cross-sectional momentum in crypto](https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf)
- [Caleb & Brown — Is Bitcoin's four-year cycle broken?](https://calebandbrown.com/blog/is-bitcoins-four-year-cycle-broken/)
- [sciforum — Cryptocurrencies in portfolio diversification](https://sciforum.net/paper/view/23278)

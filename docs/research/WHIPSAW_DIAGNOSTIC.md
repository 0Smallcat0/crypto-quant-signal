# Whipsaw diagnostic — turning-point months vs published thresholds (P2-10)

Date: 2026-07-15 · Data: Binance Spot daily closes, 2017-08 → 2026-06 (month-end sampled)
Method: `scripts/analyze_whipsaw.py` (unit-tested: `tests/scripts/test_analyze_whipsaw.py`)
Status: **pre-registered diagnostic executed — verdict: hysteresis experiments move to the top of Goal P**

## Question

Goulding, Harvey & Mazzoleni ("Breaking Bad Trends", *Financial Analysts
Journal* 2024; 43 futures markets, 1990-2022) quantify when trend following
breaks: a **turning-point month** is a month whose fast momentum sign (1-2
month) disagrees with the slow 12-month momentum sign. Their thresholds:

- **≥ 6** turning-point months in a year → static trend's median return turns negative;
- **≥ 8** → median Sharpe below −1.25.

Does OUR decision universe (BTCUSDT, ETHUSDT daily) live in that regime?
This was pre-registered in the product optimization plan (P2-10) as a
compute-only diagnostic: measure first, change nothing.

## Result

Turning-point months per calendar year, both fast definitions
(1-month / 2-month vs slow 12M), month-end closes:

| Year | BTC 1M | BTC 2M | ETH 1M | ETH 2M | Note |
|------|-------:|-------:|-------:|-------:|------|
| 2018 | 2 | 1 | 1 | 0 | partial (warmup ends 2018-08) |
| 2019 | **8** | **8** | **8** | 7 | **both symbols at/near severe** |
| 2020 | 3 | 3 | 2 | 4 | |
| 2021 | **6** | 3 | 4 | 3 | BTC at warning on 1M only |
| 2022 | 5 | 4 | 3 | 4 | |
| 2023 | **6** | **6** | **7** | **8** | **warning both symbols; ETH severe on 2M** |
| 2024 | 4 | 5 | **6** | 4 | ETH at warning on 1M only |
| 2025 | 4 | 3 | 4 | 4 | |
| 2026 | 2 | 2 | 0 | 1 | partial (through June) |

Median over the seven complete years (2019-2025): **BTC 5 / 4, ETH 4 / 4**
(1M / 2M) — below the warning line in the typical year.

## Verdict (per the pre-registered decision rule)

The rule said: if BTC/ETH land in the ≥6-8 zone, hysteresis-band /
N-day-confirmation experiments go to the top of Goal P; if safely below,
accept the whipsaw budget and spend effort on compliance measurement instead.

The data land **in the zone, intermittently but robustly**: two of seven
complete years (2019, 2023 — 29%) breach the warning threshold on *both*
symbols under *both* fast definitions, and the severe threshold is hit in
2019 (both symbols) and 2023 (ETH). The typical year is fine; the tail year
is exactly the regime the paper says destroys static trend rules.

**Consequence taken:** hysteresis-band / N-day-confirmation variants move to
the **top of the Goal P experiment queue** — every variant pre-registered in
the trial registry and counted toward N, judged by the same six gates as
everything else. Compliance measurement (P2-9) proceeds in parallel; it was
never mutually exclusive. Explicitly NOT done, per the research's negative
results: no MA rule-type swap (algebraically equivalent reweightings) and no
plain lookback shortening (faster signals add bad bets).

Nothing in the live system changes: the observation period's strategy
contract stays frozen; this diagnostic only re-ordered future research.

## Honest limitations

1. **Domain transfer.** The thresholds come from 43 futures markets
   (1990-2022) with zero crypto in sample, at trend-*portfolio* level. We
   borrow their metric, not their regression.
2. **This metric ≠ our ladder churn.** The system's observed ~63 ladder
   changes per symbol-year is a daily-rung statistic and is NOT comparable
   to monthly turning points; this diagnostic measures the trendiness of the
   underlying price path, not the strategy's trade count.
3. **Partial years.** 2018 has five evaluable months (12-month warmup eats
   the rest), 2026 has six; both are flagged, neither drives the verdict.
4. **Definition end-points.** The paper blends 1-2 month fast momentum; we
   report both end-points instead of reproducing the blend. The verdict is
   the same under either, which is why it is trusted.
5. **Single venue.** Binance daily closes only.

## Reproduce

```bash
python -m scripts.analyze_whipsaw                      # full local history
python -m scripts.analyze_whipsaw --candles-dir demo/candles   # bundled sample (2024-01→2026-06)
```

The bundled demo candles cover only the recent, below-threshold stretch —
reproducing the 2019/2023 rows needs the full history via
`scripts/ingest_public_ohlcv.py`.

# Strategy Contract: Large Liquid Trend 15

Status: Core MVP Goal F contract

## Purpose

`Large Liquid Trend 15` is the first active Core MVP strategy.

It converts one closed-candle `FeatureSnapshot` into one auditable strategy decision.
It does not submit orders, choose position size, inspect account state, or bypass risk.

## Inputs

The strategy accepts point-in-time feature snapshots built from closed 15-minute candles.

Required feature values:

- `momentum_return`
- `trend_distance`
- `recent_high_distance`
- `volume_ratio`
- `btc_momentum_return`
- `btc_trend_distance`

All values must be finite `Decimal` values.

## Output

Each decision contains only:

- `symbol`
- `signal`: `LONG` or `FLAT`
- `score`: `Decimal` between `0` and `1`
- `reason_codes`
- `generated_at_bar_close`
- `executable_from_next_bar`

The decision must not contain final quantity, cash amount, virtual order, broker action, or
private API action.

## Score

The score is deterministic and uses contract-fixed components:

| Component | Condition | Weight | Positive reason | Negative reason |
| --- | --- | ---: | --- | --- |
| Momentum | `momentum_return > 0` | `0.25` | `MOMENTUM_POSITIVE` | `MOMENTUM_NOT_POSITIVE` |
| Trend | `trend_distance > 0` | `0.25` | `TREND_POSITIVE` | `TREND_NOT_POSITIVE` |
| Breakout | `recent_high_distance > 0` | `0.20` | `BREAKOUT_CONFIRMED` | `BREAKOUT_NOT_CONFIRMED` |
| Volume | `volume_ratio >= 1` | `0.15` | `VOLUME_CONFIRMED` | `VOLUME_NOT_CONFIRMED` |
| BTC market support | `btc_momentum_return > 0` and `btc_trend_distance > 0` | `0.15` | `BTC_TREND_SUPPORTS` | `BTC_TREND_NOT_SUPPORTIVE` |

Default signal rule:

- `LONG` when `score >= 0.70`
- `FLAT` otherwise
- add `EXIT_SCORE_MET` when `score <= 0.40`

## Default Parameters

Runtime config must be able to provide these values without editing strategy,
feature, or portfolio code:

- `momentum_lookback_candles`: `12`
- `trend_lookback_candles`: `48`
- `breakout_lookback_candles`: `96`
- `volume_lookback_candles`: `96`
- `volatility_lookback_candles`: `48`
- `minimum_entry_score`: `0.70`
- `exit_score`: `0.40`

## Safety Rules

- Only `LONG` and `FLAT` are valid signals.
- Still-open candles are not accepted as strategy input because they must be blocked before
  feature snapshot generation.
- `generated_at_bar_close` is the feature snapshot `as_of` timestamp.
- `executable_from_next_bar` must be after `generated_at_bar_close`.
- The strategy must remain public-data only.
- Portfolio sizing, risk approval, and paper execution belong to later goals.

# Universe Contract

Status: Core MVP Goal D contract

## Purpose

The Core MVP universe defines which public Binance Spot symbols are eligible to reach the feature and strategy layers.

It is an input-safety contract, not a research or optimizer contract.

## Source Boundary

Allowed sources:

- Binance Spot public `exchangeInfo`
- Binance Spot public closed 15-minute candles

Forbidden sources:

- private exchange API
- account balances
- order history
- real order endpoints
- paid or private data

## Eligibility Rules

A symbol is eligible only when all rules are true:

- exchange status is `TRADING`
- spot trading is allowed
- quote asset is `USDT`
- base asset is not a stablecoin
- base asset is not a fiat proxy
- base asset is not a leveraged-token suffix such as `UP`, `DOWN`, `BULL`, or `BEAR`
- symbol has at least `96` closed 15-minute candles in the recent public-data window
- recent quote volume is at least `100000` USDT-equivalent over that same window

Recent quote volume is computed from public candles as:

```text
sum(close_price * base_volume)
```

## Ranking Rule

Eligible symbols are ranked by recent quote volume descending.

If recent quote volume is tied, rank by Binance-native symbol ascending for deterministic output.

## Output

Universe snapshots contain:

- eligible symbols
- UTC creation time
- public data source name

The snapshot must not contain private account data, order data, strategy scores, target weights, or execution actions.

## Core MVP Boundary

This contract does not authorize:

- research lab candidate search
- ML, HMM, GA, or optimizer logic
- private API use
- real orders
- margin, leverage, derivatives, or short exposure

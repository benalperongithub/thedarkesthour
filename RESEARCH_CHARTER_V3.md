# The Darkest Hour research charter — v3 TP-union ranker

## Why v3 exists

The v2 primary book reached a nominal 52.38% positive-trade rate but only ten
of 42 trades reached the structural 2R target. Twelve additional "wins" were
small positive time stops, reducing realized RR to 1.17. Thirty-one of 42
trades were TRXUSDT and only two of five outer folds were positive. V2 failed.

## Frozen v3 primary experiment

- Use the 2% stop / 4% target tapes for `trend_pullback`,
  `compression_breakout` and `impulse_continuation`.
- Deduplicate equal symbol, entry timestamp and direction outcomes before fit.
- Preserve family-presence flags and their count as causal confluence features.
- Predict exactly `exit_reason == TP_SINGLE_EXCHANGE`; a positive time stop is
  not a positive target label.
- Do not use symbol identity or an outcome-derived symbol prior.
- L2 alpha: 10.0; quarterly expanding fit; probability threshold: 0.50.
- A training label is usable only after its exit timestamp.
- Highest predicted TP probability wins simultaneous competition; one global
  position is allowed and exit-bar re-entry is forbidden.
- Primary design scoring window: 2024-01-01 through 2025-03-31 with 2023 as
  initial training history.

The original acceptance gate remains unchanged. This is another design
iteration on already inspected history, not a fresh validation or live-trading
authorization.

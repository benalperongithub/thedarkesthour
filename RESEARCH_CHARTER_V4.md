# TDH V4 — Frozen Cross-Sectional Momentum Test

V1–V3 tested variations of the same event-trigger family. V4 is a genuinely
different hypothesis: liquid cryptocurrency returns contain time-series and
cross-sectional momentum that may survive a one-position, cost-aware book.

This document freezes the primary test before its first result is inspected.
The 2023-01-01 through 2025-04-01 period is still historical design data, not
an unseen holdout. A pass can only justify forward paper trading.

## Frozen primary policy

- Binance perpetual 5-minute bars; causal trailing 24-hour quote-volume floor
  of USD 10 million; at least 20 eligible symbols.
- Decisions only at 00:00, 06:00, 12:00 and 18:00 UTC on weekdays.
- Momentum horizons: 24 hours, 7 days and 30 days, all known at the decision
  close. Entry is the following 5-minute close.
- BTC regime: long only when BTC 7-day and 30-day returns are both positive;
  short only when both are negative; otherwise remain flat.
- A coin must agree with the regime at all three horizons. Select the highest
  (long) or lowest (short) mean cross-sectional percentile rank.
- One global position. No replacement while a trade is open.
- Fixed 2% stop, fixed 4% target (structural 2R), 48-hour time stop,
  worst-case intrabar ordering, 9.5 bps round-trip cost and 10.95% annualized
  funding carry charged conservatively to every position.
- No fitted model, probability threshold, symbol prior or parameter sweep.

## Pre-registered acceptance gate

The primary passes only if all conditions hold after costs:

1. at least 150 resolved trades;
2. win rate at least 50%;
3. profit factor at least 1.50;
4. maximum drawdown no greater than 10R (USD 2,000 at USD 200/R);
5. positive total R for both long and short trades; and
6. positive total R in at least 60% of active calendar quarters.

Frequency and monthly USD are reported, not optimized. Failure does not permit
changing a horizon, threshold, stop or decision clock and calling it V4.

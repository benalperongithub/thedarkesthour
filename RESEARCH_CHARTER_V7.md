# TDH V7 — Perpetual Crowding Reversal

V6 found a gross four-hour reversal effect of roughly 9.34 bps per selected
trade, but it did not clear the 9.5 bps round-trip assumption plus holding cost
and its strongest-coin score was not significant against random selection. V7
tests whether futures-native crowding data can separate the useful reversals
from the false ones.

## Frozen data contract

- Source: checksum-verified official Binance USD-M monthly archives.
- Premium index: completed 1-hour rows, available at `close_time + 1 ms`.
- Funding: a realized rate becomes available only at its `calc_time`.
- Price and liquidity: the existing causally aligned 5-minute perpetual bars.
- Research interval: `2023-03-01 <= entry < 2025-04-01`.
- This history has already been inspected by earlier TDH experiments. Results
  are retrospective outer diagnostics, not a genuinely unseen holdout.

## Frozen primary signal

At each completed UTC hour on weekdays:

1. require prior-24h quote volume of at least USD 10 million and at least 20
   eligible non-BTC symbols;
2. standardize the current premium-index close against the preceding 720 hours,
   excluding the current observation, with a 240-hour minimum;
3. reuse V6's one-hour and four-hour BTC-residual price z-scores;
4. attach the latest realized funding rate and standardize it against the
   preceding 90 funding observations, excluding that observation;
5. positive crowding requires a top-decile cross-sectional premium, premium
   z-score at least +1, and positive BTC-residual price at both horizons;
6. negative crowding uses the exact symmetric rules;
7. trade against crowding: positive is SHORT and negative is LONG;
8. rank candidates by absolute premium z plus 0.5 times absolute one-hour
   residual z plus 0.25 times funding z in the crowding direction;
9. take one global strongest candidate and hold the diagnostic position for a
   fixed four hours before any exit family is considered.

Funding is a continuous ranking feature, not a sign gate. A sign gate would
remove most long candidates when the whole market carries the common positive
funding cap and would introduce a hidden directional choice.

## Costs and primary decision

- Round-trip execution friction: 9.5 bps.
- Funding PnL: the actual realized funding events crossed during each holding
  interval; longs pay positive funding and shorts receive it.
- Primary outcome: four-hour net directional return.

V7 passes only if all checks pass:

1. at least 300 non-overlapping observations;
2. positive mean four-hour net return;
3. net win rate at least 50%;
4. positive net return in at least 60% of active quarters;
5. the strongest score beats the median random qualified candidate;
6. no more than 10% of random simulations equal or beat it;
7. the primary selector beats both a premium-only selector and the frozen V6
   residual-only selector on mean net return.

No stop, target, break-even, partial TP, or trailing policy may be selected
until this entry gate passes. A pass authorizes a separately purged exit
tournament; it does not authorize live trading.

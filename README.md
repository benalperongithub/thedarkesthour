# The Darkest Hour

Single-exchange crypto strategy research package for Phoenix Strategy Suite S1.

This repository owns signal generation, experiment definitions, validation and
reporting. Phoenix owns bar loading, trade simulation, fixed-R exits, costs,
funding, liquidation modelling and the S1 ledger.

The primary research target is deliberately hard:

- structural take-profit / stop-loss: 2R / 1R;
- out-of-sample win rate: at least 50%;
- portfolio maximum drawdown: at most 10% of USD 20,000;
- one global position chosen from the eligible Binance perpetual universe;
- all metrics after fees, slippage, spread stress and funding.

These are acceptance criteria, not promised results. See
[`RESEARCH_CHARTER.md`](RESEARCH_CHARTER.md).

## Integration

The Phoenix checkout and this repository must both be importable:

```bash
export PHOENIX_ROOT=/home/tdw/phx-st6
export TDH_ROOT=/home/tdw/the-darkest-hour
export PYTHONPATH="$TDH_ROOT:$PHOENIX_ROOT"
```

Phoenix resolves the external class from the config:

```yaml
strategy:
  module: darkest_hour.strategies.tdh_v1
  class: TheDarkestHourStrategy
```

The first version contains four frozen signal families. They share the same S1
exit and cost engine and differ only in their causal entry stream:

- `trend_pullback`
- `compression_breakout`
- `failed_breakout`
- `impulse_continuation`

No live-order implementation is included.

## VPS smoke test

After extracting the repository to `/home/tdw/the-darkest-hour`:

```bash
cd /home/tdw/the-darkest-hour
PY=/home/tdw/ThePhoenixStrategySuite/.venv/bin/python
PHX=/home/tdw/phx-st6

PYTHONPATH="$PWD:$PHX" \
  "$PY" -m pytest tests -q

PYTHONPATH="$PWD:$PHX" \
  "$PY" "$PHX/scripts/phx_symbol_sweep.py" \
    --base-config "$PWD/configs/tdh_v1_5m.yaml" \
    --symbols ADAUSDT \
    --set strategy.tdh_family=trend_pullback \
    --set general.start_date=2025-01-01 \
    --set general.end_date=2025-03-31 \
    --out results/smoke_summary.csv \
    --trades-out results/smoke_trades.csv
```

The 77-symbol tournament is deliberately not the first command. The one-symbol
smoke must prove that Phoenix can import the external class, that S1 produces a
trade log and that the configured stop/target geometry is present.

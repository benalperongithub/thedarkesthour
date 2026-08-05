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

## Frozen research sequence

The v1 research calendar is split before scanner selection. The Q1 2025 mini
tournament has already been inspected, so that quarter is part of design—not
an unseen validation period:

- design/discovery: `2023-01-01 <= entry < 2025-04-01`;
- validation: `2025-04-01 <= entry < 2026-01-01`;
- retrospective stress: `2026-01-01 <= entry < 2026-08-01`.

The wider Phoenix programme has already inspected the 2026 market history, so
it is not described as a genuinely unseen holdout. It must not be used to
rescue a failed discovery/internal-validation result.
`build_statefree_tape.py` independently replays every raw signal so candidate
labels are not suppressed by per-symbol position state. `run_causal_scanner.py`
then walks those candidates chronologically, selects only the strongest
simultaneous signal without reading outcomes, and permits one global position.
Its random-selector simulation measures whether the frozen strength score adds
anything beyond having a useful eligible universe.

For the 77-symbol discovery and validation runs, eligibility uses a frozen
USD 10 million trailing-24h approximate quote-volume floor. The value at an
entry is shifted from completed bars, so the filter never reads the entry bar
or later volume.

The v1 raw-strength selector failed inside design. The frozen causal ranker
follow-up is documented in [`RESEARCH_CHARTER_V2.md`](RESEARCH_CHARTER_V2.md).
V2 also failed after its positive time-stop labels produced low realized RR and
severe symbol concentration. The TP-specific, deduplicated family-union v3 is
frozen in [`RESEARCH_CHARTER_V3.md`](RESEARCH_CHARTER_V3.md).

## V4: a new hypothesis, not another V1 threshold

V3 closed the event-trigger/ranker branch after its frozen 50% TP-probability
gate produced no trades and its all-score diagnostic lost money. V4 therefore
tests a separate cross-sectional momentum hypothesis. Its exact policy and
acceptance gate are frozen in `RESEARCH_CHARTER_V4.md`; run it with
`scripts/run_momentum_v4.py`.

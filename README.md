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

V4 failed its frozen gate. V5 does not cherry-pick its positive short side:
it selects direction mode and one of five fixed/managed exit policies inside a
purged nested quarterly procedure. The selection rule is frozen in
`RESEARCH_CHARTER_V5.md` and implemented by `scripts/run_exit_tournament_v5.py`.

V5 also failed, leaving the combined outer book almost exactly at break-even
with excessive drawdown. Before V6 chooses another entry family,
`scripts/audit_data_capabilities.py` inventories whether the local perpetual
dataset contains basis, funding, open-interest, mark/index-price or taker-flow
features rather than silently assuming an OHLCV-only research universe.

The audit found no basis, funding, mark/index price, open interest, or
liquidation history, but all 77 symbols contain quote volume, trade count, and
aggressive taker-buy flow at every stored timeframe. V6 therefore tests a new
short-horizon residual-reversal hypothesis before adding external data. Its
signal and pass/fail rule are frozen in `RESEARCH_CHARTER_V6.md`.

```bash
cd /home/tdw/the-darkest-hour
PY=/home/tdw/ThePhoenixStrategySuite/.venv/bin/python
DATA=/home/tdw/phx-research/data-perp

PYTHONPATH="$PWD" "$PY" scripts/run_residual_reversal_v6.py \
  --data-root "$DATA" \
  --start 2023-03-01 \
  --end 2025-04-01 \
  --simulations 500 \
  --output-root results/v6_residual_reversal1
```

V6 first asks whether the entry has positive 1–4 hour forecasting value after
costs. It intentionally performs no stop, target, partial-profit, or trailing
exit search. Those trade-management choices become eligible for a purged
tournament only if the pre-registered four-hour signal gate passes.

V6 failed narrowly on mean return but materially on time stability and selector
significance. V7 therefore begins with a bounded, checksum-verified download of
official Binance USD-M funding-rate and premium-index archives. Run the smoke
before expanding the date range or symbol universe:

```bash
PYTHONPATH="$PWD" "$PY" scripts/download_v7_basis_data.py \
  --symbols BTCUSDT ETHUSDT SOLUSDT \
  --start-month 2024-01 \
  --end-month 2024-02 \
  --workers 4 \
  --output-root results/v7_data_smoke1
```

The downloader verifies Binance's published SHA-256 for every archive, rejects
unsafe or malformed ZIP members, and records the observed CSV schema. No V7
signal is defined until this data contract passes.

After the bounded smoke passes, the full retrospective acquisition and
normalization commands are:

```bash
DATA=/home/tdw/phx-research/data-perp
V7RAW=results/v7_data_2023_2025
V7NORM=results/v7_normalized_2023_2025

PYTHONPATH="$PWD" "$PY" scripts/download_v7_basis_data.py \
  --symbols-from-data-root "$DATA/binance" \
  --start-month 2023-01 \
  --end-month 2025-03 \
  --workers 8 \
  --progress-every 50 \
  --output-root "$V7RAW"

PYTHONPATH="$PWD" "$PY" scripts/normalize_v7_basis_data.py \
  --manifest "$V7RAW/v7_download_manifest.csv" \
  --output-root "$V7NORM"
```

The frozen crowding hypothesis and its acceptance gate are documented in
`RESEARCH_CHARTER_V7.md`. Downloading and normalizing data does not run the V7
signal or inspect its forward returns.


## Agentic research controller

The current TDH Strategy Lab extends this repository's frozen research sequence
with a deterministic, dual-lane research controller:

- bounded Deep Researcher and Independent Critic advisory roles;
- one causal Codex proposal lane and one adversarial Claude lane;
- registered-family-only validation and controller-only promotion;
- candidate, baseline, and negative-control S1 evaluation;
- robust positive/negative memory and duplicate prevention;
- lane-local quarantine and bounded epoch rollover on frontier exhaustion;
- a proposed Frontier Scout intake layer for continuous, source-grounded
  replenishment without allowing arbitrary executable strategy code.

See [the architecture](docs/architecture.md), [agent contract](AGENTS.md), and
[research queue contract](research/README.md). TDH remains strictly
research-and-backtest-only: no live trading, paper trading, exchange API access,
or S6 execution is part of this controller.

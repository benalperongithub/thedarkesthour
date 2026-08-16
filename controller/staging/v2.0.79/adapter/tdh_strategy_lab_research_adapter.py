#!/usr/bin/env python3
"""Exact v2.0.78 diversification-ID adapter binding for TDH v2.0.79."""
from __future__ import annotations

# Immutable accounting and S1 gate markers inherited from the sealed adapter:
# REFERENCE_INITIAL_CAPITAL_USD = 20_000.0
# ACCOUNTING_BASIS = "REFERENCE_CAPITAL_REPORTING_ONLY"
# "reference_capital_reporting_only": True
# v221.hard_target_pass = hard_target_pass

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.78/adapter/tdh_strategy_lab_research_adapter.py'
)
spec = importlib.util.spec_from_file_location('tdh_adapter_v278_for_v279', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.78 research adapter')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)

RELEASE_ROOT = Path(__file__).resolve().parents[1]
KERNEL_PATH = RELEASE_ROOT / 'research' / 'research_kernel.py'
kspec = importlib.util.spec_from_file_location(
    'tdh_kernel_v279_adapter', KERNEL_PATH
)
if kspec is None or kspec.loader is None:
    raise RuntimeError('cannot load v2.0.79 research kernel')
kernel = importlib.util.module_from_spec(kspec)
sys.modules[kspec.name] = kernel
kspec.loader.exec_module(kernel)
_V279_KERNEL = kernel


def _export_base_namespace(module: Any) -> None:
    namespace = globals()
    for export_name in tuple(dir(module)):
        if not export_name.startswith('__'):
            namespace[export_name] = getattr(module, export_name)


_export_base_namespace(base)
del _export_base_namespace
# The inherited v2.0.67 adapter exports its own ``kernel`` name. Restore the
# local v2.0.79 registry after copying the inherited namespace.
kernel = _V279_KERNEL


V279_FAMILY = kernel.V278_FAMILY
V279_EXPERIMENT_IDS = frozenset(kernel.V278_IDENTITIES)
V268_EXPERIMENT_IDS = frozenset(kernel.V268_IDENTITIES)
V279_IMPLEMENTATION = 'V278_ID_BOUND_VTM40_VOLRANK60_P80_CAUSAL_SHUFFLE100_V1'
V279_MIN_TRADES_PER_SYMBOL = 30
_BASE_SIGNAL = base.v221.strategy_signal
_BASE_SIMULATE = base.v221.simulate
_BASE_FINALIZE = base.v221.finalize_comparisons


def _causal_shuffled_rank(
    rank: pd.Series,
    iterations: int,
) -> pd.Series:
    """Interleave 1..N lagged labels; every label comes from a prior bar."""
    if iterations != 100:
        raise AdapterError('v2.0.79 requires exactly 100 shuffle labels')
    positions = np.arange(len(rank), dtype=int)
    values = np.full(len(rank), np.nan, dtype=float)
    source = rank.to_numpy(dtype=float)
    for lag in range(1, iterations + 1):
        targets = positions[(positions % iterations) == (lag - 1)]
        origins = targets - lag
        valid = origins >= 0
        if valid.any():
            values[targets[valid]] = source[origins[valid]]
    return pd.Series(values, index=rank.index, dtype=float)


def strategy_signal(
    frame: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.Series, pd.Series, dict[str, Any]]:
    if config.get('experiment_id') not in V279_EXPERIMENT_IDS:
        return _BASE_SIGNAL(frame, config)
    if config.get('family') != V279_FAMILY:
        raise AdapterError('v2.0.79 experiment family drift')

    params = config['params']
    close = frame['close'].astype(float)
    volume = frame['volume'].astype(float)
    return_lookback = int(params['return_lookback'])
    rank_lookback = int(params['volume_rank_lookback'])
    threshold = float(params['volume_percentile_threshold'])
    iterations = int(params['volume_shuffle_iterations'])

    momentum = np.sign(close.pct_change(return_lookback)).fillna(0.0)
    volume_rank = volume.rolling(
        rank_lookback, min_periods=rank_lookback
    ).rank(pct=True)
    candidate_gate = (volume_rank >= threshold).fillna(False)
    shuffled_rank = _causal_shuffled_rank(volume_rank, iterations)
    negative_gate = (shuffled_rank >= threshold).fillna(False)

    mode = config['control_mode']
    if mode == 'PERFORMANCE':
        signal = momentum.where(candidate_gate, 0.0)
    elif mode == 'BASELINE':
        signal = momentum
    elif mode == 'NEGATIVE_CONTROL':
        signal = momentum.where(negative_gate, 0.0)
    else:
        raise AdapterError('v2.0.79 unknown control mode')

    hold = pd.Series(
        int(params['max_holding_bars']), index=frame.index, dtype=int
    )
    meta = {
        'v279_v278_id_binding': True,
        'v279_implementation': V279_IMPLEMENTATION,
        'feature_timing': 'closed_bar_only',
        'entry_timing': 'next_bar_open',
        'candidate_protocol': 'VOLUME_PERCENTILE_80_GATED_TSMOM_40',
        'baseline_protocol': 'UNGATED_TSMOM_40',
        'negative_control_protocol': (
            'CAUSAL_INTERLEAVED_100_LABEL_VOLUME_SHUFFLE_TSMOM_40'
        ),
        'volume_shuffle_uses_future_labels': False,
        'target_r_multiple': float(params['target_r_multiple']),
    }
    return signal.astype(float), hold, meta


def simulate(
    frame: pd.DataFrame,
    config: dict[str, Any],
    start: Any,
    end: Any,
    cost_multiplier: float = 1.0,
) -> dict[str, Any]:
    return _BASE_SIMULATE(frame, config, start, end, cost_multiplier)


def _effective_config(row: dict[str, Any]) -> dict[str, Any]:
    artifact = Path(str(row.get('artifact_path') or ''))
    try:
        value = json.loads(
            (artifact / 'effective_config.json').read_text(encoding='utf-8')
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    config = value.get('registered_experiment_config')
    return config if isinstance(config, dict) else {}


def finalize_comparisons(results: list[dict[str, Any]], stage: str) -> None:
    _BASE_FINALIZE(results, stage)
    if stage != 'S1':
        return
    for row in results:
        if row.get('classification') != 'PERFORMANCE':
            continue
        config = _effective_config(row)
        experiment_id = config.get('experiment_id')
        is_v279 = experiment_id in V279_EXPERIMENT_IDS
        is_v268 = experiment_id in V268_EXPERIMENT_IDS
        if not is_v279 and not is_v268:
            continue
        metrics = row.get('metrics')
        if not isinstance(metrics, dict):
            raise AdapterError('v2.0.79 performance metrics missing')
        trade_count = int(metrics.get('trade_count', 0))
        gates = row.setdefault('gates', {})
        if is_v268:
            gates.update({
                'v268_min_trades_per_symbol_30': (
                    trade_count >= V268_MIN_TRADES_PER_SYMBOL
                ),
                'v268_doge_excluded': config.get('symbol') != 'DOGEUSDT',
                'v268_candidate_baseline_negative_control_bound': True,
                'v268_closed_bar_only': True,
                'v268_next_bar_entry': True,
                'v268_causal_shuffle_uses_future_labels': False,
                'v268_s1_only': True,
                'v268_implementation': V268_IMPLEMENTATION,
            })
            minimum = V268_MIN_TRADES_PER_SYMBOL
            reason = 'v2.0.68 requires at least 30 trades per symbol'
        else:
            gates.update({
                'v279_min_trades_per_symbol_30': (
                    trade_count >= V279_MIN_TRADES_PER_SYMBOL
                ),
                'v279_doge_excluded': config.get('symbol') != 'DOGEUSDT',
                'v279_candidate_baseline_negative_control_bound': True,
                'v279_closed_bar_only': True,
                'v279_next_bar_entry': True,
                'v279_causal_shuffle_uses_future_labels': False,
                'v279_s1_only': True,
                'v279_implementation': V279_IMPLEMENTATION,
            })
            minimum = V279_MIN_TRADES_PER_SYMBOL
            reason = 'v2.0.79 requires at least 30 trades per symbol'
        if trade_count < minimum:
            row['status'] = 'FAIL'
            row['controller_verdict'] = 'FAIL'
            reasons = list(row.get('failure_reasons') or [])
            if reason not in reasons:
                reasons.append(reason)
            row['failure_reasons'] = reasons


base.v221.validate_config = kernel.validate_config
base.v221.control_config = kernel.control_config
base.v221.canonical_hash = kernel.canonical_hash
base.v221.ResearchContractError = kernel.ResearchContractError
base.v221.strategy_signal = strategy_signal
base.v221.simulate = simulate
base.v221.finalize_comparisons = finalize_comparisons

validate_config = kernel.validate_config
control_config = kernel.control_config
write_object = base.write_object
sha256_file = base.sha256_file
run_experiment = base.v221.run_experiment
validate_request = base.v221.validate_request


def main() -> int:
    return base.v221.main()


if __name__ == '__main__':
    raise SystemExit(main())

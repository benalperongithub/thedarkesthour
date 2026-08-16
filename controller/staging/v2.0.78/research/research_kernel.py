#!/usr/bin/env python3
"""Sealed four-coin VOLUME_TSMOM diversification overlay for TDH v2.0.78."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.77/research/research_kernel.py'
)
spec = importlib.util.spec_from_file_location('tdh_kernel_v277_for_v278', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.77 research kernel')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)


def _export_base_namespace(module: Any) -> None:
    namespace = globals()
    for export_name in tuple(dir(module)):
        if not export_name.startswith('__'):
            namespace[export_name] = getattr(module, export_name)


_export_base_namespace(base)
del _export_base_namespace


ROOT = Path(__file__).resolve().parent
SEEDS_PATH = ROOT / 'v278-volume-tsmom-diversification-bridge-v1.jsonl'
V278_REGISTRY_VERSION = 'tdh-v278-volume-tsmom-diversification-bridge-v1'
V278_FAMILY = 'VOLUME_TSMOM'
V278_SOURCE_RUN_ID = 'tdh-strategy-lab-v2-20260815T235506Z'
V278_SOURCE_PROPOSAL_SHA256 = (
    '2069e9cda9a547673dfaca423a56ae18e1876fe3ce25cfe7f64f7290822eec9d'
)
V278_SOURCE_DECISION_SHA256 = (
    '0bb3daa9128445315ff12c63674006af7660cce0098c08b7ddc1282e88969b01'
)
V278_SOURCE_PACKET_SHA256 = (
    '00fb1e774ed428c662ec534cd3b476ac5c173fb451021d0748fc6761d2bd2419'
)
V278_SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT')
V278_IDENTITIES = {
    f'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-{timeframe.upper()}': timeframe
    for timeframe in ('1h', '4h', '1d')
}
V278_PARAMS = {
    'return_lookback': 40,
    'volume_rank_lookback': 60,
    'volume_percentile_threshold': 0.80,
    'volume_shuffle_iterations': 100,
    'volume_shuffle_scheme': 'CAUSAL_INTERLEAVED_LAGS_1_TO_100',
    'max_holding_bars': 10,
    'target_r_multiple': 2.0,
    'feature_timing': 'closed_bar_only',
}
BASE_REGISTRY = base.registry


def _fail(message: str) -> None:
    raise ResearchContractError(
        f'v2.0.78 VOLUME_TSMOM diversification registry: {message}'
    )


def _rows() -> list[dict[str, Any]]:
    if not SEEDS_PATH.is_file() or SEEDS_PATH.is_symlink():
        _fail('seed file missing or is a symlink')
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        SEEDS_PATH.read_text(encoding='utf-8').splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ResearchContractError(
                f'v2.0.78 seed line {line_number} invalid: {exc}'
            ) from exc
        if not isinstance(value, dict):
            _fail('seed must be an object')
        rows.append(value)
    if len(rows) != len(V278_IDENTITIES):
        _fail('exactly three bounded timeframe seeds are required')
    return rows


def _validate_row(row: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        'registry_id', 'experiment_id', 'family_id', 'timeframe', 'universe',
        'evidence_score', 'research_priority', 'params', 'controller_admission',
    }
    if set(row) != expected_fields:
        _fail('seed fields differ from sealed schema')
    experiment_id = row.get('experiment_id')
    if experiment_id not in V278_IDENTITIES:
        _fail('experiment identity is not controller-approved')
    timeframe = V278_IDENTITIES[experiment_id]
    if (
        row.get('registry_id') != V278_REGISTRY_VERSION
        or row.get('family_id') != V278_FAMILY
        or row.get('timeframe') != timeframe
        or tuple(row.get('universe') or ()) != V278_SYMBOLS
        or row.get('evidence_score') != 86
        or row.get('research_priority') != 'critical'
        or row.get('params') != V278_PARAMS
    ):
        _fail('seed identity or parameters drift')
    if row.get('controller_admission') != {
        'review_version': 'tdh-controller-admission-v278',
        'status': 'CONTROLLER_APPROVED_SEALED_REGISTRY',
        'source_run_id': V278_SOURCE_RUN_ID,
        'source_hypothesis_id': 'TDH-SCOUT-000001',
        'source_proposal_sha256': V278_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V278_SOURCE_DECISION_SHA256,
        'source_packet_sha256': V278_SOURCE_PACKET_SHA256,
        'reviewed_family': V278_FAMILY,
        'candidate': 'VOLUME_PERCENTILE_80_GATED_TSMOM_40',
        'baseline': 'UNGATED_TSMOM_40',
        'negative_control': 'CAUSAL_100_LABEL_VOLUME_SHUFFLE_TSMOM_40',
        'excluded_symbol': 'DOGEUSDT',
        'primary_change': 'UNIVERSE_COUNT_3_TO_4',
        'min_unique_coins_required': 4,
        'max_single_coin_contribution_pct': 40,
        'min_expectancy_r_threshold': 0.05,
        'deferred_return_lookbacks': [10, 20, 50],
        'deferred_volume_lookbacks': [20, 50, 100],
        'single_material_axis': True,
        'contains_executable_code': False,
        'raw_proposal_executed': False,
        'controller_only_promotion': True,
        's1_only': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }:
        _fail('controller admission provenance drift')
    value = dict(row)
    value['effective_timeframe'] = timeframe
    return value


def registry() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    families, historical = BASE_REGISTRY()
    if V278_FAMILY not in families:
        _fail('registered executable family is missing')
    experiments = dict(historical)
    observed: set[str] = set()
    for raw in _rows():
        row = _validate_row(raw)
        experiment_id = row['experiment_id']
        if experiment_id in observed or experiment_id in experiments:
            _fail('duplicate experiment identity')
        observed.add(experiment_id)
        experiments[experiment_id] = row
    if observed != set(V278_IDENTITIES):
        _fail('approved identity set is incomplete')
    return dict(families), experiments


for function_name in (
    'validate_config', 'performance_config', 'control_config', 'select_context'
):
    function = getattr(base, function_name)
    function.__globals__['registry'] = registry

base.registry = registry
validate_config = base.validate_config
performance_config = base.performance_config
control_config = base.control_config
select_context = base.select_context


def v278_registry_status() -> dict[str, Any]:
    _, experiments = registry()
    rows = [
        row for row in experiments.values()
        if row.get('registry_id') == V278_REGISTRY_VERSION
    ]
    return {
        'version': V278_REGISTRY_VERSION,
        'status': 'ACTIVE_SEALED_S1_DIVERSIFICATION_BRIDGE',
        'source_proposal_sha256': V278_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V278_SOURCE_DECISION_SHA256,
        'source_packet_sha256': V278_SOURCE_PACKET_SHA256,
        'approved_seed_count': len(rows),
        'family': V278_FAMILY,
        'symbols': list(V278_SYMBOLS),
        'timeframes': sorted(row['effective_timeframe'] for row in rows),
        'primary_change': 'UNIVERSE_COUNT_3_TO_4',
        'candidate_baseline_negative_control_bound': True,
        'deferred_parameter_axes_remain_closed': True,
        'raw_proposal_executed': False,
        'controller_only_promotion': True,
        's1_only': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }

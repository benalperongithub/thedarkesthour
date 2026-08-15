#!/usr/bin/env python3
"""Sealed VOLUME_TSMOM ablation registry overlay for TDH v2.0.68."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.67/research/research_kernel.py'
)
spec = importlib.util.spec_from_file_location('tdh_kernel_v267_for_v268', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.67 research kernel')
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
SEEDS_PATH = ROOT / 'v268-volume-tsmom-ablation-seeds-v1.jsonl'
V268_REGISTRY_VERSION = 'tdh-v268-volume-tsmom-ablation-seeds-v1'
V268_FAMILY = 'VOLUME_TSMOM'
V268_SOURCE_RUN_ID = 'tdh-strategy-lab-v2-20260815T170425Z'
V268_SOURCE_PROPOSAL_SHA256 = (
    '0878bd689f1e14f310c3a0f697d6b5ecf8e25308f04bab0a487af34090ece0c8'
)
V268_SOURCE_DECISION_SHA256 = (
    '92b6929ab84f97b4f451d283110d2f525d623fd084bafff268e725b5a871329a'
)
V268_SUPERSEDES_DECISION_SHA256 = (
    '3055bca68d1b6fab32b15a454f8bc320c99af5c85466f64367d9345ae0dfe99b'
)
V268_SYMBOLS = ('BTCUSDT', 'XRPUSDT', 'SOLUSDT')
V268_IDENTITIES = {
    f'TDH-SCOUT-000001-VTM-VOL80-NODOGE-{timeframe.upper()}': timeframe
    for timeframe in ('1h', '4h', '1d')
}
V268_PARAMS = {
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
    raise ResearchContractError(f'v2.0.68 VOLUME_TSMOM registry: {message}')


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
                f'v2.0.68 seed line {line_number} invalid: {exc}'
            ) from exc
        if not isinstance(value, dict):
            _fail('seed must be an object')
        rows.append(value)
    if len(rows) != len(V268_IDENTITIES):
        _fail('exactly three bounded seeds are required')
    return rows


def _validate_row(row: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        'registry_id', 'experiment_id', 'family_id', 'timeframe', 'universe',
        'evidence_score', 'research_priority', 'params', 'controller_admission',
    }
    if set(row) != expected_fields:
        _fail('seed fields differ from sealed schema')
    experiment_id = row.get('experiment_id')
    if experiment_id not in V268_IDENTITIES:
        _fail('experiment identity is not controller-approved')
    timeframe = V268_IDENTITIES[experiment_id]
    if (
        row.get('registry_id') != V268_REGISTRY_VERSION
        or row.get('family_id') != V268_FAMILY
        or row.get('timeframe') != timeframe
        or tuple(row.get('universe') or ()) != V268_SYMBOLS
        or row.get('evidence_score') != 82
        or row.get('research_priority') != 'critical'
        or row.get('params') != V268_PARAMS
    ):
        _fail('seed identity or parameters drift')
    if row.get('controller_admission') != {
        'review_version': 'tdh-controller-admission-v268',
        'status': 'CONTROLLER_APPROVED_SEALED_REGISTRY',
        'source_run_id': V268_SOURCE_RUN_ID,
        'source_hypothesis_id': 'TDH-SCOUT-000001',
        'source_proposal_sha256': V268_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V268_SOURCE_DECISION_SHA256,
        'supersedes_decision_sha256': V268_SUPERSEDES_DECISION_SHA256,
        'reviewed_family': V268_FAMILY,
        'candidate': 'VOLUME_PERCENTILE_80_GATED_TSMOM_40',
        'baseline': 'UNGATED_TSMOM_40',
        'negative_control': 'CAUSAL_100_LABEL_VOLUME_SHUFFLE_TSMOM_40',
        'excluded_symbol': 'DOGEUSDT',
        'min_trades_per_symbol': 30,
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
    if V268_FAMILY not in families:
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
    if observed != set(V268_IDENTITIES):
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


def v268_registry_status() -> dict[str, Any]:
    _, experiments = registry()
    rows = [
        row for row in experiments.values()
        if row.get('registry_id') == V268_REGISTRY_VERSION
    ]
    return {
        'version': V268_REGISTRY_VERSION,
        'status': 'ACTIVE_SEALED_S1_ABLATION',
        'source_proposal_sha256': V268_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V268_SOURCE_DECISION_SHA256,
        'approved_seed_count': len(rows),
        'family': V268_FAMILY,
        'symbols': list(V268_SYMBOLS),
        'timeframes': sorted(row['effective_timeframe'] for row in rows),
        'candidate_baseline_negative_control_bound': True,
        'causal_volume_shuffle_only': True,
        'raw_proposal_executed': False,
        'controller_only_promotion': True,
        's1_only': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }

#!/usr/bin/env python3
"""Bounded RSI-gated reversion registry overlay for TDH v2.0.61."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.60/research/research_kernel.py'
)
spec = importlib.util.spec_from_file_location('tdh_kernel_v260_for_v261', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.60 research kernel')
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
SEEDS_PATH = ROOT / 'rsi-gated-reversion-seeds-v1.jsonl'
V261_REGISTRY_VERSION = 'tdh-rsi-gated-reversion-packet-a-v1'
V261_FAMILY = 'RSI_GATED_REVERSION'
V261_EXPERIMENT_ID = 'TDH-VIDEO-RSI-GATED-REV-PACKET-A-15M'
V261_SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')
V261_PARAMS = {
    'rsi_period': 14,
    'long_threshold': 25,
    'short_threshold': 75,
    'adx_period': 14,
    'adx_max': 20,
    'atr_period': 14,
    'stop_atr': 1.0,
    'target_r_multiple': 2.0,
    'max_holding_bars': 24,
    'regime_gate': 'ADX_LOW_TREND',
    'feature_timing': 'closed_bar_only',
}
BASE_REGISTRY = base.registry
SUPPORTED_FAMILIES = frozenset(set(base.SUPPORTED_FAMILIES) | {V261_FAMILY})


def _fail(message: str) -> None:
    raise ResearchContractError(f'v2.0.61 RSI Paket-A registry: {message}')


def _row() -> dict[str, Any]:
    if not SEEDS_PATH.is_file() or SEEDS_PATH.is_symlink():
        _fail('seed file missing or is a symlink')
    lines = [line for line in SEEDS_PATH.read_text(encoding='utf-8').splitlines()
             if line.strip()]
    if len(lines) != 1:
        _fail('exactly one bounded seed is required')
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise ResearchContractError(f'v2.0.61 seed JSON invalid: {exc}') from exc
    if not isinstance(value, dict):
        _fail('seed must be an object')
    expected_fields = {
        'registry_id', 'experiment_id', 'family_id', 'timeframe', 'universe',
        'evidence_score', 'research_priority', 'params', 'controller_admission',
    }
    if set(value) != expected_fields:
        _fail('seed fields differ from sealed schema')
    if (
        value.get('registry_id') != V261_REGISTRY_VERSION
        or value.get('experiment_id') != V261_EXPERIMENT_ID
        or value.get('family_id') != V261_FAMILY
        or value.get('timeframe') != '15m'
        or tuple(value.get('universe') or ()) != V261_SYMBOLS
        or value.get('evidence_score') != 90
        or value.get('research_priority') != 'critical'
        or value.get('params') != V261_PARAMS
    ):
        _fail('sealed seed identity or parameters drift')
    if value.get('controller_admission') != {
        'review_version': 'tdh-controller-admission-v261',
        'status': 'CONTROLLER_APPROVED_SEALED_REGISTRY',
        'source_document': (
            'research/intake/pending/'
            'TDH_Video_Stratejileri_Research_Intake_2026-08-14.md'
        ),
        'packet': 'PAKET_A_ONLY',
        'candidate': 'RSI_14_25_75_WITH_ADX_LE_20',
        'baseline': 'RSI_14_25_75_WITHOUT_ADX_GATE',
        'negative_control': 'INVERTED_RSI_WITH_ADX_LE_20',
        'contains_executable_code': False,
        'controller_only_promotion': True,
        's1_only': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }:
        _fail('controller admission provenance drift')
    row = dict(value)
    row['effective_timeframe'] = '15m'
    return row


def _card() -> dict[str, Any]:
    return {
        'family_id': V261_FAMILY,
        'name': 'RSI Gated Reversion Paket A',
        'bucket': 'bounded_mean_reversion',
        'evidence_score': 90,
        'research_priority': 'critical',
        'required_data': ['ohlcv'],
        'thesis': (
            'Test whether a closed-bar ADX low-trend gate improves a fixed '
            'RSI(14) 25/75 mean-reversion baseline after costs.'
        ),
        'main_failure_modes': [
            'NO_INCREMENTAL_GATE_EDGE',
            'TREND_REGIME_FRAGILITY',
            'LOW_TRADE_DENSITY',
        ],
    }


def registry() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    families, experiments = BASE_REGISTRY()
    families = dict(families)
    experiments = dict(experiments)
    if V261_FAMILY in families or V261_EXPERIMENT_ID in experiments:
        _fail('duplicate family or experiment identity')
    families[V261_FAMILY] = _card()
    experiments[V261_EXPERIMENT_ID] = _row()
    return families, experiments


for function_name in (
    'validate_config', 'performance_config', 'control_config', 'select_context'
):
    function = getattr(base, function_name)
    function.__globals__['registry'] = registry
    function.__globals__['SUPPORTED_FAMILIES'] = SUPPORTED_FAMILIES

base.registry = registry
base.SUPPORTED_FAMILIES = SUPPORTED_FAMILIES
validate_config = base.validate_config
performance_config = base.performance_config
control_config = base.control_config
select_context = base.select_context


def v261_registry_status() -> dict[str, Any]:
    families, experiments = registry()
    return {
        'version': V261_REGISTRY_VERSION,
        'status': 'ACTIVE_BOUNDED_PACKET_A',
        'family_registered': V261_FAMILY in families,
        'experiment_registered': V261_EXPERIMENT_ID in experiments,
        'seed_count': 1,
        'symbols': list(V261_SYMBOLS),
        'timeframes': ['15m'],
        'candidate_baseline_negative_control_bound': True,
        'closed_bar_only': True,
        's1_only': True,
        'controller_only_promotion': True,
        'untrusted_scout_text_executable': False,
        'trading_actions': False,
        'exchange_api_access': False,
    }

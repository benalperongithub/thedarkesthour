#!/usr/bin/env python3
"""Sealed controller-reviewed Scout seed overlay for TDH v2.0.58."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.57/research/research_kernel.py'
)
spec = importlib.util.spec_from_file_location('tdh_kernel_v257_for_v258', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.57 research kernel')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
for name in dir(base):
    if not name.startswith('__'):
        globals()[name] = getattr(base, name)


ROOT = Path(__file__).resolve().parent
APPROVED_SEEDS_PATH = ROOT / 'frontier-scout-approved-seeds-v1.jsonl'
V258_REGISTRY_VERSION = 'tdh-controller-reviewed-scout-seeds-v1'
SOURCE_HYPOTHESIS_ID = 'TDH-SCOUT-000001'
SOURCE_PROPOSAL_SHA256 = (
    '9a7b8893dc11cc9ae86cb5ef85da2694c1041b589a184c2cdda14351c88308b6'
)
FULL_UNIVERSE = ('BTCUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT')
NO_DOGE_UNIVERSE = ('BTCUSDT', 'XRPUSDT', 'SOLUSDT')
APPROVED_IDENTITIES = {
    f'TDH-SCOUT-000001-VTM-FULL-{tf.upper()}': (tf, FULL_UNIVERSE)
    for tf in ('1h', '4h', '1d')
} | {
    f'TDH-SCOUT-000001-VTM-NODOGE-{tf.upper()}': (tf, NO_DOGE_UNIVERSE)
    for tf in ('1h', '4h', '1d')
}
BASE_REGISTRY = base.registry


def _fail(message: str) -> None:
    raise ResearchContractError(f'v2.0.58 approved Scout registry: {message}')


def _approved_rows() -> list[dict[str, Any]]:
    if not APPROVED_SEEDS_PATH.is_file() or APPROVED_SEEDS_PATH.is_symlink():
        _fail('seed file missing or is a symlink')
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        APPROVED_SEEDS_PATH.read_text(encoding='utf-8').splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ResearchContractError(
                f'v2.0.58 approved Scout registry line {line_number}: {exc}'
            ) from exc
        if not isinstance(row, dict):
            _fail('entry must be an object')
        rows.append(row)
    if len(rows) != len(APPROVED_IDENTITIES):
        _fail('exactly six reviewed ablation seeds are required')
    return rows


def _validate_approved_row(row: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        'registry_id', 'experiment_id', 'family_id', 'timeframe', 'universe',
        'evidence_score', 'research_priority', 'params', 'controller_admission',
    }
    if set(row) != expected_fields:
        _fail('entry fields differ from sealed schema')
    experiment_id = row.get('experiment_id')
    if experiment_id not in APPROVED_IDENTITIES:
        _fail('experiment identity is not controller-approved')
    timeframe, universe = APPROVED_IDENTITIES[experiment_id]
    if (
        row.get('registry_id') != V258_REGISTRY_VERSION
        or row.get('family_id') != 'VOLUME_TSMOM'
        or row.get('timeframe') != timeframe
        or tuple(row.get('universe') or ()) != universe
        or row.get('evidence_score') != 82
        or row.get('research_priority') != 'high'
    ):
        _fail('registered experiment identity drift')
    if row.get('params') != {
        'return_lookback': 10,
        'volume_lookback': 20,
        'volume_weight': 'ratio',
    }:
        _fail('bounded VOLUME_TSMOM parameters drift')
    admission = row.get('controller_admission')
    if admission != {
        'review_version': 'tdh-controller-admission-v258',
        'status': 'CONTROLLER_APPROVED_SEALED_REGISTRY',
        'source_hypothesis_id': SOURCE_HYPOTHESIS_ID,
        'source_proposal_sha256': SOURCE_PROPOSAL_SHA256,
        'reviewed_family': 'VOLUME_TSMOM',
        'contains_executable_code': False,
        'controller_only_promotion': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }:
        _fail('controller admission provenance drift')
    value = dict(row)
    value['effective_timeframe'] = timeframe
    return value


def registry() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    families, historical = BASE_REGISTRY()
    if 'VOLUME_TSMOM' not in families:
        _fail('reviewed family is not already executable')
    experiments = dict(historical)
    observed: set[str] = set()
    for raw in _approved_rows():
        row = _validate_approved_row(raw)
        experiment_id = row['experiment_id']
        if experiment_id in observed or experiment_id in experiments:
            _fail('duplicate experiment identity')
        observed.add(experiment_id)
        experiments[experiment_id] = row
    if observed != set(APPROVED_IDENTITIES):
        _fail('approved identity set is incomplete')
    return dict(families), experiments


# Inherited functions resolve their defining module globals. Rebind only the
# registry name used by deterministic selection and config validation.
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


def approved_registry_status() -> dict[str, Any]:
    _, experiments = registry()
    rows = [
        row for row in experiments.values()
        if row.get('registry_id') == V258_REGISTRY_VERSION
    ]
    return {
        'version': V258_REGISTRY_VERSION,
        'status': 'ACTIVE_CONTROLLER_REVIEWED_SEALED_REGISTRY',
        'source_hypothesis_id': SOURCE_HYPOTHESIS_ID,
        'source_proposal_sha256': SOURCE_PROPOSAL_SHA256,
        'approved_seed_count': len(rows),
        'families': sorted({row['family_id'] for row in rows}),
        'timeframes': sorted({row['effective_timeframe'] for row in rows}),
        'untrusted_scout_text_executable': False,
        'new_family_auto_admitted': False,
        'controller_only_promotion': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }

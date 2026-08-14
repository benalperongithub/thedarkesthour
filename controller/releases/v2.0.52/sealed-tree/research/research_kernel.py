#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

BASE = Path('/srv/tdh-collab/controller/strategy-lab-v2/v2.0.38/research/research_kernel.py')
spec = importlib.util.spec_from_file_location('tdh_kernel_v238_mkbase', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.38 kernel')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
for name in dir(base):
    if not name.startswith('__'):
        globals()[name] = getattr(base, name)

ROOT = Path(__file__).resolve().parent
METE_SEEDS_PATH = ROOT / 'mete-kaplan-seeds-v1.jsonl'
METE_SOURCE_PACK_PATH = ROOT / 'TDH_Mete_Kaplan_STR_LIQ_IMB_Research_Pack_v1.md'
METE_REGISTRY_VERSION = 'MK_STR_LIQ_IMB_v1'
METE_EXECUTABLE_FAMILIES = frozenset({'MK_A_LIQ_IMB','MK_B_STR_IMB','MK_C_STR_LIQ_IMB'})
METE_EXECUTABLE_SYMBOLS = frozenset({'BTCUSDT','ETHUSDT','SOLUSDT'})
SUPPORTED_FAMILIES = frozenset(set(base.SUPPORTED_FAMILIES) | set(METE_EXECUTABLE_FAMILIES))
BASE_REGISTRY = base.registry


def _cards() -> dict[str, dict[str, Any]]:
    return {
        'MK_A_LIQ_IMB': {'family_id':'MK_A_LIQ_IMB','name':'Mete Kaplan LIQ + IMB','bucket':'smc_price_action','evidence_score':94,'research_priority':'high','required_data':['ohlcv'],'thesis':'Test liquidity sweep/reclaim plus imbalance retest.','main_failure_modes':['NO_INCREMENTAL_FAMILY_EDGE','DENSITY_FAILURE']},
        'MK_B_STR_IMB': {'family_id':'MK_B_STR_IMB','name':'Mete Kaplan STR + IMB','bucket':'smc_price_action','evidence_score':94,'research_priority':'high','required_data':['ohlcv'],'thesis':'Test strong structure break plus imbalance retest.','main_failure_modes':['NO_INCREMENTAL_FAMILY_EDGE','SIGNAL_PRECISION_CEILING']},
        'MK_C_STR_LIQ_IMB': {'family_id':'MK_C_STR_LIQ_IMB','name':'Mete Kaplan STR + LIQ + IMB','bucket':'smc_price_action','evidence_score':98,'research_priority':'critical','required_data':['ohlcv'],'thesis':'Test sweep then strong break then imbalance retest.','main_failure_modes':['NO_INCREMENTAL_FAMILY_EDGE','DENSITY_FAILURE']},
    }


def _rows() -> list[dict[str, Any]]:
    rows=[]
    for line in METE_SEEDS_PATH.read_text(encoding='utf-8').splitlines():
        if line.strip():
            value=json.loads(line)
            if isinstance(value,dict): rows.append(value)
    if len(rows) != 12:
        raise ResearchContractError('Mete executable registry must contain 12 seeds')
    return rows


def registry() -> tuple[dict[str,dict[str,Any]],dict[str,dict[str,Any]]]:
    families, experiments = BASE_REGISTRY(); families=dict(families); experiments=dict(experiments); families.update(_cards())
    for row in _rows():
        family=row.get('family_id'); eid=row.get('experiment_id'); tf=effective_timeframe(row); universe=row.get('universe'); params=row.get('params')
        if family not in METE_EXECUTABLE_FAMILIES or tf != '5m': raise ResearchContractError('Mete executable identity invalid')
        if not isinstance(eid,str) or eid in experiments: raise ResearchContractError('Mete experiment identity invalid')
        if set(universe or []) != set(METE_EXECUTABLE_SYMBOLS): raise ResearchContractError('Mete universe invalid')
        if not isinstance(params,dict) or params.get('timeframe') != '5m' or params.get('profile') not in {'BASE','LOOSE','STRICT','CONFIRM'}: raise ResearchContractError('Mete profile invalid')
        value=dict(row); value['effective_timeframe']='5m'; experiments[eid]=value
    return families, experiments


def validate_config(raw: Any, *, allow_legacy: bool=False) -> dict[str,Any]:
    if allow_legacy and isinstance(raw,dict) and raw.get('family') == 'phoenix_single_exchange_rr2': return raw
    if not isinstance(raw,dict): raise ResearchContractError('strategy config must be an object')
    expected={'family','symbol','timeframe','experiment_id','params','control_mode'}
    if set(raw) != expected: raise ResearchContractError('strategy config fields invalid')
    families, experiments=registry(); family=raw.get('family'); eid=raw.get('experiment_id'); row=experiments.get(str(eid)); symbol=raw.get('symbol'); tf=raw.get('timeframe'); mode=raw.get('control_mode')
    if family not in families or row is None or row.get('family_id') != family: raise ResearchContractError('experiment family invalid')
    if symbol not in REGISTERED_SYMBOLS or symbol not in row.get('universe',[]): raise ResearchContractError('experiment symbol invalid')
    if tf != row.get('effective_timeframe') or raw.get('params') != row.get('params'): raise ResearchContractError('experiment config drift')
    if mode not in {'PERFORMANCE','BASELINE','NEGATIVE_CONTROL'}: raise ResearchContractError('control mode invalid')
    return {'family':family,'symbol':symbol,'timeframe':tf,'experiment_id':eid,'params':dict(row['params']),'control_mode':mode}


def performance_config(experiment: dict[str,Any], symbol: str|None=None) -> dict[str,Any]:
    chosen=symbol or next(item for item in experiment['universe'] if item in REGISTERED_SYMBOLS)
    return validate_config({'family':experiment['family_id'],'symbol':chosen,'timeframe':experiment['effective_timeframe'],'experiment_id':experiment['experiment_id'],'params':experiment['params'],'control_mode':'PERFORMANCE'})


def control_config(candidate_config: dict[str,Any], classification: str) -> dict[str,Any]:
    value=dict(validate_config(candidate_config)); value['control_mode']=classification; return validate_config(value)


def mete_registry_status() -> dict[str,Any]:
    families, experiments=registry()
    return {'registry_id':METE_REGISTRY_VERSION,'status':'ACTIVE_EXECUTABLE_CORE_ABC_5M','executable_family_count':sum(x in families for x in METE_EXECUTABLE_FAMILIES),'executable_seed_count':sum(row.get('family_id') in METE_EXECUTABLE_FAMILIES for row in experiments.values()),'symbols':sorted(METE_EXECUTABLE_SYMBOLS),'timeframes':['5m'],'blocked':['1m','MK_D_MTF_BIAS','MK_E_SESSION','MK_F_MAGIC_ALIGNMENT','MK_G_BREAKER_RETEST','MK_H_RANGE_DEVIATION','MK_I_PO3_EXPANSION','MK_J_BPR_INDUCEMENT']}


def _patch_api(target: Any, expose_supported: bool=False) -> None:
    if target is None: return
    target.registry=registry; target.validate_config=validate_config; target.performance_config=performance_config; target.control_config=control_config
    if expose_supported: target.SUPPORTED_FAMILIES=SUPPORTED_FAMILIES
    target.METE_EXECUTABLE_FAMILIES=METE_EXECUTABLE_FAMILIES
    target.METE_EXECUTABLE_SYMBOLS=METE_EXECUTABLE_SYMBOLS
    target.METE_REGISTRY_VERSION=METE_REGISTRY_VERSION
    target.METE_SEEDS_PATH=METE_SEEDS_PATH
    target.METE_SOURCE_PACK_PATH=METE_SOURCE_PACK_PATH
    target.mete_registry_status=mete_registry_status

# The v2.0.38 wrapper may expose the expanded family set, but the immutable
# v2.0.33 atlas reader must retain its original SUPPORTED_FAMILIES set while its
# select_context global registry function is redirected here.
_patch_api(base, expose_supported=True)
if hasattr(base,'_base'): _patch_api(base._base, expose_supported=False)
_patch_api(sys.modules.get('tdh_research_kernel_v235_adapter'), expose_supported=True)

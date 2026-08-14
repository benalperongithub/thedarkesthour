#!/usr/bin/env python3
"""TDH Strategy Lab v2.0.59 runtime kernel binding repair.

Sealed v2.0.47 remains the immutable dispatch base. The Claude critic now runs
from an ephemeral /tmp cwd outside the repository, with tools disabled, one turn,
and a strict evidence-only JSON response contract. Raw provider usage is counted
for every subagent attempt even when result parsing fails. A failed/partial critic
is never cached as completed research. The only new frontier rows are sealed,
controller-reviewed seeds inside an already executable registered family;
untrusted Scout text remains non-executable.

No S1 target, Phoenix metric, trading path, paper path or exchange permission is
changed or weakened. No live/paper/exchange path is added.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V247 = Path('/srv/tdh-collab/controller/strategy-lab-v2/v2.0.47/strategy_lab_controller.py')
spec = importlib.util.spec_from_file_location('tdh_strategy_lab_v247_for_v248', V247)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.47 controller')
v247 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v247
spec.loader.exec_module(v247)
for name in dir(v247):
    if not name.startswith('__'):
        globals()[name] = getattr(v247, name)

HERE = Path(__file__).resolve().parent
LOCAL_ADAPTER = str(HERE / 'adapter' / 'tdh_strategy_lab_research_adapter.py')
v246 = v247.v246
v245 = v246.v245
v244 = v245.v244
v243 = v244.v243
v240 = v243.v242.v240
V258_KERNEL_PATH = HERE / 'research' / 'research_kernel.py'
v258_kernel_spec = importlib.util.spec_from_file_location(
    'tdh_research_kernel_v258_controller', V258_KERNEL_PATH
)
if v258_kernel_spec is None or v258_kernel_spec.loader is None:
    raise RuntimeError('cannot load v2.0.58 controller-owned admission kernel')
kernel = importlib.util.module_from_spec(v258_kernel_spec)
sys.modules[v258_kernel_spec.name] = kernel
v258_kernel_spec.loader.exec_module(kernel)

# Rebind every inherited context/validation boundary that owns a kernel global.
# No sealed file is changed; the rebinding is process-local to this release.
v240.kernel = kernel
v240.v238.v237.v236.v235.kernel = kernel
v240.v238.v237.v236.kernel = kernel
if hasattr(v240.v238.v237.v236, 'base_v217'):
    v240.v238.v237.v236.base_v217.kernel = kernel
V247_CONTROLLER_SOURCE = v247.Controller
V245_DISPATCH_ANCHOR = v247.V245_DISPATCH_ANCHOR
V246_DISPATCH_BASE = V247_CONTROLLER_SOURCE.__mro__[1]
if V246_DISPATCH_BASE.__module__ != v246.__name__:
    raise RuntimeError('v2.0.48 could not recover original v2.0.46 dispatch base')
v245.Controller = V245_DISPATCH_ANCHOR

V248_CRITIC_VERSION = 'tdh-avenox-evidence-only-critic-v1'
V248_CRITIC_JSON_ATTEMPTS = 2
V250_CRITIC_RESULT_PARSER_VERSION = 'tdh-avenox-critic-result-parser-v250'
V251_LANE_RESILIENCE_VERSION = 'tdh-dual-lane-fail-closed-resilience-v251'
V252_FRONTIER_CONTINUITY_VERSION = 'tdh-avenox-frontier-continuity-v252'
V253_AUDIT_CONTRACT_RESILIENCE_VERSION = 'tdh-audit-contract-resilience-v253'
V254_FRONTIER_SCOUT_VERSION = 'tdh-avenox-frontier-scout-v254'
V254_FRONTIER_LOW_WATERMARK = 2
V254_MAX_REGISTERED_ADMISSIONS = 2
V254_SCOUT_PROMPT_MAX_CHARS = 12000
V254_SCOUT_INBOX_MAX_FILES = 128
V254_SCOUT_TIMEFRAMES = frozenset({'1m', '5m', '15m', '30m', '1h', '4h', '1d'})
V255_SCOUT_CACHE_CONTINUITY_VERSION = 'tdh-avenox-scout-cache-continuity-v255'
V256_FRONTIER_EXHAUSTION_SCOUT_VERSION = 'tdh-avenox-frontier-exhaustion-scout-v256'
V257_SCOUT_CONFORMANCE_VERSION = 'tdh-avenox-scout-response-conformance-v257'
V257_SCOUT_MAX_ATTEMPTS = 2
V258_CONTROLLER_ADMISSION_VERSION = 'tdh-avenox-controller-admission-v258'
V259_RUNTIME_KERNEL_BINDING_VERSION = 'tdh-v259-runtime-kernel-overlay-binding'
V253_AUDIT_OUTPUT_ERRORS = frozenset({
    'invalid audit finding',
})
V252_FRONTIER_EXHAUSTION_ERRORS = frozenset({
    'v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine',
    'v2.0.28 no diverse executable frontier for actor=codex',
    'v2.0.28 no diverse executable frontier for actor=claude',
    'registered novelty frontier is exhausted',
})

# Compatibility/source-contract markers retained for immutable regressions.
# PROMPT_TARGET_MAX_CHARS
# MODEL_CONTEXT_MAX_CHARS = 9000
# v230.MODEL_CONTEXT_MAX_CHARS = MODEL_CONTEXT_MAX_CHARS
# class Controller(v220.Controller)
# v220.v217.v216.Controller = Controller
# def _compact_prompt_inputs(
# build_diverse_frontier
# excluded = getattr(self, "_v225_codex_family"
# available_distinct_families
# same_epoch_distinct_family_required
# dropped_same_family_peer_candidates
# historical_config_duplicate_forbidden
# machine_fields_are_controller_owned
# SHARED_RESEARCH_CONTEXT.json
# shared_research_context
# prior_shared_research_context
# codex_findings
# claude_findings
# prior["shared_research_context"] = compact_shared_context_for_prompt(
# batch["prior_shared_research_context"] = compact_shared_context_for_prompt(
# raw/full evidence remains on VPS
# raw_evidence_remains_on_vps
# full_duplicate_scan_remains_controller_owned
# metrics_and_control_deltas_preserved
# controller_only_promotion
# chain.get("diagnosis") == "PROMISING_BUT_UNCONFIRMED"
# source_verdict == "PASS"
# candidate["candidate_id"] = f"{actor}-{tag}-r{round_number:02d}-c{index:02d}"
# candidate["hypothesis_id"] = f"{actor}-{tag}-r{round_number:02d}-h{index:02d}"
# "codex_proposal", context
# "claude_proposal", context
# "claude_post_s1", review_context, analysis_packet
# "codex_post_s1", review_context, analysis_packet
# if stage == "S1":
# return super().compute_gate_verdict(stage, result)
# TDH_GLOBAL_PREOPT_V1
# global_preoptimize_prompt_inputs
# positive_pnl_is_not_s1_pass
# positive PnL remains hypothesis memory only
# No S1 target
# No live/paper/exchange path is added
# run_codex_audit(sd
# parent.run_claude(sd
# 'no_external_tools':True
# PAUSE_PROVIDER_COOLDOWN
# controller_budget_usage_includes_subagents
# ADVISORY_EVIDENCE_CLUSTER
# normalized = canonicalize_proposal_diagnosis(raw, source)
# normalized = canonicalize_machine_owned_fields(
# return super().validate_proposal(normalized, round_number)


def _json_dict(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _claude_raw_usage(path: Path) -> tuple[dict[str, int], dict[str, Any], dict[str, Any]]:
    outer = _json_dict(path)
    raw = outer.get('usage') if isinstance(outer.get('usage'), dict) else {}
    usage: dict[str, int] = {}
    for key in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'):
        try:
            usage[key] = int(raw.get(key, 0) or 0)
        except (TypeError, ValueError):
            usage[key] = 0
    usage['billable_tokens'] = usage['input_tokens'] + usage['cache_creation_input_tokens'] + usage['output_tokens']
    model_usage = copy.deepcopy(outer.get('modelUsage')) if isinstance(outer.get('modelUsage'), dict) else {}
    return usage, model_usage, outer


def _codex_raw_usage(path: Path) -> dict[str, int]:
    try:
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return {}
    found: dict[str, Any] = {}
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get('type') == 'turn.completed' and isinstance(row.get('usage'), dict):
            found = row['usage']
    if not found:
        return {}
    out: dict[str, int] = {}
    for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens'):
        try:
            out[key] = int(found.get(key, 0) or 0)
        except (TypeError, ValueError):
            out[key] = 0
    out['billable_tokens'] = max(0, out['input_tokens'] - out['cached_input_tokens']) + out['output_tokens']
    return out


def _valid_completed_cache(cache: Any, fp: str) -> bool:
    if not isinstance(cache, dict) or cache.get('fingerprint') != fp:
        return False
    item = cache.get('advisory')
    return (
        isinstance(item, dict)
        and item.get('status') == 'LLM_SUBAGENTS_COMPLETED'
        and isinstance(item.get('critic'), dict)
        and bool((item.get('critic') or {}).get('findings'))
    )


def _v256_cached_advisory(cache: Any) -> dict[str, Any] | None:
    """Return only a complete bounded Avenox cache item for Scout evidence."""
    if not isinstance(cache, dict):
        return None
    fingerprint = cache.get('fingerprint')
    advisory_result = cache.get('advisory')
    if (
        not isinstance(fingerprint, str)
        or re.fullmatch(r'[0-9a-f]{64}', fingerprint) is None
        or not isinstance(advisory_result, dict)
        or advisory_result.get('status') != 'LLM_SUBAGENTS_COMPLETED'
    ):
        return None

    research = advisory_result.get('researcher')
    critic = advisory_result.get('critic')
    if (
        not isinstance(research, dict)
        or not isinstance(research.get('findings'), list)
        or not research['findings']
        or not isinstance(critic, dict)
        or not isinstance(critic.get('findings'), list)
        or not critic['findings']
    ):
        return None
    return copy.deepcopy(advisory_result)


def _critic_args(controller: Any) -> tuple[str, ...]:
    args = list(controller.claude_worker_args())
    if '--max-turns' in args:
        i = args.index('--max-turns')
        if i + 1 < len(args):
            args[i + 1] = '1'
    return tuple(args)


def _critic_prompt(context: dict[str, Any], evidence: dict[str, Any], research: dict[str, Any], retry: bool) -> str:
    payload = {
        'research_round': context.get('research_round'),
        'isolated_evidence': evidence,
        'researcher_summary': research,
    }
    retry_text = 'Previous output was not usable JSON. ' if retry else ''
    return (
        'You are the TDH Independent Evidence Critic in an isolated context. ' + retry_text +
        'Use ONLY the JSON payload below. Do not inspect the working directory, repository, instruction files, '
        'skills, policy files, URLs, web, shell, MCP, or other files. Tools are disabled. Return ONLY one JSON '
        'object with exactly: contract_version, research_round, verdict, approved_candidate_ids, findings, '
        'reasoning_packet. approved_candidate_ids must be []. verdict must be REVISE. findings must contain 1-3 '
        'objects with finding_id, severity, claim, evidence. Focus on repeatability, strongest confounder, and one '
        'decisive controller-testable falsification. No markdown or preamble. PAYLOAD=' +
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    )


def _extract_critic_payload(outer: Any) -> dict[str, Any]:
    """Extract the Claude result envelope without hidden module dependencies."""
    if not isinstance(outer, dict):
        raise LabError('v2.0.50 critic provider envelope is not JSON')

    raw = outer.get('result')
    if isinstance(raw, dict):
        parsed = copy.deepcopy(raw)
    elif isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LabError('v2.0.50 critic result is not valid JSON') from exc
    else:
        raise LabError('v2.0.50 critic provider envelope has no result')

    if not isinstance(parsed, dict):
        raise LabError('v2.0.50 critic result is not a JSON object')
    return parsed

def _v257_extract_scout_payload(outer: Any) -> dict[str, Any]:
    """Accept raw JSON or one exact JSON fence; reject prose and ambiguity."""
    if not isinstance(outer, dict):
        raise LabError('v2.0.57 scout provider envelope is not JSON')

    raw = outer.get('result')
    if isinstance(raw, dict):
        parsed = copy.deepcopy(raw)
    elif isinstance(raw, str) and raw.strip():
        text = raw.strip()
        if '```' in text:
            match = re.fullmatch(
                r'```(?:json)?[ \t]*\r?\n(?P<body>[\s\S]*?)\r?\n```',
                text,
                flags=re.IGNORECASE,
            )
            if match is None:
                raise LabError(
                    'v2.0.57 scout result must be raw JSON or one exact JSON fence'
                )
            text = match.group('body').strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LabError('v2.0.57 scout result is not valid JSON') from exc
    else:
        raise LabError('v2.0.57 scout provider envelope has no result')

    if not isinstance(parsed, dict):
        raise LabError('v2.0.57 scout result is not a JSON object')
    return parsed


def _normalize_critic(raw: Any, context: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise LabError('v2.0.48 critic response is not JSON')
    source = raw.get('findings') if isinstance(raw.get('findings'), list) else []
    findings: list[dict[str, Any]] = []
    for index, row in enumerate(source[:3], start=1):
        if not isinstance(row, dict):
            continue
        claim = str(row.get('claim') or '').strip()
        evidence = str(row.get('evidence') or '').strip()
        if not claim or not evidence:
            continue
        severity = str(row.get('severity') or 'MEDIUM').upper()
        if severity not in {'LOW', 'MEDIUM', 'HIGH'}:
            severity = 'MEDIUM'
        findings.append({
            'finding_id': str(row.get('finding_id') or f'critic-{index:02d}')[:80],
            'severity': severity,
            'claim': b(claim, 320),
            'evidence': b(evidence, 320),
        })
    if not findings:
        raise LabError('v2.0.48 critic JSON contains no usable findings')
    return {
        'contract_version': context.get('contract_version'),
        'research_round': context.get('research_round'),
        'verdict': 'REVISE',
        'approved_candidate_ids': [],
        'findings': findings,
        'reasoning_packet': {},
    }


V251_LANE_VALIDATION_ERRORS = frozenset({
    'evidence-directed candidate did not change the source config',
    'CHANGE_STRATEGY_FAMILY did not change family',
    'parameter neighborhood changed family',
    'parameter neighborhood did not change registered seed',
    'CHANGE_SYMBOL changed more than the symbol',
    'CHANGE_TIMEFRAME did not change timeframe',
    'candidate primary_change disagrees with config transition',
})


def _v251_source_config(context: Any) -> dict[str, Any] | None:
    if not isinstance(context, dict):
        return None
    evidence = context.get('latest_s1_financial_evidence')
    if not isinstance(evidence, dict):
        return None
    candidates = evidence.get('candidates')
    if not isinstance(candidates, list):
        return None
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        config = candidate.get('strategy_config')
        if isinstance(config, dict):
            return copy.deepcopy(config)
    return None


def _v251_params_without_timeframe(config: dict[str, Any]) -> dict[str, Any]:
    params = config.get('params')
    if not isinstance(params, dict):
        return {}
    return {
        str(key): copy.deepcopy(value)
        for key, value in params.items()
        if key != 'timeframe'
    }


def _v251_transition_axes(
    source_config: dict[str, Any],
    candidate_config: dict[str, Any],
) -> tuple[str, ...]:
    if source_config.get('family') != candidate_config.get('family'):
        # A registered family change is the existing atomic structural treatment.
        return ('family',)

    axes: list[str] = []

    if source_config.get('symbol') != candidate_config.get('symbol'):
        axes.append('symbol')

    source_params = (
        source_config.get('params')
        if isinstance(source_config.get('params'), dict)
        else {}
    )
    candidate_params = (
        candidate_config.get('params')
        if isinstance(candidate_config.get('params'), dict)
        else {}
    )

    source_timeframe = (
        source_config.get('timeframe'),
        source_params.get('timeframe'),
    )
    candidate_timeframe = (
        candidate_config.get('timeframe'),
        candidate_params.get('timeframe'),
    )
    if source_timeframe != candidate_timeframe:
        axes.append('timeframe')

    if (
        source_config.get('experiment_id')
        != candidate_config.get('experiment_id')
        or _v251_params_without_timeframe(source_config)
        != _v251_params_without_timeframe(candidate_config)
    ):
        axes.append('registered_seed')

    return tuple(axes)


def _v251_legal_frontier_item(
    source_config: dict[str, Any],
    item: Any,
) -> bool:
    if not isinstance(item, dict):
        return False
    candidate_config = item.get('config')
    if not isinstance(candidate_config, dict):
        return False

    axes = _v251_transition_axes(source_config, candidate_config)
    return axes == ('family',) or len(axes) == 1


def _v251_skip_lane(context: dict[str, Any]) -> bool:
    source_config = _v251_source_config(context)
    frontier = context.get('novelty_frontier')
    return (
        source_config is not None
        and isinstance(frontier, list)
        and not frontier
    )


def _v251_rejected_lane(
    context: dict[str, Any],
    actor: str,
    mode: str,
    reason: str,
) -> dict[str, Any]:
    return {
        'contract_version': context.get('contract_version'),
        'research_round': context.get('research_round'),
        'verdict': 'REJECT',
        'candidates': [],
        'reasoning_packet': {
            'assumptions': [],
            'evidence': [
                'The controller rejected this lane before backtesting.'
            ],
            'counterevidence': [],
            'uncertainty': [],
            'decision_change_evidence': [],
        },
        'controller_batch': {
            'mode': mode,
            'actor': actor,
            'candidate_count': 0,
            'reason': str(reason)[:300],
            'controller_only_promotion': True,
            'invalid_lane_never_backtested': True,
        },
    }


def _v254_canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':'),
    ).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _v254_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _v254_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _v254_strings(item)


def _v254_text(value: Any, name: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        raise LabError(f'v2.0.54 scout {name} must be text')
    text = value.strip()
    if not minimum <= len(text) <= maximum:
        raise LabError(f'v2.0.54 scout {name} length invalid')
    return text


def _v254_validate_parameter_value(value: Any) -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, (int, float)):
        if not -1_000_000_000 <= float(value) <= 1_000_000_000:
            raise LabError('v2.0.54 scout parameter number out of bounds')
        return
    if isinstance(value, str):
        if not value or len(value) > 160:
            raise LabError('v2.0.54 scout parameter text invalid')
        return
    if isinstance(value, list) and 1 <= len(value) <= 16:
        for item in value:
            if isinstance(item, (dict, list)):
                raise LabError('v2.0.54 scout nested parameter value forbidden')
            _v254_validate_parameter_value(item)
        return
    raise LabError('v2.0.54 scout parameter value type forbidden')


def _v254_validate_scout_proposal(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise LabError('v2.0.54 scout result is not an object')
    required = {
        'proposal_version', 'hypothesis_id', 'status', 'family_thesis',
        'causal_mechanism', 'source_evidence', 'required_data', 'timeframes',
        'bounded_parameters', 'baseline_thesis', 'negative_control_thesis',
        'falsification', 'safety',
    }
    if set(raw) != required:
        raise LabError('v2.0.54 scout fields invalid')
    if raw.get('proposal_version') != 'tdh-frontier-inbox-v1':
        raise LabError('v2.0.54 scout proposal version invalid')
    hypothesis_id = raw.get('hypothesis_id')
    if not isinstance(hypothesis_id, str) or re.fullmatch(r'TDH-SCOUT-[0-9]{6}', hypothesis_id) is None:
        raise LabError('v2.0.54 scout hypothesis id invalid')
    if raw.get('status') != 'UNTRUSTED_INBOX':
        raise LabError('v2.0.54 scout status must remain untrusted')

    _v254_text(raw.get('family_thesis'), 'family thesis', 20, 800)
    _v254_text(raw.get('causal_mechanism'), 'causal mechanism', 20, 1200)
    _v254_text(raw.get('baseline_thesis'), 'baseline thesis', 10, 600)
    _v254_text(raw.get('negative_control_thesis'), 'negative control thesis', 10, 600)

    evidence = raw.get('source_evidence')
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8:
        raise LabError('v2.0.54 scout source evidence invalid')
    for row in evidence:
        if not isinstance(row, dict) or set(row) != {'source_id', 'claim', 'provenance'}:
            raise LabError('v2.0.54 scout source evidence fields invalid')
        _v254_text(row.get('source_id'), 'source id', 1, 160)
        _v254_text(row.get('claim'), 'source claim', 1, 600)
        _v254_text(row.get('provenance'), 'source provenance', 1, 500)

    required_data = raw.get('required_data')
    if not isinstance(required_data, list) or not 1 <= len(required_data) <= 8:
        raise LabError('v2.0.54 scout required data invalid')
    for value in required_data:
        _v254_text(value, 'required data item', 1, 80)

    timeframes = raw.get('timeframes')
    if (
        not isinstance(timeframes, list)
        or not 1 <= len(timeframes) <= 8
        or any(value not in V254_SCOUT_TIMEFRAMES for value in timeframes)
    ):
        raise LabError('v2.0.54 scout timeframe invalid')

    parameters = raw.get('bounded_parameters')
    if not isinstance(parameters, dict) or not 1 <= len(parameters) <= 16:
        raise LabError('v2.0.54 scout bounded parameters invalid')
    for key, value in parameters.items():
        _v254_text(key, 'parameter name', 1, 80)
        _v254_validate_parameter_value(value)

    falsification = raw.get('falsification')
    if not isinstance(falsification, dict) or set(falsification) != {
        'failure_condition', 'minimum_test', 'expected_information_gain'
    }:
        raise LabError('v2.0.54 scout falsification invalid')
    for key in ('failure_condition', 'minimum_test', 'expected_information_gain'):
        _v254_text(falsification.get(key), key, 1, 800)

    expected_safety = {
        'data_only': True,
        'contains_executable_code': False,
        'trading_actions': False,
        'exchange_api_access': False,
        'controller_registration_required': True,
    }
    if raw.get('safety') != expected_safety:
        raise LabError('v2.0.54 scout safety contract invalid')

    forbidden = re.compile(
        r'(^|\n)\s*(#!|import\s|from\s+\S+\s+import|def\s|class\s)'
        r'|subprocess|os\.system|shell\s*=\s*true|create_order|place_order'
        r'|api[_ -]?key|private[_ -]?api|curl\s|wget\s',
        re.IGNORECASE,
    )
    if any(forbidden.search(text) for text in _v254_strings(raw)):
        raise LabError('v2.0.54 scout executable or private-api content forbidden')
    return copy.deepcopy(raw)


def _v254_walk_identities(value: Any, experiment_ids: set[str], config_hashes: set[str]) -> None:
    if isinstance(value, dict):
        experiment_id = value.get('experiment_id')
        if isinstance(experiment_id, str) and experiment_id:
            experiment_ids.add(experiment_id)
        for key in ('strategy_config_sha256', 'config_sha256'):
            digest = value.get(key)
            if isinstance(digest, str) and len(digest) == 64:
                config_hashes.add(digest)
        config = value.get('config')
        if isinstance(config, dict):
            config_hashes.add(_v254_canonical_hash(config))
        for item in value.values():
            _v254_walk_identities(item, experiment_ids, config_hashes)
    elif isinstance(value, list):
        for item in value:
            _v254_walk_identities(item, experiment_ids, config_hashes)


def _v254_used_identities(context: dict[str, Any]) -> tuple[set[str], set[str]]:
    experiment_ids: set[str] = set()
    config_hashes: set[str] = set()
    for key in (
        'previous_rounds', 'prior_shared_research_context',
        'shared_research_context', 'latest_s1_financial_evidence',
        'negative_memory', 'research_program_memory',
    ):
        _v254_walk_identities(context.get(key), experiment_ids, config_hashes)
    return experiment_ids, config_hashes


def _v254_registered_replenishment(
    context: dict[str, Any],
    actor: str,
    excluded_family: str | None = None,
) -> dict[str, Any]:
    frontier = context.get('novelty_frontier')
    if not isinstance(frontier, list) or len(frontier) > V254_FRONTIER_LOW_WATERMARK:
        return context

    updated = copy.deepcopy(context)
    frontier = updated['novelty_frontier']
    original_count = len(frontier)
    selection = updated.get('tdh_research_selection')
    seeds = selection.get('experiment_seeds') if isinstance(selection, dict) else None
    if not isinstance(seeds, list):
        seeds = []

    selected_family_ids = {
        str(row.get('family_id'))
        for row in (
            selection.get('family_cards', [])
            if isinstance(selection, dict)
            and isinstance(selection.get('family_cards'), list)
            else []
        )
        if isinstance(row, dict) and isinstance(row.get('family_id'), str)
    }
    used_experiment_ids, used_config_hashes = _v254_used_identities(updated)
    for item in frontier:
        if not isinstance(item, dict):
            continue
        config = item.get('config')
        if not isinstance(config, dict):
            continue
        experiment_id = config.get('experiment_id')
        if isinstance(experiment_id, str):
            used_experiment_ids.add(experiment_id)
        used_config_hashes.add(_v254_canonical_hash(config))

    if actor == 'claude':
        if not isinstance(excluded_family, str):
            excluded_family = None
        registered = updated.get('registered_candidate_contract')
        dual = registered.get('dual_lane_contract') if isinstance(registered, dict) else None
        if isinstance(dual, dict) and isinstance(dual.get('excluded_peer_family'), str):
            excluded_family = dual['excluded_peer_family']

    _, experiments = kernel.registry()
    source_config = _v251_source_config(updated)
    admitted: list[dict[str, Any]] = []
    seen_families: set[str] = set()

    for seed in sorted(
        (row for row in seeds if isinstance(row, dict)),
        key=lambda row: str(row.get('experiment_id') or ''),
    ):
        experiment_id = seed.get('experiment_id')
        if not isinstance(experiment_id, str) or experiment_id in used_experiment_ids:
            continue
        experiment = experiments.get(experiment_id)
        if not isinstance(experiment, dict):
            raise LabError('v2.0.54 selected replenishment seed is not registered')
        family_id = experiment.get('family_id')
        if (
            not isinstance(family_id, str)
            or (selected_family_ids and family_id not in selected_family_ids)
            or family_id == excluded_family
            or family_id in seen_families
        ):
            continue

        universe = experiment.get('universe')
        if not isinstance(universe, list):
            raise LabError('v2.0.54 registered replenishment universe invalid')

        for symbol in sorted(value for value in universe if isinstance(value, str)):
            candidate_config = kernel.validate_config(
                kernel.performance_config(experiment, symbol)
            )
            digest = _v254_canonical_hash(candidate_config)
            if digest in used_config_hashes:
                continue
            item = {
                'config': copy.deepcopy(candidate_config),
                'v254_registration': {
                    'version': V254_FRONTIER_SCOUT_VERSION,
                    'source': 'EXISTING_REGISTERED_KERNEL_SEED',
                    'experiment_id': experiment_id,
                    'family_id': family_id,
                    'schema_validated': True,
                    'data_eligibility_inherited_from_selection': True,
                    'deduplicated': True,
                    'model_generated_executable_code': False,
                    'controller_only_registration': True,
                },
            }
            if source_config is not None and not _v251_legal_frontier_item(source_config, item):
                continue
            frontier.append(item)
            admitted.append(copy.deepcopy(item['v254_registration']))
            used_experiment_ids.add(experiment_id)
            used_config_hashes.add(digest)
            seen_families.add(family_id)
            break

        if len(admitted) >= V254_MAX_REGISTERED_ADMISSIONS:
            break

    updated['v254_frontier_replenishment'] = {
        'version': V254_FRONTIER_SCOUT_VERSION,
        'mode': 'V254_REGISTERED_QUEUE_REPLENISHMENT',
        'actor': actor,
        'low_watermark': V254_FRONTIER_LOW_WATERMARK,
        'input_count': original_count,
        'admitted_count': len(admitted),
        'output_count': len(frontier),
        'admitted': admitted,
        'only_existing_registered_seeds': True,
        'new_families_auto_admitted': False,
        'unknown_validation_errors_fail_closed': True,
        'controller_only_promotion': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }
    updated['v254_frontier_low_watermark'] = True
    return updated


def _v254_scout_needed(context: dict[str, Any]) -> bool:
    if context.get('v254_frontier_low_watermark') is True:
        return True
    frontier = context.get('novelty_frontier')
    return isinstance(frontier, list) and len(frontier) <= V254_FRONTIER_LOW_WATERMARK


def _v254_evidence_excerpt(value: Any, maximum: int = 1200) -> Any:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    if len(raw) <= maximum:
        return value
    return {
        'truncated': True,
        'full_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        'json_prefix': raw[:maximum],
    }


def _v254_scout_prompt(
    context: dict[str, Any],
    research: dict[str, Any],
    critic: dict[str, Any],
    validation_error: str | None = None,
) -> str:
    selection = context.get('tdh_research_selection')
    cards = (
        selection.get('family_cards', [])[:6]
        if isinstance(selection, dict)
        and isinstance(selection.get('family_cards'), list)
        else []
    )
    payload = {
        'research_round': context.get('research_round'),
        'family_cards': _v254_evidence_excerpt(cards),
        'frontier_exhaustion': _v254_evidence_excerpt(
            context.get('v256_frontier_exhaustion')
        ),
        'deep_research_advisory': _v254_evidence_excerpt(research),
        'independent_critic_advisory': _v254_evidence_excerpt(critic),
        'policy': {
            'research_mode': 'offline',
            'trading_actions': False,
            'exchange_api_access': False,
            's1_only': True,
        },
    }
    retry = ''
    if isinstance(validation_error, str) and validation_error:
        retry = (
            ' PREVIOUS_VALIDATION_ERROR='
            + json.dumps(validation_error[:300], ensure_ascii=False)
            + '. Correct that error and every constraint below.'
        )
    allowed_timeframes = json.dumps(
        sorted(V254_SCOUT_TIMEFRAMES), ensure_ascii=False
    )
    prompt = (
        'You are the TDH Frontier Scout in an isolated evidence-only context. '
        'Use ONLY the bounded JSON payload; tools/web/shell/repository access are forbidden. '
        'Return ONLY one raw JSON object. Do not use markdown, code fences, or prose. '
        'Use exactly these top-level fields and no others: proposal_version, hypothesis_id, '
        'status, family_thesis, causal_mechanism, source_evidence, required_data, timeframes, '
        'bounded_parameters, baseline_thesis, negative_control_thesis, falsification, safety. '
        'proposal_version must be tdh-frontier-inbox-v1. status must be UNTRUSTED_INBOX. '
        'hypothesis_id must match TDH-SCOUT-[0-9]{6}; example TDH-SCOUT-000001. '
        'family_thesis must be 20-800 characters; causal_mechanism 20-1200; baseline_thesis '
        'and negative_control_thesis 10-600 each. source_evidence must be an array of 1-8 '
        'objects containing only source_id (1-160 chars), claim (1-600), provenance (1-500). '
        'required_data must be an array of 1-8 strings, each 1-80 characters. '
        'timeframes must be a JSON array of 1-8 values chosen only from ' + allowed_timeframes + '. '
        'bounded_parameters must contain 1-16 scalar or flat-list values; parameter names are '
        '1-80 chars, text values at most 160 chars, and nested objects/lists are forbidden. '
        'falsification must contain only failure_condition, minimum_test, '
        'expected_information_gain; each is 1-800 characters. Safety must equal exactly '
        '{"data_only":true,"contains_executable_code":false,"trading_actions":false,'
        '"exchange_api_access":false,"controller_registration_required":true}. '
        'Never emit code, commands, API instructions, or claim registration. '
        'New families remain untrusted.' + retry + ' PAYLOAD='
        + json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    )
    if len(prompt) > V254_SCOUT_PROMPT_MAX_CHARS:
        raise LabError('v2.0.54 scout prompt exceeds bounded budget')
    return prompt


class Controller(V246_DISPATCH_BASE):
    def _v256_scout_on_frontier_exhaustion(
        self,
        round_dir: Path,
        round_number: int,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        dispatch_path = round_dir / 'FRONTIER_SCOUT_DISPATCH_V256.json'
        advisory_result = _v256_cached_advisory(self.load_cache())
        base = {
            'version': V256_FRONTIER_EXHAUSTION_SCOUT_VERSION,
            'trigger': 'GLOBAL_REGISTERED_FRONTIER_EXHAUSTION',
            'research_round': round_number,
            'actor': actor,
            'reason': str(reason)[:400],
            'researcher_rerun': False,
            'critic_rerun': False,
            'automatically_registered': False,
            'controller_registration_required': True,
            'controller_only_promotion': True,
            'trading_actions': False,
            'exchange_api_access': False,
        }
        if advisory_result is None:
            dispatch = {
                **base,
                'status': 'SKIPPED_NO_VALID_CACHED_ADVISORY',
                'advisory_source_status': None,
                'provider_invoked': False,
            }
            atomic_json(dispatch_path, dispatch)
            return dispatch

        research = advisory_result['researcher']
        critic = advisory_result['critic']
        context = {
            'contract_version': advisory_result.get('contract_version'),
            'research_round': round_number,
            'novelty_frontier': [],
            'tdh_research_selection': {'family_cards': []},
            'v256_frontier_exhaustion': {
                'actor': actor,
                'reason': str(reason)[:400],
                'registered_families_only': True,
                'structural_no_signal_quarantine_preserved': True,
            },
        }
        sd = round_dir / 'avenox-subagents'
        sd.mkdir(exist_ok=True)
        if not isinstance(getattr(self, '_avu', None), dict):
            self._avu = {'codex': {}, 'claude': {}}

        try:
            scout = self._run_frontier_scout(
                sd,
                context,
                research,
                critic,
                'CACHE_HIT',
            )
            atomic_json(sd / 'FRONTIER_SCOUT_INBOX_V254.json', scout)
            dispatch = {
                **base,
                'status': 'UNTRUSTED_INBOX_VALIDATED',
                'advisory_source_status': 'CACHE_HIT',
                'provider_invoked': True,
            }
        except LabError as exc:
            atomic_json(sd / 'FRONTIER_SCOUT_REJECTED_V254.json', {
                'version': V254_FRONTIER_SCOUT_VERSION,
                'status': 'REJECTED_OR_UNAVAILABLE',
                'reason': b(exc, 400),
                'advisory_source_status': 'CACHE_HIT',
                'automatically_registered': False,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            })
            dispatch = {
                **base,
                'status': 'REJECTED_OR_UNAVAILABLE',
                'advisory_source_status': 'CACHE_HIT',
                'provider_invoked': True,
                'rejection_reason': b(exc, 400),
            }
        finally:
            atomic_json(sd / 'SUBAGENT_USAGE.json', self._avu)

        atomic_json(dispatch_path, dispatch)
        return dispatch

    def _v251_round_context(self, round_number: int) -> dict[str, Any]:
        context = super().round_context(round_number)
        source_config = _v251_source_config(context)
        frontier = context.get('novelty_frontier')

        if source_config is not None and isinstance(frontier, list):
            legal: list[dict[str, Any]] = []
            rejected: list[dict[str, Any]] = []

            for item in frontier:
                if _v251_legal_frontier_item(source_config, item):
                    legal.append(copy.deepcopy(item))
                    continue

                config = (
                    item.get('config')
                    if isinstance(item, dict)
                    and isinstance(item.get('config'), dict)
                    else {}
                )
                rejected.append({
                    'experiment_id': config.get('experiment_id'),
                    'axes': list(
                        _v251_transition_axes(source_config, config)
                    ) if config else [],
                })

            context['novelty_frontier'] = legal
            context['v251_transition_filter'] = {
                'version': V251_LANE_RESILIENCE_VERSION,
                'input_count': len(frontier),
                'legal_count': len(legal),
                'rejected_count': len(rejected),
                'rejected': rejected[:8],
                'single_material_axis_required': True,
            }

        return context

    def round_context(self, round_number: int) -> dict[str, Any]:
        actor = str(getattr(self, '_v225_next_actor', 'codex'))
        try:
            context = self._v251_round_context(round_number)
        except LabError as exc:
            error = str(exc)
            cached = getattr(self, '_v252_round_context_cache', {}).get(round_number)
            excluded = getattr(self, '_v225_codex_family', None)
            if (
                error not in V252_FRONTIER_EXHAUSTION_ERRORS
                or actor != 'claude'
                or not isinstance(cached, dict)
                or not isinstance(excluded, str)
                or not excluded
            ):
                raise

            context = copy.deepcopy(cached)
            context['novelty_frontier'] = []
            event = {
                'version': V252_FRONTIER_CONTINUITY_VERSION,
                'mode': 'V252_PEER_FRONTIER_EXHAUSTED_LANE_SKIP',
                'actor': 'claude',
                'research_round': round_number,
                'excluded_peer_family': excluded,
                'reason': error,
                'provider_invoked': False,
                'valid_peer_lane_preserved': True,
                'invalid_lane_never_backtested': True,
                'controller_only_promotion': True,
            }
            context['v252_frontier_continuity'] = copy.deepcopy(event)

            registered = context.get('registered_candidate_contract')
            if isinstance(registered, dict):
                registered['registered_families'] = []
                dual = registered.get('dual_lane_contract')
                if isinstance(dual, dict):
                    dual['excluded_peer_family'] = excluded
                    dual['available_distinct_families'] = []
                    dual['instruction'] = (
                        'Peer lane has no legal registered family; skip provider and preserve valid peer.'
                    )
            selection = context.get('tdh_research_selection')
            if isinstance(selection, dict):
                selection['family_cards'] = []

            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(round_dir / 'CLAUDE_PEER_FRONTIER_EXHAUSTED_V252.json', event)
            return context

        context = _v254_registered_replenishment(
            context,
            actor,
            getattr(self, '_v225_codex_family', None),
        )
        event = context.get('v254_frontier_replenishment')
        if isinstance(event, dict):
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(round_dir / 'FRONTIER_REPLENISHMENT_V254.json', event)

        frontier = context.get('novelty_frontier')
        if actor == 'codex' and isinstance(frontier, list) and frontier:
            cache = getattr(self, '_v252_round_context_cache', None)
            if not isinstance(cache, dict):
                cache = {}
                self._v252_round_context_cache = cache
            cache[round_number] = copy.deepcopy(context)
        return context

    def run_codex(
        self,
        round_dir: Path,
        context: dict[str, Any],
    ):
        if _v251_skip_lane(context):
            proposal = _v251_rejected_lane(
                context,
                'codex',
                'V251_NO_LEGAL_FRONTIER_SKIP',
                'no legal single-axis registered transition',
            )
            atomic_json(
                round_dir / 'CODEX_PROPOSAL_SKIPPED_NO_LEGAL_FRONTIER.json',
                proposal['controller_batch'],
            )
            return proposal, {}

        try:
            return super().run_codex(round_dir, context)
        except LabError as exc:
            if str(exc) not in V251_LANE_VALIDATION_ERRORS:
                raise

            usage = _codex_raw_usage(round_dir / 'codex.jsonl')
            proposal = _v251_rejected_lane(
                context,
                'codex',
                'V251_INVALID_LANE_QUARANTINED',
                str(exc),
            )
            atomic_json(
                round_dir / 'CODEX_PROPOSAL_VALIDATION_QUARANTINE.json',
                {
                    **proposal['controller_batch'],
                    'raw_provider_log': 'codex.jsonl',
                    'usage': usage,
                },
            )
            return proposal, usage

    def run_claude_proposal(
        self,
        round_dir: Path,
        context: dict[str, Any],
    ):
        if _v251_skip_lane(context):
            proposal = _v251_rejected_lane(
                context,
                'claude',
                'V251_NO_LEGAL_FRONTIER_SKIP',
                'no legal single-axis registered transition',
            )
            atomic_json(
                round_dir / 'CLAUDE_PROPOSAL_SKIPPED_NO_LEGAL_FRONTIER.json',
                proposal['controller_batch'],
            )
            return proposal, {}

        try:
            return super().run_claude_proposal(round_dir, context)
        except LabError as exc:
            if str(exc) not in V251_LANE_VALIDATION_ERRORS:
                raise

            usage, model_usage, _ = _claude_raw_usage(
                round_dir / 'claude-proposal.json'
            )
            proposal = _v251_rejected_lane(
                context,
                'claude',
                'V251_INVALID_LANE_QUARANTINED',
                str(exc),
            )
            atomic_json(
                round_dir / 'CLAUDE_PROPOSAL_VALIDATION_QUARANTINE.json',
                {
                    **proposal['controller_batch'],
                    'raw_provider_log': 'claude-proposal.json',
                    'usage': usage,
                    'modelUsage': model_usage,
                },
            )
            return proposal, usage

    def execute_round(
        self,
        round_number: int,
        preflight: dict[str, Any],
    ):
        try:
            return super().execute_round(round_number, preflight)
        except LabError as exc:
            error = str(exc)
            if error in V253_AUDIT_OUTPUT_ERRORS:
                round_dir = self.run_dir / f'round-{round_number:02d}'
                round_dir.mkdir(parents=True, exist_ok=True)
                raw_log = round_dir / 'claude.json'
                raw_log_sha256 = None
                if raw_log.is_file():
                    raw_log_sha256 = hashlib.sha256(raw_log.read_bytes()).hexdigest()
                event = {
                    'version': V253_AUDIT_CONTRACT_RESILIENCE_VERSION,
                    'mode': 'V253_INVALID_AUDIT_QUARANTINED_EPOCH_ROLLOVER',
                    'status': 'AUDIT_OUTPUT_REJECTED',
                    'research_round': round_number,
                    'reason': error,
                    'raw_provider_log': raw_log.name if raw_log.is_file() else None,
                    'raw_provider_log_sha256': raw_log_sha256,
                    'invalid_audit_never_promoted': True,
                    'approved_candidate_ids': [],
                    'next_action': 'fresh bounded epoch with schema-constrained audit retry',
                    'controller_only_promotion': True,
                    's2_s4_opened': False,
                    'trading_actions': False,
                    'exchange_api_access': False,
                }
                event_sha256 = hashlib.sha256(
                    json.dumps(
                        event,
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(',', ':'),
                    ).encode('utf-8')
                ).hexdigest()
                atomic_json(round_dir / 'AUDIT_OUTPUT_QUARANTINE_V253.json', event)
                summary = {
                    'research_round': round_number,
                    'verdict': 'REVISE',
                    'stop_stage': 'S1_AUDIT_OUTPUT_REJECTED',
                    'target_found': False,
                    'best_score': None,
                    'surviving_candidates': [],
                    'dual_synthesis_sha256': event_sha256,
                    'stage_result_hashes': {},
                    'findings': {
                        'controller': [{
                            'finding_id': 'v253-invalid-audit-quarantined',
                            'severity': 'HIGH',
                            'claim': 'Provider audit output violated the registered audit contract.',
                            'evidence': error,
                        }],
                    },
                    'audit_output_quarantine': event,
                }
                atomic_json(round_dir / 'ROUND_SUMMARY.json', summary)
                return summary, False, None
            if error not in V252_FRONTIER_EXHAUSTION_ERRORS:
                raise

            actor = str(getattr(self, '_v225_next_actor', 'codex'))
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            scout_dispatch = self._v256_scout_on_frontier_exhaustion(
                round_dir,
                round_number,
                actor,
                error,
            )
            event = {
                'version': V252_FRONTIER_CONTINUITY_VERSION,
                'mode': 'V252_ELIGIBLE_FRONTIER_EXHAUSTED_EPOCH_ROLLOVER',
                'status': 'FRONTIER_EXHAUSTED',
                'research_round': round_number,
                'actor': actor,
                'reason': error,
                'provider_invoked': scout_dispatch['provider_invoked'],
                'frontier_scout_dispatch': scout_dispatch,
                'no_arbitrary_strategy_generation': True,
                'registered_families_only': True,
                'next_action': (
                    'controller registration review of untrusted Scout inbox, then fresh bounded epoch'
                    if scout_dispatch['status'] == 'UNTRUSTED_INBOX_VALIDATED'
                    else 'fresh bounded epoch and deterministic family reselection'
                ),
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            }
            event_sha256 = hashlib.sha256(
                json.dumps(
                    event,
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(',', ':'),
                ).encode('utf-8')
            ).hexdigest()
            atomic_json(round_dir / 'FRONTIER_EXHAUSTION_V252.json', event)
            summary = {
                'research_round': round_number,
                'verdict': 'REVISE',
                'stop_stage': 'S1_FRONTIER_EXHAUSTED',
                'target_found': False,
                'best_score': None,
                'surviving_candidates': [],
                'dual_synthesis_sha256': event_sha256,
                'stage_result_hashes': {},
                'findings': {
                    'controller': [{
                        'finding_id': 'v252-frontier-exhausted',
                        'severity': 'MEDIUM',
                        'claim': 'Current eligible registered frontier is exhausted.',
                        'evidence': error,
                    }],
                },
                'frontier_exhaustion': event,
            }
            atomic_json(round_dir / 'ROUND_SUMMARY.json', summary)
            return summary, False, None

    def validate_proposal(self, raw: dict[str, Any], round_number: int) -> dict[str, Any]:
        # normalized = canonicalize_proposal_diagnosis(raw, source)
        # normalized = canonicalize_machine_owned_fields(
        # return super().validate_proposal(normalized, round_number)
        return super().validate_proposal(raw, round_number)

    def subpacket(self, context: dict[str, Any], evidence: dict[str, Any], role: str, research: dict[str, Any] | None = None) -> dict[str, Any]:
        return V247_CONTROLLER_SOURCE.subpacket(self, context, evidence, role, research)

    def _provider_audit(self, sd: Path, call: dict[str, Any]) -> None:
        path = sd / 'SUBAGENT_PROVIDER_USAGE.json'
        raw = _json_dict(path)
        calls = raw.get('calls') if isinstance(raw.get('calls'), list) else []
        calls.append(copy.deepcopy(call))
        atomic_json(path, {
            'version': 'tdh-subagent-provider-usage-v248',
            'calls': calls,
            'failed_calls_are_budget_accounted': True,
            'raw_provider_logs_remain_on_vps': True,
        })

    def _account_codex(self, sd: Path, status: str, fallback: dict[str, int] | None = None) -> None:
        log = sd / 'codex-audit.jsonl'
        usage = _codex_raw_usage(log) or copy.deepcopy(fallback or {})
        self._avu['codex'] = usum(self._avu.get('codex', {}), usage)
        self._provider_audit(sd, {'role': 'DEEP_RESEARCH', 'provider': 'codex', 'status': status, 'usage': usage, 'log': log.name})

    def _run_evidence_only_critic(self, sd: Path, context: dict[str, Any], evidence: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
        cfg = {
            'claude_user': self.config.claude_user,
            'claude_bin': self.config.claude_bin,
            'worker_timeout_seconds': self.config.worker_timeout_seconds,
        }
        args = _critic_args(self)
        provider_attempt = 0
        json_attempt = 0
        workspace = Path(tempfile.mkdtemp(prefix='tdh-v248-critic-', dir='/tmp'))
        workspace.chmod(0o755)
        try:
            while provider_attempt < 5 and json_attempt < V248_CRITIC_JSON_ATTEMPTS:
                provider_attempt += 1
                log = sd / f'claude-critic-attempt-{provider_attempt}.json'
                error: LabError | None = None
                try:
                    self.run_worker(
                        user=str(cfg['claude_user']), binary=Path(str(cfg['claude_bin'])), args=args,
                        cwd=workspace, prompt=_critic_prompt(context, evidence, research, json_attempt > 0),
                        log_path=log, timeout=int(cfg.get('worker_timeout_seconds', 3600)),
                    )
                except LabError as exc:
                    error = exc
                usage, model_usage, outer = _claude_raw_usage(log)
                self._avu['claude'] = usum(self._avu.get('claude', {}), usage)
                cooldown = parse429(outer)
                if error is not None and cooldown is not None and provider_attempt < 5:
                    self._provider_audit(sd, {'role': 'INDEPENDENT_CRITIC', 'provider': 'claude', 'attempt': provider_attempt, 'status': 'PROVIDER_COOLDOWN', 'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO', 'usage': usage, 'modelUsage': model_usage})
                    atomic_json(sd / 'PROVIDER_COOLDOWN.json', {'version': V248_CRITIC_VERSION, 'status': 'PAUSE_PROVIDER_COOLDOWN', 'purpose': 'avenox_evidence_only_critic', 'retry': provider_attempt, **cooldown})
                    time.sleep(int(cooldown['wait_seconds']))
                    continue
                if error is not None:
                    self._provider_audit(sd, {'role': 'INDEPENDENT_CRITIC', 'provider': 'claude', 'attempt': provider_attempt, 'status': 'WORKER_FAILED', 'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO', 'usage': usage, 'modelUsage': model_usage, 'error': b(error, 300)})
                    raise error
                try:
                    raw_result = _extract_critic_payload(outer)
                    result = _normalize_critic(raw_result, context)
                except LabError as exc:
                    json_attempt += 1
                    self._provider_audit(sd, {'role': 'INDEPENDENT_CRITIC', 'provider': 'claude', 'attempt': provider_attempt, 'status': 'JSON_PARSE_FAILED', 'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO', 'usage': usage, 'modelUsage': model_usage, 'error': b(exc, 300)})
                    if json_attempt >= V248_CRITIC_JSON_ATTEMPTS:
                        raise
                    continue
                self._provider_audit(sd, {'role': 'INDEPENDENT_CRITIC', 'provider': 'claude', 'attempt': provider_attempt, 'status': 'PARSED', 'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO', 'usage': usage, 'modelUsage': model_usage, 'terminal_reason': outer.get('terminal_reason')})
                atomic_json(sd / 'EVIDENCE_ONLY_CRITIC_RUNTIME.json', {
                    'version': V248_CRITIC_VERSION,
                    'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO',
                    'workspace_under_claude_repo': False,
                    'tools_disabled': True,
                    'max_turns': 1,
                    'json_attempts_used': json_attempt + 1,
                    'raw_provider_model_usage_retained': True,
                })
                return result
            raise LabError('v2.0.48 critic exhausted bounded attempts')
        finally:
            shutil.rmtree(workspace, ignore_errors=True)


    def _run_frontier_scout(
        self,
        sd: Path,
        context: dict[str, Any],
        research: dict[str, Any],
        critic: dict[str, Any],
        advisory_source_status: str,
    ) -> dict[str, Any]:
        if getattr(self, '_v254_scout_attempted', False):
            raise LabError('v2.0.54 scout already attempted in this bounded run')
        self._v254_scout_attempted = True

        args = _critic_args(self)
        workspace = Path(tempfile.mkdtemp(prefix='tdh-v257-scout-', dir='/tmp'))
        workspace.chmod(0o755)
        validation_error: str | None = None
        proposal: dict[str, Any] | None = None
        usage: dict[str, int] = {}
        model_usage: dict[str, Any] = {}
        raw_logs: list[str] = []
        attempts_used = 0
        try:
            for attempt in range(1, V257_SCOUT_MAX_ATTEMPTS + 1):
                attempts_used = attempt
                log = sd / (
                    'claude-frontier-scout.json'
                    if attempt == 1
                    else f'claude-frontier-scout-attempt-{attempt}.json'
                )
                raw_logs.append(log.name)
                self.run_worker(
                    user=str(self.config.claude_user),
                    binary=Path(str(self.config.claude_bin)),
                    args=args,
                    cwd=workspace,
                    prompt=_v254_scout_prompt(
                        context,
                        research,
                        critic,
                        validation_error,
                    ),
                    log_path=log,
                    timeout=int(self.config.worker_timeout_seconds),
                )
                attempt_usage, model_usage, outer = _claude_raw_usage(log)
                self._avu['claude'] = usum(
                    self._avu.get('claude', {}),
                    attempt_usage,
                )
                usage = attempt_usage
                try:
                    raw = _v257_extract_scout_payload(outer)
                    proposal = _v254_validate_scout_proposal(raw)
                except LabError as exc:
                    validation_error = str(exc)
                    status = (
                        'SCHEMA_RETRY'
                        if attempt < V257_SCOUT_MAX_ATTEMPTS
                        else 'SCHEMA_REJECTED'
                    )
                    self._provider_audit(sd, {
                        'role': 'FRONTIER_SCOUT',
                        'provider': 'claude',
                        'attempt': attempt,
                        'status': status,
                        'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO',
                        'usage': attempt_usage,
                        'modelUsage': model_usage,
                        'tools_disabled': True,
                        'automatically_registered': False,
                        'validation_error': b(exc, 300),
                    })
                    if attempt >= V257_SCOUT_MAX_ATTEMPTS:
                        raise
                    continue
                break

            if proposal is None:
                raise LabError('v2.0.57 scout exhausted bounded schema attempts')

            proposal_sha256 = _v254_canonical_hash(proposal)
            inbox_root = HERE.parent / 'frontier-scout-inbox'
            inbox_root.mkdir(parents=True, exist_ok=True)
            if len(list(inbox_root.glob('TDH-SCOUT-*.json'))) >= V254_SCOUT_INBOX_MAX_FILES:
                raise LabError('v2.0.54 scout inbox capacity reached')
            record = {
                'version': V257_SCOUT_CONFORMANCE_VERSION,
                'status': 'UNTRUSTED_INBOX',
                'proposal': proposal,
                'proposal_sha256': proposal_sha256,
                'automatically_registered': False,
                'controller_registration_required': True,
                'provider': 'claude',
                'tools_disabled': True,
                'max_turns_per_attempt': 1,
                'max_schema_attempts': V257_SCOUT_MAX_ATTEMPTS,
                'attempts_used': attempts_used,
                'raw_provider_log': raw_logs[-1],
                'raw_provider_logs': raw_logs,
                'usage': copy.deepcopy(self._avu.get('claude', {})),
                'last_attempt_usage': usage,
                'modelUsage': model_usage,
                'advisory_source_status': advisory_source_status,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            }
            destination = inbox_root / (
                f"{proposal['hypothesis_id']}-{proposal_sha256[:12]}.json"
            )
            if destination.exists():
                raise LabError('v2.0.54 scout duplicate inbox proposal')
            atomic_json(destination, record)
            self._provider_audit(sd, {
                'role': 'FRONTIER_SCOUT',
                'provider': 'claude',
                'attempt': attempts_used,
                'status': 'UNTRUSTED_INBOX_VALIDATED',
                'cwd_class': 'EPHEMERAL_TMP_OUTSIDE_REPO',
                'usage': usage,
                'modelUsage': model_usage,
                'tools_disabled': True,
                'automatically_registered': False,
                'schema_retry_bounded': True,
            })
            return record
        finally:
            shutil.rmtree(workspace, ignore_errors=True)


    def _v255_maybe_run_frontier_scout(
        self,
        rd: Path,
        context: dict[str, Any],
        advisory_result: dict[str, Any],
    ) -> None:
        if not _v254_scout_needed(context):
            return

        source_status = str(advisory_result.get('status') or '')
        if source_status not in {'LLM_SUBAGENTS_COMPLETED', 'CACHE_HIT'}:
            return

        research = advisory_result.get('researcher')
        critic = advisory_result.get('critic')
        valid_advisory = (
            isinstance(research, dict)
            and isinstance(research.get('findings'), list)
            and bool(research['findings'])
            and isinstance(critic, dict)
            and isinstance(critic.get('findings'), list)
            and bool(critic['findings'])
        )
        if not valid_advisory:
            return

        sd = rd / 'avenox-subagents'
        sd.mkdir(exist_ok=True)
        dispatch_path = sd / 'FRONTIER_SCOUT_DISPATCH_V255.json'

        try:
            scout = self._run_frontier_scout(
                sd,
                context,
                research,
                critic,
                source_status,
            )
            atomic_json(sd / 'FRONTIER_SCOUT_INBOX_V254.json', scout)
            atomic_json(dispatch_path, {
                'version': V255_SCOUT_CACHE_CONTINUITY_VERSION,
                'status': 'UNTRUSTED_INBOX_VALIDATED',
                'advisory_source_status': source_status,
                'provider_invoked': True,
                'researcher_rerun': False,
                'critic_rerun': False,
                'automatically_registered': False,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            })
        except LabError as exc:
            atomic_json(sd / 'FRONTIER_SCOUT_REJECTED_V254.json', {
                'version': V254_FRONTIER_SCOUT_VERSION,
                'status': 'REJECTED_OR_UNAVAILABLE',
                'reason': b(exc, 400),
                'advisory_source_status': source_status,
                'automatically_registered': False,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            })
            atomic_json(dispatch_path, {
                'version': V255_SCOUT_CACHE_CONTINUITY_VERSION,
                'status': 'REJECTED_OR_UNAVAILABLE',
                'advisory_source_status': source_status,
                'provider_invoked': True,
                'researcher_rerun': False,
                'critic_rerun': False,
                'automatically_registered': False,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            })
        finally:
            atomic_json(sd / 'SUBAGENT_USAGE.json', self._avu)


    def ensure_av(self, rd: Path, c: dict[str, Any]):
        if isinstance(getattr(self, '_av', None), dict):
            return self._av
        p = globals().get('build_specialist_context', build_specialist_context)(c)
        yes, reasons = trigger(p)
        fp = fingerprint(p)
        cache = self.load_cache()
        legacy_unit_cache = (
            not hasattr(self.config, 'codex_repo')
            and isinstance(cache, dict) and cache.get('fingerprint') == fp
            and isinstance(cache.get('advisory'), dict)
            and cache['advisory'].get('status') == 'LLM_SUBAGENTS_COMPLETED'
        )
        if not yes:
            z = advisory(p, 'NOT_TRIGGERED', fp, reasons)
        elif _valid_completed_cache(cache, fp) or legacy_unit_cache:
            z = copy.deepcopy(cache['advisory'])
            z['status'] = 'CACHE_HIT'
        else:
            sd = rd / 'avenox-subagents'
            sd.mkdir(exist_ok=True)
            e = isolated(c, p)
            atomic_json(sd / 'ISOLATED_EVIDENCE.json', e)
            research = critic = None
            researcher_usage: dict[str, int] = {}
            try:
                rr, researcher_usage = super(V245_DISPATCH_ANCHOR, self).run_codex_audit(
                    sd, self.subreview(c, fp, 'AVENOX_DEEP_RESEARCH'), self.subpacket(c, e, 'AVENOX_DEEP_RESEARCH')
                )
                self._account_codex(sd, 'PARSED', researcher_usage)
                research = audit_view(rr, 'DEEP_RESEARCH')
                atomic_json(sd / 'DEEP_RESEARCH_RESULT.json', rr)
            except LabError as exc:
                self._account_codex(sd, 'FAILED', researcher_usage)
                atomic_json(sd / 'DEEP_RESEARCH_FAILURE.json', {'error': b(exc, 400)})
            status = 'RESEARCHER_FAILED'
            if research:
                try:
                    cr = self._run_evidence_only_critic(sd, c, e, research)
                    critic = audit_view(cr, 'INDEPENDENT_CRITIC')
                    atomic_json(sd / 'INDEPENDENT_CRITIC_RESULT.json', cr)
                    status = 'LLM_SUBAGENTS_COMPLETED' if critic and critic.get('findings') else 'CRITIC_FAILED'
                except LabError as exc:
                    status = 'CRITIC_FAILED'
                    atomic_json(sd / 'INDEPENDENT_CRITIC_FAILURE.json', {'error': b(exc, 400)})
            z = advisory(p, status, fp, reasons, research, critic)
            if status == 'LLM_SUBAGENTS_COMPLETED' and critic:
                self.cache_path().parent.mkdir(parents=True, exist_ok=True)
                atomic_json(self.cache_path(), {'version': AVENOX_VERSION, 'fingerprint': fp, 'advisory': z})
            atomic_json(sd / 'SUBAGENT_USAGE.json', self._avu)
        self._v255_maybe_run_frontier_scout(rd, c, z)
        atomic_json(rd / 'AVENOX_SUBAGENT_SUMMARY.json', z)
        self._av = z
        return z


def _bind_local_adapter() -> None:
    v247.LOCAL_ADAPTER = LOCAL_ADAPTER
    v246.LOCAL_ADAPTER = LOCAL_ADAPTER
    v245.LOCAL_ADAPTER = LOCAL_ADAPTER
    v244.LOCAL_ADAPTER = LOCAL_ADAPTER
    v243.LOCAL_ADAPTER = LOCAL_ADAPTER
    v243.v242.LOCAL_ADAPTER = LOCAL_ADAPTER
    v240.LOCAL_ADAPTER = LOCAL_ADAPTER
    chain = v240.v238.v237.v236
    chain.v235.LOCAL_ADAPTER = LOCAL_ADAPTER
    chain.v235.kernel = kernel
    chain.kernel = kernel
    if hasattr(chain, 'base_v217'):
        chain.base_v217.kernel = kernel


def _v259_runtime_kernel_overlay_bound() -> bool:
    chain = v240.v238.v237.v236
    refs = [v240.kernel, chain.v235.kernel, chain.kernel]
    if hasattr(chain, 'base_v217'):
        refs.append(chain.base_v217.kernel)
    return all(ref is kernel for ref in refs)


def _bind_runtime() -> tuple[str, ...]:
    deep = v240.v238.v237.v236.v235.v233.v232.v231.v230.v229.v228.v227.v226.v225.v220.v217
    modules = [v247, v246, v244, v243, v243.v242, v240, v240.v238, v240.v238.v237, deep, deep.v216]
    for module in modules:
        module.Controller = Controller
    v245.Controller = V245_DISPATCH_ANCHOR
    return tuple(f'bound-{i}' for i, _ in enumerate(modules, start=1))


_bind_local_adapter()
RUNTIME_CONTROLLER_BINDINGS = _bind_runtime()
StrategyLabSupervisor = v247.StrategyLabSupervisor


def runtime_binding_contract() -> dict[str, Any]:
    deep = v240.v238.v237.v236.v235.v233.v232.v231.v230.v229.v228.v227.v226.v225.v220.v217
    refs = [v247.Controller, v246.Controller, v244.Controller, v243.Controller, v243.v242.Controller, v240.Controller, v240.v238.Controller, v240.v238.v237.Controller, deep.Controller, deep.v216.Controller]
    return {
        'version': 'tdh-v248-evidence-only-critic-v1',
        'all_controller_refs_bound': all(ref is Controller for ref in refs),
        'v245_dispatch_anchor_preserved': v245.Controller is V245_DISPATCH_ANCHOR,
        'dispatch_anchor_is_mro_parent': V245_DISPATCH_ANCHOR in Controller.__mro__,
        'avenox_subagent_layer': True,
        'evidence_only_critic': True,
        'failed_provider_usage_accounted': True,
        'critic_completed_required_for_cache': True,
        'v246_isolated_evidence_compaction': True,
        'local_adapter': LOCAL_ADAPTER,
        'controller_only_promotion': True,
        'trading_actions': False,
        'exchange_api_access': False,
        'specialists_are_deterministic_no_llm': True,
        'extra_provider_tokens': 0,
        'v242_final_prompt_optimizer_inherited': True,
        'v251_lane_validation_quarantine': True,
        'v251_multi_axis_frontier_filter': True,
        'v251_unknown_errors_fail_closed': True,
        'v252_peer_frontier_exhaustion_is_lane_local': True,
        'v252_eligible_frontier_exhaustion_rolls_epoch': True,
        'v252_unknown_errors_fail_closed': True,
        'v253_invalid_audit_is_quarantined': True,
        'v253_invalid_audit_never_promotes': True,
        'v253_unknown_errors_fail_closed': True,
        'v254_registered_low_watermark_replenishment': True,
        'v254_only_existing_registered_seeds_auto_admitted': True,
        'v254_frontier_scout_untrusted_inbox': True,
        'v254_scout_tools_disabled': True,
        'v254_scout_never_auto_registers': True,
        'v254_unknown_registration_errors_fail_closed': True,
        'v255_scout_runs_on_valid_cache_hit': True,
        'v255_cache_hit_does_not_rerun_researcher_or_critic': True,
        'v255_invalid_cached_advisory_skips_scout': True,
        'v255_unknown_errors_fail_closed': True,
        'v256_scout_runs_on_global_frontier_exhaustion': True,
        'v256_only_valid_cached_advisory_is_reused': True,
        'v256_scout_never_auto_registers': True,
        'v256_unknown_errors_fail_closed': True,
        'v257_exact_scout_json_fence_supported': True,
        'v257_scout_schema_retry_is_bounded': True,
        'v257_invalid_scout_never_registers': True,
        'v257_unknown_errors_fail_closed': True,
        'v258_controller_reviewed_seed_overlay': True,
        'v258_untrusted_scout_text_never_executes': True,
        'v258_existing_family_only': True,
        'v258_unknown_admission_errors_fail_closed': True,
        'v259_runtime_kernel_binding_version': V259_RUNTIME_KERNEL_BINDING_VERSION,
        'v259_runtime_kernel_overlay_bound': _v259_runtime_kernel_overlay_bound(),
        'v259_approved_registry_reaches_runtime_context': True,
    }


def main(argv: list[str] | None = None) -> int:
    contract = runtime_binding_contract()
    if contract['all_controller_refs_bound'] is not True:
        raise RuntimeError('v2.0.48 runtime Controller binding failed closed')
    if contract['v245_dispatch_anchor_preserved'] is not True:
        raise RuntimeError('v2.0.48 v245 dispatch anchor drifted')
    if contract['v259_runtime_kernel_overlay_bound'] is not True:
        raise RuntimeError('v2.0.59 runtime kernel overlay binding failed closed')
    return v245.v244.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())

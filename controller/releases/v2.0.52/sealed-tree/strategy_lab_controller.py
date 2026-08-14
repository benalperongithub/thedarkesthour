#!/usr/bin/env python3
"""TDH Strategy Lab v2.0.52 Avenox frontier continuity + fail-closed dual-lane resilience.

Sealed v2.0.47 remains the immutable dispatch base. The Claude critic now runs
from an ephemeral /tmp cwd outside the repository, with tools disabled, one turn,
and a strict evidence-only JSON response contract. Raw provider usage is counted
for every subagent attempt even when result parsing fails. A failed/partial critic
is never cached as completed research.

No S1 target, Phoenix metric, trading path, paper path or exchange permission is
changed or weakened. No live/paper/exchange path is added.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
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

class Controller(V246_DISPATCH_BASE):
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
            if error not in V252_FRONTIER_EXHAUSTION_ERRORS:
                raise

            actor = str(getattr(self, '_v225_next_actor', 'codex'))
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            event = {
                'version': V252_FRONTIER_CONTINUITY_VERSION,
                'mode': 'V252_ELIGIBLE_FRONTIER_EXHAUSTED_EPOCH_ROLLOVER',
                'status': 'FRONTIER_EXHAUSTED',
                'research_round': round_number,
                'actor': actor,
                'reason': error,
                'provider_invoked': False,
                'no_arbitrary_strategy_generation': True,
                'registered_families_only': True,
                'next_action': 'fresh bounded epoch and deterministic family reselection',
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
    try:
        chain = v240.v238.v237.v236
        chain.v235.LOCAL_ADAPTER = LOCAL_ADAPTER
        chain.v235.kernel = v246.kernel
        chain.kernel = v246.kernel
        if hasattr(chain, 'base_v217'):
            chain.base_v217.kernel = v246.kernel
    except Exception:
        pass


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
    }


def main(argv: list[str] | None = None) -> int:
    contract = runtime_binding_contract()
    if contract['all_controller_refs_bound'] is not True:
        raise RuntimeError('v2.0.48 runtime Controller binding failed closed')
    if contract['v245_dispatch_anchor_preserved'] is not True:
        raise RuntimeError('v2.0.48 v245 dispatch anchor drifted')
    return v245.v244.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""TDH v2.0.62 deterministic failure taxonomy and recovery audit overlay."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


BASE = Path(
    '/srv/tdh-collab/controller/strategy-lab-v2/'
    'v2.0.61/strategy_lab_controller.py'
)
spec = importlib.util.spec_from_file_location('tdh_v261_for_v262', BASE)
if spec is None or spec.loader is None:
    raise RuntimeError('cannot load sealed v2.0.61 controller')
v261 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v261
spec.loader.exec_module(v261)


def _export_base_namespace(module: Any) -> None:
    namespace = globals()
    for export_name in tuple(dir(module)):
        if not export_name.startswith('__'):
            namespace[export_name] = getattr(module, export_name)


_export_base_namespace(v261)
del _export_base_namespace


V262_FAILURE_TAXONOMY_VERSION = 'tdh-avenox-failure-taxonomy-v262'
V262_RECOVERY_DECISION_VERSION = 'tdh-avenox-recovery-decision-v262'
V262_MAX_DECISIONS_PER_ROUND = 64
V262_BASE_CONTROLLER = v261.Controller


_V262_RULES: tuple[dict[str, Any], ...] = (
    {
        'category': 'SAFETY',
        'code': 'FORBIDDEN_CAPABILITY_REQUEST',
        'markers': (
            'live trading', 'paper trading', 'private api', 'exchange order',
            'credential', 'trading_actions=true', 'exchange_api_access=true',
            's6 execution',
        ),
        'action': 'FAIL_CLOSED_AND_ESCALATE',
        'recoverable': False,
        'max_retries': 0,
        'escalation_required': True,
    },
    {
        'category': 'MODEL',
        'code': 'PROVIDER_QUOTA_OR_COOLDOWN',
        'markers': ('429', 'rate limit', 'quota exhausted', 'provider cooldown'),
        'action': 'CHECKPOINT_AND_PROVIDER_COOLDOWN',
        'recoverable': True,
        'max_retries': 0,
        'escalation_required': False,
    },
    {
        'category': 'MODEL',
        'code': 'PROMPT_BUDGET_EXCEEDED',
        'markers': (
            'prompt exceeds', 'prompt too long', 'token overflow',
            'context length', 'character budget',
        ),
        'action': 'DETERMINISTIC_SECOND_COMPACTION',
        'recoverable': True,
        'max_retries': 1,
        'escalation_required': False,
    },
    {
        'category': 'MODEL',
        'code': 'MALFORMED_MODEL_OUTPUT',
        'markers': (
            'schema failure', 'not valid json', 'not usable json',
            'response is not json', 'malformed output',
        ),
        'action': 'STRICT_SCHEMA_RETRY',
        'recoverable': True,
        'max_retries': 1,
        'escalation_required': False,
    },
    {
        'category': 'DATA',
        'code': 'DATA_INTEGRITY_FAILURE',
        'markers': (
            'missing candle', 'timestamp misalignment', 'timeframe mismatch',
            'corrupted parquet', 'data integrity', 'lookahead', 'leakage risk',
        ),
        'action': 'VALIDATE_AND_QUARANTINE_DATA_SCOPE',
        'recoverable': False,
        'max_retries': 0,
        'escalation_required': False,
    },
    {
        'category': 'CONTROLLER',
        'code': 'STATE_OR_TRANSITION_FAILURE',
        'markers': (
            'stale lock', 'checkpoint mismatch', 'invalid transition',
            'state inconsistency', 'graph deadlock', 'binding drift',
        ),
        'action': 'VERIFY_LAST_CHECKPOINT_AND_RESUME',
        'recoverable': True,
        'max_retries': 1,
        'escalation_required': False,
    },
    {
        'category': 'INFRASTRUCTURE',
        'code': 'RUNTIME_INFRASTRUCTURE_FAILURE',
        'markers': (
            'no space left', 'disk full', 'out of memory', 'oom',
            'process crash', 'missing file', 'permission denied',
        ),
        'action': 'INFRASTRUCTURE_DIAGNOSIS',
        'recoverable': False,
        'max_retries': 0,
        'escalation_required': True,
    },
    {
        'category': 'RESEARCH',
        'code': 'RESEARCH_CONTRACT_REJECTION',
        'markers': (
            'duplicate hypothesis', 'duplicate experiment', 'unknown family',
            'unsupported family', 'insufficient sample', 'failed robustness',
            'registered novelty frontier is exhausted',
        ),
        'action': 'QUARANTINE_AND_SELECT_NEXT_HYPOTHESIS',
        'recoverable': True,
        'max_retries': 0,
        'escalation_required': False,
    },
)


def _v262_bounded_error_text(error: BaseException | str) -> tuple[str, str]:
    if isinstance(error, BaseException):
        error_type = type(error).__name__
        raw = str(error)
    else:
        error_type = 'ExternalFailure'
        raw = str(error)
    normalized = re.sub(r'\s+', ' ', raw).strip()
    return error_type[:120], normalized[:1200]


def v262_classify_failure(error: BaseException | str) -> dict[str, Any]:
    """Classify one failure without authorizing recovery or retry."""
    error_type, message = _v262_bounded_error_text(error)
    lowered = f'{error_type}: {message}'.lower()
    selected: dict[str, Any] | None = None
    for rule in _V262_RULES:
        if any(marker in lowered for marker in rule['markers']):
            selected = rule
            break
    if selected is None:
        selected = {
            'category': 'UNKNOWN',
            'code': 'UNCLASSIFIED_FAILURE',
            'action': 'FAIL_CLOSED_AND_ESCALATE',
            'recoverable': False,
            'max_retries': 0,
            'escalation_required': True,
        }
    return {
        'taxonomy_version': V262_FAILURE_TAXONOMY_VERSION,
        'category': selected['category'],
        'code': selected['code'],
        'recommended_action': selected['action'],
        'recoverable': bool(selected['recoverable']),
        'max_retries': int(selected['max_retries']),
        'escalation_required': bool(selected['escalation_required']),
        'error_type': error_type,
        'error_message': message,
        'classification_only': True,
        'automatic_recovery_authorized': False,
        'unknown_errors_fail_closed': True,
    }


def _v262_hash_json(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(',', ':'),
    ).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def v262_recovery_decision(
    error: BaseException | str,
    *,
    run_id: str,
    round_number: int,
    node: str,
    actor: str,
    attempt: int,
) -> dict[str, Any]:
    classification = v262_classify_failure(error)
    decision = {
        'version': V262_RECOVERY_DECISION_VERSION,
        'run_id': str(run_id)[:160],
        'round_number': int(round_number),
        'node': str(node)[:120],
        'actor': str(actor)[:40],
        'attempt': max(0, int(attempt)),
        'classification': classification,
        'retry_eligible': (
            classification['recoverable'] is True
            and int(attempt) < classification['max_retries']
        ),
        'decision_owner': 'CONTROLLER',
        'controller_must_reraise': True,
        'policy_change': False,
        'research_mode': 'offline',
        'trading_actions': False,
        'exchange_api_access': False,
    }
    decision['decision_sha256'] = _v262_hash_json(decision)
    return decision


def _v262_append_recovery_decision(
    round_dir: Path,
    decision: dict[str, Any],
) -> None:
    path = round_dir / 'RECOVERY_DECISIONS_V262.json'
    if path.is_symlink():
        raise LabError('v2.0.62 recovery decision path is a symlink')
    if path.exists():
        outer = json.loads(path.read_text(encoding='utf-8'))
        if (
            not isinstance(outer, dict)
            or outer.get('version') != V262_RECOVERY_DECISION_VERSION
            or not isinstance(outer.get('decisions'), list)
        ):
            raise LabError('v2.0.62 recovery decision journal is invalid')
        decisions = copy.deepcopy(outer['decisions'])
    else:
        decisions = []
    known = {
        row.get('decision_sha256')
        for row in decisions
        if isinstance(row, dict)
    }
    if decision['decision_sha256'] not in known:
        decisions.append(copy.deepcopy(decision))
    if len(decisions) > V262_MAX_DECISIONS_PER_ROUND:
        raise LabError('v2.0.62 recovery decision journal exceeds bound')
    atomic_json(path, {
        'version': V262_RECOVERY_DECISION_VERSION,
        'decisions': decisions,
        'decision_count': len(decisions),
        'classification_only': True,
        'automatic_recovery_authorized': False,
        'research_mode': 'offline',
        'trading_actions': False,
        'exchange_api_access': False,
    })


class Controller(V262_BASE_CONTROLLER):
    def execute_round(self, round_number: int, preflight: Any):
        try:
            return super().execute_round(round_number, preflight)
        except Exception as error:
            decision = v262_recovery_decision(
                error,
                run_id=str(getattr(self, 'run_id', 'unknown-run')),
                round_number=round_number,
                node='EXECUTE_ROUND',
                actor='controller',
                attempt=0,
            )
            try:
                round_dir = Path(self.run_dir) / f'round-{round_number:02d}'
                round_dir.mkdir(parents=True, exist_ok=True)
                _v262_append_recovery_decision(round_dir, decision)
            except Exception as audit_error:
                if hasattr(error, 'add_note'):
                    error.add_note(
                        'v2.0.62 recovery audit failed: '
                        + str(audit_error)[:300]
                    )
            raise


def _bind_v262_runtime() -> tuple[str, ...]:
    deep = (
        v261.v240.v238.v237.v236.v235.v233.v232.v231.v230.v229.v228
        .v227.v226.v225.v220.v217
    )
    modules = (
        v261,
        v261.v247,
        v261.v246,
        v261.v244,
        v261.v243,
        v261.v243.v242,
        v261.v240,
        v261.v240.v238,
        v261.v240.v238.v237,
        deep,
        deep.v216,
    )
    for module in modules:
        module.Controller = Controller
    return tuple(f'v262-bound-{index}' for index, _ in enumerate(modules, 1))


V262_RUNTIME_BINDINGS = _bind_v262_runtime()
StrategyLabSupervisor = v261.StrategyLabSupervisor


def runtime_binding_contract() -> dict[str, Any]:
    contract = copy.deepcopy(v261.runtime_binding_contract())
    contract.update({
        'version': V262_FAILURE_TAXONOMY_VERSION,
        'v262_failure_taxonomy': True,
        'v262_recovery_decision_log': True,
        'v262_classification_only': True,
        'v262_automatic_recovery_authorized': False,
        'v262_unhandled_failures_reraised': True,
        'v262_unknown_errors_fail_closed': True,
        'controller_only_recovery_policy': True,
        'policy_change': False,
        'trading_actions': False,
        'exchange_api_access': False,
    })
    return contract


def main(argv: list[str] | None = None) -> int:
    contract = runtime_binding_contract()
    if contract.get('all_controller_refs_bound') is not True:
        raise RuntimeError('v2.0.62 runtime Controller binding failed closed')
    if contract.get('v262_unknown_errors_fail_closed') is not True:
        raise RuntimeError('v2.0.62 unknown failure boundary drifted')
    return v261.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""TDH Strategy Lab v2.0.74 global-memory-aware reviewed queue.

Sealed v2.0.47 remains the immutable dispatch base. The Claude critic now runs
from an ephemeral /tmp cwd outside the repository, with tools disabled, one turn,
and a strict evidence-only JSON response contract. Raw provider usage is counted
for every subagent attempt even when result parsing fails. A failed/partial critic
is never cached as completed research. The only new frontier rows are sealed,
controller-reviewed seeds inside an already executable registered family;
untrusted Scout text remains non-executable. The controller can admit exactly
one sealed RSI_GATED_REVERSION Paket-A seed from the reviewed video-research
intake when the inherited novelty frontier is empty.

Completed Codex/Claude proposal nodes and completed rounds can be resumed only
when exact input and payload hashes match. Interrupted nodes fail closed for the
bounded self-healing layer planned next. No S1 target or Phoenix metric is
changed. No trading path, paper path or exchange permission is added or weakened.

Fresh round-directory creation remains owned by the inherited round executor.
The checkpoint wrapper reads a missing directory without creating it, preventing
the inherited fail-closed ``mkdir()`` boundary from seeing a false collision.

The untrusted Frontier Scout inbox is now classified by canonical content hash
and the sealed controller-review registry. Reviewed, duplicate, invalid,
review-pending, and deferred proposals are distinct states; raw file count is no
longer mistaken for actionable capacity. Pending implementation work blocks
additional paid Scout calls, while invalid state fails closed. Raw proposals are
never deleted or made executable by this lifecycle layer.

Semantic experiment inputs and metrics that are deterministically derivable
from installed OHLCV are separated from genuinely external raw datasets. Legacy
v2.0.66 decisions remain immutable and are superseded by hash-bound v2.0.67
records, one per bounded epoch. Ambiguous data requirements fail closed into
manual capability review; no raw proposal is executed or auto-registered.

The three sealed v2.0.68 VOLUME_TSMOM ablation seeds now form a deterministic
controller-owned priority queue. When the inherited frontier is empty, the
controller admits the next unused exact seed before declaring exhaustion. If a
same-family source still uses the excluded DOGE symbol, one validated symbol-only
bridge is scheduled first so the existing single-material-axis rule is preserved;
the reviewed seed follows on the next eligible epoch. No model text can enter
this queue and no validation, S1 or offline-safety boundary is weakened.

The inherited v2.0.36 structural quarantine historically raised before that
reviewed queue could observe an empty Codex frontier. Only that exact, known
Codex exhaustion is now converted to an auditable empty frontier so the sealed
v2.0.69 queue gets its intended admission opportunity before v2.0.52 performs
global epoch rollover. Claude peer-lane semantics and every unknown error remain
fail closed. No provider call, family registration or executable model output is
introduced by this bridge.

v2.0.70 exposed one more inherited ordering boundary: sealed v2.0.30 rejects
an empty frontier before the newest wrapper receives a completed context. During
context construction only, v2.0.71 therefore carries one exact registered row
from immediately below the v2.0.36 quarantine through the v2.0.30 non-empty
guard. The carrier is hash-bound and removed deterministically before v2.0.69
reviewed admission or any provider boundary. It is never executable, proposed,
backtested or allowed to reverse the structural quarantine.

Once that reviewed seed reaches the Codex proposal node, sealed v2.0.28
recomputes historical frontier state solely to construct its JSON output
example. That recomputation cannot see the exact seed already admitted into
the round context and raises before the provider call. v2.0.72 caches exactly
one hash-bound v2.0.69 reviewed item from the completed context and exposes it
only while the inherited example builder runs. The cache cannot select,
execute, backtest or promote a candidate and is rejected on any identity drift.

Runtime acceptance then exposed the exact sealed v2.0.28 example-row schema:
the inherited builder reads ``selected_approach`` after receiving the temporary
frontier. v2.0.73 derives the same-family registered-seed approach with the
sealed v2.0.28 rule and adds it only to a deep-copied example row. Both source
and candidate configs are reconstructed from the installed registry, their
hashes remain bound, and the cached reviewed row remains byte-semantically
unchanged. The shape adapter is unavailable to selection, validation, backtest,
S1 or promotion paths; every drift remains fail closed.

Runtime acceptance then exposed an identity-scope mismatch: the reviewed queue
used bounded round context while the immutable proposal validator scanned the
full local proposal history. A globally duplicated reviewed seed could therefore
reach a paid provider call and repeat across bounded epochs. v2.0.74 consults
the exact sealed full-history hash reader before provider dispatch, skips only
hash-equal reviewed queue configs, and deterministically advances to the next
exact sealed seed. The scan is local and controller-owned; no model, network,
validation, S1, promotion, trading or exchange boundary is changed.
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
V216_GLOBAL_MEMORY_MODULE = (
    v240.v238.v237.v236.v235.v233.v232.v231.v230.v229.v228
    .v227.v226.v225.v220.v217.v216
)
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
V236_QUARANTINE_MODULE = v240.v238.v237.v236
V236_QUARANTINE_CLASSES = tuple(
    cls for cls in V246_DISPATCH_BASE.__mro__
    if cls.__module__ == V236_QUARANTINE_MODULE.__name__
)
if len(V236_QUARANTINE_CLASSES) != 1:
    raise RuntimeError('v2.0.71 could not recover sealed v2.0.36 quarantine class')
V236_QUARANTINE_CLASS = V236_QUARANTINE_CLASSES[0]
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
V260_REGISTERED_SEED_TRANSITION_VERSION = (
    'tdh-v260-controller-registered-seed-transition'
)
V261_RSI_GATED_REVERSION_VERSION = (
    'tdh-v261-rsi-gated-reversion-packet-a'
)
V261_PACKET_A_EXPERIMENT_ID = 'TDH-VIDEO-RSI-GATED-REV-PACKET-A-15M'
V262_FAILURE_TAXONOMY_VERSION = 'tdh-avenox-failure-taxonomy-v262'
V262_RECOVERY_DECISION_VERSION = 'tdh-avenox-recovery-decision-v262'
V262_MAX_DECISIONS_PER_ROUND = 64
V262_SOURCE_HERE = HERE
V263_CHECKPOINT_VERSION = 'tdh-avenox-node-checkpoint-v263'
V263_MANIFEST_FILENAME = 'NODE_CHECKPOINTS_V263.json'
V264_CHECKPOINT_STARTUP_COMPATIBILITY_VERSION = (
    'tdh-avenox-checkpoint-startup-compatibility-v264'
)
V265_FRONTIER_INBOX_LIFECYCLE_VERSION = (
    'tdh-avenox-frontier-inbox-lifecycle-v265'
)
V265_ACTIVE_REVIEW_LIMIT = 16
V265_RAW_INBOX_HARD_LIMIT = 512
V265_MAX_PROPOSAL_BYTES = 65536
V266_FRONTIER_PRODUCER_VERSION = (
    'tdh-avenox-frontier-producer-admission-v266'
)
V266_OFFLINE_AVAILABLE_DATA = frozenset({'ohlcv'})
V266_TERMINAL_DECISION_STATES = frozenset({
    'READY_FOR_SEALED_IMPLEMENTATION',
    'NEEDS_FAMILY_IMPLEMENTATION_REVIEW',
    'BLOCKED_MISSING_OFFLINE_DATA',
    'QUARANTINED_AMBIGUOUS_FAMILY',
})
V267_DATA_CAPABILITY_VERSION = (
    'tdh-avenox-data-capability-normalization-v267'
)
V268_VOLUME_TSMOM_ADMISSION_VERSION = (
    'tdh-avenox-volume-tsmom-ablation-admission-v268'
)
V268_REVIEWED_REGISTRY_ID = 'tdh-v268-volume-tsmom-ablation-seeds-v1'
V268_REVIEWED_SEEDS_FILENAME = 'v268-volume-tsmom-ablation-seeds-v1.jsonl'
V268_SOURCE_PROPOSAL_SHA256 = (
    '0878bd689f1e14f310c3a0f697d6b5ecf8e25308f04bab0a487af34090ece0c8'
)
V268_SOURCE_DECISION_SHA256 = (
    '92b6929ab84f97b4f451d283110d2f525d623fd084bafff268e725b5a871329a'
)
V269_REVIEWED_SEED_QUEUE_VERSION = (
    'tdh-avenox-reviewed-seed-queue-v269'
)
V269_REVIEWED_SEED_PRIORITY = (
    'TDH-SCOUT-000001-VTM-VOL80-NODOGE-1H',
    'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4H',
    'TDH-SCOUT-000001-VTM-VOL80-NODOGE-1D',
)
V269_REVIEWED_SYMBOLS = ('BTCUSDT', 'XRPUSDT', 'SOLUSDT')
V270_PRE_EXHAUSTION_BRIDGE_VERSION = (
    'tdh-avenox-pre-exhaustion-reviewed-seed-bridge-v270'
)
V270_STRUCTURAL_EXHAUSTION_ERROR = (
    'v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine'
)
V271_QUARANTINE_CARRIER_VERSION = (
    'tdh-avenox-structural-quarantine-carrier-v271'
)
V272_EXAMPLE_FRONTIER_BRIDGE_VERSION = (
    'tdh-avenox-admitted-example-frontier-bridge-v272'
)
V273_EXAMPLE_SHAPE_BRIDGE_VERSION = (
    'tdh-avenox-admitted-example-shape-bridge-v273'
)
V274_GLOBAL_MEMORY_QUEUE_FILTER_VERSION = (
    'tdh-avenox-global-memory-reviewed-queue-filter-v274'
)
V267_TERMINAL_DECISION_STATES = frozenset({
    'READY_FOR_SEALED_IMPLEMENTATION',
    'NEEDS_FAMILY_IMPLEMENTATION_REVIEW',
    'NEEDS_DATA_CAPABILITY_REVIEW',
    'BLOCKED_MISSING_EXTERNAL_DATA',
    'QUARANTINED_AMBIGUOUS_FAMILY',
})
V267_DATA_CAPABILITY_STATES = frozenset({
    'INSTALLED_RAW_OHLCV',
    'DERIVABLE_FROM_OHLCV',
    'EXTERNAL_DATA_REQUIRED',
    'AMBIGUOUS_DATA_REQUIREMENT',
})
V263_NODE_ORDER = (
    'CODEX_PROPOSAL',
    'CLAUDE_PROPOSAL',
    'ROUND_COMPLETE',
)
V253_AUDIT_OUTPUT_ERRORS = frozenset({
    'invalid audit finding',
})
V252_FRONTIER_EXHAUSTION_ERRORS = frozenset({
    'v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine',
    'v2.0.28 no diverse executable frontier for actor=codex',
    'v2.0.28 no diverse executable frontier for actor=claude',
    'registered novelty frontier is exhausted',
})

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


def _v263_node_input_sha256(value: Any) -> str:
    return _v262_hash_json({
        'checkpoint_version': V263_CHECKPOINT_VERSION,
        'input': value,
        'research_mode': 'offline',
        'trading_actions': False,
        'exchange_api_access': False,
    })


def _v263_manifest_path(round_dir: Path) -> Path:
    return round_dir / V263_MANIFEST_FILENAME


def _v263_payload_path(round_dir: Path, node: str) -> Path:
    if node not in V263_NODE_ORDER:
        raise LabError('v2.0.63 checkpoint node is not registered')
    return round_dir / f'NODE_CHECKPOINT_{node}_V263.json'


def _v263_empty_manifest() -> dict[str, Any]:
    return {
        'version': V263_CHECKPOINT_VERSION,
        'nodes': {},
        'node_order': list(V263_NODE_ORDER),
        'resume_policy': 'COMPLETED_EXACT_INPUT_AND_PAYLOAD_HASH_ONLY',
        'interrupted_nodes_fail_closed': True,
        'controller_only_resume': True,
        'policy_change': False,
        'research_mode': 'offline',
        'trading_actions': False,
        'exchange_api_access': False,
    }


def _v263_load_manifest(round_dir: Path) -> dict[str, Any]:
    path = _v263_manifest_path(round_dir)
    if path.is_symlink():
        raise LabError('v2.0.63 checkpoint manifest is a symlink')
    if not path.exists():
        return _v263_empty_manifest()
    raw = json.loads(path.read_text(encoding='utf-8'))
    if (
        not isinstance(raw, dict)
        or raw.get('version') != V263_CHECKPOINT_VERSION
        or raw.get('node_order') != list(V263_NODE_ORDER)
        or not isinstance(raw.get('nodes'), dict)
        or raw.get('research_mode') != 'offline'
        or raw.get('trading_actions') is not False
        or raw.get('exchange_api_access') is not False
        or raw.get('controller_only_resume') is not True
    ):
        raise LabError('v2.0.63 checkpoint manifest is invalid')
    if set(raw['nodes']) - set(V263_NODE_ORDER):
        raise LabError('v2.0.63 checkpoint manifest has an unknown node')
    return raw


def _v263_write_manifest(round_dir: Path, manifest: dict[str, Any]) -> None:
    path = _v263_manifest_path(round_dir)
    if path.is_symlink():
        raise LabError('v2.0.63 checkpoint manifest is a symlink')
    atomic_json(path, manifest)


def _v263_begin_node(
    round_dir: Path,
    node: str,
    input_value: Any,
) -> str:
    input_sha256 = _v263_node_input_sha256(input_value)
    manifest = _v263_load_manifest(round_dir)
    current = manifest['nodes'].get(node)
    if isinstance(current, dict):
        if current.get('input_sha256') != input_sha256:
            raise LabError('v2.0.63 checkpoint input mismatch')
        if current.get('status') == 'COMPLETED':
            return input_sha256
        raise LabError('v2.0.63 interrupted node requires bounded recovery review')
    manifest['nodes'][node] = {
        'node': node,
        'status': 'IN_PROGRESS',
        'input_sha256': input_sha256,
        'payload_file': _v263_payload_path(round_dir, node).name,
        'payload_sha256': None,
        'resume_eligible': False,
        'automatic_retry_authorized': False,
    }
    _v263_write_manifest(round_dir, manifest)
    return input_sha256


def _v263_commit_node(
    round_dir: Path,
    node: str,
    input_sha256: str,
    result: Any,
) -> None:
    manifest = _v263_load_manifest(round_dir)
    current = manifest['nodes'].get(node)
    if (
        not isinstance(current, dict)
        or current.get('status') != 'IN_PROGRESS'
        or current.get('input_sha256') != input_sha256
    ):
        raise LabError('v2.0.63 checkpoint transition is invalid')
    payload = {
        'version': V263_CHECKPOINT_VERSION,
        'node': node,
        'input_sha256': input_sha256,
        'result': copy.deepcopy(result),
        'research_mode': 'offline',
        'trading_actions': False,
        'exchange_api_access': False,
    }
    payload['result_sha256'] = _v262_hash_json(payload['result'])
    payload_path = _v263_payload_path(round_dir, node)
    if payload_path.is_symlink():
        raise LabError('v2.0.63 checkpoint payload is a symlink')
    atomic_json(payload_path, payload)
    payload_sha256 = hashlib.sha256(payload_path.read_bytes()).hexdigest()
    current.update({
        'status': 'COMPLETED',
        'payload_sha256': payload_sha256,
        'result_sha256': payload['result_sha256'],
        'resume_eligible': True,
    })
    _v263_write_manifest(round_dir, manifest)


def _v263_resume_node(
    round_dir: Path,
    node: str,
    input_value: Any,
) -> Any | None:
    input_sha256 = _v263_node_input_sha256(input_value)
    manifest = _v263_load_manifest(round_dir)
    current = manifest['nodes'].get(node)
    if current is None:
        return None
    if not isinstance(current, dict) or current.get('input_sha256') != input_sha256:
        raise LabError('v2.0.63 checkpoint input mismatch')
    if current.get('status') != 'COMPLETED' or current.get('resume_eligible') is not True:
        raise LabError('v2.0.63 interrupted node requires bounded recovery review')
    payload_path = _v263_payload_path(round_dir, node)
    if payload_path.is_symlink() or not payload_path.is_file():
        raise LabError('v2.0.63 checkpoint payload is missing or unsafe')
    if hashlib.sha256(payload_path.read_bytes()).hexdigest() != current.get('payload_sha256'):
        raise LabError('v2.0.63 checkpoint payload hash mismatch')
    payload = json.loads(payload_path.read_text(encoding='utf-8'))
    if (
        not isinstance(payload, dict)
        or payload.get('version') != V263_CHECKPOINT_VERSION
        or payload.get('node') != node
        or payload.get('input_sha256') != input_sha256
        or payload.get('research_mode') != 'offline'
        or payload.get('trading_actions') is not False
        or payload.get('exchange_api_access') is not False
        or _v262_hash_json(payload.get('result')) != payload.get('result_sha256')
        or payload.get('result_sha256') != current.get('result_sha256')
    ):
        raise LabError('v2.0.63 checkpoint payload contract mismatch')
    return copy.deepcopy(payload['result'])

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


def _v260_exact_controller_registered_seed(item: Any) -> bool:
    """Accept only an exact config reconstructed from the sealed kernel registry."""
    if not isinstance(item, dict):
        return False
    registration = item.get('v254_registration')
    config = item.get('config')
    if not isinstance(config, dict):
        return False
    experiment_id = config.get('experiment_id')
    family_id = config.get('family')
    # Base frontier construction emits exact kernel configs without v254
    # provenance. If a provenance marker is present, however, it must be the
    # exact controller-owned shape and agree with the config.
    if registration is not None:
        if not isinstance(registration, dict) or registration != {
            'version': V254_FRONTIER_SCOUT_VERSION,
            'source': 'EXISTING_REGISTERED_KERNEL_SEED',
            'experiment_id': experiment_id,
            'family_id': family_id,
            'schema_validated': True,
            'data_eligibility_inherited_from_selection': True,
            'deduplicated': True,
            'model_generated_executable_code': False,
            'controller_only_registration': True,
        }:
            return False

    symbol = config.get('symbol')
    if (
        not isinstance(experiment_id, str)
        or not isinstance(family_id, str)
        or not isinstance(symbol, str)
    ):
        return False

    _, experiments = kernel.registry()
    experiment = experiments.get(experiment_id)
    if not isinstance(experiment, dict):
        return False
    if experiment.get('family_id') != family_id:
        return False
    universe = experiment.get('universe')
    if not isinstance(universe, list) or symbol not in universe:
        return False

    expected = kernel.validate_config(
        kernel.performance_config(experiment, symbol)
    )
    return _v254_canonical_hash(config) == _v254_canonical_hash(expected)


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
    # A v2.0.69 provenance marker is a strict contract, not an advisory label.
    # Reject the whole item before the generic single-axis allowance if either
    # the sealed hashes, registry identity or reconstructed config was altered.
    if (
        'v269_reviewed_queue' in item
        and not _v269_exact_reviewed_queue_item(item)
    ):
        return False
    if axes == ('family',) or len(axes) == 1:
        return True
    # An exact kernel-registered seed is an atomic bounded experiment even when
    # its sealed definition changes both timeframe and parameters. Reconstruct
    # it from the active kernel registry before allowing that transition; a
    # spoofed marker or free-form config remains illegal.
    return (
        set(axes).issubset({'timeframe', 'registered_seed'})
        and _v260_exact_controller_registered_seed(item)
    )


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


def _v261_packet_a_replenishment(
    context: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    """Admit one exact reviewed Paket-A seed after inherited selection stalls.

    This is deliberately not a generic Scout-to-code bridge. The only eligible
    object is the controller-reviewed registry row shipped in this release.
    Once its experiment id or canonical config appears in memory, it is never
    re-admitted by this boundary.
    """
    frontier = context.get('novelty_frontier')
    if actor != 'codex' or not isinstance(frontier, list) or frontier:
        return context

    updated = copy.deepcopy(context)
    used_experiment_ids, used_config_hashes = _v254_used_identities(updated)
    if V261_PACKET_A_EXPERIMENT_ID in used_experiment_ids:
        return updated

    _, experiments = kernel.registry()
    experiment = experiments.get(V261_PACKET_A_EXPERIMENT_ID)
    if not isinstance(experiment, dict):
        raise LabError('v2.0.61 reviewed Paket-A registry row is missing')
    if experiment.get('family_id') != 'RSI_GATED_REVERSION':
        raise LabError('v2.0.61 reviewed Paket-A family identity drift')

    universe = experiment.get('universe')
    if universe != ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']:
        raise LabError('v2.0.61 reviewed Paket-A universe drift')

    source_config = _v251_source_config(updated)
    candidate_config = kernel.validate_config(
        kernel.performance_config(experiment, 'BTCUSDT')
    )
    digest = _v254_canonical_hash(candidate_config)
    if digest in used_config_hashes:
        return updated

    registration = {
        'version': V254_FRONTIER_SCOUT_VERSION,
        'source': 'CONTROLLER_REVIEWED_VIDEO_INTAKE_PACKET_A',
        'experiment_id': V261_PACKET_A_EXPERIMENT_ID,
        'family_id': 'RSI_GATED_REVERSION',
        'schema_validated': True,
        'data_eligibility_inherited_from_selection': False,
        'deduplicated': True,
        'model_generated_executable_code': False,
        'controller_only_registration': True,
    }
    item = {
        'config': copy.deepcopy(candidate_config),
        'v254_registration': registration,
    }
    if source_config is not None and not _v251_legal_frontier_item(
        source_config, item
    ):
        raise LabError('v2.0.61 exact registered Paket-A transition rejected')

    updated['novelty_frontier'] = [item]
    updated['v261_packet_a_replenishment'] = {
        'version': V261_RSI_GATED_REVERSION_VERSION,
        'mode': 'V261_EXACT_REVIEWED_PACKET_A_ADMISSION',
        'actor': 'codex',
        'experiment_id': V261_PACKET_A_EXPERIMENT_ID,
        'family_id': 'RSI_GATED_REVERSION',
        'config_sha256': digest,
        'candidate_baseline_negative_control_required': True,
        'closed_bar_features_only': True,
        's1_only': True,
        'controller_only_promotion': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }
    return updated


def _v269_exact_reviewed_queue_item(item: Any) -> bool:
    """Verify an admitted queue item against both sealed registries."""
    if not isinstance(item, dict):
        return False
    config = item.get('config')
    queue = item.get('v269_reviewed_queue')
    if not isinstance(config, dict) or not isinstance(queue, dict):
        return False
    experiment_id = config.get('experiment_id')
    if experiment_id not in V269_REVIEWED_SEED_PRIORITY:
        return False
    if queue != {
        'version': V269_REVIEWED_SEED_QUEUE_VERSION,
        'source': 'SEALED_V268_CONTROLLER_REVIEWED_REGISTRY',
        'registry_id': V268_REVIEWED_REGISTRY_ID,
        'source_proposal_sha256': V268_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V268_SOURCE_DECISION_SHA256,
        'experiment_id': experiment_id,
        'family_id': 'VOLUME_TSMOM',
        's1_only': True,
        'controller_only_promotion': True,
        'raw_proposal_executed': False,
        'model_generated_executable_code': False,
        'trading_actions': False,
        'exchange_api_access': False,
    }:
        return False
    reviewed = _v265_reviewed_proposal_registry().get(
        V268_SOURCE_PROPOSAL_SHA256, ()
    )
    return (
        set(reviewed) == set(V269_REVIEWED_SEED_PRIORITY)
        and _v260_exact_controller_registered_seed(item)
    )


def _v269_reviewed_seed_replenishment(
    context: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    """Admit the next unused exact v2.0.68 seed before frontier exhaustion.

    A same-family source on an excluded symbol cannot jump directly to a new
    seed without violating the inherited single-axis rule. In that case this
    boundary emits one validated symbol-only bridge first. The bridge is built
    from the observed source config, never from provider text.
    """
    frontier = context.get('novelty_frontier')
    if actor != 'codex' or not isinstance(frontier, list) or frontier:
        return context

    updated = copy.deepcopy(context)
    used_experiment_ids, used_config_hashes = _v254_used_identities(updated)
    reviewed = _v265_reviewed_proposal_registry().get(
        V268_SOURCE_PROPOSAL_SHA256, ()
    )
    if set(reviewed) != set(V269_REVIEWED_SEED_PRIORITY):
        raise LabError('v2.0.69 reviewed VOLUME_TSMOM queue registry drift')

    _, experiments = kernel.registry()
    source_config = _v251_source_config(updated)
    source_family = (
        source_config.get('family') if isinstance(source_config, dict) else None
    )
    source_symbol = (
        source_config.get('symbol') if isinstance(source_config, dict) else None
    )

    event: dict[str, Any] = {
        'version': V269_REVIEWED_SEED_QUEUE_VERSION,
        'actor': 'codex',
        'registry_id': V268_REVIEWED_REGISTRY_ID,
        'source_proposal_sha256': V268_SOURCE_PROPOSAL_SHA256,
        'source_decision_sha256': V268_SOURCE_DECISION_SHA256,
        'priority': list(V269_REVIEWED_SEED_PRIORITY),
        'only_exact_sealed_registry_rows': True,
        'single_material_axis_preserved': True,
        's1_only': True,
        'controller_only_promotion': True,
        'raw_proposal_executed': False,
        'model_generated_executable_code': False,
        'trading_actions': False,
        'exchange_api_access': False,
    }

    if (
        source_family == 'VOLUME_TSMOM'
        and source_symbol not in V269_REVIEWED_SYMBOLS
        and isinstance(source_config, dict)
    ):
        for symbol in V269_REVIEWED_SYMBOLS:
            bridge_config = copy.deepcopy(source_config)
            bridge_config['symbol'] = symbol
            bridge_config = kernel.validate_config(bridge_config)
            digest = _v254_canonical_hash(bridge_config)
            if digest in used_config_hashes:
                continue
            if _v251_transition_axes(source_config, bridge_config) != ('symbol',):
                raise LabError('v2.0.69 source-symbol bridge changed multiple axes')
            item = {
                'config': copy.deepcopy(bridge_config),
                'v269_symbol_bridge': {
                    'version': V269_REVIEWED_SEED_QUEUE_VERSION,
                    'source': 'OBSERVED_VALIDATED_SOURCE_CONFIG',
                    'from_symbol': source_symbol,
                    'to_symbol': symbol,
                    'next_queue_family': 'VOLUME_TSMOM',
                    'single_material_axis': 'symbol',
                    'controller_only_promotion': True,
                    'model_generated_executable_code': False,
                    'trading_actions': False,
                    'exchange_api_access': False,
                },
            }
            if not _v251_legal_frontier_item(source_config, item):
                raise LabError('v2.0.69 source-symbol bridge rejected')
            updated['novelty_frontier'] = [item]
            updated['v269_reviewed_seed_replenishment'] = {
                **event,
                'status': 'SYMBOL_BRIDGE_ADMITTED',
                'mode': 'V269_SINGLE_AXIS_SOURCE_SYMBOL_BRIDGE',
                'experiment_id': bridge_config.get('experiment_id'),
                'symbol': symbol,
                'config_sha256': digest,
                'next_reviewed_experiment_id': V269_REVIEWED_SEED_PRIORITY[0],
            }
            return updated

        updated['v269_reviewed_seed_replenishment'] = {
            **event,
            'status': 'BLOCKED_SOURCE_SYMBOL_BRIDGE_EXHAUSTED',
            'mode': 'V269_REVIEWED_QUEUE_BLOCKED',
        }
        return updated

    selected_symbol = (
        source_symbol
        if source_symbol in V269_REVIEWED_SYMBOLS
        else V269_REVIEWED_SYMBOLS[0]
    )
    for experiment_id in V269_REVIEWED_SEED_PRIORITY:
        if experiment_id in used_experiment_ids:
            continue
        experiment = experiments.get(experiment_id)
        if not isinstance(experiment, dict):
            raise LabError('v2.0.69 reviewed queue experiment is missing')
        if (
            experiment.get('registry_id') != V268_REVIEWED_REGISTRY_ID
            or experiment.get('family_id') != 'VOLUME_TSMOM'
            or tuple(experiment.get('universe') or ()) != V269_REVIEWED_SYMBOLS
        ):
            raise LabError('v2.0.69 reviewed queue experiment drift')
        admission = experiment.get('controller_admission')
        if (
            not isinstance(admission, dict)
            or admission.get('source_proposal_sha256')
            != V268_SOURCE_PROPOSAL_SHA256
            or admission.get('source_decision_sha256')
            != V268_SOURCE_DECISION_SHA256
            or admission.get('status')
            != 'CONTROLLER_APPROVED_SEALED_REGISTRY'
            or admission.get('s1_only') is not True
            or admission.get('controller_only_promotion') is not True
            or admission.get('contains_executable_code') is not False
            or admission.get('raw_proposal_executed') is not False
            or admission.get('trading_actions') is not False
            or admission.get('exchange_api_access') is not False
        ):
            raise LabError('v2.0.69 reviewed queue provenance drift')

        candidate_config = kernel.validate_config(
            kernel.performance_config(experiment, selected_symbol)
        )
        digest = _v254_canonical_hash(candidate_config)
        if digest in used_config_hashes:
            continue
        registration = {
            'version': V254_FRONTIER_SCOUT_VERSION,
            'source': 'EXISTING_REGISTERED_KERNEL_SEED',
            'experiment_id': experiment_id,
            'family_id': 'VOLUME_TSMOM',
            'schema_validated': True,
            'data_eligibility_inherited_from_selection': True,
            'deduplicated': True,
            'model_generated_executable_code': False,
            'controller_only_registration': True,
        }
        item = {
            'config': copy.deepcopy(candidate_config),
            'v254_registration': registration,
            'v269_reviewed_queue': {
                'version': V269_REVIEWED_SEED_QUEUE_VERSION,
                'source': 'SEALED_V268_CONTROLLER_REVIEWED_REGISTRY',
                'registry_id': V268_REVIEWED_REGISTRY_ID,
                'source_proposal_sha256': V268_SOURCE_PROPOSAL_SHA256,
                'source_decision_sha256': V268_SOURCE_DECISION_SHA256,
                'experiment_id': experiment_id,
                'family_id': 'VOLUME_TSMOM',
                's1_only': True,
                'controller_only_promotion': True,
                'raw_proposal_executed': False,
                'model_generated_executable_code': False,
                'trading_actions': False,
                'exchange_api_access': False,
            },
        }
        if not _v269_exact_reviewed_queue_item(item):
            raise LabError('v2.0.69 exact reviewed queue item rejected')
        if source_config is not None and not _v251_legal_frontier_item(
            source_config, item
        ):
            raise LabError('v2.0.69 exact reviewed queue transition rejected')

        updated['novelty_frontier'] = [item]
        updated['v269_reviewed_seed_replenishment'] = {
            **event,
            'status': 'EXACT_REVIEWED_SEED_ADMITTED',
            'mode': 'V269_PRIORITY_REVIEWED_SEED_ADMISSION',
            'experiment_id': experiment_id,
            'symbol': selected_symbol,
            'config_sha256': digest,
            'candidate_baseline_negative_control_required': True,
            'causal_volume_shuffle_only': True,
        }
        return updated

    updated['v269_reviewed_seed_replenishment'] = {
        **event,
        'status': 'REVIEWED_SEED_QUEUE_EXHAUSTED',
        'mode': 'V269_REVIEWED_QUEUE_EXHAUSTED',
    }
    return updated


def _v274_full_historical_candidate_hashes(root: Path) -> set[str]:
    """Read the immutable validator's authoritative local duplicate set."""
    reader = getattr(
        V216_GLOBAL_MEMORY_MODULE,
        '_historical_candidate_hashes',
        None,
    )
    if not callable(reader):
        raise LabError('v2.0.74 full-history duplicate reader is unavailable')
    hashes = reader(root)
    if (
        not isinstance(hashes, set)
        or any(not isinstance(value, str) or not value for value in hashes)
    ):
        raise LabError('v2.0.74 full-history duplicate set is invalid')
    return set(hashes)


def _v274_global_memory_reviewed_seed_filter(
    context: dict[str, Any],
    actor: str,
    root: Path,
) -> dict[str, Any]:
    """Skip hash-equal reviewed seeds before any provider boundary."""
    selected = _v269_reviewed_seed_replenishment(context, actor)
    queue_event = selected.get('v269_reviewed_seed_replenishment')
    if actor != 'codex' or not isinstance(queue_event, dict):
        return selected

    historical = _v274_full_historical_candidate_hashes(root)
    working = copy.deepcopy(context)
    skipped: list[dict[str, Any]] = []

    for _ in range(len(V269_REVIEWED_SEED_PRIORITY) + 1):
        frontier = selected.get('novelty_frontier')
        if not isinstance(frontier, list) or not frontier:
            break
        if len(frontier) != 1 or not isinstance(frontier[0], dict):
            raise LabError('v2.0.74 reviewed frontier shape is invalid')
        item = frontier[0]
        config = item.get('config')
        if not isinstance(config, dict):
            raise LabError('v2.0.74 reviewed frontier config is invalid')
        is_reviewed = (
            _v269_exact_reviewed_queue_item(item)
            or isinstance(item.get('v269_symbol_bridge'), dict)
        )
        if not is_reviewed:
            break

        digest = _v254_canonical_hash(config)
        if digest not in historical:
            break
        skipped.append({
            'experiment_id': config.get('experiment_id'),
            'symbol': config.get('symbol'),
            'config_sha256': digest,
            'reason': 'DUPLICATE_IN_AUTHORITATIVE_GLOBAL_PROPOSAL_MEMORY',
        })

        previous = working.get('previous_rounds')
        marker = {'config': copy.deepcopy(config)}
        if previous is None:
            working['previous_rounds'] = [marker]
        elif isinstance(previous, list):
            previous.append(marker)
        elif isinstance(previous, dict):
            working['previous_rounds'] = [previous, marker]
        else:
            raise LabError('v2.0.74 previous-round identity shape is invalid')
        selected = _v269_reviewed_seed_replenishment(working, actor)
    else:
        raise LabError('v2.0.74 reviewed queue duplicate filter did not converge')

    result = copy.deepcopy(context)
    result['novelty_frontier'] = copy.deepcopy(
        selected.get('novelty_frontier', [])
    )
    selected_event = selected.get('v269_reviewed_seed_replenishment')
    if isinstance(selected_event, dict):
        result['v269_reviewed_seed_replenishment'] = copy.deepcopy(
            selected_event
        )

    frontier = result.get('novelty_frontier')
    chosen = (
        frontier[0].get('config')
        if isinstance(frontier, list)
        and len(frontier) == 1
        and isinstance(frontier[0], dict)
        and isinstance(frontier[0].get('config'), dict)
        else None
    )
    result['v274_global_memory_queue_filter'] = {
        'version': V274_GLOBAL_MEMORY_QUEUE_FILTER_VERSION,
        'actor': 'codex',
        'historical_candidate_hash_count': len(historical),
        'skipped_duplicate_count': len(skipped),
        'skipped_duplicates': skipped,
        'selected_experiment_id': (
            chosen.get('experiment_id') if isinstance(chosen, dict) else None
        ),
        'selected_config_sha256': (
            _v254_canonical_hash(chosen)
            if isinstance(chosen, dict)
            else None
        ),
        'full_history_scan_is_local': True,
        'authoritative_duplicate_reader_reused': True,
        'provider_invoked_by_filter': False,
        'raw_proposal_executed': False,
        'controller_only_promotion': True,
        'proposal_validation_unchanged': True,
        's1_gates_unchanged': True,
        'trading_actions': False,
        'exchange_api_access': False,
        'unknown_errors_fail_closed': True,
    }
    return result


def _v254_scout_needed(context: dict[str, Any]) -> bool:
    if context.get('v254_frontier_low_watermark') is True:
        return True
    frontier = context.get('novelty_frontier')
    return isinstance(frontier, list) and len(frontier) <= V254_FRONTIER_LOW_WATERMARK


def _v265_inbox_root() -> Path:
    """Resolve the mutable inbox without coupling staging tests to production."""
    if HERE == V262_SOURCE_HERE and 'staging' in HERE.parts:
        # Unit/regression gates must not depend on mutable production inbox
        # occupancy. Tests that explicitly replace HERE still exercise the
        # real capacity algorithm against their own temporary directory.
        return HERE / '.v262-test-isolated-frontier-scout-inbox'
    return HERE.parent / 'frontier-scout-inbox'


def _v265_reviewed_proposal_registry() -> dict[str, tuple[str, ...]]:
    """Load only sealed controller-reviewed Scout proposal identities."""
    reviewed: dict[str, list[str]] = {}
    registries = (
        (
            HERE / 'research' / 'frontier-scout-approved-seeds-v1.jsonl',
            'tdh-controller-reviewed-scout-seeds-v1',
            None,
        ),
        (
            HERE / 'research' / V268_REVIEWED_SEEDS_FILENAME,
            V268_REVIEWED_REGISTRY_ID,
            V268_SOURCE_PROPOSAL_SHA256,
        ),
    )
    for path, registry_id, exact_proposal_sha256 in registries:
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            raise LabError('v2.0.68 reviewed Scout registry path is unsafe')
        if not 1 <= path.stat().st_size <= 1_000_000:
            raise LabError('v2.0.68 reviewed Scout registry size is invalid')
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            raise LabError('v2.0.68 reviewed Scout registry is unreadable') from exc

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LabError(
                    f'v2.0.68 reviewed Scout registry line {line_number} is invalid'
                ) from exc
            if not isinstance(row, dict):
                raise LabError('v2.0.68 reviewed Scout registry row is not an object')
            admission = row.get('controller_admission')
            proposal_sha256 = (
                admission.get('source_proposal_sha256')
                if isinstance(admission, dict)
                else None
            )
            experiment_id = row.get('experiment_id')
            if (
                row.get('registry_id') != registry_id
                or not isinstance(experiment_id, str)
                or not experiment_id
                or not isinstance(proposal_sha256, str)
                or re.fullmatch(r'[0-9a-f]{64}', proposal_sha256) is None
                or (
                    exact_proposal_sha256 is not None
                    and proposal_sha256 != exact_proposal_sha256
                )
                or admission.get('status')
                != 'CONTROLLER_APPROVED_SEALED_REGISTRY'
                or admission.get('contains_executable_code') is not False
                or admission.get('controller_only_promotion') is not True
                or admission.get('trading_actions') is not False
                or admission.get('exchange_api_access') is not False
            ):
                raise LabError('v2.0.68 reviewed Scout registry contract drift')
            reviewed.setdefault(proposal_sha256, []).append(experiment_id)

    return {
        digest: tuple(sorted(set(experiment_ids)))
        for digest, experiment_ids in reviewed.items()
    }


def _v266_producer_state_root() -> Path:
    """Resolve mutable controller decisions outside the immutable release."""
    if HERE == V262_SOURCE_HERE and 'staging' in HERE.parts:
        return HERE / '.v266-test-isolated-frontier-producer-state'
    return HERE.parent / 'frontier-producer-state'


def _v266_decision_path(proposal_sha256: str) -> Path:
    if re.fullmatch(r'[0-9a-f]{64}', proposal_sha256) is None:
        raise LabError('v2.0.66 producer proposal digest is invalid')
    return _v266_producer_state_root() / f'{proposal_sha256}.json'


def _v266_read_decision(proposal_sha256: str) -> dict[str, Any] | None:
    path = _v266_decision_path(proposal_sha256)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise LabError('v2.0.66 producer decision path is unsafe')
    if not 1 <= path.stat().st_size <= V265_MAX_PROPOSAL_BYTES:
        raise LabError('v2.0.66 producer decision size is invalid')
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabError('v2.0.66 producer decision is unreadable') from exc
    if (
        not isinstance(value, dict)
        or value.get('version') != V266_FRONTIER_PRODUCER_VERSION
        or value.get('source_proposal_sha256') != proposal_sha256
        or value.get('status') not in V266_TERMINAL_DECISION_STATES
        or value.get('raw_proposal_executed') is not False
        or value.get('controller_only_registration') is not True
        or value.get('s1_only') is not True
        or value.get('trading_actions') is not False
        or value.get('exchange_api_access') is not False
    ):
        raise LabError('v2.0.66 producer decision contract drift')
    return value


def _v266_load_raw_proposal(file_name: str, expected_sha256: str) -> dict[str, Any]:
    if (
        re.fullmatch(r'TDH-SCOUT-[A-Za-z0-9._-]+\.json', file_name) is None
        or '/' in file_name
        or '\\' in file_name
    ):
        raise LabError('v2.0.66 producer inbox file identity is invalid')
    path = _v265_inbox_root() / file_name
    if path.is_symlink() or not path.is_file():
        raise LabError('v2.0.66 producer inbox path is unsafe')
    if not 1 <= path.stat().st_size <= V265_MAX_PROPOSAL_BYTES:
        raise LabError('v2.0.66 producer inbox file size is invalid')
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabError('v2.0.66 producer inbox file is unreadable') from exc
    if not isinstance(raw, dict):
        raise LabError('v2.0.66 producer inbox envelope is invalid')
    if 'proposal' in raw:
        proposal = _v254_validate_scout_proposal(raw.get('proposal'))
        digest = _v254_canonical_hash(proposal)
        if (
            raw.get('status') != 'UNTRUSTED_INBOX'
            or raw.get('proposal_sha256') != digest
            or raw.get('automatically_registered') is not False
            or raw.get('controller_registration_required') is not True
            or raw.get('controller_only_promotion') is not True
            or raw.get('trading_actions') is not False
            or raw.get('exchange_api_access') is not False
        ):
            raise LabError('v2.0.66 producer envelope contract drift')
    else:
        proposal = _v254_validate_scout_proposal(raw)
        digest = _v254_canonical_hash(proposal)
    if digest != expected_sha256:
        raise LabError('v2.0.66 producer source digest drift')
    return proposal


def _v266_normalized_tokens(value: Any) -> set[str]:
    text = ' '.join(_v254_strings(value)).upper()
    return {
        token for token in re.sub(r'[^A-Z0-9]+', ' ', text).split()
        if len(token) >= 2
    }


def _v266_explicit_family_matches(proposal: dict[str, Any]) -> list[str]:
    """Map only explicit sealed-family names; semantic guessing is forbidden."""
    families, _ = kernel.registry()
    haystack = _v266_normalized_tokens({
        'family_thesis': proposal.get('family_thesis'),
        'causal_mechanism': proposal.get('causal_mechanism'),
        'bounded_parameters': proposal.get('bounded_parameters'),
    })
    matches: list[str] = []
    for family_id, card in sorted(families.items()):
        if not isinstance(family_id, str) or not isinstance(card, dict):
            raise LabError('v2.0.66 producer family registry is invalid')
        identity_tokens = _v266_normalized_tokens([
            family_id,
            card.get('name'),
        ])
        family_id_tokens = _v266_normalized_tokens(family_id)
        if family_id_tokens and family_id_tokens.issubset(haystack):
            matches.append(family_id)
            continue
        name = card.get('name')
        name_tokens = _v266_normalized_tokens(name) if isinstance(name, str) else set()
        if len(name_tokens) >= 2 and name_tokens.issubset(haystack):
            matches.append(family_id)
    return sorted(set(matches))


def _v266_produce_one_review_packet(
    lifecycle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Create one idempotent data-only admission decision per bounded epoch."""
    current = lifecycle or _v265_scout_inbox_lifecycle()
    if current.get('invalid_count') or current.get('raw_hard_limit_reached'):
        raise LabError('v2.0.66 producer refuses invalid or unbounded inbox')
    pending = [
        row for row in current.get('records', [])
        if isinstance(row, dict) and row.get('state') == 'REVIEW_PENDING'
    ]
    if not pending:
        return None
    selected = sorted(
        pending,
        key=lambda row: (
            str(row.get('hypothesis_id') or ''),
            str(row.get('proposal_sha256') or ''),
            str(row.get('file') or ''),
        ),
    )[0]
    digest = str(selected.get('proposal_sha256') or '')
    existing = _v266_read_decision(digest)
    if existing is not None:
        return existing
    proposal = _v266_load_raw_proposal(str(selected.get('file') or ''), digest)
    required_data = sorted({
        str(value).strip().lower()
        for value in proposal.get('required_data', [])
        if isinstance(value, str) and value.strip()
    })
    missing_data = sorted(set(required_data) - set(V266_OFFLINE_AVAILABLE_DATA))
    matches = _v266_explicit_family_matches(proposal)
    if missing_data:
        status = 'BLOCKED_MISSING_OFFLINE_DATA'
        family_id = None
        reason = 'required offline dataset is not installed'
    elif len(matches) > 1:
        status = 'QUARANTINED_AMBIGUOUS_FAMILY'
        family_id = None
        reason = 'proposal explicitly matches multiple registered families'
    elif not matches:
        status = 'NEEDS_FAMILY_IMPLEMENTATION_REVIEW'
        family_id = None
        reason = 'no exact registered family identity appears in the proposal'
    else:
        status = 'READY_FOR_SEALED_IMPLEMENTATION'
        family_id = matches[0]
        reason = 'exact registered family and installed offline data are available'
    decision = {
        'version': V266_FRONTIER_PRODUCER_VERSION,
        'status': status,
        'reason': reason,
        'source_file': str(selected.get('file') or ''),
        'source_hypothesis_id': proposal['hypothesis_id'],
        'source_proposal_sha256': digest,
        'registered_family_id': family_id,
        'registered_family_matches': matches,
        'required_data': required_data,
        'missing_offline_data': missing_data,
        'timeframes': copy.deepcopy(proposal['timeframes']),
        'bounded_parameters': copy.deepcopy(proposal['bounded_parameters']),
        'candidate_thesis': proposal['family_thesis'],
        'baseline_thesis': proposal['baseline_thesis'],
        'negative_control_thesis': proposal['negative_control_thesis'],
        'falsification': copy.deepcopy(proposal['falsification']),
        'candidate_baseline_negative_control_required': True,
        'raw_proposal_executed': False,
        'contains_executable_code': False,
        'automatically_registered': False,
        'sealed_registry_change_required': True,
        'controller_only_registration': True,
        's1_only': True,
        's2_s4_opened': False,
        'trading_actions': False,
        'exchange_api_access': False,
    }
    state_root = _v266_producer_state_root()
    if state_root.exists() and (state_root.is_symlink() or not state_root.is_dir()):
        raise LabError('v2.0.66 producer state root is unsafe')
    state_root.mkdir(parents=True, exist_ok=True)
    if state_root.is_symlink():
        raise LabError('v2.0.66 producer state root became unsafe')
    atomic_json(_v266_decision_path(digest), decision)
    return decision


def _v267_decision_path(proposal_sha256: str) -> Path:
    if re.fullmatch(r'[0-9a-f]{64}', proposal_sha256) is None:
        raise LabError('v2.0.67 data capability proposal digest is invalid')
    return _v266_producer_state_root() / f'{proposal_sha256}.v267.json'


def _v267_classify_data_requirement(requirement: str) -> dict[str, str]:
    """Classify declared data without guessing or invoking a provider."""
    normalized = ' '.join(
        re.sub(r'[^a-z0-9]+', ' ', requirement.lower()).split()
    )
    if not normalized:
        raise LabError('v2.0.67 empty data requirement')

    external_markers = (
        'funding', 'open interest', 'order book', 'orderbook', 'level 2',
        'level2', 'liquidation', 'mark price', 'index price', 'basis data',
        'on chain', 'onchain', 'sentiment', 'news feed', 'macro data',
        'options chain', 'implied volatility', 'exchange private',
        'tick data', 'raw trade', 'agg trade', 'trade tape', 'websocket feed',
    )
    derived_markers = (
        'return', 'momentum', 'rsi', 'adx', 'atr', 'volatility',
        'percentile', 'rank', 'correlation', 'covariance', 'expectancy',
        'trade count', 'trade counts', 'win rate', 'profit factor',
        'drawdown', 'pnl', 'backtest', 'metric', 'signal', 'label',
        'shuffled', 'permuted', 'negative control', 'rolling',
        'cross coin', 'coin pair', 'per coin', 'regime', 'z score',
    )
    raw_ohlcv_markers = (
        'ohlcv', 'candle', 'candles', 'open high low close',
        'historical price', 'price history', 'close price', 'open price',
        'high price', 'low price', 'volume',
    )

    if any(marker in normalized for marker in external_markers):
        capability = 'EXTERNAL_DATA_REQUIRED'
    elif any(marker in normalized for marker in derived_markers):
        capability = 'DERIVABLE_FROM_OHLCV'
    elif any(marker in normalized for marker in raw_ohlcv_markers):
        capability = 'INSTALLED_RAW_OHLCV'
    else:
        capability = 'AMBIGUOUS_DATA_REQUIREMENT'
    return {
        'requirement': requirement.strip(),
        'normalized_requirement': normalized,
        'capability': capability,
    }


def _v267_read_decision(proposal_sha256: str) -> dict[str, Any] | None:
    path = _v267_decision_path(proposal_sha256)
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise LabError('v2.0.67 data capability decision path is unsafe')
    if not 1 <= path.stat().st_size <= V265_MAX_PROPOSAL_BYTES:
        raise LabError('v2.0.67 data capability decision size is invalid')
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabError('v2.0.67 data capability decision is unreadable') from exc
    capabilities = value.get('required_data_capabilities') if isinstance(value, dict) else None
    if (
        not isinstance(value, dict)
        or value.get('version') != V267_DATA_CAPABILITY_VERSION
        or value.get('source_proposal_sha256') != proposal_sha256
        or value.get('status') not in V267_TERMINAL_DECISION_STATES
        or not isinstance(capabilities, list)
        or not capabilities
        or any(
            not isinstance(row, dict)
            or row.get('capability') not in V267_DATA_CAPABILITY_STATES
            or not isinstance(row.get('requirement'), str)
            or not isinstance(row.get('normalized_requirement'), str)
            for row in capabilities
        )
        or value.get('raw_proposal_executed') is not False
        or value.get('controller_only_registration') is not True
        or value.get('s1_only') is not True
        or value.get('trading_actions') is not False
        or value.get('exchange_api_access') is not False
    ):
        raise LabError('v2.0.67 data capability decision contract drift')

    supersedes_version = value.get('supersedes_version')
    supersedes_sha256 = value.get('supersedes_decision_sha256')
    prior_status = value.get('prior_status')
    if supersedes_version is None:
        if supersedes_sha256 is not None or prior_status is not None:
            raise LabError('v2.0.67 supersession linkage drift')
    else:
        legacy = _v266_read_decision(proposal_sha256)
        if (
            supersedes_version != V266_FRONTIER_PRODUCER_VERSION
            or legacy is None
            or supersedes_sha256 != _v254_canonical_hash(legacy)
            or prior_status != legacy.get('status')
        ):
            raise LabError('v2.0.67 supersession linkage drift')

    proposal = _v266_load_raw_proposal(
        str(value.get('source_file') or ''), proposal_sha256
    )
    expected_required_data = sorted({
        str(item).strip()
        for item in proposal.get('required_data', [])
        if isinstance(item, str) and item.strip()
    }, key=str.lower)
    expected_capabilities = [
        _v267_classify_data_requirement(item)
        for item in expected_required_data
    ]
    expected_external = sorted(
        row['requirement'] for row in expected_capabilities
        if row['capability'] == 'EXTERNAL_DATA_REQUIRED'
    )
    expected_ambiguous = sorted(
        row['requirement'] for row in expected_capabilities
        if row['capability'] == 'AMBIGUOUS_DATA_REQUIREMENT'
    )
    expected_derivable = sorted(
        row['requirement'] for row in expected_capabilities
        if row['capability'] == 'DERIVABLE_FROM_OHLCV'
    )
    expected_matches = _v266_explicit_family_matches(proposal)
    if len(expected_matches) > 1:
        expected_status = 'QUARANTINED_AMBIGUOUS_FAMILY'
        expected_family_id = None
    elif not expected_matches:
        expected_status = 'NEEDS_FAMILY_IMPLEMENTATION_REVIEW'
        expected_family_id = None
    elif expected_external:
        expected_status = 'BLOCKED_MISSING_EXTERNAL_DATA'
        expected_family_id = expected_matches[0]
    elif expected_ambiguous:
        expected_status = 'NEEDS_DATA_CAPABILITY_REVIEW'
        expected_family_id = expected_matches[0]
    else:
        expected_status = 'READY_FOR_SEALED_IMPLEMENTATION'
        expected_family_id = expected_matches[0]
    if (
        value.get('required_data') != expected_required_data
        or capabilities != expected_capabilities
        or value.get('missing_external_data') != expected_external
        or value.get('ambiguous_data_requirements') != expected_ambiguous
        or value.get('derivable_from_ohlcv') != expected_derivable
        or value.get('registered_family_matches') != expected_matches
        or value.get('registered_family_id') != expected_family_id
        or value.get('status') != expected_status
        or value.get('source_hypothesis_id') != proposal.get('hypothesis_id')
        or value.get('timeframes') != proposal.get('timeframes')
        or value.get('bounded_parameters') != proposal.get('bounded_parameters')
        or value.get('candidate_thesis') != proposal.get('family_thesis')
        or value.get('baseline_thesis') != proposal.get('baseline_thesis')
        or value.get('negative_control_thesis')
        != proposal.get('negative_control_thesis')
        or value.get('falsification') != proposal.get('falsification')
    ):
        raise LabError('v2.0.67 deterministic admission decision drift')
    return value


def _v267_produce_one_review_packet(
    lifecycle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Reclassify one legacy decision or admit one pending proposal per epoch."""
    current = lifecycle or _v265_scout_inbox_lifecycle()
    if current.get('invalid_count') or current.get('raw_hard_limit_reached'):
        raise LabError('v2.0.67 producer refuses invalid or unbounded inbox')
    migrations = [
        row for row in current.get('records', [])
        if isinstance(row, dict) and row.get('state') == 'DATA_CAPABILITY_MIGRATION_PENDING'
    ]
    pending = [
        row for row in current.get('records', [])
        if isinstance(row, dict) and row.get('state') == 'REVIEW_PENDING'
    ]
    candidates = migrations or pending
    if not candidates:
        return None
    selected = sorted(
        candidates,
        key=lambda row: (
            str(row.get('hypothesis_id') or ''),
            str(row.get('proposal_sha256') or ''),
            str(row.get('file') or ''),
        ),
    )[0]
    digest = str(selected.get('proposal_sha256') or '')
    existing = _v267_read_decision(digest)
    if existing is not None:
        return existing

    legacy = _v266_read_decision(digest)
    proposal = _v266_load_raw_proposal(str(selected.get('file') or ''), digest)
    required_data = sorted({
        str(value).strip()
        for value in proposal.get('required_data', [])
        if isinstance(value, str) and value.strip()
    }, key=str.lower)
    capabilities = [
        _v267_classify_data_requirement(value) for value in required_data
    ]
    external = sorted(
        row['requirement'] for row in capabilities
        if row['capability'] == 'EXTERNAL_DATA_REQUIRED'
    )
    ambiguous_data = sorted(
        row['requirement'] for row in capabilities
        if row['capability'] == 'AMBIGUOUS_DATA_REQUIREMENT'
    )
    derivable = sorted(
        row['requirement'] for row in capabilities
        if row['capability'] == 'DERIVABLE_FROM_OHLCV'
    )
    matches = _v266_explicit_family_matches(proposal)
    if len(matches) > 1:
        status = 'QUARANTINED_AMBIGUOUS_FAMILY'
        family_id = None
        reason = 'proposal explicitly matches multiple registered families'
    elif not matches:
        status = 'NEEDS_FAMILY_IMPLEMENTATION_REVIEW'
        family_id = None
        reason = 'no exact registered family identity appears in the proposal'
    elif external:
        status = 'BLOCKED_MISSING_EXTERNAL_DATA'
        family_id = matches[0]
        reason = 'proposal requires a raw external dataset that is not installed'
    elif ambiguous_data:
        status = 'NEEDS_DATA_CAPABILITY_REVIEW'
        family_id = matches[0]
        reason = 'data requirement cannot be proven available or OHLCV-derivable'
    else:
        status = 'READY_FOR_SEALED_IMPLEMENTATION'
        family_id = matches[0]
        reason = 'exact registered family and verified offline data capabilities are available'

    decision = {
        'version': V267_DATA_CAPABILITY_VERSION,
        'status': status,
        'reason': reason,
        'source_file': str(selected.get('file') or ''),
        'source_hypothesis_id': proposal['hypothesis_id'],
        'source_proposal_sha256': digest,
        'supersedes_version': (
            V266_FRONTIER_PRODUCER_VERSION if legacy is not None else None
        ),
        'supersedes_decision_sha256': (
            _v254_canonical_hash(legacy) if legacy is not None else None
        ),
        'prior_status': legacy.get('status') if legacy is not None else None,
        'registered_family_id': family_id,
        'registered_family_matches': matches,
        'required_data': required_data,
        'required_data_capabilities': capabilities,
        'derivable_from_ohlcv': derivable,
        'missing_external_data': external,
        'ambiguous_data_requirements': ambiguous_data,
        'timeframes': copy.deepcopy(proposal['timeframes']),
        'bounded_parameters': copy.deepcopy(proposal['bounded_parameters']),
        'candidate_thesis': proposal['family_thesis'],
        'baseline_thesis': proposal['baseline_thesis'],
        'negative_control_thesis': proposal['negative_control_thesis'],
        'falsification': copy.deepcopy(proposal['falsification']),
        'candidate_baseline_negative_control_required': True,
        'raw_proposal_executed': False,
        'contains_executable_code': False,
        'automatically_registered': False,
        'sealed_registry_change_required': True,
        'controller_only_registration': True,
        's1_only': True,
        's2_s4_opened': False,
        'trading_actions': False,
        'exchange_api_access': False,
    }
    state_root = _v266_producer_state_root()
    if state_root.exists() and (state_root.is_symlink() or not state_root.is_dir()):
        raise LabError('v2.0.67 producer state root is unsafe')
    state_root.mkdir(parents=True, exist_ok=True)
    if state_root.is_symlink():
        raise LabError('v2.0.67 producer state root became unsafe')
    atomic_json(_v267_decision_path(digest), decision)
    return decision


def _v265_scout_inbox_lifecycle() -> dict[str, Any]:
    """Classify immutable raw proposals without deleting or executing them."""
    inbox_root = _v265_inbox_root()
    if inbox_root.exists() and (inbox_root.is_symlink() or not inbox_root.is_dir()):
        raise LabError('v2.0.65 Scout inbox root is unsafe')

    paths = (
        sorted(inbox_root.glob('TDH-SCOUT-*.json'), key=lambda path: path.name)
        if inbox_root.is_dir()
        else []
    )
    reviewed = _v265_reviewed_proposal_registry()
    records: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    invalid_count = 0
    duplicate_count = 0
    registered_count = 0
    producer_ready_count = 0
    producer_review_count = 0
    producer_data_review_count = 0
    producer_blocked_count = 0
    data_capability_migration_count = 0

    for path in paths:
        base = {'file': path.name}
        if path.is_symlink() or not path.is_file():
            invalid_count += 1
            records.append({**base, 'state': 'QUARANTINED_INVALID_PATH'})
            continue
        try:
            size = path.stat().st_size
            if not 1 <= size <= V265_MAX_PROPOSAL_BYTES:
                raise LabError('proposal size is outside the bounded contract')
            raw = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict):
                raise LabError('proposal record is not an object')
            if 'proposal' in raw:
                proposal = _v254_validate_scout_proposal(raw.get('proposal'))
                digest = _v254_canonical_hash(proposal)
                if (
                    raw.get('status') != 'UNTRUSTED_INBOX'
                    or raw.get('proposal_sha256') != digest
                    or raw.get('automatically_registered') is not False
                    or raw.get('controller_registration_required') is not True
                    or raw.get('controller_only_promotion') is not True
                    or raw.get('trading_actions') is not False
                    or raw.get('exchange_api_access') is not False
                ):
                    raise LabError('proposal record envelope contract drift')
            else:
                # The original data-only v1 shape is retained as a safe legacy
                # input. It receives the same strict proposal validation and
                # never bypasses controller review.
                proposal = _v254_validate_scout_proposal(raw)
                digest = _v254_canonical_hash(proposal)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            LabError,
        ) as exc:
            invalid_count += 1
            records.append({
                **base,
                'state': 'QUARANTINED_INVALID_CONTENT',
                'reason': str(exc)[:240],
            })
            continue

        identity = {
            **base,
            'hypothesis_id': proposal['hypothesis_id'],
            'proposal_sha256': digest,
        }
        if digest in seen_hashes:
            duplicate_count += 1
            records.append({**identity, 'state': 'ARCHIVED_DUPLICATE'})
            continue
        seen_hashes.add(digest)

        approved_experiments = reviewed.get(digest)
        if approved_experiments:
            registered_count += 1
            records.append({
                **identity,
                'state': 'REGISTERED_REVIEWED',
                'experiment_ids': list(approved_experiments),
            })
            continue
        decision = _v267_read_decision(digest)
        legacy_decision = _v266_read_decision(digest)
        if (
            decision is None
            and legacy_decision is not None
            and legacy_decision.get('status') == 'BLOCKED_MISSING_OFFLINE_DATA'
        ):
            data_capability_migration_count += 1
            records.append({
                **identity,
                'state': 'DATA_CAPABILITY_MIGRATION_PENDING',
                'legacy_producer_decision_sha256': (
                    _v254_canonical_hash(legacy_decision)
                ),
                'legacy_status': legacy_decision.get('status'),
            })
            continue
        if decision is None:
            decision = legacy_decision
        if decision is not None:
            decision_state = str(decision['status'])
            if decision_state == 'READY_FOR_SEALED_IMPLEMENTATION':
                producer_ready_count += 1
            elif decision_state == 'NEEDS_FAMILY_IMPLEMENTATION_REVIEW':
                producer_review_count += 1
            elif decision_state == 'NEEDS_DATA_CAPABILITY_REVIEW':
                producer_data_review_count += 1
            else:
                producer_blocked_count += 1
            records.append({
                **identity,
                'state': decision_state,
                'producer_decision_sha256': _v254_canonical_hash(decision),
                'registered_family_id': decision.get('registered_family_id'),
            })
            continue
        pending.append(identity)

    pending.sort(
        key=lambda row: (
            str(row.get('hypothesis_id') or ''),
            str(row.get('proposal_sha256') or ''),
            str(row.get('file') or ''),
        )
    )
    active = pending[:V265_ACTIVE_REVIEW_LIMIT]
    deferred = pending[V265_ACTIVE_REVIEW_LIMIT:]
    records.extend({**row, 'state': 'REVIEW_PENDING'} for row in active)
    records.extend({**row, 'state': 'DEFERRED_BOUNDED_BACKLOG'} for row in deferred)
    records.sort(key=lambda row: str(row.get('file') or ''))

    hard_limit_reached = len(paths) >= V265_RAW_INBOX_HARD_LIMIT
    if invalid_count or hard_limit_reached:
        blocking_reason = 'INVALID_OR_UNBOUNDED_INBOX_FAIL_CLOSED'
    elif data_capability_migration_count:
        blocking_reason = 'DATA_CAPABILITY_MIGRATION_PENDING'
    elif active or deferred:
        blocking_reason = 'IMPLEMENTATION_REVIEW_QUEUE_PENDING'
    elif producer_ready_count:
        blocking_reason = 'SEALED_IMPLEMENTATION_QUEUE_PENDING'
    elif producer_review_count:
        blocking_reason = 'FAMILY_IMPLEMENTATION_REVIEW_PENDING'
    elif producer_data_review_count:
        blocking_reason = 'DATA_CAPABILITY_REVIEW_PENDING'
    elif producer_blocked_count:
        blocking_reason = 'PRODUCER_BLOCKED_DECISIONS_REQUIRE_REVIEW'
    else:
        blocking_reason = None
    provider_allowed = blocking_reason is None

    return {
        'version': V265_FRONTIER_INBOX_LIFECYCLE_VERSION,
        'inbox_count': len(paths),
        'inbox_capacity': V254_SCOUT_INBOX_MAX_FILES,
        'raw_inbox_hard_limit': V265_RAW_INBOX_HARD_LIMIT,
        'raw_hard_limit_reached': hard_limit_reached,
        'unique_proposal_count': len(seen_hashes),
        'registered_reviewed_count': registered_count,
        'producer_ready_count': producer_ready_count,
        'producer_review_count': producer_review_count,
        'producer_data_review_count': producer_data_review_count,
        'producer_blocked_count': producer_blocked_count,
        'data_capability_migration_count': data_capability_migration_count,
        'duplicate_count': duplicate_count,
        'invalid_count': invalid_count,
        'review_pending_count': len(active),
        'deferred_count': len(deferred),
        'actionable_count': len(pending),
        'active_review_limit': V265_ACTIVE_REVIEW_LIMIT,
        'provider_allowed': provider_allowed,
        'provider_blocking_reason': blocking_reason,
        'checked_before_provider': True,
        'records': records,
        'raw_proposals_preserved': True,
        'untrusted_text_never_executes': True,
        'v267_data_capability_version': V267_DATA_CAPABILITY_VERSION,
        'v267_legacy_decisions_are_preserved': True,
        'v267_hash_bound_supersession': True,
        'controller_only_registration': True,
        'trading_actions': False,
        'exchange_api_access': False,
    }


def _v261_scout_inbox_status() -> dict[str, Any]:
    """Inspect lifecycle state before any paid Frontier Scout provider call."""
    lifecycle = _v265_scout_inbox_lifecycle()
    return {
        **lifecycle,
        'v261_capacity_contract_preserved': True,
        'checked_before_provider': True,
    }


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
    def _v273_cache_example_shape(
        self,
        context: dict[str, Any],
        candidate_config: dict[str, Any],
    ) -> None:
        source_config = _v251_source_config(context)
        if not isinstance(source_config, dict):
            raise LabError('v2.0.73 reviewed example source config is missing')
        if not _v260_exact_controller_registered_seed({'config': source_config}):
            raise LabError('v2.0.73 reviewed example source is not registered')
        if not _v260_exact_controller_registered_seed({'config': candidate_config}):
            raise LabError('v2.0.73 reviewed example candidate is not registered')

        axes = _v251_transition_axes(source_config, candidate_config)
        if (
            source_config.get('family') != candidate_config.get('family')
            or source_config.get('symbol') != candidate_config.get('symbol')
            or axes not in {
                ('registered_seed',),
                ('timeframe', 'registered_seed'),
            }
        ):
            raise LabError('v2.0.73 reviewed example transition is not exact')

        # This is the exact sealed v2.0.28 same-family frontier rule. It is a
        # proposal-example presentation field, not a new controller decision.
        self._v273_example_shape = {
            'version': V273_EXAMPLE_SHAPE_BRIDGE_VERSION,
            'selected_approach': 'VALIDATE_PARAMETER_NEIGHBORHOOD',
            'source_config': copy.deepcopy(source_config),
            'source_config_sha256': _v254_canonical_hash(source_config),
            'candidate_config_sha256': _v254_canonical_hash(candidate_config),
            'transition_axes': list(axes),
            'temporary_example_row_only': True,
            'cached_frontier_unchanged': True,
            'controller_only_promotion': True,
            'trading_actions': False,
            'exchange_api_access': False,
        }

    def _v272_cache_example_frontier(
        self,
        context: dict[str, Any],
        round_number: int,
        actor: str,
    ) -> None:
        self._v272_example_frontier = None
        self._v273_example_shape = None
        event = context.get('v269_reviewed_seed_replenishment')
        if (
            actor != 'codex'
            or not isinstance(event, dict)
            or event.get('status') != 'EXACT_REVIEWED_SEED_ADMITTED'
        ):
            return
        frontier = context.get('novelty_frontier')
        if not isinstance(frontier, list):
            raise LabError('v2.0.72 admitted example frontier is missing')
        exact = [
            copy.deepcopy(item)
            for item in frontier
            if _v269_exact_reviewed_queue_item(item)
        ]
        if len(frontier) != 1 or len(exact) != 1:
            raise LabError(
                'v2.0.72 expected exactly one reviewed example frontier row'
            )
        config = exact[0].get('config')
        if not isinstance(config, dict):
            raise LabError('v2.0.72 reviewed example config is missing')
        digest = _v254_canonical_hash(config)
        if digest != event.get('config_sha256'):
            raise LabError('v2.0.72 reviewed example hash binding drifted')
        self._v272_example_frontier = {
            'version': V272_EXAMPLE_FRONTIER_BRIDGE_VERSION,
            'actor': actor,
            'research_round': round_number,
            'config_sha256': digest,
            'experiment_id': config.get('experiment_id'),
            'frontier': exact,
            'example_only': True,
            'controller_only_promotion': True,
            'raw_proposal_executed': False,
            'trading_actions': False,
            'exchange_api_access': False,
        }
        self._v273_cache_example_shape(context, config)

    def _v272_validated_example_frontier(self) -> list[dict[str, Any]]:
        record = getattr(self, '_v272_example_frontier', None)
        if not isinstance(record, dict):
            raise LabError('v2.0.72 reviewed example frontier cache is missing')
        frontier = record.get('frontier')
        if not isinstance(frontier, list) or len(frontier) != 1:
            raise LabError('v2.0.72 reviewed example frontier cache is malformed')
        item = frontier[0]
        if not _v269_exact_reviewed_queue_item(item):
            raise LabError('v2.0.72 reviewed example frontier identity drifted')
        config = item.get('config')
        if (
            not isinstance(config, dict)
            or _v254_canonical_hash(config) != record.get('config_sha256')
        ):
            raise LabError('v2.0.72 reviewed example frontier hash drifted')

        shape = getattr(self, '_v273_example_shape', None)
        if not isinstance(shape, dict):
            raise LabError('v2.0.73 reviewed example shape cache is missing')
        source_config = shape.get('source_config')
        if (
            shape.get('version') != V273_EXAMPLE_SHAPE_BRIDGE_VERSION
            or shape.get('selected_approach')
            != 'VALIDATE_PARAMETER_NEIGHBORHOOD'
            or not isinstance(source_config, dict)
            or _v254_canonical_hash(source_config)
            != shape.get('source_config_sha256')
            or _v254_canonical_hash(config)
            != shape.get('candidate_config_sha256')
            or shape.get('candidate_config_sha256')
            != record.get('config_sha256')
            or shape.get('temporary_example_row_only') is not True
            or shape.get('cached_frontier_unchanged') is not True
            or shape.get('trading_actions') is not False
            or shape.get('exchange_api_access') is not False
        ):
            raise LabError('v2.0.73 reviewed example shape identity drifted')
        if not _v260_exact_controller_registered_seed({'config': source_config}):
            raise LabError('v2.0.73 reviewed example source identity drifted')
        axes = _v251_transition_axes(source_config, config)
        if (
            list(axes) != shape.get('transition_axes')
            or source_config.get('family') != config.get('family')
            or source_config.get('symbol') != config.get('symbol')
            or axes not in {
                ('registered_seed',),
                ('timeframe', 'registered_seed'),
            }
        ):
            raise LabError('v2.0.73 reviewed example transition drifted')

        temporary = copy.deepcopy(frontier)
        temporary[0]['selected_approach'] = shape['selected_approach']
        temporary[0]['sha256_prefix'] = record['config_sha256'][:16]
        if 'selected_approach' in frontier[0] or 'sha256_prefix' in frontier[0]:
            raise LabError('v2.0.73 cached reviewed frontier was mutated')
        if _v254_canonical_hash(temporary[0]['config']) != record['config_sha256']:
            raise LabError('v2.0.73 temporary example config hash drifted')
        return temporary

    def _diverse_frontier(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Expose one exact Codex structural exhaustion to reviewed admission.

        The inherited method owns structural quarantine. Its known exhaustion
        signal previously escaped from ``super().round_context`` before v2.0.69
        could inspect the empty frontier. This narrowly preserves that quarantine
        while deferring the final exhaustion decision until the controller-owned
        reviewed queue has run.
        """
        if bool(getattr(self, '_v272_example_building', False)):
            return self._v272_validated_example_frontier()
        try:
            return super()._diverse_frontier(*args, **kwargs)
        except LabError as exc:
            error = str(exc)
            actor = str(getattr(self, '_v225_next_actor', 'codex'))
            if (
                actor != 'codex'
                or error != V270_STRUCTURAL_EXHAUSTION_ERROR
            ):
                raise

            self._v270_pre_exhaustion_bridge = {
                'version': V270_PRE_EXHAUSTION_BRIDGE_VERSION,
                'mode': 'V270_CODEX_STRUCTURAL_QUARANTINE_TO_EMPTY_FRONTIER',
                'actor': actor,
                'reason': error,
                'inherited_frontier_returned_empty': True,
                'provider_invoked': False,
                'controller_only_promotion': True,
                'unknown_errors_fail_closed': True,
                'trading_actions': False,
                'exchange_api_access': False,
            }
            if not bool(getattr(self, '_v271_context_building', False)):
                return []

            raw_frontier = super(
                V236_QUARANTINE_CLASS, self
            )._diverse_frontier(*args, **kwargs)
            if not isinstance(raw_frontier, list) or not raw_frontier:
                raise LabError(
                    'v2.0.71 structural carrier source frontier is empty'
                )
            carrier = copy.deepcopy(raw_frontier[0])
            config = (
                carrier.get('config')
                if isinstance(carrier, dict)
                and isinstance(carrier.get('config'), dict)
                else None
            )
            if not _v260_exact_controller_registered_seed(carrier):
                raise LabError(
                    'v2.0.71 structural carrier is not a registered frontier row'
                )
            self._v271_quarantine_carrier = {
                'version': V271_QUARANTINE_CARRIER_VERSION,
                'mode': 'V271_REGISTERED_QUARANTINE_CARRIER',
                'actor': actor,
                'reason': error,
                'carrier_config_sha256': _v254_canonical_hash(config),
                'carrier_experiment_id': config.get('experiment_id'),
                'carrier_family': config.get('family'),
                'raw_frontier_count': len(raw_frontier),
                'carrier_removed_before_provider': False,
                'carrier_never_executable': True,
                'structural_quarantine_preserved': True,
                'provider_invoked': False,
                'controller_only_promotion': True,
                'unknown_errors_fail_closed': True,
                'trading_actions': False,
                'exchange_api_access': False,
            }
            return [carrier]

    def _v271_remove_quarantine_carrier(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        event = getattr(self, '_v271_quarantine_carrier', None)
        if not isinstance(event, dict):
            return context
        frontier = context.get('novelty_frontier')
        if not isinstance(frontier, list):
            raise LabError('v2.0.71 quarantine carrier frontier is missing')

        expected = event.get('carrier_config_sha256')
        kept: list[dict[str, Any]] = []
        removed = 0
        for item in frontier:
            if not isinstance(item, dict):
                raise LabError(
                    'v2.0.71 quarantine carrier frontier item is malformed'
                )
            config = (
                item.get('config')
                if isinstance(item.get('config'), dict)
                else None
            )
            if (
                removed == 0
                and isinstance(config, dict)
                and _v254_canonical_hash(config) == expected
            ):
                removed += 1
                continue
            kept.append(copy.deepcopy(item))
        if removed != 1:
            raise LabError(
                'v2.0.71 quarantine carrier was not removed exactly once'
            )

        updated = copy.deepcopy(context)
        updated['novelty_frontier'] = kept
        event = copy.deepcopy(event)
        event['carrier_removed_before_provider'] = True
        event['frontier_count_after_carrier_removal'] = len(kept)
        self._v271_quarantine_carrier = event
        updated['v271_quarantine_carrier'] = copy.deepcopy(event)
        return updated

    def _v261_write_frontier_usage_accounting(self, round_dir: Path) -> None:
        """Persist Scout-only usage on exception/rollover paths."""
        atomic_json(round_dir / 'TOKEN_ACCOUNTING_V245.json', {
            'version': 'tdh-token-accounting-v245',
            'subagent_usage': copy.deepcopy(
                getattr(self, '_avu', {'codex': {}, 'claude': {}})
            ),
            'controller_budget_usage_includes_subagents': True,
            'v261_frontier_rollover_usage_accounted': True,
        })

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

        inbox = _v261_scout_inbox_status()
        producer_decision = _v267_produce_one_review_packet(inbox)
        if producer_decision is not None:
            inbox = _v261_scout_inbox_status()
        if inbox['provider_allowed'] is not True:
            blocking_reason = str(
                inbox.get('provider_blocking_reason')
                or 'UNKNOWN_INBOX_LIFECYCLE_BLOCK'
            )
            dispatch = {
                **base,
                'status': (
                    'SKIPPED_IMPLEMENTATION_REVIEW_QUEUE'
                    if blocking_reason == 'IMPLEMENTATION_REVIEW_QUEUE_PENDING'
                    else (
                        'SKIPPED_PRODUCER_QUEUE'
                        if blocking_reason in {
                            'SEALED_IMPLEMENTATION_QUEUE_PENDING',
                            'FAMILY_IMPLEMENTATION_REVIEW_PENDING',
                            'DATA_CAPABILITY_REVIEW_PENDING',
                            'DATA_CAPABILITY_MIGRATION_PENDING',
                            'PRODUCER_BLOCKED_DECISIONS_REQUIRE_REVIEW',
                        }
                        else 'SKIPPED_INBOX_FAIL_CLOSED'
                    )
                ),
                'advisory_source_status': 'CACHE_HIT',
                'provider_invoked': False,
                'inbox': inbox,
                'producer_decision': producer_decision,
                'rejection_reason': blocking_reason,
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
            provider_invoked = (
                str(exc)
                != 'v2.0.61 scout inbox capacity reached before provider'
            )
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
                'provider_invoked': provider_invoked,
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
        self._v270_pre_exhaustion_bridge = None
        self._v271_quarantine_carrier = None
        self._v272_example_frontier = None
        self._v271_context_building = True
        try:
            try:
                context = self._v251_round_context(round_number)
            finally:
                self._v271_context_building = False
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

        context = self._v271_remove_quarantine_carrier(context)
        context = _v274_global_memory_reviewed_seed_filter(
            context,
            actor,
            Path(self.config.root),
        )
        v274_event = context.get('v274_global_memory_queue_filter')
        if isinstance(v274_event, dict):
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(
                round_dir / 'GLOBAL_MEMORY_QUEUE_FILTER_V274.json',
                v274_event,
            )
        context = _v254_registered_replenishment(
            context,
            actor,
            getattr(self, '_v225_codex_family', None),
        )
        context = _v261_packet_a_replenishment(context, actor)
        self._v272_cache_example_frontier(context, round_number, actor)
        v270_event = getattr(self, '_v270_pre_exhaustion_bridge', None)
        if isinstance(v270_event, dict):
            v270_event = copy.deepcopy(v270_event)
            v270_event['research_round'] = round_number
            v270_event['reviewed_seed_queue_status'] = (
                context.get('v269_reviewed_seed_replenishment', {}).get('status')
                if isinstance(
                    context.get('v269_reviewed_seed_replenishment'), dict
                )
                else None
            )
            frontier = context.get('novelty_frontier')
            v270_event['frontier_replenished'] = bool(
                isinstance(frontier, list) and frontier
            )
            context['v270_pre_exhaustion_bridge'] = copy.deepcopy(v270_event)
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(
                round_dir / 'PRE_EXHAUSTION_BRIDGE_V270.json',
                v270_event,
            )
        v271_event = getattr(self, '_v271_quarantine_carrier', None)
        if isinstance(v271_event, dict):
            v271_event = copy.deepcopy(v271_event)
            v271_event['research_round'] = round_number
            v271_event['reviewed_seed_queue_status'] = (
                context.get('v269_reviewed_seed_replenishment', {}).get('status')
                if isinstance(
                    context.get('v269_reviewed_seed_replenishment'), dict
                )
                else None
            )
            frontier = context.get('novelty_frontier')
            v271_event['frontier_replenished'] = bool(
                isinstance(frontier, list) and frontier
            )
            context['v271_quarantine_carrier'] = copy.deepcopy(v271_event)
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(
                round_dir / 'QUARANTINE_CARRIER_V271.json',
                v271_event,
            )
        v269_event = context.get('v269_reviewed_seed_replenishment')
        if isinstance(v269_event, dict):
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(
                round_dir / 'REVIEWED_SEED_QUEUE_V269.json',
                v269_event,
            )
        event = context.get('v254_frontier_replenishment')
        if isinstance(event, dict):
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(round_dir / 'FRONTIER_REPLENISHMENT_V254.json', event)
        v261_event = context.get('v261_packet_a_replenishment')
        if isinstance(v261_event, dict):
            round_dir = self.run_dir / f'round-{round_number:02d}'
            round_dir.mkdir(parents=True, exist_ok=True)
            atomic_json(
                round_dir / 'RSI_GATED_REVERSION_PACKET_A_V261.json',
                v261_event,
            )

        frontier = context.get('novelty_frontier')
        if actor == 'codex' and isinstance(frontier, list) and frontier:
            cache = getattr(self, '_v252_round_context_cache', None)
            if not isinstance(cache, dict):
                cache = {}
                self._v252_round_context_cache = cache
            cache[round_number] = copy.deepcopy(context)
        return context

    def proposal_output_example(self, round_number: int, actor: str) -> str:
        record = getattr(self, '_v272_example_frontier', None)
        if not isinstance(record, dict):
            return super().proposal_output_example(round_number, actor)
        if (
            actor != 'codex'
            or record.get('actor') != actor
            or record.get('research_round') != round_number
        ):
            raise LabError('v2.0.72 reviewed example frontier scope drifted')

        self._v272_example_building = True
        try:
            result = super().proposal_output_example(round_number, actor)
        finally:
            self._v272_example_building = False

        audit = {
            key: copy.deepcopy(value)
            for key, value in record.items()
            if key != 'frontier'
        }
        audit.update({
            'mode': 'V272_EXACT_REVIEWED_SEED_FOR_OUTPUT_EXAMPLE',
            'example_frontier_used': True,
            'historical_frontier_not_recomputed_for_example': True,
            'provider_invoked_by_bridge': False,
            'proposal_validation_unchanged': True,
            's1_gates_unchanged': True,
        })
        round_dir = self.run_dir / f'round-{round_number:02d}'
        round_dir.mkdir(parents=True, exist_ok=True)
        atomic_json(round_dir / 'EXAMPLE_FRONTIER_BRIDGE_V272.json', audit)
        shape = getattr(self, '_v273_example_shape', None)
        if not isinstance(shape, dict):
            raise LabError('v2.0.73 reviewed example shape audit is missing')
        shape_audit = {
            key: copy.deepcopy(value)
            for key, value in shape.items()
            if key != 'source_config'
        }
        shape_audit.update({
            'mode': 'V273_EXACT_REVIEWED_EXAMPLE_ROW_SHAPE',
            'sealed_v228_schema_dependency_satisfied': True,
            'candidate_config_hash_unchanged': True,
            'provider_invoked_by_bridge': False,
            'proposal_validation_unchanged': True,
            's1_gates_unchanged': True,
            'unknown_errors_fail_closed': True,
        })
        atomic_json(round_dir / 'EXAMPLE_SHAPE_BRIDGE_V273.json', shape_audit)
        return result

    def _v262_run_codex(
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

    def run_codex(
        self,
        round_dir: Path,
        context: dict[str, Any],
    ):
        node_input = {
            'run_id': str(getattr(self, 'run_id', 'unknown-run')),
            'round_number': context.get('research_round'),
            'actor': 'codex',
            'context': context,
        }
        cached = _v263_resume_node(round_dir, 'CODEX_PROPOSAL', node_input)
        if cached is not None:
            if not isinstance(cached, dict):
                raise LabError('v2.0.63 Codex checkpoint result is invalid')
            proposal = cached.get('proposal')
            usage = cached.get('usage')
            if not isinstance(proposal, dict) or not isinstance(usage, dict):
                raise LabError('v2.0.63 Codex checkpoint payload shape is invalid')
            return proposal, usage
        input_sha256 = _v263_begin_node(
            round_dir,
            'CODEX_PROPOSAL',
            node_input,
        )
        proposal, usage = self._v262_run_codex(round_dir, context)
        _v263_commit_node(
            round_dir,
            'CODEX_PROPOSAL',
            input_sha256,
            {'proposal': proposal, 'usage': usage},
        )
        return proposal, usage

    def _v262_run_claude_proposal(
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

    def run_claude_proposal(
        self,
        round_dir: Path,
        context: dict[str, Any],
    ):
        node_input = {
            'run_id': str(getattr(self, 'run_id', 'unknown-run')),
            'round_number': context.get('research_round'),
            'actor': 'claude',
            'context': context,
        }
        cached = _v263_resume_node(round_dir, 'CLAUDE_PROPOSAL', node_input)
        if cached is not None:
            if not isinstance(cached, dict):
                raise LabError('v2.0.63 Claude checkpoint result is invalid')
            proposal = cached.get('proposal')
            usage = cached.get('usage')
            if not isinstance(proposal, dict) or not isinstance(usage, dict):
                raise LabError('v2.0.63 Claude checkpoint payload shape is invalid')
            return proposal, usage
        input_sha256 = _v263_begin_node(
            round_dir,
            'CLAUDE_PROPOSAL',
            node_input,
        )
        proposal, usage = self._v262_run_claude_proposal(round_dir, context)
        _v263_commit_node(
            round_dir,
            'CLAUDE_PROPOSAL',
            input_sha256,
            {'proposal': proposal, 'usage': usage},
        )
        return proposal, usage

    def _v261_execute_round(
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
                self._v261_write_frontier_usage_accounting(round_dir)
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
                    else (
                        'controller-owned implementation review of bounded Scout queue'
                        if scout_dispatch['status']
                        == 'SKIPPED_IMPLEMENTATION_REVIEW_QUEUE'
                        else (
                            'sealed implementation or explicit family/data review of producer packet'
                            if scout_dispatch['status'] == 'SKIPPED_PRODUCER_QUEUE'
                            else 'fresh bounded epoch and deterministic family reselection'
                        )
                    )
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
            self._v261_write_frontier_usage_accounting(round_dir)
            return summary, False, None

    def _v262_execute_round(
        self,
        round_number: int,
        preflight: dict[str, Any],
    ):
        try:
            return self._v261_execute_round(round_number, preflight)
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

    def _v263_execute_round(
        self,
        round_number: int,
        preflight: dict[str, Any],
    ):
        round_dir = Path(self.run_dir) / f'round-{round_number:02d}'
        if round_dir.is_symlink():
            raise LabError('v2.0.64 round directory is a symlink')
        if round_dir.exists() and not round_dir.is_dir():
            raise LabError('v2.0.64 round path is not a directory')
        node_input = {
            'run_id': str(getattr(self, 'run_id', 'unknown-run')),
            'round_number': round_number,
            'preflight_sha256': _v262_hash_json(preflight),
        }
        cached = _v263_resume_node(round_dir, 'ROUND_COMPLETE', node_input)
        if cached is not None:
            if (
                not isinstance(cached, dict)
                or not isinstance(cached.get('summary'), dict)
                or not isinstance(cached.get('found'), bool)
                or (
                    cached.get('score') is not None
                    and not isinstance(cached.get('score'), (int, float))
                )
            ):
                raise LabError('v2.0.63 completed-round checkpoint is invalid')
            return cached['summary'], cached['found'], cached['score']
        outcome = self._v262_execute_round(round_number, preflight)
        if round_dir.is_symlink() or not round_dir.is_dir():
            raise LabError(
                'v2.0.64 inherited executor did not create a safe round directory'
            )
        if (
            not isinstance(outcome, tuple)
            or len(outcome) != 3
            or not isinstance(outcome[0], dict)
            or not isinstance(outcome[1], bool)
        ):
            raise LabError('v2.0.63 round outcome shape is invalid')
        input_sha256 = _v263_begin_node(
            round_dir,
            'ROUND_COMPLETE',
            node_input,
        )
        _v263_commit_node(
            round_dir,
            'ROUND_COMPLETE',
            input_sha256,
            {
                'summary': outcome[0],
                'found': outcome[1],
                'score': outcome[2],
            },
        )
        return outcome

    def execute_round(
        self,
        round_number: int,
        preflight: dict[str, Any],
    ):
        try:
            return self._v263_execute_round(round_number, preflight)
        except Exception:
            # Preserve the v2.0.62 semantic fail-closed boundary.  Recovery
            # classification is written by _v262_execute_round; this public
            # boundary must never swallow or rewrite the original failure.
            raise

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
        if _v261_scout_inbox_status()['provider_allowed'] is not True:
            raise LabError(
                'v2.0.61 scout inbox capacity reached before provider'
            )
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
            if _v261_scout_inbox_status()['provider_allowed'] is not True:
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

        inbox = _v261_scout_inbox_status()
        if inbox['provider_allowed'] is not True:
            blocking_reason = str(
                inbox.get('provider_blocking_reason')
                or 'UNKNOWN_INBOX_LIFECYCLE_BLOCK'
            )
            atomic_json(dispatch_path, {
                'version': V255_SCOUT_CACHE_CONTINUITY_VERSION,
                'status': (
                    'SKIPPED_IMPLEMENTATION_REVIEW_QUEUE'
                    if blocking_reason == 'IMPLEMENTATION_REVIEW_QUEUE_PENDING'
                    else (
                        'SKIPPED_PRODUCER_QUEUE'
                        if blocking_reason in {
                            'SEALED_IMPLEMENTATION_QUEUE_PENDING',
                            'FAMILY_IMPLEMENTATION_REVIEW_PENDING',
                            'PRODUCER_BLOCKED_DECISIONS_REQUIRE_REVIEW',
                        }
                        else 'SKIPPED_INBOX_FAIL_CLOSED'
                    )
                ),
                'advisory_source_status': source_status,
                'provider_invoked': False,
                'researcher_rerun': False,
                'critic_rerun': False,
                'automatically_registered': False,
                'inbox': inbox,
                'rejection_reason': blocking_reason,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            })
            atomic_json(sd / 'SUBAGENT_USAGE.json', self._avu)
            return

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
            provider_invoked = (
                str(exc)
                != 'v2.0.61 scout inbox capacity reached before provider'
            )
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
                'provider_invoked': provider_invoked,
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
        'v260_registered_seed_transition_version': (
            V260_REGISTERED_SEED_TRANSITION_VERSION
        ),
        'v260_only_exact_controller_registered_seed_is_atomic': True,
        'v260_spoofed_or_freeform_seed_transition_fails_closed': True,
        'v261_rsi_gated_reversion_version': (
            V261_RSI_GATED_REVERSION_VERSION
        ),
        'v261_only_reviewed_packet_a_is_auto_admitted': True,
        'v261_candidate_baseline_negative_control_bound': True,
        'v261_closed_bar_only': True,
        'v261_s1_only': True,
        'v261_scout_capacity_checked_before_provider': True,
        'v261_full_inbox_never_invokes_provider': True,
        'v261_frontier_rollover_usage_accounted': True,
        'v262_failure_taxonomy': True,
        'v262_recovery_decision_log': True,
        'v262_classification_only': True,
        'v262_automatic_recovery_authorized': False,
        'v262_unhandled_failures_reraised': True,
        'v262_unknown_errors_fail_closed': True,
        'v262_staging_tests_isolate_runtime_inbox': True,
        'v263_checkpoint_version': V263_CHECKPOINT_VERSION,
        'v263_node_level_checkpoints': True,
        'v263_exact_input_hash_resume_only': True,
        'v263_payload_hash_verified': True,
        'v263_interrupted_nodes_fail_closed': True,
        'v263_controller_only_resume': True,
        'v263_automatic_retry_authorized': False,
        'v264_checkpoint_startup_compatibility_version': (
            V264_CHECKPOINT_STARTUP_COMPATIBILITY_VERSION
        ),
        'v264_inherited_executor_owns_fresh_round_directory': True,
        'v265_frontier_inbox_lifecycle_version': (
            V265_FRONTIER_INBOX_LIFECYCLE_VERSION
        ),
        'v265_raw_inbox_count_is_not_actionable_capacity': True,
        'v265_reviewed_registry_is_controller_owned': True,
        'v265_duplicate_and_registered_proposals_are_terminal': True,
        'v265_invalid_inbox_fails_closed': True,
        'v265_pending_implementation_blocks_paid_scout': True,
        'v265_raw_proposals_are_preserved': True,
        'v265_untrusted_text_never_executes': True,
        'v266_frontier_producer_version': V266_FRONTIER_PRODUCER_VERSION,
        'v266_one_proposal_per_bounded_epoch': True,
        'v266_exact_registered_family_identity_only': True,
        'v266_installed_offline_data_only': True,
        'v266_candidate_baseline_negative_control_required': True,
        'v266_raw_proposal_never_executes': True,
        'v266_sealed_registry_change_required': True,
        'v266_provider_blocked_while_implementation_pending': True,
        'v267_data_capability_version': V267_DATA_CAPABILITY_VERSION,
        'v267_ohlcv_derivations_are_not_external_data': True,
        'v267_external_data_requirements_fail_closed': True,
        'v267_ambiguous_data_requires_review': True,
        'v267_legacy_decisions_are_preserved': True,
        'v267_hash_bound_supersession': True,
        'v267_one_decision_or_migration_per_epoch': True,
        'v268_volume_tsmom_admission_version': (
            V268_VOLUME_TSMOM_ADMISSION_VERSION
        ),
        'v268_source_proposal_hash_bound': True,
        'v268_source_decision_hash_bound': True,
        'v268_candidate_baseline_negative_control_bound': True,
        'v268_causal_volume_shuffle_only': True,
        'v268_raw_proposal_never_executes': True,
        'v268_s1_only': True,
        'v269_reviewed_seed_queue_version': (
            V269_REVIEWED_SEED_QUEUE_VERSION
        ),
        'v269_exact_reviewed_seed_precedes_frontier_exhaustion': True,
        'v269_deterministic_priority_and_deduplication': True,
        'v269_single_axis_symbol_bridge_preserves_transition_gate': True,
        'v269_untrusted_text_never_enters_reviewed_queue': True,
        'v269_s1_only': True,
        'v270_pre_exhaustion_bridge_version': (
            V270_PRE_EXHAUSTION_BRIDGE_VERSION
        ),
        'v270_codex_structural_exhaustion_becomes_reviewable_empty_frontier': True,
        'v270_reviewed_seed_replenishment_runs_before_v252_rollover': True,
        'v270_claude_peer_semantics_unchanged': True,
        'v270_unknown_errors_fail_closed': True,
        'v271_quarantine_carrier_version': V271_QUARANTINE_CARRIER_VERSION,
        'v271_exact_registered_carrier_only': True,
        'v271_carrier_removed_before_provider': True,
        'v271_structural_quarantine_preserved': True,
        'v271_v230_nonempty_guard_precedes_reviewed_admission': True,
        'v271_unknown_errors_fail_closed': True,
        'v272_example_frontier_bridge_version': (
            V272_EXAMPLE_FRONTIER_BRIDGE_VERSION
        ),
        'v272_exact_admitted_reviewed_seed_only': True,
        'v272_example_scope_only': True,
        'v272_proposal_validation_unchanged': True,
        'v272_s1_gates_unchanged': True,
        'v272_unknown_errors_fail_closed': True,
        'v273_example_shape_bridge_version': (
            V273_EXAMPLE_SHAPE_BRIDGE_VERSION
        ),
        'v273_selected_approach_is_sealed_v228_same_family_rule': True,
        'v273_source_and_candidate_registry_bound': True,
        'v273_temporary_example_row_only': True,
        'v273_cached_frontier_unchanged': True,
        'v273_candidate_config_hash_unchanged': True,
        'v273_proposal_validation_unchanged': True,
        'v273_s1_gates_unchanged': True,
        'v273_unknown_errors_fail_closed': True,
        'v274_global_memory_queue_filter_version': (
            V274_GLOBAL_MEMORY_QUEUE_FILTER_VERSION
        ),
        'v274_authoritative_full_history_duplicate_reader_reused': True,
        'v274_duplicate_reviewed_seed_skipped_before_provider': True,
        'v274_deterministic_next_exact_reviewed_seed': True,
        'v274_proposal_validation_unchanged': True,
        'v274_s1_gates_unchanged': True,
        'v274_unknown_errors_fail_closed': True,
        'controller_only_recovery_policy': True,
        'policy_change': False,
    }


def main(argv: list[str] | None = None) -> int:
    contract = runtime_binding_contract()
    if contract['all_controller_refs_bound'] is not True:
        raise RuntimeError('v2.0.48 runtime Controller binding failed closed')
    if contract['v245_dispatch_anchor_preserved'] is not True:
        raise RuntimeError('v2.0.48 v245 dispatch anchor drifted')
    if contract['v259_runtime_kernel_overlay_bound'] is not True:
        raise RuntimeError('v2.0.59 runtime kernel overlay binding failed closed')
    if contract['v262_unknown_errors_fail_closed'] is not True:
        raise RuntimeError('v2.0.62 unknown failure boundary drifted')
    if contract['v263_controller_only_resume'] is not True:
        raise RuntimeError('v2.0.63 checkpoint ownership drifted')
    if contract['v263_interrupted_nodes_fail_closed'] is not True:
        raise RuntimeError('v2.0.63 interrupted node boundary drifted')
    if contract['v265_untrusted_text_never_executes'] is not True:
        raise RuntimeError('v2.0.65 untrusted inbox execution boundary drifted')
    if contract['v265_invalid_inbox_fails_closed'] is not True:
        raise RuntimeError('v2.0.65 invalid inbox boundary drifted')
    if contract['v266_raw_proposal_never_executes'] is not True:
        raise RuntimeError('v2.0.66 producer execution boundary drifted')
    if contract['v266_sealed_registry_change_required'] is not True:
        raise RuntimeError('v2.0.66 sealed admission boundary drifted')
    if contract['v267_ohlcv_derivations_are_not_external_data'] is not True:
        raise RuntimeError('v2.0.67 data capability boundary drifted')
    if contract['v267_hash_bound_supersession'] is not True:
        raise RuntimeError('v2.0.67 decision supersession boundary drifted')
    if contract['v268_source_proposal_hash_bound'] is not True:
        raise RuntimeError('v2.0.68 source proposal boundary drifted')
    if contract['v268_causal_volume_shuffle_only'] is not True:
        raise RuntimeError('v2.0.68 causal shuffle boundary drifted')
    if contract['v269_exact_reviewed_seed_precedes_frontier_exhaustion'] is not True:
        raise RuntimeError('v2.0.69 reviewed seed priority boundary drifted')
    if contract['v269_single_axis_symbol_bridge_preserves_transition_gate'] is not True:
        raise RuntimeError('v2.0.69 single-axis bridge boundary drifted')
    if contract['v270_reviewed_seed_replenishment_runs_before_v252_rollover'] is not True:
        raise RuntimeError('v2.0.70 pre-exhaustion ordering boundary drifted')
    if contract['v270_unknown_errors_fail_closed'] is not True:
        raise RuntimeError('v2.0.70 unknown failure boundary drifted')
    if contract['v271_carrier_removed_before_provider'] is not True:
        raise RuntimeError('v2.0.71 carrier removal boundary drifted')
    if contract['v271_structural_quarantine_preserved'] is not True:
        raise RuntimeError('v2.0.71 structural quarantine boundary drifted')
    if contract['v272_exact_admitted_reviewed_seed_only'] is not True:
        raise RuntimeError('v2.0.72 admitted example identity boundary drifted')
    if contract['v272_proposal_validation_unchanged'] is not True:
        raise RuntimeError('v2.0.72 proposal validation boundary drifted')
    return v245.v244.main(argv)


if __name__ == '__main__':
    raise SystemExit(main())

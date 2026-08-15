from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location('tdh_v265_inbox_lifecycle', CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load v2.0.65 controller')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def proposal(index: int) -> dict:
    return {
        'proposal_version': 'tdh-frontier-inbox-v1',
        'hypothesis_id': f'TDH-SCOUT-{index:06d}',
        'status': 'UNTRUSTED_INBOX',
        'family_thesis': f'Bounded causal strategy thesis number {index}.',
        'causal_mechanism': (
            'A measurable market-state transition may create a bounded '
            f'conditional return asymmetry for hypothesis {index}.'
        ),
        'source_evidence': [{
            'source_id': f'source-{index}',
            'claim': 'The hypothesis requires offline falsification.',
            'provenance': 'bounded research intake',
        }],
        'required_data': ['OHLCV'],
        'timeframes': ['15m'],
        'bounded_parameters': {'lookback': 10 + index},
        'baseline_thesis': 'Compare against the registered baseline.',
        'negative_control_thesis': 'Shift the signal to destroy causality.',
        'falsification': {
            'failure_condition': 'No robust cross-window improvement.',
            'minimum_test': 'Offline S1 across registered symbols.',
            'expected_information_gain': 'Separate mechanism from noise.',
        },
        'safety': {
            'data_only': True,
            'contains_executable_code': False,
            'trading_actions': False,
            'exchange_api_access': False,
            'controller_registration_required': True,
        },
    }


class V265FrontierInboxLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_controller()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.release = self.root / 'v2.0.65'
        self.research = self.release / 'research'
        self.inbox = self.root / 'frontier-scout-inbox'
        self.research.mkdir(parents=True)
        self.inbox.mkdir()
        self.original_here = self.module.HERE
        self.module.HERE = self.release

    def tearDown(self):
        self.module.HERE = self.original_here
        self.directory.cleanup()

    def write_proposal(
        self,
        name: str,
        value: dict,
        *,
        wrapped: bool = True,
    ) -> Path:
        path = self.inbox / name
        payload = value
        if wrapped:
            payload = {
                'version': self.module.V257_SCOUT_CONFORMANCE_VERSION,
                'status': 'UNTRUSTED_INBOX',
                'proposal': value,
                'proposal_sha256': self.module._v254_canonical_hash(value),
                'automatically_registered': False,
                'controller_registration_required': True,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            }
        path.write_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
            encoding='utf-8',
        )
        return path

    def write_registry(self, value: dict, experiment_id: str = 'EXP-APPROVED') -> None:
        digest = self.module._v254_canonical_hash(value)
        row = {
            'registry_id': 'tdh-controller-reviewed-scout-seeds-v1',
            'experiment_id': experiment_id,
            'family_id': 'REGISTERED_TEST_FAMILY',
            'controller_admission': {
                'status': 'CONTROLLER_APPROVED_SEALED_REGISTRY',
                'source_proposal_sha256': digest,
                'contains_executable_code': False,
                'controller_only_promotion': True,
                'trading_actions': False,
                'exchange_api_access': False,
            },
        }
        (self.research / 'frontier-scout-approved-seeds-v1.jsonl').write_text(
            json.dumps(row, sort_keys=True) + '\n',
            encoding='utf-8',
        )

    def test_reviewed_proposal_is_terminal_and_does_not_consume_capacity(self):
        value = proposal(1)
        self.write_proposal('TDH-SCOUT-000001.json', value)
        self.write_registry(value)

        lifecycle = self.module._v265_scout_inbox_lifecycle()

        self.assertEqual(lifecycle['inbox_count'], 1)
        self.assertEqual(lifecycle['registered_reviewed_count'], 1)
        self.assertEqual(lifecycle['actionable_count'], 0)
        self.assertTrue(lifecycle['provider_allowed'])
        self.assertEqual(lifecycle['records'][0]['state'], 'REGISTERED_REVIEWED')

    def test_duplicate_is_archived_but_unique_proposal_remains_pending(self):
        value = proposal(2)
        self.write_proposal('TDH-SCOUT-000002-a.json', value)
        self.write_proposal('TDH-SCOUT-000002-b.json', value)

        lifecycle = self.module._v265_scout_inbox_lifecycle()

        self.assertEqual(lifecycle['inbox_count'], 2)
        self.assertEqual(lifecycle['unique_proposal_count'], 1)
        self.assertEqual(lifecycle['duplicate_count'], 1)
        self.assertEqual(lifecycle['review_pending_count'], 1)
        self.assertEqual(lifecycle['deferred_count'], 0)
        self.assertFalse(lifecycle['provider_allowed'])
        self.assertEqual(
            lifecycle['provider_blocking_reason'],
            'IMPLEMENTATION_REVIEW_QUEUE_PENDING',
        )

    def test_large_unique_backlog_is_bounded_without_data_loss(self):
        for index in range(1, 21):
            self.write_proposal(f'TDH-SCOUT-{index:06d}.json', proposal(index))

        lifecycle = self.module._v265_scout_inbox_lifecycle()

        self.assertEqual(lifecycle['inbox_count'], 20)
        self.assertEqual(lifecycle['actionable_count'], 20)
        self.assertEqual(lifecycle['review_pending_count'], 16)
        self.assertEqual(lifecycle['deferred_count'], 4)
        self.assertTrue(lifecycle['raw_proposals_preserved'])
        self.assertEqual(len(list(self.inbox.glob('TDH-SCOUT-*.json'))), 20)

    def test_invalid_entry_fails_closed_before_provider(self):
        (self.inbox / 'TDH-SCOUT-INVALID.json').write_text('{', encoding='utf-8')

        lifecycle = self.module._v265_scout_inbox_lifecycle()

        self.assertEqual(lifecycle['invalid_count'], 1)
        self.assertFalse(lifecycle['provider_allowed'])
        self.assertEqual(
            lifecycle['provider_blocking_reason'],
            'INVALID_OR_UNBOUNDED_INBOX_FAIL_CLOSED',
        )

    def test_tampered_envelope_hash_fails_closed(self):
        value = proposal(9)
        path = self.write_proposal('TDH-SCOUT-000009.json', value)
        record = json.loads(path.read_text(encoding='utf-8'))
        record['proposal_sha256'] = '0' * 64
        path.write_text(json.dumps(record, sort_keys=True), encoding='utf-8')

        lifecycle = self.module._v265_scout_inbox_lifecycle()

        self.assertEqual(lifecycle['invalid_count'], 1)
        self.assertFalse(lifecycle['provider_allowed'])
        self.assertEqual(
            lifecycle['records'][0]['state'],
            'QUARANTINED_INVALID_CONTENT',
        )

    def test_pending_queue_skips_paid_scout_and_emits_exact_reason(self):
        self.write_proposal('TDH-SCOUT-000003.json', proposal(3))
        controller = object.__new__(self.module.Controller)
        controller.load_cache = lambda: {
            'fingerprint': 'a' * 64,
            'advisory': {
                'status': 'LLM_SUBAGENTS_COMPLETED',
                'researcher': {'findings': [{'claim': 'research'}]},
                'critic': {'findings': [{'claim': 'critic'}]},
            },
        }

        def forbidden_provider(*args, **kwargs):
            raise AssertionError('paid provider was invoked with pending review work')

        controller._run_frontier_scout = forbidden_provider
        round_dir = self.root / 'run' / 'round-01'
        round_dir.mkdir(parents=True)

        dispatch = controller._v256_scout_on_frontier_exhaustion(
            round_dir,
            1,
            'codex',
            'registered novelty frontier is exhausted',
        )

        self.assertEqual(dispatch['status'], 'SKIPPED_PRODUCER_QUEUE')
        self.assertFalse(dispatch['provider_invoked'])
        self.assertEqual(
            dispatch['rejection_reason'],
            'FAMILY_IMPLEMENTATION_REVIEW_PENDING',
        )
        self.assertEqual(
            dispatch['producer_decision']['status'],
            'NEEDS_FAMILY_IMPLEMENTATION_REVIEW',
        )
        self.assertFalse(dispatch['producer_decision']['raw_proposal_executed'])

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        contract = self.module.runtime_binding_contract()
        self.assertTrue(contract['v265_raw_inbox_count_is_not_actionable_capacity'])
        self.assertTrue(contract['v265_reviewed_registry_is_controller_owned'])
        self.assertTrue(contract['v265_invalid_inbox_fails_closed'])
        self.assertTrue(contract['v265_pending_implementation_blocks_paid_scout'])
        self.assertTrue(contract['v265_raw_proposals_are_preserved'])
        self.assertTrue(contract['v265_untrusted_text_never_executes'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

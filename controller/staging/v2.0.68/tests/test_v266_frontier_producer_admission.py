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
    spec = importlib.util.spec_from_file_location(
        'tdh_v266_frontier_producer_admission', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load v2.0.66 controller')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def proposal(
    index: int,
    *,
    family_text: str = 'REGISTERED_TEST_FAMILY',
    required_data: list[str] | None = None,
) -> dict:
    return {
        'proposal_version': 'tdh-frontier-inbox-v1',
        'hypothesis_id': f'TDH-SCOUT-{index:06d}',
        'status': 'UNTRUSTED_INBOX',
        'family_thesis': (
            f'{family_text} provides a bounded causal strategy thesis {index}.'
        ),
        'causal_mechanism': (
            'A measurable closed-bar market-state transition may create a '
            'bounded conditional return asymmetry that requires falsification.'
        ),
        'source_evidence': [{
            'source_id': f'source-{index}',
            'claim': 'The hypothesis requires offline falsification.',
            'provenance': 'bounded research intake',
        }],
        'required_data': required_data or ['OHLCV'],
        'timeframes': ['15m'],
        'bounded_parameters': {'lookback': 10 + index},
        'baseline_thesis': 'Compare against the immutable registered baseline.',
        'negative_control_thesis': 'Shift the signal to destroy causal timing.',
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


class V266FrontierProducerAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_controller()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.release = self.root / 'v2.0.66'
        self.research = self.release / 'research'
        self.inbox = self.root / 'frontier-scout-inbox'
        self.research.mkdir(parents=True)
        self.inbox.mkdir()
        self.original_here = self.module.HERE
        self.original_registry = self.module.kernel.registry
        self.module.HERE = self.release
        self.module.kernel.registry = lambda: ({
            'REGISTERED_TEST_FAMILY': {
                'family_id': 'REGISTERED_TEST_FAMILY',
                'name': 'Registered Test Family',
                'required_data': ['ohlcv'],
            },
            'SECOND_TEST_FAMILY': {
                'family_id': 'SECOND_TEST_FAMILY',
                'name': 'Second Test Family',
                'required_data': ['ohlcv'],
            },
        }, {})

    def tearDown(self):
        self.module.kernel.registry = self.original_registry
        self.module.HERE = self.original_here
        self.directory.cleanup()

    def write_proposal(self, name: str, value: dict) -> Path:
        digest = self.module._v254_canonical_hash(value)
        payload = {
            'version': self.module.V257_SCOUT_CONFORMANCE_VERSION,
            'status': 'UNTRUSTED_INBOX',
            'proposal': value,
            'proposal_sha256': digest,
            'automatically_registered': False,
            'controller_registration_required': True,
            'controller_only_promotion': True,
            'trading_actions': False,
            'exchange_api_access': False,
        }
        path = self.inbox / name
        path.write_text(json.dumps(payload, sort_keys=True), encoding='utf-8')
        return path

    def test_exact_family_and_installed_data_create_sealed_implementation_packet(self):
        value = proposal(1)
        raw_path = self.write_proposal('TDH-SCOUT-000001.json', value)
        lifecycle = self.module._v265_scout_inbox_lifecycle()

        decision = self.module._v266_produce_one_review_packet(lifecycle)

        self.assertEqual(decision['status'], 'READY_FOR_SEALED_IMPLEMENTATION')
        self.assertEqual(decision['registered_family_id'], 'REGISTERED_TEST_FAMILY')
        self.assertTrue(decision['candidate_baseline_negative_control_required'])
        self.assertTrue(decision['sealed_registry_change_required'])
        self.assertFalse(decision['raw_proposal_executed'])
        self.assertTrue(raw_path.is_file())
        after = self.module._v265_scout_inbox_lifecycle()
        self.assertEqual(after['review_pending_count'], 0)
        self.assertEqual(after['producer_ready_count'], 1)
        self.assertEqual(after['records'][0]['state'], 'READY_FOR_SEALED_IMPLEMENTATION')
        self.assertEqual(
            after['provider_blocking_reason'],
            'SEALED_IMPLEMENTATION_QUEUE_PENDING',
        )

    def test_same_input_is_idempotent_and_never_duplicates_state(self):
        value = proposal(2)
        self.write_proposal('TDH-SCOUT-000002.json', value)
        lifecycle = self.module._v265_scout_inbox_lifecycle()

        first = self.module._v266_produce_one_review_packet(lifecycle)
        second = self.module._v266_produce_one_review_packet(lifecycle)

        self.assertEqual(first, second)
        state_files = list((self.root / 'frontier-producer-state').glob('*.json'))
        self.assertEqual(len(state_files), 1)

    def test_missing_offline_dataset_is_blocked_without_execution(self):
        value = proposal(3, required_data=['OHLCV', 'funding'])
        self.write_proposal('TDH-SCOUT-000003.json', value)

        decision = self.module._v266_produce_one_review_packet()

        self.assertEqual(decision['status'], 'BLOCKED_MISSING_OFFLINE_DATA')
        self.assertEqual(decision['missing_offline_data'], ['funding'])
        self.assertFalse(decision['raw_proposal_executed'])

    def test_unknown_family_requires_implementation_review(self):
        value = proposal(4, family_text='A novel spectral entropy hypothesis')
        self.write_proposal('TDH-SCOUT-000004.json', value)

        decision = self.module._v266_produce_one_review_packet()

        self.assertEqual(
            decision['status'], 'NEEDS_FAMILY_IMPLEMENTATION_REVIEW'
        )
        self.assertIsNone(decision['registered_family_id'])
        self.assertFalse(decision['automatically_registered'])

    def test_ambiguous_family_identity_is_quarantined(self):
        value = proposal(
            5,
            family_text='REGISTERED_TEST_FAMILY plus SECOND_TEST_FAMILY',
        )
        self.write_proposal('TDH-SCOUT-000005.json', value)

        decision = self.module._v266_produce_one_review_packet()

        self.assertEqual(decision['status'], 'QUARANTINED_AMBIGUOUS_FAMILY')
        self.assertEqual(
            decision['registered_family_matches'],
            ['REGISTERED_TEST_FAMILY', 'SECOND_TEST_FAMILY'],
        )

    def test_tampered_persisted_decision_fails_closed(self):
        value = proposal(6)
        self.write_proposal('TDH-SCOUT-000006.json', value)
        decision = self.module._v266_produce_one_review_packet()
        path = self.module._v266_decision_path(decision['source_proposal_sha256'])
        stored = json.loads(path.read_text(encoding='utf-8'))
        stored['raw_proposal_executed'] = True
        path.write_text(json.dumps(stored, sort_keys=True), encoding='utf-8')

        with self.assertRaisesRegex(
            self.module.LabError, 'producer decision contract drift'
        ):
            self.module._v265_scout_inbox_lifecycle()

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        contract = self.module.runtime_binding_contract()
        self.assertTrue(contract['v266_one_proposal_per_bounded_epoch'])
        self.assertTrue(contract['v266_exact_registered_family_identity_only'])
        self.assertTrue(contract['v266_installed_offline_data_only'])
        self.assertTrue(contract['v266_candidate_baseline_negative_control_required'])
        self.assertTrue(contract['v266_raw_proposal_never_executes'])
        self.assertTrue(contract['v266_sealed_registry_change_required'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

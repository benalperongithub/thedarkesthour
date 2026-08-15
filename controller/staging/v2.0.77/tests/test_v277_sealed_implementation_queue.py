from __future__ import annotations

import copy
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
        'tdh_v277_sealed_implementation_queue_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def proposal(
    index: int,
    *,
    required_data: list[str] | None = None,
) -> dict:
    return {
        'proposal_version': 'tdh-frontier-inbox-v1',
        'hypothesis_id': f'TDH-SCOUT-{index:06d}',
        'status': 'UNTRUSTED_INBOX',
        'family_thesis': (
            f'REGISTERED_TEST_FAMILY provides a bounded causal thesis {index}.'
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


class V277SealedImplementationQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_controller()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.release = self.root / 'v2.0.77'
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
        }, {})

    def tearDown(self):
        self.module.kernel.registry = self.original_registry
        self.module.HERE = self.original_here
        self.directory.cleanup()

    def write_proposal(self, index: int, value: dict) -> Path:
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
        path = self.inbox / f'TDH-SCOUT-{index:06d}.json'
        path.write_text(json.dumps(payload, sort_keys=True), encoding='utf-8')
        return path

    def admit_all(self) -> dict:
        while True:
            decision = self.module._v267_produce_one_review_packet()
            if decision is None:
                break
        return self.module._v265_scout_inbox_lifecycle()

    def test_selects_one_ready_record_in_deterministic_identity_order(self):
        self.write_proposal(2, proposal(2))
        self.write_proposal(1, proposal(1))
        lifecycle = self.admit_all()

        packet = self.module._v277_select_sealed_implementation_packet(lifecycle)

        self.assertIsNotNone(packet)
        assert packet is not None
        self.assertEqual(packet['status'], 'SELECTED_FOR_CONTROLLER_IMPLEMENTATION_REVIEW')
        self.assertEqual(packet['source_hypothesis_id'], 'TDH-SCOUT-000001')
        self.assertEqual(packet['registered_family_id'], 'REGISTERED_TEST_FAMILY')
        self.assertEqual(packet['selection_order'], 'hypothesis_id,proposal_sha256,file')
        self.assertTrue(packet['data_only_review_packet'])
        self.assertFalse(packet['provider_invoked_by_selector'])
        self.assertFalse(packet['automatically_registered'])
        self.assertFalse(packet['s1_invoked_by_selector'])
        self.assertFalse(packet['trading_actions'])
        self.assertFalse(packet['exchange_api_access'])
        payload = copy.deepcopy(packet)
        payload_digest = payload.pop('packet_payload_sha256')
        self.assertEqual(payload_digest, self.module._v254_canonical_hash(payload))

    def test_ohlcv_derived_requirements_are_hash_bound_without_execution(self):
        self.write_proposal(
            3,
            proposal(3, required_data=['OHLCV', 'rolling return']),
        )
        lifecycle = self.admit_all()

        packet = self.module._v277_select_sealed_implementation_packet(lifecycle)

        self.assertIsNotNone(packet)
        assert packet is not None
        capabilities = {
            row['requirement']: row['capability']
            for row in packet['required_data_capabilities']
        }
        self.assertEqual(capabilities['OHLCV'], 'INSTALLED_RAW_OHLCV')
        self.assertEqual(capabilities['rolling return'], 'DERIVABLE_FROM_OHLCV')
        self.assertEqual(packet['source_decision_version'], self.module.V267_DATA_CAPABILITY_VERSION)
        self.assertRegex(packet['source_proposal_sha256'], r'^[0-9a-f]{64}$')
        self.assertRegex(packet['source_decision_sha256'], r'^[0-9a-f]{64}$')
        self.assertFalse(packet['raw_proposal_executed'])
        self.assertFalse(packet['contains_executable_code'])

    def test_no_ready_record_returns_no_packet(self):
        self.assertIsNone(self.module._v277_select_sealed_implementation_packet())

    def test_external_data_record_remains_blocked_and_unselected(self):
        self.write_proposal(4, proposal(4, required_data=['OHLCV', 'funding']))
        lifecycle = self.admit_all()

        self.assertEqual(lifecycle['producer_ready_count'], 0)
        self.assertIsNone(
            self.module._v277_select_sealed_implementation_packet(lifecycle)
        )

    def test_lifecycle_decision_hash_drift_fails_closed(self):
        self.write_proposal(5, proposal(5))
        lifecycle = self.admit_all()
        tampered = copy.deepcopy(lifecycle)
        ready = next(
            row for row in tampered['records']
            if row['state'] == 'READY_FOR_SEALED_IMPLEMENTATION'
        )
        ready['producer_decision_sha256'] = '0' * 64

        with self.assertRaisesRegex(self.module.LabError, 'decision drifted'):
            self.module._v277_select_sealed_implementation_packet(tampered)

    def test_invalid_or_unbounded_inbox_fails_closed(self):
        lifecycle = {
            'invalid_count': 1,
            'raw_hard_limit_reached': False,
            'records': [],
        }
        with self.assertRaisesRegex(self.module.LabError, 'refuses unsafe inbox'):
            self.module._v277_select_sealed_implementation_packet(lifecycle)

    def test_runtime_contract_preserves_controller_only_offline_policy(self):
        contract = self.module.runtime_binding_contract()
        self.assertEqual(
            contract['v277_sealed_implementation_queue_version'],
            self.module.V277_SEALED_IMPLEMENTATION_QUEUE_VERSION,
        )
        self.assertTrue(contract['v277_one_deterministic_packet_selected'])
        self.assertTrue(contract['v277_proposal_and_decision_hash_bound'])
        self.assertTrue(contract['v277_registered_family_and_data_capability_bound'])
        self.assertTrue(contract['v277_data_only_review_packet'])
        self.assertFalse(contract['v277_provider_invoked_by_selector'])
        self.assertFalse(contract['v277_automatic_registration'])
        self.assertFalse(contract['v277_s1_invoked_by_selector'])
        self.assertTrue(contract['v277_unknown_errors_fail_closed'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

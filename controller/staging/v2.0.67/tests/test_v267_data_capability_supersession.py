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
        'tdh_v267_data_capability_supersession', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('cannot load v2.0.67 controller')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def proposal(index: int, required_data: list[str]) -> dict:
    return {
        'proposal_version': 'tdh-frontier-inbox-v1',
        'hypothesis_id': f'TDH-SCOUT-{index:06d}',
        'status': 'UNTRUSTED_INBOX',
        'family_thesis': (
            f'VOLUME_TSMOM provides a bounded causal strategy thesis {index}.'
        ),
        'causal_mechanism': (
            'A closed-bar volume-conditioned momentum transition may create '
            'a bounded return asymmetry that requires falsification.'
        ),
        'source_evidence': [{
            'source_id': f'source-{index}',
            'claim': 'The hypothesis requires offline falsification.',
            'provenance': 'bounded research intake',
        }],
        'required_data': required_data,
        'timeframes': ['15m'],
        'bounded_parameters': {'lookback': 10 + index},
        'baseline_thesis': 'Compare against the immutable registered baseline.',
        'negative_control_thesis': 'Shuffle volume labels to destroy timing.',
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


class V267DataCapabilitySupersessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_controller()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.release = self.root / 'v2.0.67'
        self.inbox = self.root / 'frontier-scout-inbox'
        (self.release / 'research').mkdir(parents=True)
        self.inbox.mkdir()
        self.original_here = self.module.HERE
        self.original_registry = self.module.kernel.registry
        self.module.HERE = self.release
        self.module.kernel.registry = lambda: ({
            'VOLUME_TSMOM': {
                'family_id': 'VOLUME_TSMOM',
                'name': 'Volume Time Series Momentum',
                'required_data': ['ohlcv'],
            },
        }, {})

    def tearDown(self):
        self.module.kernel.registry = self.original_registry
        self.module.HERE = self.original_here
        self.directory.cleanup()

    def write_proposal(self, value: dict) -> tuple[Path, str]:
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
        path = self.inbox / f"{value['hypothesis_id']}.json"
        path.write_text(json.dumps(payload, sort_keys=True), encoding='utf-8')
        return path, digest

    def test_live_semantic_requirements_are_ohlcv_derivable(self):
        raw_path, digest = self.write_proposal(proposal(1, [
            'coin-pair trade counts',
            'cross-coin correlation matrix excluding DOGE',
            'non-DOGE OHLCV+volume',
            'S1 expectancy per coin',
            'shuffled volume-label control series',
            'volume percentile rank',
        ]))

        legacy = self.module._v266_produce_one_review_packet()
        self.assertEqual(legacy['status'], 'BLOCKED_MISSING_OFFLINE_DATA')
        before = self.module._v265_scout_inbox_lifecycle()
        self.assertEqual(before['data_capability_migration_count'], 1)

        decision = self.module._v267_produce_one_review_packet(before)

        self.assertEqual(decision['status'], 'READY_FOR_SEALED_IMPLEMENTATION')
        self.assertEqual(decision['registered_family_id'], 'VOLUME_TSMOM')
        self.assertEqual(decision['missing_external_data'], [])
        self.assertEqual(decision['ambiguous_data_requirements'], [])
        self.assertEqual(decision['prior_status'], 'BLOCKED_MISSING_OFFLINE_DATA')
        self.assertEqual(
            decision['supersedes_decision_sha256'],
            self.module._v254_canonical_hash(legacy),
        )
        self.assertTrue(raw_path.is_file())
        self.assertTrue(self.module._v266_decision_path(digest).is_file())
        self.assertTrue(self.module._v267_decision_path(digest).is_file())
        after = self.module._v265_scout_inbox_lifecycle()
        self.assertEqual(after['data_capability_migration_count'], 0)
        self.assertEqual(after['producer_ready_count'], 1)

    def test_external_raw_datasets_remain_blocked(self):
        self.write_proposal(proposal(2, [
            'OHLCV', 'funding rates', 'open interest',
            'L2 order book snapshots', 'liquidation feed',
        ]))

        decision = self.module._v267_produce_one_review_packet()

        self.assertEqual(decision['status'], 'BLOCKED_MISSING_EXTERNAL_DATA')
        self.assertEqual(len(decision['missing_external_data']), 4)
        self.assertFalse(decision['raw_proposal_executed'])

    def test_ambiguous_requirement_needs_review_and_never_executes(self):
        self.write_proposal(proposal(3, ['proprietary composite feed']))

        decision = self.module._v267_produce_one_review_packet()

        self.assertEqual(decision['status'], 'NEEDS_DATA_CAPABILITY_REVIEW')
        self.assertEqual(
            decision['ambiguous_data_requirements'],
            ['proprietary composite feed'],
        )
        self.assertFalse(decision['raw_proposal_executed'])

    def test_only_one_legacy_decision_is_superseded_per_epoch(self):
        for index in (4, 5):
            self.write_proposal(proposal(index, ['S1 expectancy per coin']))
            legacy = self.module._v266_produce_one_review_packet()
            self.assertEqual(legacy['status'], 'BLOCKED_MISSING_OFFLINE_DATA')
        lifecycle = self.module._v265_scout_inbox_lifecycle()
        self.assertEqual(lifecycle['data_capability_migration_count'], 2)

        self.module._v267_produce_one_review_packet(lifecycle)

        state_root = self.root / 'frontier-producer-state'
        self.assertEqual(len(list(state_root.glob('*.v267.json'))), 1)
        after = self.module._v265_scout_inbox_lifecycle()
        self.assertEqual(after['data_capability_migration_count'], 1)

    def test_tampered_supersession_link_fails_closed(self):
        _, digest = self.write_proposal(proposal(6, ['volume percentile rank']))
        self.module._v266_produce_one_review_packet()
        self.module._v267_produce_one_review_packet()
        path = self.module._v267_decision_path(digest)
        stored = json.loads(path.read_text(encoding='utf-8'))
        stored['supersedes_decision_sha256'] = '0' * 64
        path.write_text(json.dumps(stored, sort_keys=True), encoding='utf-8')

        with self.assertRaisesRegex(
            self.module.LabError, 'supersession linkage drift'
        ):
            self.module._v265_scout_inbox_lifecycle()

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        contract = self.module.runtime_binding_contract()
        self.assertTrue(contract['v267_ohlcv_derivations_are_not_external_data'])
        self.assertTrue(contract['v267_external_data_requirements_fail_closed'])
        self.assertTrue(contract['v267_ambiguous_data_requires_review'])
        self.assertTrue(contract['v267_legacy_decisions_are_preserved'])
        self.assertTrue(contract['v267_hash_bound_supersession'])
        self.assertTrue(contract['v267_one_decision_or_migration_per_epoch'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

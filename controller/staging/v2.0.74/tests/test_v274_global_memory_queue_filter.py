from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v274_global_memory_queue_filter_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V274GlobalMemoryQueueFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-VOL80-NODOGE-1D'],
                'BTCUSDT',
            )
        )
        cls.queue_configs = {}
        for experiment_id in MODULE.V269_REVIEWED_SEED_PRIORITY:
            cls.queue_configs[experiment_id] = MODULE.kernel.validate_config(
                MODULE.kernel.performance_config(
                    experiments[experiment_id],
                    'BTCUSDT',
                )
            )

    def context(self):
        return {
            'novelty_frontier': [],
            'previous_rounds': [],
            'negative_memory': [],
            'research_program_memory': {},
            'latest_s1_financial_evidence': {
                'source_run_id': 'sealed-source-run',
                'source_round': 1,
                'source_result_sha256': 'a' * 64,
                'candidates': [{
                    'candidate_id': 'sealed-source-candidate',
                    'strategy_config': copy.deepcopy(self.source),
                    'observations': ['PAYOFF_BELOW_TARGET'],
                }],
            },
        }

    def filtered(self, hashes):
        original = MODULE._v274_full_historical_candidate_hashes
        MODULE._v274_full_historical_candidate_hashes = (
            lambda root: set(hashes)
        )
        try:
            return MODULE._v274_global_memory_reviewed_seed_filter(
                self.context(),
                'codex',
                Path('/tmp/tdh-v274-test-root'),
            )
        finally:
            MODULE._v274_full_historical_candidate_hashes = original

    def digest(self, experiment_id):
        return MODULE._v254_canonical_hash(
            self.queue_configs[experiment_id]
        )

    def test_global_duplicate_is_skipped_before_provider(self):
        first, second, _ = MODULE.V269_REVIEWED_SEED_PRIORITY
        value = self.filtered({self.digest(first)})

        self.assertEqual(
            value['novelty_frontier'][0]['config']['experiment_id'],
            second,
        )
        audit = value['v274_global_memory_queue_filter']
        self.assertEqual(audit['skipped_duplicate_count'], 1)
        self.assertEqual(
            audit['skipped_duplicates'][0]['experiment_id'],
            first,
        )
        self.assertEqual(audit['selected_experiment_id'], second)
        self.assertFalse(audit['provider_invoked_by_filter'])
        self.assertFalse(audit['raw_proposal_executed'])
        self.assertEqual(value['previous_rounds'], [])

    def test_no_global_duplicate_preserves_first_exact_seed(self):
        first = MODULE.V269_REVIEWED_SEED_PRIORITY[0]
        value = self.filtered(set())
        self.assertEqual(
            value['novelty_frontier'][0]['config']['experiment_id'],
            first,
        )
        self.assertEqual(
            value['v274_global_memory_queue_filter'][
                'skipped_duplicate_count'
            ],
            0,
        )

    def test_exhausted_exact_queue_remains_empty_and_model_free(self):
        first, second, _ = MODULE.V269_REVIEWED_SEED_PRIORITY
        value = self.filtered({
            self.digest(first),
            self.digest(second),
        })
        self.assertEqual(value['novelty_frontier'], [])
        self.assertEqual(
            value['v269_reviewed_seed_replenishment']['status'],
            'REVIEWED_SEED_QUEUE_EXHAUSTED',
        )
        audit = value['v274_global_memory_queue_filter']
        self.assertEqual(audit['skipped_duplicate_count'], 2)
        self.assertIsNone(audit['selected_experiment_id'])
        self.assertFalse(audit['provider_invoked_by_filter'])
        self.assertTrue(audit['unknown_errors_fail_closed'])

    def test_authoritative_reader_shape_drift_fails_closed(self):
        original_module = MODULE.V216_GLOBAL_MEMORY_MODULE
        MODULE.V216_GLOBAL_MEMORY_MODULE = object()
        try:
            with self.assertRaisesRegex(
                MODULE.LabError,
                'duplicate reader is unavailable',
            ):
                MODULE._v274_full_historical_candidate_hashes(
                    Path('/tmp/tdh-v274-test-root')
                )
        finally:
            MODULE.V216_GLOBAL_MEMORY_MODULE = original_module

    def test_legacy_staging_fixture_without_config_is_isolated(self):
        fixture = type('LegacyFixture', (), {})()
        fixture.run_dir = Path('/tmp/tdh-v274-legacy-fixture')
        self.assertIsNone(MODULE._v274_controller_memory_root(fixture))

    def test_missing_runtime_root_fails_closed(self):
        with self.assertRaisesRegex(
            MODULE.LabError,
            'controller memory root is unavailable',
        ):
            MODULE._v274_controller_memory_root(object())

    def test_runtime_contract_preserves_offline_s1_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v274_global_memory_queue_filter_version'],
            MODULE.V274_GLOBAL_MEMORY_QUEUE_FILTER_VERSION,
        )
        self.assertTrue(
            contract[
                'v274_authoritative_full_history_duplicate_reader_reused'
            ]
        )
        self.assertTrue(
            contract['v274_duplicate_reviewed_seed_skipped_before_provider']
        )
        self.assertTrue(
            contract['v274_deterministic_next_exact_reviewed_seed']
        )
        self.assertTrue(contract['v274_proposal_validation_unchanged'])
        self.assertTrue(contract['v274_s1_gates_unchanged'])
        self.assertTrue(contract['v274_unknown_errors_fail_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

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
        'tdh_v276_packet_a_global_memory_filter_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V276PacketAGlobalMemoryFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-VOL80-NODOGE-1D'],
                'BTCUSDT',
            )
        )
        cls.queue_hashes = set()
        for experiment_id in MODULE.V269_REVIEWED_SEED_PRIORITY[:2]:
            config = MODULE.kernel.validate_config(
                MODULE.kernel.performance_config(
                    experiments[experiment_id],
                    'BTCUSDT',
                )
            )
            cls.queue_hashes.add(MODULE._v254_canonical_hash(config))

    def base_context(self):
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
                    'observations': ['NEGATIVE_EXPECTANCY'],
                }],
            },
        }

    def packet_context(self):
        original = MODULE._v274_full_historical_candidate_hashes
        MODULE._v274_full_historical_candidate_hashes = (
            lambda root: set(self.queue_hashes)
        )
        try:
            context = MODULE._v274_global_memory_reviewed_seed_filter(
                self.base_context(),
                'codex',
                Path('/tmp/tdh-v276-test-root'),
            )
        finally:
            MODULE._v274_full_historical_candidate_hashes = original
        context = MODULE._v261_packet_a_replenishment(context, 'codex')
        self.assertTrue(
            MODULE._v275_exact_packet_a_item(
                context['novelty_frontier'][0]
            )
        )
        return context

    def filtered(self, packet_duplicate):
        context = self.packet_context()
        packet_hash = context['v261_packet_a_replenishment'][
            'config_sha256'
        ]
        historical = set(self.queue_hashes)
        if packet_duplicate:
            historical.add(packet_hash)
        original = MODULE._v274_full_historical_candidate_hashes
        MODULE._v274_full_historical_candidate_hashes = (
            lambda root: set(historical)
        )
        try:
            return MODULE._v276_global_memory_packet_a_filter(
                context,
                'codex',
                Path('/tmp/tdh-v276-test-root'),
            )
        finally:
            MODULE._v274_full_historical_candidate_hashes = original

    def test_global_duplicate_is_removed_before_provider(self):
        value = self.filtered(True)
        self.assertEqual(value['novelty_frontier'], [])
        audit = value['v276_packet_a_global_memory_filter']
        self.assertEqual(audit['status'], 'DUPLICATE_PACKET_A_FILTERED')
        self.assertTrue(audit['duplicate_in_authoritative_global_memory'])
        self.assertTrue(audit['frontier_removed_before_provider'])
        self.assertTrue(audit['authoritative_duplicate_reader_reused'])
        self.assertFalse(audit['provider_invoked_by_filter'])
        self.assertFalse(audit['raw_proposal_executed'])

    def test_novel_exact_packet_a_is_preserved_for_v275(self):
        value = self.filtered(False)
        self.assertEqual(len(value['novelty_frontier']), 1)
        self.assertTrue(
            MODULE._v275_exact_packet_a_item(value['novelty_frontier'][0])
        )
        audit = value['v276_packet_a_global_memory_filter']
        self.assertEqual(audit['status'], 'NOVEL_PACKET_A_PRESERVED')
        self.assertFalse(audit['duplicate_in_authoritative_global_memory'])
        self.assertFalse(audit['frontier_removed_before_provider'])

        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v275_cache_packet_a_example_frontier(
            value, 1, 'codex'
        )
        self.assertIsInstance(
            controller._v275_packet_a_example_frontier, dict
        )

    def test_filtered_packet_a_disables_example_cache_cleanly(self):
        value = self.filtered(True)
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v275_cache_packet_a_example_frontier(
            value, 1, 'codex'
        )
        self.assertIsNone(controller._v275_packet_a_example_frontier)

    def test_provenance_and_hash_drift_fail_closed(self):
        context = self.packet_context()
        context['v261_packet_a_replenishment']['family_id'] = 'VOLUME_TSMOM'
        with self.assertRaisesRegex(
            MODULE.LabError,
            'filter provenance drifted',
        ):
            MODULE._v276_global_memory_packet_a_filter(
                context, 'codex', Path('/tmp/tdh-v276-test-root')
            )

        context = self.packet_context()
        context['v261_packet_a_replenishment']['config_sha256'] = '0' * 64
        with self.assertRaisesRegex(
            MODULE.LabError,
            'hash binding drifted',
        ):
            MODULE._v276_global_memory_packet_a_filter(
                context, 'codex', Path('/tmp/tdh-v276-test-root')
            )

    def test_non_codex_and_missing_packet_event_are_unchanged(self):
        context = self.base_context()
        self.assertIs(
            MODULE._v276_global_memory_packet_a_filter(
                context, 'claude', Path('/tmp/tdh-v276-test-root')
            ),
            context,
        )
        self.assertIs(
            MODULE._v276_global_memory_packet_a_filter(
                context, 'codex', Path('/tmp/tdh-v276-test-root')
            ),
            context,
        )

    def test_runtime_contract_preserves_offline_s1_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v276_packet_a_global_memory_filter_version'],
            MODULE.V276_PACKET_A_GLOBAL_MEMORY_FILTER_VERSION,
        )
        self.assertTrue(
            contract[
                'v276_authoritative_full_history_duplicate_reader_reused'
            ]
        )
        self.assertTrue(contract['v276_exact_packet_a_only'])
        self.assertTrue(contract['v276_duplicate_removed_before_provider'])
        self.assertTrue(contract['v276_novel_packet_a_preserved'])
        self.assertFalse(contract['v276_provider_invoked_by_filter'])
        self.assertTrue(contract['v276_proposal_validation_unchanged'])
        self.assertTrue(contract['v276_s1_gates_unchanged'])
        self.assertTrue(contract['v276_unknown_errors_fail_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v278_sealed_diversification_bridge_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V278SealedDiversificationBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.old_source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-VOL80-NODOGE-1H'],
                'BTCUSDT',
            )
        )

    def context(self, frontier=None):
        return {
            'contract_version': '2.0.2',
            'research_round': 1,
            'novelty_frontier': list(frontier or []),
            'previous_rounds': [],
            'negative_memory': [],
            'research_program_memory': {},
            'latest_s1_financial_evidence': {
                'candidates': [{
                    'strategy_config': copy.deepcopy(self.old_source),
                }],
            },
            'v269_reviewed_seed_replenishment': {
                'status': 'REVIEWED_SEED_QUEUE_EXHAUSTED',
            },
            'v274_global_memory_queue_filter': {
                'selected_experiment_id': None,
            },
        }

    def test_exact_three_hash_bound_four_coin_seeds(self):
        families, experiments = MODULE.kernel.registry()
        self.assertIn('VOLUME_TSMOM', families)
        rows = [
            row for row in experiments.values()
            if row.get('registry_id') == MODULE.V278_REVIEWED_REGISTRY_ID
        ]
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row['effective_timeframe'] for row in rows},
            {'1h', '4h', '1d'},
        )
        self.assertEqual(
            {row['experiment_id'] for row in rows},
            set(MODULE.V278_REVIEWED_SEED_PRIORITY),
        )
        for row in rows:
            self.assertEqual(row['universe'], list(MODULE.V278_REVIEWED_SYMBOLS))
            self.assertNotIn('DOGEUSDT', row['universe'])
            admission = row['controller_admission']
            self.assertEqual(
                admission['source_proposal_sha256'],
                MODULE.V278_SOURCE_PROPOSAL_SHA256,
            )
            self.assertEqual(
                admission['source_decision_sha256'],
                MODULE.V278_SOURCE_DECISION_SHA256,
            )
            self.assertEqual(
                admission['source_packet_sha256'],
                MODULE.V278_SOURCE_PACKET_SHA256,
            )
            self.assertEqual(admission['primary_change'], 'UNIVERSE_COUNT_3_TO_4')
            self.assertEqual(admission['min_unique_coins_required'], 4)
            self.assertEqual(admission['max_single_coin_contribution_pct'], 40)
            self.assertEqual(admission['min_expectancy_r_threshold'], 0.05)
            self.assertEqual(admission['deferred_return_lookbacks'], [10, 20, 50])
            self.assertEqual(admission['deferred_volume_lookbacks'], [20, 50, 100])
            self.assertTrue(admission['single_material_axis'])
            self.assertFalse(admission['contains_executable_code'])
            self.assertFalse(admission['raw_proposal_executed'])
            self.assertTrue(admission['controller_only_promotion'])
            self.assertTrue(admission['s1_only'])

    def test_review_registry_binds_selected_v277_packet(self):
        reviewed = MODULE._v265_reviewed_proposal_registry()
        self.assertEqual(
            set(reviewed[MODULE.V278_SOURCE_PROPOSAL_SHA256]),
            set(MODULE.V278_REVIEWED_SEED_PRIORITY),
        )

    def test_empty_exhausted_frontier_admits_first_exact_seed(self):
        with mock.patch.object(
            MODULE, '_v274_full_historical_candidate_hashes',
            return_value=set(),
        ):
            updated = MODULE._v278_sealed_diversification_replenishment(
                self.context(), 'codex', Path('/sealed/history')
            )

        self.assertEqual(len(updated['novelty_frontier']), 1)
        item = updated['novelty_frontier'][0]
        self.assertTrue(MODULE._v278_exact_diversification_item(item))
        self.assertTrue(
            MODULE._v251_legal_frontier_item(self.old_source, item)
        )
        self.assertEqual(
            item['config']['experiment_id'],
            MODULE.V278_REVIEWED_SEED_PRIORITY[0],
        )
        self.assertEqual(item['config']['symbol'], 'BTCUSDT')
        event = updated['v278_diversification_bridge']
        self.assertEqual(event['status'], 'EXACT_DIVERSIFICATION_BRIDGE_ADMITTED')
        self.assertEqual(event['primary_change'], 'UNIVERSE_COUNT_3_TO_4')
        self.assertEqual(event['symbols'], list(MODULE.V278_REVIEWED_SYMBOLS))
        self.assertFalse(event['provider_invoked_by_bridge'])
        self.assertFalse(event['raw_proposal_executed'])
        self.assertFalse(event['s2_s4_opened'])

    def test_global_duplicate_advances_deterministically(self):
        _, experiments = MODULE.kernel.registry()
        first = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments[MODULE.V278_REVIEWED_SEED_PRIORITY[0]],
                'BTCUSDT',
            )
        )
        first_hash = MODULE._v254_canonical_hash(first)
        with mock.patch.object(
            MODULE, '_v274_full_historical_candidate_hashes',
            return_value={first_hash},
        ):
            updated = MODULE._v278_sealed_diversification_replenishment(
                self.context(), 'codex', Path('/sealed/history')
            )

        self.assertEqual(
            updated['novelty_frontier'][0]['config']['experiment_id'],
            MODULE.V278_REVIEWED_SEED_PRIORITY[1],
        )
        skipped = updated['v278_diversification_bridge']['skipped_duplicates']
        self.assertEqual([row['experiment_id'] for row in skipped], [
            MODULE.V278_REVIEWED_SEED_PRIORITY[0]
        ])

    def test_all_global_duplicates_close_without_provider_or_invention(self):
        _, experiments = MODULE.kernel.registry()
        historical = {
            MODULE._v254_canonical_hash(
                MODULE.kernel.validate_config(
                    MODULE.kernel.performance_config(
                        experiments[experiment_id], 'BTCUSDT'
                    )
                )
            )
            for experiment_id in MODULE.V278_REVIEWED_SEED_PRIORITY
        }
        with mock.patch.object(
            MODULE, '_v274_full_historical_candidate_hashes',
            return_value=historical,
        ):
            updated = MODULE._v278_sealed_diversification_replenishment(
                self.context(), 'codex', Path('/sealed/history')
            )

        self.assertEqual(updated['novelty_frontier'], [])
        event = updated['v278_diversification_bridge']
        self.assertEqual(event['status'], 'DIVERSIFICATION_QUEUE_EXHAUSTED')
        self.assertEqual(len(event['skipped_duplicates']), 3)
        self.assertFalse(event['provider_invoked_by_bridge'])
        self.assertFalse(event['raw_proposal_executed'])

    def test_spoofed_packet_or_config_is_rejected(self):
        with mock.patch.object(
            MODULE, '_v274_full_historical_candidate_hashes',
            return_value=set(),
        ):
            updated = MODULE._v278_sealed_diversification_replenishment(
                self.context(), 'codex', Path('/sealed/history')
            )
        item = updated['novelty_frontier'][0]

        packet_spoof = copy.deepcopy(item)
        packet_spoof['v278_diversification_queue'][
            'source_packet_sha256'
        ] = '0' * 64
        self.assertFalse(MODULE._v278_exact_diversification_item(packet_spoof))

        config_spoof = copy.deepcopy(item)
        config_spoof['config']['params']['return_lookback'] = 20
        self.assertFalse(MODULE._v278_exact_diversification_item(config_spoof))
        self.assertFalse(
            MODULE._v251_legal_frontier_item(self.old_source, config_spoof)
        )

    def test_non_codex_and_nonempty_frontier_are_unchanged(self):
        context = self.context()
        self.assertEqual(
            MODULE._v278_sealed_diversification_replenishment(
                context, 'claude', None
            ),
            context,
        )
        occupied = self.context([{'config': copy.deepcopy(self.old_source)}])
        self.assertEqual(
            MODULE._v278_sealed_diversification_replenishment(
                occupied, 'codex', None
            ),
            occupied,
        )

    def test_runtime_contract_preserves_offline_s1_boundary(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v278_diversification_bridge_version'],
            MODULE.V278_DIVERSIFICATION_BRIDGE_VERSION,
        )
        self.assertTrue(contract['v278_source_packet_hash_bound'])
        self.assertTrue(contract['v278_exact_four_coin_universe'])
        self.assertTrue(contract['v278_single_primary_change_universe_only'])
        self.assertTrue(
            contract['v278_candidate_baseline_negative_control_bound']
        )
        self.assertTrue(contract['v278_deferred_parameter_axes_remain_closed'])
        self.assertTrue(contract['v278_authoritative_global_memory_checked'])
        self.assertTrue(contract['v278_raw_proposal_never_executes'])
        self.assertFalse(contract['v278_provider_invoked_by_bridge'])
        self.assertTrue(contract['v278_s1_only'])
        self.assertTrue(contract['v278_unknown_errors_fail_closed'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

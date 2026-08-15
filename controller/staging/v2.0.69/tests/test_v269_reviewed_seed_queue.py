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
        'tdh_v269_reviewed_seed_queue_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V269ReviewedSeedQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.experiments = MODULE.kernel.registry()
        cls.legacy_nodoge_id = 'TDH-SCOUT-000001-VTM-NODOGE-1H'
        cls.legacy_full_id = 'TDH-SCOUT-000001-VTM-FULL-4H'
        cls.reviewed_1h = MODULE.V269_REVIEWED_SEED_PRIORITY[0]
        cls.reviewed_4h = MODULE.V269_REVIEWED_SEED_PRIORITY[1]
        cls.source_btc = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                cls.experiments[cls.legacy_nodoge_id], 'BTCUSDT'
            )
        )
        cls.source_doge = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                cls.experiments[cls.legacy_full_id], 'DOGEUSDT'
            )
        )

    def context(self, source=None, used_ids=()):
        context = {
            'contract_version': '2.0.2',
            'research_round': 1,
            'novelty_frontier': [],
            'previous_rounds': [
                {'experiment_id': experiment_id}
                for experiment_id in used_ids
            ],
            'negative_memory': [],
            'research_program_memory': {},
        }
        if source is not None:
            context['latest_s1_financial_evidence'] = {
                'candidates': [{'strategy_config': copy.deepcopy(source)}]
            }
        return context

    def test_empty_frontier_admits_first_exact_reviewed_seed(self):
        updated = MODULE._v269_reviewed_seed_replenishment(
            self.context(self.source_btc), 'codex'
        )
        self.assertEqual(len(updated['novelty_frontier']), 1)
        item = updated['novelty_frontier'][0]
        self.assertEqual(item['config']['experiment_id'], self.reviewed_1h)
        self.assertEqual(item['config']['symbol'], 'BTCUSDT')
        self.assertTrue(MODULE._v269_exact_reviewed_queue_item(item))
        self.assertTrue(MODULE._v251_legal_frontier_item(self.source_btc, item))
        event = updated['v269_reviewed_seed_replenishment']
        self.assertEqual(event['status'], 'EXACT_REVIEWED_SEED_ADMITTED')
        self.assertEqual(
            event['source_proposal_sha256'],
            MODULE.V268_SOURCE_PROPOSAL_SHA256,
        )
        self.assertFalse(event['trading_actions'])
        self.assertFalse(event['exchange_api_access'])

    def test_priority_is_deterministic_and_used_seed_advances_queue(self):
        updated = MODULE._v269_reviewed_seed_replenishment(
            self.context(self.source_btc, (self.reviewed_1h,)), 'codex'
        )
        item = updated['novelty_frontier'][0]
        self.assertEqual(item['config']['experiment_id'], self.reviewed_4h)
        self.assertEqual(item['config']['symbol'], 'BTCUSDT')
        self.assertTrue(MODULE._v269_exact_reviewed_queue_item(item))

    def test_excluded_same_family_symbol_uses_one_axis_bridge_first(self):
        updated = MODULE._v269_reviewed_seed_replenishment(
            self.context(self.source_doge), 'codex'
        )
        item = updated['novelty_frontier'][0]
        self.assertEqual(
            updated['v269_reviewed_seed_replenishment']['status'],
            'SYMBOL_BRIDGE_ADMITTED',
        )
        self.assertEqual(item['config']['symbol'], 'BTCUSDT')
        self.assertEqual(
            MODULE._v251_transition_axes(self.source_doge, item['config']),
            ('symbol',),
        )
        self.assertTrue(MODULE._v251_legal_frontier_item(self.source_doge, item))
        self.assertNotIn('v254_registration', item)
        self.assertFalse(item['v269_symbol_bridge']['trading_actions'])
        self.assertFalse(item['v269_symbol_bridge']['exchange_api_access'])

    def test_spoofed_registration_or_config_fails_closed(self):
        updated = MODULE._v269_reviewed_seed_replenishment(
            self.context(self.source_btc), 'codex'
        )
        item = updated['novelty_frontier'][0]

        spoofed_registration = copy.deepcopy(item)
        spoofed_registration['v269_reviewed_queue'][
            'source_proposal_sha256'
        ] = '0' * 64
        self.assertFalse(
            MODULE._v269_exact_reviewed_queue_item(spoofed_registration)
        )

        spoofed_config = copy.deepcopy(item)
        spoofed_config['config']['params']['return_lookback'] += 1
        self.assertFalse(MODULE._v269_exact_reviewed_queue_item(spoofed_config))
        self.assertFalse(
            MODULE._v251_legal_frontier_item(self.source_btc, spoofed_config)
        )

    def test_non_codex_and_nonempty_frontier_are_unchanged(self):
        context = self.context(self.source_btc)
        self.assertIs(
            MODULE._v269_reviewed_seed_replenishment(context, 'claude'),
            context,
        )
        context['novelty_frontier'] = [{'config': copy.deepcopy(self.source_btc)}]
        self.assertIs(
            MODULE._v269_reviewed_seed_replenishment(context, 'codex'),
            context,
        )

    def test_exhausted_reviewed_queue_does_not_invoke_or_invent(self):
        updated = MODULE._v269_reviewed_seed_replenishment(
            self.context(
                self.source_btc,
                MODULE.V269_REVIEWED_SEED_PRIORITY,
            ),
            'codex',
        )
        self.assertEqual(updated['novelty_frontier'], [])
        self.assertEqual(
            updated['v269_reviewed_seed_replenishment']['status'],
            'REVIEWED_SEED_QUEUE_EXHAUSTED',
        )
        self.assertFalse(
            updated['v269_reviewed_seed_replenishment'][
                'model_generated_executable_code'
            ]
        )

    def test_runtime_contract_preserves_offline_s1_fail_closed_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v269_reviewed_seed_queue_version'],
            MODULE.V269_REVIEWED_SEED_QUEUE_VERSION,
        )
        self.assertTrue(
            contract['v269_exact_reviewed_seed_precedes_frontier_exhaustion']
        )
        self.assertTrue(
            contract['v269_single_axis_symbol_bridge_preserves_transition_gate']
        )
        self.assertTrue(contract['v269_untrusted_text_never_enters_reviewed_queue'])
        self.assertTrue(contract['v269_s1_only'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

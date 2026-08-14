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
        'tdh_v260_registered_seed_transition_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V260RegisteredSeedTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source_id = 'TDH-SCOUT-000001-VTM-NODOGE-1H'
        cls.target_id = 'TDH-SCOUT-000001-VTM-FULL-4H'
        cls.source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments[cls.source_id], 'BTCUSDT'
            )
        )
        cls.target = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments[cls.target_id], 'BTCUSDT'
            )
        )
        cls.registration = {
            'version': MODULE.V254_FRONTIER_SCOUT_VERSION,
            'source': 'EXISTING_REGISTERED_KERNEL_SEED',
            'experiment_id': cls.target_id,
            'family_id': 'VOLUME_TSMOM',
            'schema_validated': True,
            'data_eligibility_inherited_from_selection': True,
            'deduplicated': True,
            'model_generated_executable_code': False,
            'controller_only_registration': True,
        }

    def test_exact_registered_seed_is_one_atomic_legal_transition(self):
        item = {
            'config': copy.deepcopy(self.target),
            'v254_registration': copy.deepcopy(self.registration),
        }
        self.assertEqual(
            MODULE._v251_transition_axes(self.source, self.target),
            ('timeframe', 'registered_seed'),
        )
        self.assertTrue(MODULE._v260_exact_controller_registered_seed(item))
        self.assertTrue(MODULE._v251_legal_frontier_item(self.source, item))

    def test_freeform_or_spoofed_multi_axis_transition_fails_closed(self):
        self.assertTrue(MODULE._v251_legal_frontier_item(
            self.source, {'config': copy.deepcopy(self.target)}
        ))

        spoofed = copy.deepcopy(self.target)
        spoofed['params']['return_lookback'] += 1
        item = {
            'config': spoofed,
            'v254_registration': copy.deepcopy(self.registration),
        }
        self.assertFalse(MODULE._v260_exact_controller_registered_seed(item))
        self.assertFalse(MODULE._v251_legal_frontier_item(self.source, item))

        unregistered = copy.deepcopy(self.target)
        unregistered['experiment_id'] = 'TDH-SCOUT-999999-UNREGISTERED'
        self.assertFalse(MODULE._v251_legal_frontier_item(
            self.source, {'config': unregistered}
        ))

    def test_replenishment_admits_next_exact_registered_seed(self):
        context = {
            'contract_version': '2.0.2',
            'novelty_frontier': [],
            'latest_s1_financial_evidence': {
                'candidates': [
                    {'strategy_config': copy.deepcopy(self.source)}
                ]
            },
            'tdh_research_selection': {
                'family_cards': [{'family_id': 'VOLUME_TSMOM'}],
                'experiment_seeds': [{'experiment_id': self.target_id}],
            },
        }
        updated = MODULE._v254_registered_replenishment(context, 'codex')
        event = updated['v254_frontier_replenishment']
        self.assertEqual(event['admitted_count'], 1)
        self.assertEqual(event['output_count'], 1)
        self.assertEqual(
            updated['novelty_frontier'][0]['config'], self.target
        )
        self.assertFalse(event['trading_actions'])
        self.assertFalse(event['exchange_api_access'])
        self.assertTrue(event['controller_only_promotion'])

    def test_runtime_contract_records_fail_closed_boundary(self):
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(
            contract['v260_only_exact_controller_registered_seed_is_atomic']
        )
        self.assertTrue(
            contract['v260_spoofed_or_freeform_seed_transition_fails_closed']
        )
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

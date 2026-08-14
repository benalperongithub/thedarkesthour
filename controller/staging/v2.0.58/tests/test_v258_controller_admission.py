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
        'tdh_v258_controller_admission_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V258ControllerAdmissionTests(unittest.TestCase):
    def test_registry_contains_exact_reviewed_ablation_design(self):
        families, experiments = MODULE.kernel.registry()
        self.assertIn('VOLUME_TSMOM', families)
        approved = {
            key: value for key, value in experiments.items()
            if value.get('registry_id') == MODULE.kernel.V258_REGISTRY_VERSION
        }
        self.assertEqual(set(approved), set(MODULE.kernel.APPROVED_IDENTITIES))
        self.assertEqual(len(approved), 6)
        self.assertEqual(
            {row['effective_timeframe'] for row in approved.values()},
            {'1h', '4h', '1d'},
        )
        self.assertEqual({row['family_id'] for row in approved.values()}, {'VOLUME_TSMOM'})
        self.assertTrue(all(
            row['controller_admission']['status']
            == 'CONTROLLER_APPROVED_SEALED_REGISTRY'
            for row in approved.values()
        ))

    def test_every_reviewed_seed_is_adapter_validated_without_free_form_code(self):
        _, experiments = MODULE.kernel.registry()
        for experiment_id in sorted(MODULE.kernel.APPROVED_IDENTITIES):
            row = experiments[experiment_id]
            for symbol in row['universe']:
                config = MODULE.kernel.performance_config(row, symbol)
                self.assertEqual(MODULE.kernel.validate_config(config), config)
                self.assertEqual(config['family'], 'VOLUME_TSMOM')
                self.assertEqual(config['params'], {
                    'return_lookback': 10,
                    'volume_lookback': 20,
                    'volume_weight': 'ratio',
                })
            self.assertFalse(row['controller_admission']['contains_executable_code'])

    def test_registered_replenishment_admits_reviewed_seed_controller_only(self):
        experiment_id = 'TDH-SCOUT-000001-VTM-FULL-1H'
        context = {
            'novelty_frontier': [],
            'tdh_research_selection': {
                'family_cards': [{'family_id': 'VOLUME_TSMOM'}],
                'experiment_seeds': [
                    {'experiment_id': experiment_id, 'family_id': 'VOLUME_TSMOM'}
                ],
            },
        }
        result = MODULE._v254_registered_replenishment(context, 'codex')
        event = result['v254_frontier_replenishment']
        self.assertEqual(event['admitted_count'], 1)
        self.assertTrue(event['only_existing_registered_seeds'])
        self.assertTrue(event['controller_only_promotion'])
        self.assertEqual(
            result['novelty_frontier'][0]['config']['experiment_id'],
            experiment_id,
        )

    def test_unknown_or_mutated_admission_fails_closed(self):
        context = {
            'novelty_frontier': [],
            'tdh_research_selection': {
                'family_cards': [{'family_id': 'VOLUME_TSMOM'}],
                'experiment_seeds': [
                    {'experiment_id': 'TDH-SCOUT-UNREVIEWED', 'family_id': 'VOLUME_TSMOM'}
                ],
            },
        }
        with self.assertRaisesRegex(MODULE.LabError, 'not registered'):
            MODULE._v254_registered_replenishment(context, 'codex')

        _, experiments = MODULE.kernel.registry()
        bad = copy.deepcopy(experiments['TDH-SCOUT-000001-VTM-FULL-1H'])
        bad.pop('effective_timeframe')
        bad['params']['return_lookback'] = 11
        with self.assertRaises(MODULE.kernel.ResearchContractError):
            MODULE.kernel._validate_approved_row(bad)

    def test_status_and_runtime_contract_preserve_hard_safety(self):
        status = MODULE.kernel.approved_registry_status()
        self.assertEqual(status['approved_seed_count'], 6)
        self.assertFalse(status['untrusted_scout_text_executable'])
        self.assertFalse(status['new_family_auto_admitted'])
        self.assertTrue(status['controller_only_promotion'])
        self.assertFalse(status['trading_actions'])
        self.assertFalse(status['exchange_api_access'])

        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract['v258_controller_reviewed_seed_overlay'])
        self.assertTrue(contract['v258_untrusted_scout_text_never_executes'])
        self.assertTrue(contract['v258_existing_family_only'])
        self.assertTrue(contract['v258_unknown_admission_errors_fail_closed'])
        self.assertTrue(contract['controller_only_promotion'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

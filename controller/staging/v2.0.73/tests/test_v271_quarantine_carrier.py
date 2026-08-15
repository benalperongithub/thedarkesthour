from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v271_quarantine_carrier_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V271QuarantineCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.registered_config = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-NODOGE-1H'],
                'BTCUSDT',
            )
        )

    def controller(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v225_next_actor = 'codex'
        controller._v225_codex_family = None
        return controller

    @staticmethod
    def structural_exhaustion(controller, *args, **kwargs):
        raise MODULE.LabError(MODULE.V270_STRUCTURAL_EXHAUSTION_ERROR)

    def test_context_building_uses_one_exact_registered_carrier(self):
        parent = MODULE.Controller.__mro__[1]
        raw_parent = MODULE.V236_QUARANTINE_CLASS.__mro__[1]
        controller = self.controller()
        controller._v271_context_building = True

        def raw_frontier(this, *args, **kwargs):
            return [{'config': copy.deepcopy(self.registered_config)}]

        with mock.patch.object(
            parent,
            '_diverse_frontier',
            new=self.structural_exhaustion,
        ), mock.patch.object(
            raw_parent,
            '_diverse_frontier',
            new=raw_frontier,
        ):
            carrier = controller._diverse_frontier()

        self.assertEqual(len(carrier), 1)
        self.assertEqual(carrier[0]['config'], self.registered_config)
        event = controller._v271_quarantine_carrier
        self.assertEqual(
            event['version'], MODULE.V271_QUARANTINE_CARRIER_VERSION
        )
        self.assertEqual(
            event['carrier_config_sha256'],
            MODULE._v254_canonical_hash(self.registered_config),
        )
        self.assertTrue(event['structural_quarantine_preserved'])
        self.assertTrue(event['carrier_never_executable'])
        self.assertFalse(event['provider_invoked'])

    def test_carrier_is_removed_exactly_once_before_provider(self):
        controller = self.controller()
        digest = MODULE._v254_canonical_hash(self.registered_config)
        controller._v271_quarantine_carrier = {
            'version': MODULE.V271_QUARANTINE_CARRIER_VERSION,
            'carrier_config_sha256': digest,
        }
        context = {
            'novelty_frontier': [{
                'config': copy.deepcopy(self.registered_config),
            }],
        }
        updated = controller._v271_remove_quarantine_carrier(context)
        self.assertEqual(updated['novelty_frontier'], [])
        event = updated['v271_quarantine_carrier']
        self.assertTrue(event['carrier_removed_before_provider'])
        self.assertEqual(event['frontier_count_after_carrier_removal'], 0)

    def test_missing_or_mutated_carrier_fails_closed(self):
        controller = self.controller()
        controller._v271_quarantine_carrier = {
            'version': MODULE.V271_QUARANTINE_CARRIER_VERSION,
            'carrier_config_sha256': MODULE._v254_canonical_hash(
                self.registered_config
            ),
        }
        mutated = copy.deepcopy(self.registered_config)
        mutated['params']['return_lookback'] += 1
        with self.assertRaisesRegex(MODULE.LabError, 'exactly once'):
            controller._v271_remove_quarantine_carrier({
                'novelty_frontier': [{'config': mutated}],
            })

        with self.assertRaisesRegex(MODULE.LabError, 'malformed'):
            controller._v271_remove_quarantine_carrier({
                'novelty_frontier': ['not-a-frontier-row'],
            })

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v271_quarantine_carrier_version'],
            MODULE.V271_QUARANTINE_CARRIER_VERSION,
        )
        self.assertTrue(contract['v271_exact_registered_carrier_only'])
        self.assertTrue(contract['v271_carrier_removed_before_provider'])
        self.assertTrue(contract['v271_structural_quarantine_preserved'])
        self.assertTrue(contract['v271_unknown_errors_fail_closed'])
        self.assertTrue(contract['controller_only_promotion'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

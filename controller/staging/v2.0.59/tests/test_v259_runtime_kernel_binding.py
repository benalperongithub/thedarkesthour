from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v259_runtime_kernel_binding_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V259RuntimeKernelBindingTests(unittest.TestCase):
    def test_v258_overlay_survives_runtime_local_adapter_binding(self):
        chain = MODULE.v240.v238.v237.v236
        self.assertIs(MODULE.v240.kernel, MODULE.kernel)
        self.assertIs(chain.v235.kernel, MODULE.kernel)
        self.assertIs(chain.kernel, MODULE.kernel)
        if hasattr(chain, 'base_v217'):
            self.assertIs(chain.base_v217.kernel, MODULE.kernel)
        self.assertTrue(MODULE._v259_runtime_kernel_overlay_bound())

    def test_runtime_context_can_see_all_six_controller_reviewed_seeds(self):
        chain = MODULE.v240.v238.v237.v236
        _, experiments = chain.v235.kernel.registry()
        approved = {
            experiment_id: row
            for experiment_id, row in experiments.items()
            if row.get('registry_id') == MODULE.kernel.V258_REGISTRY_VERSION
        }
        self.assertEqual(set(approved), set(MODULE.kernel.APPROVED_IDENTITIES))
        self.assertEqual(len(approved), 6)

    def test_binding_is_idempotent_and_safety_contract_is_unchanged(self):
        MODULE._bind_local_adapter()
        MODULE._bind_local_adapter()
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract['v259_runtime_kernel_overlay_bound'])
        self.assertTrue(contract['v259_approved_registry_reaches_runtime_context'])
        self.assertTrue(contract['controller_only_promotion'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

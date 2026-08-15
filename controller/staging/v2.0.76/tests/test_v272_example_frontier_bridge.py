from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v272_example_frontier_bridge_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V272ExampleFrontierBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source = MODULE.kernel.validate_config(
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

    def admitted_context(self):
        context = {
            'novelty_frontier': [],
            'previous_rounds': [],
            'negative_memory': [],
            'research_program_memory': {},
            'latest_s1_financial_evidence': {
                'candidates': [{
                    'strategy_config': copy.deepcopy(self.source),
                }],
            },
        }
        updated = MODULE._v269_reviewed_seed_replenishment(
            context, 'codex'
        )
        self.assertEqual(
            updated['v269_reviewed_seed_replenishment']['status'],
            'EXACT_REVIEWED_SEED_ADMITTED',
        )
        return updated

    def test_cache_accepts_only_one_exact_hash_bound_reviewed_seed(self):
        controller = self.controller()
        context = self.admitted_context()
        controller._v272_cache_example_frontier(context, 1, 'codex')

        record = controller._v272_example_frontier
        self.assertEqual(
            record['version'], MODULE.V272_EXAMPLE_FRONTIER_BRIDGE_VERSION
        )
        self.assertEqual(record['research_round'], 1)
        self.assertEqual(
            record['config_sha256'],
            context['v269_reviewed_seed_replenishment']['config_sha256'],
        )
        self.assertTrue(
            MODULE._v269_exact_reviewed_queue_item(record['frontier'][0])
        )
        self.assertTrue(record['example_only'])
        self.assertFalse(record['raw_proposal_executed'])

    def test_inherited_example_builder_sees_cached_frontier_only(self):
        parent = MODULE.Controller.__mro__[1]
        controller = self.controller()
        context = self.admitted_context()
        controller._v272_cache_example_frontier(context, 1, 'codex')

        def inherited_example(this, round_number, actor):
            frontier = this._diverse_frontier()
            return json.dumps({
                'actor': actor,
                'round': round_number,
                'experiment_id': frontier[0]['config']['experiment_id'],
            })

        with tempfile.TemporaryDirectory() as temp_dir:
            controller.run_dir = Path(temp_dir)
            with mock.patch.object(
                parent,
                'proposal_output_example',
                new=inherited_example,
            ):
                result = json.loads(
                    controller.proposal_output_example(1, 'codex')
                )

            self.assertEqual(
                result['experiment_id'],
                MODULE.V269_REVIEWED_SEED_PRIORITY[0],
            )
            artifact = (
                Path(temp_dir)
                / 'round-01'
                / 'EXAMPLE_FRONTIER_BRIDGE_V272.json'
            )
            audit = json.loads(artifact.read_text(encoding='utf-8'))
            self.assertTrue(audit['example_frontier_used'])
            self.assertTrue(audit['proposal_validation_unchanged'])
            self.assertTrue(audit['s1_gates_unchanged'])
            self.assertFalse(audit['provider_invoked_by_bridge'])

    def test_mutated_cache_and_scope_drift_fail_closed(self):
        controller = self.controller()
        controller._v272_cache_example_frontier(
            self.admitted_context(), 1, 'codex'
        )
        controller._v272_example_frontier['frontier'][0][
            'config'
        ]['params']['return_lookback'] += 1
        controller._v272_example_building = True
        with self.assertRaisesRegex(MODULE.LabError, 'identity drifted'):
            controller._diverse_frontier()

        controller = self.controller()
        controller._v272_cache_example_frontier(
            self.admitted_context(), 1, 'codex'
        )
        with self.assertRaisesRegex(MODULE.LabError, 'scope drifted'):
            controller.proposal_output_example(1, 'claude')

    def test_runtime_contract_preserves_offline_s1_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v272_example_frontier_bridge_version'],
            MODULE.V272_EXAMPLE_FRONTIER_BRIDGE_VERSION,
        )
        self.assertTrue(contract['v272_exact_admitted_reviewed_seed_only'])
        self.assertTrue(contract['v272_example_scope_only'])
        self.assertTrue(contract['v272_proposal_validation_unchanged'])
        self.assertTrue(contract['v272_s1_gates_unchanged'])
        self.assertTrue(contract['v272_unknown_errors_fail_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

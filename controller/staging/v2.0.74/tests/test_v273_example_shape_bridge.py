from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v273_example_shape_bridge_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V273ExampleShapeBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-VOL80-NODOGE-1D'],
                'BTCUSDT',
            )
        )

    def controller(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v225_next_actor = 'codex'
        controller._v225_codex_family = None
        controller.task = types.SimpleNamespace(experiment_plan={
            'plan_id': 'candidate-baseline-negative-v1',
            's1_trial_budget_per_candidate': 3,
        })
        return controller

    def admitted_context(self):
        context = {
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
        updated = MODULE._v269_reviewed_seed_replenishment(
            context, 'codex'
        )
        self.assertEqual(
            updated['v269_reviewed_seed_replenishment']['status'],
            'EXACT_REVIEWED_SEED_ADMITTED',
        )
        self.assertEqual(
            updated['novelty_frontier'][0]['config']['experiment_id'],
            MODULE.V269_REVIEWED_SEED_PRIORITY[0],
        )
        return updated

    def bind_sealed_example_source(self, controller, context):
        evidence = copy.deepcopy(context['latest_s1_financial_evidence'])

        def source_config(this):
            return copy.deepcopy(self.source), copy.deepcopy(evidence)

        controller._source_config = types.MethodType(source_config, controller)

    def test_real_sealed_example_builder_receives_exact_temporary_shape(self):
        controller = self.controller()
        context = self.admitted_context()
        controller._v272_cache_example_frontier(context, 1, 'codex')
        self.bind_sealed_example_source(controller, context)

        cached_before = json.dumps(
            controller._v272_example_frontier['frontier'],
            sort_keys=True,
            separators=(',', ':'),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            controller.run_dir = Path(temp_dir)
            result = json.loads(controller.proposal_output_example(1, 'codex'))

            candidate = result['candidates'][0]
            self.assertEqual(
                candidate['config']['experiment_id'],
                MODULE.V269_REVIEWED_SEED_PRIORITY[0],
            )
            self.assertEqual(
                candidate['evidence_chain']['selected_approach'],
                'VALIDATE_PARAMETER_NEIGHBORHOOD',
            )
            self.assertEqual(
                candidate['primary_change']['component'],
                'registered_parameter_seed',
            )
            self.assertEqual(
                candidate['primary_change']['from'],
                self.source['experiment_id'],
            )
            self.assertEqual(
                candidate['primary_change']['to'],
                MODULE.V269_REVIEWED_SEED_PRIORITY[0],
            )

            round_dir = Path(temp_dir) / 'round-01'
            self.assertTrue(
                (round_dir / 'EXAMPLE_FRONTIER_BRIDGE_V272.json').is_file()
            )
            artifact = json.loads(
                (round_dir / 'EXAMPLE_SHAPE_BRIDGE_V273.json').read_text(
                    encoding='utf-8'
                )
            )
            self.assertTrue(
                artifact['sealed_v228_schema_dependency_satisfied']
            )
            self.assertTrue(artifact['candidate_config_hash_unchanged'])
            self.assertTrue(artifact['temporary_example_row_only'])
            self.assertTrue(artifact['cached_frontier_unchanged'])
            self.assertFalse(artifact['provider_invoked_by_bridge'])

        cached_after = json.dumps(
            controller._v272_example_frontier['frontier'],
            sort_keys=True,
            separators=(',', ':'),
        )
        self.assertEqual(cached_before, cached_after)
        self.assertNotIn(
            'selected_approach',
            controller._v272_example_frontier['frontier'][0],
        )

    def test_shape_is_registry_bound_and_matches_sealed_same_family_rule(self):
        controller = self.controller()
        context = self.admitted_context()
        controller._v272_cache_example_frontier(context, 1, 'codex')

        shape = controller._v273_example_shape
        self.assertEqual(
            shape['version'], MODULE.V273_EXAMPLE_SHAPE_BRIDGE_VERSION
        )
        self.assertEqual(
            shape['selected_approach'],
            'VALIDATE_PARAMETER_NEIGHBORHOOD',
        )
        self.assertEqual(
            shape['transition_axes'], ['timeframe', 'registered_seed']
        )
        self.assertTrue(
            MODULE._v260_exact_controller_registered_seed({
                'config': shape['source_config'],
            })
        )
        self.assertEqual(
            shape['candidate_config_sha256'],
            context['v269_reviewed_seed_replenishment']['config_sha256'],
        )

    def test_shape_mutation_and_transition_drift_fail_closed(self):
        controller = self.controller()
        controller._v272_cache_example_frontier(
            self.admitted_context(), 1, 'codex'
        )
        controller._v273_example_shape[
            'selected_approach'
        ] = 'CHANGE_TIMEFRAME'
        controller._v272_example_building = True
        with self.assertRaisesRegex(MODULE.LabError, 'shape identity drifted'):
            controller._diverse_frontier()

        controller = self.controller()
        controller._v272_cache_example_frontier(
            self.admitted_context(), 1, 'codex'
        )
        controller._v273_example_shape['source_config']['symbol'] = 'XRPUSDT'
        controller._v273_example_shape['source_config_sha256'] = (
            MODULE._v254_canonical_hash(
                controller._v273_example_shape['source_config']
            )
        )
        controller._v272_example_building = True
        with self.assertRaisesRegex(MODULE.LabError, 'transition drifted'):
            controller._diverse_frontier()

    def test_runtime_contract_preserves_offline_s1_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v273_example_shape_bridge_version'],
            MODULE.V273_EXAMPLE_SHAPE_BRIDGE_VERSION,
        )
        self.assertTrue(
            contract[
                'v273_selected_approach_is_sealed_v228_same_family_rule'
            ]
        )
        self.assertTrue(contract['v273_source_and_candidate_registry_bound'])
        self.assertTrue(contract['v273_temporary_example_row_only'])
        self.assertTrue(contract['v273_cached_frontier_unchanged'])
        self.assertTrue(contract['v273_candidate_config_hash_unchanged'])
        self.assertTrue(contract['v273_proposal_validation_unchanged'])
        self.assertTrue(contract['v273_s1_gates_unchanged'])
        self.assertTrue(contract['v273_unknown_errors_fail_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

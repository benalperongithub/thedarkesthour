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
        'tdh_v275_packet_a_example_bridge_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V275PacketAExampleBridgeTests(unittest.TestCase):
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
                Path('/tmp/tdh-v275-test-root'),
            )
        finally:
            MODULE._v274_full_historical_candidate_hashes = original

        self.assertEqual(
            context['v269_reviewed_seed_replenishment']['status'],
            'REVIEWED_SEED_QUEUE_EXHAUSTED',
        )
        self.assertEqual(context['novelty_frontier'], [])
        context = MODULE._v261_packet_a_replenishment(context, 'codex')
        self.assertEqual(
            context['v261_packet_a_replenishment']['experiment_id'],
            MODULE.V261_PACKET_A_EXPERIMENT_ID,
        )
        return context

    def controller(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v225_next_actor = 'codex'
        controller._v225_codex_family = None
        controller.task = types.SimpleNamespace(experiment_plan={
            'plan_id': 'candidate-baseline-negative-v1',
            's1_trial_budget_per_candidate': 3,
        })
        return controller

    def bind_sealed_example_source(self, controller, context):
        evidence = copy.deepcopy(context['latest_s1_financial_evidence'])

        def source_config(this):
            return copy.deepcopy(self.source), copy.deepcopy(evidence)

        controller._source_config = types.MethodType(source_config, controller)

    def test_real_sealed_builder_receives_exact_packet_a_shape(self):
        context = self.packet_context()
        controller = self.controller()
        controller._v275_cache_packet_a_example_frontier(
            context, 1, 'codex'
        )
        self.bind_sealed_example_source(controller, context)

        cached_before = json.dumps(
            controller._v275_packet_a_example_frontier['frontier'],
            sort_keys=True,
            separators=(',', ':'),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            controller.run_dir = Path(temp_dir)
            result = json.loads(controller.proposal_output_example(1, 'codex'))
            candidate = result['candidates'][0]
            self.assertEqual(
                candidate['config']['experiment_id'],
                MODULE.V261_PACKET_A_EXPERIMENT_ID,
            )
            self.assertEqual(
                candidate['evidence_chain']['selected_approach'],
                'CHANGE_STRATEGY_FAMILY',
            )
            self.assertEqual(
                candidate['config']['family'],
                'RSI_GATED_REVERSION',
            )

            artifact = json.loads(
                (
                    Path(temp_dir)
                    / 'round-01'
                    / 'PACKET_A_EXAMPLE_FRONTIER_V275.json'
                ).read_text(encoding='utf-8')
            )
            self.assertTrue(artifact['example_frontier_used'])
            self.assertTrue(
                artifact['historical_frontier_not_recomputed_for_example']
            )
            self.assertTrue(artifact['cached_frontier_unchanged'])
            self.assertFalse(artifact['provider_invoked_by_bridge'])

        cached_after = json.dumps(
            controller._v275_packet_a_example_frontier['frontier'],
            sort_keys=True,
            separators=(',', ':'),
        )
        self.assertEqual(cached_before, cached_after)
        self.assertNotIn(
            'selected_approach',
            controller._v275_packet_a_example_frontier['frontier'][0],
        )

    def test_only_exact_packet_a_provenance_is_accepted(self):
        item = copy.deepcopy(self.packet_context()['novelty_frontier'][0])
        self.assertTrue(MODULE._v275_exact_packet_a_item(item))
        item['v254_registration']['source'] = 'UNTRUSTED_INBOX'
        self.assertFalse(MODULE._v275_exact_packet_a_item(item))

    def test_queue_and_hash_binding_drift_fail_closed(self):
        context = self.packet_context()
        context['v269_reviewed_seed_replenishment']['status'] = (
            'EXACT_REVIEWED_SEED_ADMITTED'
        )
        with self.assertRaisesRegex(
            MODULE.LabError,
            'provenance drifted',
        ):
            self.controller()._v275_cache_packet_a_example_frontier(
                context, 1, 'codex'
            )

        context = self.packet_context()
        context['v261_packet_a_replenishment']['config_sha256'] = '0' * 64
        with self.assertRaisesRegex(
            MODULE.LabError,
            'hash binding drifted',
        ):
            self.controller()._v275_cache_packet_a_example_frontier(
                context, 1, 'codex'
            )

    def test_cached_shape_mutation_fails_closed(self):
        controller = self.controller()
        controller._v275_cache_packet_a_example_frontier(
            self.packet_context(), 1, 'codex'
        )
        controller._v275_packet_a_example_frontier[
            'selected_approach'
        ] = 'VALIDATE_PARAMETER_NEIGHBORHOOD'
        controller._v275_example_building = True
        with self.assertRaisesRegex(
            MODULE.LabError,
            'cache identity drifted',
        ):
            controller._diverse_frontier()

    def test_runtime_contract_preserves_offline_s1_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v275_packet_a_example_bridge_version'],
            MODULE.V275_PACKET_A_EXAMPLE_BRIDGE_VERSION,
        )
        self.assertTrue(contract['v275_exact_packet_a_replenishment_only'])
        self.assertTrue(contract['v275_sealed_change_family_shape_only'])
        self.assertTrue(
            contract[
                'v275_historical_frontier_not_recomputed_for_example'
            ]
        )
        self.assertTrue(contract['v275_cached_frontier_unchanged'])
        self.assertFalse(contract['v275_provider_invoked_by_bridge'])
        self.assertTrue(contract['v275_proposal_validation_unchanged'])
        self.assertTrue(contract['v275_s1_gates_unchanged'])
        self.assertTrue(contract['v275_unknown_errors_fail_closed'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

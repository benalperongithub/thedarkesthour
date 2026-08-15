from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v270_pre_exhaustion_bridge_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


class V270PreExhaustionBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, experiments = MODULE.kernel.registry()
        cls.source = MODULE.kernel.validate_config(
            MODULE.kernel.performance_config(
                experiments['TDH-SCOUT-000001-VTM-NODOGE-1H'],
                'BTCUSDT',
            )
        )

    def controller(self, actor='codex'):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v225_next_actor = actor
        controller._v225_codex_family = None
        return controller

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
                    'strategy_config': copy.deepcopy(self.source),
                }],
            },
        }

    @staticmethod
    def structural_exhaustion(controller, *args, **kwargs):
        raise MODULE.LabError(MODULE.V270_STRUCTURAL_EXHAUSTION_ERROR)

    def test_exact_codex_structural_exhaustion_returns_auditable_empty_frontier(self):
        parent = MODULE.Controller.__mro__[1]
        controller = self.controller('codex')
        with mock.patch.object(
            parent,
            '_diverse_frontier',
            new=self.structural_exhaustion,
        ):
            self.assertEqual(controller._diverse_frontier(), [])

        event = controller._v270_pre_exhaustion_bridge
        self.assertEqual(
            event['version'], MODULE.V270_PRE_EXHAUSTION_BRIDGE_VERSION
        )
        self.assertEqual(event['actor'], 'codex')
        self.assertFalse(event['provider_invoked'])
        self.assertFalse(event['trading_actions'])
        self.assertFalse(event['exchange_api_access'])

    def test_claude_and_unknown_errors_remain_fail_closed(self):
        parent = MODULE.Controller.__mro__[1]
        claude = self.controller('claude')
        with mock.patch.object(
            parent,
            '_diverse_frontier',
            new=self.structural_exhaustion,
        ):
            with self.assertRaisesRegex(
                MODULE.LabError, 'structural NO_SIGNAL quarantine'
            ):
                claude._diverse_frontier()

        def unknown(controller, *args, **kwargs):
            raise MODULE.LabError('unexpected data or provider failure')

        codex = self.controller('codex')
        with mock.patch.object(parent, '_diverse_frontier', new=unknown):
            with self.assertRaisesRegex(MODULE.LabError, 'unexpected data'):
                codex._diverse_frontier()

    def test_round_context_runs_reviewed_queue_before_global_rollover(self):
        parent = MODULE.Controller.__mro__[1]
        raw_parent = MODULE.V236_QUARANTINE_CLASS.__mro__[1]
        controller = self.controller('codex')

        def raw_registered_frontier(this, *args, **kwargs):
            return [{'config': copy.deepcopy(self.source)}]

        def inherited_round_context(this, round_number):
            return self.context(this._diverse_frontier())

        controller._v251_round_context = types.MethodType(
            inherited_round_context, controller
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            controller.run_dir = Path(temp_dir)
            with mock.patch.object(
                parent,
                '_diverse_frontier',
                new=self.structural_exhaustion,
            ), mock.patch.object(
                raw_parent,
                '_diverse_frontier',
                new=raw_registered_frontier,
            ):
                updated = controller.round_context(1)

            self.assertEqual(len(updated['novelty_frontier']), 1)
            admitted = updated['novelty_frontier'][0]
            self.assertEqual(
                admitted['config']['experiment_id'],
                MODULE.V269_REVIEWED_SEED_PRIORITY[0],
            )
            self.assertTrue(MODULE._v269_exact_reviewed_queue_item(admitted))
            self.assertEqual(
                updated['v269_reviewed_seed_replenishment']['status'],
                'EXACT_REVIEWED_SEED_ADMITTED',
            )
            self.assertTrue(
                updated['v270_pre_exhaustion_bridge']['frontier_replenished']
            )
            self.assertEqual(
                updated['v270_pre_exhaustion_bridge'][
                    'reviewed_seed_queue_status'
                ],
                'EXACT_REVIEWED_SEED_ADMITTED',
            )

            round_dir = Path(temp_dir) / 'round-01'
            queue_path = round_dir / 'REVIEWED_SEED_QUEUE_V269.json'
            bridge_path = round_dir / 'PRE_EXHAUSTION_BRIDGE_V270.json'
            carrier_path = round_dir / 'QUARANTINE_CARRIER_V271.json'
            self.assertTrue(queue_path.is_file())
            self.assertTrue(bridge_path.is_file())
            self.assertTrue(carrier_path.is_file())
            self.assertEqual(
                json.loads(queue_path.read_text(encoding='utf-8'))['status'],
                'EXACT_REVIEWED_SEED_ADMITTED',
            )
            self.assertTrue(
                json.loads(bridge_path.read_text(encoding='utf-8'))[
                    'frontier_replenished'
                ]
            )
            self.assertTrue(
                json.loads(carrier_path.read_text(encoding='utf-8'))[
                    'carrier_removed_before_provider'
                ]
            )

    def test_runtime_contract_preserves_offline_s1_fail_closed_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v270_pre_exhaustion_bridge_version'],
            MODULE.V270_PRE_EXHAUSTION_BRIDGE_VERSION,
        )
        self.assertTrue(
            contract[
                'v270_codex_structural_exhaustion_becomes_reviewable_empty_frontier'
            ]
        )
        self.assertTrue(
            contract[
                'v270_reviewed_seed_replenishment_runs_before_v252_rollover'
            ]
        )
        self.assertTrue(contract['v270_claude_peer_semantics_unchanged'])
        self.assertTrue(contract['v270_unknown_errors_fail_closed'])
        self.assertTrue(contract['controller_only_promotion'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])


if __name__ == '__main__':
    unittest.main()

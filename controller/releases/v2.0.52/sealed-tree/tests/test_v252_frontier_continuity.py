import copy
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v252_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.52 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SOURCE_CONFIG = {
    "control_mode": "PERFORMANCE",
    "experiment_id": "TDH-LIT-0663",
    "family": "VOL_MANAGED_MOM",
    "params": {
        "max_leverage": 1,
        "momentum_lookback_days": 112,
        "target_vol_pct": 25,
        "vol_lookback_days": 30,
    },
    "symbol": "BTCUSDT",
    "timeframe": "1d",
}


def valid_context():
    return {
        "contract_version": "2.0.2",
        "research_round": 1,
        "latest_s1_financial_evidence": {
            "candidates": [{"strategy_config": copy.deepcopy(SOURCE_CONFIG)}],
        },
        "novelty_frontier": [{
            "config": {
                **copy.deepcopy(SOURCE_CONFIG),
                "experiment_id": "TDH-LIT-0664",
            },
        }],
        "registered_candidate_contract": {
            "registered_families": ["VOL_MANAGED_MOM"],
            "dual_lane_contract": {},
        },
        "tdh_research_selection": {"family_cards": [{"family_id": "VOL_MANAGED_MOM"}]},
    }


class V252FrontierContinuityTests(unittest.TestCase):
    def test_current_peer_lane_failure_becomes_local_skip(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._v225_next_actor = "codex"
        controller._v251_round_context = types.MethodType(
            lambda self, round_number: valid_context(), controller
        )
        with tempfile.TemporaryDirectory() as td:
            controller.run_dir = Path(td)
            codex_context = controller.round_context(1)
            self.assertTrue(codex_context["novelty_frontier"])

            controller._v225_next_actor = "claude"
            controller._v225_codex_family = "VOL_MANAGED_MOM"

            def peer_exhausted(self, round_number):
                raise MODULE.LabError(
                    "v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine"
                )

            controller._v251_round_context = types.MethodType(peer_exhausted, controller)
            claude_context = controller.round_context(1)
            self.assertEqual(claude_context["novelty_frontier"], [])
            self.assertEqual(
                claude_context["v252_frontier_continuity"]["mode"],
                "V252_PEER_FRONTIER_EXHAUSTED_LANE_SKIP",
            )
            artifact = Path(td) / "round-01" / "CLAUDE_PEER_FRONTIER_EXHAUSTED_V252.json"
            self.assertTrue(artifact.is_file())
            self.assertFalse(json.loads(artifact.read_text())["provider_invoked"])

    def test_global_exhaustion_is_bounded_epoch_outcome(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.execute_round

        def exhausted(controller, round_number, preflight):
            raise MODULE.LabError(
                "v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine"
            )

        parent.execute_round = exhausted
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            controller._v225_next_actor = "codex"
            with tempfile.TemporaryDirectory() as td:
                controller.run_dir = Path(td)
                summary, found, score = controller.execute_round(1, {})
                self.assertFalse(found)
                self.assertIsNone(score)
                self.assertEqual(summary["verdict"], "REVISE")
                self.assertEqual(summary["stop_stage"], "S1_FRONTIER_EXHAUSTED")
                event = Path(td) / "round-01" / "FRONTIER_EXHAUSTION_V252.json"
                self.assertTrue(event.is_file())
                self.assertFalse(json.loads(event.read_text())["provider_invoked"])
        finally:
            parent.execute_round = original

    def test_unknown_errors_still_fail_closed(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.execute_round

        def unknown(controller, round_number, preflight):
            raise MODULE.LabError("unexpected provider or data failure")

        parent.execute_round = unknown
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            with tempfile.TemporaryDirectory() as td:
                controller.run_dir = Path(td)
                with self.assertRaisesRegex(MODULE.LabError, "unexpected provider"):
                    controller.execute_round(1, {})
        finally:
            parent.execute_round = original

    def test_runtime_contract_preserves_safety_and_avenox_continuity(self):
        contract = MODULE.runtime_binding_contract()
        self.assertIs(contract["controller_only_promotion"], True)
        self.assertIs(contract["trading_actions"], False)
        self.assertIs(contract["exchange_api_access"], False)
        self.assertIs(contract["v252_peer_frontier_exhaustion_is_lane_local"], True)
        self.assertIs(contract["v252_eligible_frontier_exhaustion_rolls_epoch"], True)
        self.assertIs(contract["v252_unknown_errors_fail_closed"], True)


if __name__ == "__main__":
    unittest.main()

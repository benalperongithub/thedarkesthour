import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location(
    "tdh_strategy_lab_v251_lane_test",
    CONTROLLER,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.51 controller")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SOURCE_CONFIG = {
    "control_mode": "PERFORMANCE",
    "experiment_id": "TDH-LIT-0723",
    "family": "SUPPORT_RES_BREAK",
    "params": {
        "buffer_pct": 0.25,
        "level_window": 10,
        "persistence_bars": 5,
        "timeframe": "1d",
    },
    "symbol": "ETHUSDT",
    "timeframe": "1d",
}

CURRENT_FAILURE_TARGET = {
    "control_mode": "PERFORMANCE",
    "experiment_id": "TDH-LIT-0724",
    "family": "SUPPORT_RES_BREAK",
    "params": {
        "buffer_pct": 0.25,
        "level_window": 100,
        "persistence_bars": 2,
        "timeframe": "1d",
    },
    "symbol": "BTCUSDT",
    "timeframe": "1d",
}


class V251LaneResilienceTests(unittest.TestCase):
    def test_current_symbol_plus_seed_failure_is_filtered(self):
        axes = MODULE._v251_transition_axes(
            SOURCE_CONFIG,
            CURRENT_FAILURE_TARGET,
        )
        self.assertEqual(axes, ("symbol", "registered_seed"))
        self.assertFalse(MODULE._v251_legal_frontier_item(
            SOURCE_CONFIG,
            {"config": CURRENT_FAILURE_TARGET},
        ))

    def test_each_legal_single_axis_transition_remains_available(self):
        pure_symbol = json.loads(json.dumps(SOURCE_CONFIG))
        pure_symbol["symbol"] = "BTCUSDT"

        pure_seed = json.loads(json.dumps(SOURCE_CONFIG))
        pure_seed["experiment_id"] = "TDH-LIT-0724"
        pure_seed["params"]["level_window"] = 100
        pure_seed["params"]["persistence_bars"] = 2

        family_change = json.loads(json.dumps(CURRENT_FAILURE_TARGET))
        family_change["family"] = "VOL_MANAGED_MOM"

        for target in (pure_symbol, pure_seed, family_change):
            with self.subTest(target=target):
                self.assertTrue(MODULE._v251_legal_frontier_item(
                    SOURCE_CONFIG,
                    {"config": target},
                ))

    def test_known_validation_failure_is_quarantined_with_usage(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.run_claude_proposal

        def failing_parent(controller, round_dir, context):
            envelope = {
                "result": "{}",
                "usage": {
                    "input_tokens": 2,
                    "output_tokens": 4,
                    "cache_creation_input_tokens": 3,
                },
            }
            (round_dir / "claude-proposal.json").write_text(
                json.dumps(envelope),
                encoding="utf-8",
            )
            raise MODULE.LabError(
                "CHANGE_SYMBOL changed more than the symbol"
            )

        parent.run_claude_proposal = failing_parent
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            with tempfile.TemporaryDirectory() as td:
                round_dir = Path(td)
                proposal, usage = controller.run_claude_proposal(
                    round_dir,
                    {
                        "contract_version": "2.0.2",
                        "research_round": 1,
                    },
                )
                self.assertEqual(proposal["candidates"], [])
                self.assertEqual(
                    proposal["controller_batch"]["mode"],
                    "V251_INVALID_LANE_QUARANTINED",
                )
                self.assertEqual(usage["billable_tokens"], 9)
                self.assertTrue((
                    round_dir
                    / "CLAUDE_PROPOSAL_VALIDATION_QUARANTINE.json"
                ).is_file())
        finally:
            parent.run_claude_proposal = original

    def test_unknown_error_still_fails_closed(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.run_claude_proposal

        def failing_parent(controller, round_dir, context):
            raise MODULE.LabError("unexpected provider or data failure")

        parent.run_claude_proposal = failing_parent
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaisesRegex(
                    MODULE.LabError,
                    "unexpected provider or data failure",
                ):
                    controller.run_claude_proposal(
                        Path(td),
                        {
                            "contract_version": "2.0.2",
                            "research_round": 1,
                        },
                    )
        finally:
            parent.run_claude_proposal = original

    def test_empty_legal_frontier_skips_provider(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.run_claude_proposal
        called = {"value": False}

        def forbidden_parent(controller, round_dir, context):
            called["value"] = True
            raise AssertionError("provider must not be invoked")

        parent.run_claude_proposal = forbidden_parent
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            context = {
                "contract_version": "2.0.2",
                "research_round": 1,
                "latest_s1_financial_evidence": {
                    "candidates": [{
                        "strategy_config": SOURCE_CONFIG,
                    }],
                },
                "novelty_frontier": [],
            }
            with tempfile.TemporaryDirectory() as td:
                proposal, usage = controller.run_claude_proposal(
                    Path(td),
                    context,
                )
                self.assertFalse(called["value"])
                self.assertEqual(proposal["candidates"], [])
                self.assertEqual(usage, {})
        finally:
            parent.run_claude_proposal = original

    def test_rejected_lane_does_not_remove_valid_peer_lane(self):
        valid = {
            "contract_version": "2.0.2",
            "candidates": [{
                "candidate_id": "codex-valid",
                "config": {
                    "family": "VOL_MANAGED_MOM",
                    "symbol": "BTCUSDT",
                    "timeframe": "1d",
                },
            }],
        }
        rejected = MODULE._v251_rejected_lane(
            {"contract_version": "2.0.2", "research_round": 1},
            "claude",
            "V251_INVALID_LANE_QUARANTINED",
            "invalid transition",
        )

        merged = MODULE.Controller._merge_proposals(
            valid,
            rejected,
            1,
        )
        self.assertEqual(len(merged["candidates"]), 1)
        self.assertEqual(
            merged["candidates"][0]["candidate_id"],
            "codex-valid",
        )

    def test_runtime_safety_contract_is_unchanged(self):
        contract = MODULE.runtime_binding_contract()
        self.assertIs(contract["controller_only_promotion"], True)
        self.assertIs(contract["trading_actions"], False)
        self.assertIs(contract["exchange_api_access"], False)
        self.assertIs(
            contract["v251_lane_validation_quarantine"],
            True,
        )
        self.assertIs(
            contract["v251_multi_axis_frontier_filter"],
            True,
        )
        self.assertIs(
            contract["v251_unknown_errors_fail_closed"],
            True,
        )


if __name__ == "__main__":
    unittest.main()

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v254_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.54 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def scout_proposal():
    return {
        "proposal_version": "tdh-frontier-inbox-v1",
        "hypothesis_id": "TDH-SCOUT-000001",
        "status": "UNTRUSTED_INBOX",
        "family_thesis": "Funding dislocations may predict bounded mean reversion after crowding.",
        "causal_mechanism": "Extreme funding can proxy leveraged positioning that unwinds after price confirmation.",
        "source_evidence": [{
            "source_id": "atlas-card-01",
            "claim": "Funding extremes were associated with later reversals in the supplied evidence.",
            "provenance": "TDH internal evidence atlas; requires controller source verification.",
        }],
        "required_data": ["OHLCV", "funding_rate"],
        "timeframes": ["1h", "4h"],
        "bounded_parameters": {"funding_z": [1.5, 2.0, 2.5], "lookback": [48, 96]},
        "baseline_thesis": "Compare against the registered no-funding baseline.",
        "negative_control_thesis": "Shuffle funding timestamps while preserving return order.",
        "falsification": {
            "failure_condition": "Reject if robust S1 windows do not improve expectancy and profit factor.",
            "minimum_test": "Run only the controller-owned offline S1 partition gate.",
            "expected_information_gain": "Distinguish positioning information from generic reversal exposure.",
        },
        "safety": {
            "data_only": True,
            "contains_executable_code": False,
            "trading_actions": False,
            "exchange_api_access": False,
            "controller_registration_required": True,
        },
    }


class V254FrontierScoutTests(unittest.TestCase):
    def setUp(self):
        self.original_registry = MODULE.kernel.registry
        self.original_performance_config = MODULE.kernel.performance_config
        self.original_validate_config = MODULE.kernel.validate_config

    def tearDown(self):
        MODULE.kernel.registry = self.original_registry
        MODULE.kernel.performance_config = self.original_performance_config
        MODULE.kernel.validate_config = self.original_validate_config

    def install_kernel(self):
        experiments = {
            "EXP-A": {"experiment_id": "EXP-A", "family_id": "FAM-A", "universe": ["BTCUSDT"]},
            "EXP-B": {"experiment_id": "EXP-B", "family_id": "FAM-B", "universe": ["ETHUSDT"]},
            "EXP-C": {"experiment_id": "EXP-C", "family_id": "FAM-C", "universe": ["SOLUSDT"]},
        }
        MODULE.kernel.registry = lambda: ({}, copy.deepcopy(experiments))

        def performance_config(experiment, symbol):
            return {
                "family": experiment["family_id"],
                "experiment_id": experiment["experiment_id"],
                "symbol": symbol,
                "timeframe": "1h",
                "params": {"timeframe": "1h", "window": 24},
                "control_mode": "PERFORMANCE",
            }

        MODULE.kernel.performance_config = performance_config
        MODULE.kernel.validate_config = lambda config: copy.deepcopy(config)

    def test_strict_scout_payload_remains_untrusted(self):
        proposal = MODULE._v254_validate_scout_proposal(scout_proposal())
        self.assertEqual(proposal["status"], "UNTRUSTED_INBOX")
        self.assertTrue(proposal["safety"]["controller_registration_required"])
        self.assertFalse(proposal["safety"]["contains_executable_code"])

    def test_executable_content_and_safety_mutation_are_rejected(self):
        executable = scout_proposal()
        executable["causal_mechanism"] = "Use subprocess to execute a generated strategy before testing."
        with self.assertRaisesRegex(MODULE.LabError, "forbidden"):
            MODULE._v254_validate_scout_proposal(executable)

        unsafe = scout_proposal()
        unsafe["safety"]["controller_registration_required"] = False
        with self.assertRaisesRegex(MODULE.LabError, "safety contract"):
            MODULE._v254_validate_scout_proposal(unsafe)

    def test_low_watermark_admits_only_registered_deduplicated_seeds(self):
        self.install_kernel()
        context = {
            "novelty_frontier": [],
            "tdh_research_selection": {
                "experiment_seeds": [
                    {"experiment_id": "EXP-A"},
                    {"experiment_id": "EXP-B"},
                    {"experiment_id": "EXP-C"},
                ],
                "family_cards": [
                    {"family_id": "FAM-A"},
                    {"family_id": "FAM-B"},
                    {"family_id": "FAM-C"},
                ],
            },
            "previous_rounds": [{"experiment_id": "EXP-A"}],
        }
        result = MODULE._v254_registered_replenishment(context, "codex")
        configs = [item["config"] for item in result["novelty_frontier"]]
        self.assertEqual([row["experiment_id"] for row in configs], ["EXP-B", "EXP-C"])
        self.assertEqual(result["v254_frontier_replenishment"]["admitted_count"], 2)
        self.assertTrue(result["v254_frontier_replenishment"]["only_existing_registered_seeds"])
        self.assertFalse(result["v254_frontier_replenishment"]["new_families_auto_admitted"])
        self.assertEqual(context["novelty_frontier"], [])

    def test_claude_replenishment_excludes_codex_peer_family(self):
        self.install_kernel()
        context = {
            "novelty_frontier": [],
            "tdh_research_selection": {
                "experiment_seeds": [{"experiment_id": "EXP-A"}, {"experiment_id": "EXP-B"}],
                "family_cards": [{"family_id": "FAM-A"}, {"family_id": "FAM-B"}],
            },
        }
        result = MODULE._v254_registered_replenishment(context, "claude", "FAM-A")
        self.assertEqual(
            [item["config"]["family"] for item in result["novelty_frontier"]],
            ["FAM-B"],
        )

    def test_unknown_selected_seed_fails_closed(self):
        self.install_kernel()
        context = {
            "novelty_frontier": [],
            "tdh_research_selection": {
                "experiment_seeds": [{"experiment_id": "EXP-UNKNOWN"}],
                "family_cards": [],
            },
        }
        with self.assertRaisesRegex(MODULE.LabError, "not registered"):
            MODULE._v254_registered_replenishment(context, "codex")

    def test_scout_prompt_is_bounded_and_tools_are_forbidden(self):
        context = {
            "novelty_frontier": [],
            "tdh_research_selection": {
                "family_cards": [{"family_id": f"FAM-{index}", "thesis": "x" * 3000} for index in range(12)]
            },
            "negative_memory": [{"large": "y" * 20000}],
        }
        prompt = MODULE._v254_scout_prompt(
            context,
            {"findings": [{"claim": "bounded research finding"}]},
            {"findings": [{"claim": "bounded critic finding"}]},
        )
        self.assertLessEqual(len(prompt), MODULE.V254_SCOUT_PROMPT_MAX_CHARS)
        self.assertIn("tools/web/shell/repository access are forbidden", prompt)
        self.assertIn("New families remain untrusted", prompt)

    def test_runtime_contract_preserves_hard_safety(self):
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract["controller_only_promotion"])
        self.assertFalse(contract["trading_actions"])
        self.assertFalse(contract["exchange_api_access"])
        self.assertTrue(contract["v254_only_existing_registered_seeds_auto_admitted"])
        self.assertTrue(contract["v254_frontier_scout_untrusted_inbox"])
        self.assertTrue(contract["v254_scout_tools_disabled"])
        self.assertTrue(contract["v254_scout_never_auto_registers"])
        self.assertTrue(contract["v254_unknown_registration_errors_fail_closed"])


if __name__ == "__main__":
    unittest.main()

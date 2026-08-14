from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SEALED_V220 = Path(
    "/srv/tdh-collab/controller/strategy-lab-v2/v2.0.20/strategy_lab_controller.py"
)


class DualAgentContractTests(unittest.TestCase):
    def test_config_is_offline_and_dual(self):
        config = json.loads((ROOT / "config.json").read_text())
        self.assertEqual("offline", config["research_mode"])
        self.assertFalse(config["trading_actions"])
        self.assertFalse(config["exchange_api_access"])
        self.assertTrue(config["dual_agent_research"])
        self.assertTrue(config["both_agents_propose_each_round"])
        self.assertTrue(config["both_agents_analyze_each_s1_batch"])

    def test_controller_has_dual_sequence_and_consensus(self):
        source = SEALED_V220.read_text()
        for marker in (
            "CODEX_INDEPENDENT_PROPOSAL", "CLAUDE_INDEPENDENT_PROPOSAL",
            "DUAL_POST_S1_ANALYSIS", "DUAL_AGENT_SYNTHESIS.json",
            "s1_pass & codex_approved & claude_approved",
        ):
            self.assertIn(marker, source)
        wrapper = (ROOT / "strategy_lab_controller.py").read_text()
        self.assertIn("class Controller(v220.Controller)", wrapper)
        self.assertIn("v220.v217.v216.Controller = Controller", wrapper)

    def test_dashboard_is_tdh_only(self):
        source = (ROOT / "tdh_research_dashboard.py").read_text()
        self.assertIn("TDH Research Lab", source)
        self.assertIn("127.0.0.1", source)
        self.assertIn("8765", source)
        self.assertNotIn("8502", source)
        self.assertNotIn("8501", source)


if __name__ == "__main__":
    unittest.main()

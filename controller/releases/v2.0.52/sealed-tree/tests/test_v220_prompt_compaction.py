import unittest
from pathlib import Path


V220_SOURCE_PATH = Path(
    "/srv/tdh-collab/controller/strategy-lab-v2/v2.0.20/strategy_lab_controller.py"
)
SOURCE = V220_SOURCE_PATH.read_text(encoding="utf-8")


class V220PromptCompactionRegressionTests(unittest.TestCase):
    def test_full_round_context_is_not_reused_after_s1(self):
        self.assertNotIn(
            "review_context = self.round_context(round_number)",
            SOURCE,
        )

    def test_compact_evidence_and_budget_are_enforced(self):
        self.assertIn('"s1_evidence": evidence', SOURCE)
        self.assertIn('"POST_S1_PROMPT_BUDGET.json"', SOURCE)
        self.assertIn("if prompt_input_chars > 10000:", SOURCE)

    def test_hard_targets_remain_conjunctive(self):
        for text in (
            '"net_win_rate_min": 0.50',
            '"realized_reward_risk_min": 2.0',
            '"max_drawdown_pct_max": 10.0',
            '"baseline_and_negative_control_must_be_beaten": True',
            '"all_wfo_windows_required": True',
        ):
            self.assertIn(text, SOURCE)

    def test_offline_policy_remains_explicit(self):
        self.assertIn('"research_mode": "offline"', SOURCE)
        self.assertIn('"trading_actions": False', SOURCE)
        self.assertIn('"exchange_api_access": False', SOURCE)


if __name__ == "__main__":
    unittest.main()

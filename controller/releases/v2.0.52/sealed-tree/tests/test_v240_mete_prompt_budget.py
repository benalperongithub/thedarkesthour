from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v240_budget_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V240MetePromptBudgetTests(unittest.TestCase):
    def test_prompt_target_is_unchanged(self):
        module = load_controller()
        self.assertEqual(module.PROMPT_TARGET_MAX_CHARS, 12000)
        self.assertEqual(module.PROMPT_HARD_CEILING_CHARS, 16000)

    def test_mete_card_is_bounded_and_fail_closed(self):
        module = load_controller()
        card = module.compact_mete_prompt_card()
        encoded = json.dumps(card, sort_keys=True, separators=(",", ":"))
        self.assertLessEqual(len(encoded), 320)
        self.assertEqual(card["id"], "MK_STR_LIQ_IMB_v1")
        self.assertEqual(card["active"], "A/B/C@5m")
        self.assertEqual(card["min_trades"], 300)
        self.assertEqual(card["promotion"], "BLOCKED_PENDING_B0")
        self.assertTrue(card["full_spec_on_vps"])
        self.assertNotIn("blocked", card)
        self.assertNotIn("instruction", card)
        self.assertNotIn("source_claim", card)

    def test_authoritative_s1_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location(
    "tdh_strategy_lab_v250_parser_test",
    CONTROLLER,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.50 controller")

MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class V250CriticResultParserTests(unittest.TestCase):
    def test_real_provider_envelope_shape_and_usage(self):
        result = {
            "contract_version": "tdh-test",
            "research_round": 1,
            "verdict": "REVISE",
            "approved_candidate_ids": [],
            "findings": [{
                "finding_id": "critic-01",
                "severity": "HIGH",
                "claim": "The apparent edge is regime-fragile.",
                "evidence": "The control comparison fails outside one window.",
            }],
            "reasoning_packet": {},
        }
        envelope = {
            "result": json.dumps(result),
            "usage": {
                "input_tokens": 11,
                "output_tokens": 7,
                "cache_read_input_tokens": 3,
                "cache_creation_input_tokens": 2,
            },
            "modelUsage": {"claude-test": {"inputTokens": 11}},
        }

        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "claude-result.json"
            log.write_text(json.dumps(envelope), encoding="utf-8")
            usage, model_usage, outer = MODULE._claude_raw_usage(log)

        self.assertEqual(usage["billable_tokens"], 20)
        self.assertIn("claude-test", model_usage)

        raw = MODULE._extract_critic_payload(outer)
        normalized = MODULE._normalize_critic(
            raw,
            {"contract_version": "tdh-test", "research_round": 1},
        )
        self.assertEqual(normalized["verdict"], "REVISE")
        self.assertEqual(normalized["approved_candidate_ids"], [])
        self.assertEqual(len(normalized["findings"]), 1)

    def test_dict_result_is_copied(self):
        original = {
            "findings": [{
                "claim": "Claim",
                "evidence": "Evidence",
            }]
        }
        parsed = MODULE._extract_critic_payload({"result": original})
        self.assertEqual(parsed, original)
        self.assertIsNot(parsed, original)

        parsed["findings"][0]["claim"] = "Changed"
        self.assertEqual(original["findings"][0]["claim"], "Claim")

    def test_invalid_results_fail_closed(self):
        invalid = (
            {},
            {"result": ""},
            {"result": "not-json"},
            {"result": json.dumps(["not", "an", "object"])},
        )
        for envelope in invalid:
            with self.subTest(envelope=envelope):
                with self.assertRaises(MODULE.LabError):
                    MODULE._extract_critic_payload(envelope)

    def test_hidden_parser_dependency_removed_and_safety_preserved(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertNotIn(
            "raw_result, _ = extract_claude_final(log)",
            source,
        )

        contract = MODULE.runtime_binding_contract()
        self.assertIs(contract["controller_only_promotion"], True)
        self.assertIs(contract["trading_actions"], False)
        self.assertIs(contract["exchange_api_access"], False)


if __name__ == "__main__":
    unittest.main()

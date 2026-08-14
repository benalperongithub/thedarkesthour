import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v257_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.57 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def valid_proposal():
    return {
        "proposal_version": "tdh-frontier-inbox-v1",
        "hypothesis_id": "TDH-SCOUT-000147",
        "status": "UNTRUSTED_INBOX",
        "family_thesis": "A coin-diversity control may expose a single-asset artifact.",
        "causal_mechanism": (
            "A volume signal dominated by one asset can mimic cross-coin persistence."
        ),
        "source_evidence": [{
            "source_id": "critic:finding-1",
            "claim": "DOGE appears in every positive cluster.",
            "provenance": "cached independent critic advisory",
        }],
        "required_data": ["OHLCV", "per-coin expectancy"],
        "timeframes": ["5m", "15m"],
        "bounded_parameters": {
            "minimum_unique_coins": 5,
            "exclude_doge_control": True,
        },
        "baseline_thesis": "The signal persists after DOGE exclusion.",
        "negative_control_thesis": "The signal vanishes after DOGE exclusion.",
        "falsification": {
            "failure_condition": "DOGE-excluded expectancy is non-positive.",
            "minimum_test": "Run the registered signal on five non-DOGE assets.",
            "expected_information_gain": "Separates cross-coin edge from one-asset noise.",
        },
        "safety": {
            "data_only": True,
            "contains_executable_code": False,
            "trading_actions": False,
            "exchange_api_access": False,
            "controller_registration_required": True,
        },
    }


def provider_outer(result):
    return {
        "result": result,
        "usage": {
            "input_tokens": 1,
            "output_tokens": 2,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
        },
        "modelUsage": {},
        "terminal_reason": "completed",
    }


class V257ScoutResponseConformanceTests(unittest.TestCase):
    def test_accepts_raw_json_object(self):
        proposal = valid_proposal()
        parsed = MODULE._v257_extract_scout_payload(
            provider_outer(json.dumps(proposal))
        )
        self.assertEqual(parsed, proposal)

    def test_accepts_exact_single_json_fence(self):
        proposal = valid_proposal()
        fenced = "```json\n" + json.dumps(proposal) + "\n```"
        parsed = MODULE._v257_extract_scout_payload(provider_outer(fenced))
        self.assertEqual(parsed, proposal)

    def test_rejects_prose_around_fenced_json(self):
        fenced = "Here is the result:\n```json\n{}\n```"
        with self.assertRaisesRegex(
            MODULE.LabError, "must be raw JSON or one exact JSON fence"
        ):
            MODULE._v257_extract_scout_payload(provider_outer(fenced))

    def test_prompt_states_exact_machine_constraints(self):
        prompt = MODULE._v254_scout_prompt(
            {"research_round": 1, "novelty_frontier": []},
            {"findings": [{"claim": "research"}]},
            {"findings": [{"claim": "critic"}]},
            "v2.0.54 scout timeframe invalid",
        )
        self.assertIn("TDH-SCOUT-000001", prompt)
        self.assertIn("raw JSON", prompt)
        self.assertIn("1-80 characters", prompt)
        self.assertIn("timeframes must be a JSON array", prompt)
        self.assertIn("PREVIOUS_VALIDATION_ERROR", prompt)
        self.assertLessEqual(len(prompt), MODULE.V254_SCOUT_PROMPT_MAX_CHARS)

    def test_schema_failure_retries_once_then_validates_inbox(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller.config = SimpleNamespace(
            claude_user="claude-agent",
            claude_bin="/bin/true",
            worker_timeout_seconds=5,
        )
        controller._avu = {"codex": {}, "claude": {}}
        controller._provider_audit = lambda *args, **kwargs: None
        calls = []

        def run_worker(**kwargs):
            calls.append(kwargs["prompt"])
            result = (
                json.dumps({"proposal_version": "tdh-frontier-inbox-v1"})
                if len(calls) == 1
                else "```json\n" + json.dumps(valid_proposal()) + "\n```"
            )
            kwargs["log_path"].write_text(
                json.dumps(provider_outer(result)), encoding="utf-8"
            )

        controller.run_worker = run_worker
        original_args = MODULE._critic_args
        original_here = MODULE.HERE
        try:
            MODULE._critic_args = lambda self: []
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                MODULE.HERE = root / "v2.0.57"
                sd = root / "run" / "avenox-subagents"
                sd.mkdir(parents=True)
                record = controller._run_frontier_scout(
                    sd,
                    {"research_round": 1, "novelty_frontier": []},
                    {"findings": [{"claim": "research"}]},
                    {"findings": [{"claim": "critic"}]},
                    "CACHE_HIT",
                )
                self.assertEqual(len(calls), 2)
                self.assertEqual(record["status"], "UNTRUSTED_INBOX")
                self.assertEqual(record["attempts_used"], 2)
                self.assertFalse(record["automatically_registered"])
                self.assertTrue(
                    list((root / "frontier-scout-inbox").glob("TDH-SCOUT-*.json"))
                )
                self.assertIn("PREVIOUS_VALIDATION_ERROR", calls[1])
        finally:
            MODULE._critic_args = original_args
            MODULE.HERE = original_here

    def test_unknown_errors_fail_closed_without_retry(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller.config = SimpleNamespace(
            claude_user="claude-agent",
            claude_bin="/bin/true",
            worker_timeout_seconds=5,
        )
        controller._avu = {"codex": {}, "claude": {}}
        calls = []

        def run_worker(**kwargs):
            calls.append(kwargs["prompt"])
            raise RuntimeError("unexpected Scout provider integration failure")

        controller.run_worker = run_worker
        original_args = MODULE._critic_args
        try:
            MODULE._critic_args = lambda self: []
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaisesRegex(RuntimeError, "unexpected Scout"):
                    controller._run_frontier_scout(
                        Path(td), {}, {}, {}, "CACHE_HIT"
                    )
            self.assertEqual(len(calls), 1)
        finally:
            MODULE._critic_args = original_args

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract["v257_exact_scout_json_fence_supported"])
        self.assertTrue(contract["v257_scout_schema_retry_is_bounded"])
        self.assertTrue(contract["v257_invalid_scout_never_registers"])
        self.assertTrue(contract["v257_unknown_errors_fail_closed"])
        self.assertTrue(contract["controller_only_promotion"])
        self.assertFalse(contract["trading_actions"])
        self.assertFalse(contract["exchange_api_access"])


if __name__ == "__main__":
    unittest.main()

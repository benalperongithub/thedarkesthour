from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"
V230_TEST = ROOT / "tests" / "test_v230_inheritance_boundary.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_controller():
    return load_module(CONTROLLER, "tdh_v231_target_test")


def raw_context():
    helper = load_module(V230_TEST, "tdh_v230_fixture_for_v231")
    return helper.raw_v227_context()


class V231TargetAlignedBoundaryTests(unittest.TestCase):
    def test_boundary_limit_matches_v221_target_max(self):
        module = load_controller()
        self.assertEqual(module.PROMPT_TARGET_MAX_CHARS, 12000)
        self.assertEqual(module.MODEL_CONTEXT_MAX_CHARS, module.PROMPT_TARGET_MAX_CHARS)
        self.assertEqual(module.v230.MODEL_CONTEXT_MAX_CHARS, 12000)
        self.assertEqual(module.PROMPT_HARD_CEILING_CHARS, 16000)

    def test_real_failure_class_above_9000_but_below_12000_is_accepted(self):
        module = load_controller()
        base = raw_context()
        accepted = None
        for pad in range(500, 9001, 250):
            probe = copy.deepcopy(base)
            candidate = probe["latest_s1_financial_evidence"]["candidates"][0]
            candidate["delta_vs_baseline"]["boundary_padding"] = "X" * pad
            try:
                compact = module.compact_model_context_from_raw_boundary(probe)
                size = module._json_chars(compact)
                final_context, _, report = module._compact_prompt_inputs("codex_proposal", compact)
            except module.LabError:
                continue
            if 9000 < size <= module.PROMPT_TARGET_MAX_CHARS and report["final_input_chars"] <= module.PROMPT_TARGET_MAX_CHARS:
                accepted = (compact, final_context, report, size)
                break
        self.assertIsNotNone(accepted, "could not construct a 9k-12k accepted boundary packet")
        compact, final_context, report, size = accepted
        self.assertGreater(size, 9000)
        self.assertLessEqual(size, 12000)
        self.assertLessEqual(report["final_input_chars"], 12000)
        evidence = final_context["latest_s1_financial_evidence"]
        self.assertTrue(evidence["candidates"])
        self.assertEqual(evidence["candidates"][0]["candidate_id"], "claude-r01-c01")
        shared = evidence["prior_dual_agent_synthesis"]["shared_research_context"]
        self.assertEqual(shared["source_run_id"], "tdh-prior")

    def test_boundary_above_12000_still_fails_closed(self):
        module = load_controller()
        probe = raw_context()
        candidate = probe["latest_s1_financial_evidence"]["candidates"][0]
        candidate["delta_vs_baseline"]["boundary_padding"] = "X" * 30000
        with self.assertRaises(module.LabError):
            module.compact_model_context_from_raw_boundary(probe)

    def test_final_v221_compactor_remains_authoritative(self):
        module = load_controller()
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn("v230.MODEL_CONTEXT_MAX_CHARS = MODEL_CONTEXT_MAX_CHARS", source)
        self.assertIn("PROMPT_TARGET_MAX_CHARS", source)
        self.assertIs(module._compact_prompt_inputs.__name__, module._compact_prompt_inputs.__name__)

    def test_v224_s1_gate_identity_remains_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)


if __name__ == "__main__":
    unittest.main()

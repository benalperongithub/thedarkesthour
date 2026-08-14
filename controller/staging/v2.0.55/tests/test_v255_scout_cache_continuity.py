import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v255_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.55 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def valid_advisory(status="CACHE_HIT"):
    return {
        "status": status,
        "researcher": {
            "role": "DEEP_RESEARCH",
            "findings": [{"severity": "HIGH", "claim": "bounded research", "evidence": "S1 evidence"}],
        },
        "critic": {
            "role": "INDEPENDENT_CRITIC",
            "findings": [{"severity": "HIGH", "claim": "bounded critique", "evidence": "worst window"}],
        },
    }


class V255ScoutCacheContinuityTests(unittest.TestCase):
    def controller(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._avu = {"codex": {}, "claude": {}}
        return controller

    def test_valid_cache_hit_dispatches_only_frontier_scout(self):
        controller = self.controller()
        calls = []

        def scout(sd, context, research, critic, source_status):
            calls.append({
                "source_status": source_status,
                "research": research,
                "critic": critic,
            })
            return {
                "version": MODULE.V254_FRONTIER_SCOUT_VERSION,
                "status": "UNTRUSTED_INBOX",
                "automatically_registered": False,
            }

        controller._run_frontier_scout = scout
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            controller._v255_maybe_run_frontier_scout(
                root,
                {"novelty_frontier": []},
                valid_advisory("CACHE_HIT"),
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["source_status"], "CACHE_HIT")
            dispatch = json.loads(
                (root / "avenox-subagents" / "FRONTIER_SCOUT_DISPATCH_V255.json").read_text()
            )
            self.assertEqual(dispatch["status"], "UNTRUSTED_INBOX_VALIDATED")
            self.assertFalse(dispatch["researcher_rerun"])
            self.assertFalse(dispatch["critic_rerun"])
            self.assertFalse(dispatch["automatically_registered"])

    def test_high_watermark_does_not_dispatch(self):
        controller = self.controller()
        calls = []
        controller._run_frontier_scout = lambda *args: calls.append(args)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            controller._v255_maybe_run_frontier_scout(
                root,
                {"novelty_frontier": [{}, {}, {}]},
                valid_advisory("CACHE_HIT"),
            )
            self.assertEqual(calls, [])
            self.assertFalse((root / "avenox-subagents").exists())

    def test_invalid_cached_advisory_is_skipped_without_provider(self):
        controller = self.controller()
        calls = []
        controller._run_frontier_scout = lambda *args: calls.append(args)
        advisory = valid_advisory("CACHE_HIT")
        advisory["critic"]["findings"] = []
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            controller._v255_maybe_run_frontier_scout(
                root,
                {"novelty_frontier": []},
                advisory,
            )
            self.assertEqual(calls, [])
            self.assertFalse((root / "avenox-subagents").exists())

    def test_fresh_completed_advisory_still_dispatches(self):
        controller = self.controller()
        calls = []

        def scout(sd, context, research, critic, source_status):
            calls.append(source_status)
            return {"status": "UNTRUSTED_INBOX", "automatically_registered": False}

        controller._run_frontier_scout = scout
        with tempfile.TemporaryDirectory() as td:
            controller._v255_maybe_run_frontier_scout(
                Path(td),
                {"novelty_frontier": []},
                valid_advisory("LLM_SUBAGENTS_COMPLETED"),
            )
        self.assertEqual(calls, ["LLM_SUBAGENTS_COMPLETED"])

    def test_unknown_errors_remain_fail_closed(self):
        controller = self.controller()

        def unknown(*args):
            raise RuntimeError("unexpected scout integration failure")

        controller._run_frontier_scout = unknown
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError, "unexpected scout"):
                controller._v255_maybe_run_frontier_scout(
                    Path(td),
                    {"novelty_frontier": []},
                    valid_advisory("CACHE_HIT"),
                )

    def test_runtime_contract_preserves_hard_safety(self):
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract["controller_only_promotion"])
        self.assertFalse(contract["trading_actions"])
        self.assertFalse(contract["exchange_api_access"])
        self.assertTrue(contract["v255_scout_runs_on_valid_cache_hit"])
        self.assertTrue(contract["v255_cache_hit_does_not_rerun_researcher_or_critic"])
        self.assertTrue(contract["v255_invalid_cached_advisory_skips_scout"])
        self.assertTrue(contract["v255_unknown_errors_fail_closed"])


if __name__ == "__main__":
    unittest.main()

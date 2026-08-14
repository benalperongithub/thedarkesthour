import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v256_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.56 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


FRONTIER_ERROR = (
    "v2.0.36 novelty frontier exhausted after structural NO_SIGNAL quarantine"
)


def completed_advisory():
    return {
        "status": "LLM_SUBAGENTS_COMPLETED",
        "contract_version": "2.0.2",
        "researcher": {
            "role": "DEEP_RESEARCH",
            "findings": [{
                "severity": "HIGH",
                "claim": "registered families reached a structural ceiling",
                "evidence": "bounded S1 evidence",
            }],
        },
        "critic": {
            "role": "INDEPENDENT_CRITIC",
            "findings": [{
                "severity": "HIGH",
                "claim": "new thesis requires a decisive control",
                "evidence": "worst-window counterexample",
            }],
        },
    }


def valid_cache():
    return {
        "version": "tdh-avenox-v245",
        "fingerprint": "f" * 64,
        "advisory": completed_advisory(),
    }


class V256FrontierExhaustionScoutTests(unittest.TestCase):
    def controller(self):
        controller = MODULE.Controller.__new__(MODULE.Controller)
        controller._avu = {"codex": {}, "claude": {}}
        return controller

    def test_global_exhaustion_reuses_valid_cache_for_scout_only(self):
        controller = self.controller()
        controller.load_cache = valid_cache
        calls = []

        def scout(sd, context, research, critic, source_status):
            calls.append({
                "context": context,
                "research": research,
                "critic": critic,
                "source_status": source_status,
            })
            return {
                "version": MODULE.V254_FRONTIER_SCOUT_VERSION,
                "status": "UNTRUSTED_INBOX",
                "automatically_registered": False,
            }

        controller._run_frontier_scout = scout
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dispatch = controller._v256_scout_on_frontier_exhaustion(
                root, 1, "codex", FRONTIER_ERROR
            )
            self.assertEqual(dispatch["status"], "UNTRUSTED_INBOX_VALIDATED")
            self.assertTrue(dispatch["provider_invoked"])
            self.assertFalse(dispatch["researcher_rerun"])
            self.assertFalse(dispatch["critic_rerun"])
            self.assertFalse(dispatch["automatically_registered"])
            self.assertEqual(calls[0]["source_status"], "CACHE_HIT")
            self.assertEqual(
                calls[0]["context"]["v256_frontier_exhaustion"]["reason"],
                FRONTIER_ERROR,
            )
            self.assertTrue((root / "FRONTIER_SCOUT_DISPATCH_V256.json").is_file())
            self.assertTrue(
                (root / "avenox-subagents" / "FRONTIER_SCOUT_INBOX_V254.json").is_file()
            )

    def test_incomplete_cache_skips_without_provider(self):
        controller = self.controller()
        cache = valid_cache()
        cache["advisory"]["critic"]["findings"] = []
        controller.load_cache = lambda: cache
        controller._run_frontier_scout = lambda *args: self.fail("provider invoked")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dispatch = controller._v256_scout_on_frontier_exhaustion(
                root, 1, "codex", FRONTIER_ERROR
            )
            self.assertEqual(
                dispatch["status"], "SKIPPED_NO_VALID_CACHED_ADVISORY"
            )
            self.assertFalse(dispatch["provider_invoked"])
            self.assertFalse((root / "avenox-subagents").exists())

    def test_known_scout_rejection_is_audited_and_never_registered(self):
        controller = self.controller()
        controller.load_cache = valid_cache

        def rejected(*args):
            raise MODULE.LabError("v2.0.54 scout result is not an object")

        controller._run_frontier_scout = rejected
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dispatch = controller._v256_scout_on_frontier_exhaustion(
                root, 1, "codex", FRONTIER_ERROR
            )
            self.assertEqual(dispatch["status"], "REJECTED_OR_UNAVAILABLE")
            self.assertTrue(dispatch["provider_invoked"])
            self.assertFalse(dispatch["automatically_registered"])
            rejected_path = (
                root / "avenox-subagents" / "FRONTIER_SCOUT_REJECTED_V254.json"
            )
            self.assertTrue(rejected_path.is_file())

    def test_execute_round_dispatches_before_epoch_rollover(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.execute_round

        def exhausted(controller, round_number, preflight):
            raise MODULE.LabError(FRONTIER_ERROR)

        parent.execute_round = exhausted
        try:
            controller = self.controller()
            controller._v225_next_actor = "codex"
            controller.load_cache = valid_cache
            controller._run_frontier_scout = lambda *args: {
                "status": "UNTRUSTED_INBOX",
                "automatically_registered": False,
            }
            with tempfile.TemporaryDirectory() as td:
                controller.run_dir = Path(td)
                summary, found, score = controller.execute_round(1, {})
                self.assertFalse(found)
                self.assertIsNone(score)
                self.assertEqual(summary["stop_stage"], "S1_FRONTIER_EXHAUSTED")
                dispatch = summary["frontier_exhaustion"]["frontier_scout_dispatch"]
                self.assertEqual(dispatch["status"], "UNTRUSTED_INBOX_VALIDATED")
                self.assertTrue(summary["frontier_exhaustion"]["provider_invoked"])
                self.assertIn(
                    "controller registration review",
                    summary["frontier_exhaustion"]["next_action"],
                )
        finally:
            parent.execute_round = original

    def test_unknown_errors_still_fail_closed(self):
        controller = self.controller()
        controller.load_cache = valid_cache

        def unknown(*args):
            raise RuntimeError("unexpected frontier Scout integration failure")

        controller._run_frontier_scout = unknown
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError, "unexpected frontier Scout"):
                controller._v256_scout_on_frontier_exhaustion(
                    Path(td), 1, "codex", FRONTIER_ERROR
                )

    def test_runtime_contract_preserves_hard_safety(self):
        contract = MODULE.runtime_binding_contract()
        self.assertTrue(contract["controller_only_promotion"])
        self.assertFalse(contract["trading_actions"])
        self.assertFalse(contract["exchange_api_access"])
        self.assertTrue(contract["v256_scout_runs_on_global_frontier_exhaustion"])
        self.assertTrue(contract["v256_only_valid_cached_advisory_is_reused"])
        self.assertTrue(contract["v256_scout_never_auto_registers"])
        self.assertTrue(contract["v256_unknown_errors_fail_closed"])


if __name__ == "__main__":
    unittest.main()

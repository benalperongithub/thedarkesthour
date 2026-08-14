import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


CONTROLLER = Path(__file__).resolve().parents[1] / "strategy_lab_controller.py"
SPEC = importlib.util.spec_from_file_location("tdh_strategy_lab_v253_test", CONTROLLER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load v2.0.53 controller")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class V253AuditContractResilienceTests(unittest.TestCase):
    def test_invalid_audit_is_quarantined_and_rolls_epoch(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.execute_round

        def invalid_audit(controller, round_number, preflight):
            raise MODULE.LabError("invalid audit finding")

        parent.execute_round = invalid_audit
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            with tempfile.TemporaryDirectory() as td:
                controller.run_dir = Path(td)
                round_dir = Path(td) / "round-01"
                round_dir.mkdir(parents=True)
                raw = b'{"result":"audit with unsupported INFO severity"}\n'
                (round_dir / "claude.json").write_bytes(raw)

                summary, found, score = controller.execute_round(1, {})

                self.assertFalse(found)
                self.assertIsNone(score)
                self.assertEqual(summary["verdict"], "REVISE")
                self.assertEqual(summary["stop_stage"], "S1_AUDIT_OUTPUT_REJECTED")
                self.assertEqual(summary["surviving_candidates"], [])
                event_path = round_dir / "AUDIT_OUTPUT_QUARANTINE_V253.json"
                self.assertTrue(event_path.is_file())
                event = json.loads(event_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    event["mode"],
                    "V253_INVALID_AUDIT_QUARANTINED_EPOCH_ROLLOVER",
                )
                self.assertEqual(event["approved_candidate_ids"], [])
                self.assertTrue(event["invalid_audit_never_promoted"])
                self.assertFalse(event["s2_s4_opened"])
                self.assertEqual(
                    event["raw_provider_log_sha256"],
                    hashlib.sha256(raw).hexdigest(),
                )
        finally:
            parent.execute_round = original

    def test_unknown_errors_remain_fail_closed(self):
        parent = MODULE.Controller.__mro__[1]
        original = parent.execute_round

        def unknown(controller, round_number, preflight):
            raise MODULE.LabError("unexpected provider or data failure")

        parent.execute_round = unknown
        try:
            controller = MODULE.Controller.__new__(MODULE.Controller)
            with tempfile.TemporaryDirectory() as td:
                controller.run_dir = Path(td)
                with self.assertRaisesRegex(MODULE.LabError, "unexpected provider"):
                    controller.execute_round(1, {})
        finally:
            parent.execute_round = original

    def test_runtime_contract_preserves_hard_safety(self):
        contract = MODULE.runtime_binding_contract()
        self.assertIs(contract["controller_only_promotion"], True)
        self.assertIs(contract["trading_actions"], False)
        self.assertIs(contract["exchange_api_access"], False)
        self.assertIs(contract["v253_invalid_audit_is_quarantined"], True)
        self.assertIs(contract["v253_invalid_audit_never_promotes"], True)
        self.assertIs(contract["v253_unknown_errors_fail_closed"], True)


if __name__ == "__main__":
    unittest.main()

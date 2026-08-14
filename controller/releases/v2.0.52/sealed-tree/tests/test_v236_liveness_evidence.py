from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v236_liveness_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def candidate(
    candidate_id: str,
    experiment_id: str,
    symbol: str,
    trades: int,
    max_dd: float,
    family: str = "FILTER_BREAKOUT",
    timeframe: str = "1h",
    persistence: int = 5,
):
    return {
        "candidate_id": candidate_id,
        "controller_verdict": "FAIL",
        "strategy_config": {
            "family": family,
            "symbol": symbol,
            "timeframe": timeframe,
            "experiment_id": experiment_id,
            "params": {
                "persistence_bars": persistence,
                "break_pct": 2.0,
                "recent_extreme_window": 5,
                "fixed_hold_bars": 5,
                "timeframe": timeframe,
            },
            "control_mode": "PERFORMANCE",
        },
        "metrics": {
            "expectancy_r": -0.15 if trades else 0.0,
            "profit_factor": 0.7 if trades else 0.0,
            "net_win_rate": 0.35 if trades else 0.0,
            "realized_payoff_ratio": 1.2 if trades else 0.0,
            "max_drawdown_pct": max_dd,
            "trade_count": trades,
            "weekday_trades": 1.2 if trades else 0.0,
        },
        "gates": {"baseline_beaten": False, "negative_control_beaten": False},
        "observations": ["NEGATIVE_EXPECTANCY"] if trades else ["NO_TRADES", "NO_SIGNAL"],
    }


class V236LivenessEvidenceTests(unittest.TestCase):
    def test_zero_trade_is_liveness_not_financial_source(self):
        module = load_controller()
        zero = candidate("codex-r01-c01", "TDH-LIT-ZERO", "BTCUSDT", 0, 0.0)
        good_sample = candidate("claude-r01-c01", "TDH-LIT-SAMPLE", "ETHUSDT", 120, 8.0)
        evidence = module.sanitize_financial_evidence({"candidates": [zero, good_sample]})
        self.assertEqual([row["candidate_id"] for row in evidence["candidates"]], ["claude-r01-c01"])
        self.assertEqual(evidence["financial_source_candidate_count"], 1)
        self.assertEqual(evidence["liveness_failures"][0]["candidate_id"], "codex-r01-c01")
        self.assertEqual(evidence["liveness_failures"][0]["sample_status"], "NO_SIGNAL")
        self.assertEqual(evidence["liveness_failures"][0]["financial_metrics_status"], "NOT_ESTIMABLE_NO_TRADES")
        self.assertTrue(evidence["financial_source_contract"]["zero_trade_is_not_negative_expectancy"])

    def test_legacy_additive_accounting_is_quarantined_but_signal_stats_are_kept_for_audit(self):
        module = load_controller()
        legacy = candidate("codex-old", "TDH-OLD", "BTCUSDT", 21000, 1165.0, family="VOLUME_TSMOM", timeframe="5m", persistence=1)
        evidence = module.sanitize_financial_evidence({"candidates": [legacy]})
        self.assertEqual(evidence["candidates"], [])
        self.assertEqual(len(evidence["legacy_accounting_quarantine"]), 1)
        row = evidence["legacy_accounting_quarantine"][0]
        self.assertEqual(row["evidence_class"], "LEGACY_ADDITIVE_ACCOUNTING")
        self.assertEqual(row["valid_signal_statistics"]["trade_count"], 21000)
        self.assertIn("max_drawdown_pct", row["invalid_accounting_fields"])
        self.assertIn("final_capital", row["invalid_accounting_fields"])

    def test_shared_context_separates_financial_liveness_and_legacy_rows(self):
        module = load_controller()
        valid = candidate("valid", "E0", "BTCUSDT", 50, 9.0)
        zero = candidate("zero", "E1", "ETHUSDT", 0, 0.0)
        legacy = candidate("legacy", "E2", "SOLUSDT", 500, 150.0)
        shared = module.sanitize_shared_context({"verified_s1": [valid, zero, legacy], "codex_findings": []})
        self.assertEqual([x["candidate_id"] for x in shared["verified_s1"]], ["valid"])
        self.assertEqual(shared["liveness_failures"][0]["candidate_id"], "zero")
        self.assertEqual(shared["legacy_accounting_quarantine"][0]["candidate_id"], "legacy")
        self.assertTrue(shared["evidence_interpretation_contract"]["zero_trade_may_not_be_financial_source"])

    def test_two_independent_zero_panels_quarantine_shared_structural_signature(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
            for run_index, experiment_id in enumerate(("ZERO-A", "ZERO-B"), start=1):
                path = root / "runs" / f"run-{run_index}" / "round-01" / "S1_FINANCIAL_EVIDENCE.json"
                path.parent.mkdir(parents=True)
                rows = [candidate(f"c-{run_index}-{i}", experiment_id, symbol, 0, 0.0) for i, symbol in enumerate(symbols)]
                path.write_text(json.dumps({"candidates": rows}), encoding="utf-8")
            signatures = module.historical_structural_inert_signatures(root)
            expected = ("FILTER_BREAKOUT", "1h", "persistence_bars", 5)
            self.assertIn(expected, signatures)
            frontier = [
                {"config": candidate("x", "NEW-DEAD", "BTCUSDT", 0, 0.0)["strategy_config"]},
                {"config": {
                    "family": "MA_TREND", "symbol": "BTCUSDT", "timeframe": "1h",
                    "experiment_id": "LIVE", "params": {"fast": 12, "slow": 48, "persistence_bars": 2, "threshold_pct": 0.05, "timeframe": "1h"},
                    "control_mode": "PERFORMANCE",
                }},
            ]
            filtered = module.filter_structural_quarantine(frontier, signatures)
            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0]["config"]["experiment_id"], "LIVE")

    def test_nonzero_panel_does_not_create_structural_quarantine(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "runs" / "run-1" / "round-01" / "S1_FINANCIAL_EVIDENCE.json"
            path.parent.mkdir(parents=True)
            rows = [
                candidate("a", "MIXED-A", "BTCUSDT", 0, 0.0),
                candidate("b", "MIXED-A", "ETHUSDT", 0, 0.0),
                candidate("c", "MIXED-A", "SOLUSDT", 3, 1.0),
            ]
            path.write_text(json.dumps({"candidates": rows}), encoding="utf-8")
            self.assertEqual(module.historical_structural_inert_signatures(root), set())

    def test_scalping_status_is_reconciled_from_executable_registry(self):
        module = load_controller()
        context = {
            "registered_candidate_contract": {
                "dual_lane_contract": {
                    "scalping_exploration": {
                        "status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS",
                        "target_fraction": 0.3,
                    }
                }
            }
        }
        value = module.reconcile_scalping_metadata(context)
        status = value["registered_candidate_contract"]["dual_lane_contract"]["scalping_exploration"]
        self.assertEqual(status["status"], "ACTIVE_EXECUTABLE_5M_15M")
        self.assertEqual(status["eligible_frontier_configs"], 8)
        self.assertEqual(set(status["eligible_families"]), {"FILTER_BREAKOUT", "MA_TREND", "SUPPORT_RES_BREAK", "VOLUME_TSMOM"})
        self.assertEqual(status["target_fraction"], 0.3)

    def test_authoritative_s1_gate_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)


if __name__ == "__main__":
    unittest.main()

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
    spec = importlib.util.spec_from_file_location("tdh_v233_zero_trade_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V233ZeroTradeSemanticsTests(unittest.TestCase):
    def test_zero_trade_is_no_signal_not_negative_expectancy(self):
        module = load_controller()
        raw = {
            "candidate_id": "codex-old-r01-c01",
            "controller_verdict": "FAIL",
            "metrics": {
                "trade_count": 0,
                "expectancy_r": 0.0,
                "net_win_rate": 0.0,
                "profit_factor": 0.0,
                "realized_payoff_ratio": 0.0,
                "max_drawdown_pct": 0.0,
            },
            "observations": [
                "NEGATIVE_EXPECTANCY",
                "WIN_RATE_BELOW_TARGET",
                "PAYOFF_BELOW_TARGET",
                "NO_BASELINE_EDGE",
                "NO_NEGATIVE_CONTROL_EDGE",
            ],
        }
        value = module.normalize_zero_trade_candidate(raw)
        self.assertEqual(value["controller_verdict"], "FAIL")
        self.assertEqual(value["sample_status"], "NO_SIGNAL")
        self.assertEqual(value["financial_metrics_status"], "NOT_ESTIMABLE_NO_TRADES")
        self.assertIn("NO_TRADES", value["observations"])
        self.assertIn("NO_SIGNAL", value["observations"])
        self.assertIn("INSUFFICIENT_SAMPLE", value["observations"])
        self.assertIn("FREQUENCY_BELOW_TARGET", value["observations"])
        self.assertNotIn("NEGATIVE_EXPECTANCY", value["observations"])
        self.assertNotIn("NO_BASELINE_EDGE", value["observations"])
        self.assertNotIn("NO_NEGATIVE_CONTROL_EDGE", value["observations"])

    def test_measured_negative_candidate_is_not_relabelled(self):
        module = load_controller()
        raw = {
            "metrics": {"trade_count": 40, "expectancy_r": -0.2},
            "observations": ["NEGATIVE_EXPECTANCY", "WIN_RATE_BELOW_TARGET"],
        }
        value = module.normalize_zero_trade_candidate(raw)
        self.assertEqual(value, raw)

    def test_three_symbol_zero_trade_panel_marks_exact_seed_inert(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            round_dir = root / "runs" / "run-a" / "round-01"
            round_dir.mkdir(parents=True)
            candidates = []
            for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
                candidates.append({
                    "strategy_config": {
                        "experiment_id": "TDH-LIT-0330",
                        "family": "FILTER_BREAKOUT",
                        "symbol": symbol,
                    },
                    "metrics": {"trade_count": 0},
                })
            (round_dir / "S1_FINANCIAL_EVIDENCE.json").write_text(
                json.dumps({"candidates": candidates}), encoding="utf-8"
            )
            inert = module.historical_inert_experiment_ids(root)
            self.assertIn("TDH-LIT-0330", inert)

    def test_nonzero_symbol_prevents_inert_classification(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            round_dir = root / "runs" / "run-a" / "round-01"
            round_dir.mkdir(parents=True)
            counts = {"BTCUSDT": 0, "ETHUSDT": 0, "SOLUSDT": 1}
            rows = [
                {
                    "strategy_config": {
                        "experiment_id": "E1",
                        "family": "FILTER_BREAKOUT",
                        "symbol": symbol,
                    },
                    "metrics": {"trade_count": count},
                }
                for symbol, count in counts.items()
            ]
            (round_dir / "S1_FINANCIAL_EVIDENCE.json").write_text(
                json.dumps({"candidates": rows}), encoding="utf-8"
            )
            self.assertNotIn("E1", module.historical_inert_experiment_ids(root))

    def test_run_tag_makes_cross_epoch_identity_distinct_and_s1_gate_is_unchanged(self):
        module = load_controller()
        a = module.run_tag("tdh-strategy-lab-v2-20260812T235243Z")
        b = module.run_tag("tdh-strategy-lab-v2-20260813T000101Z")
        self.assertNotEqual(a, b)
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn('candidate["candidate_id"] = f"{actor}-{tag}-r{round_number:02d}-c{index:02d}"', source)
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()

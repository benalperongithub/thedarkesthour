from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"
ADAPTER = ROOT / "adapter" / "tdh_strategy_lab_research_adapter.py"
PHOENIX_PYTHON = Path("/srv/tdh-research/phoenix-venv/bin/python")


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v224_gate_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def integrity_gates():
    return {
        "no_leakage": True,
        "data_integrity": True,
        "accounting_reconciled": True,
        "execution_model_compliant": True,
        "single_position_compliant": True,
        "costs_included": True,
        "funding_included": True,
        "deterministic_rerun": True,
        "baseline_beaten": True,
        "negative_control_beaten": True,
    }


def strong_metrics(trade_count=60):
    return {
        "trade_count": trade_count,
        "net_win_rate": 0.55,
        "realized_payoff_ratio": 2.20,
        "max_drawdown_pct": 6.0,
        "expectancy_r": 0.15,
        "weekday_trades": 1.20,
        "profit_factor": 1.30,
        "simultaneous_positions_max": 1,
    }


def result_with(metrics, folds):
    return {
        "classification": "PERFORMANCE",
        "gates": integrity_gates(),
        "metrics": metrics,
        "fold_results": [
            {
                "metrics": fold,
                "gates": {
                    "baseline_beaten": True,
                    "negative_control_beaten": True,
                    "all_s1_gates": True,
                },
            }
            for fold in folds
        ],
    }


class V224GateConsistencyTests(unittest.TestCase):
    def test_c04_regression_is_fail_closed(self):
        module = load_controller()
        c04 = {
            "trade_count": 17,
            "net_win_rate": 0.50,
            "realized_payoff_ratio": 1.9351944216851396,
            "max_drawdown_pct": 2.059977866717233,
            "expectancy_r": 0.484684170380394,
            "weekday_trades": 0.015384615384615385,
            "profit_factor": 1.956915586097124,
            "simultaneous_positions_max": 1,
        }
        self.assertFalse(module.authoritative_s1_hard_target_pass(c04))
        self.assertEqual(
            module.authoritative_s1_verdict(result_with(c04, [c04, c04, c04, c04])),
            "FAIL",
        )
        controller = object.__new__(module.Controller)
        self.assertEqual(controller.compute_gate_verdict("S1", result_with(c04, [c04])), "FAIL")

    def test_pass_requires_aggregate_and_every_fold(self):
        module = load_controller()
        aggregate = strong_metrics(160)
        folds = [strong_metrics(40) for _ in range(4)]
        self.assertEqual(module.authoritative_s1_verdict(result_with(aggregate, folds)), "PASS")

        bad_fold = strong_metrics(40)
        bad_fold["weekday_trades"] = 0.50
        self.assertEqual(
            module.authoritative_s1_verdict(result_with(aggregate, folds[:3] + [bad_fold])),
            "FAIL",
        )

        no_controls = result_with(aggregate, folds)
        no_controls["gates"]["baseline_beaten"] = False
        self.assertEqual(module.authoritative_s1_verdict(no_controls), "FAIL")

    def test_adapter_imports_exact_controller_gate_function(self):
        script = textwrap.dedent(
            """
            import importlib.util
            import sys
            from pathlib import Path

            adapter_path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location("tdh_v224_adapter_gate_test", adapter_path)
            if spec is None or spec.loader is None:
                raise RuntimeError("adapter import failed")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            assert module.hard_target_pass is module.v224_contract.authoritative_s1_hard_target_pass
            assert module.v221.hard_target_pass is module.hard_target_pass

            c04 = {
                "trade_count": 17,
                "net_win_rate": 0.50,
                "realized_payoff_ratio": 1.9351944216851396,
                "max_drawdown_pct": 2.059977866717233,
                "expectancy_r": 0.484684170380394,
                "weekday_trades": 0.015384615384615385,
                "profit_factor": 1.956915586097124,
                "simultaneous_positions_max": 1,
            }
            good = {
                "trade_count": 60,
                "net_win_rate": 0.55,
                "realized_payoff_ratio": 2.2,
                "max_drawdown_pct": 6.0,
                "expectancy_r": 0.15,
                "weekday_trades": 1.2,
                "profit_factor": 1.3,
                "simultaneous_positions_max": 1,
            }
            assert module.hard_target_pass(c04) is False
            assert module.hard_target_pass(good) is True
            print("V224_SINGLE_S1_GATE_OK")
            """
        )
        completed = subprocess.run(
            [str(PHOENIX_PYTHON), "-c", script, str(ADAPTER)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn("V224_SINGLE_S1_GATE_OK", completed.stdout)

    def test_non_s1_stages_still_delegate_to_v223(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn('if stage == "S1":', source)
        self.assertIn("return super().compute_gate_verdict(stage, result)", source)
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        self.assertTrue(
            "v221.hard_target_pass = hard_target_pass" in adapter_source
            or "v2.0.38/adapter/tdh_strategy_lab_research_adapter.py" in adapter_source
        )


if __name__ == "__main__":
    unittest.main()

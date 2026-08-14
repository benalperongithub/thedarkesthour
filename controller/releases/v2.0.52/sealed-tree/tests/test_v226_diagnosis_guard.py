from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v226_diagnosis_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def failed_source():
    return {
        "candidate_id": "claude-r01-c01",
        "controller_verdict": "FAIL",
        "metrics": {
            "expectancy_r": -0.37122171348797084,
            "max_drawdown_pct": 3.712217134879714,
            "net_win_rate": 0.30,
            "profit_factor": 0.3196103471828117,
            "realized_payoff_ratio": 0.679112844978745,
            "trade_count": 38,
            "weekday_trades": 0.12307692307692308,
        },
        "gates": {
            "baseline_beaten": True,
            "negative_control_beaten": True,
        },
        "observations": [
            "NEGATIVE_EXPECTANCY",
            "WIN_RATE_BELOW_TARGET",
            "PAYOFF_BELOW_TARGET",
            "FREQUENCY_BELOW_TARGET",
        ],
    }


def proposal(diagnosis: str):
    return {
        "contract_version": "2.0.2",
        "research_round": 1,
        "verdict": "CONTINUE",
        "candidates": [
            {
                "candidate_id": "claude-r01-c02",
                "evidence_chain": {
                    "diagnosis": diagnosis,
                },
            }
        ],
    }


class V226DiagnosisGuardTests(unittest.TestCase):
    def test_real_v225_failure_is_canonicalized_before_validation(self):
        module = load_controller()
        source = failed_source()
        self.assertEqual(
            module.canonical_diagnosis_from_source(source),
            "NEGATIVE_EXPECTANCY",
        )
        normalized = module.canonicalize_proposal_diagnosis(
            proposal("PROMISING_BUT_UNCONFIRMED"), source
        )
        self.assertEqual(
            normalized["candidates"][0]["evidence_chain"]["diagnosis"],
            "NEGATIVE_EXPECTANCY",
        )

    def test_passed_source_may_remain_promising(self):
        module = load_controller()
        source = failed_source()
        source["controller_verdict"] = "PASS"
        source["observations"] = []
        source["metrics"] = {
            "expectancy_r": 0.15,
            "net_win_rate": 0.55,
            "realized_payoff_ratio": 2.2,
            "max_drawdown_pct": 6.0,
            "weekday_trades": 1.2,
            "profit_factor": 1.3,
            "trade_count": 60,
        }
        self.assertEqual(
            module.canonical_diagnosis_from_source(source),
            "PROMISING_BUT_UNCONFIRMED",
        )
        raw = proposal("PROMISING_BUT_UNCONFIRMED")
        self.assertEqual(module.canonicalize_proposal_diagnosis(raw, source), raw)

    def test_valid_non_promising_diagnosis_is_not_overwritten(self):
        module = load_controller()
        raw = proposal("LOW_WIN_RATE")
        normalized = module.canonicalize_proposal_diagnosis(raw, failed_source())
        self.assertEqual(
            normalized["candidates"][0]["evidence_chain"]["diagnosis"],
            "LOW_WIN_RATE",
        )

    def test_guard_does_not_weaken_v224_s1_contract(self):
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
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )

    def test_guard_is_applied_before_inherited_validate_proposal(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        normalize = source.index("normalized = canonicalize_proposal_diagnosis(raw, source)")
        inherited = source.index("return super().validate_proposal(normalized, round_number)")
        self.assertLess(normalize, inherited)
        self.assertIn('chain.get("diagnosis") == "PROMISING_BUT_UNCONFIRMED"', source)
        self.assertIn('source_verdict == "PASS"', source)


if __name__ == "__main__":
    unittest.main()

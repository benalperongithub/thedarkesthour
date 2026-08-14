from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v232_repair_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_candidate(target_source_config):
    return {
        "candidate_id": "claude-r01-c01",
        "controller_verdict": "FAIL",
        "strategy_config": target_source_config,
        "metrics": {
            "expectancy_r": -0.379,
            "profit_factor": 0.313,
            "net_win_rate": 0.20,
            "realized_payoff_ratio": 0.418,
            "max_drawdown_pct": 6.05,
            "trade_count": 39,
            "weekday_trades": 0.123,
        },
        "gates": {"baseline_beaten": True, "negative_control_beaten": False},
        "observations": [
            "NEGATIVE_EXPECTANCY",
            "WIN_RATE_BELOW_TARGET",
            "PAYOFF_BELOW_TARGET",
            "NO_NEGATIVE_CONTROL_EDGE",
        ],
    }


class V232RepairCanonicalizationTests(unittest.TestCase):
    def _registry_pair(self, module):
        base = module.v231.v230.v229.v228.v227.v226.v225.v224.v220.v217
        kernel = base.kernel
        _, experiments = kernel.registry()
        source_row = experiments["TDH-LIT-0292"]
        source = kernel.performance_config(source_row, "BTCUSDT")
        target_row = next(
            row for row in experiments.values()
            if row.get("family_id") == "VOL_REGIME_GATE"
            and row.get("effective_timeframe") == "1h"
            and "BTCUSDT" in row.get("universe", [])
        )
        target = kernel.performance_config(target_row, "BTCUSDT")
        return source, target

    def test_real_claude_repair_shape_is_recovered_from_frontier(self):
        module = load_controller()
        source_config, target = self._registry_pair(module)
        source = source_candidate(source_config)
        raw = {
            "contract_version": "2.0.2",
            "research_round": 1,
            "verdict": "CONTINUE",
            "candidates": [{
                "candidate_id": "claude-r01-c01",
                "hypothesis_id": "claude-r01-h01",
                "family": "VOL_REGIME_GATE",
                "config": {
                    "family": "VOL_REGIME_GATE",
                    "overrides": {},
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                },
                "evaluation_plan": {"plan_id": "wrong", "s1_trial_budget": 999},
                "evidence_chain": {
                    "diagnosis": "CONTROL_FAILURE",
                    "selected_approach": "CHANGE_STRATEGY_FAMILY",
                },
                "primary_change": {"component": "wrong"},
                "strategy_config_sha256": "model-owned-wrong-hash",
            }],
        }
        plan = {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget_per_candidate": 3,
        }
        value = module.canonicalize_repair_safe_fields(
            raw, 1, source, plan,
            [{"config": target, "selected_approach": "CHANGE_STRATEGY_FAMILY"}],
            "claude",
        )
        candidate = value["candidates"][0]
        self.assertEqual(candidate["config"], target)
        self.assertNotIn("overrides", candidate["config"])
        self.assertNotIn("strategy_config_sha256", candidate)
        self.assertEqual(candidate["family"], "VOL_REGIME_GATE")
        self.assertEqual(candidate["evaluation_plan"], {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget": 3,
        })
        self.assertEqual(candidate["evidence_chain"]["diagnosis"], "NEGATIVE_EXPECTANCY")
        self.assertEqual(candidate["evidence_chain"]["selected_approach"], "CHANGE_STRATEGY_FAMILY")
        self.assertEqual(candidate["primary_change"]["component"], "strategy_family")
        self.assertEqual(candidate["primary_change"]["from"], "TSMOM_RETURN_SIGN")
        self.assertEqual(candidate["primary_change"]["to"], "VOL_REGIME_GATE")

    def test_wrong_round_and_ids_are_forced_to_current_round(self):
        module = load_controller()
        source_config, target = self._registry_pair(module)
        source = source_candidate(source_config)
        raw = {
            "research_round": 2,
            "candidates": [{
                "candidate_id": "claude-r02-c01",
                "hypothesis_id": "claude-r02-h01",
                "config": target,
                "family": target["family"],
                "evidence_chain": {
                    "diagnosis": "GENESIS_HYPOTHESIS",
                    "selected_approach": "GENESIS_REGISTERED_HYPOTHESIS",
                },
            }],
        }
        plan = {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget_per_candidate": 3}
        value = module.canonicalize_repair_safe_fields(
            raw, 1, source, plan, [{"config": target}], "claude"
        )
        self.assertEqual(value["research_round"], 1)
        self.assertEqual(value["candidates"][0]["candidate_id"], "claude-r01-c01")
        self.assertEqual(value["candidates"][0]["hypothesis_id"], "claude-r01-h01")
        self.assertEqual(value["candidates"][0]["evidence_chain"]["diagnosis"], "NEGATIVE_EXPECTANCY")

    def test_complete_identity_overrides_model_authored_params(self):
        module = load_controller()
        source_config, target = self._registry_pair(module)
        source = source_candidate(source_config)
        supplied = dict(target)
        supplied["params"] = {"model": "invented"}
        supplied["overrides"] = {}
        raw = {
            "research_round": 1,
            "candidates": [{
                "candidate_id": "claude-r01-c01",
                "hypothesis_id": "claude-r01-h01",
                "config": supplied,
                "family": "WRONG",
                "evidence_chain": {"diagnosis": "LOW_WIN_RATE", "selected_approach": "CHANGE_SYMBOL"},
            }],
        }
        plan = {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget_per_candidate": 3}
        value = module.canonicalize_repair_safe_fields(
            raw, 1, source, plan, [{"config": target}], "claude"
        )
        self.assertEqual(value["candidates"][0]["config"], target)
        self.assertEqual(value["candidates"][0]["family"], target["family"])

    def test_ambiguous_or_unknown_partial_config_is_not_guessed(self):
        module = load_controller()
        source_config, target = self._registry_pair(module)
        source = source_candidate(source_config)
        unknown = {"family": "NOT_A_REGISTERED_FAMILY", "symbol": "BTCUSDT", "timeframe": "1h"}
        raw = {
            "research_round": 1,
            "candidates": [{
                "candidate_id": "claude-r01-c01",
                "hypothesis_id": "claude-r01-h01",
                "config": unknown,
                "evidence_chain": {"diagnosis": "LOW_WIN_RATE", "selected_approach": "CHANGE_SYMBOL"},
            }],
        }
        plan = {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget_per_candidate": 3}
        value = module.canonicalize_repair_safe_fields(
            raw, 1, source, plan, [{"config": target}], "claude"
        )
        self.assertEqual(value["candidates"][0]["config"], unknown)

    def test_v224_s1_gate_identity_remains_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)


if __name__ == "__main__":
    unittest.main()

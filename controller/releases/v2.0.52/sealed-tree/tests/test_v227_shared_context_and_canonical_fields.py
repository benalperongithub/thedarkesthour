from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v227_compact_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_shared():
    long_claim = "C" * 1400
    long_evidence = "E" * 1800
    verified = []
    for i in range(12):
        verified.append({
            "candidate_id": f"claude-r01-c{i+1:02d}",
            "family": "TSMOM_RETURN_SIGN",
            "timeframe": "1d",
            "experiment_id": "TDH-LIT-0292",
            "config_sha256": str(i) * 64,
            "controller_verdict": "FAIL",
            "metrics": {
                "expectancy_r": -0.1 - i / 100,
                "profit_factor": 0.7,
                "net_win_rate": 0.3,
                "realized_payoff_ratio": 0.8,
                "max_drawdown_pct": 4.0,
                "trade_count": 40,
                "weekday_trades": 0.12,
                "net_return_pct": -2.0,
            },
            "gates": {
                "baseline_beaten": True,
                "negative_control_beaten": False,
                "no_leakage": True,
                "data_integrity": True,
            },
        })
    findings = [
        {"severity": "HIGH", "claim": long_claim, "evidence": long_evidence}
        for _ in range(6)
    ]
    return {
        "shared_context_version": "tdh-shared-research-context-v1",
        "source_run_id": "tdh-test",
        "source_round": 1,
        "context_sha256": "a" * 64,
        "codex_lane": {
            "candidate_count": 6,
            "families": ["MA_TREND"],
            "timeframes": ["4h"],
            "experiment_ids": ["A"],
            "config_hashes": ["x" * 64] * 6,
        },
        "claude_lane": {
            "candidate_count": 6,
            "families": ["TSMOM_RETURN_SIGN"],
            "timeframes": ["1d"],
            "experiment_ids": ["B"],
            "config_hashes": ["y" * 64] * 6,
        },
        "verified_s1": verified,
        "codex_findings": findings,
        "claude_findings": findings,
        "controller_synthesis": {
            "s1_pass_ids": [],
            "consensus_ids": [],
            "next_selection_rule": "N" * 1000,
        },
        "scalping_exploration": {
            "status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS",
            "eligible_frontier_configs": 0,
            "eligible_families": [],
            "one_minute_status": "BLOCKED_NOT_REGISTERED_OR_EXECUTABLE",
            "target_fraction": 0.3,
        },
    }


class V227CompactSharedAndCanonicalFieldsTests(unittest.TestCase):
    def test_shared_prompt_view_is_deterministic_and_under_3200_chars(self):
        module = load_controller()
        full = synthetic_shared()
        self.assertGreater(len(json.dumps(full)), 20000)
        first = module.compact_shared_context_for_prompt(full)
        second = module.compact_shared_context_for_prompt(full)
        self.assertEqual(first, second)
        encoded = json.dumps(first, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        self.assertLessEqual(len(encoded), module.SHARED_PROMPT_MAX_CHARS)
        self.assertEqual(first["full_context_sha256"], "a" * 64)
        self.assertLessEqual(len(first["verified_s1"]), 3)
        self.assertLessEqual(len(first["codex_findings"]), 1)
        self.assertLessEqual(len(first["claude_findings"]), 1)

    def test_controller_rebuilds_config_primary_change_and_plan_from_registry(self):
        module = load_controller()
        base = module.v226.v225.v224.v220.v217
        kernel = base.kernel
        _, experiments = kernel.registry()
        row = next(iter(experiments.values()))
        symbol = next(item for item in row["universe"] if item in kernel.REGISTERED_SYMBOLS)
        canonical = kernel.performance_config(row, symbol)
        source = {
            "strategy_config": canonical,
            "controller_verdict": "FAIL",
            "metrics": {"expectancy_r": -0.2},
            "observations": ["NEGATIVE_EXPECTANCY"],
        }
        target = next(
            item for item in experiments.values()
            if item["experiment_id"] != row["experiment_id"]
            and any(sym in kernel.REGISTERED_SYMBOLS for sym in item["universe"])
        )
        target_symbol = next(sym for sym in target["universe"] if sym in kernel.REGISTERED_SYMBOLS)
        expected = kernel.performance_config(target, target_symbol)
        raw = {
            "candidates": [{
                "candidate_id": "codex-r01-c01",
                "family": "WRONG_FAMILY",
                "config": {
                    "experiment_id": target["experiment_id"],
                    "symbol": target_symbol,
                    "family": "WRONG_FAMILY",
                    "timeframe": "WRONG",
                    "params": {"wrong": "types"},
                    "control_mode": "PERFORMANCE",
                    "overrides": {},
                },
                "primary_change": {
                    "component": "wrong", "from": "14", "to": "28",
                    "atomic_bundle": False, "rationale": "wrong",
                },
                "evaluation_plan": {"plan_id": "wrong", "s1_trial_budget": 999},
                "strategy_config_sha256": "wrong",
                "evidence_chain": {"selected_approach": "CHANGE_STRATEGY_FAMILY"},
            }]
        }
        plan = {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget_per_candidate": 3}
        normalized = module.canonicalize_machine_owned_fields(raw, source, plan)
        candidate = normalized["candidates"][0]
        self.assertEqual(candidate["config"], expected)
        self.assertEqual(candidate["family"], expected["family"])
        self.assertNotIn("overrides", candidate["config"])
        self.assertNotIn("strategy_config_sha256", candidate)
        self.assertEqual(candidate["evaluation_plan"], {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget": 3,
        })
        self.assertEqual(candidate["primary_change"]["component"], "strategy_family")
        self.assertEqual(candidate["primary_change"]["to"], expected["family"])

    def test_v226_diagnosis_guard_is_still_executed_before_machine_field_rebuild(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        method_start = source.index("    def validate_proposal(self, raw:")
        diagnosis = source.index("normalized = canonicalize_proposal_diagnosis(raw, source)", method_start)
        machine = source.index("normalized = canonicalize_machine_owned_fields(", diagnosis)
        inherited = source.index("return super().validate_proposal(normalized, round_number)", machine)
        self.assertLess(diagnosis, machine)
        self.assertLess(machine, inherited)

    def test_both_proposer_and_post_s1_paths_replace_full_shared_context(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn('prior["shared_research_context"] = compact_shared_context_for_prompt(', source)
        self.assertIn('batch["prior_shared_research_context"] = compact_shared_context_for_prompt(', source)
        self.assertIn("raw/full evidence remains on VPS", source)

    def test_s1_gate_identity_remains_v224(self):
        module = load_controller()
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()

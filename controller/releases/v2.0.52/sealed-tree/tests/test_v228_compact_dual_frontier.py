from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v228_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def perf(row, symbol=None):
    chosen = symbol or row["universe"][0]
    return {
        "family": row["family_id"],
        "symbol": chosen,
        "timeframe": row["effective_timeframe"],
        "experiment_id": row["experiment_id"],
        "params": dict(row.get("params", {})),
        "control_mode": "PERFORMANCE",
    }


def hash_fn(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class V228CompactDualFrontierTests(unittest.TestCase):
    def test_diverse_frontier_is_one_seed_per_family_and_peer_family_is_excluded(self):
        module = load_controller()
        families = {
            "A": {"family_id": "A", "evidence_score": 90, "research_priority": "high"},
            "B": {"family_id": "B", "evidence_score": 85, "research_priority": "high"},
            "C": {"family_id": "C", "evidence_score": 80, "research_priority": "medium"},
        }
        experiments = {
            "A1": {"experiment_id": "A1", "family_id": "A", "effective_timeframe": "4h", "universe": ["BTCUSDT"], "params": {"x": 1}},
            "A2": {"experiment_id": "A2", "family_id": "A", "effective_timeframe": "1h", "universe": ["BTCUSDT"], "params": {"x": 2}},
            "B1": {"experiment_id": "B1", "family_id": "B", "effective_timeframe": "15m", "universe": ["BTCUSDT"], "params": {"x": 3}},
            "C1": {"experiment_id": "C1", "family_id": "C", "effective_timeframe": "6h", "universe": ["BTCUSDT"], "params": {"x": 4}},
        }
        source = perf(experiments["A1"], "BTCUSDT")
        frontier = module.build_diverse_frontier(
            families, experiments, set(), set(), ["BTCUSDT"], hash_fn, perf,
            source_config=source, limit=5,
        )
        self.assertGreaterEqual(len(frontier), 2)
        family_ids = [item["config"]["family"] for item in frontier]
        self.assertEqual(len(family_ids), len(set(family_ids)))
        self.assertNotEqual(family_ids[0], "A")  # source family is deliberately deprioritized

        peer = module.build_diverse_frontier(
            families, experiments, set(), set(), ["BTCUSDT"], hash_fn, perf,
            source_config=source, excluded_family=family_ids[0], limit=5,
        )
        self.assertNotIn(family_ids[0], {item["config"]["family"] for item in peer})

    def test_real_registry_can_supply_multiple_distinct_executable_families(self):
        module = load_controller()
        base_v217 = module.v227.v226.v225.v224.v220.v217
        kernel = base_v217.kernel
        families, experiments = kernel.registry()
        frontier = module.build_diverse_frontier(
            families,
            experiments,
            set(),
            set(),
            kernel.REGISTERED_SYMBOLS,
            kernel.canonical_hash,
            kernel.performance_config,
            source_config=None,
            limit=5,
        )
        self.assertGreaterEqual(len(frontier), 2)
        ids = [item["config"]["family"] for item in frontier]
        self.assertEqual(len(ids), len(set(ids)))

    def test_model_packet_removes_repeated_memory_and_survives_v221_compactor(self):
        module = load_controller()
        config = {
            "family": "TSMOM_RETURN_SIGN",
            "symbol": "BTCUSDT",
            "timeframe": "1d",
            "experiment_id": "TDH-LIT-0292",
            "params": {"holding_bars": 10, "lookback_bars": 28, "timeframe": "1d", "vol_target_pct": 15},
            "control_mode": "PERFORMANCE",
        }
        huge_text = "same repeated research narrative " * 250
        shared = {
            "source_run_id": "run-prior",
            "source_round": 1,
            "context_sha256": "a" * 64,
            "codex_lane": {"candidate_count": 6, "families": ["A"], "timeframes": ["4h"], "experiment_ids": ["A1"]},
            "claude_lane": {"candidate_count": 6, "families": ["B"], "timeframes": ["1h"], "experiment_ids": ["B1"]},
            "verified_s1": [
                {"candidate_id": f"c{i}", "family": "A", "timeframe": "4h", "experiment_id": f"E{i}", "controller_verdict": "FAIL",
                 "metrics": {"expectancy_r": -0.1 * i, "net_win_rate": 0.3, "realized_payoff_ratio": 0.7, "trade_count": 40},
                 "gates": {"baseline_beaten": True, "negative_control_beaten": False}}
                for i in range(6)
            ],
            "codex_findings": [{"severity": "HIGH", "claim": huge_text, "evidence": huge_text}],
            "claude_findings": [{"severity": "HIGH", "claim": huge_text, "evidence": huge_text}],
            "controller_synthesis": {"s1_pass_ids": [], "consensus_ids": [], "next_selection_rule": huge_text},
            "scalping_exploration": {"status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS", "one_minute_status": "BLOCKED_NOT_REGISTERED_OR_EXECUTABLE", "eligible_families": []},
        }
        candidate = {
            "candidate_id": "c0",
            "controller_verdict": "FAIL",
            "strategy_config": config,
            "metrics": {"expectancy_r": -0.37, "profit_factor": 0.32, "net_win_rate": 0.3, "realized_payoff_ratio": 0.68, "max_drawdown_pct": 3.7, "trade_count": 38, "weekday_trades": 0.12},
            "gates": {"baseline_beaten": True, "negative_control_beaten": True},
            "observations": ["NEGATIVE_EXPECTANCY", "LOW_WIN_RATE", "PAYOFF_BELOW_TARGET"],
            "delta_vs_baseline": {"expectancy_r": 0.12, "profit_factor": 0.15, "net_win_rate": 0.1, "realized_payoff_ratio": 0.2},
            "delta_vs_negative_control": {"expectancy_r": 0.09, "profit_factor": 0.14, "net_win_rate": 0.03, "realized_payoff_ratio": 0.28},
        }
        raw = {
            "contract_version": "2.0.2",
            "data_class": "DEVELOPMENT_VALIDATION_ONLY",
            "task_id": "tdh-strategy-lab-v2",
            "round_id": "TDH-R02",
            "research_round": 1,
            "trial_count": 0,
            "objective": huge_text,
            "targets": {"net_win_rate": 0.5, "realized_payoff_ratio": 2.0, "max_drawdown_pct": 10.0, "weekday_trades": 1.0},
            "round_roles": {"proposer": "codex", "peer": "claude", "mode": "DUAL"},
            "frozen_experiment_plan": {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget_per_candidate": 3, "wfo_identity": {"windows": 4}},
            "proposal_evaluation_plan_exact_shape": {"plan_id": "candidate-baseline-negative-v1", "s1_trial_budget": 3},
            "latest_s1_financial_evidence": {
                "source_run_id": "run-1", "source_round": 1, "source_stage": "S1", "source_result_sha256": "b" * 64,
                "candidates": [candidate, candidate],
                "prior_dual_agent_synthesis": {"shared_research_context": shared},
                "interpretation_contract": {"s1_only_until_pass": True, "rule": huge_text},
                "additional_ranked_candidates_on_vps": 10,
            },
            "novelty_frontier": [
                {"config": {**config, "family": family, "experiment_id": f"E-{family}"}, "selected_approach": "CHANGE_STRATEGY_FAMILY", "sha256_prefix": family, "evidence_score": 80}
                for family in ["A", "B", "C", "D", "E"]
            ],
            "research_program_memory": {
                "completed_rounds": 208,
                "evaluated_s1_candidates": 744,
                "status_counts": {"PASS": 1, "FAIL": 743},
                "observation_counts": {"NEGATIVE_EXPECTANCY": 710, "WIN_RATE_BELOW_TARGET": 739},
                "unresolved_audit_findings": [{"finding_id": "audit-1", "severity": "HIGH", "claim": huge_text, "evidence": huge_text}],
            },
            "tdh_research_selection": {
                "registry_version": "tdh-registry-v1", "blocked_by_data_family_count": 37, "robust_state_sha256": "c" * 64,
                "family_cards": [{"family_id": family, "name": family, "bucket": "trend", "evidence_score": 80, "thesis": huge_text} for family in ["A", "B", "C", "D", "E"]],
            },
            "registered_candidate_contract": {
                "instruction": huge_text,
                "causal_contract": huge_text,
                "promotion_contract": "controller only",
                "financial_reasoning_contract": {"diagnoses": ["NEGATIVE_EXPECTANCY"], "approaches": ["CHANGE_STRATEGY_FAMILY"]},
                "dual_lane_contract": {"actor": "codex", "excluded_peer_family": None, "shared_peer_findings_are_binding_context": True,
                    "scalping_exploration": {"status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS", "target_fraction": 0.3}},
            },
            "global_research_memory": {"candidate_count": 873, "recent_candidate_configs": [{"x": huge_text} for _ in range(12)]},
            "previous_rounds": [{"verdict": "REVISE", "large": huge_text}],
        }
        compact = module.compact_model_context(raw)
        self.assertLessEqual(module._json_chars(compact), module.MODEL_CONTEXT_MAX_CHARS)
        final_context, _, report = module._compact_prompt_inputs("codex_proposal", compact)
        self.assertLessEqual(report["final_input_chars"], module.PROMPT_TARGET_MAX_CHARS)
        self.assertEqual(final_context["targets"], raw["targets"])
        self.assertNotIn("recent_candidate_configs", compact["global_research_memory"])

    def test_source_contains_actor_specific_rebuild_and_hard_distinct_family_contract(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        for marker in (
            "build_diverse_frontier",
            "excluded = getattr(self, \"_v225_codex_family\"",
            "available_distinct_families",
            "same_epoch_distinct_family_required",
            "MODEL_CONTEXT_MAX_CHARS = 9000",
            "machine_fields_are_controller_owned",
        ):
            self.assertIn(marker, source)

    def test_v224_s1_gate_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(
            module.authoritative_s1_hard_target_pass,
            module.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()

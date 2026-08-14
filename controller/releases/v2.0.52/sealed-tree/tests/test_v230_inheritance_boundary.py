from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v230_boundary_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_candidate():
    return {
        "candidate_id": "claude-r01-c01",
        "controller_verdict": "FAIL",
        "strategy_config": {
            "family": "TSMOM_RETURN_SIGN",
            "symbol": "BTCUSDT",
            "timeframe": "1d",
            "experiment_id": "TDH-LIT-0292",
            "params": {
                "holding_bars": 10,
                "lookback_bars": 28,
                "timeframe": "1d",
                "vol_target_pct": 15,
            },
            "control_mode": "PERFORMANCE",
        },
        "metrics": {
            "expectancy_r": -0.37938110819773685,
            "profit_factor": 0.31281480131332284,
            "net_win_rate": 0.2,
            "realized_payoff_ratio": 0.417548256446416,
            "max_drawdown_pct": 6.051742449427984,
            "trade_count": 39,
            "weekday_trades": 0.12307692307692308,
        },
        "gates": {
            "baseline_beaten": True,
            "negative_control_beaten": False,
        },
        "observations": [
            "NEGATIVE_EXPECTANCY",
            "WIN_RATE_BELOW_TARGET",
            "PAYOFF_BELOW_TARGET",
            "FREQUENCY_BELOW_TARGET",
            "NO_NEGATIVE_CONTROL_EDGE",
        ],
        "delta_vs_baseline": {
            "expectancy_r": 0.117,
            "profit_factor": 0.149,
        },
        "delta_vs_negative_control": {
            "expectancy_r": -0.0066,
            "profit_factor": 0.0033,
        },
    }


def raw_v227_context():
    src = source_candidate()
    shared = {
        "shared_context_version": "tdh-shared-research-context-v1",
        "source_run_id": "tdh-prior",
        "source_round": 1,
        "context_sha256": "b" * 64,
        "codex_lane": {
            "candidate_count": 1,
            "families": ["MA_TREND"],
            "timeframes": ["1h"],
            "experiment_ids": ["X"],
        },
        "claude_lane": {
            "candidate_count": 1,
            "families": ["TSMOM_RETURN_SIGN"],
            "timeframes": ["1d"],
            "experiment_ids": ["Y"],
        },
        "verified_s1": [{
            "candidate_id": "Y",
            "family": "TSMOM_RETURN_SIGN",
            "timeframe": "1d",
            "experiment_id": "TDH-LIT-0292",
            "controller_verdict": "FAIL",
            "metrics": {
                "expectancy_r": -0.2,
                "net_win_rate": 0.3,
                "realized_payoff_ratio": 0.7,
                "trade_count": 40,
            },
            "gates": {
                "baseline_beaten": True,
                "negative_control_beaten": False,
            },
        }],
        "codex_findings": [{
            "severity": "HIGH",
            "claim": "Codex peer finding survives boundary.",
            "evidence": "verified evidence",
        }],
        "claude_findings": [{
            "severity": "HIGH",
            "claim": "Claude peer finding survives boundary.",
            "evidence": "verified evidence",
        }],
        "controller_synthesis": {
            "s1_pass_ids": [],
            "consensus_ids": [],
            "next_selection_rule": "change strategy family",
        },
        "scalping_exploration": {
            "status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS",
            "one_minute_status": "BLOCKED_NOT_REGISTERED_OR_EXECUTABLE",
            "eligible_families": [],
            "target_fraction": 0.3,
        },
    }
    return {
        "contract_version": "2.0.2",
        "data_class": "DEVELOPMENT_VALIDATION_ONLY",
        "task_id": "tdh-strategy-lab-v2",
        "round_id": "TDH-R02",
        "research_round": 1,
        "trial_count": 0,
        "round_roles": {"proposer": "codex", "peer": "claude", "mode": "DUAL"},
        "targets": {
            "net_win_rate": 0.5,
            "realized_payoff_ratio": 2.0,
            "max_drawdown_pct": 10.0,
            "weekday_trades": 1.0,
        },
        "objective": "bounded offline dual-agent research",
        "frozen_experiment_plan": {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget_per_candidate": 3,
            "wfo_identity": {"windows": 4},
        },
        "proposal_evaluation_plan_exact_shape": {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget": 3,
        },
        "latest_s1_financial_evidence": {
            "source_run_id": "tdh-prior",
            "source_round": 1,
            "source_stage": "S1",
            "source_result_sha256": "a" * 64,
            "candidates": [src],
            "prior_dual_agent_synthesis": {
                "shared_research_context": shared,
            },
            "interpretation_contract": {
                "s1_only_until_pass": True,
                "no_flat_loop": True,
                "no_micro_tuning": True,
                "rule": "diagnose verified financial failure and make one causal change",
            },
            "additional_ranked_candidates_on_vps": 5,
        },
        "novelty_frontier": [{
            "config": {
                "family": "VOL_REGIME_GATE",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "experiment_id": "TDH-LIT-1364",
                "params": {
                    "high_vol_percentile": 80,
                    "high_vol_risk_mult": 0,
                    "normal_target_vol_pct": 15,
                    "vol_lookback": "168h",
                },
                "control_mode": "PERFORMANCE",
            },
            "selected_approach": "CHANGE_STRATEGY_FAMILY",
            "sha256_prefix": "abc",
            "evidence_score": 80,
        }],
        "research_program_memory": {
            "completed_rounds": 209,
            "evaluated_s1_candidates": 744,
            "status_counts": {"FAIL": 743, "PASS": 1},
            "observation_counts": {"NEGATIVE_EXPECTANCY": 710},
            "unresolved_audit_findings": [],
        },
        "tdh_research_selection": {
            "registry_version": "tdh-registry-v1",
            "blocked_by_data_family_count": 37,
            "robust_state_sha256": "c" * 64,
            "family_cards": [{
                "family_id": "VOL_REGIME_GATE",
                "name": "Volatility regime",
                "bucket": "risk_overlay",
                "evidence_score": 80,
            }],
        },
        "registered_candidate_contract": {
            "instruction": "choose one supplied frontier seed",
            "causal_contract": "one material change",
            "promotion_contract": "controller only",
            "financial_reasoning_contract": {
                "diagnoses": ["NEGATIVE_EXPECTANCY"],
                "approaches": ["CHANGE_STRATEGY_FAMILY"],
            },
            "dual_lane_contract": {
                "actor": "codex",
                "excluded_peer_family": None,
                "shared_peer_findings_are_binding_context": True,
                "scalping_exploration": {
                    "status": "BLOCKED_NO_EXECUTABLE_5M_15M_SEEDS",
                },
            },
        },
        "global_research_memory": {"candidate_count": 879},
        "previous_rounds": [],
    }


class V230InheritanceBoundaryTests(unittest.TestCase):
    def test_boundary_preserves_candidate_before_v221_compaction(self):
        module = load_controller()
        raw = raw_v227_context()
        compact = module.compact_model_context_from_raw_boundary(raw)
        evidence = compact["latest_s1_financial_evidence"]
        self.assertEqual(len(evidence["candidates"]), 1)
        self.assertEqual(evidence["candidates"][0]["candidate_id"], "claude-r01-c01")
        self.assertTrue(compact["model_context_contract"]["v227_boundary_preserved"])
        self.assertTrue(compact["model_context_contract"]["source_candidate_preserved_from_raw_context"])

    def test_boundary_preserves_shared_peer_memory(self):
        module = load_controller()
        compact = module.compact_model_context_from_raw_boundary(raw_v227_context())
        shared = compact["latest_s1_financial_evidence"]["prior_dual_agent_synthesis"]["shared_research_context"]
        self.assertEqual(shared["source_run_id"], "tdh-prior")
        self.assertTrue(shared["codex_findings"])
        self.assertTrue(shared["claude_findings"])
        self.assertTrue(compact["model_context_contract"]["shared_context_preserved_from_raw_context"])

    def test_candidate_and_shared_memory_survive_final_v221_compactor(self):
        module = load_controller()
        compact = module.compact_model_context_from_raw_boundary(raw_v227_context())
        self.assertLessEqual(module._json_chars(compact), module.MODEL_CONTEXT_MAX_CHARS)
        final_context, _, report = module._compact_prompt_inputs("codex_proposal", compact)
        self.assertLessEqual(report["final_input_chars"], module.PROMPT_TARGET_MAX_CHARS)
        evidence = final_context["latest_s1_financial_evidence"]
        self.assertTrue(evidence["candidates"])
        self.assertEqual(evidence["candidates"][0]["candidate_id"], "claude-r01-c01")
        shared = evidence["prior_dual_agent_synthesis"]["shared_research_context"]
        self.assertEqual(shared["source_run_id"], "tdh-prior")
        self.assertTrue(shared["codex_findings"])
        self.assertTrue(shared["claude_findings"])

    def test_runtime_reasoning_labels_remain_controller_owned(self):
        module = load_controller()
        src = source_candidate()
        raw = {"candidates": [{
            "config": {
                "family": "VOL_REGIME_GATE",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "experiment_id": "TDH-LIT-1364",
                "params": {
                    "high_vol_percentile": 80,
                    "high_vol_risk_mult": 0,
                    "normal_target_vol_pct": 15,
                    "vol_lookback": "168h",
                },
                "control_mode": "PERFORMANCE",
            },
            "evidence_chain": {
                "diagnosis": "GENESIS_HYPOTHESIS",
                "selected_approach": "GENESIS_REGISTERED_HYPOTHESIS",
            },
            "primary_change": {"component": "wrong"},
        }]}
        value = module.canonicalize_controller_owned_diagnosis(raw, src)
        value = module.canonicalize_controller_owned_reasoning_labels(value, src)
        candidate = value["candidates"][0]
        self.assertEqual(candidate["evidence_chain"]["diagnosis"], "NEGATIVE_EXPECTANCY")
        self.assertEqual(candidate["evidence_chain"]["selected_approach"], "CHANGE_STRATEGY_FAMILY")
        self.assertEqual(candidate["primary_change"]["component"], "strategy_family")

    def test_v224_s1_gate_identity_remains_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)


if __name__ == "__main__":
    unittest.main()

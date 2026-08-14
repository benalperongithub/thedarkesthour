from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "strategy_lab_controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("tdh_v238_positive_compaction_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def positive_memory():
    rows = []
    for index in range(4):
        rows.append({
            "positive_class": "PROMISING_POSITIVE",
            "experiment_id": f"TDH-LIT-POS-{index}",
            "family": "TSMOM_RETURN_SIGN",
            "symbol": "DOGEUSDT" if index % 2 == 0 else "SOLUSDT",
            "timeframe": "4h",
            "strategy_config_sha256": str(index) * 16,
            "params": {
                "lookback_bars": 7 + index,
                "holding_bars": 3,
                "timeframe": "4h",
            },
            "metrics": {
                "net_pnl": 1000.0 - index * 100,
                "net_return_pct": 5.0 - index * 0.5,
                "trade_count": 300 + index * 20,
                "net_win_rate": 0.45 + index * 0.01,
                "realized_payoff_ratio": 1.3,
                "max_drawdown_pct": 7.0,
                "expectancy_r": 0.05,
                "profit_factor": 1.2,
                "weekday_trades": 1.2,
            },
            "controller_verdict": "FAIL",
        })
    return {
        "memory_version": "tdh-positive-pnl-memory-v1",
        "verified_current_positive_count": 5,
        "legacy_positive_quarantined_count": 27,
        "top_verified_current_positives": rows,
        "interpretation_contract": {
            "positive_pnl_is_hypothesis_memory_not_promotion": True,
            "s1_gate_remains_authoritative": True,
            "legacy_positive_metrics_are_not_model_financial_evidence": True,
            "prefer_mechanism_contrasts_over_micro_tuning": True,
        },
    }


def proposal_context(module):
    memory = positive_memory()
    raw = {
        "contract_version": "2.0.2",
        "data_class": "DEVELOPMENT_VALIDATION_ONLY",
        "task_id": "tdh-strategy-lab-v2",
        "round_id": "TDH-R02",
        "research_round": 1,
        "trial_count": 0,
        "targets": {
            "net_win_rate": 0.50,
            "realized_payoff_ratio": 2.0,
            "max_drawdown_pct": 10.0,
        },
        "objective": "offline deterministic strategy research",
        "registered_candidate_contract": {
            "instruction": "Choose exactly one registered candidate.",
            "promotion_contract": "controller only",
        },
        "latest_s1_financial_evidence": {
            "source_run_id": "run-1",
            "source_round": 1,
            "source_stage": "S1",
            "source_result_sha256": "a" * 64,
            "candidates": [],
            "prior_dual_agent_synthesis": {
                "shared_research_context": {
                    "source_run_id": "run-1",
                    "codex_findings": [],
                    "claude_findings": [],
                }
            },
        },
        "novelty_frontier": [],
        "research_program_memory": {
            "completed_rounds": 200,
            "evaluated_s1_candidates": 900,
            "positive_pnl_memory": memory,
        },
        "previous_rounds": [],
    }
    return module.attach_positive_prompt_boundary(raw, memory)


class V238PositiveMemoryCompactionTests(unittest.TestCase):
    def test_prompt_memory_is_small_and_has_no_params(self):
        module = load_controller()
        compact = module.compact_positive_memory_for_prompt(positive_memory())
        self.assertLessEqual(module._json_chars(compact), module.POSITIVE_PROMPT_MEMORY_MAX_CHARS)
        self.assertLessEqual(len(compact["top_verified_current_positives"]), 2)
        self.assertTrue(compact["interpretation_contract"]["s1_gate_remains_authoritative"])
        for row in compact["top_verified_current_positives"]:
            self.assertNotIn("params", row)
            self.assertEqual(row["controller_verdict"], "FAIL")

    def test_both_proposer_paths_preserve_positive_memory_after_final_compaction(self):
        module = load_controller()
        context = proposal_context(module)
        for call_kind in ("codex_proposal", "claude_proposal"):
            compact_context, packet, report = module._compact_prompt_inputs(call_kind, context)
            self.assertIsNone(packet)
            self.assertLessEqual(report["final_input_chars"], module.PROMPT_TARGET_MAX_CHARS)
            memory = (
                compact_context["latest_s1_financial_evidence"]
                ["prior_dual_agent_synthesis"]
                ["shared_research_context"]
                ["positive_pnl_memory"]
            )
            self.assertEqual(memory["memory_version"], "tdh-positive-pnl-prompt-v1")
            self.assertEqual(memory["verified_current_positive_count"], 5)
            self.assertTrue(memory["interpretation_contract"]["positive_pnl_is_hypothesis_memory_not_promotion"])

    def test_both_post_s1_paths_preserve_positive_memory_in_controller_batch(self):
        module = load_controller()
        review_context = {
            "contract_version": "2.0.2",
            "research_round": 1,
            "policy": {
                "research_mode": "offline",
                "trading_actions": False,
                "exchange_api_access": False,
            },
            "hard_targets": {
                "net_win_rate_min": 0.5,
                "realized_reward_risk_min": 2.0,
                "max_drawdown_pct_max": 10.0,
            },
            "evidence_sha256": "b" * 64,
        }
        packet = module.attach_positive_analysis_memory({
            "contract_version": "2.0.2",
            "research_round": 1,
            "verdict": "CONTINUE",
            "candidates": [],
            "s1_evidence": [],
            "controller_batch": {"mode": "DUAL_AGENT_DISTINCT_FAMILY_UNION"},
        }, positive_memory())
        for call_kind in ("claude_post_s1", "codex_post_s1"):
            _, compact_packet, report = module._compact_prompt_inputs(
                call_kind, review_context, packet
            )
            self.assertLessEqual(report["final_input_chars"], module.PROMPT_TARGET_MAX_CHARS)
            self.assertIsNotNone(compact_packet)
            memory = compact_packet["controller_batch"]["positive_pnl_memory"]
            self.assertEqual(memory["memory_version"], "tdh-positive-pnl-prompt-v1")
            self.assertEqual(memory["legacy_positive_quarantined_count"], 27)
            self.assertTrue(memory["interpretation_contract"]["s1_gate_remains_authoritative"])

    def test_raw_program_memory_and_prompt_boundary_are_both_present(self):
        module = load_controller()
        memory = positive_memory()
        raw = module.attach_positive_research_memory(
            {"research_program_memory": {"completed_rounds": 1}}, memory
        )
        raw["latest_s1_financial_evidence"] = {
            "prior_dual_agent_synthesis": {"shared_research_context": {}}
        }
        bounded = module.attach_positive_prompt_boundary(raw, memory)
        self.assertEqual(
            bounded["research_program_memory"]["positive_pnl_memory"]["memory_version"],
            "tdh-positive-pnl-memory-v1",
        )
        self.assertEqual(
            bounded["latest_s1_financial_evidence"]["prior_dual_agent_synthesis"]
            ["shared_research_context"]["positive_pnl_memory"]["memory_version"],
            "tdh-positive-pnl-prompt-v1",
        )

    def test_authoritative_s1_gate_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)

    def test_source_states_no_promotion_and_no_live_path(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn("positive PnL remains hypothesis memory only", source)
        self.assertIn("No S1 target", source)
        self.assertIn("trading path", source)
        self.assertIn("controller_only_promotion", source)


if __name__ == "__main__":
    unittest.main()

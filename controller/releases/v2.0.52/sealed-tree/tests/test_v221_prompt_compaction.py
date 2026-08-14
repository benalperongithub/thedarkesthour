import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "strategy_lab_controller.py").read_text(encoding="utf-8")
SPEC = importlib.util.spec_from_file_location(
    "tdh_strategy_lab_v221_test", ROOT / "strategy_lab_controller.py"
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def _large_proposal_context():
    family_cards = []
    for index in range(6):
        family_cards.append({
            "family_id": f"FAMILY_{index}",
            "bucket": "trend",
            "evidence_score": 80 + index,
            "name": f"Family {index}",
            "thesis": "registered deterministic thesis " * 20,
            "main_failure_modes": ["x" * 2500, "y" * 2500],
        })
    return {
        "contract_version": "2.0.2",
        "data_class": "DEVELOPMENT_VALIDATION_ONLY",
        "task_id": "tdh-strategy-lab-v2",
        "round_id": "TDH-R02",
        "research_round": 1,
        "trial_count": 0,
        "objective": "offline deterministic research objective " * 300,
        "targets": {
            "net_win_rate": 0.50,
            "realized_payoff_ratio": 2.0,
            "max_drawdown_pct": 10.0,
        },
        "frozen_experiment_plan": {"plan_id": "candidate-baseline-negative-v1"},
        "proposal_evaluation_plan_exact_shape": {
            "plan_id": "candidate-baseline-negative-v1",
            "s1_trial_budget": 3,
        },
        "registered_candidate_contract": {
            "instruction": "Choose exactly one immutable novelty frontier config.",
            "registered_symbols": ["BTCUSDT", "ETHUSDT"],
            "registered_timeframes": ["15m", "4h"],
            "registered_families": ["DONCHIAN_VOL", "MA_TREND"],
            "promotion_contract": "controller only",
        },
        "dual_agent_contract": {"post_s1": "both agents analyze same evidence"},
        "round_roles": {"proposer": "codex", "peer": "claude", "mode": "DUAL"},
        "global_research_memory": {
            "candidate_count": 237,
            "recent_candidate_configs": [
                {"symbol": "BTCUSDT", "timeframe": "4h", "sha256_prefix": str(i)}
                for i in range(12)
            ],
            "validation_scope": "all historical proposal fingerprints are checked locally",
        },
        "latest_s1_financial_evidence": {
            "source_run_id": "run-1",
            "source_round": 1,
            "source_stage": "S1",
            "source_result_sha256": "a" * 64,
            "candidates": [{
                "candidate_id": "c1",
                "controller_verdict": "FAIL",
                "strategy_config": {
                    "family": "DONCHIAN_VOL",
                    "symbol": "BTCUSDT",
                    "timeframe": "4h",
                    "experiment_id": "TDH-LIT-0180",
                    "params": {"entry_lookback": 80},
                    "control_mode": "PERFORMANCE",
                },
                "metrics": {"expectancy_r": -0.2, "net_win_rate": 0.3},
                "gates": {"baseline_beaten": False},
                "observations": ["NEGATIVE_EXPECTANCY"],
                "delta_vs_baseline": {"expectancy_r": -0.1},
                "delta_vs_negative_control": {"expectancy_r": -0.2},
            }],
            "interpretation_contract": {"s1_only_until_pass": True},
        },
        "novelty_frontier": [{
            "config": {
                "family": "DONCHIAN_VOL",
                "symbol": symbol,
                "timeframe": "6h",
                "experiment_id": "TDH-LIT-0178",
                "params": {"entry_lookback": 80},
                "control_mode": "PERFORMANCE",
            },
            "selected_approach": "VALIDATE_PARAMETER_NEIGHBORHOOD",
            "sha256_prefix": str(index),
        } for index, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"])],
        "research_program_memory": {
            "completed_rounds": 117,
            "evaluated_s1_candidates": 126,
            "status_counts": {"PASS": 1, "FAIL": 125},
            "observation_counts": {"NEGATIVE_EXPECTANCY": 119},
            "unresolved_audit_findings": [{
                "finding_id": "audit-01",
                "severity": "HIGH",
                "claim": "claim " * 200,
                "evidence": "evidence " * 200,
            }],
        },
        "tdh_research_selection": {
            "registry_version": "tdh-registry-v1",
            "blocked_by_data_family_count": 37,
            "family_cards": family_cards,
        },
        "previous_rounds": [],
    }


class V221PromptCompactionTests(unittest.TestCase):
    def test_all_four_llm_paths_use_common_compactor(self):
        for marker in (
            '"codex_proposal", context',
            '"claude_proposal", context',
            '"claude_post_s1", review_context, analysis_packet',
            '"codex_post_s1", review_context, analysis_packet',
        ):
            self.assertIn(marker, SOURCE)
        self.assertIn("def _compact_prompt_inputs(", SOURCE)

    def test_second_compaction_reduces_oversized_proposal(self):
        context = _large_proposal_context()
        compact, packet, report = MOD._compact_prompt_inputs(
            "codex_proposal", context
        )
        self.assertIsNone(packet)
        self.assertEqual(report["compaction_level"], 2)
        self.assertGreater(report["level1_input_chars"], MOD.PROMPT_TARGET_MAX_CHARS)
        self.assertLessEqual(report["final_input_chars"], MOD.PROMPT_TARGET_MAX_CHARS)
        self.assertEqual(compact["targets"], context["targets"])
        self.assertEqual(
            compact["registered_candidate_contract"],
            context["registered_candidate_contract"],
        )
        self.assertTrue(compact["prompt_context_contract"]["raw_evidence_remains_on_vps"])

    def test_post_s1_preserves_metrics_control_deltas_and_config_hash(self):
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
        packet = {
            "contract_version": "2.0.2",
            "research_round": 1,
            "candidates": [{
                "candidate_id": "c1",
                "hypothesis_id": "h1",
                "family": "DONCHIAN_VOL",
                "config": {
                    "family": "DONCHIAN_VOL",
                    "symbol": "BTCUSDT",
                    "timeframe": "4h",
                    "experiment_id": "TDH-LIT-0180",
                },
                "primary_change": {"component": "strategy_family"},
            }],
            "s1_evidence": [{
                "candidate_id": "c1",
                "controller_verdict": "FAIL",
                "metrics": {"expectancy_r": -0.2},
                "gates": {"baseline_beaten": False},
                "observations": ["NEGATIVE_EXPECTANCY"],
                "delta_vs_baseline": {"expectancy_r": -0.1},
                "delta_vs_negative_control": {"expectancy_r": -0.2},
            }],
        }
        _, compact_packet, report = MOD._compact_prompt_inputs(
            "claude_post_s1", review_context, packet
        )
        self.assertLessEqual(report["final_input_chars"], MOD.PROMPT_TARGET_MAX_CHARS)
        self.assertIsNotNone(compact_packet)
        self.assertIn("config_sha256", compact_packet["candidates"][0])
        self.assertEqual(
            compact_packet["s1_evidence"][0]["delta_vs_baseline"],
            packet["s1_evidence"][0]["delta_vs_baseline"],
        )
        self.assertEqual(
            compact_packet["s1_evidence"][0]["delta_vs_negative_control"],
            packet["s1_evidence"][0]["delta_vs_negative_control"],
        )

    def test_target_and_absolute_ceiling_are_explicit(self):
        self.assertEqual(MOD.PROMPT_TARGET_MIN_CHARS, 10000)
        self.assertEqual(MOD.PROMPT_TARGET_MAX_CHARS, 12000)
        self.assertEqual(MOD.PROMPT_HARD_CEILING_CHARS, 16000)
        self.assertEqual(MOD.PROMPT_SAFETY_HEADROOM_CHARS, 256)

    def test_offline_and_controller_owned_contracts_remain_explicit(self):
        for text in (
            "raw_evidence_remains_on_vps",
            "full_duplicate_scan_remains_controller_owned",
            "controller_only_promotion",
            "metrics_and_control_deltas_preserved",
        ):
            self.assertIn(text, SOURCE)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTRL = ROOT / "strategy_lab_controller.py"


def load():
    spec = importlib.util.spec_from_file_location(
        "tdh_v242_preopt_test",
        CTRL,
    )
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def context():
    huge = [f"FAMILY_{i:04d}_" + "X" * 25 for i in range(500)]

    return {
        "contract_version": "2.0.2",
        "data_class": "DEVELOPMENT_VALIDATION_ONLY",
        "task_id": "tdh-strategy-lab-v2",
        "round_id": "TDH-R02",
        "research_round": 1,
        "trial_count": 0,
        "targets": {
            "net_win_rate": 0.5,
            "realized_payoff_ratio": 2.0,
            "max_drawdown_pct": 10.0,
        },
        "registered_candidate_contract": {
            "instruction":
                "Choose exactly one novelty_frontier config.",
            "promotion_contract": "controller only",
            "causal_contract": "C" * 600,
            "controller_owned_fields": [
                "config",
                "family",
                "primary_change",
            ],
            "dual_lane_contract": {
                "exact_config_duplicate_forbidden": True,
                "historical_config_duplicate_forbidden": True,
                "same_epoch_distinct_family_required": True,
                "scalping_exploration": {
                    "status": "ACTIVE_EXECUTABLE_5M_15M",
                    "eligible_families": huge,
                    "eligible_frontier_configs": 999,
                    "one_minute_status": "BLOCKED",
                    "target_fraction": 0.3,
                },
            },
        },
        "novelty_frontier": [{
            "config": {
                "control_mode": "PERFORMANCE",
                "experiment_id": "MK-C-5M-STRICT",
                "family": "MK_C_STR_LIQ_IMB",
                "params": {
                    "profile": "STRICT",
                    "timeframe": "5m",
                },
                "symbol": "BTCUSDT",
                "timeframe": "5m",
            },
            "selected_approach": "CHANGE_STRATEGY_FAMILY",
            "sha256_prefix": "abc123",
        }],
        "latest_s1_financial_evidence": {
            "source_run_id": "old-run",
            "source_round": 1,
            "source_stage": "S1",
            "source_result_sha256": "a" * 64,
            "candidates": [{
                "candidate_id": "old-c1",
                "controller_verdict": "FAIL",
                "strategy_config": {
                    "family": "TSMOM_RETURN_SIGN",
                    "symbol": "BTCUSDT",
                    "timeframe": "6h",
                    "experiment_id": "TDH-LIT-0298",
                    "params": {"lookback": 28},
                    "control_mode": "PERFORMANCE",
                },
                "metrics": {
                    "expectancy_r": -0.2,
                    "profit_factor": 0.7,
                    "net_win_rate": 0.3,
                    "realized_payoff_ratio": 1.1,
                    "max_drawdown_pct": 12,
                    "trade_count": 150,
                    "weekday_trades": 0.5,
                },
                "gates": {
                    "baseline_beaten": False,
                    "negative_control_beaten": False,
                },
                "observations": ["NEGATIVE_EXPECTANCY"],
            }],
        },
        "research_program_memory": {
            "completed_rounds": 250,
            "evaluated_s1_candidates": 1200,
            "status_counts": {"FAIL": 1199, "PASS": 1},
            "positive_pnl_memory": {
                "memory_version": "tdh-positive-pnl-memory-v1",
                "verified_current_positive_count": 7,
                "legacy_positive_quarantined_count": 27,
                "top_verified_current_positives": [],
                "interpretation_contract": {
                    "positive_pnl_is_hypothesis_memory_not_promotion": True,
                    "s1_gate_remains_authoritative": True,
                },
            },
        },
        "previous_rounds": [],
    }


class Tests(unittest.TestCase):
    def test_failure_class_is_preoptimized(self):
        m = load()
        raw = context()

        with self.assertRaises(m.LabError):
            m._compact_prompt_inputs(
                "codex_proposal",
                raw,
            )

        optimized, packet, report = (
            m.global_preoptimize_prompt_inputs(
                "codex_proposal",
                raw,
            )
        )

        self.assertIsNone(packet)
        self.assertIn(
            report["preoptimization_level"],
            (1, 2),
        )

        _, _, final = m._compact_prompt_inputs(
            "codex_proposal",
            optimized,
        )

        self.assertLessEqual(
            final["final_input_chars"],
            12000,
        )

        self.assertEqual(
            optimized["novelty_frontier"],
            raw["novelty_frontier"],
        )

        self.assertEqual(
            optimized[
                "latest_s1_financial_evidence"
            ]["candidates"],
            raw[
                "latest_s1_financial_evidence"
            ]["candidates"],
        )

        self.assertTrue(report["limits_unchanged"])

    def test_limits_and_s1_identity_unchanged(self):
        m = load()

        self.assertEqual(
            m.PROMPT_TARGET_MAX_CHARS,
            12000,
        )

        self.assertEqual(
            m.POST_S1_PRECHECK_HARD_LIMIT,
            10000,
        )

        self.assertEqual(
            m.PROMPT_HARD_CEILING_CHARS,
            16000,
        )

        self.assertIs(
            m.authoritative_s1_hard_target_pass,
            m.v224.authoritative_s1_hard_target_pass,
        )


if __name__ == "__main__":
    unittest.main()

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
    spec = importlib.util.spec_from_file_location("tdh_v237_positive_test", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError("controller import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_trial_run(
    root: Path,
    run_id: str,
    candidate_id: str,
    *,
    pnl: float,
    trades: int,
    basis: str,
    symbol: str = "DOGEUSDT",
    timeframe: str = "4h",
    family: str = "TSMOM_RETURN_SIGN",
    experiment_id: str = "TDH-LIT-POS",
    expectancy: float = 0.06,
    profit_factor: float = 1.2,
    max_dd: float = 7.0,
    status: str = "FAILED_GATE",
):
    run = root / "runs" / run_id
    artifact = run / "round-01" / "s1" / "experiments" / candidate_id
    artifact.mkdir(parents=True)
    config = {
        "family": family,
        "symbol": symbol,
        "timeframe": timeframe,
        "experiment_id": experiment_id,
        "params": {"lookback_bars": 7, "holding_bars": 3, "timeframe": timeframe},
        "control_mode": "PERFORMANCE",
    }
    (artifact / "effective_config.json").write_text(
        json.dumps({"registered_experiment_config": config}), encoding="utf-8"
    )
    trial = {
        "trial_id": f"trial-{run_id}-{candidate_id}",
        "candidate_id": candidate_id,
        "hypothesis_id": candidate_id.replace("c", "h", 1),
        "classification": "PERFORMANCE",
        "experiment_id": candidate_id,
        "artifact_path": str(artifact),
        "research_round": 1,
        "stage": "S1",
        "status": status,
        "finished_at_utc": "2026-08-13T10:00:00Z",
        "strategy_config_sha256": "a" * 64,
        "result_summary": {
            "accounting_basis": basis,
            "initial_capital": 20000.0,
            "final_capital": 20000.0 + pnl,
            "net_pnl": pnl,
            "net_return_pct": pnl / 200.0,
            "pnl_per_trade": pnl / trades if trades else 0.0,
            "trade_count": trades,
            "net_win_rate": 0.46,
            "realized_payoff_ratio": 1.35,
            "max_drawdown_pct": max_dd,
            "expectancy_r": expectancy,
            "profit_factor": profit_factor,
            "weekday_trades": 1.2,
            "simultaneous_positions_max": 1,
        },
    }
    (run / "TRIALS.jsonl").write_text(json.dumps(trial) + "\n", encoding="utf-8")
    evidence = {
        "source_run_id": run_id,
        "source_round": 1,
        "candidates": [{
            "candidate_id": candidate_id,
            "controller_verdict": "PASS" if status == "COMPLETED" else "FAIL",
            "strategy_config": config,
            "strategy_config_sha256": "a" * 64,
            "gates": {"baseline_beaten": True, "negative_control_beaten": True},
            "baseline_metrics": {"expectancy_r": -0.1},
            "negative_control_metrics": {"expectancy_r": -0.2},
            "fold_results": [{"fold_id": "W1", "metrics": {"expectancy_r": expectancy}}],
            "robust_aggregate": {"positive_expectancy_window_rate": 0.5},
            "observations": [],
        }],
    }
    (run / "round-01" / "S1_FINANCIAL_EVIDENCE.json").write_text(
        json.dumps(evidence), encoding="utf-8"
    )
    return run


class V237PositivePnlLedgerTests(unittest.TestCase):
    def test_current_positive_is_promising_and_preserves_s1_fail(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "tdh-strategy-lab-v2-20260813T100000Z"
            write_trial_run(
                root, run_id, "claude-20260813T100000Z-r01-c06",
                pnl=1070.57, trades=338, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            records = module.collect_positive_records(root)
            self.assertEqual(len(records), 1)
            row = records[0]
            self.assertEqual(row["positive_class"], "PROMISING_POSITIVE")
            self.assertTrue(row["positive_pnl"])
            self.assertFalse(row["s1_pass"])
            self.assertEqual(row["controller_verdict"], "FAIL")
            self.assertEqual(row["symbol"], "DOGEUSDT")
            self.assertEqual(row["timeframe"], "4h")
            self.assertTrue(row["contract"]["positive_pnl_is_not_s1_pass"])

    def test_negative_and_zero_trade_trials_are_not_recorded(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100001Z", "codex-a",
                pnl=-10.0, trades=100, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100002Z", "codex-b",
                pnl=10.0, trades=0, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            self.assertEqual(module.collect_positive_records(root), [])

    def test_legacy_positive_is_quarantined(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100003Z", "claude-old",
                pnl=1100.0, trades=338, basis="REFERENCE_CAPITAL_REPORTING_ONLY",
            )
            row = module.collect_positive_records(root)[0]
            self.assertEqual(row["positive_class"], "LEGACY_POSITIVE_QUARANTINED")
            self.assertFalse(row["accounting_evidence_valid"])
            self.assertTrue(row["contract"]["legacy_positive_is_quarantined"])

    def test_sync_is_idempotent_and_backfills_multiple_runs(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100004Z", "codex-one",
                pnl=100.0, trades=100, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100005Z", "claude-two",
                pnl=200.0, trades=120, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            first = module.sync_positive_pnl_ledger(root)
            second = module.sync_positive_pnl_ledger(root)
            self.assertEqual(first["appended_records"], 2)
            self.assertEqual(second["appended_records"], 0)
            self.assertEqual(second["total_records"], 2)
            ledger = module.load_positive_ledger(root / module.POSITIVE_LEDGER_REL)
            self.assertEqual(len(ledger), 2)
            self.assertEqual(len({row["record_id"] for row in ledger}), 2)

    def test_memory_uses_only_current_accounting_and_is_bounded(self):
        module = load_controller()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100006Z", "codex-current",
                pnl=500.0, trades=300, basis=module.CURRENT_ACCOUNTING_BASIS,
            )
            write_trial_run(
                root, "tdh-strategy-lab-v2-20260813T100007Z", "claude-legacy",
                pnl=1500.0, trades=300, basis="REFERENCE_CAPITAL_REPORTING_ONLY",
            )
            module.sync_positive_pnl_ledger(root)
            memory = module.positive_research_memory(root)
            self.assertEqual(memory["verified_current_positive_count"], 1)
            self.assertEqual(memory["legacy_positive_quarantined_count"], 1)
            self.assertEqual(len(memory["top_verified_current_positives"]), 1)
            self.assertEqual(memory["top_verified_current_positives"][0]["experiment_id"], "TDH-LIT-POS")
            self.assertLessEqual(module._json_chars(memory), module.POSITIVE_MEMORY_MAX_CHARS)
            self.assertTrue(memory["interpretation_contract"]["positive_pnl_is_hypothesis_memory_not_promotion"])

    def test_positive_memory_is_attached_under_research_program_memory(self):
        module = load_controller()
        memory = {
            "memory_version": "tdh-positive-pnl-memory-v1",
            "top_verified_current_positives": [],
            "interpretation_contract": {"s1_gate_remains_authoritative": True},
        }
        context = module.attach_positive_research_memory(
            {"research_program_memory": {"completed_rounds": 1}}, memory
        )
        self.assertEqual(
            context["research_program_memory"]["positive_pnl_memory"]["memory_version"],
            "tdh-positive-pnl-memory-v1",
        )

    def test_authoritative_s1_gate_identity_is_unchanged(self):
        module = load_controller()
        self.assertIs(module.authoritative_s1_hard_target_pass, module.v224.authoritative_s1_hard_target_pass)

    def test_source_keeps_controller_owned_guard_and_no_live_paths(self):
        source = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn("normalized = canonicalize_proposal_diagnosis(raw, source)", source)
        self.assertIn("return super().validate_proposal(normalized, round_number)", source)
        self.assertTrue(
            "positive_pnl_is_not_s1_pass" in source
            or "positive PnL remains hypothesis memory only" in source
        )
        self.assertTrue(
            "No live/paper/exchange path is added" in source
            or "No S1 target, Phoenix metric, trading path, paper path or exchange permission" in source
        )


if __name__ == "__main__":
    unittest.main()

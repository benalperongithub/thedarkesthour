#!/usr/bin/env python3
"""TDH Strategy Lab v2.0.17 offline agentic research controller.

This is a deliberately narrow extension of the sealed v2.0.16 controller.  It
keeps the immutable orchestration, safety, WFO, supervisor and audit machinery,
while replacing the Phoenix-only proposal surface with exact seeds from the TDH
evidence atlas and experiment registry.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
V216_PATH = Path("/srv/tdh-collab/controller/strategy-lab-v2/v2.0.16/strategy_lab_controller.py")
if not V216_PATH.is_file():
    local = HERE.parents[1] / "tdh-v216-testenv" / "strategy_lab_controller.py"
    if not local.is_file():
        local = HERE.parents[1] / "tdh-v216-vps-sweep-engine-rev3" / "payload" / "strategy_lab_controller.py"
    if local.is_file():
        V216_PATH = local
if not V216_PATH.is_file():
    legacy = HERE / "legacy_controller.py"
    if legacy.is_file():
        V216_PATH = legacy
if not V216_PATH.is_file():
    raise RuntimeError(f"sealed v2.0.16 controller missing: {V216_PATH}")

spec = importlib.util.spec_from_file_location("tdh_strategy_lab_v216", V216_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load sealed v2.0.16 controller")
v216 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v216
spec.loader.exec_module(v216)

RESEARCH_DIR = HERE / "research"
sys.path.insert(0, str(RESEARCH_DIR))
import research_kernel as kernel  # noqa: E402


CONTRACT_VERSION = v216.CONTRACT_VERSION
Config = v216.Config
LabError = v216.LabError
StrategyLabSupervisor = v216.StrategyLabSupervisor
atomic_json = v216.atomic_json
load_json = v216.load_json
sha256 = v216.sha256
hash_json = v216.hash_json

RESEARCH_CONFIG_CONTRACT = {
    "research_registry_version": "tdh-registry-v1",
    "research_state_max_chars": 16000,
    "one_primary_change": True,
    "controller_only_promotion": True,
    "data_integrity_preflight": True,
    "experiment_ledger_append_only": True,
    "strategy_panel_max_symbols": 10,
}


def validate_registered_config_shape(raw: Any) -> dict[str, Any]:
    try:
        # The sealed v2.0.2 Task parser re-validates its frozen historical
        # baseline/negative-control plan with the old Phoenix shape.  Keep that
        # narrow compatibility path; v2.0.17 proposal validation below still
        # requires the strict registry shape.
        return kernel.validate_config(raw, allow_legacy=True)
    except kernel.ResearchContractError as exc:
        raise LabError(str(exc)) from exc


# The inherited validator is called through both module namespaces.
v216.validate_registered_config_shape = validate_registered_config_shape
v216.base.validate_registered_config_shape = validate_registered_config_shape
v216.REGISTERED_SYMBOLS = kernel.REGISTERED_SYMBOLS
v216.REGISTERED_TIMEFRAMES = set(kernel.SUPPORTED_TIMEFRAMES)
v216.FINANCIAL_DIAGNOSES = kernel.DIAGNOSES
v216.RESEARCH_APPROACHES = kernel.APPROACHES
v216.DIAGNOSIS_OBSERVATIONS = dict(v216.DIAGNOSIS_OBSERVATIONS)
v216.DIAGNOSIS_OBSERVATIONS.update({
    "PAYOFF_FAMILY_CEILING": {"PAYOFF_BELOW_TARGET"},
    "SIGNAL_PRECISION_CEILING": {"WIN_RATE_BELOW_TARGET"},
    "RISK_REGIME_FAILURE": {"DRAWDOWN_ABOVE_TARGET"},
    "NO_INCREMENTAL_FAMILY_EDGE": {"NO_BASELINE_EDGE", "NO_NEGATIVE_CONTROL_EDGE"},
    "FRAGILE_REGIME_FIT": {"NEGATIVE_EXPECTANCY", "DRAWDOWN_ABOVE_TARGET"},
})


def _source_from_evidence(evidence: dict[str, Any]) -> dict[str, Any] | None:
    candidates = evidence.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return None
    for item in candidates:
        if isinstance(item, dict) and isinstance(item.get("strategy_config"), dict):
            return item
    return None


def _diagnosis(source: dict[str, Any] | None) -> str:
    if source is None:
        return "GENESIS_HYPOTHESIS"
    observations = set(source.get("observations", []))
    for observation, diagnosis in (
        ("NEGATIVE_EXPECTANCY", "NEGATIVE_EXPECTANCY"),
        ("NO_BASELINE_EDGE", "NO_INCREMENTAL_EDGE"),
        ("NO_NEGATIVE_CONTROL_EDGE", "CONTROL_FAILURE"),
        ("WIN_RATE_BELOW_TARGET", "LOW_WIN_RATE"),
        ("PAYOFF_BELOW_TARGET", "PAYOFF_COMPRESSION"),
        ("DRAWDOWN_ABOVE_TARGET", "EXCESS_DRAWDOWN"),
        ("FREQUENCY_BELOW_TARGET", "LOW_FREQUENCY"),
    ):
        if observation in observations:
            return diagnosis
    return "PROMISING_BUT_UNCONFIRMED"


def _primary_change(
    approach: str,
    source_config: dict[str, Any] | None,
    candidate_config: dict[str, Any],
) -> dict[str, Any]:
    if source_config is None:
        component = "registered_strategy_seed"
        old: Any = "GENESIS"
        new: Any = candidate_config["experiment_id"]
        atomic_bundle = True
    elif approach == "CHANGE_STRATEGY_FAMILY":
        component = "strategy_family"
        old, new, atomic_bundle = source_config.get("family"), candidate_config["family"], True
    elif approach == "CHANGE_SYMBOL":
        component = "symbol"
        old, new, atomic_bundle = source_config.get("symbol"), candidate_config["symbol"], False
    elif approach == "CHANGE_TIMEFRAME":
        component = "timeframe"
        old, new, atomic_bundle = source_config.get("timeframe"), candidate_config["timeframe"], False
    else:
        component = "registered_parameter_seed"
        old, new = source_config.get("experiment_id"), candidate_config["experiment_id"]
        atomic_bundle = True
    return {
        "component": component,
        "from": old,
        "to": new,
        "atomic_bundle": atomic_bundle,
        "rationale": "One pre-registered causal treatment is frozen before any result is observed.",
    }


PROMPT_EVIDENCE_CANDIDATE_LIMIT = 2
PROMPT_FRONTIER_LIMIT = 5


def _compact_candidate_evidence(raw: Any) -> dict[str, Any] | None:
    """Keep the causal contrast and hard-gate evidence, not readable repetition."""
    if not isinstance(raw, dict) or not isinstance(raw.get("strategy_config"), dict):
        return None
    metrics = raw.get("metrics") if isinstance(raw.get("metrics"), dict) else {}
    return {
        "candidate_id": raw.get("candidate_id"),
        "controller_verdict": raw.get("controller_verdict"),
        "strategy_config": raw["strategy_config"],
        "metrics": {
            key: metrics.get(key)
            for key in (
                "expectancy_r", "profit_factor", "net_win_rate",
                "realized_payoff_ratio", "max_drawdown_pct",
                "trade_count", "weekday_trades",
            )
        },
        "gates": raw.get("gates", {}),
        "observations": list(raw.get("observations", []))[:6]
        if isinstance(raw.get("observations"), list) else [],
        "delta_vs_baseline": raw.get("delta_vs_baseline", {}),
        "delta_vs_negative_control": raw.get("delta_vs_negative_control", {}),
    }


def summarize_financial_evidence(raw: Any) -> dict[str, Any]:
    """Build a deterministic bounded prompt packet while raw evidence stays on disk."""
    if not isinstance(raw, dict):
        return {}
    candidates = raw.get("candidates") if isinstance(raw.get("candidates"), list) else []
    compact_candidates = [
        value for value in (_compact_candidate_evidence(item) for item in candidates)
        if value is not None
    ][:PROMPT_EVIDENCE_CANDIDATE_LIMIT]
    batch = raw.get("batch_summary") if isinstance(raw.get("batch_summary"), dict) else {}
    return {
        "financial_evidence_version": raw.get("financial_evidence_version"),
        "source_run_id": raw.get("source_run_id"),
        "source_round": raw.get("source_round"),
        "source_stage": raw.get("source_stage"),
        "source_result_sha256": raw.get("source_result_sha256"),
        "batch_summary": {
            "performance_candidates": batch.get("performance_candidates"),
            "status_counts": batch.get("status_counts", {}),
            "observation_counts": batch.get("observation_counts", {}),
            "full_results_location": "hash-bound evidence on VPS",
        },
        "candidates": compact_candidates,
        "prompt_candidate_count": len(compact_candidates),
        "additional_ranked_candidates_on_vps": max(0, len(candidates) - len(compact_candidates)),
        "interpretation_contract": raw.get("interpretation_contract", {}),
    }


def summarize_novelty_frontier(raw: Any) -> list[dict[str, Any]]:
    """Expose only exact executable seeds and their causal transition."""
    if not isinstance(raw, list):
        return []
    result: list[dict[str, Any]] = []
    for item in raw[:PROMPT_FRONTIER_LIMIT]:
        if not isinstance(item, dict) or not isinstance(item.get("config"), dict):
            continue
        result.append({
            "config": item["config"],
            "selected_approach": item.get("selected_approach"),
            "sha256_prefix": item.get("sha256_prefix"),
        })
    return result


def summarize_program_memory(raw: Any) -> dict[str, Any]:
    """Retain verified aggregates and terse unresolved findings for the proposer."""
    if not isinstance(raw, dict):
        return {}
    findings = raw.get("unresolved_audit_findings")
    if not isinstance(findings, list):
        findings = []
    compact_findings = []
    for item in findings[:2]:
        if not isinstance(item, dict):
            continue
        compact_findings.append({
            "finding_id": item.get("finding_id"),
            "severity": item.get("severity"),
            "claim": str(item.get("claim", ""))[:180],
            "evidence": str(item.get("evidence", ""))[:180],
        })
    return {
        "memory_contract": "verified aggregates; raw evidence retained on VPS",
        "completed_rounds": int(raw.get("completed_rounds", 0)),
        "evaluated_s1_candidates": int(raw.get("evaluated_s1_candidates", 0)),
        "status_counts": raw.get("status_counts", {}),
        "observation_counts": raw.get("observation_counts", {}),
        "by_symbol": list(raw.get("by_symbol", []))[:2]
        if isinstance(raw.get("by_symbol"), list) else [],
        "by_timeframe": list(raw.get("by_timeframe", []))[:2]
        if isinstance(raw.get("by_timeframe"), list) else [],
        "by_research_approach": list(raw.get("by_research_approach", []))[:2]
        if isinstance(raw.get("by_research_approach"), list) else [],
        "recent_verified_results": list(raw.get("recent_verified_results", []))[-1:]
        if isinstance(raw.get("recent_verified_results"), list) else [],
        "unresolved_audit_findings": compact_findings,
        "full_duplicate_validation": "controller scans all historical hashes on disk",
    }


class Controller(v216.Controller):
    """Registry-bound v2.0.17 controller with deterministic robust memory."""

    def __init__(self, config_path: Path, task_path: Path, run_id: str | None = None):
        raw = load_json(config_path)
        for key, expected in RESEARCH_CONFIG_CONTRACT.items():
            if raw.get(key) != expected:
                raise LabError(f"v2.0.17 research config contract mismatch: {key}")
        super().__init__(config_path, task_path, run_id)

    def round_context(self, round_number: int) -> dict[str, Any]:
        context = super().round_context(round_number)
        evidence = self._latest_financial_evidence()
        source = _source_from_evidence(evidence)
        source_config = source.get("strategy_config") if source else None
        selection = kernel.select_context(self.config.root, source_config, limit=8)
        context["latest_s1_financial_evidence"] = summarize_financial_evidence(evidence)
        context["novelty_frontier"] = summarize_novelty_frontier(selection["novelty_frontier"])
        context["research_program_memory"] = summarize_program_memory(
            context.get("research_program_memory")
        )
        context["tdh_research_selection"] = {
            "registry_version": selection["registry_version"],
            "family_cards": selection["family_cards"],
            "blocked_by_data_family_count": selection["blocked_by_data_family_count"],
            "robust_state_sha256": selection["state_sha256"],
        }
        registered = context["registered_candidate_contract"]
        registered.clear()
        registered.update({
            "config_exact_shape": {
                "family": "one executable TDH registry family",
                "symbol": "one registered symbol",
                "timeframe": "exact registry effective timeframe",
                "experiment_id": "exact immutable registry seed",
                "params": "exact immutable registry params",
                "control_mode": "PERFORMANCE",
            },
            "registered_symbols": list(kernel.REGISTERED_SYMBOLS),
            "registered_timeframes": sorted(kernel.SUPPORTED_TIMEFRAMES),
            "registered_families": sorted(kernel.SUPPORTED_FAMILIES),
            "instruction": (
                "Choose exactly one novelty_frontier config. Do not modify a field. "
                "Candidate, baseline and negative control share symbol, timeframe and seed."
            ),
            "data_contract": (
                "Canonical Binance perpetual OHLCV only; deterministic integrity preflight "
                "must pass before any experiment. No network or exchange access."
            ),
            "causal_contract": (
                "One primary change per hypothesis. A registry seed may be an atomic structural "
                "bundle only when its fields are inseparable by design."
            ),
            "promotion_contract": "Only the deterministic controller may promote S1 to S2-S4.",
            "financial_reasoning_contract": {
                "diagnoses": sorted(kernel.DIAGNOSES),
                "approaches": sorted(kernel.APPROACHES),
            },
        })
        return context

    def proposal_output_example(self, round_number: int, actor: str) -> str:
        evidence = self._latest_financial_evidence()
        source = _source_from_evidence(evidence)
        source_config = source.get("strategy_config") if source else None
        selection = kernel.select_context(self.config.root, source_config, limit=8)
        if not selection["novelty_frontier"]:
            raise LabError("registered novelty frontier is exhausted")
        entry = selection["novelty_frontier"][0]
        config = entry["config"]
        approach = entry["selected_approach"]
        if source is None:
            identity = {
                "source_run_id": "GENESIS", "source_round": 0,
                "source_result_sha256": "GENESIS", "source_candidate_id": "NONE",
            }
        else:
            identity = {
                "source_run_id": evidence["source_run_id"],
                "source_round": evidence["source_round"],
                "source_result_sha256": evidence["source_result_sha256"],
                "source_candidate_id": source["candidate_id"],
            }
        chain = {
            **identity,
            "diagnosis": _diagnosis(source),
            "financial_interpretation": "Use only the cited verified S1 result and control deltas.",
            "selected_approach": approach,
            "causal_bridge": "The exact registered seed makes the proposed causal contrast reproducible.",
            "expected_metric_effect": {
                "primary_metric": "expectancy_r", "direction": "increase",
                "rationale": "A real edge must improve worst-fold expectancy while beating both controls.",
            },
            "discarded_alternatives": ["Unregistered tuning and live execution are outside the contract."],
            "why_not_parameter_tuning": "The controller admits only immutable registered seeds.",
        }
        value = {
            "contract_version": CONTRACT_VERSION,
            "research_round": round_number,
            "verdict": "CONTINUE",
            "candidates": [{
                "candidate_id": f"{actor}-r{round_number:02d}-c01",
                "hypothesis_id": f"{actor}-r{round_number:02d}-h01",
                "family": config["family"],
                "mechanism": "Test the exact registered causal mechanism against frozen controls.",
                "rules": {
                    "signal": "Use the exact registered signal with lagged inputs only.",
                    "entry": "Enter only on the next eligible bar.",
                    "exit": "Use deterministic stop and target handling with at least 2.0R target.",
                    "risk": "At most one position; fees, slippage and funding included.",
                },
                "config": config,
                "primary_change": _primary_change(approach, source_config, config),
                "evaluation_plan": {
                    "plan_id": self.task.experiment_plan["plan_id"],
                    "s1_trial_budget": self.task.experiment_plan["s1_trial_budget_per_candidate"],
                },
                "evidence_chain": chain,
                "falsification": "Reject on any S1 hard gate, control failure or fragile WFO fold.",
                "expected_success_regimes": ["stable directional or breakout regimes"],
                "expected_failure_regimes": ["chop, fee drag, unstable risk regimes"],
            }],
            "reasoning_packet": {
                "assumptions": [], "evidence": [], "counterevidence": [],
                "uncertainty": [], "decision_change_evidence": [],
            },
        }
        return json.dumps(value, sort_keys=True, ensure_ascii=False)

    def _validate_material_transition(
        self,
        approach: str,
        source_config: dict[str, Any],
        candidate_config: dict[str, Any],
    ) -> None:
        if source_config == candidate_config:
            raise LabError("evidence-directed candidate did not change the source config")
        if approach == "CHANGE_STRATEGY_FAMILY" and source_config.get("family") == candidate_config.get("family"):
            raise LabError("CHANGE_STRATEGY_FAMILY did not change family")
        if approach == "VALIDATE_PARAMETER_NEIGHBORHOOD":
            if source_config.get("family") != candidate_config.get("family"):
                raise LabError("parameter neighborhood changed family")
            if source_config.get("experiment_id") == candidate_config.get("experiment_id"):
                raise LabError("parameter neighborhood did not change registered seed")
        if approach == "CHANGE_SYMBOL":
            frozen = ("family", "timeframe", "experiment_id", "params")
            if candidate_config.get("symbol") == source_config.get("symbol") or any(
                candidate_config.get(key) != source_config.get(key) for key in frozen
            ):
                raise LabError("CHANGE_SYMBOL changed more than the symbol")
        if approach == "CHANGE_TIMEFRAME" and source_config.get("timeframe") == candidate_config.get("timeframe"):
            raise LabError("CHANGE_TIMEFRAME did not change timeframe")

    def validate_proposal(self, raw: dict[str, Any], round_number: int) -> dict[str, Any]:
        value = super().validate_proposal(raw, round_number)
        candidate = value["candidates"][0]
        try:
            candidate["config"] = kernel.validate_config(candidate["config"])
        except kernel.ResearchContractError as exc:
            raise LabError(str(exc)) from exc
        primary = candidate.get("primary_change")
        expected = {"component", "from", "to", "atomic_bundle", "rationale"}
        if not isinstance(primary, dict) or set(primary) != expected:
            raise LabError("candidate primary_change has invalid exact shape")
        if not isinstance(primary.get("atomic_bundle"), bool):
            raise LabError("candidate primary_change atomic_bundle must be boolean")
        v216.bounded_string("primary_change.component", primary.get("component"), 80)
        v216.bounded_string("primary_change.rationale", primary.get("rationale"), 600)
        source = _source_from_evidence(self._latest_financial_evidence())
        source_config = source.get("strategy_config") if source else None
        expected_primary = _primary_change(
            candidate["evidence_chain"]["selected_approach"], source_config, candidate["config"]
        )
        for key in ("component", "from", "to", "atomic_bundle"):
            if primary.get(key) != expected_primary[key]:
                raise LabError("candidate primary_change disagrees with config transition")
        return value

    def control_config(self, candidate: dict[str, Any], classification: str) -> dict[str, Any]:
        try:
            return kernel.control_config(candidate["config"], classification)
        except kernel.ResearchContractError as exc:
            raise LabError(str(exc)) from exc

    def expand_validated_proposal_batch(
        self, proposal: dict[str, Any], context: dict[str, Any], actor: str
    ) -> dict[str, Any]:
        candidates = proposal.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 1:
            return proposal
        anchor = candidates[0]
        config = anchor.get("config")
        if not isinstance(config, dict):
            return proposal
        _, experiments = kernel.registry()
        row = experiments.get(config["experiment_id"])
        if row is None:
            return proposal
        limit = min(self.vps_sweep.candidates_per_hypothesis, len(kernel.REGISTERED_SYMBOLS))
        historical = v216._historical_candidate_hashes(self.config.root)
        batch: list[dict[str, Any]] = []
        for symbol in row.get("universe", []):
            if symbol not in kernel.REGISTERED_SYMBOLS:
                continue
            variant_config = kernel.performance_config(row, symbol)
            digest = hash_json(variant_config)
            if digest in historical:
                continue
            variant = copy.deepcopy(anchor)
            index = len(batch) + 1
            variant["candidate_id"] = f"{actor}-r{context['research_round']:02d}-c{index:02d}"
            variant["hypothesis_id"] = f"{actor}-r{context['research_round']:02d}-h{index:02d}"
            variant["config"] = variant_config
            variant["strategy_config_sha256"] = digest
            batch.append(variant)
            if len(batch) >= limit:
                break
        if batch:
            proposal["candidates"] = batch
            proposal["controller_batch"] = {
                "mode": "ATOMIC_SYMBOL_ROBUSTNESS_PANEL",
                "candidate_count": len(batch),
                "llm_analysis_count": 1,
                "result_context_top_k": self.vps_sweep.result_top_k,
                "audit_shortlist_top_k": self.vps_sweep.audit_top_k,
                "raw_results_remain_on_vps": True,
            }
        return proposal

    def _financial_evidence_from_result(
        self, round_dir: Path, result: dict[str, Any], round_number: int, source_run_id: str
    ) -> dict[str, Any]:
        evidence = super()._financial_evidence_from_result(
            round_dir, result, round_number, source_run_id
        )
        rows = result.get("experiment_results", result.get("candidate_results", []))
        performance = {
            str(item.get("candidate_id")): item
            for item in rows if isinstance(item, dict) and item.get("classification") == "PERFORMANCE"
        } if isinstance(rows, list) else {}
        for candidate in evidence["candidates"]:
            raw = performance.get(str(candidate["candidate_id"]), {})
            candidate["strategy_config_sha256"] = hash_json(candidate["strategy_config"])
            candidate["fold_results"] = raw.get("fold_results", [])
            candidate["robust_aggregate"] = kernel.aggregate_candidate(candidate)
        evidence["robust_contract"] = {
            "all_wfo_folds_required": True,
            "targets": {"realized_rr_min": 2.0, "win_rate_min": 0.5, "max_drawdown_pct_max": 10.0},
            "controls": ["BASELINE", "NEGATIVE_CONTROL"],
        }
        return evidence

    def execute_round(
        self, round_number: int, preflight: dict[str, Any]
    ) -> tuple[dict[str, Any], bool, float | None]:
        outcome = super().execute_round(round_number, preflight)
        round_dir = self.run_dir / f"round-{round_number:02d}"
        evidence_path = round_dir / v216.FINANCIAL_EVIDENCE_FILENAME
        proposal_paths = [round_dir / "CODEX_PROPOSAL.json", round_dir / "CLAUDE_PROPOSAL.json"]
        proposal_path = next((path for path in proposal_paths if path.is_file()), None)
        if evidence_path.is_file() and proposal_path is not None:
            critique_path = next(iter(
                [path for path in (
                    round_dir / "CLAUDE_REVIEW_OF_CODEX.json",
                    round_dir / "CODEX_REVIEW_OF_CLAUDE.json",
                ) if path.is_file()]), None)
            kernel.persist_round_memory(
                self.config.root,
                self.run_id,
                round_number,
                load_json(proposal_path),
                load_json(evidence_path),
                load_json(critique_path) if critique_path else None,
            )
        return outcome


# The inherited supervisor resolves this module global at runtime.
v216.Controller = Controller


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TDH Strategy Lab Controller v2.0.17 + Supervisor v2.1.8")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--run-id")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--execute", action="store_true")
    action.add_argument("--monitor", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.monitor:
            config = Config.from_path(args.config)
            return v216._render_monitor(config.root, args.run_id)
        controller = Controller(args.config, args.task, args.run_id)
        if args.preflight:
            result = controller.preflight()
            settings = v216.SupervisorSettings.from_path(args.config)
            if settings.enabled:
                result["supervisor"] = {"version": settings.version, "status": "PREFLIGHT_OK"}
        else:
            settings = v216.SupervisorSettings.from_path(args.config)
            result = (
                StrategyLabSupervisor(args.config, args.task).run(args.run_id)
                if settings.enabled else controller.execute()
            )
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    except (LabError, kernel.ResearchContractError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

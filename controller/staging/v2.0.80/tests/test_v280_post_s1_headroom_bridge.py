from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'
PHOENIX_PYTHON = Path('/srv/tdh-research/phoenix-venv/bin/python')


def run_phoenix(
    script: str,
    *,
    stdin: str = '',
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(PHOENIX_PYTHON),
            '-c',
            textwrap.dedent(script),
            str(CONTROLLER),
        ],
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )


def runtime_packet() -> dict[str, object]:
    candidates = []
    evidence = []
    symbols = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT')
    for index, symbol in enumerate(symbols, 1):
        candidate_id = f'codex-runtime-r01-c{index:02d}'
        config = {
            'control_mode': 'PERFORMANCE',
            'experiment_id': (
                'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-4H'
            ),
            'family': 'VOLUME_TSMOM',
            'params': {
                'return_lookback': 40,
                'volume_rank_lookback': 60,
                'volume_percentile': 0.8,
                'target_r': 2.0,
                'max_hold_bars': 10,
            },
            'symbol': symbol,
            'timeframe': '4h',
        }
        candidates.append({
            'candidate_id': candidate_id,
            'hypothesis_id': f'codex-runtime-r01-h{index:02d}',
            'family': 'VOLUME_TSMOM',
            'config': config,
            'primary_change': {
                'component': 'universe',
                'from': ['BTCUSDT', 'XRPUSDT', 'SOLUSDT'],
                'to': list(symbols),
                'atomic_bundle': True,
                'rationale': 'R' * 1400,
            },
            'falsification': 'F' * 1200,
        })
        metrics = {
            'expectancy_r': -0.04 * index,
            'profit_factor': 0.95 - index / 20,
            'net_win_rate': 0.44 - index / 50,
            'realized_payoff_ratio': 1.10 + index / 40,
            'max_drawdown_pct': 7.0 + index / 3,
            'net_pnl': -300.0 * index,
            'net_return_pct': -1.5 * index,
            'trade_count': 170 - index,
            'weekday_trades': 0.6,
        }
        evidence.append({
            'candidate_id': candidate_id,
            'controller_verdict': 'FAIL',
            'failure_reasons': ['one or more robust hard gates failed'],
            'metrics': metrics,
            'gates': {
                'no_leakage': True,
                'data_integrity': True,
                'accounting_reconciled': True,
                'execution_model_compliant': True,
                'single_position_compliant': True,
                'costs_included': True,
                'funding_included': True,
                'deterministic_rerun': True,
                'baseline_beaten': index != 2,
                'negative_control_beaten': index != 3,
                'v279_s1_only': True,
                'v279_implementation': (
                    'V278_ID_BOUND_VTM40_VOLRANK60_P80_'
                    'CAUSAL_SHUFFLE100_V1'
                ),
            },
            'observations': [
                'NEGATIVE_EXPECTANCY',
                'WIN_RATE_BELOW_TARGET',
                'PAYOFF_BELOW_TARGET',
            ],
            'delta_vs_baseline': metrics,
            'delta_vs_negative_control': metrics,
            'fold_results': [
                {
                    'fold_id': 'W1',
                    'start_utc': '2024-04-01T00:00:00+00:00',
                    'end_utc': '2024-07-01T00:00:00+00:00',
                    'metrics': {**metrics, 'expectancy_r': 0.02},
                    'gates': {'all_s1_gates': False},
                },
                {
                    'fold_id': 'W3',
                    'start_utc': '2024-10-01T00:00:00+00:00',
                    'end_utc': '2025-01-01T00:00:00+00:00',
                    'metrics': {**metrics, 'expectancy_r': -0.2 - index / 10},
                    'gates': {
                        'all_s1_gates': False,
                        'baseline_beaten': False,
                        'negative_control_beaten': False,
                    },
                },
            ],
            'identity': {
                'experiment_id': candidate_id,
                'strategy_config_sha256': f'{index}' * 64,
                'partition_sha256': f'{index + 1}' * 64,
                'data_manifest_sha256': f'{index + 2}' * 64,
                'strategy_code_commit': 'dfbe6a1c10cf405b6f1fd5884d7e815b632668e9',
            },
        })
    return {
        'contract_version': '2.0.2',
        'research_round': 1,
        'verdict': 'CONTINUE',
        'candidates': candidates,
        's1_evidence': evidence,
        'controller_batch': {
            'mode': 'DUAL_AGENT_POST_S1_COMPACT',
            'candidate_count': 4,
            'full_s1_result_count': 12,
            'selection_uses_llm': False,
            'full_raw_evidence_remains_on_vps': True,
            'positive_pnl_memory': {
                'memory_version': 'tdh-positive-pnl-prompt-v1',
                'verified_current_positive_count': 7,
                'legacy_positive_quarantined_count': 27,
                'top_verified_current_positives': [],
                'interpretation_contract': {
                    'positive_pnl_is_hypothesis_memory_not_promotion': True,
                    's1_gate_remains_authoritative': True,
                },
            },
            'prior_shared_research_context': {
                'source_run_id': 'prior-run',
                'source_round': 9,
                'codex_findings': [
                    {'severity': 'HIGH', 'claim': 'C' * 1600},
                ],
                'claude_findings': [
                    {'severity': 'HIGH', 'claim': 'D' * 1600},
                ],
                'controller_synthesis': {
                    's1_pass_ids': [],
                    'consensus_ids': [],
                    'next_selection_rule': 'N' * 1400,
                },
                'verified_s1': [],
            },
        },
        'audit_instruction': 'A' * 4000,
    }


class V280PostS1HeadroomBridgeTests(unittest.TestCase):
    def test_exact_legacy_failure_uses_bounded_evidence_preserving_fallback(self):
        packet = runtime_packet()
        completed = run_phoenix(
            """
            import copy
            import importlib.util
            import json
            import sys

            path = sys.argv[1]
            spec = importlib.util.spec_from_file_location(
                'tdh_v280_headroom_test', path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            raw = json.loads(sys.stdin.read())
            before = copy.deepcopy(raw)

            original = module.V280_BASE_POST_S1_COMPACTOR
            def legacy_failure(_raw):
                raise module.LabError(
                    'v2.0.41 post-S1 precheck compaction '
                    'cannot preserve headroom: 7255'
                )
            module.V280_BASE_POST_S1_COMPACTOR = legacy_failure
            try:
                compact, report = module.compact_post_s1_precheck_packet(raw)
            finally:
                module.V280_BASE_POST_S1_COMPACTOR = original

            assert raw == before
            assert report['compaction_level'] == 3
            assert report['legacy_error'].endswith('7255')
            assert report['output_chars'] <= 6200
            assert report['provider_invoked_by_compactor'] is False
            assert module._v280_json_chars(compact) <= 6200
            assert len(compact['candidates']) == 4
            assert len(compact['s1_evidence']) == 4
            for source, bounded in zip(raw['candidates'], compact['candidates']):
                assert bounded['candidate_id'] == source['candidate_id']
                assert bounded['config'] == source['config']
            for source, bounded in zip(
                raw['s1_evidence'], compact['s1_evidence']
            ):
                for key in module._V280_METRIC_KEYS:
                    assert bounded['metrics'][key] == source['metrics'][key]
                assert bounded['provenance']['strategy_config_sha256'] == (
                    source['identity']['strategy_config_sha256']
                )
                for key, value in source['gates'].items():
                    if value is False:
                        assert bounded['gates'][key] is False
            counterexample = compact['strongest_counterexample']
            assert counterexample['candidate_id'] == 'codex-runtime-r01-c04'
            assert counterexample['fold_id'] == 'W3'
            assert counterexample['metrics']['expectancy_r'] < -0.59
            contract = compact['v280_headroom_contract']
            assert contract['raw_evidence_remains_on_vps'] is True
            assert 'all_current_configs' in contract['preserved']
            assert 'hard_metrics' in contract['preserved']
            assert 'failed_gates' in contract['preserved']
            assert 'strongest_counterexample' in contract['preserved']
            assert contract['policy']['research_mode'] == 'offline'
            assert contract['policy']['trading_actions'] is False
            assert contract['policy']['exchange_api_access'] is False
            assert getattr(
                module.V280_POST_S1_OWNER,
                'compact_post_s1_precheck_packet',
            ) is module.compact_post_s1_precheck_packet
            print('V280_POST_S1_HEADROOM_FALLBACK_OK')
            """,
            stdin=json.dumps(packet),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V280_POST_S1_HEADROOM_FALLBACK_OK', completed.stdout)

    def test_unknown_failure_and_hard_contract_remain_fail_closed(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys

            path = sys.argv[1]
            spec = importlib.util.spec_from_file_location(
                'tdh_v280_fail_closed_test', path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            original = module.V280_BASE_POST_S1_COMPACTOR
            def unknown(_raw):
                raise module.LabError('unexpected post-S1 failure')
            module.V280_BASE_POST_S1_COMPACTOR = unknown
            try:
                try:
                    module.compact_post_s1_precheck_packet({})
                except module.LabError as exc:
                    assert str(exc) == 'unexpected post-S1 failure'
                else:
                    raise AssertionError('unknown failure was swallowed')
            finally:
                module.V280_BASE_POST_S1_COMPACTOR = original

            contract = module.runtime_binding_contract()
            assert contract['v280_exact_legacy_error_only'] is True
            assert contract['v280_analysis_max_chars'] == 6200
            assert contract['v280_raw_evidence_remains_on_vps'] is True
            assert contract['v280_compactor_owner_bound'] is True
            assert contract['v280_provider_invoked_by_compactor'] is False
            assert contract['v280_s1_gates_unchanged'] is True
            assert contract['v280_unknown_errors_fail_closed'] is True
            assert contract['controller_only_promotion'] is True
            assert contract['trading_actions'] is False
            assert contract['exchange_api_access'] is False
            assert module.POST_S1_PRECHECK_HARD_LIMIT == 10000
            assert module.PROMPT_TARGET_MAX_CHARS == 12000
            assert module.PROMPT_HARD_CEILING_CHARS == 16000
            print('V280_POST_S1_FAIL_CLOSED_CONTRACT_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V280_POST_S1_FAIL_CLOSED_CONTRACT_OK', completed.stdout)


if __name__ == '__main__':
    unittest.main()

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


def runtime_fixture() -> dict[str, object]:
    stamp = '20260816T015618Z'
    proposal_rows = []
    prompt_evidence = []
    full_evidence = []
    for index, symbol in enumerate(('BTCUSDT', 'ETHUSDT'), 1):
        candidate_id = f'codex-{stamp}-r01-c{index:02d}'
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
        metrics = {
            'expectancy_r': -0.05 * index,
            'profit_factor': 0.9 - index / 20,
            'net_win_rate': 0.44 - index / 30,
            'realized_payoff_ratio': 1.1 + index / 20,
            'max_drawdown_pct': 7.0 + index,
            'net_pnl': -250.0 * index,
            'trade_count': 150 - index,
            'weekday_trades': 0.6,
        }
        gates = {
            'baseline_beaten': False,
            'negative_control_beaten': False,
            'v279_s1_only': True,
        }
        proposal_rows.append({
            'candidate_id': candidate_id,
            'hypothesis_id': f'codex-{stamp}-r01-h{index:02d}',
            'config': config,
            'primary_change': {
                'component': 'universe',
                'from': ['BTCUSDT', 'XRPUSDT', 'SOLUSDT'],
                'to': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT'],
                'atomic_bundle': True,
                'rationale': 'registered universe bridge',
            },
        })
        prompt_evidence.append({
            'candidate_id': candidate_id,
            'controller_verdict': 'FAIL',
            'strategy_config': config,
            'metrics': metrics,
            'gates': gates,
            'observations': [
                'NEGATIVE_EXPECTANCY',
                'WIN_RATE_BELOW_TARGET',
            ],
            'delta_vs_baseline': {'expectancy_r': -0.03},
            'delta_vs_negative_control': {'expectancy_r': -0.02},
        })
        full_evidence.append({
            'candidate_id': candidate_id,
            'controller_verdict': 'FAIL',
            'strategy_config': config,
            'metrics': metrics,
            'gates': gates,
            'fold_results': [
                {
                    'fold_id': 'W1',
                    'metrics': {**metrics, 'expectancy_r': 0.01},
                },
                {
                    'fold_id': 'W4',
                    'metrics': {
                        **metrics,
                        'expectancy_r': -0.25 - index / 10,
                    },
                },
            ],
        })
    return {
        'stamp': stamp,
        'packet': {
            'contract_version': '2.0.2',
            'research_round': 1,
            'verdict': 'CONTINUE',
            'candidates': proposal_rows,
            's1_evidence': prompt_evidence,
            'controller_batch': {
                'mode': 'DUAL_AGENT_POST_S1_COMPACT',
                'candidate_count': 2,
                'full_raw_evidence_remains_on_vps': True,
            },
        },
        'full_evidence': {
            'financial_evidence_version': 'tdh-s1-financial-evidence-v1',
            'source_run_id': f'tdh-strategy-lab-v2-{stamp}',
            'source_round': 1,
            'source_stage': 'S1',
            'source_result_sha256': 'a' * 64,
            'candidates': full_evidence,
        },
    }


class V281PostS1FoldCounterexampleBridgeTests(unittest.TestCase):
    def test_exact_current_run_artifact_supplies_hash_bound_worst_fold(self):
        completed = run_phoenix(
            """
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            path = sys.argv[1]
            spec = importlib.util.spec_from_file_location(
                'tdh_v281_runtime_artifact_test', path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            fixture = json.loads(sys.stdin.read())
            packet = fixture['packet']
            full = fixture['full_evidence']
            for row in full['candidates']:
                row['strategy_config_sha256'] = module._v280_hash_json(
                    row['strategy_config']
                )

            with tempfile.TemporaryDirectory() as temporary:
                module.V281_RUNS_ROOT = Path(temporary)
                evidence_path = (
                    module.V281_RUNS_ROOT
                    / full['source_run_id']
                    / 'round-01'
                    / module.V281_FINANCIAL_EVIDENCE_FILENAME
                )
                evidence_path.parent.mkdir(parents=True)
                evidence_path.write_text(
                    json.dumps(full, sort_keys=True), encoding='utf-8'
                )

                original = module.V280_BASE_POST_S1_COMPACTOR
                def legacy_failure(_raw):
                    raise module.LabError(
                        'v2.0.41 post-S1 precheck compaction '
                        'cannot preserve headroom: 7255'
                    )
                module.V280_BASE_POST_S1_COMPACTOR = legacy_failure
                try:
                    compact, report = module.compact_post_s1_precheck_packet(
                        packet
                    )
                finally:
                    module.V280_BASE_POST_S1_COMPACTOR = original

            assert report['compaction_level'] == 3
            assert report['output_chars'] <= 6200
            counterexample = compact['strongest_counterexample']
            assert counterexample['candidate_id'].endswith('c02')
            assert counterexample['fold_id'] == 'W4'
            assert counterexample['metrics']['expectancy_r'] < -0.44
            assert counterexample['evidence_source'] == (
                'immutable_s1_financial_evidence'
            )
            assert counterexample['source_result_sha256'] == 'a' * 64
            for source, bounded in zip(
                full['candidates'], compact['s1_evidence']
            ):
                assert bounded['provenance'][
                    'strategy_config_sha256'
                ] == source['strategy_config_sha256']
                assert bounded['metrics'] == module._v280_metrics(
                    source['metrics']
                )
                assert bounded['gates']['baseline_beaten'] is False
                assert bounded['gates']['negative_control_beaten'] is False
            print('V281_EXACT_RUNTIME_ARTIFACT_BRIDGE_OK')
            """,
            stdin=json.dumps(runtime_fixture()),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn(
            'V281_EXACT_RUNTIME_ARTIFACT_BRIDGE_OK', completed.stdout
        )

    def test_identity_config_and_result_hash_drift_fail_closed(self):
        completed = run_phoenix(
            """
            import copy
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            path = sys.argv[1]
            spec = importlib.util.spec_from_file_location(
                'tdh_v281_artifact_fail_closed_test', path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            fixture = json.loads(sys.stdin.read())

            def write_and_probe(full, packet):
                with tempfile.TemporaryDirectory() as temporary:
                    module.V281_RUNS_ROOT = Path(temporary)
                    evidence_path = (
                        module.V281_RUNS_ROOT
                        / full['source_run_id']
                        / 'round-01'
                        / module.V281_FINANCIAL_EVIDENCE_FILENAME
                    )
                    evidence_path.parent.mkdir(parents=True)
                    evidence_path.write_text(
                        json.dumps(full, sort_keys=True), encoding='utf-8'
                    )
                    candidates = [
                        module._v280_compact_candidate(row)
                        for row in packet['candidates']
                    ]
                    evidence = [
                        module._v280_compact_evidence(row)
                        for row in packet['s1_evidence']
                    ]
                    return module._v281_full_s1_counterexamples(
                        candidates, evidence
                    )

            valid = copy.deepcopy(fixture['full_evidence'])
            for row in valid['candidates']:
                row['strategy_config_sha256'] = module._v280_hash_json(
                    row['strategy_config']
                )

            spoofed_hash = copy.deepcopy(valid)
            spoofed_hash['source_result_sha256'] = 'spoofed'
            try:
                write_and_probe(spoofed_hash, fixture['packet'])
            except module.LabError as exc:
                assert str(exc) == (
                    'v2.0.81 immutable S1 result hash is invalid'
                )
            else:
                raise AssertionError('spoofed result hash was accepted')

            drifted_config = copy.deepcopy(valid)
            drifted_config['candidates'][0]['strategy_config']['symbol'] = (
                'XRPUSDT'
            )
            drifted_config['candidates'][0]['strategy_config_sha256'] = (
                module._v280_hash_json(
                    drifted_config['candidates'][0]['strategy_config']
                )
            )
            try:
                write_and_probe(drifted_config, fixture['packet'])
            except module.LabError as exc:
                assert str(exc) == (
                    'v2.0.81 prompt/full S1 strategy config drifted'
                )
            else:
                raise AssertionError('drifted strategy config was accepted')

            bad_packet = copy.deepcopy(fixture['packet'])
            bad_packet['candidates'][0]['candidate_id'] = 'invalid-candidate'
            bad_packet['s1_evidence'][0]['candidate_id'] = 'invalid-candidate'
            try:
                write_and_probe(valid, bad_packet)
            except module.LabError as exc:
                assert str(exc) == (
                    'v2.0.81 post-S1 candidate run identity is invalid'
                )
            else:
                raise AssertionError('invalid candidate identity was accepted')

            print('V281_ARTIFACT_IDENTITY_FAIL_CLOSED_OK')
            """,
            stdin=json.dumps(runtime_fixture()),
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn(
            'V281_ARTIFACT_IDENTITY_FAIL_CLOSED_OK', completed.stdout
        )

    def test_runtime_contract_preserves_offline_s1_boundary(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys

            path = sys.argv[1]
            spec = importlib.util.spec_from_file_location(
                'tdh_v281_contract_test', path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            contract = module.runtime_binding_contract()
            assert contract['v281_exact_runtime_artifact_lookup'] is True
            assert contract['v281_candidate_run_round_path_bound'] is True
            assert contract['v281_worst_fold_from_full_evidence'] is True
            assert contract['v281_source_result_hash_bound'] is True
            assert contract['v281_strategy_config_hash_bound'] is True
            assert contract['v281_raw_folds_remain_on_vps'] is True
            assert contract[
                'v281_provider_invoked_by_artifact_bridge'
            ] is False
            assert contract['v281_s1_gates_unchanged'] is True
            assert contract['v281_unknown_shapes_fail_closed'] is True
            assert contract['controller_only_promotion'] is True
            assert contract['trading_actions'] is False
            assert contract['exchange_api_access'] is False
            assert module.POST_S1_PRECHECK_HARD_LIMIT == 10000
            assert module.PROMPT_TARGET_MAX_CHARS == 12000
            assert module.PROMPT_HARD_CEILING_CHARS == 16000
            print('V281_OFFLINE_S1_CONTRACT_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V281_OFFLINE_S1_CONTRACT_OK', completed.stdout)


if __name__ == '__main__':
    unittest.main()

from __future__ import annotations

import contextlib
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'


def load_controller():
    spec = importlib.util.spec_from_file_location(
        'tdh_v282_legal_frontier_recovery_test', CONTROLLER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError('controller import failed')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_controller()


FAMILIES, EXPERIMENTS = MODULE.kernel.registry()


def config_for(experiment_id: str, symbol: str) -> dict:
    return MODULE.kernel.validate_config(
        MODULE.kernel.performance_config(EXPERIMENTS[experiment_id], symbol)
    )


class V282LegalFrontierRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = MODULE._v282_registry_rotation_pool()
        # A full scan reconstructs and validates every registered row, which
        # costs 20-40s against the production registry. Most cases here
        # exercise lane logic rather than registry breadth, so they run against
        # a representative slice: several families, several experiments each.
        # The cases that genuinely depend on the whole registry ask for it.
        by_family: dict[str, list[tuple[str, str]]] = {}
        for family, experiment_id in cls.pool:
            by_family.setdefault(family, []).append((family, experiment_id))
        bounded: list[tuple[str, str]] = []
        for family in sorted(by_family)[:4]:
            bounded.extend(by_family[family][:2])
        cls.bounded_pool = tuple(bounded)
        # The inherited source candidate is the exact four-coin daily seed that
        # runtime acceptance left in immutable S1 evidence.
        cls.source = config_for(
            'TDH-SCOUT-000001-VTM-VOL80-NODOGE-4COIN-1D', 'BTCUSDT'
        )

    def context(self, frontier=None, **extra):
        base = {
            'contract_version': '2.0.2',
            'task_id': 'tdh-strategy-lab-v2',
            'round_id': 'round-01',
            'research_round': 1,
            'trial_count': 0,
            'novelty_frontier': list(frontier or []),
            'previous_rounds': [],
            'negative_memory': [],
            'research_program_memory': {},
            'latest_s1_financial_evidence': {
                'candidates': [{
                    'strategy_config': copy.deepcopy(self.source),
                }],
            },
        }
        base.update(extra)
        return base

    def recover(
        self,
        context=None,
        actor='codex',
        historical=None,
        full_registry=False,
        **kwargs,
    ):
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(
                MODULE, '_v274_full_historical_candidate_hashes',
                return_value=set(historical or ()),
            ))
            if not full_registry:
                stack.enter_context(mock.patch.object(
                    MODULE, '_v282_registry_rotation_pool',
                    return_value=self.bounded_pool,
                ))
            return MODULE._v282_legal_frontier_recovery(
                context if context is not None else self.context(),
                actor,
                Path('/sealed/history'),
                **kwargs,
            )

    # 1. an eligible candidate produces a deterministic recovery selection
    def test_eligible_candidate_is_admitted_deterministically(self):
        updated = self.recover(full_registry=True)
        self.assertEqual(
            len(updated['novelty_frontier']),
            MODULE.V282_MAX_REGISTRY_ADMISSIONS,
        )
        event = updated['v282_legal_frontier_recovery']
        self.assertEqual(event['status'], MODULE.V282_STATUS_ADMITTED)
        self.assertEqual(
            event['next_action'], 'PROPOSE_ROTATED_REGISTERED_CANDIDATE'
        )
        # Independent oracle: with empty global memory the lane must land on
        # the first registry row in pool order that is neither already used by
        # the inherited source candidate nor gated out by its timeframe.
        used_ids, _ = MODULE._v254_used_identities(self.context())
        expected_family, expected_experiment = next(
            (family, experiment_id)
            for family, experiment_id in self.pool
            if experiment_id not in used_ids
            and MODULE._v282_experiment_timeframe(EXPERIMENTS[experiment_id])
            in MODULE.V282_ELIGIBLE_TIMEFRAMES
        )
        self.assertEqual(event['selected_family_id'], expected_family)
        self.assertEqual(event['selected_experiment_id'], expected_experiment)
        self.assertEqual(event['family_cursor'], expected_family)
        self.assertEqual(event['frontier_cursor'], expected_experiment)
        self.assertEqual(len(event['decision_sha256']), 64)
        self.assertTrue(event['selection_is_deterministic'])

    # 2. the admitted row is an exact registered seed, never an invention
    def test_admitted_row_is_exact_registered_kernel_seed(self):
        item = self.recover()['novelty_frontier'][0]
        self.assertTrue(MODULE._v282_exact_rotation_item(item))
        self.assertTrue(MODULE._v260_exact_controller_registered_seed(item))
        self.assertTrue(
            MODULE._v251_legal_frontier_item(self.source, item)
        )
        rotation = item['v282_registry_rotation']
        self.assertEqual(rotation['source'], 'SEALED_KERNEL_REGISTRY_ROTATION')
        self.assertFalse(rotation['model_generated_executable_code'])
        self.assertFalse(rotation['raw_proposal_executed'])
        self.assertFalse(rotation['trading_actions'])
        self.assertFalse(rotation['exchange_api_access'])
        self.assertTrue(rotation['s1_only'])

    # 3. rotation reaches the next eligible registered family
    def test_rotation_advances_to_next_eligible_family(self):
        first_family, _ = self.bounded_pool[0]
        historical = {
            MODULE._v254_canonical_hash(config_for(experiment_id, symbol))
            for family, experiment_id in self.bounded_pool
            if family == first_family
            for symbol in EXPERIMENTS[experiment_id]['universe']
        }
        event = self.recover(
            historical=historical
        )['v282_legal_frontier_recovery']
        self.assertEqual(event['status'], MODULE.V282_STATUS_ADMITTED)
        self.assertNotEqual(event['selected_family_id'], first_family)
        self.assertGreaterEqual(
            event['rejection_reason_distribution'][
                'DUPLICATE_IN_AUTHORITATIVE_GLOBAL_MEMORY'
            ],
            1,
        )

    # 4. a globally rejected candidate is never selected again
    def test_global_memory_duplicate_is_not_reselected(self):
        first = self.recover()['v282_legal_frontier_recovery']
        event = self.recover(
            historical={first['selected_config_sha256']}
        )['v282_legal_frontier_recovery']
        self.assertNotEqual(
            event['selected_config_sha256'], first['selected_config_sha256']
        )
        self.assertGreaterEqual(
            event['rejection_reason_distribution'][
                'DUPLICATE_IN_AUTHORITATIVE_GLOBAL_MEMORY'
            ],
            1,
        )

    # 5. negative memory, quarantine and duplicate identities stay excluded
    def test_negative_memory_identity_is_not_reselected(self):
        first = self.recover()['v282_legal_frontier_recovery']
        context = self.context()
        context['negative_memory'] = [
            {'experiment_id': first['selected_experiment_id']}
        ]
        event = self.recover(context)['v282_legal_frontier_recovery']
        self.assertNotEqual(
            event['selected_experiment_id'], first['selected_experiment_id']
        )
        self.assertGreaterEqual(
            event['rejection_reason_distribution'][
                'ALREADY_USED_EXPERIMENT_ID'
            ],
            1,
        )

    def test_round_context_duplicate_config_is_rejected(self):
        first = self.recover()['v282_legal_frontier_recovery']
        context = self.context()
        context['previous_rounds'] = [
            {'config_sha256': first['selected_config_sha256']}
        ]
        event = self.recover(context)['v282_legal_frontier_recovery']
        self.assertNotEqual(
            event['selected_config_sha256'], first['selected_config_sha256']
        )

    # 6. a registered row on an unsupported timeframe is eliminated
    def test_unsupported_timeframe_is_rejected_with_reason(self):
        target = self.bounded_pool[0][1]
        drifted = copy.deepcopy(EXPERIMENTS)
        drifted[target]['effective_timeframe'] = '3w'
        drifted[target].pop('timeframe', None)
        with mock.patch.object(
            MODULE.kernel, 'registry',
            return_value=(copy.deepcopy(FAMILIES), drifted),
        ):
            event = self.recover()['v282_legal_frontier_recovery']
        self.assertGreaterEqual(
            event['rejection_reason_distribution']['UNSUPPORTED_TIMEFRAME'], 1
        )
        self.assertNotEqual(event['selected_experiment_id'], target)

    def test_peer_lane_is_deliberately_recovered_too(self):
        # Unlike the inherited lanes this one is not codex-only. Both peer
        # lanes stall on the same exhausted queues, so both are recovered; the
        # accepted cost is a claude provider call that v2.0.81 did not make.
        codex = self.recover()['v282_legal_frontier_recovery']
        context = self.context()
        context['registered_candidate_contract'] = {
            'dual_lane_contract': {
                'excluded_peer_family': codex['selected_family_id'],
            },
        }
        updated = self.recover(context, actor='claude')
        event = updated['v282_legal_frontier_recovery']
        self.assertEqual(len(updated['novelty_frontier']), 1)
        self.assertEqual(event['status'], MODULE.V282_STATUS_ADMITTED)
        self.assertEqual(event['actor'], 'claude')
        self.assertNotEqual(
            event['selected_family_id'], codex['selected_family_id']
        )

    def test_excluded_peer_family_is_honoured(self):
        first_family = self.bounded_pool[0][0]
        context = self.context()
        context['registered_candidate_contract'] = {
            'dual_lane_contract': {'excluded_peer_family': first_family},
        }
        event = self.recover(
            context, actor='claude'
        )['v282_legal_frontier_recovery']
        self.assertNotEqual(event['selected_family_id'], first_family)
        self.assertEqual(event['excluded_peer_family'], first_family)
        self.assertGreaterEqual(
            event['rejection_reason_distribution']['EXCLUDED_PEER_FAMILY'], 1
        )

    # 7. the same state always produces the same decision after restart
    def test_same_state_produces_identical_decision(self):
        first = self.recover()['v282_legal_frontier_recovery']
        second = self.recover()['v282_legal_frontier_recovery']
        self.assertEqual(first['decision_sha256'], second['decision_sha256'])
        self.assertEqual(
            first['selected_config_sha256'], second['selected_config_sha256']
        )
        self.assertEqual(
            first['eligible_set_sha256'], second['eligible_set_sha256']
        )

    # 8. the next state never re-proposes the same candidate
    def test_next_state_never_reproposes_same_candidate(self):
        seen = set()
        historical = set()
        for _ in range(4):
            event = self.recover(
                historical=historical
            )['v282_legal_frontier_recovery']
            digest = event['selected_config_sha256']
            self.assertIsNotNone(digest)
            self.assertNotIn(digest, seen)
            seen.add(digest)
            historical.add(digest)

    # 9. eligible/rejected sets and provenance are hash bound
    def test_candidate_sets_and_provenance_are_hash_bound(self):
        event = self.recover()['v282_legal_frontier_recovery']
        for key in (
            'eligible_set_sha256',
            'rejected_set_sha256',
            'memory_snapshot_sha256',
            'decision_sha256',
        ):
            self.assertEqual(len(event[key]), 64, key)
        core = {
            key: value for key, value in event.items()
            if key != 'decision_sha256'
        }
        self.assertEqual(
            MODULE._v254_canonical_hash(core), event['decision_sha256']
        )
        self.assertEqual(
            set(event['rejection_reason_distribution']),
            set(MODULE.V282_REJECTION_REASONS),
        )
        self.assertEqual(
            sum(event['rejection_reason_distribution'].values()),
            event['rejected_count'],
        )

    def test_set_hash_is_order_independent(self):
        rows = [
            {'experiment_id': 'B', 'symbol': 'X', 'reason': 'R1'},
            {'experiment_id': 'A', 'symbol': 'Y', 'reason': 'R2'},
        ]
        keys = ('experiment_id', 'symbol', 'reason')
        self.assertEqual(
            MODULE._v282_set_hash(rows, keys),
            MODULE._v282_set_hash(list(reversed(rows)), keys),
        )

    def test_decision_chains_to_previous_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / 'round-01').mkdir()
            (run_dir / 'round-01' / MODULE.V282_RECOVERY_ARTIFACT_FILENAME
             ).write_text(
                json.dumps({'research_round': 1, 'decision_sha256': 'a' * 64}),
                encoding='utf-8',
            )
            self.assertEqual(
                MODULE._v282_previous_decision_hash(run_dir, 2), 'a' * 64
            )
            self.assertIsNone(
                MODULE._v282_previous_decision_hash(run_dir, 1)
            )

    def test_malformed_previous_decision_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / 'round-01').mkdir()
            (run_dir / 'round-01' / MODULE.V282_RECOVERY_ARTIFACT_FILENAME
             ).write_text('{"research_round": 1}', encoding='utf-8')
            with self.assertRaises(MODULE.LabError):
                MODULE._v282_previous_decision_hash(run_dir, 2)

    # 10. the recovery decision stays inside a bounded prompt budget
    def test_rejected_sample_is_bounded_and_marked(self):
        event = self.recover()['v282_legal_frontier_recovery']
        self.assertLessEqual(
            len(event['rejected_sample']), MODULE.V282_REJECTED_SAMPLE_LIMIT
        )
        self.assertEqual(
            event['rejected_sample_truncated'],
            event['rejected_count'] > MODULE.V282_REJECTED_SAMPLE_LIMIT,
        )
        # The frontier row handed to a provider carries no recovery audit.
        item = self.recover()['novelty_frontier'][0]
        self.assertEqual(
            set(item), {'config', 'v254_registration', 'v282_registry_rotation'}
        )

    # 11 / 12. offline safety and staged-research boundaries are unchanged
    def test_runtime_contract_preserves_offline_s1_boundary(self):
        contract = MODULE.runtime_binding_contract()
        self.assertEqual(
            contract['v282_legal_frontier_recovery_version'],
            MODULE.V282_LEGAL_FRONTIER_RECOVERY_VERSION,
        )
        self.assertTrue(contract['v282_registry_rotation_is_deterministic'])
        self.assertTrue(contract['v282_only_exact_registered_kernel_seeds'])
        self.assertTrue(contract['v282_registry_rotation_hash_bound'])
        self.assertTrue(contract['v282_single_material_axis_required'])
        self.assertTrue(contract['v282_authoritative_global_memory_checked'])
        self.assertTrue(
            contract['v282_negative_memory_and_quarantine_preserved']
        )
        self.assertTrue(contract['v282_duplicate_candidate_never_reproposed'])
        self.assertTrue(contract['v282_rejection_reasons_recorded'])
        self.assertTrue(
            contract['v282_eligible_and_rejected_sets_hash_bound']
        )
        self.assertTrue(
            contract['v282_decision_chained_to_previous_decision']
        )
        self.assertTrue(contract['v282_exhausted_registry_fails_closed'])
        self.assertTrue(contract['v282_peer_lane_rotation_enabled'])
        self.assertTrue(contract['v282_peer_lane_families_stay_disjoint'])
        self.assertEqual(
            contract['v282_max_registry_admissions'],
            MODULE.V282_MAX_REGISTRY_ADMISSIONS,
        )
        self.assertTrue(contract['v282_s1_only'])
        self.assertTrue(contract['v282_s1_gates_unchanged'])
        self.assertTrue(contract['v282_unknown_errors_fail_closed'])
        self.assertFalse(contract['v282_new_families_auto_registered'])
        self.assertFalse(contract['v282_model_generated_executable_code'])
        self.assertFalse(contract['v282_provider_invoked_by_recovery'])
        self.assertFalse(contract['v282_s2_s4_opened'])
        self.assertFalse(contract['policy_change'])
        self.assertFalse(contract['trading_actions'])
        self.assertFalse(contract['exchange_api_access'])

    # 13. an admitted row satisfies the S1 execution contract
    #
    # A real candidate/baseline/negative-control S1 run needs the sealed
    # adapter and installed OHLCV, so end-to-end execution is verified on the
    # VPS during staging. Offline this asserts the admitted row is exactly the
    # executable shape the S1 executor requires.
    def test_admitted_row_matches_s1_execution_contract(self):
        updated = self.recover(full_registry=True)
        event = updated['v282_legal_frontier_recovery']
        config = updated['novelty_frontier'][0]['config']
        experiment = EXPERIMENTS[event['selected_experiment_id']]
        self.assertIn(config['family'], FAMILIES)
        self.assertIn(config['symbol'], experiment['universe'])
        self.assertEqual(config['control_mode'], 'PERFORMANCE')
        self.assertIn(
            MODULE._v282_experiment_timeframe(experiment),
            MODULE.V282_ELIGIBLE_TIMEFRAMES,
        )
        # Re-validating an admitted row must not raise under the sealed schema.
        MODULE.kernel.validate_config(copy.deepcopy(config))
        self.assertEqual(
            MODULE._v254_canonical_hash(config),
            event['selected_config_sha256'],
        )

    # 14. a genuinely exhausted registry completes fail closed
    def test_exhausted_registry_fails_closed_with_reason_codes(self):
        bounded = self.bounded_pool[:3]
        historical = {
            MODULE._v254_canonical_hash(config_for(experiment_id, symbol))
            for _, experiment_id in bounded
            for symbol in EXPERIMENTS[experiment_id]['universe']
        }
        with mock.patch.object(
            MODULE, '_v282_registry_rotation_pool', return_value=bounded
        ):
            updated = self.recover(historical=historical, full_registry=True)
        event = updated['v282_legal_frontier_recovery']
        self.assertEqual(updated['novelty_frontier'], [])
        self.assertEqual(event['status'], MODULE.V282_STATUS_EXHAUSTED)
        self.assertEqual(
            event['next_action'], 'FAIL_CLOSED_CONTROLLER_REVIEW_REQUIRED'
        )
        self.assertEqual(event['eligible_count'], 0)
        self.assertIsNone(event['selected_experiment_id'])
        self.assertIsNone(event['selected_config_sha256'])
        self.assertGreater(event['rejected_count'], 0)
        self.assertEqual(len(event['rejected_set_sha256']), 64)
        self.assertFalse(event['provider_invoked_by_recovery'])

    def test_unknown_rejection_reason_fails_closed(self):
        with self.assertRaises(MODULE.LabError):
            MODULE._v282_reason_distribution([{'reason': 'MADE_UP_REASON'}])

    # guards: the lane never fires outside its exact state
    def test_non_empty_frontier_and_missing_source_are_unchanged(self):
        occupied = self.context([{'config': copy.deepcopy(self.source)}])
        self.assertEqual(self.recover(occupied), occupied)
        no_source = self.context()
        no_source['latest_s1_financial_evidence'] = {}
        self.assertEqual(self.recover(no_source), no_source)

    def test_spoofed_rotation_marker_is_rejected(self):
        item = self.recover()['novelty_frontier'][0]
        spoof = copy.deepcopy(item)
        spoof['v282_registry_rotation']['selection_rule'] = 'ARBITRARY'
        self.assertFalse(MODULE._v282_exact_rotation_item(spoof))
        self.assertFalse(MODULE._v251_legal_frontier_item(self.source, spoof))

        experiment = EXPERIMENTS[item['config']['experiment_id']]
        # Another symbol from the same sealed universe is a legitimate
        # registered seed, not a spoof: the validator rebuilds the expected
        # config for whichever symbol the row names.
        peers = [
            symbol for symbol in experiment['universe']
            if symbol != item['config']['symbol']
        ]
        if peers:
            peer = copy.deepcopy(item)
            peer['config'] = MODULE.kernel.validate_config(
                MODULE.kernel.performance_config(experiment, peers[0])
            )
            self.assertTrue(MODULE._v282_exact_rotation_item(peer))

        # A symbol outside the sealed universe breaks the registry binding.
        outside = next(
            symbol for symbol in ('DOGEUSDT', 'SHIBUSDT', 'TDH-NOT-A-SYMBOL')
            if symbol not in experiment['universe']
        )
        drifted = copy.deepcopy(item)
        drifted['config']['symbol'] = outside
        self.assertFalse(MODULE._v282_exact_rotation_item(drifted))

        # So does any parameter mutation.
        mutated = copy.deepcopy(item)
        mutated['config']['params']['tdh_injected_param'] = 1
        self.assertFalse(MODULE._v282_exact_rotation_item(mutated))
        self.assertFalse(MODULE._v251_legal_frontier_item(self.source, mutated))

    def test_registry_rotation_pool_is_sorted_and_complete(self):
        self.assertEqual(list(self.pool), sorted(self.pool))
        self.assertEqual(len(self.pool), len(EXPERIMENTS))
        self.assertEqual(
            {experiment_id for _, experiment_id in self.pool},
            set(EXPERIMENTS),
        )

    # the v2.0.78 queue now records its previously silent used-id exit
    def test_v278_records_used_experiment_id_skips(self):
        context = {
            'contract_version': '2.0.2',
            'research_round': 1,
            'novelty_frontier': [],
            'previous_rounds': [],
            'negative_memory': [
                {'experiment_id': MODULE.V278_REVIEWED_SEED_PRIORITY[0]}
            ],
            'research_program_memory': {},
            'latest_s1_financial_evidence': {
                'candidates': [{
                    'strategy_config': config_for(
                        'TDH-SCOUT-000001-VTM-VOL80-NODOGE-1H', 'BTCUSDT'
                    ),
                }],
            },
            'v269_reviewed_seed_replenishment': {
                'status': 'REVIEWED_SEED_QUEUE_EXHAUSTED',
            },
            'v274_global_memory_queue_filter': {
                'selected_experiment_id': None,
            },
        }
        with mock.patch.object(
            MODULE, '_v274_full_historical_candidate_hashes',
            return_value=set(),
        ):
            updated = MODULE._v278_sealed_diversification_replenishment(
                context, 'codex', Path('/sealed/history')
            )
        event = updated['v278_diversification_bridge']
        self.assertEqual(
            [row['experiment_id'] for row in
             event['skipped_used_experiment_ids']],
            [MODULE.V278_REVIEWED_SEED_PRIORITY[0]],
        )


if __name__ == '__main__':
    unittest.main()

from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'strategy_lab_controller.py'
PHOENIX_PYTHON = Path('/srv/tdh-research/phoenix-venv/bin/python')


def run_phoenix(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PHOENIX_PYTHON), '-c', textwrap.dedent(script), str(CONTROLLER)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )


class V262FailureTaxonomyTests(unittest.TestCase):
    def test_failure_classes_are_deterministic_and_fail_closed(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v262_taxonomy_test', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            cases = {
                '429 provider cooldown': ('MODEL', 'PROVIDER_QUOTA_OR_COOLDOWN'),
                'prompt exceeds character budget': ('MODEL', 'PROMPT_BUDGET_EXCEEDED'),
                'response is not valid JSON': ('MODEL', 'MALFORMED_MODEL_OUTPUT'),
                'timestamp misalignment in candles': ('DATA', 'DATA_INTEGRITY_FAILURE'),
                'checkpoint mismatch': ('CONTROLLER', 'STATE_OR_TRANSITION_FAILURE'),
                'No space left on device': ('INFRASTRUCTURE', 'RUNTIME_INFRASTRUCTURE_FAILURE'),
                'duplicate experiment': ('RESEARCH', 'RESEARCH_CONTRACT_REJECTION'),
            }
            for message, expected in cases.items():
                first = module.v262_classify_failure(message)
                second = module.v262_classify_failure(message)
                assert first == second
                assert (first['category'], first['code']) == expected
                assert first['classification_only'] is True
                assert first['automatic_recovery_authorized'] is False

            safety = module.v262_classify_failure(
                'quota exhausted while requesting live trading'
            )
            assert safety['category'] == 'SAFETY'
            assert safety['recoverable'] is False
            assert safety['escalation_required'] is True

            unknown = module.v262_classify_failure('unexpected frobnicator')
            assert unknown['category'] == 'UNKNOWN'
            assert unknown['recommended_action'] == 'FAIL_CLOSED_AND_ESCALATE'
            assert unknown['unknown_errors_fail_closed'] is True
            print('V262_FAILURE_TAXONOMY_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V262_FAILURE_TAXONOMY_OK', completed.stdout)

    def test_unhandled_failure_is_audited_once_and_reraised(self):
        completed = run_phoenix(
            """
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v262_audit_test', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            original = module.V262_BASE_EXECUTE_ROUND
            def fail_round(self, round_number, preflight):
                raise module.LabError('checkpoint mismatch after process crash')
            module.V262_BASE_EXECUTE_ROUND = fail_round
            try:
                with tempfile.TemporaryDirectory() as directory:
                    controller = object.__new__(module.Controller)
                    controller.run_dir = Path(directory)
                    controller.run_id = 'v262-test-run'
                    for _ in range(2):
                        try:
                            controller.execute_round(3, {})
                        except module.LabError as exc:
                            assert 'checkpoint mismatch' in str(exc)
                        else:
                            raise AssertionError('failure was swallowed')
                    journal = json.loads(
                        (Path(directory) / 'round-03' /
                         'RECOVERY_DECISIONS_V262.json').read_text(encoding='utf-8')
                    )
                    assert journal['decision_count'] == 1
                    decision = journal['decisions'][0]
                    assert decision['classification']['category'] == 'CONTROLLER'
                    assert decision['controller_must_reraise'] is True
                    assert decision['trading_actions'] is False
                    assert decision['exchange_api_access'] is False
            finally:
                module.V262_BASE_EXECUTE_ROUND = original
            print('V262_RECOVERY_AUDIT_RERAISE_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V262_RECOVERY_AUDIT_RERAISE_OK', completed.stdout)

    def test_runtime_contract_preserves_hard_safety(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v262_contract_test', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            contract = module.runtime_binding_contract()
            assert contract['all_controller_refs_bound'] is True
            assert contract['v262_failure_taxonomy'] is True
            assert contract['v262_classification_only'] is True
            assert contract['v262_automatic_recovery_authorized'] is False
            assert contract['v262_unhandled_failures_reraised'] is True
            assert contract['v262_unknown_errors_fail_closed'] is True
            assert contract['controller_only_recovery_policy'] is True
            assert contract['policy_change'] is False
            assert contract['trading_actions'] is False
            assert contract['exchange_api_access'] is False
            print('V262_RUNTIME_CONTRACT_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V262_RUNTIME_CONTRACT_OK', completed.stdout)

    def test_source_contains_no_automatic_recovery_path(self):
        source = CONTROLLER.read_text(encoding='utf-8')
        self.assertIn("'automatic_recovery_authorized': False", source)
        self.assertIn("'controller_must_reraise': True", source)
        tree = ast.parse(source)
        boundary = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == '_v262_execute_round'
        )
        self.assertTrue(any(
            isinstance(node, ast.Raise) and node.exc is None
            for node in ast.walk(boundary)
        ))
        self.assertNotIn('trading_actions\': True', source)
        self.assertNotIn('exchange_api_access\': True', source)


if __name__ == '__main__':
    unittest.main()

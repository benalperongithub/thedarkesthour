from __future__ import annotations

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


class V263CheckpointResumeTests(unittest.TestCase):
    def test_completed_provider_node_resumes_without_duplicate_call(self):
        completed = run_phoenix(
            """
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v263_provider_resume', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            calls = {'count': 0}
            original = module.Controller._v262_run_codex
            def provider(self, round_dir, context):
                calls['count'] += 1
                return {'verdict': 'CONTINUE', 'candidates': []}, {'input_tokens': 7}
            module.Controller._v262_run_codex = provider
            try:
                with tempfile.TemporaryDirectory() as directory:
                    controller = object.__new__(module.Controller)
                    controller.run_id = 'v263-provider-resume'
                    round_dir = Path(directory)
                    context = {'research_round': 2, 'novelty_frontier': []}
                    first = controller.run_codex(round_dir, context)
                    second = controller.run_codex(round_dir, context)
                    assert first == second
                    assert calls['count'] == 1
                    manifest = json.loads(
                        (round_dir / module.V263_MANIFEST_FILENAME).read_text(
                            encoding='utf-8'
                        )
                    )
                    node = manifest['nodes']['CODEX_PROPOSAL']
                    assert node['status'] == 'COMPLETED'
                    assert node['resume_eligible'] is True
            finally:
                module.Controller._v262_run_codex = original
            print('V263_PROVIDER_RESUME_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V263_PROVIDER_RESUME_OK', completed.stdout)

    def test_interrupted_provider_node_fails_closed_without_duplicate_call(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys
            import tempfile
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v263_interrupted', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            calls = {'count': 0}
            original = module.Controller._v262_run_codex
            def provider(self, round_dir, context):
                calls['count'] += 1
                raise module.LabError('process crash after provider dispatch')
            module.Controller._v262_run_codex = provider
            try:
                with tempfile.TemporaryDirectory() as directory:
                    controller = object.__new__(module.Controller)
                    controller.run_id = 'v263-interrupted'
                    round_dir = Path(directory)
                    context = {'research_round': 4, 'novelty_frontier': []}
                    try:
                        controller.run_codex(round_dir, context)
                    except module.LabError:
                        pass
                    else:
                        raise AssertionError('provider failure was swallowed')
                    try:
                        controller.run_codex(round_dir, context)
                    except module.LabError as exc:
                        assert 'interrupted node' in str(exc)
                    else:
                        raise AssertionError('interrupted checkpoint resumed unsafely')
                    assert calls['count'] == 1
            finally:
                module.Controller._v262_run_codex = original
            print('V263_INTERRUPTED_FAIL_CLOSED_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V263_INTERRUPTED_FAIL_CLOSED_OK', completed.stdout)

    def test_tampered_payload_is_rejected(self):
        completed = run_phoenix(
            """
            import importlib.util
            import json
            import sys
            import tempfile
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v263_tamper', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            with tempfile.TemporaryDirectory() as directory:
                round_dir = Path(directory)
                value = {'run_id': 'r', 'round_number': 1, 'actor': 'codex'}
                digest = module._v263_begin_node(round_dir, 'CODEX_PROPOSAL', value)
                module._v263_commit_node(
                    round_dir, 'CODEX_PROPOSAL', digest,
                    {'proposal': {}, 'usage': {}},
                )
                payload = module._v263_payload_path(round_dir, 'CODEX_PROPOSAL')
                raw = json.loads(payload.read_text(encoding='utf-8'))
                raw['result']['proposal']['tampered'] = True
                payload.write_text(json.dumps(raw), encoding='utf-8')
                try:
                    module._v263_resume_node(round_dir, 'CODEX_PROPOSAL', value)
                except module.LabError as exc:
                    assert 'hash mismatch' in str(exc)
                else:
                    raise AssertionError('tampered payload was accepted')
            print('V263_TAMPER_FAIL_CLOSED_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V263_TAMPER_FAIL_CLOSED_OK', completed.stdout)

    def test_completed_round_resumes_without_duplicate_execution(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys
            import tempfile
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v263_round_resume', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            calls = {'count': 0}
            original = module.Controller._v262_execute_round
            def execute(self, round_number, preflight):
                calls['count'] += 1
                (Path(self.run_dir) / f'round-{round_number:02d}').mkdir()
                return ({'research_round': round_number, 'verdict': 'REVISE'}, False, None)
            module.Controller._v262_execute_round = execute
            try:
                with tempfile.TemporaryDirectory() as directory:
                    controller = object.__new__(module.Controller)
                    controller.run_id = 'v263-round-resume'
                    controller.run_dir = Path(directory)
                    first = controller.execute_round(5, {'status': 'PREFLIGHT_OK'})
                    second = controller.execute_round(5, {'status': 'PREFLIGHT_OK'})
                    assert first == second
                    assert calls['count'] == 1
            finally:
                module.Controller._v262_execute_round = original
            print('V263_ROUND_RESUME_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V263_ROUND_RESUME_OK', completed.stdout)

    def test_runtime_contract_preserves_offline_fail_closed_policy(self):
        completed = run_phoenix(
            """
            import importlib.util
            import sys
            from pathlib import Path

            path = Path(sys.argv[1])
            spec = importlib.util.spec_from_file_location('tdh_v263_contract', path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            contract = module.runtime_binding_contract()
            assert contract['v263_node_level_checkpoints'] is True
            assert contract['v263_exact_input_hash_resume_only'] is True
            assert contract['v263_payload_hash_verified'] is True
            assert contract['v263_interrupted_nodes_fail_closed'] is True
            assert contract['v263_controller_only_resume'] is True
            assert contract['v263_automatic_retry_authorized'] is False
            assert contract['policy_change'] is False
            assert module._v263_empty_manifest()['research_mode'] == 'offline'
            assert contract['trading_actions'] is False
            assert contract['exchange_api_access'] is False
            print('V263_RUNTIME_CONTRACT_OK')
            """
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertIn('V263_RUNTIME_CONTRACT_OK', completed.stdout)


if __name__ == '__main__':
    unittest.main()

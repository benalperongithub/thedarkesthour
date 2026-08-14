from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]

def load():
 s=importlib.util.spec_from_file_location('v248probe',ROOT/'strategy_lab_controller.py'); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

class Probe(unittest.TestCase):
 def test_probe_claude_worker_args(self):
  m=load(); o=object.__new__(m.Controller); o.config=SimpleNamespace(claude_model='sonnet')
  print('V248_CLAUDE_ARGS='+repr(o.claude_worker_args()))
  self.assertTrue(True)
if __name__=='__main__': unittest.main()

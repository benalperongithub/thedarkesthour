from __future__ import annotations
import importlib.util, json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]; CTRL=ROOT/'strategy_lab_controller.py'
def load():
    s=importlib.util.spec_from_file_location('tdh_v245_test',CTRL); m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

def packet():
    return {'version':'tdh-specialist-context-v1','workers':{
        'cross_coin':{'top_cross_coin_configs':[{'experiment_id':'E1','family':'VOLUME_TSMOM','coins':['DOGEUSDT','XRPUSDT'],'unique_coins':2,'avg_expectancy_r':.05}]},
        'positive_edge':{'top_hypotheses':[{'experiment_id':'E2','family':'VOLUME_TSMOM','symbol':'DOGEUSDT','timeframe':'6h','expectancy_r':.11,'profit_factor':1.34}]},
        's1_forensics':{'dominant_failures':[['PAYOFF_BELOW_TARGET',10],['WIN_RATE_BELOW_TARGET',9]]},
        'scalping_mtf':{'status':'ACTIVE_EXECUTABLE_5M_15M'},
    },'contract':{'controller_only_promotion':True}}

def context():
    return {
        'contract_version':'2.0.2','data_class':'DEVELOPMENT_VALIDATION_ONLY','task_id':'tdh-strategy-lab-v2','round_id':'TDH-R02','research_round':1,'trial_count':0,
        'targets':{'net_win_rate':.5,'realized_payoff_ratio':2.0,'max_drawdown_pct':10.0},
        'registered_candidate_contract':{'instruction':'choose exact seed','promotion_contract':'controller only'},
        'dual_agent_contract':{'post_s1':'both agents analyze same evidence'},
        'latest_s1_financial_evidence':{'source_run_id':'r1','source_round':1,'source_stage':'S1','source_result_sha256':'a'*64,'candidates':[{'candidate_id':'c1','controller_verdict':'FAIL','strategy_config':{'family':'X','symbol':'BTCUSDT','timeframe':'1h','experiment_id':'X1','params':{},'control_mode':'PERFORMANCE'},'metrics':{'expectancy_r':-.1,'profit_factor':.8,'net_win_rate':.4,'realized_payoff_ratio':1.2,'max_drawdown_pct':4,'trade_count':100,'weekday_trades':1.1},'gates':{'baseline_beaten':False,'negative_control_beaten':False},'observations':['NEGATIVE_EXPECTANCY']}]},
        'novelty_frontier':[{'config':{'family':'Y','symbol':'BTCUSDT','timeframe':'4h','experiment_id':'Y1','params':{},'control_mode':'PERFORMANCE'},'selected_approach':'CHANGE_STRATEGY_FAMILY','sha256_prefix':'abc'}],
        'research_program_memory':{'completed_rounds':10,'evaluated_s1_candidates':50,'status_counts':{'FAIL':50},'observation_counts':{'NEGATIVE_EXPECTANCY':40}},
        'tdh_research_selection':{'registry_version':'tdh-registry-v1','family_cards':[]},'previous_rounds':[],'RAW_SENTINEL':'DO_NOT_LEAK_TO_MAIN_OR_SUBAGENT'
    }

class Tests(unittest.TestCase):
    def test_trigger_and_fingerprint_ignore_monotonic_counts(self):
        m=load(); p=packet(); yes,reasons=m.trigger(p); self.assertTrue(yes); self.assertIn('CROSS_COIN_POSITIVE_2PLUS',reasons); a=m.fingerprint(p); p['workers']['s1_forensics']['dominant_failures'][0][1]=999999; self.assertEqual(a,m.fingerprint(p))
    def test_isolated_evidence_is_bounded_and_excludes_unselected_raw_fields(self):
        m=load(); e=m.isolated(context(),packet()); self.assertLessEqual(m.jchars(e),m.EVIDENCE_MAX); self.assertNotIn('RAW_SENTINEL',json.dumps(e)); self.assertTrue(e['contract']['controller_only_promotion'])
    def test_main_advisory_is_bounded_and_survives_authoritative_compactor(self):
        m=load(); p=packet(); fp=m.fingerprint(p); a=m.advisory(p,'LLM_SUBAGENTS_COMPLETED',fp,['CROSS_COIN_POSITIVE_2PLUS'],{'role':'DEEP_RESEARCH','findings':[{'severity':'HIGH','claim':'mechanism','evidence':'e'}]},{'role':'INDEPENDENT_CRITIC','findings':[{'severity':'HIGH','claim':'confounder','evidence':'e'}]}); self.assertLessEqual(m.jchars(a),m.ADVISORY_MAX)
        raw=m.inject(context(),a); pre,_,_=m.global_preoptimize_prompt_inputs('codex_proposal',raw); final,_,report=m._compact_prompt_inputs('codex_proposal',pre); self.assertLessEqual(report['final_input_chars'],12000); self.assertEqual(final['dual_agent_contract']['avenox_subagent_advisory'],a); self.assertNotIn('RAW_SENTINEL',json.dumps(final))
    def test_cache_hit_skips_llm_path(self):
        m=load(); p=packet(); fp=m.fingerprint(p); cached=m.advisory(p,'LLM_SUBAGENTS_COMPLETED',fp,['CROSS_COIN_POSITIVE_2PLUS']); old=m.build_specialist_context; m.build_specialist_context=lambda c:p
        try:
            with tempfile.TemporaryDirectory() as td:
                obj=object.__new__(m.Controller); obj.config=SimpleNamespace(root=Path(td)); obj._av=None; obj._avu={'codex':{},'claude':{}}; obj.cache_path().parent.mkdir(parents=True); obj.cache_path().write_text(json.dumps({'fingerprint':fp,'advisory':cached})); rd=Path(td)/'round'; rd.mkdir(); out=obj.ensure_av(rd,context()); self.assertEqual(out['status'],'CACHE_HIT'); self.assertFalse((rd/'avenox-subagents').exists())
        finally: m.build_specialist_context=old
    def test_claude_429_reset_parser(self):
        m=load(); now=datetime(2026,8,13,18,0,tzinfo=timezone.utc); x=m.parse429({'api_error_status':429,'result':"You've hit your session limit · resets 6:50pm (UTC)"},now); self.assertIsNotNone(x); self.assertEqual(x['http_status'],429); self.assertGreaterEqual(x['wait_seconds'],49*60); self.assertLessEqual(x['wait_seconds'],51*60)
    def test_usage_document_counts_subagents(self):
        m=load(); obj=object.__new__(m.Controller); obj._avu={'codex':{'input_tokens':100,'output_tokens':10,'billable_tokens':110},'claude':{'input_tokens':2,'output_tokens':20,'billable_tokens':22}}; out=obj._usage_document({'input_tokens':1000,'output_tokens':100,'billable_tokens':1100},{'input_tokens':3,'output_tokens':30,'billable_tokens':33}); self.assertEqual(out['codex']['billable_tokens'],1210); self.assertEqual(out['claude']['billable_tokens'],55)
    def test_runtime_binding_and_safety_are_exact(self):
        m=load(); c=m.runtime_binding_contract(); self.assertTrue(c['all_controller_refs_bound']); self.assertTrue(c['avenox_subagent_layer']); self.assertTrue(c['controller_only_promotion']); self.assertFalse(c['trading_actions']); self.assertFalse(c['exchange_api_access']); self.assertIs(m.authoritative_s1_hard_target_pass,m.v224.authoritative_s1_hard_target_pass)
    def test_source_has_two_isolated_llm_subagent_paths_without_new_shell_network(self):
        source=CTRL.read_text(); self.assertIn("run_codex_audit(sd",source); self.assertIn("parent.run_claude(sd",source); self.assertIn("'no_external_tools':True",source); self.assertNotIn('subprocess.',source); self.assertNotIn('os.system',source)
if __name__=='__main__': unittest.main()

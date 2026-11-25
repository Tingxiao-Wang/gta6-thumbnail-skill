#!/usr/bin/env python3
"""Offline title impact / integration checks. Not a substitute for visual QA."""
import json,sys,subprocess,pathlib,tempfile
R=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from title_impact_v271 import load_title_rule,build_title_impact,focus_term
from select_references import choose
from style_system_v27 import plan_from_route
from compile_reference_handoff import compile_handoff
spec=load_title_rule()
assert len(spec['styles'])==12
assert focus_term('13年的等待，值得吗？')=='13年'
assert focus_term('GTA6值不值得买')=='值不值得'
for sid in spec['styles']:
 p=build_title_impact(sid,{'exact_headline':'13年的等待，值得吗？','title_impact_level':'bold'})
 assert p['title_enabled'] and p['focus_exact']=='13年' and p['title_exact']=='13年的等待，值得吗？'
 assert ''.join(b['text'] for b in p['blocks'])==p['title_exact']
 assert p['level']=='bold' and p['title_system'] and p['prompt'].count('13年的等待，值得吗？')==1
 q=build_title_impact(sid,{'exact_headline':'13年的等待，值得吗？','no_text':True})
 assert not q['title_enabled'] and not q['blocks'] and '不要生成任何文字' in q['prompt']
 empty=build_title_impact(sid,{})
 assert not empty['title_enabled'] and not empty['focus_exact']
route=choose('bilibili','GTA6游戏评测')
brief={'platform':'bilibili','preset_id':'bili16','topic':'GTA6游戏评测', 'exact_headline':'13年的等待，值得吗？',
 'style_id':'cinematic_poster','creative_level':'standard','output_mode':'editable','image_mode':'concept','assets':[],
 'protected_elements':[], 'title_impact_level':'bold','intake_state':{'generation_allowed':True,'pending_question':None,'answers':{'platform':'bilibili','headline_exact':'13年的等待，值得吗？'},'assets':[]}}
plans,selection=plan_from_route(route,brief)
assert len(plans)==3
assert [v['style_id'] for v in plans]==['S04','S03','S06']
assert all('【V2.7.1 标题视觉冲击力' in p['prompt'] for p in plans)
assert all(p['title_impact']['title_exact']=='13年的等待，值得吗？' for p in plans)
handoff=compile_handoff(brief,route)
assert handoff['status']=='ready'
assert len(handoff['title_impact_variants'])==3
assert handoff['title_impact_system']=='references/title_impact_v271.json'
assert compile_handoff({},route)['status']=='needs_clarification'
with tempfile.TemporaryDirectory() as tmp:
 tmp=pathlib.Path(tmp);f=tmp/'brief.json';f.write_text(json.dumps(brief,ensure_ascii=False),encoding='utf8')
 out=tmp/'out';run=subprocess.run([sys.executable,str(R/'tools/compile_brief.py'),'--brief',str(f),'--out',str(out)],capture_output=True,text=True)
 assert run.returncode==0,run.stderr
 for slot in 'ABC':
  data=json.loads((out/f'editor-project-{slot}.json').read_text('utf8'))
  impact=data['titleImpact'];blocks=data['layers']['headlineBlocks']
  assert impact['title_exact']=='13年的等待，值得吗？'
  assert ''.join(b['text'] for b in blocks)==brief['exact_headline']
  focus=next(b for b in blocks if b['role']=='focus')
  assert focus['text']=='13年' and focus['rotation']==impact['tilt_deg']
  assert focus['titleImpactStyle']==impact['style_id']
  prompt=(out/f'prompt-{slot}.txt').read_text('utf8')
  assert '【V2.7.1 标题视觉冲击力' in prompt
 m=json.loads((out/'variant-manifest.json').read_text('utf8'))
 assert m['title_impact_version']=='2.7.1'
html=(R/'tools/thumbnail-editor.html').read_text('utf8')
for tok in ['id="applyTitleImpactBtn"','id="undoTitleImpactBtn"','id="titleImpactStyle"','titleImpact271Profiles','b.titleImpactStyle=id']:
 assert tok in html
print('PASS V2.7.1: 12 style title profiles, exact text, no-text, strong/bold routing, A/B/C editor output, handoff gate, editor controls')

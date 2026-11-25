#!/usr/bin/env python3
"""Offline source, integration and no-bypass tests for V2.7; not image quality tests."""
import json,pathlib,sys,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from style_system_v27 import load_system,load_style,plan_from_route,style_selection
from select_references import choose
from compile_reference_handoff import compile_handoff
from quality_review_v27 import evaluate

sysrules=load_system()
assert len(sysrules['global_principles'])==8
assert len(sysrules['platforms'])==3
assert len(sysrules['content_style_match'])==14
assert len(list((ROOT/'styles').glob('S[0-9][0-9].json')))==12
assert set(sysrules['quality_review']['scores'].values())=={30,20,15,10,5}
assert sum(sysrules['quality_review']['scores'].values())==100
for i in range(1,13):
 s=load_style('S'+str(i).zfill(2))
 assert s['required_visual_anchors'] and s['forbidden_elements']
 assert (ROOT/s['preview_svg']).is_file()
 assert '<svg' in (ROOT/s['preview_svg']).read_text(encoding='utf-8')
assert sysrules['platforms']['bilibili']['width']==1920
assert sysrules['platforms']['xiaohongshu']['height']==1440
assert sysrules['platforms']['youtube']['width']==1280

cases=[('bilibili','游戏评测'),('bilibili','预告片解析'),('bilibili','彩蛋'),
 ('bilibili','搞笑'),('xiaohongshu','避坑'),('xiaohongshu','截图美学'),
 ('xiaohongshu','剧情CP'),('youtube','GTA6 game review')]
for plat,topic in cases:
 route=choose(plat,topic)
 brief={'topic':topic,'exact_headline':'13年的等待，值得吗？'}
 plans,sel=plan_from_route(route,brief)
 assert len(plans)==3
 assert len({p['id'] for p in plans})==3
 assert len({p['prompt'] for p in plans})==3
 assert len({p['style_id'] for p in plans})==3,(plat,topic,[p['style_id'] for p in plans])
 assert all(p['required_visual_anchors'] and p['qa_status']=='pending_real_image_review' for p in plans)
 assert all('不得伪造' in p['prompt'] or '不得编造' in p['prompt'] for p in plans)
 assert all('13年的等待，值得吗？' in p['prompt'] for p in plans)
 assert all(('仅在截图叠一行字幕视为失败' in p['prompt']) if p['style_id'] not in ('S11','S12') else True for p in plans)
# User explicitly specifies a style: keep it across all 3 variants, no automatic style shuffle.
route=choose('bilibili','评测')
for creative in ['standard','expanded','strict']:
 plans,sel=plan_from_route(route,{'requested_style':'S06','creative_level':creative,'exact_headline':'值得吗？'})
 assert [p['style_id'] for p in plans]==['S06']*3
 assert all('巨型背景字' in p['prompt'] and '遮挡关系' in p['prompt'] for p in plans)
# Strict creative mode without explicit style still locks one coherent style.
plans,sel=plan_from_route(route,{'creative_level':'strict','exact_headline':'13年等待，值吗？'})
assert len({p['style_id'] for p in plans})==1
# User's style reference overrides auto style design's palette.
state={'generation_allowed':True,'pending_question':None,'answers':{'platform':'bilibili','headline_exact':'值得吗'},
       'assets':[{'id':'one','path':'portrait.png','role':'subject'}, {'id':'two','path':'style.png','role':'style_reference'}]}
ready=compile_handoff({'intake_state':state},route)
assert ready['status']=='ready' and len(ready['visual_variants'])==3
assert ready['style_reference_source']=='user_style_override'
assert ready['style_selection']['user_style_reference_priority']
assert all('用户确认的风格参考优先' in v['prompt'] for v in ready['visual_variants'])
assert all(v['headline_exact']=='值得吗' for v in ready['visual_variants'])
assert 'quality_review_policy' in ready
# Explicit S04 with no numeric evidence must stop and request factual value.
blocked_number=compile_handoff({'intake_state':state,'requested_style':'S04', 'exact_headline':'GTA6值得玩吗？'},route)
assert blocked_number['status']=='needs_clarification' and not blocked_number['generation_allowed']
# Hard-gate cannot be bypassed by the compiler or handoff.
assert compile_handoff({},route)['status']=='needs_clarification'
planned=compile_handoff({'intake_state':{'generation_allowed':True,'assets':[{'id':'p','role':'subject'}]}},route)
assert planned['status']=='needs_clarification' and not planned['generation_allowed']
# S04 must not fabricate a score from the game title 'GTA6'.
plans,sel=plan_from_route(route,{'exact_headline':'值得玩吗？','topic':'GTA6评测'})
assert all(p['style_id']!='S04' for p in plans)
# QA cannot pass without actual supplied review; any veto fails even if 100 score.
assert evaluate({})['status']=='review_required'
w=sysrules['quality_review']['scores'];vs={k:False for k in sysrules['quality_review']['vetoes']}
assert evaluate({'scores':w,'vetoes':vs})['passed']
vs['mere_subtitle_overlay_except_S11_S12']=True
assert evaluate({'scores':w,'vetoes':vs})['status']=='failed'
# Legacy compiler must require confirmed intake and output new 12-style prompts.
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);brief={'platform':'bilibili','preset_id':'bili16','style_id':'cinematic_poster',
     'topic':'GTA6游戏评测','exact_headline':'13年的等待，值得吗？',
     'tag':'','subtitle':'','composition_note':'','color_tone':'',
     'output_mode':'editable','image_mode':'concept','assets':[],'protected_elements':[]}
 b=d/'input.json';o=d/'out';b.write_text(json.dumps(brief,ensure_ascii=False),encoding='utf-8')
 r=subprocess.run([sys.executable,str(ROOT/'tools/compile_brief.py'),'--brief',str(b),'--out',str(o)],capture_output=True,text=True)
 assert r.returncode!=0 and 'intake_state' in r.stderr
 brief['intake_state']={'generation_allowed':True,'pending_question':None,'answers':{'platform':'bilibili'},'assets':[]}
 b.write_text(json.dumps(brief,ensure_ascii=False),encoding='utf-8')
 r=subprocess.run([sys.executable,str(ROOT/'tools/compile_brief.py'),'--brief',str(b),'--out',str(o)],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 manifest=json.loads((o/'variant-manifest.json').read_text(encoding='utf-8'))
 assert manifest['design_system_version']=='2.7-test'
 assert [v['style_id'] for v in manifest['visual_variants']]==['S04','S03','S06']
 assert all('【必须实现的视觉锚点】' in (o/f'prompt-{x}.txt').read_text(encoding='utf-8') for x in 'ABC')
 assert all('【V2.7' in (o/f'visual-prompt-{x}.txt').read_text(encoding='utf-8') for x in 'ABC')
 assert json.loads((o/'editor-project.json').read_text('utf-8'))['grade']['preset']=='none'
# Old public-safe content atlas must not accidentally reintroduce embedded screenshots.
source=(ROOT/'references/content_atlas/GTA6封面内容参考手册.html').read_text(encoding='utf-8')
assert 'data:image/webp;base64,' not in source
assert not list((ROOT/'assets').rglob('b_*webp'))
print('PASS V2.7: 12 styles, 14 match rows, 3 platforms, original SVGs, style fidelity/variety, no fabricated rating, QA gate, intake gate, compiler, and safe atlas')

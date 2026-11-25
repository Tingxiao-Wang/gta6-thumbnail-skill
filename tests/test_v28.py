#!/usr/bin/env python3
"""V2.8 decision/handoff/editor structural tests (NOT real rendered-image QA)."""
from __future__ import annotations
import json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from select_references import choose
from style_system_v27 import plan_from_route
from compile_reference_handoff import compile_handoff
from creative_director_v28 import split_title
from visual_benchmark_v28 import evaluate_pair

headline='万字解析：GTA6到底讲了什么故事？'
route=choose('bilibili','GTA6 剧情解析')
base={'topic':'GTA6 剧情解析','exact_headline':headline}
plans,selection=plan_from_route(route,base)
assert selection['style_ids']==['S01','S05','S06'],selection
assert len(plans)==3
assert len({p['visual_architecture'] for p in plans})==3
assert len({p['scene_shot'] for p in plans})==3
assert len({p['layout_blueprint']['id'] for p in plans})==3
for p in plans:
    assert p['decision_version']=='2.8'
    assert len(p['non_textual_actions'])>=2
    h=p['headline_hierarchy']
    assert h['full_exact']==headline
    assert h['segments']['intro']+h['segments']['focus']+h['segments']['outro']==headline
    assert h['segments']['focus']=='GTA6'
    assert '万字解析' in h['segments']['intro']
    assert '到底讲了什么故事？' in h['segments']['outro']
    assert '【第一眼要传达的内容】' in p['prompt']
    assert '【非文字视觉设计动作】' in p['prompt']
    assert '【标题作为整图构图的一部分】' in p['prompt']
    assert '仅在截图叠一行字幕视为失败' in p['prompt']
    assert '全网首发' not in p['prompt']
    assert 'prompt完成等于出图' not in p['prompt']
    assert p['native_baseline_comparison']=='pending_rendered_image'
    assert p['source_evidence']['mode'] in ('concept_only','storyboard_concept_not_evidence')
assert split_title('万字解析：GTA6到底讲了什么故事？')['reconstructed']==headline
assert split_title('13年的等待，值得吗？')['focus']=='13年'

# Individual style lock: the same language, three different scenes.
locked,s=plan_from_route(route,{**base,'requested_style':'S06'})
assert [x['style_id'] for x in locked]==['S06']*3
assert len({x['scene_shot'] for x in locked})==3
assert len({x['layout_blueprint']['id'] for x in locked})==3
# User style reference override still wins.
state={'generation_allowed':True,'pending_question':None,
       'answers':{'platform':'bilibili','headline_exact':headline},
       'assets':[{'id':'style-1','role':'style_reference','path':'my-style.png'}]}
ready=compile_handoff({'intake_state':state,'topic':base['topic']},route)
assert ready['status']=='ready'
assert ready['creative_director']=='scripts/creative_director_v28.py'
assert ready['creative_decision_version']=='2.8'
assert all(v['user_style_reference_priority'] for v in ready['visual_variants'])
assert all('用户确认的风格参考优先' in v['prompt'] for v in ready['visual_variants'])
assert len(ready['creative_variants'])==3
assert compile_handoff({},route)['status']=='needs_clarification'

# Real person photos are not available for regeneration even with bolder visual
# composition; A/B/C must reuse the original image layer.
state2={**state,'assets':[{'id':'host','role':'subject','path':'portrait.png',
                         'asset_kind':'real_person_photo','description':'本人照片'}]}
photo=compile_handoff({'intake_state':state2,'topic':base['topic']},route)
assert photo['status']=='ready' and photo['person_photo_protection']['requires_pixel_preserving_compositing']
assert all('本人真实照片不得无授权重绘' in x['prompt'] for x in photo['visual_variants'])

# Compile the same case as three real editor projects, not three old fixed text
# coordinates. No external image generation is claimed or invoked.
with tempfile.TemporaryDirectory() as tmp:
    tmp=pathlib.Path(tmp);src=tmp/'input.json';dest=tmp/'output'
    src.write_text(json.dumps({'platform':'bilibili','preset_id':'bili16','style_id':'cinematic_poster',
         'topic':base['topic'],'exact_headline':headline,
         'tag':'','subtitle':'','composition_note':'','color_tone':'',
         'output_mode':'editable','image_mode':'concept','assets':[],
         'protected_elements':[],'intake_state':{**state,'assets':[]}},ensure_ascii=False),'utf8')
    r=subprocess.run([sys.executable,str(ROOT/'tools/compile_brief.py'),
        '--brief',str(src),'--out',str(dest)],capture_output=True,text=True)
    assert r.returncode==0,(r.stdout,r.stderr)
    mani=json.loads((dest/'variant-manifest.json').read_text('utf8'))
    assert mani['creative_decision_version']=='2.8'
    assert mani['design_system_version']=='2.7-test'
    assert len({x['visual_architecture'] for x in mani['visual_variants']})==3
    coords=[]
    for variant in 'ABC':
        p=(dest/f'prompt-{variant}.txt').read_text('utf8')
        assert '【唯一画面与排版决策来源】V2.8' in p
        assert '【第一眼要传达的内容】' in p
        assert '【版式母版】' not in p
        assert '固定 A/B/C 字幕位置' in p  # prohibition rather than enforcement
        assert '全网首发' not in p
        editor=json.loads((dest/f'editor-project-{variant}.json').read_text('utf8'))
        blocks=editor['layers']['headlineBlocks']
        assert ''.join(x['text'] for x in blocks)==headline
        assert len(blocks)==3
        assert [x['role'] for x in blocks]==['intro','focus','outro']
        coords.append([(x['x'],x['y'],x['width']) for x in blocks])
        assert editor['visualScenePlan']['decision_version']=='2.8'
    assert len(set(map(str,coords)))==3
    assert '【第一眼要传达的内容】' in (dest/'prompt.txt').read_text('utf8')

assert evaluate_pair({'actual_images_reviewed':False})['status']=='needs_real_images'
sample={'actual_images_reviewed':True,
  'native':{k:3 for k in ('visual_story','non_textual_design','title_hierarchy','composition_depth','content_truth')},
  'with_skill':{k:4 for k in ('visual_story','non_textual_design','title_hierarchy','composition_depth','content_truth')},
  'flat_one_line_subtitle':True}
assert evaluate_pair(sample)['passed'] is False
sample['flat_one_line_subtitle']=False
assert evaluate_pair(sample)['passed'] is True
print('PASS V2.8: genuine visual story + scene decisions, lossless 3-layer title, A/B/C distinct, editor follows director, role/photo guard, no fake quality claims')

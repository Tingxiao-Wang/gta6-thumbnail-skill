#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
selector=load('select',ROOT/'scripts'/'select_references.py')
compiler=load('handoff',ROOT/'scripts'/'compile_reference_handoff.py')
gate=load('gate',ROOT/'scripts'/'intake_gate_v252.py')
data=json.loads((ROOT/'references'/'content_atlas'/'content_atlas_index_v26.json').read_text('utf-8'))
assert len(data['cases'])==15
assert sum(x['platform']=='bilibili' for x in data['cases'])==8
assert sum(x['platform']=='xiaohongshu' for x in data['cases'])==7
assert data['platform_coverage']['youtube']['case_count']==0
assert not (ROOT/'assets'/'bundled_references').exists()
assert not (ROOT/'references'/'bundled_reference_manifest_v25.json').exists()
for q,id in [('评测评分','bili_D'),('解析地图','bili_B'),('通关实况','bili_C'),('预告','bili_A'),('攻略彩蛋','bili_E'),('搞笑名场面','bili_F'),('AI二创','bili_G'),('爆料新闻','bili_H')]:
    r=selector.choose('bilibili',q)
    assert r['selected'][0]['id']==id,(q,r)
for q,id in [('避坑买哪个','xhs_C'),('游戏拍照壁纸','xhs_D'),('剧情爱情CP','xhs_G'),('仿妆情侣','xhs_F')]:
    r=selector.choose('xiaohongshu',q)
    assert r['selected'][0]['id']==id,(q,r)
assert selector.choose('bilibili','chase')['selected'][0]['id']=='bili_C'
assert selector.choose('xiaohongshu','review')['selected'][0]['id']=='xhs_C'
assert not selector.choose('bilibili','不存在的类型子串XYZ')['selected']
for p in ['bilibili','xiaohongshu']:
    r=selector.choose(p,'评测')
    for x in r['image_paths']:
        assert (ROOT/x).exists(),x
fallback=selector.choose('youtube','review')
assert fallback['status']=='platform_fallback' and not fallback['selected']
assert not compiler.compile_handoff({},selector.choose('bilibili','评测'))['generation_allowed']
# role unknown -> blocked, confirm subject then normal question then ready
first=gate.evaluate(None,'B站GTA测评',[{'id':'portrait','path':'portrait.png'}])
assert first['gate']=='image_role'
blocked=compiler.compile_handoff({'intake_state':first['state']},selector.choose('bilibili','测评'))
assert blocked['status']=='needs_clarification'
second=gate.evaluate(first['state'],'1')
assert second['status']=='needs_clarification'
third=gate.evaluate(second['state'],'4')
assert third['status']=='ready'
ready=compiler.compile_handoff({'intake_state':third['state']},selector.choose('bilibili','测评'))
assert ready['status']=='ready' and ready['content_inputs'][0]['role']=='subject'
assert ready['style_reference_source'].startswith('manual_atlas_')
# confirmed user's visual style is stronger than manual imagery
other=gate.evaluate(None,'图1做主体，图2作为风格参考，B站游戏评测，标题「值得吗」',[
    {'id':'image_1','path':'subject.png'}, {'id':'image_2','path':'style.png'}])
assert other['status']=='ready',other
out=compiler.compile_handoff({'intake_state':other['state']},selector.choose('bilibili','评测'))
assert out['status']=='ready' and out['style_reference_source']=='user_style_override'
assert out['style_inputs'][0]['path']=='style.png'
assert not out['atlas_reference_images']
assert out['atlas_entries'][0]['id']=='bili_D'
print('PASS V2.6 atlas: 15 types, 8+7, 12 routes, youtube fallback, role gate, user style override')

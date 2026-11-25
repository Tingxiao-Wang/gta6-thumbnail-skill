#!/usr/bin/env python3
"""V2.8: visual director layered over the user's 12-style design planner, NOT an image generator.

Input route is the V2.6 content router output; brief retains exact user text
and confirmed asset roles. All design constants originate in the user's V1.0
HTML (extracted to references/design_principles/design_system_v27.json).
"""
from __future__ import annotations
from person_photo_protection_v272 import build_photo_protection, instruction as person_instruction
import argparse
import json
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
SYS=ROOT/'references'/'design_principles'/'design_system_v27.json'
STYLE_DIR=ROOT/'styles'
CASENAME={
    'bili_A':'官方物料／预告','bili_B':'深度解析／考据',
    'bili_C':'全流程／实况','bili_D':'评测／锐评',
    'bili_E':'彩蛋／发现','bili_F':'搞笑／名场面',
    'bili_G':'二创／AI作品','bili_H':'资讯／爆料',
    'xhs_A':'晒单／选购','xhs_B':'搞笑／名场面',
    'xhs_C':'晒单／选购','xhs_D':'摄影／壁纸',
    'xhs_E':'实景打卡／旅行','xhs_F':'穿搭／仿妆',
    'xhs_G':'剧情／CP'
}
CONTENT_KEYWORDS=[
    ('攻略／教程',['攻略','教程','路线','收集','通关','mission','how to','guide','walkthrough']),
    ('彩蛋／发现',['彩蛋','秘密','隐藏','线索','发现','easter egg','secret']),
    ('评测／锐评',['评测','评价','锐评','评分','打分','review','worth','值得吗','值不值']),
    ('深度解析／考据',['解析','细节','拆解','考据','analysis','explained','深度']),
    ('资讯／爆料',['资讯','快讯','爆料','更新','官宣','发售','news','leak','announcement']),
    ('搞笑／名场面',['搞笑','整活','挑战失败','名场面','funny','meme','absurd']),
    ('全流程／实况',['实况','全流程','开荒','playthrough','gameplay','直播']),
    ('穿搭／仿妆',['穿搭','妆','cos','outfit']),
    ('摄影／壁纸',['截图美学','壁纸','摄影','photography','aesthetic']),
    ('实景打卡／旅行',['打卡','旅行','实景','现实对照','citywalk','travel']),
    ('剧情／CP',['剧情','cp','爱情','角色关系','romance','story']),
    ('晒单／选购',['选购','避坑','晒单','购买','价格','buying','purchase','worth buying']),
    ('二创／AI作品',['二创','混剪','ai创作','fan art','fanmade']),
    ('官方物料／预告',['预告','预告片','trailer','首发','物料'])
]
VARIATION_NOTES={
    'A':'突出一个主角、主物件或主视觉符号；近景或中景；建立最强第一眼焦点',
    'B':'利用明显的空间、景别或信息结构变化，形成第二种视觉关系；不得只是标题改位置',
    'C':'采用更有叙事性或编辑感的构图方式；根据内容选择少字、无字或特别的图层遮挡'
}
STYLE_FALLBACK={
    'S01':['S06','S12'], 'S02':['S11','S05'], 'S03':['S06','S01'],
    'S04':['S03','S06'], 'S05':['S02','S10'], 'S06':['S01','S10'],
    'S07':['S11','S06'], 'S08':['S06','S04'], 'S09':['S02','S05'],
    'S10':['S01','S06'], 'S11':['S01','S12'], 'S12':['S01','S10']
}

def load_system():
    return json.loads(SYS.read_text(encoding='utf-8'))

def load_style(style_id):
    if not re.fullmatch(r'S(?:0[1-9]|1[0-2])',str(style_id)):
        raise ValueError('未知风格编号: '+str(style_id)+'；仅接受 S01–S12')
    return json.loads((STYLE_DIR/(style_id+'.json')).read_text(encoding='utf-8'))

def content_type_for(route,brief):
    text=' '.join(str(x or '') for x in (brief.get('topic'),brief.get('content_type'),route.get('topic'))).lower()
    for name,keys in CONTENT_KEYWORDS:
        if any(k in text for k in keys): return name
    cases=route.get('selected') or []
    if cases:
        case_id=cases[0].get('id')
        if case_id=='bili_E' and '攻略' in text:return '攻略／教程'
        return CASENAME.get(case_id,'全流程／实况')
    return '全流程／实况'

def style_selection(route,brief):
    sys=load_system()
    match={c['content_type']:c for c in sys['content_style_match']}
    ctype=content_type_for(route,brief)
    entry=match.get(ctype) or match['全流程／实况']
    explicit=str(brief.get('requested_style') or brief.get('design_style_id') or '').strip().upper()
    if explicit and not re.fullmatch(r'S(?:0[1-9]|1[0-2])',explicit):
        raise ValueError('指定风格必须为 S01–S12，例如 requested_style="S06"')
    intake=brief.get('intake_state') or {}
    assets=brief.get('uploaded_images')
    if assets is None:assets=intake.get('assets',[])
    has_style=any(isinstance(x,dict) and x.get('role') in ('style_reference','both','style','reference') for x in (assets or []))
    creative=str(brief.get('creative_level') or 'standard').lower().strip()
    creative={'strict':'strict','严格复现':'strict','standard':'standard','标准创作':'standard','expanded':'expanded','创意拓展':'expanded'}.get(creative,creative)
    if creative not in ('strict','standard','expanded'):
        raise ValueError('creative_level 只能为 strict, standard 或 expanded')
    preferred=explicit or entry['primary_style_id']
    alternatives=entry['alternative_style_ids']
    if explicit or has_style or creative=='strict':
        ids=[preferred]*3
    else:
        options=[preferred]+alternatives+STYLE_FALLBACK.get(preferred,[])
        if creative=='expanded':
            options=[preferred]+list(reversed(STYLE_FALLBACK.get(preferred,[])))+alternatives
        ids=list(dict.fromkeys(options))
        ids=(ids+[preferred]*3)[:3]
    # V2.8: narrative deep-dives need STORY visual options, not a fabricated
    # walkthrough/map just because S09 was an alternative in the source table.
    story_text=' '.join((str(brief.get('topic') or ''),str(brief.get('exact_headline') or '')))
    if (ctype=='深度解析／考据' and not (explicit or has_style or creative=='strict')
            and any(w in story_text for w in ('故事','剧情','人物关系','万字解析','story','plot'))):
        ids=['S01','S05','S06']
    # A GTA6 product name is not an evidence-bearing score/price/quantity.
    exact=str(brief.get('exact_headline') or (brief.get('intake_state') or {}).get('answers',{}).get('headline_exact') or '')
    numeric_text=re.sub(r'GTA\s*(?:VI|6)', '', exact, flags=re.IGNORECASE)
    has_number=bool(re.search(r'\d',numeric_text)) or bool(brief.get('verified_numbers'))
    if not has_number and not explicit:
        feasible=[s for s in ids if s!='S04']
        feasible+=['S03','S06','S01','S11']
        ids=list(dict.fromkeys(feasible))[:3]
        if creative=='strict':ids=[ids[0]]*3
    return {'content_type':ctype,'click_motive':entry['click_motive'],'primary_style':preferred,
        'style_ids':ids,'needs_verified_numeric_for_explicit_S04':bool(explicit=='S04' and not has_number),
        'creative_level':creative,
        'explicit_style':bool(explicit),'user_style_reference_priority':has_style,
        'matching_source':'GTA6封面设计原则_V1.0.html #match'}

def protected_asset_info(brief):
    state=brief.get('intake_state') or {}
    assets=brief.get('uploaded_images')
    if assets is None:assets=state.get('assets',[])
    has_subject=any(isinstance(x,dict) and x.get('role') in ('subject','both') for x in (assets or []))
    return has_subject

# V2.8 removed the retired pre-creative-director prompt builder; the only
# final scene prompt comes from creative_director_v28.build().

def plan_from_route(route,brief=None):
    brief=brief or {}
    from visual_diversity_v261 import plan_from_route as scene_planner
    from title_impact_v271 import build_title_impact
    sel=style_selection(route,brief)
    original_scenes=scene_planner(route,brief)
    platform=route.get('platform') or (brief.get('intake_state') or {}).get('answers',{}).get('platform')
    if platform not in load_system()['platforms']:
        raise ValueError('平台无效：'+str(platform))
    plat=load_system()['platforms'][platform]
    headline=(brief.get('exact_headline') or (brief.get('intake_state') or {}).get('answers',{}).get('headline_exact') or '')
    topic=brief.get('topic') or route.get('topic') or 'GTA6 封面'
    factual_nums=brief.get('verified_numbers') or []
    if not isinstance(factual_nums,list):raise ValueError('verified_numbers 必须为数组')
    # Topic 'GTA6' does not itself qualify as evidence of a numeric review score.
    numeric=bool(re.search(r'\d',re.sub(r'GTA\s*(?:VI|6)','',headline,flags=re.IGNORECASE))) or bool(factual_nums)
    out=[]
    for i,scene in enumerate(original_scenes):
        sid=sel['style_ids'][i]
        s=load_style(sid)
        v={**scene,'style_id':sid,'style_name':s['name'],'style':s,
           'design_system_version':'2.7-test','headline_exact':headline,'topic':topic,
           'platform':platform,'content_type':sel['content_type'],
           'click_motive':sel['click_motive'],'creative_level':sel['creative_level'],
           'user_style_reference_priority':sel['user_style_reference_priority'],
           'user_has_subject':protected_asset_info(brief),'numeric_evidence_available':numeric,
           'person_photo_protection':build_photo_protection(brief),
           'required_visual_anchors':s['required_visual_anchors'],
           'optional_visual_elements':[] if sel['creative_level']=='strict' else s['optional_visual_elements'],
           'forbidden_elements':s['forbidden_elements'],
           'visual_reconstruction_required':sid not in ('S11','S12'),
           'qa_status':'pending_real_image_review',
           'variation_note':VARIATION_NOTES[scene['id']]}
        # V2.8: creative director owns the final composition, visual story and
        # headline hierarchy. Legacy design plans remain as source metadata only.
        from creative_director_v28 import build as direct_creative
        from title_impact_v271 import build_title_impact as _title_impact
        from person_photo_protection_v272 import instruction as _photo_instruction
        creative=direct_creative(v,brief,sel,plat,_photo_instruction(brief))
        v.update(creative)
        focused=creative['headline_hierarchy']['segments']['focus']
        enhanced_brief=dict(brief)
        if focused: enhanced_brief['emphasis_keyword']=focused
        v['title_impact']=_title_impact(sid,enhanced_brief)
        # Legacy font recipes are advisory; do not prepend their coordinates.
        # Keep a small compatible style-anchor contract for regression checking.
        v['prompt']=(creative['prompt']+
            f'【必须实现的视觉锚点】{chr(12289).join(v["required_visual_anchors"])}；'+
            '只能作为整体画面语言，不是新一层贴纸。\n'+
            f'【独立场景/景别】{creative["scene_shot"]}。\n'+
            '【回归禁令】仅在截图叠一行字幕视为失败；不得编造、不得伪造实机、数字或新闻事实。\n'+
            v['title_impact']['prompt']+'\n')
        out.append(v)
    return out,sel


def neutral_prompt_for_brief(brief,platform):
    plat=load_system()['platforms'][platform]
    assets=brief.get('uploaded_images') or brief.get('assets') or []
    lines=['【V2.7 公共交接约束】',f'内容主题：{brief.get("topic", "GTA6封面")}',
        f'平台：{platform}；建议{plat["width"]}×{plat["height"]}；{plat["aspect_ratio"]}',
        '用户原文：'+str(brief.get('exact_headline') or '（未提供）'),
        '严格保留用户已确认的主体图、风格参考图角色及用户指定的文案。',
        person_instruction(brief),
        '本版不强制默认粉紫调色，也不强制所有封面使用大字幕；独立风格规则优先于旧通用字效模板。',
        '不得添加未经确认的地图、游戏实机、评分、新闻及主播照片。',
        '本地程序只生成提示词和编辑器交接数据；不会调用生图模型。']
    if assets: lines.append('素材摘要：'+str([(a.get('id'),a.get('role')) for a in assets if isinstance(a,dict)]))
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route',required=True)
    p.add_argument('--brief',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    route=json.loads(pathlib.Path(a.route).read_text(encoding='utf-8'))
    brief=json.loads(pathlib.Path(a.brief).read_text(encoding='utf-8'))
    plans,sel=plan_from_route(route,brief)
    output=pathlib.Path(a.out);output.mkdir(parents=True,exist_ok=True)
    (output/'design-selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'visual-plans-v27.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for plan in plans:
        (output/f'visual-prompt-{plan["id"]}.txt').write_text(plan['prompt'],encoding='utf-8')
    print('Generated V2.7 design plans and prompts, not actual images.')

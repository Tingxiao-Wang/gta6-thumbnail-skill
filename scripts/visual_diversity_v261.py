#!/usr/bin/env python3
"""V2.6.1 content-aware scene director. No image generation is performed.

The variation layer outputs three independent scene designs and corresponding prompts
and does not alter the V2.5.2 role gate or the older browser editor.
"""
from __future__ import annotations
import json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DB=ROOT/'references'/'visual_diversity_v261.json'

def load_rules():
    return json.loads(DB.read_text(encoding='utf-8'))

def plan_from_route(route,brief=None):
    brief=brief or {}
    rules=load_rules()
    rows=route.get('selected',[])
    case_id=rows[0]['id'] if rows else None
    template=rules['cases'].get(case_id) or rules['youtube_fallback']
    intake=brief.get('intake_state') or {}
    assets=brief.get('uploaded_images') or intake.get('assets') or []
    roles=[(a.get('role') if isinstance(a,dict) else None) for a in assets]
    user_has_subject=any(r in ('subject','both') for r in roles)
    user_has_style=any(r in ('style_reference','both') for r in roles)
    original_headline=brief.get('exact_headline') or intake.get('answers',{}).get('headline_exact') or ''
    topic=brief.get('topic') or route.get('topic') or 'GTA6 gaming'
    out=[]
    for row in template['variants']:
        v=dict(row)
        v.update({'platform':route.get('platform'), 'content_type':case_id or 'platform_fallback',
                  'topic':topic,'headline_exact':original_headline,
                  'scene_source':'user_original_content' if user_has_subject else 'concept_or_confirmed_source',
                  'background_asset_strategy':'independent_scene',
                  'word_layer_strategy':'separate_editable_text_layer',
                  'original_user_style_priority':user_has_style})
        v['prompt']=prompt_for_plan(v,user_has_subject,user_has_style)
        out.append(v)
    return out

def prompt_for_plan(p,user_has_subject=False,user_has_style=False):
    role=('保持用户上传的封面主体与人像身份，绝不擅自替换主体；' if user_has_subject else '只使用用户已有或有权使用的画面，缺失的真实素材不能伪造；')
    style=('用户风格参考图高于手册默认风格，保留其可观察构图和色彩语言；' if user_has_style else '采用本次内容类型的设计方向，可使用已有手册中的设计规律；')
    return '\n'.join([
        f'【独立封面方案 {p["id"]} · {p["mode"]}】{p["name"]}',
        f'【平台/主题】{p["platform"]} / {p["topic"]}',
        f'【独立画面构图】{p["scene_direction"]}',
        f'【主体占比与空间】{p["composition"]}',
        f'【功能性视觉元素判定】{p["evidence_rule"]}；只允许对真实可见内容添加证据圈注、箭头、编号、局部放大窗和对比区。它们必须承担信息功能，不得纯装饰。',
        f'【画面素材与保护】{role}',
        f'【参考风格】{style}',
        f'【标题设计】用户原文：{p["headline_exact"]!r}；建议表达：{p["headline_treatment"]}；不许改变字面原文。允许少字/无字封面时不要强制生成字幕。',
        '【三种方案差异】本方案应有独立景别/分镜/视觉焦点；不能仅把相同底图的文字换位或换色。另两方案会采用其他结构。',
        '【生成策略】背景和人物视觉结构优先；中文复杂文字建议先生成无字背景后使用编辑器添加。若需要不同视觉底图，A/B/C 分别执行三次图像生成或编辑。',
        '【真实性】不得凭空编造评分、日期、游戏事件、新闻证据、主播肖像；没有素材时按场景提示进行降级。'
    ])

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--route',required=True)
    ap.add_argument('--brief')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    route=json.loads(pathlib.Path(args.route).read_text('utf-8'))
    brief=json.loads(pathlib.Path(args.brief).read_text('utf-8')) if args.brief else {}
    plans=plan_from_route(route,brief)
    dest=pathlib.Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/'visual-plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2),encoding='utf-8')
    for p in plans:(dest/f'visual-prompt-{p["id"]}.txt').write_text(p['prompt'],encoding='utf-8')
    print('Created 3 independent scene plans; no image API was called.')

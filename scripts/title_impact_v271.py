#!/usr/bin/env python3
"""V2.7.1 title hierarchy planner. Produces instructions/edit metadata, not rendered images."""
from __future__ import annotations
import json,re,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
RULE=ROOT/'references'/'title_impact_v271.json'
def load_title_rule():return json.loads(RULE.read_text('utf8'))
def focus_term(text,desired=''):
    text=str(text or ''); desired=str(desired or '').strip()
    if desired and desired in text:return desired
    # Extract only characters that already appear in the user's exact headline.
    # "GTA6" is a product name, not evidence for a score.
    if not text:return ''
    for pattern in [r'(?<![A-Za-z])\d{1,4}(?:\.\d+)?\s*(?:年|小时|天|次|分钟|GB|G|%|元)(?![A-Za-z])',r'值不值得|值得吗|真相|隐藏|秘密|震惊|必看|最强|崩溃|对比|彩蛋|攻略']:
        m=re.search(pattern,text,re.I)
        if m:return m.group(0)
    for piece in re.split(r'[，。！？!?：:、\s]+',text):
        if 2<=len(piece)<=5 and not re.fullmatch(r'GTA\s*(?:6|VI)',piece,re.I):return piece
    return text[:min(4,len(text))]
def build_title_impact(style_id,brief):
    spec=load_title_rule()
    if style_id not in spec['styles']:raise ValueError('unknown title impact style '+style_id)
    s=spec['styles'][style_id]
    title=str(brief.get('exact_headline') or (brief.get('intake_state') or {}).get('answers',{}).get('headline_exact') or '')
    no_text=brief.get('no_text') is True or brief.get('output_mode')=='no_text'
    level=str(brief.get('title_impact_level') or s['default_level']).lower()
    if level not in spec['levels']:raise ValueError('title_impact_level must be subtle/strong/bold')
    factor=spec['levels'][level]
    focus=focus_term(title,brief.get('emphasis_keyword') or '') if not no_text else ''
    anchors=[] if no_text else ([{'role':'intro','text':title[:title.index(focus)]}] if focus and title.index(focus)>0 else []) + ([{'role':'focus','text':focus}] if focus else []) + ([{'role':'outro','text':title[title.index(focus)+len(focus):]}] if focus and title[title.index(focus)+len(focus):] else [])
    # If no title, no fabricated text is permitted even when the style normally uses giant typography.
    enabled=bool(title) and not no_text
    info={'style_id':style_id,'style_name':s['name'],'title_exact':title,'title_enabled':enabled,'no_text_requested':no_text,'level':level,'focus_exact':focus,'blocks':anchors,'title_system':s['system'],'composition_rule':s['layout_direction'],'material_rule':s['material'],'color_rule':s['color_contrast'],'space_rule':s['space_relation'],'target_focus_ratio':round(s['focus_ratio']*factor['scale'],3),'tilt_deg':round(s['tilt_deg']*factor['motion'],1),'suggested_editor_recipe':s['suggested_edit_recipe'],'requires_real_occlusion':style_id=='S06','qa_status':'unverified_requires_actual_image'}
    if no_text:info['prompt']='【标题层】用户明确要求无字：不要生成任何文字、角标和伪造字样。用画面主体承载冲击力。'
    elif not enabled:info['prompt']='【标题层】没有准确标题，禁止临时编造标题、评分和消息；保持真实视觉焦点。'
    else:
        info['prompt']=(f'【V2.7.1 标题视觉冲击力 · {style_id}】完整标题原文「{title}」，必须逐字准确，不能增减。核心视觉字词「{focus}」仅来自原标题；其余字为次级解释。'+f'标题结构：{s["layout_direction"]}。材质：{s["material"]}。色彩：{s["color_contrast"]}。空间关系：{s["space_relation"]}。'+f'强度 {level}，核心主词建议相对次级文字放大约 {int(round(info["target_focus_ratio"]*100))}%（需要按画幅和实际字数调整，不可强挤或裁字），倾斜约 {info["tilt_deg"]}°。'+('若要真实前后穿插，必须使用有权使用的独立透明主体图层或蒙版；无图层不得声称实现遮挡。' if style_id=='S06' else '')+'先设计标题的几何结构，再决定配方；使用可编辑文字图层确保中文准确。旧去AI味规则不得将本风格必需的描边、立体厚度、动势全删掉；禁止无意义英文和假评分。')
    return info

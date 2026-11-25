#!/usr/bin/env python3
"""V2.6 intake-protected handoff from confirmed image roles and content-atlas routing.
This produces a manifest and prompt instructions; it cannot send image bytes to the model.
"""
import argparse, json, pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from style_system_v27 import plan_from_route,load_system
from person_photo_protection_v272 import build_photo_protection, instruction
ALLOWED={'subject','style_reference','both','excluded'}
ALIASES={'content':'subject','content_image':'subject','style':'style_reference','reference':'style_reference','skip':'excluded'}
def normalize(a,i):
    a={'path':a} if isinstance(a,str) else dict(a)
    role=ALIASES.get(a.get('role'),a.get('role'))
    return {'id':a.get('id') or f'image_{i+1}','path':a.get('path') or a.get('uri'),
            'role':role if role in ALLOWED else None,
            'role_source':a.get('role_source','unspecified'),
            'description':a.get('description',''),
            'asset_kind':a.get('asset_kind') or a.get('image_kind'),
            'is_real_person_photo':a.get('is_real_person_photo',False)}
def compile_handoff(brief,route):
    intake=brief.get('intake_state')
    # ALWAYS enforce intake, not just when 'version' is exactly V2.5.2.
    if not isinstance(intake,dict):
        return {'version':'2.8-visual-decision-test','status':'needs_clarification','generation_allowed':False,
                'question':'请先完成V2.5.2问答关卡，并传入已确认的 intake_state。'}
    if intake.get('pending_question') or intake.get('generation_allowed') is not True:
        p=intake.get('pending_question') or {}
        return {'version':'2.8-visual-decision-test','status':'needs_clarification','generation_allowed':False,
                'question':p.get('text') or '请先完成当前必要的需求确认。','pending_question':p}
    raw=brief.get('uploaded_images')
    if raw is None:raw=intake.get('assets',[])
    images=[normalize(a,i) for i,a in enumerate(raw)]
    missing=[a['id'] for a in images if a['role'] is None]
    if missing:
        return {'version':'2.8-visual-decision-test','status':'needs_clarification','generation_allowed':False,
                'question':'请确认这些图片是主体、风格参考还是两者都要：'+', '.join(missing)}
    unavailable=[a['id'] for a in images if a['role']!='excluded' and (not a['path'] or a.get('role_source') in ('planned','not_uploaded'))]
    if unavailable:
        return {'version':'2.8-visual-decision-test','status':'needs_clarification','generation_allowed':False,
                'question':'已选择要使用的图片尚未实际提供，请先上传：'+', '.join(unavailable)}
    contents=[a for a in images if a['role'] in ('subject','both')]
    styles=[a for a in images if a['role'] in ('style_reference','both')]
    route_selected=route.get('selected',[])
    atlas_images=[p for s in route_selected for p in s.get('image_paths',[]) if p]
    if styles:
        style_mode='user_style_override'
        atlas_images=[]
    elif atlas_images:
        style_mode='manual_atlas_visual_samples'
    else:
        style_mode='manual_atlas_text_rules_only'
    plans,design_selection=plan_from_route(route,brief)
    photo_policy=build_photo_protection(brief)
    if design_selection.get('needs_verified_numeric_for_explicit_S04'):
        return {'version':'2.8-visual-decision-test','status':'needs_clarification','generation_allowed':False,
                'question':'你指定了 S04 超大数字风，请提供要展示的真实数字（如用户给出的时长、分数或数量），或者换用其他风格。'}
    return {'version':'2.8-visual-decision-test','status':'ready','generation_allowed':True,
        'visual_variants':plans,'style_selection':design_selection,
        'creative_director':'scripts/creative_director_v28.py',
        'creative_decision_version':'2.8',
        'creative_variants':{v['id']:{'visual_story':v['visual_story'],
           'visual_architecture':v['visual_architecture'],
           'non_textual_actions':v['non_textual_actions'],
           'headline_hierarchy':v['headline_hierarchy'],
           'layout_blueprint':v['layout_blueprint']} for v in plans},
        'title_impact_system':'references/title_impact_v271.json',
        'person_photo_protection':photo_policy,
        'person_photo_rule_source':'references/person_photo_protection_v272.json',
        'title_impact_variants':{p['id']:p['title_impact'] for p in plans},
        'quality_review_policy':load_system()['quality_review'],
        'design_principles_source':'references/design_principles/GTA6封面设计原则_V1.0.html',
        'background_strategy':'independent_per_variant',
        'fast_mode':'same_background_three_editable_text_layouts (visual diversity not achieved)',
        'platform':route.get('platform') or intake.get('answers',{}).get('platform'),
        'content_topic':route.get('topic'),'content_inputs':contents,'style_inputs':styles,
        'excluded_inputs':[a for a in images if a['role']=='excluded'],
        'previous_result':brief.get('previous_result'),'atlas_entries':route_selected,
        'atlas_reference_images':atlas_images,'style_reference_source':style_mode,
        'platform_fallback':route.get('status')=='platform_fallback',
        'design_constraints':{
          'keep_title_exact':True,'preserve_subject_identity':True,
          'photo_original_pixels_required_by_default':True,
          'photo_protection_instruction':instruction(brief),
          'content_formula':[x.get('cover_formula') for x in route_selected],
          'A_B_C':'Visual story and independent composition before typography; three real designs, not the same screenshot with a bottom subtitle. User confirmed style reference remains highest among visual styles.',
          'grading':'Preserve the selected style palette. Do not apply the old default pink/purple grade.',
          'truthful_content':'Do not invent game release dates, sale figures, ratings or scores from research examples.'},
        'image_delivery_note':'The output lists local image paths; the host must actually attach/read reference image bytes to enable visual reference. Text-only routing is disclosed when images are unavailable.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--brief',required=True)
    ap.add_argument('--references',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    result=compile_handoff(json.loads(pathlib.Path(args.brief).read_text('utf-8')),
                           json.loads(pathlib.Path(args.references).read_text('utf-8')))
    pathlib.Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result['status'],args.out)

#!/usr/bin/env python3
"""Manual *paired rendered-cover* benchmark. No image assessment happens here.

Input: two sets of user/vision-reviewer scores from actual inspected images,
0..5. Never infer scores from prompts; never claim that the skill wins without
real evidence. A pass is only a provisional within-case comparison.
"""
from __future__ import annotations
import argparse,json,pathlib
FIELDS=('visual_story','non_textual_design','title_hierarchy','composition_depth','content_truth')

def evaluate_pair(data):
    if not isinstance(data,dict) or data.get('actual_images_reviewed') is not True:
        return {'status':'needs_real_images','passed':None,'message':'先提供两张真实封面并由人工/视觉模型观察后评分；不得由本脚本假装已经看过图片。'}
    for label in ('native','with_skill'):
        scores=data.get(label)
        if not isinstance(scores,dict) or set(scores)!=set(FIELDS):
            raise ValueError(label+' 必须包含 '+','.join(FIELDS))
        for k,v in scores.items():
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=5:
                raise ValueError(label+'.'+k+' 应为 0–5')
    n=data['native'];s=data['with_skill'];d={k:round(s[k]-n[k],2) for k in FIELDS}
    points=sum(d.values())
    problems=[]
    if data.get('flat_one_line_subtitle') is True:problems.append('flattened_to_single_subtitle')
    if data.get('unauthorized_person_redraw') is True:problems.append('unconsented_person_regeneration')
    if data.get('fabricated_fact') is True:problems.append('fabricated_content_claim')
    if data.get('same_scene_three_text_variants') is True:problems.append('ABC_has_no_independent_visual_scenes')
    # NOT a quantitative validated user-performance prediction; only a local
    # convenience measure that penalizes clear regression and quality vetoes.
    passed=(points>0 and d['visual_story']>=0 and d['non_textual_design']>0
            and d['title_hierarchy']>=0 and not problems)
    return {'status':'manual_comparison_recorded','passed':passed,
            'dimension_deltas':d,'sum_delta':round(points,2),'vetoes':problems,
            'interpretation':'单组主观视觉配对比较，不代表实际点击率提升或跨模型稳定性',
            'reviewer':str(data.get('reviewer') or 'not_given')}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review',required=True);p.add_argument('--out')
    a=p.parse_args();data=json.loads(pathlib.Path(a.review).read_text('utf8'))
    result=evaluate_pair(data)
    txt=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.out:pathlib.Path(a.out).write_text(txt,encoding='utf8')
    else:print(txt,end='')

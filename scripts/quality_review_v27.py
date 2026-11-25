#!/usr/bin/env python3
"""V2.7 QA rubric evaluator: manual/vision-assessed scores only.
This script does not inspect, see, or judge generated images automatically.
"""
from __future__ import annotations
import argparse,json,pathlib
from style_system_v27 import load_system


def evaluate(review):
    policy=load_system()['quality_review']
    weights=policy['scores']
    if not isinstance(review,dict) or not isinstance(review.get('scores'),dict) or not isinstance(review.get('vetoes'),dict):
        return {'status':'review_required','passed':False,'total':None,
                'message':'需要真实成品图的人工或视觉模型评分；不得将仅生成提示词视为已通过质量审核。'}
    scores=review['scores'];vetoes=review['vetoes']
    if set(scores)!=set(weights):raise ValueError('Score fields must match rubric exactly: '+', '.join(weights))
    for k,maxv in weights.items():
        v=scores[k]
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not 0<=v<=maxv:
            raise ValueError(f'{k} must be 0..{maxv}')
    if set(vetoes)!=set(policy['vetoes']):raise ValueError('Veto fields must match rubric exactly')
    if not all(type(v) is bool for v in vetoes.values()):raise ValueError('Vetoes must be true/false')
    total=sum(scores.values());fired=[k for k,v in vetoes.items() if v]
    passed=total>=policy['threshold'] and not fired
    return {'status':'passed' if passed else 'failed','passed':passed,'total':total,
            'threshold':policy['threshold'],'vetoes_triggered':fired,
            'max_autoretries':policy['max_autoretries'],
            'method':'based_on_supplied_human_or_vision_assessment_not_autoscored'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--review',required=True)
    ap.add_argument('--out')
    a=ap.parse_args()
    review=json.loads(pathlib.Path(a.review).read_text(encoding='utf-8'))
    result=evaluate(review)
    s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.out:pathlib.Path(a.out).write_text(s,encoding='utf-8')
    else:print(s,end='')

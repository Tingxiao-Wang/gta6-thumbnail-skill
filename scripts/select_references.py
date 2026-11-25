#!/usr/bin/env python3
"""V2.6 content-atlas router. Matches platform+content type, not the retired 29-photo database.
Usage: python scripts/select_references.py --platform bilibili --topic 评测
"""
import argparse, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DB=ROOT/'references'/'content_atlas'/'content_atlas_index_v26.json'
def choose(platform,topic,manual_id=None,limit=2):
    data=json.loads(DB.read_text(encoding='utf-8'))
    if platform not in ('bilibili','xiaohongshu','youtube'):
        raise ValueError('Unsupported platform: '+str(platform))
    if platform=='youtube':
        return {'status':'platform_fallback','platform':platform,'topic':topic,'selected':[],
                'image_paths':[],'atlas_source':data['source'],
                'note':'本手册没有YouTube独立案例；使用原YouTube画幅/字效/排版规则。不要声称从新手册选到了YouTube参考图片。'}
    candidates=[c for c in data['cases'] if c['platform']==platform]
    if manual_id:
        matched=[c for c in candidates if c['id']==manual_id]
        if not matched:raise ValueError('Unknown atlas id for '+platform+': '+manual_id)
        candidates=matched
    else:
        q=str(topic or '').lower()
        # Map V2.5.2 gate categories to the new content taxonomy before scoring.
        aliases={
            'bilibili':{'chase':'gameplay','comparison':'review','story':'remix',
                        'reaction':'funny','challenge':'gameplay','cinematic':'remix'},
            'xiaohongshu':{'review':'buying_guide','guide':'buying_guide','comparison':'buying_guide',
                           'story':'story_romance','reaction':'meme','chase':'meme',
                           'cinematic':'screenshot_art','gameplay':'meme'}
        }
        query=aliases.get(platform,{}).get(q,q)
        def score(c):
            keys=c['keywords']+[c['topic'],c['name']]
            return sum((12 if w.lower() in query else 0) for w in keys if len(w)>1) + (4 if c['topic']==query else 0)
        candidates=sorted(candidates,key=lambda x:(-score(x),x['id']))
        # No evidence -> do not fabricate a matching manual visual type.
        candidates=candidates[:1] if candidates and score(candidates[0])>0 else []
    chosen=[]
    for c in candidates:
        available=[]
        if c.get('samples'):
            available=[s['image_path'] for s in c['samples'] if s.get('image_path') and (ROOT/s['image_path']).exists()][:limit]
        elif c.get('image_path') and (ROOT/c['image_path']).exists():
            available=[c['image_path']]
        chosen.append({'id':c['id'],'platform':c['platform'],'topic':c['topic'],
           'name':c['name'],'cover_formula':c['cover_formula'],
           'design_intent':c['design_intent'],'image_paths':available,
           'image_path':available[0] if available else None,
           'visual_reference_available':bool(available),
           'research_status':c['research_status'],
           'sample_kind':c.get('sample_kind','third_party_research_example')})
    return {'status':'atlas_routed','platform':platform,'topic':topic,'selected':chosen,
            'image_paths':[p for c in chosen for p in c['image_paths']],
            'atlas_source':data['source'],
            'note':('未匹配到确切内容类型，应回退到平台/现有构图规则并根据需要询问用户重点。' if not chosen else '手册是用户上传的内容研究，文字规则可用；第三方封面图仅限私人测试，真实模型视觉输入须由宿主实际上传图像。')}
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--platform',required=True,choices=['bilibili','xiaohongshu','youtube'])
    ap.add_argument('--topic',required=True)
    ap.add_argument('--manual-id')
    ap.add_argument('--out')
    args=ap.parse_args()
    out=choose(args.platform,args.topic,args.manual_id)
    s=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
    pathlib.Path(args.out).write_text(s,encoding='utf-8') if args.out else print(s,end='')

#!/usr/bin/env python3
"""Rebuild the V2.6 structured case index from the source HTML.
This script preserves high-value routing tags and does not extract embedded Bilibili images.
For new material, update the section taxonomy carefully before rebuilding.
"""
from bs4 import BeautifulSoup
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
manual=ROOT/'references'/'content_atlas'/'GTA6封面内容参考手册.html'
idx=ROOT/'references'/'content_atlas'/'content_atlas_index_v26.json'
s=BeautifulSoup(manual.read_text('utf-8'),'html.parser')
d=json.loads(idx.read_text('utf-8'))
normalize=lambda x:re.sub(r'\s+',' ',x or '').strip()
for code,t in zip('ABCDEFGH',s.select('.type')):
    c=next(x for x in d['cases'] if x['id']=='bili_'+code)
    c['name']=normalize(t.select_one('h3').get_text(' ',strip=True))
    c['cover_formula']=normalize(t.select_one('.formula').get_text(' ',strip=True)).removeprefix('封面公式')
    c['design_intent']=normalize(t.select_one('.why').get_text(' ',strip=True))
for code,t in zip('ABCDEFG',s.select('.xhs')):
    c=next(x for x in d['cases'] if x['id']=='xhs_'+code)
    c['name']=normalize(t.select_one('.xn b').get_text(' ',strip=True))
    c['cover_formula']=normalize(t.select_one('.xn').get_text(' ',strip=True))
    c['design_intent']=c['cover_formula']
    c['sample_text']=normalize(t.select_one('.big').get_text(' ',strip=True))
idx.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Rebuilt',idx,'cases',len(d['cases']))

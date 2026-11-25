#!/usr/bin/env python3
"""Deterministic GTA Thumbnail Pro design-brief to prompt + editor project.
Offline, Python standard library only. Does NOT call an image generation API.
"""
import argparse, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS = {
 'xiaohongshu': {'xhs34':(1080,1440),'xhs11':(1080,1080)},
 'bilibili': {'bili16':(1920,1080),'bili43':(1200,900)},
 'youtube': {'yt16':(3840,2160),'ytshort':(2160,3840)},
}
RECIPE_DEFAULTS={'xiaohongshu':['F11','F12','F16'],'bilibili':['F01','F02','F09'],'youtube':['F25','F24','F18']}
DEFAULT_PRESET={'xiaohongshu':'xhs34','bilibili':'bili16','youtube':'yt16'}
PRESET_MAP={'cinema':'cinema','reaction':'reaction','review':'review','question':'question','action':'action'}
EDITOR_EFFECTS={
 'cinema':dict(fontFamily='Microsoft YaHei',fontWeight=700,fill='#F7F1DD',stroke='#11171E',strokeWidth=3,shadowBlur=7,shadowColor='#000000'),
 'reaction':dict(fontFamily='Microsoft YaHei',fontWeight=900,fill='#FFDD54',stroke='#080808',strokeWidth=8,shadowBlur=5,shadowColor='#000000'),
 'review':dict(fontFamily='Microsoft YaHei',fontWeight=900,fill='#FFDD54',stroke='#080808',strokeWidth=8,shadowBlur=5,shadowColor='#000000'),
 'question':dict(fontFamily='Microsoft YaHei',fontWeight=900,fill='#FFF1A9',stroke='#121214',strokeWidth=7,shadowBlur=4,shadowColor='#000000'),
 'action':dict(fontFamily='Impact',fontWeight=900,fill='#FFFFFF',stroke='#090B0E',strokeWidth=10,shadowBlur=7,shadowColor='#000000'),
}
POSITIONS={
 'xiaohongshu': {'cinema':(.07,.12,.85,.084),'reaction':(.06,.66,.88,.095),'review':(.07,.20,.87,.105),'question':(.07,.12,.86,.105),'action':(.06,.18,.87,.12)},
 'bilibili': {'cinema':(.07,.12,.72,.09),'reaction':(.06,.68,.78,.112),'review':(.06,.24,.52,.11),'question':(.06,.12,.85,.12),'action':(.55,.25,.4,.13)},
 'youtube':{'cinema':(.06,.15,.66,.09),'reaction':(.05,.65,.75,.11),'review':(.05,.24,.5,.11),'question':(.06,.17,.70,.12),'action':(.55,.24,.4,.14)},
}

def read_json(p):
 with open(p,encoding='utf-8') as f:return json.load(f)

def as_string(obj,key,default=''):
 v=obj.get(key,default)
 if not isinstance(v,str):raise ValueError(f'{key} must be string')
 return v

def verify(b,catalog):
 if not isinstance(b,dict):raise ValueError('brief must be JSON object')
 platform=as_string(b,'platform')
 if platform not in PRESETS: raise ValueError('platform must be xiaohongshu/bilibili/youtube')
 preset=as_string(b,'preset_id',DEFAULT_PRESET[platform])
 if preset not in PRESETS[platform]:raise ValueError('preset_id incompatible with platform')
 style=as_string(b,'style_id','cinematic_poster')
 available={s['id']:s for s in catalog['styles']}
 if style not in available:raise ValueError('unknown style_id: '+style)
 mode=as_string(b,'output_mode','editable')
 if mode not in ('editable','direct_text','no_text'):raise ValueError('output_mode must be editable/direct_text/no_text')
 image_mode=as_string(b,'image_mode','concept')
 if image_mode not in ('concept','screenshot_based_cover','edit_existing'):raise ValueError('invalid image_mode')
 assets=b.get('assets',[])
 if not isinstance(assets,list) or len(assets)>10:raise ValueError('assets must be list up to 10')
 for a in assets:
  if not isinstance(a,dict) or not isinstance(a.get('role'),str) or not isinstance(a.get('description'),str):raise ValueError('invalid asset manifest')
 protected=b.get('protected_elements',[])
 if not isinstance(protected,list) or not all(isinstance(x,str) for x in protected):raise ValueError('protected_elements must be strings')
 for k in ['topic','exact_headline','tag','subtitle','composition_note','color_tone']:
  as_string(b,k)
 if mode=='direct_text' and not as_string(b,'exact_headline'):
  raise ValueError('direct_text requires exact_headline; otherwise choose editable or no_text')
 if len(as_string(b,'exact_headline'))>160:raise ValueError('title too long for a thumbnail')
 gaze=as_string(b,'portrait_gaze','unknown')
 if gaze not in ('left','right','front','unknown'):raise ValueError('portrait_gaze must be left/right/front/unknown')
 gp=as_string(b,'grade_preset','none')
 if gp not in ('vice_sunset','neon_night','cinema_natural','none'):raise ValueError('invalid grade_preset')
 if not isinstance(b.get('grade_intensity',32),(int,float)) or not 0<=b.get('grade_intensity',32)<=100:raise ValueError('grade_intensity must be 0..100')
 return platform,preset,available[style],mode,image_mode

def prompt_for(b,platform,preset,style,mode,image_mode):
 w,h=PRESETS[platform][preset];ratio=f'{w//__import__("math").gcd(w,h)}:{h//__import__("math").gcd(w,h)}'
 asset_lines=['  - '+a.get('id','image_'+str(i+1))+f': {a["role"]} / {a["description"]}' for i,a in enumerate(b.get('assets',[]))]
 protect='、'.join(b.get('protected_elements',[])) or '不凭空捏造特定真实人物或游戏细节'
 topic=b.get('topic') or 'GTA 主题游戏视频'
 title=b.get('exact_headline','')
 text_mode=('只生成无字满版底图；绝对不要生成任何主标题、副标题、角标和随机英文。标题稍后在独立编辑器中添加。'
  if mode=='editable' else ('生成没有任何文字的完整封面。' if mode=='no_text' else f'直接生成精确文字：主标题「{title}」；只允许用户提供的其他文字，中文不能错字、漏字或乱加标点。'))
 if mode=='direct_text':
  if b.get('tag'):text_mode+=' 标签原文「'+b['tag']+'」。'
  if b.get('subtitle'):text_mode+=' 副标题原文「'+b['subtitle']+'」。'
 c=b.get('composition_note') or style['visual_contract']
 tone=b.get('color_tone') or '电影质感、层次清楚、不过度叠加光效'
 from person_photo_protection_v272 import instruction as person_instruction
 image_rule=('必须以用户实际提交的原截图为源图进行二次设计，不允许仅凭文字重新伪造原截图；若生成工具没有收到源图，请停止并提醒上传。' if image_mode!='concept' else '使用原创游戏灵感概念画面，不宣称为真实游戏实机截图。')
 avoid=['不要灰底/白底内嵌截图，不加无意义细边框','不要伪造平台UI、播放量、时长、水印','不要加入未经授权的Logo、主播肖像、官方角色立绘','不要虚构游戏机制、评测事实、奖励或官方消息']+style.get('negative_rules',[])
 parts=[f'【目标】制作面向 {platform} 的 GTA 视频封面；内容：{topic}',f'【画幅】{ratio}，目标工作画布 {w}×{h}；实际输出像素以工具可用能力为准。',f'【创作任务】{image_mode}。{image_rule}', '【素材角色】\n'+('\n'.join(asset_lines) if asset_lines else '未提供可访问图片；不得声称已收到游戏截图或主播照片。'),f'【保护原图】{protect}',person_instruction(b),f'【唯一主风格】{style["name"]}；视觉特征：{style["visual_contract"]}；风格素材指令：{style["prompt_core"]}',f'【空间布局】{c}；画面满版，优先选择真实负空间安放标题，标题不遮挡原图关键人物和地标。',f'【光影二次包装】{tone}。截图应做分层光影与局部信息强化，而不是仅加文字。',f'【文字处理】{text_mode}', '【禁止事项】'+'；'.join(dict.fromkeys(avoid)),'【去AI味审稿】默认不额外生成英文REVIEW/LIVE/PLAY装饰、不绘制无信息作用的横线竖线/斜杠/角标、不叠加无意义图标与多重霓虹描边；保留用户明确指定的标签/副标题/品牌信息，不篡改文案；只有真实攻略指示/双图对比需要时使用少量功能性线或箭头。优先通过留白、主体与光影层次建立设计感。', '【V2.4.2 主标题占比】小红书有主标题时建议字块近似面积≥12%，B站/YouTube建议≥8.5%；这是内部缩略图设计警戒线，不是官方要求。标题太小时优先放大核心提问词、扩充文字负空间，不能无意压住脸、Logo或关键事件；用户明确选择极简/少字时按用户要求。',
 f'【V2.4.2 真人视线布局】朝向{b.get("portrait_gaze","unknown")}；真人视线看左优先位于右侧，看右优先位于左侧，正面时根据标题留白决定；若真实人物当前视线或身体朝外，只能通过移动、裁切原照片与布局补偿，不得重绘眼神、头部或身体姿态。不得反向镜像含文字/标记的人物原图；如果人物已经烘焙到底图无法独立移动，请要求用户提供透明人物层或返回完整重构提示词。',
 f'【V2.4.2 GTA6 视觉统一收尾】版式与人物排好后，按用户指定或默认 {b.get("grade_preset","vice_sunset")}、强度 {b.get("grade_intensity",32)}% 进行原创的轻度色彩统一；热带日落偏粉橙、夜景偏蓝紫、写实偏暖灰。先统一不同图层的肤色与环境光，再叠加独立标题层，勿让滤镜污染可编辑文字。不是官方LUT，避免强行变霓虹、过曝和肤色失真。',
 '【质检】确保比例、主体、信息层级、标题原文真实性；无文字模式不得有任何随机文字。']
 return '\n\n'.join(parts)+'\n'

def layer(text,visible,x,y,width,fs,effects):
 d=dict(visible=bool(visible),text=text,x=x,y=y,width=width,fontFamily='Microsoft YaHei',fontWeight=900,fontSize=fs,fill='#FFFFFF',stroke='#151515',strokeWidth=5,shadowBlur=5,shadowColor='#000000',align='left',letterSpacing=0)
 d.update(effects)
 return d

def project_for(b,platform,preset,style,mode):
 layout=style['editor_preset'];x,y,width,fs=POSITIONS[platform][layout]
 portrait=PRESETS[platform][preset][1]>PRESETS[platform][preset][0]
 if portrait and platform=='youtube': x,y,width,fs=.06,.10,.88,.092
 effects=EDITOR_EFFECTS[layout]
 headline=layer(b.get('exact_headline',''),mode!='no_text' and bool(b.get('exact_headline')),x,y,width,fs,effects)
 tag=layer(b.get('tag',''),mode!='no_text' and bool(b.get('tag')),.06,.06,.48,.042,dict(fontFamily='Microsoft YaHei',fontWeight=700,fill='#FFFFFF',stroke='#10121A',strokeWidth=4,shadowBlur=4,shadowColor='#000000'))
 subtitle=layer(b.get('subtitle',''),mode!='no_text' and bool(b.get('subtitle')),.06,.80,.8,.050,dict(fontFamily='Microsoft YaHei',fontWeight=700,fill='#FFFFFF',stroke='#10121A',strokeWidth=5,shadowBlur=4,shadowColor='#000000'))
 return {'format':'gta-thumbnail-pro-project','version':'1.8.0','platform':platform,'presetId':preset,
         'background':{'zoom':100,'x':0,'y':0,'brightness':100,'contrast':106,'saturation':105,'darken':0,'vignette':22},
         'grade':{'preset':b.get('grade_preset','none'),'intensity':b.get('grade_intensity',0)},
         'portrait':{'direction':b.get('portrait_gaze','unknown'),'x':(.62 if b.get('portrait_gaze','unknown')=='left' else .03),'y':.08,'width':.34,'imageDataUrl':None},
         'layers':{'headline':headline,'tag':tag,'subtitle':subtitle},'userTouched':{'headline':True,'tag':bool(b.get('tag')),'subtitle':bool(b.get('subtitle'))},'imageDataUrl':None}


# V2.4.1: layout coordinates are a separate contract from font recipes.
V241_LAYOUTS=read_json(ROOT/'references/layout_masters_v241.json')['masters']
def split_headline(full,preferred=''):
    full=str(full or '');term=str(preferred or '').strip()
    if not term or term not in full:
        for candidate in ('史一游','GTA6','GTA 6','BUG','真是游戏','值不值','真正','玩法','细节','游戏'):
            if candidate in full:term=candidate;break
    if not term or term not in full:return dict(intro='',focus=full,outro='')
    idx=full.index(term)
    return dict(intro=full[:idx],focus=term,outro=full[idx+len(term):])

def build_blocks(headline,slot,preset,emphasis=''):
    portrait=(preset[1]>preset[0]); region=V241_LAYOUTS[slot]['portrait' if portrait else 'landscape']
    pieces=split_headline(headline['text'],emphasis or headline.get('highlightTerm',''))
    blocks=[]
    for role in ('intro','focus','outro'):
        phrase=pieces[role]
        if not phrase:continue
        g=region[role]
        block={**headline,'role':role,'text':phrase,'x':g['x'],'y':g['y'],'width':g['width'],'fontSize':g['fontSize'],'noWrap':True,'visible':True,'rotation':0,'align':'left','keywordControls':{'scale':1,'dx':0,'dy':0,'rotate':0},'highlightTerm':phrase if role=='focus' else ''}
        if role=='focus':block['fill']=headline.get('highlightFill','#ffdd54');block['fontWeight']=900
        if slot=='B':block['strokeWidth']=min(block['strokeWidth'],4);block['shadowBlur']=min(block['shadowBlur'],5)
        blocks.append(block)
    return blocks



# V2.8: editor headline blocks inherit the creative director's actual spatial
# plan; never use the V2.4.1 A/B/C subtitle coordinates as an overriding layout.
def director_blocks(headline,plan):
    h=plan['headline_hierarchy']
    if h['no_text'] or not h['full_exact']:
        return []
    parts=h['segments'];geo=plan['layout_blueprint']['text_regions']
    assert parts['intro']+parts['focus']+parts['outro']==h['full_exact']
    result=[]
    for role in ('intro','focus','outro'):
        value=parts[role]
        if not value:continue
        x,y,width,font_size=geo[role]
        # Keep the main word striking, but allow long phrases to wrap rather
        # than compressing everything into one thin bottom subtitle.
        if role=='focus':
            font_size=min(.2,max(.10,font_size))
        elif len(value)>10:
            font_size=min(font_size,.070)
        block={**headline,'role':role,'text':value,'x':x,'y':y,
               'width':width,'fontSize':font_size,'noWrap':len(value)<=9,
               'visible':True,'rotation':0,'align':'left',
               'keywordControls':{'scale':1,'dx':0,'dy':0,'rotate':0},
               'highlightTerm':value if role=='focus' else ''}
        if role=='focus':
            block['fill']=headline.get('highlightFill','#FFDD54')
            block['fontWeight']=900
        result.append(block)
    return result

# V2.7.1: editor understands independent headline block size, outline and tilt.
# Conservative geometry cap: preserve exact text, avoid automatic clipping.
def apply_title_impact_blocks(blocks,impact):
    if not impact.get('title_enabled'):return blocks
    focus=next((b for b in blocks if b.get('role')=='focus'),None)
    if focus:
        ratio=max(.85,min(1.5,float(impact.get('target_focus_ratio',1.1))))
        focus['fontSize']=min(.22,float(focus['fontSize'])*ratio)
        focus['rotation']=max(-12,min(12,float(impact.get('tilt_deg',0))))
        focus['strokeWidth']=min(18,max(float(focus.get('strokeWidth',0)),7 if impact['level']!='subtle' else 3))
        focus['shadowBlur']=min(15,max(float(focus.get('shadowBlur',0)),4 if impact['level']!='subtle' else 1))
        focus['fontWeight']=900 if impact.get('title_system') not in ('minimal','cinematic','editorial') else focus.get('fontWeight',700)
        focus['titleImpactStyle']=impact.get('style_id')
    for b in blocks:
        if b.get('role')!='focus':
            b['fontSize']=max(.035,float(b['fontSize'])*(.89 if impact.get('level')=='bold' else .95))
            b['rotation']=0
    return blocks

def pick_cluster(b, platform, catalog):
    options=catalog['platforms'][platform]['clusters']
    chosen=b.get('style_cluster_id')
    if chosen:
        for c in options:
            if c['id']==chosen:return c
        raise ValueError(f'unknown style_cluster_id for {platform}: {chosen}')
    style=b.get('style_id','cinematic_poster')
    if 'cinematic' in style or 'documentary' in style:
        for c in options:
            if 'cinematic' in c['id'] or 'story' in c['id']:return c
    if 'reaction' in style or 'hype' in style:
        for c in options:
            if 'reaction' in c['id'] or 'emotion' in c['id']:return c
    return options[0]

def create_variant_layers(base,platform,preset,font_data):
    import copy
    portrait=PRESETS[platform][preset][1]>PRESETS[platform][preset][0]
    variants={}
    for f in font_data['presets']:
        id=f['id']; d=copy.deepcopy(base); h=d['headline'];t=d['tag'];sub=d['subtitle']
        cfg=f['headline'];rect=f['layout']['portrait' if portrait else 'landscape']
        h.update(x=rect['x'],y=rect['y'],width=rect['width'],fontSize=cfg['fontSize_portrait' if portrait else 'fontSize_landscape'],fontFamily=('SimSun' if re.search(r'[\u3400-\u9fff]',h['text']) else 'Georgia') if id=='B' else cfg['fontFamily'],fontWeight=700 if cfg['fontWeight']==800 else cfg['fontWeight'],fill=cfg['fill'],stroke=cfg['stroke'],strokeWidth=cfg['strokeWidth'],shadowColor=cfg['shadowColor'],shadowBlur=cfg['shadowBlur'],letterSpacing=cfg['letterSpacing'])
        if id=='B': t.update(fontWeight=600,strokeWidth=1,shadowBlur=0);sub.update(fontWeight=400,fontFamily='SimSun',strokeWidth=1,shadowBlur=0)
        elif id=='A':t.update(fontWeight=700,strokeWidth=3,shadowBlur=2);sub.update(fontWeight=700,strokeWidth=3,shadowBlur=2)
        else:t.update(fontWeight=700,strokeWidth=2,shadowBlur=1);sub.update(fontWeight=600,strokeWidth=2,shadowBlur=1)
        if t['text'].strip() in ['GTA · 游戏封面','REVIEW','CINEMATIC'] :t['visible']=False
        variants[id]=d
    return variants

def variant_prompt(b,plat,preset,style,mode,image_mode,font,cluster):
    # If a tool can only generate whole images, each prompt stands alone. For editable work prefer one background and separate text layers.
    effective='direct_text' if b.get('exact_headline') else 'no_text'
    built=prompt_for(b,plat,preset,style,effective,image_mode)
    cfg=font['headline'];layout=font['layout']['portrait' if PRESETS[plat][preset][1]>PRESETS[plat][preset][0] else 'landscape']
    title=b.get('exact_headline') or '(未提供标题，保留无字图)'
    instructions=[f'【三张候选之 {font["id"]}】{font["name"]}；与A/B/C其他候选使用同一主截图、同一准确标题、同一主体场景，不要重生成另一个故事。',f'【参考图风格簇】{cluster["label"]}。{cluster["contract"]}',f'【标题版式】{title}；区域x={layout["x"]:.3f},y={layout["y"]:.3f},width={layout["width"]:.3f}；字体{cfg["fontFamily"]}、字重{cfg["fontWeight"]}、标题颜色{cfg["fill"]}、描边宽度{cfg["strokeWidth"]}；画幅比例按首段。', '【交付】这是完整单张成品图的提示词。若模型无法精确还原文字，改为无字底图后由可视化编辑器叠加文字，不得冒充文字已准确生成。']
    return '\n'.join(instructions)+'\n\n'+built

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--brief',required=True,type=pathlib.Path)
 p.add_argument('--out',required=True,type=pathlib.Path)
 p.add_argument('--variants',type=int,choices=[1,3],default=3,help='Number of design variants; defaults to 3')
 args=p.parse_args(argv)
 try:
  brief=read_json(args.brief)
  # V2.7: prevent legacy compile_brief.py from bypassing the mandatory role/intake gate.
  state=brief.get('intake_state')
  if not isinstance(state,dict) or state.get('generation_allowed') is not True or state.get('pending_question'):
   raise ValueError('V2.7: must pass confirmed intake_state (generation_allowed=true, no pending question); use scripts/intake_gate_v252.py first.')
  for asset in state.get('assets',[]):
   if not isinstance(asset,dict) or asset.get('role') not in ('subject','style_reference','both','excluded') or (asset.get('role')!='excluded' and not (asset.get('path') or asset.get('uri'))):
    raise ValueError('V2.7: unresolved or unavailable image in intake_state; confirm/upload it before compiling.')
  for asset in brief.get('assets',[])+brief.get('uploaded_images',[]):
   if not isinstance(asset,dict) or asset.get('role') not in ('subject','style_reference','both','excluded') or (asset.get('role')!='excluded' and not (asset.get('path') or asset.get('uri') or asset.get('file_id'))):
    raise ValueError('V2.7: image manifest must have a confirmed role and actual image path/uri/file_id.')
  brief.setdefault('grade_preset','none')
  brief.setdefault('grade_intensity',0)
  catalog=read_json(ROOT/'references/style_catalog_v2.json')
  fonts=read_json(ROOT/'references/font_style_presets.json')
  # V2.6.1: the old 29-image cluster database was retired in V2.6.
  clusters=None
  recipe_data=read_json(ROOT/'references/typography_reference_recipes.json')
  hf_effects=read_json(ROOT/'references/typography_effects_v24.json')['effects']
  recipe_map={r['id']:r for r in recipe_data['recipes']}
  recipe_routing=read_json(ROOT/'references/typography_routing_v23.json')
  platform,preset,style,mode,image_mode=verify(brief,catalog)
  # V2.6.1: derive distinct scene plans from the same content atlas.
  # This is the offline prompt compiler; no image API is called.
  sys.path.insert(0,str(ROOT/'scripts'))
  from select_references import choose
  from style_system_v27 import plan_from_route
  from person_photo_protection_v272 import build_photo_protection
  scene_route=choose(platform,brief.get('topic',''))
  scene_plans, design_selection=plan_from_route(scene_route,brief)
  photo_policy=build_photo_protection(brief)
  if photo_policy['has_real_person_photo'] and image_mode=='concept':
   raise ValueError('V2.7.2: 本人真实照片必须采用 screenshot_based_cover/edit_existing 原图合成模式，不能在 concept 模式中重新生成真人。')
  if design_selection.get('needs_verified_numeric_for_explicit_S04'):
   raise ValueError('S04 超大数字风需要用户提供实际可核对的数值，不能自造评分或数字。')
  ids=brief.get('typography_recipe_ids')
  if not ids:
   context=' '.join(str(brief.get(k,'')) for k in ['topic','style_id','composition_note','exact_headline'])
   matched=next((row for row in recipe_routing['triggers_ordered'] if any(word.casefold() in context.casefold() for word in row['keywords'])),None)
   ids=(matched['variants'][platform] if matched else recipe_routing['fallback'][platform])[:args.variants]
  if not isinstance(ids,list) or len(ids)<args.variants or any(x not in recipe_map for x in ids[:args.variants]):
   raise ValueError('typography_recipe_ids must list valid F01–F26 IDs (one for each requested variant)')
  ids=ids[:args.variants]
  project=project_for(brief,platform,preset,style,mode)
  chosen=scene_route.get('selected',[])
  case=chosen[0] if chosen else None
  cluster={'id':case['id'] if case else 'youtube_fallback',
           'label':case['name'] if case else 'YouTube 基础构图',
           'contract':(case['cover_formula']+'。'+case['design_intent']) if case else '根据平台画幅及用户素材选择不同构图，不使用未核实的专属案例。'}
  projects={}
  if args.variants==3:
   import copy
   variants={}
   for id,recipe_id in zip(['A','B','C'],ids):
    r=recipe_map[recipe_id];d=copy.deepcopy(project['layers']);h=d['headline'];f=r['font_recipe'];portrait=PRESETS[platform][preset][1]>PRESETS[platform][preset][0]
    h.update(fontFamily=f['family_preference'][0],fontWeight=f['weight'],fill=f['fill'],stroke=f['stroke'],strokeWidth=f['strokeWidth_at_1080h'],shadowColor=f['shadowColor'],shadowBlur=f['shadowBlur_at_1080h'],letterSpacing=f['letterSpacing'],highlightTerm=brief.get('emphasis_keyword','') if r['emphasis']['max_keywords'] else '',highlightFill=r['emphasis']['fill'],keywordControls={'scale':1,'dx':0,'dy':0,'rotate':0})
    # Never hide explicitly provided titles merely because the reference recipe was logo-only.
    if r['id']=='F21':h['backplateFill']='#FFDD26'
    d['headlineBlocks']=director_blocks(h,scene_plans[['A','B','C'].index(id)])
    d['headlineBlocks']=apply_title_impact_blocks(d['headlineBlocks'],scene_plans[['A','B','C'].index(id)]['title_impact'])
    variants[id]=d
   project.update(version='2.4.2',activeVariant='A',recipeIds=dict(zip(['A','B','C'],ids)),variants=variants,layers=variants['A'])
   projects={k:{**project,'activeVariant':k,'layers':v} for k,v in variants.items()}
  else:
   r=recipe_map[ids[0]];f=r['font_recipe'];portrait=PRESETS[platform][preset][1]>PRESETS[platform][preset][0];pos=r['layout']['portrait' if portrait else 'landscape'];h=project['layers']['headline']
   h.update(x=pos['x'],y=pos['y'],width=pos['width'],fontSize=f['fontSize_portrait' if portrait else 'fontSize_landscape'],fontFamily=f['family_preference'][0],fontWeight=f['weight'],fill=f['fill'],stroke=f['stroke'],strokeWidth=f['strokeWidth_at_1080h'],shadowColor=f['shadowColor'],shadowBlur=f['shadowBlur_at_1080h'],highlightTerm=brief.get('emphasis_keyword',''),highlightFill=r['emphasis']['fill'],keywordControls={'scale':hf_effects[r['id']]['default_keyword_scale'] if r['id'] in hf_effects else 1.15,'dx':0,'dy':0,'rotate':0})
   if r['title_mode'] in ('tiny_label','logo_only'):h['visible']=False
   h['visible']=mode!='no_text' and bool(h.get('text'))
   project['layers']['headlineBlocks']=director_blocks(h,scene_plans[0])
   project['layers']['headlineBlocks']=apply_title_impact_blocks(project['layers']['headlineBlocks'],scene_plans[0]['title_impact'])
   project['version']='2.4.2';project['recipeIds']={'A':ids[0]}

  args.out.mkdir(parents=True,exist_ok=True)
  (args.out/'prompt.txt').write_text('【V2.8 单张主方案】\n'+scene_plans[0]['prompt']+'\n【A/B/C 提示】独立方案请分别读取 prompt-A.txt / prompt-B.txt / prompt-C.txt。\n',encoding='utf8')
  (args.out/'visual-plans.json').write_text(json.dumps(scene_plans,ensure_ascii=False,indent=2),encoding='utf8')
  (args.out/'person-photo-protection.json').write_text(json.dumps(photo_policy,ensure_ascii=False,indent=2),encoding='utf8')
  (args.out/'design-selection.json').write_text(json.dumps(design_selection,ensure_ascii=False,indent=2),encoding='utf8')
  (args.out/'design-brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding='utf8')
  (args.out/'editor-project.json').write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf8')
  if args.variants==3:
   for slot,recipe_id in zip(['A','B','C'],ids):
    recipe=recipe_map[recipe_id]
    scene=scene_plans[['A','B','C'].index(slot)]
    projects[slot]['visualScenePlan']=scene
    projects[slot]['titleImpact']=scene['title_impact']
    (args.out/f'editor-project-{slot}.json').write_text(json.dumps(projects[slot],ensure_ascii=False,indent=2),encoding='utf8')
    # V2.8: make image-story and scene composition the ONLY layout authority.
    # Fxx recipe contributes materials/shape, never a competing position or
    # stock-template prompt (these previously flattened all images).
    fr=recipe['font_recipe']
    recipe_note=(f'【可编辑字体材质建议，仅供后期】F{recipe_id[1:]} {recipe["label"]}；'
                 f'主字体气质：{fr["family_preference"][0]}，字重 {fr["weight"]}；'
                 f'描边色 {fr["stroke"]}，强调色 {recipe["emphasis"]["fill"]}。'
                 '位置、拆字、大小关系全部以 V2.8 的场景及标题层级规划为准；'
                 '不得继承旧版固定 A/B/C 字幕位置。\n')
    (args.out/f'visual-prompt-{slot}.txt').write_text(scene['prompt'],encoding='utf8')
    (args.out/f'prompt-{slot}.txt').write_text(
      '【唯一画面与排版决策来源】V2.8 创意导演；优先做整图设计，再整合标题。\n'
      +scene['prompt']+'\n'+recipe_note,encoding='utf8')
   (args.out/'variant-manifest.json').write_text(json.dumps({'version':'2.8-visual-decision-test','person_photo_protection':photo_policy,'platform':platform,'preset_id':preset,'cluster_id':cluster['id'],'variants':[{'id':slot,'typography_recipe_id':recipe_id,'layout_master':slot,'name':recipe_map[recipe_id]['label'],'renderer':'svg_layers' if recipe_id in hf_effects else 'canvas_compatible','file':f'editor-project-{slot}.json','style_id':scene_plans[['A','B','C'].index(slot)]['style_id']} for slot,recipe_id in zip(['A','B','C'],ids)],'background_strategy':'independent_scene_per_variant','design_system_version':'2.7-test','creative_decision_version':'2.8','style_selection':design_selection,'title_impact_version':'2.7.1','title_impact_variants':{p['id']:p['title_impact'] for p in scene_plans},'visual_variants':[{'id':p['id'],'mode':p['mode'],'name':p['name'],'style_id':p['style_id'],'style_name':p['style_name'],'required_visual_anchors':p['required_visual_anchors'],'qa_status':p['qa_status'],'visual_architecture':p['visual_architecture'],'non_textual_actions':p['non_textual_actions'],'headline_hierarchy':p['headline_hierarchy'],'layout_blueprint':p['layout_blueprint']} for p in scene_plans], 'note':'V2.8 创意导演先设计故事与整图空间，字幕按各自布局拆为三层；Fxx 配方只提供字体材质。实际生图/质量需由宿主完成。'},ensure_ascii=False,indent=2),encoding='utf8')
  print('OK design brief, prompt, editor project'+(' + 3 variants' if args.variants==3 else '')+' ->',args.out)
  print('注意：未生成图片；editor-project.json 不含底图，请在 HTML 编辑器中上传无字底图。')
 except (ValueError,FileNotFoundError,json.JSONDecodeError) as e:
  print('ERROR:',e,file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())

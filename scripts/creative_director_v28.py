#!/usr/bin/env python3
"""V2.8 visual creative director. Deterministic DESIGN DECISION ONLY.

This layer plans visual story, spatial composition, title hierarchy and truthful
assets *before* text rendering. It neither creates images nor grades image quality.
User's V1.0 twelve styles remain a vocabulary, not a rigid template catalog.
"""
from __future__ import annotations
import re
from copy import deepcopy

# Every architecture includes non-text visual work. Optional elements are justified
# by the user's subject and evidence, never invented to decorate the frame.
ARCH = {
 'S01': ('叙事关系', '前后景中的人物或场景建立情绪张力；远景解释发生在哪里',
         ['重排人物与环境的景别关系', '建立明确前中后景层次'], '以人物的姿态、眼神方向与环境对照表达故事氛围'),
 'S02': ('线索聚焦', '主场景承载一个可见的真实疑点，局部镜头解释观众应该看哪里',
         ['突出已提供素材中真实可见的目标', '建立主场景与细节的空间对应'], '让视觉注意力落在能够证实的细节上'),
 'S03': ('两端对照', '两个具有真实依据的对象或角度构成对比，不伪造差异',
         ['重新安排两端主体比例', '构造清晰可见的对照空间'], '通过事实上的差异让问题更值得讨论'),
 'S04': ('数字张力', '只让用户提供或已核实的数字成为图形主体，旁边是相关对象',
         ['将真实数字作为图形体块', '将相关主体与数字建立大小和视线关系'], '从一个真实数字进入观点，不以假评分制造刺激'),
 'S05': ('编辑叙事', '一个占绝对主导的主画面与几个不同功能的次级视觉区域组织信息',
         ['构建大主图与非对称次级画面的层次', '让图像区域承担不同的信息功能'], '视觉上呈现深入研究的层次而不是满屏字幕'),
 'S06': ('文字参与空间', '巨型字形作为构图元素，主体从字形前方或侧方进入场景',
         ['把巨字作为真正的画面图形体块', '设计人物/主体与文字的空间距离或蒙版遮挡'], '让文字像场景的一部分，而不是贴在下沿的字幕'),
 'S07': ('事件瞬间', '异常动作和结果是主角，环境与方向感辅助呈现现场',
         ['突出确实出现的动作形态', '通过景别和斜向动线增强现场感'], '观众不读文字也能理解异常瞬间'),
 'S08': ('资讯编辑', '明确的新闻信息区与事件主体分区，保留来源可核验性',
         ['将新闻与画面分区组织', '使用明确但克制的资讯层级'], '观众第一眼知道消息是什么而非只看到大字'),
 'S09': ('行动路径', '有依据的地图、道具和行动目标构成真实信息图',
         ['使用真实路线/目标数据构图', '设计主目标与步骤的空间关系'], '让观众明白攻略会解决什么问题'),
 'S10': ('出版物编辑', '用刊头、主图、编辑信息区和纸感呈现城市文化',
         ['用出版物网格重新裁切主图', '建立非对称刊头与主体关系'], '设计成为编辑封面，而非游戏画面加粗体字'),
 'S11': ('原生瞬间', '一张真实有传播价值的游戏画面成为绝对焦点',
         ['重新选取和裁切真正有冲击力的瞬间', '利用光线与视觉引导强化事件'], '画面本身就是最强标题，默认允许无字'),
 'S12': ('氛围主题', '一个环境、人物或视觉符号与留白共同传递情绪',
         ['选择明确的低信息区域', '统一背景和主体光影层次'], '通过反常规留白和氛围产生吸引力')
}
# Same style still has three visually different spatial treatments.
COMPOSITIONS = {
 'A': {'id':'asymmetric_dual_focus','name':'非对称主次','scene':'人物/关键物位于右侧或主区域，左侧以真实负空间承接信息；至少一处景别前后关系',
       'text_regions':{'intro':(.055,.105,.43,.055),'focus':(.055,.245,.43,.16),'outro':(.055,.470,.44,.090)},
       'hero_region':(.51,.07,.45,.82),'support_region':(.56,.60,.36,.25)},
 'B': {'id':'editorial_depth','name':'主图+次级画面','scene':'主场景占画面约三分之二，次级区域以不同真实信息或原创概念纹理形成深度，不使用重复截图冒充证据',
       'text_regions':{'intro':(.058,.060,.48,.060),'focus':(.058,.155,.54,.140),'outro':(.058,.790,.76,.085)},
       'hero_region':(.27,.12,.70,.58),'support_region':(.05,.56,.30,.32)},
 'C': {'id':'type_in_space','name':'图形与场景穿插','scene':'主体偏心放大，采用与画面结构发生关系的巨字/图形/局部特写；信息区随场景重新布局，而不是统一下沿字幕',
       'text_regions':{'intro':(.06,.10,.40,.058),'focus':(.34,.12,.59,.220),'outro':(.05,.79,.62,.075)},
       'hero_region':(.14,.12,.65,.75),'support_region':(.79,.38,.17,.38)}
}

# Style-specific visual shot directions, rather than only selecting a palette.
STYLE_SCENES = {
 'S01':('两位相关角色的关系形成前中景；另一端是城市/环境远景', '情节相关的环境以宽幅镜头与人物近景形成对照', '一位主体极近景与另一位远景产生尺度差'),
 'S02':('可见线索的近景与环境全貌同时呈现', '用真实局部视窗和原画位置建立对照', '让特定对象占据画面中心并用背景提供上下文'),
 'S03':('左右两端主体以统一观察尺度并置', '上下层分镜呈现可比对象', '对角线切分，两个对象之间的界线成为视觉节奏'),
 'S04':('真实数字偏左巨大，真实主体偏右', '数字与画面上下错位成为双重焦点', '数字成为背景图形，主体作为前景跨越数字'),
 'S05':('一个大主场景加两个不同主题的小视窗', '一个大场景与横向剪辑条形成纵深', '主视觉居中，围绕其建立非对称编辑信息布局'),
 'S06':('大字在左后景，独立主体位于右前景', '字形在画面上沿成为场景上层，主体从下方进入', '巨字倾斜贯穿画面，主体与字形有前后层次'),
 'S07':('异常动作极近景，环境退到后层', '动作发生之前与结果之间的实据对照', '动作轨迹构成主方向，人物/载具占中前景'),
 'S08':('左侧清晰新闻区，右侧事件主体', '上方消息区配横向实况画面', '主体占大部分空间，来源/时间以真实依据的编辑条排列'),
 'S09':('目标与所在区域并列', '主地图与真实步骤卡片形成上下关系', '路线/目标作为大图形，现实道具作为辅助'),
 'S10':('大刊名与非对称主图', '中间主图加侧栏编辑信息', '纸面网格、错位图块及明确留白'),
 'S11':('单个真实强事件满版构图', '极低角度或高角度的真实瞬间裁切', '从一张真实场景的细节切入高张力局部'),
 'S12':('单一环境的偏心主题与大块静区', '地平线/建筑成为核心视觉结构', '单一象征物与环境尺度对照')
}

# The picture is not allowed to make claims about unverified game plot or features.
MOTIVES = [
 (('解析','考据','剧情','故事','explained','analysis','plot'), '“这期视频将讲清楚什么”', '以角色/事件关系和不同镜头建立叙事，避免虚构具体剧情'),
 (('测评','锐评','值得','review','评价'), '“究竟值得吗/好不好”', '让观点的张力成为画面关系，不必捏造评分'),
 (('彩蛋','秘密','隐藏','发现','secret'), '“到底发现了什么”', '使用用户提供的真实线索对象，无法确认则避免伪造发现'),
 (('攻略','教程','路线','guide'), '“看完能解决什么”', '目标/路径/步骤可视化，但必须有事实依据'),
 (('搞笑','整活','名场面','meme'), '“发生了什么意外”', '用可见动作和人物反应解释梗，不靠装饰标注'),
 (('资讯','预告','官宣','news'), '“什么新信息值得关注”', '让被确认的事件成为中心，不伪装官方快讯')
]

def _text_of(brief):
    return str(brief.get('exact_headline') or (brief.get('intake_state') or {}).get('answers',{}).get('headline_exact') or '')

def split_title(full,preferred=''):
    """Lossless exact-title segmentation; never add hooks, labels, claims or characters."""
    full=str(full or '')
    if not full:return {'intro':'','focus':'','outro':'','reconstructed':''}
    term=str(preferred or '').strip()
    if not term or term not in full:
        matches=([r'\d{1,3}(?:\.\d+)?\s*(?:年|小时|天|GB|元|次)',r'GTA\s*(?:6|VI)'] if any(w in full for w in ('等待','评测','值不值','值得吗')) else [r'GTA\s*(?:6|VI)',r'\d{1,3}(?:\.\d+)?\s*(?:年|小时|天|GB|元|次)']) + [r'万字解析',r'真相',r'秘密',r'值得吗|值不值']
        term=''
        for expr in matches:
            m=re.search(expr,full,flags=re.I)
            if m:term=m.group(0);break
        if not term:
            phrase=re.split(r'[：:，,。?？!！\s]',full)[0]
            term=phrase[:min(6,len(phrase))] or full
    i=full.find(term)
    if i<0:term=full;i=0
    blocks={'intro':full[:i],'focus':term,'outro':full[i+len(term):]}
    blocks['reconstructed']=blocks['intro']+blocks['focus']+blocks['outro']
    assert blocks['reconstructed']==full
    return blocks

def visual_story(brief,content_type):
    target=' '.join((str(brief.get('topic') or ''),_text_of(brief),str(content_type or ''))).lower()
    for cues,question,scene_rule in MOTIVES:
        if any(c in target for c in cues):return {'question':question,'visual_answer':scene_rule}
    return {'question':'“我为什么要点开这个视频”','visual_answer':'让用户明确提供的主体关系和情绪成为第一眼信息，不以普通字幕代替画面'}

def _evidence(brief,style_id):
    state=brief.get('intake_state') or {}
    assets=brief.get('uploaded_images')
    if assets is None:assets=state.get('assets') or brief.get('assets') or []
    active=[a for a in assets if isinstance(a,dict) and a.get('role') in ('subject','both')]
    distinct=len({str(a.get('id') or a.get('path') or a.get('uri')) for a in active})
    supported=bool(distinct)
    if style_id=='S05' and distinct<2:
        return {'asset_count':distinct,'mode':'storyboard_concept_not_evidence',
          'guidance':'当前未提供至少两张不同信息的源画面。可使用一张主素材加原创的抽象编辑图形、纹理/留白来表达解析感；不得把重复裁切称为多个剧情证据，也不得伪造游戏实机。'}
    if style_id in ('S02','S03','S09') and not supported:
        return {'asset_count':distinct,'mode':'concept_only',
          'guidance':'尚无可验证的真实线索/对比/地图素材，使用不宣称为实机事实的原创概念镜头；不能编造具体证据。'}
    return {'asset_count':distinct,'mode':'source_guided' if supported else 'concept_only',
       'guidance':'只对已提供或可验证的画面和信息做事实性描述；不足素材时使用原创概念表达，不冒充真实游戏截图。'}

def build(variant,brief,selection,platform_rec,photo_instruction):
    sid=variant['style_id'];slot=variant['id']
    if sid not in ARCH:raise ValueError('Unrecognized style')
    archetype,principle,actions,meaning=ARCH[sid]
    shot=STYLE_SCENES[sid]['ABC'.index(slot)]
    comp=deepcopy(COMPOSITIONS[slot])
    if sid=='S11':
        # An exceptional native screenshot can be minimalist, but not artificially richer.
        comp['scene']='真实高能事件占满画幅，去掉不必要的字幕层'
    if sid=='S12':
        comp['scene']='一个氛围主题与至少35%低信息量空间形成清楚的对照'
    story=visual_story(brief,selection.get('content_type'))
    title=_text_of(brief)
    no_text=brief.get('no_text') is True or brief.get('output_mode')=='no_text'
    segments=split_title(title,brief.get('emphasis_keyword','')) if not no_text else {'intro':'','focus':'','outro':'','reconstructed':''}
    if no_text: text_plan='用户明确选择无字：不生成文字，使用画面本身表达；不添加随机英文。'
    elif title: text_plan=(f'必须完整使用原文「{title}」。拆成 前导「{segments["intro"]}」／第一视觉主词「{segments["focus"]}」／悬念或解释「{segments["outro"]}」。'+
          '三段在空间、体量、明度上有层级，不得合并成底部一行普通字幕；可分独立可编辑图层，禁止增加用户没提供的角标。')
    else:text_plan='未提供标题：不得编造标题、评分或“全网首发”；画面主体必须能独立传达看点。'
    evidence=_evidence(brief,sid)
    scene=(f'{archetype}。{shot}。{comp["scene"]}')
    protected=variant.get('person_photo_protection') or {}
    photo_locked=bool(protected.get('requires_pixel_preserving_compositing'))
    if photo_locked:
        image_rule='有真实本人照片：必须原像素抠图与合成，背景和元素可改，严禁人像生成；仅无法抠图时须报告能力限制，不得悄悄退化成画中画。'
    else:
        image_rule='保持用户上传的真实主体和身份，只有已提供的真实素材可作为真实内容；无用户素材时使用原创游戏灵感概念画面，不冒充官方GTA6实机或具体剧情；不得编造未给定的事实。'
    ref='用户确认的风格参考优先：其可观察构图、视觉语言和颜色优先；S风格仅作为辅助编排词汇。' if selection.get('user_style_reference_priority') else '从当前风格提取画面组织方法，但不要把风格变成固定模板、单一调色或统一字幕。'
    full=(f'【V2.8 单张完整封面的创意导演指令 · {slot}】\n'
          f'【第一眼要传达的内容】{story["question"]}；画面方式：{story["visual_answer"]}。\n'
          f'【实际画面与视觉关系】{scene}。{meaning}。\n'
          f'【非文字视觉设计动作】{actions[0]}；{actions[1]}。这是必须在画面上完成的重构，不是文字效果。\n'
          f'【层次组织】主体主区域 {comp["hero_region"]}；辅助视觉区 {comp["support_region"]}；区分前景主体、中景关系和背景环境。坐标只作构图草图，必须让真实素材及人物视线优先。\n'
          f'【标题作为整图构图的一部分】{text_plan}\n'
          f'【标题图层参考区域】{comp["text_regions"]}。这不是固定模板；可因人物朝向/文案长度调整。不能再调用旧Fxx三套固定位置覆盖它。\n'
          f'【色彩与气质】{variant["style"]["palette"]}，前景/后景色温和亮度统一；不默认粉紫调色。{ref}\n'
          f'【素材真实性】{evidence["guidance"]}。{image_rule}\n'
          f'【真人原图保护】{photo_instruction}\n'
          f'【文字执行方式】优先让图像生成器生成完整排版的封面；若中文不能准确生成，先生成与三段文字区域匹配的画面，再以独立文字图层精修。无字底图只是中间产物，不能当最终成品交付。\n'
          f'【失败信号】若画面只是原底图+底部一行大字幕、没有上述非文字设计动作或主次关系，本方案不合格；需重新设计画面而不是再加一层特效。\n'
          f'【交付】方案{slot}与另外两种方案要有不同的场景组织/景别，不得共享同一底图仅移动标题。仅在实际看过成品后做质量评分。\n')
    return {'decision_version':'2.8','visual_story':story,'visual_architecture':archetype,
            'creative_intent':meaning,'non_textual_actions':actions,'scene_shot':shot,
            'layout_blueprint':comp,'headline_hierarchy':{'full_exact':title,'segments':segments,'no_text':no_text,
                'label_exact':str(brief.get('tag') or ''),'subtitle_exact':str(brief.get('subtitle') or '')},
            'source_evidence':evidence,'native_baseline_comparison':'pending_rendered_image',
            'manual_visual_review_required':True,'prompt':full}

#!/usr/bin/env python3
"""GTA Thumbnail Pro V2.5.2 conversation intake gate.

A deterministic local reference implementation of the questionnaire. It does not
call image-generation tools or persist state outside a passed JSON file. Host
assistants must apply the same gate before any image call.
"""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDED = json.loads((ROOT / 'references' / 'guided_flow.json').read_text(encoding='utf-8'))
ROLES = {'1':'subject','2':'style_reference','3':'both',
         'subject':'subject','style_reference':'style_reference','both':'both'}
GUIDED_WORDS = ['八步','8步','一步一步','逐步定制','按步骤','带我做','逐步选择','完整定制']
INSTANT_WORDS = ['直接生成','别问','不要问','先出图','马上生成','你决定','你来决定']


def empty_state():
    return {'version':'2.5.2','mode':'assisted','assets':[], 'answers':{},
            'guided_step':1,'pending_question':None,'completed_steps':[],
            'skipped_steps':[],'assisted_question_count':0,
            'generation_allowed':False,'event_log':[]}


def normalized_assets(raw):
    result=[]
    for i,a in enumerate(raw or []):
        a={'path':a} if isinstance(a,str) else dict(a)
        k=a.get('id') or f'image_{i+1}'
        role=a.get('role')
        role=ROLES.get(str(role),None)
        entry={'id':k,'path':a.get('path') or a.get('uri'),'role':role,
               'role_source':('explicit' if role else 'unresolved')}
        # V2.7.2: propagate real-person photo metadata for downstream protection.
        for field in ('asset_kind','image_kind','is_real_person_photo','description','user_description'):
            if field in a: entry[field]=a[field]
        result.append(entry)
    return result


def merge_assets(state,assets):
    known={a['id']:a for a in state['assets']}
    for a in normalized_assets(assets):
        if not a['path']:
            raise ValueError('each uploaded image must include a path')
        if a['id'] in known:
            prev=known[a['id']]
            if prev['path'] != a['path']:
                # A changed file at the same ID is a new unconfirmed asset.
                prev.update(a)
            else:
                # Later host visual inspection may identify a real portrait after
                # the image role has already been confirmed. Never lose that flag.
                for field in ('asset_kind','image_kind','is_real_person_photo','description','user_description'):
                    if field in a:prev[field]=a[field]
                if a['role'] and prev['role'] is None:
                    prev.update(role=a['role'],role_source=a['role_source'])
        else:
            state['assets'].append(a)
            known[a['id']]=a


def role_from_text(text, asset_id):
    n = re.search(r'(\d+)$',asset_id)
    aliases=[asset_id]
    if n:
        aliases.extend([f'图{n.group(1)}', f'image_{n.group(1)}', f'图片{n.group(1)}'])
    for alias in aliases:
        token=re.escape(alias)
        m=re.search(token+r'\s*[=:：]\s*(1|2|3|subject|style_reference|both)\b',text,re.I)
        if m:return ROLES[m.group(1).lower()]
        # Description-based explicit intent for a numbered image.
        if re.search(token+r'[^，。；;\n]{0,12}(做主体|作主体|作为主体|放到封面|用.*人物|用.*车|保留人物|当主图)',text):
            return 'subject'
        if re.search(token+r'[^，。；;\n]{0,14}(参考风格|参考排版|参考字效|作为风格参考|作为参考|做风格参考)',text):
            return 'style_reference'
    return None


def parse_roles(state,text):
    unknown=[a for a in state['assets'] if not a['role']]
    for a in unknown:
        role=role_from_text(text,a['id'])
        if role:
            a.update(role=role,role_source='confirmed')
    unknown=[a for a in state['assets'] if not a['role']]
    if len(unknown)==1:
        if re.search(r'(这张图|这张照片|这张截图|我的照片).{0,14}(作为主体|做主体|作为封面主图|用作封面背景|放到封面|保留人物|保留车辆|做封面|作为封面)',text):
            unknown[0].update(role='subject',role_source='confirmed')
        elif re.search(r'(这张图|这张照片|这张截图).{0,12}(做风格参考|作为风格参考|只参考风格|参考排版|参考字体|学习风格)',text):
            unknown[0].update(role='style_reference',role_source='confirmed')
        pending=state.get('pending_question') or {}
        if pending.get('type')=='image_roles':
            if text.strip() in ('主体','封面主体','作为主体'):unknown[0].update(role='subject',role_source='confirmed')
            elif text.strip() in ('参考图','风格参考','作为风格参考'):unknown[0].update(role='style_reference',role_source='confirmed')
            elif text.strip() in ('两者都要','都要'):unknown[0].update(role='both',role_source='confirmed')
        m=re.fullmatch(r'\s*(1|2|3)\s*',text)
        # Numeric response to a pending image-role question ONLY.
        pending=state.get('pending_question') or {}
        if m and pending.get('type')=='image_roles':
            unknown[0].update(role=ROLES[m.group(1)],role_source='confirmed')
    if state.get('pending_question',{}):
        p=state['pending_question']
        if p.get('type')=='image_roles' and all(a['role'] for a in state['assets']):
            state['pending_question']=None


def parse_basics(state,text):
    ans=state['answers']
    if re.search(r'小红书|xhs|rednote',text,re.I):ans['platform']='xiaohongshu'
    elif re.search(r'B站|哔哩|bilibili',text,re.I):ans['platform']='bilibili'
    elif re.search(r'youtube|油管',text,re.I):ans['platform']='youtube'
    if re.search(r'测评|评测|review',text,re.I):ans['topic']='review'
    elif re.search(r'通缉|追逐|追杀|chase',text,re.I):ans['topic']='chase'
    elif re.search(r'攻略|彩蛋|隐藏',text):ans['topic']='guide'
    elif re.search(r'对比|vs|比较',text,re.I):ans['topic']='comparison'
    elif re.search(r'剧情|电影|故事',text):ans['topic']='story'
    if '标题' in text:
        m=re.search(r'标题\s*(?:是|为|：|:|用|叫)?\s*[「“\"]([^」”\"]+)[」”\"]',text)
        if m:ans['headline_exact']=m.group(1).strip()
    # clear content focus, if user explicitly mentions one
    if re.search(r'画质|驾驶手感|优缺点|值不值得|深度测评|深度评测|车辆性能',text):
        ans['content_angle']=text[:100]
    if re.search(r'电影感|电影海报|电影叙事',text):ans['cover_style']='cinematic_poster'
    elif re.search(r'主播反应|真人反应',text):ans['cover_style']='streamer_reaction'


def answer_pending(state,text):
    p=state.get('pending_question')
    if not p:return False
    if p['type']=='image_roles':
        parse_roles(state,text)
        return state.get('pending_question') is None
    if '上一步' in text and state['mode']=='guided8':
        i=int(p['step'])
        state['guided_step']=max(1,i-1)
        prev_key=GUIDED['steps'][state['guided_step']-1]['key']
        state['answers'].pop(prev_key,None)
        state['completed_steps']=[v for v in state['completed_steps'] if v!=state['guided_step']]
        state['pending_question']=None
        return True
    choices=p.get('choices',[])
    txt=text.strip()
    picked=None
    for item in choices:
        if txt==str(item['number']):picked=item;break
    if picked is None and txt in ['跳过','你推荐','按推荐','自动','使用推荐']:
        picked={'value':'auto','label':'按推荐'}
    if picked is None and txt in INSTANT_WORDS:
        state['mode']='instant';state['pending_question']=None;return True
    if picked is None and txt and not txt.startswith('图'):
        picked={'value':txt,'label':txt}
    if picked is None:return False
    if p['type']=='guided_step':
        k=p['key'];state['answers'][k]=picked['value']
        if p['step'] not in state['completed_steps']:state['completed_steps'].append(p['step'])
        if picked['value']=='auto' and p['step'] not in state['skipped_steps']:state['skipped_steps'].append(p['step'])
        if p['step']==2 and picked['value']=='none':state['answers']['person_present']=False
        if p['step']==2 and picked['value'] in ('source_character','user_authorized_host'):state['answers']['person_present']=True
        if p['step']==8 and picked['value']=='custom':
            # Need actual custom title, not an unfilled placeholder.
            state['answers'].pop('final_headline',None)
            state['completed_steps']=[v for v in state['completed_steps'] if v!=8]
            state['guided_step']=8
        else:state['guided_step']=int(p['step'])+1
    elif p['type']=='assisted':
        k=p['key']
        val=picked.get('value',txt)
        if k=='platform':state['answers']['platform']=val if val in ('bilibili','xiaohongshu','youtube') else 'bilibili'
        elif k=='review_focus':state['answers']['content_angle']=val
        elif k=='video_topic':state['answers']['topic']=val
        state['assisted_question_count']+=1
    state['event_log'].append({'event':'answer','question':p['id'],'selected':picked['value']})
    state['pending_question']=None
    return True


def role_question(state):
    missing=[a for a in state['assets'] if not a['role']]
    if not missing:return None
    if len(missing)==1:
        q=f"{missing[0]['id']} 想如何使用？① 作为封面主体 ② 作为风格参考 ③ 两者都要。回复 1/2/3。"
    else:
        q='请确认以下图片分别用于什么：'+ '、'.join(x['id'] for x in missing) + '。①封面主体 ②风格参考 ③两者都要。可回复「image_1=1，image_2=2」。'
    return {'id':'image_roles','type':'image_roles','text':q,'choices':[],
            'asset_ids':[a['id'] for a in missing]}


def step_is_filled(state,idx):
    ans=state['answers']
    key=GUIDED['steps'][idx-1]['key']
    if key in ans and ans[key] not in (None,''):return True
    aliases={1:'cover_style',2:'person_reference',3:'expression_action',4:'additional_assets',5:'background_tone',6:'font_style',7:'font_effect',8:'headline_exact'}
    if idx==8 and ans.get('headline_exact'):return True
    if idx==1 and ans.get('cover_style'):return True
    if idx==2 and ans.get('person_present') is False:return True
    if idx==3 and ans.get('person_present') is False:return True
    if idx==3 and ans.get('expression_action')=='preserve_source':return True
    return False


def get_guided_question(state):
    for step in GUIDED['steps']:
        idx=step['step']
        if step_is_filled(state,idx):
            if idx not in state['completed_steps']:state['completed_steps'].append(idx)
            continue
        state['guided_step']=idx
        opts=step.get('options',step.get('example_options',[]))
        opts=[{'number':x['number'],'label':x['label'],'value':x.get('value') or x.get('label')} for x in opts]
        txt=f'第 {idx}/8 步｜{step["title"]}\n{step["question"]}'
        if opts:txt+='\n'+'\n'.join(f"{o['number']}. {o['label']}" for o in opts)
        txt+='\n回复序号、直接输入、跳过或说“上一步”。'
        return {'id':f'guided_{idx}','type':'guided_step','step':idx,'key':step['key'],'text':txt,'choices':opts}
    state['guided_step']=9
    return None


def assisted_question(state):
    ans=state['answers']
    if state['assisted_question_count']>=2:return None
    if not ans.get('platform'):
        return {'id':'platform','type':'assisted','key':'platform',
                'text':'这张封面准备发到哪里？①小红书（3:4） ②B站（16:9） ③YouTube（16:9） ④先按通用横版生成。',
                'choices':[{'number':1,'value':'xiaohongshu','label':'小红书'}, {'number':2,'value':'bilibili','label':'B站'},
                {'number':3,'value':'youtube','label':'YouTube'}, {'number':4,'value':'bilibili','label':'通用横版'}]}
    if not ans.get('topic') and not ans.get('headline_exact'):
        return {'id':'video_topic','type':'assisted','key':'video_topic',
                'text':'这期 GTA 视频主要讲什么？①实况/挑战 ②攻略/发现 ③测评/观点 ④先生成中性体验版。',
                'choices':[{'number':1,'value':'chase','label':'实况/挑战'},{'number':2,'value':'guide','label':'攻略/发现'},{'number':3,'value':'review','label':'测评/观点'},{'number':4,'value':'story','label':'中性体验'}]}
    if ans.get('topic')=='review' and not ans.get('content_angle') and not ans.get('headline_exact'):
        return {'id':'review_focus','type':'assisted','key':'review_focus',
                'text':'这期测评最想突出什么？①值不值得玩（疑问式） ②深度评测（画质/玩法） ③优缺点拆解（对比式） ④先按中性综合评测生成。',
                'choices':[{'number':1,'value':'worth_it','label':'值不值得玩'}, {'number':2,'value':'deep_review','label':'深度评测'},
                {'number':3,'value':'pros_cons','label':'优缺点拆解'}, {'number':4,'value':'neutral_review','label':'中性综合评测'}]}
    return None


def evaluate(state,message,assets=None):
    st=copy.deepcopy(state or empty_state())
    for k,v in empty_state().items():st.setdefault(k,copy.deepcopy(v))
    merge_assets(st,assets)
    text=(message or '').strip()
    if st['pending_question']:
        answer_pending(st,text)
    # Explicit per-image roles on a new user message.
    parse_roles(st,text)
    parse_basics(st,text)
    if any(x in text for x in GUIDED_WORDS):st['mode']='guided8'
    elif any(x in text for x in INSTANT_WORDS) and not st['pending_question']:st['mode']='instant'
    elif re.search(r'只改|只修改|上版|上一版|保持上一张',text):st['mode']='edit'
    # Changing a named earlier step.
    change=re.search(r'修改第\s*(\d+)\s*(?:项|步)',text)
    if change and st['mode']=='guided8':
        n=int(change.group(1))
        if 1<=n<=8:
            key=GUIDED['steps'][n-1]['key']
            st['answers'].pop(key,None)
            if n==8:st['answers'].pop('headline_exact',None)
            st['completed_steps']=[v for v in st['completed_steps'] if v!=n]
            st['guided_step']=n;st['pending_question']=None
    rq=role_question(st)
    if rq:
        st['pending_question']=rq;st['generation_allowed']=False
        return {'status':'needs_clarification','generation_allowed':False,'question':rq['text'], 'gate':'image_role','state':st}
    if st['pending_question']:
        st['generation_allowed']=False
        return {'status':'needs_clarification','generation_allowed':False,'question':st['pending_question']['text'],'gate':st['pending_question']['type'],'state':st}
    q=None
    if st['mode']=='guided8':
        # Publishing format is a prerequisite to the eight design steps.
        q=assisted_question(st) if not st['answers'].get('platform') else get_guided_question(st)
    elif st['mode']=='assisted':q=assisted_question(st)
    if q:
        st['pending_question']=q;st['generation_allowed']=False
        st['event_log'].append({'event':'question','id':q['id']})
        return {'status':'needs_clarification','generation_allowed':False,'question':q['text'],'gate':q['type'],'state':st}
    st['generation_allowed']=True
    st['pending_question']=None
    st['event_log'].append({'event':'ready'})
    return {'status':'ready','generation_allowed':True, 'gate':'clear','state':st,
            'next_action':'Use confirmed content/style images and existing layout/typography rules to generate A/B/C.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--state',help='JSON file containing previous conversation state')
    ap.add_argument('--message',required=True)
    ap.add_argument('--assets-json',default='[]',help='JSON string array of newly uploaded images')
    ap.add_argument('--out')
    args=ap.parse_args()
    previous=json.loads(Path(args.state).read_text(encoding='utf-8')) if args.state else None
    if previous and 'state' in previous and 'version' not in previous:
        previous=previous['state']
    attachments=json.loads(args.assets_json)
    result=evaluate(previous,args.message,attachments)
    s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.out:Path(args.out).write_text(s,encoding='utf-8')
    else:print(s)

if __name__=='__main__':main()

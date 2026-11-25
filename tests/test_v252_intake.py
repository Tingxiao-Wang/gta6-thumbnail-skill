import importlib.util
from pathlib import Path

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gate_v252',root/'scripts'/'intake_gate_v252.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

def turn(state,message,assets=None):
    r=gate.evaluate(state,message,assets)
    assert isinstance(r['generation_allowed'],bool)
    if r['status']=='needs_clarification':
        assert not r['generation_allowed'] and r.get('question')
    return r['state'],r

def test(name,call):
    call();print('PASS',name)

def role_block():
    s,r=turn(None,'用这两张图做B站GTA测评', [{'id':'image_1','path':'one.png'},{'id':'image_2','path':'two.png'}])
    assert r['gate']=='image_role' and len(s['assets'])==2
    s,r=turn(s,'直接生成')
    assert r['gate']=='image_role' and not r['generation_allowed']
    s,r=turn(s,'image_1=1，image_2=2')
    assert [a['role'] for a in s['assets']]==['subject','style_reference']
    assert r['gate']=='assisted' and r['question'].startswith('这期测评')
    s,r=turn(s,'2')
    assert r['status']=='ready' and s['answers']['content_angle']=='deep_review'
    s,r=turn(s,'直接生成')
    assert r['status']=='ready' and s['assets'][0]['role']=='subject'

def immediate_clear():
    s,r=turn(None,'B站GTA6五星通缉，标题「五星通缉！」直接生成')
    assert r['status']=='ready'

def vague_review():
    s,r=turn(None,'我要做B站 GTA 测评封面')
    assert r['gate']=='assisted' and '测评' in r['question']
    s,r=turn(s,'1')
    assert r['status']=='ready' and s['answers']['content_angle']=='worth_it'

def one_image_confirmation():
    s,r=turn(None,'我上传了一张图片，请帮我生成封面',[{'id':'image_1','path':'me.png'}])
    assert r['gate']=='image_role'
    s,r=turn(s,'作为主体')
    assert s['assets'][0]['role']=='subject' and r['gate']=='assisted'

def guided_eight():
    s,r=turn(None,'我要在B站按八步一步一步定制GTA封面')
    assert r['gate']=='guided_step' and r['state']['pending_question']['step']==1
    s,r=turn(s,'1')
    assert r['state']['pending_question']['step']==2
    s,r=turn(s,'3')
    assert r['state']['pending_question']['step']==4
    assert s['answers']['person_present'] is False
    for reply,next_id in [('2',5),('1',6),('1',7),('2',8)]:
        s,r=turn(s,reply)
        assert r['state']['pending_question']['step']==next_id
    s,r=turn(s,'1')
    assert r['status']=='ready' and s['guided_step']==9
    assert set(s['completed_steps'])==set(range(1,9))

def prefilled_title_skips_step8():
    s,r=turn(None,'按八步流程做B站GTA封面，标题「史一游来了」')
    assert r['state']['pending_question']['step']==1
    for reply in ['1','3','2','1','1','2']:
        s,r=turn(s,reply)
    assert r['status']=='ready', r
    assert s['answers']['headline_exact']=='史一游来了'

def back_and_change():
    s,r=turn(None,'B站 GTA 逐步定制')
    s,r=turn(s,'1')
    assert r['state']['pending_question']['step']==2
    s,r=turn(s,'上一步')
    assert r['state']['pending_question']['step']==1
    s,r=turn(s,'2')
    assert s['answers']['cover_style']=='streamer_reaction'

def user_style_doesnt_override_subject():
    s,r=turn(None,'图1作主体，图2参考风格，B站游戏追逐封面，标题「逃出全城」',
             [{'id':'image_1','path':'a.png'}, {'id':'image_2','path':'b.png'}])
    assert r['status']=='ready' and s['assets'][0]['role']=='subject' and s['assets'][1]['role']=='style_reference'

def role_reused():
    s,r=turn(None,'B站GTA测评，用图1做主体',[{'id':'image_1','path':'photo.png'}])
    assert r['gate']=='assisted'
    s,r=turn(s,'4')
    assert r['status']=='ready'
    s,r=turn(s,'把文字调大一点')
    assert r['status']=='ready' and s['assets'][0]['role']=='subject'

def fallback_platform():
    s,r=turn(None,'做一个GTA视频封面')
    assert r['gate']=='assisted' and '准备发' in r['question']
    s,r=turn(s,'2')
    assert s['answers']['platform']=='bilibili' and r['gate']=='assisted'
    s,r=turn(s,'4')
    assert r['status']=='ready'

def answer_lock():
    s,r=turn(None,'请按照八步流程制作B站封面，标题「终极测评」')
    assert r['gate']=='guided_step'
    # No edit from ambiguous free text without an answer
    s,r=turn(s,'')
    assert r['gate']=='guided_step'

for n,f in [
    ('ambiguous multiple images always block, confirmation persists',role_block),
    ('clear instant request directly generates',immediate_clear),
    ('review focus must be asked',vague_review),
    ('single image natural language role answer',one_image_confirmation),
    ('guided eight steps, no-human skip',guided_eight),
    ('known headline skips last step',prefilled_title_skips_step8),
    ('back navigates and changes state',back_and_change),
    ('explicit per-image mixed roles',user_style_doesnt_override_subject),
    ('answered roles not asked again',role_reused),
    ('unknown platform then topic',fallback_platform),
    ('empty reply cannot advance',answer_lock)
]:test(n,f)
print('11 scenario tests passed')

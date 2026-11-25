"""V2.7.2 regression: uploaded self-portrait is composited, never silently regenerated."""
from pathlib import Path
import sys,json,tempfile,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from person_photo_protection_v272 import build_photo_protection,instruction
from compile_reference_handoff import compile_handoff
from select_references import choose
from style_system_v27 import plan_from_route
from quality_review_v27 import evaluate

photo={'id':'me1','role':'subject','path':'me_photo.jpg','asset_kind':'real_person_photo','description':'我的本人照片'}
state={'generation_allowed':True,'pending_question':None,'answers':{'platform':'bilibili','headline_exact':'13年的等待，值得吗？'},'assets':[photo]}
brief={'intake_state':state,'topic':'GTA6评测','exact_headline':'13年的等待，值得吗？','title_impact_level':'bold','requested_style':'S06'}
route=choose('bilibili','GTA6评测')
lock=build_photo_protection(brief)
assert lock['has_real_person_photo'] and lock['entries'][0]['mode']=='preserve_original_pixels'
assert lock['requires_pixel_preserving_compositing']
assert '严禁重新生成或替换人脸' in instruction(brief)
plans,sel=plan_from_route(route,brief)
assert len(plans)==3 and [p['style_id'] for p in plans]==['S06']*3
assert all('本人真实照片不得无授权重绘' in p['prompt'] and '人物原始像素' in p['prompt'] for p in plans)
handoff=compile_handoff(brief,route)
assert handoff['status']=='ready' and handoff['person_photo_protection']['entries'][0]['mode']=='preserve_original_pixels'
assert all(p['person_photo_protection']['has_real_person_photo'] for p in handoff['visual_variants'])
# "more cinematic" is not approval, even with person_regeneration_approval metadata.
generic={**brief,'person_regeneration_approval':{'approved':True,'asset_ids':['me1'],'allowed_changes':['change_face'],'explicit_user_request':'再更有电影感一点'}}
assert build_photo_protection(generic)['entries'][0]['mode']=='preserve_original_pixels'
# The actual direct request must specify portrait transformation and exact asset scope.
consent={**brief,'person_regeneration_approval':{'approved':True,'asset_ids':['me1'],'allowed_changes':['anime_stylization'],'explicit_user_request':'把我这张照片变成动漫角色'}}
assert build_photo_protection(consent)['entries'][0]['mode']=='scoped_regeneration_allowed'
assert '仅限 anime_stylization' in instruction(consent)
assert build_photo_protection({**consent,'person_regeneration_approval':{**consent['person_regeneration_approval'],'asset_ids':['not-me']}})['entries'][0]['mode']=='preserve_original_pixels'
# Style-only real-person photo is not a subject to be used/re-created.
style_only={**photo,'role':'style_reference'}
assert build_photo_protection({'intake_state':{**state,'assets':[style_only]}})['has_real_person_photo'] is False
# Intake metadata survives deterministic state merge.
from intake_gate_v252 import normalized_assets
assert normalized_assets([photo])[0]['asset_kind']=='real_person_photo'
# The old compiler also produces locked prompts and policy and rejects concept mode.
with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp);base={'platform':'bilibili','preset_id':'bili16','style_id':'cinematic_poster','topic':'GTA6评测',
        'exact_headline':'13年的等待，值得吗？','tag':'','subtitle':'','composition_note':'','color_tone':'',
        'output_mode':'editable','assets':[],'protected_elements':[],'intake_state':state}
    f=t/'in.json';o=t/'out'
    for mode,expected in [('concept',2),('screenshot_based_cover',0)]:
        f.write_text(json.dumps({**base,'image_mode':mode},ensure_ascii=False),'utf-8')
        run=subprocess.run([sys.executable,str(ROOT/'tools/compile_brief.py'),'--brief',str(f),'--out',str(o)],capture_output=True,text=True)
        assert run.returncode==expected,(mode,run.stdout,run.stderr)
    assert json.loads((o/'person-photo-protection.json').read_text('utf-8'))['has_real_person_photo']
    m=json.loads((o/'variant-manifest.json').read_text('utf-8'))
    assert m['person_photo_protection']['entries'][0]['mode']=='preserve_original_pixels'
    assert all('本人真实照片不得无授权重绘' in (o/f'prompt-{x}.txt').read_text('utf-8') for x in 'ABC')
# Manual QA veto flags a rendered fake even with perfect scores.
from style_system_v27 import load_system
w=load_system()['quality_review']['scores']
v={k:False for k in load_system()['quality_review']['vetoes']}
v['unconsented_real_person_recreation']=True
assert evaluate({'scores':w,'vetoes':v})['status']=='failed'
print('PASS V2.7.2 photo preservation: default lock, A/B/C, handoff, legacy compiler, explicit scoped consent, QA veto')

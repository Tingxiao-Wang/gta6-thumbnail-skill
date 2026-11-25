#!/usr/bin/env python3
"""V2.7.2 real-person photo preserve-original policy.

Only routes metadata and produces instructions. It does NOT inspect image pixels,
separate people from backgrounds, or enforce host image generator pixel fidelity.
Host must identify real-person photos via the uploaded image/user statement and
mark asset_kind=real_person_photo; missing flags are not proof of no people.
"""
from __future__ import annotations
import re

KINDS={'real_person_photo','self_photo','portrait_photo','real_photo_of_person',
       'real_human_photo','user_portrait','host_photo','real_person'}
PHOTO_MARKERS=('本人照片','我的照片','我的自拍','自拍照','真人照片','真人肖像','真人出镜',
               '主播照片','人物实拍','个人写真','real person photo','portrait photo',
               'my selfie','photo of me','photo of myself')
TRANSFORM_MARKERS=('重新生成我的形象','重绘我的人物','重绘我','重新画我','改我的脸','换我的脸',
                   '修改我的五官','改变我的发型','给我换发型','改我的身材','换我的衣服',
                   '把我变成动漫','把我画成动漫','把我变成卡通','把我变成游戏角色',
                   '将我的照片动漫化','把我这张照片变成动漫','把这张照片中的我变成动漫','把我这张照片画成动漫','照片转动漫','照片转卡通','真人变动漫','真人变卡通',
                   'regenerate my face','redraw me','turn me into anime',
                   'turn my photo into','change my hairstyle','change my face',
                   'change my body','stylize my portrait')

def all_assets(brief):
    state=(brief.get('intake_state') or {})
    all_items={}
    for raw in (state.get('assets') or [], brief.get('assets') or [], brief.get('uploaded_images') or []):
        for i,item in enumerate(raw):
            if not isinstance(item,dict):continue
            key=str(item.get('id') or f'image_{i+1}')
            all_items[key]={**all_items.get(key,{}),**{k:v for k,v in item.items() if v is not None}}
    return list(all_items.values())

def is_real_person_photo(asset):
    k=str(asset.get('asset_kind') or asset.get('image_kind') or asset.get('kind') or '').lower()
    if k in KINDS:return True
    if asset.get('is_real_person_photo') is True:return True
    desc=' '.join(str(asset.get(x) or '') for x in ('description','user_description','filename_context')).lower()
    return any(marker in desc for marker in PHOTO_MARKERS)

def approval_for(brief,asset_id):
    approval=brief.get('person_regeneration_approval') or {}
    if not isinstance(approval,dict):return None
    if approval.get('approved') is not True:return None
    ids=approval.get('asset_ids') or []
    if not isinstance(ids,list) or str(asset_id) not in [str(x) for x in ids]:return None
    changes=approval.get('allowed_changes') or []
    if not isinstance(changes,list) or not changes or not all(isinstance(x,str) and x.strip() for x in changes):return None
    quote=str(approval.get('explicit_user_request') or '').lower().strip()
    # No inferred consent from generic "make it cooler", subject use or a style selection.
    if not quote or not any(term in quote for term in TRANSFORM_MARKERS):return None
    # Host must quote real user text, not synthesize authorization.
    return {'asset_id':str(asset_id),'allowed_changes':changes,'explicit_user_request':quote}

def build_photo_protection(brief):
    assets=all_assets(brief)
    found=[a for a in assets if is_real_person_photo(a) and a.get('role') in ('subject','both','host_reference')]
    entries=[]
    for a in found:
        approved=approval_for(brief,a.get('id'))
        entries.append({'asset_id':str(a.get('id')),'source_path':a.get('path') or a.get('uri') or a.get('file_id'),
                        'mode':'scoped_regeneration_allowed' if approved else 'preserve_original_pixels',
                        'allowed_changes':approved['allowed_changes'] if approved else [],
                        'explicit_user_request':approved['explicit_user_request'] if approved else None})
    return {'version':'2.7.2','has_real_person_photo':bool(entries),
            'default':'preserve_original_pixels_no_person_regeneration',
            'entries':entries,
            'host_must_detect_people':'Inspect actual uploaded images and mark asset_kind=real_person_photo for true user/person portraits; metadata alone is not an image classifier.',
            'requires_pixel_preserving_compositing':any(e['mode']=='preserve_original_pixels' for e in entries),
            'quality_review':'Any unauthorized replacement, re-generated likeness, face/hairstyle/body reshape or identity drift is a veto.'}

def instruction(brief):
    rule=build_photo_protection(brief)
    if not rule['entries']:
        return ('【V2.7.2 真人照片保护】若宿主实际识别到用户上传的真人/本人照片，必须将它标记为 real_person_photo 并默认以原图图层合成；'
                '不能因为元数据未标记就推断可以重绘真人。风格参考图中的真人不应被复制为成品人物。')
    parts=['【V2.7.2 最高优先级：本人真实照片不得无授权重绘】']
    for e in rule['entries']:
        if e['mode']=='preserve_original_pixels':
            parts.append('照片 '+e['asset_id']+'：只允许保留真实照片的人物原始像素，做非生成式抠图/裁切/缩放/移位/叠加文字/独立背景与色光适配。'
                         '严禁重新生成或替换人脸、五官、发型、服饰、身材、表情和姿态；不得把原照片当作生成相似人物的参考。')
        else:
            parts.append('照片 '+e['asset_id']+'：用户已明确请求的修改仅限 '+ '、'.join(e['allowed_changes']) +
                         '；未授权的面部、发型、身形或其他形象重绘仍须保留原照片。')
    parts.append('A/B/C 三张方案必须复用同一原始真人照片图层，仅改变真人外部的背景、构图、图文和可添加元素。'
                 '不能用生成三张新人物图的方式模拟 A/B/C。若宿主的生图编辑会整体重绘并无法保证人物像素原样，停止真人再生成，'
                 '改用无真人的背景单独生图 + 原照片蒙版合成/离线编辑；做不到时说明限制，不得声称保留了原照片。'
                 '即使用户要求“更酷、更电影感、加强冲击力”也不等于授权改变其真实形象。')
    return '\n'.join(parts)

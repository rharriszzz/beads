"""Freeze real-photo cases BEFORE detector implementation. No segmentation imports."""
import hashlib
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from photo2.bead_detection.brightness_r270 import linearize
from .common import *

CATEGORIES = {
 'separated-red': ['T1','T2','T3','T7','T8'],
 'separated-yellow': ['T1','T2','T3','T7','T8'],
 'touching-same-color': ['T1','T2','T4','T5','T7'],
 'touching-different-color': ['T1','T2','T3','T6','T7'],
 'multiple-highlights': ['T2','T4','T5','T7'],
 'bright-near-boundary': ['T1','T2','T6','T8'],
 'diffuse-illumination': ['T1','T2','T3','T8'],
 'weak-illumination': ['T1','T3','T7','T8'],
 'internal-darkness-or-hole': ['T1','T2','T5','T7'],
 'occlusion': ['T2','T3','T6','T7'],
 'dark-neighbor-seam': ['T1','T2','T4','T5'],
 'colored-beside-black': ['T1','T3','T6','T8'],
 'black-reflection': ['T1','T3','T4','T5','T8'],
 'paper-adjacency': ['T1','T2','T3','T6'],
 'historical-merger': ['T1','T2','T4','T5'],
 'historical-truncation': ['T1','T2','T3','T7'],
 'historical-tail': ['T1','T2','T3','T7'],
 'historical-missing-boundary': ['T1','T2','T6','T7']}

def main():
    if (EVIDENCE/'collection.json').exists():
        raise RuntimeError('Collection already frozen; do not overwrite.')
    native,rgb,meta=photo();lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722])
    features=[r for r in read(ROOT/'photo2/r289/results/photo-landmarks.json.gz')['records'] if r['accepted']]
    cases=[];missing=[]
    def add(name,xy,tags,source,split='development',exact=None):
        q=next((q for q in features if q['id']==exact),None) if exact else min(features,key=lambda q:np.linalg.norm(np.array(q['point'])-xy))
        distance=float(np.linalg.norm(np.array(q['point'])-xy)) if q else None
        if q is None or distance>20:
            missing.append(dict(name=name,xy=xy,reason='No accepted R289 feature within20px; no invented seed.'));return
        cases.append(dict(case_id=name,feature=q,selection_anchor=list(map(float,xy)),anchor_distance_px=distance,
                          split=split,categories=tags,selection_source=source,category_certification='Historical mechanism or automatic proxy; user confirmation pending.',tests=list('T'+str(i) for i in range(1,9))))
    old=read(ROOT/'photo2/r285/results/selection.json')['development']
    bank={q['id']:q for q in read(ROOT/'photo2/r285/results/development.json.gz')['observations']}
    for name,ex,tags in [('P1','e01',['historical-tail','touching-different-color','paper-adjacency']),('P2','e02',['historical-truncation','diffuse-illumination','colored-beside-black']),('P3','e04',['historical-tail','occlusion']),('P4','e07',['black-reflection']),('P5',None,['multiple-highlights','historical-merger','touching-same-color','dark-neighbor-seam'])]:
        xy=[1642,2980] if ex is None else bank[next(q['observation_id'] for q in old if q['example']==ex)]['seed']
        add(name,xy,tags,'R285/R286 named user-reviewed photographic case')
    for stage in ('development','confirmation'):
        for q in read(ROOT/f'photo2/r288/results/{stage}.json.gz')['cases']:
            if q['name'] in ('N06','N07','N11','C05','Q14','Q06'):
                add(q['name'],q['seed'],['historical-merger','dark-neighbor-seam','touching-same-color'] if q['name'] in ('N06','Q06') else ['historical-truncation','diffuse-illumination','historical-missing-boundary'],f'R288 {stage} {q["name"]}')
    for q in read(ROOT/'photo2/r289/results/review-manifest.json'):
        if q['name'] in ('red-worst','yellow-worst','red-multiple','yellow-multiple'):
            for i,hid in enumerate(q['matches']):
                f=next(f for f in features if f['id']==hid)
                add(q['name']+(f'-{i+1}' if len(q['matches'])>1 else ''),f['point'],['multiple-highlights','internal-darkness-or-hole'] if 'multiple' in q['name'] else ['bright-near-boundary','historical-truncation'],f'R289 {q["name"]}; reference ownership not inferred from centroid',exact=hid)
    for name,xy,tags in [('R215-A',[964,2722],['diffuse-illumination','internal-darkness-or-hole']),('R215-B',[2231,2234],['touching-different-color','occlusion']),('R215-R',[975,2301],['black-reflection']),('R265-R00956',[976,2668],['bright-near-boundary','touching-same-color','historical-missing-boundary']),('R284B-upper-black',[517,1582],['black-reflection','colored-beside-black']),('R284B-lower-black',[515,1594],['black-reflection','multiple-highlights'])]:
        add(name,xy,tags,'Original historical photographic coordinates; nearest independent R289 feature <=20px, selection only')
    h,w=lum.shape
    def rank(q):return hashlib.sha256(('R290-collection:'+q['id']).encode()).hexdigest()
    def far(q,dist):return all(np.linalg.norm(np.array(q['point'])-c['feature']['point'])>=dist for c in cases)
    # Central means the interior image rectangle, not an inferred bead/string identity.
    for split,count in [('development',8),('reserved',8)]:
        for color in ('red','yellow'):
            for i in range(count):
                pool=[]
                for q in features:
                    x,y=q['point']
                    if q['color']!=color or not (.12*w<x<.88*w and .12*h<y<.88*h) or not far(q,110):continue
                    exposure=float(np.median(lum[y-5:y+6,x-5:x+6]))
                    if exposure<.025:continue
                    pool.append(q)
                if not pool:
                    missing.append(dict(name=f'{split}-{color}-{i}',reason='Unfilled independent central bright stratum'));continue
                q=min(pool,key=rank);p=np.array(q['point']);near=[f for f in features if f['id']!=q['id'] and np.linalg.norm(np.array(f['point'])-p)<32]
                tags=['diffuse-illumination']
                if not near:tags+=['separated-'+color]
                if any(f['color']==color for f in near):tags+=['touching-same-color','multiple-highlights']
                if any(f['color'] not in (color,'unknown') for f in near):tags+=['touching-different-color','occlusion']
                if any(f['color']=='unknown' for f in near):tags+=['colored-beside-black']
                add(f'{split}-{color}-{i+1:02}',q['point'],tags,'SHA256(R290-collection:featureID) rank; central12–88%; median11Y>=.025; >=110px from earlier cases; neighbor tags are <=32px proxies',split,q['id'])
    for i in range(4):
        pool=[q for q in features if q['color']=='unknown' and far(q,110)]
        if not pool:break
        q=min(pool,key=rank);add(f'diagnostic-{i+1:02}',q['point'],['black-reflection','weak-illumination','paper-adjacency'],'Hash-ranked unknown-context feature; black/paper classification is unconfirmed proxy','reserved' if i%2 else 'development',q['id'])
    source=['photo2/r289/results/photo-landmarks.json.gz','photo2/r289/results/review-manifest.json','photo2/r285/results/selection.json','photo2/r285/results/development.json.gz','photo2/r288/results/development.json.gz','photo2/r288/results/confirmation.json.gz','photo2/r290/evidence/tests.json','photo2/r290/select.py']
    save(EVIDENCE/'collection.json',dict(schema='R290-collection-v1',photo=meta,cases=cases,missing_selection=missing,categories=CATEGORIES,source_hashes={s:sha(ROOT/s) for s in source},reserved_policy='No reserved crop/result inspection until frozen detector; >=110px from all development case features; postfreeze no retuning.',missing_coverage=['Exact pixel ground truth, certified complete boundaries, physical hole identity, true occluder identity and trustworthy centroid truth are unavailable.','Automatic separated/touching/occlusion/black/paper tags are selection proxies awaiting batch review.']))
    # Historical byte manifest; audit excludes only new R290 files and ongoing handoff metadata.
    paths=subprocess.check_output(['git','ls-files','photo2'],text=True).splitlines()
    save(EVIDENCE/'historical-hashes.json.gz',{s:sha(ROOT/s) for s in paths if not s.startswith(('photo2/r290/','photo2/review/r290/','photo2/R290'))})
    # ONLY development crops opened prior to algorithm freeze.
    dev=[c for c in cases if c['split']=='development'];sheet=Image.new('RGB',(700,((len(dev)+6)//7)*125),'#eee');d=ImageDraw.Draw(sheet)
    for i,c in enumerate(dev):
        x,y=c['feature']['point'];crop=Image.fromarray(native[y-24:y+25,x-24:x+25]).resize((98,98),Image.Resampling.NEAREST)
        sheet.paste(crop,((i%7)*100,(i//7)*125));d.text(((i%7)*100,(i//7)*125+98),c['case_id'][:16],fill='black')
    EVIDENCE.mkdir(parents=True,exist_ok=True);sheet.save(EVIDENCE/'development-contact.png')
    print('Frozen',len(cases),'cases;',sum(c['split']=='reserved' for c in cases),'reserved;',len(missing),'unfilled')

if __name__=='__main__':main()

"""Independent POV benchmark. Truth is opened only after photo-only inference."""
from collections import Counter
import numpy as np
from PIL import Image
from photo2.r280.synthetic import render
from photo2.r280.geometry import certify,INDICES
from .common import OUT,read,save,sha,pixels
from .ownership import detect,audit


def baseline(rows):
    from copy import deepcopy
    rows=deepcopy(rows);owned=set()
    for r in sorted(rows,key=lambda a:(-a['phase1_reliability'],a['record_id'])):
        if r['status']=='rejected':continue
        p=set(map(tuple,pixels(r['measured_support'])));foreign=len(p&owned)
        if foreign>max(4,.12*len(p)):r['status']='unresolved'
        else:owned|=p
    return rows


def evaluate(rows,truth,classes):
    # Eligible bodies have >=40 visible native pixels and a visible centroid in
    # the detector's 24px crop margin. Deep shadow is NOT removed from recall.
    eligible=[];centroids={}
    for j in range(29):
        yy,xx=np.where(truth==j);centroids[j]=np.array([xx.mean(),yy.mean()]) if len(xx) else None
        if len(xx)>=40 and 24<=xx.mean()<296 and 24<=yy.mean()<200:eligible.append(j)
    hits=[]
    for r in rows:
        if r['status']!='high':continue
        p=pixels(r['measured_support']);vals=truth[p[:,1],p[:,0]];counts=Counter(vals.tolist());body,n=max(counts.items(),key=lambda kv:kv[1]);purity=n/len(p)
        correct=body>=0 and purity>=.95
        color=('red','yellow','black')[classes[body]] if body>=0 else 'background'
        hits.append(dict(id=r['record_id'],owner=int(body),purity=purity,correct_support=bool(correct),
            color_correct=r['color']==color,observed_color=r['color'],truth_color=color,
            centroid_visible_body_offset=float(np.linalg.norm(p.mean(0)-centroids[body])) if body>=0 else None,
            centroid_on_owner=bool(truth[tuple(np.rint(p.mean(0)).astype(int)[::-1])]==body) if body>=0 else False))
    owned=Counter(h['owner'] for h in hits if h['correct_support']);unique=set(owned)
    return dict(eligible=eligible,eligible_colors=Counter(('red','yellow','black')[classes[j]] for j in eligible),
        hits=hits,high=len(hits),correct_support=sum(h['correct_support'] for h in hits),
        distinct_correct=len(unique),duplicates=sum(n-1 for n in owned.values()),
        false_or_wrong_body=sum(not h['correct_support'] for h in hits),
        detected_eligible=len(unique&set(eligible)),missed_eligible=sorted(set(eligible)-unique),
        recall=len(unique&set(eligible))/len(eligible) if eligible else None,
        support_precision=sum(h['correct_support'] for h in hits)/len(hits) if hits else None,
        unique_precision=len(unique)/len(hits) if hits else None,
        color_correct=sum(h['color_correct'] for h in hits if h['correct_support']))


def main():
    import os
    seed=int(os.environ.get('R283_SYNTHETIC_SEED','283601'));split=os.environ.get('R283_SYNTHETIC_SPLIT','confirmation')
    freeze=read(OUT/'method-freeze.json');rng=np.random.default_rng(seed);results=[]
    for s in range(16):
        folder=OUT/split/f'scene-{s:02}';folder.mkdir(parents=True,exist_ok=True)
        p=dict(hand=(-1,1)[s%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=(1.12,1.16,1.20,1.24)[s%4],
            inclination=float(rng.uniform(-32,32)),roll=float(rng.uniform(-30,30)),scale=float(rng.uniform(8,10)),
            translation=[159.5,111.5],light=[float(rng.uniform(-.8,.8)),-.8,1.],light_power=1.1,
            specular=(1.2,.5,.12,1.8)[s%4],roughness=(.025,.06,.1,.035)[s%4],ambient=(.1,.06,.03,.13)[s%4],
            background=[.47,.31,.43])
        classes=rng.integers(0,3,29);classes[10:15]=s%3
        cert=certify(p);assert cert['certified']
        if not (folder/'photo.png').exists():render(folder,p,classes)
        rgb=np.asarray(Image.open(folder/'photo.png').convert('RGB'))
        starts,features=detect(rgb);before=baseline(starts);after,pairs=audit(before,features)
        # Inference is serialized before rendering/opening ownership truth.
        save(folder/'inference.json.gz',dict(before=before,after=after,pairs=pairs))
        if not (folder/'identity.png').exists():render(folder,p,classes,True)
        truth=np.asarray(Image.open(folder/'identity.png'))[:,:,0].astype(int)-1
        save(folder/'truth.json',dict(parameters=p,classes=classes.tolist(),certificate=cert,
            photo_sha256=sha(folder/'photo.png'),identity_sha256=sha(folder/'identity.png')))
        res=dict(scene=s,before=evaluate(before,truth,classes),after=evaluate(after,truth,classes))
        results.append(res);print('synthetic',s,'before',res['before']['high'],res['before']['false_or_wrong_body'],'after',res['after']['high'],res['after']['false_or_wrong_body'],flush=True)
    summary={}
    for method in ('before','after'):
        rr=[r[method] for r in results];n=sum(r['high'] for r in rr);eligible=sum(len(r['eligible']) for r in rr)
        hh=[h for r in rr for h in r['hits']];correct=sum(r['correct_support'] for r in rr)
        summary[method]=dict(high=n,eligible=eligible,correct_support=correct,
            support_precision=correct/n if n else None,distinct_precision=sum(r['distinct_correct'] for r in rr)/n if n else None,
            duplicates=sum(r['duplicates'] for r in rr),false_or_wrong_body=sum(r['false_or_wrong_body'] for r in rr),
            detected_eligible=sum(r['detected_eligible'] for r in rr),recall=sum(r['detected_eligible'] for r in rr)/eligible,
            color_accuracy=sum(r['color_correct'] for r in rr)/max(1,correct),
            centroid_median_offset_visible_body=float(np.median([h['centroid_visible_body_offset'] for h in hh if h['correct_support']])),
            per_color={c:dict(high=sum(h['truth_color']==c for h in hh),correct=sum(h['truth_color']==c and h['correct_support'] for h in hh),
                eligible=sum(r['eligible_colors'].get(c,0) for r in rr),
                detected=sum(len({h['owner'] for h in r['hits'] if h['correct_support'] and h['truth_color']==c and h['owner'] in r['eligible']}) for r in rr)) for c in ('red','yellow','black')})
    # Paired scene bootstrap includes empty detections; scenes are the units.
    boot=np.random.default_rng(283502);delta=[]
    for _ in range(2000):
        sample=[results[i] for i in boot.integers(0,len(results),len(results))];pp=[]
        for m in ('before','after'):
            n=sum(r[m]['high'] for r in sample);pp.append(sum(r[m]['distinct_correct'] for r in sample)/max(1,n))
        delta.append(pp[1]-pp[0])
    save(OUT/(split+'-results.json'),dict(seed=seed,split=split,scenes=results,summary=summary,
        paired_scene_bootstrap_distinct_precision_difference=np.quantile(delta,[.025,.975]).tolist(),
        limitations=['Synthetic illumination/material domain is narrower than real photograph; no real precision calibration.',
            'Visible silhouette centroid is not the expected centroid of a conservative interior; reported offset is descriptive.',
            'Confirmation seed283601 held out from revised thresholds; seed283501 is now development, with first-pass results retained.'],method_freeze_sha256=sha(OUT/'method-freeze.json')))
    print(summary,flush=True)

if __name__=='__main__':main()

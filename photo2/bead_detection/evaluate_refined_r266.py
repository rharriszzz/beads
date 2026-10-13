"""Final R266 synthetic and native audits; all truth remains outside detection."""
import argparse,gzip,json,time
from dataclasses import replace
from pathlib import Path
import numpy as np
from matplotlib.colors import rgb_to_hsv
from scipy import ndimage as ndi
from . import annular_detect as d
from . import refine_r266 as ref
from .stress_r266 import stress_scenes
from .experiment_r266 import ROOT,OUT,WORK,VARIANTS,photo,truth_metrics,all_records,save,irregularity,outline_image
from .test_annular import audit


def synthetic():
    deadline=json.loads((OUT/'checkpoint.json').read_text())['deadline_epoch'];rows=[];status='complete';start=time.time()
    for name,rgb,truth,centers,conditions in stress_scenes():
        for threshold in (12,6,3):
            for method in ('straight','annular'):
                if time.time()>=deadline:status='deadline';break
                p=replace(VARIANTS[method+'-0-joint'],recovery_prominence_dn=threshold);data,_,_=d.detect(rgb,p);data['generation_id']='synthetic'
                data=ref.refine(data,rgb);rows.append(dict(scene=name,method=method,prominence=threshold,conditions=conditions,**truth_metrics(data,truth,centers)))
            if status!='complete':break
        save(OUT/'refined-synthetic.json',dict(status='running',results=rows,elapsed_seconds=time.time()-start))
        if status!='complete':break
    save(OUT/'refined-synthetic.json',dict(status=status,results=rows,elapsed_seconds=time.time()-start,source_sha256=d.sha(ref.__file__)))
    print(status,len(rows),round(time.time()-start,1),flush=True)


def evaluate():
    rgb=photo();v=rgb.max(axis=2);hsv=rgb_to_hsv(rgb/255.);visual=json.loads((ROOT/'photo2/review/r264/visual-review.json').read_text());results={};audits={};bases={}
    deadline=json.loads((OUT/'checkpoint.json').read_text())['deadline_epoch']
    for method in ('straight','annular'):
        for threshold in (12,6,3):
            name=f'{method}-0-selected{threshold}';path=WORK/name
            if not (path/'complete.json').exists():continue
            data=json.loads((path/'regions.json').read_text());assert data['association_sha256']==d.sha(ref.__file__)
            rs=data['regions'];ids={r['id'] for r in rs};coords=np.array([r['location'] for r in rs]);landmarks=[]
            for item in visual['missing']:
                distances=np.linalg.norm(coords-item['approximate_review_location'],axis=1);j=int(distances.argmin());landmarks.append(dict(label=item['label'],distance=float(distances[j]),nearest_id=rs[j]['id'],confidence=item['confidence']))
            irr={r['id']:irregularity(r) for r in rs}
            met=dict(regions=len(rs),deferred=len(data['deferred']),suppressed=len(data['suppressed']),landmarks=landmarks,review_duplicate_pairs_remaining=sum(all(k in ids for k in row['ids']) for row in visual['duplicates']),paper_window_pixels=sum(1992<=x<=1997 and 2628<=y<=2634 for r in rs for y,a,b in r['pixel_runs'] for x in range(a,b+1)),thin_pixels=sum(q['thin_pixels'] for q in irr.values()),mean_perimeter_area=float(np.mean([q['perimeter_area'] for q in irr.values()])))
            # Exact native supports unchanged by selecting/suppressing/deferring.
            parent=WORK/data['parent_run'];before=json.loads((parent/'regions.json').read_text());b={r['id']:r for r in all_records(before)};after={r['id']:r for r in all_records(data)}
            assert b.keys()==after.keys()
            assert all(b[k]['pixel_runs']==after[k]['pixel_runs'] and b[k]['location']==after[k]['location'] and b[k]['centroid']==after[k]['centroid'] for k in b)
            native_audit=dict(unchanged_masks_coordinates=len(b),strict_accepted=0,strict_stops=0)
            if threshold!=12:
                # The main supervisor already audits the 12-DN parent inventories.
                p=replace(VARIANTS[method+'-0-joint'],recovery_prominence_dn=threshold)
                for r in all_records(data):
                    if time.time()>=deadline:raise TimeoutError('Shared computation deadline reached')
                    with gzip.open(parent/r['trace_file'],'rt') as f:t=json.load(f)
                    a=t['accepted'];mx,my=t['mask_offset'];mask=np.zeros((max(q[1] for q in a)-my+1,max(q[0] for q in a)-mx+1),bool)
                    for q in a:
                        if q[7]:mask[q[1]-my,q[0]-mx]=True
                    na,ns=audit(v,hsv,mask,t,p);native_audit['strict_accepted']+=na;native_audit['strict_stops']+=ns
            results[name]=met;audits[name]=native_audit
            save(OUT/'refined-metrics.json',dict(results=results,audits=audits,warning='Photographic landmark proximity and old duplicate IDs are proxies, not verified coverage or bead count.'))
            if threshold==12:bases[method]=rs
            print(name,met,flush=True)
    # Geographically distributed strict final comparisons at both recovery levels.
    baseline=json.loads((WORK/'straight-0/regions.json').read_text())
    cases=json.loads((ROOT/'photo2/review/r264/comparison.json').read_text())['cases']
    for c in cases:
        outline_image(rgb,c['box'],[('R265 strict',baseline['regions'])]+[(method+' strict / prom12',bases[method]) for method in ('straight','annular')],OUT/('conservative-'+c['name']+'.png'),c['name']+' | strict descent / conservative recovery')
    save(OUT/'refined-evaluation-complete.json',dict(status='complete',detector_sha256=d.sha(d.__file__),association_sha256=d.sha(ref.__file__),evaluator_sha256=d.sha(__file__)))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['synthetic','evaluate']);a=ap.parse_args();globals()[a.stage]()

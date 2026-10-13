"""R266 peak-association refinement. Reads RGB plus automatic candidate inventories.

Preserves pilot association results. Gradual within-body shading is distinguished
from abrupt native color steps. Growth/masks are byte-preserved for each maximum.
"""
from __future__ import annotations
import argparse,copy,csv,gzip,hashlib,json,shutil,tarfile,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from matplotlib.colors import rgb_to_hsv
from . import annular_detect as d
from .experiment_r266 import ROOT,WORK,OUT,photo,save,outline_image,irregularity
RULE=dict(radius_px=18,hue_range_deg=25,hue_step_deg=12,saturation_range=.50,saturation_step=.22,bridge_min_fraction=.60,distant_bridge_min_fraction=.80,distant_bridge_distance_px=10,bridge_max_drop_dn=75,ribbon_min_fraction=.50)


def quality(r,value,hsv):
    q=d.region_quality(r,value,hsv);x,y=r['bright_patch']['peak'];patch=value[max(0,y-3):y+4,max(0,x-3):x+4]
    q['neighborhood_median_dn']=float(np.median(patch));q['neighborhood_p25_dn']=float(np.percentile(patch,25))
    q['score']=.04*q['brightness_dn']+.08*min(q['prominence_lower_bound_dn'],60)+.20*q['neighborhood_median_dn']+.25*q['neighborhood_p25_dn']+.04*min(r['pixel_count'],150)+q['compactness']*60
    return q


def associate(regions,value,hsv):
    if not regions:return [],[],[]
    peaks=np.array([r['bright_patch']['peak'] for r in regions]);tree=cKDTree(peaks);h,w=value.shape
    qualities=[quality(r,value,hsv) for r in regions]
    for r,q in zip(regions,qualities):r['peak_quality']=q
    order=sorted(range(len(regions)),key=lambda i:(-qualities[i]['score'],regions[i]['id']));winners=[];won=set();removed=set();suppressed=[];evidence=[]
    for i in order:
        if i in removed:continue
        winners.append(regions[i]);won.add(i);x,y=peaks[i]
        for j in sorted(tree.query_ball_point(peaks[i],RULE['radius_px'])):
            if j==i or j in removed or j in won or qualities[j]['score']>qualities[i]['score']:continue
            tx,ty=peaks[j];line=d.straight_pixels((x,y),(tx,ty));cross=(0,1) if abs(tx-x)>=abs(ty-y) else (1,0)
            ribbons=[[(lx+cross[0]*delta,ly+cross[1]*delta) for lx,ly in line] for delta in (-2,-1,0,1,2)]
            if any(not(0<=xx<w and 0<=yy<h) for ribbon in ribbons for xx,yy in ribbon):continue
            qs=np.array([[hsv[yy,xx] for xx,yy in ribbon] for ribbon in ribbons]);vs=np.array([[value[yy,xx] for xx,yy in ribbon] for ribbon in ribbons],float)
            hue_delta=abs((qs[:,:,0]-qs[2,0,0]+.5)%1-.5)*360
            hue_steps=abs((np.diff(qs[:,:,0],axis=1)+.5)%1-.5)*360
            sat_steps=abs(np.diff(qs[:,:,1],axis=1));reliable=qs[:,:,1]>=.25
            reliable_steps=reliable[:,1:] & reliable[:,:-1]
            # Each ribbon is checked; no ring average controls pixel growth.
            color=bool(np.quantile(hue_delta[reliable],.9)<=RULE['hue_range_deg'] and np.quantile(hue_steps[reliable_steps],.95)<=RULE['hue_step_deg'] and np.ptp(qs[:,:,1])<=RULE['saturation_range'] and np.quantile(sat_steps,.95)<=RULE['saturation_step']) if reliable.any() and reliable_steps.any() else bool(np.max(qs[:,:,1])<.18)
            endmin=float(min(value[y,x],value[ty,tx]));shallow=bool(vs[2].min()>=max(100,(RULE['distant_bridge_min_fraction'] if np.linalg.norm(peaks[i]-peaks[j])>RULE['distant_bridge_distance_px'] else RULE['bridge_min_fraction'])*endmin,endmin-RULE['bridge_max_drop_dn']) and np.quantile(vs,.1)>=max(90,RULE['ribbon_min_fraction']*endmin))
            strong=color and shallow
            item=dict(ids=[regions[i]['id'],regions[j]['id']],distance=float(np.linalg.norm(peaks[i]-peaks[j])),bridge_min_dn=float(vs[2].min()),ribbon_p10_dn=float(np.quantile(vs,.1)),hue_p90_deg=float(np.quantile(hue_delta[reliable],.9)) if reliable.any() else None,hue_step_p95_deg=float(np.quantile(hue_steps[reliable_steps],.95)) if reliable_steps.any() else None,saturation_range=float(np.ptp(qs[:,:,1])),color_compatible=color,shallow_broad_bridge=shallow,decision='suppress' if strong else 'uncertain-alternatives')
            evidence.append(item)
            if strong:
                removed.add(j);r=regions[j];r.update(status='suppressed',suppressed_by=regions[i]['id'],suppression_reason='inferior neighborhood/region quality; broad bright bridge and gradual compatible shading');r['bright_patch'].update(status='suppressed',reason=r['suppression_reason']);suppressed.append(r)
    return winners,suppressed,evidence


def refine(data,rgb):
    data=copy.deepcopy(data);rs=data['regions']+data['suppressed']
    for r in rs:
        r['status']='retained';r.pop('suppressed_by',None);r.pop('suppression_reason',None);r['bright_patch'].update(status='retained',reason='ambiguous-candidate')
        r['ambiguity']=[a for a in r['ambiguity'] if a not in ('multiple-highlights-not-merged','overlapping-independent-supports')]+['remaining-peak-associations-unresolved']
    kept,suppressed,associations=associate(rs,rgb.max(axis=2),rgb_to_hsv(rgb/255.))
    data.update(regions=kept,suppressed=suppressed,associations=associations,association_parameters=RULE,association_sha256=d.sha(__file__),version='r266-refined-v1')
    # JSON-loaded records and maxima are separate objects: synchronize explicitly.
    byid={r['id']:r for group in ('regions','suppressed','deferred','rejected') for r in data[group]}
    for m in data['maxima']:
        if m['region_id'] in byid:
            r=byid[m['region_id']];m.update(status=r['status'],reason=r.get('suppression_reason',r.get('deferred_reason',m['reason'])))
    data['parent_generation_id']=data['generation_id'];data['generation_id']=hashlib.sha256((data['generation_id']+d.sha(__file__)+json.dumps(RULE,sort_keys=True)).encode()).hexdigest()[:16]
    coverage=np.zeros((data['height'],data['width']),np.uint16)
    for r in kept:
        for y,a,b in r['pixel_runs']:coverage[y,a:b+1]+=1
    for r in kept:r['overlap_pixel_count']=sum(int(np.count_nonzero(coverage[y,a:b+1]>1)) for y,a,b in r['pixel_runs'])
    return data


def save_run(source,name,rgb):
    data=refine(json.loads((source/'regions.json').read_text()),rgb);data['parent_run']=source.name;dest=WORK/name;dest.mkdir(exist_ok=True);(dest/'traces').mkdir(exist_ok=True)
    # Identical masks and traces; retain both coordinate inventories and source lineage.
    for p in (source/'traces').glob('*.gz'):shutil.copyfile(p,dest/'traces'/p.name)
    for f in ('photo.png',):shutil.copyfile(source/f,dest/f)
    d.save(dest/'regions.json',data)
    with (dest/'coordinates.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['region_id','status','location_x','location_y','centroid_x','centroid_y','pixels','suppressed_by'])
        for group in ('regions','suppressed','deferred','rejected'):
            for r in data[group]:w.writerow([r['id'],r['status'],*r['location'],*r['centroid'],r['pixel_count'],r.get('suppressed_by','')])
    sizes=np.array([r['pixel_count'] for r in data['regions']]);summary=dict(generation_id=data['generation_id'],regions=len(data['regions']),suppressed=len(data['suppressed']),deferred=len(data['deferred']),parameters=data['parameters'],association_parameters=RULE,sizes=dict(min=int(sizes.min()),median=float(np.median(sizes)),max=int(sizes.max())))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4));ax.hist(sizes,bins=30,color='#008caa');ax.set(xlabel='Native pixels per selected support',ylabel='Regions',title='R266 selected supports');fig.tight_layout();fig.savefig(dest/'size-distribution.png',dpi=150);plt.close(fig)
    with (dest/'rank-size.csv').open('w') as f:
        f.write('rank,region_id,pixel_count\n')
        for i,r in enumerate(sorted(data['regions'],key=lambda r:-r['pixel_count']),1):f.write(f'{i},{r["id"]},{r["pixel_count"]}\n')
    labels=np.zeros((data['height'],data['width']),np.int32);coverage=np.zeros_like(labels,dtype=np.uint16)
    for r in data['regions']:
        for y,a,b in r['pixel_runs']:
            c=coverage[y,a:b+1];labels[y,a:b+1]=np.where(c>0,-1,int(r['id'][1:]));c+=1
    np.savez_compressed(dest/'labels.npz',labels=labels,membership_count=coverage)
    d.save(dest/'summary.json',summary);d.save(dest/'complete.json',dict(generation_id=data['generation_id'],parent_generation_id=data['parent_generation_id']))
    out=OUT/name;out.mkdir(exist_ok=True)
    for f in ('summary.json','coordinates.csv'):(out/f).write_bytes((dest/f).read_bytes())
    with gzip.GzipFile(filename=str(out/'regions.json.gz'),mode='wb',mtime=0) as f:f.write((dest/'regions.json').read_bytes())
    # Native traces already archived under the parent; explicit source reference
    # avoids multiplying identical replay payloads in tracked evidence.
    save(out/'trace-source.json',dict(parent_run=source.name,association_sha256=d.sha(__file__)))
    return data


def main():
    rgb=photo();results={};deadline=json.loads((OUT/'checkpoint.json').read_text())['deadline_epoch']
    for threshold in (12,6,3):
        for method in ('straight','annular'):
            parent=f'{method}-0-joint'+(str(threshold) if threshold!=12 else '');name=f'{method}-0-selected{threshold}';source=WORK/parent
            if time.time()>=deadline:save(OUT/'refinement-status.json',dict(status='deadline',completed=list(results)));return
            if not (source/'complete.json').exists():continue
            data=save_run(source,name,rgb);results[name]=data['regions'];print(name,len(data['regions']),len(data['suppressed']),flush=True)
    cases=json.loads((ROOT/'photo2/review/r264/comparison.json').read_text())['cases'];base=json.loads((WORK/'straight-0/regions.json').read_text())
    for c in cases:
        selected=[('R265 strict',base['regions'])]+[(k,results[k]) for k in ('straight-0-selected6','annular-0-selected6') if k in results]
        outline_image(rgb,c['box'],selected,OUT/('selected-'+c['name']+'.png'),c['name']+' | strict descent, refined peak association')
    save(OUT/'refinement-status.json',dict(status='complete',completed=list(results),parameters=RULE))
if __name__=='__main__':main()

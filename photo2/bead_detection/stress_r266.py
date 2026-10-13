"""Additional R266 known-truth stress tests and lower-prominence diagnostics.

Native rendering; image-derived detection has no access to truth. This shares the
main supervisor's absolute deadline and records incomplete trials explicitly.
"""
import argparse,json,time,gzip
from pathlib import Path
from dataclasses import replace
import numpy as np
from matplotlib.colors import hsv_to_rgb,rgb_to_hsv
from scipy import ndimage as ndi
from skimage.morphology import h_maxima,local_maxima
from . import annular_detect as d
from .experiment_r266 import OUT,WORK,VARIANTS,photo,truth_metrics,outline_image,save


def stress_scenes():
    rng=np.random.default_rng(26619);y,x=np.mgrid[:71,:91]
    for i in range(96):
        hue=(i*.173)%1;same=i%2==0;gap=(-6,-2,0,4)[(i//2)%4];sep=24+gap
        centers=[[43-sep//2,35],[43+sep//2,35]];hsv=np.full((71,91,3),[(hue+.43)%1,.42,.77]);truth=np.zeros((71,91),np.int16)
        # Raw smooth cast shadow on the paper, unrelated to detector rules.
        hsv[:,:,2]-=.28*np.exp(-((x-44)**2+(y-40)**2)/360)
        for k,(cx,cy) in enumerate(centers,1):
            radius=((x-cx)/12)**2+((y-cy)/14)**2;body=radius<=1
            h=hue if same else (hue+(k-1)*.18)%1
            val=.90-.46*np.minimum(radius,1)**.6
            if i%3==1: # two modest maxima on one connected illuminated interior
                val=.65-.22*np.minimum(radius,1)+.20*np.exp(-((x-cx-4)**2+(y-cy)**2)/5)+.23*np.exp(-((x-cx+4)**2+(y-cy)**2)/5)
            elif i%3==2:val-=.14*(x-cx)/12
            if (i//8)%3==1:val*=.65
            sat=.8
            if (i//8)%3==2 and k==1:sat=.08;val=.12+.82*np.exp(-((x-cx)**2+(y-cy)**2)/9)
            hsv[body,0]=h;hsv[body,1]=sat;hsv[body,2]=val[body];truth[body]=k
        rgb=np.round(hsv_to_rgb(hsv.clip(0,1))*255).astype(int)
        noise=i//24
        if noise:rgb+=rng.integers(-noise,noise+1,rgb.shape)
        yield f'stress-{i:03d}',np.clip(rgb,0,255).astype(np.uint8),truth,centers,dict(same_color=same,gap=gap,noise=noise,lighting=(i//8)%3,multiple_highlights=i%3==1)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',type=Path,default=OUT/'checkpoint.json');a=ap.parse_args();deadline=json.loads(a.checkpoint.read_text())['deadline_epoch']
    start=time.time();rows=[];ranked=[];status='complete'
    for name,rgb,truth,centers,conditions in stress_scenes():
        records={}
        for variant in ('straight-0','annular-0','straight-0-joint','annular-0-joint'):
            if time.time()>=deadline:status='deadline';break
            data,_,_=d.detect(rgb,VARIANTS[variant]);records[variant]=data
            row=dict(scene=name,variant=variant,conditions=conditions,**truth_metrics(data,truth,centers));rows.append(row)
        if status!='complete':break
        old=next(r for r in rows[-4:] if r['variant']=='straight-0');new=rows[-1]
        delta=sum(new[k]-old[k] for k in ('missing','duplicates','background_coordinates'))
        ranked.append((delta,name,rgb,records))
        save(OUT/'stress.json',dict(status='running',seed=26619,elapsed_seconds=time.time()-start,results=rows))
    save(OUT/'stress.json',dict(status=status,seed=26619,elapsed_seconds=time.time()-start,results=rows))
    for label,reverse in [('improvement',False),('regression',True)]:
        for j,(score,name,rgb,records) in enumerate(sorted(ranked,key=lambda r:(r[0],r[1]),reverse=reverse)[:2]):
            outline_image(rgb,[0,0,91,71],[(k,records[k]['regions']) for k in ('straight-0','straight-0-joint','annular-0-joint')],OUT/f'stress-{label}-{j+1}.png',f'{name}: known truth errors delta {score}; 2 bodies')
    # Global h-maxima thresholds evaluated at every raw maximum in diagnostic crops.
    rgb=photo();value=rgb.max(axis=2);labels,n=ndi.label(local_maxima(value,connectivity=2,allow_borders=True),np.ones((3,3)))
    with gzip.open(d.ROOT/'photo2/review/r265-first-dark/regions.json.gz','rt') as f:baseline=json.load(f)
    visual=json.loads((d.ROOT/'photo2/review/r264/visual-review.json').read_text());targets=[]
    for item in visual['missing']:
        x,y=item['approximate_review_location']
        for m in baseline['maxima']:
            if (m['peak'][0]-x)**2+(m['peak'][1]-y)**2<=12**2:targets.append(dict(landmark=item['label'],id=m['region_id'],peak=m['peak'],value_dn=m['value_dn'],passing_prominence=[]))
    for threshold in (3,6,12,20,35):
        if time.time()>=deadline:status='deadline';break
        meaningful=set(np.unique(labels[h_maxima(value,threshold,footprint=np.ones((3,3))).astype(bool)]))-{0}
        for row in targets:
            x,y=row['peak']
            if labels[y,x] in meaningful:row['passing_prominence'].append(threshold)
        save(OUT/'missing-seed-prominence.json',dict(status='running',thresholds_completed=threshold,candidates=targets))
    save(OUT/'missing-seed-prominence.json',dict(status=status,candidates=targets,note='Review coordinates only select diagnostics after automatic whole-image maxima; never passed to detector.'))
    print(json.dumps(dict(status=status,elapsed_seconds=time.time()-start,trials=len(rows))))
if __name__=='__main__':main()

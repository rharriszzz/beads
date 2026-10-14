"""Fresh independently rendered confirmation; truth opened after saved inference.

Scene geometry only renders benchmark pixels. Detector sees RGB and image-only
cues, never classes, physical positions or identity raster. No real-photo tuning.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from collections import Counter
from photo2.r282.common import save,read,sha,support,pixels
from photo2.r280.synthetic import render
from photo2.r280.geometry import certify
from photo2.r283.ownership import detect
from .select import OUT
from .methods import infer
from .run import old_control

def main():
    rng=np.random.default_rng(285501);scenes=[]
    for s in range(4):
        folder=OUT/'synthetic'/f'scene-{s:02}';folder.mkdir(parents=True,exist_ok=True)
        p=dict(hand=(-1,1)[s%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=1.20,inclination=(-24,0,18,30)[s],roll=float(rng.uniform(-25,25)),scale=9.,translation=[159.5,111.5],light=[-.6,-.8,1.],light_power=1.1,specular=(.15,1.5,.5,1.8)[s],roughness=(.10,.025,.06,.035)[s],ambient=.10,background=[.47,.31,.43])
        classes=rng.integers(0,3,29);classes[10:15]=s%2;cert=certify(p);assert cert['certified']
        rgb=render(folder,p,classes);a=rgb/255.;rgb=np.uint8(np.rint(255*np.where(a<=.0031308,12.92*a,1.055*a**(1/2.4)-.055)))
        Image.fromarray(rgb).save(folder/'analysis-srgb.png');starts,f=detect(rgb);records=[]
        pad={k:np.pad(f[k],((48,48),(48,48),(0,0)) if k=='hsv' else 48,mode='edge') for k in ('lum','hsv','paper')}
        for o in starts:
            if o['color'] not in ('red','yellow'):continue
            x,y=o['seed'];sl=np.s_[y:y+97,x:x+97];alt=infer(pad['lum'][sl],pad['hsv'][sl],pad['paper'][sl],f['palette'],f['background_hue'],o['color']);controls=old_control(f,[x,y],o['color']);rr={m:v['measured_support'] for m,v in controls.items()}
            for m,(mask,info) in alt.items():
                yy,xx=np.where(mask);rr[m]=support(np.c_[xx+x-48,yy+y-48])
            records.append(dict(seed=[x,y],color=o['color'],supports=rr))
        save(folder/'inference.json.gz',records)
        # Truth generation/read occurs strictly after photographic inference save.
        truth=render(folder,p,classes,True)[:,:,0].astype(int)-1
        eligible=[j for j in range(29) if classes[j]!=2 and (truth==j).sum()>=40]
        summary={}
        for m in ('A','J','D','S','G'):
            hits=[]
            for o in records:
                pts=pixels(o['supports'][m]);inside=np.all((pts>=0)&(pts<[320,224]),axis=1);vals=np.full(len(pts),-1,int);vals[inside]=truth[pts[inside,1],pts[inside,0]]
                if not len(vals):continue
                body,n=Counter(vals.tolist()).most_common(1)[0];hits.append(dict(seed=o['seed'],area=len(vals),owner=int(body),purity=n/len(vals),pure=bool(body>=0 and n/len(vals)>=.95),within_cap=len(vals)<=870))
            valid=[h for h in hits if h['within_cap']];owners=Counter(h['owner'] for h in valid if h['pure']);summary[m]=dict(proposals=len(records),nonempty=len(hits),within_cap=len(valid),pure=sum(h['pure'] for h in valid),distinct=len(owners),duplicates=sum(n-1 for n in owners.values()),eligible=len(eligible),recovered=len(set(eligible)&set(owners)),mixed_or_background=sum(not h['pure'] for h in valid),hits=hits)
        # Normalize renderer source/log whitespace for tracked review artifacts.
        for artifact in folder.iterdir():
            if artifact.suffix in ('.pov','.log'):artifact.write_text('\n'.join(line.rstrip() for line in artifact.read_text().splitlines()).rstrip()+'\n')
        save(folder/'truth.json',dict(parameters=p,classes=classes.tolist(),certificate=cert,inference_sha256=sha(folder/'inference.json.gz'),semantics='Truth evaluation only; purity95% is not real-photo calibration.'))
        scenes.append(summary);print('rendered confirmation',s,len(records),flush=True)
    totals={m:{k:sum(r[m][k] for r in scenes) for k in ('proposals','nonempty','within_cap','pure','distinct','duplicates','eligible','recovered','mixed_or_background')} for m in ('A','J','D','S','G')}
    save(OUT/'synthetic-summary.json',dict(seed=285501,scenes=scenes,totals=totals,scope='Four independent POV scenes; automatic cues fixed across methods, no calibrated real precision. Full visible bodies are a recall denominator, not a target silhouette.'))
if __name__=='__main__':main()

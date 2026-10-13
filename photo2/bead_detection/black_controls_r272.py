"""Single-factor black signal/material controls, no evaluation coordinates."""
import gzip,json,copy,time
from dataclasses import replace
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from matplotlib.colors import rgb_to_hsv
from .coverage_r272 import Parameters,black_region,select_nonoverlap
from .brightness_r270 import color_managed_photo,linearize
from .climb_r268 import background
from .experiment_coverage_r272 import ROOT,OUT,save,lines,check_budget

def main():
    t=time.monotonic();native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();hsv=rgb_to_hsv(srgb/255.);nhsv,paper,_=background(native);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);rows=[]
    with gzip.open(OUT/'pilot-native-v/candidates.jsonl.gz','rt') as f:
        for l in f:
            r=json.loads(l)
            if r['pathway']=='black' and not(set(r['reasons'])&{'context','black-color','black-contrast','background'}):rows.append(r)
    base=replace(Parameters(),black_signal='native-v',black_surround_fraction=.65)
    variants={'native-v':base,'native-v-sigma055':replace(base,black_sigma=.55),'icc-gray':replace(base,black_signal='icc-gray'),'native-v-material050':replace(base,black_surround_fraction=.50),'icc-gray-material050':replace(base,black_signal='icc-gray',black_surround_fraction=.50)};summaries={}
    for name,p in variants.items():
        check_budget();results=[]
        for old in rows:
            x,y=old['anchor']
            if min(x,y,lum.shape[1]-1-x,lum.shape[0]-1-y)<25:continue
            r=dict(id=old['id'],anchor=old['anchor'],pathway='black',confidence=dict(raw_y=old['confidence']['raw_y']),reasons=[],accepted=False);black_region(r,native,srgb,hsv,nhsv,lum,paper,p);results.append(r)
        select_nonoverlap(results,lum);beads=[r for r in results if r['accepted']];lines('black-control-'+name+'.jsonl.gz',results);summaries[name]=dict(accepted=len(beads),reasons=dict(Counter(k for r in results for k in r['reasons'])),ids=[r['id'] for r in beads]);print(name,len(beads),flush=True)
    save('black-controls.json',dict(variants=summaries,elapsed_seconds=time.monotonic()-t,scope='Same original native-Y maxima; candidates failing initial color/brightness/background gate omitted consistently, no photo annotations used. Each signal has its own measured first enclosing perimeter.'))
if __name__=='__main__':main()

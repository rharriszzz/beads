"""Simple dot-only photographs; review coordinates never enter detection."""
import gzip,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .brightness_r270 import color_managed_photo
from .experiment_r271 import OUT,ROOT,save
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n=20):return ImageFont.truetype(FONT,n)
def pair(rgb,box,points,path,scale=3,caption=None,color='#00ffff'):
    x0,y0,x1,y1=box;raw=Image.fromarray(rgb[y0:y1,x0:x1]).resize((round((x1-x0)*scale),round((y1-y0)*scale)),Image.Resampling.NEAREST)
    marked=raw.copy();d=ImageDraw.Draw(marked)
    for p in points:
        x,y=p['x'],p['y']
        if x0<=x<x1 and y0<=y<y1:
            cx=(x-x0+.5)*scale;cy=(y-y0+.5)*scale;r=max(2,scale*.6);d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=color)
    lines=[];line=''
    for word in (caption or '').split():
        trial=(line+' '+word).strip()
        if font(18).getlength(trial)>2*raw.width-8 and line:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    gap=12;top=38;bottom=10+26*len(lines)
    out=Image.new('RGB',(2*raw.width+gap,raw.height+top+bottom),'white');out.paste(raw,(0,top));out.paste(marked,(raw.width+gap,top));d=ImageDraw.Draw(out);d.text((8,8),'Original',fill='black',font=font());d.text((raw.width+gap+8,8),'Proposed trusted locations' if color=='#00ffff' else 'Excluded candidate',fill='black',font=font())
    for i,line in enumerate(lines):d.text((8,top+raw.height+6+i*26),line,fill='black',font=font(18))
    out.save(path)
def main():
    rgb,_=color_managed_photo();h,w=rgb.shape[:2];rows=[json.loads(s) for s in gzip.open(OUT/'all-candidates.jsonl.gz','rt')];trusted=[r for r in rows if r['trusted']]
    # Boxes are display-only and are loaded AFTER image-only acceptance is saved.
    cases=json.load(open(ROOT/'photo2/review/r269/starts.json'))
    for name,c in cases.items():pair(rgb,c['box'],trusted,OUT/(name+'-trusted.png'),5)
    pair(rgb,[0,0,w,h],trusted,OUT/'whole-photo-trusted.png',.4)
    tiles=[]
    for iy in range(4):
        for ix in range(4):
            box=[ix*w//4,iy*h//4,(ix+1)*w//4,(iy+1)*h//4];name=f'area-{iy+1}-{ix+1}.png';pair(rgb,box,trusted,OUT/name,1);tiles.append(dict(row=iy+1,column=ix+1,file=name,trusted=sum(box[0]<=p['x']<box[2] and box[1]<=p['y']<box[3] for p in trusted)))
    # R270's named origins are evaluation-only. Automatic decision must already
    # exist; nearest candidate lookup cannot alter that decision.
    focus=json.load(open(ROOT/'photo2/review/r270/focus-results.json'));checks=[]
    for f in focus:
        if f['measure']!='Y' or f['window']!=7 or f['policy']!='raw24-mean2':continue
        xy=f['endpoint'];r=min(rows,key=lambda r:(r['x']-xy[0])**2+(r['y']-xy[1])**2);checks.append(dict(case=f['case'],crop=f['crop'],review_xy=xy,nearest_candidate_id=r['id'],distance=float(np.hypot(r['x']-xy[0],r['y']-xy[1])),candidate=r))
    save('review-checks.json',checks)
    shadow=next(c['candidate'] for c in checks if c['case']=='shadowed-neighbor');assert not shadow['trusted'],'User review contradicts automatic acceptance: do not silently exclude by coordinates'
    pair(rgb,[shadow['x']-23,shadow['y']-23,shadow['x']+24,shadow['y']+24],[shadow],OUT/'R01284-excluded-shadowed-neighbor.png',6,'A real separate bead, excluded because the patch is too dim for this conservative set. The rule excludes it automatically.','#ff8800')
    # Representative exclusions across the image, one marker and plain reasons
    # per photograph. The complete inventory remains in compressed JSON/CSV.
    selected=[]
    for tile in tiles:
        ix=tile['column']-1;iy=tile['row']-1
        opts=[r for r in rows if not r['trusted'] and r['background_code']==0 and r['x']*4//w==ix and r['y']*4//h==iy and 24<=r['x']<w-24 and 24<=r['y']<h-24]
        if not opts:continue
        # Strongest rejected candidate per fixed geographic cell: diagnostic only.
        r=max(opts,key=lambda r:r['mean_y']);name=f'excluded-area-{iy+1}-{ix+1}.png';pair(rgb,[r['x']-24,r['y']-24,r['x']+25,r['y']+25],[r],OUT/name,5,' '.join(r['explanations']),'#ff8800');selected.append(dict(file=name,id=r['id'],reasons=r['explanations']))
    save('display-index.json',dict(tiles=tiles,excluded=selected))
    s='''# R271 — trusted location review

Each cyan dot is one automatically accepted location. There are no paths, IDs,
rank labels or outlines on these photographs. The unmarked original is beside it.
These are proposed trusted image locations, not physical bead centers or a bead census.

- [Whole photograph](whole-photo-trusted.png)
- [R00956](R00956-trusted.png)
- [R01284](R01284-trusted.png)
- [Shadowed neighbor: separately excluded](R01284-excluded-shadowed-neighbor.png)
- [Acceptance rule and results](../../TRUSTED_LOCATIONS_R271.md)

All areas, in photograph order (rows top to bottom, columns left to right):

| Row | Left | Left middle | Right middle | Right |
|---|---|---|---|---|
'''
    for iy in range(4):s+='| '+str(iy+1)+' | '+' | '.join(f'[Photo](area-{iy+1}-{ix+1}.png)' for ix in range(4))+' |\n'
    s+='\n## Excluded candidates\n\nOrange dots appear only in these separate diagnostic photographs. Each caption explains why the rule withheld the location.\n\n'
    for r in selected:s+=f"- [Photograph]({r['file']}): {' '.join(r['reasons'])}\n"
    s+='''
## Numerical evidence

`trusted-locations.json` contains the accepted set. `all-candidates.jsonl.gz` and
`candidate-measurements.csv.gz` retain every mean7 maximum plateau, its native
pixels, measurements, decision and reasons. `search-traces.jsonl.gz` preserves
all 18 stability routes for candidates that pass the inexpensive gates. Later
checks are deliberately not run for obvious exclusions; `search_checked` says so.
`candidate-and-background-maps.npz` preserves native maxima and fixed background.
`synthetic-*` uses known scene identities only after selection for evaluation.
`review-checks.json` compares old named coordinates only after detection.

Reproduce in the existing Python 3.12 environment:

```sh
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.experiment_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.review_r271
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m unittest photo2.bead_detection.test_trusted_r271 > photo2/review/r271/tests.log 2>&1
MPLCONFIGDIR=/tmp/beads-r271-mpl .venv/bin/python -m photo2.bead_detection.validate_r271
```

Archive the existing R271 directory before reproducing, to preserve this delivery.
'''
    (OUT/'README.md').write_text(s)
if __name__=='__main__':main()

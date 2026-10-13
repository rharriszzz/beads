"""Curated original-photo comparisons and complete numbered maximum maps."""
from collections import defaultdict
import csv,gzip,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .audit_r267 import ROOT,save,csvsave,map_image,FONT
from .brightness_r270 import MEASURES,SCALE,color_managed_photo
from .experiment_r270 import OUT
from .experiment_r269 import FOCUS

BG='#172028';WHITE='#ffffff';COLORS={5:'#00eaff',7:'#ffe564',9:'#ff77cf'}
NAMES={'V':'HSV Value (native baseline)','Y':'sRGB relative luminance','OKL':'OKLab lightness L','VS':'Experimental native V(1-S/2)'}
font=lambda n:ImageFont.truetype(FONT,n)

def panel(rgb,box,scale,header=102):
    x0,y0,x1,y1=box;im=Image.new('RGB',((x1-x0)*scale,(y1-y0)*scale+header),BG);im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST),(0,header))
    return im,lambda x,y:((x-x0+.5)*scale,header+(y-y0+.5)*scale)

def draw_path(im,project,path,color):
    p=[project(z['x'],z['y']) for z in path];d=ImageDraw.Draw(im)
    if len(p)>1:d.line(p,fill=color,width=2)
    if p:
        x,y=p[0];d.rectangle((x-3,y-3,x+3,y+3),outline=WHITE);x,y=p[-1];d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2)

def join(panels,path,rows=1):
    cols=len(panels)//rows;w=max(p.width for p in panels);h=max(p.height for p in panels);im=Image.new('RGB',(w*cols,h*rows),BG)
    for i,p in enumerate(panels):im.paste(p,((i%cols)*w,(i//cols)*h))
    im.save(path)

def main():
    rgb,profile=color_managed_photo();focus=json.load(open(OUT/'focus-results.json'));candidates=json.load(open(OUT/'candidate-points.json'));legacy=json.load(open(OUT/'legacy-starts.json'));index=[];summary=[];layouts={}
    for crop,pairs in FOCUS.items():
      for label,pid in pairs:
        rs=[r for r in focus if r['crop']==crop and r['case']==label and r['policy']=='raw24-mean2'];coords=[(p['x'],p['y']) for r in rs for p in r['climb']['steps']+r['path']];a=np.array(coords);size=max(42,int(np.ptp(a[:,0]))+22,int(np.ptp(a[:,1]))+22);cx=int((a[:,0].min()+a[:,0].max())//2);cy=int((a[:,1].min()+a[:,1].max())//2);box=[cx-size//2,cy-size//2,cx-size//2+size,cy-size//2+size];scale=max(4,384//size);panels=[]
        im,project=panel(rgb,box,scale);d=ImageDraw.Draw(im);d.text((8,8),crop+' '+label,fill=WHITE,font=font(16));d.text((8,34),'Original photograph, ICC to sRGB display',fill=WHITE,font=font(13));d.text((8,58),'5x5 cyan | 7x7 yellow | 9x9 magenta',fill=WHITE,font=font(13));d.text((8,80),'White square start; ring final; radius16',fill=WHITE,font=font(13));panels.append(im)
        for m in MEASURES:
            im,project=panel(rgb,box,scale);d=ImageDraw.Draw(im);d.text((8,8),NAMES[m],fill=WHITE,font=font(15))
            for j,n in enumerate((5,7,9)):
                r=next(r for r in rs if r['measure']==m and r['window']==n);p=r['climb']['steps']+r['path'][1:];draw_path(im,project,p,COLORS[n]);d.text((8,34+j*21),f"{n}: {r['endpoint']} mean {r['end_mean']:.3f}",fill=COLORS[n],font=font(13))
                summary.append(dict(crop=crop,case=label,measure=m,window=n,start=r['start'],climb_endpoint=r['climb']['endpoint'],broad_endpoint=r['endpoint'],mean=r['end_mean'],raw_floor=r['raw_floor'],mean_floor=r['mean_floor'],climb_stop=r['climb_stop']))
            panels.append(im)
        join(panels,OUT/f'{crop}-{label}-four-measures.png');index.append((crop,label))
    csvsave(OUT/'focus-coordinate-summary.csv',summary)
    # Every raw/mean maximum is numbered without label overlap. No prominence gate.
    maxima_index=['# Independent maxima for every brightness measure','','Native pixels on the original photograph (ICC-managed sRGB display). Every plateau pixel crossing a crop boundary is retained. Colors rank mean7 among the displayed population. C numbers in the numeric CSV identify pixels, never beads. Prominence censor flags indicate that the fixed context cannot establish global prominence.','', '| Crop | Measure | Raw maxima | Mean5 maxima | Mean7 maxima | Mean9 maxima | Numerical table |','|---|---|---|---|---|---|---|']
    for crop,rs in candidates.items():
        for m in MEASURES:
            paths=[]
            for kind in ('raw','mean5','mean7','mean9'):
                pts=[dict(r) for r in rs if m+'-'+kind in r['types']];box=list(legacy[crop]['box']);box[0]=min(box[0],min(r['x'] for r in pts)-2);box[1]=min(box[1],min(r['y'] for r in pts)-2);box[2]=max(box[2],max(r['x'] for r in pts)+3);box[3]=max(box[3],max(r['y'] for r in pts)+3)
                key=m+'_mean7';values=[r[key] for r in pts]
                for r in pts:r['rank_'+key]=1+sum(v>r[key] for v in values)
                name=f'{crop}-{m}-all-{kind}-maxima.png';layouts[name]=map_image(rgb,box,pts,key,OUT/name,f'{crop} | {NAMES[m]} | all {kind} maxima; no prominence filtering');paths.append(name)
            maxima_index.append(f"| {crop} | {m} | [photo]({paths[0]}) | [photo]({paths[1]}) | [photo]({paths[2]}) | [photo]({paths[3]}) | [CSV]({crop}-candidate-measurements.csv) |")
    (OUT/'MAXIMA_INDEX.md').write_text('\n'.join(maxima_index)+'\n');save(OUT/'label-validation.json',layouts)
    # Matched coordinates make score ranking interpretable without comparing units.
    lookup={(r['x'],r['y']):r for r in candidates['R01284']};coord=[('A',(981,2673),'old mean7 endpoint'),('C',(976,2668),'pale raw peak, 5px from E'),('E',(980,2671),'old mean9 endpoint')]
    for m in ('Y','OKL','VS'):
        r=next(r for r in focus if r['case']=='central-yellow' and r['measure']==m and r['window']==7 and r['policy']=='raw24-mean2');xy=tuple(r['endpoint'])
        if xy not in [a[1] for a in coord]:coord.append((m,xy,'new '+m+' mean7 endpoint'))
    # Endpoints need not be local maxima, so sample fields if absent from inventory.
    fields=np.load(OUT/'R01284-fields.npz');ox,oy=fields['origin'];points=[]
    for label,(x,y),desc in coord:
        r=dict(lookup.get((x,y),{}));r.update(label=label,x=x,y=y,description=desc,native_rgb=fields['rgb'][y-oy,x-ox].tolist(),srgb=fields['srgb'][y-oy,x-ox].tolist())
        for m in MEASURES:
            r[m+'_raw']=float(fields['raw_'+m][y-oy,x-ox])
            for n in (5,7,9):r[f'{m}_mean{n}']=float(fields[f'sum_{m}_{n}'][y-oy,x-ox]/(SCALE*n*n))
        points.append(r)
    save(OUT/'pale-peak-matched-coordinates.json',points);csvsave(OUT/'pale-peak-matched-coordinates.csv',[{k:r[k] for k in ['label','x','y','description','native_rgb','srgb']+[m+'_'+stat for m in MEASURES for stat in ('raw','mean5','mean7','mean9')]} for r in points])
    box=[967,2654,994,2684];clean,proj=panel(rgb,box,16,70);marked=clean.copy();d=ImageDraw.Draw(clean);d.text((8,10),'Original photograph, ICC to sRGB',fill=WHITE,font=font(16));d=ImageDraw.Draw(marked);d.text((8,10),'Old points and new candidates',fill=WHITE,font=font(16))
    for r in points:
        x,y=proj(r['x'],r['y']);d.ellipse((x-4,y-4,x+4,y+4),outline='#00ffff',width=2);d.text((x+6,y-18),r['label'],fill='#00ffff',font=font(20),stroke_width=2,stroke_fill=BG)
    im=Image.new('RGB',(clean.width*2+910,max(clean.height,70+len(points)*112)+45),BG);im.paste(clean,(0,0));im.paste(marked,(clean.width,0));d=ImageDraw.Draw(im);px=clean.width*2+14;d.text((px,10),'Matched points: raw / mean5 / mean7 / mean9',fill=WHITE,font=font(18))
    for i,r in enumerate(points):
        py=53+i*112;d.text((px,py),f"{r['label']} ({r['x']},{r['y']}) {r['description']}",fill=WHITE,font=font(16))
        for j,m in enumerate(MEASURES):d.text((px,py+24+j*19),f"{m:4}  "+' / '.join(f"{r[m+'_'+stat]:.3f}" for stat in ('raw','mean5','mean7','mean9')),fill=COLORS[7] if m=='V' else WHITE,font=font(15))
    d.text((10,im.height-34),'Each score has its own units (normalized x255); compare points within a score, not absolute numbers between scores.',fill=WHITE,font=font(16));im.save(OUT/'R01284-pale-peak-score-comparison.png')
    # Confirmed separate origins: endpoints remain proposals; no identity merge.
    cells=[];box=[965,2652,1016,2689]
    for n in (5,7,9):
      for m in MEASURES:
        im,proj=panel(rgb,box,7,106);d=ImageDraw.Draw(im);d.text((8,7),f'{m}: {n}x{n}, radius16, raw24/mean2',fill=WHITE,font=font(14))
        for k,(label,color) in enumerate([('central-yellow','#99ff75'),('shadowed-neighbor','#00eaff')]):
            r=next(r for r in focus if r['case']==label and r['measure']==m and r['window']==n and r['policy']=='raw24-mean2');draw_path(im,proj,r['climb']['steps']+r['path'][1:],color);d.text((8,34+22*k),f"{label}: {r['endpoint']}",fill=color,font=font(13))
        d.text((8,80),'Separate origins preserved; no automatic merge',fill=WHITE,font=font(12));cells.append(im)
    join(cells,OUT/'R01284-separate-neighbors-all-measures.png',rows=3)
    loose=[]
    for n in (7,9):
      for m in MEASURES:
        im,proj=panel(rgb,box,7,106);d=ImageDraw.Draw(im);wrong=n==9 or m in ('V','VS');d.text((8,7),f'{m} mean{n}, mean6: '+('UNSAFE CROSSING' if wrong else 'separate proposals'),fill='#ff85a6' if wrong else WHITE,font=font(13))
        for k,(label,color) in enumerate([('central-yellow','#99ff75'),('shadowed-neighbor','#00eaff')]):
            r=next(r for r in focus if r['case']==label and r['measure']==m and r['window']==n and r['policy']=='raw24-mean6');draw_path(im,proj,r['climb']['steps']+r['path'][1:],color);d.text((8,34+22*k),f"{label}: {r['endpoint']}",fill=color,font=font(13))
        d.text((8,80),'Diagnostic only; confirmed separate origins',fill=WHITE,font=font(12));loose.append(im)
    join(loose,OUT/'R01284-permissive-boundary-failures.png',rows=2)
    # Current supported coordinates: all sources in prior selected12 review.
    current_ids={crop:{s['id'] for s in c['starts'] if any(z['source']=='straight-0-selected12' and z['role']=='supported-coordinate' and z['status']=='retained' for z in s['origins'])} for crop,c in legacy.items()};current=[];guard_control=[]
    for line in gzip.open(OUT/'photo-searches.jsonl.gz','rt'):
        r=json.loads(line)
        if r['radius']==16 and r['window']==7 and r['legacy'] and r['policy'] in ('raw24-mean2','common-V-raw24-mean2'):
            guard_control.append({k:r[k] for k in ('crop','measure','start_id','policy','anchor','endpoint','end_mean')})
            if r['start_id'] in current_ids[r['crop']] and r['policy']=='raw24-mean2':current.append(r)
    csvsave(OUT/'common-guard-comparison.csv',guard_control);csvsave(OUT/'current-supported-comparison.csv',[{k:r[k] for k in ('crop','measure','start_id','start','anchor','endpoint','anchor_mean','end_mean','gain','climb_stop')} for r in current])
    for crop,c in legacy.items():
        panels=[]
        for m in ('original',)+MEASURES:
            im,proj=panel(rgb,c['box'],7,65);d=ImageDraw.Draw(im);d.text((9,9),'Original photograph' if m=='original' else NAMES[m],fill=WHITE,font=font(16))
            if m!='original':
                d.text((9,34),'Current supported origins; mean7, radius16',fill=WHITE,font=font(14))
                for r in current:
                    if r['crop']==crop and r['measure']==m:draw_path(im,proj,r['path'],'#00eaff')
            panels.append(im)
        join(panels,OUT/f'{crop}-current-supported-four-measures.png')
    # Compact reference-score table used by the scientific report.
    text=['# R270 evidence','', '[Scientific report](../../BRIGHTNESS_COMPARISON_R270.md) · [All independent maxima](MAXIMA_INDEX.md)','',
      'Start with the [pale-peak score comparison](R01284-pale-peak-score-comparison.png) and [separate neighboring origins at every score/window](R01284-separate-neighbors-all-measures.png), plus [permissive boundary failures](R01284-permissive-boundary-failures.png). Photographic displays use ICC-converted sRGB. Historical V and experimental V/S use original native RGB; standard Y/OKLab use ICC-converted sRGB, as documented in color-profile.json. The initial all-native-as-sRGB experiment survives in native-rgb-control.','', '| Example | Original photograph and all four measures |','|---|---|']
    for crop,label in index:text.append(f'| {crop} {label} | [5/7/9 paths and endpoints]({crop}-{label}-four-measures.png) |')
    text+=['','All previously displayed supported coordinates: [R00956](R00956-current-supported-four-measures.png), [R01284](R01284-current-supported-four-measures.png).','',
      '- `candidate-points.json`, `*-candidate-measurements.csv`: union of every independent raw/mean maximum and prior candidates, cross-score values, prominence/context censor flags and original HSV/background evidence.','- `*-fields.npz`: source native RGB, ICC-managed sRGB, fixed native HSV/background, unrounded float64 score rasters, raw 1e-9-unit integer scores and exact 5/7/9 sums.','- `starts.json`, `legacy-starts.json`: all original starts, plus each measure’s own independent raw/mean maximum pixels. No V-prominence gate.','- `photo-climbs.jsonl.gz`: every guarded/unguarded prefix, step, score, blocked alternative and stationary-plateau diagnosis.','- `photo-searches.jsonl.gz`, `search-endpoints.csv.gz`: every radius/policy/measure result and selected route. Named examples also preserve full reachable predecessor trees and blocked frontier edges.','- `focus-results.json`, `focus-candidate-decisions.csv`, `alternative-paths.jsonl.gz`: every named-example endpoint and candidate decision; direct violations, shortest admissible and greatest raw/mean-bottleneck paths.','- `pale-peak-matched-coordinates.{csv,json}`, `common-guard-comparison.csv`: matched-point score rankings and original-V-anchor/raw-guard control.','- `native-rgb-control/`: preserved initial experiment treating native RGB as sRGB; it isolates the newly inspected ICC-profile issue.','- `synthetic-inputs.npz`, `synthetic-truth.npz`, `synthetic-fields/`, `synthetic-starts.json`, `synthetic-results.csv`, `synthetic-*.jsonl.gz`: complete known-scene arrays, all raw/mean maximum masks and paired paths. Truth is evaluation-only.','- `input-hashes.json`, `artifact-hashes.json`, `validation.json`, `tests.log`, `budget.json`: old evidence preservation, exact baseline replay, numerical checks and shared30-minute compute deadline.','',
      'Reproduce (Python3.12 environment):','', '```sh','MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.experiment_r270','MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r270','MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.review_r270','MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m unittest photo2.bead_detection.test_brightness_r270 > photo2/review/r270/tests.log 2>&1','MPLCONFIGDIR=/tmp/beads-r270-mpl .venv/bin/python -m photo2.bead_detection.validate_r270','```','', 'For a fresh run, archive the completed R270 directory first; experiment_r270 initializes a 30-minute deadline only when budget.json does not exist. Production detector, growth, viewer, bead geometry and indexing remain untouched.']
    (OUT/'README.md').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()

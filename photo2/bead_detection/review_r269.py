"""Original-photo comparisons, nonoverlapping competing-point labels and tables."""
import csv,gzip,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .audit_r267 import photo,FONT,save,csvsave
from .experiment_r269 import OUT,PRIOR,FOCUS

BG='#172028';WHITE='#ffffff';CYAN='#00efff';ORANGE='#ffb347';GREEN='#9aff75';PINK='#ff85a6'
font=lambda n:ImageFont.truetype(FONT,n)

def photo_panel(rgb,box,scale=12,header=60):
    x0,y0,x1,y1=box;w=(x1-x0)*scale;h=(y1-y0)*scale
    im=Image.new('RGB',(w,h+header),BG);im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(0,header))
    return im,lambda x,y:((x-x0+.5)*scale,header+(y-y0+.5)*scale)

def path_draw(im,project,path,color,width=2,start=True):
    d=ImageDraw.Draw(im);pts=[project(p['x'],p['y']) for p in path]
    if len(pts)>1:d.line(pts,fill=color,width=width)
    if not pts:return
    if start:
        x,y=pts[0];d.rectangle((x-4,y-4,x+4,y+4),outline=WHITE,width=1)
    x,y=pts[-1];d.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2)

def peak_map(rgb,box,candidates,status,path,title):
    im,project=photo_panel(rgb,box,18,95);d=ImageDraw.Draw(im);occupied=[];markers=[];placements=[]
    d.text((12,8),title,fill=WHITE,font=font(17));d.text((12,35),'Green best mean | cyan reachable lower | pink blocked | gray outside radius',fill=WHITE,font=font(14));d.text((12,59),'C numbers identify competing pixels, not beads. Exact reasons in accompanying table.',fill=WHITE,font=font(14))
    for c in candidates:
        x,y=project(c['x'],c['y']);markers.append((x-5,y-5,x+5,y+5))
    def overlap(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
    for c,marker in zip(candidates,markers):
        x,y=project(c['x'],c['y']);label=c['id'];bw=d.textbbox((0,0),label,font=font(14))[2]+6;bh=21;chosen=None
        for radius in range(11,700,10):
            for angle in np.linspace(-math.pi/2,3*math.pi/2,32,endpoint=False):
                xx=int(x+radius*math.cos(angle)-bw/2);yy=int(y+radius*math.sin(angle)-bh/2);b=(xx,yy,xx+bw,yy+bh)
                if xx<1 or yy<96 or b[2]>=im.width or b[3]>=im.height:continue
                if any(overlap(b,z) for z in occupied+markers):continue
                chosen=b;break
            if chosen:break
        assert chosen is not None
        occupied.append(chosen);reason=status.get(c['id'],'outside-search-radius');col=GREEN if reason=='best-mean-proposal' else CYAN if reason.startswith('reachable') else '#aaaaaa' if reason=='outside-search-radius' else PINK
        placements.append((c,x,y,chosen,col))
    for c,x,y,b,col in placements:d.line((x,y,(b[0]+b[2])/2,(b[1]+b[3])/2),fill=col,width=1)
    for c,x,y,b,col in placements:
        d.rectangle(b,fill=BG);d.text((b[0]+3,b[1]+1),c['id'],fill=col,font=font(14));d.ellipse((x-3,y-3,x+3,y+3),outline=col,width=2)
    assert all(not overlap(a,b) for i,a in enumerate(occupied) for b in occupied[i+1:]);im.save(path)
    return dict(labels=len(candidates),overlapping_labels=0)

def main():
    rgb=photo();focus=json.load(open(OUT/'focus-results.json'));allc=json.load(open(OUT/'all-competing-points.json'));cases=json.load(open(OUT/'starts.json'))
    decisions=list(csv.DictReader(open(OUT/'focus-candidate-decisions.csv')));layout={};neighbor_rows=[];summary_rows=[];links=[]
    bycase={}
    for crop,pairs in FOCUS.items():
      for label,pid in pairs:
        records=[r for r in focus if r['crop']==crop and r['case']==label];bycase[crop,label]=records
        primary=[next(r for r in records if r['window']==n and r['policy']=='raw24-mean2') for n in (5,7,9)]
        anchors=np.array([r['anchor'] for r in primary]);x0=int(anchors[:,0].min())-20;y0=int(anchors[:,1].min())-20;x1=int(anchors[:,0].max())+21;y1=int(anchors[:,1].max())+21;box=[x0,y0,x1,y1]
        cards=[]
        for title,row in [('Original photograph',None)]+[(f'{n}x{n}: R268 yellow, broader cyan',r) for n,r in zip((5,7,9),primary)]:
            im,project=photo_panel(rgb,box,10,84);d=ImageDraw.Draw(im);d.text((8,8),title,fill=WHITE,font=font(15))
            if row:
                path_draw(im,project,row['r268_trace']['steps'],ORANGE);path_draw(im,project,row['path'],CYAN)
                d.text((8,33),f"r16: {row['anchor']} -> {row['endpoint']}",fill=WHITE,font=font(13));d.text((8,54),f"mean {row['anchor_mean']:.2f} -> {row['end_mean']:.2f}; raw24 / mean2",fill=WHITE,font=font(13))
                summary_rows.append({k:row[k] for k in ('crop','case','window','anchor','endpoint','anchor_mean','end_mean','gain','steps','raw_floor','mean_floor')})
            cards.append(im)
        strip=Image.new('RGB',(sum(i.width for i in cards),max(i.height for i in cards)),BG);off=0
        for im in cards:strip.paste(im,(off,0));off+=im.width
        strip.save(OUT/f'{crop}-{label}-comparison.png')
        candidates=[c for c in allc[crop] if min((c['x']-a[0])**2+(c['y']-a[1])**2 for a in anchors)<=256]
        status={r['candidate_id']:r['reason'] for r in decisions if r['crop']==crop and r['case']==label and r['window']=='7' and r['radius']=='16' and r['policy']=='raw24-mean2'}
        layout[crop+'-'+label]=peak_map(rgb,box,candidates,status,OUT/f'{crop}-{label}-all-peaks.png',f'{crop} {label} | all competing points | mean7, radius16, raw24/mean2')
        lines=[f'# {crop} {label}: all competing points','',f'[Clean original and paths]({crop}-{label}-comparison.png) · [Numbered photographic map]({crop}-{label}-all-peaks.png)','',
            'All original raw maxima, new mean maxima and preserved R268 endpoints within 16 pixels of any of the three anchors. Decisions below use mean7 / radius16 / raw24-mean2; all other controls remain in focus-candidate-decisions.csv. Accepted means route/score eligibility, never assigned bead identity. Prominence is raw-V topographic prominence; a non-raw-maximum point has zero, not a missing measurement.','',
            '| Point | Native x,y | Raw V | Mean5 | Mean7 | Mean9 | Raw prominence | H° / S | Decision |','|---|---|---:|---:|---:|---:|---:|---|---|']
        for c in candidates:lines.append(f"| {c['id']} | {c['x']},{c['y']} | {c['raw_v']} | {c['mean5']:.2f} | {c['mean7']:.2f} | {c['mean9']:.2f} | {c['raw_prominence']} | {c['h_deg']:.1f} / {c['s']:.3f} | {status.get(c['id'],'outside-search-radius')} |")
        (OUT/f'{crop}-{label}-PEAKS.md').write_text('\n'.join(lines)+'\n');links.append((crop,label))
        for r in primary:
            n=r['window'];x,y=r['anchor'];last=r['r268_trace']['steps'][-1];blocked={tuple(b['to_xy']):b['reasons'] for b in r['r268_trace']['blocked'] if b['step']==len(r['r268_trace']['steps'])-1}
            for dy in (-1,0,1):
              for dx in (-1,0,1):
                if not(dx or dy):continue
                xx,yy=x+dx,y+dy;rr=n//2;mean=float(rgb[yy-rr:yy+rr+1,xx-rr:xx+rr+1].max(axis=2).mean())
                neighbor_rows.append(dict(crop=crop,case=label,window=n,anchor=r['anchor'],neighbor=[xx,yy],raw_v=int(rgb[yy,xx].max()),mean=mean,difference=mean-r['anchor_mean'],reason=blocked.get((xx,yy),'not-strictly-higher' if mean<=r['anchor_mean'] else 'admissible-higher'),r268_stop=r['r268_stop']))
    csvsave(OUT/'focus-summary.csv',summary_rows);csvsave(OUT/'r268-final-eight-neighbors.csv',neighbor_rows);save(OUT/'label-validation.json',layout)
    # Revisit every previously displayed supported coordinate, including reflections.
    current_ids={crop:{s['id'] for s in c['starts'] if any(o['source']=='straight-0-selected12' and o['role']=='supported-coordinate' and o['status']=='retained' for o in s['origins'])} for crop,c in cases.items()}
    current=[]
    for line in gzip.open(OUT/'photo-search-traces.jsonl.gz','rt'):
        r=json.loads(line)
        if r['start_id'] in current_ids[r['crop']] and r['radius']==16 and r['policy']=='raw24-mean2':current.append(r)
    csvsave(OUT/'current-supported-comparison.csv',[{k:r[k] for k in ('crop','start_id','window','original_start','anchor','endpoint','r268_stop','anchor_mean','end_mean','gain','steps','raw_floor','mean_floor','start_background')} for r in current])
    for crop,c in cases.items():
        box=c['box'];old=json.load(gzip.open(PRIOR/f'{crop}-traces.json.gz'));panels=[]
        for n in (0,5,7,9):
            im,proj=photo_panel(rgb,box,7,82);d=ImageDraw.Draw(im);d.text((10,10),'Original photograph' if n==0 else f'{n}x{n}: R268 yellow / broader cyan',fill=WHITE,font=font(16))
            if n:
                d.text((10,38),'All current supported points; r16 / raw24 / mean2',fill=WHITE,font=font(14))
                for r in current:
                    if r['crop']==crop and r['window']==n:
                        path_draw(im,proj,old[str(n)]['guarded12'][r['start_id']]['steps'],ORANGE)
                        path_draw(im,proj,r['path'],CYAN)
            panels.append(im)
        strip=Image.new('RGB',(panels[0].width*4,panels[0].height),BG)
        for i,panel in enumerate(panels):strip.paste(panel,(i*panel.width,0))
        strip.save(OUT/f'{crop}-all-current-supported.png')
    # The missed-looking patch: review coordinates are chosen AFTER all searches.
    # No point here is a runtime input, body label or identity constraint.
    labeled=[('A',(981,2673),'R268 mean7 endpoint'),('B',(978,2668),'nearby mean7 local peak'),('C',(976,2668),'pale raw local peak'),('D',(979,2663),'upper raw V252 peak'),('E',(980,2671),'R268 mean9 endpoint'),('F',(983,2675),'original raw seed')]
    lookup={(c['x'],c['y']):c for c in allc['R01284']};points=[dict(lookup[xy],label=label,description=desc) for label,xy,desc in labeled]
    save(OUT/'central-missed-looking-points.json',points)
    box=[967,2654,993,2683];base,project=photo_panel(rgb,box,18,68);marked=base.copy();d=ImageDraw.Draw(base);d.text((10,10),'Original central-yellow photograph',fill=WHITE,font=font(17));d=ImageDraw.Draw(marked);d.text((10,10),'Competing bright-looking pixels',fill=WHITE,font=font(17))
    for c in points:
        x,y=project(c['x'],c['y']);col=CYAN if c['label'] in ('A','E') else GREEN;d.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2);d.text((x+7,y-16),c['label'],fill=col,font=font(21),stroke_width=2,stroke_fill=BG)
    im=Image.new('RGB',(base.width*2+790,base.height+60),BG);im.paste(base,(0,0));im.paste(marked,(base.width,0));d=ImageDraw.Draw(im);px=base.width*2+15
    d.text((px,12),'HSV Value = maximum RGB channel; all values in DN',fill=WHITE,font=font(17))
    for i,c in enumerate(points):
        py=58+i*75;d.text((px,py),f"{c['label']}  ({c['x']},{c['y']})  {c['description']}",fill=WHITE,font=font(17));d.text((px,py+24),f"V {c['raw_v']} | mean5 {c['mean5']:.2f} | mean7 {c['mean7']:.2f} | mean9 {c['mean9']:.2f}",fill=WHITE,font=font(16));d.text((px,py+46),f"RGB {c['rgb']} | prominence {c['raw_prominence']} | H {c['h_deg']:.1f} S {c['s']:.3f}",fill=ORANGE,font=font(15))
    d.text((12,im.height-44),'The pale patch has stronger green/blue channels. It is not the highest neighborhood-average HSV Value.',fill=WHITE,font=font(18));im.save(OUT/'R01284-missed-looking-peak.png')
    # Explicit route to B and exact score fluctuations, not a silently chosen detour.
    alternatives=[json.loads(line) for line in gzip.open(OUT/'focus-alternative-paths.jsonl.gz','rt')]
    b=next(r for r in alternatives if r['case']=='central-yellow' and r['window']==7 and (r['x'],r['y'])==(978,2668));save(OUT/'central-alternative-route.json',b)
    route,project=photo_panel(rgb,box,18,100);d=ImageDraw.Draw(route);d.text((10,8),'Best bottleneck route to B (mean7)',fill=WHITE,font=font(16));d.text((10,34),'Diagnostic: requires 2.245 DN mean decline',fill=PINK,font=font(15));d.text((10,57),'raw/color pass; mean2 blocks; mean6 admits',fill=WHITE,font=font(14));path_draw(route,project,b['widest_mean_with_raw_and_color'],CYAN)
    panel=Image.new('RGB',(route.width+640,route.height),BG);panel.paste(route,(0,0));d=ImageDraw.Draw(panel);x=route.width+16
    d.text((x,12),'Native steps on the best mean-bottleneck path',fill=WHITE,font=font(18))
    d.text((x,52),'Step     coordinate        raw V       mean7',fill=ORANGE,font=font(17))
    for i,p in enumerate(b['widest_mean_with_raw_and_color']):d.text((x,88+i*35),f"{i:>3}       ({p['x']},{p['y']})       {p['raw_v']:>3}        {p['mean']:.6f}",fill=WHITE,font=font(17))
    for i,line in enumerate(['R268 stops immediately: 241.183673 -> 240.918367','is a decrease of 0.265306 DN, forbidden by strict ascent.','Best reachable saddle to B: 238.938776 DN.','B itself is 239.244898 DN, below A by 1.938776 DN.','Even unrestricted radius16 chooses A for mean7.']):d.text((x,365+i*33),line,fill=WHITE,font=font(15))
    panel.save(OUT/'R01284-central-alternative-route.png')
    c9=next(r for r in alternatives if r['case']=='central-yellow' and r['window']==9 and (r['x'],r['y'])==(976,2668));save(OUT/'central-five-pixel-route.json',c9)
    route,project=photo_panel(rgb,box,18,100);d=ImageDraw.Draw(route);d.text((10,8),'Exactly five pixels: E -> pale raw peak C',fill=WHITE,font=font(16));d.text((10,34),'Raw V improves 244 -> 248',fill=GREEN,font=font(15));d.text((10,57),'Mean9 declines 238.47 -> 229.16',fill=PINK,font=font(15));path_draw(route,project,c9['widest_mean_with_raw_and_color'],CYAN)
    panel=Image.new('RGB',(route.width+680,route.height),BG);panel.paste(route,(0,0));d=ImageDraw.Draw(panel);x=route.width+16
    d.text((x,12),'Best mean-bottleneck path to the pale raw peak',fill=WHITE,font=font(17));d.text((x,52),'Step     coordinate        raw V       mean9',fill=ORANGE,font=font(17))
    for i,p in enumerate(c9['widest_mean_with_raw_and_color']):d.text((x,88+i*35),f"{i:>3}       ({p['x']},{p['y']})       {p['raw_v']:>3}        {p['mean']:.6f}",fill=WHITE,font=font(17))
    for i,line in enumerate(['E=(980,2671); C=(976,2668); distance = 5.000 pixels.','R268 refuses the first step: 238.469136 -> 238.444444.','All eight immediate neighbors score lower (saved CSV).','Raw/color evidence admits a route; the mean score falls.','C has raw prominence 5 DN, H45.85 degrees, S0.496.','Even an unrestricted radius16 search keeps E for mean9.']):d.text((x,335+i*33),line,fill=WHITE,font=font(15))
    panel.save(OUT/'R01284-exact-five-pixel-route.png')
    # User-confirmed separate origins: retain both and illustrate unsafe controls.
    central=bycase['R01284','central-yellow'];shadow=bycase['R01284','shadowed-neighbor'];box=[967,2654,1015,2688];panels=[]
    for pname,title in [('original','Original: origins belong to separate beads'),('raw24-mean2','Mean2: separate endpoint proposals'),('raw24-mean6','Mean6: WRONG crossing into central patch'),('radius-only','No barriers: WRONG crossing')]:
        im,proj=photo_panel(rgb,box,10,82);d=ImageDraw.Draw(im);d.text((8,8),title,fill=PINK if pname in ('raw24-mean6','radius-only') else WHITE,font=font(14));d.text((8,34),'mean7, search radius16; green central / cyan shadow',fill=WHITE,font=font(12))
        for records,col in [(central,GREEN),(shadow,CYAN)]:
            r=next(r for r in records if r['window']==7 and r['policy']==('raw24-mean2' if pname=='original' else pname))
            path=r['r268_trace']['steps'][:1] if pname=='original' else r['r268_trace']['steps']+r['path'][1:];path_draw(im,proj,path,col)
        panels.append(im)
    im=Image.new('RGB',(panels[0].width*2,panels[0].height*2),BG)
    for j,p in enumerate(panels):im.paste(p,((j%2)*p.width,(j//2)*p.height))
    im.save(OUT/'R01284-separate-neighbor-controls.png')
    lines=['# R269 photographic evidence','', '[Concise report](../../BROADER_PEAK_SEARCH_R269.md)','',
      'Also compare all previously displayed supported coordinates: [R00956](R00956-all-current-supported.png) and [R01284](R01284-all-current-supported.png). `current-supported-comparison.csv` records each outcome.', '', 'Start with the [missed-looking central peak](R01284-missed-looking-peak.png), [exact five-pixel route](R01284-exact-five-pixel-route.png), [nearby mean-peak route](R01284-central-alternative-route.png), and [separate-neighbor controls](R01284-separate-neighbor-controls.png).','',
      '| Example | Original and 5/7/9 paths | All competing points | Measurements and exact decisions |','|---|---|---|---|']
    for crop,label in links:lines.append(f'| {crop} {label} | [comparison]({crop}-{label}-comparison.png) | [numbered photo]({crop}-{label}-all-peaks.png) | [table]({crop}-{label}-PEAKS.md) |')
    lines+=['','Numerical files retain all 451 original starting coordinates and their sources. Every original R267 raw maximum is present in the competing-point inventory; new mean maxima and old R268 endpoints remain separate types. No proposal receives a manually assigned bead identity.','',
      '- `*-all-competing-points.csv`, `all-competing-points.json`: raw V, all three means, exact raw prominence, H/S, RGB and original IDs.','- `*-search-endpoints.csv`: all four radii and four policies for all starts/windows.','- `photo-search-traces.jsonl.gz`: every winning route, reconstructible predecessor tree to every reachable point, and every blocked frontier edge with reasons. Tree predecessors are flat indices in the saved graph shape/origin.','- `focus-candidate-decisions.csv`: accept/reject reason and certified bottleneck capacities for every nearby competing point in each named example/control.','- `focus-alternative-paths.jsonl.gz`: direct route and its violations, shortest admissible route, best raw-bottleneck color-only route, best mean-bottleneck raw/color route and best raw-bottleneck mean/color route.','- `r268-final-eight-neighbors.csv`: the exact eight alternatives at each old stopping point.','- `*-score-images.npz`: original native RGB, HSV, V, exact score sums and unchanged background codes across the full search halo.','- `synthetic-starts.json`, `synthetic-results.csv`, `synthetic-search-traces.jsonl.gz`: every raw synthetic maximum, image-only eligibility, all controls and full selected traces; ground truth is evaluation-only. Original scene arrays remain in R268.','- `input-hashes.json`, `artifact-hashes.json`, `validation.json`, `tests.log`: preservation and numerical checks.','',
      'Reproduce from the repository root:','', '```sh','MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.experiment_r269','MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.synthetic_r269','MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.review_r269','MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m unittest photo2.bead_detection.test_search_r269 > photo2/review/r269/tests.log 2>&1','MPLCONFIGDIR=/tmp/beads-r269-mpl .venv/bin/python -m photo2.bead_detection.validate_r269','```','', 'Production detector, previous evidence, outlines, geometry and indexing remain unchanged.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()

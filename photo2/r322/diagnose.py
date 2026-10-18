"""Post-freeze photographic failure analysis, not tracker repair or refitting."""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageOps,ImageDraw,ImageFont
from photo2.r322.tracker import ROOT,CROP,save
from photo2.r322.review import FONT
OUT=ROOT/'photo2/r322/results'

def main():
    g=json.loads((OUT/'graph.json').read_text());v=json.loads((OUT/'validation.json').read_text())
    maker=json.loads((ROOT/'photo2/manual-labels-r161.json').read_text());points={p['number']:[p['x'],p['y']] for p in maker['annotations']}
    hist=json.loads((ROOT/'photo2/review/r161/report.json').read_text());co=hist['conditional_charts'][0]['coordinates']
    transform=lambda c:np.array([c[0]+c[1],-c[0]])
    origin=transform(co['23']);nodes={p['id']:p for p in g['intersections']};rows=[]
    for m in v['associations']:
        if not m['status'].startswith('unambiguous'):continue
        n=nodes[m['node']];expected=transform(co[str(m['maker'])])-origin;delta=np.array(n['relative_ab'])-expected
        rows.append(dict(maker=m['maker'],node=n['id'],xy=n['xy'],observed_color=n['color'],
            frozen_ab=n['relative_ab'],heldout_expected_ab=expected.tolist(),residual_ab=delta.tolist(),
            A_index_error=int(7*delta[0]+6*delta[1]),B_index_error=int(6*delta[0]+7*delta[1]),
            bandwidth_shifts_px=n['bandwidth_crossing_shifts_px'],priority=m['priority']))
    unmatched=[o for o in g['observations'] if o['id'] not in {n['observation'] for n in g['intersections']}]
    wrong=[e for e in v['automatic_links'] if e['validation']=='disagrees with maker chart']
    record=dict(index_residuals=rows,chart_consistent_matched_beads=sum(r['residual_ab']==[0,0] for r in rows),
        incorrect_index_beads=[r for r in rows if r['residual_ab']!=[0,0]],wrong_links=wrong,unassigned_observations=unmatched,
        classification='Photographic tracker row-identity error. Not evidence for any A/B/C/D defect in a frozen 3D model.',
        first_error='Maker 2→3 is d1, but F0-02 calls it the down-right diagonal d2. F0-03 similarly calls 4→5 d2; implied 4→3 is then wrong.',
        mechanism='The appearance phase field changes row identity near the left pigment transition. Its smooth, stable bands need not be bead diagonals. Cycles constructed from those phases still close.',
        causality_limit='The wrong continuation is demonstrated. A unique optical or texture cause is not established. This is not a proof that Fourier evidence cannot assist a surface-based tracker.',
        r171='11→14 and 14→16 both recovered as F1, without a point-pair angle gate. Reflection on14 is not relocated.',
        deferred_models=[dict(name=n,status='E: insufficient independently trustworthy automatic photographic topology; diagnostic comparison not run') for n in ['R319 best-full','R321 geometry-best','R321 photo-sized-rescue']],
        pattern='Deferred; no repeat candidates tested.',
        future_fix='Preserve joint path alternatives through several supported bead surfaces and cross-family cells; phase bands may suggest direction but cannot certify row identity. Do not silently splice the failed bands using held-out maker links.')
    save(OUT/'diagnosis.json',record)
    # Every panel uses the untouched RGB; evaluator-only paths are visibly labeled.
    source=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    panels=[]
    for crop,title,labels,paths in [
        ((1185,250,1285,355),'FAILURE: orange = wrong automatic links; white dashed = held-out row',list(range(1,12)),[[1,4,8,11],[2,5,9]]),
        ((1260,240,1340,325),'RECOVERED: 11 → 14 → 16; reflection locations remain unchanged',[11,14,16,17,13,15],[[11,14,16]]),
        ((1340,235,1508,330),'INTERIOR: consistent local relative indexing, still A/B ambiguous',[20,21,22,23,24,25,26,27,31,32,33,34,38,39],[])]:
        scale=6;im=source.crop(crop).resize(((crop[2]-crop[0])*scale,(crop[3]-crop[1])*scale),Image.Resampling.NEAREST)
        canvas=Image.new('RGB',(max(1100,im.width),im.height+65),'#181818');canvas.paste(im,(0,65));d=ImageDraw.Draw(canvas)
        d.text((10,10),title,font=ImageFont.truetype(FONT,18),fill='white')
        def pos(p):return ((p[0]-crop[0])*scale,(p[1]-crop[1])*scale+65)
        for t in g['tracks']:
            pts=[pos(p) for p in t['points']]
            for a,b in zip(pts,pts[1:]):
                if 0<=a[0]<im.width and 65<=a[1]<canvas.height and 0<=b[0]<im.width and 65<=b[1]<canvas.height:d.line([a,b],fill=['#00eaff','#9cff40'][t['family']],width=2)
        for path in paths:
            for a,b in zip(path,path[1:]):
                pts=[pos(p) for p in np.linspace(points[a],points[b],31)]
                for i in range(0,30,5):d.line(pts[i:i+3],fill='white',width=3)
        for e in wrong:
            a,b=pos(nodes[e['source']]['xy']),pos(nodes[e['target']]['xy'])
            if all(0<=p[0]<im.width and 65<=p[1]<canvas.height for p in (a,b)):d.line([a,b],fill='#ff852d',width=5)
        for number in labels:
            p=pos(points[number]);d.text((p[0]+5,p[1]-20),str(number),font=ImageFont.truetype(FONT,20),fill='white',stroke_width=2,stroke_fill='black')
        panels.append(canvas)
    sheet=Image.new('RGB',(max(p.width for p in panels),sum(p.height for p in panels)+20*(len(panels)-1)),'#181818');y=0
    for p in panels:sheet.paste(p,(0,y));y+=p.height+20
    sheet.save(OUT/'failure-and-recovery.png')
    print('Conditional chart consistent',record['chart_consistent_matched_beads'],'of',len(rows),'matched beads')
if __name__=='__main__':main()

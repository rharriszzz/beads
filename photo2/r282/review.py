"""Static real-photo comparisons and a compact phase-separated review browser."""
import html
import json
import textwrap
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT,OUT,read,save,photo,pixels,COLORS

REVIEW=ROOT/'photo2/review/r282'
PALETTE={'red':'#ef404b','yellow':'#ffce35','black':'#141824','unknown':'#b4b6bf'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def label(draw,xy,text,width=42,size=14,fill='white'):
    font=ImageFont.truetype(FONT,size)
    for line in textwrap.wrap(str(text),width):
        draw.text(xy,line,fill=fill,font=font);xy=(xy[0],xy[1]+size+4)
    return xy[1]


def annotated(raw,origin,region=None,centroid=None,outline=None):
    out=np.asarray(raw).copy();h,w=out.shape[:2]
    mask=np.zeros((h,w),bool)
    if region:
        xy=pixels(region)-origin;ok=(xy[:,0]>=0)&(xy[:,1]>=0)&(xy[:,0]<w)&(xy[:,1]<h);xy=xy[ok]
        mask[xy[:,1],xy[:,0]]=True
        out[mask]=(out[mask]*.45+np.array([30,240,150])*.55).astype(np.uint8)
        edge=mask&~ndi.binary_erosion(mask);out[edge]=[30,240,255]
    if outline:
        m=np.zeros_like(mask);xy=pixels(outline)-origin;ok=(xy[:,0]>=0)&(xy[:,1]>=0)&(xy[:,0]<w)&(xy[:,1]<h);xy=xy[ok];m[xy[:,1],xy[:,0]]=True
        out[m&~ndi.binary_erosion(m)]=[255,150,0]
    im=Image.fromarray(out).resize((288,288),Image.Resampling.NEAREST)
    if centroid is not None:
        c=(np.array(centroid)-origin)*3;d=ImageDraw.Draw(im);d.line((c[0]-5,c[1],c[0]+5,c[1]),fill='white',width=2);d.line((c[0],c[1]-5,c[0],c[1]+5),fill='white',width=2)
    return im


def case_panel(identifier,row,alternatives,baseline,native,first):
    center=np.rint(row['seed']).astype(int);origin=center-48
    raw=Image.fromarray(native).crop((*origin,*(origin+96)))
    raw.save(REVIEW/(identifier+'-raw.png'));raw.resize((576,576),Image.Resampling.NEAREST).save(REVIEW/(identifier+'-enlarged.png'))
    entries=[('Original pixels',None,None,None,'Native 96 x 96 crop; enlargement is nearest-neighbor.'),
             ('Previous image-only support',baseline,baseline.get('centroid') if baseline else None,None,'Historical Phase1 support, preserved unchanged.')]
    if identifier in first:
        old=first[identifier][2];reg=old['region'];entries.append(('First integrated pass',reg,reg['centroid'] if reg else None,None,old['color']+' / '+old['quality']+'; '+', '.join(old['reasons'])))
    # Exact same recent-review yellow/black areas. This is review-only historical evidence.
    if identifier in ('C-0603-1587','K-0603-1624'):
        olddir=ROOT/'photo2/r281/results/real';doc=read(olddir/'measurements.json');freeze=read(olddir/'prediction-freeze.json');anchor=read(olddir/'anchors.json')
        target='model-02-k-06-candidate' if identifier.startswith('C-') else 'model-02-k-07-candidate'
        result=next(r for r in doc['rows'] if r['id']==target)['result'];hyp=next(r for r in freeze['predictions'] if r['id']==target)['hypothesis'];ox,oy=anchor['origin']
        reg={'runs':[[y+oy,a+ox,b+ox] for y,a,b in result['support']]}
        boundary={'runs':[[y+oy,a+ox,b+ox] for y,a,b in hyp['h1_surfaces'][str(hyp['target'])]]}
        centroid=(np.array(result['location'])+[ox,oy]).tolist() if result['location'] else None
        entries.append(('R281 Phase2 review',reg,centroid,boundary,'Orange: predicted model boundary. Green: old geometry-assisted support. Neither is a Phase1 measurement.'))
    explanations={
        'A':'Broad connected material; may wander or retain necks. Black: broad dark/neutral region.',
        'B':'Compact local core; may lose useful area. Black: bounded dark body around reflection.',
        'C':'Colored: neck removal and native inset. Black: owned reflection with measured dark collar; not full-body boundary.'}
    for a in alternatives:
        reg=a['region'];m=a['metrics'];text=f"{a['quality']}; {a['color']}; {m['area']}px; {m['components']} component(s); solidity {m['solidity']:.2f}. "+explanations[a['method']]
        if a['reasons']:text+=' Flags: '+', '.join(a['reasons'])
        entries.append((f"Attempt {a['method']}",reg,reg['centroid'] if reg else None,None,text))
    canvas=Image.new('RGB',(4*306,2*450),(24,29,36));draw=ImageDraw.Draw(canvas)
    for j,(title,reg,centroid,boundary,caption) in enumerate(entries):
        x=(j%4)*306+8;y=(j//4)*450
        label(draw,(x,y+5),title,35,15);canvas.paste(annotated(raw,origin,reg,centroid,boundary),(x,y+33))
        label(draw,(x,y+326),caption,40,12)
    selected=next(a for a in alternatives if a['method']=='C')
    review_note=('Prefer C as a compact measured interior; retain A/B for the area/shape tradeoff.' if selected['quality']=='high'
                 else 'No certified best measurement: C remains uncertain/rejected. A/B do not override its unresolved ownership.')
    label(draw,(3*306+8,450+8),identifier+'\n'+review_note,34,15)
    name=identifier+'-attempts.png';canvas.save(REVIEW/name)
    return dict(id=identifier,file=name,raw=identifier+'-raw.png',enlarged=identifier+'-enlarged.png',note=review_note,
                final_status=row['status'],final_notes=row['notes'],attempts=[dict(method=a['method'],quality=a['quality'],metrics=a['metrics'],reasons=a['reasons']) for a in alternatives])


def phase1_review(native,p1):
    rows=p1['records'];by={r['record_id']:r for r in rows};attempt=read(OUT/'phase1-attempts.json.gz');baseline=read(OUT/'phase1-baseline-supports.json.gz')
    first=read(ROOT/'photo2/r282/first-pass/phase1-attempts.json.gz')
    ids=['C-0603-1587','K-0603-1624','C-0565-1588']
    for color in COLORS:
        eligible=[r for r in rows if r['color']==color and r['status']=='high' and r['near_centerline']]
        if eligible:
            chosen=min(eligible,key=lambda r:(r['centerline_distance'],-r['metrics']['area'],r['record_id']))
            if chosen['record_id'] not in ids:ids.append(chosen['record_id'])
    cases=[case_panel(k,by[k],attempt[k],baseline.get(k),native,first) for k in ids if k in by]
    im=Image.fromarray(native).resize((762,955));draw=ImageDraw.Draw(im);scale=762/native.shape[1]
    curve=np.array(read(OUT/'centerline.json')['points']);draw.line([tuple(p*scale) for p in curve[::8]],fill='#ff9e34',width=1)
    colors={'high':'#24ffff','medium':'#ffe66e','unresolved':'#f36dff','rejected':'#ffffff'}
    for row in rows:
        if row['status']=='rejected':continue
        p=np.array(row['measured_photo_location'] or row['seed'])*scale;r=1.4 if row['status']=='high' else .7
        draw.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),outline=colors[row['status']])
    im.save(REVIEW/'phase1-overview.png')
    curve_doc=read(OUT/'centerline.json');distance=np.array(curve_doc['nearest_high_distance'])
    # Deterministic worst uncovered station in each of eight arcs, including failures.
    gaps=[];sheet=Image.new('RGB',(4*260,2*300),(24,29,36));sd=ImageDraw.Draw(sheet)
    for sector in range(8):
        start=sector*len(curve)//8;end=(sector+1)*len(curve)//8;j=start+int(distance[start:end].argmax());center=np.rint(curve[j]).astype(int);origin=center-48
        raw=Image.fromarray(native).crop((*origin,*(origin+96)));ann=np.array(raw)
        points=[r for r in rows if abs(r['seed'][0]-center[0])<48 and abs(r['seed'][1]-center[1])<48]
        image=raw.resize((240,240),Image.Resampling.NEAREST);d=ImageDraw.Draw(image)
        for r in points:
            q=(np.array(r['measured_photo_location'] or r['seed'])-origin)*2.5;d.ellipse((q[0]-2,q[1]-2,q[0]+2,q[1]+2),outline=colors[r['status']],width=2)
        x=(sector%4)*260;y=(sector//4)*300;sheet.paste(image,(x+10,y+24));label(sd,(x+10,y+3),f'Arc {sector+1}: gap {distance[j]:.1f}px',35,13)
        gaps.append(dict(sector=sector,center=center.tolist(),nearest_high_distance=float(distance[j]),records=[r['record_id'] for r in points]))
    sheet.save(REVIEW/'phase1-gaps.png');save(REVIEW/'phase1-cases.json',cases);save(REVIEW/'phase1-gaps.json',gaps)
    return cases


def phase2_review(native,p2):
    items=[]
    for name in p2['selected_ids']:
        doc=read(OUT/(name+'-inventory.json.gz'));rows=doc['records'];im=Image.fromarray(native).resize((762,955));draw=ImageDraw.Draw(im);scale=762/native.shape[1]
        for r in rows:
            if not r['visibility']:continue
            point=r['predicted_visible_centroid'];p=np.array(point)*scale
            color=PALETTE[r['color']] if r['color_reliability']>=.6 else '#9f9fa6'
            radius=1.8 if r.get('source_record_ids') else .6
            draw.ellipse((p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius),fill=color)
        im.save(REVIEW/(name+'-overlay.png'))
        matched=[r for r in rows if r.get('source_record_ids') and r['measured_photo_location']]
        good=sorted(matched,key=lambda r:(-r['phase1_support_fraction'],-r['color_reliability']))[:2]
        bad=sorted(matched,key=lambda r:(r['phase1_support_fraction'],r['color_reliability']))[:2]
        candidates=good+bad;canvas=Image.new('RGB',(4*310,430),(24,29,36));d=ImageDraw.Draw(canvas);examples=[]
        for j,r in enumerate(candidates):
            origin=np.rint(r['measured_photo_location']).astype(int)-48;raw=Image.fromarray(native).crop((*origin,*(origin+96)))
            pane=annotated(raw,origin,r['measured_support'],r['measured_photo_location'],r['visible_support']);canvas.paste(pane,(j*310+8,28))
            label(d,(j*310+8,5),'Good support' if j<2 else 'Uncertain ownership',36,14)
            label(d,(j*310+8,322),f"Index {r['physical_model_index']}: {r['color']}, color {r['color_reliability']:.2f}, identity {r['phase2_identity_reliability']:.2f}; Phase1 containment {r['phase1_support_fraction']:.2f}.",39,13)
            examples.append({k:r[k] for k in ('record_id','physical_model_index','source_record_ids','color','color_reliability','phase2_identity_reliability','phase1_support_fraction','notes')})
        canvas.save(REVIEW/(name+'-examples.png'));items.append(dict(id=name,overlay=name+'-overlay.png',examples=name+'-examples.png',records=examples))
    save(REVIEW/'phase2-examples.json',items);return items


def phase3_review(p3):
    items=[]
    for model in p3['models']:
        name=model['id'];doc=read(OUT/(name+'-patterns.json'));candidates=doc['weighted'][:5]
        width=1000;height=160+sum(70+24*int(np.ceil(c['period']/50)) for c in candidates)
        im=Image.new('RGB',(width,height),(24,29,36));d=ImageDraw.Draw(im);label(d,(15,12),name+' — conditional patterns; no accepted reconstruction',90,20)
        y=55
        for c in candidates:
            label(d,(15,y),f"Period {c['period']}, {c['repeats']} complete repeats; CV score {c['validation_score']:.3f}; unknown {c['unknown_slots']}/{c['period']}; weighted disagreement {c['disagreement']:.3f}",110,14);y+=44
            for j,color in enumerate(c['sequence']):
                x=15+(j%50)*19;yy=y+(j//50)*24;d.rectangle((x,yy,x+16,yy+18),fill=PALETTE[color],outline='white' if color=='unknown' else '#555')
                if color=='unknown':d.line((x,yy,x+16,yy+18),fill='#666')
            y+=24*int(np.ceil(c['period']/50))+26
        label(d,(15,y+5),'Gray/crossed = unknown. Origin/reversal and physical correspondence remain uncertain. Colors above are pattern hypotheses; measured upstream colors are unchanged.',110,14)
        im.save(REVIEW/(name+'-patterns.png'));items.append(dict(id=name,file=name+'-patterns.png'))
    return items


def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();p1=read(OUT/'phase1.json.gz');p2=read(OUT/'phase2.json');p3=read(OUT/'phase3.json')
    cases=phase1_review(native,p1);physical=phase2_review(native,p2);patterns=phase3_review(p3)
    counts=p1['summary']['counts'];fig,axes=plt.subplots(1,3,figsize=(14,4))
    first=read(ROOT/'photo2/r282/first-pass/phase1-summary.json')
    labels=['high','medium','unresolved','rejected'];x=np.arange(4)
    axes[0].bar(x-.18,[first['counts'].get(k,0) for k in labels],.36,label='First integrated pass')
    axes[0].bar(x+.18,[counts.get(k,0) for k in labels],.36,label='Repaired pass');axes[0].set(xticks=x,xticklabels=labels,title='Phase1 algorithmic reliability');axes[0].tick_params(axis='x',rotation=20);axes[0].legend(fontsize=8)
    c=p2['candidates'];axes[1].bar(np.arange(len(c)),[r['evaluation']['holdout']['mean_support'] for r in c]);axes[1].set(xticks=np.arange(len(c)),xticklabels=[r['id'] for r in c],title='Held-out anchor support',ylim=(0,1));axes[1].tick_params(axis='x',rotation=75,labelsize=8)
    for m in p3['models']:axes[2].plot(m['leading_periods'],m['leading_scores'],'o-',label=m['id'])
    axes[2].set(title='Leading weighted pattern hypotheses',xlabel='Period',ylabel='Held-out loss + complexity');axes[2].legend(fontsize=7);fig.tight_layout();fig.savefig(REVIEW/'summary.png',dpi=150);plt.close(fig)
    gallery=[dict(phase='Phase 1',title='Geographic coverage',file='phase1-overview.png',note='Cyan high, yellow medium, magenta unresolved; orange is the image-derived reference centerline.'),
             dict(phase='Phase 1',title='Worst coverage gap in each arc',file='phase1-gaps.png',note='These retained gaps prevent a completeness claim.')]
    gallery += [dict(phase='Phase 1',title=c['id']+' — A/B/C',file=c['file'],note=c['note']) for c in cases]
    for m in physical:
        gallery += [dict(phase='Phase 2',title=m['id']+' — overlay',file=m['overlay'],note='Predicted visible centroids; colors read from photo. Gray means uncertain.'),dict(phase='Phase 2',title=m['id']+' — good/uncertain',file=m['examples'],note='Green: measured Phase1 support. Orange: predicted first-hit surface. White cross: measured centroid.')]
        if (REVIEW/(m['id']+'-pov.png')).exists():
            gallery.append(dict(phase='Phase 2',title=m['id']+' — shared-light POV',file=m['id']+'-pov.png',note='Independent POV-Ray rendering of the conditional fit. Colors are read from the image; one shared distant light. Poor appearance remains evidence against the fit.'))
    gallery += [dict(phase='Phase 3',title=m['id'],file=m['file'],note='Conditional sequence alternatives, with uncertainty. No pattern is accepted.') for m in patterns]
    save(REVIEW/'manifest.json',dict(gallery=gallery,phase1_counts=counts,selected_models=p2['selected_ids'],patterns=p3['models']))
    script='const entries='+json.dumps(gallery)+';'
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R282 three-phase review</title>
<style>body{font:16px system-ui;background:#181d24;color:#eee;margin:24px;max-width:1500px}a{color:#8ee0ff}select{padding:7px;font:inherit;margin:8px}img{max-width:100%;image-rendering:pixelated}#note{padding:12px;background:#263444}h1{font-size:26px}</style>
<h1>Three-phase reconstruction — photographic evidence first</h1><p><a href="../../R282_INTEGRATED.md">Report</a> · <a href="../../R282_SPECIFICATION.md">Specification</a> · <a href="../../R282_CHECKLIST.md">Checklist</a> · <a href="summary.png">Summary picture</a></p>
<p>Phase1 reliability is an algorithmic assessment, not verified accuracy. Physical identities and patterns remain conditional. Original and failed attempts are preserved.</p>
<select id="phase" aria-label="Phase"><option>Phase 1</option><option>Phase 2</option><option>Phase 3</option></select><select id="example" aria-label="Example"></select><p id="note"></p><img id="picture" alt="Selected static evidence panel"><p><a id="full" href="#">Open full-resolution picture</a></p><script>'''+script+'''
const phase=document.getElementById('phase'),example=document.getElementById('example');
function show(){const r=entries[+example.value];document.getElementById('picture').src=r.file;document.getElementById('picture').alt=r.title;document.getElementById('note').textContent=r.note;document.getElementById('full').href=r.file}
function load(){example.replaceChildren();entries.forEach((r,i)=>{if(r.phase===phase.value)example.add(new Option(r.title,i))});show()}
phase.onchange=load;example.onchange=show;load();</script></html>'''
    (REVIEW/'index.html').write_text(document);print('review',len(gallery),'panels',len(cases),'Phase1 cases',flush=True)


if __name__=='__main__':main()

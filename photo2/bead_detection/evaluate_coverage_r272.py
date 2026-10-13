"""Known-identity synthetic evaluation and frozen blind-photo sample association."""
import json,time,gzip,hashlib
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from matplotlib.colors import hsv_to_rgb
from .coverage_r272 import detect
from .experiment_coverage_r272 import ROOT,OUT,save,lines,check_budget

def scenes():
    yy,xx=np.mgrid[:110,:140]
    for pair in [('black','black'),('red','red'),('yellow','yellow'),('black','red'),('black','yellow'),('red','yellow')]:
        for condition in ('clear','dim','uneven','touching','multiple-highlights','colored-highlight','cast-shadow','no-black-reflection'):
            rgb=np.full((110,140,3),hsv_to_rgb([.83,.42,.78]));truth=np.zeros((110,140),np.uint8);centers=[(49,55),(79 if condition=='touching' else 87,55)]
            if condition=='cast-shadow':rgb*= (1-.65*np.exp(-((xx-68)**2+(yy-58)**2)/1100))[:,:,None]
            for body,(color,(cx,cy)) in enumerate(zip(pair,centers),1):
                rad=((xx-cx)/16)**2+((yy-cy)/19)**2;inside=rad<=1;shade=.38+.50*np.maximum(0,1-rad)**.5
                if condition=='dim':shade*=.55
                if condition=='uneven':shade*=np.clip(.75+.35*(xx-cx)/16,.3,1)
                hue=0 if color=='red' else 1/6
                body_rgb=hsv_to_rgb(np.stack([np.full_like(shade,hue),np.full_like(shade,.82),shade],axis=-1))
                highlight=np.exp(-((xx-cx+3)**2+(yy-cy+4)**2)/12)
                if condition=='multiple-highlights':highlight=np.maximum(highlight,.9*np.exp(-((xx-cx-4)**2+(yy-cy+2)**2)/10))
                if color=='black':body_rgb=np.full_like(rgb,.055)+.80*highlight[:,:,None]
                else:body_rgb=body_rgb*(1-.35*highlight[:,:,None])+.75*.35*highlight[:,:,None]
                if condition=='colored-highlight':body_rgb=body_rgb*(1-.22*highlight[:,:,None])+np.array([.90,.85,.62])*.22*highlight[:,:,None]
                if condition=='no-black-reflection' and color=='black':body_rgb[:]=.07
                rgb[inside]=body_rgb[inside];truth[inside]=body
            yield '-'.join(pair)+'-'+condition,np.rint(np.clip(rgb,0,1)*255).astype(np.uint8),truth,dict(enumerate(pair,1)),condition
    for hue in (.0,.16,.5,.83):
        rgb=np.full((110,140,3),hsv_to_rgb([hue,.4,.75]));rgb*= (1-.5*np.exp(-((xx-70)**2+(yy-55)**2)/500))[:,:,None]
        yield f'background-{hue}',np.rint(rgb*255).astype(np.uint8),np.zeros((110,140),np.uint8),{},'background'

def metric(beads,truth,colors):
    totals={c:dict(visible=sum(v==c for v in colors.values()),detected=0,accepted=0,false_positive=0,duplicate_extras=0,wrong_color=0,background_pixels=0,other_body_pixels=0) for c in ('black','red','yellow')};owners=Counter();associations=[]
    for b in beads:
        x,y=b['brightest']['x'],b['brightest']['y'];body=int(truth[y,x]);c=b['color'];m=totals[c];m['accepted']+=1;correct=body>0 and colors[body]==c
        if not correct:m['false_positive']+=1;m['wrong_color']+=int(body>0)
        elif owners[body]:m['duplicate_extras']+=1;m['false_positive']+=1
        else:m['detected']+=1
        owners[body]+=1;vals=[int(truth[y,x]) for y,a,z in b['region']['runs'] for x in range(a,z+1)];m['background_pixels']+=sum(v==0 for v in vals);m['other_body_pixels']+=sum(v not in (0,body) for v in vals);associations.append(dict(id=b['id'],body=body,correct_color=correct))
    return totals,associations

def add_metrics(total,new):
    for c,d in new.items():
        for k,v in d.items():total[c][k]+=v

def finish(total):
    for d in total.values():d['recall']=d['detected']/d['visible'] if d['visible'] else None;d['false_discovery_fraction']=d['false_positive']/d['accepted'] if d['accepted'] else None
    return total

def synthetic():
    total={c:Counter() for c in ('black','red','yellow')};rows=[];records=[];images={};truths={};examples=[];t=time.monotonic()
    for name,rgb,truth,colors,condition in scenes():
        check_budget();beads,candidates,_,summary,_=detect(rgb);m,assoc=metric(beads,truth,colors);add_metrics(total,m);rows.append(dict(scene=name,colors=colors,condition=condition,metrics=m,associations=assoc,summary=summary));records.extend(dict(scene=name,**r) for r in candidates);images[name]=rgb;truths[name]=truth
        if condition in ('clear','multiple-highlights','touching','no-black-reflection'):examples.append((name,rgb,beads))
    np.savez_compressed(OUT/'synthetic-inputs.npz',**images);np.savez_compressed(OUT/'synthetic-truth.npz',**truths);lines('synthetic-candidates.jsonl.gz',records);save('synthetic-evaluation.json',dict(scenes=len(rows),metrics=finish(total),results=rows,elapsed_seconds=time.monotonic()-t,note='Known visible body denominator includes black with no visible reflection. No truth supplied to detector.'))
    for label,selected in [('synthetic-examples',examples[:8]),('synthetic-mixed-examples',examples[-8:])]:
        sheet=Image.new('RGB',(840,240*len(selected)),'white');d=ImageDraw.Draw(sheet)
        for j,(name,rgb,beads) in enumerate(selected):
            im=Image.fromarray(rgb).resize((420,220),Image.Resampling.NEAREST);sheet.paste(im,(0,240*j+20));sheet.paste(im,(420,240*j+20));d.text((5,240*j+3),name,fill='black')
            for b in beads:
                pts=[(420+3*x+1.5,240*j+20+2*y+1) for x,y in b['outline']['smooth']];d.line(pts,fill='cyan',width=1)
        sheet.save(OUT/(label+'.png'))
    print('synthetic',json.dumps(finish(total)),flush=True)

def photo():
    raw=(OUT/'photo-samples.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==(OUT/'photo-samples.sha256').read_text().strip();samples=json.loads(raw);data=json.loads((OUT/'inventory.json').read_text());total={c:Counter() for c in ('black','red','yellow')};results=[]
    for s in samples['samples']:
        x0,y0,x1,y1=s['box'];bodies=s['bodies'];owners=Counter();assoc=[];counts={c:dict(visible=sum(b['color']==c for b in bodies),detected=0,accepted=0,false_positive=0,duplicate_extras=0,wrong_color=0,unmatched=0) for c in total}
        for b in data['beads']:
            x,y=b['brightest']['x']-x0,b['brightest']['y']-y0
            matches=[z for z in bodies if sum(((v-c)/r)**2 for v,c,r in zip((x,y),z['center'],z['matching_ellipse_radii']))<=1]
            in_core=20<=x<80 and 20<=y<80
            if not matches and not in_core:continue
            c=b['color'];m=counts[c];m['accepted']+=1
            match=min(matches,key=lambda z:sum(((v-c)/r)**2 for v,c,r in zip((x,y),z['center'],z['matching_ellipse_radii']))) if matches else None
            if match and match['color']==c:
                if owners[match['id']]:m['duplicate_extras']+=1;m['false_positive']+=1
                else:m['detected']+=1
                owners[match['id']]+=1
            else:m['false_positive']+=1;m['wrong_color']+=int(match is not None);m['unmatched']+=int(match is None)
            assoc.append(dict(id=b['id'],color=c,local_peak=[x,y],body=match['id'] if match else None,possible_bodies=[z['id'] for z in matches]))
        add_metrics(total,counts);results.append(dict(sample=s['id'],metrics=counts,associations=assoc,missed=[b['id'] for b in bodies if not owners[b['id']]]))
    save('photo-evaluation.json',dict(metrics=finish(total),results=results,possible_additional_bodies=samples['possible_additional_bodies'],limitations=['Small deliberate geographic sample, no random sampling error guarantee or whole-image extrapolation.','Single assistant annotations frozen before detection; no independent human adjudication.','Ellipses associate peaks with visible bodies; not segmentation ground truth.','Unmatched predictions require visual review; not automatically established false beads.']))
    print('photo',json.dumps(finish(total)),flush=True)

def ablations():
    # Same downstream search/region/ownership pipeline; individually restore or
    # relax cheap R271 gates without rerunning or pretending R271 stability equal.
    rows=[]
    with gzip.open(OUT/'candidates.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line)
            if r['pathway']=='colored' and r['accepted']:rows.append(r)
    # 9x9 background is recomputed from photograph, not inferred from core3.
    from .climb_r268 import background
    from PIL import ImageOps
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));_,paper,_=background(native)
    def failures(r):
        c=r['confidence'];x,y=r['anchor'];return [k for fail,k in [(c['mean7_y']<.25,'brightness'),(c['lit_fraction']<.85,'illumination'),(c['core_pixels']<25,'patch'),(c['window_ratio']<.65,'window'),(c['local_contrast']<.15,'contrast'),(np.any(paper[y-4:y+5,x-4:x+5]>0),'background')] if fail]
    gates=['brightness','illumination','patch','window','contrast','background'];checks=[dict(id=r['id'],color=r['color'],old_gate_failures=failures(r)) for r in rows];variants={}
    for variant,relaxed in [('old-cheap-gates',[]),*[(f'only-{g}',[g]) for g in gates],('all-targeted-relaxations',gates)]:
        keep=[r for r in checks if not(set(r['old_gate_failures'])-set(relaxed))];variants[variant]=dict(accepted=len(keep),colors=dict(Counter(r['color'] for r in keep)),ids=[r['id'] for r in keep])
    save('gate-ablations.json',dict(scope='Exact post-filter controls on common final downstream candidates; isolates cheap gates, not a claim to rerun original R271 18-way stability and rival checks.',variants=variants,sole_old_gate_failures=dict(Counter(r['old_gate_failures'][0] for r in checks if len(r['old_gate_failures'])==1)),rows=checks))

if __name__=='__main__':
    synthetic();photo();ablations()

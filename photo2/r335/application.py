"""Apply globally audited red/black evidence, without pattern-derived pigment.

R334's classifier is immutable. A compact luminance-reflection check prevents
its broad max-channel reflection mask from using a dark bead edge as body proof.
Only concordant darkness decisions are applied automatically. Maker decisions
are authoritative independently of either mask. No new bead/link/site is admitted.
"""
import argparse,copy,csv,time
from collections import Counter
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r334.common import read,save,ROOT
from photo2.r333.common import dataset

BASE='4e40da6a2b222ae1a755f0dc4d403e6d9ad7ec7f'
MAKER=['NEW-2237-1522','REC266-P032517','C-1284-0332','NEW-2257-2004',
       'NEW-2060-796','NEW-2186-2343','NEW-2167-1179','NEW-1920-531']
COLORS=['red','yellow','black']

def compact_test(photo,xy,radius,tree,names,obs,oid,lighting):
    """Same spatial geometry, luminance-only reflection extent, no hue/pattern."""
    cx,cy=xy;x,y=np.rint(xy).astype(int);x0=max(0,x-radius);y0=max(0,y-radius)
    p=photo[y0:y+radius+1,x0:x+radius+1];gray=p@np.array([.299,.587,.114])
    yy,xx=np.indices(gray.shape);xx+=x0;yy+=y0;d2=(xx-cx)**2+(yy-cy)**2
    domain=d2<=radius**2
    for j in tree.query_ball_point(xy,2*radius+6):
        q=obs[names[j]]['xy']
        if names[j]==oid or np.linalg.norm(np.array(q)-xy)<8:continue
        domain&=d2<.86*((xx-q[0])**2+(yy-q[1])**2)
    central=domain&(d2<=100);peak=float(gray[central].max());base=float(np.quantile(gray[domain],.2))
    threshold=base+.7*(peak-base);labels,_=ndi.label(domain&(gray>=threshold))
    py,px=np.unravel_index(np.where(central,gray,-1).argmax(),gray.shape)
    reflection=labels==labels[py,px] if labels[py,px] else np.zeros_like(domain)
    reflection=ndi.binary_dilation(reflection,iterations=1)&domain
    bright=ndi.binary_dilation(domain&(gray>=threshold),iterations=1)&domain
    ring=ndi.binary_dilation(reflection,iterations=4)&~ndi.binary_dilation(reflection,iterations=1)&domain&~bright
    sy,sx=np.where(reflection);ry,rx=np.where(ring);value=p[ring].max(1);v=gray[ring]
    sectors=len(set(((np.arctan2(ry-sy.mean(),rx-sx.mean())+np.pi)/(2*np.pi)*8).astype(int).clip(0,7))) if len(v) else 0
    valid=len(v)>=25 and sectors>=4 and peak-base>=.08
    median=float(np.median(v)) if len(v) else 1.;q75=float(np.quantile(v,.75)) if len(v) else 1.
    maximum=float(np.median(value)) if len(v) else 1.;upper=float(np.quantile(value,.75)) if len(v) else 1.
    dark=float(np.mean(value<=.35)) if len(v) else 0.;ratio=median/max(lighting,.1)
    positive=bool(valid and median<=.15 and q75<=.20 and maximum<=.30 and upper<=.40 and dark>=.70 and ratio<=.65)
    negative=bool(valid and (maximum>=.45 or dark<=.30))
    return dict(radius=radius,ring_pixels=np.c_[rx+x0,ry+y0].tolist(),reflection_pixels=np.c_[sx+x0,sy+y0].tolist(),
                domain_pixels=np.c_[xx[domain],yy[domain]].tolist(),count=len(v),sectors=sectors,valid=bool(valid),
                median_intensity=median,q75_intensity=q75,median_max_channel=maximum,q75_max_channel=upper,
                dark_fraction=dark,lighting_ratio=ratio,peak=peak,base=base,threshold=threshold,
                positive=positive,negative=negative,hue_used=False)

def run(out):
    t=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    r334=ROOT/'photo2/r334';g=read(r334/'overlay/graph.json.gz');before=copy.deepcopy(g)
    obs={r['id']:r for r in g['observations']};names=sorted(obs);tree=cKDTree([obs[o]['xy'] for o in names])
    audit=read(r334/'classification/audit.json.gz');photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))/255.
    rows=[];changes=[]
    for r in audit['records']:
        tests=[compact_test(photo,r['xy'],radius,tree,names,obs,r['id'],r['lighting']['intensity']) for radius in [9,12,15]]
        positives=sum(x['positive'] for x in tests);negatives=sum(x['negative'] for x in tests)
        decision='black' if positives>=2 and negatives==0 else 'not-black' if negatives>=2 and positives==0 else 'unknown'
        confirmed=r['id'] in MAKER
        automatic=r['overlay_color']=='red' and r['body_prediction']=='black' and decision=='black' and not confirmed
        color='black' if confirmed or automatic else r['overlay_color']
        row=dict(id=r['id'],xy=r['xy'],status=r['status'],before_color=r['overlay_color'],color=color,
                 R334_body_prediction=r['body_prediction'],compact_decision=decision,scales=tests,
                 maker_accepted=confirmed,automatic_applied=automatic,changed=color!=r['overlay_color'],
                 admission='unchanged inventory status; pigment layer only',
                 evidence='maker acceptance of eight listed candidates' if confirmed else 'two independent reflection-extent masks support very dark body' if automatic else 'no automatic change',
                 policy='No hue or pattern color enters the black test. No abstention is converted into a color correction.')
        rows.append(row)
        if row['changed']:
            changes.append({k:row[k] for k in ['id','xy','status','before_color','color','maker_accepted','automatic_applied','evidence']})
            if r['id'] in obs:
                obs[r['id']].update(color=color,r335_color_provenance=row['evidence'],r334_color=r['overlay_color'])
    g.update(schema='r335-global-audited-pigment-overlay-v1',baseline_commit=BASE,
             previous_overlay='photo2/r334/overlay/graph.json.gz',policy='R334 maker fixes retained. Eight additional maker-accepted colors plus concordant native-intensity changes. Candidate pigment updates do not admit observations, associations or links.')
    co={r['id']:r['ab'] for r in g['coordinates']};g['indexed_colors']=dict(Counter(obs[o]['color'] for o in co))
    save(out/'graph.json.gz',g);save(out/'application.json.gz',dict(records=rows,changes=changes,policy=g['policy']))
    with (out/'changes.csv').open('w',newline='') as f:
        fields=['id','xy','status','before_color','color','maker_accepted','automatic_applied','evidence'];w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(changes)
    # One fixed diagnostic replay of the existing (16,16) relation, not a search.
    raw,rawobs,_,ids,ab,c,weights,blocks,_=dataset();ix={o:i for i,o in enumerate(ids)};occ={tuple(v):o for o,v in co.items()};pred=[]
    for o in ids:
        cell=np.array(co[o]);block=int(blocks[ix[o]]);examples=[]
        for mul in range(-15,16):
            z=occ.get(tuple(cell+mul*np.array([16,16])))
            if mul and z and blocks[ix[z]] not in [(block-1)%12,block,(block+1)%12]:
                examples.append(dict(id=z,color=obs[z]['color'],section=int(blocks[ix[z]]),translation=[mul*16,mul*16]))
        counts=Counter(e['color'] for e in examples);winner,n=counts.most_common(1)[0] if counts else ('?',0)
        sections={e['section'] for e in examples if e['color']==winner};strong=n>=3 and len(sections)>=3 and n/max(len(examples),1)>=.8
        pred.append(dict(id=o,color=obs[o]['color'],prediction=winner if strong else '?',strong=strong,support=n,total=len(examples),examples=examples,
                         disagreement=bool(strong and obs[o]['color']!=winner),red_black_only=bool({obs[o]['color'],winner}=={'red','black'})))
    # Refresh only the existing 208 consensus using its original weights/folds.
    entries=[];k=ab@np.array([7,6]);current=np.array([COLORS.index(obs[o]['color']) for o in ids])
    for residue in range(208):
        jj=np.flatnonzero(k%208==residue);counts=np.bincount(current[jj],weights=weights[jj],minlength=3);win=int(counts.argmax());fraction=float(counts[win]/counts.sum()) if len(jj) else 0
        supporting=[j for j in jj if current[j]==win];sections=sorted(set(int(blocks[j]) for j in supporting));known=fraction>=.8 and len(supporting)>=3 and len(sections)>=3
        entries.append(dict(residue=residue,color=COLORS[win] if known else '?',plurality=COLORS[win] if len(jj) else '?',fraction=fraction,observations=len(jj),supporting=len(supporting),sections=sections,ids=[ids[j] for j in jj]))
    newbreaks=[r for r in pred if r['disagreement']];r334layer=next(x for x in read(r334/'analysis/analysis.json.gz')['layers'] if x['layer']=='relocated')
    remaining=dict(predictions=pred,breaks=newbreaks,motif208=entries,known208=sum(x['color']!='?' for x in entries),
                   unknown208=sum(x['color']=='?' for x in entries),baseline_R334_breaks=r334layer['breaks'],
                   fixed_rule='Existing guarded (16,16) copies; >=3 supporting observations/sections and >=80% agreement. No new search or rule learning.',
                   interpretation='Disagreement is a model/reconstruction diagnostic, not proof of color error. Red/black-only flags are not maker questions by default.')
    save(out/'remaining.json.gz',remaining)
    summary=dict(scanned=len(rows),recorded=sum(r['status']=='recorded' for r in rows),
                 maker_accepted=8,automatic_recorded=sum(r['automatic_applied'] and r['status']=='recorded' for r in rows),
                 automatic_candidate_labels=sum(r['automatic_applied'] and r['status']!='recorded' for r in rows),
                 changes_by_status=dict(Counter(r['status'] for r in changes)),indexed_colors=g['indexed_colors'],
                 unchanged_locations=True,unchanged_coordinates=True,unchanged_links=True,
                 R334_significant_breaks=14,current_fixed_rule_breaks=len(newbreaks),
                 red_black_only_breaks=sum(x['red_black_only'] for x in newbreaks),known208=remaining['known208'],unknown208=remaining['unknown208'],
                 seconds=time.perf_counter()-t,scope='Global pigment application and one fixed diagnostic refresh; no period/spiral/classifier training or reconstruction search.')
    save(out/'summary.json',summary);print(summary)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)

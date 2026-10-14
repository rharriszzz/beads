"""R278 physical construction, native positive-pixel fitting and full ledger.

Run phase1_r278 first; its frozen hash is an input, never modified by this module.
"""
from __future__ import annotations
import argparse,copy,csv,gzip,json,time
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
from .construction_r278 import Scene,base_model,contact_audit,surface_samples,sdf,RADIUS
from .reconstruct_r276 import DEFAULT,pixels,physical,light,bright_prediction,stats,basis
from .bead_debugger.surface import shade
from .bead_debugger.generate import ROOT,save,sha
from .bead_detection.brightness_r270 import color_managed_photo,linearize

OUT=ROOT/'photo2/review/r278'


def observations():
    with gzip.open(OUT/'phase1-inventory.json.gz','rt') as f:inv=json.load(f)
    regions={b['id']:b for b in inv['beads']}
    prior={r['id']:r for r in json.loads((ROOT/'photo2/review/r276/observations.json').read_text())['observations']}
    rows=[]
    for loc in inv['locations']:
        if loc['id'] in prior:r=copy.deepcopy(prior[loc['id']])
        else:
            xy=[loc['point']['x'],loc['point']['y']];a=(np.arctan2(xy[1]-1590.5,xy[0]-1269.5)%(2*np.pi))/(2*np.pi)*16
            split='holdout' if int(a) in (1,5,9,13) else 'train'
            if split=='train' and min(abs(a-k) for k in (1,2,5,6,9,10,13,14))<.12:split='buffer'
            b=regions[loc['id']]
            r=dict(id=loc['id'],color=loc['color'],xy=xy,region_runs=b['region']['runs'],area=b['region']['pixel_count'],
                   bright_shape={'centroid':loc['bright_patch']['centroid']},specular_candidate=False,split=split,
                   interior_centroid=b['region']['centroid'],strong=True,sector=int(a),source='R278 image only')
        rows.append(r)
    return rows


def assign(hist, n, fraction_threshold=.15):
    """One-to-one positive support, with explicit unmatched dummy columns."""
    cost=np.full((len(hist),n+len(hist)),1-fraction_threshold)
    cost[:,:n]=2.
    for i,h in enumerate(hist):
        for k,v in h.items():cost[i,k]=1-v
    a,b=linear_sum_assignment(cost)
    result=np.full(len(hist),-1,int);result[a]=np.where(b<n,b,-1)
    support=np.array([h.get(int(k),0.) if k>=0 else 0. for h,k in zip(hist,result)])
    return result,support


class Evidence:
    def __init__(self, rows, samples=16):
        self.rows=[r for r in rows if r['region_runs']]
        groups=[pixels(r['region_runs']) for r in self.rows]
        if samples:groups=[p[np.linspace(0,len(p)-1,min(samples,len(p))).astype(int)] for p in groups]
        self.groups=groups;self.xy=np.concatenate(groups);self.lengths=np.array([len(p) for p in groups]);self.ends=np.r_[0,np.cumsum(self.lengths)]

    def evaluate(self,s):
        d=s.camera(self.xy);hist=[]
        for a,b in zip(self.ends[:-1],self.ends[1:]):
            k,c=np.unique(d['owner'][a:b],return_counts=True)
            hist.append({int(i):float(v/(b-a)) for i,v in zip(k,c) if i>=0})
        owners,support=assign(hist,len(s.centers))
        return float(np.mean(1-support)),dict(owners=owners,support=support,hist=hist,data=d)


def score(base,p,ev):
    s=Scene(base,p);loss,_=ev.evaluate(s)
    penalty=.002*np.sum((p[:4]/6)**2)+.003*np.sum((p[4:8]/.006)**2)+.003*np.sum((p[8:12]/.08)**2)
    return loss+penalty


def fit(base,rows,budget=145):
    ev=Evidence([r for r in rows if r['split']=='train'],12)
    # Full phase search, with the same starts for every count and handedness.
    trials=[];best=np.inf;p=DEFAULT.copy();trace=[];calls=0
    for phase in np.linspace(0,2*np.pi,24,endpoint=False):
        q=DEFAULT.copy();q[13]=phase;v=score(base,q,ev);calls+=1
        trials.append(dict(phase_rad=float(phase),loss=v))
        if v<best:best=v;p=q
    # Geometry only: brightness never chooses an identity or trains geometry.
    active=[13,12,14,15,0,1,2,3,4,5,8,9,16,17]
    steps={13:.13,12:.2,14:2.,15:2.,0:2.,1:2.,2:2.,3:2.,4:.001,5:.001,8:.025,9:.025,16:1.,17:.2}
    limits={12:1.,14:10.,15:10.,0:8.,1:8.,2:8.,3:8.,4:.006,5:.006,8:.08,9:.08,16:4.,17:1.}
    # A cheap coarse contact gate rejects known overlaps; denser final audit is mandatory.
    rejected=0
    while calls+2*len(active)<=budget:
        improved=False
        for k in active:
            options=[]
            for sign in (-1,1):
                q=p.copy();q[k]+=sign*steps[k]
                if k in limits:q[k]=np.clip(q[k],-limits[k],limits[k])
                v=score(base,q,ev);calls+=1;options.append((v,q))
            v,q=min(options,key=lambda a:a[0])
            if v<best:
                audit=contact_audit(Scene(base,q),8,8)
                if audit['penetrating_pairs']:rejected+=1
                else:best,p=v,q;improved=True
        trace.append(dict(evaluations=calls,loss=best,p=p.tolist()))
        if not improved:steps={k:v*.5 for k,v in steps.items()}
    return p,dict(evaluations=calls,budget=budget,phase_trials=trials,trace=trace,loss=best,contact_rejected_improvements=rejected,
                  objective='mean unowned positive-pixel fraction after one-to-one assignment plus low-mode priors; train only',samples_per_observation=12)


def comparison(base,p,rows):
    s=Scene(base,p);metrics={}
    for split in ('train','holdout','buffer'):
        ev=Evidence([r for r in rows if r['split']==split],48);loss,d=ev.evaluate(s)
        metrics[split]=dict(observations=len(ev.rows),mean_support=float(d['support'].mean()),unmatched=int(np.sum(d['owners']<0)),
                           supported_80=int(np.sum(d['support']>=.8)),unfinished_rays=int(np.sum(d['data']['unknown']>0)))
        metrics[split]['colors']={c:dict(count=sum(r['color']==c for r in ev.rows),mean_support=float(np.mean([v for r,v in zip(ev.rows,d['support']) if r['color']==c]))) for c in ('red','yellow','black')}
        metrics[split]['sectors']={str(k):float(np.mean([v for r,v in zip(ev.rows,d['support']) if r['sector']==k])) for k in sorted({r['sector'] for r in ev.rows})}
    a=contact_audit(s,32,32)
    ph=physical(s.model);ph['hole_axis']='local centerline tangent' if not base.get('hole_tilt_deg') else 'shared signed circumferential tilt from local tangent'
    ph['hole_tilt_deg']=base.get('hole_tilt_deg',0)
    return dict(metrics=metrics,contact={k:v for k,v in a.items() if k not in ('pairs','minimum_sdf_by_pair')},physical=ph)


def run_fit():
    rows=observations();results=[]
    # Pairwise identical construction and optimization budgets for both hands.
    hypotheses=[(1950,1.45),(2300,1.40),(2600,1.35),(2696,1.35)]
    for n,pitch in hypotheses:
        for h in (-1,1):
            b=base_model(n,h,'intended',pitch);name=b['id'];path=OUT/(name+'.json')
            if path.exists():
                doc=json.loads(path.read_text())
                if doc['phase1_sha256']!=sha(OUT/'phase1-inventory.json.gz'):
                    raise ValueError('Frozen Phase 1 changed; archive obsolete fit before rerunning: '+name)
            else:
                p,fitlog=fit(b,rows);doc=dict(id=name,base=b,p=p.tolist(),fit=fitlog,phase1_sha256=sha(OUT/'phase1-inventory.json.gz'))
                doc.update(comparison(b,p,rows));save(path,doc)
            results.append(doc);print(name,doc['metrics'],'contact',doc['contact']['penetrating_pairs'],flush=True)
    save(OUT/'comparison.json',[{k:v for k,v in d.items() if k not in ('base','p')} for d in results])


def run_extended():
    rows=observations();configs=[]
    for h in (-1,1):
        configs.append(base_model(2080,h,pitch_factor=1.4))
        configs.append(base_model(1950,h,pitch_factor=1.45,focal=9598.))
        b=base_model(2696,h,pitch_factor=1.3);b['hole_tilt_deg']=-8.;b['id']+='_tilt-8';configs.append(b)
    for b in configs:
        path=OUT/(b['id']+'.json')
        if path.exists():
            if json.loads(path.read_text())['phase1_sha256']!=sha(OUT/'phase1-inventory.json.gz'):
                raise ValueError('Frozen Phase 1 changed; archive obsolete fit before rerunning: '+b['id'])
            continue
        p,fitlog=fit(b,rows);doc=dict(id=b['id'],base=b,p=p.tolist(),fit=fitlog,phase1_sha256=sha(OUT/'phase1-inventory.json.gz'),stage='exploratory extension; equal budgets within each hand pair')
        doc.update(comparison(b,p,rows));save(path,doc);print(doc['id'],doc['metrics'],'contact',doc['contact']['penetrating_pairs'],flush=True)
    docs=[json.loads(p.read_text()) for p in sorted(OUT.glob('intended_N*.json')) if '-accounting' not in p.name and '-contact' not in p.name and '-discrepancies' not in p.name]
    save(OUT/'comparison.json',[{k:v for k,v in d.items() if k not in ('base','p')} for d in docs if 'base' in d])


def grid(s,step=2):
    mask=np.zeros((int(np.ceil(3182/step)),int(np.ceil(2540/step))),bool)
    # Bounding projected sphere, enlarged conservatively for perspective.
    bound=s.bound*s.model.view.scale*1.5+3
    for x,y in s.pc:
        a=np.floor((np.array([x,y])-bound)/step).astype(int);b=np.ceil((np.array([x,y])+bound)/step).astype(int)+1
        mask[max(0,a[1]):min(mask.shape[0],b[1]),max(0,a[0]):min(mask.shape[1],b[0])]=True
    y,x=np.where(mask);return np.c_[x,y]*step


def color_model(rows,rgb):
    """Learn color distributions from measured interiors; no repeating pattern."""
    from matplotlib.colors import rgb_to_hsv
    hsv=rgb_to_hsv(rgb/255.)
    # Chromatic hue prototypes from training interiors only. Black is accepted
    # only with reflection/body evidence below; darkness alone is insufficient.
    proto={}
    for c in ('red','yellow'):
        pts=np.concatenate([pixels(r['region_runs'])[::5] for r in rows if r['color']==c and r['split']=='train' and r['region_runs']])
        hs=hsv[pts[:,1],pts[:,0]];h=hs[(hs[:,1]>.35)&(hs[:,2]>.1),0]*2*np.pi
        proto[c]=float(np.arctan2(np.sin(h).mean(),np.cos(h).mean())%(2*np.pi)/(2*np.pi))
    return hsv,proto


def classify_pixels(xy,hsv,proto):
    if len(xy)<12:return 'unknown',dict(reason='too few inset visible samples')
    x,y=np.asarray(xy,int).T;hs=hsv[y,x];good=(hs[:,1]>.35)&(hs[:,2]>.12)
    votes={c:float(np.mean(good&(abs((hs[:,0]-h+.5)%1-.5)<10/360))) for c,h in proto.items()}
    ranked=sorted(votes,key=votes.get,reverse=True)
    if votes[ranked[0]]>=.65 and votes[ranked[0]]-votes[ranked[1]]>=.45:return ranked[0],dict(votes=votes,reason='image-learned hue on inset visible surface')
    dark=(hs[:,2]<.25)&(hs[:,1]<.4);glints=(hs[:,2]>.6)&(hs[:,1]<.35)
    if dark.mean()>=.55 and glints.sum()>=2 and good.mean()<.25:
        return 'black',dict(votes=votes,dark_fraction=float(dark.mean()),neutral_glints=int(glints.sum()),reason='neutral reflection plus surrounding dark inset visible body; conditional geometry-assisted evidence')
    return 'unknown',dict(votes=votes,reason='mixed, dark or insufficiently chromatic pixels; darkness alone cannot confirm black')


def export(name):
    doc=json.loads((OUT/(name+'.json')).read_text())
    if doc['phase1_sha256']!=sha(OUT/'phase1-inventory.json.gz'):raise ValueError('Model belongs to a different frozen inventory')
    s=Scene(doc['base'],np.array(doc['p']));rows=observations();rgb,_=color_managed_photo()
    ev=Evidence(rows,0);_,assigned=ev.evaluate(s);xy=grid(s);d=s.camera(xy);step=2
    # An inset prevents colors bleeding across predicted silhouette/occlusion boundaries.
    owner_image=np.full((1591,1270),-1,int);owner_image[(xy[:,1]//2).astype(int),(xy[:,0]//2).astype(int)]=d['owner']
    from scipy import ndimage as ndi
    maxo=ndi.maximum_filter(owner_image,3,mode='constant',cval=-2);mino=ndi.minimum_filter(owner_image,3,mode='constant',cval=-2)
    inset=(maxo==mino)&(owner_image>=0)
    hsv,proto=color_model(rows,rgb);observed={};obsrows=[]
    with gzip.open(OUT/'phase1-features.json.gz','rt') as f:features=json.load(f)
    features=[f for f in features if f['method'].startswith('LoG') and f['stable'] and f['feature_value']>=.03 and f['nearest_existing_distance']>=8]
    feature_tree=cKDTree([f['anchor'] for f in features])
    for row,k,f,h in zip(ev.rows,assigned['owners'],assigned['support'],assigned['hist']):
        alternatives=sorted(h.items(),key=lambda a:-a[1]);runner=max((v for kk,v in h.items() if kk!=k),default=0.)
        status='confident conditional match' if f>=.8 and f-runner>=.5 else ('ambiguous correspondence' if k>=0 else 'independent observation unexplained')
        rec=dict(id=row['id'],color=row['color'],split=row['split'],observed_peak=row['xy'],interior_centroid=row['interior_centroid'],owner=int(k),support_fraction=float(f),status=status,alternatives=[dict(index=kk,fraction=v) for kk,v in alternatives],physical_center_is_observed=False)
        obsrows.append(rec)
        if k>=0:observed[int(k)]=rec
    for r in rows:
        if not r['region_runs']:obsrows.append(dict(id=r['id'],color=r['color'],observed_peak=r['xy'],owner=-1,status='independent location without measured interior',alternatives=[]))
    beads=[];supports={};assisted=[]
    for k in range(len(s.centers)):
        ix=np.flatnonzero(d['owner']==k);pts=xy[ix];inside=pts[inset[pts[:,1]//2,pts[:,0]//2]] if len(pts) else pts
        col,evidence=classify_pixels(inside,hsv,proto);r=observed.get(k)
        nearby=sorted(set(j for p in inside for j in feature_tree.query_ball_point(p,2.))) if len(inside) else []
        evidence['independent_feature_ids']=[features[j]['id'] for j in nearby]
        conflict=bool(r and col!='unknown' and col!=r['color'])
        votes=evidence.get('votes',{})
        if r and sum(v>.25 for v in votes.values())>1:conflict=True
        evidence['observation_color_conflict']=conflict
        if r and r['status']=='confident conditional match' and not conflict:status=r['status'];col=r['color']
        elif r and conflict:
            status='ambiguous correspondence';r['status']=status;r['surface_color_conflict']=True;col='unknown'
        elif r:status='ambiguous correspondence'
        elif len(pts)>=30 and col!='unknown' and nearby:status='geometry-assisted image-supported candidate';assisted.append(k)
        elif len(pts):status='predicted but unconfirmed'
        else:status='no sampled visible surface'
        supports[str(k)]=pts.tolist()
        beads.append(dict(candidate_index=k,physical_identity_status='conditional on this unvalidated model',world_center=s.centers[k].tolist(),predicted_center=s.pc[k].tolist(),visible_centroid=pts.mean(0).tolist() if len(pts) else None,
                          visible_area_px2=len(pts)*4,inset_samples=len(inside),phase1_id=r['id'] if r else None,status=status,color=col,color_evidence=evidence,
                          neighbors={str(delta):int((k+delta)%len(s.centers)) for delta in (-7,-6,-1,1,6,7)}))
    prefix=OUT/name
    for suffix,obj in [('correspondence.json.gz',dict(model=name,beads=beads,observations=obsrows,visibility_grid_px=2,unknown_rays=xy[d['unknown']>0].tolist(),colors_from='photograph; no pattern',limitations=['Conditional indices, not recovered physical string order','No grid samples does not prove complete occlusion','Shared warm start; holdouts exploratory'])),('visible-support.json.gz',supports)]:
        with gzip.GzipFile(filename=str(prefix)+'-'+suffix,mode='wb',mtime=0) as f:f.write(json.dumps(obj,separators=(',',':')).encode())
    with (OUT/(name+'-beads.csv')).open('w') as f:
        fields=['candidate_index','status','color','phase1_id','visible_area_px2','inset_samples','predicted_center','visible_centroid'];w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(beads)
    audit=contact_audit(s,128,64);save(OUT/(name+'-contact.json'),audit)
    summary=dict(model=name,beads=len(beads),categories=dict(Counter(b['status'] for b in beads)),observations=dict(Counter(r['status'] for r in obsrows)),
                 colors=dict(Counter(b['color'] for b in beads if b['visible_area_px2'])),native_mean_support=float(assigned['support'].mean()),native_pixel_weighted_support=float(np.average(assigned['support'],weights=ev.lengths)),
                 grazing_rays=int(np.sum(d['unknown']>0)),contact={k:v for k,v in audit.items() if k not in ('pairs','minimum_sdf_by_pair')},phase1_sha256=sha(OUT/'phase1-inventory.json.gz'))
    save(OUT/(name+'-accounting.json'),summary)
    draw_results(name,rgb,beads,obsrows,supports)
    print(json.dumps(summary,indent=2),flush=True)


def draw_results(name,rgb,beads,observations,supports):
    im=Image.fromarray(rgb);overlay=im.copy();d=ImageDraw.Draw(overlay)
    for b in beads:
        if not b['visible_area_px2']:continue
        x,y=b['predicted_center'];d.line((x-3,y,x+3,y),fill='magenta',width=1);d.line((x,y-3,x,y+3),fill='magenta',width=1)
    for r in observations:
        x,y=r['observed_peak'];d.ellipse((x-2,y-2,x+2,y+2),outline='cyan',width=1)
    d.rectangle((20,20,830,72),fill='white');d.text((30,30),'CYAN circles: image-only locations. MAGENTA crosses: conditional physical centers.',fill='black')
    d.text((30,48),'Centers are not highlights. No string identity or complete reconstruction is certified.',fill='black')
    overlay.resize((1270,1591)).save(OUT/(name+'-overlay.jpg'),quality=95)
    cases=sorted([r for r in observations if 'support_fraction' in r],key=lambda r:r['support_fraction'])[:12]
    # Add distributed black matches and geometry-assisted color candidates.
    cases += [r for r in observations if r['color']=='black' and r['status']=='confident conditional match'][::max(1,sum(r['color']=='black' and r['status']=='confident conditional match' for r in observations)//6)][:6]
    cases += [dict(id='predicted-'+str(b['candidate_index']),observed_peak=b['visible_centroid'],owner=b['candidate_index'],status=b['status']) for b in beads if b['status']=='geometry-assisted image-supported candidate'][::max(1,sum(b['status']=='geometry-assisted image-supported candidate' for b in beads)//6)][:6]
    for i,r in enumerate(cases):
        x,y=map(int,r['observed_peak']);box=(x-42,y-42,x+42,y+42);raw=im.crop(box).resize((336,336));marked=overlay.crop(box).resize((336,336));dd=ImageDraw.Draw(marked)
        if r['owner']>=0:
            for px,py in supports[str(r['owner'])]:
                if box[0]<=px<box[2] and box[1]<=py<box[3]:dd.point(((px-box[0])*4,(py-box[1])*4),fill='white')
        sheet=Image.new('RGB',(680,365),'white');sheet.paste(raw,(0,29));sheet.paste(marked,(344,29));ImageDraw.Draw(sheet).text((3,3),r['id']+' '+r['status'],fill='black');sheet.save(OUT/(name+f'-crop-{i+1:02d}.png'))
        r['image']=name+f'-crop-{i+1:02d}.png'
    save(OUT/(name+'-discrepancies.json'),cases)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['fit','extended','export']);parser.add_argument('--name');args=parser.parse_args()
    if args.stage=='fit':run_fit()
    elif args.stage=='extended':run_extended()
    else:export(args.name)


if __name__=='__main__':main()

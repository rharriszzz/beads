"""Reliable photographic anchors -> competing physical fits -> every-bead ledger."""
from collections import Counter
from copy import deepcopy
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from .common import ROOT,OUT,read,save,sha,photo,pixels,support,record,validate,circular_distance
from .phase1 import image_features
from .geometry import Scene,cold_parameters,smooth_curve,unit,R

COUNTS=(1950,2080,2300,2600,2696)


def assignment(hist,n,minimum=.3):
    cost=np.full((len(hist),n+len(hist)),1-minimum)
    cost[:,:n]=2.
    for i,h in enumerate(hist):
        for k,f in h.items():cost[i,k]=1-f
    a,b=linear_sum_assignment(cost);owners=np.full(len(hist),-1,int)
    owners[a]=np.where(b<n,b,-1)
    fractions=np.array([h.get(int(k),0.) if k>=0 else 0. for h,k in zip(hist,owners)])
    return owners,fractions


def evaluate(scene,rows,samples=12):
    groups=[]
    for row in rows:
        xy=pixels(row['measured_support'])
        if samples and len(xy)>samples:xy=xy[np.linspace(0,len(xy)-1,samples).astype(int)]
        groups.append(xy)
    if not groups:return dict(mean_support=0.,owners=[],fractions=[],hist=[],unknown=0)
    xy=np.concatenate(groups);data=scene.trace(xy);hist=[];start=0
    for group in groups:
        owner=data['owner'][start:start+len(group)];ids,counts=np.unique(owner,return_counts=True)
        hist.append({int(k):float(v/len(group)) for k,v in zip(ids,counts) if k>=0});start+=len(group)
    owners,fractions=assignment(hist,scene.n)
    return dict(mean_support=float(fractions.mean()),owners=owners.tolist(),fractions=fractions.tolist(),
                hist=hist,unknown=int(data['unknown'].sum()))


def proxy(scene,rows):
    points=np.array([r['measured_photo_location'] for r in rows]);visible=(scene.g['radial']@scene.eye)>-.15
    centers=scene.pc[visible];distance,index=cKDTree(centers).query(points)
    return float(np.mean(np.minimum(distance,30)**2))


def fit(curve,rows,n,hand):
    # Equal budgets, independent of color or held-out observations.
    coarse=[]
    for elevation in (60.,75.,90.):
        for pitch in (1.35,1.45):
            for phase in np.linspace(0,2*np.pi,16,endpoint=False):
                p=cold_parameters(n,hand,elevation,pitch);p['phase']=float(phase)
                score=proxy(Scene(curve,p),rows);coarse.append(dict(parameters=p,proxy_mse=score))
    shortlisted=sorted(coarse,key=lambda r:r['proxy_mse'])[:3]
    trials=[];best=None
    for initial in shortlisted:
        p=initial['parameters'];scene=Scene(curve,p);v=evaluate(scene,rows,8)['mean_support']
        trials.append(dict(parameters=deepcopy(p),support=v,kind='cold-start'))
        if best is None or v>best[0]:best=(v,deepcopy(p))
    value,p=best
    for scale in (1.,.5):
        for key,delta in [('phase',.16),('origin',.25),('dx',2.),('dy',2.),('bend0',2.),('bend1',2.)]:
            options=[]
            for sign in (-1,1):
                q=deepcopy(p)
                if key.startswith('bend'):q['bend'][int(key[-1])]+=sign*delta*scale
                else:q[key]+=sign*delta*scale
                v=evaluate(Scene(curve,q),rows,8)['mean_support']
                trials.append(dict(parameters=q,support=v,kind='shared-pose'))
                penalty=.0005*np.sum(np.asarray(q['bend'])**2)+.0002*(q['dx']**2+q['dy']**2)
                options.append((v-penalty,v,q))
            score,v,q=max(options,key=lambda a:a[0])
            current_penalty=.0005*np.sum(np.asarray(p['bend'])**2)+.0002*(p['dx']**2+p['dy']**2)
            if score>value-current_penalty:value,p=v,q
    scene=Scene(curve,p);cert=scene.certify()
    return dict(parameters=p,coarse_trials=coarse,refinement_trials=trials,
                train_objective=value,certificate=cert,evaluations=len(trials),
                limitation='Bounded cold-start search; proxy initializes exact first-hit support matching. No global optimum or unique count claimed.')


def measure_color(rgb,features,xy):
    xy=np.asarray(xy,int).reshape(-1,2)
    if not len(xy):return 'unknown',0.,dict(reason='no-visible-pixels'),np.empty((0,2),int)
    hsv=features['hsv'][xy[:,1],xy[:,0]];lum=features['lum'][xy[:,1],xy[:,0]];paper=features['paper'][xy[:,1],xy[:,0]]
    colored=(hsv[:,1]>.35)&(lum>.025)&~paper
    votes={}
    masks={}
    for color,hue in features['palette'].items():
        other=features['palette']['yellow' if color=='red' else 'red']
        own=circular_distance(hsv[:,0]*360,hue);rival=circular_distance(hsv[:,0]*360,other)
        mask=colored&(own<30)&(rival-own>5);masks[color]=mask;votes[color]=int(mask.sum())
    neutral=((hsv[:,1]<.65)|(hsv[:,1]*hsv[:,2]<.12))&~paper
    dark=neutral&(lum<min(.12,max(.035,float(lum.max())*.35)))
    reflection=neutral&(lum>max(.055,float(lum.max())*.32))
    votes['black']=int(dark.sum()) if dark.mean()>=.45 else 0;masks['black']=dark|reflection
    color=max(votes,key=votes.get);fraction=votes[color]/len(xy)
    if fraction<(.45 if color=='black' else .55) or votes[color]<8:return 'unknown',0.,dict(votes=votes,mean_luminance=float(lum.mean()),reason='mixed-or-insufficient-visible-color'),np.empty((0,2),int)
    confidence=min(.95,fraction)
    if color=='black' and reflection.sum()<3:confidence=min(confidence,.25)
    if len(xy)<40:confidence=min(confidence,.45)
    return color,float(confidence),dict(votes=votes,mean_luminance=float(lum.mean()),reflection_pixels=int(reflection.sum()),
                 classification='actual inset predicted-visible pixels; unknown for conflicting materials'),xy[masks[color]]


def light_check(scene,rows,mapping,features):
    evidence=[]
    for row,k in zip(rows,mapping):
        if k<0:continue
        xy=pixels(row['measured_support']);lum=features['lum'][xy[:,1],xy[:,0]];hsv=features['hsv'][xy[:,1],xy[:,0]]
        keep=(lum>=np.quantile(lum,.9))&(lum>.16)&((hsv[:,1]<.45)|(hsv[:,1]<np.median(hsv[:,1])*.75))
        if keep.sum()<3:continue
        point=xy[keep].mean(0);d=scene.trace(point[None],normals=True)
        item=dict(record_id=row['record_id'],model_index=int(k),split=row['split'],point=point.tolist(),first_owner=int(d['owner'][0]),usable=bool(d['owner'][0]==k))
        if item['usable']:
            normal=d['normal'][0];direction=unit(2*np.dot(normal,scene.eye)*normal-scene.eye)
            item.update(inferred_light_direction=direction.tolist(),normal=normal.tolist())
        evidence.append(item)
    train=[r for r in evidence if r['usable'] and r['split']=='train']
    light=unit(np.median([r['inferred_light_direction'] for r in train],axis=0)) if train else scene.eye
    for row in evidence:
        if row['usable']:
            row['angular_disagreement_deg']=float(np.degrees(np.arccos(np.clip(np.dot(row['inferred_light_direction'],light),-1,1))))
            row['expected_side_consistent']=row['angular_disagreement_deg']<30
    summary={}
    for split in ('train','holdout'):
        rr=[r for r in evidence if r['split']==split];good=[r for r in rr if r['usable']]
        summary[split]=dict(candidates=len(rr),usable=len(good),wrong_first_owner=len(rr)-len(good),
                           consistent=sum(r['expected_side_consistent'] for r in good),
                           median_angle_deg=float(np.median([r['angular_disagreement_deg'] for r in good])) if good else None)
    return dict(direction=light.tolist(),records=evidence,summary=summary,
                limitation='Shared distant-light side check, train highlights only; not radiometric calibration or a measured light position. Wrong owners retained.')


def export(curve,model,rows,rgb,features):
    name=model['id'];scene=Scene(curve,model['parameters'])
    linked=evaluate(scene,rows,0);by_index={k:(r,f) for r,k,f in zip(rows,linked['owners'],linked['fractions']) if k>=0}
    # Native pixel centers, including every projected bounding square, resolve visibility.
    xy,data=scene.grid(rgb.shape[:2],step=1)
    counts=np.bincount(data['owner'][data['owner']>=0],minlength=scene.n)
    owner_image=np.full(rgb.shape[:2],-1,np.int32);owner_image[xy[:,1],xy[:,0]]=data['owner']
    interior=np.ones(len(xy),bool)
    for delta in ((0,1),(0,-1),(1,0),(-1,0)):
        q=xy+delta;valid=(q[:,0]>=0)&(q[:,1]>=0)&(q[:,0]<rgb.shape[1])&(q[:,1]<rgb.shape[0])
        neighbor=np.full(len(xy),-2,int);neighbor[valid]=owner_image[q[valid,1],q[valid,0]]
        interior &= neighbor==data['owner']
    ledger=[];physical_ok=model['certificate']['certified']
    for k in range(scene.n):
        ix=np.flatnonzero(data['owner']==k);visible=xy[ix];inset=xy[ix[interior[ix]]]
        sample=inset;sampling='inset predicted visible surface'
        if k in by_index and by_index[k][1]>=.6:
            parent_xy=pixels(by_index[k][0]['measured_support'])
            common=np.intersect1d(parent_xy[:,1]*rgb.shape[1]+parent_xy[:,0],inset[:,1]*rgb.shape[1]+inset[:,0])
            if len(common)>=12:
                sample=np.c_[common%rgb.shape[1],common//rgb.shape[1]]
                sampling='intersection with independent Phase1 support; actual RGB remeasured'
        color,confidence,color_info,measured=measure_color(rgb,features,sample)
        color_info.update(sampling=sampling,sampled_pixels=len(sample))
        row=record(f'{name}:bead-{k:04}','phase2')
        identity=.18 if physical_ok else .05;parent=None;fraction=0.
        if k in by_index:
            parent,fraction=by_index[k];identity=float(min(.65,fraction*.65)*parent['phase1_reliability'])
            if not physical_ok:identity*=.25
            row['phase_origin']=['phase1','phase2'];row['phase_history']=['phase1','phase2']
            row['phase1_reliability']=parent['phase1_reliability'];row['importance']='high'
            row['measured_support']=deepcopy(parent['measured_support']);row['measured_photo_location']=parent['measured_photo_location']
            row['source_record_ids']=[parent['record_id']]
            row['phase1_color']=parent['color'];row['phase1_color_reliability']=parent['color_reliability']
            if color!=parent['color'] and color!='unknown':identity*=.5;row['notes'].append('Phase1 and predicted-surface colors conflict.')
        elif len(measured)>=40 and confidence>=.75:
            # Geometry-assisted evidence is explicitly Phase2, never Phase1.
            lo=measured.min(0);hi=measured.max(0)+1;mask=np.zeros((hi[1]-lo[1],hi[0]-lo[0]),bool)
            mask[measured[:,1]-lo[1],measured[:,0]-lo[0]]=True;labels,_=ndi.label(mask);size=np.bincount(labels.ravel());size[0]=0
            yy,xx=np.where(labels==size.argmax());measured=np.c_[xx,yy]+lo
            row['measured_support']=support(measured);row['measured_photo_location']=measured.mean(0).tolist()
            row['notes'].append('Geometry-assisted coherent color pixels; independent body/identity not established.')
        else:row['notes'].append('No reliable independent photographic support assigned.')
        visibility=float(counts[k]/max(1,data['isolated_counts'][k]))
        if not len(visible):color='unknown';confidence=0.;identity=min(identity,.1)
        row.update(model_hypothesis=name,physical_model_index=k,physical_model_confidence=float(identity),
                   phase2_identity_reliability=float(identity),physical_identity_reliability=float(identity),
                   visibility=visibility,visibility_kind='native first-hit visible pixels / isolated projected pixels; subpixel slivers unresolved',
                   visible_pixels=int(counts[k]),isolated_projected_pixels=int(data['isolated_counts'][k]),
                   color=color,color_reliability=confidence,color_evidence=color_info,
                   predicted_physical_center_xyz=scene.centers[k].tolist(),predicted_physical_center_xy=scene.pc[k].tolist(),
                   predicted_visible_centroid=visible.mean(0).tolist() if len(visible) else None,
                   visible_support=dict(runs=support(visible)['runs'],pixel_count=len(visible)) if len(visible) else None,
                   phase1_support_fraction=float(fraction),evidence_links=['phase1.json.gz',f'{name}-fit.json'],
                   status='conditional matched' if parent else 'geometry-assisted candidate' if row['measured_support'] else 'predicted unconfirmed')
        row['notes'].append('Conditional generator index; competing counts/hands/origins prevent a confirmed physical identity.')
        validate(row);ledger.append(row)
    light=light_check(scene,rows,linked['owners'],features)
    save(OUT/(name+'-inventory.json.gz'),dict(records=ledger,phase1_sha256=sha(OUT/'phase1.json.gz'),model=model['parameters']))
    save(OUT/(name+'-light.json'),light)
    summary=dict(id=name,n=scene.n,hand=model['parameters']['hand'],physical_certified=physical_ok,
        statuses=dict(Counter(r['status'] for r in ledger)),colors=dict(Counter(r['color'] for r in ledger)),
        invisible_native=sum(r['visibility']==0 for r in ledger),visible_native=sum(r['visibility']>0 for r in ledger),
        linked_phase1=sum(bool(r.get('source_record_ids')) for r in ledger),unlinked_phase1=sum(k<0 for k in linked['owners']),
        mean_all_anchor_support=linked['mean_support'],unknown_camera_rays=int(data['unknown'].sum()),
        light_summary=light['summary'],visibility_grid_step=1)
    save(OUT/(name+'-summary.json'),summary);print('export',summary,flush=True)
    return summary


def main():
    source=read(OUT/'phase1.json.gz');all_rows=source['records'];rows=[]
    for original in all_rows:
        if original['status']!='high' or not original['measured_support']:continue
        r=deepcopy(original);sector=int(r['arc_fraction']*16)%16;r['split']='holdout' if sector%4==1 else 'train';rows.append(r)
    assert len(rows)>=12,'Too few high-reliability anchors; retain Phase1 failures rather than fabricate a fit'
    curve=smooth_curve(read(OUT/'centerline.json')['points'])
    train=[r for r in rows if r['split']=='train'];fit_rows=sorted(train,key=lambda r:r['arc_fraction'])
    if len(fit_rows)>180:fit_rows=[fit_rows[k] for k in np.linspace(0,len(fit_rows)-1,180).astype(int)]
    models=[]
    for n in COUNTS:
        for hand in (-1,1):
            model=fit(curve,fit_rows,n,hand);name=f'N{n}-h{hand:+}';model['id']=name
            scene=Scene(curve,model['parameters']);model['evaluation']={}
            for split in ('train','holdout'):
                rr=[r for r in rows if r['split']==split];d=evaluate(scene,rr,24)
                model['evaluation'][split]=dict(mean_support=d['mean_support'],observations=len(rr),
                     supported80=sum(f>=.8 for f in d['fractions']),unmatched=sum(k<0 for k in d['owners']),unknown=d['unknown'])
            save(OUT/(name+'-fit.json'),model);models.append(model)
            print('fit',name,model['train_objective'],model['evaluation']['holdout'],model['certificate']['certified'],flush=True)
    # Training-only ranking; retain two count alternatives for each hand.
    selected=[]
    for hand in (-1,1):
        ranked=sorted([m for m in models if m['parameters']['hand']==hand],
                      key=lambda m:(not m['certificate']['certified'],-m['train_objective']))
        selected+=ranked[:2]
    native,rgb,meta=photo();features=image_features(rgb)
    summaries=[export(curve,m,rows,rgb,features) for m in selected]
    comparison=[{k:m[k] for k in ('id','parameters','train_objective','evaluation','evaluations')}|
                {'certified':m['certificate']['certified'],'minimum_gap':m['certificate'].get('minimum_gap_units')} for m in models]
    result=dict(candidates=comparison,exported=summaries,selected_ids=[m['id'] for m in selected],
                phase1_sha256=sha(OUT/'phase1.json.gz'),anchors=len(rows),fit_anchors=len(fit_rows),
                anchor_ids=[r['record_id'] for r in rows],training_ids=[r['record_id'] for r in fit_rows],
                curve=curve.tolist(),unique_count=False,unique_hand=False,
                limits='Five-count grid and bounded shared-pose search; all assignments conditional. No pattern input or fit-to-output iteration.')
    save(OUT/'phase2.json',result);return result


if __name__=='__main__':main()

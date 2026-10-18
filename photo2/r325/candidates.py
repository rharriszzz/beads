"""Shared affine geometry, colored-only initialization, bidirectional proposals.
No color-dependent size/orientation; sigma describes bright-support localization.
"""
from collections import defaultdict
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r323 import tracker as joint
from photo2.r322 import tracker as base
from .batched_fit import fit_hypotheses


def signature(h):
    a=h['assignments'];first=a[sorted(a)[0]]['ab']
    return tuple((o,*(np.array(a[o]['ab'])-first)) for o in sorted(a))


def refine(xy,sigma,weight,B,offset,ids):
    B=B.copy();B0=B.copy();offset=offset.copy();n=len(xy)
    for iteration in range(5):
        ab=np.rint((xy-offset)@np.linalg.inv(B).T).astype(int);pred=ab@B.T+offset;err=np.linalg.norm(pred-xy,axis=1)/sigma;good=err<2
        for cell in set(map(tuple,ab[good])):
            ii=np.flatnonzero(good&np.all(ab==cell,axis=1))
            if len(ii)>1:good[ii[np.argsort(err[ii])[1:]]]=False
        if good.sum()<6:return None
        X=np.column_stack([ab,np.ones(n)]);w=weight*np.exp(-.5*err**2)/sigma**2;w[~good]=0
        coef=np.linalg.lstsq(X*np.sqrt(w[:,None]),xy*np.sqrt(w[:,None]),rcond=None)[0];nb=coef[:2].T
        if not joint.valid_basis(nb,B0):break
        B=nb;offset=coef[2]
    pred=ab@B.T+offset;res=np.linalg.norm(pred-xy,axis=1);err=res/sigma;good=err<2
    for cell in set(map(tuple,ab[good])):
        ii=np.flatnonzero(good&np.all(ab==cell,axis=1))
        if len(ii)>1:good[ii[np.argsort(err[ii])[1:]]]=False
    lookup={tuple(ab[i]):i for i in np.flatnonzero(good)};tri=0;edges=[]
    for i in np.flatnonzero(good):
        for d,f in joint.STEPS.items():
            j=lookup.get(tuple(ab[i]+d))
            if j is not None:edges.append((ids[i],ids[j],f))
        tri+=int(tuple(ab[i]+(1,0)) in lookup and tuple(ab[i]+(0,1)) in lookup)
    if tri<2:return None
    return dict(score=float(np.sum(weight[good]*(1-.25*err[good]**2))+.18*tri),basis=B.tolist(),offset=offset.tolist(),triangles=tri,
        assignments={ids[i]:dict(ab=ab[i].tolist(),predicted_xy=pred[i].tolist(),residual_px=float(res[i])) for i in np.flatnonzero(good)},edges=edges)


def to_world(h,w):
    R=np.array(w['frame']);cen=np.array(w['center']);h['basis_local']=h['basis'];h['offset_local']=h['offset']
    h['basis']=(R@h['basis']).tolist();h['offset']=(R@h['offset']+cen).tolist()
    for a in h['assignments'].values():a['predicted_xy']=(R@a['predicted_xy']+cen).tolist()
    return h


def inputs(w,op):
    ids=w['observation_ids'];xy=(np.array([op[o]['xy'] for o in ids])-w['center'])@np.array(w['frame'])
    return ids,xy,np.array([8 if op[o]['color']=='black' else 5 for o in ids]),np.array([1 if op[o]['band_clearance_px']>=18 else .55 for o in ids])


def augment(windows,obs,data):
    op={o['id']:o for o in obs};rng=np.random.default_rng(325);initial=[list(w['hypotheses']) for w in windows];predictions=[];stats=[]
    for wi,w in enumerate(windows):
        ids,xy,sig,wt=inputs(w,op);ci=np.array([i for i,o in enumerate(ids) if op[o]['color'] in ['red','yellow']]);extras=[];colored=[]
        if len(ci)>=6:
            for B in w.get('competing_bases_local',[])[:3]:
                hh,_,_=fit_hypotheses(xy[ci],sig[ci],wt[ci],np.array(B),[ids[i] for i in ci],rng);colored+=hh
            seen=set();kept=[]
            for h in sorted(colored,key=lambda h:-h['score']):
                s=signature(h)
                if s not in seen:kept.append(h);seen.add(s)
                if len(kept)>=2:break
            for rank,h in enumerate(kept):
                B=np.array(h['basis']);offset=np.array(h['offset']);a=h['assignments'];cells={tuple(v['ab']):o for o,v in a.items()};neighbors=defaultdict(list)
                for cell,oid in cells.items():
                    for d in [(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)]:neighbors[(cell[0]+d[0],cell[1]+d[1])].append(oid)
                for cell,anchors in neighbors.items():
                    if cell in cells or len(anchors)<2:continue
                    # Avoid two opposite collinear neighbors as sole geometry.
                    ac=np.array([a[o]['ab'] for o in anchors])-cell
                    if np.linalg.matrix_rank(ac)<2:continue
                    local=B@cell+offset
                    if max(abs(local))>84:continue
                    point=np.array(w['frame'])@local+w['center']
                    if float(base.sample(data['clearance'],point[None])[0])<18:continue
                    distances=np.linalg.norm(np.array([o['xy'] for o in obs])-point,axis=1);j=int(np.argmin(distances));near=obs[j]
                    predictions.append(dict(window=w['id'],colored_hypothesis=rank,cell_ab=list(cell),predicted_xy=point.tolist(),colored_anchors=anchors,
                        nearest_observation=near['id'],nearest_color=near['color'],distance_px=float(distances[j]),
                        status='geometric candidate; no new observed bead implied',basis_local=B.tolist(),offset_local=offset.tolist(),colored_assignments={o:v['ab'] for o,v in a.items()}))
                hh=refine(xy,sig,wt,B,offset,ids)
                if hh:hh.update(proposal_source='colored-only initialization then shared all-color refinement',colored_seed_ids=sorted(a));extras.append(to_world(hh,w))
        for delta in (-2,-1,1,2):
            jj=(wi+delta)%len(windows)
            for h in initial[jj][:2]:
                common=sorted(set(ids)&h['assignments'].keys())
                if len(common)<4:continue
                B=np.array(h['basis_local']);ii=[ids.index(o) for o in common];ab=np.array([h['assignments'][o]['ab'] for o in common]);offset=np.median(xy[ii]-ab@B.T,axis=0)
                hh=refine(xy,sig,wt,B,offset,ids)
                if hh:hh.update(proposal_source='bidirectional neighboring candidate reuse',source_window=windows[jj]['id']);extras.append(to_world(hh,w))
        unique={signature(h):h for h in initial[wi]};added=[]
        # Original six retained, plus at most four distinct new hypotheses.
        for h in sorted(extras,key=lambda h:-h['score']):
            key=signature(h)
            if key in unique:continue
            unique[key]=h;added.append(h)
            if len(added)>=4:break
        w['hypotheses']=initial[wi]+added
        stats.append(dict(window=w['id'],original=len(initial[wi]),colored_only_fits=len(colored),extra_proposals=len(extras),retained_extra=len(added)))
    return predictions,stats


def inspect_black_predictions(predictions,obs,data):
    """Raw-pixel search at geometry-predicted sites, including faint reflections.
    Unassociated evidence stays conditional; duplicate/body identity is unresolved.
    """
    rgb=data['rgb'];minimum=rgb.min(2);white=np.where(minimum<=.04045,minimum/12.92,((minimum+.055)/1.055)**2.4);records=[]
    for p in predictions:
        if p['distance_px']<=12:
            if p['nearest_color']=='black':records.append(dict(**p,evidence='existing independently measured black support',measured_observation=p['nearest_observation']))
            continue
        x,y=map(lambda a:int(round(a)),p['predicted_xy']);y0=max(0,y-10);x0=max(0,x-10);patch=white[y0:y+11,x0:x+11]
        yy,xx=np.unravel_index(np.argmax(patch),patch.shape);peak=float(patch[yy,xx]);med=np.median(rgb[y0:y+11,x0:x+11].reshape(-1,3),axis=0)
        contrast=peak-float(np.median(patch));dark=med.max()<.35 and np.ptp(med)<.12
        row=dict(**p,peak_linear_white=peak,contrast_linear_white=contrast,median_rgb=med.tolist(),dark_neutral_neighborhood=bool(dark),evidence='conditional expected site; no independent observed bead support',measured_observation=None)
        if peak>=.015 and contrast>=.006 and dark:
            lab,_=ndi.label(patch>=.5*peak,np.ones((3,3)));label=lab[yy,xx];py,px=np.where(lab==label)
            if 2<=len(px)<=150 and not np.any((px==0)|(py==0)|(px==patch.shape[1]-1)|(py==patch.shape[0]-1)):
                coords=np.column_stack([px+x0,py+y0]);centroid=np.average(coords,axis=0,weights=white[coords[:,1],coords[:,0]])
                row.update(evidence='faint native reflection candidate; body identity unconfirmed',raw_support_pixels=coords.tolist(),raw_centroid_xy=centroid.tolist())
        records.append(row)
    groups=defaultdict(list)
    for r in records:
        if r['measured_observation']:groups[r['measured_observation']].append(r)
    supported=[dict(observation=o,windows=sorted({r['window'] for r in rr}),minimum_prediction_distance_px=min(r['distance_px'] for r in rr),colored_anchors=sorted({a for r in rr for a in r['colored_anchors']})) for o,rr in groups.items() if len({r['window'] for r in rr})>=2]
    return dict(predictions=records,black_supports_predicted_by_colored_only=supported,
        policy='Same shared basis and size for every color. Black sigma concerns the bright support, not bead radius. Faint/raw/dark-only candidates are not promoted to confirmed beads without identity evidence.')

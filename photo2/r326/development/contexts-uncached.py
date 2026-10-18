"""Cached multiscale measurements and selective candidate transport, image only."""
from collections import defaultdict
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r325.spectral import directions
from photo2.r325.batched_fit import fit_hypotheses
from photo2.r325.candidates import signature,refine,to_world,inputs
from photo2.r322 import tracker as base


def measure(w,obs,data,size=160,shift=0.,seed=326):
    R=np.array(w['frame']);cen=np.array(w['center'])+shift*R[:,0]
    grid=np.indices((size,size))[::-1].reshape(2,-1).T-(size-1)/2;pts=grid@R.T+cen
    patch={k:base.sample(data[k],pts).reshape(size,size) for k in ['z','fg']};patch['fg']=patch['fg']>.5
    patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(size)[None,:]
    xy=np.array([o['xy'] for o in obs]);local=(xy-cen)@R
    ii=np.flatnonzero((np.abs(local).max(1)<size/2-8)&np.array([o['band_clearance_px']>=10 for o in obs]))
    ids=[obs[i]['id'] for i in ii];row=dict(id=f"{w['id']}-{size}-{shift:g}",parent=w['id'],center=cen.tolist(),frame=R.tolist(),size=size,shift=shift,observation_ids=ids,hypotheses=[])
    if len(ids)<8:row['stop']='insufficient observations';return row
    try:_,sp=directions(patch)
    except ValueError as ex:row['stop']=str(ex);return row
    bases=[];hs=[];rng=np.random.default_rng(seed+int(w['id'])*100+size+int(shift));sig=np.array([8 if obs[i]['color']=='black' else 5 for i in ii]);wt=np.array([1 if obs[i]['band_clearance_px']>=18 else .55 for i in ii])
    for tri in sp['triangles']:
        B=np.linalg.inv(np.array([sp['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
        if any(np.linalg.norm(B-b)<4 for b in bases):continue
        bases.append(B);hs+=fit_hypotheses(local[ii],sig,wt,B,ids,rng)[0]
        if len(bases)>=10:break
    unique={}
    for h in sorted(hs,key=lambda h:-h['score']):
        s=signature(h)
        if s not in unique:unique[s]=h
    row['hypotheses']=list(unique.values())[:6];row['spectral']=sp
    return row


def pair_evidence(contexts):
    """One envelope per parent region. Correlated sizes are not vote multipliers."""
    votes=defaultdict(lambda:defaultdict(list))
    for c in contexts:
        if not c['hypotheses']:continue
        best=c['hypotheses'][0]['score'];pairs=defaultdict(set)
        for hi,h in enumerate(c['hypotheses']):
            if h['score']<best-1.:continue
            a=h['assignments'];ids=sorted(a)
            for ii,x in enumerate(ids):
                for y in ids[ii+1:]:
                    d=tuple(np.array(a[y]['ab'])-a[x]['ab'])
                    if max(abs(z) for z in d)<=4:pairs[x,y].add(d)
        for pair,ds in pairs.items():votes[pair][c['parent']].append(dict(context=c['id'],deltas=sorted(ds)))
    return votes


def rescore(windows,contexts):
    evidence=pair_evidence(contexts);ledger=[]
    for wi,w in enumerate(windows):
        for hi,h in enumerate(w['hypotheses']):
            h.setdefault('photo_score',h['score']);a=h['assignments'];ids=sorted(a);regions=defaultdict(list)
            for ii,x in enumerate(ids):
                for y in ids[ii+1:]:
                    pair=(x,y)
                    if pair not in evidence:continue
                    d=tuple(np.array(a[y]['ab'])-a[x]['ab'])
                    for region,rows in evidence[pair].items():
                        # The strongest contradiction from any size remains;
                        # ambiguous contexts contribute half of a contradiction.
                        losses=[0 if r['deltas']==[d] else (.5 if d in r['deltas'] else 1.) for r in rows]
                        regions[region].append(max(losses))
            # Bounded regional mean prevents larger contexts dominating by pair count.
            penalty=4.*float(np.mean([np.mean(v) for v in regions.values()])) if regions else 0.
            h['context_penalty']=penalty;h['score']=h['photo_score']-penalty
            ledger.append(dict(window=w['id'],hypothesis=hi,penalty=penalty,regions=len(regions)))
    return ledger,evidence


def augment_contexts(windows,contexts,obs,affected,max_add=4):
    op={o['id']:o for o in obs};records=[]
    for wi in sorted(affected):
        w=windows[wi];ids,xy,sig,wt=inputs(w,op);seen={signature(h) for h in w['hypotheses']};proposals=[]
        for c in contexts:
            if np.linalg.norm(np.array(c['center'])-w['center'])>130:continue
            for hi,h in enumerate(c['hypotheses']):
                common=set(ids)&h['assignments'].keys()
                if len(common)<6:continue
                worldB=np.array(c['frame'])@h['basis'];worldoff=np.array(c['frame'])@h['offset']+c['center']
                B=np.array(w['frame']).T@worldB;offset=(worldoff-w['center'])@np.array(w['frame'])
                hh=refine(xy,sig,wt,B,offset,ids)
                if hh:
                    hh.update(proposal_source='changed-context transported fit',source_context=c['id'],source_hypothesis=hi);proposals.append(to_world(hh,w))
        added=[]
        # Keep disagreement-diverse candidates, not just the highest local score.
        # Round robin over contexts, with all original states retained forever.
        groups=defaultdict(list)
        for h in sorted(proposals,key=lambda h:-h['score']):groups[h['source_context']].append(h)
        while groups and len(added)<max_add:
            for key in list(groups):
                h=groups[key].pop(0);s=signature(h)
                if s not in seen:seen.add(s);added.append(h)
                if not groups[key]:del groups[key]
                if len(added)>=max_add:break
        w['hypotheses']+=added
        records.append(dict(window=w['id'],proposed=len(proposals),added=len(added),sources=[h['source_context'] for h in added]))
    return records


def edge_context(e,evidence):
    a,b=e['source'],e['target'];d=tuple(e['delta_ab']);pair=tuple(sorted([a,b]));d=d if a<b else tuple(-np.array(d))
    regions=evidence.get(pair,{})
    rows=[dict(region=k,context=r['context'],deltas=[list(x) for x in r['deltas']]) for k,rr in regions.items() for r in rr]
    excludes=sum(d not in [tuple(x) for x in r['deltas']] for r in rows);amb=sum(len(r['deltas'])>1 for r in rows)
    status='untested' if not rows else ('contested' if excludes else ('ambiguous' if amb else 'consistent'))
    return dict(status=status,contexts=rows,excludes=excludes,ambiguous=amb,correlated_regions=len(regions))

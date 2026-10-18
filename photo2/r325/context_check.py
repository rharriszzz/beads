"""Post-selection multiscale photo consistency stress test, never training labels.
New window sizes and offsets measure the same original photograph; this is not
an independent ground-truth denominator. All competing local deltas are retained.
"""
import json,time
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r324 import fast_tracker as old
from .spectral import directions
from .batched_fit import fit_hypotheses
from .candidates import signature
OUT=Path(__file__).parent/'results'
def main():
    start=time.perf_counter();g=json.load(open(OUT/'graph.json'));op={o['id']:o for o in g['observations']};obs=g['observations'];xy=np.array([o['xy'] for o in obs]);tree=cKDTree(xy);data=old.preprocess(ImageOps.exif_transpose(Image.open('beads-photo-2.jpg')).convert('RGB'));rng=np.random.default_rng(32501)
    # Includes all old breaks, plus the narrow unresolved winding cut.
    centers=[dict(name=f'old-break-{i}',xy=g['windows'][i]['center'],frame=g['windows'][i]['frame']) for i in [14,15,73,74,81,85,110,111,114,120,121,125,126,129,130,131,142,162,167]]
    centers+=[dict(name='winding-gap',xy=[1485,3010],frame=g['windows'][72]['frame']),dict(name='upper-contested',xy=[1585,280],frame=g['windows'][11]['frame'])]
    ledger=[];votes=defaultdict(list)
    for c in centers:
        R=np.array(c['frame'])
        for size in [160,240,280]:
            cen=np.array(c['xy']);grid=np.indices((size,size))[::-1].reshape(2,-1).T-(size-1)/2;pts=grid@R.T+cen
            patch={k:old.base.sample(data[k],pts).reshape(size,size) for k in ['z','fg']};patch['fg']=patch['fg']>.5;patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(size)[None,:]
            ii=[i for i in sorted(tree.query_ball_point(cen,size*.75)) if np.max(abs((xy[i]-cen)@R))<size/2-8 and obs[i]['band_clearance_px']>=10];ids=[obs[i]['id'] for i in ii];local=(xy[ii]-cen)@R
            row=dict(id=len(ledger),region=c['name'],center=cen.tolist(),size=size,observations=ids,hypotheses=[]);ledger.append(row)
            try:_,sp=directions(patch)
            except ValueError as ex:row['stop']=str(ex);continue
            bases=[];hs=[];sig=np.array([8 if obs[i]['color']=='black' else 5 for i in ii]);wt=np.array([1 if obs[i]['band_clearance_px']>=18 else .55 for i in ii])
            for tri in sp['triangles']:
                B=np.linalg.inv(np.array([sp['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
                if any(np.linalg.norm(B-b)<4 for b in bases):continue
                bases.append(B);hs+=fit_hypotheses(local,sig,wt,B,ids,rng)[0]
                if len(bases)>=10:break
            unique={}
            for h in sorted(hs,key=lambda h:-h['score']):
                s=signature(h)
                if s not in unique:unique[s]=h
            row['hypotheses']=list(unique.values())[:6]
            if not row['hypotheses']:continue
            best=row['hypotheses'][0]['score'];selected=[(k,h) for k,h in enumerate(row['hypotheses']) if h['score']>=best-1.]
            for e in g['graph']['edges']+g['graph']['unresolved_edges']:
                a,b=e['source'],e['target']
                if np.linalg.norm((np.array(op[a]['xy'])+op[b]['xy'])/2-cen)>size/2-20:continue
                deltas=sorted({tuple(np.array(h['assignments'][b]['ab'])-h['assignments'][a]['ab']) for k,h in selected if a in h['assignments'] and b in h['assignments']})
                if deltas:votes[a,b].append(dict(context=row['id'],region=c['name'],size=size,deltas=[list(x) for x in deltas],selected_hypotheses=[k for k,h in selected]))
    edges=[]
    for e in g['graph']['edges']+g['graph']['unresolved_edges']:
        v=votes[e['source'],e['target']]
        if not v:continue
        d=e['delta_ab'];agree=sum(d in r['deltas'] for r in v);only=sum(r['deltas']==[d] for r in v);contr=sum(d not in r['deltas'] for r in v);amb=sum(len(r['deltas'])>1 for r in v)
        edges.append(dict(source=e['source'],target=e['target'],global_delta=d,primary_status=e['status'],contexts=len(v),contains_global=agree,only_global=only,excludes_global=contr,ambiguous_contexts=amb,votes=v,
            status='context-contested' if contr else ('context-ambiguous' if amb else 'consistent in tested contexts')))
    report=dict(seconds=time.perf_counter()-start,windows=ledger,edges=edges,summary=dict(Counter(e['status'] for e in edges)),
        accepted_edge_summary=dict(Counter(e['status'] for e in edges if e['primary_status']=='accepted conditional')),
        policy='Post-freeze stress test at changed window widths, same original pixels. Local maxima are not global truth. Conflicting contexts are retained and mark fixed model correspondences as unresolved. No optimization or R161 tuning.')
    old.save(OUT/'context-check.json',report);print({k:report[k] for k in ['seconds','summary','accepted_edge_summary']})
if __name__=='__main__':main()

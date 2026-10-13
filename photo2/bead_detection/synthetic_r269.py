"""Broad-search neighbor validation; scene truth never enters search or eligibility."""
from collections import Counter,defaultdict
import gzip,json
import numpy as np
from skimage.morphology import h_maxima
from .audit_r267 import save,csvsave
from .climb_r268 import background,Surface,VARIANTS
from .synthetic_r268 import start_points
from .search_r269 import Neighborhood,POLICIES
from .experiment_r269 import OUT,PRIOR,RADII,writegz

def main():
    images=np.load(PRIOR/'synthetic-inputs.npz');truths=np.load(PRIOR/'synthetic-truth.npz');rows=[];inventory=[];moves=0;paths=0;failures={};summaries={}
    with gzip.GzipFile(filename=str(OUT/'synthetic-search-traces.jsonl.gz'),mode='wb',mtime=0) as f:
      for index,name in enumerate(images.files):
        rgb=images[name];value=rgb.max(axis=2);hsv,paper,model=background(rgb);points=start_points(value);strong=h_maxima(value,12,footprint=np.ones((3,3)))
        # Eligibility uses only fixed image background evidence. Keep every excluded
        # maximum and its reason; withheld truth is evaluated afterwards.
        eligible=[p for p in points if paper[p[1],p[0]]==0]
        truth=truths[name]
        inventory.append(dict(scene=name,raw_starts=[dict(x=x,y=y,eligible=bool(paper[y,x]==0),background_code=int(paper[y,x]),truth=int(truth[y,x]),prominence12=bool(strong[y,x])) for x,y in points]))
        scene_results=defaultdict(list)
        for side in (5,7,9):
          surface=Surface(value,hsv,paper,side)
          for start_index,xy in enumerate(eligible):
            prefix=surface.climb(xy,VARIANTS['guarded12']);g=Neighborhood(value,hsv,paper,surface.sums,side,prefix['endpoint'],reference_raw=prefix['steps'][-1]['running_raw_peak'])
            body=int(truth[xy[1],xy[0]])
            for radius in RADII:
              for pname,policy in POLICIES.items():
                q=g.search(radius,policy);path=g.path(q['pred'],q['end']);moves+=g.audit(path,radius,policy);paths+=1;ex,ey=g.xy[q['end']];endbody=int(truth[ey,ex])
                crossed=body>0 and endbody not in (0,body);bg=body>0 and endbody==0
                path_cross=body>0 and any(truth[p['y'],p['x']] not in (0,body) for p in path)
                record=dict(scene=name,start_index=start_index,original_start=list(xy),window=side,radius=radius,policy=pname,
                    anchor=prefix['endpoint'],raw_reference=g.reference_raw,endpoint=[int(ex),int(ey)],truth_start=body,truth_end=endbody,
                    prominence12=bool(strong[xy[1],xy[0]]),anchor_mean=g.reference_mean,end_mean=float(g.mean[q['end']]),gain=float(g.mean[q['end']]-g.reference_mean),
                    prefix=prefix,path=path,raw_floor=g.reference_raw-policy.raw_drop,mean_floor=g.reference_mean-policy.mean_drop,
                    endpoint_cross=bool(crossed),path_cross=bool(path_cross),body_to_background=bool(bg))
                writegz(f,record);scene_results[side,radius,pname].append(record)
                label=('unobservable' if name.startswith('no-visible') and crossed else 'cross-body' if crossed else 'background' if bg else None)
                if label and body and radius==16 and side==7:
                    key=label+'-'+pname
                    if key not in failures:failures[key]=dict(record,blocked_frontier=q['frontier'])
        for (side,radius,pname),rs in scene_results.items():
            groups=defaultdict(set)
            for r in rs:groups[tuple(r['endpoint'])].add(r['truth_start'])
            rows.append(dict(scene=name,window=side,radius=radius,policy=pname,raw_starts=len(points),eligible_starts=len(eligible),
                raw_body_starts=sum(truth[y,x]>0 for x,y in points).item(),eligible_body_starts=sum(r['truth_start']>0 for r in rs),
                endpoint_cross=sum(r['endpoint_cross'] for r in rs),path_cross=sum(r['path_cross'] for r in rs),body_to_background=sum(r['body_to_background'] for r in rs),
                background_to_body=sum(r['truth_start']==0 and r['truth_end']>0 for r in rs),mixed_endpoint_groups=sum(len(s-{0})>1 for s in groups.values()),
                strong_body_starts=sum(r['prominence12'] and r['truth_start']>0 for r in rs),strong_cross=sum(r['prominence12'] and r['endpoint_cross'] for r in rs),
                strong_background=sum(r['prominence12'] and r['body_to_background'] for r in rs)))
        if (index+1)%25==0:print('scenes',index+1,'paths',paths,flush=True)
    for category in ('stress','no-visible-interface'):
      for side in (5,7,9):
       for radius in RADII:
        for pname in POLICIES:
            rs=[r for r in rows if r['scene'].startswith(category) and r['window']==side and r['radius']==radius and r['policy']==pname]
            summaries[f'{category}-{side}-r{radius}-{pname}']={k:sum(r[k] for r in rs) for k in rows[0] if k not in ('scene','window','radius','policy')}
    csvsave(OUT/'synthetic-results.csv',rows);save(OUT/'synthetic-starts.json',inventory);save(OUT/'synthetic-failures.json',failures)
    save(OUT/'synthetic-summary.json',dict(scenes=len(images.files),paths=paths,audited_moves=moves,results=summaries,
         interpretation='All raw maxima retained in inventory. Only fixed-background-eligible starts searched; exclusions remain separate. Repeated windows/policies/radii are not independent trials. No truth in eligibility or paths.'))
    print('complete',paths,moves,summaries['stress-7-r16-raw24-mean2'],flush=True)
if __name__=='__main__':main()

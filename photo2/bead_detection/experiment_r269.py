"""R269 photograph inventory, exhaustive bounded searches and focused route evidence."""
from collections import defaultdict,Counter
from dataclasses import asdict
import csv,gzip,hashlib,json,time
from pathlib import Path
import numpy as np
from skimage.morphology import local_maxima
from .audit_r267 import ROOT,photo,save,csvsave,exact_prominence
from .climb_r268 import background,score_sums
from .search_r269 import Neighborhood,POLICIES,Policy,REASONS

OUT=ROOT/'photo2/review/r269';PRIOR=ROOT/'photo2/review/r268';RADII=(3,6,10,16)
FOCUS={'R00956': [('upper-yellow','P090697'),('middle-yellow','P091868'),('lower-yellow','P093030')],
       'R01284':[('central-yellow','P128915'),('shadowed-neighbor','P129034')]}

def writegz(f,r):f.write((json.dumps(r,separators=(',',':'),default=lambda x:x.item() if isinstance(x,np.generic) else list(x))+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def shift_path(path,origin):
    return [dict(p,x=p['x']+int(origin[0]),y=p['y']+int(origin[1])) for p in path]
def shift_xy(xy,origin):return (np.asarray(xy)+origin).astype(int).tolist()

def direct_path(g,target):
    a=np.array(g.anchor);b=g.xy[target];n=int(np.abs(b-a).max())
    pts=[tuple(np.rint(a+(b-a)*t/max(n,1)).astype(int)) for t in range(n+1)]
    ids=[g.index(p) for p in pts];pred=np.full(len(g.v),-9999,int)
    for p,q in zip(ids,ids[1:]):pred[q]=p
    return g.path(pred,target)

def direct_failures(g,path,radius,policy):
    spatial,bits=g.edge_masks(radius,policy);lookup={(int(a),int(b)):i for i,(a,b) in enumerate(zip(g.a,g.b))};out=[]
    for a,b in zip(path,path[1:]):
        edge=lookup[g.index((a['x'],a['y'])),g.index((b['x'],b['y']))]
        reasons=[s for k,s in REASONS.items() if bits[edge]&k]
        if not spatial[edge]:reasons.append('outside-search-radius-or-image-window')
        if reasons:out.append(dict(from_xy=[a['x'],a['y']],to_xy=[b['x'],b['y']],reasons=reasons))
    return out

def main():
    OUT.mkdir(exist_ok=True);beg=time.time();rgb=photo();v=rgb.max(axis=2);hsv,paper,model=background(rgb)
    sums={n:score_sums(v,n) for n in (5,7,9)}
    cases=json.loads((PRIOR/'starts.json').read_text());save(OUT/'starts.json',cases)
    save(OUT/'parameters.json',dict(windows=[5,7,9],search_radii=list(RADII),policies={k:asdict(p) for k,p in POLICIES.items()},
         primary_review='raw24-mean2; diagnostic only',anchor='each original start preserves its R268 guarded12 endpoint for each window',
         raw_reference='maximum raw V actually visited on that R268 prefix; does not reset at endpoint',
         mean_reference='mean V at the R268 endpoint',background=model,
         path='all 8-neighbor paths inside closed Euclidean disk; equality/descent allowed above floors; diagonal corners also inside disk and pass barriers',
         ranking='greatest exact mean sum, then least displacement from anchor, then y/x; prominence and H/S reported independently, no mixed weights or prominence gate',
         identity='coordinate proposals only; original provenance never merged; supplied separate-bead observation used only in review'))
    focus=[];rows=[];decisions=[];all_candidates={};moves=0;replays=0;summary={};candidate_paths=[]
    with gzip.GzipFile(filename=str(OUT/'photo-search-traces.jsonl.gz'),mode='wb',mtime=0) as traces:
      for crop,case in cases.items():
        old=json.load(gzip.open(PRIOR/f'{crop}-traces.json.gz'))
        anchors=[t['endpoint'] for n in ('5','7','9') for t in old[n]['guarded12'].values()]
        a=np.array(anchors);x0=max(0,int(a[:,0].min())-21);y0=max(0,int(a[:,1].min())-21);x1=min(v.shape[1],int(a[:,0].max())+22);y1=min(v.shape[0],int(a[:,1].max())+22)
        origin=np.array([x0,y0]);cut=np.s_[y0:y1,x0:x1];vv=v[cut];hh=hsv[cut];pp=paper[cut];ss={n:sums[n][cut] for n in sums}
        np.savez_compressed(OUT/f'{crop}-score-images.npz',origin=origin,rgb=rgb[cut],raw_v=vv,hsv=hh,background_stop_codes=pp,**{f'sum{n}':ss[n] for n in ss})
        # All original maxima survive; add native raw/mean maxima in the search halo.
        locations=defaultdict(set);rawids={};knownprom={}
        for r in csv.DictReader(open(ROOT/f'photo2/review/r267/{crop}-all-maximum-pixels.csv')):
            xy=int(r['x']),int(r['y']);locations[xy].add('original-raw-maximum');rawids[xy]=r['plateau_id'];knownprom[xy]=(int(r['prominence_dn']),int(r['saddle_v']),r['prominence_certificate'])
        for name,arr in [('raw',vv)]+[(f'mean{n}',ss[n]) for n in ss]:
            yy,xx=np.where(local_maxima(arr,connectivity=2,allow_borders=False))
            for x,y in zip(xx,yy):
                xy=(int(x+x0),int(y+y0))
                if 4<=x<vv.shape[1]-4 and 4<=y<vv.shape[0]-4:locations[xy].add(name+'-regional-maximum-pixel')
        for n in ('5','7','9'):
            for t in old[n]['guarded12'].values():locations[tuple(t['endpoint'])].add('R268-mean'+n+'-endpoint')
        missing=[xy for xy,types in locations.items() if any('raw' in z for z in types) and xy not in knownprom]
        if missing:
            for xy,p in zip(missing,exact_prominence(v,missing,[x0,y0,x1,y1])):knownprom[xy]=p
        candidates=[]
        for i,(xy,types) in enumerate(sorted(locations.items(),key=lambda p:(p[0][1],p[0][0])),1):
            x,y=xy;p=knownprom.get(xy,(0,None,'non-raw-maximum: higher raw neighbor reachable without descent'));c=rgb[y,x]
            candidates.append(dict(id=f'C{i:04d}',number=i,x=x,y=y,types=sorted(types),raw_maximum_id=rawids.get(xy,''),raw_v=int(v[y,x]),
                 mean5=float(sums[5][y,x]/25),mean7=float(sums[7][y,x]/49),mean9=float(sums[9][y,x]/81),raw_prominence=p[0],raw_saddle=p[1],prominence_certificate=p[2],
                 h_deg=float(hsv[y,x,0]*360),s=float(hsv[y,x,1]),rgb=c.tolist(),srgb_weighted_channels=float(c@[.2126,.7152,.0722])))
        all_candidates[crop]=candidates;csvsave(OUT/f'{crop}-all-competing-points.csv',candidates)
        named={}
        for label,pid in FOCUS[crop]:
            start=next(s for s in case['starts'] if any(o['id']==pid and o['role']=='seed' and o['source']=='straight-0-selected12' for o in s['origins']))
            named[start['id']]=(label,pid)
        crop_rows=[]
        for n in (5,7,9):
          for s in case['starts']:
            t=old[str(n)]['guarded12'][s['id']];anchor=np.array(t['endpoint'])-origin
            g=Neighborhood(vv,hh,pp,ss[n],n,anchor,reference_raw=t['steps'][-1]['running_raw_peak'])
            special=s['id'] in named
            for radius in RADII:
              for policy_name,policy in POLICIES.items():
                q=g.search(radius,policy);path=g.path(q['pred'],q['end']);moves+=g.audit(path,radius,policy)
                row=dict(crop=crop,start_id=s['id'],window=n,radius=radius,policy=policy_name,original_start=s['xy'],anchor=t['endpoint'],endpoint=shift_xy(g.xy[q['end']],origin),
                     r268_stop=t['stop'],raw_reference=g.reference_raw,raw_floor=g.reference_raw-policy.raw_drop,mean_floor=g.reference_mean-policy.mean_drop,
                     anchor_mean=g.reference_mean,end_mean=float(g.mean[q['end']]),gain=float(g.mean[q['end']]-g.reference_mean),
                     end_raw=int(g.v[q['end']]),steps=len(path)-1,reachable_pixels=len(q['order']),start_background=q['start_blocked'])
                rows.append(row);crop_rows.append(row)
                frontier=[dict(e,from_xy=shift_xy(e['from_xy'],origin),to_xy=shift_xy(e['to_xy'],origin)) for e in q['frontier']]
                # Predecessor tree saves a reconstructible route to every reachable
                # pixel, not just the winning endpoint. Cut edges certify exclusions.
                tree=[[int(g.xy[i,0]+x0),int(g.xy[i,1]+y0),int(q['pred'][i])] for i in q['order']]
                writegz(traces,dict(**row,path=shift_path(path,origin),graph_origin=[g.x0+x0,g.y0+y0],graph_shape=list(g.shape),reachable_tree=tree,blocked_frontier=frontier))
                if special:
                    label,pid=named[s['id']]
                    if radius==16:
                        replay=g.search(radius,policy);assert q['end']==replay['end'] and np.array_equal(q['pred'],replay['pred']);replays+=1
                        focus.append(dict(**row,case=label,maximum_id=pid,r268_trace=t,path=shift_path(path,origin)))
                    cap_raw,pred_raw=g.widest(radius,Policy(256,256,policy.color),'raw')
                    cap_mean,pred_mean=g.widest(radius,policy,'mean')
                    cap_constrained,pred_constrained=g.widest(radius,policy,'raw')
                    for c in candidates:
                        idx=g.index((c['x']-x0,c['y']-y0))
                        if idx is None or g.dist2[idx]>16**2:continue
                        inside=g.dist2[idx]<=radius**2;reachable=inside and q['reachable'][idx]
                        if not inside:reason='outside-search-radius'
                        elif q['start_blocked']:reason='anchor-background-or-context-uncertainty'
                        elif reachable:reason='best-mean-proposal' if idx==q['end'] else 'reachable-but-lower-mean-or-tie'
                        elif cap_raw[idx]<0:reason='no-color/background-admissible-path'
                        elif cap_raw[idx]<g.reference_raw-policy.raw_drop:reason='all-color-admissible-paths-below-raw-floor'
                        elif round(cap_mean[idx]*n*n)<g.sums[g.start]-policy.mean_drop*n*n:reason='all-raw/color-admissible-paths-below-mean-floor'
                        else:raise AssertionError('Unexplained inaccessible candidate')
                        d=dict(crop=crop,case=label,start_id=s['id'],window=n,radius=radius,policy=policy_name,candidate_id=c['id'],x=c['x'],y=c['y'],
                               distance=float(np.sqrt(g.dist2[idx])),reachable=bool(reachable),reason=reason,raw_v=c['raw_v'],mean5=c['mean5'],mean7=c['mean7'],mean9=c['mean9'],
                               raw_prominence=c['raw_prominence'],h_deg=c['h_deg'],s=c['s'],best_raw_saddle=float(cap_raw[idx]),
                               best_mean_saddle_given_raw_floor=float(cap_mean[idx]),best_raw_saddle_given_mean_floor=float(cap_constrained[idx]))
                        decisions.append(d)
                        if radius==16 and policy_name=='raw24-mean2':
                            direct=direct_path(g,idx);violations=direct_failures(g,direct,radius,policy)
                            candidate_paths.append(dict(**d,shortest_admissible=shift_path(g.path(q['pred'],idx) if reachable else [],origin),
                                widest_raw_with_color_only=shift_path(g.path(pred_raw,idx),origin),widest_mean_with_raw_and_color=shift_path(g.path(pred_mean,idx),origin),
                                widest_raw_with_mean_and_color=shift_path(g.path(pred_constrained,idx),origin),direct=shift_path(direct,origin),
                                direct_violations=[dict(e,from_xy=shift_xy(e['from_xy'],origin),to_xy=shift_xy(e['to_xy'],origin)) for e in violations]))
        csvsave(OUT/f'{crop}-search-endpoints.csv',crop_rows);summary[crop]=dict(starts=len(case['starts']),candidate_pixels=len(candidates),searches=len(crop_rows))
        print(crop,summary[crop],flush=True)
    save(OUT/'all-competing-points.json',all_candidates);save(OUT/'focus-results.json',focus);csvsave(OUT/'focus-candidate-decisions.csv',decisions)
    with gzip.GzipFile(filename=str(OUT/'focus-alternative-paths.jsonl.gz'),mode='wb',mtime=0) as f:
        for r in candidate_paths:writegz(f,r)
    save(OUT/'photo-summary.json',dict(cases=summary,searches=len(rows),audited_selected_moves=moves,deterministic_replays=replays,focus_candidate_comparisons=len(decisions),focus_alternative_route_records=len(candidate_paths),elapsed_seconds=time.time()-beg))
    inputs=[ROOT/'beads-photo-2.jpg']+[p for d in ('r267','r268') for p in sorted((ROOT/'photo2/review'/d).rglob('*')) if p.is_file()]+[ROOT/'photo2/bead_detection'/n for n in ['annular_detect.py','repaired_detect.py','refine_r266.py','climb_r268.py']]
    save(OUT/'input-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in inputs})
    print('complete',len(rows),moves,flush=True)
if __name__=='__main__':main()

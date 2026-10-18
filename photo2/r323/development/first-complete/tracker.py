"""Joint local photographic lattice hypotheses; no maker or 3D runtime inputs.

Observation locations are bright supports, not physical centers. Each local
hypothesis fits both families to multiple supports simultaneously. A beam joins
hypotheses by their shared observed identities and relative integer coordinates.
Unsupported/competing adjacencies abstain rather than stopping the whole patch.
"""
from __future__ import annotations
import argparse, json, time, hashlib
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from photo2.r322 import tracker as base
ROOT=Path(__file__).resolve().parents[2]
CROP=(900,0,1900,700)
CONFIG=dict(crop=CROP,window_width=200,window_stride=60,window_height=200,
    candidate_limit=6,beam_width=48,beam_score_allowance=3.0,
    colored_location_sigma=5.0,black_location_sigma=8.0,
    support_radius_sigma=2.0,minimum_window_observations=8,
    minimum_shared_observations=4,minimum_edge_windows=2,edge_consensus=.85,
    minimum_interior_clearance=18,seed=323)
STEPS={(1,0):'F0',(0,1):'F1',(1,-1):'difference'}
def save(p,o):
    Path(p).write_text(json.dumps(o,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist())+'\n')
def sha(p):return base.sha(p)
def utc():return datetime.now(timezone.utc).isoformat()

def fit_hypotheses(xy,sigma,weight,B0,ids,rng):
    """Discrete two-family alternatives; iterative affine fit, shared across beads."""
    n=len(xy);diff=xy[None,:,:]-xy[:,None,:];seeds=[]
    # Candidate pairs are only proposals. No pair-angle criterion accepts an edge.
    for i in range(n):
        near0=np.flatnonzero(np.linalg.norm(diff[i]-B0[:,0],axis=1)<19)
        near1=np.flatnonzero(np.linalg.norm(diff[i]-B0[:,1],axis=1)<19)
        for j in near0:
            for k in near1:
                if len({i,int(j),int(k)})<3:continue
                seeds.append((i,np.column_stack([diff[i,j],diff[i,k]])))
    # Fourier basis with every observed anchor also competes.
    seeds += [(i,B0.copy()) for i in range(n)]
    if len(seeds)>1500:seeds=[seeds[i] for i in rng.choice(len(seeds),1500,replace=False)]
    hypotheses={}
    for anchor,B in seeds:
        if not valid_basis(B,B0):continue
        offset=xy[anchor].copy()
        for iteration in range(5):
            ab=np.rint((xy-offset)@np.linalg.inv(B).T).astype(int)
            pred=ab@B.T+offset;err=np.linalg.norm(pred-xy,axis=1)/sigma
            # One observed support per site; nearby extras remain unresolved.
            good=err<2.0
            for cell in set(map(tuple,ab[good])):
                ii=np.flatnonzero(good & np.all(ab==cell,axis=1))
                if len(ii)>1:good[ii[np.argsort(err[ii])[1:]]]=False
            if good.sum()<6:break
            X=np.column_stack([ab,np.ones(n)]);w=weight*np.exp(-.5*err**2)/sigma**2;w[~good]=0
            coef=np.linalg.lstsq(X*np.sqrt(w[:,None]),xy*np.sqrt(w[:,None]),rcond=None)[0]
            newB=coef[:2].T
            if not valid_basis(newB,B0):break
            B=newB;offset=coef[2]
        pred=ab@B.T+offset;res=np.linalg.norm(pred-xy,axis=1);err=res/sigma
        good=err<2
        for cell in set(map(tuple,ab[good])):
            ii=np.flatnonzero(good & np.all(ab==cell,axis=1))
            if len(ii)>1:good[ii[np.argsort(err[ii])[1:]]]=False
        if good.sum()<6:continue
        lookup={tuple(ab[i]):i for i in np.flatnonzero(good)}
        triangles=0;edges=[]
        for i in np.flatnonzero(good):
            for d,f in STEPS.items():
                j=lookup.get(tuple(ab[i]+d))
                if j is not None:edges.append((ids[i],ids[j],f))
            triangles+=int(tuple(ab[i]+(1,0)) in lookup and tuple(ab[i]+(0,1)) in lookup)
        if triangles<2:continue
        # Saturating evidence score: blank sites earn no reward, no color pattern.
        score=float(np.sum(weight[good]*(1-.25*err[good]**2))+.18*triangles)
        accepted=np.flatnonzero(good);norm=ab-ab[accepted[0]]
        signature=tuple((ids[i],*norm[i]) for i in accepted)
        h=dict(score=score,basis=B.tolist(),offset=offset.tolist(),triangles=triangles,
            assignments={ids[i]:dict(ab=ab[i].tolist(),predicted_xy=pred[i].tolist(),residual_px=float(res[i])) for i in accepted},
            edges=edges)
        if signature not in hypotheses or score>hypotheses[signature]['score']:hypotheses[signature]=h
    ranked=sorted(hypotheses.values(),key=lambda h:-h['score'])
    # Keep distinct relative-coordinate alternatives, including near competitors.
    return ranked[:CONFIG['candidate_limit']],len(seeds),len(hypotheses)

def valid_basis(B,B0):
    if np.linalg.det(B)*np.linalg.det(B0)<=0:return False
    stretch=np.linalg.norm(B,axis=0)/np.linalg.norm(B0,axis=0)
    return bool(np.all((stretch>.62)&(stretch<1.5)) and .55<abs(np.linalg.det(B)/np.linalg.det(B0))<1.65
        and np.all(np.sum(B*B0,axis=0)/(np.linalg.norm(B,axis=0)*np.linalg.norm(B0,axis=0))>.68))

def overlap(h,k):
    common=sorted(set(h['assignments'])&set(k['assignments']))
    if len(common)<4:return dict(common=len(common),agree=0,disagree=0,translation=None,score=0)
    shifts=[tuple(np.array(h['assignments'][i]['ab'])-k['assignments'][i]['ab']) for i in common]
    delta,count=Counter(shifts).most_common(1)[0]
    return dict(common=len(common),agree=count,disagree=len(common)-count,translation=list(delta),
        score=.35*count-2.5*(len(common)-count))

def joint_select(windows):
    beam=[dict(score=0.,choices=[])]
    for wi,w in enumerate(windows):
        nxt=[]
        if not w['hypotheses']:
            for b in beam:nxt.append(dict(score=b['score'],choices=b['choices']+[None]))
        else:
            best=w['hypotheses'][0]['score']
            for b in beam:
                for hi,h in enumerate(w['hypotheses']):
                    value=h['score']-best
                    for prev in range(max(0,wi-2),wi):
                        pi=b['choices'][prev]
                        if pi is not None:value+=overlap(windows[prev]['hypotheses'][pi],h)['score']
                    nxt.append(dict(score=b['score']+value,choices=b['choices']+[hi]))
        beam=sorted(nxt,key=lambda b:-b['score'])[:CONFIG['beam_width']]
    return beam

def infer_graph(obs,windows,beam,data):
    near=[b for b in beam if b['score']>=beam[0]['score']-CONFIG['beam_score_allowance']]
    # Union of credible window states on the retained joint paths.
    selected=[sorted({b['choices'][wi] for b in near if b['choices'][wi] is not None}) for wi in range(len(windows))]
    votes=defaultdict(lambda:defaultdict(list));membership=Counter();proposals=[]
    for wi,choices in enumerate(selected):
        for hi in choices:
            h=windows[wi]['hypotheses'][hi]
            for oid in h['assignments']:membership[oid]+=1
            keys=list(h['assignments'])
            for ii,a in enumerate(keys):
                for b in keys[ii+1:]:
                    aa,bb=sorted([a,b]);delta=tuple(np.array(h['assignments'][bb]['ab'])-h['assignments'][aa]['ab'])
                    if max(abs(x) for x in delta)>2:continue
                    votes[(aa,bb)][delta].append([wi,hi])
    op={o['id']:o for o in obs};edges=[];uncertain=[];checks=[]
    for (a,b),versions in sorted(votes.items()):
        totals={d:len({wi for wi,hi in v}) for d,v in versions.items()}
        delta=max(totals,key=totals.get);win=totals[delta];allwindows=len({wi for v in versions.values() for wi,hi in v})
        disagreement_windows={wi for d,v in versions.items() if d!=delta for wi,hi in v}
        agree_ratio=1-len(disagreement_windows)/max(allwindows,1)
        direct=delta in STEPS or tuple(-np.array(delta)) in STEPS
        if not direct:continue
        if delta in STEPS:s,t,d=a,b,delta
        else:s,t,d=b,a,tuple(-np.array(delta))
        p=np.array(op[s]['xy']);q=np.array(op[t]['xy']);v=q-p;length=np.linalg.norm(v)
        nearby=[]
        for o in obs:
            if o['id'] in (s,t):continue
            z=np.array(o['xy'])-p;fraction=float(z@v/(v@v))
            if .2<fraction<.8 and np.linalg.norm(z-fraction*v)<7:nearby.append(o['id'])
        pts=np.linspace(p,q,31)-CROP[:2];vals=base.sample(data['rgb'].max(2),pts)
        fg=float(base.sample(data['fg'].astype(float),pts).mean())
        separator=float(np.min(vals[8:23])/(.5*(vals[:5].mean()+vals[-5:].mean())+1e-8))
        row=dict(source=s,target=t,family=STEPS[d],delta_ab=list(d),
            supporting_windows=win,competing_windows=len(disagreement_windows),consensus=agree_ratio,
            alternatives=[dict(delta_ab=list(dd),window_states=vv) for dd,vv in versions.items()],
            intervening_observations=nearby,foreground_fraction=fg,separator_brightness_ratio=separator,
            location_warning='Bright supports are not bead centers; separator is descriptive, not an acceptance gate.',
            priority='interior' if min(op[s]['band_clearance_px'],op[t]['band_clearance_px'])>=18 else 'edge')
        accept=win>=CONFIG['minimum_edge_windows'] and agree_ratio>=CONFIG['edge_consensus'] and not nearby and fg>.95
        row['status']='accepted conditional' if accept else 'unresolved continuation'
        row['reasons']=[]
        if win<2:row['reasons'].append('fewer than two overlapping observation-supported windows')
        if agree_ratio<CONFIG['edge_consensus']:row['reasons'].append('competing row assignment across joint hypotheses')
        if nearby:row['reasons'].append('potential intervening observed bead; skip unresolved')
        if fg<=.95:row['reasons'].append('segment approaches background/silhouette')
        (edges if accept else uncertain).append(row)
    # Propagate links while refusing inconsistent integer cycles. Evidence order
    # matters and is explicit; a zero cycle residual is never a photo certificate.
    edges.sort(key=lambda e:(-e['supporting_windows'],-e['consensus'],e['source'],e['target']))
    adjacency=defaultdict(list);accepted=[];conflicts=[]
    def relative(start,target):
        todo=[start];seen={start:np.zeros(2,int)}
        while todo:
            x=todo.pop()
            if x==target:return seen[x]
            for y,d in adjacency[x]:
                if y not in seen:seen[y]=seen[x]+d;todo.append(y)
        return None
    for e in edges:
        s,t=e['source'],e['target'];d=np.array(e['delta_ab']);existing=relative(s,t)
        if existing is not None and not np.array_equal(existing,d):
            e['status']='unresolved cycle conflict';e['reasons'].append('independent local proposals contradict propagated coordinates');conflicts.append(e);uncertain.append(e)
        else:adjacency[s].append((t,d));adjacency[t].append((s,-d));accepted.append(e)
    coords={};components=[]
    for start in sorted(op):
        if start in coords or not adjacency[start]:continue
        ci=len(components);coords[start]=(ci,np.zeros(2,int));todo=[start];group=[]
        while todo:
            s=todo.pop();group.append(s)
            for t,d in adjacency[s]:
                if t not in coords:coords[t]=(ci,coords[s][1]+d);todo.append(t)
        components.append(dict(id=ci,origin=start,nodes=sorted(group)))
    nodes=[]
    for o in obs:
        oid=o['id'];n=dict(id=oid,observation=oid,xy=o['xy'],color=o['color'],
            region_priority='interior' if o['band_clearance_px']>=18 else 'edge',band_clearance_px=o['band_clearance_px'],
            status='ambiguous or unresolved',relative_ab=None,conditional_indices=None,component=None,track_ids=[],
            index_status='unresolved; no single global origin across disconnected components')
        if oid in coords:
            ci,ab=coords[oid];a,b=map(int,ab);n.update(component=ci,relative_ab=[a,b],ab=[a,b],
                conditional_indices=dict(A=7*a+6*b,B=6*a+7*b,reverse_A=-7*a-6*b,reverse_B=-6*a-7*b),
                status='confident bead' if o['band_clearance_px']>=18 else 'probable bead',
                index_status='conditional component-relative topology; not externally certified')
        nodes.append(n)
    # Each fragment is an actual connected chain of accepted family edges.
    tracks=[]
    for family in ('F0','F1'):
        adj=defaultdict(set)
        for e in accepted:
            if e['family']==family:adj[e['source']].add(e['target']);adj[e['target']].add(e['source'])
        seen=set()
        for start in sorted(adj):
            if start in seen:continue
            todo=[start];group=[]
            while todo:
                s=todo.pop()
                if s in seen:continue
                seen.add(s);group.append(s);todo+=sorted(adj[s]-seen)
            group.sort(key=lambda s:coords[s][1][0 if family=='F0' else 1])
            tid=f'{family}-{sum(t["family"]==int(family[-1]) for t in tracks)+1:03}'
            tracks.append(dict(id=tid,family=int(family[-1]),observations=group,points=[op[s]['xy'] for s in group],
                status='observation-supported conditional chain; polyline anchors are not centers'))
            for n in nodes:
                if n['id'] in group:n['track_ids'].append(tid)
    return nodes,dict(edges=accepted,unresolved_edges=uncertain,components=components,conflicts=conflicts,
        cycle_rank=len(accepted)-len(coords)+len(components),
        warning='Photographic consistency is heuristic; overlapping windows are correlated. Cycle closure is not independent evidence.'),tracks,selected

def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);timings={};t=time.perf_counter()
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');data=base.preprocess(image,CROP)
    base.CROP=CROP
    obs,pixels=base.observations(data)
    timings['preprocessing_and_observations']=time.perf_counter()-t;t=time.perf_counter()
    windows=[];rng=np.random.default_rng(CONFIG['seed']);spectral_seconds=0.;candidate_seconds=0.
    for cx in range(CROP[0]+70,CROP[2]-40,CONFIG['window_stride']):
        xx=cx-CROP[0];ys=np.flatnonzero(data['fg'][:,max(0,xx-8):xx+9].any(1))
        if not len(ys):continue
        cy=int(np.median(ys))+CROP[1];crop=(max(CROP[0],cx-100),max(CROP[1],cy-100),min(CROP[2],cx+100),min(CROP[3],cy+100))
        local=[o for o in obs if crop[0]+8<=o['xy'][0]<crop[2]-8 and crop[1]+8<=o['xy'][1]<crop[3]-8 and o['band_clearance_px']>=10]
        w=dict(id=len(windows),crop=crop,observation_ids=[o['id'] for o in local],hypotheses=[])
        windows.append(w)
        if len(local)<CONFIG['minimum_window_observations']:w['stop']='insufficient visible support';continue
        st=time.perf_counter()
        try:ks,spectral=base.directions(base.preprocess(image,crop));B0=np.linalg.inv(ks)[:,::-1];w['spectral']=spectral
        except ValueError as ex:w['stop']=str(ex);continue
        spectral_seconds+=time.perf_counter()-st;st=time.perf_counter()
        xy=np.array([o['xy'] for o in local]);sigma=np.array([8. if o['color']=='black' else 5. for o in local]);weight=np.array([1. if o['band_clearance_px']>=18 else .55 for o in local])
        hs,seeds,count=fit_hypotheses(xy,sigma,weight,B0,w['observation_ids'],rng)
        w.update(hypotheses=hs,seed_basis=B0.tolist(),seed_count=seeds,distinct_hypotheses=count)
        candidate_seconds+=time.perf_counter()-st
    timings['spectral_analysis']=spectral_seconds;timings['local_diagonal_candidate_generation']=candidate_seconds
    t=time.perf_counter();beam=joint_select(windows);timings['joint_track_selection']=time.perf_counter()-t
    t=time.perf_counter();nodes,g,tracks,selected=infer_graph(obs,windows,beam,data);timings['row_checks_intersections_association_indexing_graph']=time.perf_counter()-t
    summary=dict(observations=len(obs),windows=len(windows),diagonal_fragments=[sum(t['family']==f for t in tracks) for f in (0,1)],
        status=dict(Counter(n['status'] for n in nodes)),colors=dict(Counter(n['color'] for n in nodes if n['component'] is not None)),
        accepted_links=len(g['edges']),unresolved_links=len(g['unresolved_edges']),components=[len(c['nodes']) for c in g['components']],
        conflicting_cycle_proposals=len(g['conflicts']),competing_row_connections=sum('competing row assignment across joint hypotheses' in e['reasons'] for e in g['unresolved_edges']),
        independent_photographic_check_types=['multi-observation two-family fit','shared-observation relative-coordinate overlap','intervening observed support','foreground support'],
        independent_ground_truth_checks_outside_R161=0)
    doc=dict(schema='r323-joint-image-lattice-v1',created_utc=utc(),configuration=CONFIG,summary=summary,
        observations=obs,intersections=nodes,tracks=tracks,graph=g,windows=windows,joint_beam=beam,selected_window_states=selected,
        timings_seconds=timings,image_sha256=sha(ROOT/'beads-photo-2.jpg'),source_sha256=sha(__file__),
        inherited_source_sha256=sha(base.__file__),appearance_catalog_sha256=sha(ROOT/'photo2/review/r275/inventory.json'),
        provenance='Original RGB + R275 bright pixels/colors only. No R161/R322 graph or 3D positions read. Shared supports reconcile windows; no arbitrary phase-reset labels.',
        limitations=['No calibrated confidence probability','Observation positions are not centers','No complete visible-body segmentation','Overlapping windows are correlated','Component origins independent','No claimed generality across photographs or palettes'])
    save(output/'graph.json',doc);save(output/'observation-pixels.json',pixels)
    np.savez_compressed(output/'fields.npz',foreground=data['fg'],clearance=data['clearance'])
    print(json.dumps(dict(summary=summary,timings=timings),indent=2));return doc
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/r323/results');args=ap.parse_args();run(args.output)

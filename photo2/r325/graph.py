"""Photographic edge evidence after joint cyclic selection; no chart gate."""
from collections import defaultdict,Counter
import time
import numpy as np
from scipy.spatial import cKDTree
from photo2.r323 import tracker as joint
from photo2.r322 import tracker as base
from .consistency import synchronize
def infer_graph(obs,windows,selected,data,stations,period):
    tree=cKDTree(np.array([o["xy"] for o in obs]))
    foreground_float=data['fg'].astype(float)
    stage_start=time.perf_counter();stage_times={}
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
    stage_times['joint_candidate_pair_votes']=time.perf_counter()-stage_start;stage_start=time.perf_counter()
    op={o['id']:o for o in obs};edges=[];uncertain=[];checks=[]
    for (a,b),versions in sorted(votes.items()):
        totals={d:len({wi for wi,hi in v}) for d,v in versions.items()}
        delta=max(totals,key=totals.get);win=totals[delta];allwindows=len({wi for v in versions.values() for wi,hi in v})
        disagreement_windows={wi for d,v in versions.items() if d!=delta for wi,hi in v}
        agree_ratio=1-len(disagreement_windows)/max(allwindows,1)
        direct=delta in joint.STEPS or tuple(-np.array(delta)) in joint.STEPS
        if not direct:continue
        if delta in joint.STEPS:s,t,d=a,b,delta
        else:s,t,d=b,a,tuple(-np.array(delta))
        p=np.array(op[s]['xy']);q=np.array(op[t]['xy']);v=q-p;length=np.linalg.norm(v)
        nearby=[]
        for oi in tree.query_ball_point((p+q)/2,length/2+7):
            o=obs[oi]
            if o['id'] in (s,t):continue
            z=np.array(o['xy'])-p;fraction=float(z@v/(v@v))
            if .2<fraction<.8 and np.linalg.norm(z-fraction*v)<7:nearby.append(o['id'])
        pts=np.linspace(p,q,31);vals=base.sample(data['v'],pts)
        fg=float(base.sample(foreground_float,pts).mean())
        separator=float(np.min(vals[8:23])/(.5*(vals[:5].mean()+vals[-5:].mean())+1e-8))
        row=dict(source=s,target=t,family=joint.STEPS[d],delta_ab=list(d),
            supporting_windows=win,competing_windows=len(disagreement_windows),consensus=agree_ratio,
            alternatives=[dict(delta_ab=list(dd),window_states=vv) for dd,vv in versions.items()],
            intervening_observations=nearby,foreground_fraction=fg,separator_brightness_ratio=separator,
            location_warning='Bright supports are not bead centers; separator is descriptive, not an acceptance gate.',
            priority='interior' if min(op[s]['band_clearance_px'],op[t]['band_clearance_px'])>=18 else 'edge')
        accept=win>=joint.CONFIG['minimum_edge_windows'] and agree_ratio>=joint.CONFIG['edge_consensus'] and not nearby and fg>.95
        row['status']='accepted conditional' if accept else 'unresolved continuation'
        row['reasons']=[]
        if win<2:row['reasons'].append('fewer than two overlapping observation-supported windows')
        if agree_ratio<joint.CONFIG['edge_consensus']:row['reasons'].append('competing row assignment across joint hypotheses')
        if nearby:row['reasons'].append('potential intervening observed bead; skip unresolved')
        if fg<=.95:row['reasons'].append('segment approaches background/silhouette')
        (edges if accept else uncertain).append(row)
    stage_times['row_switch_skip_and_photographic_checks']=time.perf_counter()-stage_start;stage_start=time.perf_counter()
    accepted,conflicts,coords,components,closure=synchronize(edges,obs,stations,period)
    uncertain.extend(conflicts)
    stage_times['graph_validation_and_coordinate_propagation']=time.perf_counter()-stage_start;stage_start=time.perf_counter()
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
                index_status='conditional globally selected topology; component gauge and winding remain explicit')
        evidence=[]
        for wi,choices in enumerate(selected):
            for hi in choices:
                a=windows[wi]['hypotheses'][hi]['assignments'].get(oid)
                if a is not None:evidence.append(dict(window=wi,hypothesis=hi,**a))
        n['local_hypothesis_evidence']=evidence
        n['representative_location_uncertainty_px']=8 if o['color']=='black' else 5
        n['uncertainty_kind']='exploratory bright-support sigma, not calibrated bead-center confidence interval'
        if evidence:
            reps=np.array([a['predicted_xy'] for a in evidence]);n['representative_xy']=np.median(reps,axis=0).tolist()
            n['representative_spread_px']=float(np.linalg.norm(reps-n['representative_xy'],axis=1).max())
        else:n['representative_xy']=None;n['representative_spread_px']=None
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
    stage_times['supported_intersections_association_indexing_and_fragments']=time.perf_counter()-stage_start
    return nodes,dict(stage_timings_seconds=stage_times,edges=accepted,unresolved_edges=uncertain,components=components,conflicts=conflicts,
        cycle_rank=len(accepted)-len(coords)+len(components),
        closure=closure,warning='Photographic consistency is heuristic; overlapping windows are correlated. Cycle closure is not independent evidence.'),tracks,selected

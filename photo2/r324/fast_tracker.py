"""Full-circuit original-photo joint lattices in transported tangent frames.
No physical model, maker graph, or fitted center enters detection.
"""
import json,time,resource,copy,argparse
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r323 import tracker as joint
from photo2.r322 import tracker as base
from photo2.fft_dense import curve_samples
ROOT=joint.ROOT;OUT=ROOT/'photo2/r324/results';save=joint.save

# The only chart transformations accepted here are integer translations in a
# continuously transported oriented frame. Other D6 alternatives are diagnosed,
# never silently applied to repair an incompatible chart.
def rotations():
    S={(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)};out=[]
    for a in S:
        for b in S:
            M=np.array([a,b]).T
            if abs(round(np.linalg.det(M)))==1 and tuple(M@np.array([1,-1])) in S:out.append(M)
    return out

def preprocess(image):
    rgb=np.asarray(image,float)/255;r,g,b=rgb.transpose(2,0,1);v=rgb.max(2)
    fg=((r>1.5*b)&(r>.13))|(v<.30);fg=ndi.binary_closing(fg,iterations=5)
    lab,_=ndi.label(~fg);sizes=np.bincount(lab.ravel());small=sizes<600;small[0]=False
    fg|=small[lab] # fill bead-scale holes, never fill the necklace's central paper
    lab,_=ndi.label(fg);sizes=np.bincount(lab.ravel());sizes[0]=0;fg=lab==sizes.argmax()
    z=np.log(.05+v);z-=ndi.gaussian_filter(z,8);z/=np.sqrt(ndi.gaussian_filter(z*z,16)+.03)
    return dict(rgb=rgb,fg=fg,clearance=ndi.distance_transform_edt(fg),z=z,v=v)

def run(out=OUT):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();tm={}
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');data=preprocess(image)
    tm['decode_preprocess']=time.perf_counter()-start;t=time.perf_counter()
    base.CROP=(0,0,*image.size);joint.CROP=base.CROP
    old_sha=base.sha
    cached_catalog=old_sha(ROOT/'photo2/review/r275/inventory.json')
    base.sha=lambda p:cached_catalog if Path(p)==ROOT/'photo2/review/r275/inventory.json' else old_sha(p)
    obs,pixels=base.observations(data);base.sha=old_sha;tm['observations']=time.perf_counter()-t
    xyall=np.array([o['xy'] for o in obs]);tree=cKDTree(xyall)
    length,guide=curve_samples(2000);gxy=np.array([[r['x'],r['y']] for r in guide]);gtree=cKDTree(gxy)
    # Start near old reference so its local component can be checked before seam.
    origin=int(gtree.query([1000,365])[1]);guide=guide[origin:]+guide[:origin]
    if guide[1]['x']<guide[0]['x']:guide=[guide[0]]+guide[:0:-1]
    ordered=np.array([[r['x'],r['y']] for r in guide]);tang=np.roll(ordered,-1,axis=0)-np.roll(ordered,1,axis=0);tang/=np.linalg.norm(tang,axis=1)[:,None]
    clearance=base.sample(data['clearance'],ordered)
    save(out/'guide.json',dict(length_px=length,samples=guide,centerline_clearance_px=clearance.tolist(),policy='R250 image spline, geography only; no bead identities',origin=origin))
    picks=[];s=0.
    while s<length:
        j=int(s/length*2000)%2000;picks.append(j)
        # More overlap at bends and requested uncertain upper bridge.
        x,y=ordered[j];step=35 if abs(guide[j]['curvature'])>.0018 or (1500<x<1800 and y<500) else 60
        s+=step
    rng=np.random.default_rng(324);wins=[];spectral=0.;fit=0.;grid=np.indices((200,200))[::-1].reshape(2,-1).T-99.5
    for wi,j in enumerate(picks):
        cen=ordered[j];tangent=tang[j];R=np.column_stack([tangent,[-tangent[1],tangent[0]]]);near=tree.query_ball_point(cen,142)
        ii=[i for i in sorted(near) if np.max(abs((xyall[i]-cen)@R))<92 and obs[i]['band_clearance_px']>=10]
        w=dict(id=wi,center=cen.tolist(),frame=R.tolist(),guide_index=j,arc_px=j*length/2000,curvature=guide[j]['curvature'],observation_ids=[obs[i]['id'] for i in ii],hypotheses=[])
        wins.append(w)
        if len(ii)<8:w['stop']='insufficient observed supports';continue
        pts=grid@R.T+cen;st=time.perf_counter()
        patch={k:base.sample(data[k],pts).reshape(200,200) for k in ['z','fg']};patch['fg']=patch['fg']>.5;patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(200)[None,:]
        try:ks,spec=base.directions(patch)
        except ValueError as ex:w['stop']=str(ex);continue
        spectral+=time.perf_counter()-st;st=time.perf_counter();bases=[]
        for tri in spec['triangles']:
            bb=np.linalg.inv(np.array([spec['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
            if any(np.linalg.norm(bb-b)<4 for b in bases):continue
            bases.append(bb)
            if len(bases)>=10:break
        local=(xyall[ii]-cen)@R;sig=np.array([8 if obs[i]['color']=='black' else 5 for i in ii]);wt=np.array([1 if obs[i]['band_clearance_px']>=18 else .55 for i in ii]);allhs=[]
        for bb in bases:
            hh,_,_=joint.fit_hypotheses(local,sig,wt,bb,w['observation_ids'],rng);allhs+=hh
        unique={}
        for h in sorted(allhs,key=lambda h:-h['score']):
            a=h['assignments'];first=a[sorted(a)[0]]['ab'];signature=tuple((oid,*map(int,np.array(a[oid]['ab'])-first)) for oid in sorted(a))
            if signature in unique:continue
            h['basis_local']=h['basis'];h['offset_local']=h['offset'];h['basis']=(R@np.array(h['basis'])).tolist();h['offset']=(R@h['offset']+cen).tolist()
            for a in h['assignments'].values():a['predicted_xy']=(R@a['predicted_xy']+cen).tolist()
            unique[signature]=h
        w.update(hypotheses=list(unique.values())[:6],spectral=spec,competing_bases_local=[b.tolist() for b in bases]);fit+=time.perf_counter()-st
        if wi%25==0:print('window',wi,'/',len(picks),'observations',len(ii),'elapsed',round(time.perf_counter()-start,2),flush=True)
    tm.update(spectral=spectral,joint_candidates=fit);t=time.perf_counter()
    # Bounded global beam; credible means within three score units among the
    # retained 48 paths, not all mathematically possible histories.
    beam=joint.joint_select(wins);selected=[sorted({b['choices'][wi] for b in beam if b['score']>=beam[0]['score']-3 and b['choices'][wi] is not None}) for wi in range(len(wins))]
    transitions=[];chart=0
    for wi in range(len(wins)):
        prev=(wi-1)%len(wins);checks=[]
        for a in selected[prev]:
            for b in selected[wi]:
                h,k=wins[prev]['hypotheses'][a],wins[wi]['hypotheses'][b];v=joint.overlap(h,k)
                checks.append(dict(previous=a,current=b,**v))
        good=bool(checks and all(c['common']>=4 and c['disagree']==0 for c in checks))
        if wi and not good:chart+=1
        wins[wi]['chart']=chart
        transforms=[]
        if checks and not good:
            h=wins[prev]['hypotheses'][selected[prev][0]];k=wins[wi]['hypotheses'][selected[wi][0]];common=sorted(set(h['assignments'])&set(k['assignments']))
            for M in rotations():
                if not common:continue
                shifts=[tuple(np.array(h['assignments'][o]['ab'])-M@k['assignments'][o]['ab']) for o in common];shift,count=Counter(shifts).most_common(1)[0]
                transforms.append(dict(matrix=M.tolist(),translation=list(shift),agree=count,common=len(common)))
        transitions.append(dict(previous=prev,current=wi,translation_consistent=good,checks=checks,triangular_lattice_alternatives=transforms,status='conditional overlap' if good else 'unresolved chart boundary',seam=wi==0))
    owners={o['id']:wins[int(np.argmin(np.linalg.norm(np.array([w['center'] for w in wins])-o['xy'],axis=1)))]['chart'] for o in obs}
    tm['beam_transport']=time.perf_counter()-t;t=time.perf_counter()
    # Fast inference adapter below retains the R323 gates, uses precomputed V,
    # KD-tree corridors, and refuses cross-boundary propagation.
    nodes,g,tracks,selected=infer_graph(obs,wins,beam,data,owners)
    tm.update(g['stage_timings_seconds']);tm['graph_total']=time.perf_counter()-t
    for n in nodes:n['geographic_chart']=owners[n['id']]
    coverage=[]
    for section in range(16):
        ws=[w for w in wins if int(w['arc_px']/length*16)==section];ids={o for w in ws for o in w['observation_ids']};ns=[n for n in nodes if n['id'] in ids]
        coverage.append(dict(section=section,arc_interval=[section*length/16,(section+1)*length/16],windows=len(ws),successful_windows=sum(bool(w['hypotheses']) for w in ws),observations=len(ids),indexed=sum(n['component'] is not None for n in ns),interior=sum(n['region_priority']=='interior' for n in ns)))
    summary=dict(observations=len(obs),windows=len(wins),successful_windows=sum(bool(w['hypotheses']) for w in wins),indexed=sum(n['component'] is not None for n in nodes),status=dict(Counter(n['status'] for n in nodes)),accepted_links=len(g['edges']),unresolved_links=len(g['unresolved_edges']),components=[len(c['nodes']) for c in g['components']],fragments=len(tracks),chart_breaks=sum(not t['translation_consistent'] for t in transitions),full_loop_closure=False)
    tm['total_before_serialization']=time.perf_counter()-start
    doc=dict(schema='r324-full-circuit-v1',summary=summary,observations=obs,intersections=nodes,graph=g,tracks=tracks,windows=wins,joint_beam=beam,selected_window_states=selected,transitions=transitions,coverage=coverage,timings_seconds=tm,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,image_sha256=joint.sha(ROOT/'beads-photo-2.jpg'),source_sha256=joint.sha(__file__),provenance='Original RGB, R275 appearance supports, R250 geographic spline only; no 3D or maker runtime data',closure='Not established; component origins independent; 6/7 assignment and both global reversals retained',configuration=dict(joint.CONFIG,adaptive_stride=[35,60],full_image=list(image.size)))
    save(out/'graph.json',doc);save(out/'observation-pixels.json',pixels);save(out/'coverage.json',coverage);save(out/'performance.json',dict(stages=tm,peak_rss_mb=doc['peak_rss_mb'],seconds_per_window=tm['total_before_serialization']/len(wins),seconds_per_observation=tm['total_before_serialization']/len(obs),image_decodes=1,global_preprocesses=1,spatial_index=True))
    print(json.dumps(summary),flush=True);return doc

def infer_graph(obs,windows,beam,data,owners):
    tree=cKDTree(np.array([o["xy"] for o in obs]))
    foreground_float=data['fg'].astype(float)
    stage_start=time.perf_counter();stage_times={}
    near=[b for b in beam if b['score']>=beam[0]['score']-joint.CONFIG['beam_score_allowance']]
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
        accept=owners[s]==owners[t] and win>=joint.CONFIG['minimum_edge_windows'] and agree_ratio>=joint.CONFIG['edge_consensus'] and not nearby and fg>.95
        row['status']='accepted conditional' if accept else 'unresolved continuation'
        row['reasons']=[]
        if owners[s]!=owners[t]:row['reasons'].append('unresolved transported chart boundary; no index propagation')
        if win<2:row['reasons'].append('fewer than two overlapping observation-supported windows')
        if agree_ratio<joint.CONFIG['edge_consensus']:row['reasons'].append('competing row assignment across joint hypotheses')
        if nearby:row['reasons'].append('potential intervening observed bead; skip unresolved')
        if fg<=.95:row['reasons'].append('segment approaches background/silhouette')
        (edges if accept else uncertain).append(row)
    stage_times['row_switch_skip_and_photographic_checks']=time.perf_counter()-stage_start;stage_start=time.perf_counter()
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
                index_status='conditional component-relative topology; not externally certified')
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
        warning='Photographic consistency is heuristic; overlapping windows are correlated. Cycle closure is not independent evidence.'),tracks,selected

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='/tmp/r324-fast');run(ap.parse_args().output)

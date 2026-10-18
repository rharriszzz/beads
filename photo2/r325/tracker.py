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
from .batched_fit import fit_hypotheses
from .spectral import directions
from .observations import observations
from .global_solver import solve
from .candidates import augment,inspect_black_predictions
from .graph import infer_graph
ROOT=joint.ROOT;OUT=ROOT/'photo2/r325/results';save=joint.save

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
    obs,pixels=observations(data);base.sha=old_sha;tm['observations']=time.perf_counter()-t
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
        try:ks,spec=directions(patch)
        except ValueError as ex:w['stop']=str(ex);continue
        spectral+=time.perf_counter()-st;st=time.perf_counter();bases=[]
        for tri in spec['triangles']:
            bb=np.linalg.inv(np.array([spec['peaks'][k]['frequency_xy'] for k in tri['peaks'][:2]]))[:,::-1]
            if any(np.linalg.norm(bb-b)<4 for b in bases):continue
            bases.append(bb)
            if len(bases)>=10:break
        local=(xyall[ii]-cen)@R;sig=np.array([8 if obs[i]['color']=='black' else 5 for i in ii]);wt=np.array([1 if obs[i]['band_clearance_px']>=18 else .55 for i in ii]);allhs=[]
        for bb in bases:
            hh,_,_=fit_hypotheses(local,sig,wt,bb,w['observation_ids'],rng);allhs+=hh
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
    predictions,augmentation=augment(wins,obs,data)
    tm['colored_and_bidirectional_candidates']=time.perf_counter()-t;t=time.perf_counter()
    black=inspect_black_predictions(predictions,obs,data)
    tm['black_neighborhood_inspection']=time.perf_counter()-t;t=time.perf_counter()
    solution=solve(wins,cyclic=True)
    tm['global_cyclic_optimization']=time.perf_counter()-t;t=time.perf_counter()
    # Station is geographic, independent of every inferred lattice identity.
    guide_tree=cKDTree(ordered)
    stations={o['id']:float(guide_tree.query(o['xy'])[1])*length/2000 for o in obs}
    nodes,g,tracks,selected=infer_graph(obs,wins,solution['selected'],data,stations,length)
    tm.update(g['stage_timings_seconds']);tm['graph_total']=time.perf_counter()-t
    transitions=[]
    for wi in range(len(wins)):
        prev=(wi-1)%len(wins);checks=[]
        for a in selected[prev]:
            for b in selected[wi]:
                checks.append(dict(previous=a,current=b,**joint.overlap(wins[prev]['hypotheses'][a],wins[wi]['hypotheses'][b])))
        good=bool(checks and all(c['common']>=4 and c['disagree']==0 for c in checks))
        transitions.append(dict(previous=prev,current=wi,translation_consistent=good,checks=checks,
            status='conditional global overlap' if good else 'ambiguous global overlap; never a geographic barrier',seam=wi==0))
    indexed={n['id'] for n in nodes if n['component'] is not None}
    black['indexed_black_with_colored_prediction']=[r for r in black['black_supports_predicted_by_colored_only'] if r['observation'] in indexed]
    coverage=[]
    for section in range(16):
        ws=[w for w in wins if int(w['arc_px']/length*16)==section];ids={o for w in ws for o in w['observation_ids']};ns=[n for n in nodes if n['id'] in ids]
        coverage.append(dict(section=section,arc_interval=[section*length/16,(section+1)*length/16],windows=len(ws),successful_windows=sum(bool(w['hypotheses']) for w in ws),observations=len(ids),indexed=sum(n['component'] is not None for n in ns),interior=sum(n['region_priority']=='interior' for n in ns)))
    summary=dict(observations=len(obs),windows=len(wins),successful_windows=sum(bool(w['hypotheses']) for w in wins),indexed=sum(n['component'] is not None for n in nodes),status=dict(Counter(n['status'] for n in nodes)),accepted_links=len(g['edges']),unresolved_links=len(g['unresolved_edges']),components=[len(c['nodes']) for c in g['components']],fragments=len(tracks),ambiguous_transitions=sum(not t['translation_consistent'] for t in transitions),full_loop_closure=g['closure']['identified'],black_colored_supported=len(black['indexed_black_with_colored_prediction']))
    tm['total_before_serialization']=time.perf_counter()-start
    doc=dict(schema='r325-global-cyclic-v1',summary=summary,observations=obs,intersections=nodes,graph=g,tracks=tracks,windows=wins,global_solution=solution,selected_window_states=selected,transitions=transitions,coverage=coverage,timings_seconds=tm,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,image_sha256=joint.sha(ROOT/'beads-photo-2.jpg'),source_sha256=joint.sha(__file__),provenance='Original RGB, R275 appearance supports, R250 geographic spline only; no 3D or maker runtime data',closure=g['closure'],stations_px=stations,period_px=length,candidate_augmentation=augmentation,configuration=dict(joint.CONFIG,crop=[0,0,*image.size],adaptive_stride=[35,60],full_image=list(image.size),maximum_augmented_candidates=10,cyclic_memory=2,global_score_allowance=3.0))
    serialization_start=time.perf_counter()
    save(out/'graph.json',doc);save(out/'observation-pixels.json',pixels);save(out/'coverage.json',coverage);save(out/'performance.json',dict(stages=tm,peak_rss_mb=doc['peak_rss_mb'],seconds_per_window=tm['total_before_serialization']/len(wins),seconds_per_observation=tm['total_before_serialization']/len(obs),image_decodes=1,global_preprocesses=1,spatial_index=True))
    save(out/'colored-first.json',black);tm['output_serialization']=time.perf_counter()-serialization_start
    save(out/'performance.json',dict(stages=tm,peak_rss_mb=doc['peak_rss_mb'],total_measured_seconds=time.perf_counter()-start))
    print(json.dumps(summary),flush=True);return doc


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=OUT);run(ap.parse_args().output)

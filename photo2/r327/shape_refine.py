"""Native shared-shape metric distinguishes affine-equivalent neighbor shears.
Visible pigment regions are shape proxies, never complete contours. All colors
use one local metric. No maker label, expected count or fitted model is read.
"""
import argparse,copy,hashlib,math,shutil,time
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageOps
from photo2.r325.global_solver import solve
from photo2.r325.tracker import preprocess
from photo2.r325.graph import infer_graph
from .compatibility import relations,cycle_audit
from .continue_run import graph_for
from .select_working import working_objective
from .runner import ROOT,OUT,OLD,read,save,change_ledger
ARCHIVE=ROOT/'photo2/r327/development/before-shape'
DIRECTIONS=[(a,b) for a in range(-2,3) for b in range(-2,3) if (a>0 or (a==0 and b>0)) and math.gcd(abs(a),abs(b))==1]

def pigment_regions(obs,rgb):
    regions=[]
    for o in obs:
        if o['color']=='black':continue
        x,y=np.rint(o['xy']).astype(int);x0,y0=x-19,y-19;patch=rgb[y0:y+20,x0:x+20];yy,xx=np.indices(patch.shape[:2]);r,gg,b=patch.transpose(2,0,1);pigment=((r>1.8*gg)&(r>2.5*b)) if o['color']=='red' else ((gg>.45*r)&(gg>1.8*b)&(r>.9*gg));mask=pigment&(r>.16)&((xx-19)**2+(yy-19)**2<=19**2);labels,_=ndi.label(mask);k=labels[19,19]
        if not k:
            py,px=np.where(mask)
            if not len(px):continue
            dist=(px-19)**2+(py-19)**2;j=int(np.argmin(dist))
            if dist[j]>49:continue
            k=labels[py[j],px[j]]
        py,px=np.where(labels==k)
        if len(px)<20:continue
        pts=np.column_stack([px+x0,py+y0]);regions.append(dict(observation=o['id'],xy=o['xy'],pixels_xy=pts.tolist(),color=o['color'],covariance_px2=np.cov(pts.T).tolist()))
    return regions

def metric(w,regions):
    local=[r for r in regions if np.linalg.norm(np.array(r['xy'])-w['center'])<100]
    if len(local)<3:return np.eye(2)*49,[],False
    cov=np.median([r['covariance_px2'] for r in local],axis=0);ev,E=np.linalg.eigh(cov);cov=(E*np.clip(ev,16,100))@E.T
    return cov,[r['observation'] for r in local],True

def reduction(B,cov,n):
    inv=np.linalg.inv(cov);lengths=[float(np.sqrt((B@d)@inv@(B@d))) for d in map(np.array,DIRECTIONS)];rank=sorted(zip(lengths,DIRECTIONS));third=rank[2][0];declared=[(1,0),(0,1),(1,-1)];actual=[float(np.sqrt((B@d)@inv@(B@d))) for d in map(np.array,declared)]
    # Penalize only directions longer than an observed-shape metric's third
    # shortest primitive direction; no target angle/equal-length/count imposed.
    penalty=n/3.*sum(max(0.,math.log(v/third)) for v in actual)
    return dict(penalty=penalty,declared_directions=declared,declared_metric_lengths=actual,three_shortest_primitive_directions=[dict(delta=list(d),length=l) for l,d in rank[:3]],third_shortest_length=third)

def main():
    start=time.perf_counter();g=read(ARCHIVE/'graph.json.gz');ws=g['windows'];obs=g['observations'];old=read(OLD/'graph.json');data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));regions=pigment_regions(obs,data['rgb']);metrics=[]
    for w in ws:
        cov,anchors,measured=metric(w,regions);metrics.append(dict(window=w['id'],covariance_px2=cov.tolist(),colored_region_anchors=anchors,measured=measured))
        for h in w['hypotheses']:
            h['pre_shape_score']=h['score'];ev=reduction(np.array(h['basis']),cov,len(h['assignments']));ev['measured_metric']=measured
            if not measured:ev['penalty']=0.
            h['r327_shared_shape']=ev;h['score']-=ev['penalty']
    sol=solve(ws);proposal=graph_for(g,ws,obs,data,sol);states=[('previous working primary',g['selected_window_states']),('shared-shape proposal',proposal['selected_window_states']),('R326',old['selected_window_states'])]
    for folder in (ROOT/'photo2/r327/development/cycle-prefix-run',ARCHIVE):
        for p in sorted(folder.glob('iteration-*.json.gz')):states.append((str(p.relative_to(ROOT)),read(p)['selected_window_states']))
    records=[];best=None
    for label,sels in states:
        c=[s[0] if s else None for s in sels];active,conflicts,ll=relations(ws,c,g['stations_px'],g['period_px']);bad,audit=cycle_audit(set(active),ll);assert not conflicts and not bad;score=working_objective(ws,sels);records.append(dict(configuration=label,score=score,holonomies=audit['possible_holonomies']))
        if best is None or score['total']>best[0]+1e-9:best=(score['total'],label,sels,audit)
    _,label,sels,audit=best;nodes,graph,tracks,_=infer_graph(obs,ws,sels,data,g['stations_px'],g['period_px']);assert not graph['conflicts']
    for n in nodes:n['status']='working indexed support' if n['component'] is not None else 'unindexed observed support'
    for e in graph['edges']:e['status']='working provisional link';e['independently_established']=False
    result=dict(g,intersections=nodes,graph=graph,tracks=tracks,selected_window_states=sels,global_solution=sol,compatibility=dict(selected_windows=[i for i,s in enumerate(sels) if s],abstained_windows=[i for i,s in enumerate(sels) if not s],cycle_audit=audit,policy='Best sampled compatible witness under native shared-shape corrected photographic objective'),incumbent_selection=dict(source=label,objective=working_objective(ws,sels),configurations_tested=len(records)),shape_refinement=dict(reason='Visual review exposed sheared neighbor directions despite equivalent coordinate fits',budget_seconds=120,proposal_compatibility=proposal['compatibility'],native_regions=len(regions),windows_with_measured_shape=sum(m['measured'] for m in metrics)))
    save(OUT/'shared-shape-evidence.json.gz',dict(regions=regions,window_metrics=metrics,policy='Visible colored pigment component covariance, radius19 crop and eigenvalue16..100 inherited from R326; explicit red/yellow chromaticity excludes pink paper and unlike neighboring pigment. Same local metric for every color. Shape proxy and shortest-direction preference are conditional geometry evidence, not complete contours or proof of contact.'))
    save(OUT/'shared-shape-selection.json',dict(records=records,selected=label,previous_primary_score=records[0]['score'],new_score=working_objective(ws,sels)));save(OUT/'shared-shape-changes.json.gz',change_ledger(g,result,ws));save(OUT/'graph.json.gz',result);save(OUT/'final-changes.json.gz',change_ledger(old,result,ws));perf=read(ARCHIVE/'performance.json');perf['shape_correction_seconds']=time.perf_counter()-start;perf['broad_mask_correction_seconds']=read(ROOT/'photo2/r327/development/broad-pigment-mask/performance.json')['shape_correction_seconds'];perf['all_refinement_seconds']=perf['refinement_plus_incumbent_seconds']+perf['broad_mask_correction_seconds']+perf['shape_correction_seconds'];save(OUT/'performance.json',perf)
    # Prior seal is preserved with the entire previous epoch. No R161 data enters
    # this correction; the historical reference was already exposed, as reported.
    seal={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'photo2/r327').glob('*.py'))};seal['graph_sha256']=hashlib.sha256((OUT/'graph.json.gz').read_bytes()).hexdigest();save(OUT/'scientific-seal.json',seal)
    print('SHAPE',label,'links',len(graph['edges']),'indexed',sum(n['component'] is not None for n in nodes),'H',audit['possible_holonomies'],'seconds',perf['shape_correction_seconds'],'scores',records[0]['score'],working_objective(ws,sels),flush=True)
if __name__=='__main__':main()

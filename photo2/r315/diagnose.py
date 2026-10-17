"""Fixed-photo ledger, true occluders, counterfactuals, camera and contact bounds."""
import time
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import paper,contacts
from photo2.r314.diagnostics import EARLY
from photo2.r295.geometry import AXES
from .model import Chain,refined_trace,subset
OUT=ROOT/'photo2/r315/results'
NAMES=['R306-2405','R313-focused-3','R312-local']

def brackets(e,tr):
    own=tr['owner'].reshape(e.shape);un=tr['unknown'].reshape(e.shape);rows=[];h,w=e.shape
    for bid,(y,x,axis,sign,gap) in enumerate(e.m['external_brackets']):
        y,x,axis,sign,gap=map(int,[y,x,axis,sign,gap]);dy,dx=(0,sign) if axis==0 else (sign,0)
        t=np.arange(-max(h,w),max(h,w));yy=y+t*dy;xx=x+t*dx;valid=(yy>=0)&(yy+dy>=0)&(yy<h)&(yy+dy<h)&(xx>=0)&(xx+dx>=0)&(xx<w)&(xx+dx<w);t,yy,xx=t[valid],yy[valid],xx[valid]
        good=(own[yy,xx]>=0)&(own[yy+dy,xx+dx]<0)&~un[yy,xx]&~un[yy+dy,xx+dx]
        excess=np.maximum(np.maximum(-t,t-(gap-1)),0);j=np.flatnonzero(good);best=j[np.argmin(excess[j])] if len(j) else None
        rows.append(dict(id=bid,material_endpoint=(e.m['origin']+[x,y]).tolist(),paper_endpoint=(e.m['origin']+[x+gap*dx,y+gap*dy]).tolist(),axis=axis,direction=sign,interval=[0,gap],split=int(e.m['split'][y,x]),strength=float(np.max(e.m['strength'][:,y,x])) if e.m['strength'].ndim==3 else float(e.m['strength'][y,x]),found=best is not None,displacement=None if best is None else float(excess[best]),signed_station=None if best is None else float(t[best]+.5),outside_old_scan=best is None or not(-12<=t[best]<gap+12),classification='missing_on_entire_raster_line' if best is None else ('inside_bracket' if excess[best]==0 else 'outside_bracket'),photographic_classification='fixed pigment/paper plus adjacent-row support; uncalibrated, no reclassification'))
    return rows

def contact_graph(s):
    cert=contacts(s,seconds=2);lookup={tuple(w['pair']):w for w in cert['witnesses']};target=set(np.flatnonzero((s.indices>=-100)&(s.indices<=99)));pairs={tuple(sorted([j,j+d])) for j in target for d in [1,6,7] if j+d<s.n};pairs|={p for p in lookup if p[0] in target or p[1] in target};rows=[]
    for a,b in sorted(pairs):
        d=s.centers[b]-s.centers[a];n=d/np.linalg.norm(d);w=lookup.get((a,b));n=np.array(w['normal']) if w else n
        def values(n):
            n=n/np.linalg.norm(n);ha,ga=s.support(n,s.g[AXES[0]][a],True);hb,gb=s.support(-n,s.g[AXES[0]][b],True);pa=s.centers[a]+ga;pb=s.centers[b]+gb
            return float(d@n-ha-hb),pa,pb
        lower,pa,pb=values(n);upper=float(np.linalg.norm(pb-pa));rows.append(dict(pair=[int(s.indices[a]),int(s.indices[b])],offset=int(s.indices[b]-s.indices[a]),minor_revolution=int(np.floor(s.indices[a]/6.5)),center_delta=d.tolist(),axis_angle_deg=float(np.degrees(np.arccos(np.clip(s.g[AXES[0]][a]@s.g[AXES[0]][b],-1,1)))),support_lower=lower,solid_surface_upper=upper,refined=False,certified=lower>1e-6,_a=a,_b=b,_n=n.tolist()))
    # Independently optimize closest support pair; primal points checked on actual solid.
    nearest=sorted(rows,key=lambda r:r['support_lower'])[:60]
    for r in nearest:
        a,b=r['_a'],r['_b'];delta=s.centers[b]-s.centers[a]
        def val(n):
            n=n/np.linalg.norm(n);ha,ga=s.support(n,s.g[AXES[0]][a],True);hb,gb=s.support(-n,s.g[AXES[0]][b],True);return float(delta@n-ha-hb),s.centers[a]+ga,s.centers[b]+gb
        opt=minimize(lambda n:-val(n)[0],r['_n'],method='BFGS',options={'gtol':1e-10,'maxiter':150});lo,pa,pb=val(opt.x)
        qa=np.array([(pa-s.centers[a])@s.g[k][a] for k in AXES]);qb=np.array([(pb-s.centers[b])@s.g[k][b] for k in AXES]);sd=max(abs(float(s.local_sdf(qa))),abs(float(s.local_sdf(qb))));hi=float(np.linalg.norm(pb-pa));r.update(refined=True,support_lower=lo,solid_surface_upper=hi,uncertainty_width=hi-lo,actual_surface_residual=sd,witness_points=[pa.tolist(),pb.tolist()],optimizer_success=bool(opt.success),certified=lo>1e-6)
    for r in rows:
        for k in ['_a','_b','_n']:r.pop(k)
    support=paper(s);z=np.tile([0.,0.,1.],(s.n,1));clear=s.centers[:,2]-s.support(z,s.g[AXES[0]])-support['plane_z']
    return dict(full_chain=cert,pairs=rows,paper=support,local_paper=[dict(index=int(s.indices[j]),clearance=float(clear[j])) for j in sorted(target)],policy='Support lower is not exact gap; actual-surface witness distance is upper. Refined primal/dual interval is tight only if width and SDF residual are small. No universal contact or equilibrium imposed.')

def main():
    began=time.monotonic();e=engine();data=load()[0];ledger=[];summary=[]
    previous=read(ROOT/'photo2/r314/results/geometry-diagnostics.json.gz');arc={r['id']:r['arc'] for r in previous['models'][0]['regions']}
    for name in NAMES:
        row=read(ROOT/f'photo2/r314/results/models/{name}.json.gz');s=Chain(row['parameters'],data);old=np.load(ROOT/f'photo2/r314/results/models/{name}.npz');tr={k:old[k].copy() for k in ['owner','unknown']};ix=np.flatnonzero(tr['unknown']);rr=refined_trace(s,e.xy[ix]);tr['owner'][ix]=rr['owner'];tr['unknown'][ix]=rr['unknown'];np.savez_compressed(OUT/f'{name}-raster.npz',**tr)
        unknown=dict(before=len(ix),after=int(rr['unknown'].sum()),pixels=e.xy[ix].tolist(),material=int(e.m['material'].ravel()[ix].sum()),paper=int(e.m['paper'].ravel()[ix].sum()),core=int((e.m['core'].ravel()[ix]>0).sum()),roi=int(e.m['roi'].ravel()[ix].sum()))
        metrics={key:e.measure(tr['owner'],tr['unknown'],s.indices,i,True) for i,key in enumerate(['development','comparison','buffer'])};bs=brackets(e,tr)
        save(OUT/f'{name}-brackets.json.gz',bs)
        for core in e.doc['regions']:
            if core['id'] not in EARLY:continue
            ix=np.flatnonzero(e.m['core'].ravel()==core['label']);xy=e.xy[ix];full=refined_trace(s,xy);candidates=s.tree.query_ball_point(core['point'],s.query_radius+20);cs=[]
            for j in candidates:
                iso=refined_trace(subset(s,[j]),xy);mask=(iso['owner']>=0)&~iso['unknown'];f=float(mask.mean())
                if f==0:continue
                vis=(full['owner']==j)&~full['unknown'];hidden=mask&~vis&(full['owner']>=0);ids,counts=np.unique(full['owner'][hidden],return_counts=True);oc=[]
                for jj,num in sorted(zip(ids,counts),key=lambda z:-z[1]):
                    sel=hidden&(full['owner']==jj);dif=full['depth'][sel]-iso['depth'][sel];cf=refined_trace(s,xy,remove=(int(s.indices[jj]),));oc.append(dict(index=int(s.indices[jj]),pixels=int(num),depth_difference_min=float(dif.min()),depth_difference_median=float(np.median(dif)),depth_difference_max=float(dif.max()),removed_candidate_visible_fraction=float(np.mean(cf['owner']==j)),counterfactual_only=True))
                cs.append(dict(index=int(s.indices[j]),isolated_fraction=f,visible_fraction=float(vis.mean()),occluders=oc,center=s.centers[j].tolist(),projected_center=s.pc[j].tolist(),axes={k:s.g[k][j].tolist() for k in AXES},neighbors=[dict(index=int(s.indices[j+d]),center=s.centers[j+d].tolist(),projected=s.pc[j+d].tolist()) for d in [1,6,7] if j+d<s.n]))
            cs.sort(key=lambda r:-r['isolated_fraction']);plausible=[r for r in cs if r['isolated_fraction']>=.8];bestvis=max([r['visible_fraction'] for r in cs],default=0)
            outcome='multiple_isolated_aliases' if len(plausible)>1 else ('plausible_isolated_hidden' if plausible and bestvis<.8 else ('no_80percent_isolated_explanation' if not plausible else 'surface_plausibly_explained'))
            ledger.append(dict(model=name,id=core['id'],point=core['point'],arc=arc[core['id']],color=core['color'],pixels=xy.tolist(),reliability='fixed eroded pigment core; correlated pixels; no complete contour or identity',candidates=cs,outcome=outcome,threshold=.8,alternative_assignment_explains_core=bestvis>=.8))
        summary.append(dict(name=name,parameters=row['parameters'],unknown=unknown,metrics=metrics,brackets=dict(count=len(bs),missing=sum(not b['found'] for b in bs),old_missing=sum(b['outside_old_scan'] for b in bs)),positions=dict(indices=s.indices.tolist(),centers=s.centers.tolist(),projected=s.pc.tolist())))
        print('diagnosed',name,unknown['before'],unknown['after'],flush=True)
        if name==NAMES[0]:save(OUT/'contacts.json.gz',contact_graph(s))
    save(OUT/'ledger.json.gz',ledger);save(OUT/'baseline-summary.json.gz',summary)
    save(OUT/'diagnosis-receipt.json',dict(seconds=time.monotonic()-began,evidence_sha=sha(ROOT/'photo2/r314/evidence/maps.npz'),model_names=NAMES))
if __name__=='__main__':main()

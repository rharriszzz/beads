"""Grouped native material evidence plus inexpensive silhouette/reflection search.

Coarse reflection raster is a proposal-ranking approximation. Native finalists
and frozen historical controls use identical exact first-hit definitions.
"""
from functools import lru_cache
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import linear_sum_assignment
from photo2.r297.geometry import reference
from photo2.r298.geometry import outlines, envelope, bead_extents
from photo2.r298.photometry import PhotoScore
from photo2.r299.forward import shade, light_params, highlight
from .geometry import FIELD

@lru_cache(maxsize=4)
def lattice(step):
    yy,xx=np.mgrid[0:3182:step,0:2540:step]; xy=np.c_[xx.ravel(),yy.ravel()]
    # Conservative strip for all permitted centerline offsets and rope extents.
    dist=cKDTree(reference().points).query(xy)[0]
    return xy[dist<150]

def predict(scene, step=3., observations=None, detail=False):
    xy=lattice(step)
    owners=np.arange(scene.n)
    if observations is not None:
        # Complete selected-body boxes, with the entire model still occluding.
        near=scene.tree.query_ball_point([r['point'] for r in observations],55.)
        owners=np.array(sorted({j for row in near for j in row}),int)
        if len(owners):
            d=cKDTree(scene.pc[owners]).query(xy)[0]; xy=xy[d<=scene.query_radius+1]
        else:xy=xy[:0]
    else:
        d=scene.tree.query(xy)[0];xy=xy[d<=scene.query_radius+1]
    light=light_params([scene.p['light_az'],scene.p['light_el'],scene.p.get('roughness',10.)], 'directional', scene.centers.mean(0))
    parts=[]; intensity=[]; unknown=0; shadow=0
    for start in range(0,len(xy),16000):
        tr=scene.camera(xy[start:start+16000]); sh=shade(scene,tr,light)
        parts.append(tr['owner']);intensity.append(sh['intensity']);unknown+=int(tr['unknown'].sum());shadow+=sh['unknown_shadow_pairs']
    owner=np.concatenate(parts) if parts else np.empty(0,int); w=np.concatenate(intensity) if intensity else np.empty(0)
    pred=[]
    for j in owners:
        keep=owner==j; h=highlight(xy[keep],w[keep],step)
        if h:pred.append(dict(index=int(scene.indices[j]),point=h['centroid'],peak=h['peak'],strength=h['peak_intensity'],area_px2=h['area_px2']))
    meta=dict(rays=len(xy),unknown_camera=unknown,unknown_shadow=shadow,step=step)
    if detail:meta.update(xy=xy,owner=owner,intensity=w)
    return pred,meta

def match(obs,pred,gap=24.,fixed=None):
    if not obs:return dict(loss=0.,rms=None,median=None,p90=None,matched=0,unmatched=0,ambiguous=0,records=[])
    points=np.array([p['point'] for p in pred]).reshape(-1,2)
    d=np.linalg.norm(np.array([o['point'] for o in obs])[:,None,:]-points[None],axis=2)
    # Unmatched observation costs full gap^2; no free skipped-observation reward.
    # Predictions may lack measured reflections and never imply missing bodies.
    cost=np.c_[d*d,np.full((len(obs),len(obs)),gap*gap)]
    if fixed is None:
        ii,jj=linear_sum_assignment(cost);mapping=dict(zip(ii,jj))
    else:
        lookup={p['index']:j for j,p in enumerate(pred)};mapping={i:lookup.get(fixed.get(o['id']),len(pred)) for i,o in enumerate(obs)}
    records=[]; residual=[]; ref=reference()
    for i,o in enumerate(obs):
        j=mapping[i]; p=pred[j] if j<len(pred) else None
        order=np.argsort(d[i])[:4];alternatives=[dict(index=pred[k]['index'],distance_px=float(d[i,k]),point=pred[k]['point']) for k in order]
        a=o['arc'];eps=1.; aa=(a+np.array([-eps,eps]))%ref.length
        tt=np.array([[np.interp(v,ref.arc,ref.points[:,k]) for k in range(2)] for v in aa]);t=tt[1]-tt[0];t/=np.linalg.norm(t)
        delta=np.array(p['point'])-o['point'] if p else None
        error=float(np.linalg.norm(delta)) if p else None
        rival=min((v['distance_px'] for v in alternatives if not p or v['index']!=p['index']),default=gap)
        ambiguous=bool(p and (error>8 or rival-error<8 or o.get('uncertainty_px',3)>3))
        records.append(dict(id=o['id'],observed=o['point'],predicted=p['point'] if p else None,index=p['index'] if p else None,
            arc=a,section=o['section'],split=o['split'],strong=o['strong'],color=o['color'],uncertainty_px=o['uncertainty_px'],
            error_px=error,tangent_px=float(delta@t) if p else None,normal_px=float(delta@[-t[1],t[0]]) if p else None,
            status='ambiguous' if ambiguous else 'conditional' if p else 'unmatched',alternatives=alternatives))
        # Uncertainty softens influence only within a bounded factor, never erases it.
        residual.append((min(error,gap) if p else gap)/max(1.,min(2.,o.get('uncertainty_px',3.)/3.)))
    errors=[r['error_px'] for r in records if r['error_px'] is not None]
    return dict(loss=float(np.mean(np.minimum(np.square(residual),gap*gap)))/64,
        rms=float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
        median=float(np.median(errors)) if errors else None,p90=float(np.percentile(errors,90)) if errors else None,
        matched=len(errors),unmatched=len(obs)-len(errors),ambiguous=sum(r['status']=='ambiguous' for r in records),records=records)

class Objective:
    def __init__(self,data,m,obs,split='development'):
        self.data=data;self.m=m;self.split=split;self.obs=[r for r in obs if r['strong'] and r['split']==split]
        self.photo=PhotoScore(data,split)
        self.bi=[i for i,r in enumerate(m['beads']) if r['split']==split]
        self.ei=[i for i,r in enumerate(m['envelope']) if r['fit_eligible'] and r['split']==split]
        self.targetb=np.array([r['extent_px'] for r in m['beads']]);self.targete=np.array([r['bounds'] for r in m['envelope']])

    def assess(self,scene,reflections=True,step=3.,pred=None):
        poly=outlines(scene);bd=bead_extents(scene,self.m['beads'],poly);en=envelope(scene,self.m['envelope'],poly)
        br=bd[self.bi]-self.targetb[self.bi];er=en[self.ei]-self.targete[self.ei]
        dimensions=float(np.mean(np.minimum((br/3.)**2,16)))
        envelopes=float(np.mean(np.minimum((er/4.)**2,16)))
        photo=self.photo.assess(scene)
        # Balance by measured support and geographic region, not pixel count.
        sections=[]; lookup={r['id']:r for r in self.photo.rows}
        for j in range(32):
            rows=[r for r in photo['assignments'] if int(lookup[r['id']]['station']/self.data['length']*32)%32==j]
            sections.append(dict(section=j,n=len(rows),containment=float(np.mean([r['fraction'] for r in rows])) if rows else None))
        material=np.mean([r['containment'] for r in sections if r['n']])
        nodes=np.array(scene.p.get('axis_nodes',[0.]*32)); phase=np.array(scene.p.get('local_phase',[0.]*32));spacing=np.array(scene.p.get('local_spacing',[0.]*32))
        regularity=float(.10*np.mean((nodes/10)**2)+.15*np.mean(((np.roll(nodes,1)-2*nodes+np.roll(nodes,-1))/8)**2)
                         +.05*np.mean((phase/.3)**2)+.04*np.mean((spacing/.02)**2))
        structural=dimensions+envelopes+4*(1-material)+5*photo['colored_missing']+8*photo['paper_occupied']+2*photo['color_conflict']+photo['separator_error_px']/6
        # Strong photographic contradictions cannot be paid away by specular gains.
        barrier=40*(max(0,photo['paper_occupied']-.12)**2+max(0,photo['colored_missing']-.30)**2)
        reflection=None;meta=None
        if reflections:
            if pred is None:pred,meta=predict(scene,step,self.obs)
            reflection=match(self.obs,pred)
        loss=structural+barrier+regularity+(.35*reflection['loss'] if reflection else 0)
        return dict(loss=float(loss),structural_loss=float(structural+barrier),regularity=regularity,dimensions_loss=dimensions,envelope_loss=envelopes,
            bead_extent_mae=float(np.mean(abs(br))),bead_axial_mae=float(np.mean(abs(br[:,0]))),bead_face_mae=float(np.mean(abs(br[:,1]))),
            envelope_edge_mae=float(np.mean(abs(er))),envelope_width_mae=float(np.mean(abs(np.diff(er,axis=1)))),
            envelope_common_mae=float(np.mean(abs(er.mean(1)))),beads=bd.tolist(),envelope=en.tolist(),
            photographic=photo,sections=sections,reflection=reflection,reflection_numerics=meta,bead_indices=self.bi,envelope_indices=self.ei)

def vector(result):
    """Grouped response at engineering scales, not a statistical rank estimate."""
    p=result['photographic']
    return np.r_[np.array(result['beads'])[result['bead_indices']].ravel()/3, np.array(result['envelope'])[result['envelope_indices']].ravel()/4,
                 p['paper_occupied']/.1,p['colored_missing']/.1,p['region_containment']/.1,
                 p['separator_error_px']/4]

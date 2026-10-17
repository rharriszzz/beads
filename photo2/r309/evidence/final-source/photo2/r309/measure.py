"""One independent photographic length; common outcomes and competing losses."""
import numpy as np
from scipy.ndimage import binary_erosion,binary_dilation,distance_transform_edt
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist
from photo2.r297.common import ROOT,read,save,sha
from .structural import Objective

def reference_dimension(m):
    rows=[]
    for r in m['beads']:
        p=np.asarray(r['polygon']);dist=cdist(p,p);a,b=np.unravel_index(dist.argmax(),dist.shape)
        rows.append(dict(id=r['id'],point=r['point'],major_axis_px=float(dist[a,b]),endpoints=p[[a,b]].tolist(),uncertainty_px=6.,source=r['provenance'],status=r['status']))
    largest=max(rows,key=lambda r:r['major_axis_px'])
    return dict(D_px=largest['major_axis_px'],reference=largest,all_contours=rows,source='photo2/r298/evidence/measurements.json',source_sha256=sha(ROOT/'photo2/r298/evidence/measurements.json'),photo_sha256=sha(ROOT/'beads-photo-2.jpg'),policy='Fixed longest digitized visible-contour Feret major-axis length. Not a trustworthy maximum over all photographed beads: only16 uncertain contours exist. Each endpoint may move3px, giving conservative ±6px length uncertainty; not a confidence interval. No model size or pixel area determines D.')

def distances(rows,D,key='error_px'):
    valid=[r for r in rows if r.get(key) is not None];a=np.array([r[key] for r in valid]);maximum=max(valid,key=lambda r:r[key]) if valid else None
    out=dict(observations=len(rows),measured=len(valid),missing=len(rows)-len(valid),uncertain_correspondences=sum(not r.get('physical_identity_verified',False) for r in rows),close_alternative_count=sum(r.get('ambiguous',True) for r in rows))
    for name,value in [('rms',np.sqrt(np.mean(a*a)) if len(a) else None),('maximum',a.max() if len(a) else None),('p95',np.percentile(a,95) if len(a) else None)]:
        out[name+'_px']=float(value) if value is not None else None;out[name+'_D']=float(value/D) if value is not None else None
    out['maximum_record']=maximum
    return out

def tail_loss(a):
    a=np.asarray(a,float);return float(np.mean(a*a)+.5*np.sqrt(np.mean(a**4))) if len(a) else 0.

class Measures:
    def __init__(self,data,m,obs,split='development',dense=False):
        self.o=Objective(data,m,obs,split,dense);self.D=reference_dimension(m)['D_px'];self.split=split;self.obs={r['id']:r for r in obs};self.dense=dense
    def evaluate(self,scene,anchors=None,step=1.,threshold=.5):
        _,r,a=self.o.evaluate(scene,anchors,step=step,detail=True);o=self.o;D=self.D;pred,smooth,meta=scene._optics
        reflections=[];sv=[]
        for row in r['reflections']:
            obs=self.obs[row['id']];x=np.asarray(obs['point']);index=row['index'];s=smooth.get(index);effective=2*D;mass=0.;center=None
            if s is not None and s['mass']>1e-15:
                mass=s['mass'];dist=np.sum((s['xy']-x)**2,axis=1);sigma=D/3
                overlap=float(np.sum(s['w']*np.exp(-dist/(2*sigma*sigma)))/mass)
                effective=float(np.sqrt(max(0,-2*sigma*sigma*np.log(max(overlap,1e-12)))))
                center=np.average(s['xy'],weights=s['w'],axis=0).tolist()
            alternatives=sorted([dict(index=p['index'],distance_px=float(np.linalg.norm(np.array(p['point'])-x))) for p in pred],key=lambda z:z['distance_px'])[:4]
            ambiguous=len(alternatives)>1 and alternatives[1]['distance_px']-alternatives[0]['distance_px']<3
            reflections.append(dict(**row,color=obs['color'],strong=obs['strong'],arc=obs['arc'],split=obs['split'],reliability='strong localized, conditional owner',ambiguous=ambiguous,alternatives=alternatives,smooth_distance_px=effective,intensity_mass=mass,unthresholded_centroid=center))
            sv.append(effective/D)
        tr=o.last_trace;own=tr['owner'];unknown=tr['unknown'];start=len(o.supportxy)+len(o.cues['xy'])+97*len(o.separators);boundary=[];bv=[]
        for cnt,cr in zip(o.contours,r['contours']):
            n=len(cnt['xy']);os=own[start:start+n].reshape(cnt['shape']);un=unknown[start:start+n].reshape(cnt['shape']);start+=n
            mask=os==cr['index']-int(scene.indices[0]);edge=mask&~binary_erosion(mask)&~binary_dilation(un);oe=cnt['inside']&~binary_erosion(cnt['inside'])
            ep=cnt['xy'][edge.ravel()];op=cnt['xy'][oe.ravel()];rows=[]
            for direction,source,target in [('observed-to-predicted',op,ep),('predicted-to-observed',ep,op)]:
                dis=cKDTree(target).query(source)[0] if len(target) else np.full(len(source),np.nan)
                for pt,e in zip(source,dis):rows.append(dict(id=cnt['row']['id'],point=pt.tolist(),direction=direction,error_px=float(e) if np.isfinite(e) else None,banded_error_px=float(max(0,e-3)) if np.isfinite(e) else None,ambiguous=True,reliability='uncertain digitized contour, ±3px',split=self.split,index=cr['index']))
            es=np.array([v['banded_error_px'] if v['banded_error_px'] is not None else D for v in rows]);bv.append(np.sqrt(tail_loss(es/D)))
            boundary.extend(rows)
        hist=o.last_hist;supports=[]
        for i,s in enumerate(r['supports']):
            alternatives=s['alternatives'];modal=s['modal_fraction'];missing=s['missing'];supports.append(dict(**s,color=o.rows[i]['color'],competing_fraction=max(0,1-missing-modal),major_conflict=bool(o.confidence[i]>=.5 and sum(v['fraction']>=.2 for v in alternatives)>1)))
        reverse=[]
        for k in np.flatnonzero((hist>=.2).sum(0)>1):
            ii=np.flatnonzero(hist[:,k]>=.2);distinct=len({o.rows[i]['color'] for i in ii})>1
            if distinct:reverse.append(dict(index=int(scene.indices[k]),regions=[o.rows[i]['id'] for i in ii],fractions=hist[ii,k].tolist(),status='cross-color evidence; distinct interior supports, no physical identity proof'))
        conf=o.confidence;cv=np.sqrt(conf)*(1-np.array([s['modal_fraction'] for s in supports]));rv=np.sqrt(r['reverse_conflict']);om=np.array([s['missing'] for s in supports])
        material=r['material'];mv=np.array([[np.sqrt(z['paper']),np.sqrt(z['omission'])] for z in material]).ravel()
        sep=np.array([z['error']/D for z in r['separators']]);env=np.sqrt(r['blocks']['envelope']/1.5)*4/D
        components=dict(reflection=tail_loss(sv),boundary=tail_loss(bv)+.5*tail_loss(sep)+.25*env**2,ownership=float(np.mean(cv**2)+r['reverse_conflict']),material=float(np.mean(mv**2)+np.mean(om)))
        # Missing exact lobes never become good displacements, even in smooth fit.
        components['missing_penalty']=r['unmatched']/max(1,len(reflections))
        scores={k:components[k]+.15*components['material']+.25*components['missing_penalty'] for k in ['reflection','boundary','ownership']}
        scores['balanced']=sum(components[k] for k in ['reflection','boundary','ownership','material'])+components['missing_penalty']
        # Fixed-dimensional whole-circuit residual blocks for derivative diagnostics.
        vectors=dict(reflection=sv,boundary=bv+sep.tolist()+[env],ownership=cv.tolist()+[rv],material=mv.tolist()+om.tolist())
        for k,v in vectors.items():vectors[k]=(np.array(v)/np.sqrt(max(1,len(v)))).tolist()
        result=dict(scores=scores,components=components,reflections=reflections,boundary=boundary,supports=supports,reverse_conflicts=reverse,material=material,separators=r['separators'],contours=r['contours'],vectors=vectors,unknown=r['unknown'],rays=r['rays']+meta['rays'],missing=r['unmatched'],D_px=D,anchors=a,numerics=meta)
        result['metrics']=summarize(result,D)
        return result

def summarize(r,D):
    refs=r['reflections'];bd=r['boundary'];su=r['supports'];mat=r['material']
    return dict(reflection=distances(refs,D),by_color={c:distances([v for v in refs if v['color']==c],D) for c in ['black','red','yellow']},boundary=distances(bd,D),boundary_directions={c:distances([v for v in bd if v['direction']==c],D) for c in ['observed-to-predicted','predicted-to-observed']},boundary_banded=distances(bd,D,'banded_error_px'),ownership=dict(regions=len(su),coherent_percent=100*float(np.mean([x['modal_fraction'] for x in su])),competing_percent=100*float(np.mean([x['competing_fraction'] for x in su])),missing_percent=100*float(np.mean([x['missing'] for x in su])),major_conflicts=sum(x['major_conflict'] for x in su),cross_color_bodies=len(r['reverse_conflicts']),possible_mergers=sum(x['confidence']<.5 for x in su)),material=dict(foreground_omission_percent=100*float(np.mean([x['omission'] for x in mat])),background_occupation_percent=100*float(np.mean([x['paper'] for x in mat]))),supported_contours=len(r['contours']),boundary_limitation='Only16 uncertain observed contours across the circuit; all other bead boundaries unmeasured. Correlated pixels retained, objective balances contours.',unknown_rays=r['unknown'])

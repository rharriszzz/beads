"""Part A checks: ownership alternatives, threshold uncertainty and neighbor proxies."""
import numpy as np
from types import MethodType
from photo2.r305.diagnose import isolated
from photo2.r307.fast import Chain as Fast
from scipy.ndimage import binary_erosion
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,utc
from .analysis import OUT,MODELS,D,models,evidence,points,stats,ANCHOR

def controls():
    data,m,obs,supports=evidence();results=[];neighbor=[]
    for name,doc,scene,raster in models():
        a=read(OUT/f'{name}-partA.json.gz');rows=a['supports'];address=raster['address'];unknown=raster['unknown'];by={r['id']:r for r in rows};supportby={r['id']:r for r in supports};sens=[]
        for r in rows:
            if abs(r['distance_px'])>230:continue
            pts=points(supportby[r['id']]);lo=pts.min(0)-4;hi=pts.max(0)+5;mask=np.zeros((hi[1]-lo[1],hi[0]-lo[0]),bool);mask[pts[:,1]-lo[1],pts[:,0]-lo[0]]=1
            for erosion in [0,1,2,3]:
                y,x=np.where(binary_erosion(mask,iterations=erosion) if erosion else mask);pp=np.c_[x+lo[0],y+lo[1]];valid=~unknown[pp[:,1],pp[:,0]];own=address[pp[:,1],pp[:,0]];vals,counts=np.unique(own[valid&(own!=-32768)],return_counts=True);j=np.argmax(counts);k=int(vals[j]);b=next(b for b in doc['positions'] if b['index']==k);c=np.array(b['projected_center']);bl=np.maximum([0,0],np.floor(c-scene.query_radius-4)).astype(int);bh=np.minimum([2540,3182],np.ceil(c+scene.query_radius+4)).astype(int);yy,xx=np.where((address[bl[1]:bh[1],bl[0]:bh[0]]==k)&~unknown[bl[1]:bh[1],bl[0]:bh[0]]);dd=cKDTree(np.c_[xx+bl[0],yy+bl[1]]).query(pp)[0];dd=dd[valid]
                sens.append(dict(id=r['id'],distance_px=r['distance_px'],erosion=erosion,pixels=len(pp),owner=k,coherence=float(counts[j]/len(pp)),distances=stats(dd.tolist()),far_fraction={str(t):float(np.mean(dd>t*D)) for t in [.1,.15,.2]}))
        sensitivity=[]
        for sign in [-1,1]:
            for erosion in [0,1,2,3]:
                for threshold in [.1,.15,.2]:
                    eligible=sorted([r for r in sens if r['erosion']==erosion and sign*r['distance_px']>0 and r['pixels']>=40 and r['coherence']<.65 and r['far_fraction'][str(threshold)]>=.2],key=lambda r:abs(r['distance_px']));sensitivity.append(dict(direction=sign,erosion=erosion,distance_threshold_D=threshold,first=eligible[0]['id'] if eligible else None,first_distance_px=eligible[0]['distance_px'] if eligible else None,range_px=230))
        # Observed centroid vectors are independent image proxies, not physical center vectors.
        near=[r for r in rows if abs(r['distance_px'])<230]
        for i,r in enumerate(near):
            for q in near[i+1:]:
                delta=np.array(q['point'])-r['point'];norm=np.linalg.norm(delta)
                if not 12<norm<65:continue
                va=np.array(q['predicted_visible_centroid'])-r['predicted_visible_centroid'];pc=np.array(q['modeled_center'])-r['modeled_center'];diff=va-delta
                e=next((e for e in data['edges'] if set(e['ids'])=={r['id'],q['id']}),None)
                neighbor.append(dict(model=name,ids=[r['id'],q['id']],observed_interior_centroid_vector_px=delta.tolist(),observed_length_D=float(norm/D),predicted_visible_centroid_vector_px=va.tolist(),predicted_physical_center_vector_px=pc.tolist(),visible_proxy_error_px=float(np.linalg.norm(diff)),visible_proxy_error_D=float(np.linalg.norm(diff)/D),conditional_index_difference=q['index']-r['index'],relationship_in_1_6_7=abs(q['index']-r['index']) in [1,6,7],owner_coverages=[r['coherence'],q['coherence']],existing_separator=e,physical_neighbor_verified=False,center_uncertainty='Unbounded from these partial interiors; visible centroid and physical center must not be identified. No center displacement inferred.'))
        isolatedmax=[]
        for r in near:
            pts=points(supportby[r['id']]);radius=float(np.linalg.norm(pts-np.array(r['point']),axis=1).max())+scene.query_radius;owners=[]
            for j in scene.tree.query_ball_point(r['point'],radius):
                k=int(scene.indices[j]);single=isolated(scene,k);single.trace=MethodType(Fast.trace,single);tr=single.trace(pts);hit=(tr['owner']>=0)&~tr['unknown'];visible=address[pts[:,1],pts[:,0]]==k
                owners.append(dict(index=k,isolated_fraction=float(hit.mean()),visible_fraction=float(visible.mean()),hidden_fraction=float(np.mean(hit&~visible)),unknown_fraction=float(tr['unknown'].mean())))
            owners.sort(key=lambda x:-x['isolated_fraction']);isolatedmax.append(dict(id=r['id'],best_visible=r['coherence'],best_isolated=owners[0]['isolated_fraction'] if owners else None,owners=owners))
        results.append(dict(model=name,threshold_controls=sensitivity,measurements=sens,isolated_controls=isolatedmax,reassignment_only=a['reassignment_only'],reference_observations=[dict(id=r['id'],interior=r['point'],reflection=r['observed_reflection'],modeled_center=r['modeled_center'],alternatives=r['alternatives']) for r in near if r['id']==ANCHOR]))
    save(OUT/'partA-controls.json.gz',results);save(OUT/'neighbor-vectors.json.gz',dict(rows=neighbor,verified_physical_neighbor_pairs=0,policy='All observed vectors join independent measured visible-interior centroids. +1/+6/+7 membership is predicted conditional identity only; zero measured physical-center neighbor vectors. Existing dark-separation evidence does not determine crochet sequence.'))
    save(OUT/'partA-completion.json',dict(utc=utc(),completed_before_curvature=True,geometry_changed=False,fit_evaluations=0,conclusion='Reference photograph established, model identities conditional (R3060/R3092/R2970). Earliest supported fragmentation is close to anchor, with threshold-sensitive material misses. No physical-center chain supports a unique first positioning-error index. Isolated-versus-visible controls distinguish coverage loss through occlusion from body-shape/pose misses; relabeling cannot recover missing single-owner coverage. Curvature investigation may now proceed.'))
if __name__=='__main__':controls()

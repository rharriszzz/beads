"""Frozen models -> full native first-hit review and identical-evidence tables."""
import csv
import json
from pathlib import Path
from PIL import Image
from scipy import ndimage as ndi
from .calibrate import *
from .photometry import PhotoScore
from .fft import diagnostic
from photo2.r297.common import photo,pixels
REVIEW=ROOT/'photo2/review/r298'

def raster(scene,shape):
    h,w=shape[:2];mask=np.zeros((h,w),bool);bound=scene.query_radius+2
    for cx,cy in scene.pc:
        x0,y0=np.maximum(0,np.floor([cx-bound,cy-bound]).astype(int));x1,y1=np.minimum([w,h],np.ceil([cx+bound+1,cy+bound+1]).astype(int));mask[y0:y1,x0:x1]=True
    yy,xx=np.where(mask);xy=np.c_[xx,yy];tr=scene.trace(xy)
    owners=np.full((h,w),-1,np.int32);unknown=np.zeros((h,w),bool);owners[yy,xx]=tr['owner'];unknown[yy,xx]=tr['unknown']
    return xy,tr,owners,unknown

def main():
    data,_=load_evidence();m=measurements();selection=read(BASE/'results/selection.json');history=read(BASE/'results/refinement-history.json.gz');rgb,_,meta=photo();REVIEW.mkdir(exist_ok=True,parents=True)
    import shutil
    shutil.copy2(ROOT/'beads-photo-2.jpg',REVIEW/'original.jpg')
    bundle=dict(measurements={k:v for k,v in m.items() if k!='envelope'},profiles=[{k:v for k,v in r.items() if k not in ['samples_xy','samples_rgb']} for r in m['envelope']],separators=read(BASE/'evidence/separators.json')['records'],primary=selection['primary'],models=[],photo=meta)
    ids=[0]+selection['families'];objects={s:PhotoScore(data,s) for s in ['development','comparison']}
    for ident in ids:
        start=monotonic();p=history[ident]['parameters'];scene,poly,bd,en=prediction(p,data,m);cert=contact(scene,exact=True)
        if not cert['certified']:raise ValueError('Selected model not certified')
        print('native model',ident,'start',flush=True);xy,tr,owners,unknown=raster(scene,rgb.shape)
        np.savez_compressed(BASE/f'results/native-{ident}.npz',xy=xy,owner=tr['owner'],unknown=tr['unknown'])
        boundary=np.zeros(owners.shape,bool)
        boundary[1:]|=owners[1:]!=owners[:-1];boundary[:-1]|=owners[:-1]!=owners[1:];boundary[:,1:]|=owners[:,1:]!=owners[:,:-1];boundary[:,:-1]|=owners[:,:-1]!=owners[:,1:];boundary&=owners>=0
        overlay=np.zeros((*owners.shape,4),np.uint8);overlay[boundary]=[255,187,53,220] if ident==0 else [43,255,220,220];Image.fromarray(overlay).save(REVIEW/f'surfaces-{ident}.png')
        native_env=[];profile_unknown=[]
        for r in m['envelope']:
            ij=np.array(r['samples_xy']).reshape(9,191,2);o=owners[ij[:,:,1],ij[:,:,0]];v=[]
            for line in o:
                hits=np.flatnonzero(line>=0);v.append([float(hits[0]-95),float(hits[-1]-95)] if len(hits) else [0.,0.])
            native_env.append(np.median(v,axis=0));profile_unknown.append(int(unknown[ij[:,:,1],ij[:,:,0]].sum()))
        native_env=np.array(native_env);observations=[]
        for r in data['rows']:
            pix=pixels(r['pixels']);o=owners[pix[:,1],pix[:,0]];ii,cc=np.unique(o[o>=0],return_counts=True);order=np.argsort(-cc);alts=[dict(index=int(scene.indices[ii[j]]),fraction=float(cc[j]/len(pix))) for j in order];fr=alts[0]['fraction'] if alts else 0.
            observations.append(dict(id=r['id'],kind=r['kind'],split=r['split'],point=r['point'],station=r['station'],fraction=fr,alternatives=alts,unknown=int(unknown[pix[:,1],pix[:,0]].sum()),trust=r['trust']))
        photographic={s:o.assess(scene) for s,o in objects.items()}
        axis=scene.project(scene.line);arc=reference_arc(axis)
        bead_visible=[]
        for r in m['beads']:
            c=np.array(r['point']);neigh=scene.tree.query_ball_point(c,35);best=None
            for k in neigh:
                yy,xx=np.where(owners[max(0,int(c[1]-45)):int(c[1]+46),max(0,int(c[0]-45)):int(c[0]+46)]==k)
                if len(xx):
                    pts=np.c_[xx+max(0,int(c[0]-45)),yy+max(0,int(c[1]-45))];err=np.linalg.norm(pts.mean(0)-c)
                    if best is None or err<best[0]:best=(err,k,pts)
            if best:
                err,k,pts=best;bead_visible.append(dict(id=r['id'],index=int(scene.indices[k]),centroid_error=float(err),extent=np.ptp(pts@np.array([r['tangent'],r['normal']]).T,axis=0).tolist(),meaning='Nearest visible-surface centroid conditional assignment, not identity'))
            else:bead_visible.append(dict(id=r['id'],index=None))
        neighbors=[]
        for r in m['beads']:
            i=int(scene.tree.query(r['point'])[1]);v=[]
            for step in [1,6,7]:
                j=(i+step)%scene.n
                if not scene.closed and i+step>=scene.n:continue
                delta=scene.pc[j]-scene.pc[i];direction=delta/max(np.linalg.norm(delta),1e-12)
                # Signed projected interval gap can be negative under occlusion;
                # physical separation is independently certified in 3D.
                gap=float(np.min(poly[j]@direction)-np.max(poly[i]@direction))
                v.append(dict(step=step,indices=[int(scene.indices[i]),int(scene.indices[j])],points=[scene.pc[i].tolist(),scene.pc[j].tolist()],center_displacement=delta.tolist(),center_distance=float(np.linalg.norm(delta)),projected_interval_gap=gap,physical_center_distance=float(np.linalg.norm(scene.centers[j]-scene.centers[i]))))
            neighbors.append(dict(id=r['id'],predictions=v))
        dimension=dict(face_diameter_units=2*scene.radius,axial_thickness_units=1.4*scene.radius*scene.axial,axial_face_ratio=.7*scene.axial,transverse_face_ratio=(p['minor']+scene.radius)/scene.radius,minor_face_ratio=p['minor']/(2*scene.radius),reference_face_diameter_px=2*scene.radius*scene.scale,reference_transverse_diameter_px=2*(p['minor']+scene.radius)*scene.scale)
        model=dict(id=ident,name=('R297' if ident==0 else f"R298 hand {p['hand']:+} / {p['topology']} / N{p['count']}"),parameters=p,dimensions=dimension,contact=cert,closure=scene.closure(),axis=axis.tolist(),axis_reference_arc=arc.tolist(),envelope=native_env.tolist(),polygon_envelope=en.tolist(),bead_extents=bd.tolist(),visible_beads=bead_visible,profile_unknown=profile_unknown,photographic=photographic,metrics={s:metrics((bd,native_env),m,s) for s in ['development','comparison']},observations=observations,neighbors=neighbors,positions=scene.pc.tolist(),indices=scene.indices.tolist(),world_centers=scene.centers.tolist(),polygons=poly.tolist(),native_unknown=int(tr['unknown'].sum()),native_rays=len(xy))
        save(BASE/f'results/model-{ident}.json.gz',model);save(BASE/f'results/fft-{ident}.json',diagnostic(scene))
        public={k:v for k,v in model.items() if k not in ['contact','observations','world_centers','polygons']};public['contact']={k:v for k,v in cert.items() if k not in ['witnesses','index_pairs']};public['axis']=np.round(axis[::2],2).tolist();public['positions']=np.round(scene.pc,2).tolist();public['photographic']={s:{k:v for k,v in q.items() if k!='assignments'} for s,q in photographic.items()};bundle['models'].append(public)
        with (BASE/f'results/positions-{ident}.csv').open('w') as f:
            writer=csv.writer(f);writer.writerow(['index','x','y','z','image_x','image_y']);writer.writerows([[int(k),*xyz,*uv] for k,xyz,uv in zip(scene.indices,scene.centers,scene.pc)])
        print('native model',ident,'done',round(monotonic()-start,2),model['metrics'],flush=True)
    bundle['models'].sort(key=lambda r:(r['id']!=0,r['id']!=selection['primary'],r['id']))
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(bundle,separators=(',',':'))+';\n')
    save(BASE/'results/export-manifest.json',dict(ids=ids,primary=selection['primary'],photo_sha256=meta['photo_sha256'],models={str(i):sha(BASE/f'results/model-{i}.json.gz') for i in ids}))

def reference_arc(xy):
    from photo2.r293.geometry import Reference
    return Reference().project(xy)['arc']
if __name__=='__main__':main()

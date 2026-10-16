"""Native owner raster and shared-light reflections, with complete guard bodies."""
import time
import numpy as np
from PIL import Image
from photo2.r299.forward import shade,highlight,light_params
from photo2.r302.experiment import clean
from photo2.r297.common import save,sha,utc
from .model import *

def box(scene):
    k=(scene.indices>=FIRST)&(scene.indices<=LAST);r=scene.query_radius+3
    lo=np.maximum([0,0],np.floor(scene.pc[k].min(0)-r)).astype(int)
    hi=np.minimum([2539,3181],np.ceil(scene.pc[k].max(0)+r)).astype(int)
    return [*lo,*hi]

def raster(scene,bounds,step=1.):
    x0,y0,x1,y1=bounds;yy,xx=np.mgrid[y0:y1+step/2:step,x0:x1+step/2:step]
    xy=np.c_[xx.ravel(),yy.ravel()];chunks=[];light=light_params([scene.p['light_az'],scene.p['light_el'],10.],'directional',scene.centers.mean(0))
    for i in range(0,len(xy),24000):
        tr=scene.camera(xy[i:i+24000]);sh=shade(scene,tr,light)
        chunks.append((tr,sh))
    owner=np.concatenate([c[0]['owner'] for c in chunks]);unknown=np.concatenate([c[0]['unknown'] for c in chunks]);intensity=np.concatenate([c[1]['intensity'] for c in chunks])
    # Persist addresses, not array offsets; background sentinel is outside domain.
    address=np.full(len(owner),-32768,np.int16);ok=owner>=0;address[ok]=scene.indices[owner[ok]]
    isolated=sum(c[0]['isolated_counts'] for c in chunks)
    shadow={k:sum(c[1][k] for c in chunks) for k in ['unknown_shadow_pairs','self_shadow_samples','neighbor_shadow_samples']}
    return dict(xy=xy,address=address.reshape(xx.shape),unknown=unknown.reshape(xx.shape),intensity=intensity.reshape(xx.shape),isolated=isolated,shadow=shadow,rays=len(xy),step=step,bounds=bounds)

def segments(mask,x0,y0):
    """Exact cell edges from native first-hit ownership; inner holes retained."""
    pad=np.pad(mask.astype(np.int8),1);out=[]
    h=np.diff(pad,axis=0)!=0;v=np.diff(pad,axis=1)!=0
    for y in range(h.shape[0]):
        xs=np.flatnonzero(h[y]);groups=np.split(xs,np.flatnonzero(np.diff(xs)>1)+1)
        for g in groups:
            if len(g):out.append([float(x0+g[0]-1.5),float(y0+y-.5),float(x0+g[-1]-.5),float(y0+y-.5)])
    for x in range(v.shape[1]):
        ys=np.flatnonzero(v[:,x]);groups=np.split(ys,np.flatnonzero(np.diff(ys)>1)+1)
        for g in groups:
            if len(g):out.append([float(x0+x-.5),float(y0+g[0]-1.5),float(x0+x-.5),float(y0+g[-1]-.5)])
    return out

def records(scene,r):
    a=r['address'];xy=r['xy'];out=[]
    for j,k in enumerate(scene.indices):
        yy,xx=np.where(a==k);mask=a.ravel()==k;h=highlight(xy[mask],r['intensity'].ravel()[mask],r['step']);boundaries=[]
        if len(xx):
            lo=[xx.min(),yy.min()];hi=[xx.max()+1,yy.max()+1];m=a[lo[1]:hi[1],lo[0]:hi[0]]==k
            boundaries=segments(m,r['bounds'][0]+lo[0],r['bounds'][1]+lo[1])
        uncertainty=None
        if h:
            w=r['intensity'].ravel()[mask];pts=xy[mask];centroids=[]
            for threshold in [.4,.5,.6]:
                keep=w>=max(threshold*w.max(),1e-4);centroids.append(np.average(pts[keep],axis=0,weights=w[keep]).tolist())
            near=pts[w>=.98*w.max()]
            uncertainty=dict(threshold_centroids=centroids,centroid_sensitivity_px=max(np.linalg.norm(np.array(q)-h['centroid']) for q in centroids),peak_plateau_radius_px=float(np.linalg.norm(near-h['peak'],axis=1).max()),native_grid_step_px=1.,not_confidence_interval=True)
        out.append(dict(index=int(k),displayed=bool(FIRST<=k<=LAST),center=scene.centers[j].tolist(),projected_center=scene.pc[j].tolist(),axis_xy=scene.axis_xy[j].tolist(),phase=float(scene.phase[j]),world_arc=float(scene.arc[j]),photo_arc=float(scene.photo_arc[j]),axis_departure_px=float(scene.axis_departure[j]),tangent=scene.axis_tangent[j].tolist(),visible_area_px2=int(len(xx)),isolated_area_within_raster_px2=int(r['isolated'][j]),visible_fraction=float(len(xx)/max(1,r['isolated'][j])),visibility='visible' if len(xx) else 'occluded_or_outside_raster',reflection={key:h[key] for key in ['centroid','peak','peak_intensity','area_px2','covariance']} if h else None,reflection_status='predicted' if h else 'no_lobe_above_threshold' if len(xx) else 'occluded_or_outside_raster',numerical=uncertainty,boundary_segments=boundaries))
    return out

def physical(scene):
    cert=scene.certify();xyz,_=scene.samples(1);checks=[]
    for row in cert['witnesses']:
        row['address_pair']=[int(scene.indices[j]) for j in row['pair']]
        if row['separated']:continue
        a,b=row['pair'];minimum=0.
        for j,k in [(a,b),(b,a)]:
            delta=xyz[j]-scene.centers[k];q=np.stack([delta@scene.g[key][k] for key in AXES],axis=1);minimum=min(minimum,float(scene.local_sdf(q).min()))
        checks.append(dict(pair=row['address_pair'],sampled_min_sdf=minimum,demonstrated_penetration=minimum<-.001))
    cert['penetration_checks']=checks;cert['minimum_demonstrated_separating_margin']=min(r['gap_units'] for r in cert['witnesses'] if r['separated']);cert['demonstrated_penetrating_pairs']=sum(r['demonstrated_penetration'] for r in checks)
    return cert

def images(name,r):
    a=r['address'];valid=a!=-32768;rgba=np.zeros((*a.shape,4),np.uint8)
    tone=np.clip(85+150*np.sqrt(r['intensity']),0,255)
    rgba[valid,:3]=np.stack([tone*.55,tone*.8,tone],axis=-1)[valid].astype(np.uint8);rgba[valid,3]=255
    Image.fromarray(rgba).save(REVIEW/f'{name}-surface.png')
    edge=np.zeros(a.shape,bool)
    edge[1:]|=a[1:]!=a[:-1];edge[:-1]|=a[:-1]!=a[1:];edge[:,1:]|=a[:,1:]!=a[:,:-1];edge[:,:-1]|=a[:,:-1]!=a[:,1:];edge&=valid
    rgba[:]=0;rgba[edge]=[30,225,255,255];Image.fromarray(rgba).save(REVIEW/f'{name}-boundary.png')

def main():
    start=time.monotonic();cost=[]
    for name in FAMILIES:
        target=BASE/f'results/{name}.json.gz'
        if target.exists():raise RuntimeError('Output already exists; use a separate output/replay, never overwrite sealed predictions')
        t=time.monotonic();scene=Extended(name);bounds=box(scene);r=raster(scene,bounds);beads=records(scene,r);cert=physical(scene)
        for b in beads:
            b['uncertified_pairs']=[q['address_pair'] for q in cert['witnesses'] if not q['separated'] and b['index'] in q['address_pair']]
        np.savez_compressed(BASE/f'results/{name}-raster.npz',address=r['address'],intensity=r['intensity'],unknown=r['unknown'],bounds=bounds,isolated=r['isolated'])
        images(name,r);elapsed=time.monotonic()-t
        save(target,clean(dict(name=name,source=scene.source,parameters=scene.p,registration=scene.registration,range=[FIRST,LAST],guards_each_side=64,positions=beads,bounds=bounds,physical=cert,numerical=dict(rays=r['rays'],unknown_camera_pixels=int(r['unknown'].sum()),shadow=r['shadow']),seconds=elapsed)))
        cost.append(dict(stage='native-export',model=name,seconds=elapsed));print(name,'native',elapsed,'rays',r['rays'],'penetrating',cert['demonstrated_penetrating_pairs'],flush=True)
        # All pixels repeated with 96 guards; compare owners and shading directly.
        t=time.monotonic();extended=Extended(name,96);g=raster(extended,bounds);extra=physical(extended)
        delta=abs(g['intensity']-r['intensity']);check=dict(model=name,base_guards=64,extended_guards=96,pixels=r['rays'],owner_changes=int(np.sum(g['address']!=r['address'])),maximum_intensity_change=float(delta.max()),unknown_changes=int(np.sum(g['unknown']!=r['unknown'])),extended_physical=extra,seconds=time.monotonic()-t)
        save(BASE/f'results/{name}-guard-check.json.gz',clean(check));cost.append(dict(stage='guard-check',model=name,seconds=check['seconds']));print(name,'guard',check['seconds'],check['owner_changes'],check['maximum_intensity_change'],flush=True)
    save(BASE/'results/computation.json',dict(utc=utc(),stages=cost,total_seconds=time.monotonic()-start,optimization_evaluations=0))

if __name__=='__main__':main()

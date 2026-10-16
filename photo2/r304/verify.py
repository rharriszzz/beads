"""Replay every native pixel and witness; independently refine image sampling."""
import time,subprocess
import numpy as np
from scipy.ndimage import label
from PIL import Image,ImageOps
from photo2.r297.common import save,sha,utc
from photo2.r302.experiment import clean
from photo2.r299.forward import highlight
from .model import *
from .forward import raster,segments,physical

def main():
    start=time.monotonic();results=[]
    for name in FAMILIES:
        t=time.monotonic();scene=Extended(name);doc=read(BASE/f'results/{name}.json.gz');saved=dict(np.load(BASE/f'results/{name}-raster.npz'));r=raster(scene,doc['bounds'])
        for key in ['address','intensity','unknown','isolated']:np.testing.assert_array_equal(r[key],saved[key])
        witnesses=physical(scene);assert witnesses==doc['physical'];boundary_count=0
        for b in doc['positions']:
            j=np.searchsorted(scene.indices,b['index']);np.testing.assert_allclose(b['center'],scene.centers[j],atol=1e-12);np.testing.assert_allclose(b['projected_center'],scene.pc[j],atol=1e-12)
            yy,xx=np.where(saved['address']==b['index']);assert len(xx)==b['visible_area_px2'];segs=[]
            if len(xx):
                lo=[xx.min(),yy.min()];hi=[xx.max()+1,yy.max()+1];mask=saved['address'][lo[1]:hi[1],lo[0]:hi[0]]==b['index'];segs=segments(mask,doc['bounds'][0]+lo[0],doc['bounds'][1]+lo[1]);assert segs==b['boundary_segments'];boundary_count+=len(segs)
                # Every retained segment is on a pixel-cell boundary, between
                # this owner and a different owner/background, including holes.
                for x1,y1,x2,y2 in segs:
                    x=(x1+x2)/2-doc['bounds'][0];y=(y1+y2)/2-doc['bounds'][1]
                    if y1==y2:a=(int(np.floor(y)),int(np.floor(x+.5)));c=(a[0]+1,a[1])
                    else:a=(int(np.floor(y+.5)),int(np.floor(x)));c=(a[0],a[1]+1)
                    aa=[saved['address'][v] if 0<=v[0]<r['address'].shape[0] and 0<=v[1]<r['address'].shape[1] else -32768 for v in [a,c]]
                    assert (aa[0]==b['index']) != (aa[1]==b['index']),(name,b['index'],aa)
            else:assert not b['boundary_segments']
            if b['reflection']:
                mask=r['address'].ravel()==b['index'];h=highlight(r['xy'][mask],r['intensity'].ravel()[mask]);assert h['centroid']==b['reflection']['centroid'];assert h['peak']==b['reflection']['peak']
        # Half-pixel native-coordinate evaluation, not a geometry change.
        fine=raster(scene,doc['bounds'],.5);checks=[]
        for b in doc['positions']:
            if not b['displayed']:continue
            mask=fine['address'].ravel()==b['index'];h=highlight(fine['xy'][mask],fine['intensity'].ravel()[mask],.5);old=b['reflection'];row=dict(index=b['index'],native_present=bool(old),half_pixel_present=bool(h),half_pixel_centroid=h['centroid'] if h else None,half_pixel_peak=h['peak'] if h else None,centroid_change_px=float(np.linalg.norm(np.array(h['centroid'])-old['centroid'])) if h and old else None,peak_change_px=float(np.linalg.norm(np.array(h['peak'])-old['peak'])) if h and old else None)
            mask=r['address']==b['index'];w=r['intensity'];binary=mask&(w>=max(float(w[mask].max())*.5,1e-4)) if mask.any() else mask;_,components=label(binary);row['half_max_components_native']=int(components);row['native_centroid_owner']=None
            if old:
                x,y=np.rint(old['centroid']).astype(int)-np.array(doc['bounds'][:2]);row['native_centroid_owner']=int(r['address'][y,x]);row['centroid_inside_own_visible_surface']=row['native_centroid_owner']==b['index']
            checks.append(row)
        guard=read(BASE/f'results/{name}-guard-check.json.gz');assert guard['owner_changes']==0 and guard['maximum_intensity_change']==0
        # Normals independently checked by finite differences at first-hit points.
        xy=np.array([b['reflection']['peak'] for b in doc['positions'] if b['reflection'] and b['displayed']]);tr=scene.camera(xy);ok=tr['owner']>=0;k=tr['owner'][ok];delta=tr['points'][ok]-scene.centers[k];axes=[scene.g[key][k] for key in AXES];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);grad=np.stack([(scene.local_sdf(q+np.eye(3)[j]*1e-6)-scene.local_sdf(q-np.eye(3)[j]*1e-6))/2e-6 for j in range(3)],axis=1);normal=unit(sum(grad[:,j,None]*a for j,a in enumerate(axes)));normal_error=float(np.linalg.norm(normal-tr['normal'][ok],axis=1).max());assert normal_error<1e-4
        # Check true arclength and unit/orthogonal body frames.
        chord=np.linalg.norm(np.diff(scene.line,axis=0),axis=1);advance=np.diff(scene.arc);assert np.all(chord<=advance+1e-6);assert np.max(advance-chord)<.001
        frame=np.stack([scene.g[key] for key in AXES],axis=1);np.testing.assert_allclose(frame@np.swapaxes(frame,1,2),np.broadcast_to(np.eye(3),(scene.n,3,3)),atol=1e-12)
        changes=[r['centroid_change_px'] for r in checks if r['centroid_change_px'] is not None];result=dict(model=name,seconds=time.monotonic()-t,native_pixels_replayed=r['rays'],half_pixel_rays=fine['rays'],boundary_segments_replayed=boundary_count,all_positions_replayed=scene.n,physical_witnesses_replayed=len(witnesses['witnesses']),maximum_normal_error=normal_error,guard_invariant=True,half_pixel_centroid_change_median=float(np.median(changes)),half_pixel_centroid_change_max=float(max(changes)),presence_changes=sum(r['native_present']!=r['half_pixel_present'] for r in checks),checks=checks)
        save(BASE/f'results/{name}-numerical.json',clean(result));results.append({k:v for k,v in result.items() if k!='checks'});print(results[-1],flush=True)
    raw=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));np.testing.assert_array_equal(raw,np.asarray(Image.open(REVIEW/'photo.png')))
    protected=read(BASE/'evidence/preservation.json.gz');changed=[p for p,h in protected.items() if sha(ROOT/p)!=h];assert not changed,changed
    save(BASE/'results/verification.json',dict(utc=utc(),seconds=time.monotonic()-start,models=results,protected_files=len(protected),changed=changed,photo_native_exact=True,environment_versions=subprocess.check_output([str(ROOT/'.venv/bin/python'),'-c','import sys,numpy,scipy;print(sys.version);print(numpy.__version__,scipy.__version__)'],text=True)))

if __name__=='__main__':main()

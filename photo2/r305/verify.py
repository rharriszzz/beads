"""Replay full native predictions and contacts; converge every displayed lobe."""
import time,resource,json,hashlib
import numpy as np
from scipy.ndimage import label
from PIL import Image,ImageOps
from photo2.r297.common import save,sha,utc
from photo2.r302.experiment import clean
from photo2.r299.forward import highlight
from photo2.r304.model import Extended as Previous
from .model import *
from .forward import raster,records,physical

def main():
    start=time.monotonic();results=[]
    for name in FAMILIES:
        t=time.monotonic();scene=Extended(name);doc=read(BASE/f'results/{name}.json.gz');saved=dict(np.load(BASE/f'results/{name}-raster.npz'));r=raster(scene,doc['bounds']);bs=records(scene,r)
        for key in ['address','intensity','unknown','isolated']:np.testing.assert_array_equal(r[key],saved[key])
        for a,b in zip(bs,doc['positions']):
            for key in a:assert a[key]==b[key],(name,b['index'],key)
        cert=physical(scene);assert cert==doc['physical'];oldscene=Previous(name);ix=np.searchsorted(scene.indices,oldscene.indices)
        assert np.array_equal(scene.pc[ix],oldscene.pc);assert np.array_equal(scene.centers[ix],oldscene.centers);assert np.array_equal(scene.phase[ix],oldscene.phase)
        old=read(ROOT/f'photo2/r304/results/{name}.json.gz');oldr=dict(np.load(ROOT/f'photo2/r304/results/{name}-raster.npz'));ox,oy,ex,ey=old['bounds'];x0,y0,x1,y1=doc['bounds'];new=r['address'][oy-y0:ey-y0+1,ox-x0:ex-x0+1];neww=r['intensity'][oy-y0:ey-y0+1,ox-x0:ex-x0+1];region=((oldr['address']>=-20)&(oldr['address']<=329))|((new>=-20)&(new<=329));delta=abs(neww-oldr['intensity'])
        oldcheck=dict(centers_world_max_change=0.,centers_projected_max_change_px=0.,phase_max_change=0.,core_owner_pixel_changes=int(np.sum(region&(new!=oldr['address']))),core_maximum_intensity_change=float(delta[region].max()),core_pixels=int(region.sum()))
        guard=raster(Extended(name,96),doc['bounds']);region=((r['address']>=FIRST)&(r['address']<=LAST))|((guard['address']>=FIRST)&(guard['address']<=LAST));delta=abs(guard['intensity']-r['intensity']);gc=dict(core_owner_changes=int(np.sum(region&(guard['address']!=r['address']))),core_maximum_intensity_change=float(delta[region].max()),core_unknown_changes=int(np.sum(region&(guard['unknown']!=r['unknown']))),all_rectangle_owner_changes=int(np.sum(guard['address']!=r['address'])),all_changed_owners=sorted(set(guard['address'][guard['address']!=r['address']].astype(int).tolist())),meaning='Full rectangle can expose extra guard bodies outside the requested chain. Core check covers union of all requested owners in either raster; shadows on every requested surface are compared.')
        assert gc['core_owner_changes']==0 and gc['core_maximum_intensity_change']==0 and gc['core_unknown_changes']==0,gc
        del guard
        checks=[];core=[b for b in doc['positions'] if b['displayed']];by={b['index']:b for b in core}
        # Chunked half-pixel convergence, all displayed positions. Conservative
        # projected sphere bounds include each entire bead; all guards still trace.
        for lo in range(FIRST,LAST+1,50):
            chunk=[b for b in core if lo<=b['index']<lo+50];pc=np.array([b['projected_center'] for b in chunk]);rad=scene.query_radius+2;low=np.maximum(doc['bounds'][:2],np.floor(pc.min(0)-rad)).astype(int);hi=np.minimum(doc['bounds'][2:],np.ceil(pc.max(0)+rad)).astype(int);fine=raster(scene,[*low,*hi],.5)
            for b in chunk:
                mask=fine['address'].ravel()==b['index'];h=highlight(fine['xy'][mask],fine['intensity'].ravel()[mask],.5);oldh=b['reflection'];row=dict(index=b['index'],native_present=bool(oldh),half_pixel_present=bool(h),half_pixel_centroid=h['centroid'] if h else None,half_pixel_peak=h['peak'] if h else None,centroid_change_px=float(np.linalg.norm(np.array(h['centroid'])-oldh['centroid'])) if h and oldh else None,peak_change_px=float(np.linalg.norm(np.array(h['peak'])-oldh['peak'])) if h and oldh else None)
                cx,cy=b['projected_center'];xa=max(0,int(cx-rad-x0));xb=min(r['address'].shape[1],int(cx+rad-x0)+2);ya=max(0,int(cy-rad-y0));yb=min(r['address'].shape[0],int(cy+rad-y0)+2);mask=r['address'][ya:yb,xa:xb]==b['index'];w=r['intensity'][ya:yb,xa:xb];binary=mask&(w>=max(float(w[mask].max())*.5,1e-4)) if mask.any() else mask;_,components=label(binary);row['half_max_components_native']=int(components);row['native_centroid_owner']=None
                if oldh:
                    xx,yy=np.rint(oldh['centroid']).astype(int)-[x0,y0];row['native_centroid_owner']=int(r['address'][yy,xx]);row['centroid_inside_own_visible_surface']=row['native_centroid_owner']==b['index']
                checks.append(row)
            del fine
        chord=np.linalg.norm(np.diff(scene.line,axis=0),axis=1);advance=np.diff(scene.arc);assert np.all(chord<=advance+1e-6)
        frame=np.stack([scene.g[key] for key in AXES],axis=1);np.testing.assert_allclose(frame@np.swapaxes(frame,1,2),np.broadcast_to(np.eye(3),(scene.n,3,3)),atol=1e-12)
        assert np.diff(scene.photo_arc).min()>0;assert np.max(abs(np.diff(scene.phase)-scene.hand*2*np.pi/scene.p['turn']))<1e-10
        xy=np.array([b['reflection']['peak'] for b in core if b['reflection']]);tr=scene.camera(xy);ok=tr['owner']>=0;k=tr['owner'][ok];delta=tr['points'][ok]-scene.centers[k];axes=[scene.g[key][k] for key in AXES];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);grad=np.stack([(scene.local_sdf(q+np.eye(3)[j]*1e-6)-scene.local_sdf(q-np.eye(3)[j]*1e-6))/2e-6 for j in range(3)],axis=1);normal=unit(sum(grad[:,j,None]*a for j,a in enumerate(axes)));normal_error=float(np.linalg.norm(normal-tr['normal'][ok],axis=1).max());assert normal_error<1e-4
        changes=[r['centroid_change_px'] for r in checks if r['centroid_change_px'] is not None];result=dict(model=name,seconds=time.monotonic()-t,native_pixels_replayed=r['rays'],active_pixels=r['active_rays'],boundary_segments_replayed=sum(len(b['boundary_segments']) for b in bs),positions_replayed=scene.n,physical_witnesses_replayed=len(cert['witnesses']),maximum_normal_error=normal_error,maximum_chord_deficit=float(np.max(advance-chord)),old_interval=oldcheck,guard=gc,half_pixel_centroid_change_median=float(np.median(changes)),half_pixel_centroid_change_max=float(max(changes)),presence_changes=sum(r['native_present']!=r['half_pixel_present'] for r in checks),checks=checks)
        save(BASE/f'results/{name}-numerical.json',clean(result));results.append({k:v for k,v in result.items() if k!='checks'});print(name,results[-1],flush=True)
    raw=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));np.testing.assert_array_equal(raw,np.asarray(Image.open(REVIEW/'photo.png')))
    protected=read(BASE/'evidence/preservation.json.gz');changed=[p for p,h in protected.items() if sha(ROOT/p)!=h]
    handoff_extended=False
    if 'AGENTS.md' in changed:
        content=(ROOT/'AGENTS.md').read_bytes();marker=b'# R304 completed'
        if marker in content and hashlib.sha256(content[content.index(marker):]).hexdigest()==protected['AGENTS.md']:
            changed.remove('AGENTS.md');handoff_extended=True
    assert not changed,changed
    save(BASE/'results/verification.json',clean(dict(utc=utc(),seconds=time.monotonic()-start,peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,models=results,protected_files=len(protected),handoff_extended_with_original_suffix_preserved=handoff_extended,changed=changed,photo_native_exact=True)))
    # Enrich saved viewer after replay; predictions remain immutable.
    path=REVIEW/'data.js';data=json.loads(path.read_text()[11:-2])
    for m in data['models']:
        rows={b['index']:b for b in read(BASE/f"results/{m['name']}-numerical.json")['checks']}
        for b in m['positions']:b['sampling_check']=rows[b['index']]
    path.write_text('const DATA='+json.dumps(clean(data),separators=(',',':'))+';\n')
if __name__=='__main__':main()

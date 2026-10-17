"""Independent native ray, correspondence arithmetic, atlas and immutable-model checks."""
from types import MethodType
import subprocess,time
import numpy as np
from PIL import Image,ImageOps
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.geometry import Chain as Original
from photo2.r305.forward import segments
from photo2.r305.diagnose import isolated
from .analysis import OUT,BASE,MODELS,models,evidence,points,D

def verify(preservation=True):
    began=time.monotonic();data,m,obs,supports=evidence();records=[];rays=0;segments_checked=0
    for name,doc,scene,raster in models():
        np.testing.assert_allclose(scene.pc,[b['projected_center'] for b in doc['positions']],atol=1e-8,rtol=0);np.testing.assert_allclose(scene.centers,[b['center'] for b in doc['positions']],atol=1e-9,rtol=0)
        # Trace through original inherited Python implementation on the unchanged scene.
        scene.trace=MethodType(Original.trace,scene)
        p=np.concatenate([points(r) for r in supports if abs(r['distance_px'])<230]);far=raster['xy'][np.linspace(0,len(raster['xy'])-1,8000).astype(int)];p=np.unique(np.concatenate([p,far]),axis=0).astype(int);tr=scene.trace(p);expected=raster['owner'][p[:,1],p[:,0]];np.testing.assert_array_equal(tr['owner'],expected);np.testing.assert_array_equal(tr['unknown'],raster['unknown'][p[:,1],p[:,0]]);rays+=len(p)
        a=read(OUT/f'{name}-partA.json.gz');assert doc['parameters']==a['parameters'];assert sha(ROOT/MODELS[name][0]/f'{MODELS[name][1]}.json.gz')==a['parameter_sha256']
        for r in a['supports']:
            original=next(s for s in supports if s['id']==r['id']);pts=points(original);actual=np.mean(raster['address'][pts[:,1],pts[:,0]]==r['index']);assert abs(actual-r['coherence'])<1e-12
            if abs(r['distance_px'])<230:
                for alt in r['isolated']:
                    single=isolated(scene,alt['index']);single.trace=MethodType(Original.trace,single);tr=single.trace(pts);actual=np.mean((tr['owner']>=0)&~tr['unknown']);assert abs(actual-alt['isolated_fraction'])<1e-12
        for r in a['reflections']:
            if r['predicted'] is not None:assert abs(np.linalg.norm(np.array(r['predicted'])-r['observed'])-r['error_px'])<1e-9
        for sign in [-1,1]:
            for n in [10,20,40,80,160,320]:
                prefix=next(r for r in a['prefixes'] if r['direction']==sign and r['length']==n);assert len(prefix['indices'])==n+1;assert prefix['indices'][0]==a['anchor']['index'];assert len(set(prefix['indices']))==n+1
        # Exhaustive saved boundary segments for the 641 inspected index addresses.
        keys={s['index'] for s in a['sequences']}
        for b in doc['positions']:
            if b['index'] not in keys:continue
            x,y=b['projected_center'];rad=scene.query_radius+2;x0=max(0,int(x-rad));x1=min(2540,int(x+rad)+2);y0=max(0,int(y-rad));y1=min(3182,int(y+rad)+2)
            actual=segments(raster['address'][y0:y1,x0:x1]==b['index'],x0,y0);assert actual==b['boundary_segments'];segments_checked+=len(actual)
        records.append(dict(model=name,positions=scene.n,original_rays=len(p),parameter_and_centers_exact=True,prefixes=12,inspected_addresses=len(keys)))
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');review=ROOT/'photo2/review/r310';assert np.array_equal(im,Image.open(review/'photo.png'))
    atlas=read(OUT/'atlas.json')
    for a in atlas:
        raw=Image.open(review/a['raw']);assert np.array_equal(raw,im.crop(a['crop']));panel=Image.open(review/a['image']);assert np.array_equal(raw,panel.crop((0,56,raw.width,56+raw.height)))
    if preservation:
        protected=read(BASE/'evidence/preservation.json.gz');head=read(BASE/'evidence/start.json')['head'];allowed=[]
        for p,h in protected.items():
            if sha(ROOT/p)!=h:
                assert p in ['AGENTS.md','PLAN.md','METHODS.md','REQUEST_LOG.md'];old=subprocess.check_output(['git','show',head+':'+p]);assert old in (ROOT/p).read_bytes();allowed.append(p)
        preserve=dict(files=len(protected),byte_identical=len(protected)-len(allowed),additive_handoffs=allowed,historical_science_changed=[])
    else:preserve=None
    result=dict(passed=True,utc=utc(),models=records,original_rays=rays,native_boundary_segments=segments_checked,raw_atlas_panels=len(atlas),photo_exact=True,preservation=preserve,seconds=time.monotonic()-began,physical_certificate_policy='Inherited unmodified whole-model certificates and exact centers/parameters verified; no new geometry to recertify. Support-plane proof remains conditional physical nonintersection, not photographic accuracy.')
    save(OUT/'verification.json',result);print(result)
if __name__=='__main__':verify()

"""Validate native inventory measurements, ownership and old evidence preservation."""
import json,gzip
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .experiment_r272 import ROOT,OUT,save,sha
from .brightness_r270 import color_managed_photo,linearize
from .inventory_r272 import CROSS,features,classify,component,build_region
from .climb_r268 import background

def main():
    old=json.load(open(OUT/'input-hashes.json'))
    for name,h in old.items():assert sha(ROOT/name)==h,name
    data=json.load(open(OUT/'inventory.json'));native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();np.testing.assert_array_equal(srgb,np.asarray(Image.open(OUT/'photo-srgb.png')));hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);_,paper,_=background(native);summary=json.load(open(OUT/'summary.json'));locations=list(map(json.loads,gzip.open(OUT/'location-candidates.jsonl.gz','rt')));byloc={r['id']:r for r in locations};beads=data['beads'];seen=set();pixels=0;patch_pixels=0;closed=0;maxdisplacement=0.
    assert len({b['id'] for b in beads})==len(beads);assert [b['inventory_number'] for b in beads]==list(range(1,len(beads)+1))
    for b in beads:
        x,y=b['anchor'];assert b['id']==f'B-{x:04d}-{y:04d}';assert byloc[b['candidate_id']]['trusted'];assert b['accepted'] and not b['reasons']
        f=features(hsv,lum,paper,x,y);assert classify(f,summary['palette'])[0]==b['color']
        rebuilt=build_region(byloc[b['candidate_id']],native,srgb,hsv,lum,paper,summary['palette'],f,locations)
        assert rebuilt['region']==b['region'] and rebuilt['bright_patch']==b['bright_patch'] and rebuilt['brightest']==b['brightest'] and rebuilt['accepted']
        sets={}
        for key in ('region','bright_patch'):
            coords=[(xx,yy) for yy,a,z in b[key]['runs'] for xx in range(a,z+1)];assert len(coords)==len(set(coords))==b[key]['pixel_count'];np.testing.assert_allclose(np.mean(coords,axis=0),b[key]['centroid'],atol=1e-12);sets[key]=set(coords)
            local=np.zeros((41,41),bool)
            for xx,yy in coords:local[yy-y+20,xx-x+20]=True
            assert ndi.label(local,CROSS)[1]==1
            if key=='region':assert not np.any(ndi.binary_fill_holes(local)&~local)
        assert sets['bright_patch']<=sets['region'];assert not(seen&sets['region']);seen|=sets['region'];pixels+=len(sets['region']);patch_pixels+=len(sets['bright_patch'])
        p=b['brightest'];assert (p['x'],p['y']) in sets['region'];maximum=max(lum[yy,xx] for xx,yy in sets['region']);assert p['luminance']==maximum==float(lum[y-4:y+5,x-4:x+5].max());assert (p['x'],p['y'])==min((xy for xy in sets['region'] if lum[xy[1],xy[0]]==maximum),key=lambda z:(z[1],z[0]));assert p['rgb_srgb']==srgb[p['y'],p['x']].tolist();assert p['rgb_native']==native[p['y'],p['x']].tolist()
        assert all(paper[yy,xx]==0 for xx,yy in sets['region'])
        for key in ('raw','smooth'):
            pts=np.array(b['outline'][key]);assert len(pts)>=4 and np.array_equal(pts[0],pts[-1]);assert np.isfinite(pts).all()
            # Reject any proper self-crossing of nonadjacent polygon edges.
            a=pts[:-1];v=pts[1:]-a;n=len(a)
            def cross(u,w):return u[...,0]*w[...,1]-u[...,1]*w[...,0]
            for i in range(n):
                js=np.arange(i+2,n)
                if i==0:js=js[js!=n-1]
                if not len(js):continue
                u=a[js]-a[i];den=cross(v[i],v[js]);valid=np.abs(den)>1e-12;t=np.divide(cross(u,v[js]),den,out=np.zeros(len(js)),where=valid);q=np.divide(cross(u,v[i]),den,out=np.zeros(len(js)),where=valid)
                assert not np.any(valid&(t>1e-10)&(t<1-1e-10)&(q>1e-10)&(q<1-1e-10)),(b['id'],key)
            closed+=1
        maxdisplacement=max(maxdisplacement,b['outline']['maximum_vertex_displacement']);assert b['outline']['maximum_vertex_displacement']<1.
    ownership=json.load(open(OUT/'synthetic-ownership.json'));assert ownership['background_pixels']==ownership['other_body_pixels']==ownership['duplicate_bodies']==0 and ownership['accepted']>0
    audit=json.load(open(OUT/'requirement-failures.json'));diagnostic=list(map(json.loads,gzip.open(OUT/'single-gate-diagnostics.jsonl.gz','rt')));assert len(diagnostic)==audit['audited_single_failure_candidates'];assert not({r['candidate_id'] for r in diagnostic}&{b['candidate_id'] for b in beads});assert all(r['diagnostic_only'] and r['passes_remaining_checks']==(not r['other_failures']) for r in diagnostic)
    assert 'Ran 12 tests' in (OUT/'tests.log').read_text() and (OUT/'tests.log').read_text().rstrip().endswith('OK')
    save('validation.json',dict(status='pass',unit_tests=12,accepted=len(beads),exact_region_pixels=pixels,exact_patch_pixels=patch_pixels,closed_simple_contours_checked=closed,max_display_vertex_displacement=maxdisplacement,old_hashes_preserved=len(old),source_icc_pixels_verified=True,all_masks_recomputed=True,counts_centroids_rgb_hsv_peaks_and_id_ties_checked=True,no_accepted_ownership_overlap=True,synthetic_scenes=ownership['scenes'],synthetic_accepted=ownership['accepted'],synthetic_background_pixels=0,synthetic_other_body_pixels=0,diagnostic_only_candidates=len(diagnostic)))
    print((OUT/'validation.json').read_text())
if __name__=='__main__':main()

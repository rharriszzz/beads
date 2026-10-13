"""Delivery checks of saved decisions, native measures, paths and preservation."""
import gzip,json,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from skimage.morphology import local_maxima
from .experiment_r271 import ROOT,OUT,save,sha
from .brightness_r270 import color_managed_photo,linearize,sums,SCALE,Search
from .climb_r268 import background
from .search_r269 import Policy
from .trusted_r271 import Criteria

def load(name):return [json.loads(s) for s in gzip.open(OUT/name,'rt')]
def main():
    start=time.monotonic();old=json.load(open(OUT/'input-hashes.json'))
    for name,digest in old.items():assert sha(ROOT/name)==digest,name
    native=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));srgb,_=color_managed_photo();hsv,paper,_=background(native)
    lum=255*(linearize(srgb.astype(float)/255)@np.array([.2126,.7152,.0722]));q=np.rint(lum*SCALE).astype(np.int64);ss={n:sums(q,n) for n in (5,7,9)}
    maps=dict(np.load(OUT/'candidate-and-background-maps.npz'));np.testing.assert_array_equal(maps['background'],paper);np.testing.assert_array_equal(maps['mean7_maxima'],local_maxima(ss[7],connectivity=2,allow_borders=True)&(ss[7]>=0))
    rows=load('all-candidates.jsonl.gz');index={r['id']:r for r in rows};inventory=np.zeros(q.shape,bool);c=Criteria();accepted=[]
    for r in rows:
        x,y=r['x'],r['y'];assert abs(r['mean_y']-ss[7][y,x]/(SCALE*49*255))<1e-12
        for xx,yy in r['plateau_pixels']:assert maps['mean7_maxima'][yy,xx] and ss[7][yy,xx]==ss[7][y,x];inventory[yy,xx]=True
        assert r['trusted']==(not r['reasons']);assert len(r['explanations'])==len(r['reasons'])
        if r['trusted']:
            accepted.append((x,y));assert r['mean_y']>=c.minimum_mean_y and r['lit_fraction']>=c.minimum_lit_fraction and r['core_pixels']>=c.minimum_core_pixels and r['window_ratio']>=c.minimum_window_ratio and r['local_contrast']>=c.minimum_local_contrast
            assert r['plateau_diameter']<=c.maximum_plateau_diameter and r['endpoint_spread']<=c.maximum_endpoint_spread and r['background_pixels']==0
            assert not np.any(paper[y-4:y+5,x-4:x+5]);assert r['primary_endpoint']==[x,y];assert not any(z['ambiguous'] for z in r['rivals'])
    np.testing.assert_array_equal(inventory,maps['mean7_maxima']);moves=0;paths=0
    for t in load('search-traces.jsonl.gz'):
        row=index[t['id']];x,y=row['x'],row['y'];cut=np.s_[y-21:y+22,x-21:x+22];graphs={}
        for r in t['searches']:
            n=r['window']
            if n not in graphs:graphs[n]=Search(q[cut],hsv[cut],paper[cut],ss[n][cut],n,(21,21),'Y')
            g=graphs[n];path=[dict(p,x=p['x']-x+21,y=p['y']-y+21) for p in r['path']];policy=Policy(r['raw_allowance'],r['mean_allowance']);moves+=g.audit_path(path,r['radius'],policy);paths+=1
            for p in r['path']:
                px,py=p['x'],p['y'];assert p['sum_q']==ss[n][py,px];assert p['raw']==q[py,px]/SCALE;assert p['mean']==ss[n][py,px]/(SCALE*n*n)
            result=g.search(r['radius'],policy);assert list(g.xy[result['end']]+[x-21,y-21])==r['endpoint']
        endpoints=np.array([r['endpoint'] for r in t['searches']]);spread=float(np.sqrt(((endpoints[:,None]-endpoints[None,:])**2).sum(axis=2)).max());assert spread==row['endpoint_spread']
    from scipy.spatial.distance import pdist
    assert np.all(pdist(accepted)>c.final_conflict_distance)
    synth=load('synthetic-candidates.jsonl.gz');truth=np.load(ROOT/'photo2/review/r270/synthetic-truth.npz');si={(r['scene'],r['id']):r for r in synth};counts=Counter();bodycounts=Counter();routecounts=Counter()
    for r in synth:
        assert r['truth_body']==truth[r['scene']][r['y'],r['x']]
        if r['trusted']:counts['accepted']+=1;counts['background']+=r['truth_body']==0;bodycounts[r['scene'],r['truth_body']]+=1
    for t in load('synthetic-traces.jsonl.gz'):
        r=si[t['scene'],t['id']]
        if not r['trusted']:continue
        for path in t['searches']:
            ids=[int(truth[t['scene']][p['y'],p['x']]) for p in path['path']];routecounts['routes']+=1;routecounts['background']+=0 in ids;routecounts['other_body']+=any(i not in (0,r['truth_body']) for i in ids)
    assert counts['background']==0 and max(bodycounts.values())==1 and routecounts['background']==0 and routecounts['other_body']==0
    tests=(OUT/'tests.log').read_text();assert 'Ran 9 tests' in tests and tests.rstrip().endswith('OK')
    checks=json.load(open(OUT/'review-checks.json'));shadow=next(z for z in checks if z['case']=='shadowed-neighbor');assert not shadow['candidate']['trusted'] and 'insufficient-light' in shadow['candidate']['reasons']
    save('validation.json',dict(status='pass',tests=9,old_hashes_preserved=len(old),photo_candidates=len(rows),trusted=len(accepted),native_maximum_pixels=int(inventory.sum()),photo_stability_paths=paths,checked_photo_moves=moves,synthetic_locations=dict(counts),synthetic_accepted_paths=dict(routecounts),review_shadow_excluded=True,review_coordinates_are_evaluation_only=True,elapsed_seconds=time.monotonic()-start))
    print((OUT/'validation.json').read_text())
if __name__=='__main__':main()

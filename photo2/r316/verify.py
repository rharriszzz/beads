"""Independent support formulas, original Python rays, exact saved-state/metric replay."""
import time,re,subprocess
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r295.geometry import AXES,Chain as Python
from photo2.r315.diagnose import brackets
from photo2.r315.measurement import measure_readiness
from .model import Chain
OUT=ROOT/'photo2/r316/results'


def independent_support(s,n,t):
    dot=n@t;rad=np.linalg.norm(np.cross(n,t));r=s.edge if s.exterior else (1-s.hole)*s.rounding/2;f=s.face if s.exterior else s.rounding
    return s.radius*((1-r)*rad+.7*s.axial*(1-f)*abs(dot)+np.hypot(r*rad,.7*s.axial*f*dot))


def original(s,xy):
    # Explicit small chunks avoid dynamic-dispatch recursion into compiled trace.
    parts=[Python.trace(s,xy[i:i+3000]) for i in range(0,len(xy),3000)]
    return {k:np.concatenate([t[k] for t in parts]) for k in ['owner','unknown']}


def main():
    start=time.monotonic();data=load()[0];e=engine();rows=[]
    for p in sorted(OUT.glob('*-model.json.gz')):
        r=read(p);s=Chain(r['parameters'],data);name=r['name'];a=np.load(OUT/f'{name}-raster.npz');np.testing.assert_array_equal(s.indices,r['positions']['indices']);np.testing.assert_array_equal(s.centers,r['positions']['centers']);np.testing.assert_array_equal(s.pc,r['positions']['projected']);assert list(s.indices[(s.indices>=-100)&(s.indices<=99)])==list(range(-100,100))
        for k in AXES:np.testing.assert_array_equal(s.g[k],r['positions']['frames'][k])
        pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');ws={tuple(w['pair']):w for w in r['physical']['witnesses']};assert len(ws)==len(pairs);mins=[]
        for i,j in pairs:
            w=ws[int(i),int(j)];n=np.array(w['normal']);gap=(s.centers[j]-s.centers[i])@n-independent_support(s,n,s.g[AXES[0]][i])-independent_support(s,-n,s.g[AXES[0]][j]);assert abs(gap-w['gap_units'])<1e-9;assert gap>1e-6;mins.append(float(gap))
        for split,k in enumerate(['development','comparison','buffer']):
            metric=e.measure(a['owner'],a['unknown'],s.indices,split,True);assert metric==r[k],(name,k);assert measure_readiness(e,a,metric,split)==r['readiness'][k]
        assert brackets(e,a)==read(OUT/f'{name}-brackets.json.gz');assert not a['unknown'].any()
        ix=np.unique(np.r_[np.arange(0,len(e.xy),113),np.flatnonzero(e.m['core'].ravel())[::7],np.flatnonzero(e.m['edges'].any(0).ravel())[::3]]);py=original(s,e.xy[ix]);known=~py['unknown'];np.testing.assert_array_equal(py['owner'][known],a['owner'][ix][known]);tt=np.load(OUT/f'{name}-target.npz');j=np.arange(0,len(tt['xy']),29);pt=original(s,tt['xy'][j]);kk=~pt['unknown'];np.testing.assert_array_equal(pt['owner'][kk],tt['owner'][j][kk]);assert not tt['unknown'].any()
        for c in r['target']['visible_counts']:assert c['pixels']==int(np.sum(tt['owner']==np.flatnonzero(s.indices==c['index'])[0]))
        rows.append(dict(name=name,positions=s.n,contact_witnesses=len(pairs),minimum_support_margin=min(mins),original_python_rays=len(ix)+len(j),python_unresolved=int(py['unknown'].sum()+pt['unknown'].sum()),full_target_rays=len(tt['xy']),metrics_exact=True));print('verified',name,flush=True)
    manifest=read(OUT/'review-manifest.json')
    for item in manifest:
        x,y=np.array(item['crop_origin'])-e.m['origin'];raw=e.m['native'][y:y+121,x:x+121];im=np.array(Image.open(OUT/item['image']));np.testing.assert_array_equal(im[38:401:3,0:363:3],raw)
        crop=np.load(OUT/item['arrays']);mask=crop['isolated'];assert not (mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any())
    for p in (OUT/'review').glob('*.png'):
        with Image.open(p) as im:im.verify()
    links=re.findall(r'(?:src|href)="([^"]+)"',(OUT/'index.html').read_text())
    for link in links:assert (OUT/link).exists(),link
    ledger=read(OUT/'ledger.json.gz')
    for r in ledger:
        for c in r['candidates']:
            assert c['visible_fraction']<=c['isolated_fraction']+1e-10
            for o in c['occluders']:assert o['depth_margin_min']>=-1e-6
    assert sha(ROOT/'photo2/r314/evidence/maps.npz')==read(OUT/'start.json')['evidence_sha']
    parent=read(OUT/'start.json')['head'];changed=subprocess.check_output(['git','diff','--diff-filter=MDRT',parent,'--name-only'],cwd=ROOT,text=True).splitlines()
    for p in changed:
        assert p in ['AGENTS.md','SESSION_HANDOFF.md','REQUEST_LOG.md'],p
        assert subprocess.check_output(['git','show',parent+':'+p],cwd=ROOT) in (ROOT/p).read_bytes()
    for name in ['benchmark-summary.json','fixtures.json','clipping.json','cache-benchmark.json']:assert read(OUT/name)['passed'],name
    sources={str(p.relative_to(ROOT)):sha(p) for folder in ['r314','r315','r316'] for p in sorted((ROOT/'photo2'/folder).glob('*.py'))}
    save(OUT/'verification.json',dict(passed=True,utc=utc(),seconds=time.monotonic()-start,models=rows,raw_photo_crops_exact=len(manifest),ledger_records=len(ledger),local_links=len(links),historical_changes=changed,evidence_unchanged=True,source_hashes=sources,policy='All selected positions and full-necklace separation witnesses replay; sampled independent Python rays compare only known oracle rays, unresolved counts explicit. Numerical equality is not photographic reconstruction.'))
if __name__=='__main__':main()

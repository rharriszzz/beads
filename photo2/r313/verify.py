"""Fresh-process original Python ray audit, independent contacts and exact saved metrics."""
import time,subprocess,re,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import Chain as Python,AXES
from photo2.r295.physical_audit import independent_support
from .objective import Objective,scene

def run(out):
    began=time.monotonic();out=Path(out);ev=out.parent/'evidence';doc=read(ev/'freeze.json');m=dict(np.load(ev/'maps.npz'))
    assert sha(ev/'maps.npz')==doc['maps_sha256'];engine=Objective(m,doc);data,_,_=load();rows=[]
    frozen=read(ev/'fitting-freeze.json') if (ev/'fitting-freeze.json').exists() else None
    if frozen:
        for path,h in frozen['sources'].items():assert sha(ROOT/path)==h,path
    for path in sorted((out/'models').glob('*.json.gz')):
        model=read(path);s=scene(model['parameters'],data,model['implementation']);raster=dict(np.load(path.with_name(model['name']+'.npz')))
        np.testing.assert_array_equal(s.indices,model['positions']['indices']);np.testing.assert_allclose(s.centers,model['positions']['centers'],atol=1e-12,rtol=0)
        assert s.indices[(s.indices>=-100)&(s.indices<=99)].tolist()==list(range(-100,100))
        for key in AXES:np.testing.assert_allclose(s.g[key],model['positions']['frames'][key],atol=1e-12,rtol=0)
        # Independent complete candidate-pair enumeration and literal support formula.
        pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');cert=model['physical'];witness={tuple(r['pair']):r for r in cert['witnesses']}
        assert len(pairs)==len(witness),(model['name'],len(pairs),len(witness));gaps=[]
        for a,b in pairs:
            r=witness[(int(a),int(b))];n=np.array(r['normal']);gap=float((s.centers[b]-s.centers[a])@n-independent_support(n,s.g[AXES[0]][a],s.radius,s.axial)-independent_support(n,s.g[AXES[0]][b],s.radius,s.axial))
            assert gap>1e-6;assert abs(gap-r['gap_units'])<1e-9;gaps.append(gap)
        # Stratified sample includes all evidence kinds and worst local transition pixels.
        ix=np.unique(np.r_[np.linspace(0,len(engine.xy)-1,2000).astype(int),np.flatnonzero(m['material'].ravel())[::9],np.flatnonzero(m['edges'].any(0).ravel()),np.flatnonzero(m['paper'].ravel())[::25]])
        xy=engine.xy[ix];t=time.monotonic();fast=s.trace(xy);fast_seconds=time.monotonic()-t
        # Bind the original method so recursive batches cannot dispatch to fast trace.
        original=s.trace
        from types import MethodType
        s.trace=MethodType(Python.trace,s);t=time.monotonic();slow=s.trace(xy);slow_seconds=time.monotonic()-t;s.trace=original
        np.testing.assert_array_equal(fast['owner'],slow['owner']);np.testing.assert_array_equal(fast['unknown'],slow['unknown'])
        np.testing.assert_array_equal(slow['owner'],raster['owner'][ix]);np.testing.assert_array_equal(slow['unknown'],raster['unknown'][ix])
        for split,label in [(0,'development'),(1,'comparison')]:
            actual=engine.measure(raster['owner'],raster['unknown'],s.indices,split,True)
            assert actual==model[label],(model['name'],label)
        rows.append(dict(name=model['name'],positions=s.n,target_positions=200,independent_contact_pairs=len(pairs),minimum_independent_margin=min(gaps),original_python_rays=len(ix),fast_seconds=fast_seconds,original_seconds=slow_seconds,exact_owners=True,exact_unknown=True,exact_metrics=True))
        print('verified',model['name'],len(ix),'Python rays',len(pairs),'contacts',flush=True)
    # Every old tracked file must remain byte-identical except additive handoff.
    before=read(ev/'start.json')['head'];diff=subprocess.check_output(['git','diff',before,'--name-only'],cwd=ROOT,text=True).splitlines()
    allowed=['AGENTS.md','SESSION_HANDOFF.md','REQUEST_LOG.md']
    for path in diff:
        assert path in allowed,path
        prior=subprocess.check_output(['git','show',before+':'+path],cwd=ROOT);assert prior in (ROOT/path).read_bytes(),path
    images=[];links=[]
    for p in (out/'review').glob('*.png'):
        with Image.open(p) as image:image.verify()
        images.append(p.name)
    if (out/'index.html').exists():
        for link in re.findall(r'(?:src|href)="([^"]+)"',(out/'index.html').read_text()):
            if link=='verification.json':continue
            assert (out/link).exists(),link;links.append(link)
    trials=[read(p) for p in sorted((out/'trials').glob('*.json.gz'))]
    if (out/'selection.json').exists():
        selected=read(out/'selection.json');assert selected['sealed'];assert len(trials)==selected['evaluations']
        feasible=[r for r in trials if r['feasible']];assert abs(min(r['score'] for r in feasible)-selected['selected']['score'])<1e-12
        assert selected['seconds']<=frozen['seconds']+5
    result=dict(passed=True,utc=utc(),models=rows,positions=sum(r['positions'] for r in rows),independent_contacts=sum(r['independent_contact_pairs'] for r in rows),original_python_rays=sum(r['original_python_rays'] for r in rows),trials=len(trials),pngs_checked=len(images),local_links_checked=len(links),historical_modified_files=diff,seconds=time.monotonic()-began,limitation='Original Python ray agreement is sampled; full saved-raster metrics and complete pair contact witnesses are checked. No physical identity or boundary ground truth is established.')
    save(out/'verification.json',result);print('PASS',result['seconds'],flush=True);return result

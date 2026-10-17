"""Independent full-chain certificates, original Python rays, arithmetic and history."""
import time,subprocess,re
from types import MethodType
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import Chain as Python,AXES
from photo2.r295.contact_fallback import audit_pair
from .run import OUT,EV,engine,make,merit
from .objective import acceptance

def support(s,n,t):
    dot=np.sum(n*t,axis=-1);rad=np.linalg.norm(np.cross(n,t),axis=-1)
    edge=s.edge if s.exterior else (1-s.hole)*s.rounding/2
    face=s.face if s.exterior else s.rounding
    return s.radius*((1-edge)*rad+.7*s.axial*(1-face)*abs(dot)+np.hypot(edge*rad,.7*s.axial*face*dot))

def main():
    began=time.monotonic();data,_,_=load();eng=engine();selection=read(OUT/'selection.json');assert selection['sealed'];checks=[];base=read(OUT/'models/R306-2405.json.gz')
    assert sha(EV/'maps.npz')==selection['sources'].get('unused',read(OUT/'search-plan.json')['evidence_sha256'])
    for p,h in selection['sources'].items():assert sha(ROOT/p)==h,p
    # Old evidence and all old tracked sources/results must be byte-unchanged.
    old=np.load(ROOT/'photo2/r313/evidence/maps.npz')
    for k in ['material','paper','core','color','xy','native','roi','split','arc']:np.testing.assert_array_equal(old[k],eng.m[k])
    diff=subprocess.check_output(['git','diff','--name-only','--diff-filter=MDRCT',read(OUT/'start.json')['head']],text=True).splitlines()
    allowed={'REQUEST_LOG.md','AGENTS.md','INITIAL_QUESTION.md','METHODS.md'}
    assert set(diff)<=allowed,diff
    for p in diff:
        before=subprocess.check_output(['git','show',read(OUT/'start.json')['head']+':'+p]);after=(ROOT/p).read_bytes();assert before in after,p
    for path in sorted((OUT/'models').glob('*.json.gz')):
        r=read(path);s=make(r['parameters'],data);a=np.load(path.with_name(r['name']+'.npz'));np.testing.assert_allclose(s.centers,r['positions']['centers'],atol=1e-12,rtol=0);np.testing.assert_allclose(s.pc,r['positions']['projected'],atol=1e-12,rtol=0);np.testing.assert_array_equal(s.indices,r['positions']['indices']);assert r['cohort']==list(range(-100,100));assert r['cohort_positions']==200
        frames=np.stack([s.g[k] for k in AXES],1);np.testing.assert_allclose(frames@frames.transpose(0,2,1),np.broadcast_to(np.eye(3),frames.shape),atol=1e-9)
        pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');ws={tuple(w['pair']):w for w in r['physical']['witnesses']};assert len(pairs)==len(ws);minimum=1e9
        for i,j in pairs:
            w=ws[int(i),int(j)];n=np.array(w['normal']);gap=float((s.centers[j]-s.centers[i])@n-support(s,n,s.g[AXES[0]][i])-support(s,n,s.g[AXES[0]][j]));assert abs(gap-w['gap_units'])<1e-9;minimum=min(minimum,gap)
            if w['separated']:assert gap>1e-6
            else:assert audit_pair(s,int(i),int(j),max_depth=16,max_nodes=300000)['state']=='certified-nonintersection'
        ix=np.unique(np.r_[np.linspace(0,len(eng.xy)-1,1600).astype(int),np.flatnonzero(eng.m['material'].ravel())[::17],np.flatnonzero(eng.m['paper'].ravel())[::31],np.flatnonzero(eng.m['edges'].any(0).ravel())]);method=s.trace;s.trace=MethodType(Python.trace,s);tr=s.trace(eng.xy[ix]);s.trace=method;np.testing.assert_array_equal(tr['owner'],a['owner'][ix]);np.testing.assert_array_equal(tr['unknown'],a['unknown'][ix])
        for split,k in enumerate(['development','comparison','buffer']):assert eng.measure(a['owner'],a['unknown'],s.indices,split,True)==r[k],(r['name'],k)
        target=np.load(OUT/'target-rasters'/f'{r["name"]}.npz');tix=np.linspace(0,len(target['xy'])-1,1200).astype(int);s.trace=MethodType(Python.trace,s);tt=s.trace(target['xy'][tix]);s.trace=method;np.testing.assert_array_equal(tt['owner'],target['owner'][tix]);np.testing.assert_array_equal(tt['unknown'],target['unknown'][tix])
        checks.append(dict(name=r['name'],positions=s.n,target=200,contacts=len(pairs),minimum_margin=minimum,original_python_rays=len(ix)+len(tix),metrics_exact=True));print('VERIFY',r['name'],flush=True)
    trials=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];assert len(trials)==selection['evaluations'];assert len({r['id'] for r in trials})==len(trials)
    for b in selection['best']:
        candidates=[r for r in trials if r['start']==b['start'] and r['feasible']]+[read(OUT/'models'/f'{b["start"]}.json.gz')];best=min(candidates,key=merit);assert list(merit(best))==b['merit'];assert best['parameters']==b['parameters']
    # Replay every stored actual penetration point independently against both solids.
    witnessed=0
    for r in trials:
        if r['classification']!='demonstrated-interpenetration':continue
        s=make(r['parameters'],data)
        for c in r['physical']['actual_solid_checks']:
            if c['state']!='demonstrated-interpenetration':continue
            xyz=np.array(c['point'])
            for j in c['pair']:
                frame=np.array([s.g[k][j] for k in AXES]);assert float(s.local_sdf((xyz-s.centers[j])@frame.T))< -1e-7
            witnessed+=1
    ctl=read(OUT/'controls.json')['cases'];assert ctl[0]['metrics']['vector']==ctl[1]['metrics']['vector'];assert all(not c['acceptance']['passed'] for c in ctl[2:])
    np.testing.assert_array_equal(np.array(Image.open(OUT/'review/original-native.png')),eng.m['native']);links=[]
    for ref in re.findall(r'(?:href|src)="([^"]+)"',(OUT/'index.html').read_text()):
        if ref.startswith(('http','#')):continue
        if ref!='verification.json':assert (OUT/ref).resolve().exists(),ref
        links.append(ref)
    for p in (OUT/'review').glob('*.png'):
        with Image.open(p) as im:im.verify()
    save(OUT/'verification.json',dict(passed=True,utc=utc(),seconds=time.monotonic()-began,models=checks,trials=len(trials),penetration_witnesses=witnessed,old_tracked_files_unchanged_except_additive_handoffs=True,raw_pixels_exact=True,links=len(links),search_sources_exact=True,measurement_arrays_preserved=True,limitations='Computational reproduction and necessary physical separation, not photographic truth or settled mechanical equilibrium.'))
    assert (OUT/'verification.json').exists()
if __name__=='__main__':main()

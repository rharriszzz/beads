"""Bounded structural controls, physical feasibility classifications, no adoption."""
from copy import deepcopy
import time
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r313.objective import Objective,scene
from .geometry_experiment import ShapeChain,ShapeLegacy,contacts,paper
from photo2.r295.geometry import Chain as Python,AXES
from types import MethodType

OUT=ROOT/'photo2/r313/continuation'
def make(p,data,implementation):return ShapeLegacy(p,data) if implementation in ['R297','R313-R297'] else ShapeChain(p,data)

def evaluate(p,data,engine,implementation,detail=False,contact_seconds=.4):
 began=time.monotonic();s=make(p,data,implementation);placed=time.monotonic();cert=contacts(s,seconds=contact_seconds);checked=time.monotonic()
 # An unresolved contact alternative is rendered diagnostically rather than discarded.
 # Its score NEVER makes it physically admissible without a complete certificate.
 tr=s.trace(engine.xy);rendered=time.monotonic();r=dict(parameters=p,implementation='R313-R297' if isinstance(s,ShapeLegacy) else 'R313-R306',feasible=cert['certified'],physical=cert,development=engine.measure(tr['owner'],tr['unknown'],s.indices,0,detail),paper=paper(s),seconds=time.monotonic()-began)
 if detail:r['comparison']=engine.measure(tr['owner'],tr['unknown'],s.indices,1,True)
 r['profile']=dict(geometry=placed-began,contact=checked-placed,render=rendered-checked,measure=time.monotonic()-rendered)
 return r,s,tr

def main():
 began=time.monotonic();data,_,_=load();ev=ROOT/'photo2/r313/evidence';maps=dict(np.load(ev/'maps.npz'));eng=Objective(maps,read(ev/'freeze.json'))
 bases=[]
 for name in ['R306-2405','R309-2733','R312-local','R313-initial-R297-2337']:
  row=read(ROOT/f'photo2/r313/results/models/{name}.json.gz');bases.append((name,row))
 # Exact old-shape identity and independent new-shape Python-ray/support check.
 checks=[];rng=np.random.default_rng(31302);xy=eng.xy[rng.choice(len(eng.xy),4000,replace=False)]
 for name,row in bases:
  s=make(row['parameters'],data,row['implementation']);old=scene(row['parameters'],data,row['implementation']);a=s.trace(xy);b=old.trace(xy)
  np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown']);np.testing.assert_allclose(s.centers,old.centers,rtol=0,atol=1e-12)
  n=rng.normal(size=(100,3));n/=np.linalg.norm(n,axis=1)[:,None];t=s.g[AXES[0]][:100];np.testing.assert_allclose(s.support(n,t),old.support(n,t),atol=1e-12,rtol=0)
  checks.append(dict(name=name,unchanged_shape_native_owner_exact=True,positions_exact=True,support_exact=True,rays=4000))
 p=deepcopy(bases[0][1]['parameters']);p.update(hole=.35,rounding=.5,trajectory_mix=.5);s=make(p,data,'R306');a=s.trace(xy);method=s.trace;s.trace=MethodType(Python.trace,s);b=s.trace(xy);s.trace=method
 np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown']);checks.append(dict(name='new_shape_trajectory',original_python_exact=True,rays=4000))
 save(OUT/'geometry-preflight.json',dict(passed=True,checks=checks,seconds=time.monotonic()-began,shape_formula='Rounded rectangle in radial/axial cross section; shared hole radius/outer-radius h and round fraction. Outer radius and axial halfheight retained. h=.14,round=.8 exactly reproduce original.',orientation='Spherical interpolation of existing body axis toward numerical derivative of the actual helical center trajectory. Mix0 reproduces existing; mix1 is trajectory alignment, not assumed truth.'))
 cases=[]
 for name,row in bases:
  p=row['parameters'];cases.append((name,'unchanged',deepcopy(p),row['implementation']))
  for mix in [-.5,.25,.5,.75,1.]:
   q=deepcopy(p);q['trajectory_mix']=mix;cases.append((name,f'trajectory-{mix}',q,row['implementation']))
  for tilt in [-83.,-45.,45.,83.]:
   q=deepcopy(p);q['tilt']=tilt;cases.append((name,f'tilt-{tilt}',q,row['implementation']))
  for hole,rounding in [(.03,.8),(.30,.8),(.50,.8),(.14,.4),(.14,1.),(.30,1.)]:
   q=deepcopy(p);q.update(hole=hole,rounding=rounding);cases.append((name,f'hole-{hole}-round-{rounding}',q,row['implementation']))
  for mix,axial in [(1.,.5),(.5,.6),(-.5,.6)]:
   q=deepcopy(p);q.update(trajectory_mix=mix,axial=axial,minor=p['minor']*1.1);cases.append((name,f'coupled-trajectory-{mix}-axial-{axial}',q,row['implementation']))
 save(OUT/'diagnostic-plan.json',dict(utc=utc(),cases=[dict(base=n,kind=k,parameters=p,implementation=i) for n,k,p,i in cases],sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).with_name('geometry_experiment.py'),Path(__file__).with_name('shape_kernel.cpp')]},evidence_sha256=sha(ev/'maps.npz'),new_observations=False))
 rows=[]
 for j,(name,kind,p,impl) in enumerate(cases):
  r,s,tr=evaluate(p,data,eng,impl,True);r.update(id=j,base=name,kind=kind)
  # Preserve geometry/rasters even for failed physical candidates for diagnosis only.
  np.savez_compressed(OUT/'diagnostic-rasters'/f'{j:03d}.npz',owner=tr['owner'],unknown=tr['unknown']) if (OUT/'diagnostic-rasters').exists() else None
  save(OUT/'diagnostics'/f'{j:03d}.json.gz',r);rows.append(dict(id=j,base=name,kind=kind,classification=r['physical']['classification'],score=r['development']['score'],comparison=r['comparison']['score'],failed_envelopes=r['physical']['unresolved_pairs'],paper=r['paper']))
  print(j,name,kind,r['physical']['classification'],round(r['development']['score'],4),flush=True)
 save(OUT/'diagnostic-summary.json',dict(rows=rows,seconds=time.monotonic()-began))
if __name__=='__main__':main()

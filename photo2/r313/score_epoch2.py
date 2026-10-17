import numpy as np
from pathlib import Path
from photo2.r297.common import ROOT,read,save,sha,utc
from .objective_v2 import SurfaceObjective

def main():
 out=ROOT/'photo2/r313/continuation';original=ROOT/'photo2/r313/results';ev=out.parent/'evidence';m=dict(np.load(ev/'maps.npz'));eng=SurfaceObjective(m,read(ev/'freeze.json'));rows=[]
 for path in sorted((original/'models').glob('*.json.gz')):
  model=read(path);raster=np.load(path.with_name(model['name']+'.npz'));idx=np.array(model['positions']['indices']);dev=eng.measure(raster['owner'],raster['unknown'],idx,0,True);comp=eng.measure(raster['owner'],raster['unknown'],idx,1,True)
  rows.append(dict(name=model['name'],development=dev,comparison=comp,parameters=model['parameters'],implementation=model['implementation']));print(model['name'],dev['score'],dev['owner_specific_terms'],flush=True)
 save(out/'epoch2-baselines.json',rows)
 # Preserve epoch1 failures and score corrections; photo map bytes identical.
 save(out/'epoch2-freeze.json',dict(utc=utc(),source_sha256=sha(Path(__file__).with_name('objective_v2.py')),maps_sha256=sha(ev/'maps.npz'),reason='Initial score accepts material-coverage gains despite visibly wrong individual outlines. Add largest-core miss distances and owner-specific external transitions; no hole edge may substitute for an exterior in the added term. Original score and photographic maps unchanged.',limitations='Partial transitions cannot establish complete contours. Same-color/core identity ambiguities and unsupported black surfaces remain unidentifiable. This objective is a search instrument, never sufficient for adoption.'))
if __name__=='__main__':main()

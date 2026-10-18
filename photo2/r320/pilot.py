"""Structured physical grid; all proposals serialized, no photo-based packing."""
import time,itertools
from collections import Counter
from photo2.r297.common import ROOT,save,read,utc,sha
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from .model import parameters,derive
OUT=ROOT/'photo2/r320/results'
def main():
 data=load()[0];rows=[];start=time.perf_counter()
 counts=[2000,2200,2404,2405,2406,2600,2800,3000,3200]
 radii=[1.35,1.65,1.95,2.25];axials=[.65,.85,1.05,1.25]
 save(OUT/'start.json',dict(start='2026-10-18T04:10:01Z',scientific_cutoff='2026-10-18T04:34:01Z',deadline='2026-10-18T04:40:01Z',photo_sha256=sha(ROOT/'beads-photo-2.jpg'),counts=counts,radii=radii,axials=axials,hands=[-1,1]))
 for n,r,a,h in itertools.product(counts,radii,axials,[-1,1]):
  p=parameters(n,r,a,h);s,z=derive(p,data)
  # A broad grid retains all circumference ratios, but only close-rise models
  # qualify for the primary optical pilot. Wider ones are explicit controls.
  if not z['certified']:
   c=contacts(s,seconds=.15);z['classification']=c['classification'];z['solid_checks']=c['actual_solid_checks']
  z.update(id=len(rows),parameters=s.p,utc=utc());rows.append(z)
  save(OUT/'physical-trials'/f'{z["id"]:04}.json.gz',z)
  if len(rows)%32==0:print('GRID',len(rows),Counter(q['classification'] for q in rows),'eligible',sum(q['eligible'] for q in rows),flush=True)
 save(OUT/'physical-grid.json',dict(rows=rows,seconds=time.perf_counter()-start,unique=len(rows),counts=counts,radii=radii,axials=axials,hands=[-1,1]))
 print('FINISHED',len(rows),time.perf_counter()-start,flush=True)
if __name__=='__main__':main()

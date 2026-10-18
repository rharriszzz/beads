from photo2.r321.packing import *
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r297.common import save,ROOT
D=load()[0];out=[]
for a in [.55,.65,.75,.85,1.05,1.25]:
 z=straight_reference(2800/431,a);print('straight',a,z,flush=True);out.append(z)
save(ROOT/'photo2/r321/results/straight-reference.json',out)
for n in [2200,2600,2800,3000]:
 for a in [.65,.75,.85]:
  s,z=derive(parameters(n,1.95,a),D);c=contacts(s,seconds=.15);print('closed',n,a,s.p['minor'],c['classification'],c['minimum_gap_units'],flush=True)

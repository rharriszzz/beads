"""Few joint radius/thickness/centerline/registration interventions."""
from copy import deepcopy
import itertools
import numpy as np
from photo2.r297.common import save
from .continue_campaign import resumed
from .campaign import OUT
from .model import corrected

def main():
 c=resumed()
 for parent_id in [98,109]:
  parent=c.rows[parent_id]
  for sign1,sign2,sign3 in itertools.product([-1,1],repeat=3):
   p=deepcopy(parent['parameters']);p['radius']+=.025*sign1;p['axial']+=.018*sign2;p['phase']+=.06*sign3;p['s0']=2.*sign2
   co=np.zeros(32);co[0]=sign3*2.;co[14]=sign2*1.;p=corrected(p,co)
   c.trial(p,'joint-physical-centerline-registration',dict(parent=parent_id,signs=[sign1,sign2,sign3]))
 save(OUT/'campaign-summary.json',dict(trials=len(c.rows),certified=sum(r['contact']['certified'] for r in c.rows),optical=sum('optical' in r for r in c.rows)))
if __name__=='__main__':main()

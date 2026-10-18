"""Contact-derived curvature spacing epoch, preserving previous frozen maps."""
from copy import deepcopy
import itertools
from photo2.r297.common import ROOT,read,save
from .campaign import Campaign,OUT
from .packing import parameters

def resumed():
 c=Campaign();c.rows=[read(f) for f in sorted((OUT/'trials').glob('*.gz'))]
 for f in OUT.glob('epoch-N*-h*.json.gz'):
  z=read(f);p=z['parameters'];c.maps[(p['count'],p['hand'])]=z
 return c

def main():
 c=resumed()
 # Same physical inputs across modes; important causal comparison, not extra
 # independent basins. The old correspondence maps remain frozen.
 for n,r,a,h in itertools.product([2400,2600,2800,2801,3000,3200],[1.85,1.95,2.05],[.85],[-1,1]):
  c.trial(parameters(n,r,a,h),'curvature-density')
 # Dense contact branches around the known photographed-size failure.
 for n,a,h in itertools.product([2600,2800,3000],[.9,.95],[-1,1]):
  c.trial(parameters(n,1.95,a,h),'curvature-thickness')
 save(OUT/'campaign-summary.json',dict(trials=len(c.rows),certified=sum(r['contact']['certified'] for r in c.rows),optical=sum('optical' in r for r in c.rows)))
if __name__=='__main__':main()

from .common import *
from .traverse import run

def main():
 g,b,p,ss=inputs();summary=[];base=canonical(ss[0])
 for label,origin,direction,width in [('inward-forward-width128',124,1,128),('inward-reverse-width128',124,-1,128),('outer-bend-forward',35,1,32),('outer-bend-reverse',35,-1,32)]:
  z=run(b,p,origin,direction,width=width,budget=140);save(OUT/'traversals'/f'{label}.json.gz',z);s=z['states'][0];changed=None
  if z['completed'] and s['H']:
   c=canonical(s,direction);changed=sum(c[o]!=base[o] for o in c.keys()&base.keys())
  summary.append(dict(label=label,origin=origin,direction=direction,width=width,seed=z['seed'],seconds=z['seconds'],completed=z['completed'],normalized_H=z['normalized_H'],changed_coordinates=changed,returns=len(s['returns']),skips=[r['window'] for r in s['path'] if r.get('skipped')],windings=[[direction*v for v in st['H']] for st in z['states'] if st['H']]))
  save(OUT/'extra-traversal-summary.json',dict(runs=summary));print('EXTRA',summary[-1],flush=True)
if __name__=='__main__':main()

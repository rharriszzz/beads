"""Compare colored material with frozen visible body geometry; no black light."""
from .continuity import *

def main():
 m=np.load(OUT/'model-geometry.npz');owner=m['owner'].reshape(m['shape']);bbox=m['bbox'];step=float(m['step']);rows=[]
 for oid,addr in [('C-1302-0316',-64),('C-1391-0312',-38),('C-1422-0264',-26)]:
  j=int(np.flatnonzero(m['indices']==addr)[0]);variants=[]
  for radius in [16,18,20]:
   for threshold in [.95,1,1.05]:
    _,px=measure(OBS[oid],radius,threshold);own=owner[((px[:,1]-bbox[1])/step).astype(int),((px[:,0]-bbox[0])/step).astype(int)];covered=int((own==j).sum())
    variants.append(dict(radius=radius,threshold=threshold,pixels=len(px),covered=covered,coverage=covered/len(px)))
  rows.append(dict(id=oid,model_address=addr,base=next(v for v in variants if v['radius']==18 and v['threshold']==1),range=[min(v['coverage'] for v in variants),max(v['coverage'] for v in variants)],variants=variants))
 (OUT/'colored-model-comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()

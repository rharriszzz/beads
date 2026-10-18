"""Independent additional-context photo checks; no model preference input."""
import time,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from .tracker import ROOT,OUT,save,preprocess,base,joint

def main():
 start=time.perf_counter();g=json.loads((OUT/'graph.json').read_text());obs=g['observations'];data=preprocess(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'));rng=np.random.default_rng(1324)
 pairs=[['C-1559-0252','C-1582-0272'],['K-1721-0308','C-1729-0337']];rows=[]
 for size in [160,240,280]:
  for cx in [1530,1570,1610,1650,1690,1730,1770]:
   near=min(g['windows'],key=lambda w:abs(w['center'][0]-cx)+4*abs(w['center'][1]-290));R=np.array(near['frame']);cen=np.array([cx,near['center'][1]])
   local=[o for o in obs if np.max(abs((np.array(o['xy'])-cen)@R))<size/2-8 and o['band_clearance_px']>=10]
   grid=np.indices((size,size))[::-1].reshape(2,-1).T-(size-1)/2;pts=grid@R.T+cen;patch={k:base.sample(data[k],pts).reshape(size,size) for k in ['z','fg']};patch['fg']=patch['fg']>.5;patch['weight']=ndi.gaussian_filter(patch['fg'].astype(float),5)*np.hanning(size)[None,:]
   row=dict(size=size,center=cen.tolist(),frame=R.tolist(),observations=[o['id'] for o in local],hypotheses=[]);rows.append(row)
   try:_,spec=base.directions(patch)
   except ValueError as e:row['failure']=str(e);continue
   bases=[];hs=[];xy=np.array([o['xy'] for o in local]);sig=np.array([8 if o['color']=='black' else 5 for o in local]);weight=np.array([1 if o['band_clearance_px']>=18 else .55 for o in local])
   for tri in spec['triangles']:
    B=np.linalg.inv(np.array([spec['peaks'][i]['frequency_xy'] for i in tri['peaks'][:2]]))[:,::-1]
    if any(np.linalg.norm(B-b)<4 for b in bases):continue
    bases.append(B);hh,_,_=joint.fit_hypotheses((xy-cen)@R,sig,weight,B,[o['id'] for o in local],rng);hs+=hh
    if len(bases)>=10:break
   hs=sorted(hs,key=lambda h:-h['score']);seen=set()
   for h in hs:
    a=h['assignments'];first=a[sorted(a)[0]]['ab'];key=tuple((o,*map(int,np.array(a[o]['ab'])-first)) for o in sorted(a))
    if key in seen:continue
    seen.add(key);row['hypotheses'].append(h)
    if len(row['hypotheses'])>=6:break
   row['pair_alternatives']=[]
   for p,q in pairs:
    for hi,h in enumerate(row['hypotheses']):
     a=h['assignments']
     if p in a and q in a:row['pair_alternatives'].append(dict(pair=[p,q],hypothesis=hi,delta_ab=(np.array(a[q]['ab'])-a[p]['ab']).tolist(),score=h['score'],loss_from_best=row['hypotheses'][0]['score']-h['score'],observations=len(a),triangles=h['triangles']))
 summaries=[]
 for pair in pairs:
  votes=[dict(size=r['size'],center=r['center'],**a) for r in rows for a in r.get('pair_alternatives',[]) if a['pair']==pair]
  credible=[v for v in votes if v['loss_from_best']<=1.0];deltas=sorted(set(tuple(v['delta_ab']) for v in credible))
  summaries.append(dict(pair=pair,credible_local_deltas=deltas,observed_alternatives=votes,resolved=False,reason='Multiscale affine context is correlated and not calibrated; retain R323 contrary continuation unless independently eliminated.'))
 save(OUT/'bridge.json',dict(seconds=time.perf_counter()-start,windows=rows,summary=summaries,model_inputs=False,changes_to_frozen_graph=False,policy='Additional 160/240/280px contexts and bases; local score loss <=1 is descriptive credibility, not posterior probability. No bridge-wide origin propagation.'))
 print('BRIDGE',time.perf_counter()-start,[(r['pair'],r['credible_local_deltas']) for r in summaries],flush=True)
if __name__=='__main__':main()

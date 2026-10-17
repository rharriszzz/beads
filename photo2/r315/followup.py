"""Early-core causal audit for the selected narrow-field candidate, same pixels."""
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from .model import Chain,refined_trace,subset
from .diagnose import OUT

def main():
 ledger=read(OUT/'ledger.json.gz');ledger=[r for r in ledger if r['model']!='R315-narrow'];s=Chain(read(OUT/'narrow-model.json.gz')['parameters'],load()[0])
 for base in [r for r in ledger if r['model']=='R306-2405']:
  xy=np.array(base['pixels']);full=refined_trace(s,xy);cs=[]
  for j in s.tree.query_ball_point(base['point'],s.query_radius+20):
   iso=refined_trace(subset(s,[j]),xy);mask=iso['owner']>=0
   if not mask.any():continue
   vis=full['owner']==j;hidden=mask&~vis&(full['owner']>=0);ids,counts=np.unique(full['owner'][hidden],return_counts=True);oc=[]
   for jj,num in sorted(zip(ids,counts),key=lambda z:-z[1]):
    sel=hidden&(full['owner']==jj);dif=full['depth'][sel]-iso['depth'][sel];cf=refined_trace(s,xy,remove=(int(s.indices[jj]),));oc.append(dict(index=int(s.indices[jj]),pixels=int(num),depth_difference_min=float(dif.min()),depth_difference_median=float(np.median(dif)),depth_difference_max=float(dif.max()),removed_candidate_visible_fraction=float(np.mean(cf['owner']==j)),counterfactual_only=True))
   cs.append(dict(index=int(s.indices[j]),isolated_fraction=float(mask.mean()),visible_fraction=float(vis.mean()),occluders=oc,center=s.centers[j].tolist(),projected_center=s.pc[j].tolist(),axes={k:s.g[k][j].tolist() for k in AXES},neighbors=[dict(index=int(s.indices[j+d]),center=s.centers[j+d].tolist(),projected=s.pc[j+d].tolist()) for d in [1,6,7]]))
  cs.sort(key=lambda r:-r['isolated_fraction']);plausible=[r for r in cs if r['isolated_fraction']>=.8];bestvis=max(r['visible_fraction'] for r in cs);outcome='multiple_isolated_aliases' if len(plausible)>1 else ('plausible_isolated_hidden' if plausible and bestvis<.8 else ('no_80percent_isolated_explanation' if not plausible else 'surface_plausibly_explained'));ledger.append(dict(base,model='R315-narrow',candidates=cs,outcome=outcome,alternative_assignment_explains_core=bestvis>=.8))
 save(OUT/'ledger.json.gz',ledger)
if __name__=='__main__':main()

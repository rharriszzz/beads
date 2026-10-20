"""Three predeclared fixed-pixel alternatives; no size, affine fit, or motif input."""
from common import *
from recognize import sample,THRESHOLD

def confusion(rows,truth,decisions=None):
 c=Counter(dict(TP=0,TN=0,FP=0,FN=0,abstain=0))
 for o,t in truth.items():
  m=rows.get(o);d=decisions[o] if decisions is not None else (m['decision'] if m else 'unknown')
  if d=='unknown':c['abstain']+=1
  else:c[('TP' if t=='black' else 'FP') if d=='black' else ('FN' if t=='black' else 'TN')]+=1
 return dict(c,n=len(truth))
def main():
 g,obs,co,rgb,auth=load();names=sorted(obs);tree=cKDTree([obs[o]['xy'] for o in names]);neighbors={o:[names[j] for j in tree.query_ball_point(obs[o]['xy'],30) if names[j]!=o] for o in names}
 selection=read(ROOT/'photo2/r341/selection.json');dev=dict(selection['development_ids'],**MAKER);held=selection['heldout_ids'];assert not set(dev)&set(held);truth={o:r['color'] for o,r in auth.items() if o in obs};variants={kind:{o:sample(rgb,obs[o]['xy'],[obs[z]['xy'] for z in neighbors[o]],kind) for o in names} for kind in ['at-support','offset-core','neighbor-clipped']}
 devscores={k:confusion(v,dev) for k,v in variants.items()}
 # Select fewest total development errors; simpler wins ties.
 kinds=list(variants);chosen=min(kinds,key=lambda k:(devscores[k]['FP']+devscores[k]['FN']+devscores[k]['abstain'],kinds.index(k)))
 evaluation={k:dict(development=devscores[k],heldout=confusion(v,held),maker=confusion(v,truth),errors=[dict(id=o,color=truth[o],score=v[o]['score'] if v[o] else None) for o in truth if v[o] is None or (truth[o]=='black')!=(v[o]['decision']=='black')]) for k,v in variants.items()}
 save(OUT/'alternatives.json.gz',variants);save(OUT/'experiment.json',dict(alternatives=evaluation,selected=chosen,development=dev,heldout=held,neighbors=neighbors,threshold=THRESHOLD,design='Fixed9x9 core; offsets0 or6pixels, optional fixed2pixel Voronoi inset. No spacing or diameter. Neighbor queries30pixels. Selection development only: total errors including abstentions; simpler wins ties. Initial false-positive-first selection is archived; its support-core misses24 known blacks and is rejected as unusable.'))
 prior={r['id']:r for r in read(ROOT/'photo2/r341/native-audit.json.gz')['records']}
 rows=[dict(id=o,xy=obs[o]['xy'],recorded_color=MAKER.get(o,obs[o]['color']),measurement=variants[chosen][o],maker_color=truth.get(o),R341_owned=prior[o]['measured_pixels_convincingly_owned']) for o in names]
 save(OUT/'classification.json.gz',dict(selected=chosen,records=rows,pattern_used=False));print(json.dumps(dict(selected=chosen,evaluation=evaluation),indent=2))
if __name__=='__main__':main()

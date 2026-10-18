from .common import *
from .localize import evidence

def main():
 g,b,p,states=inputs();s0,_,cp=replay(b,p,states[0]['path']);novel=read(OUT/'novel-windings.json.gz')['alternatives'];results=[]
 for n in novel:
  pathmap={r['window']:r for r in n['state']['path'][:-1]};path=[dict(pathmap[i]) for i in range(len(b['windows']))]+[dict(pathmap[0])];diff=[i for i in range(len(b['windows'])) if path[i].get('patch')!=states[0]['path'][i].get('patch')];start=min(diff);ss,receipt,_=replay(b,p,path,checkpoint=cp[start],start=start)
  one=list(states[0]['path']);one[start]=path[start];_,single,_=replay(b,p,one,checkpoint=cp[start],start=start)
  evp=evidence(b,p,states[0]);eva=evidence(b,p,n['state']);local=[]
  for wi in diff:
   a=states[0]['path'][wi];bb=path[wi]
   if bb.get('skipped'):local.append(dict(window=wi,skipped=True));continue
   pa=p['patches'][wi][a['patch']];pb=p['patches'][wi][bb['patch']]
   local.append(dict(window=wi,primary_hypothesis=a['hypothesis'],alternative_hypothesis=bb['hypothesis'],primary_score_terms=pa['score_terms'],alternative_score_terms=pb['score_terms'],primary_shape=b['windows'][wi]['hypotheses'][a['hypothesis']]['r327_shared_shape'],alternative_shape=b['windows'][wi]['hypotheses'][bb['hypothesis']]['r327_shared_shape'],primary_assignments=pa['assignments'],alternative_assignments=pb['assignments'],primary_edges=pa['edges'],alternative_edges=pb['edges']))
  results.append(dict(H=n['H'],changed_windows=diff,first_window=start,last_window=max(diff),replay=receipt,single_patch_counterfactual=single,state=serialize(ss) if ss else None,local_evidence=local,first_comparisons=[{k:v for k,v in c.items() if k!='rows'} for c in n['comparisons']],primary_evidence_reuse={k:v for k,v in evp.items() if k!='predictions'},alternative_evidence_reuse={k:v for k,v in eva.items() if k!='predictions'}))
 save(OUT/'novel-replays.json.gz',dict(cases=results));print([(z['H'],z['replay'],z['single_patch_counterfactual']) for z in results],flush=True)
if __name__=='__main__':main()

"""Higher-budget actual-solid follow-up for promising unresolved search proposals."""
from photo2.r297.common import read,save
from photo2.r306.evidence import load
from .run import OUT,make,merit
from .geometry import contacts

def main():
 data,_,_=load();rows=[read(p) for p in (OUT/'trials').glob('*.gz')];un=[r for r in rows if r['classification']=='unresolved' and 'development' in r];chosen=sorted(un,key=merit)[:3];checks=[]
 for r in chosen:
  s=make(r['parameters'],data);c=contacts(s,seconds=5.);checks.append(dict(trial=r['id'],parameters=r['parameters'],prior=r['classification'],physical=c,development=r['development']));print(r['id'],c['classification'],flush=True)
 save(OUT/'unresolved-followup.json.gz',dict(unresolved_trials=len(un),checks=checks,policy='Post-seal diagnostics only. Unresolved is not collision. No new proposal, reranking or adoption.'))
if __name__=='__main__':main()

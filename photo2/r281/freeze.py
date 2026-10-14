"""Development-only calibration. Must run before new held-out scenes exist."""
from datetime import datetime,timezone
from .common import OUT,ROOT,read,save,sha
from .evaluate import evaluate,summarize
from .detector import DEFAULT

def main():
 assert not (OUT/'heldout').exists(),'Do not recalibrate after held-out generation'
 rows=evaluate('dev');grid=[]
 for coverage in (.65,.45,.25,0.):
  for margin in (.05,.10,.15,.20,.25,.30,.40):
   rules={**DEFAULT,'coverage':coverage,'margin':margin}
   for level in (0.,.05,.10):
    rr=[r for r in rows if r['method']=='combined' and r['kind'] in ('present','removed') and r['level']==level]
    grid.append(dict(rules=rules,level=level,summary=summarize(rr,rules)))
 # Require at least a quarter of H0 material extrapolation to have independent
 # context, retaining an explicit floor instead of maximizing acceptance count.
 feasible=[r for r in grid if r['level']==0 and r['rules']['coverage']>=.25 and r['summary']['precision'] is not None and r['summary']['precision']>=.95 and r['summary']['recall']>=.5]
 selected=max(feasible,key=lambda r:(r['summary']['recall'],r['summary']['precision'],r['rules']['coverage']))
 sources=['detector.py','geometry.py','run.py','synthetic.py','real_fit.py','real_select.py','PROTOCOL.md']
 save(OUT/'calibration.json',dict(grid=grid,selected=selected,previous_default=DEFAULT,criterion='>=95% paired precision, >=50% recall, >=.25 independent H0 context. Highest recall then precision/context; no heldout data.'))
 save(OUT/'freeze.json',dict(utc=datetime.now(timezone.utc).isoformat(),rules=selected['rules'],source_hashes={s:sha(ROOT/'photo2/r281'/s) for s in sources},heldout_scenes=40,seed=281202,development_scenes=12,development_targets=23))
 print(selected)
if __name__=='__main__':main()

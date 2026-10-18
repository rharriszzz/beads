"""Short same-evidence R324 versus global lower-bend practice experiment."""
import copy,json,time,resource
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from photo2.r324 import fast_tracker as old
from photo2.r325.global_solver import solve
OUT=Path(__file__).parent/'results';ROOT=old.ROOT

def main():
    g=json.loads((ROOT/'photo2/r324/results/graph.json').read_text())
    # 29 consecutive windows straddle three difficult lower-bend continuations.
    ws=copy.deepcopy(g['windows'][65:94]);ids={x for w in ws for x in w['observation_ids']}
    obs=[o for o in g['observations'] if o['id'] in ids]
    assert 100<=len(obs)<=200,len(obs)
    start=time.perf_counter();data=old.preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));prep=time.perf_counter()-start
    start=time.perf_counter();beam=old.joint.joint_select(ws);chart=0
    for i,w in enumerate(ws):
        prev=i-1;choices=sorted({b['choices'][i] for b in beam if b['score']>=beam[0]['score']-3 and b['choices'][i] is not None})
        previous=sorted({b['choices'][prev] for b in beam if b['score']>=beam[0]['score']-3 and b['choices'][prev] is not None}) if i else []
        checks=[old.joint.overlap(ws[prev]['hypotheses'][a],w['hypotheses'][b]) for a in previous for b in choices]
        if i and not(checks and all(c['common']>=4 and c['disagree']==0 for c in checks)):chart+=1
        w['chart']=chart
    centers=np.array([w['center'] for w in ws]);owners={o['id']:ws[np.argmin(np.linalg.norm(centers-o['xy'],axis=1))]['chart'] for o in obs}
    ns,gr,tr,sel=old.infer_graph(obs,ws,beam,data,owners);baseline_seconds=time.perf_counter()-start
    baseline=dict(indexed=sum(n['component'] is not None for n in ns),edges=len(gr['edges']),unresolved=len(gr['unresolved_edges']),components=len(gr['components']),seconds=baseline_seconds)
    # This crop is open; closing it would connect spatially unrelated endpoints.
    sol=solve(ws,cyclic=False)
    # Adapter exposes all max-marginal states, retaining ambiguity conservatively.
    bb=[dict(score=0.,choices=[(s[k%len(s)] if s else None) for s in sol['selected']]) for k in range(max(map(len,sol['selected'])))]
    start=time.perf_counter();ns2,gr2,tr2,_=old.infer_graph(obs,ws,bb,data,{o['id']:0 for o in obs});gt=time.perf_counter()-start
    new=dict(indexed=sum(n['component'] is not None for n in ns2),edges=len(gr2['edges']),unresolved=len(gr2['unresolved_edges']),components=len(gr2['components']),seconds=sol['seconds']+gt,cycle_conflicts=len(gr2['conflicts']))
    report=dict(observations=len(obs),colors=dict(Counter(o['color'] for o in obs)),window_ids=[w['id'] for w in ws],source='same frozen R324 photographic candidate bank; candidate generation excluded from this first solver test',preprocessing_seconds=prep,R324=baseline,R325=new,solver=sol,peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,observed_ids=sorted(ids),limitation='No independent photographic identity denominator outside R161; these are coverage and internal consistency counts.')
    old.save(OUT/'practice-initial.json',report);old.save(OUT/'practice-graph.json',dict(observations=obs,windows=ws,baseline=gr,global_graph=gr2));print({k:v for k,v in report.items() if k not in ['solver','observed_ids']})
if __name__=='__main__':main()

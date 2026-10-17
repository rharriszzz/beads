"""Contingent bounded four-variable sampling around promising discovered basins."""
from pathlib import Path
from copy import deepcopy
import time
import numpy as np
from scipy.stats import qmc
from photo2.r297.common import ROOT,read,save,sha,utc
from .model import canonical,starts
from .search import Runner,coordinate_distance

EXTRA_SECONDS=600.

def run(out):
    out=Path(out);state=read(out/'checkpoint.json')
    if state.get('coupled_4d',{}).get('complete'):return state
    assert not state['sealed']
    runner=Runner(out,state['elapsed']+EXTRA_SECONDS,True,2000);st=runner.state
    if 'coupled_4d' not in st:
        selected=[]
        for seed in starts()[:3]:
            rows=[r for r in runner.rows if r['feasible'] and r['family']==seed['name']]
            base=next(r for r in rows if r['kind']=='start')
            pool=sorted(rows,key=lambda r:r['global_score'])[:1]
            local=sorted([r for r in rows if r['global_score']<=base['global_score']*1.15],key=lambda r:r['target_loss'])[:1]
            anchored=sorted([r for r in rows if r['global_score']<=base['global_score']*1.15 and r['first_errors'][0]['modal_fraction']>=base['first_errors'][0]['modal_fraction']-.05],key=lambda r:r['target_loss'])[:1]
            for r in pool+local+anchored:
                promising=r['global_score']<base['global_score']*.98 or (r['target_loss']<base['target_loss']-.15 and r['global_score']<=base['global_score']*1.15)
                if promising and all(r['family']!=z['family'] or coordinate_distance(r['parameters'],z['parameters'])>.035 for z in selected):selected.append(r)
        jobs=[]
        # Basin-centered scrambled designs explore FOUR variables together.
        blocks=[(['phase','s0','elevation','roll'],[.65,8.,8.,12.]),
                (['minor','scale','axial','tilt'],[.4,.65,.12,10.])]
        for i,r in enumerate(selected):
            for bi,(keys,widths) in enumerate(blocks):
                for j,x in enumerate(qmc.Sobol(4,scramble=True,seed=31100+10*i+bi).random_base2(4)):
                    p=deepcopy(r['parameters'])
                    for k,w,z in zip(keys,widths,x):p[k]+=float((2*z-1)*w)
                    jobs.append(dict(family=r['family'],parameters=canonical(p),kind='basin-sobol',block=keys,
                                     sample=j,parent=r['id'],parent_score=r['search_score'],predicted_score=r['search_score'],
                                     prediction_policy='Constant basin-center forecast; measured changes retained'))
        # Round-robin the blocks/parents so a late deadline cannot omit a basin.
        if selected:jobs=sorted(jobs,key=lambda j:(j['sample'],j['block'][0],j['family']))
        st['coupled_4d']=dict(started=utc(),source_sha256=sha(Path(__file__)),initial_elapsed=runner.elapsed(),
                              allowance_seconds=EXTRA_SECONDS,selected=[r['id'] for r in selected],plan=jobs,cursor=0,complete=False,
                              trigger='>2% whole-development gain OR >15pp mean first-error gain with whole score<=115% baseline; no comparison outcomes consulted.')
        st['transitions'].append(dict(event='contingent basin-centered4D stage',elapsed=runner.elapsed(),parents=[r['id'] for r in selected]))
        runner.checkpoint()
    stage=st['coupled_4d'];assert stage['source_sha256']==sha(Path(__file__))
    deadline=stage['initial_elapsed']+stage['allowance_seconds'];runner.seconds=deadline
    while stage['cursor']<len(stage['plan']) and runner.elapsed()<deadline and not runner.stop:
        job=stage['plan'][stage['cursor']]
        # trial() itself recovers a fully published orphan at next_id.
        runner.trial(job);stage['cursor']+=1;runner.checkpoint()
    stage['complete']=not runner.stop
    stage['seconds']=runner.elapsed()-stage['initial_elapsed']
    stage['stop_reason']='signal' if runner.stop else 'planned four-variable basin samples complete' if stage['cursor']==len(stage['plan']) else '600-second contingent limit'
    st['stop_reason']='signal' if runner.stop else stage['stop_reason'];runner.detect_basins();runner.checkpoint()
    save(out/'coupled-4d.json',stage)
    # Update the aggregate ledger; initial schedule and its stopping cause remain
    # preserved under initial-search-summary.json.
    if not (out/'initial-search-summary.json').exists():save(out/'initial-search-summary.json',read(out/'search-summary.json'))
    from collections import Counter
    save(out/'search-summary.json',dict(stop_reason=st['stop_reason'],elapsed=st['elapsed'],initial_budget_seconds=2400,
         contingent_allowance_seconds=EXTRA_SECONDS,evaluations=st['next_id'],statuses=dict(Counter(r['status'] for r in runner.rows)),
         broad_completed=st['cursor'],broad_planned=len(st['plan']),deduplicated=st['deduplicated'],basins=st['basins'],coupled_stage=stage['stop_reason']))
    return st

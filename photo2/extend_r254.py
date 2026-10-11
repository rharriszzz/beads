"""Bounded count/turn extension, seeded by R253 geometry without color fitting."""
import json, argparse
import numpy as np
import global_fit_r253 as old
from pattern_r254 import OLD,OUT,diagnostic
from camera_r254 import fit,audit


def run(out=OUT):
    existing=json.loads((out/'camera-results.json').read_text());bases=json.loads((OLD/'models.json').read_text());rigid=json.loads((OLD/'rigid.json').read_text());scan=json.loads((OLD/'scan.json').read_text());allrows=old.data();groups,_=old.patch_points(allrows);results=[];ps=[];pruned=[]
    # All integers in the original requested neighborhood, plus surviving wider
    # rigid basins already optimized by R253. Prime-like totals are excluded
    # algebraically before image computation.
    counts=sorted(set(range(2670,2701))|{r['n'] for r in rigid})
    for n in counts:
        periods=[P for P in range(2,400) if n%P==0 and P%13]
        if not periods:pruned.append(dict(n=n,reason='Only admissible period is 1; trusted red and yellow preclude it'));continue
        for h in [1,-1]:
            found=[b for b in bases if b['n']==n and b['h']==h and b['kind']=='rigid']
            if found:base=found[0];rows=json.loads((OLD/f'{base["model_id"]}-assignments.json').read_text())
            elif (out/f'N{n}_h{h:+d}-initial-model.json').exists():
                base=json.loads((out/f'N{n}_h{h:+d}-initial-model.json').read_text());rows=json.loads((out/f'N{n}_h{h:+d}-initial-assignments.json').read_text())
            else:
                rr=[r for r in rigid if r['n']==n and r['h']==h]
                candidate=rr[0] if rr else next(r for r in scan if r['n']==n and r['h']==h)
                if not rr:candidate=old.fit(n,h,candidate['p'],[r for r in allrows if r['split']=='train'],budget=20)
                trial={k:candidate[k] for k in ['n','h','p','train_score']};trial['kind']='r254_initial'
                base,rows,_,_=old.audit_one(trial,allrows,groups)
                old.save(out/f'N{n}_h{h:+d}-initial-assignments.json',rows);old.save(out/f'N{n}_h{h:+d}-initial-model.json',base)
            trials=[(0.,0)] if not any(x['n']==n and x['h']==h for x in existing) else []
            # Independent turn hypotheses for the matched nonprime near leaders.
            if n in [2670,2679,2698,2700]:trials +=[(0.,-1),(0.,1)]
            for focal,td in trials:
                mid=f'N{n}_h{h:+d}_f0'+(f'_T{td:+d}' if td else '')
                if (out/f'{mid}-camera.json').exists() and json.loads((out/f'{mid}-camera.json').read_text()).get('protocol_version')==2:trial=json.loads((out/f'{mid}-camera.json').read_text());metrics=trial['metrics'];metrics['chart_holdout_total']=5;records=json.loads((out/f'{mid}-assignments.json').read_text())
                else:
                    trial=fit(base,focal,rows,20,td);metrics,records=audit(trial,rows,groups);trial.update(model_id=mid,metrics=metrics)
                    old.save(out/f'{mid}-camera.json',trial);old.save(out/f'{mid}-assignments.json',records)
                results.append(trial)
                for subset in ['all','unique','train_unique']:
                    rr=[r for r in records if subset=='all' or r['conditional_unique'] and (subset!='train_unique' or r['split']=='train')];dd=[diagnostic(rr,P,n) for P in range(1,400)];allowed=[d for d in dd if d['admissible_by_maker']];best=min(allowed,key=lambda d:(d['minimum_conflicting_assignments'],d['P']))
                    ps.append(dict(model_id=mid,subset=subset,count=len(rr),best_P=best['P'],min_conflicts=best['minimum_conflicting_assignments'],exact_periods=[d['P'] for d in allowed if d['exact']],admissible_periods=[d['P'] for d in allowed],period_conflicts=[d['minimum_conflicting_assignments'] for d in dd]))
                print(mid,'graph',metrics['chart_owned'],'anchor',metrics['anchor_owned'],'min admissible conflicts',ps[-2]['min_conflicts'],flush=True)
                old.save(out/'extended-results.json',results);old.save(out/'extended-pattern-summary.json',ps)
    old.save(out/'count-pruning.json',dict(counts=counts,pruned=pruned))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=__import__('pathlib').Path,default=OUT);a=ap.parse_args();run(a.output)

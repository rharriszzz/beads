"""Integrity, independent arithmetic controls and deterministic geometry replay."""
import argparse,hashlib,json,subprocess,sys,platform
from pathlib import Path
import numpy as np
from pattern_r254 import OUT,OLD,ROOT,diagnostic,propagate
from camera_r254 import Model,audit,fit
import global_fit_r253 as old

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(out):
    # Original accepted observations and all original evidence must match HEAD.
    sources=[ROOT/'photo2/review/r252/accepted.csv',ROOT/'photo2/review/r252/inventory.json',ROOT/'beads-photo-2.jpg',ROOT/'photo2/spline-seed-r175.json',ROOT/'beads.pov']+list(OLD.glob('*'))
    integrity={}
    for p in sources:
        if not p.is_file():continue
        relative=str(p.relative_to(ROOT));original=subprocess.check_output(['git','show','1529674:'+relative],cwd=ROOT);integrity[relative]=sha(p)
        if hashlib.sha256(original).hexdigest()!=sha(p):raise AssertionError(relative+' changed')
    old.save(out/'source-integrity.json',dict(base_commit='1529674',unchanged_count=len(integrity),hashes=integrity))
    selected=json.loads((OLD/'selected.json').read_text());controls=[]
    # Independent implementation: dictionary of explicit color labels rather
    # than sharing the numpy counting path.
    for mid in selected:
        rows=json.loads((OLD/f'{mid}-assignments.json').read_text());rr=[r for r in rows if r['conditional_unique']]
        values=[]
        for P in range(1,400):
            groups={}
            for r in rr:groups.setdefault(r['k']%P,[]).append(r['color'])
            count=sum(len(v)-max(v.count(c) for c in set(v)) for v in groups.values())
            assert count==diagnostic(rr,P)['minimum_conflicting_assignments'];values.append(count)
        controls.append(dict(model_id=mid,minimum=min(values),periods=[i+1 for i,v in enumerate(values) if v==min(values)],periods_checked=399))
    # Local camera solution replay, using train-only inputs and complete patch audit.
    replay=[]
    for mid in ['N2670_h+1_f0','N2679_h-1_f0','N2670_h+1_f4799']:
        m=json.loads((out/f'{mid}-camera.json').read_text());base=next(b for b in json.loads((OLD/'models.json').read_text()) if b['model_id']==m['base_model']);rows=json.loads((OLD/f'{m["base_model"]}-assignments.json').read_text());groups,_=old.patch_points(rows)
        trial=fit(base,m['focal'],rows,20);np.testing.assert_allclose(trial['p'],m['p'],atol=1e-10,rtol=0)
        metrics,records=audit(trial,rows,groups);saved=json.loads((out/f'{mid}-assignments.json').read_text());assert records==saved;assert metrics==m['metrics'];replay.append(dict(model_id=mid,parameters_and_all_assignments_exact=True))
    # Every final assignment stays one-to-one and preserves reserved identities.
    for filename in out.glob('*-camera.json'):
        m=json.loads(filename.read_text());rr=json.loads((out/f"{m['model_id']}-assignments.json").read_text())
        assert len(rr)==310 and len({r['generator_index'] for r in rr})==310
        assert m['metrics']['chart_holdout_total']==5
        for r in rr:
            if r['observation_id'] in m['stars']:assert r['generator_index']==m['stars'][r['observation_id']]
    # Replay every discrete contradiction witness in its original cost envelope.
    proofs=[]
    for fname,root in [('alternative-proofs.json',OLD),('refined-alternative-proofs.json',out)]:
        pp=json.loads((out/fname).read_text());cache={}
        for proof in pp:
            mid=proof['model_id']
            if mid not in cache:cache[mid]=json.loads((root/f'{mid}-assignments.json').read_text())
            rr=cache[mid];wanted=set(proof['witness']);use=[r for r in rr if r['observation_id'] in wanted]
            if proof['status']=='infeasible' and wanted:
                domains=[]
                for r in use:
                    cost=r.get('exact_audit_cost',next(a['exact_audit_cost'] for a in r['alternatives'] if a['k']==r['k']))
                    domains.append([a['k'] for a in r['alternatives'] if a['exact_audit_cost']<=cost+proof['delta_cost']+1e-12])
                assert propagate(use,domains,proof['P'])['status']=='infeasible'
        proofs.append(dict(file=fname,cases=len(pp),all_propagation_witnesses_replayed=True))
    commands=['PYTHONPATH=photo2 .venv/bin/python -m unittest photo2/test_pattern_r254.py photo2/test_global_fit_r253.py',
              '.venv/bin/python photo2/pattern_r254.py','.venv/bin/python photo2/alternatives_r254.py','.venv/bin/python photo2/camera_r254.py','.venv/bin/python photo2/extend_r254.py','.venv/bin/python photo2/evidence_r254.py','.venv/bin/python photo2/review_visuals_r254.py','.venv/bin/python photo2/geometry_changes_r254.py','.venv/bin/python photo2/verify_r254.py']
    old.save(out/'verification.json',dict(python=platform.python_version(),base_commit='1529674',fixed_independent_count_controls=controls,camera_replay=replay,proof_replay=proofs,reproduction_commands=commands,
       source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2').glob('*r254.py'))},artifact_hashes={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='verification.json'}))
    print('Source integrity, independent counts, camera replay and proof witnesses pass',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();run(a.output)

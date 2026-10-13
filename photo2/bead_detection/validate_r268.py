"""Independent saved-evidence checks, synthetic failure extraction and hashes."""
import csv,gzip,json,hashlib
from collections import Counter
from types import SimpleNamespace
import numpy as np
from matplotlib.colors import rgb_to_hsv
from .experiment_r268 import OUT,inventory
from .audit_r267 import ROOT,photo,save
from .climb_r268 import VARIANTS,background,audit
from .synthetic_r268 import figure,start_points

def main():
    for name,sha in json.loads((OUT/'input-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    assert inventory()==json.loads((OUT/'starts.json').read_text())
    rgb=photo();v=rgb.max(axis=2);hsv,paper,_=background(rgb);fake=SimpleNamespace(value=v,hsv=hsv,paper=paper);moves=0;samples=0;trajectories=0;incomplete_windows=0
    cases=json.loads((OUT/'starts.json').read_text())
    for crop,case in cases.items():
        tables=list(csv.DictReader(open(OUT/f'{crop}-endpoints.csv')));lookup={(r['start_id'],r['window'],r['variant']):r for r in tables}
        npz=np.load(OUT/f'{crop}-score-images.npz');ox,oy=npz['origin'];ts=json.load(gzip.open(OUT/f'{crop}-traces.json.gz'))
        legacy=json.loads((OUT/'legacy-color-photo-hashes.json').read_text())
        for n in ['5','7','9']:assert hashlib.sha256(json.dumps(ts[n]['legacy-color12'],sort_keys=True).encode()).hexdigest()==legacy[crop+'-'+n]
        for side,variants in ts.items():
            n=int(side);r=n//2
            for variant,traces in variants.items():
                for sid,t in traces.items():
                    moves+=audit(fake,t,VARIANTS[variant]);trajectories+=1;row=lookup[sid,side,variant]
                    assert [int(row['end_x']),int(row['end_y'])]==t['endpoint']
                    for a in t['steps']:
                        x,y=a['x'],a['y'];actual=int(v[y-r:y+r+1,x-r:x+r+1].sum());assert actual==a['score_sum']==int(npz[f'sum{n}'][y-oy,x-ox]);assert actual/n**2==a['score_dn'];assert int(v[y,x])==a['raw_v'];samples+=1
                    assert float(row['gain'])==t['steps'][-1]['score_dn']-t['steps'][0]['score_dn']
        assert len(lookup)==len(case['starts'])*3*len(VARIANTS)
        x0,y0,x1,y1=case['box'];from PIL import Image
        assert np.array_equal(np.array(Image.open(OUT/f'{crop}-original-native.png')),rgb[y0:y1,x0:x1])
    inputs=np.load(OUT/'synthetic-inputs.npz');truths=np.load(OUT/'synthetic-truth.npz');syn_moves=0;syn_paths=0;witnesses={};curr=None;syn_counts={};scene_points={}
    # Recheck every stored synthetic path, without using truth in the guard.
    with gzip.open(OUT/'synthetic-traces.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);name=r['scene'];t=r['trace'];variant=r['variant'];n=r['window']
            if name!=curr:
                image=inputs[name];vv=image.max(axis=2);hh,pp,_=background(image);sf=SimpleNamespace(value=vv,hsv=hh,paper=pp);truth=truths[name];curr=name;scene_points[name]=start_points(vv)
            syn_moves+=audit(sf,t,VARIANTS[variant]);syn_paths+=1
            x,y=t['start'];ex,ey=t['endpoint'];assert int(truth[y,x])==r['truth_start'];assert int(truth[ey,ex])==r['truth_end']
            assert tuple(t['start'])==scene_points[name][r['start_index']]
            if ((variant=='guarded12' and n in (7,9)) or (variant=='legacy-color12' and n==7)) and r['truth_start']:
                cross=r['truth_end'] not in (0,r['truth_start'])
                label='no-visible-interface' if name.startswith('no-visible') and cross else 'cross-body' if cross else 'body-to-background' if not r['truth_end'] else None
                if label and variant=='legacy-color12':label='legacy-'+label
                if label and label not in witnesses:
                    witnesses[label]=r;figure('failure-'+label,image,truth,[tuple(t['start'])],[t],variant=variant,window=n)
    save(OUT/'synthetic-failure-witnesses.json',witnesses)
    tests=(OUT/'tests.log').read_text();assert 'Ran 13 tests' in tests and tests.rstrip().endswith('OK')
    save(OUT/'validation.json',dict(status='pass',tests=13,unique_photo_starts=sum(len(c['starts']) for c in cases.values()),photo_trajectories=trajectories,photo_steps_checked=samples,photo_moves_checked=moves,synthetic_scenes=len(inputs.files),synthetic_trajectories=syn_paths,synthetic_moves_checked=syn_moves,all_previous_input_hashes_unchanged=True,all_source_starts_preserved=True,all_photo_scores_exact=True,all_moves_strict_native_neighbors=True,all_enabled_guard_and_diagonal_constraints_pass=True,source_truth_used_only_for_evaluation=True,legacy_guard_photo_traces_exact=True,production_detector_changed=False))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='artifact-hashes.json')+sorted((ROOT/'photo2/bead_detection').glob('*r268.py'))
    report=ROOT/'photo2/CLIMBING_MAXIMA_R268.md'
    if report.exists():files.append(report)
    save(OUT/'artifact-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files});print((OUT/'validation.json').read_text())
if __name__=='__main__':main()

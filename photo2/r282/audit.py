"""Saved-evidence contracts, complete deterministic replay, and historical preservation."""
import subprocess
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from .common import ROOT,OUT,read,save,sha,pixels,validate


def main():
    p1=read(OUT/'phase1.json.gz');byid={r['record_id']:r for r in p1['records']};masks=high=0
    for row in p1['records']:
        validate(row);assert row['phase_origin']==['phase1'];assert row['physical_model_index'] is None
        xy=pixels(row['measured_support'])
        if not len(xy):continue
        masks+=1;assert len(xy)==row['measured_support']['pixel_count']
        np.testing.assert_allclose(xy.mean(0),row['measured_photo_location'],atol=1e-12)
        lo=xy.min(0);hi=xy.max(0);m=np.zeros((hi[1]-lo[1]+1,hi[0]-lo[0]+1),bool);m[xy[:,1]-lo[1],xy[:,0]-lo[0]]=True
        assert ndi.label(m)[1]==1
        if row['status']=='high':assert 12<=len(xy)<=870;high+=1
    p2=read(OUT/'phase2.json');total=links=pattern_cases=0
    for name in p2['selected_ids']:
        data=read(OUT/(name+'-inventory.json.gz'));rows=data['records'];n=data['model']['n'];assert len(rows)==n
        assert [r['physical_model_index'] for r in rows]==list(range(n));seen=set()
        p3rows=read(OUT/(name+'-phase3-inventory.json.gz'))['records']
        for row,p3 in zip(rows,p3rows):
            validate(row);validate(p3);total+=1
            assert 0<=row['visibility']<=1;assert row['visible_pixels']<=row['isolated_projected_pixels']
            if row['visibility']==0:assert row['color']=='unknown' and row['color_reliability']==0
            for key in ('measured_photo_location','measured_support','color','color_reliability','physical_model_index'):assert row[key]==p3[key]
            for sid in row.get('source_record_ids',[]):
                assert sid not in seen;seen.add(sid);links+=1
                assert row['measured_support']==byid[sid]['measured_support']
                assert row['measured_photo_location']==byid[sid]['measured_photo_location']
        patterns=read(OUT/(name+'-patterns.json'))
        for kind in ('weighted','strict'):
            for c in patterns[kind]:
                assert n%c['period']==0 and n//c['period']>=4
                assert c['unknown_slots']==c['sequence'].count('unknown');pattern_cases+=1
    upstream=read(OUT/'phase3.json')['upstream_hashes'];assert all(sha(OUT/f)==h for f,h in upstream.items())
    # Compare every algorithm output from an independent full entry-point rerun.
    replay=Path('/tmp/beads-r282-replay');replayed=[]
    for f in replay.iterdir():
        if f.name=='pipeline-complete.json' or not f.is_file():continue
        assert sha(f)==sha(OUT/f.name),f.name;replayed.append(f.name)
    assert (replay/'pipeline-complete.json').exists()
    mutable={'AGENTS.md','PLAN.md','SESSION_HANDOFF.md','REQUEST_LOG.md','METHODS.md'}
    tree=subprocess.check_output(['git','ls-tree','-r','e6a6d4c'],cwd=ROOT,text=True)
    old={line.split('\t',1)[1]:line.split()[2] for line in tree.splitlines() if line.split('\t',1)[1] not in mutable}
    actual=subprocess.check_output(['git','hash-object','--stdin-paths'],input='\n'.join(old)+'\n',cwd=ROOT,text=True).splitlines()
    assert all(old[p]==h for p,h in zip(old,actual));assert len(actual)==len(old)
    result=dict(phase1_records=len(p1['records']),connected_native_masks=masks,high_masks=high,
        physical_records=total,immutable_phase1_links=links,pattern_cases=pattern_cases,
        exact_replay_files=replayed,protected_historical_files=len(old),base='e6a6d4c',
        upstream_unchanged=True,source_hashes={p.name:sha(p) for p in (ROOT/'photo2/r282').glob('*.py')})
    save(OUT/'audit.json',result);print(result)


if __name__=='__main__':main()

"""Read-only scientific verification of the delivered pilot and resumed replica."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import numpy as np
from PIL import Image
from photo2.r296.common import *
from photo2.r296.geometry import Chain,contact
from photo2.r296.tests import science


def main():
    out=BASE/'results/pilot';other=BASE/'checkpoints/resume-validation'
    a,b=[read(p/'checkpoint.json') for p in (out,other)]
    assert a['next_id']==b['next_id']==192
    for k in ('rng','pool','seen','next_id'):assert a[k]==b[k],k
    crashed=BASE/'checkpoints/pilot-recovered-v3'
    for n in range(192):
        name=f'{n:06d}.json.gz'
        assert science(read(out/'candidates'/name))==science(read(other/'candidates'/name))==science(read(crashed/'candidates'/name)),n
    result=dict(candidate_replay=192,resume_histories=['final locked CLI uninterrupted192','102 completed then daemon restart; pending102 recovered','64 completed, then resume to192'],
        rng_equal=True,population_equal=True,wall_clock_excluded=True)
    if not (out/'exports/manifest.json').exists():
        save(BASE/'results/resume-check.json',result);print(result);return
    manifest=read(out/'exports/manifest.json');data=read(EVIDENCE/'inputs.json.gz');native,_,_=photo()
    np.testing.assert_array_equal(np.asarray(Image.open(out/'review/original.png')),native)
    checks=[]
    for identifier in manifest['ids']:
        positions=read(out/'exports'/f'model-{identifier}.json.gz');evaluation=read(out/'exports'/f'evaluation-{identifier}.json.gz')
        scene=Chain(positions['parameters'],data);rows=positions['records'];cert=contact(scene,exact=True)
        assert cert['certified'];assert cert==evaluation['contact']
        assert [r['index'] for r in rows]==scene.indices.tolist()
        assert [r['historical_index'] for r in rows if r['historical_index'] is not None]==list(range(-20,201))
        np.testing.assert_allclose([r['projected_center'] for r in rows],scene.pc,atol=0,rtol=0)
        np.testing.assert_allclose([r['center_xyz'] for r in rows],scene.centers,atol=0,rtol=0)
        raw=np.load(out/'exports'/f'model-{identifier}-visibility.npz');owner=raw['owner'];sentinel=int(raw['background_sentinel'])
        assert sentinel not in scene.indices and -999 in scene.indices
        assert set(np.unique(owner)) <= set(scene.indices)|{sentinel}
        count_map=dict(zip(*np.unique(owner,return_counts=True)))
        for r in rows:assert r['visible_pixels']==int(count_map.get(r['index'],0))
        sample=np.linspace(0,len(owner)-1,4000).astype(int);tr=scene.trace(raw['xy'][sample]);expected=np.full(4000,sentinel,dtype=np.int32)
        good=tr['owner']>=0;expected[good]=scene.indices[tr['owner'][good]]
        np.testing.assert_array_equal(expected,owner[sample]);np.testing.assert_array_equal(tr['unknown'],raw['unknown'][sample])
        # Independently replay exact native support containment for a spread of cases.
        by={r['id']:r for r in data['rows']};replayed=0
        for r in evaluation['observations'][::73]:
            xy=pixels(by[r['id']]['pixels']);o=scene.trace(xy)['owner'];ids,counts=np.unique(o,return_counts=True)
            maximum=max((v/len(xy) for k,v in zip(ids,counts) if k>=0),default=0.)
            assert abs(maximum-r['containment'])<1e-15;replayed+=1
        checks.append(dict(id=identifier,sites=scene.n,independent_pairs=cert['pairs'],visibility_ray_replays=4000,native_support_replays=replayed,minimum_gap=cert['minimum_gap_units']))
    freeze=read(out/'final-freeze.json')
    first=read(BASE/'checkpoints/first-seal-v4/final-freeze.json')
    assert first['parameters']==freeze['parameters']
    import ast
    def body(path,name):
        tree=ast.parse(path.read_text());node=tree
        for part in name.split('.'):
            node=next(x for x in node.body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name==part)
        return ast.dump(node,include_attributes=False)
    unchanged=[]
    for module,names in dict(search=['starting_models','merit','select_population','propose','Runner.evaluate','Runner.incorporate','Runner.run'],review=['native_observations','summarize','evaluate_model','overlay']).items():
        for name in names:
            assert body(BASE/f'{module}.py',name)==body(BASE/'checkpoints/implementation-v4'/f'{module}.py',name)
            unchanged.append(module+'.'+name)
    for module in ('geometry','objective'):
        assert sha(BASE/f'{module}.py')==sha(BASE/'checkpoints/implementation-v4'/f'{module}.py')
        unchanged.append(module+' (complete module)')
    hashes=read(BASE/'checkpoints/first-seal-v4/artifact-hashes.json')
    exact=[]
    for name,value in hashes.items():
        if name.startswith('exports/') and name!='exports/manifest.json':
            assert sha(out/name)==value,name
            exact.append(name)
    result.update(unchanged_scientific_functions=unchanged,first_sealed_parameters_identical=True,byte_exact_first_seal_exports=exact)
    assert freeze['ids']==manifest['ids']
    from datetime import datetime
    freeze_time=datetime.fromisoformat(freeze['utc']).timestamp()
    assert all((out/'exports'/f'evaluation-{i}.json.gz').stat().st_mtime>=freeze_time for i in manifest['ids'])
    result.update(models=checks,original_photo_pixels_exact=True,sealed=a['sealed'],final_freeze_before_reserved=True)
    save(BASE/'results/pilot-audit.json',result);print(result)

if __name__=='__main__':main()

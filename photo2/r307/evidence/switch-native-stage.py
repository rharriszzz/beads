"""One documented campaign source transition after the first stage has stopped."""
from pathlib import Path
import shutil,time
from photo2.r297.common import ROOT,read,save,utc,sha
out=ROOT/'photo2/r307/results/campaign';state=read(out/'checkpoint.json')
assert state.get('stop_reason') in ['budget','ten complete blocks without native accepted improvement'],state.get('stop_reason')
archive=ROOT/'photo2/r307/evidence/before-native-correction';archive.mkdir(exist_ok=False)
shutil.copyfile(out/'checkpoint.json',archive/'checkpoint.json');shutil.copyfile(out/'benchmark.json',archive/'benchmark.json')
for name in ['search.py','objective.py','fast.py','kernel.cpp','__init__.py']:
    shutil.copyfile(ROOT/'photo2/r307'/name,archive/name)
shutil.copyfile(ROOT/'photo2/phase2_guided_fit.py',archive/'phase2_guided_fit.py')
for path in out.glob('sensitivity-*.json.gz'):shutil.copyfile(path,archive/path.name)
path=ROOT/'photo2/r307/search.py';source=path.read_text()
source=source.replace("result=dict(utc=utc(),kernel=rows", "k=max(1,int(np.ceil(len(good)/4)));recall=len(set(np.argsort(x)[:k])&set(np.argsort(y)[:k]))/k\n    added_missing=max(r['2']['unmatched']-r['1']['unmatched'] for r in good)\n    suitable=rho>=.9 and recall>=.8 and added_missing==0\n    result=dict(top_quartile_recall=recall,maximum_added_coarse_missing=added_missing,utc=utc(),kernel=rows")
source=source.replace("Two-pixel native surface/shadow predictor only if rank correlation >= .8; final acceptance uses native fixed owners.","Two-pixel predictor only if correlation >= .9, best-quartile recall >= .8 and no added missing assigned lobes; otherwise all sensitivities are native. Final acceptance uses native fixed owners.")
source=source.replace("fit_step=2. if rho>=.8 else 1.","fit_step=2. if suitable else 1.")
source=source.replace("dict(cycle=cycle,family=family['name'],names=names,base=base['id']", "dict(cycle=cycle,predictor_step=self.fit_step,family=family['name'],names=names,base=base['id']")
source=source.replace("dict(cycle=cycle,family=family['name'],improved=improved", "dict(cycle=cycle,step=self.fit_step,family=family['name'],improved=improved")
source=source.replace("recent=self.state['sensitivity'][-10:]", "recent=[r for r in self.state['sensitivity'] if r.get('step')==self.fit_step][-10:]")
source=source.replace("class Budget(Exception):pass", """def block_names(p,cycle,data):
    if cycle%5==0:return list(SCALARS)
    first=(cycle%5-1)*8;axis_ids=list(range(first,first+8))
    s=Chain(p,data);k=(np.arange(32)/32-.5)*s.n
    from photo2.r297.geometry import reference
    arc=reference().project(s.project(s.placement(k)[0]))['arc']
    geographic=(arc/reference().length*32).astype(int)%32
    field_ids=np.flatnonzero(np.isin(geographic,axis_ids))
    return [f'axis_nodes:{j}' for j in axis_ids]+[f'{key}:{j}' for key in ['local_phase','local_spacing'] for j in field_ids]

class Budget(Exception):pass""")
source=source.replace("names=list(SCALARS) if cycle%5==0 else [f'{key}:{j}' for key in SCALES for j in range((cycle%5-1)*8,(cycle%5)*8)]", "names=block_names(p,cycle,self.data)")
path.write_text(source)
# Only the benchmark suitability rule and resolution-specific stagnation epoch
# change. All geometry, residual definitions, weights, observations and owners stay.
from photo2.r307.search import sources
old_sources=state['sources'];new_sources=sources();changed=[p for p,h in new_sources.items() if old_sources.get(p)!=h];assert changed==['photo2/r307/search.py'],changed
state['sources']=new_sources
state.setdefault('source_transitions',[]).append(dict(utc=utc(),first_new_trial=state['next_id'],elapsed=state['elapsed'],old_sources=old_sources,new_sources=new_sources,archive=str(archive.relative_to(ROOT)),reason='Measured coarse best-quartile recall .5 and added missing lobes require native sensitivities. Align phase/spacing knots to the same photographic geography as each axis block; original matching coefficient numbers used different origins. Reset stagnation epoch for changed predictor resolution; full cumulative1200s fitting cap.'))
save(out/'checkpoint.json',state)
b=read(out/'benchmark.json');a=read(out/'ranking-analysis.json');b.update(fit_step=1.,top_quartile_recall=a['top_quartile_recall'],decision_correction_utc=utc(),policy='Native sensitivities: original .8 correlation-only suitability gate was inadequate; stricter .9 correlation/.8 quartile/no extra missing-lobe gate fails. Earlier benchmark preserved byte-exact.')
save(out/'benchmark.json',b);save(ROOT/'photo2/r307/evidence/native-correction.json',state['source_transitions'][-1]);print('Switched at',state['elapsed'],'seconds; remaining',1200-state['elapsed'],flush=True)

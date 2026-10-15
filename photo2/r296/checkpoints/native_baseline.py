"""Native-support comparison to the pre-reserved frozen global-stage baseline."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from photo2.r296.common import *
from photo2.r296.geometry import Chain,contact
from photo2.r296.review import native_observations,summarize


def main():
    out=BASE/'results/pilot';state=read(out/'checkpoint.json');assert state['sealed']
    frozen=read(out/'baseline-freeze.json');final=read(out/'final-freeze.json')
    assert frozen['utc']<final['utc']
    data=read(EVIDENCE/'inputs.json.gz');scene=Chain(frozen['parameters'],data);cert=contact(scene,exact=True);assert cert['certified']
    rows=native_observations(scene,data,['train','validation','reserved'])
    result=dict(id=frozen['id'],parameters=frozen['parameters'],contact=cert,observations=rows,
        summary={s:{k:summarize([r for r in rows if r['split']==s and r['kind']==k]) for k in ('patch','region')} for s in ('train','validation','reserved')})
    save(out/'exports/global-baseline-native.json.gz',result)
    best=read(out/'exports'/f"evaluation-{state['pool'][0]}.json.gz");before={r['id']:r for r in rows}
    changes=[dict(id=r['id'],kind=r['kind'],split=r['split'],old_index=before[r['id']]['index'],new_index=r['index'],
        old_containment=before[r['id']]['containment'],new_containment=r['containment'],delta=r['containment']-before[r['id']]['containment']) for r in best['observations']]
    save(BASE/'results/native-progress.json',dict(initial_id=frozen['id'],final_id=best['id'],initial=result['summary'],final=best['summary'],
        stable_assignments=sum(r['old_index']==r['new_index'] for r in changes),observations=len(changes),changes=changes,
        baseline_frozen_before_reserved=True,limits='Exact native supports; conditional first-hit compatibility, not physical ownership. No post-reserved model selection.'))
    print('Native baseline and progress:',result['summary'],best['summary'])

if __name__=='__main__':main()

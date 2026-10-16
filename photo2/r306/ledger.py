"""Summarize recorded computation and expose the selected geometric parameters."""
from pathlib import Path
from collections import Counter
from photo2.r297.common import ROOT,read,save,utc

def build(out):
    out=Path(out);runs=[]
    for name in ['preflight','qualification','campaign-initial','campaign','independent']:
        folder=out.parent/name;path=folder/'checkpoint.json'
        if not path.exists():continue
        state=read(path);history=state['history']
        runs.append(dict(name=name,seed=state['seed'],proposals=len(history),
            elapsed_seconds=state['elapsed_seconds'],evaluation_seconds=sum(r['seconds'] for r in history),
            statuses=dict(Counter(r['status'] for r in history)),stages=dict(Counter(r['stage'] for r in history)),
            stop_reason=state['stop_reason'],sensitivity_blocks=len(state.get('sensitivities',[])),
            best=history[-1] if history else None,
            interpretation='Qualification' if name in ['preflight','qualification'] else 'Substantive fitting'))
    native=read(out/'native-refinement/checkpoint.json') if (out/'native-refinement/checkpoint.json').exists() else {}
    ranking=read(out/'native-ranking.json.gz') if (out/'native-ranking.json.gz').exists() else []
    audits=read(out/'native-progress.json.gz') if (out/'native-progress.json.gz').exists() else []
    manifest=read(out/'export-manifest.json')
    models=[read(out/'exports'/f'{name}.json.gz') for name in manifest['models']]
    controls=read(out/'controlled-diagnosis.json.gz')['controls']
    result=dict(utc=utc(),runs=runs,native_refinement=dict(proposals=native.get('next_id',0),
        elapsed_seconds=native.get('elapsed_seconds',0),history=native.get('history',[])),
        aggregate_fitting_seconds=sum(r['elapsed_seconds'] for r in runs if r['interpretation']=='Substantive fitting')+native.get('elapsed_seconds',0),
        timing_interpretation='Aggregate elapsed fitting time across runs, including evaluation/checkpoint overhead. Main and independent runs overlap in wall time. Native ranking, audits, controls, exports and verification are separate. No CPU-time or peak-memory measurement is claimed.',
        native_ranking=dict(candidates=len(ranking),seconds=sum(r['seconds'] for r in ranking)),
        native_progress_audits=dict(candidates=len(audits),records=audits),
        exports=dict(models=len(models),seconds=sum(r['seconds'] for r in models),positions=sum(len(r['positions']) for r in models),contacts=sum(r['physical']['pairs'] for r in models)),
        controlled_diagnosis=dict(proposals=len(controls),seconds=sum(r['seconds'] for r in controls)))
    if (out/'verification.json').exists():result['verification']=read(out/'verification.json')['seconds']
    save(out/'computation.json',result)
    model=next(r for r in models if r['name']=='primary')
    save(out/'model-parameters.json',dict(parameters=model['parameters'],geometry_definition=model['geometry_definition'],
        closure=model['closure'],selection=manifest['selection'],
        interpretation='Conditional best native-training model in this bounded campaign; not identified physical truth.'))
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();build(a.output)

"""Read-only diagnosis of all completed global trials; never proposes new fits."""
import numpy as np
from photo2.r297.common import read,save
from .search import OBJECTIVES

def run(out):
    trials={r['id']:r for f in sorted((out/'trials').glob('*.gz')) if (r:=read(f))};state=read(out/'checkpoint.json');predictions=[]
    def vector(r,kind):
        v=r['result']['vectors'];keys=list(v) if kind=='balanced' else [kind,'material'];return np.concatenate([v[k] for k in keys])
    for kind,b in state['branches'].items():
        for block in b['controls']:
            base=trials[block['base']];v=vector(base,kind);J=np.array(block['jacobian']);radius=block['radius']
            for i,key in enumerate(block['keys']):
                for j,sign in enumerate([-1,1]):
                    target=trials[block['trial_ids'][2*i+j]]
                    if not target['feasible']:continue
                    estimate=v+sign*radius*J[:,i];actual=vector(target,kind)
                    predictions.append(dict(objective=kind,base=base['id'],trial=target['id'],parameter=key,radius=radius,sign=sign,derivative_admitted=block['reliable'][i],predicted_reduction=float(v@v-estimate@estimate),actual_reduction=float(v@v-actual@actual),smooth_score_change=target['result']['scores']['reflection']-base['result']['scores']['reflection'],centroid_rms_change_px=target['result']['metrics']['reflection']['rms_px']-base['result']['metrics']['reflection']['rms_px'],missing_change=target['result']['missing']-base['result']['missing']))
    a=np.array([r['predicted_reduction'] for r in predictions]);b=np.array([r['actual_reduction'] for r in predictions]);use=abs(a)+abs(b)>1e-10
    numerical=dict(records=predictions,nonzero_pairs=int(use.sum()),direction_agreement=float(np.mean(np.sign(a[use])==np.sign(b[use]))) if use.any() else None,admitted_columns=sum(x['derivative_admitted'] for x in predictions),actual_GN_proposals=sum(r['tag'].endswith(':guided') for r in trials.values()),policy='Central-difference predicted versus actual fixed-owner squared residual changes at the SAME saved bracket endpoints. Tail-weighted objective remains separately scored. Repeated cache controls preserved; not independent samples or new fitting.')
    save(out/'numerical-descent.json.gz',numerical)
    initial={r['tag'][6:]:r for r in trials.values() if r['tag'].startswith('start:')};height=[];periodic=[]
    for r in read(out/'parameter-responses.json.gz'):
        if r['tag'].startswith('height-light:'):
            _,family,key,value=r['tag'].split(':');base=initial[family];entry=dict(trial=r['id'],family=family,parameter=key,value=float(value),feasible=r['feasible'])
            if r['feasible']:entry.update(score_changes={k:r['result']['scores'][k]-base['result']['scores'][k] for k in OBJECTIVES},reflection_rms_change_px=r['result']['metrics']['reflection']['rms_px']-base['result']['metrics']['reflection']['rms_px'],coherence_change_pp=r['result']['metrics']['ownership']['coherent_percent']-base['result']['metrics']['ownership']['coherent_percent'],missing_change=r['result']['missing']-base['result']['missing'])
            height.append(entry)
        elif r['tag'].startswith('curve:'):
            _,family,key,offset=r['tag'].split(':');base=initial[family];entry=dict(trial=r['id'],family=family,parameter=key,offset=float(offset),feasible=r['feasible'])
            if r['feasible']:
                a=base['result']['anchors']['reflections'];b=r['result']['anchors']['reflections'];entry.update(score_changes={k:r['result']['scores'][k]-base['result']['scores'][k] for k in OBJECTIVES},changed_owners=sum(a[k]!=b[k] for k in a),missing=r['result']['missing'])
            periodic.append(entry)
    comparisons={r['model']:r for r in read(out/'comparison.json')};ablations=[]
    for key,r in comparisons.items():
        if key.endswith('-zeroheight'):
            fitted=comparisons[key.replace('-zeroheight','')];a=r['all'];b=fitted['all'];ablations.append(dict(model=fitted['model'],control=key,reflection_rms_change_px=b['reflection']['rms_px']-a['reflection']['rms_px'],reflection_max_change_px=b['reflection']['maximum_px']-a['reflection']['maximum_px'],boundary_rms_change_px=b['boundary']['rms_px']-a['boundary']['rms_px'],coherence_change_pp=b['ownership']['coherent_percent']-a['ownership']['coherent_percent'],background_change_pp=b['material']['background_occupation_percent']-a['material']['background_occupation_percent'],policy='Fitted globals unchanged; set only three height geometry coefficients to zero. Read-only, no reoptimization.'))
    save(out/'height-controls.json',dict(shared_training_controls=height,final_all_circuit_ablations=ablations));save(out/'periodic-controls.json',periodic)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,6),layout='constrained')
    for kind in OBJECTIVES:
        rs=[r for r in predictions if r['objective']==kind];ax.scatter([r['predicted_reduction'] for r in rs],[r['actual_reduction'] for r in rs],s=9,alpha=.6,label=kind)
    ax.axhline(0,color='gray',lw=.5);ax.axvline(0,color='gray',lw=.5);ax.set(xlabel='Predicted squared-residual improvement',ylabel='Actual native squared-residual improvement',title='Fixed-owner linear predictions at saved native brackets');ax.legend();fig.savefig(out/'review/predicted-actual.png',dpi=140);plt.close(fig)
    return numerical


def predictiveness(out):
    """Descriptive outcome association, not an independent validation experiment."""
    from scipy.stats import spearmanr
    from photo2.r297.common import digest
    summary=read(out/'comparison.json');unique=[];seen=set()
    for row in summary:
        key=digest(row['parameters'])
        if key not in seen:unique.append(row);seen.add(key)
    records=[]
    for kind in OBJECTIVES:
        x=[read(out/'metrics'/f"{r['model']}.json.gz")['development']['scores'][kind] for r in unique]
        for label,fn in [('reflection_rms',lambda m:m['reflection']['rms_D']),('reflection_max',lambda m:m['reflection']['maximum_D']),('boundary_rms',lambda m:m['boundary']['rms_D']),('boundary_max',lambda m:m['boundary']['maximum_D']),('ownership_deficit',lambda m:100-m['ownership']['coherent_percent']),('paper_occupation',lambda m:m['material']['background_occupation_percent']),('foreground_omission',lambda m:m['material']['foreground_omission_percent'])]:
            y=[fn(r['splits']['comparison']) for r in unique];rho=float(spearmanr(x,y).statistic) if np.std(x)>0 and np.std(y)>0 else None
            records.append(dict(training_objective=kind,comparison_outcome=label,spearman_rho=rho,models=len(unique)))
    save(out/'objective-predictiveness.json',dict(records=records,models=[r['model'] for r in unique],interpretation='Descriptive rank association across unique retained settings, not confidence or causal attribution. Positive rho means lower training score accompanies lower comparison error. Historically exposed comparison; small, deliberately selected candidate sample.'))

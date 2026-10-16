"""Descriptive post-seal summaries, no parameter selection using held evidence."""
import csv
import numpy as np
from .core import *

def main():
    diag=read(BASE/'results/diagnosis.json.gz');seal=read(BASE/'results/fit-freeze.json')
    models=read(BASE/'results/native-manifest.json.gz');s=read(BASE/'evidence/section.json.gz')
    selected={r['name']:r for r in seal['selected']};paired=[]
    for start in read(BASE/'evidence/protocol.json')['starts']:
        a=selected['hierarchy-'+start['name']];b=selected['accurate-DE-'+start['name']]
        paired.append(dict(start=start['name'],hierarchy_loss=a['loss'],control_loss=b['loss'],hierarchy_seconds=a['elapsed'],control_seconds=b['elapsed'],hierarchy_evaluations=a['evaluations'],control_evaluations=b['evaluations'],hierarchy_wins=a['loss']<b['loss']))
    # Primary is determined solely by the sealed training objective.
    primary=min((r for r in seal['selected'] if r['name'].startswith('hierarchy-')),key=lambda r:r['loss'])['name']
    summaries=[]
    for m in models:
        d=m['result'];sec=d['secondary'];held=d['withheld_material']
        summaries.append(dict(name=m['name'],hand=d['hand'],train_rms=d['summary']['train']['finite_rms'],held_rms=d['summary']['withheld']['finite_rms'],train_matched=d['summary']['train']['matched'],held_matched=d['summary']['withheld']['matched'],dimension_mae=sec['dimension_mae'],boundary_mae=sec.get('boundary_mae'),paper=sec['paper'],missing=sec['material_missing'],held_paper=held['paper'],held_missing=held['material_missing'],held_valley_mae=held['separator_mae'],local_positions=d.get('local_positions'),flags=d.get('flags'),parameters=d['parameters']))
    with (BASE/'results/comparison.csv').open('w') as stream:
        rows=[{k:v for k,v in r.items() if k!='parameters'} for r in summaries];writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    sensitivity=[]
    for r in diag['sensitivity']:
        v=r['start']['parameters'];J=np.array(r['jacobian'],float);g=np.array(r['groups']);norm=np.array(r['column_norms'])
        response=[]
        for j,name in enumerate(NAMES):
            block={key:float(values[j]) for key,values in r['group_norms'].items() if key!='prediction_only'}
            response.append(dict(parameter=name,step=STEPS[j],group_response=block,largest_block=max(block,key=block.get),total=norm[j]))
        owners=sorted({tuple(p['metrics']['contour_owners']) for p in r['perturbations']})
        sensitivity.append(dict(start=r['start']['name'],resolved_scale_directions=int(np.sum(np.array(r['singular_values'])>=1)),singular_values=r['singular_values'],condition_ratio=r['singular_values'][0]/r['singular_values'][-1],response=response,coupled_pairs=r['coupled_pairs'],contour_owner_alternatives=[list(x) for x in owners],failed_physical_perturbations=sum(not p['physical']['certified'] for p in r['perturbations']),analytic_dimensions=dict(face_diameter=2*v[9],axial_width=2*v[0]*v[9],face_response_per_step={'scale':2*STEPS[9]},axial_response_per_step={'scale':2*v[0]*STEPS[9],'axial':2*v[9]*STEPS[0]})))
    accepted=[r for r in summaries if r['flags']==[]]
    spread={k:dict(minimum=min(r['parameters'][k] for r in accepted),maximum=max(r['parameters'][k] for r in accepted)) for k in NAMES} if accepted else {}
    result=dict(primary_by_sealed_training=primary,paired=paired,summaries=summaries,sensitivity=sensitivity,accepted_training_parameter_spread=spread,numerical_seconds=seal['numerical_seconds'],primary_is_not_physical_truth=True)
    save(BASE/'results/analysis.json',result)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    groups=['reflection','dimension','boundary','material']
    response=np.mean([np.array([r['group_norms'][g] for g in groups]) for r in diag['sensitivity']],axis=0)
    fig,(ax,bx)=plt.subplots(2,1,figsize=(13,7),layout='constrained')
    im=ax.imshow(np.log10(np.maximum(response,.01)),aspect='auto',vmin=-2,vmax=.6,cmap='viridis');ax.set_xticks(range(18),NAMES,rotation=45,ha='right');ax.set_yticks(range(4),groups);ax.set_title('Mean standardized response per declared parameter step (four starts)');fig.colorbar(im,ax=ax,label='log10 response; correlated rows are not independent data')
    for r in diag['sensitivity']:bx.semilogy(np.arange(1,19),r['singular_values'],marker='.',label=r['start']['name'])
    bx.axhline(1,color='gray',ls='--');bx.set_xlabel('Singular direction');bx.set_ylabel('Standardized response');bx.legend(fontsize=8);bx.set_title('A scale diagnostic, not a Fisher confidence analysis');fig.savefig(BASE/'results/sensitivity.png',dpi=150);plt.close(fig)
    print('Primary by sealed training:',primary)
    for r in summaries:
        print(r['name'],{k:round(r[k],3) if isinstance(r[k],float) else r[k] for k in ['train_rms','held_rms','dimension_mae','boundary_mae','paper','missing','held_missing','held_valley_mae','local_positions','flags']})

if __name__=='__main__':main()

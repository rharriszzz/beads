"""Trace deterministic camera/deformation changes separately from index changes."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r254-mpl')
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pattern_r254 import OUT,OLD
import global_fit_r253 as old
from camera_r254 import Model
from evidence_r254 import load_models

def run(out):
    models=load_models(out);records=[];profiles=[];source=json.loads((OLD/'models.json').read_text())
    for m in models:
        base=next((r for r in source if r['model_id']==m['base_model']),None)
        if base is None:base=json.loads((out/f'N{m["n"]}_h{m["h"]:+d}-initial-model.json').read_text())
        before=old.Model(base['n'],base['h'],base['p']);after=Model(m['n'],m['h'],m['p'],m['focal'],m.get('turn_delta',0));ii=np.arange(m['n']);a=before.view.project(before.geometry(ii)['centers']);b=after.view.project(after.geometry(ii)['centers']);delta=np.linalg.norm(b-a,axis=1)
        t=np.linspace(0,1,1024,endpoint=False);p=np.array(m['p']);stretch=old.harmonics(t)@p[6:10];ds,tw=old.correction(t,p)
        records.append(dict(model_id=m['model_id'],base_model=m['base_model'],same_index_displacement_rms=float(np.sqrt(np.mean(delta**2))),same_index_displacement_max=float(delta.max()),stretch_max=float(abs(stretch).max()),stretch_rms=float(np.sqrt(np.mean(stretch**2))),twist_max_deg=float(np.degrees(abs(tw).max())),twist_rms_deg=float(np.degrees(np.sqrt(np.mean(tw**2)))),longitudinal_displacement_max_px=float(abs(ds).max()*after.unscaled_length),elevation=p[4],roll=p[5],turns=after.turns))
        if m['model_id'] in json.loads((out/'display-selection.json').read_text())['display']:
            profiles.extend(dict(model_id=m['model_id'],fraction=float(f),stretch=float(s),twist_deg=float(np.degrees(w))) for f,s,w in zip(t,stretch,tw))
    old.table(out/'geometry-changes.csv',records);old.table(out/'geometry-profiles.csv',profiles)
    fig,axs=plt.subplots(2,1,figsize=(13,7))
    for mid in dict.fromkeys(r['model_id'] for r in profiles):
        rr=[r for r in profiles if r['model_id']==mid];axs[0].plot([r['fraction'] for r in rr],[100*r['stretch'] for r in rr],label=mid);axs[1].plot([r['fraction'] for r in rr],[r['twist_deg'] for r in rr],label=mid)
    axs[0].set(ylabel='Longitudinal stretch (%)',title='C2: bounded deterministic corrections; no centerline shape edit');axs[1].set(xlabel='Material string fraction',ylabel='Added winding phase (degrees)');axs[0].legend(fontsize=8,ncol=2);fig.tight_layout();fig.savefig(out/'C2-geometric-corrections.png',dpi=170);plt.close(fig)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();run(a.output)

"""Machine-readable reporting quantities; preserves all original metric definitions."""
from collections import Counter
import numpy as np
from photo2.r297.common import read,save,sha,utc
from .search import OUT,SPLITS
from .finalize import NAMES

def main():
    rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];diag={m['name']:m for m in read(OUT/'diagnostics.json.gz')['models']};models=[]
    for name in NAMES:
        r=read(OUT/f'{name}-model.json.gz');d=diag[name];rr=[]
        for c in r['early']:
            best=max(c['candidates'],key=lambda c:c['visible_fraction']);rr.append(dict(id=c['id'],modal_index=best['index'],modal_isolated=best['isolated_fraction'],modal_visible=best['visible_fraction'],best_isolated=c['best_isolated'],aliases=[v for v in c['candidates'] if v['index'] in [-15,-14,11,12]]))
        br=read(OUT/f'{name}-brackets.json.gz');metrics={}
        for part,k in enumerate(SPLITS):
            bs=[b for b in br if b['split']==part];metrics[k]=dict(**r[k]['vector'],finite_bracket_p95=float(np.percentile([b['displacement'] for b in bs if b['found']],95)),finite_bracket_max=max(b['displacement'] for b in bs if b['found']),missing_brackets=sum(not b['found'] for b in bs),group_summary=d['group_metrics'][k],readiness=r['readiness'][k])
        models.append(dict(name=name,trial=r['source_trial'],epoch=r['source_epoch'],early=rr,early_mean_visible=float(np.mean([x['modal_visible'] for x in rr])),metrics=metrics,first_failure=d['first_failure'],physical=dict(bodies=r['target']['full_bodies'],witnesses=len(r['physical']['witnesses']),minimum_support_gap=min(w['gap_units'] for w in r['physical']['witnesses']),paper=d['paper']),changed_R316_owners=sum(z['modal']['index']!=z['fixed_R316_index'] for z in d['regions']),mean_fixed_R316_visible=float(np.mean([z['fixed_R316_visible'] for z in d['regions']])),mean_modal_visible=float(np.mean([z['modal']['modal_fraction'] for z in d['regions']])),rates=r['compact_rates'],parameters={k:r['parameters'].get(k) for k in ['radius','axial','tilt','rounding','exterior','edge','face','radial_cant','compact_cant','compact_centers','compact_phase','compact_spacing','compact_tilt','translation','elevation']}))
    cached=[r['cache'] for r in rows if 'cache' in r];ranges={}
    for k in ['radius','axial','tilt','elevation','radial_cant']:
        x=[r['parameters'].get(k,0.) for r in rows];ranges[k]=dict(minimum=min(x),maximum=max(x))
    save(OUT/'scientific-summary.json',dict(utc=utc(),trials=len(rows),classifications=dict(Counter(r['classification'] for r in rows)),stages=dict(Counter(r['stage'] for r in rows)),models=models,parameter_ranges=ranges,cache=dict(evaluations=len(cached),median_reused_beads=float(np.median([r['reused_beads'] for r in cached])),median_total_layers=float(np.median([r['layer_count'] for r in cached])),median_render_seconds=float(np.median([r['total_seconds'] for r in cached])),policy='Observed run diagnostics, not a matched speedup benchmark.'),historical_groups=read(OUT/'correlation-groups.json'),bright=read(OUT/'bright-readiness.json')))
if __name__=='__main__':main()

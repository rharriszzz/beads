"""Photographic diagnostics, never real-body ground truth or acceptance scores."""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r282.common import ROOT,read,save,photo,pixels
from .run import OUT
from .review import REVIEW,focus
from .methods import COLOR_METHODS,BLACK_METHODS

def main():
    native,_,_=photo();curve=np.array(read(ROOT/'photo2/r282/results/centerline.json')['points']);baseline=read(ROOT/'photo2/r283/results/phase1.json.gz')['records'];by={r['record_id']:r for r in baseline}
    data=[read(OUT/(c['name']+'.json.gz')) for c in read(OUT/'cases.json')];observations=[o for d in data for o in d['observations']];summary={};anchors=[]
    for color in ('red','yellow','black'):
        summary[color]={}
        for method in BLACK_METHODS if color=='black' else COLOR_METHODS:
            os=[o for o in observations if o['color']==color and method in o['variants']];rs=[o['variants'][method] for o in os];good=[r for r in rs if r['measured_support']];valid=[r for r in good if r['metrics']['area']<=870]
            overlaps=[p for d in data for p in d['pairs'] if p['method']==method and p['kind']=='overlap-owner-unresolved' and all(next(o for o in d['observations'] if o['id']==i)['color']==color for i in p['ids'])]
            def avg(key):
                values=[r['metrics'][key] for r in good if r['metrics'][key] is not None]
                return float(np.mean(values)) if values else None
            summary[color][method]=dict(observations=len(rs),nonempty=len(good),admissible_area=len(valid),
                near=sum(r['centerline']['near'] for r in good),crossing=sum(r['centerline']['crosses'] for r in good),
                admissible_near=sum(r['centerline']['near'] for r in valid),admissible_crossing=sum(r['centerline']['crosses'] for r in valid),
                retained_mean=float(np.mean([r['metrics']['retained_fraction'] for r in rs])),centroid_shift_mean=avg('centroid_shift'),
                boundary_gradient_mean=avg('boundary_gradient'),thin_fraction_mean=avg('thin_fraction'),turn_energy_mean=avg('turn_energy'),
                seed_lost=sum(not r['metrics']['seed_preserved'] for r in rs),overlap_pairs=len(overlaps),overlap_pixels=sum(p['shared_pixels'] for p in overlaps),
                possible_partition_flags=sum(r['method_evidence'].get('possible_false_partition',False) for r in rs),
                brighter_neighbor_flags=sum(r['method_evidence'].get('brighter_neighbor_in_support',False) for r in rs),
                ineligible_peak_flags=sum(r['method_evidence'].get('peak_material_eligible') is False for r in rs),
                snake_guard_rejections=sum(r['method_evidence'].get('snake_guard_rejected',False) for r in rs),
                perturb_mean_distance=float(np.mean([p['contour_mean_distance'] for r in rs for p in r['method_evidence'].get('perturbations',[]) if p['contour_mean_distance'] is not None])) if method.startswith('R') and method!='R283' else None,
                components={str(i):sum(r['metrics']['components']==i for r in rs) for i in (0,1)},
                calibrated_precision=None,full_body_recall=None,false_partitions_verified=None,verified_leaks=None)
    for d in data[3:]:
        for k,identifier in enumerate(d['case']['selection_ids']):
            src=by[identifier];ob=min(d['observations'],key=lambda o:np.linalg.norm(np.array(o['seed'])-src['seed']))
            label=f"{d['case']['name']} anchor {k+1} ({ob['color']})";filename=d['case']['name']+f'-anchor-{k+1}.png'
            table=focus(native,curve,d,[(label,ob['seed'])],REVIEW/filename)
            anchors.append(dict(case=d['case']['name'],source_id=identifier,selected_observation=ob['id'],seed_distance=float(np.linalg.norm(np.array(ob['seed'])-src['seed'])),figure=filename,metrics=table))
    # Feature pairs and side accounting, with each observation ID counted once.
    combinations={}
    for cm,bm in [('A','A'),('T','R1'),('T','R4'),('I','R1'),('J','R1')]:
        rs=[o['variants'][bm if o['color']=='black' else cm] for o in observations];rs=[r for r in rs if r['measured_support'] and r['metrics']['area']<=870]
        sides={s:sum(r['centerline']['near'] and r['centerline']['side']==s for r in rs) for s in ('crossing','negative','positive')}
        flank=[]
        for d in data:
            rr=[o['variants'][bm if o['color']=='black' else cm] for o in d['observations']];rr=[r for r in rr if r['centerline']['near'] and 0<r['metrics']['area']<=870]
            for i,a in enumerate(rr):
                for b in rr[i+1:]:
                    if abs(a['centerline']['arc_px']-b['centerline']['arc_px'])<=16 and {a['centerline']['side'],b['centerline']['side']}=={'positive','negative'}:
                        if not set(map(tuple,pixels(a['measured_support'])))&set(map(tuple,pixels(b['measured_support']))):flank.append([a['record_id'],b['record_id']])
        combinations[cm+'+'+bm]=dict(nonempty_admissible=len(rs),near=sum(sides.values()),sides=sides,disjoint_flanking_candidate_pairs=flank,
            warning='Observed features, not distinct beads; black-body crossing unknown. Counts include unresolved cues.')
    save(OUT/'validation.json',dict(by_color=summary,anchors=anchors,combinations=combinations,total_observations=len(observations),unique_seeds=len({tuple(o['seed']) for o in observations}),
        interpretation='Overlaps are algorithmic conflict diagnostics, not verified leakage. Marker multiplicity is not verified body splitting. No calibrated high-confidence count or full-body recall.'))
    print(summary,flush=True)

if __name__=='__main__':main()

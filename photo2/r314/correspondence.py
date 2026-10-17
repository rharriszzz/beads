"""Conservative fixed-lobe tracking in bead-local surface coordinates.

Component ordinals are not identities: connected components may reorder, split,
merge or disappear. Ambiguous tracking is a missing prediction for a strict maximum,
never a convenient substitution. This is uncalibrated numerical tracking, not proof
of photographed physical identities; the geometry gate remains separate.
"""
import numpy as np

def track(reference,current,tolerance_radius=.25,ambiguity_radius=.05):
    output=[];events=[];used=set()
    for r in reference:
        candidates=[p for p in current if p['index']==r['index']]
        distance=[float(np.linalg.norm(np.array(p['peak_local_radius'])-r['peak_local_radius'])) for p in candidates]
        order=np.argsort(distance);reason=None
        if not len(order) or distance[order[0]]>tolerance_radius:reason='missing_or_excess_local_surface_motion'
        elif len(order)>1 and distance[order[1]]-distance[order[0]]<ambiguity_radius:reason='ambiguous_lobe_competitors'
        else:
            p=candidates[order[0]];key=(p['index'],p['component'])
            if key in used:reason='merged_or_reused_lobe'
            else:
                used.add(key);output.append(dict(p,lobe=r['lobe'],reference_local_radius=r['peak_local_radius'],tracking_distance_radius=distance[order[0]]))
        events.append(dict(index=r['index'],lobe=r['lobe'],reason=reason,alternatives=[dict(component=candidates[j]['component'],distance_radius=distance[j]) for j in order],verified_physical_identity=False))
    # If two reference lobes compete for one component, invalidate both rather than
    # let iteration order decide which difficult feature survives.
    merged={(e['index'],e['alternatives'][0]['component']) for e in events if e['reason']=='merged_or_reused_lobe'}
    output=[p for p in output if (p['index'],p['component']) not in merged]
    return dict(predictions=output,events=events,unresolved=any(e['reason'] for e in events),policy='Local surface motion bounds are numerical tracking limits, not measured physical shape constraints.')

def evaluate_fixed(epoch,predictions,assignments=None,geometry_passed=False):
    """Validate the stored map and cohort too, not just an optional replacement map."""
    from photo2.r297.common import digest
    from .bright import evaluate
    if digest(epoch['assignments'])!=epoch['assignment_hash']:
        raise ValueError('Stored correspondence map changed; new epoch required')
    expected=[o['id'] for o in epoch['observations'] if o.get('reliable_correspondence') and o.get('reliably_localized') and o.get('specular_status')=='supported']
    if epoch['cohort']!=expected:raise ValueError('Predeclared cohort changed')
    return evaluate(epoch,predictions,assignments,geometry_passed)

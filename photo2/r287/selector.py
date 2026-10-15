"""Interpretable J/M partial choice. No color, coordinates, IDs or review labels.

Both means retain two alternatives, not their union. Abstain retains source
observations but supplies no accepted support. Reliability remains uncalibrated.
"""
PARAMETERS=dict(cap=870,minimum_area=12,minimum_pigment_fraction=.60,maximum_paper_fraction=.03,
    minimum_exposure=.025,minimum_core_pigment=.4,minimum_stability_iou=.70,
    maximum_centroid_shift=4.,domain_iou=.90,diffuse_gain_fraction=.30,
    diffuse_gain_pixels=50,bright_continuation_fraction=.25,coherent_bright_pixels=8,minimum_diffuse_route_fraction=.85,
    comparable_iou=.65,policy='v2-direct-shading-continuity-with-vetoes')

def decide(e):
    reasons={};valid={}
    for name in ('J','M'):
        c=e['candidates'][name];s=c['stability'];bad=[]
        if not PARAMETERS['minimum_area']<=c['area']<=PARAMETERS['cap']:bad.append('empty/tiny or exceeds established area ceiling')
        if c['components']!=1 or not c['seed_supported']:bad.append('not connected to local photographic cue')
        if c['pigment_fraction']<PARAMETERS['minimum_pigment_fraction'] or c['paper_fraction']>PARAMETERS['maximum_paper_fraction']:bad.append('weak pigment/background distinction')
        if e['core_exposure_Y']<PARAMETERS['minimum_exposure'] or e['core_pigment_fraction']<PARAMETERS['minimum_core_pigment']:bad.append('weak native cue illumination/material')
        if c['coherent_seam_conflicts']:bad.append('support includes both sides of a coherent multi-route dark seam')
        if s['minimum_iou']<PARAMETERS['minimum_stability_iou'] or s['maximum_centroid_shift']>PARAMETERS['maximum_centroid_shift']:bad.append('unstable under modest photographic/seed perturbation')
        if s['domain_minimum_iou']<PARAMETERS['domain_iou'] or s['window_contact']:bad.append('computational domain remains a boundary explanation')
        valid[name]=not bad;reasons[name]=bad
    if not any(valid.values()):return dict(decision='neither reliable; abstain',alternatives=[],reasons=['Both candidates have unresolved photographic evidence.'],candidate_objections=reasons)
    if valid['J']!=valid['M']:
        choice='J' if valid['J'] else 'M';return dict(decision='prefer '+choice,alternatives=[choice],reasons=['Only '+choice+' survives the explicit evidence vetoes; this is an uncalibrated preference.'],candidate_objections=reasons)
    j=e['candidates']['J']['boundary'];m=e['candidates']['M']['boundary']
    routes=e['diffuse_routes']
    continuation=(routes['supported_pixels']>=PARAMETERS['diffuse_gain_pixels'] and routes['supported_pixels']/max(1,e['candidates']['J']['area'])>=PARAMETERS['diffuse_gain_fraction'] and routes['supported_fraction']>=PARAMETERS['minimum_diffuse_route_fraction'])
    if continuation:
        return dict(decision='prefer M',alternatives=['M'],reasons=['Substantial M-only diffuse pigment is supported by multiple direct color/intensity routes without a dark valley and renewed rise; both candidates pass the independent seam/stability vetoes.'],candidate_objections=reasons)
    if e['agreement_iou']>=PARAMETERS['comparable_iou']:
        return dict(decision='both comparably supported',alternatives=['J','M'],reasons=['Both survive evidence checks; moderate boundary differences do not establish a unique photographic interior.'],candidate_objections=reasons)
    return dict(decision='neither reliable; abstain',alternatives=[],reasons=['Substantial J/M disagreement remains without sufficient ownership/continuation evidence to choose.'],candidate_objections=reasons)

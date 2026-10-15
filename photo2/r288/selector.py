"""Five-way experimental interpretation; J inadequacy independent of M instability."""
from photo2.r287.selector import decide as old_decide
PARAMETERS=dict(minimum_area=12,maximum_area=870,minimum_pigment=.6,maximum_paper=.03,
 minimum_stability=.7,maximum_centroid_shift=4.,minimum_domain_iou=.9,
 meaningful_diffuse_pixels=50,meaningful_diffuse_fraction=.30,comparable=.70,unchanged=.98)

def decide(e):
    old=old_decide(e);objections={m:list(v) for m,v in old['candidate_objections'].items()}
    for m in ('E','W'):
        c=e['candidates'][m];s=c['stability'];bad=[]
        if not 12<=c['area']<=870:bad.append('tiny/empty or area ceiling exceeded')
        if c['components']!=1 or not c['seed_supported']:bad.append('not connected to local photographic cue')
        if c['pigment_fraction']<.6 or c['paper_fraction']>.03 or e['core_exposure_Y']<.025 or e['core_pigment_fraction']<.4:bad.append('weak native material/illumination evidence')
        if c['coherent_seam_conflicts']:bad.append('contains both sides of independently tested coherent seam')
        if s['minimum_iou']<.7 or s['maximum_centroid_shift']>4:bad.append('new support remains perturbation-sensitive')
        if s['domain_minimum_iou']<.9 or s['window_contact']:bad.append('computational boundary remains plausible')
        objections[m]=bad
    good={m:not v for m,v in objections.items()}
    # New material must have evidence beyond merely being inside M or outside J.
    inadequacy=[]
    for m in ('E','W'):
        d=e['continuation_to_new'][m]
        if good[m] and d['supported_pixels']>=50 and d['supported_pixels']/max(1,e['candidates']['J']['area'])>=.30:
            inadequacy.append(dict(candidate=m,supported_pixels=d['supported_pixels'],reason='Stable material/seam-checked candidate retains substantial directly supported diffuse pigment beyond J.'))
    if inadequacy:good['J']=False;objections['J'].append('independent inadequacy: excludes substantial supported diffuse pigment')
    valid_new=[m for m in ('W','E') if good[m]]
    decision='neither reliable; abstain';alternatives=[];reason='Photographic defects or conflicting explanations remain; no forced fallback.'
    if len(valid_new)==2 and e['new_agreement_iou']<.70:
        reason='Both new candidates pass local checks but disagree substantially; ownership remains unresolved.'
    elif valid_new and (inadequacy or not good['M'] or not good['J']):
        m=valid_new[0]
        if good['M'] and e['new_M_iou'][m]>=.98:
            decision='prefer M';alternatives=['M'];reason='M is independently reproduced by the supported new construction, with no measured instability veto.'
        else:
            decision='new interior';alternatives=[m];reason=m+' supplies a connected, stable, material/seam-supported interior; instability of another mask does not erase these pixels.'
    elif good['J'] and good['M']:
        if e['agreement_iou']>=.65:decision='both plausible';alternatives=['J','M'];reason='Both old interiors remain plausible; no independently significant excluded diffuse region requires a unique replacement.'
        elif valid_new:
            decision='new interior';alternatives=[valid_new[0]];reason='New construction supplies additional photographic evidence for an interior amid old J/M disagreement.'
    elif good['J']:
        decision='prefer J';alternatives=['J'];reason='J passes photographic checks and no reliable diffuse-continuation defect is established; uncertainty is retained.'
    elif good['M']:
        decision='prefer M';alternatives=['M'];reason='M passes checks; no new supported interior establishes a preferable measurement.'
    return dict(decision=decision,alternatives=alternatives,reasons=[reason],candidate_objections=objections,J_inadequacy=inadequacy,physical_ownership='unknown',reliability='unrated evidence; not calibrated acceptance')

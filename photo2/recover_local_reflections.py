"""R196: assisted native reflection/region diagnosis around confirmed point D.

The maker point selects this diagnostic window only. No automatic detector,
simulated-position fit, live annotation or previously trusted ledger is changed.
Local peaks and small interior patches remain proposals until reviewed.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import uuid

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi
from skimage.feature import peak_local_max

import auto_label_beads as auto
from bead_evidence_inventory import connected_near, encode_pixels, region_record
from label_beads import atomic_json
from review_bead_evidence import pixels


def native_peaks(rgb, origin, scales=(.6, .8, 1.2, 1.8), broad_sigma=5., floor=.003):
    """Unclassified local V-contrast maxima; never proof of a bead/reflection."""
    hsv = rgb_to_hsv(np.asarray(rgb, float) / 255)
    value = hsv[:, :, 2]
    broad = ndi.gaussian_filter(value, broad_sigma)
    runs = []
    for sigma in scales:
        response = ndi.gaussian_filter(value, sigma) - broad
        locations = peak_local_max(response, min_distance=3, threshold_abs=floor)
        runs.append(dict(sigma=sigma, response=response, locations=locations))
    output = []
    for y, x in runs[1]['locations']:
        support_radius = 4
        yy, xx = np.indices(value.shape)
        disk = np.hypot(xx-x, yy-y) <= support_radius
        ring = (np.hypot(xx-x, yy-y) > support_radius) & (np.hypot(xx-x, yy-y) <= 8)
        surround = float(np.median(value[ring]))
        peak = float(value[y, x])
        threshold = min(peak, surround + max(0., peak-surround) * .6)
        bright = connected_near(disk & (value >= threshold), np.array([x, y]), maximum_shift=0.)
        weights = np.maximum(value[bright]-surround, .001) ** 2
        xy = np.average(np.column_stack([xx[bright], yy[bright]]), axis=0, weights=weights) + origin
        alternatives = []
        for fraction in [.5, .7]:
            mask = connected_near(disk & (value >= min(peak, surround + max(0., peak-surround)*fraction)),
                                  np.array([x, y]), maximum_shift=0.)
            alternatives.append((np.average(np.column_stack([xx[mask], yy[mask]]), axis=0,
                weights=np.maximum(value[mask]-surround, .001)**2)+origin).tolist())
        matches = []
        for run in runs:
            locations = run['locations']
            if len(locations):
                distances = np.linalg.norm(locations-[y, x], axis=1)
                closest = int(np.argmin(distances))
                if distances[closest] <= 3:
                    q = locations[closest]
                    matches.append(dict(sigma=run['sigma'], xy=(q[::-1]+origin).tolist(),
                                        response=float(run['response'][tuple(q)])))
        output.append(dict(peak_xy=(np.array([x, y])+origin).tolist(), xy=xy.tolist(),
            response=float(runs[1]['response'][y, x]), peak_value=peak, surround_value=surround,
            positive_peak_surround_contrast=peak-surround, peak_saturation=float(hsv[y, x, 1]),
            localization_status='positive raw peak above ring median' if peak > surround else
                'unresolved: contrast-filter maximum has no positive raw peak above ring median',
            pixel_runs=encode_pixels(bright, origin), pixels=int(bright.sum()),
            scale_matches=matches, threshold_alternative_positions=alternatives,
            threshold_sensitivity_pixels=float(np.max(np.linalg.norm(np.array(alternatives)-xy, axis=1))),
            role='Bright feature hypothesis; not certified specular reflection or body identity'))
    return output


def small_dark_patch(hsv, point, origin):
    """Assisted local appearance patch, not a recovered dark-body boundary."""
    yy, xx = np.indices(hsv.shape[:2])
    local_point = np.asarray(point)-origin
    distance = np.hypot(xx-local_point[0], yy-local_point[1])
    value = hsv[:, :, 2]
    dark_limit = float(np.quantile(value[distance <= 7], .8))
    support = (distance <= 7) & (value <= dark_limit)
    region, _ = region_record(support, local_point, origin, inset=1., footprint=3.)
    return dict(region=region, value_limit=dark_limit, support_radius_pixels=7,
                footprint_radius_pixels=3, role='Unreviewed positive patch around confirmed point; nearby black bodies/shadow can share appearance')


def apply_local_answers(prior, report, answer):
    """Positive region review and negative reflection review have separate scopes."""
    if answer['target_observation_id'] != report['target']['observation_id']:
        raise ValueError('Reviewed D identity changed')
    points=[dict(label=p['question_label'],hypothesis_id=p['hypothesis_id'],xy=p['xy'])
            for p in report['peaks'] if p.get('question_label')]
    replies=answer['answers']
    if replies['Q196.1']['answer']!='Neither' or replies['Q196.1']['points']!=points:
        raise ValueError('Negative reflection answer differs from pictured hypotheses')
    if replies['Q196.2']['answer']!='Yes' or replies['Q196.2']['region']!=report['assisted_sampling_patch']['region']:
        raise ValueError('Positive region answer differs from pictured sampling pixels')
    facts=deepcopy(prior)
    facts['region_facts'].append(dict(observation_id=report['target']['observation_id'],
        appearance='black',region=deepcopy(replies['Q196.2']['region']),
        confirmation='Maker yes R198 / Q196.2: safely inside D away from seams/background',
        source=answer['report_source'],supporting_image=answer['supporting_image'],
        supporting_image_sha256=answer['supporting_image_sha256'],
        limits='Confirmed positive sampling pixels/loop only; geometric guard is not a measured numeric bead margin, body boundary, center or outward point'))
    facts['negative_reflection_facts']=[dict(target_observation_id=report['target']['observation_id'],
        hypothesis_id=p['hypothesis_id'],xy=p['xy'],confirmation='R197 / Q196.1: neither is a specular reflection on D',
        limits='Not a D reflection; other body ownership, specularity elsewhere and background/texture interpretations unresolved') for p in points]
    for gap in facts['confirmed_coverage_gaps']:
        if gap['observation_id']==report['target']['observation_id']:
            gap['region_status']='maker-confirmed 13-pixel positive patch R198'
            gap['reflection_status']='unresolved; P1/P2 excluded as D specular reflections R197'
    facts.update(request='R196–R198',local_answer_requests=['R197','R198'],complete=False,
        stage='D positive patch confirmed; its specular reflection and other aliases still unresolved')
    return facts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=auto.ROOT/'photo2/review/r196')
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    previous = auto.ROOT/'photo2/review/r193'
    old_summary = json.loads((previous/'summary.json').read_text())
    protected = {name:auto.sha(auto.ROOT/name) for name in old_summary['preserved_inputs']}
    facts = json.loads((previous/'trusted-facts.json').read_text())
    target = facts['confirmed_coverage_gaps'][0]
    point = np.array(target['xy'], float)
    data_path = auto.ROOT/'photo2/review/r192/candidates.json'
    data = json.loads(data_path.read_text()); rows = data['records']
    image = ImageOps.exif_transpose(Image.open(auto.ROOT/'beads-photo-2.jpg')).convert('RGB')
    if auto.sha(auto.ROOT/'beads-photo-2.jpg') != data['image_sha256']:
        raise ValueError('Source photo changed')
    diameter = data['parameters']['native_diameter']
    lo = np.maximum(0, np.floor(point-diameter*2.5)).astype(int)
    hi = np.minimum(image.size, np.ceil(point+diameter*2.5)).astype(int)
    rgb = np.asarray(image)[lo[1]:hi[1], lo[0]:hi[0]]
    hsv = rgb_to_hsv(rgb/255.)
    # Image-derived scale; native maxima precede any candidate-alias annotations.
    peaks = native_peaks(rgb, lo, broad_sigma=diameter*.20)
    peaks = [p for p in peaks if np.linalg.norm(np.array(p['xy'])-point) <= diameter*1.2]
    modes = data['parameters']['detector']['hue_modes_degrees']
    saturation_floor = data['parameters']['detector']['saturation_floor']
    for peak in peaks:
        xy = pixels(peak).astype(int)-lo
        appearance = hsv[xy[:, 1], xy[:, 0]]
        hue_family = np.zeros(len(appearance), bool)
        for mode in modes:
            hue_family |= abs((appearance[:, 0]*360-mode+180)%360-180) <= 20
        peak['learned_color_fraction'] = float(np.mean(hue_family & (appearance[:, 1] >= saturation_floor)))
        peak['distance_from_D_pixels'] = float(np.linalg.norm(np.array(peak['xy'])-point))
        nearest = sorted(rows, key=lambda r:np.linalg.norm(np.array(r['seed_xy'])-peak['xy']))[:3]
        peak['nearby_observations'] = [dict(observation_number=r['observation_number'],
            observation_id=r['observation_id'], kind=r['kind'], status=r['status'],
            distance_pixels=float(np.linalg.norm(np.array(r['seed_xy'])-peak['xy']))) for r in nearest]
        peak['hypothesis_id'] = str(uuid.uuid5(uuid.NAMESPACE_URL,
            f"{data['image_sha256']}:native-reflection-hypothesis:{peak['peak_xy']}"))
    peaks.sort(key=lambda p:(p['distance_from_D_pixels'], -p['response']))
    # Select two near-D features not already close to a frozen observation.
    # This is a question selector, not an automatic ownership or color decision.
    unmatched = [p for p in peaks if p['positive_peak_surround_contrast'] > 0 and
                 p['nearby_observations'][0]['distance_pixels'] > diameter*.5]
    selected = unmatched[:2]
    for label, peak in zip(['P1','P2'], selected): peak['question_label'] = label
    try:
        patch = small_dark_patch(hsv, point, lo)
    except ValueError as exc:
        patch = dict(region=None, unresolved_reason=str(exc))
    # Explicit assisted sampling disk after the intensity inset failed. This
    # geometric support is not bead evidence or a detector fallback.
    yy,xx = np.indices(hsv.shape[:2])
    geometric_support = np.hypot(xx-(point[0]-lo[0]),yy-(point[1]-lo[1])) <= 7
    sampling_region,_ = region_record(geometric_support,point-lo,lo,inset=1.,footprint=2.)
    sampling_region['margin_role'] = 'Geometric guard only; no measured margin to bead boundary or rejected appearance'
    sampling = dict(region=sampling_region,radius_pixels=2.,
        status='unreviewed assisted sampling proposal',
        role='Tiny disk around maker-confirmed point; does not establish ownership of surrounding pixels')
    # Replay the unchanged coarse response to explain why these were not selected.
    detector = auto.detect(np.array(image))
    v = detector['rgb'].max(axis=2); d = detector['diameter']
    response = ndi.gaussian_filter(v, max(.65, min(1.5, d*.08))) - ndi.gaussian_filter(v, d*.40)
    coarse_peaks = peak_local_max(response, min_distance=2,
        threshold_abs=detector['parameters']['reflection_response_floor'], labels=detector['band'])
    scale = float(np.sqrt(np.prod(detector['scale'])))
    original_narrow = max(.65,min(1.5,d*.08))/scale
    original_broad = d*.40/scale
    native_value = hsv[:,:,2]
    variants = dict(native_equivalent_original=(original_narrow, original_broad),
        native_narrow_only=(.8,original_broad),
        native_broad_only=(original_narrow,diameter*.20),
        native_both=(.8,diameter*.20))
    fields = {name:ndi.gaussian_filter(native_value,a)-ndi.gaussian_filter(native_value,b)
              for name,(a,b) in variants.items()}
    for peak in selected:
        coarse = (np.asarray(peak['peak_xy'])+.5)*detector['scale']-.5
        x, y = np.rint(coarse).astype(int)
        peak['coarse_diagnostic'] = dict(analysis_xy=coarse.tolist(),
            response=float(response[y, x]), response_floor=detector['parameters']['reflection_response_floor'],
            in_search_band=bool(detector['band'][y, x]),
            nearest_extracted_peak_pixels=float(np.min(np.linalg.norm(coarse_peaks-coarse[::-1],axis=1))),
            nearby_rejections=[p for p in detector['reflection_rejections']
                               if np.linalg.norm(np.array(p['source_xy'])-peak['xy']) < diameter*.5])
        local = (np.asarray(peak['peak_xy'])-lo).astype(int)
        peak['kernel_comparison'] = {name:dict(narrow_sigma=a,broad_sigma=b,
            response=float(fields[name][local[1],local[0]])) for name,(a,b) in variants.items()}
    alias_candidates = [dict(observation_number=r['observation_number'], observation_id=r['observation_id'],
        kind=r['kind'], status=r['status'], seed_xy=r['seed_xy'], reflection=r.get('reflection'),
        distance_from_D_pixels=float(np.linalg.norm(np.array(r['seed_xy'])-point)),
        relation='maker-confirmed distinct from D' if r['observation_number']==777 else 'unresolved')
        for r in rows if np.linalg.norm(np.array(r['seed_xy'])-point) <= diameter*2.5]
    report = dict(request='R196', role='Assisted local diagnosis only; no automatic-runtime change',
        image_sha256=data['image_sha256'], target=target, crop=[*lo.tolist(), *hi.tolist()],
        native_diameter=diameter, parameters=dict(narrow_sigmas=[.6,.8,1.2,1.8],
            broad_sigma=diameter*.20, response_floor=.003, peak_spacing=3,
            search_radius_diameters=1.2, alternative_support_fractions=[.5,.7]),
        peaks=peaks, selected_hypotheses=[p['hypothesis_id'] for p in selected], dark_patch=patch,
        assisted_sampling_patch=sampling,
        alias_candidates=alias_candidates, trusted_update=False,
        limitations='Scale persistence/contrast does not prove specularity. Dark patches can cross same-color neighbors or shadow. No existing alias except R777 resolved.')
    atomic_json(args.output/'report.json', report)
    # Wider raw context keeps the neighboring body at R visible.
    display = [point[0]-85, point[1]-82, point[0]+80, point[1]+83]
    fig, axes = plt.subplots(1,3,figsize=(15,6),layout='constrained')
    for ax in axes[:2]: ax.imshow(image)
    axes[2].imshow(hsv[:,:,2],cmap='gray',vmin=.04,vmax=.25,
        extent=[lo[0]-.5,hi[0]-.5,hi[1]-.5,lo[1]-.5])
    r777 = next(r for r in rows if r['observation_number']==777)
    labels = [('D',point),('R777',r777['reflection']['xy'])]+[(p['question_label'],p['xy']) for p in selected]
    offsets = {'D':[23,0], 'R777':[-30,18], 'P1':[24,17], 'P2':[23,-18]}
    for ax in axes:
        ax.set_xlim(display[0],display[2]);ax.set_ylim(display[3],display[1]);ax.axis('off')
        for label,xy in labels:
            ax.annotate(label,xy,xytext=np.array(xy)+offsets[label],color='cyan',fontsize=9,
                bbox=dict(facecolor='black',alpha=.75,pad=1),arrowprops=dict(arrowstyle='->',color='cyan',lw=.6))
    loop=np.array(sampling_region['loop_xy']);axes[1].plot(*loop.T,color='lime',lw=.8)
    for peak in selected: axes[1].plot(*peak['xy'],'+',color='cyan',ms=5,mew=.8)
    axes[0].set_title('Raw photo; arrows locate hypotheses')
    axes[1].set_title('Green: proposed D sampling disk; cyan: features')
    axes[2].set_title('Diagnostic V stretch 0.04–0.25; clipped')
    fig.savefig(args.output/'D-reflection-question.png',dpi=170);plt.close(fig)
    # Map shows all native peaks, not only the two selected question points.
    fig, axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    axes[0].imshow(image)
    resp=ndi.gaussian_filter(hsv[:,:,2],.8)-ndi.gaussian_filter(hsv[:,:,2],diameter*.20)
    axes[1].imshow(resp,cmap='coolwarm',vmin=-.08,vmax=.08,
        extent=[lo[0]-.5,hi[0]-.5,hi[1]-.5,lo[1]-.5])
    for ax in axes:
        ax.set_xlim(point[0]-40,point[0]+40);ax.set_ylim(point[1]+40,point[1]-40)
        for i,p in enumerate(peaks,1):
            ax.plot(*p['xy'],'+',color='cyan',ms=4)
            ax.text(p['xy'][0]+2,p['xy'][1]-2,str(i),fontsize=6,color='white',bbox=dict(facecolor='black',alpha=.5,pad=.2))
        ax.plot(*point,'o',mfc='none',color='lime',ms=6)
    axes[0].set_title('Raw: all local peak hypotheses')
    axes[1].set_title('Native V contrast, sigma 0.8 minus broad')
    fig.savefig(args.output/'native-peak-context.png',dpi=160);plt.close(fig)
    answer_path=auto.ROOT/'photo2/D-interior-answers-r197-r198.json'
    answer=json.loads(answer_path.read_text())
    if answer['image_sha256']!=data['image_sha256'] or auto.sha(args.output/'report.json')!=answer['report_sha256'] or \
            auto.sha(args.output/'D-reflection-question.png')!=answer['supporting_image_sha256']:
        raise ValueError('Reviewed local pixels/question image changed')
    updated_facts=apply_local_answers(facts,report,answer)
    atomic_json(args.output/'trusted-facts.json',updated_facts)
    scope_path=auto.ROOT/'photo2/position-basis-scope-r199.json'
    scope=json.loads(scope_path.read_text())
    # User R199 excludes difficult black bodies from the current position basis,
    # without erasing already confirmed pixels or requiring complete coverage.
    active_regions=[dict(observation_id=f['observation_id'],
        maker_number=f.get('maker_number'),observation_number=f.get('observation_number'),
        appearance=f['appearance'],use='Positive body/interior constraints; not exact visible center or minor-outward anchor')
        for f in updated_facts['region_facts'] if f['observation_id']!=target['observation_id']]
    active=dict(request='R199',scope_source='photo2/position-basis-scope-r199.json',
        trusted_source='photo2/review/r196/trusted-facts.json',
        region_records=active_regions,black_reflection_locators=updated_facts['black_reflection_point_facts'],
        colored_point_identities=[f for f in updated_facts['other_point_facts'] if f.get('appearance') in ['red','yellow']],
        excluded=[dict(observation_id=target['observation_id'],reason=scope['D']['reason'],
            fact_retained='R198 confirmed positive interior')],
        future_saved_centers=dict(source='photo2/output/tangent-viewer/centers.json',
            source_sha256=protected['photo2/output/tangent-viewer/centers.json'],
            count=len(json.loads((auto.ROOT/'photo2/output/tangent-viewer/centers.json').read_text())['points']),
            status='Existing maker visible-part center marks; next audit for new color/obvious-reflection scope before selection'),
        requires_complete_inventory=False,matching_performed=False,
        limits='Records are different evidence types with possible aliases, not a count of independent beads. Reflection/interior points are not exact outward anchors.')
    atomic_json(args.output/'active-position-basis.json',active)
    if any(auto.sha(auto.ROOT/name)!=digest for name,digest in protected.items()):
        raise ValueError('Preserved input changed during this read-only diagnosis')
    sources=[Path(__file__),data_path,previous/'trusted-facts.json',answer_path,scope_path,
             auto.ROOT/'photo2/ownership-answers-r194-r195.json',
             auto.ROOT/'photo2/bead_evidence_inventory.py',auto.ROOT/'photo2/auto_label_beads.py',
             auto.ROOT/'photo2/test_local_reflections.py',
             auto.ROOT/'beads-photo-2.jpg']
    atomic_json(args.output/'summary.json',dict(request='R196',
        sources={str(p.relative_to(auto.ROOT)):auto.sha(p) for p in sources},preserved_inputs=protected,
        curated_sha256={p.name:auto.sha(p) for p in args.output.iterdir() if p.name!='summary.json'},
        selected_points=[dict(label=p['question_label'],xy=p['xy'],hypothesis_id=p['hypothesis_id'],
            response=p['response'],scale_matches=p['scale_matches'],coarse=p['coarse_diagnostic']) for p in selected],
        trusted_update='Exact assisted patch confirmed R198; P1/P2 excluded as D specular reflections R197',
        trusted_region_records=len(updated_facts['region_facts']),
        trusted_black_locator_records=len(updated_facts['black_reflection_point_facts']),fit_performed=False))
    print(json.dumps(dict(selected=[{k:p[k] for k in ['question_label','xy','response',
        'learned_color_fraction','scale_matches','coarse_diagnostic']} for p in selected],
        dark_patch_pixels=patch['region']['pixels'] if patch['region'] else None),indent=2))


if __name__=='__main__': main()

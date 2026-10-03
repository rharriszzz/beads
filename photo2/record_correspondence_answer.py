"""R211: bind the three same-bead points; clarify brightness evidence scope."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from check_placement import ROOT, sha
from practice_centerline_profiles import sample_path


def bind_answer(manifest, proposal, answer):
    if answer['question'] != manifest['question_id'] or answer['answer'] != 'V M and O are all in the same bead.':
        raise ValueError('Unexpected question or reply')
    if manifest['points'] != proposal['points'] or answer['points'] != manifest['points']:
        raise ValueError('Reviewed point coordinates changed')
    if not (answer['center_id'] == manifest['center_id'] == proposal['center_id'] and
            answer['center_number'] == manifest['center_number'] == proposal['center_number']):
        raise ValueError('Reviewed center identity changed')
    return dict(request='R211', question_id=manifest['question_id'], question_status='answered',
        confirmed_same_bead_points=manifest['points'],
        photo_reference=dict(center_id=manifest['center_id'], center_number=manifest['center_number']),
        safe_regions_confirmed=False, exact_centers_measured=False,
        predicted_visible_region_accepted=False, outward_geometry_measured=False,
        model_count_or_hand_confirmed=False, predicted_generator_index_confirmed=False,
        bead_index=None, limits='Point/body memberships only; original geometric model remains a hypothesis')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/review/r211')
    args = parser.parse_args()
    manifest_path = ROOT/'photo2/correspondence-question-r210.json'
    answer_path = ROOT/'photo2/correspondence-answer-r211.json'
    manifest = json.loads(manifest_path.read_text()); answer = json.loads(answer_path.read_text())
    if sha(manifest_path) != answer['question_manifest_sha256']:
        raise ValueError('Issued question manifest changed')
    for path, digest in manifest['source_sha256'].items():
        if sha(ROOT/path) != digest:
            raise ValueError('Reviewed photo, image, proposal or inventory changed: '+path)
    proposal = json.loads((ROOT/'photo2/review/r210/question-proposal.json').read_text())
    facts = bind_answer(manifest, proposal, answer)
    image = np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'), float)/255
    points = manifest['points']; labels = list(points)
    colors, hsv = sample_path(image, np.array([points[k] for k in labels]))
    facts['appearance_at_confirmed_points'] = {
        k: dict(rgb_encoded_0_1=colors[i].tolist(), hue_degrees=float(hsv[i, 0]*360),
                saturation=float(hsv[i, 1]), value=float(hsv[i, 2])) for i, k in enumerate(labels)}
    start = np.asarray(points['V']); end = np.asarray(points['O'])
    length = float(np.linalg.norm(end-start)); samples = int(np.ceil(length))+1
    xy = np.linspace(start, end, samples); _, route_hsv = sample_path(image, xy)
    vmin = float(route_hsv[:, 2].min()); lower_endpoint = float(min(route_hsv[0, 2], route_hsv[-1, 2]))
    facts['assisted_same_bead_endpoint_diagnostic'] = dict(
        start='V', end='O', path_length_pixels=length, sample_count=samples,
        coordinates=xy.tolist(), hsv=route_hsv.tolist(),
        outward_endpoint_darker_fraction=float(1-route_hsv[-1, 2]/route_hsv[0, 2]),
        minimum_value=vmin, dip_below_lower_endpoint_fraction=float(1-vmin/lower_endpoint),
        path_pixels_confirmed=False,
        interpretation='Confirmed endpoints on one bead have different brightness; no bead boundary or distance to its edge follows from darkness',
        sampling='Unsmoothed bilinear encoded RGB then HSV; native pixels, x right/y down; no fixed hue ranges')
    facts['code_role_audit'] = dict(
        V_and_O_placement_uses_photo_brightness=False,
        V_definition='Mean visible-owned model pixels after all occlusion',
        O_definition='Model minor-outward surface point',
        positive_interior_selection_uses_local_appearance=True,
        dark_troughs_used_as_certified_photo_seams=False,
        reliability='Conservative positive patches are the required evidence; complete photo boundaries have not been established',
        known_counterexample='photo2/review/r208/adverse-trough.json: persistent trough inside a single known body',
        next_task='Limited phase/origin registration using positive patch pixels and saved centers; no dark-edge/gap classification prerequisite')
    facts['current_scope'] = json.loads((ROOT/'photo2/positive-patch-scope-r212.json').read_text())
    facts['evidence_priority'] = json.loads((ROOT/'photo2/easy-evidence-priority-r213.json').read_text())
    sources = list(manifest['source_sha256'])+[
        'photo2/correspondence-question-r210.json', 'photo2/correspondence-answer-r211.json',
        'photo2/record_correspondence_answer.py', 'photo2/test_correspondence_answer.py',
        'photo2/practice_centerline_profiles.py', 'photo2/visible_correspondence.py',
        'photo2/review_visible_correspondence.py', 'photo2/bead_profile_cues.py',
        'photo2/review/r208/adverse-trough.json', 'photo2/positive-patch-scope-r212.json',
        'photo2/easy-evidence-priority-r213.json']
    facts['source_sha256'] = {p: sha(ROOT/p) for p in sources}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'confirmed-point-facts.json').write_text(json.dumps(facts, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(same_bead_points=labels, question_status='answered',
        endpoint_darkening_fraction=facts['assisted_same_bead_endpoint_diagnostic']['outward_endpoint_darker_fraction'],
        dip_below_lower_endpoint_fraction=facts['assisted_same_bead_endpoint_diagnostic']['dip_below_lower_endpoint_fraction'])))


if __name__ == '__main__':
    main()

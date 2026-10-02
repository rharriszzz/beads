"""Exact R204/R205 point facts and the supported 1D transition diagnostic."""
import json
from pathlib import Path
import numpy as np
import auto_label_beads as auto
from label_beads import atomic_json


def interpret(manifest, report, answers):
    right = next(s for s in report['sections'] if s['name']=='right')
    by_label = {p['label']: p for p in right['question_points']}
    expected = {'Q203.1': ('Two different yellow beads', ['S', 'Q']),
                'Q203.2': ('Yes', ['R'])}
    for key, (answer, labels) in expected.items():
        points = [by_label[label] for label in labels]
        if answers['answers'][key]['answer'] != answer or answers['answers'][key]['points'] != points:
            raise ValueError('Answer differs from the pictured points or supplied reply')
        if manifest['questions'][key]['points'] != points:
            raise ValueError('Question points differ from the reviewed report')
    a, b = by_label['S']['distance_pixels'], by_label['Q']['distance_pixels']
    hsv = np.array(right['hsv'])[a+140:b+141]
    coordinates = np.array(right['coordinates'])[a+140:b+141]
    k = int(np.argmin(hsv[:, 2])); reference = min(hsv[0, 2], hsv[-1, 2])
    return dict(requests=['R204','R205'],
        yellow_distinct_points=[by_label['S'],by_label['Q']],
        confirmed_black_reflection_point=by_label['R'], black_active_for_fitting=False,
        exact_regions_confirmed=False, exact_centers_measured=False, adjacency_inferred=False,
        transition=dict(route='Existing cyan spline from S0 through Q+20; bilinear encoded RGB then HSV',
            sample_count=len(hsv), path_length_pixels=b-a,
            minimum_value=float(hsv[k, 2]), minimum_value_distance_pixels=a+k,
            minimum_value_xy=coordinates[k].tolist(),
            minimum_value_over_lower_endpoint=float(hsv[k, 2]/reference),
            endpoint_hue_change_degrees=float((hsv[-1, 0]*360-hsv[0, 0]*360+180)%360-180),
            endpoint_hue_degrees=(hsv[[0, -1], 0]*360).tolist(),
            endpoint_saturation=hsv[[0,-1], 1].tolist(), endpoint_value=hsv[[0,-1], 2].tolist(),
            interpretation='Confirmed two yellow bodies despite shallow V dip; hue variation supplies complementary evidence',
            boundary_status='V minimum is a diagnostic candidate; maker supplied distinct identities, not exact seam pixels'),
        reflection=dict(point=by_label['R'],
            interpretation='Maker-confirmed black reflection has high V/low S; hue does not imply a colored bead',
            locator_role='Reviewed feature point, not an optical centroid, bead center or outward anchor'),
        limits=['No numeric image-wide seam rule or color box adopted from this one confirmed example.',
            'Other body aliases/global string indices unknown; old spline and manual references remain diagnostic only.'])


def main():
    root = auto.ROOT
    manifest_path = root/'photo2/profile-questions-r203.json'
    answer_path = root/'photo2/profile-answers-r204-r205.json'
    manifest = json.loads(manifest_path.read_text()); answers = json.loads(answer_path.read_text())
    if auto.sha(manifest_path) != answers['question_manifest_sha256']:
        raise ValueError('Reviewed question manifest changed')
    for key, digest in [('report', 'report_sha256'), ('supporting_image', 'supporting_image_sha256')]:
        if answers[key] != manifest[key] or answers[digest] != manifest[digest] or auto.sha(root/answers[key]) != answers[digest]:
            raise ValueError('Reviewed report/image changed')
    report = json.loads((root/answers['report']).read_text())
    result = interpret(manifest, report, answers)
    result.update(sources={p: auto.sha(root/p) for p in [
        'photo2/profile-questions-r203.json', 'photo2/profile-answers-r204-r205.json',
        'photo2/review/r203/report.json', 'photo2/review/r203/right.png', 'photo2/record_profile_answers.py']})
    atomic_json(root/'photo2/review/r203/confirmed-profile-facts.json', result)
    print(json.dumps(result['transition']))


if __name__ == '__main__':
    main()

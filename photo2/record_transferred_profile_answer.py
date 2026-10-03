"""Seal R209's yellow-body distinction and measure the exact reviewed path."""
import json
import numpy as np
from PIL import Image, ImageOps
import auto_label_beads as auto
from label_beads import atomic_json
from practice_centerline_profiles import sample_path


def bind_answer(manifest,proposal,answer):
    question=manifest['questions']['Q208.1']
    if answer['question']!='Q208.1' or answer['answer']!='Two different yellow beads':
        raise ValueError('Unsupported question or reply')
    if question['points']!=proposal['points'] or answer['points']!=question['points']:
        raise ValueError('Reply must bind to the exact reviewed points')
    if question['observation_id']!=proposal['observation_id']:
        raise ValueError('Reference identity changed')
    return dict(request='R209',confirmed_distinct_yellow_points=question['points'],
        safe_regions_confirmed=False,exact_centers_measured=False,adjacency_inferred=False,
        reference_origin_alias_confirmed=False,
        limits='Point/body distinction only; original interior reference and new points remain distinct evidence objects')


def main():
    root=auto.ROOT; manifest_path=root/'photo2/profile-transfer-question-r208.json'
    answer_path=root/'photo2/profile-transfer-answer-r209.json'
    manifest=json.loads(manifest_path.read_text()); answer=json.loads(answer_path.read_text())
    if auto.sha(manifest_path)!=answer['question_manifest_sha256']:
        raise ValueError('Reviewed question manifest changed')
    for path,digest in [('source_photo','source_photo_sha256'),('report','report_sha256'),
                        ('supporting_image','supporting_image_sha256'),('inventory','inventory_sha256')]:
        if auto.sha(root/manifest[path])!=manifest[digest]:
            raise ValueError('Reviewed photo, report, image or inventory changed')
    proposal=json.loads((root/manifest['report']).read_text())
    result=bind_answer(manifest,proposal,answer)
    a,b=answer['points']; xy=np.linspace(a['xy'],b['xy'],b['distance_pixels']-a['distance_pixels']+1)
    image=ImageOps.exif_transpose(Image.open(root/manifest['source_photo'])).convert('RGB')
    _,hsv=sample_path(np.asarray(image,float)/255,xy)
    np.testing.assert_allclose(hsv[[0,-1]],[a['hsv'],b['hsv']],atol=1e-12,rtol=0)
    k=int(np.argmin(hsv[:,2])); lower=min(hsv[0,2],hsv[-1,2])
    result['transition']=dict(sample_count=len(xy),path_length_pixels=float(np.linalg.norm(xy[-1]-xy[0])),
        minimum_value=float(hsv[k,2]),minimum_value_distance_pixels=a['distance_pixels']+k,
        minimum_value_xy=xy[k].tolist(),value_dip_fraction=float(1-hsv[k,2]/lower),
        endpoint_hue_change_degrees=float((hsv[-1,0]*360-hsv[0,0]*360+180)%360-180),
        endpoint_hue_degrees=(hsv[[0,-1],0]*360).tolist(),
        proposed_hue_event=proposal['event'],
        seam_status='Minimum V and weighted hue event are measured cues, not maker-confirmed seam pixels')
    sources=['photo2/profile-transfer-question-r208.json','photo2/profile-transfer-answer-r209.json',
        manifest['source_photo'],manifest['report'],manifest['supporting_image'],manifest['inventory'],
        'photo2/record_transferred_profile_answer.py','photo2/practice_centerline_profiles.py']
    result['sources']={p:auto.sha(root/p) for p in sources}
    atomic_json(root/'photo2/review/r208/confirmed-transfer-facts.json',result)
    print(json.dumps(result['transition']))


if __name__=='__main__': main()

"""R215 controlled specular evidence from the existing source scene, phong off.

This is a rendered validation pair, never a source of photo masks or positions.
"""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-segmentation-mpl')
import numpy as np
from PIL import Image
from matplotlib.colors import rgb_to_hsv
import auto_label_beads as auto
from check_placement import run_pov
from segment_colored_beads import appearance_context, reflection_regions, resize_mask


def main():
    name='hand+1-palette0-shift0'
    original=auto.ROOT/'photo2/output/r167/calibration'/name
    out=auto.ROOT/'photo2/output/r215/specular-control'; out.mkdir(parents=True,exist_ok=True)
    source=original.with_suffix('.pov').read_text()
    assert source.count('phong 1.4')==3
    scene=out/'diffuse-only.pov'; scene.write_text(source.replace('phong 1.4','phong 0'))
    png,command=run_pov(scene,800,800)
    appearance=np.asarray(Image.open(original.with_suffix('.png')).convert('RGB'),np.float32)/255
    diffuse=np.asarray(Image.open(png).convert('RGB'),np.float32)/255
    context=appearance_context((appearance*255).astype(np.uint8)); diameter=context['diameter']/np.sqrt(np.prod(context['scale']))
    band=resize_mask(context['band'],appearance.shape[:2])
    border=np.zeros(band.shape,bool); border[:20]=True; border[-20:]=True; border[:,:20]=True; border[:,-20:]=True
    masks,rows,_=reflection_regions(rgb_to_hsv(appearance),band,diameter,border,context['parameters']['reflection_response_floor'])
    no_masks,no_rows,_=reflection_regions(rgb_to_hsv(diffuse),band,diameter,border,context['parameters']['reflection_response_floor'])
    # A clipped blue/red channel can have unchanged maximum V while other
    # channels brighten strongly. Measure the largest added channel instead.
    contribution=np.max(appearance-diffuse,axis=2)
    evidence=contribution>.04
    details=[]
    for row in rows:
        pixels=masks==row['reflection_number']; x,y=np.rint(row['xy']).astype(int)
        details.append(dict(reflection_number=row['reflection_number'],
            fraction_with_phong_difference_over_004=float(evidence[pixels].mean()),
            centroid_phong_difference=float(contribution[y,x])))
    result=dict(appearance_sha256=auto.sha(original.with_suffix('.png')),source_scene_sha256=auto.sha(original.with_suffix('.pov')),
        diffuse_scene_sha256=auto.sha(scene),diffuse_png_sha256=auto.sha(png),command=command,
        specular_term='Only phong 1.4 changed to phong 0 in the three materials',
        difference_measure='max over RGB channels of appearance minus diffuse-only, encoded 0–1 PNG values',
        detected_reflections=len(rows),diffuse_only_false_reflections=len(no_rows),
        mask_pixels=int((masks>0).sum()),mask_pixels_with_specular_evidence_fraction=float(evidence[masks>0].mean()),
        reflection_centroids_with_specular_evidence=sum(r['centroid_phong_difference']>.04 for r in details),details=details,
        limitation='One controlled scene; encoded image differences support specular origin here, not physical reflection truth on the photo')
    (out/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['details','command']}),flush=True)


if __name__=='__main__':
    main()

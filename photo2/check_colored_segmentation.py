"""Known-ID evaluator; all image-only extraction completes before IDs are read."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from segment_colored_beads import segment
from auto_label_beads import ROOT, sha


def evaluate(report, masks, labels, nbeads=312):
    valid = (labels >= 0) & (labels < nbeads)
    colored = valid & (labels % 3 != 2)
    selected = masks['retained'] > 0
    area = np.bincount(labels[valid],minlength=nbeads)
    minimum = max(20.,float(np.quantile(area[area>0],.5)*.35))
    eligible = [i for i in range(nbeads) if i % 3 != 2 and area[i] >= minimum]
    bodies = []
    for ident in eligible:
        ids, counts = np.unique(masks['retained'][labels==ident],return_counts=True)
        inside = counts[ids>0]
        best = int(inside.max()) if len(inside) else 0
        recall = float(inside.sum()/area[ident])
        bodies.append(dict(known_body=ident,visible_pixels=int(area[ident]),
            retained_visible_fraction=recall,best_single_region_recall=best/float(area[ident]),
            retained_regions=int(np.sum(ids>0))))
    regions = []
    for row in report['records']:
        owners, counts = np.unique(labels[masks['retained']==row['region_number']],return_counts=True)
        top = int(counts.argmax()); owner = int(owners[top]); purity = float(counts[top]/counts.sum())
        regions.append(dict(region_number=row['region_number'],dominant_known_body=owner,purity=purity,
            dominant_is_colored=bool(0<=owner<nbeads and owner%3!=2),
            pixels=int(counts.sum()),owners=[dict(body=int(i),pixels=int(k)) for i,k in zip(owners,counts)]))
    reflection_owners = []
    for row in report['reflections']:
        x,y = np.rint(row['xy']).astype(int); owner=int(labels[y,x])
        reflection_owners.append(dict(reflection_number=row['reflection_number'],known_body=owner,
            on_body=bool(0<=owner<nbeads),status='Owner truth only; ID masks do not establish specular physics'))
    return dict(eligible_visible_area_threshold=minimum,eligible_colored_bodies=len(eligible),
        eligible_recall_quantiles=np.quantile([r['retained_visible_fraction'] for r in bodies],[0,.1,.5,.9,1]).tolist(),
        eligible_bodies_in_70_to_90_percent=sum(.70<=r['retained_visible_fraction']<=.90 for r in bodies),
        eligible_bodies_at_least_70_percent=sum(r['retained_visible_fraction']>=.70 for r in bodies),
        eligible_missed_bodies=[r['known_body'] for r in bodies if r['retained_visible_fraction']==0],
        all_colored_visible_pixels=int(colored.sum()),retained_colored_pixels=int((selected&colored).sum()),
        all_colored_pixel_recall=float((selected&colored).sum()/colored.sum()),
        retained_color_precision=float((selected&colored).sum()/max(1,selected.sum())),
        retained_background_pixels=int((selected&~valid).sum()),retained_black_pixels=int((selected&valid&~colored).sum()),
        high_purity_colored_regions=sum(r['purity']>=.98 and r['dominant_is_colored'] for r in regions),
        total_regions=len(regions),reflections_on_body=sum(r['on_body'] for r in reflection_owners),
        total_reflections=len(reflection_owners),bodies=bodies,regions=regions,reflections=reflection_owners,
        limitation='Known synthetic pixel ownership; no photo recall, distinct-body completeness or true reflection-mask certification')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r215/calibration')
    parser.add_argument('--extra-fixture',action='append',default=[],help='Additional existing appearance/ID fixture, e.g. hand+1-palette1-shift3')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    fixtures=ROOT/'photo2/output/r167/calibration'; pending=[]
    for name in ['hand+1-palette0-shift0','hand-1-palette0-shift0','hand+1-palette1-shift2']+args.extra_fixture:
        path=fixtures/(name+'.png'); image=np.asarray(Image.open(path).convert('RGB'))
        report,masks=segment(image,sha(path)); pending.append((name,path,report,masks))
        (args.output/(name+'-regions.json')).write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        np.savez_compressed(args.output/(name+'-masks.npz'),**masks)
        print(json.dumps(dict(fixture=name,extraction=report['counts'])),flush=True)
    results=[]
    # Every mask is frozen before any owner truth is loaded.
    for name,path,report,masks in pending:
        ids=fixtures/(name+'-ids.png'); rgb=np.asarray(Image.open(ids).convert('RGB'),int)
        labels=rgb[...,0]+256*rgb[...,1]-1
        measured=evaluate(report,masks,labels)
        result=dict(fixture=name,appearance_sha256=sha(path),ids_sha256=sha(ids),result=measured)
        results.append(result)
        print(json.dumps(dict(fixture=name,**{k:v for k,v in measured.items() if k not in ['bodies','regions','reflections']})),flush=True)
    (args.output/'report.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    main()

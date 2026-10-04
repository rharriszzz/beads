"""Compare R218 diffuse-core methods with frozen R215 on known-ID scenes.

The image-only masks are finished before owner masks are read. Controls are
existing development/regression scenes, not independent generality proof.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from auto_label_beads import ROOT,sha
from segment_colored_beads import segment
from refine_colored_masks import refine
from check_colored_segmentation import evaluate

FIXTURES=['hand+1-palette0-shift0','hand-1-palette0-shift0',
          'hand+1-palette1-shift2','hand+1-palette1-shift3']


def ownership_measurements(report,arrays,labels):
    measured=evaluate(report,arrays,labels)
    pure={r['region_number']:r for r in measured['regions'] if r['purity']>=.98 and r['dominant_is_colored']}
    best={}
    for region in pure.values():
        owner=region['dominant_known_body']
        pixels=int(np.sum((arrays['retained']==region['region_number'])&(labels==owner)))
        best[owner]=max(best.get(owner,0),pixels)
    for body in measured['bodies']:
        body['best_pure_single_region_recall']=best.get(body['known_body'],0)/body['visible_pixels']
    measured['eligible_bodies_with_pure_single_region_70_to_90_percent']=sum(.70<=b['best_pure_single_region_recall']<=.90 for b in measured['bodies'])
    measured['eligible_bodies_with_pure_single_region_at_least_70_percent']=sum(b['best_pure_single_region_recall']>=.70 for b in measured['bodies'])
    measured['mixed_region_minority_pixels']=sum(r['pixels']-max(o['pixels'] for o in r['owners']) for r in measured['regions'])
    return measured


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r218/calibration')
    parser.add_argument('--prominence',type=float,default=.08)
    parser.add_argument('--hue-weight',type=float,default=0.)
    parser.add_argument('--no-neutral-support',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    fixtures=ROOT/'photo2/output/r167/calibration';pending=[]
    for name in FIXTURES:
        path=fixtures/(name+'.png');image=np.asarray(Image.open(path).convert('RGB'));base=segment(image,sha(path))
        for method in ['baseline','supplement','reseed']:
            report,arrays=base if method=='baseline' else refine(image,sha(path),method,args.prominence,base,args.hue_weight,not args.no_neutral_support)
            pathbase=args.output/(name+'-'+method)
            pathbase.with_suffix('.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
            np.savez_compressed(str(pathbase)+'.npz',**arrays)
            pending.append((name,method,report,arrays))
        print(json.dumps(dict(fixture=name,extraction_completed=True)),flush=True)
    results=[]
    for name,method,report,arrays in pending:
        ids=fixtures/(name+'-ids.png');rgb=np.asarray(Image.open(ids).convert('RGB'),int);labels=rgb[...,0]+256*rgb[...,1]-1
        measured=ownership_measurements(report,arrays,labels)
        row=dict(fixture=name,method=method,appearance_sha256=sha(fixtures/(name+'.png')),ids_sha256=sha(ids),
            result=measured,reflection_masks_match_baseline=np.array_equal(arrays['reflections'],pending[FIXTURES.index(name)*3][3]['reflections']))
        assert row['reflection_masks_match_baseline']
        results.append(row)
        print(json.dumps(dict(fixture=name,method=method,**{k:v for k,v in measured.items() if k not in ['bodies','regions','reflections']})),flush=True)
    (args.output/'report.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()

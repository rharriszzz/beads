"""R231: measure prototype seed ownership on four frozen development scenes.

All candidate lists are finished before known-owner images are opened. No photo
truth, unique-bead inventory or generalization is inferred from these controls.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

from auto_label_beads import ROOT, sha
from compare_seed_methods import methods, save

FIXTURES=['hand+1-palette0-shift0','hand-1-palette0-shift0',
          'hand+1-palette1-shift2','hand+1-palette1-shift3']


def main():
    cache=ROOT/'photo2/output/r218/calibration-final'
    fixtures=ROOT/'photo2/output/r167/calibration'
    out=ROOT/'photo2/output/r231/calibration';out.mkdir(parents=True,exist_ok=True)
    pending=[]
    for name in FIXTURES:
        photo=fixtures/(name+'.png');image=np.asarray(Image.open(photo).convert('RGB'))
        records_path=cache/(name+'-reseed.json');arrays_path=cache/(name+'-reseed.npz')
        report=json.loads(records_path.read_text());assert report['image_sha256']==sha(photo)
        with np.load(arrays_path) as z:arrays={k:z[k] for k in ['domain','family','reflections']}
        original=[dict(seed_xy=p['seed_xy'],appearance_mode=p['appearance_mode']) for p in report['records']]
        original += [dict(seed_xy=p['xy'],appearance_mode=p['appearance_mode']) for p in report['excluded_refinement']]
        original.sort(key=lambda p:(p['seed_xy'][1],p['seed_xy'][0],p['appearance_mode']))
        baseline=[dict(marker_xy=list(map(round,p['seed_xy'])),appearance_mode=p['appearance_mode'],seed_number=i)
                  for i,p in enumerate(original,1)]
        result,_,_,params=methods(image,report,arrays,baseline)
        save(out/(name+'-points.json'),result)
        pending.append(dict(name=name,rows=result,params=params,photo=photo,
            records_path=records_path,arrays_path=arrays_path))
        print(json.dumps({'fixture':name,'image_only_proposals_finished':True}),flush=True)
    measured=[]
    for scene in pending:
        name=scene['name'];ids=fixtures/(name+'-ids.png')
        rgb=np.asarray(Image.open(ids).convert('RGB'),int);labels=rgb[...,0]+256*rgb[...,1]-1
        valid=(labels>=0)&(labels<312);area=np.bincount(labels[valid],minlength=312)
        minimum=max(20.,np.quantile(area[area>0],.5)*.35)
        eligible=set(np.where((np.arange(312)%3!=2)&(area>=minimum))[0].tolist())
        rows=[]
        for key,points in scene['rows'].items():
            owners=[int(labels[p['xy'][1],p['xy'][0]]) for p in points]
            colored=[o for o in owners if 0<=o<312 and o%3!=2]
            visited=set(colored);counts={o:colored.count(o) for o in visited}
            result=dict(method=key,seeds=len(points),on_colored=len(colored),on_background=sum(not 0<=o<312 for o in owners),
                on_black=sum(0<=o<312 and o%3==2 for o in owners),eligible_colored_bodies=len(eligible),
                eligible_with_a_seed=len(eligible&visited),eligible_missed=sorted(eligible-visited),
                colored_bodies_with_multiple_seeds=sum(n>1 for n in counts.values()),
                all_visible_colored_bodies_seeded=len(visited))
            if key=='M3':
                radius=scene['params']['M3']['patch_radius'];pure=0;mixed=[]
                for p,owner in zip(points,owners):
                    x,y=p['xy'];r=int(np.ceil(radius));x0,x1=max(0,x-r),min(labels.shape[1],x+r+1)
                    y0,y1=max(0,y-r),min(labels.shape[0],y+r+1);yy,xx=np.mgrid[y0:y1,x0:x1]
                    disk=np.hypot(xx-x,yy-y)<=radius;values=labels[y0:y1,x0:x1][disk]
                    if 0<=owner<312 and owner%3!=2 and np.all(values==owner):pure+=1
                    else:mixed.append(dict(id=p['id'],xy=p['xy'],seed_owner=owner,
                        owners=[dict(body=int(o),pixels=int(n)) for o,n in zip(*np.unique(values,return_counts=True))]))
                result.update(pure_single_colored_body_disks=pure,mixed_or_noncolored_disks=mixed)
            rows.append(result)
        measured.append(dict(fixture=name,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in
            [scene['photo'],ids,scene['records_path'],scene['arrays_path']]},
            eligible_minimum_visible_area=float(minimum),results=rows))
    report=dict(request='R231',image_only_extraction_before_truth=True,fixtures=measured,
        limitations='Four previously used development scenes. Seed-point truth and small-disk purity only; no photo error rate, full-body masks or unique-bead guarantee.',
        source_sha256={p:sha(ROOT/p) for p in ['photo2/check_seed_methods.py','photo2/compare_seed_methods.py']})
    save(ROOT/'photo2/review/r231/calibration.json',report)
    print(json.dumps({r['fixture']:{p['method']:{k:p[k] for k in ['seeds','on_colored','on_background','on_black','eligible_with_a_seed','eligible_colored_bodies']}
        for p in r['results']} for r in measured},indent=2),flush=True)


if __name__=='__main__':main()

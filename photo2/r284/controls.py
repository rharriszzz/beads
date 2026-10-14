"""Original-cue ablation isolates changed support rules from expanded cue discovery."""
import numpy as np
from photo2.r282.common import ROOT,photo,read,save
from photo2.r282.phase1 import image_features
from photo2.r283.coverage import relationships
from .run import OUT,OLD,shift_rows,in_case,summary
from .methods import infer,cut_features,seed_color


def main():
    _,rgb,_=photo();features=image_features(rgb);baseline=read(OLD/'phase1.json.gz')['records'];curve=read(ROOT/'photo2/r282/results/centerline.json')['points'];results=[]
    for case in read(OUT/'cases.json'):
        origin=np.array(case['origin'])-48;f=cut_features(features,origin,[224,224]);old=shift_rows([r for r in baseline if np.all(np.array(r['seed'])>=origin+24) and np.all(np.array(r['seed'])<origin+200)],-origin)
        bank=[dict(id=r['record_id'],xy=list(map(int,np.rint(r['seed']))),color=seed_color(f,r['seed']),sources=[r['record_id']]) for r in old]
        out={}
        for m in 'ABC':
            rows,pairs=infer(f,bank,m);rows=shift_rows(rows,origin);relationships(rows,curve)
            # Use the same frozen near scale as main comparison.
            from scipy.spatial import cKDTree
            tree=cKDTree([r['measured_photo_location'] or r['seed'] for r in baseline])
            for r in rows:
                _,ix=tree.query(r['measured_photo_location'] or r['seed']);scale=baseline[ix]['centerline']['local_support_scale'];c=r['centerline'];c['local_support_scale']=scale;c['near']=c['unsigned_support_distance'] is not None and c['unsigned_support_distance']<=scale/2
            rows=[r for r in rows if in_case(r,case)];out[m]=dict(records=rows,summary=summary(rows,pairs))
        results.append(dict(case=case['name'],methods=out))
    save(OUT/'original-cue-control.json.gz',dict(cases=results,meaning='Exact original R283 seeds; no fresh cue bank or cue consolidation. This isolates support changes but deliberately retains old duplicate starts.'))
    print({m:sum(r['methods'][m]['summary']['high_near'] for r in results) for m in 'ABC'})

if __name__=='__main__':main()

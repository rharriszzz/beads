"""R135: check whether stronger boundary penalties remove the size tradeoff."""
import json
import numpy as np
from local_surface_fit import ROOT,polygons
from fit_boundary_arcs import support,losses,optimize
from refine_surface_constraints import cast,metrics
from check_local_perspective import render
from check_placement import sha


def main():
    out=ROOT/'photo2/output/r135';out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    arcs=json.loads((ROOT/'photo2/boundary-arcs-r135.json').read_text())['arcs']
    old=json.loads((ROOT/'photo2/review/r132/report.json').read_text());cases=[]
    for chart in ['H1','H2']:
        starts=[c for method in ['masked_regions','cores'] for c in old['cases'] if c['dataset']=='photo'
            and c['hypothesis']==chart and c['method']==method and c['ignore_radius_px']==6 and c['erosion_px']==3]
        f=starts[0];camera=f['camera'];p,stages=optimize(cfg,arcs,starts,camera,3,weight=3)
        stem=f'photo-{chart}-band3-weight3'
        labels,provenance=render(p,f['hand'],cfg['crop'],camera['focal_px'],np.array(camera['principal_xy']),out,stem)
        xy,shape,_=polygons(cfg);diff=int((cast(p,xy,f,camera).reshape(shape)!=labels).sum())
        assert diff/labels.size<.001,(stem,diff)
        xy,core,pairs,samples=support(cfg,arcs,3)
        training=losses(cast(p,xy,f,camera),f['mapping'],core,pairs,weight=3)
        case=dict(stem=stem,dataset='photo',hypothesis=chart,hand=f['hand'],mapping=f['mapping'],camera=camera,
            parameters=p.tolist(),start_parameters=[s['parameters'] for s in starts],halfwidth_px=3,bracket_weight=3,
            optimizer=stages,training=training,metrics=metrics(labels,dict(cfg,active_mapping=f['mapping']),[1364,278]),
            samples=samples,arcs=arcs,ray_pov_mismatches=diff,render_provenance=provenance)
        cases.append(case)
        report=dict(request_id='R135',cases=cases,source_sha256={n:sha(ROOT/n) for n in [
            'photo2/check_boundary_weight.py','photo2/fit_boundary_arcs.py','photo2/boundary-arcs-r135.json',
            'photo2/local-fit-r126.json','photo2/review/r132/report.json','photo2/review/r135/report.json']})
        (out/'weight-report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(stem=stem,training=training,metrics=case['metrics'])),flush=True)

if __name__=='__main__':main()

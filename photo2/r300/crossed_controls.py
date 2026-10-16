"""Two crossed, fixed-light controls to separate saved phase and roughness effects.

No search: reuse the two R299 endpoint geometries and frozen owners. Baseline and
selected diagonal cells are saved R299 outputs; only the two off-diagonal cells
are evaluated. All geometry/photographic checks refer to those identical geometries.
"""
from copy import deepcopy
import time
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,load_evidence,utc
from photo2.r299.experiment import observations,evaluate
from photo2.r299.forward import Surface,grids
from photo2.r298.geometry import contact
from .analyze import describe,seam_stats,BASE


def main():
    out=BASE/'results/crossed-controls.json'
    if out.exists():raise SystemExit('Frozen controls already exist')
    save(BASE/'evidence/crossed-protocol.json',dict(utc=utc(),reason='R299 parallel slope -9.66px/circuit versus R298 -6.76 while both phase and roughness changed. Isolate those two saved changes; no optimization or novel geometry.',cells=['R298 phase .69 / R299 roughness 13.25','R299 phase .54 / R298 roughness 10.25'],fixed='All 52 original observations and ownership-49; saved direction, all remaining geometry and source controls.',budget='Exactly two native evaluations; two full-chain certificate replays. Stop regardless of outcome.'))
    inputs,_=load_evidence();obs=observations();assign=read(ROOT/'photo2/r299/evidence/ownership-49.json')['assignments'];ledger=read(BASE/'results/ledger.json');analysis=read(BASE/'results/analysis.json');results=[];start=time.monotonic()
    for geometry_name,light_name in [('fixed-49-directional','joint-15'),('joint-15','fixed-49-directional')]:
        geom=read(ROOT/f'photo2/r299/results/native-{geometry_name}.json.gz');light=read(ROOT/f'photo2/r299/results/native-{light_name}.json.gz')['light'];s=Surface(geom['parameters'],inputs);cert=contact(s,exact=True);assert cert['certified'];data=grids(s,[a['owner'] for a in assign],1.)
        records,shadow=evaluate(s,data,light,obs,assign,1.,5,False);template={r['id']:r for r in ledger if r['model']==geometry_name};rows=[]
        for z in records:
            r=deepcopy(template[z['id']]);r['model']=geometry_name+'__light_'+light_name;r['exists']=z['exists'];r['missing_reason']=z['missing_reason']
            for kind in ['centroid','peak']:
                delta=np.array(z[kind+'_residual']) if z['exists'] else None;mt=r['model_tangent'];mn=[-mt[1],mt[0]]
                r[kind+'_xy']=delta.tolist() if delta is not None else None;r[kind+'_tn']=[float(delta@r['tangent']),float(delta@r['normal'])] if delta is not None else None;r[kind+'_model_tn']=[float(delta@mt),float(delta@mn)] if delta is not None else None;r[kind+'_diameters']=z[kind+'_normalized_error'];r[kind+'_index_equivalent']=float(delta@r['tangent']/r['pitch_px']) if delta is not None else None
            rows.append(r)
        result=dict(geometry=geometry_name,light_source=light_name,parameters=geom['parameters'],light=light,records=records,derived=rows,summary={kind:describe([r for r in rows if r['trusted']],kind) for kind in ['centroid','peak']},physical=cert,geometry_checks=analysis['models'][geometry_name]['geometry_metrics'],photographic_checks=analysis['models'][geometry_name]['photographic'],source_geometry_sha256=sha(ROOT/f'photo2/r299/results/native-{geometry_name}.json.gz'))
        results.append(result);print(geometry_name,light_name,result['summary']['centroid']['parallel']['slope'],flush=True)
    save(out,dict(controls=results,elapsed=time.monotonic()-start,decision='Diagnostic only; no chosen correction, no optimization.'))
if __name__=='__main__':main()

"""Frozen coherent local alias controls at exactly identical geometry."""
from copy import deepcopy
import numpy as np
from photo2.r318.optics import Engine,Chain
from photo2.r318.search import compact
from photo2.r315.model import refined_trace,subset
from photo2.r306.evidence import load
from .common import *

def main():
    epoch=read(OLD/'epoch2/epoch.json');p=read(OLD/'epoch2/best.json.gz')['parameters'];s=Chain(p,load()[0]);baseline=read(OLD/'epoch2/best.json.gz');out=[]
    for shift in [0,-7,-6,-1,1,6,7]:
        e=deepcopy(epoch)
        e['mapping']={k:v+shift if 51<=v<=66 else v for k,v in epoch['mapping'].items()}
        if len(set(e['mapping'].values()))!=len(e['mapping']):
            out.append(dict(shift=shift,feasible_map=False,reason='one-to-one collision at local interval boundary'));continue
        for o in e['observations']:o['index']=e['mapping'][o['id']]
        e['id']=f'R319-alias-{shift:+d}';e['binding']=digest(dict(observations=e['observations'],mapping=e['mapping'],method=e['method']))
        r=compact(Engine(e).evaluate(p));rows=[]
        for o in e['observations']:
            if not 51<=epoch['mapping'][o['id']]<=66:continue
            idx=e['mapping'][o['id']];j=int(np.flatnonzero(s.indices==idx)[0]);xy=np.array(o['component']['pixels']);tr=refined_trace(s,xy);iso=refined_trace(subset(s,[j]),xy)
            point=refined_trace(s,[o['point']]);owner=int(point['owner'][0]);rows.append(dict(id=o['id'],before=epoch['mapping'][o['id']],after=idx,visible_bright_support_fraction=float(np.mean(tr['owner']==j)),isolated_bright_support_fraction=float(np.mean(iso['owner']>=0)),owner_at_observed=int(s.indices[owner]) if owner>=0 else None,projected_center=s.pc[j].tolist(),neighbors=[dict(index=int(s.indices[j+d]),projected=s.pc[j+d].tolist()) for d in [-7,-6,-1,1,6,7]],error_px=next(z['error_px'] for z in r['rows'] if z['id']==o['id'])))
        out.append(dict(shift=shift,feasible_map=True,epoch=e,result=r,local_support=rows,geometry_hash=digest(p),geometric_gain=False,adjacency='All internal address differences within shifted 51..66 block preserved; interfaces to unchanged block are provisional and explicitly discontinuous. No identity inferred.'))
    # Sole 58->52 is shown only as a non-coherent diagnostic, never an accepted map.
    e=deepcopy(epoch);e['mapping']['auto-0063']=52
    for o in e['observations']:o['index']=e['mapping'][o['id']]
    e['id']='R319-single-alias-diagnostic';e['binding']=digest(dict(observations=e['observations'],mapping=e['mapping'],method=e['method']));r=compact(Engine(e).evaluate(p))
    out.append(dict(kind='single58to52-diagnostic-only',epoch=e,result=r,geometry_hash=digest(p),geometric_gain=False,coherent_hypothesis=False))
    save(OUT/'correspondence-controls.json.gz',dict(baseline_emax=baseline['emax_px'],controls=out,policy='Original epochs immutable. These are separately frozen diagnostic maps, all22 retained, identical geometry/light. No optical-nearest assignment or fit.'))
    # Audit the smaller-interval photographic catalog before any expansion claim.
    doc=read(OLD/'observations.json.gz');records=[]
    for o in doc['observations']:
        x,y=o['point']
        if not (1540<x<1705 and 200<y<345):continue
        tr=refined_trace(s,[o['point']]);j=int(tr['owner'][0]);idx=int(s.indices[j]) if j>=0 else None
        records.append(dict(id=o['id'],point=o['point'],eligible=o['eligible'],color=o['color'],owner_at_point=idx,exclusion_reasons=o['exclusion_reasons'],in_primary=o['id'] in epoch['mapping']))
    save(OUT/'small-catalog-audit.json',dict(records=records,policy='Broad photo neighborhood includes potential additional reflections; observed-point owner is a provisional diagnostic, never physical identity or automatic exclusion.'))
    print('CORRESPONDENCE',[(r.get('shift',r.get('kind')),r.get('result',{}).get('emax_px'),r.get('result',{}).get('missing')) for r in out],flush=True)
if __name__=='__main__':main()

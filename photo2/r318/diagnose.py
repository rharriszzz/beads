"""Worst reflection: camera occlusion, alternate lobes and fixed-light controls."""
import numpy as np
from photo2.r297.common import read,save,utc
from photo2.r315.model import subset,refined_trace
from photo2.r307.fast import grid
from photo2.r299.forward import shade
from photo2.r314.bright import components
from .detect import OUT,principal
from .optics import Engine,make_light

def main():
    for folder in [OUT,OUT/'epoch2']:
        if not (folder/'best.json.gz').exists():continue
        epoch=read(folder/'epoch.json');best=read(folder/'best.json.gz');result,s,a=Engine(epoch).evaluate(best['parameters'],True);rows=[]
        for r in sorted(result['rows'],key=lambda r:-r['error_px'])[:4]:
            j=int(np.flatnonzero(s.indices==r['index'])[0]);single=subset(s,[j]);xy=grid(s,1.,[j]);iso=single.camera(xy)
            # Camera-isolation diagnostic ONLY; illumination shadows still use
            # every body in the original complete scene.
            sh=shade(s,iso,make_light(s.p,s));h=principal(xy,sh['intensity']);visible=a['owner']==j
            cc=components(a['xy'][visible],a['intensity'][visible]);lobes=[]
            for c in cc:
                lobes.append(dict(point=c['weighted_centroid'],peak=c['peak'],relative_peak=c['peak_intensity']/max(z['peak_intensity'] for z in cc),error_px=float(np.linalg.norm(np.array(c['weighted_centroid'])-r['observed'])),pixels=len(c['pixels'])))
            at=refined_trace(s,np.array([r['observed'],h['point'] if h else r['observed']]))
            rows.append(dict(id=r['id'],index=r['index'],observed=r['observed'],visible_predicted=r['predicted'],visible_error_px=r['error_px'],isolated_camera_predicted=h['point'] if h else None,
                             isolated_camera_error_px=float(np.linalg.norm(np.array(h['point'])-r['observed'])) if h else None,
                             full_scene_owner_at_observed=int(s.indices[at['owner'][0]]) if at['owner'][0]>=0 else None,
                             full_scene_owner_at_isolated_lobe=int(s.indices[at['owner'][1]]) if at['owner'][1]>=0 else None,
                             visible_components=lobes,policy='Isolated-camera counterfactual is diagnostic, never a fitted prediction; complete-chain light shadows retained.'))
        save(folder/'worst-diagnosis.json',dict(utc=utc(),rows=rows))
        print(folder.name,[(r['id'],round(r['visible_error_px'],3),round(r['isolated_camera_error_px'],3) if r['isolated_camera_error_px'] is not None else None,r['full_scene_owner_at_observed']) for r in rows],flush=True)

if __name__=='__main__':main()

"""Short independent size/renderer/derivative preflight; no fitting selection."""
from copy import deepcopy
from pathlib import Path
from types import MethodType
import time,subprocess
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r307.fast import predict as old_predict
from photo2.r299.forward import Surface,shade,light_params
from .geometry import Chain
from .search import starts,move,sources
from .measure import Measures,reference_dimension,distances
from .render import predict

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.monotonic();data,m,obs=load();obj=Measures(data,m,obs);p=starts()[0]['parameters'];s=Chain(p,data)
    d=reference_dimension(m);save(out/'D.json',d);save(ROOT/'photo2/r309/evidence/D.json',d)
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');pt=np.array(d['reference']['point']);lo=(pt-65).astype(int);raw=im.crop((*lo,*(lo+130)));annot=raw.copy();dr=ImageDraw.Draw(annot);ep=np.array(d['reference']['endpoints'])-lo;dr.line(tuple(ep.ravel()),fill='cyan',width=1)
    page=Image.new('RGB',(780,420),'#13232c');page.paste(raw.resize((390,390)),(0,30));page.paste(annot.resize((390,390)),(390,30));ImageDraw.Draw(page).text((10,8),f"Original photo / fixed reference B14: D={d['D_px']:.3f}px; +/-6px, not true maximum",fill='white');page.save(out/'D-reference.png')
    old=Original(p,data);np.testing.assert_allclose(s.centers,old.centers,atol=1e-12);np.testing.assert_allclose(s.pc,old.pc,atol=1e-12)
    xy=obj.o.xy[::11];a=s.trace(xy);b=old.trace(xy);np.testing.assert_array_equal(a['owner'],b['owner']);np.testing.assert_array_equal(a['unknown'],b['unknown'])
    t=time.monotonic();base=obj.evaluate(s);base_seconds=time.monotonic()-t;save(out/'baseline.json.gz',base)
    prior,_=old_predict(s,1.,obj.o.obs);native,_=predict(s,1.,obj.o.obs);assert prior==native
    derivatives=[]
    for key in ['phase','tilt_y']:
        levels=[]
        for h in [1.,.5]:
            sides=[]
            for sign in [-1,1]:
                q=move(p,[key],[sign*h]);scene=Chain(q,data);cert=scene.certify(iterations=100,witnesses=False)
                r=obj.evaluate(scene,base['anchors']) if cert['certified'] else None;sides.append(r)
            if all(sides):
                levels.append(dict(h=h,smooth_derivative=(sides[1]['scores']['reflection']-sides[0]['scores']['reflection'])/(2*h),centroid_squared_derivative=(sides[1]['metrics']['reflection']['rms_px']**2-sides[0]['metrics']['reflection']['rms_px']**2)/(2*h),missing=[v['missing'] for v in sides],smooth_second_over_first=abs(sides[1]['scores']['reflection']+sides[0]['scores']['reflection']-2*base['scores']['reflection'])/max(1e-12,abs(sides[1]['scores']['reflection']-sides[0]['scores']['reflection']))))
        derivatives.append(dict(parameter=key,levels=levels))
    half=obj.evaluate(Chain(p,data),base['anchors'],step=.5)
    threshold=[]
    for fraction in [.25,.5,.75]:
        preds,meta=predict(s,1.,obj.o.obs,threshold=fraction);lookup={r['index']:r for r in preds};rows=[]
        for o in obj.o.obs:
            h=lookup.get(base['anchors']['reflections'][o['id']]);rows.append(dict(id=o['id'],point=o['point'],error_px=float(np.linalg.norm(np.array(h['point'])-o['point'])) if h else None,ambiguous=True))
        threshold.append(dict(fraction=fraction,metrics=distances(rows,d['D_px'])))
    q=deepcopy(p);q['light_inverse']=.001;finite=Chain(q,data);camera=finite.camera(obj.o.xy[::25]);light=light_params([p['light_az'],p['light_el'],p['roughness'],1000.],'finite',finite.centers.mean(0));fastshade=shade(finite,camera,light);finite.blocked=MethodType(Surface.blocked,finite);originalshade=shade(finite,camera,light);np.testing.assert_allclose(fastshade['intensity'],originalshade['intensity'],atol=1e-12)
    result=dict(passed=True,seconds=time.monotonic()-start,baseline_seconds=base_seconds,native_original_trace_rays=len(xy),native_centroids_exact=True,finite_shadow_original_intensity_max_delta=float(abs(fastshade['intensity']-originalshade['intensity']).max()),derivatives=derivatives,thresholds=threshold,sampling=dict(native=base['metrics']['reflection'],half=half['metrics']['reflection'],native_smooth_loss=base['scores']['reflection'],half_smooth_loss=half['scores']['reflection'],missing_native=base['missing'],missing_half=half['missing']),policy='Native1px fitting only. Smooth overlap is a positional fitting surrogate from unthresholded specular intensity, not centroid distance or calibrated brightness. Gradient proposals require measured local linearity; otherwise bounded coordinate brackets. All ray unknowns retain R308 correction.')
    save(out/'preflight.json',result);print('preflight passed',result['seconds'],flush=True)
    return result
if __name__=='__main__':run(ROOT/'photo2/r309/results/preflight')

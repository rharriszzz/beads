"""R278 recovery verbatim except removing the historical Band I/O dependency."""
import copy
import numpy as np
from scipy.spatial import cKDTree
from dataclasses import replace
from photo2.bead_detection.phase1_r278 import features,WholePhoto,Recovery,pixels,core,guard_ownership,reflection_region,Parameters,resolve
from .phase1 import FullDomain

def recover(native,srgb,old,base):
    band=FullDomain();e=Recovery(native,srgb,base,band,pale=True)
    known=cKDTree(np.array([[l['point']['x'],l['point']['y']] for l in old['locations']]).reshape(-1,2))
    owned=set().union(*(pixels(r) for r in old['beads']));proposals=[];decisions=[]
    fs=features(e)
    for i,f in enumerate(fs):
        f['id']=f'F278-{i:05d}';f['nearest_existing_distance']=float(known.query(f['anchor'])[0])
        if not f['stable'] or f['nearest_existing_distance']<8:
            f['status']='unstable scale response' if not f['stable'] else 'near existing photographic location';continue
        r=e.new_colored(f['anchor'],'R278',True)
        if r.get('color'):
            if r.get('region'):
                # Some new full-photo seeds fail before a bounded broad region
                # exists. Use the ordinary hue fallback then the guarded core.
                r=e.interior(r,layered=False)
                if not r.get('accepted'):r=core(e,r,owned)
                r=guard_ownership(r,old,e)
        elif f['method'].startswith('LoG'):
            r=dict(id='R278-K-%04d-%04d'%tuple(f['anchor']),anchor=f['anchor'],accepted=False,reasons=[],confidence={})
            reflection_region(r,native,srgb,e.hsv,e.nhsv,e.lum,e.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25),.70,list(e.palette.values()),True)
        r['r278_feature']=f;f['status']='native measurement attempted';proposals.append(r)
    beads,locations,decisions=resolve(proposals,old,WholePhoto())
    prior={l['id'] for l in old['locations']}
    for l in locations:
        if l['id'] not in prior:
            l['source']='R278 image-only multiscale/component recovery'
            b=next(b for b in beads if b['id']==l['id'])
            l['centerline_near']=band.qualifies([l['point']['x'],l['point']['y']],b['region'])
            l['physical_center']=None
            l['identity_warning']='Image-supported proposal; reflection/interior location is not the physical center.'
    return {**copy.deepcopy(old),'beads':beads,'locations':locations},fs,decisions


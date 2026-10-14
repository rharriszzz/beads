"""R278 dependency order and standalone replay/audit stages.

No old artifact is written. Expensive optimization is explicit (--stage fit).
"""
import argparse,json,gzip
import numpy as np
from .reconstruct_r278 import *
from .construction_r278 import base_model,contact_audit
from .contact_r278 import certificate

EXPORTED=('intended_N2080_h-1_p1.400_f0','intended_N2080_h+1_p1.400_f0',
          'intended_N2696_h+1_p1.300_f0_tilt-8','intended_N2696_h-1_p1.300_f0_tilt-8')

def screens():
    out=[]
    for convention in ('legacy','intended'):
        for pitch in (1.,1.05,1.1,1.15,1.2):
            s=Scene(base_model(2696,1,convention,pitch),DEFAULT);a=contact_audit(s,12,12)
            out.append(dict(convention=convention,radius=s.radius,pitch_factor=pitch,length=s.model.length,camera_scale=s.model.view.scale,penetrations=a['penetrating_pairs'],minimum=a['minimum_sdf_units'],families=a['families']))
    save(OUT/'packing-screen.json',out);out=[]
    for n in (1950,2300,2600,2696):
        for h in (-1,1):
            for pitch in (1.25,1.35,1.45):
                a=contact_audit(Scene(base_model(n,h,pitch_factor=pitch),DEFAULT),12,12)
                out.append(dict(n=n,h=h,pitch=pitch,penetrations=a['penetrating_pairs'],minimum=a['minimum_sdf_units']))
    save(OUT/'contact-screen.json',out);out=[]
    for pitch in (1.,1.1,1.2,1.3):
        for tilt in (-16,-8,0,8,16):
            b=base_model(2696,1,pitch_factor=pitch);b['hole_tilt_deg']=tilt;a=contact_audit(Scene(b,DEFAULT),16,16)
            out.append(dict(pitch=pitch,tilt=tilt,penetrations=a['penetrating_pairs'],minimum=a['minimum_sdf_units'],families=a['families']))
    save(OUT/'tilt-screen.json',out)

def audit():
    rows=observations();docs=[];certificates=[]
    for path in sorted(OUT.glob('intended_N*.json')):
        d=json.loads(path.read_text())
        if 'base' not in d:continue
        assert d['phase1_sha256']==sha(OUT/'phase1-inventory.json.gz')
        d.update(comparison(d['base'],np.array(d['p']),rows));save(path,d)
        docs.append({k:v for k,v in d.items() if k not in ('base','p')})
        c=certificate(Scene(d['base'],np.array(d['p'])));save(path.with_name(path.stem+'-separation.json'),c)
        certificates.append(dict(model=path.stem,**{k:v for k,v in c.items() if k!='witnesses'}))
    save(OUT/'comparison.json',docs);save(OUT/'separation-summary.json',certificates)
    controls=[]
    for name in ('mixed_joint','contact_joint'):
        doc=json.loads((ROOT/'photo2/review/r276'/(name+'.json')).read_text());b=doc['base'];b.update(bead_radius=RADIUS,rope_radius=b.get('rope_radius',4.),radius_convention='legacy')
        out=comparison(b,np.array(doc['p']),rows);out.update(name='R276-'+name,comparison='Frozen historical fit, identical Phase 1 evidence, different historical optimization budget');controls.append(out)
    save(OUT/'historical-comparison.json',controls)

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True,choices=['phase1','screens','fit','audit','export','light']);a=p.parse_args()
    if a.stage=='phase1':
        from .bead_detection.phase1_r278 import main as phase1
        phase1()
    elif a.stage=='screens':screens()
    elif a.stage=='fit':run_fit();run_extended()
    elif a.stage=='audit':audit()
    elif a.stage=='export':
        for name in EXPORTED:export(name)
    else:
        from .appearance_r278 import fit_light
        for name in EXPORTED:fit_light(name)

if __name__=='__main__':main()

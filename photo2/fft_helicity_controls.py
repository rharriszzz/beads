"""Matched POV-Ray known-helicity controls for R243; no photographic truth labels."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np
from photo2.fft_helicity import ROOT, OUT, BUNDLE, image_rgb, analyze, score, predicted, card, save, sha
# Existing source geometry helpers use historical script-local imports.
sys.path.insert(0,str(ROOT/'photo2'))
from bead_placement import Rope, Camera
from check_placement import source_parts, vec

SIZE=1200
N=1300

def setup(el,perspective):
    rope=Rope(N); span=2.7*(rope.chain_major+rope.chain_minor+rope.bead_radius)
    target=np.array([0.,0.,rope.chain_minor+2*rope.bead_radius]);dist=3*rope.chain_major
    eye=np.array([0.,-np.cos(np.radians(el)),np.sin(np.radians(el))])
    loc=target+dist*eye
    cam=Camera(tuple(loc),tuple(target),SIZE,SIZE,angle=float(np.degrees(2*np.arctan(span/(2*dist)))),sky=(0,0,1))
    def project(xyz):
        if perspective:return cam.project(xyz)[0]
        right,up,_=cam.basis();delta=np.array(xyz)-target
        return np.stack(((SIZE-1)/2+delta@right*SIZE/span,(SIZE-1)/2-delta@up*SIZE/span),axis=-1)
    if perspective:
        camera=f'camera {{location {vec(loc)} sky z right x up y angle {cam.angle} look_at {vec(target)} }}'
    else:
        camera=f'camera {{orthographic location {vec(loc)} sky z right x*{span} up y*{span} look_at {vec(target)} }}'
    return rope,project,camera,dict(elevation=el,perspective=perspective,span=span,location=loc.tolist(),target=target.tolist(),angle=cam.angle)

def render_all():
    folder=OUT/'controls';folder.mkdir(exist_ok=True,parents=True)
    parameters,placement,macro=source_parts();manifest=[]
    for el in (45,65,85):
      for perspective in (False,True):
       for appearance in ('uniform','mixed'):
        # 12 matched pairs, with two fixed phase/light conditions by appearance.
        for hand in (-1,1):
            key=f"e{el}-{'persp' if perspective else 'ortho'}-{appearance}-h{hand:+}"
            rope,project,camera,meta=setup(el,perspective)
            phase=0 if appearance=='uniform' else 23
            form=placement.replace('360*(bead_index/exact_beads_per_row + rclock*1.00)',f'{hand}*360*(bead_index/exact_beads_per_row + rclock*1.00)+{phase}')
            pigments=['<.7,.55,.25>'] if appearance=='uniform' else ['<.7,.025,.015>','<.9,.65,.015>','<.012,.012,.012>']
            rng=np.random.default_rng(243);palette=rng.integers(0,len(pigments),N)
            colors='\n'.join(f'#declare Pig{i}={p};' for i,p in enumerate(pigments))
            objects=[]
            for idx in range(N):
                objects.append(f'#declare bead_index={idx};\n'+form+f'object {{bead(material {{texture {{pigment {{rgb Pig{palette[idx]}}} finish {{ambient .08 diffuse .7 specular .9 roughness .025}}}}}},.8,.7,1) rotate <0,0,chain_angle> translate t1+t2+<0,0,chain_minor+2*bead_radius>}}')
            light='<-100,-140,220>' if appearance=='uniform' else '<100,-100,170>'
            scene=folder/(key+'.pov')
            scene.write_text('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'+camera+'\n'+f'#declare nbeads={N};\n#declare beads_per_row=6.5;\n#declare rclock=0;\n'+parameters+'#declare hole_size_per_bead_size=.14;\n'+macro+colors+f'\nlight_source {{{light} rgb 1.3}}\nplane {{z,0 pigment {{rgb <.5,.25,.4>}} finish {{ambient .12 diffuse .7}}}}\n'+'\n'.join(objects))
            png=scene.with_suffix('.png');cmd=['povray','+I'+str(scene),'+O'+str(png),f'+W{SIZE}',f'+H{SIZE}','+FN','-D','+A0.2','+AM2','+R2','+WT2','File_Gamma=2.2']
            if not png.exists():
                run=subprocess.run(cmd,capture_output=True,text=True);scene.with_suffix('.log').write_text(run.stdout+run.stderr);run.check_returncode()
            sites=[]
            for j,theta in enumerate(np.arange(0,360,45)+15):
                a=np.radians(theta);center=np.array([rope.chain_major*np.cos(a),rope.chain_major*np.sin(a),meta['target'][2]])
                tangent=np.array([-np.sin(a),np.cos(a),0]);normal=np.array([np.cos(a),np.sin(a),0]);xy=project(center)
                t=project(center+tangent)-xy;t/=np.linalg.norm(t)
                # Transverse extent approximation, camera-known calibration only.
                offset=np.linspace(0,2*np.pi,181)
                cross=normal[None,:]*np.sin(offset)[:,None]+np.array([0,0,1])[None,:]*np.cos(offset)[:,None]
                perp=np.array([-t[1],t[0]])
                radius=float(np.max(np.abs((project(center+(rope.chain_minor+rope.bead_radius)*cross)-xy)@perp)))
                diameter=float(2*rope.bead_radius*SIZE/meta['span'])
                if perspective:
                    _,depth=Camera(tuple(meta['location']),tuple(meta['target']),SIZE,SIZE,angle=meta['angle'],sky=(0,0,1)).project(center)
                    diameter*=np.linalg.norm(np.array(meta['location'])-meta['target'])/float(depth)
                sites.append(dict(id=f'{key}-S{j}',xy=xy.tolist(),tangent=t.tolist(),tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))),radius=radius,diameter=diameter,theta=float(theta),split='control'))
            manifest.append(dict(id=key,hand=hand,appearance=appearance,phase=phase,**meta,sites=sites,scene=str(scene.relative_to(ROOT)),image=str(png.relative_to(ROOT)),scene_sha256=sha(scene),image_sha256=sha(png),command=cmd))
            save(BUNDLE/'controls-manifest.json',manifest)
            print('Rendered',key,flush=True)
    return manifest

def evaluate():
    manifest=json.loads((BUNDLE/'controls-manifest.json').read_text());results=[]
    for case in manifest:
        rgb=image_rgb(ROOT/case['image'])
        for q in case['sites']:
            pair=[]
            for ch in ('V','Y'):
                rec,a=analyze(rgb,q,ch);pair.append((rec,a))
                # Known camera primary calibration. Image right may be -world x;
                # use the projected basis parity instead of pretending hand labels
                # are invariant under reflection. setup camera right/up/eye is proper.
                fits=[]
                for hand in (-1,1):
                    model=predicted(q['tangent_deg'],hand,case['elevation'],0,6.1109157489,0)
                    fits.append(dict(hand=hand,**score(rec['peaks'],model)))
                rec.update(truth=case['hand'],case=case['id'],appearance=case['appearance'],elevation=case['elevation'],perspective=case['perspective'],fits=fits)
                results.append(rec)
            if q==case['sites'][0] and case['elevation']==85 and not case['perspective']:
                card(q,pair,BUNDLE/(case['id']+'-control.png'))
    save(BUNDLE/'controls-results.json',results)
    print('Evaluated',len(results),'control channel-windows')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['render','evaluate']);a=p.parse_args()
    render_all() if a.stage=='render' else evaluate()

"""POV scene generator and membership-only oracle provider; never imported by inference."""
from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image
from .geometry import R,centers,frame,project,trace,contact

ROOT=Path(__file__).resolve().parents[2]

def vec(x):return '<'+','.join(f'{v:.10g}' for v in x)+'>'

def render(folder,name,p,colors,identity=False):
    indices=np.arange(-14,15);c=centers(indices,p['hand'],p['phase'],p['pitch']);r,d,e=frame(p['inclination'],p['roll']);W=320;H=224
    source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
    lines=['#version 3.7;','global_settings { assumed_gamma 1.0 }',f'#declare bead_radius={R:.16g};','#declare hole_size_per_bead_size=.14;',macro,
      f'camera {{ orthographic location {vec(e*80)} direction {vec(-e)} right {vec(r*W/p["scale"])} up {vec(-d*H/p["scale"])} }}',
      'background { color rgb <.47,.31,.43> }' if not identity else 'background {color rgb 0}']
    if not identity:
        light=np.array(p['light']);lines += [f'light_source {{ {vec(light*80)} color rgb 1.1 parallel point_at <0,0,0> }}', 'plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .18 diffuse .8}}']
    for j,cc in enumerate(c):
        col=colors[j] if not identity else [(j+1)/255,0,0]
        finish='ambient 1 diffuse 0' if identity else f'ambient .10 diffuse .75 specular {p["specular"]} roughness .025'
        # Macro's y hole axis becomes x; fixed major traversal for both hands.
        lines.append(f'object {{ bead(material {{texture {{pigment {{color rgb {vec(col)}}} finish {{{finish}}}}}}},.8,.7,1) rotate <0,0,-90> translate {vec(cc)} }}')
    pov=folder/(name+'.pov');pov.write_text('\n'.join(lines));png=folder/(name+'.png')
    command=['povray','+I'+str(pov.resolve()),'+O'+str(png.resolve()),'+W320','+H224','+FN','-D','-A','+WT2','File_Gamma=1.0']
    rrun=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (folder/(name+'.log')).write_bytes(rrun.stdout)
    if rrun.returncode:raise RuntimeError(rrun.stdout.decode()[-1500:])
    return np.asarray(Image.open(png).convert('RGB'))

def generate(folder):
    folder.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(279014);summary=[]
    for s in range(12):
        f=folder/f'scene-{s:02d}';f.mkdir(exist_ok=True)
        p=dict(hand=(-1,1)[s%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=(1.,1.10)[(s//2)%2],inclination=(-30.,0.,30.)[(s//4)%3],roll=float(rng.uniform(-30,30)),scale=12.,translation=[159.5,111.5],light=([-.5,-.7,1.],[.6,.4,1.])[(s//2)%2],specular=(.5,1.4)[(s//2)%2])
        palette=np.array([[.65,.025,.008],[.95,.65,.015],[.012,.012,.012]]);classes=rng.integers(0,3,29)
        if s in (4,5):classes[:]=1
        if s in (8,9):classes[:]=2
        colors=palette[classes];render(f,'photo',p,colors);identity=render(f,'identity',p,colors,True);owner=identity[:,:,0].astype(int)-1
        np.save(f/'truth-membership.npy',owner)
        truth=dict(parameters=p,indices=list(range(-14,15)),classes=classes.tolist(),contact=contact(p['pitch']),seed=279014,scene=s)
        (f/'truth.json').write_text(json.dumps(truth,indent=2))
        # Oracle exposes two largest visible regions, with anonymous image-derived IDs.
        regs=[];rgb=np.asarray(Image.open(f/'photo.png'));lum=rgb@np.array([.2126,.7152,.0722])/255
        for j in range(29):
            yy,xx=np.where(owner==j)
            if len(xx)<50:continue
            pix=np.c_[xx,yy];cen=pix.mean(0);pos=np.argmax(lum[yy,xx]);regs.append(dict(id=f'oracle-{len(regs)}',point=pix[pos].tolist(),centroid=cen.tolist(),physical_center=None,pixels=pix.tolist(),area=len(pix),uncertainty=2.,persistence=0.,color='unknown',quality=float(len(pix))))
        regs.sort(key=lambda o:-o['area']);a=regs[0];b=min(regs[1:],key=lambda o:np.linalg.norm(np.array(o['centroid'])-a['centroid']))
        # No physical index, hand, phase, camera or remaining mask leaves provider.
        (f/'oracle-pair.json').write_text(json.dumps([a,b]))
        # Independent Python/POV surface/camera agreement at native pixel centers.
        yy,xx=np.mgrid[0:224:3,0:320:3];xy=np.c_[xx.ravel(),yy.ravel()];pred,_,unknown=trace(p,xy);expected=owner[yy.ravel(),xx.ravel()];valid=~unknown
        expected=np.where(expected>=0,expected-14,-999)
        match=float(np.mean(pred[valid]==expected[valid]));summary.append(dict(scene=s,agreement=match,unknown=int(unknown.sum()),rays=len(xy)))
        print('rendered',s,'POV agreement',match,flush=True)
    (folder/'projection-check.json').write_text(json.dumps(summary,indent=2))

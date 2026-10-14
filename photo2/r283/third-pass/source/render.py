"""Literal POV appearance and independent local ownership raster checks."""
import subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from .common import OUT,ROOT,read,save,sha
from .local import INDICES,R,centers,frame,SHAPE,LOCAL
from photo2.r282.phase1 import image_features
from photo2.r282.phase2 import measure_color

def vec(a):return '<'+','.join(f'{v:.12g}' for v in a)+'>'

def render(folder,m,colors,identity=False):
    p=m['parameters'];h,w=SHAPE;r,d,e=frame(p['inclination'],p['roll']);cc=centers(INDICES,p['hand'],p['phase'],p['pitch'])
    target=((np.array([(w-1)/2,(h-1)/2])-p['translation'])/p['scale'])@np.array([r,d])
    source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
    lines=['#version 3.7;','global_settings {assumed_gamma 1.0}',f'#declare bead_radius={R:.16g};',
        '#declare hole_size_per_bead_size=.14;',macro,
        f'camera {{orthographic location {vec(target+e*100)} direction {vec(-e)} right {vec(r*w/p["scale"])} up {vec(-d*h/p["scale"])} }}',
        'background {color rgb 0}' if identity else 'background {color rgb <.47,.31,.43>}']
    if not identity:lines += [f'light_source {{{vec(np.array(m["light"]["direction"])*1000)} color rgb 1.1 parallel point_at <0,0,0>}}',
        'plane {z,-6 pigment {color rgb <.47,.31,.43>} finish {ambient .12 diffuse .8}}']
    palette={'red':[.65,.025,.008],'yellow':[.95,.65,.015],'black':[.012,.012,.012],'unknown':[.35,.35,.35]}
    for j,(c,k) in enumerate(zip(cc,INDICES)):
        col=[(j+1)/255,0,0] if identity else palette[colors[int(k)]]
        finish='ambient 1 diffuse 0' if identity else 'ambient .1 diffuse .75 specular 1.2 roughness .035'
        lines.append(f'object {{bead(material {{texture {{pigment {{color rgb {vec(col)}}} finish {{{finish}}}}}}},.8,.7,1) rotate <0,0,-90> translate {vec(c)}}}')
    name=m['id']+('-identity' if identity else '-pov');path=folder/(name+'.pov');path.write_text('\n'.join(lines))
    proc=subprocess.run(['povray','+I'+str(path.resolve()),'+O'+str((folder/(name+'.png')).resolve()),f'+W{w}',f'+H{h}','+FN','-D','-A','+WT2','File_Gamma=1.0'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (folder/(name+'.log')).write_bytes(proc.stdout);assert proc.returncode==0
    return np.asarray(Image.open(folder/(name+'.png')).convert('RGB'))

def main():
    folder=LOCAL;models=read(folder/'prediction-freeze.json')['models'];rgb=np.load(folder/'managed-rgb.npy');f=image_features(rgb);results=[]
    yy,xx=np.indices(SHAPE)
    for m in models:
        pred=np.load(folder/(m['id']+'-prediction.npz'));owner=pred['owner'];colors={};evidence=[]
        for k in INDICES:
            mask=ndi.binary_erosion(owner==k);p=np.c_[xx[mask],yy[mask]];color,weight,info,_=measure_color(rgb,f,p)
            colors[int(k)]=color;evidence.append(dict(index=int(k),color=color,engineering_weight=weight,photo_evidence=info))
        render(folder,m,colors);truth=render(folder,m,colors,True)[:,:,0].astype(int)
        truth=np.where(truth>0,truth-1+INDICES[0],-999)
        valid=~pred['unknown'];stable=valid.copy()
        for delta in ((0,1),(0,-1),(1,0),(-1,0)):
            stable&=owner==np.roll(owner,delta,axis=(0,1))
        results.append(dict(model=m['id'],resolved=int(valid.sum()),unknown=int((~valid).sum()),
            disagreements=int(((truth!=owner)&valid).sum()),stable_interior_disagreements=int(((truth!=owner)&stable).sum()),
            color_evidence=evidence,appearance='Colors sampled from the original photo after pose freeze; no pattern input. Shared train-yellow light, fixed material, no radiometric fit.'))
    save(folder/'pov-audit.json',dict(models=results,source_geometry_sha256=sha(ROOT/'beads.pov')))

if __name__=='__main__':main()

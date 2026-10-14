"""Benchmark provider. Evaluation truth never imported by detector."""
import argparse,subprocess
import numpy as np
from PIL import Image,ImageFilter
from .geometry import R,INDICES,centers,frame,templates,certify
from .common import OUT,ROOT,save

def vec(a):return '<'+','.join(f'{v:.12g}' for v in a)+'>'
def render(folder,p,classes,identity=False):
 W,H=320,224;r,d,e=frame(p['inclination'],p['roll']);c=centers(INDICES,p['hand'],p['phase'],p['pitch'])
 source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
 bg=vec(p['background'])
 lines=['#version 3.7;','global_settings {assumed_gamma 1.0}',f'#declare bead_radius={R:.16g};','#declare hole_size_per_bead_size=.14;',macro,f'camera {{orthographic location {vec(e*80)} direction {vec(-e)} right {vec(r*W/p["scale"])} up {vec(-d*H/p["scale"])} }}','background {color rgb 0}' if identity else f'background {{color rgb {bg}}}']
 if not identity:
  lines += [f'light_source {{{vec(np.array(p["light"])*80)} color rgb {p["light_power"]} parallel point_at <0,0,0>}}',f'plane {{z,-6 pigment {{color rgb {bg}}} finish {{ambient .18 diffuse .8}}}}']
 palette=np.array([[.65,.025,.008],[.95,.65,.015],[.012,.012,.012]])
 for j,cc in enumerate(c):
  color=[(j+1)/255,0,0] if identity else palette[classes[j]]
  finish='ambient 1 diffuse 0' if identity else f'ambient {p["ambient"]} diffuse .75 specular {p["specular"]} roughness {p["roughness"]}'
  lines.append(f'object {{bead(material {{texture {{pigment {{color rgb {vec(color)}}} finish {{{finish}}}}}}},.8,.7,1) rotate <0,0,-90> translate {vec(cc)}}}')
 name='identity' if identity else 'photo';path=folder/(name+'.pov');path.write_text('\n'.join(lines))
 command=['povray','+I'+str(path.resolve()),'+O'+str((folder/(name+'.png')).resolve()),'+W320','+H224','+FN','-D','-A','+WT2','File_Gamma=1.0']
 r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(folder/(name+'.log')).write_bytes(r.stdout)
 if r.returncode:raise RuntimeError(r.stdout.decode()[-1000:])
 return np.asarray(Image.open(folder/(name+'.png')).convert('RGB'))

def generate(split):
 seed={'dev':280101,'heldout':280202,'stress':280303}[split];rng=np.random.default_rng(seed)
 for s in range(2 if split=='stress' else 8):
  folder=OUT/split/f'scene-{s:02}';folder.mkdir(parents=True,exist_ok=True)
  p=dict(hand=(-1,1)[s%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=1. if split=='stress' else (1.12,1.20)[s//2%2],inclination=(-32.,-10.,18.,38.)[s//2],roll=float(rng.uniform(-35,35)),scale=(8.,10.)[s%2],translation=[159.5,111.5],light=([-.6,-.8,1.],[.8,.1,.7],[-.2,.9,.6],[.3,-1.,.3])[s//2],specular=(1.4,.15,0.,.6)[s//2],ambient=(.10,.06,.03,.13)[s//2],roughness=(.025,.08,.025,.06)[s//2],background=([.47,.31,.43],[.65,.63,.52],[.23,.29,.34],[.46,.38,.31])[s//2],light_power=1.1)
  classes=rng.integers(0,3,29);classes[10:14]=(0 if s%2 else 1)
  if s in (4,5):classes[8:21]=2
  cert=certify(p)
  if split!='stress' and not cert['certified']:raise AssertionError('Invalid positive control')
  render(folder,p,classes);ident=render(folder,p,classes,True);truth=ident[:,:,0].astype(np.int16)-1
  np.savez_compressed(folder/'truth.npz',owner=truth)
  pred,audit=templates(p)
  valid=~audit['unknown'];expected=np.where(truth>=0,truth-14,-999)
  agree=bool(np.array_equal(audit['owner'][valid],expected[valid]))
  if not agree:raise AssertionError('Independent POV/Python camera mismatch')
  save(folder/'geometry.json',dict(parameters=p,predictions=pred))
  # Different camera is a model input, independent of the POV ownership raster.
  camera_pred,_=templates({**p,'inclination':p['inclination']+15})
  phase_pred,_=templates({**p,'phase':p['phase']+.45})
  save(folder/'perturbed-geometry.json',dict(camera=camera_pred,phase=phase_pred))
  save(folder/'truth.json',dict(seed=seed,classes=classes.tolist(),indices=INDICES.tolist(),certificate=cert,projection_check=dict(resolved=int(valid.sum()),unknown=int((~valid).sum()),all_resolved_agree=agree),packing_valid=cert['certified']))
  print(split,s,'valid',cert['certified'],'gap',cert['minimum_gap_units'],flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('split',choices=['dev','heldout','stress']);generate(parser.parse_args().split)

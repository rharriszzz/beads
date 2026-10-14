"""Benchmark generation only: literal POV annuli, independent identities."""
import argparse,subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from .detector import boundary
from photo2.r280.synthetic import render
from photo2.r280.geometry import templates,certify
from photo2.r280.evaluate import truth_rows
from .common import OUT,save,read
from .geometry import counterfactual,serial,owner_map

def removed(folder,source,j):
 folder.mkdir(exist_ok=True)
 for name in ('photo','identity'):
  lines=(source/(name+'.pov')).read_text().splitlines();objects=[i for i,l in enumerate(lines) if l.startswith('object {bead(')];del lines[objects[j]]
  pov=folder/(name+'.pov');pov.write_text('\n'.join(lines));cmd=['povray','+I'+str(pov.resolve()),'+O'+str((folder/(name+'.png')).resolve()),'+W320','+H224','+FN','-D','-A','+WT2','File_Gamma=1.0'];r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(folder/(name+'.log')).write_bytes(r.stdout)
  if r.returncode:raise RuntimeError(r.stdout.decode()[-1000:])

def projection_audit(predicted,expected,unknown):
 valid=~unknown;bad=(predicted!=expected)&valid
 # POV CSG and implicit-ray termination can differ on isolated silhouette pixels.
 # Validate a bounded numerical raster tolerance; NEVER alter detector inputs
 # or ignore these pixels in detection/evaluation.
 near=ndi.binary_dilation(boundary(predicted)|boundary(expected),iterations=1)
 assert int(bad.sum())<=3 and not (bad&~near).any()
 return dict(resolved=int(valid.sum()),unknown=int(unknown.sum()),boundary_disagreements=int(bad.sum()),pixels=np.argwhere(bad).tolist())

def generate(split):
 if split=='heldout' and not (OUT/'freeze.json').exists():raise RuntimeError('Freeze first')
 seed=281101 if split=='dev' else 281202;rng=np.random.default_rng(seed);records=[]
 for s in range(12 if split=='dev' else 40):
  f=OUT/split/f'scene-{s:02}';f.mkdir(parents=True,exist_ok=True)
  p=dict(hand=(-1,1)[s%2],phase=float(rng.uniform(-np.pi,np.pi)),pitch=(1.12,1.20)[s//2%2],inclination=float(rng.uniform(-30,30)),roll=float(rng.uniform(-55,55)),scale=(8.,10.)[s%2],translation=[159.5,111.5],light=[float(rng.uniform(-.8,.8)),float(rng.uniform(-.7,.7)),1.],light_power=float(rng.uniform(.9,1.3)),specular=(.3,1.2,.7)[s%3],roughness=(.035,.06)[s%2],ambient=.12,background=([.47,.31,.43],[.65,.63,.52],[.23,.29,.34],[.46,.38,.31])[s%4])
  classes=rng.choice(3,29,p=[.4,.4,.2]);classes[11:14]=s%2
  if (f/'evaluation-targets.json').exists():
   eligible=read(f/'evaluation-targets.json')['targets'];records.append(dict(scene=s,targets=len(eligible),hand=p['hand']));continue
  certificate=certify(p);assert certificate['certified'];render(f,p,classes);identity=render(f,p,classes,True);owner=identity[:,:,0].astype(np.int16)-1;np.savez_compressed(f/'truth.npz',owner=owner)
  pred,audit=templates(p);valid=~audit['unknown'];expected=np.where(owner>=0,owner-14,-999);projection_check=projection_audit(audit['owner'],expected,audit['unknown'])
  save(f/'geometry.json',dict(parameters=p,predictions=pred));save(f/'truth.json',dict(seed=seed,scene=s,classes=classes.tolist(),certificate=certificate,projection_check=projection_check))
  _,tiers=truth_rows(f);eligible=[r for r in tiers if r['tier']=='easy' and abs(r['model_index'])<=10]
  # Geometry/visibility/illumination selection, before any detector measurement.
  eligible=sorted(eligible,key=lambda r:(-r['area'],r['model_index']))[:4]
  save(f/'evaluation-targets.json',dict(targets=eligible,available=len(eligible),unavailable_slots=4-len(eligible),all_tiers=tiers))
  for r in eligible:
   k=r['model_index'];absent=f/f'absent-{k:+03}';removed(absent,f,r['index']);hyp=counterfactual(p,k,(224,320),audit['owner'],audit['unknown'])
   np.savez_compressed(f/f'hyp-{k:+03}.npz',h1=hyp['h1'],h0=hyp['h0'],unknown=hyp['unknown']);save(f/f'hyp-{k:+03}.json',{a:b for a,b in hyp.items() if a not in ('h1','h0','unknown')})
   absent_owner=np.asarray(Image.open(absent/'identity.png'))[:,:,0].astype(int)-1;expected=np.where(absent_owner>=0,absent_owner-14,-999);valid=~hyp['unknown'];check=projection_audit(hyp['h0'],expected,hyp['unknown']);save(absent/'projection-audit.json',check)
  records.append(dict(scene=s,targets=len(eligible),hand=p['hand']));print(split,s,'easy',len(eligible),flush=True)
 save(OUT/(split+'-generation.json'),dict(seed=seed,scenes=records,targets=sum(r['targets'] for r in records)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('split',choices=['dev','heldout']);generate(p.parse_args().split)

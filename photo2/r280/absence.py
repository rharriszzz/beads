"""Post-freeze absence control: remove a visible easy body, retain prediction.
Selection uses evaluation truth only to define a negative benchmark scene; all
inference sees the newly rendered pixels and unchanged geometric hypotheses.
"""
import subprocess
import numpy as np
from PIL import Image
from .common import OUT,read,save
from .detector import infer

def main():
 rows=read(OUT/'heldout-evaluation.json.gz')['records'];selected=[]
 for s in sorted(set(r['scene'] for r in rows)):
  pool=[r for r in rows if r['scene']==s and r['method']=='C' and r['test']=='A1' and r['tier']=='easy']
  if pool:selected.append(pool[0])
 result=[]
 for row in selected:
  source=OUT/'heldout'/row['scene'];folder=OUT/'absence'/row['scene'];folder.mkdir(parents=True,exist_ok=True);j=int(row['id'].replace('model-',''))+14
  for name in ('photo','identity'):
   lines=(source/(name+'.pov')).read_text().splitlines();objects=[i for i,l in enumerate(lines) if l.startswith('object {bead(')];del lines[objects[j]];pov=folder/(name+'.pov');pov.write_text('\n'.join(lines))
   cmd=['povray','+I'+str(pov.resolve()),'+O'+str((folder/(name+'.png')).resolve()),'+W320','+H224','+FN','-D','-A','+WT2','File_Gamma=1.0'];r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(folder/(name+'.log')).write_bytes(r.stdout)
   if r.returncode:raise RuntimeError(r.stdout.decode()[-1000:])
  rgb=np.asarray(Image.open(folder/'photo.png').convert('RGB'));pred=read(source/'geometry.json')['predictions'];methods={m:infer(rgb,pred,m,read(OUT/'freeze.json')['thresholds']) for m in 'ABC'};save(folder/'inference.json.gz',dict(removed_model_id=row['id'],predictions=pred,methods=methods))
  result.append(dict(scene=row['scene'],removed=row['id'],methods={m:next(r for r in rs if r['id']==row['id']) for m,rs in methods.items()}))
 save(OUT/'absence-summary.json',result);print({m:sum(r['methods'][m]['status']=='strong' for r in result) for m in 'ABC'},'of',len(result))
if __name__=='__main__':main()

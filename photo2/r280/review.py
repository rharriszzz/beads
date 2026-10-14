"""Static review artifact, original pixels remain a separate immutable image."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from .common import OUT,read,save

def main():
 rows=read(OUT/'heldout-evaluation.json.gz')['records'];cases=[]
 for folder in sorted((OUT/'heldout').glob('scene-*')):
  data=read(folder/'A1-exact.json.gz');inv=read(folder/'phase1.json.gz')
  easy=[r for r in rows if r['scene']==folder.name and r['test']=='A1' and r['method']=='C' and r['tier']=='easy']
  chosen=next((r for r in easy if r['status']=='strong'),easy[0] if easy else None)
  phase1=[dict(id=l['id'],point=[l['point']['x'],l['point']['y']]) for l in inv['locations']]
  cases.append(dict(title='Held-out '+folder.name+' / exact geometry',image=str((folder/'photo.png').relative_to(OUT)),predictions=data['predictions'],results=data['methods']['C'],phase1=phase1,selected=chosen['id'] if chosen else data['predictions'][0]['id'],evaluation=[r for r in rows if r['scene']==folder.name and r['test']=='A1' and r['method']=='C']))
 for kind,label in [('unanchored-neighbor','False confirmation without identity context'),('duplicate','Ambiguous duplicate owners'),('phase','Wrong-phase alternatives'),('wrong-scale','Wrong-scale alternatives')]:
  pool=[r for r in rows if r['test']=='A4' and r['kind']==kind and r['method']=='C' and r['false'] and r['tier']=='easy']
  selected=next((r for r in pool if r['status']=='strong'),next((r for r in pool if r['status']=='ambiguous'),pool[0]))
  folder=OUT/'heldout'/selected['scene'];data=read(folder/('A4-'+kind+'.json.gz'))
  cases.append(dict(title=label,image=str((folder/'photo.png').relative_to(OUT)),predictions=data['predictions'],results=data['methods']['C'],phase1=[],selected=selected['id'],evaluation=[selected]))
 for folder in sorted((OUT/'real').glob('region-*')):
  for path in folder.glob('model-*.json.gz'):
   data=read(path);p=data['predictions'];r=data['methods']['C'];family=[x for x in r if int(x['id'].replace('model-','')) in data['target_families']]
   selected=next((x['id'] for x in family if x['status']=='strong'),family[0]['id'])
   cases.append(dict(title='Actual photo '+folder.name+' / hand '+str(data['parameters']['hand'])+' / conditional model',image=str((folder/'photo.png').relative_to(OUT)),predictions=p,results=r,phase1=data['phase1'],selected=selected,evaluation=[],fit_score=data['fit']['score']))
 for item in read(OUT/'absence-summary.json'):
  folder=OUT/'absence'/item['scene'];data=read(folder/'inference.json.gz')
  cases.append(dict(title='Removed easy bead / '+item['scene']+' / absence control',image=str((folder/'photo.png').relative_to(OUT)),predictions=data['predictions'],results=data['methods']['C'],phase1=[],selected=item['removed'],evaluation=[dict(id=item['removed'],tier='easy absence control',correct=False,wrong_owner=item['methods']['C']['status']=='strong',intended_purity=0.,location_error_diameter=None)]))
 (OUT/'viewer-data.js').write_text('window.REVIEW='+json.dumps(cases,separators=(',',':'))+';\n')
 # Curated static panels: raw vs all selected model support, never substitute render.
 panels=[];captions=[]
 for i,c in enumerate(cases):
  im=Image.open(OUT/c['image']).convert('RGB');ann=im.copy();draw=ImageDraw.Draw(ann);pred=next(p for p in c['predictions'] if p['id']==c['selected']);r=next(r for r in c['results'] if r['id']==c['selected'])
  for y,x,z in pred['visible']:draw.line((x,y,z,y),fill=(255,160,40),width=1)
  for y,x,z in r['support']:draw.line((x,y,z,y),fill=(60,230,120),width=1)
  if r['location']:
   x,y=r['location'];draw.ellipse((x-2,y-2,x+2,y+2),fill='white')
  pair=Image.new('RGB',(im.width*2,im.height+35),'white');pair.paste(im,(0,35));pair.paste(ann,(im.width,35));d=ImageDraw.Draw(pair);d.text((5,4),c['title'][:90],fill='black');d.text((5,19),c['selected']+' / '+r['status']+' / raw left; model orange; measured green',fill='black')
  path=OUT/'examples'/f'case-{i:02}.png';path.parent.mkdir(exist_ok=True);pair.save(path);captions.append(dict(file=str(path.relative_to(OUT)),title=c['title'],id=c['selected'],status=r['status']))
 save(OUT/'examples/index.json',captions)
 print('review cases',len(cases))
if __name__=='__main__':main()

"""Maker-only selection by geometry/provenance, before any pixel brightness."""
from pathlib import Path
import json,gzip,hashlib,datetime
import numpy as np
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
NEW=['E5-2272-1815','NEW-2156-1135','MAT25-K-2142-2497','K-1663-3006','NEW-1247-2991','NEW-2235-1476']
def main():
 g=json.load(gzip.open(ROOT/'photo2/r339/results/graph.json.gz','rt'));obs={r['id']:r for r in g['observations']};auth=json.load(open(ROOT/'photo2/r339/results/freeze.json'))['authoritative_labels']
 for o in NEW:auth[o]=dict(color='black',source='R340 explicit maker decision in conversation; independent of classifier')
 mustB=['R332-B-0098-0092','C-1893-2771','NEW-2259-1961','NEW-1920-531','NEW-2186-2343','NEW-2257-2004','R332-R-0025-0023','REC266-P032517']+NEW
 chosen=list(dict.fromkeys(mustB))
 for color,n in [('black',24),('red',12),('yellow',12)]:
  pool=[o for o,r in auth.items() if o in obs and r['color']==color]
  while sum(auth[o]['color']==color for o in chosen)<n:
   pts=np.array([obs[o]['xy'] for o in chosen]);o=max([o for o in pool if o not in chosen],key=lambda o:(float(np.min(np.linalg.norm(pts-obs[o]['xy'],axis=1))),o));chosen.append(o)
 rows=[];photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
 for i,o in enumerate(chosen):
  x,y=map(round,obs[o]['xy']);box=[x-20,y-20,x+21,y+21];rows.append(dict(number=i+1,id=o,color=auth[o]['color'],authority=auth[o]['source'],xy=obs[o]['xy'],bbox=box));photo.crop(box).save(OUT/f'native-{i+1:02d}.png')
 for page in range((len(rows)+11)//12):
  sheet=Image.new('RGB',(984,1464),'white');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(rows[page*12:page*12+12]):
   ox=i%3*328;oy=i//3*366;crop=Image.open(OUT/f'native-{r["number"]:02d}.png').resize((328,328),Image.Resampling.NEAREST);dc=ImageDraw.Draw(crop)
   # Local 0..40 coordinates, every5 native pixels, permit explicit hand ROIs.
   for k in range(0,41,5):
    dc.line((k*8,0,k*8,327),fill=(90,150,160),width=1);dc.line((0,k*8,327,k*8),fill=(90,150,160),width=1);dc.text((k*8+1,1),str(k),fill='white',stroke_width=1,stroke_fill='black');dc.text((1,k*8+1),str(k),fill='white',stroke_width=1,stroke_fill='black')
   sheet.paste(crop,(ox,oy+32));d.text((ox+2,oy+2),f"{r['number']} {r['id']} {r['color']}",fill='black')
  sheet.save(OUT/f'selection-{page+1:02d}.png')
 (OUT/'selection.json').write_text(json.dumps(dict(records=rows,policy='48 maker-confirmed IDs selected by previously documented hard cases, current maker decisions and spatial diversity. No new brightness score or pattern color enters selection.',previous_threshold=73.5,started_utc='2026-10-20T01:35:33Z',deadline_utc='2026-10-20T01:45:33Z'),indent=2)+'\n');print('Selected',len(rows),{c:sum(r['color']==c for r in rows) for c in ['black','red','yellow']})
if __name__=='__main__':main()

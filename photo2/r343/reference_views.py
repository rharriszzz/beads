"""Curated native contexts for color-independent selection of visible glass."""
from common import *
TARGETS=[Q101,C62,'NEW-1927-2829','REC266-P146299','R332-R-0147-0142','REC266-P074746']+P29+['C-0309-0966','C-0313-1445','C-1899-0420','NEW-1442-248','C-0445-1614','C-1559-0252','E5-1455-3009','C-1251-0290','C-1721-1566','C-1526-3018','C-1777-1612','C-1364-2971','R332-R-0167-0155','REC266-P144445','R332-R-0125-0118','R332-R-0037-0040','REC266-P035619','R332-R-0197-0183']
def main():
 _,obs,_,rgb,auth,extra=load();allobs=dict(obs,**extra);photo=Image.fromarray(rgb);manual={r['id']:r for r in read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records']};old={r['id']:r['measurement'] for r in read(ROOT/'photo2/r342/classification.json.gz')['records']};old[C62]=next(r['measurement'] for r in read(ROOT/'photo2/r342/candidate-checks.json')['records'] if r['id']==C62);manifest=[]
 for start in range(0,len(TARGETS),6):
  board=Image.new('RGB',(1200,800),'#f7f7f7');d=ImageDraw.Draw(board)
  for i,o in enumerate(TARGETS[start:start+6]):
   xy=allobs[o]['xy'];x,y=np.rint(xy).astype(int);box=[int(x-24),int(y-24),int(x+25),int(y+25)];raw=photo.crop(box).resize((343,343),Image.Resampling.NEAREST);ann=raw.copy();ad=ImageDraw.Draw(ann)
   # Absolute pixel grid every5 native pixels; original sample is cyan.
   for xx in range(x-20,x+21,5):ad.text(((xx-box[0])*7,0),str(xx),fill='white',stroke_width=1,stroke_fill='black')
   for yy in range(y-20,y+21,5):ad.text((0,(yy-box[1])*7),str(yy),fill='white',stroke_width=1,stroke_fill='black')
   ad.ellipse((24*7-3,24*7-3,24*7+3,24*7+3),outline='white')
   if o in old:
    a,b,c,e=old[o]['patch_box'];ad.rectangle(((a-box[0])*7,(b-box[1])*7,(c-box[0])*7-1,(e-box[1])*7-1),outline='cyan',width=2)
   if o in manual:
    a,b,c,e=manual[o]['absolute_material_box'];ad.rectangle(((a-box[0])*7,(b-box[1])*7,(c-box[0])*7-1,(e-box[1])*7-1),outline='lime',width=2)
   ox=i%3*400;oy=i//3*400;board.paste(ann,(ox,oy+45));d.text((ox,oy),o,fill='black');d.text((ox,oy+16),f'{authority(o,auth)}; XY {x},{y}',fill='black');manifest.append(dict(id=o,box=box,xy=xy,authority=authority(o,auth)))
  board.save(OUT/f'native-reference-{start//6+1:02d}.png')
 save(OUT/'reference-manifest.json',manifest);print('Native reference contexts',len(TARGETS))
if __name__=='__main__':main()

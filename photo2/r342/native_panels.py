"""Native comparison sheets; no pattern colors are supplied to measurements."""
from common import *
def sheets(ids,filename,measurements=None):
 _,obs,_,rgb,_=load();photo=Image.fromarray(rgb);pages=[]
 for offset in range(0,len(ids),12):
  subset=ids[offset:offset+12];board=Image.new('RGB',(1200,300*((len(subset)+2)//3)),'#f8f8f8');d=ImageDraw.Draw(board)
  for i,o in enumerate(subset):
   point=obs[o]['xy'];x,y=np.rint(point).astype(int);box=[int(x-32),int(y-32),int(x+33),int(y+33)];raw=photo.crop(box).resize((260,260),Image.Resampling.NEAREST);ann=raw.copy();ad=ImageDraw.Draw(ann);ad.ellipse((122,122,134,134),outline='white',width=1)
   m=measurements.get(o) if measurements else None
   if m:
    for px,py in m['region_pixels']:ad.point(((px-box[0])*4,(py-box[1])*4),fill='orange')
    a,b,c,e=m['patch_box'];ad.rectangle(((a-box[0])*4,(b-box[1])*4,(c-box[0])*4-1,(e-box[1])*4-1),outline='cyan',width=2)
   # Actual unmarked pixels retained beside each marked crop on alternate pages.
   col=i%3;row=i//3;ox=col*400;oy=row*300;board.paste(ann,(ox,oy+30));d.text((ox+2,oy+1),o,fill='black');d.text((ox+2,oy+16),f"recorded {MAKER.get(o,obs[o]['color'])}; score {m['score'] if m else '-'}",fill='black');d.text((ox+264,oy+55),'white: source\ncyan:3x3\norange:core',fill='black');pages.append(dict(id=o,crop_box=box))
  path=OUT/f'{filename}-{offset//12+1:02d}.png';board.save(path)
 save(OUT/f'{filename}-manifest.json',pages)
def main():
 g,obs,co,rgb,auth=load();variants=read(OUT/'alternatives.json.gz');chosen=variants['offset-core'];truth={o:MAKER.get(o,r['color']) for o,r in obs.items()};dis=[o for o in obs if (truth[o]=='black')!=(chosen[o]['decision']=='black')];print('raw discrepancies',[(o,truth[o],chosen[o]['score']) for o in dis]);sheets(dis,'fixed-disagreements',chosen)
 p=read(ROOT/'photo2/r341/pattern208.json');targets=sorted({o for e in p['entries'] if e['status']=='conflict' for o in e['ids'] if o not in MAKER});sheets(targets,'remaining-colors',chosen)
 specials=list(MAKER)+['K-1740-1575','RF70T-K-2172-1154','K-2183-1053','C-1253-2928','C-0505-1557','C-1264-2957','E5-1178-2887'];sheets(specials,'regressions',chosen)
if __name__=='__main__':main()

"""Native comparison contact sheets; pigment scores do not choose geometry."""
from explore import *
from PIL import ImageDraw

def sheet(rows,out,prefix,manual=None):
 out=Path(out);manual=manual or {};photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');pages=[]
 for page in range((len(rows)+5)//6):
  board=Image.new('RGB',(1056,min(6,len(rows)-page*6)*315),'white');draw=ImageDraw.Draw(board)
  for i,r in enumerate(rows[page*6:page*6+6]):
   x,y=map(round,r['xy']);box=[x-22,y-22,x+44,y+44];raw=photo.crop(box).resize((264,264),Image.Resampling.NEAREST);annotated=raw.copy();d=ImageDraw.Draw(annotated);m=r['measurement'];n=page*6+i+1
   if m:
    for px,py in m['region_pixels']:d.rectangle(((px-box[0])*4,(py-box[1])*4,(px-box[0]+1)*4-1,(py-box[1]+1)*4-1),outline='#f0a020')
    a,b,c,e=m['patch_box'];d.rectangle(((a-box[0])*4,(b-box[1])*4,(c-box[0])*4-1,(e-box[1])*4-1),outline='cyan',width=2)
   if r['id'] in manual:
    a,b,c,e=manual[r['id']]['absolute_material_box'];d.rectangle(((a-box[0])*4,(b-box[1])*4,(c-box[0])*4-1,(e-box[1])*4-1),outline='lime',width=2)
   py=i*315;board.paste(raw,(0,py+42));board.paste(annotated,(264,py+42));score=m['score'] if m else None;draw.text((2,py+1),f"{n} {r['id']} current {r['recorded_color']} score {score}",fill='black');draw.text((536,py+50),f"Maker: {r.get('authority')}\nPhysical interior: {r['geometry']['physical_interior']}\nNative support: {r['xy']}\nOrange: automatic region\nCyan: chosen3x3\nGreen: manual glass rectangle",fill='black')
  p=out/f'{prefix}-{page+1:02d}.png';board.save(p);pages.append(str(p))
 return pages

def main():
 d=json.load(open(OUT/'trial-1.json'));manual={r['id']:r for r in read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records']};rows=d['records'];err=[r for r in rows if r['authority'] and r['measurement'] and (r['measurement']['decision']=='black')!=(r['authority']['color']=='black')];print('Errors',sheet(err,OUT,'trial-1-errors',manual))
 suspects=[r for r in rows if r['recorded_color']!='black' and r['measurement'] and r['measurement']['decision']=='black'];print('Suspects',sheet(suspects,OUT,'trial-1-suspects',manual))
 print('black miss count',sum(bool(r['recorded_color']=='black' and r['measurement'] and r['measurement']['decision']=='not-black') for r in rows))
if __name__=='__main__':main()

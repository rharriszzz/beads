"""Complete native inventory audit, not selected by predicted pattern or score."""
from common import *

def sheets(records,prefix,small=True):
 rgb=load()[3];photo=Image.fromarray(rgb);manifest=[];perpage=48 if small else 6
 for page in range((len(records)+perpage-1)//perpage):
  subset=records[page*perpage:(page+1)*perpage];w,h=(8*200,math.ceil(len(subset)/8)*206) if small else (1040,len(subset)*290);board=Image.new('RGB',(w,h),'white');draw=ImageDraw.Draw(board)
  for i,r in enumerate(subset):
   n=page*perpage+i+1;x,y=map(round,r['xy']);half=18 if small else 26;box=[x-half,y-half,x+half+1,y+half+1];raw=photo.crop(box);scale=4 if small else 5;raw=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST);ann=raw.copy();d=ImageDraw.Draw(ann);m=r['measurement']
   if m:
    for px,py in m['region_pixels']:
     if (px-box[0])%2==0 and (py-box[1])%2==0:d.point(((px-box[0])*scale,(py-box[1])*scale),fill='orange')
    a,b,c,e=m['patch_box'];d.rectangle(((a-box[0])*scale,(b-box[1])*scale,(c-box[0])*scale-1,(e-box[1])*scale-1),outline='cyan',width=1 if small else 2)
   # White tiny cross marks the inherited support, not a claimed physical center.
   d.line(((x-box[0])*scale-2,(y-box[1])*scale,(x-box[0])*scale+2,(y-box[1])*scale),fill='white');d.line(((x-box[0])*scale,(y-box[1])*scale-2,(x-box[0])*scale,(y-box[1])*scale+2),fill='white')
   score=m['score'] if m else None
   if small:
    ox=i%8*200;oy=i//8*206;board.paste(ann,(ox+20,oy+37));draw.text((ox+2,oy),f"{n} {r['id']}",fill='black');draw.text((ox+2,oy+15),f"{r['recorded_color']} {score} {'I' if r['automatic_decision']!='unknown' else 'E'}",fill='black')
   else:
    oy=i*290;board.paste(raw,(0,oy+25));board.paste(ann,(270,oy+25));draw.text((2,oy),f"{n} {r['id']}  {r['recorded_color']}  score{score}",fill='black');draw.text((550,oy+30),f"XY {r['xy']}\nMaker {bool(r['maker_authority'])}\nAutomatic {r['automatic_decision']}\nR340 {r['r340_score']}\nCyan: new3x3; orange: region\nNo pattern information",fill='black')
   manifest.append(dict(page=page+1,number=n,id=r['id'],crop_box=box,recorded_color=r['recorded_color'],score=score))
  board.save(OUT/f'{prefix}-{page+1:02d}.png')
 save(OUT/f'{prefix}-manifest.json',manifest);return manifest

def main():
 rows=read(OUT/'classification.json.gz')['records'];br=[r for r in rows if r['recorded_color'] in ['black','red']];y=[r for r in rows if r['recorded_color']=='yellow'];dis=[r for r in rows if r['measurement'] is None or (r['recorded_color']=='black')!=(r['measurement']['raw_decision']=='black')];sheets(br,'audit-black-red');sheets(y,'audit-yellow');sheets(dis,'disagreement',False);print('Native pages B/R',len(br),'Y',len(y),'disagreements',len(dis))
if __name__=='__main__':main()

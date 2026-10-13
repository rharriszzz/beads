"""Full photographic audit atlas: raw photos and numbered automatic proposals."""
import json,csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .centerline_r275 import ROOT,OUT,Band,save,load_rows
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def textfont(n=13):return ImageFont.truetype(FONT,n)
def points(r):return [r['point']['x'],r['point']['y']]
def panel(im,box,locs,regions,scale=3,labels=True,curve=None):
 crop=im.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.NEAREST);d=ImageDraw.Draw(crop);xy=lambda p:((p[0]-box[0]+.5)*scale,(p[1]-box[1]+.5)*scale)
 if curve is not None:
  for a,b in zip(curve,curve[1:]):
   if box[0]-2<=a[0]<=box[2]+2 and box[1]-2<=a[1]<=box[3]+2:d.line([xy(a),xy(b)],fill='white',width=1)
 for r in regions:
  if r['id'] not in {l['id'] for l in locs}:continue
  d.line([xy(p) for p in r['outline']['smooth']],fill='cyan',width=1)
 used=[]
 for l in locs:
  x,y=points(l)
  if not(box[0]<=x<box[2] and box[1]<=y<box[3]):continue
  px,py=xy((x,y));color='cyan' if l.get('audit_status')!='still unresolved' else '#ffb14e';d.ellipse((px-2,py-2,px+2,py+2),fill=color)
  if not labels:continue
  label=str(l.get('audit_number',l['inventory_number']));font=textfont(12);w=d.textlength(label,font=font)+4;h=15
  choices=[(px+dx,py+dy) for radius in (8,20,32,44,56) for dx,dy in [(radius,-radius),(-radius-w,-radius),(radius,radius),(-radius-w,radius)]]
  candidates=[(ax,ay) for ax,ay in choices if 0<=ax<=crop.width-w and 0<=ay<=crop.height-h]
  def penalty(p):
   ax,ay=p;return sum(max(0,min(ax+w,c)-max(ax,a))*max(0,min(ay+h,e)-max(ay,b)) for a,b,c,e in used)
  ax,ay=min(candidates,key=lambda p:(penalty(p),(p[0]-px)**2+(p[1]-py)**2)) if candidates else (max(0,min(px,crop.width-w)),max(0,min(py,crop.height-h)))
  used.append((ax,ay,ax+w,ay+h));d.line([(px,py),(ax+w/2,ay+h/2)],fill=color,width=1);d.rectangle((ax,ay,ax+w,ay+h),fill='black');d.text((ax+2,ay),label,font=font,fill=color)
 return crop

def main():
 im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());data=json.loads((OUT/'inventory.json').read_text()) if (OUT/'inventory.json').exists() else old;band=Band();regionmap={r['id']:r for r in data['beads']};locs=[]
 for l in data['locations']:
  r=regionmap.get(l['id']);b=band.qualifies(points(l),r['region'] if r else None)
  l['centerline_near']=b
  if b['in_band']:locs.append(l)
 # Spatial reference order, never physical string indices.
 for i,l in enumerate(sorted(locs,key=lambda l:(points(l)[1],points(l)[0],l['id'])),1):l['audit_number']=i
 save('target-locations.json',locs);print('atlas locations',len(locs),flush=True)
 overview=im.copy();d=ImageDraw.Draw(overview);curve=band.points
 d.line([tuple(p) for p in curve],fill='white',width=1)
 # Thin band boundaries approximate normal offsets for display only.
 tang=np.roll(curve,-1,axis=0)-np.roll(curve,1,axis=0);normal=np.c_[-tang[:,1],tang[:,0]];normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-10)
 for s in (-12,12):d.line([tuple(p) for p in curve+s*normal],fill='#ffb14e',width=1)
 for l in locs:
  x,y=points(l);d.ellipse((x-2,y-2,x+2,y+2),fill='cyan')
 overview.resize((1270,1591)).save(OUT/'whole-photo.png')
 # Every 120px of the closed reference, overlapping 180px square tiles.
 ar=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];atlas=[]
 for i,a in enumerate(np.arange(0,ar[-1],120),1):
  k=np.searchsorted(ar,a);x,y=curve[k];box=[int(x)-90,int(y)-90,int(x)+90,int(y)+90];included=[l for l in locs if box[0]<=points(l)[0]<box[2] and box[1]<=points(l)[1]<box[3]]
  raw=im.crop(box).resize((540,540),Image.Resampling.NEAREST);unc=[dict(id=u['id'],inventory_number=0,audit_number=u['audit_number'],point=dict(x=u['anchor'][0],y=u['anchor'][1]),audit_status='still unresolved') for u in data.get('uncertain',[]) if 'audit_number' in u];new=panel(im,box,included+unc,data['beads'],curve=curve);sheet=Image.new('RGB',(1090,570),'white');sheet.paste(raw,(0,30));sheet.paste(new,(550,30));dr=ImageDraw.Draw(sheet);dr.text((5,5),f'Tile {i:02d} | original photo',fill='black',font=textfont());dr.text((555,5),'Automatic target locations (not verified bead identities)',fill='black',font=textfont());sheet.save(OUT/f'atlas-{i:02d}.jpg',quality=95)
  atlas.append(dict(tile=i,box=box,ids=[l['id'] for l in included],audit_numbers=[l['audit_number'] for l in included]))
 save('atlas.json',atlas)
 # Compact raw-only sheets allow a full-curve visual pass independent of labels.
 for j in range(0,len(atlas),12):
  sheet=Image.new('RGB',(1080,4*390),'white');dr=ImageDraw.Draw(sheet)
  for i,t in enumerate(atlas[j:j+12]):
   x=(i%3)*360;y=(i//3)*390;sheet.paste(im.crop(t['box']).resize((360,360),Image.Resampling.NEAREST),(x,y+25));dr.text((x+5,y+4),f"Tile {t['tile']:02d}",fill='black',font=textfont())
  sheet.save(OUT/f'raw-sheet-{j//12+1}.jpg',quality=95)
 if (OUT/'inventory.json').exists():save('inventory.json',data)
if __name__=='__main__':main()

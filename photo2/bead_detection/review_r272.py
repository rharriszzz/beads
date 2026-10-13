"""Smallest/median/largest inventory examples and separate exclusion audit cards."""
import json,gzip
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .experiment_r272 import ROOT,OUT,save
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n=18):return ImageFont.truetype(FONT,n)
def card(rgb,box,beads,name,caption='',dot=None):
    x0,y0,x1,y1=box;scale=6;crop=Image.fromarray(rgb[y0:y1,x0:x1]).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST);overlay=crop.copy();d=ImageDraw.Draw(overlay)
    for b in beads:
        pts=[((x-x0+.5)*scale,(y-y0+.5)*scale) for x,y in b['outline']['smooth']];d.line(pts,fill='#00ffff',width=2);x,y=b['brightest']['x'],b['brightest']['y'];cx,cy=(x-x0+.5)*scale,(y-y0+.5)*scale;d.ellipse((cx-3,cy-3,cx+3,cy+3),fill='#00ffff')
    if dot:
        cx,cy=(dot[0]-x0+.5)*scale,(dot[1]-y0+.5)*scale;d.ellipse((cx-3,cy-3,cx+3,cy+3),fill='#ff9900')
    width=2*crop.width+12;lines=[];line=''
    for word in caption.split():
        trial=(line+' '+word).strip()
        if font().getlength(trial)>width-16 and line:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    out=Image.new('RGB',(width,crop.height+42+26*len(lines)),'white');out.paste(crop,(0,34));out.paste(overlay,(crop.width+12,34));d=ImageDraw.Draw(out);d.text((8,7),'Original',fill='black',font=font());d.text((crop.width+20,7),'Excluded candidate' if dot else ('Interior and brightest point' if beads else 'No accepted interior'),fill='black',font=font())
    for i,line in enumerate(lines):d.text((8,crop.height+40+26*i),line,fill='black',font=font())
    out.save(OUT/name)
def main():
    rgb=np.asarray(Image.open(OUT/'photo-srgb.png'));data=json.load(open(OUT/'inventory.json'));beads=data['beads'];ordered=sorted(beads,key=lambda b:(b['region']['pixel_count'],b['id']));chosen=[]
    for title,i in [('smallest',0),('median',(len(ordered)-1)//2),('largest',len(ordered)-1)]:
        b=ordered[i];x,y=b['anchor'];card(rgb,[x-24,y-24,x+25,y+25],[b],title+'.png',f"{title.capitalize()}: {b['id']}, {b['color']}, {b['region']['pixel_count']} exact interior pixels. Inventory number {b['inventory_number']}; size rank {i+1} of {len(beads)}.");chosen.append(dict(example=title,id=b['id'],size_rank=i+1,pixel_count=b['region']['pixel_count']))
    save('size-examples.json',chosen)
    from .test_inventory_r272 import run
    fixture,_,_,synthetic,_=run('black')
    card(synthetic,[26,21,75,70],fixture,'synthetic-black-reflection.png','Known synthetic black bead: the accepted interior stays around its reflection, not the whole body.')
    for name in ('R00956','R01284'):
        box=json.load(open(ROOT/'photo2/review/r269/starts.json'))[name]['box'];selected=[b for b in beads if box[0]<=b['anchor'][0]<box[2] and box[1]<=b['anchor'][1]<box[3]];card(rgb,box,selected,name+'-interiors.png')
    if (OUT/'single-gate-diagnostics.jsonl.gz').exists():
        rows=list(map(json.loads,gzip.open(OUT/'single-gate-diagnostics.jsonl.gz','rt')));examples=[]
        for key in ('background-nearby','insufficient-light','uneven-light'):
            pool=[r for r in rows if r['sole_cheap_failure']==key];pool.sort(key=lambda r:(not r['passes_remaining_checks'],-r['original']['mean_y'],r['candidate_id']))
            for i,r in enumerate(pool[:3],1):
                x,y=r['anchor'];name=f'audit-{key}-{i}.png';description={'background-nearby':'The patch touches background evidence.','insufficient-light':'The neighborhood is below the brightness floor.','uneven-light':'Too much of the neighborhood is in shade.'}[key];description+=' It passes the remaining measured checks, but stays excluded.' if r['passes_remaining_checks'] else ' Additional detailed checks also fail; it stays excluded.';card(rgb,[x-24,y-24,x+25,y+25],[],name,description,dot=r['anchor']);examples.append(dict(file=name,candidate_id=r['candidate_id'],sole_cheap_failure=key,other_failures=r['other_failures'],passes_remaining_checks=r['passes_remaining_checks']))
        save('audit-examples.json',examples)
if __name__=='__main__':main()

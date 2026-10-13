"""Plain original/cyan photographic comparisons; diagnostics stay separate."""
import json,gzip
from PIL import Image,ImageDraw
from .experiment_coverage_r272 import ROOT,OUT

def marked(im,beads,box,scale=4):
    x0,y0,x1,y1=box;out=im.crop(box).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST);d=ImageDraw.Draw(out)
    for b in beads:
        if not(x0<=b['brightest']['x']<x1 and y0<=b['brightest']['y']<y1):continue
        pts=[((x-x0+.5)*scale,(y-y0+.5)*scale) for x,y in b['outline']['smooth']];d.line(pts,fill='cyan',width=max(1,scale//3));x=(b['brightest']['x']-x0+.5)*scale;y=(b['brightest']['y']-y0+.5)*scale;r=max(1,scale/3);d.ellipse((x-r,y-r,x+r,y+r),fill='cyan')
    return out

def pair(im,beads,box,name,title,scale=4):
    original=im.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale),Image.Resampling.NEAREST);overlay=marked(im,beads,box,scale);w,h=original.size;sheet=Image.new('RGB',(2*w+12,h+42),'white');sheet.paste(original,(0,42));sheet.paste(overlay,(w+12,42));d=ImageDraw.Draw(sheet);d.text((6,4),title,fill='black');d.text((6,24),'Original photograph',fill='black');d.text((w+18,24),'Accepted interiors and brightest pixels',fill='black');sheet.save(OUT/name)

def main():
    data=json.loads((OUT/'inventory.json').read_text());beads=data['beads'];im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');overview=marked(im,beads,[0,0,im.width,im.height],1);overview.resize((1016,1273),Image.Resampling.LANCZOS).save(OUT/'whole-photo.png')
    samples=json.loads((OUT/'photo-samples.json').read_text())
    for s in samples['samples']:pair(im,beads,s['box'],s['id']+'-comparison.png',s['id']+' frozen geographic evaluation sample',5)
    for c in ('black','red','yellow'):
        a=[b for b in beads if b['color']==c];a.sort(key=lambda b:(b['region']['pixel_count'],b['id']))
        if not a:continue
        for label,b in [('smallest',a[0]),('median',a[len(a)//2]),('largest',a[-1])]:
            x,y=b['anchor'];pair(im,beads,[x-40,y-40,x+41,y+41],f'{c}-{label}.png',f'{c} {label}: {b["id"]}, {b["region"]["pixel_count"]} native pixels',5)
    for name,box in [('R00956',[2233,1863,2314,1944]),('R01284',[941,2640,1022,2721])]:pair(im,beads,box,name+'.png',name,5)
    # Separate exclusions with one dot and reason, no busy overlays.
    candidates=[]
    with gzip.open(OUT/'candidates.jsonl.gz','rt') as f:
        for line in f:
            b=json.loads(line)
            if not b['accepted'] and ('region' in b or 'primary_endpoint' in b):candidates.append(b)
    chosen=[]
    for reason in ('black-material','black-size','region-small','region-holes','better-peak','ownership-conflict'):
        a=[b for b in candidates if reason in b['reasons']]
        if a:chosen.append(a[len(a)//2])
    sheet=Image.new('RGB',(930,280*len(chosen)),'white');d=ImageDraw.Draw(sheet)
    for i,b in enumerate(chosen):
        x,y=b['anchor'];crop=im.crop((x-30,y-30,x+31,y+31)).resize((244,244),Image.Resampling.NEAREST);sheet.paste(crop,(5,280*i+25));d.text((5,280*i+5),b['id'],fill='black');d.ellipse((5+119,280*i+25+119,5+125,280*i+25+125),fill='orange')
        for j,reason in enumerate(b['explanations']):
            import textwrap
            for k,line in enumerate(textwrap.wrap(reason,85)):d.text((265,280*i+35+j*45+k*16),line,fill='black')
    sheet.save(OUT/'excluded-examples.png')
if __name__=='__main__':main()

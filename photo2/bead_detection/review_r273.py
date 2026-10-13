"""Original / preserved R272 / R273 photo comparisons, without dense labels."""
import json,gzip
from PIL import Image,ImageDraw
from .experiment_r273 import ROOT,OUT,save
from .review_coverage_r272 import marked

def triplet(im,old,new,box,name,title,scale=4,labels=('Original photograph','R272','R273')):
    w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale;sheet=Image.new('RGB',(3*w+20,h+44),'white');d=ImageDraw.Draw(sheet)
    ims=[im.crop(box).resize((w,h),Image.Resampling.NEAREST),marked(im,old,box,scale),marked(im,new,box,scale)]
    d.text((5,3),title,fill='black')
    for i,(label,photo) in enumerate(zip(labels,ims)):sheet.paste(photo,(i*(w+10),44));d.text((i*(w+10)+5,25),label,fill='black')
    sheet.save(OUT/name)

def main():
    im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');old=json.loads((ROOT/'photo2/review/r272-coverage/inventory.json').read_text())['beads'];new=json.loads((OUT/'inventory.json').read_text())['beads'];lookup={r['id']:r for r in old};examples=[]
    for name,box in [('R00956',[2233,1863,2314,1944]),('R01284',[941,2640,1022,2721]),('black-glints',[1400,2990,1500,3090]),('red-context',[2120,1000,2220,1100])]:triplet(im,old,new,box,name+'.png',name,5)
    for method in ('connected','star-color','star-valley'):
        with gzip.open(OUT/(method+'-candidates.jsonl.gz'),'rt') as f:rows=[json.loads(l) for l in f]
        triplet(im,old,[r for r in rows if r['accepted']],[941,2640,1022,2721],'method-'+method+'.png','R01284: '+method,5)
    for color in ('black','red','yellow'):
        a=sorted([r for r in new if r['color']==color],key=lambda r:(r['region']['pixel_count'],r['id']))
        for label,b in [('smallest',a[0]),('median',a[len(a)//2]),('largest',a[-1])]:
            x,y=b['anchor'];title=f"{color} {label}: {b['id']} | old {lookup[b['id']]['region']['pixel_count']} / new {b['region']['pixel_count']} native pixels";triplet(im,old,new,[x-40,y-40,x+41,y+41],f'{color}-{label}.png',title,4);examples.append(dict(file=f'{color}-{label}.png',id=b['id'],old_pixels=lookup[b['id']]['region']['pixel_count'],new_pixels=b['region']['pixel_count']))
    selected=json.loads((OUT/'selection.json').read_text())['method']
    with gzip.open(OUT/(selected+'-candidates.jsonl.gz'),'rt') as f:records=[json.loads(l) for l in f]
    groups={}
    for r in records:
        if r['color']=='black' and r.get('black_ownership'):
            g=r['black_ownership'];groups[tuple(g['group'])]=g
    for i,g in enumerate(groups.values(),1):
        bs=[lookup[id] for id in g['group']];xx=[b['brightest']['x'] for b in bs];yy=[b['brightest']['y'] for b in bs];box=[min(xx)-25,min(yy)-25,max(xx)+26,max(yy)+26];name=f'black-ownership-{i:02d}.png';title='Keep '+g['winner']+'; weaker reflections excluded' if g['winner'] else 'Ambiguous close reflections: all excluded';triplet(im,old,new,box,name,title,5);g['comparison_image']=name
    save('black-review-groups.json',list(groups.values()));save('region-examples.json',examples)
    marked(im,new,[0,0,im.width,im.height],1).resize((1016,1273),Image.Resampling.LANCZOS).save(OUT/'whole-photo.png')
    for s in json.loads((ROOT/'photo2/review/r272-coverage/photo-samples.json').read_text())['samples']:triplet(im,old,new,s['box'],s['id']+'.png','Geographic sample '+s['id'],4)
if __name__=='__main__':main()

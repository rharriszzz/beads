"""Read-only illustration of the verified S25 numerical pseudo-separator."""
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load

def build(out):
    data,m,obs=load();row=next(r for r in read(ROOT/'photo2/r298/evidence/separators.json')['records'] if r['id']=='S25')
    xy=np.array(row['xy']);detail=read(ROOT/'photo2/r308/evidence/separator-discontinuity.json')['rows'][0];point=xy[72];lo=np.floor(point-65).astype(int);hi=lo+130
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');raw=photo.crop((*lo,*hi));panels=[]
    for label,overlay in [('Original photograph',False),('Observed separator route; unresolved model ray',True)]:
        im=raw.copy();d=ImageDraw.Draw(im)
        if overlay:
            d.line([tuple(p-lo) for p in xy],fill='#22baff');v=xy[int(row['valley_sample'])]-lo;u=point-lo;d.ellipse((* (v-2),*(v+2)),outline='#ffe44a');d.ellipse((* (u-3),*(u+3)),outline='#ff30df')
        p=Image.new('RGB',(520,570),'#182530');p.paste(im.resize((520,520),Image.Resampling.NEAREST),(0,50));ImageDraw.Draw(p).text((8,10),label,fill='white');panels.append(p)
    image=Image.new('RGB',(1040,570));[image.paste(p,(520*i,0)) for i,p in enumerate(panels)];image.save(out/'review/unknown-ray-separator.png')
    save(out/'unknown-ray-case.json',dict(separator='S25',unknown_sample=72,unknown_photo_point=point.tolist(),observed_valley_sample=row['valley_sample'],observed_valley_point=xy[int(row['valley_sample'])].tolist(),before_error=detail['before'],after_error=detail['after'],explanation='Magenta is an unresolved MODEL ray, not a measured separator. Yellow is the existing uncertain observed valley; blue is its original photographic sampling route. The corrected objective excludes owner transitions touching unresolved rays.'))

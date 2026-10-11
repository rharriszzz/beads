"""Curated native photographic evidence; plotting is diagnostic, not rendering."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from scipy.ndimage import binary_erosion
from .refit import OUT,ROOT,BeadCurve,SurfaceLoss,rays
from .generate import save,sha

def boundary(model,box,gi):
    y,x=np.mgrid[box[1]:box[3],box[0]:box[2]];xy=np.c_[x.ravel(),y.ravel()]
    own,_,un=rays(model,xy,model.geometry(np.arange(model.source.nbeads)));mask=((own==gi)&(un==0)).reshape(x.shape)
    return mask&~binary_erosion(mask),mask

def panel(photo,box,model=None,gi=None,support=None,title='',scale=3):
    im=photo.crop(box);d=ImageDraw.Draw(im)
    if model is not None:
        edge,_=boundary(model,box,gi);y,x=np.where(edge)
        for xx,yy in zip(x,y):d.point((int(xx),int(yy)),fill=(50,245,245))
    if support is not None:
        for x,y in support:d.point((int(x-box[0]),int(y-box[1])),fill=(255,240,40))
    im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out=Image.new('RGB',(im.width,im.height+42),(20,32,42));out.paste(im,(0,42));ImageDraw.Draw(out).text((8,8),title,fill='white');return out

def run():
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');results=json.loads((OUT/'results.json').read_text())
    box=[1318,305,1380,355];images=[panel(photo,box,title='Original photograph',scale=5)]
    for v in ['A','B','C','D']:
        c=json.loads((OUT/f'R258_origin_{v}.json').read_text());im=panel(photo,box,BeadCurve(c),(c['origin']+2)%c['n'],title=f'{v}: only predicted bead 2 footprint',scale=5);images.append(im)
    allim=Image.new('RGB',(sum(i.width for i in images),images[0].height));x=0
    for im in images:allim.paste(im,(x,0));x+=im.width
    allim.save(OUT/'bead2-comparison.png');photo.crop(box).save(OUT/'bead2-raw.png')
    ev=json.loads((OUT/'origin-evidence.json').read_text());r=next(r for r in ev['observations'] if r['identity']==2)
    im=panel(photo,box,support=r['patch'],title='Conditional positive support (not full mask)',scale=6);im.save(OUT/'bead2-confirmed-support.png')
    for name in ['origin','straight-black','bend','opposite']:
        ev=json.loads((OUT/(name+'-evidence.json')).read_text());box=ev['box'];raw=photo.crop(box);raw.save(OUT/(name+'-raw.png'));ims=[]
        for v in ['A','B','C','D']:
            c=json.loads((OUT/f'R258_{name}_{v}.json').read_text());m=BeadCurve(c);loss=SurfaceLoss(box,ev['observations'],step=1);own=loss.raster(m);edge=(own!=np.roll(own,1,0))|(own!=np.roll(own,1,1));edge&=own>=0
            im=raw.copy();arr=np.array(im);arr[edge]=[50,225,225];im=Image.fromarray(arr);top=Image.new('RGB',(im.width,im.height+24),(20,32,42));top.paste(im,(0,24));ImageDraw.Draw(top).text((6,4),v+' predicted ownership boundaries',fill='white');ims.append(top)
        out=Image.new('RGB',(raw.width*4,raw.height+24));
        for j,im in enumerate(ims):out.paste(im,(j*raw.width,0))
        out.save(OUT/(name+'-comparison.png'))
    locator=photo.resize((635,796));d=ImageDraw.Draw(locator)
    for name in ['origin','straight-black','bend','opposite']:
        box=json.loads((OUT/(name+'-evidence.json')).read_text())['box'];b=[v/4 for v in box];d.rectangle(b,outline='cyan',width=2);d.text((b[0],b[1]-12),name,fill='white')
    locator.save(OUT/'sections.png')
    save(OUT/'artifact-hashes.json',{p.name:sha(p) for p in OUT.glob('*.png')})
if __name__=='__main__':run()

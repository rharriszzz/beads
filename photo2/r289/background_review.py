"""Show a retained synthetic background false observation; no repair on holdout."""
from PIL import Image,ImageDraw
from .common import *
from .review import mark,text

def main():
    for folder in sorted((OUT/'synthetic').glob('scene-*')):
        d=read(folder/'evaluation.json')
        if d['scene']['split']!='evaluation':continue
        truth=np.load(folder/'truth.npz')['owner'];inference=read(folder/'on-inference.json.gz');rr=[r for r in inference['records'] if r['accepted'] and truth[r['point'][1],r['point'][0]]<0]
        if not rr:continue
        r=rr[0];center=np.array(r['point']);origin=center-35;im=Image.open(folder/'on-srgb.png').crop([*origin,*(center+36)]);side=284;out=Image.new('RGB',(side*2,side+65),'#20252b');draw=ImageDraw.Draw(out)
        for i in (0,1):out.paste(im.resize((side,side),Image.Resampling.NEAREST),(i*side,30))
        text(draw,(5,5),'Known background: false retained feature',16);mark(draw,r['point'],origin,(side,30),4,'cyan','plus');mark(draw,r['centroid'],origin,(side,30),4,'magenta','circle');text(draw,(5,side+35),folder.name+' / '+r['id']+' — preserved, not retuned',13);out.save(REVIEW/'synthetic-background-failure.png')
        save(OUT/'background-failure.json',dict(scene=folder.name,landmark=r['id'],point=r['point'],area=r['area'],detector_info=inference['info']));break
if __name__=='__main__':main()

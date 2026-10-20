"""Deterministic native inspection sheets, with current observations and local keys."""
import argparse
from PIL import ImageDraw
from .common import *
def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);g,obs,co=baseline();audit=read(artifact('audit/audit.json.gz'));rows=audit['rows'];chosen=[]
    plan=read(ROOT/'photo2/r338/inspection-plan.json')
    for cue in plan['cues']:chosen.append(next(r for r in rows if r['id']==cue['id'] and r['xy']==cue['xy'] and r['source_kind']==cue['source_kind']))
    photo=Image.fromarray(photograph());panels=[]
    for j,r in enumerate(chosen):
        x,y=map(int,np.rint(r['xy']));box=[x-70,y-65,x+71,y+66];crop=photo.crop(box);local=sorted([o for o in co if box[0]+3<obs[o]['xy'][0]<box[2]-3 and box[1]+3<obs[o]['xy'][1]<box[3]-3],key=lambda o:(obs[o]['xy'][1],obs[o]['xy'][0]));key=[dict(number=i+1,id=o,xy=obs[o]['xy'],ab=co[o],color=obs[o]['color']) for i,o in enumerate(local)];native=f'{j+1:02d}-native.png';crop.save(out/native);im=crop.resize((564,524),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
        for k in key:
            xx=(k['xy'][0]-box[0])*4;yy=(k['xy'][1]-box[1])*4;d.text((xx+3,yy-12),str(k['number']),fill='white',stroke_width=1,stroke_fill='black');d.ellipse((xx-2,yy-2,xx+2,yy+2),outline='white')
        xx=(r['xy'][0]-box[0])*4;yy=(r['xy'][1]-box[1])*4;d.ellipse((xx-6,yy-6,xx+6,yy+6),outline='#00ffff',width=1);d.text((xx+8,yy+4),'P',fill='#00ffff');im.save(out/f'{j+1:02d}-numbered.png');panels.append(dict(number=j+1,id=r['id'],xy=r['xy'],cell=r.get('cell'),owner=r.get('owner'),source_kind=r['source_kind'],reasons=r.get('reasons'),native=native,bbox=box,key=key))
    for page in range((len(chosen)+5)//6):
        sheet=Image.new('RGB',(564*3,550*2),'white');d=ImageDraw.Draw(sheet)
        for k in range(6):
            i=page*6+k
            if i>=len(chosen):break
            r=chosen[i];x=(k%3)*564;y=(k//3)*550;sheet.paste(Image.open(out/f'{i+1:02d}-numbered.png'),(x,y+24));d.text((x+6,y+4),f"{i+1}: {r['id']}",fill='black')
        sheet.save(out/f'sheet-{page+1:02d}.png')
    extra=[]
    for j,oid in enumerate(plan['additional_eligible_ids']):
        r=next(r for r in audit['ranked'] if r['id']==oid);x,y=np.rint(r['xy']).astype(int);box=[x-65,y-60,x+66,y+61];crop=photo.crop(box);im=crop.resize((655,605),Image.Resampling.NEAREST);d=ImageDraw.Draw(im);names=sorted([o for o in co if box[0]+4<obs[o]['xy'][0]<box[2]-4 and box[1]+4<obs[o]['xy'][1]<box[3]-4],key=lambda o:(obs[o]['xy'][1],obs[o]['xy'][0]));key=[]
        for i,o in enumerate(names):
            a,b=np.array(obs[o]['xy'])-box[:2];a*=5;b*=5;d.text((a+3,b-15),str(i+1),fill='white',stroke_width=1,stroke_fill='black');key.append(dict(number=i+1,id=o,xy=obs[o]['xy'],ab=co[o],color=obs[o]['color']))
        d.ellipse((320,294,330,304),outline='cyan',width=1);d.text((335,300),'P',fill='cyan');im.save(out/f'eligible-{j+1}-numbered.png');crop.save(out/f'eligible-{j+1}-native.png');extra.append(dict(id=oid,bbox=box,xy=r['xy'],key=key))
    save(out/'eligible-panels.json',extra)
    save(out/'panels.json',panels);print('INSPECT',len(panels),'native contexts')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)

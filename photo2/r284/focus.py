"""Evaluation-only targeted comparisons; never feeds segmentation."""
import numpy as np
from PIL import Image,ImageDraw
from photo2.r282.common import ROOT,photo,read,save,pixels
from .run import OUT
from .review import REVIEW,annotated,font,write_wrapped
from .assess import TARGETS


def main():
    native,_,_=photo();im=Image.fromarray(native);curve=read(ROOT/'photo2/r282/results/centerline.json')['points'];notes=read(OUT/'review-assessment.json');items=[]
    for name,targets in TARGETS.items():
        result=read(OUT/(name+'.json.gz'));case=result['case'];x,y=case['origin'];raw=im.crop((x,y,x+128,y+128))
        canvas=Image.new('RGB',(2000,1080),(24,29,36));d=ImageDraw.Draw(canvas)
        d.text((16,10),'R284A / '+name+' — reviewed features only; full context and all alternatives in the next panel',font=font(23),fill='white')
        for j,m in enumerate(['Raw','R283','A','B','C']):
            rows=[] if m=='Raw' else result['baseline'] if m=='R283' else result['methods'][m]['records']
            selected=[]
            for _,xy in targets:
                if not rows:break
                r=min(rows,key=lambda r:np.linalg.norm(np.array(r['seed'])-xy))
                if np.linalg.norm(np.array(r['seed'])-xy)<=6:selected.append(r)
            d.text((16+j*397,48),m,font=font(21),fill='white')
            for k,fill in enumerate((False,True)):
                picture=raw.resize((384,384),Image.Resampling.NEAREST) if m=='Raw' else annotated(raw,case['origin'],selected,curve,fill)
                canvas.paste(picture,(16+j*397,78+k*394))
        caption='Evaluation feature numbers: '+', '.join(f'{i+1} = {t[0]}' for i,t in enumerate(targets))+'. These are review locations only; no labels enter inference.\n'+' '.join(m+': '+notes[name][m] for m in 'ABC')+'\nTop: native mask edge. Bottom: measured interior. Cyan high, magenta unresolved, orange secondary; white line centerline, white dot centroid, orange cross cue. Every alternative remains in the full comparison.'
        # Grow the footer to its actual wrapped length, rather than clipping it.
        import textwrap
        lines=sum(len(textwrap.wrap(p,140)) for p in caption.split('\n'))
        final=Image.new('RGB',(2000,890+lines*24),(24,29,36));final.paste(canvas.crop((0,0,2000,862)),(0,0));write_wrapped(ImageDraw.Draw(final),(16,870),caption)
        file=name+'-focus.png';final.save(REVIEW/file);items.append(dict(file=file,title=name+' reviewed features',caption=caption))
    for case in read(OUT/'cases.json'):
        name=case['name'];result=read(OUT/(name+'.json.gz'));x,y=case['origin'];raw=im.crop((x,y,x+128,y+128));a=np.asarray(raw).copy()
        for r in result['methods']['C']['records']:
            if r['color']!='black':continue
            for field,color in [('measured_support',[40,215,255]),('reflection_support',[255,230,55])]:
                p=pixels(r[field])-[x,y];p=p[(p[:,0]>=0)&(p[:,0]<128)&(p[:,1]>=0)&(p[:,1]<128)]
                if len(p):a[p[:,1],p[:,0]]=color if r['status']!='secondary' else [255,145,35]
        canvas=Image.new('RGB',(800,540),(24,29,36));d=ImageDraw.Draw(canvas);d.text((12,8),name+' — C reflection versus dark collar',font=font(22),fill='white')
        canvas.paste(raw.resize((384,384),Image.Resampling.NEAREST),(12,46));canvas.paste(Image.fromarray(a).resize((384,384),Image.Resampling.NEAREST),(404,46))
        caption='Yellow: compact neutral reflection pixels. Blue: adjacent measured dark collar. Orange: suspected secondary feature; same body is not proven. All black candidates are shown, including unresolved/rejected. No full dark-body silhouette is invented.'
        write_wrapped(d,(12,442),caption,width=78,size=16);file=name+'-black-evidence.png';canvas.save(REVIEW/file);items.append(dict(file=file,title=name+' reflection/body evidence',caption=caption))
    save(REVIEW/'supplemental-panels.json',items)
    page=REVIEW/'index.html';s=page.read_text()
    for name in TARGETS:
        item=next(i for i in items if i['file']==name+'-focus.png')
        s=s.replace(f'<section id="{name}">',f'<section id="{name}"><a href="{item["file"]}"><img class="comparison" src="{item["file"]}" alt="{item["title"]}"></a>')
    for case in read(OUT/'cases.json'):
        name=case['name'];s=s.replace(f'<div class="native"><img src="{name}-native.png"',f'<details><summary>C: reflection and dark-body evidence separately</summary><img src="{name}-black-evidence.png" alt="{name} reflection body evidence" style="max-width:100%"></details><div class="native"><img src="{name}-native.png"')
    page.write_text(s)

if __name__=='__main__':main()

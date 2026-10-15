"""Raw/marked evidence with automatic success, typical and failure selection."""
from html import escape
from PIL import Image,ImageDraw,ImageFont
from .common import *
from .calibrate import predict
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def text(d,xy,s,size=15,fill='white'):d.text(xy,s,font=ImageFont.truetype(FONT,size),fill=fill)

def mark(d,p,origin,offset,scale,color,kind):
    x=(p[0]-origin[0]+.5)*scale+offset[0];y=(p[1]-origin[1]+.5)*scale+offset[1];r=6
    if kind=='square':d.rectangle((x-r,y-r,x+r,y+r),outline=color,width=2)
    elif kind=='circle':d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=2)
    elif kind=='cross':d.line((x-r,y-r,x+r,y+r),fill=color,width=2);d.line((x-r,y+r,x+r,y-r),fill=color,width=2)
    else:d.line((x-r,y,x+r,y),fill=color,width=2);d.line((x,y-r,x,y+r),fill=color,width=2)

def crop(native,r,label,det,models,refs):
    center=np.rint(r['old_point']).astype(int);origin=center-35;box=[*origin,*(center+36)];im=Image.fromarray(native).crop(box);im.save(REVIEW/(label+'-native.png'));s=4;side=71*s
    out=Image.new('RGB',(side*3,side+90),'#20252b');d=ImageDraw.Draw(out)
    for i,title in enumerate(('Raw photograph','Independent bright feature','Predicted / reference locations')):
        out.paste(im.resize((side,side),Image.Resampling.NEAREST),(i*side,42));text(d,(i*side+5,5),title)
    text(d,(5,side+48),f"{r['id']} | {r['color']} | {r['split']} | {r['match_status']}",14)
    text(d,(5,side+68),'White square: old peak; cyan +: independent maximum; magenta circle: patch; green +: proxy',12)
    mark(d,r['old_point'],origin,(side,42),s,'white','square')
    for hid in r['matches']:
        q=det[hid];mark(d,q['point'],origin,(side,42),s,'cyan','plus');mark(d,q['centroid'],origin,(side,42),s,'magenta','circle')
        p=np.array(q['centroid'])+models['R275/pooled/constant_patch']['coef'][0];mark(d,p,origin,(side*2,42),s,'lime','plus')
    # Available J/W references are linked by their archived cue ID, never selected
    # by nearest position or used to move the independent observation.
    mark(d,r['centroid'],origin,(side*2,42),s,'orange','cross')
    for ref,color in [('J','deepskyblue'),('W','yellow')]:
        other=refs.get((ref,r['id']))
        if other:mark(d,other['centroid'],origin,(side*2,42),s,color,'cross')
    out.save(REVIEW/(label+'.png'));return dict(name=label,id=r['id'],box=list(map(int,box)),status=r['match_status'],reference=r['reference'],matches=r['matches'])

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,rgb,_=photo();rows=read(OUT/'associations.json.gz');det={r['id']:r for r in read(OUT/'photo-landmarks.json.gz')['records']};models=read(OUT/'calibration-frozen.json')['models'];refs={(r['reference'],r['id']):r for r in rows};selected=[]
    for col in ('red','yellow'):
        rr=[r for r in rows if r['reference']=='R275' and r['color']==col and r['split']=='evaluation' and r['reliable'] and r['match_status']=='unique']
        rr.sort(key=lambda r:np.linalg.norm(predict(r,'constant_patch',models['R275/pooled/constant_patch'])-r['centroid']))
        for label,i in [('good',0),('typical',len(rr)//2),('worst',-1)]:selected.append((col+'-'+label,rr[i]))
        for status in ('multiple','missing'):
            rr=[r for r in rows if r['reference']=='R275' and r['color']==col and r['split']=='evaluation' and r['match_status']==status]
            if rr:selected.append((col+'-'+status,sorted(rr,key=lambda r:r['id'])[0]))
    for name in ('P2','P5','N11','Q14'):
        cases=[q for stage in ('development','confirmation') for q in read(ROOT/f'photo2/r288/results/{stage}.json.gz')['cases']]
        anchor=next(q['seed'] for q in cases if q['name']==name)
        rr=[r for r in rows if r['reference']=='W' and r.get('case')==name and r['old_point']==anchor]
        if rr:selected.append((name,rr[0]))
    manifest=[crop(native,r,label,det,models,refs) for label,r in selected]
    save(OUT/'review-manifest.json',manifest)
    # Overview makes geographic split and automatic example selection inspectable.
    im=Image.fromarray(native);im.thumbnail((640,800));d=ImageDraw.Draw(im);scale=im.width/native.shape[1]
    for r in rows:
        if r['reference']!='R275':continue
        x,y=np.array(r['centroid'])*scale;color={'development':'cyan','evaluation':'orange','buffer':'gray'}[r['split']];d.ellipse((x-2,y-2,x+2,y+2),fill=color)
    for label,r in selected[:10]:
        x,y=np.array(r['centroid'])*scale;text(d,(x,y),label,11)
    im.save(REVIEW/'geography.png')
    # Synthetic success/failure crops: select exact residual extremes by color.
    residual=read(OUT/'synthetic-residuals.json.gz');syn=[]
    for col in ('red','yellow','black'):
        rr=[r for r in residual if r['color']==col and r['mode']=='on' and r['target']=='physical' and r['method']=='known_specular_patch'];rr.sort(key=lambda r:r['error'])
        for label,index in [('good',0),('worst',-1)]:
            r=rr[index];folder=OUT/'synthetic'/r['scene'];data=read(folder/'evaluation.json');b=next(b for b in data['beads'] if b['owner']==r['owner']);center=np.rint(b['physical_center']).astype(int);origin=center-28;box=[*origin,*(center+29)];side=57*4
            canvas=Image.new('RGB',(side*4,side+75),'#20252b');d=ImageDraw.Draw(canvas)
            for i,(file,title) in enumerate([('on-srgb.png','Specular enabled'),('off-srgb.png','Specular disabled'),('specular.png','Isolated specular'),('on-srgb.png','Independent / truth')]):
                im=Image.open(folder/file).crop(box);canvas.paste(im.resize((side,side),Image.Resampling.NEAREST),(side*i,32));text(d,(side*i+4,5),title,14)
            m=b['measurements']['on'][0]
            for p,color,kind in [(m['point'],'cyan','plus'),(m['patch'],'magenta','circle'),(b['physical_center'],'lime','plus'),(b['visible_centroid'],'orange','cross')]:mark(d,p,origin,(side*3,32),4,color,kind)
            if b['specular']:mark(d,b['specular']['centroid'],origin,(side*2,32),4,'yellow','cross')
            if b['normal_prediction']:mark(d,b['normal_prediction']['centroid'],origin,(side*2,32),4,'cyan','circle')
            text(d,(5,side+37),f"{r['scene']} / body {r['owner']} / {col}: feature-to-predicted-specular error {r['error']:.2f}px",14)
            text(d,(5,side+57),'Last: cyan maximum, magenta patch, orange visible centroid, green physical center. No fitted pose.',12)
            name='synthetic-'+col+'-'+label;canvas.save(REVIEW/(name+'.png'));syn.append(dict(name=name,**r))
    save(OUT/'synthetic-review-manifest.json',syn)
    plot(rows,models)

def plot(rows,models):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,3,figsize=(12,3.8),layout='constrained');ev=read(OUT/'photo-evaluation.json')['scores']
    labels=['Point','Patch','+ constant','+ geography','+ patch axis','+ darkness'];methods=['raw_point','raw_patch','constant_patch','geographic','orientation','darkness']
    for col,color in [('red','#b32d25'),('yellow','#9b7800')]:
        axs[0].plot(range(6),[ev[f'R275/{col}/evaluation/{m}']['total']['rms'] for m in methods],'o-',color=color,label=col)
        rr=[r for r in rows if r['reference']=='R275' and r['color']==col and r['reliable'] and r['match_status']=='unique' and r['split']=='evaluation'];err=sorted(np.linalg.norm(predict(r,'constant_patch',models['R275/pooled/constant_patch'])-r['centroid']) for r in rr)
        axs[1].step(err,np.arange(1,len(err)+1)/len(err),where='post',label=col,color=color)
    axs[0].set(xticks=range(6),xticklabels=labels,ylabel='RMS proxy error (native px)',title='Photograph: interior reference');axs[0].tick_params(axis='x',rotation=40);axs[0].legend();axs[0].grid(alpha=.2)
    axs[1].set(xlabel='Pooled constant proxy error (px)',ylabel='Fraction of matched references',title='Failures remain in the tail',xlim=(0,14));axs[1].grid(alpha=.2)
    sy=read(OUT/'synthetic-summary.json');x=np.arange(3);emp=[];phys=[]
    for col in ('red','yellow','black'):
        p=sy['paired'][f'{col}/physical/all'];emp.append(p['empirical']['rms']);phys.append(p['known_geometry']['rms'])
    axs[2].bar(x-.16,emp,.32,label='Constant offset');axs[2].bar(x+.16,phys,.32,label='Known geometry/light');axs[2].set(xticks=x,xticklabels=['red','yellow','black'],ylabel='RMS physical-center error (px)',title='Synthetic: changed lighting');axs[2].legend(fontsize=8);axs[2].grid(axis='y',alpha=.2)
    fig.savefig(REVIEW/'comparison.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()

"""Static raw-photo evidence and all-basin geometric residual review."""
import html
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import read,save
from photo2.r313.objective import boundaries
from .run import OUT,EV

FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
def caption(im,text):
    out=Image.new('RGB',(im.width,im.height+25),'white');out.paste(im,(0,25));ImageDraw.Draw(out).text((5,4),text,font=FONT,fill='black');return out

def run():
    dest=OUT/'review';dest.mkdir(exist_ok=True);m=dict(np.load(EV/'maps.npz'));doc=read(EV/'freeze.json');summary=read(OUT/'summary.json');rows=summary['rows'];dev=[r for r in rows if r['split']=='development' and r['name'].startswith('R314')];best=min(dev,key=lambda r:max(r['vector']['worst']/3,r['vector']['seam']/10,r['vector']['external']/3))['name'];names=['R306-2405','R313-focused-1','R313-focused-3',best];names=list(dict.fromkeys(names));raw=m['native'];images={'Original':raw};origin=m['origin']
    evidence=raw.copy();evidence[m['material']]=(.65*raw[m['material']]+.35*np.array([0,255,80])).astype(np.uint8);evidence[m['paper']]=(.65*raw[m['paper']]+.35*np.array([50,120,255])).astype(np.uint8);evidence[m['edges'].any(0)]=[255,130,0];evidence[m['seams'].any(0)]=[255,255,0];im=Image.fromarray(evidence);draw=ImageDraw.Draw(im)
    for y,x,axis,sign,gap in m['external_brackets']:
        dx,dy=(sign,0) if axis==0 else (0,sign);draw.line((int(x),int(y),int(x+gap*dx),int(y+gap*dy)),fill=(0,255,255))
    images['Evidence']=np.asarray(im);Image.fromarray(raw).save(dest/'original-native.png');im.save(dest/'evidence.png')
    for name in [r['name'] for r in rows if r['split']=='development']:
        a=np.load(OUT/'models'/f'{name}.npz');edge=boundaries(a['owner'].reshape(raw.shape[:2]),a['unknown'].reshape(raw.shape[:2])).any(0);z=raw.copy();z[edge]=[0,235,240];images[name]=z;Image.fromarray(z).save(dest/f'{name}.png')
    def panel(keys,box,file,scale=2):
        ims=[]
        for k in keys:
            im=Image.fromarray(images[k]).crop(box);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);ims.append(caption(im,k))
        out=Image.new('RGB',(max(i.width for i in ims),sum(i.height for i in ims)),'white');y=0
        for im in ims:out.paste(im,(0,y));y+=im.height
        out.save(dest/file)
    panel(['Original','Evidence']+names,(0,0,raw.shape[1],raw.shape[0]),'whole-geography.png',2)
    x,y=np.rint(np.array([1499,271])-origin).astype(int);panel(['Original','Evidence']+names,(x-150,y-70,x+170,y+110),'reference-neighbors.png',3)
    d=read(OUT/'geometry-diagnostics.json.gz');models={r['name']:r for r in d['models']};cols=['Original','Evidence','R306-2405',best];core=read(OUT/'models'/f'{best}.json.gz');worst=sorted(sum([core[k]['owner_specific_cores'] for k in ['development','comparison','buffer']],[]),key=lambda r:-r['material_distance']['p95_px'])[:20];canvas=Image.new('RGB',(960,10*175),'white');draw=ImageDraw.Draw(canvas)
    for n,r in enumerate(worst):
        x,y=np.rint(np.array(r['point'])-origin).astype(int);cx=n%2*480;cy=n//2*175
        for j,key in enumerate(cols):
            im=Image.fromarray(images[key]).crop((x-30,y-30,x+30,y+30)).resize((120,120),Image.Resampling.NEAREST);canvas.paste(im,(cx+j*120,cy+20));draw.text((cx+j*120+2,cy+2),key,font=FONT,fill='black')
        draw.text((cx+2,cy+143),f"{r['id']} index {r['index']}; core p95 {r['material_distance']['p95_px']:.2f}px",font=FONT,fill='black')
    canvas.save(dest/'worst20.png')
    fig,ax=plt.subplots(2,1,figsize=(13,7),sharex=True)
    for name in ['R306-2405','R313-focused-3',best]:
        rr=sorted(models[name]['regions'],key=lambda r:r['arc']);ax[0].plot([r['arc'] for r in rr],[100*r['modal'] for r in rr],'.-',label=name,lw=.8);ax[1].plot([r['arc'] for r in rr],[100*r['fixed_R306_fraction'] for r in rr],'.-',label=name,lw=.8)
    for a in ax:a.axvline(0,color='k',lw=.5);a.axhline(80,color='gray',ls='--',lw=.5);a.set_ylim(0,105);a.grid(alpha=.2);a.legend(fontsize=9)
    ax[0].set_ylabel('Modal single-owner core %');ax[1].set_ylabel('Fixed R306-owner core %');ax[1].set_xlabel('Frozen photographic arc from reference (px); lines do not imply verified physical sequence');fig.tight_layout();fig.savefig(dest/'geographic-progression.png',dpi=150);plt.close(fig)
    from photo2.r306.evidence import load
    from .run import make
    from .diagnostics import isolated
    data,_,_=load();scene=make(core['parameters'],data);early=[r for r in models[best]['regions'] if 'isolated' in r];canvas=Image.new('RGB',(720,len(early)*215),'white');draw=ImageDraw.Draw(canvas)
    for n,r in enumerate(early):
        x,y=np.rint(r['point']).astype(int);yy,xx=np.mgrid[y-30:y+30,x-30:x+30];xy=np.c_[xx.ravel(),yy.ravel()];cx,cy=x-int(origin[0]),y-int(origin[1]);rawcrop=Image.fromarray(raw).crop((cx-30,cy-30,cx+30,cy+30));full=scene.trace(xy);modal=r['index'];bestiso=r['isolated'][0]['index'] if r['isolated'] else modal
        crops=[np.array(rawcrop)];labels=['Raw photo']
        for label,index,solo in [('Full modal',modal,False),('Isolated modal',modal,True),('Best isolated',bestiso,True)]:
            j=np.flatnonzero(scene.indices==index);im=np.array(rawcrop).copy()
            if len(j):
                tr=isolated(scene,int(j[0]),xy) if solo else full;mask=(tr['owner']>=0) if solo else (tr['owner']==j[0]);mask=mask.reshape(60,60);edge=mask&~ndi.binary_erosion(mask);im[edge]=[0,255,255]
            crops.append(im);labels.append(f'{label} {index}')
        for j,(im,label) in enumerate(zip(crops,labels)):
            canvas.paste(Image.fromarray(im).resize((180,180),Image.Resampling.NEAREST),(j*180,n*215+20));draw.text((j*180+3,n*215+2),label,font=FONT,fill='black')
        draw.text((3,n*215+201),r['id']+' — conditional owners; isolated solid rendered without neighbors',font=FONT,fill='black')
    canvas.save(dest/'isolated-versus-visible.png')
    controls=read(OUT/'controls.json')['cases'];table='<tr><th>Model / geography</th><th>Material %</th><th>Paper %</th><th>One-body %</th><th>Exterior bracket p95</th><th>Seam conflict %</th><th>Worst core p95</th><th>Accepted</th></tr>'
    for r in rows:
        if r['split']=='buffer':continue
        v=r['vector'];table+=f"<tr><td>{r['name']} / {r['split']}</td><td>{100-v['omission']:.2f}</td><td>{v['paper']:.2f}</td><td>{100-v['ownership']:.2f}</td><td>{v['external']:.2f}</td><td>{v['seam']:.2f}</td><td>{v['worst']:.2f}</td><td>{r['acceptance']['passed']}</td></tr>"
    ct=''.join(f"<li>{c['name']}: {html.escape(', '.join(c['acceptance']['failures']))}</li>" for c in controls)
    pics=['reference-neighbors.png','isolated-versus-visible.png','whole-geography.png','geographic-progression.png','worst20.png'];blocks=''.join(f'<h2>{p}</h2><a href="review/{p}"><img src="review/{p}" alt="{p}"></a>' for p in pics)
    links=''.join(f'<li><a href="review/{r["name"]}.png">{r["name"]} native overlay</a> · <a href="models/{r["name"]}.json.gz">full physical model / metrics</a></li>' for r in rows if r['split']=='development')
    (OUT/'index.html').write_text('<!doctype html><html><meta charset="utf-8"><title>R314 geometry before peak minimax</title><style>body{font:16px system-ui;max-width:1500px;margin:24px auto;padding:12px;background:#fafaf8;color:#222}img{max-width:100%}table{border-collapse:collapse}td,th{padding:7px;border:1px solid #ccc}p{max-width:1100px}</style><h1>R314 — geometry gates before peak minimax; no adoption</h1><p>Raw photograph is unchanged. Green = confident colored material; blue = confident paper; orange = persistent transitions; yellow = color-supported seams; cyan lines in Evidence = material-to-paper boundary brackets. Cyan model lines = all visible surface interfaces, including bore and occlusion edges; they are predictions, never observed black silhouettes. Physical target is exactly −100…99; all necklace bodies participate in contact and occlusion.</p><p>The illustrated R314 candidate is a diagnostic tradeoff selected by geometric violation, not an accepted reconstruction. Geographic plots use fixed photo locations. Fixed-owner plots expose reassignment. Exterior bracket p95 includes a 50px penalty for a missing boundary in the extended scan, not a measured 50px error. Comparison regions are historically exposed. Peak minimax is not claimed without convincing geometry and correspondences.</p><p><a href="../../R314_REPORT.md">Report</a> · <a href="../../R314_REPRODUCE.md">Reproduce</a> · <a href="verification.json">Independent verification</a> · <a href="controls.json">All corruption controls</a> · <a href="bright-readiness.json">Bright-feature readiness</a></p><table>'+table+'</table><ul>'+links+'</ul>'+blocks+'<h2>Deliberate prediction controls</h2><ul>'+ct+'</ul></html>')
    save(OUT/'review-selection.json',dict(illustrated=best,policy='Diagnostic maximum of exterior/seam/worst-core normalized violations; never adoption or new search. All basin overlays linked.',raw_sha_policy='Original-native PNG exactly equals frozen native pixel array'))
    print('REVIEW',best,flush=True)
if __name__=='__main__':run()

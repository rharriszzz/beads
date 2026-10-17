"""High resolution static native-photo review with geometric bore-edge separation."""
from copy import copy
from pathlib import Path
import html
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r297.geometry import reference
from .objective import boundaries
from .diagnose_geometry import make
from .review import caption,tint

OUT=ROOT/'photo2/r313/continuation';FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14);SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)

def categories(s,m,owner,unknown):
 shape=tuple(m['shape']);own=owner.reshape(shape);un=unknown.reshape(shape);edges=boundaries(own,un).any(0);holes=np.zeros(shape,bool);origin=m['origin'];h,w=shape;count=0
 for k in np.unique(own[own>=0]):
  pos=s.pc[k];rad=s.query_radius+3;lo=np.maximum([0,0],np.floor(pos-rad).astype(int));hi=np.minimum([2540,3182],np.ceil(pos+rad).astype(int)+1)
  yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xy=np.c_[xx.ravel(),yy.ravel()];iso=copy(s);iso.n=1;iso.centers=s.centers[k:k+1];iso.pc=s.pc[k:k+1];iso.tree=cKDTree(iso.pc);iso.g={key:value[k:k+1] for key,value in s.g.items()};iso.indices=s.indices[k:k+1]
  tr=iso.trace(xy);mask=(tr['owner']>=0).reshape(xx.shape);u=tr['unknown'].reshape(xx.shape);hole=ndi.binary_fill_holes(mask)&~mask&~ndi.binary_dilation(u)
  near=ndi.binary_dilation(hole);iy=yy-origin[1];ix=xx-origin[0];valid=(iy>=0)&(iy<h)&(ix>=0)&(ix<w);cy=iy[valid];cx=ix[valid];on=near[valid]&(own[cy,cx]==k)&edges[cy,cx];holes[cy[on],cx[on]]=True;count+=len(xy)
 return edges&~holes,holes,dict(isolated_native_rays=count,policy='Bore edge requires adjacency to an enclosed hole in the isolated exact annular silhouette, then visible ownership in the full necklace. Other edges include external silhouettes and occlusion boundaries; no photographed black silhouette is inferred.')

def run():
 dest=OUT/'review';dest.mkdir(exist_ok=True);m=dict(np.load(OUT.parent/'evidence/maps.npz'));doc=read(OUT.parent/'evidence/freeze.json');data,_,_=load();raw=m['native'];models={p.name.removesuffix('.json.gz'):read(p) for p in (OUT/'models').glob('*.json.gz')};names=['R297-2337','R306-2405','R309-2733','R312-best','R312-local','R313-focused-1','R313-focused-2','R313-focused-3'];images={'Original':raw};category_receipts=[]
 for name in names:
  model=models[name];a=np.load(OUT/'models'/f'{name}.npz');s=make(model['parameters'],data,model['implementation']);external,holes,receipt=categories(s,m,a['owner'],a['unknown']);near=ndi.distance_transform_edt(~m['edges'].any(0))<=8;im=raw.copy();im[external&~near]=[150,165,170];im[external&near]=[0,225,240];im[holes]=[240,80,240];images[name]=im;caption(Image.fromarray(im).resize((raw.shape[1]*2,raw.shape[0]*2),Image.Resampling.NEAREST),name).save(dest/f'{name}-boundaries.png');category_receipts.append(dict(name=name,external_edge_pixels=int(external.sum()),bore_edge_pixels=int(holes.sum()),**receipt));np.savez_compressed(dest/f'{name}-boundary-types.npz',external=external,hole=holes)
 save(OUT/'boundary-categories.json',category_receipts)
 e=tint(raw,m['material'],[30,250,80],.35);e=tint(e,m['paper'],[30,130,240],.25);e[m['edges'].any(0)]=[255,160,0];e[m['seams'].any(0)]=[255,245,0];images['Evidence']=e
 Image.fromarray(raw).save(dest/'original-native.png');caption(Image.fromarray(e).resize((raw.shape[1]*2,raw.shape[0]*2),Image.Resampling.NEAREST),'Independent evidence: green material; blue paper; orange transitions; yellow candidate seams (not verified bead identities)').save(dest/'evidence-2x.png')
 def panel(keys,box,path,scale=2):
  ims=[]
  for key in keys:
   im=Image.fromarray(images[key]).crop(box);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);ims.append(caption(im,key))
  canvas=Image.new('RGB',(max(p.width for p in ims),sum(p.height for p in ims)),'white');y=0
  for im in ims:canvas.paste(im,(0,y));y+=im.height
  canvas.save(path)
 keys=['Original','R306-2405','R313-focused-1','R313-focused-2','R313-focused-3'];panel(keys,(0,0,raw.shape[1],raw.shape[0]),dest/'whole-interval-before-after.png',2)
 anchor=np.array(data['anchor']['measured_photo_location'])-m['origin'];x,y=np.rint(anchor).astype(int);panel(keys,(x-180,y-80,x+180,y+110),dest/'reference-first40-both-directions.png',3)
 ref=reference();signed=((ref.arc-data['arc0'])*data['direction']+ref.length/2)%ref.length-ref.length/2
 for direction in [-1,1]:
  pts=ref.points[(signed*direction>=0)&(signed*direction<=170)]-m['origin'];lo=np.floor(pts.min(0)-55).astype(int);hi=np.ceil(pts.max(0)+55).astype(int);panel(keys,(*lo,*hi),dest/('negative-first40-context.png' if direction<0 else 'positive-first40-context.png'),3)
 # Strongly exposed examples selected only by frozen photographic core area.
 exposed=sorted(doc['regions'],key=lambda r:-r['pixels'])[:8]
 def atlas(rows,path,kind):
  cardw,cardh=480,180;cols=2;canvas=Image.new('RGB',(cols*cardw,((len(rows)+cols-1)//cols)*cardh),'#fafafa');draw=ImageDraw.Draw(canvas)
  for n,r in enumerate(rows):
   xx,yy=np.rint(np.array(r['point'])-m['origin']).astype(int);box=(xx-30,yy-30,xx+30,yy+30);cx=(n%cols)*cardw;cy=(n//cols)*cardh
   for j,key in enumerate(['Original','Evidence','R306-2405','R313-focused-1']):
    im=Image.fromarray(images[key]).crop(box).resize((120,120),Image.Resampling.NEAREST);canvas.paste(im,(cx+j*120,cy+18));draw.text((cx+j*120+2,cy+2),['Original','Evidence','R306','R313'][j],font=SMALL,fill='black')
   if kind=='worst':
    d=r['material_distance'];t=r['owner_specific_exterior_transition'];line=f"{r['id']} ({r['point'][0]:.0f},{r['point'][1]:.0f})  index {r['index']}";line2=f"Core miss p95/max {d['p95_px']:.1f}/{d['max_px']:.1f}px; rim p95 {t['p95_px'] or 0:.1f}px"
   else:line=f"{r['id']} ({r['point'][0]:.0f},{r['point'][1]:.0f})";line2=f"{r['pixels']} frozen pigment core pixels; complete contour unknown"
   draw.text((cx+4,cy+141),line,font=SMALL,fill='black');draw.text((cx+4,cy+157),line2,font=SMALL,fill='black')
  canvas.save(path)
 atlas(exposed,dest/'exposed-beads-before-after.png','exposed')
 best=models['R313-focused-1'];cores=sum([best[s].get('owner_specific_cores',[]) for s in ['development','comparison','buffer'] if s in best],[])
 worst=sorted(cores,key=lambda r:-(r['material_distance']['p95_px']+(r['owner_specific_exterior_transition']['p95_px'] or 0)/2))[:20];save(OUT/'worst20.json',worst);atlas(worst,dest/'worst20-geometric-mismatches.png','worst')
 fig,axes=plt.subplots(2,2,figsize=(13,7),sharey='row')
 for name,color in [('R306-2405','#777777'),('R313-focused-1','#0077bb'),('R313-focused-3','#bb6600')]:
  row=models[name];rr=sum([row[s].get('owner_specific_cores',[]) for s in ['development','comparison','buffer'] if s in row],[]);rr=[r for r in rr if r['index'] is not None]
  for j,lim in enumerate([(-100,99),(-40,40)]):
   axes[0,j].scatter([r['index'] for r in rr],[r['material_distance']['p95_px'] for r in rr],c=color,label=name,s=16)
   ee=[r for r in rr if r['owner_specific_exterior_transition']['p95_px'] is not None];axes[1,j].scatter([r['index'] for r in ee],[r['owner_specific_exterior_transition']['p95_px'] for r in ee],c=color,label=name,s=16)
   for ax in axes[:,j]:ax.set_xlim(lim);ax.axvline(0,c='k',lw=.6);ax.grid(alpha=.2);ax.legend(fontsize=8);ax.set_xlabel('Conditional modal physical index; missing samples are unmeasured')
 axes[0,0].set_ylabel('Core-to-one-visible-body p95 distance (px)');axes[1,0].set_ylabel('Owner-specific exterior transition p95 (px)');fig.suptitle('Individual material/transition errors; photographic regions fixed, physical assignments conditional');fig.tight_layout();fig.savefig(dest/'index-errors.png',dpi=160);plt.close(fig)
 table=read(OUT/'summary-table.json');headers='<tr><th>Model / set</th><th>Score</th><th>Material explained</th><th>Paper intrusion</th><th>One-body core</th><th>Transition p95 / max</th><th>Worst core p95</th></tr>';body=''
 for r in table:
  body+=f"<tr><td>{r['name']} / {r['split']}</td><td>{r['score']:.3f}</td><td>{r['explained_percent']:.1f}%</td><td>{r['paper_percent']:.2f}%</td><td>{r['core_one_owner_percent']:.1f}%</td><td>{r['transition_p95']:.1f} / {r['transition_max']:.1f}px</td><td>{r['owner_specific']['worst_core_p95_px']:.1f}px</td></tr>"
 pics=[f'{name}-boundaries.png' for name in names[:5]]+['original-native.png','evidence-2x.png','whole-interval-before-after.png','reference-first40-both-directions.png','negative-first40-context.png','positive-first40-context.png','exposed-beads-before-after.png','worst20-geometric-mismatches.png','index-errors.png']
 blocks=''.join(f'<h2>{p}</h2><a href="review/{p}"><img src="review/{p}" alt="{p}"></a>' for p in pics)
 (OUT/'index.html').write_text('<!doctype html><html><meta charset="utf-8"><title>R313 geometric diagnosis</title><style>body{font:16px system-ui;max-width:1500px;margin:24px auto;padding:12px;background:#fafaf8;color:#222}img{max-width:100%}table{border-collapse:collapse}td,th{padding:7px;border:1px solid #ccc}p{max-width:1100px}</style><h1>R313 — geometric diagnosis; experimental candidates, no adoption</h1><p>Click any image for its full-resolution PNG. Raw panels are unchanged native photographic pixels. Cyan: visible outer/occlusion edges near photographic transition support; gray: unsupported outer/occlusion edges; purple: visible bore boundaries established by isolated physical rendering. Orange/yellow photographic transitions are local evidence, not certified complete bead contours. Candidate dark seams are not independently verified physical separations. No black photographic silhouettes were inferred.</p><p>Exactly −100…99 target bodies; complete necklace occlusion/contact. First-40 crops show photographic context; labels and physical identities remain conditional. Material distances measure failure to cover a known interior, not an invented complete photographic contour. Comparison and buffer regions are historically exposed and were excluded from fitting.</p><p><a href="../../R313_REPORT.md">Report</a> · <a href="../../R313_REPRODUCE.md">Reproduction</a> · <a href="verification.json">Verification</a> · <a href="worst20.json">Worst 20 numerical records</a></p><table>'+headers+body+'</table>'+blocks+'</html>')
 print('Static review',OUT/'index.html',flush=True)
if __name__=='__main__':run()

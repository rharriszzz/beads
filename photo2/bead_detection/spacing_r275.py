"""Reference arclength angles and photographic gap flags, never predicted beads."""
import json,csv
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
from .centerline_r275 import ROOT,OUT,Band,save
from .review_r275 import panel,textfont,points

def projection(points,curve):
 # Nearest continuous line-segment projection, not nearest vertex.
 p=np.asarray(points,float);a=np.asarray(curve,float);b=np.roll(a,-1,axis=0);v=b-a;length=np.linalg.norm(v,axis=1);arc=np.r_[0,np.cumsum(length)];tree=cKDTree(a);_,idx=tree.query(p);result=[]
 for q,k in zip(p,np.atleast_1d(idx)):
  js=np.array([(int(k)+d)%len(a) for d in (-2,-1,0,1)]);t=np.clip(np.sum((q-a[js])*v[js],axis=1)/np.maximum(length[js]**2,1e-12),0,1);foot=a[js]+t[:,None]*v[js];j=int(np.argmin(np.linalg.norm(foot-q,axis=1)));index=js[j];s=float((arc[index]+t[j]*length[index])%arc[-1]);result.append(dict(arc_px=s,angle_degrees=360*s/arc[-1],distance=float(np.linalg.norm(foot[j]-q)),foot=foot[j].tolist(),signed_distance=float((v[index,0]*(q-foot[j])[1]-v[index,1]*(q-foot[j])[0])/max(length[index],1e-12))))
 return result,float(arc[-1])
def circular_intervals(rows,length):
 order=sorted(rows,key=lambda r:(r['angle_degrees'],r['id']));out=[]
 for i,r in enumerate(order):
  after=order[(i+1)%len(order)];delta=(after['arc_px']-r['arc_px'])%length
  if len(order)==1:delta=length
  out.append(dict(id=r['id'],next_id=after['id'],arc_px=r['arc_px'],angle_degrees=r['angle_degrees'],step_pixels=delta,step_degrees=delta/length*360))
 return out

def main():
 data=json.loads((OUT/'inventory.json').read_text());old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());band=Band();im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');summary={};allrows=[];selected_gaps=[]
 for name,inv in [('r274',old),('r275',data)]:
  regionmap={r['id']:r for r in inv['beads']};ps,length=projection([points(l) for l in inv['locations']],band.points);rows=[]
  for l,p in zip(inv['locations'],ps):
   r=regionmap.get(l['id']);membership=band.qualifies(points(l),r['region'] if r else None)
   if not membership['in_band']:continue
   crossed=bool(r and membership['region_distance']<=.75)
   rows.append(dict(id=l['id'],color=l['color'],point=points(l),measured_support_crosses=crossed,central_anchor=p['distance']<=14,**p))
  sets={'whole-target':rows,'central-anchors':[r for r in rows if r['central_anchor']],'measured-crossings':[r for r in rows if r['measured_support_crosses']]};summary[name]={}
  for kind,members in sets.items():
   gaps=circular_intervals(members,length);steps=np.array([r['step_pixels'] for r in gaps]);med=float(np.median(steps));q1,q3=np.percentile(steps,[25,75]);threshold=float(max(2*med,q3+1.5*(q3-q1)))
   flagged=[dict(g,threshold=threshold) for g in gaps if g['step_pixels']>threshold]
   summary[name][kind]=dict(count=len(members),total_length=length,median_step_pixels=med,median_step_degrees=med/length*360,minimum_step_pixels=float(steps.min()),maximum_step_pixels=float(steps.max()),coefficient_of_variation=float(steps.std()/steps.mean()),large_gap_threshold_pixels=threshold,large_gaps=flagged)
   allrows.extend(dict(version=name,subset=kind,**g) for g in gaps)
   if name=='r275' and kind=='whole-target':selected_gaps=sorted(flagged,key=lambda r:-r['step_pixels'])
  if name=='r275':save('angular-locations.json',rows)
 save('spacing.json',dict(definition='theta=360*s/L along existing unregistered image-derived closed reference; zero at first saved sample; orientation follows saved curve. Not physical 3D angle. A measured small support crossing is not a complete visible-body crossing census.',summary=summary))
 with (OUT/'angular-increments.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');w.writeheader();w.writerows(allrows)
 # Every flagged final target gap gets a raw/overlay photograph, with ends only.
 for i,g in enumerate(selected_gaps,1):
  s=(g['arc_px']+g['step_pixels']/2)%length;a=np.r_[0,np.cumsum(np.linalg.norm(np.diff(band.points,axis=0),axis=1))];k=min(len(a)-1,np.searchsorted(a,s));x,y=band.points[k];box=[int(x)-75,int(y)-75,int(x)+75,int(y)+75];loc=[l for l in data['locations'] if l['id'] in (g['id'],g['next_id'])];sheet=Image.new('RGB',(910,480),'white');sheet.paste(im.crop(box).resize((450,450),Image.Resampling.NEAREST),(0,30));sheet.paste(panel(im,box,loc,data['beads'],curve=band.points),(460,30));ImageDraw.Draw(sheet).text((5,5),f"Gap {i}: {g['step_pixels']:.1f}px / {g['step_degrees']:.3f} degrees; photo evidence required",fill='black',font=textfont());sheet.save(OUT/f'gap-{i:02d}.png');g['box']=box;g['image']=f'gap-{i:02d}.png'
 save('gap-review.json',selected_gaps)
 # Shareable standard plot, no inferred sites.
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,1,figsize=(12,8),sharex=True)
 for ax,kind in zip(axes,('whole-target','central-anchors','measured-crossings')):
  for version,col in [('r274','#888888'),('r275','#008b9a')]:
   rr=[r for r in allrows if r['version']==version and r['subset']==kind];ax.plot([r['angle_degrees'] for r in rr],[r['step_degrees'] for r in rr],'.',ms=3,label=version,color=col)
  ax.set_ylabel('Next step (degrees)');ax.set_title(kind);ax.legend();ax.grid(alpha=.2)
 axes[-1].set_xlabel('Progress along saved centerline (degrees)');fig.tight_layout();fig.savefig(OUT/'angular-spacing.png',dpi=150);plt.close(fig)
 print({k:{s:(v['count'],len(v['large_gaps']),round(v['maximum_step_pixels'],2)) for s,v in d.items()} for k,d in summary.items()})
if __name__=='__main__':main()

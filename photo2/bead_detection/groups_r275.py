"""Maker's alternating pair/single observation used for audit, not detection input."""
import json,csv
import numpy as np
from .centerline_r275 import OUT,save

def stations(rows,length,tolerance,central_tolerance):
 """Pair opposite-side anchors only; never infer missing members or chain groups."""
 pairs=[]
 for i,a in enumerate(rows):
  for j in range(i+1,len(rows)):
   b=rows[j];d=abs(a['arc_px']-b['arc_px']);d=min(d,length-d)
   if a['signed_distance']*b['signed_distance']<0 and min(abs(a['signed_distance']),abs(b['signed_distance']))>central_tolerance and d<=tolerance:pairs.append((d,a['id'],b['id'],i,j))
 used=set();groups=[]
 for d,_,__,i,j in sorted(pairs):
  if i in used or j in used:continue
  a,b=rows[i],rows[j];delta=(b['arc_px']-a['arc_px']+length/2)%length-length/2;s=(a['arc_px']+delta/2)%length;groups.append(dict(ids=[a['id'],b['id']],members=2,arc_px=s,angle_degrees=s/length*360,within_pair_pixels=d));used.update((i,j))
 for i,r in enumerate(rows):
  if i not in used:groups.append(dict(ids=[r['id']],members=1,arc_px=r['arc_px'],angle_degrees=r['angle_degrees'],within_pair_pixels=0.))
 groups.sort(key=lambda r:(r['arc_px'],r['ids']));steps=[(groups[(i+1)%len(groups)]['arc_px']-g['arc_px'])%length for i,g in enumerate(groups)]
 for i,g in enumerate(groups):
  # Leave the evaluated gap out of its 20-neighbor reference.
  local=[steps[(i+j)%len(steps)] for j in range(-10,11) if j];median=float(np.median(local));g.update(station=i+1,next_station=(i+1)%len(groups)+1,step_pixels=steps[i],step_degrees=steps[i]/length*360,local_median_pixels=median,gap_ratio=steps[i]/max(median,1e-8),gap_flag=bool(steps[i]>1.6*median and steps[i]>2*tolerance),short_flag=bool(steps[i]<.40*median))
 return groups

def main():
 data=json.loads((OUT/'inventory.json').read_text());rows=json.loads((OUT/'angular-locations.json').read_text());length=json.loads((OUT/'spacing.json').read_text())['summary']['r275']['whole-target']['total_length'];member_ids={r['id'] for r in rows};areas=[b['region']['pixel_count'] for b in data['beads'] if b['id'] in member_ids and b['color']!='black'];diam=float(np.median(np.sqrt(4*np.array(areas)/np.pi)));tol=.5*diam;center=.15*diam;groups=stations(rows,length,tol,center);controls={}
 for factor in (.75,1.,1.25):
  gg=stations(rows,length,tol*factor,center);controls[str(factor)]=dict(stations=len(gg),pairs=sum(g['members']==2 for g in gg),flagged_gaps=sum(g['gap_flag'] for g in gg))
 # Save every atypical long/short group interval for direct photographic audit.
 from .centerline_r275 import ROOT,Band
 from .review_r275 import panel,textfont
 from PIL import Image,ImageDraw
 band=Band();im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(band.points,axis=0),axis=1))];flags=[]
 for g in groups:
  if not(g['gap_flag'] or g['short_flag']):continue
  s=(g['arc_px']+.5*g['step_pixels'])%length;k=min(len(arc)-1,np.searchsorted(arc,s));x,y=band.points[k];box=[int(x)-60,int(y)-60,int(x)+60,int(y)+60];sheet=Image.new('RGB',(730,390),'white');sheet.paste(im.crop(box).resize((360,360),Image.Resampling.NEAREST),(0,30));sheet.paste(panel(im,box,data['locations'],data['beads'],labels=False,curve=band.points),(370,30));label='long' if g['gap_flag'] else 'short';ImageDraw.Draw(sheet).text((5,5),f"Group {g['station']}: {label} interval, {g['step_pixels']:.1f}px, local ratio {g['gap_ratio']:.2f}",fill='black',font=textfont());file=f'group-{label}-{g["station"]:03d}.png';sheet.save(OUT/file);flags.append(dict(**g,image=file,box=box))
 save('group-flags.json',flags)
 save('stations.json',dict(maker_observation='Two near-centerline beads alternate with one crossing, transitioning to stretches of single crossings and back. This is expected appearance, not a required detection count or inferred string indexing.',rule='Greedy shortest along-reference pair separation, opposite signed offsets, noncentral anchors, at most two per station, no chaining. Single/double stations are diagnostic associations, not confirmed bead rows.',colored_equivalent_diameter_pixels=diam,pair_tolerance_pixels=tol,central_tolerance_pixels=center,length=length,groups=groups,sensitivity=controls))
 with (OUT/'station-increments.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(groups[0]),lineterminator='\n');w.writeheader();w.writerows(groups)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,1,figsize=(14,9),sharex=True)
 for c,col in [('red','#bd3636'),('yellow','#ab8b00'),('black','#333333')]:
  rr=[r for r in rows if r['color']==c];axes[0].scatter([r['angle_degrees'] for r in rr],[r['signed_distance'] for r in rr],s=12,c=col,label=c)
 axes[0].axhline(0,color='cyan',lw=1);axes[0].set_ylabel('Signed offset (native px)');axes[0].legend(ncol=3)
 axes[1].scatter([g['angle_degrees'] for g in groups],[g['members'] for g in groups],s=8);axes[1].set_yticks([1,2]);axes[1].set_ylabel('Observed group size')
 axes[2].scatter([g['angle_degrees'] for g in groups],[g['step_degrees'] for g in groups],s=10,c=['#e87500' if g['gap_flag'] else '#008b9a' for g in groups]);axes[2].set_ylabel('Next group step (degrees)');axes[2].set_xlabel('Progress along saved reference (degrees)')
 for ax in axes:ax.grid(alpha=.2)
 fig.suptitle('Single/double grouping is a diagnostic; no missing positions are generated');fig.tight_layout();fig.savefig(OUT/'single-double-spacing.png',dpi=160);plt.close(fig);print(controls)
if __name__=='__main__':main()

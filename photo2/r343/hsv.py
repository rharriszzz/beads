"""Joint HSV of individually identified native glass pixels; no pigment classifier."""
from common import *
from glass_regions import REGIONS,DEFERRED,POLICY
from sample import interior_patch,inside_polygon
from scipy.ndimage import distance_transform_edt
from matplotlib.colors import rgb_to_hsv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.hashsalt']='beads-r343'
from matplotlib.lines import Line2D

def main():
 g,obs,co,rgb,auth,extra=load();allobs=dict(obs,**extra);old={r['id']:r['measurement'] for r in read(ROOT/'photo2/r342/classification.json.gz')['records']};old[C62]=next(r['measurement'] for r in read(ROOT/'photo2/r342/candidate-checks.json')['records'] if r['id']==C62);records=[];points=[];comparisons=[];photo=Image.fromarray(rgb)
 for o,poly in REGIONS.items():
  m=interior_patch(poly);assert m is not None,o;mask,xx,yy=inside_polygon(poly);fullmask=mask.copy();mask&=distance_transform_edt(mask)>=2;aa=np.c_[xx[mask],yy[mask]];pixels=rgb[aa[:,1],aa[:,0]];hsv=rgb_to_hsv(pixels/255.);hsv[:,0]=(hsv[:,0]*360+180)%360-180;color='yellow' if o in [Q101,C62] else allobs[o]['color'];category=authority(o,auth);assert o not in auth or color==auth[o]['color'];rows=[]
  for (x,y),rr,v in zip(aa,pixels,hsv):
   row=dict(id=o,xy=[int(x),int(y)],RGB=rr.tolist(),H=float(v[0]),S=float(v[1]),V=float(v[2]),hue_interpretable=bool(v[1]>=.3 and v[2]>=.2),recorded_pigment=color,authority=category,active=o in obs,individually_confirmed=category=='explicit_individual_pigment');rows.append(row);points.append(row)
  valid=[r for r in rows if r['hue_interpretable']];bins=[]
  for lo in np.arange(.2,1.,.1):
   pp=[r for r in valid if min(int(r['V']*10),9)==int(round(lo*10))]
   if len(pp)>=5:bins.append(dict(V_bin=[float(lo),float(lo+.1)],n=len(pp),H_median=float(np.median([r['H'] for r in pp])),S_median=float(np.median([r['S'] for r in pp])),V_median=float(np.median([r['V'] for r in pp]))))
  def summary(rr):return {c:[float(np.min([r[c] for r in rr])),float(np.median([r[c] for r in rr])),float(np.max([r[c] for r in rr]))] for c in ['H','S','V']} if rr else None
  def inspect_box(box):
   a,b,c,d=box;rgbpatch=rgb[b:d,a:c];v=rgb_to_hsv(rgbpatch/255.);h=(v[:,:,0]*360+180)%360-180;fullcore=set(map(tuple,np.c_[xx[fullmask],yy[fullmask]]));owned=sum((x,y) in fullcore for y in range(b,d) for x in range(a,c));return dict(patch_box=box,RGB=rgbpatch.tolist(),HSV=np.stack([h,v[:,:,1],v[:,:,2]],axis=-1).tolist(),pixels_in_conservative_core=owned,core_contains_entire_patch=owned==9,interpretation='Core containment certifies the reference pixels only. Outside this conservative core is unverified, not automatically background or a classification error.')
  x,y=np.rint(allobs[o]['xy']).astype(int);methods={'R342_darkest':inspect_box(old[o]['patch_box']) if o in old else None,'source_center':inspect_box([int(x-1),int(y-1),int(x+2),int(y+2)]),'core_clearance':inspect_box(m['patch_box'])};comparison=dict(id=o,recorded_pigment=color,authority=category,methods=methods,R342_window=old.get(o),R342_hue_feature='R342 used median hue over the WHOLE9x9, not only the selected darkest3x3; a different contaminating region. The old3x3 darkness test is preserved unchanged.');comparisons.append(comparison);record=dict(id=o,xy=allobs[o]['xy'],polygon=poly,recorded_pigment=color,authority=category,individually_confirmed=category=='explicit_individual_pigment',active=o in obs,annotated_core_pixels=int(fullmask.sum()),core_pixels=len(rows),plot_clearance_px=2,interpretable_pixels=len(valid),summary=summary(valid),observed_V_bins=bins,selected_patch=m,photographic_selection='Manually delimited visible glass core; automatic max-clearance patch inside it. No autonomous segmentation or ground-truth claim for inherited labels.');records.append(record)
 # Illustrate original, old extremum, source-centered and clearance regions.
 for start in range(0,len(comparisons),4):
  board=Image.new('RGB',(1380,400*min(4,len(comparisons)-start)),'white');d=ImageDraw.Draw(board)
  for j,r in enumerate(comparisons[start:start+4]):
   o=r['id'];x,y=np.rint(allobs[o]['xy']).astype(int);box=[int(x-22),int(y-22),int(x+23),int(y+23)];raw=photo.crop(box).resize((315,315),Image.Resampling.NEAREST);oy=j*400
   for i,(name,m) in enumerate([('Original',None)]+list(r['methods'].items())):
    im=raw.copy();dd=ImageDraw.Draw(im)
    if name=='R342_darkest' and o in old:
     pixels=np.array(old[o]['region_pixels']);a,b=pixels.min(0);c,e=pixels.max(0)+1;dd.rectangle(((a-box[0])*7,(b-box[1])*7,(c-box[0])*7-1,(e-box[1])*7-1),outline='orange',width=2)
    if name!='Original':dd.line([((px-box[0])*7,(py-box[1])*7) for px,py in REGIONS[o]+[REGIONS[o][0]]],fill='lime',width=2)
    if m:
     a,b,c,e=m['patch_box'];dd.rectangle(((a-box[0])*7,(b-box[1])*7,(c-box[0])*7-1,(e-box[1])*7-1),outline='magenta' if name=='R342_darkest' else 'cyan',width=2)
    board.paste(im,(i*345,oy+50));d.text((i*345,oy+20),name+(' core pixels '+str(m['pixels_in_conservative_core'])+'/9' if m else ''),fill='black')
   d.text((0,oy),o+' '+r['authority']+'; '+r['recorded_pigment'],fill='black')
  board.save(OUT/f'sampling-{start//4+1:02d}.png')
  if start==0:board.crop((0,0,1380,800)).save(OUT/'sampling-Q101-C62.png')
 save(OUT/'glass-regions.json',dict(records=records,deferred=DEFERRED,annotation_policy=POLICY,source_program_sha256=sha(ROOT/'photo2/r343/glass_regions.py')));save(OUT/'source-pixels.json.gz',dict(points=points,geometric_clearance_px=2,filter=dict(S_min=.3,V_min=.2,meaning='Hue reliability display filter, not a pigment separator. Low-S/V actual pixels retained but excluded from hue interpretation.'),black_detector_used=False));save(OUT/'sampling-comparison.json',dict(records=comparisons,method='Maximum geometric clearance inside a manually inspected material core. This improves curated sampling and is not an autonomous global body finder.',parameters=dict(patch=3,minimum_clearance=2),ownership_metrics_not_blind_accuracy=True))
 reliable=[r for r in points if r['hue_interpretable']];fig,ax=plt.subplots(figsize=(11,6));cm=plt.get_cmap('viridis');norm=plt.Normalize(.3,1.)
 for category in ['software_native_label','illustration_approval','explicit_individual_pigment']:
  for color,marker in [('red','o'),('yellow','^')]:
   rr=[r for r in reliable if r['authority']==category and r['recorded_pigment']==color]
   if not rr:continue
   ax.scatter([r['H'] for r in rr],[r['V'] for r in rr],c=[r['S'] for r in rr],cmap=cm,norm=norm,marker=marker,s=24 if category=='explicit_individual_pigment' else 13,alpha=.85 if category=='explicit_individual_pigment' else .36,edgecolors='black' if category=='explicit_individual_pigment' else '#999' if category=='illustration_approval' else 'none',linewidths=.4)
 for o in [Q101,C62,'NEW-1927-2829','REC266-P146299','NEW-1519-2976']:
  rr=[r for r in reliable if r['id']==o];x=float(np.median([r['H'] for r in rr]));y=float(np.median([r['V'] for r in rr]));ax.annotate(o,(x,y),xytext=(x+3,y+(.05 if o not in [C62,'NEW-1927-2829'] else -.09)),fontsize=8,arrowprops=dict(arrowstyle='-',color='gray'))
 fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),ax=ax,label='Saturation S (marker fill)');ax.set(xlabel='Native-pixel hue H (degrees; red at0)',ylabel='Native-pixel value V = max(R,G,B)/255',title='Actual visible colored glass: H–V scatter, saturation in marker fill',xlim=(-30,55),ylim=(.2,1.02));ax.grid(alpha=.2);handles=[Line2D([],[],marker='o',ls='',color='gray',label='Recorded red'),Line2D([],[],marker='^',ls='',color='gray',label='Recorded yellow'),Line2D([],[],marker='o',ls='',markerfacecolor='white',markeredgecolor='black',label='Explicit individual maker pigment'),Line2D([],[],marker='o',ls='',alpha=.45,color='gray',label='Illustration approval /native software label')];ax.legend(handles=handles,loc='upper left',fontsize=8);fig.tight_layout();fig.savefig(OUT/'HSV-HV.png',dpi=160);fig.savefig(OUT/'HSV-HV.svg',metadata={'Date':None});plt.close(fig)
 svg=OUT/'HSV-HV.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
 # Complementary H–S view: actual pixels colored by value.
 fig,ax=plt.subplots(figsize=(10,5))
 for color,marker in [('red','o'),('yellow','^')]:
  rr=[r for r in reliable if r['recorded_pigment']==color];sc=ax.scatter([r['H'] for r in rr],[r['S'] for r in rr],c=[r['V'] for r in rr],cmap='plasma',vmin=.2,vmax=1,marker=marker,s=13,alpha=.55)
 fig.colorbar(sc,ax=ax,label='Value V');ax.set(xlabel='Hue H (degrees)',ylabel='Saturation S',title='Complementary genuine-glass H–S view; circles recordedR, triangles recordedY',xlim=(-30,55));fig.tight_layout();fig.savefig(OUT/'HSV-HS.png',dpi=160);plt.close(fig)
 summary=dict(beads=len(records),pixels=len(points),hue_interpretable=len(reliable),low_SV_excluded=len(points)-len(reliable),authority_beads=dict(Counter(r['authority'] for r in records)),explicit_ids=[r['id'] for r in records if r['individually_confirmed']],all_software_labels_remain_hypotheses=True,selected_core_pixels={name:dict(certified=sum(r['methods'][name] is not None and r['methods'][name]['core_contains_entire_patch'] for r in comparisons),n=sum(r['methods'][name] is not None for r in comparisons)) for name in ['R342_darkest','source_center','core_clearance']},limits='Spatial illumination variation in one photograph, not controlled relighting. Correlated pixels are not independent beads. No fitted illumination law or complete automatic pigment classifier.');save(OUT/'HSV-summary.json',summary)
 print(summary)
 for r in records:
  if r['id'] in [Q101,C62,'NEW-1927-2829','REC266-P146299','NEW-1519-2976','R332-R-0125-0118']:print(r['id'],r['summary'],r['observed_V_bins'])
if __name__=='__main__':main()

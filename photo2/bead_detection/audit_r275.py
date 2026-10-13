"""Complete computational audit. Physical identities are not inferred from counts."""
import json,csv,hashlib
from collections import Counter
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageDraw
from .centerline_r275 import ROOT,OUT,Band,save,load_rows
from .review_r275 import panel,textfont,points
from .interiors_r273 import pixels

def main():
 data=json.loads((OUT/'inventory.json').read_text());old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());oldids={l['id'] for l in old['locations']};oldregions={b['id'] for b in old['beads']};regions={b['id']:b for b in data['beads']};band=Band();angles={r['id']:r for r in json.loads((OUT/'angular-locations.json').read_text())};increments=list(csv.DictReader((OUT/'angular-increments.csv').open()));nextstep={r['id']:float(r['step_degrees']) for r in increments if r['version']=='r275' and r['subset']=='whole-target'};locations=data['locations'];target=[]
 for l in locations:
  r=regions.get(l['id']);membership=band.qualifies(points(l),r['region'] if r else None);l['centerline_near']=membership
  if not membership['in_band']:continue
  l['audit_status']='accepted by image checks' if l['id'] in oldids else 'recovered missing candidate'
  if l['id'] in oldids and l['id'] not in oldregions and r:l['audit_status']='corrected interior'
  if l['id'] in {c['id'] for c in data.get('color_corrections',[])}:l['audit_status']='corrected color and location'
  l['angular']=angles[l['id']];l['next_step_degrees']=nextstep[l['id']];l['audit_warnings']=[]
  if r and r['color']!='black' and r['region']['pixel_count']<45:l['audit_warnings'].append('Small colored support; location retained separately from extent confidence.')
  target.append(l)
 # Close same-color pairs are doubts for photographic review, not forced merges.
 xy=np.array([points(l) for l in target]);pairs=[]
 for i,j in sorted(cKDTree(xy).query_pairs(16)):
  a,b=target[i],target[j]
  if a['color']!=b['color']:continue
  separation=float(np.linalg.norm(xy[i]-xy[j]));note='Close same-color locations; distinct native masks do not alone prove separate physical beads.'
  for l in (a,b):l['audit_warnings'].append(note)
  pairs.append(dict(a=a['id'],b=b['id'],color=a['color'],distance=separation,note=note))
 decisions=[]
 for name in ('layered-fallback','black-0.40','pale','ownership','material-0.25','connected','core','homogeneous','reflection-0.70-tinted','dim'):decisions+=load_rows(OUT/(name+'-decisions.jsonl.gz')) if (OUT/(name+'-decisions.jsonl.gz')).exists() else []
 # Resolve aliases of already diagnosed secondary peaks across measurement windows.
 resolved_peaks=[r for r in decisions if r.get('status')=='duplicate removed']
 resolved_peaks += [dict(id=r['id'],anchor=[r['brightest']['x'],r['brightest']['y']],color=r['color'],status='duplicate removed') for r in data.get('suppressed_beads',[])]
 resolved_by_color={c:[r for r in resolved_peaks if r.get('color')==c] for c in ('red','yellow','black')}
 resolved_trees={c:cKDTree([r['anchor'] for r in rows]) for c,rows in resolved_by_color.items() if rows}
 # Visible-support audit shortlist; every raw rejection remains in full traces.
 uncertain=[];allxy=np.array([points(l) for l in locations]);taken=[];accepted_pixels=set().union(*(pixels(r) for r in data['beads']));associated_rejections=[]
 for r in sorted(decisions,key=lambda r:-r.get('source_maximum',{}).get('score',r.get('brightest',{}).get('luminance',0))):
  if r.get('accepted') or r.get('status') in ('duplicate removed','outside target','previous support preserved'):continue
  p=r['anchor'];reg=r.get('region');peak=r.get('brightest');membership=band.qualifies([peak['x'],peak['y']] if peak else p,reg)
  if not membership['in_band'] or np.linalg.norm(allxy-p,axis=1).min()<8:continue
  if any((p[0]+dx,p[1]+dy) in accepted_pixels for dx in (-1,0,1) for dy in (-1,0,1)):
   associated_rejections.append(dict(id=r['id'],anchor=p,reason='Maximum lies inside or immediately against an already accepted support; retain as diagnostic, not an independent missing-bead claim.'));continue
  color=r.get('color');aliases=[resolved_by_color[color][i]['id'] for i in sorted(resolved_trees[color].query_ball_point(p,3))] if color in resolved_trees else []
  if aliases:
   associated_rejections.append(dict(id=r['id'],anchor=p,reason='Same native peak neighborhood as an already resolved secondary/contained maximum.',resolved_aliases=aliases));continue
  f=r.get('color_evidence') or {};c=r.get('confidence',{});evidence=(f.get('color_samples',0)>=20 and (f.get('hue_deviation90') or 180)<=25 and f.get('colored_core_fraction',0)>=.25) or (r.get('dark_perimeter',{}).get('closed') and r.get('dark_perimeter',{}).get('core_pixels',10000)<=220 and c.get('chromatic_core_fraction',1)<.5 and c.get('dark_neutral_shell_fraction',0)>=.35)
  if not evidence:continue
  if any(np.linalg.norm(np.array(p)-q)<8 for q in taken):continue
  taken.append(p);uncertain.append(dict(id=r['id'],anchor=p,color=r.get('color'),centerline_near=True,reasons=r['reasons'],explanations=['Unresolved image-only proposal: '+', '.join(r['reasons'])],evidence=f or c,source_status=r.get('status'),status='still unresolved',region_pixels=reg['pixel_count'] if reg else 0))
 for i,l in enumerate(sorted(target,key=lambda l:(l['point']['y'],l['point']['x'],l['id'])),1):l['audit_number']=i
 for i,r in enumerate(uncertain,1):r['audit_number']='U'+str(i)
 data['uncertain']=[deepcopy(r) for r in old['uncertain'] if r['id'] not in {l['id'] for l in locations}]+uncertain+[dict(id=l['id'],anchor=[l['point']['x'],l['point']['y']],color=l['color'],centerline_near=True,reasons=['strong-neighbor-dominance'],explanations=['Suppressed/deferred after a much stronger close same-color support was found; full evidence and measurements retained.']) for l in data.get('suppressed_locations',[])];data['centerline']=dict(points=band.points[::8].tolist(),band_half_width=12,point_reach=26,role='Existing unregistered image-derived reference only');data['beads']=[{k:v for k,v in r.items() if k not in ('direction_stops','supported_region','r272_measurements')} for r in data['beads']];save('inventory.json',data);(OUT/'inventory.js').write_text('window.BEAD_INVENTORY='+json.dumps(data,separators=(',',':'))+';\n');save('target-locations.json',target);save('unresolved-candidates.json',uncertain);save('ownership-doubts.json',pairs);save('associated-rejections.json',associated_rejections)
 fields=['audit_number','id','inventory_number','status','color','x','y','luminance','bright_patch_centroid','bright_patch_pixels','interior_pixels','interior_centroid','angle_degrees','signed_distance','next_step_degrees','warnings'];audit=[]
 for l in target:
  r=regions.get(l['id']);audit.append(dict(audit_number=l['audit_number'],id=l['id'],inventory_number=l['inventory_number'],status=l['audit_status'],color=l['color'],x=l['point']['x'],y=l['point']['y'],luminance=l['point']['luminance'],bright_patch_centroid=l['bright_patch']['centroid'],bright_patch_pixels=l['bright_patch']['pixel_count'],interior_pixels=r['region']['pixel_count'] if r else None,interior_centroid=r['region']['centroid'] if r else None,angle_degrees=l['angular']['angle_degrees'],signed_distance=l['angular']['signed_distance'],next_step_degrees=l['next_step_degrees'],warnings='; '.join(l['audit_warnings'])))
 for l in data.get('suppressed_locations',[]):audit.append(dict(id=l['id'],status='duplicate removed',color=l['color'],x=l['point']['x'],y=l['point']['y'],luminance=l['point']['luminance'],warnings='Stronger same-color owner retained; original full record preserved.'))
 for r in uncertain:audit.append(dict(audit_number=r['audit_number'],id=r['id'],status='still unresolved',color=r['color'],x=r['anchor'][0],y=r['anchor'][1],warnings='; '.join(r['explanations'])))
 with (OUT/'centerline-audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(audit)
 save('audit-summary.json',dict(locations=len(locations),interiors=len(data['beads']),target_locations=len(target),target_colors=dict(Counter(l['color'] for l in target)),whole_colors=dict(Counter(l['color'] for l in locations)),target_statuses=dict(Counter(l['audit_status'] for l in target)),unresolved_candidate_groups=len(uncertain),close_same_color_pairs=len(pairs),locations_with_doubts=sum(bool(l['audit_warnings']) for l in target),raw_suppressed_maxima=sum(r.get('status')=='duplicate removed' for r in decisions),prior_locations_preserved=len(oldids),prior_masks_preserved=len(oldregions),explicitly_suppressed=[l['id'] for l in data.get('suppressed_locations',[])],suppressed_prior_locations=sum(l['id'] in oldids for l in data.get('suppressed_locations',[])),warning='These are automatic candidate/measurement audits, not an independently adjudicated 100% physical-bead census.'))
 im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png')
 for i,pair in enumerate(pairs,1):
  ll=[l for l in target if l['id'] in (pair['a'],pair['b'])];x,y=np.mean([points(l) for l in ll],axis=0);box=[int(x)-40,int(y)-40,int(x)+40,int(y)+40];sheet=Image.new('RGB',(650,355),'white');sheet.paste(im.crop(box).resize((320,320),Image.Resampling.NEAREST),(0,35));sheet.paste(panel(im,box,ll,data['beads'],scale=4),(330,35));ImageDraw.Draw(sheet).text((5,4),f"Ownership doubt {i}: {pair['color']} locations {pair['distance']:.1f}px apart",fill='black',font=textfont());sheet.save(OUT/f'ownership-doubt-{i:02d}.png')
 for i,u in enumerate(uncertain,1):
  x,y=u['anchor'];box=[x-45,y-45,x+45,y+45];loc=[dict(id=u['id'],inventory_number=0,audit_number=u['audit_number'],point=dict(x=x,y=y),audit_status='still unresolved')];sheet=Image.new('RGB',(730,390),'white');sheet.paste(im.crop(box).resize((360,360),Image.Resampling.NEAREST),(0,30));sheet.paste(panel(im,box,loc+target,data['beads'],scale=4),(370,30));ImageDraw.Draw(sheet).text((5,5),u['audit_number']+': '+', '.join(u['reasons']),fill='black',font=textfont());sheet.save(OUT/f'unresolved-{i:02d}.png')
 # Automatically select geographically separated before/after successes by color.
 for color in ('red','yellow','black'):
  chosen=[]
  for l in sorted((l for l in target if l['id'] not in oldids and l['color']==color),key=lambda l:-regions[l['id']]['region']['pixel_count']):
   if any(np.linalg.norm(np.array(points(l))-points(z))<150 for z in chosen):continue
   chosen.append(l)
   if len(chosen)==3:break
  for i,l in enumerate(chosen,1):
   x,y=points(l);box=[x-50,y-50,x+50,y+50];sheet=Image.new('RGB',(920,330),'white');draw=ImageDraw.Draw(sheet)
   for j,(label,photo) in enumerate([('Original',im.crop(box).resize((300,300),Image.Resampling.NEAREST)),('R274',panel(im,box,old['locations'],old['beads'],labels=False)),('R275',panel(im,box,target,data['beads'],labels=False))]):sheet.paste(photo,(j*310,30));draw.text((j*310+5,5),label,fill='black',font=textfont())
   sheet.save(OUT/f'recovery-{color}-{i}.png')
 print(json.loads((OUT/'audit-summary.json').read_text()))
if __name__=='__main__':main()

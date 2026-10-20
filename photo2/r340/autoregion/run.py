"""Freeze automatic material-region results without inspecting pattern predictions."""
from explore import ROOT,OUT,setup,read
from recognize import fit_region,measure,THRESHOLD
from panels import sheet
import json,time
from collections import Counter

def main():
 start=time.perf_counter();g,obs,co,photo,geom,auth=setup();manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];training=[r for r in manual if r['number']%2==1];bounds=fit_region(training,{o:r['spacing'] for o,r in geom.items()});model=dict(bounds_fraction=bounds,threshold=THRESHOLD,training_ids=[r['id'] for r in training],comparison_ids=[r['id'] for r in manual if r['number']%2==0],fit_policy='Median of four normalized manual rectangle boundaries on odd24; no brightness/color used in fitting. Replaces inscribed disk, which threw away valid rectangle corners and sometimes could not hold a3x3 patch. Single final rectangle; trial1 kept. Geometry-only one refinement; no threshold adjustment or parameter sweep.');rows=[]
 for o in sorted(obs):
  m=measure(photo,obs[o]['xy'],geom[o]['spacing'],bounds)
  if m:
   a,b,c,d=m['region_box'];m['region_pixels']=[[x,y] for y in range(b,d) for x in range(a,c)]
  eligible=geom[o]['physical_interior'] and o in co and m is not None
  rows.append(dict(id=o,xy=obs[o]['xy'],recorded_color=obs[o]['color'],geometry=geom[o],authority=auth.get(o),measurement=m,decision=m['decision'] if eligible else 'unknown',abstention_reason=None if eligible else 'outside unchanged R338 physical-interior screen' if not geom[o]['physical_interior'] else 'unindexed; no independently established lattice neighborhood' if o not in co else 'no complete3x3 inside geometric rectangle'))
 data=dict(model=model,records=rows,seconds=time.perf_counter()-start,pattern_used=False,geometric_eligibility='Existing R338 physical-interior eligibility reused unchanged; inherited indexed identity required for automatic decisions. Raw scores also retained outside eligibility for48-example comparison.');(OUT/'classification.json').write_text(json.dumps(data,indent=2)+'\n');(OUT/'rectangle-model.json').write_text(json.dumps(model,indent=2)+'\n')
 mm={r['id']:r for r in manual};errors=[r for r in rows if r['authority'] and r['measurement'] and (r['measurement']['decision']=='black')!=(r['authority']['color']=='black')];suspects=[r for r in rows if r['recorded_color']!='black' and r['measurement'] and r['measurement']['decision']=='black'];print('Final geometry',bounds);print('Known errors',[(r['id'],r['authority']['color'],r['measurement']['score'],r['geometry']['physical_interior']) for r in errors]);print('Suspects',[(r['id'],r['measurement']['score'],r['geometry']['physical_interior']) for r in suspects]);print('decisions',Counter(r['decision'] for r in rows))
 sheet(errors,OUT,'rectangle-errors',mm);sheet(suspects,OUT,'rectangle-suspects',mm)
 sheet([r for r in rows if r['id'] in mm],OUT,'manual-comparison',mm)
 sheet([r for r in rows if (r['authority'] and r['authority']['color']!='black' and r['id'] not in mm) or r['id'] in ['C-0309-0966','C-0313-1445','C-1899-0420']],OUT,'additional-colored')
 sheet([r for r in rows if r['recorded_color']=='black' and r['measurement']['decision']!='black'],OUT,'black-misses')
if __name__=='__main__':main()

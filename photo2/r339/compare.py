"""Fixed same-target old/simple comparisons and native suspect contact sheets."""
import argparse,ast
from .common import *
def run(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);data=read(artifact('classification/classification.json.gz'));rows=data['records'];rr={r['id']:r for r in rows};auth=authority();reference={r['id']:r for r in read(ROOT/'photo2/r334/classification/audit.json.gz')['historical_reference_controls']};groups={'maker_explicit':[o for o in auth if o in rr],'maker_physical_interior':[o for o in auth if o in rr and rr[o]['physical_interior']], 'historical_R161_working_labels':[o for o in reference if o in rr],'active_all':[r['id'] for r in rows],'physical_interior':[r['id'] for r in rows if r['physical_interior']]};comparison={}
 for name,ids in groups.items():
  detail=[]
  for o in sorted(ids):
   r=rr[o];truth=auth[o]['color'] if name.startswith('maker_') else r['recorded_color'];expected='black' if truth=='black' else 'not-black';detail.append(dict(id=o,truth_color=truth,label_authority='exact maker' if name.startswith('maker_') else 'recorded working color, not independently certified',interior=r['physical_interior'],old=r['old']['decision'],simple=r['simple_decision'],simple_stable=r['simple_decision'] if r['stable_across_apertures'] else 'unknown',simple_raw=r['aperture_decisions'][1]['decision'],stable=r['stable_across_apertures'],expected=expected))
  scores={}
  for method in ['old','simple','simple_stable']:
   accepted=[r for r in detail if r[method]!='unknown'];scores[method]=dict(n=len(detail),decided=len(accepted),agree=sum(r[method]==r['expected'] for r in accepted),disagree=[r['id'] for r in accepted if r[method]!=r['expected']],abstain=len(detail)-len(accepted))
  comparison[name]=dict(scores=scores,records=detail)
 suspects=[r for r in rows if r['recorded_color']!='black' and r['simple_decision']=='black'];photo=Image.fromarray(photograph());panels=[]
 for i,r in enumerate(suspects):
  x,y=np.rint(r['xy']).astype(int);box=[x-65,y-60,x+66,y+61];im=photo.crop(box).resize((393,363),Image.Resampling.NEAREST);d=ImageDraw.Draw(im);d.ellipse((190,174,200,184),outline='cyan',width=1);im.save(out/f'suspect-{i+1:02d}.png');s=r['samples'][1];overlay=photo.crop(box).resize((393,363),Image.Resampling.NEAREST);od=ImageDraw.Draw(overlay)
  for key,color in [('body_pixels','#40e5bc'),('highlight_pixels','#ee6cbe')]:
   for xx,yy in s[key]:
    xx=(xx-box[0])*3;yy=(yy-box[1])*3;od.rectangle((xx,yy,xx+2,yy+2),outline=color)
  overlay.save(out/f'suspect-{i+1:02d}-mask.png');panels.append(dict(id=r['id'],number=i+1,bbox=box,old=r['old']['decision'],old_broad=r['old']['broad_decision'],old_compact=r['old']['compact_decision'],simple=r['simple_decision'],stable=r['stable_across_apertures'],color=r['recorded_color'],score=r['aperture_decisions'][1]['score'],body_brightness=s['brightness'],references=r['reference_ids']))
 for page in range((len(suspects)+8)//9):
  sheet=Image.new('RGB',(1179,1161),'white');d=ImageDraw.Draw(sheet)
  for j in range(9):
   i=page*9+j
   if i>=len(suspects):break
   r=suspects[i];x=j%3*393;y=j//3*387;sheet.paste(Image.open(out/f'suspect-{i+1:02d}.png'),(x,y+24));d.text((x+4,y+4),f"{i+1} {r['id']} {r['recorded_color']} ->B old {r['old']['decision']}",fill='black')
  sheet.save(out/f'suspects-{page+1:02d}.png')
 save(out/'comparison.json',dict(groups=comparison,suspects=panels,policy='Counts against working labels are agreement, not independent accuracy. Maker colors authoritative. Current maker targets excluded from all local reference training. No expected motif color used.'))
 print('COMPARE',json.dumps({n:r['scores'] for n,r in comparison.items()}),[(r['id'],r['old'],r['stable']) for r in panels])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)

"""Bounded audit of saved evidence for insufficient residues; no new bead search."""
from common import *
def main():
 g,obs,co,rgb,auth=load();wanted={43,62,75,82,89,140,147,186};bank=read(ROOT/'photo2/r332/results/omissions.json.gz');occupied={quotient(v,g['H']):o for o,v in co.items()};vetoes={r['id']:r for r in read(ROOT/'photo2/r338/results/body-freeze.json')['body_judgments']};rows=[]
 for kind in ['provisional_native_candidates','unrepresented_native_candidates','pure_predictions']:
  for r in bank[kind]:
   if not r.get('cell') or (7*r['cell'][0]+6*r['cell'][1])%208 not in wanted:continue
   o=r['id'];row=copy.deepcopy(r);row['kind342']=kind;row['residue']=(7*r['cell'][0]+6*r['cell'][1])%208;row['active_indexed']=o in co;row['current_occupant']=occupied.get(quotient(r['cell'],g['H']));row['native_observation']=kind!='pure_predictions';row['admitted']=False;row['historical_identity_veto']=vetoes.get(o);row['historical_R336_rejected']=o in ['R332-B-0196-0183','R332-B-0138-0130'];rows.append(row)
 save(OUT/'coverage-candidates.json',dict(targets=sorted(wanted),records=rows,policy='Saved R332 site assignments are hypotheses only, not R342 indexing. No color used to choose an identity or admission. Pure predictions never counted as measured beads; duplicates/exclusions preserved.'))
 # Native contexts for every distinct nonactive cached cue, all colors retained.
 photo=Image.fromarray(rgb);cues=[r for r in rows if r['native_observation'] and not r['active_indexed']];manifest=[]
 for start in range(0,len(cues),16):
  board=Image.new('RGB',(1000,280*4),'white');d=ImageDraw.Draw(board)
  for i,r in enumerate(cues[start:start+16]):
   xy=r['xy'];x,y=np.rint(xy).astype(int);box=[int(x-28),int(y-28),int(x+29),int(y+29)];im=photo.crop(box).resize((228,228),Image.Resampling.NEAREST);dd=ImageDraw.Draw(im);dd.ellipse((108,108,116,116),outline='cyan');ox=i%4*250;oy=i//4*280;board.paste(im,(ox,oy+40));d.text((ox,oy),r['id'],fill='black');d.text((ox,oy+15),f"saved site {r['residue']}; NOT admitted",fill='black');manifest.append(dict(id=r['id'],box=box,site_hypothesis=r['cell']))
  board.save(OUT/f'coverage-cues-{start//16+1:02d}.png')
 save(OUT/'coverage-manifest.json',manifest);print('cues',len(cues),'pure',sum(not r['native_observation'] for r in rows),'active',sum(r['active_indexed'] for r in rows))
if __name__=='__main__':main()

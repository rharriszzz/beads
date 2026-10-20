"""Five saved cues with strong old geometry, independently replayed without old pigment code."""
from common import *
from recognize import sample
STEPS=[(1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1)]

def main():
 g,obs,co,rgb,auth=load();bank=read(OUT/'coverage-candidates.json')['records'];wanted=['REC266-P102347','R332-Y-0104-0097','R332-B-0105-0098','R332-B-0110-0103','R332-B-0175-0167'];occupied={quotient(v,g['H']):o for o,v in co.items()};edges={frozenset([e['source'],e['target']]) for e in g['edges']};results=[];photo=Image.fromarray(rgb)
 for oid in wanted:
  r=next(v for v in bank if v['id']==oid);p=np.array(r['xy']);cell=np.array(r['cell']);near=sorted([o for o in co if np.linalg.norm(np.array(obs[o]['xy'])-p)<70],key=lambda o:np.linalg.norm(np.array(obs[o]['xy'])-p));aa=np.array([co[o] for o in near]);aa-=np.rint(((aa-cell)@g['H'])/np.dot(g['H'],g['H'])).astype(int)[:,None]*np.array(g['H']);X=np.c_[aa-cell,np.ones(len(near))];B=np.linalg.lstsq(X,[obs[o]['xy'] for o in near],rcond=None)[0];prediction=B[2];incident=[]
  for step in STEPS:
   z=occupied.get(quotient(cell+step,g['H']))
   if not z:continue
   q=np.array(obs[z]['xy']);v=q-p;dd=float(v@v);block=[]
   for other in co:
    if other==z:continue
    w=np.array(obs[other]['xy'])-p;t=float(w@v/dd)
    if .2<t<.8 and np.linalg.norm(w-t*v)<7:block.append(other)
   incident.append(dict(target=z,delta_ab=step,distance=float(np.linalg.norm(v)),interveners=block))
  blocking=[]
  for e in g['edges']:
   a=np.array(obs[e['source']]['xy']);v=np.array(obs[e['target']]['xy'])-a;t=float((p-a)@v/(v@v))
   if .2<t<.8 and np.linalg.norm(p-a-t*v)<7:blocking.append([e['source'],e['target']])
  m=sample(rgb,p,[],'offset-core');row=dict(id=oid,source_xy=r['xy'],cached_original_xy=r.get('cached_support_xy'),cell=r['cell'],measurement=m,prediction=prediction.tolist(),target_excluded_error=float(np.linalg.norm(prediction-p)),neighbors=incident,triangles=sum(frozenset([a['target'],b['target']]) in edges for i,a in enumerate(incident) for b in incident[i+1:]),blocked_existing_links=blocking,nearest_existing_distance=float(min(np.linalg.norm(np.array(obs[o]['xy'])-p) for o in co)),adopted=False)
  # All geometry retained even if darkness is compelling; no region recentering.
  row['historical_identity_veto']=r.get('historical_identity_veto');results.append(row);x,y=np.rint(p).astype(int);box=[int(x-60),int(y-60),int(x+61),int(y+61)];raw=photo.crop(box).resize((484,484),Image.Resampling.NEAREST);board=Image.new('RGB',(1000,600),'white');d=ImageDraw.Draw(board);board.paste(raw,(0,50));key=[oid]+near;pos={oid:p,**{o:np.array(obs[o]['xy']) for o in near}};colors={oid:'#888888',**{o:dict(red='#e3293b',yellow='#d2a900',black='#202128')[obs[o]['color']] for o in near}}
  for n,o in enumerate(key,1):
   xx,yy=(pos[o]-box[:2])*4;d.text((xx+5,yy+48),str(n),fill='cyan',stroke_width=1,stroke_fill='black');d.ellipse((500+xx-7,50+yy-7,500+xx+7,50+yy+7),fill=colors[o],outline='black');d.text((500+xx+8,50+yy-8),str(n),fill='black')
  for z in incident:
   a=(p-box[:2])*4;b=(pos[z['target']]-box[:2])*4;d.line((500+a[0],50+a[1],500+b[0],50+b[1]),fill='cyan',width=2)
  d.text((0,0),f'{oid}: '+('R338 REJECTED same-body cue; do NOT admit.' if r.get('historical_identity_veto') else 'Existing provisional cue, gray1; cyan proposed ONLY.'),fill='black');d.text((0,22),f"score {m['score']}; geometric error {row['target_excluded_error']:.2f}; old cached labels not treated as truth",fill='black');d.text((0,540),' | '.join(f'{i+1}:{o}' for i,o in enumerate(key[:12])),fill='black');board.save(OUT/f'candidate-{oid}.png');row['key']=key;row['crop_box']=box
 save(OUT/'candidate-checks.json',dict(records=results,policy='Bounded5 saved cues, not a growth engine. No old size/color-voting/recentering procedure reused. Native identity and association require independent certification; numerical compatibility alone never admits a body.'))
 print([(r['id'],r['measurement']['score'],r['target_excluded_error'],r['nearest_existing_distance'],r['blocked_existing_links']) for r in results])
if __name__=='__main__':main()

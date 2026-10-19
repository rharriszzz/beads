"""Matched photo comparisons for the decision audit, not a ballot."""
from photo2.r329.photographic_diagnostics.continuity import *
from PIL import ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;IMG=HERE/'images';IMG.mkdir(exist_ok=True)
PHOTO=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CYAN='#00dbff';GREEN='#9aff59';MAG='#ff50e1';ORANGE='#ffba48';DARK='#142239'
def text(d,p,s,size=25,fill=DARK,bold=False):d.text(p,s,font=ImageFont.truetype(BOLD if bold else FONT,size),fill=fill)
def arrow(d,a,b,c,width=4,halo=False):
 a=np.array(a,float);b=np.array(b,float);v=b-a;v/=np.linalg.norm(v);nn=np.array([-v[1],v[0]]);aa=a+v*13;bb=b-v*16
 d.line([tuple(aa),tuple(bb)],fill=MAG if halo else '#152331',width=width+7 if halo else width+3);d.line([tuple(aa),tuple(bb)],fill=c,width=width);d.polygon([tuple(bb),tuple(bb-v*18+nn*8),tuple(bb-v*18-nn*8)],fill=c)
record=[]
for case in ['G','H']:
 c=CASES[case];alt=c['alt'];rows=c['rows'] if case=='G' else c['rows'][:5]
 ids=list(dict.fromkeys([c['target'],c['anchor']]+[o for _,seq,_ in rows for o in seq]));pts={o:measure(OBS[o])[0] for o in ids};numbers={o:i+1 for i,o in enumerate(ids)}
 bbox=[1525,220,1700,340] if case=='G' else [1050,2800,1230,2985];scale=3.5;pw=round((bbox[2]-bbox[0])*scale);ph=round((bbox[3]-bbox[1])*scale)
 W=2*pw+100;H=ph+600+((len(ids)+1)//2)*37;im=Image.new('RGB',(W,H),'#f8fafc');d=ImageDraw.Draw(im)
 text(d,(25,18),case+' — same photograph, one tested difference',31,bold=True)
 text(d,(25,62),'Supporting comparison only. No human choice requested.',24)
 entries=[]
 for panel,st in enumerate(['working',alt]):
  ox=25+panel*(pw+50);oy=155
  text(d,(ox,102),('A — working' if panel==0 else 'B — saved alternative'),29,bold=True)
  im.paste(PHOTO.crop(bbox).resize((pw,ph),Image.Resampling.LANCZOS),(ox,oy))
  def p(o):return np.array([ox+(pts[o][0]-bbox[0])*scale,oy+(pts[o][1]-bbox[1])*scale])
  for fam,seq,steps in rows:
   for a,b,n in zip(seq,seq[1:],steps):
    if n==1:arrow(d,p(a),p(b),[CYAN,GREEN][fam],3)
    else:
     aa,bb=p(a),p(b)
     for f in np.arange(0,1,.12):d.line([tuple(aa+(bb-aa)*f),tuple(aa+(bb-aa)*min(1,f+.06))],fill=[CYAN,GREEN][fam],width=3)
  # Exactly one disputed connection. No black feature coordinate is referenced.
  source=('E5-1633-0278' if panel==0 else 'E5-1607-0290') if case=='G' else c['anchor'];target=c['target']
  col=CYAN if case=='G' else (GREEN if panel==0 else ORANGE)
  aa,bb=p(source),p(target)
  if case=='H':aa,bb=bb,aa # positive green or [+1,-1] from target toward anchor
  arrow(d,aa,bb,col,7,True)
  for oid in ids:
   pp=p(oid);lp=pp+np.array([14,-21]);d.line([tuple(pp),tuple(lp)],fill='white',width=2);d.ellipse((lp[0]-14,lp[1]-14,lp[0]+14,lp[1]+14),fill=DARK,outline='white',width=2);num=str(numbers[oid]);text(d,(lp[0]-(7 if len(num)==1 else 13),lp[1]-13),num,21,'white',True)
  idx=lambda oid:sum(CO[st][oid][j]*[6,7][j] for j in [0,1])
  text(d,(ox,oy+ph+18),f'Label 1: {target}',23,bold=True)
  text(d,(ox,oy+ph+52),f'Proposed bead index: {idx(target)}',24,bold=True)
  if case=='G':desc=f'Highlighted: {numbers[source]} → 1, cyan [1,0]'
  else:desc='Highlighted: 1 → 2, '+('[0,-1] (reverse green)' if panel==0 else '[1,-1] (derived)')
  text(d,(ox,oy+ph+88),desc,23,fill=DARK,bold=True)
  text(d,(ox,oy+ph+122),f'Other endpoint index: {idx(source)}',22)
  entries.append(dict(state=st,source=source,target=target,source_index=idx(source),target_index=idx(target),delta=(np.array(CO[st][target])-CO[st][source]).tolist(),crop=bbox,scale=scale,origin=[ox,oy],labels=[dict(number=numbers[o],id=o,xy=pts[o].tolist()) for o in ids]))
 y=oy+ph+180;text(d,(25,y),'Shared picture labels → observation IDs (not bead indices)',25,bold=True)
 for i,oid in enumerate(ids):
  xx=25+(i%2)*(pw+50);yy=y+45+(i//2)*37;text(d,(xx,yy),f'{i+1:2}  {oid}',23)
 yy=y+60+((len(ids)+1)//2)*37
 text(d,(25,yy),'Cyan [1,0] · green [0,1] · magenta border = disputed connection',23,bold=True)
 text(d,(25,yy+35),'Lines join partial colored-region locations, not measured body centers.',22)
 text(d,(25,yy+68),'Original pixels fixed. Black reflections and empty-looking slots are not tested.',22)
 im=im.crop((0,0,W,yy+110));im.save(IMG/(case.lower()+'-comparison.png'),optimize=True)
 PHOTO.crop(bbox).save(IMG/(case.lower()+'-raw.png'))
 record.append(dict(case=case,file=case.lower()+'-comparison.png',panels=entries,rows=rows,photo_dimensions=[pw,ph],disputed_connections_per_panel=1))
(HERE/'figures.json').write_text(json.dumps(record,indent=2)+'\n')

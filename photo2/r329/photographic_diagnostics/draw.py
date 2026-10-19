"""Annotated original-photo diagnostics. No generated bead boundaries."""
from .continuity import *
from PIL import ImageDraw,ImageFont
from scipy.spatial import ConvexHull
from scipy import ndimage as ndi
IM_PIL=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
ASSET=OUT/'images';ASSET.mkdir(exist_ok=True)
DATA=read(OUT/'continuity.json.gz')['cases'];MODEL=np.load(OUT/'model-geometry.npz')
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CYAN='#00d9ff';GREEN='#8fff57';INK='#172538';MAG='#f000bc';BLUE='#3095ff';VIOLET='#9656ff';ORANGE='#ffb236'
def text(d,xy,t,n=27,c=INK,b=False):d.text(xy,t,font=ImageFont.truetype(BOLD if b else FONT,n),fill=c)
def line(d,pts,color,width=5,dash=False):
 if dash:
  for a,b in zip(pts,pts[1:]):
   dist=np.linalg.norm(np.array(b)-a);nn=max(2,int(dist/10))
   for i in range(0,nn-1,2):
    p=np.array(a)+(np.array(b)-a)*i/nn;q=np.array(a)+(np.array(b)-a)*min(i+1,nn)/nn;d.line([tuple(p),tuple(q)],fill=color,width=width)
 else:d.line(pts,fill=INK,width=width+3);d.line(pts,fill=color,width=width)
def arrow(d,a,b,col,width=6):
 v=np.array(b)-a;l=np.linalg.norm(v)
 if l<1:return
 v/=l;n=np.array([-v[1],v[0]]);a=np.array(a)+v*10;b=np.array(b)-v*13;line(d,[tuple(a),tuple(b)],col,width)
 d.polygon([tuple(b),tuple(b-v*20+n*9),tuple(b-v*20-n*9)],fill=col)
def cross(d,p,col,size=12):
 for a,b in [((p[0]-size,p[1]),(p[0]+size,p[1])),((p[0],p[1]-size),(p[0],p[1]+size))]:
  d.line([a,b],fill='black',width=8);d.line([a,b],fill=col,width=4)
def label(d,p,s,col=INK):
 bb=d.textbbox(p,s,font=ImageFont.truetype(BOLD,25));d.rectangle((bb[0]-4,bb[1]-4,bb[2]+4,bb[3]+4),fill='white');text(d,p,s,25,col,True)
MAN=[]
def make(name,case,title,subtitle,mode='photo',state='working',families=(0,1),footer=None):
 c=DATA[case];cfg=c['config'];bbox=([1525,220,1710,370] if case=='G' else cfg['box']);ids=list(c['measurements']);ids.sort(key=lambda o:(o!=cfg['anchor'],o!=cfg['target'],o!=cfg['last'],c['measurements'][o]['center'][1],c['measurements'][o]['center'][0]))
 if case=='F' and mode in ['model','material']:
  bbox=[1330,225,1510,335];ids=[o for o in ids if bbox[0]<c['measurements'][o]['center'][0]<bbox[2] and bbox[1]<c['measurements'][o]['center'][1]<bbox[3]]
 H=max(1290,210+len(ids)*58+130);im=Image.new('RGB',(1600,H),'#f7f9fc');d=ImageDraw.Draw(im)
 text(d,(36,22),title,38,b=True);text(d,(36,78),subtitle,25)
 scale=min(940/(bbox[2]-bbox[0]),(H-340)/(bbox[3]-bbox[1]));w=round((bbox[2]-bbox[0])*scale);h=round((bbox[3]-bbox[1])*scale);ox=35+(940-w)//2;oy=150+(H-340-h)//2
 im.paste(IM_PIL.crop(bbox).resize((w,h),Image.Resampling.LANCZOS),(ox,oy))
 def p(xy):return (ox+(xy[0]-bbox[0])*scale,oy+(xy[1]-bbox[1])*scale)
 def center(o):return np.array(c['measurements'][o]['center'])
 # Paint only measured colored material, never complete photographic outlines.
 for oid in ids:
  px=np.array(c['measurements'][oid]['pixels']);bb=[px[:,0].min(),px[:,1].min(),px[:,0].max()+1,px[:,1].max()+1];m=np.zeros((bb[3]-bb[1],bb[2]-bb[0]),bool);m[px[:,1]-bb[1],px[:,0]-bb[0]]=True;edge=m&~ndi.binary_erosion(m)
  for yy,xx in np.argwhere(edge):
   native=(xx+bb[0],yy+bb[1])
   if not (bbox[0]<=native[0]<bbox[2] and bbox[1]<=native[1]<bbox[3]):continue
   q=p(native);d.rectangle((q[0]-scale/2,q[1]-scale/2,q[0]+scale/2,q[1]+scale/2),fill='#fff5c9')
 # Overlay actual model masks on the same original pixels, not a guessed shape.
 model_addresses=[]
 if mode in ['model','material']:
  addrs=[(-33,MAG),(-27,VIOLET)] if mode=='model' else [(-38,MAG),(-26,VIOLET)]
  shape=tuple(MODEL['shape']);mx=MODEL['xy'];owner=MODEL['owner'];indices=MODEL['indices']
  for addr,col in addrs:
   j=int(np.flatnonzero(indices==addr)[0]);vis=(owner==j).reshape(shape);edge=vis&~ndi.binary_erosion(vis)
   for xy in mx[edge.ravel()]:
    if bbox[0]<=xy[0]<bbox[2] and bbox[1]<=xy[1]<bbox[3]:
     q=p(xy);d.ellipse((q[0]-2,q[1]-2,q[0]+2,q[1]+2),fill=col)
   if mode=='model':
    iso=MODEL['isolated_'+str(addr)].reshape(shape);ee=iso&~ndi.binary_erosion(iso)
    for ii,xy in enumerate(mx[ee.ravel()]):
     if ii%6<3:
      q=p(xy);d.rectangle((q[0]-1,q[1]-1,q[0]+1,q[1]+1),fill=col)
   pc=MODEL['projected'][j];cross(d,p(pc),col)
   lp=(ox+30+(0 if addr in [-33,-38] else 320),oy+h+25);line(d,[p(pc),(lp[0]+45,lp[1])],col,2,dash=True);label(d,lp,f'M{addr}',col);model_addresses.append(addr)
  if mode=='material':
   for oid,addr in [('C-1391-0312',-38),('C-1422-0264',-26)]:
    px=np.array(c['measurements'][oid]['pixels']);mb=MODEL['bbox'];st=float(MODEL['step']);own=owner.reshape(shape)[((px[:,1]-mb[1])/st).astype(int),((px[:,0]-mb[0])/st).astype(int)];j=int(np.flatnonzero(indices==addr)[0])
    for xy in px[own!=j]:
     q=p(xy);d.rectangle((q[0]-1,q[1]-1,q[0]+1,q[1]+1),fill=ORANGE)
 # Both families remain visible, with the selected family emphasized in photo panels.
 for family,seq,steps in cfg['rows']:
  col=[CYAN,GREEN][family];width=5 if family in families else 2
  if mode in ['model','material']:width=2
  for a,b,n in zip(seq,seq[1:],steps):
   if mode=='photo' and family not in families:continue
   if a not in ids or b not in ids:continue
   if n==1:arrow(d,p(center(a)),p(center(b)),col,width)
   else:line(d,[p(center(a)),p(center(b))],col,width,dash=True)
 if case=='E' and mode=='photo' and families==(1,):
  a=p(center(cfg['anchor']));b=p(center(cfg['target']));line(d,[a,b],'white',3,dash=True);label(d,((a[0]+b[0])/2-60,(a[1]+b[1])/2+22),'colored bridge')
 if case=='E' and mode=='photo' and families==(0,):
  line(d,[p(center('C-1777-1612')),p(center(cfg['target']))],CYAN,3,dash=True)
 if mode=='derived':
  a=p(center('E5-1694-1563'));b=p(center('C-1717-1540'));arrow(d,a,b,ORANGE,7);label(d,((a[0]+b[0])/2+15,(a[1]+b[1])/2),'[1,-1]',ORANGE)
 # Variant hulls are possible slot locations, NOT black bead contours.
 prediction=None
 if mode in ['working','alternative','model']:
  chosen=state;pred=c['summaries'][chosen];bp=np.array([v for variant in c['variants'] for v in variant['predictions'][chosen]['black_predictions']]);mid=np.median(bp,0)
  delta=c['central']['predictions'][chosen]['black_delta']
  control=sum(abs(delta[f])*max(r['per_step'] for v in c['variants'] for r in v['controls'] if r['family']==f) for f in [0,1])
  # F adds measured same-family transfer residual to sensitivity range.
  lo=bp.min(0)-control;hi=bp.max(0)+control;q0=p(lo);q1=p(hi);line(d,[q0,(q1[0],q0[1]),q1,(q0[0],q1[1]),q0],BLUE,4,dash=True)
  cross(d,p(mid),BLUE,10);label(d,(p(mid)[0]+17,p(mid)[1]-35),'K slot',BLUE)
  if mode!='model':
   aa=center(cfg['anchor']);delta=c['central']['predictions'][chosen]['black_delta'];dirs=[i for i,n in enumerate(delta) if n]
   if len(dirs)==1:arrow(d,p(mid),p(aa),[CYAN,GREEN][dirs[0]],7)
   tp=np.array(pred['target_position_median']);cross(d,p(tp),MAG);actual=center(cfg['target']);line(d,[p(tp),p(actual)],'white',4,dash=True)
   if case=='E':arrow(d,p(tp),p(mid),GREEN,6)
   if case=='G':
    source='E5-1607-0290' if chosen=='working' else 'C-1585-0307';arrow(d,p(center(source)),p(mid),CYAN,6);arrow(d,p(mid),p(tp),GREEN,6)
   if case=='H':arrow(d,p(mid),p(tp),CYAN,6)
   if case=='H' and chosen=='lower':
    q=p(center(cfg['omitted']));d.ellipse((q[0]-28,q[1]-28,q[0]+28,q[1]+28),outline=MAG,width=5);label(d,(q[0]-100,q[1]+30),'unindexed',MAG)
   label(d,(p(tp)[0]+16,p(tp)[1]+15),'P',MAG)
   # A nearby text block carries the magnitude without covering the photograph.
   text(d,(1010,H-230),f'Target miss: {pred["error_median"]:.1f} px median',27,MAG,True)
   text(d,(1010,H-192),f'Variants: {pred["error_min"]:.1f}–{pred["error_max"]:.1f} px',25)
  prediction=dict(state=chosen,black_slot=mid.tolist(),slot_box=[lo.tolist(),hi.tolist()],model_addresses=model_addresses)
 # Numbered labels mark colored-material centroids, never black highlights.
 for i,oid in enumerate(ids,1):
  q=p(center(oid));d.ellipse((q[0]-8,q[1]-8,q[0]+8,q[1]+8),fill='white',outline=INK,width=2);bx=q[0]+22;by=q[1]-23
  if bx>ox+w-15:bx=q[0]-22
  d.line([q,(bx,by)],fill='white',width=2);d.ellipse((bx-16,by-16,bx+16,by+16),fill=INK,outline='white',width=2);text(d,(bx-(8 if i<10 else 14),by-14),str(i),20,'white',True)
  yy=147+(i-1)*58;text(d,(1010,yy),f'{i:2}  {oid}',24,b=oid in [cfg['anchor'],cfg['target']]);desc='measured colored material'
  if oid==cfg['anchor']:desc='anchor for this prediction'
  if oid==cfg['target']:desc='colored body check' if case=='F' else 'withheld colored target'
  if case=='F':
   kk=sum(CO['working'][oid][j]*[7,6][j] for j in [0,1]);desc=f'relative index {kk}' + ('; reference zero' if kk==0 else '; colored material')
  if case=='E' and oid==cfg['anchor']:desc='index '+str(sum(CO[state][oid][j]*[6,7][j] for j in [0,1]))+'; colored anchor'
  if case=='G' and oid==cfg['last']:desc='last agreeing colored ID; index 92'
  if case=='H' and oid==cfg['last']:desc='last agreeing ID; index 1187'
  if oid==cfg.get('omitted'):desc='visible red bead; alternative omits ID'
  text(d,(1060,yy+29),desc,20,'#526279')
 if mode in ['working','alternative','model']:
  text(d,(1010,H-325),'K slot: '+cfg['black'],24,BLUE,True)
  bi=sum(CO[state][cfg['black']][j]*([7,6] if case=='F' else [6,7])[j] for j in [0,1])
  text(d,(1010,H-292),f'Conditional index {bi}; inferred slot',23)
 y=H-137
 for x,col,lab in [(35,CYAN,'[1,0] family'),(530,GREEN,'[0,1] family'),(1050,BLUE,'inferred slot, not body outline')]:line(d,[(x,y+15),(x+40,y+15)],col,5);text(d,(x+52,y),lab,22)
 text(d,(35,H-91),'Cream edges = measured pigment only. Dashed row gaps have conditional step counts.',23)
 text(d,(35,H-55),footer or 'Black reflections are not marked or used as positioning measurements.',23)
 im.save(ASSET/(name+'.png'),optimize=True)
 MAN.append(dict(file=name+'.png',case=case,mode=mode,crop=bbox,labels=[dict(number=i,id=o,center=center(o).tolist()) for i,o in enumerate(ids,1)],prediction=prediction,model_addresses=model_addresses))

make('e-colored-cyan','E','E-A1. Establish the cyan family from colored bodies','Compare three nearby rows. The rightmost upper colored bead is withheld.',families=(0,))
make('e-colored-green','E','E-A2. Estimate the green family separately','The colored bridge across the disputed gap aligns with this family.',families=(1,))
make('d-derived-colored','E','D. A derived step between two colored observations','Orange = reverse green, then forward cyan. It is not a third primitive direction.',mode='derived')
make('e-working','E','E-B. Working: continue along the green family','K slot is inferred from colored material. P predicts the withheld yellow bead.',mode='working')
make('e-alternative','E','E-C. Alternative: a cyan step, then a green step','P lands away from the actual yellow body. White dashed segment shows the miss.',mode='alternative',state='closest')
make('f-photo','F','F-A. Photograph: neighboring colored-body rows','These partial pigment regions establish geometry; no black reflection is fitted.',mode='photo')
make('f-model','F','F-B. Actual frozen model geometry over the photograph','Solid: visible boundaries. Dotted: isolated footprints. Blue box: uncertain inferred slot.',mode='model',footer='Magenta M−33 is the assigned model bead; violet M−27 is a comparison body, not a proved identity.')
make('f-material','F','F-C. A visible model disagreement on colored bodies','Orange measured material lies outside its assigned visible model body.',mode='material',footer='M−38 corresponds to index 26; M−26 to index 38. This is not a black-light positioning test.')
for case in ['G','H']:
 make(case.lower()+'-photo',case,f'{case}-A. Estimate each direction from colored rows','Separate cyan and green references; gaps are shown rather than filled with reflections.')
 make(case.lower()+'-working',case,f'{case}-B. Working row assignment tested on colored material','P is a geometric prediction of the withheld colored target; white line marks its miss.',mode='working')
 make(case.lower()+'-alternative',case,f'{case}-C. Alternative row assignment tested on colored material','Same photo, masks and reference families; only the candidate lattice relationship changes.',mode='alternative',state=DATA[case]['config']['alt'])
(OUT/'figures.json').write_text(json.dumps(MAN,indent=2)+'\n');print('drawn',len(MAN))

for case in 'EFGH':
 box=[1525,220,1710,370] if case=='G' else DATA[case]['config']['box']
 IM_PIL.crop(box).save(ASSET/('raw-'+case.lower()+'.png'))

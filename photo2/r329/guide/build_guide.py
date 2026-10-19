"""Presentation only: draw saved photo observations and accepted local links.
Run: MPLCONFIGDIR=/tmp/r329-mpl .venv/bin/python -m photo2.r329.guide.build_guide
No detector, growth search, placement or rendering is run.
"""
import json, math, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from photo2.r329.common import ROOT, read, canonical, REF
HERE=Path(__file__).resolve().parent
ASSETS=HERE/'images'; ASSETS.mkdir(exist_ok=True)
G=read(ROOT/'photo2/r328/results/graph.json.gz')
OBS={o['id']:o for o in G['observations']}
STATES=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states']
PREP=read(ROOT/'photo2/r328/development/final256/prepared.json.gz')
NOVEL=next(a['state'] for a in read(ROOT/'photo2/r329/results/novel-windings.json.gz')['alternatives'] if a['state']['H']==[214,176])
ST={'working':STATES[0],'closest':STATES[1],'lower':STATES[5],'early':NOVEL}
CO={k:canonical(s) for k,s in ST.items()}
ED={}
for k,s in ST.items():
    ED[k]=set()
    for r in s['path']:
        if not r.get('skipped'):
            for a,b,delta in PREP['patches'][r['window']][r['patch']]['edges']:
                ED[k].add((a,b,tuple(delta))); ED[k].add((b,a,tuple(-x for x in delta)))
PHOTO=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
CYAN='#00d8ff'; GREEN='#7dff63'; ORANGE='#ffb142'; INK='#152235'; PINK='#f000b8'; PURPLE='#673aff'
COL={(1,0):CYAN,(0,1):GREEN,(1,-1):ORANGE}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def text(d,p,t,size=30,fill=INK,b=False): d.text(p,t,font=font(size,b),fill=fill)
def arrow(d,a,b,color,width=7):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    ux,uy=dx/length,dy/length
    a=(a[0]+ux*15,a[1]+uy*15);b=(b[0]-ux*17,b[1]-uy*17)
    d.line([a,b],fill='#101820',width=width+4);d.line([a,b],fill=color,width=width)
    for scale,c in [(1.2,'#101820'),(1,color)]:
        d.polygon([b,(b[0]-ux*21*scale-uy*10*scale,b[1]-uy*21*scale+ux*10*scale),(b[0]-ux*21*scale+uy*10*scale,b[1]-uy*21*scale-ux*10*scale)],fill=c)
def index(oid,state,fam):
    a,b=CO[state][oid];return (7*a+6*b) if fam=='A' else (6*a+7*b)
def legend(d,y,x=45,size=27):
    for xx,c,t in [(x,CYAN,'[1,0] primitive'),(x+510,GREEN,'[0,1] primitive'),(x+1020,ORANGE,'[1,-1] derived')]:
        d.line([(xx,y+18),(xx+50,y+18)],fill=INK,width=12);d.line([(xx,y+18),(xx+50,y+18)],fill=c,width=7)
        text(d,(xx+66,y),t,size)
MANIFEST=[]
def panel(name,title,subtitle,bbox,chains,central,extra=(),state='working',fam='B',notes=None,footer='',model=False,label_order=None):
    """Full ID legend and numbered leaders stay outside the original crop."""
    ids=list(dict.fromkeys([central]+list(extra)+[o for _,seq in chains for o in seq]))
    if label_order is not None:
        assert set(ids)<=set(label_order)
        ids=list(label_order)
    assert len(ids)<=11,(name,len(ids))
    im=Image.new('RGB',(1600,1120),'#f7f9fc');d=ImageDraw.Draw(im)
    text(d,(40,22),title,40,b=True);text(d,(40,80),subtitle,27)
    x0,y0,x1,y1=bbox; scale=min(940/(x1-x0),790/(y1-y0));w=round((x1-x0)*scale);h=round((y1-y0)*scale)
    ox=40+(940-w)//2;oy=160+(790-h)//2
    crop=PHOTO.crop(bbox);im.paste(crop.resize((w,h),Image.Resampling.LANCZOS),(ox,oy))
    def pt(oid):x,y=OBS[oid]['xy'];return (ox+(x-x0)*scale,oy+(y-y0)*scale)
    def xypt(xy):return (ox+(xy[0]-x0)*scale,oy+(xy[1]-y0)*scale)
    modelmeta=None
    if model:
        raster=np.load(ROOT/'photo2/r324/results/R321-geometry-best-raster.npz')
        positions=read(ROOT/'photo2/r324/results/R321-geometry-best-frozen.json.gz')['positions'];indices=positions['indices']
        overlay=Image.new('RGBA',im.size);od=ImageDraw.Draw(overlay)
        for addr,col in [(-33,(240,0,184,115)),(-27,(103,58,255,115))]:
            jj=indices.index(addr);pixels=raster['xy'][raster['owner']==jj]
            for x,y in pixels:
                if x0<=x<x1 and y0<=y<y1:
                    a=xypt((x-.5,y-.5));b=xypt((x+.5,y+.5));od.rectangle([a,b],fill=col)
        im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
        for addr,col,offset in [(-33,PINK,(18,15)),(-27,PURPLE,(18,-40))]:
            pp=xypt(positions['projected'][indices.index(addr)])
            d.line([(pp[0]-12,pp[1]),(pp[0]+12,pp[1])],fill='white',width=8);d.line([(pp[0],pp[1]-12),(pp[0],pp[1]+12)],fill='white',width=8)
            d.line([(pp[0]-12,pp[1]),(pp[0]+12,pp[1])],fill=col,width=4);d.line([(pp[0],pp[1]-12),(pp[0],pp[1]+12)],fill=col,width=4)
            pos=(pp[0]+offset[0],pp[1]+offset[1]);label=f'M{addr}'
            bounds=d.textbbox(pos,label,font=font(28,True));d.rectangle((bounds[0]-3,bounds[1]-3,bounds[2]+3,bounds[3]+3),fill='white');text(d,pos,label,28,col,True)
        support=next(o['pixels_xy'] for o in read(ROOT/'photo2/r324/results/observation-pixels.json') if o['id']==central)
        for pp in support:
            a=xypt((pp[0]-.5,pp[1]-.5));b=xypt((pp[0]+.5,pp[1]+.5));d.rectangle([a,b],fill='#fff000',outline='black',width=1)
        pp=pt(central);d.ellipse((pp[0]-22,pp[1]-22,pp[0]+22,pp[1]+22),outline=PURPLE,width=5)
        modelmeta={'expected_address':-33,'owner_address':-27,'support_pixels':support,'raster':'photo2/r324/results/R321-geometry-best-raster.npz','ownership_source':'photo2/r324/results/R321-geometry-best-frozen.json.gz#support','raster_scope':'Incomplete archived sampled visible pixels; support ownership is a separate saved ray test.'}
    audited=[]
    for delta,seq in chains:
        for a,b in zip(seq,seq[1:]):
            actual=tuple(CO[state][b][i]-CO[state][a][i] for i in range(2))
            assert actual==delta,(name,a,b,delta,actual)
            assert (a,b,delta) in ED[state],('missing saved edge',name,a,b,delta)
            arrow(d,pt(a),pt(b),COL[delta],4 if model else 7)
            audited.append({'source':a,'target':b,'delta':list(delta)})
    # Local label numbers are pointers, never bead indices.
    step=min(76,790/len(ids));ky=155
    for i,oid in enumerate(ids,1):
        x,y=pt(oid);rad=14 if oid==central else 10
        d.ellipse((x-rad,y-rad,x+rad,y+rad),outline='white',width=5)
        d.ellipse((x-rad-2,y-rad-2,x+rad+2,y+rad+2),outline=INK,width=2)
        # The number is offset from the actual observation; its leader ends at the ring.
        bx,by=x+25,y-25
        if bx>ox+w-22:bx=x-27
        if by<oy+20:by=y+28
        d.line([(x,y),(bx,by)],fill='white',width=3)
        d.ellipse((bx-20,by-20,bx+20,by+20),fill=INK,outline='white',width=2)
        s=str(i);bb=d.textbbox((0,0),s,font=font(23,True));text(d,(bx-(bb[2]-bb[0])/2,by-16),s,23,'white',True)
        yy=ky+(i-1)*step
        d.ellipse((1010,yy,1050,yy+40),fill=INK);text(d,(1021 if i<10 else 1013,yy+4),s,23,'white',True)
        text(d,(1064,yy-2),oid,27,b=oid==central)
        desc=(notes or {}).get(oid,f'relative index {index(oid,state,fam)}')
        text(d,(1064,yy+33),desc,23,fill='#435369')
    legend(d,973)
    text(d,(40,1025),footer or f'Arrows: saved {state} links. Index convention {fam}. Numbers in circles are picture labels.',25)
    text(d,(40,1065),'White rings mark observed features, not measured bead centers. Photo pixels have not moved.',25)
    im.save(ASSETS/(name+'.png'),optimize=True)
    MANIFEST.append({'figure':name+'.png','title':title,'state':state,'family':fam,'crop_xyxy':bbox,'labels':[{'number':i,'id':o,'xy':OBS[o]['xy'],'relative_index':index(o,state,fam)} for i,o in enumerate(ids,1)],'edges':audited,'model':modelmeta,'raw_crop_rgb_sha256':hashlib.sha256(crop.tobytes()).hexdigest()})
    return im
C='C-1721-1566';K='K-1740-1575';M='MAT25-K-1719-1592';E='E5-1694-1563';U='C-1717-1540';T='C-1705-1514';L='C-1669-1561';R='C-1770-1577';Q='K-1683-1538'
f0=[M,C,U,T];f1=[R,K,C,E,L];bend=(1638,1484,1800,1624)
panel('a-primitive-10','A. Follow the cyan row: [1,0]','Start at label 1. Follow the arrows upward through the same local row.',bend,[((1,0),f0)],C,footer='Each cyan arrow is one [1,0] lattice step. In index convention B it adds 6.')
panel('b-primitive-01','B. Follow the green row: [0,1]','The same central observation lies on a second row, crossing the first.',bend,[((0,1),f1)],C,footer='Each green arrow is one [0,1] lattice step. In index convention B it adds 7.')
panel('c-both-primitives','C. Two directions through one observed feature','Follow cyan upward; follow green from right to left. Both pass through label 1.',bend,[((1,0),f0),((0,1),f1)],C)
panel('d-derived','D. Orange combines the two primitive steps','The orange row uses nearby observations; it does not pass through label 1.',bend,[((1,0),[M,C,U]),((0,1),[K,C,E,L]),((1,0),[E,Q]),((1,-1),[L,Q,T])],C,footer='From C-1669 to K-1683: reverse one green step, then take one cyan step = [1,-1].')
e1=panel('e-working','E1. Working interpretation: K → C is [0,1]','Same photograph and feature locations as E2. The disputed segment is green.',bend,[((1,0),f0),((0,1),f1)],C,notes={C:'index 1739 = 1732 + 7',K:'index 1732; unchanged',M:'index 1733; last agreement'},footer='Working winding (214,201). Convention B: green adds 7; cyan adds 6.')
e2=panel('e-alternative','E2. Alternative interpretation: K → C is [1,0]','The same photographed segment is now cyan. The central index is one smaller.',bend,[((1,0),[K,C,U,T]),((0,1),[C,E,L]),((0,1),[R,K])],C,extra=[M],state='closest',notes={C:'index 1738 = 1732 + 6',K:'index 1732; unchanged',M:'index 1733; unchanged'},footer='Alternative winding (215,200). The feature positions are identical; the row assignment changes.')
# E overview is truly side by side, with large photo panels and a shared ID key.
def disputed_pair():
    ids=[C,K,M,U,T,E,L,R];im=Image.new('RGB',(1800,1380),'#f7f9fc');d=ImageDraw.Draw(im)
    text(d,(40,20),'E. Same segment, two interpretations',44,b=True)
    for j,(state,chains,title,result) in enumerate([
        ('working',[((1,0),f0),((0,1),f1)],'Working: K → C is [0,1]','1732 + 7 = 1739'),
        ('closest',[((1,0),[K,C,U,T]),((0,1),[C,E,L]),((0,1),[R,K])],'Alternative: K → C is [1,0]','1732 + 6 = 1738')]):
        ox=45+j*890;oy=160;scale=5.;x0,y0,x1,y1=bend
        im.paste(PHOTO.crop(bend).resize((810,700),Image.Resampling.LANCZOS),(ox,oy))
        text(d,(ox,90),title,32,b=True)
        def p(o):x,y=OBS[o]['xy'];return ox+(x-x0)*scale,oy+(y-y0)*scale
        for delta,seq in chains:
            for a,b in zip(seq,seq[1:]):arrow(d,p(a),p(b),COL[delta],7)
        for i,o in enumerate(ids,1):
            x,y=p(o);d.ellipse((x-12,y-12,x+12,y+12),outline='white',width=4)
            bx,by=x+27,y-28;d.line([(x,y),(bx,by)],fill='white',width=3);d.ellipse((bx-21,by-21,bx+21,by+21),fill=INK,outline='white',width=2);text(d,(bx-8,by-17),str(i),25,'white',True)
        text(d,(ox,880),result,40,b=True)
    for i,o in enumerate(ids,1):
        col=(i-1)%2;row=(i-1)//2;x=45+col*890;y=955+row*70
        text(d,(x,y),f'{i}  {o}',30,b=i in [1,2]);text(d,(x+470,y),f'B: {index(o,"working","B")} → {index(o,"closest","B")}',27)
    legend(d,1252,size=28)
    text(d,(45,1315),'Arrow runs from label 2 (K) to label 1 (C). Picture labels 1–8 are not bead indices.',29)
    im.save(ASSETS/'e-disputed-pair.png',optimize=True)
    MANIFEST.append({'figure':'e-disputed-pair.png','sources':['e-working.png','e-alternative.png'],'label_ids':ids,'crop_xyxy':bend})
disputed_pair()
# Model case uses convention A, explicitly distinct from the photo-photo examples.
panel('f-reference','F1. The shared photographic zero','Label 1 fixes where counting starts. It is an observation, not a model center.',(1200,242,1360,355),[((1,0),['C-1251-0290','C-1277-0302',REF,'C-1324-0332']),((0,1),['C-1284-0332',REF,'K-1319-0295','C-1339-0277'])],REF,fam='A',notes={REF:'index 0; model address −64'},footer='Convention A: cyan adds 7; green adds 6. The origin stays fixed in every comparison.')
first='K-1398-0248';last='C-1391-0312';pc=[((1,0),[first,'C-1422-0264','K-1443-0285']),((0,1),['P5-1364-0299','K-1377-0268',first]),((1,0),['C-1339-0277','P5-1364-0299',last])]
panel('f-local-frame','F2. Last agreement 26; first mismatch 31','Two local row directions locate the first mismatched photographed support.',(1318,224,1468,338),pc,first,extra=[last],fam='A',notes={first:'index 31; first mismatch',last:'index 26; last agreement'},footer='The ordering is by bead index, not left-to-right position in the photograph.')
panel('f-model-ownership','F3. Which model bead covers the observed light?','Magenta: expected M−33. Violet: owner M−27, including the ring around label 1.',(1318,224,1468,338),pc,first,extra=[last],fam='A',model=True,notes={first:'k31: expected −33; owner −27',last:'k26: expected/owner −38'},footer='Tint = incomplete model samples. Yellow = 3 support pixels. Cross = model center. Thin arrows = lattice.')
# Early row choice, each hypothesis has its own actual saved local links.
N='NEW-1621-315';earlybox=(1527,225,1698,342);last92='C-1608-0253'
early_ids=[N,last92,'C-1559-0252','C-1582-0272','E5-1607-0290','P5-1645-0309','C-1669-0293','C-1585-0307','E5-1561-0289']
panel('g-early-working','G1. Early row choice: working reconstruction','Label 1 has index 97. Label 2, index 92, is the last preceding agreement.',earlybox,[((1,0),['C-1559-0252','C-1582-0272','E5-1607-0290',N]),((0,1),[N,'P5-1645-0309','C-1669-0293'])],N,extra=[last92,'C-1585-0307'],notes={N:'index 97; first difference',last92:'index 92; last agreement'},label_order=early_ids,footer='Watch which upstream row feeds label 1. The later −175 discrepancy starts with a −7 change here.')
panel('g-early-alternative','G2. Early row choice: alternative reconstruction','The cyan predecessor row changes. The green continuation remains recognizable.',earlybox,[((1,0),['E5-1561-0289','C-1585-0307',N]),((0,1),[N,'P5-1645-0309','C-1669-0293']),((1,-1),[last92,'E5-1607-0290',N])],N,extra=[last92],state='early',notes={N:'index 90 instead of 97',last92:'index 92; unchanged'},label_order=early_ids,footer='Alternative winding (214,176): first difference −7; later accumulated difference −175 (B).')
B='NEW-1132-2925';lastlow='E5-1151-2893';lowbox=(1090,2855,1220,2970)
lower_ids=[B,lastlow,'C-1125-2900','C-1119-2879','C-1189-2919','K-1159-2920','RF70T-K-1163-2935','C-1198-2943','E5-1178-2887']
panel('h-lower-working','H1. Lower bend: working reconstruction','The first differing black feature is label 1. Last agreement is label 2.',lowbox,[((1,0),[B,'C-1125-2900','C-1119-2879']),((0,1),['C-1189-2919','K-1159-2920',B]),((1,0),['RF70T-K-1163-2935','K-1159-2920',lastlow]),((1,-1),[B,lastlow])],B,extra=[lastlow,'C-1198-2943'],notes={B:'index 1188; first difference',lastlow:'index 1187; last agreement'},label_order=lower_ids,footer='Green row: C-1189 → K-1159 → NEW-1132. Cyan row runs upward from NEW-1132.')
panel('h-lower-alternative','H2. Lower bend: alternative reconstruction','The same black feature joins the lower green row and receives index 1182.',lowbox,[((1,0),[B,'C-1125-2900','C-1119-2879']),((0,1),['C-1198-2943','RF70T-K-1163-2935',B]),((1,0),['RF70T-K-1163-2935','K-1159-2920',lastlow]),((1,-1),[B,'K-1159-2920','E5-1178-2887'])],B,extra=[lastlow],state='lower',notes={B:'index 1182 instead of 1188',lastlow:'index 1187; unchanged'},label_order=lower_ids,footer='Alternative winding (213,201): the green predecessor changes; the first index difference is −6.')
for name,bbox in [('inward',bend),('reference',(1200,242,1360,355)),('model',(1318,224,1468,338)),('early',earlybox),('lower',lowbox)]:
    PHOTO.crop(bbox).save(ASSETS/(name+'-original.png'))
(HERE/'figure-data.json').write_text(json.dumps(MANIFEST,indent=2)+'\n')
print(f'Wrote {len(MANIFEST)} figures; every drawn lattice edge checked against saved path and coordinates.')

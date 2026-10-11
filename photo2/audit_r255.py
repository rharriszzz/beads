"""Read-only R255 evidence rendering: no detector, fit, search, or recoloring.

Run from repository root: .venv/bin/python photo2/audit_r255.py
Use --output photo2/output/r255-replay for an independent artifact replay.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform, sys
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import splev
from scipy.spatial import cKDTree
from tangent_circles import SplineRope, View

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'photo2/review'
PRIMARY = 'N2696_h+1_f0'
PATTERN = 'N2674_h+1_f0'
OTHER = 'N2681_h-1_f0'
MODELS = [PRIMARY, PATTERN, OTHER]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COL = {'red':'#ff4545', 'yellow':'#ffe645', 'R':'#ef4242', 'Y':'#ffe24b', '?':'#c4c7cb', '!':'#bb55de'}
SITES = {'origin':(1150,200,1490,420), 'right':(2150,1580,2390,1900),
         'bend':(1630,1520,1850,1840), 'left':(135,1000,345,1300),
         'bottom':(1310,2890,1630,3130)}
inputs = set()

def read(path):
    path = Path(path); inputs.add(path)
    return json.loads(path.read_text())

def csvread(path):
    inputs.add(path)
    return list(csv.DictReader(path.open()))

def save(path, obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def table(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def font(n=20):return ImageFont.truetype(FONT,n)

def text(d, xy, s, size=20, fill='white', backed=True):
    d.text(xy,s,font=font(size),fill=fill,stroke_width=2 if backed else 0,stroke_fill='#18202a')

def header(im, title, subtitle):
    d=ImageDraw.Draw(im);d.rectangle((0,0,im.width,88),fill='#172330')
    text(d,(16,10),title,27);text(d,(16,50),subtitle,21)

def ring(d,x,y,color,r=7):
    d.ellipse((x-r-1,y-r-1,x+r+1,y+r+1),outline='black',width=3)
    d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=2)

def cross(d,x,y,color='cyan',r=5):
    d.line((x-r,y-r,x+r,y+r),fill=color,width=2);d.line((x-r,y+r,x+r,y-r),fill=color,width=2)

def arrow(d,p,t,length=65,color='white',width=3):
    p=np.array(p);t=np.array(t);q=p+length*t;n=np.array([-t[1],t[0]])
    d.line([tuple(p),tuple(q)],fill=color,width=width)
    d.polygon([tuple(q),tuple(q-12*t+5*n),tuple(q-12*t-5*n)],fill=color)

def triple(k,n):
    """A display address, NOT a recovered neighbor walk; balanced +1 remainder."""
    signed=k if k<=n//2 else k-n
    b=(signed+3)//7
    return signed-7*b,0,b

def ts(t):return '('+','.join(f'{v:+d}' if v else '0' for v in t)+')'

def inside(r,box):return box[0]<=float(r['x'])<box[2] and box[1]<=float(r['y'])<box[3]

def raw_pair(photo,box,title,subtitle,mark,outpath,scale=3,gutter=0):
    w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale
    im=Image.new('RGB',(2*w+gutter,h+126),'#172330')
    raw=photo.crop(box).resize((w,h),Image.Resampling.NEAREST)
    im.paste(raw,(0,110));im.paste(raw,(w,110))
    d=ImageDraw.Draw(im)
    text(d,(12,8),title,24);text(d,(12,40),subtitle,18)
    text(d,(12,76),'RAW',20);text(d,(w+12,76),'ANNOTATED',20)
    def xy(x,y):return (w+(x-box[0])*scale,110+(y-box[1])*scale)
    layer=Image.new('RGBA',im.size,(0,0,0,0))
    mark(ImageDraw.Draw(layer),xy,w,h)
    # Keep raw panel, headings and pixels outside the crop unmarked.
    im.paste(layer.crop((w,110,im.width,110+h)),(w,110),layer.crop((w,110,im.width,110+h)))
    assert np.array_equal(np.asarray(im.crop((0,110,w,110+h))),np.asarray(raw))
    im.save(outpath)

def render(out):
    out.mkdir(parents=True,exist_ok=True)
    photo_path=ROOT/'beads-photo-2.jpg';inputs.add(photo_path)
    photo=Image.open(photo_path).convert('RGB')
    seed=read(ROOT/'photo2/spline-seed-r175.json')
    hist=read(SRC/'r255/historical-splines.json')
    assert hashlib.sha256((SRC/'r255/historical-splines.json').read_bytes()).hexdigest()==seed['original_provenance']['source_sha256']
    if out != SRC/'r255':(out/'historical-splines.json').write_bytes((SRC/'r255/historical-splines.json').read_bytes())
    cand=read(SRC/'r190/candidate-spline.json')
    base=SplineRope(seed['points'],View(),smoothing=seed['smoothing_rms_target_pixels'])
    alt=SplineRope(cand['points'],View(),smoothing=cand['smoothing_rms_target_pixels'])
    curve=base.seed_image_curve;u=base.u_table
    der=np.array(splev(u,base.tck,der=1)).T;tangent=der/np.linalg.norm(der,axis=1)[:,None]
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))]
    edges={k:np.array(hist[k+'_spline']) for k in ['outer','inner']}
    # Exact line/segment intersections of the saved sampled edge curves.
    def intersection(p,normal,poly):
        hits=[]
        for a,b in zip(poly[:-1],poly[1:]):
            v=b-a;matrix=np.column_stack((normal,-v))
            if abs(np.linalg.det(matrix))<1e-10:continue
            t,z=np.linalg.solve(matrix,a-p)
            if 0<=z<=1 and abs(t)<150:hits.append(t)
        return min(hits,key=abs) if hits else None
    sections=[]
    for site,box in SITES.items():
        center=np.array([(box[0]+box[2])/2,(box[1]+box[3])/2])
        j=int(np.argmin(np.linalg.norm(curve-center,axis=1)));p=curve[j];t=tangent[j];normal=np.array([-t[1],t[0]])
        a=intersection(p,normal,edges['inner']);b=intersection(p,normal,edges['outer'])
        assert a is not None and b is not None and a*b<0
        ends=[p+a*normal,p+b*normal]
        sections.append(dict(site=site,sample=j,center_x=p[0],center_y=p[1],tangent_x=t[0],tangent_y=t[1],inner_x=ends[0][0],inner_y=ends[0][1],outer_x=ends[1][0],outer_y=ends[1][1],inner_signed_distance=a,outer_signed_distance=b,width=abs(b-a),midpoint_offset=abs(a+b)/2,status='historical edge intersections; not verified silhouette width'))
    table(out/'cross-sections.csv',sections)
    table(out/'spline-samples.csv',[dict(sample=i,u=float(u[i]),arc_px=float(arc[i]),x=float(p[0]),y=float(p[1]),tx=float(tangent[i,0]),ty=float(tangent[i,1])) for i,p in enumerate(curve)])
    def lines(d,xy,comparison=False):
        for name,color in [('outer','#ffb34d'),('inner','#62ff8c')]:
            pts=[xy(*p) for p in edges[name]]
            # Dashed historical edges: uncertainty is categorical, not a confidence band.
            for i in range(0,len(pts)-3,6):d.line(pts[i:i+4],fill=color,width=2)
        d.line([xy(*p) for p in curve[::3]],fill='#00e5ff',width=2)
        if comparison:d.line([xy(*p) for p in alt.seed_image_curve[::3]],fill='#ed7aff',width=2)
        for s in sections:
            p=np.array([s['center_x'],s['center_y']]);t=np.array([s['tangent_x'],s['tangent_y']])
            d.line([xy(s['inner_x'],s['inner_y']),xy(s['outer_x'],s['outer_y'])],fill='white',width=2)
            arrow(d,xy(*p),t,length=60)
            text(d,xy(*(p+np.array([10,8]))),s['site']+f" {s['width']:.1f}px",18)
    im=photo.copy();lines(ImageDraw.Draw(im),lambda x,y:(x,y))
    header(im,'01 | Current seed centerline + historical edge splines','cyan: active seed | dashed orange/green: unvalidated outer/inner edges | white: tangent and section')
    im.save(out/'01-splines-whole.png')
    for site,box in SITES.items():
        raw_pair(photo,box,f'01 | {site}: centerline, edges and version comparison','cyan: active R175 | magenta: unadopted R190 | dashed edges: historical, uncertain',lambda d,xy,w,h:lines(d,xy,True),out/f'01-splines-{site}.png')
    distance=cKDTree(curve).query(alt.seed_image_curve)[0]
    # Observation status inventory: retain aliases in data, collapse identical rejected marks for display.
    accepted=csvread(SRC/'r252/accepted.csv');inv=read(SRC/'r252/inventory.json')
    for r in accepted:r['x']=float(r['x']);r['y']=float(r['y'])
    ambiguous=[dict(key=r['case_id'],x=r['xy'][0],y=r['xy'][1],status='ambiguous',reason=' | '.join(r['reasons'])) for r in inv['unresolved_cases']]
    rejected={}
    for r in inv['sources']:
        if r['disposition']=='rejected' and r['color'] in ['red','yellow']:
            key=tuple(r['original_xy']);rejected.setdefault(key,dict(key='',x=key[0],y=key[1],status='rejected',reason=r['decision_reason']))
            rejected[key]['key']+=';'+r['key']
    statuses=ambiguous+list(rejected.values());table(out/'withheld-candidates.csv',statuses)
    def observations(d,xy,label=False,box=None):
        for r in accepted:
            if box is not None and not inside(r,box):continue
            x,y=xy(r['x'],r['y']);ring(d,x,y,COL[r['color']])
            if label and (box is None or inside(r,box)):text(d,(x+9,y-20),r['observation_id'][5:],16,fill=COL[r['color']])
        for r in statuses:
            if box is not None and not inside(r,box):continue
            x,y=xy(r['x'],r['y'])
            if r['status']=='rejected':cross(d,x,y,'#fa75ff',8)
            else:d.polygon([(x,y-8),(x+8,y),(x,y+8),(x-8,y)],outline='#6be8ff',width=2)
    im=photo.copy();observations(ImageDraw.Draw(im),lambda x,y:(x,y))
    header(im,'02 | 310 trusted observed interiors: 151 red + 159 yellow','R/Y rings: trusted | cyan diamonds: 29 unresolved cases | magenta X: 2 rejected colored proposals')
    im.save(out/'02-trusted-whole.png')
    for site,box in SITES.items():
        raw_pair(photo,box,f'02 | {site}: trusted and withheld observations','Short labels omit C252- | positions are observed interiors, not fitted centers',lambda d,xy,w,h:observations(d,xy,True,box),out/f'02-trusted-{site}.png')
    models={m:read(SRC/f'r254/{m}-camera.json') for m in MODELS}
    assigns={m:read(SRC/f'r254/{m}-assignments.json') for m in MODELS}
    shift=np.array(models[PRIMARY]['p'][2:4]);registered=curve+shift
    table(out/'registered-centerline.csv',[dict(sample=i,x=float(p[0]),y=float(p[1]),translation_x=float(shift[0]),translation_y=float(shift[1])) for i,p in enumerate(registered)])
    im=photo.copy();d=ImageDraw.Draw(im)
    for name,color in [('outer','#ffb34d'),('inner','#62ff8c')]:
        pts=[tuple(p) for p in edges[name]]
        for i in range(0,len(pts)-3,6):d.line(pts[i:i+4],fill=color,width=2)
    d.line([tuple(p) for p in curve[::3]],fill='white',width=1)
    d.line([tuple(p) for p in registered[::3]],fill='#00e5ff',width=2)
    header(im,'01 | '+PRIMARY+' registered centerline','cyan: current fitted translation of seed | white: unshifted seed | dashed historical edges stay at original coordinates')
    im.save(out/'01-registered-centerline-whole.png')
    byaccepted={r['observation_id']:r for r in accepted};ledger=[];alternatives=[]
    for mid in MODELS:
        n=models[mid]['n']
        for r in assigns[mid]:
            t=triple(r['k'],n);a=byaccepted[r['observation_id']]
            ledger.append(dict(observation_id=r['observation_id'],color=r['color'],image_x=r['x'],image_y=r['y'],local_triple=ts(t),n1=t[0],diagonal_a_n6=t[1],diagonal_b_n7=t[2],triple_basis='canonical index address, not observed walk',bead_index=r['k'],model=mid,N=n,helicity=models[mid]['h'],generator_index=r['generator_index'],origin_generator_index=models[mid]['origin'],owns_representative=r['owns_representative'],patch_support=r['patch_support'],conditional_unique=r['conditional_unique'],split=r['split'],evidence_level=a['evidence_level'],source_keys=a['source_keys'],projected_center_x=r['projected_center'][0],projected_center_y=r['projected_center'][1]))
            for opt in r['alternatives']:
                alternatives.append(dict(observation_id=r['observation_id'],model=mid,bead_index=opt['k'],local_triple=ts(triple(opt['k'],n)),owns_representative=opt['owns_representative'],patch_support=opt['patch_support'],exact_audit_cost=opt['exact_audit_cost']))
    table(out/'observation-index-triples.csv',ledger);table(out/'assignment-alternatives.csv',alternatives)
    rr=assigns[PRIMARY];n=models[PRIMARY]['n']
    # One readable label per sector in the overview; all points marked and all rows in CSV.
    selected={min((r for r in rr if r['sector']==s),key=lambda r:abs(r['x']-1270))['observation_id'] for s in range(1,33)}
    selected.add('C252-A948')
    for kind,num in [('triple','04'),('index','05')]:
        im=photo.copy();d=ImageDraw.Draw(im)
        for r in rr:
            x,y=r['x'],r['y'];ring(d,x,y,COL[r['color']],5)
            if not r['owns_representative']:cross(d,x,y,'#fa75ff',8)
            if r['observation_id'] in selected:
                label=ts(triple(r['k'],n)) if kind=='triple' else str(r['k'])
                label+=(' ?' if not r['conditional_unique'] else '')+(' !' if not r['owns_representative'] else '')
                text(d,(x+12,y-27),label,20)
        header(im,f'{num} | {PRIMARY} | '+('(+1, +6, +7) canonical addresses' if kind=='triple' else 'Conditional bead_index k, origin C252-A948 = 0'),'33 selected labels; all 310 interiors marked | ? ambiguous assignment | ! failed ownership | no certified global indices')
        im.save(out/f'{num}-{kind}-whole.png')
        for site,box in SITES.items():
            local=sorted((r for r in rr if inside(r,box)),key=lambda r:(r['y'],r['x']))
            # Dense labels in a separate gutter; numbered keys keep photographic faces unobstructed.
            def mark(d,xy,w,h):
                for j,r in enumerate(local,1):
                    x,y=xy(r['x'],r['y']);ring(d,x,y,COL[r['color']],9)
                    text(d,(x+10,y-17),str(j),19,fill=COL[r['color']])
                    value=ts(triple(r['k'],n)) if kind=='triple' else 'k='+str(r['k'])
                    flags=(' ?' if not r['conditional_unique'] else '')+(' !' if not r['owns_representative'] else '')
                    text(d,(2*w+15,115+(j-1)*27),f'{j:02} {r["observation_id"][5:]}  {value}{flags}',18,fill=COL[r['color']])
            raw_pair(photo,box,f'{num} | {site} | {PRIMARY}',('Triples are algebraic addresses, not verified neighbor paths.' if kind=='triple' else 'k is modulo N; ? ambiguous assignment; ! failed ownership.'),mark,out/f'{num}-{kind}-{site}.png',scale=3,gutter=490)
    anchor=next(r for r in rr if r['observation_id']=='C252-A948')
    im=photo.copy();d=ImageDraw.Draw(im);ring(d,anchor['x'],anchor['y'],'#8aff76',35)
    text(d,(anchor['x']+50,anchor['y']-80),'C252-A948 = maker 20 = C | RED | k=0',27,fill='#8aff76')
    header(im,'03 | Origin location in the original photograph','Green ring marks an observed red interior; origin is a gauge choice, not a recovered manufacturing seam.')
    im.save(out/'03-origin-whole.png')
    def originmark(d,xy,w,h):
        x,y=xy(anchor['x'],anchor['y']);ring(d,x,y,'#8aff76',18)
        cx,cy=xy(*anchor['projected_center']);cross(d,cx,cy,'cyan',7);d.line((x,y,cx,cy),fill='white',width=2)
        text(d,(w+20,h+45),'C252-A948 | RED | maker 20 = C | k=0 | generator 2162',20)
    raw_pair(photo,(1270,230,1410,345),'03 | Index origin: C252-A948 = maker 20 = C','Green ring: observed interior (1346,273); cyan X: predicted physical center',originmark,out/'03-origin.png',scale=5)
    # Maker local chart: three counted direction families; remove redundant triangular cycle deterministically.
    chart=csvread(SRC/'r253/maker-local-chart.csv');chartrows=[]
    for r in chart:
        U,V=int(r['u']),int(r['v']);a=int(np.median([-U,0,V]));A=(U+a,a,V-a);B=(-A[0],A[2],A[1])
        assert A[0]+6*A[1]+7*A[2]==int(r['k_A'])
        assert B[0]+6*B[1]+7*B[2]==int(r['k_B'])
        chartrows.append(dict(maker_number=int(r['maker_number']),maker_observation_id=r['maker_observation_id'],x=float(r['x']),y=float(r['y']),u=U,v=V,triple_A=ts(A),k_A=int(r['k_A']),triple_B=ts(B),k_B=int(r['k_B']),basis='maker local graph; family assignment conditional'))
    table(out/'maker-local-triples.csv',chartrows)
    def chartmark(d,xy,w,h):
        for j,r in enumerate(chartrows):
            x,y=xy(r['x'],r['y']);ring(d,x,y,'#8aff76',7);text(d,(x+9,y-17),str(r['maker_number']),17)
            text(d,(2*w+12,113+j*27),f'{r["maker_number"]:02} A{r["triple_A"]}  B{r["triple_B"]}',17)
    raw_pair(photo,(1170,225,1445,365),'04 | Maker local graph: family A and family B alternatives','A: d1=+1, d2=+7, d3=+6 | B: d1=-1, d2=+6, d3=+7',chartmark,out/'04-maker-triples.png',scale=6,gutter=545)
    im=Image.new('RGB',(1450,670),'#172330');d=ImageDraw.Draw(im)
    text(d,(25,15),'Three directions, six signed neighbors | schematic only',28)
    p=np.array([300.,320.]);directions=[(np.array([1.,0]),'d1: +1', 'white'),(np.array([.5,-.866]),'d2: +7 (b)', '#00e5ff'),(np.array([-.5,-.866]),'d3: +6 (a)', '#ffb34d')]
    for t,label,c in directions:
        arrow(d,p,t,170,c,4);arrow(d,p,-t,170,c,3);q=p+190*t;text(d,tuple(q),label,22,fill=c)
    ring(d,*p,'#8aff76',12);text(d,(315,340),'origin',22)
    for i,s in enumerate(['Primary triple = (n1, a=n6, b=n7)', 'k = n1 + 6*a + 7*b  (mod N)', 'One +1 step + one +6 step = one +7 step.', '(1,1,0) and (0,0,1) name the same index.', '', 'Maker chart A: (u,v)=(n1-a, a+b)', 'Maker chart B swaps diagonals and reverses d1.', 'Same path: A(n1,a,b) -> B(-n1,b,a).', '', 'Global CSV triples encode tentative k only.', 'They do not prove photographed neighbor walks.']):text(d,(650,95+43*i),s,22)
    im.save(out/'04-direction-schematic.png')
    # Pattern panels: every residue labeled, all supporting observations in CSV and readable MD.
    allres=[];conflicts=[];patternstats={}
    for mid,P in [(PATTERN,382),(PRIMARY,337)]:
        rows=assigns[mid];groups=[[] for _ in range(P)]
        for r in rows:groups[r['k']%P].append(r)
        states=['?' if not g else '!' if len({r['color'] for r in g})>1 else g[0]['color'][0].upper() for g in groups]
        loss=sum(min(sum(r['color']=='red' for r in g),sum(r['color']=='yellow' for r in g)) for g in groups)
        patternstats[mid]=dict(P=P,minimum_conflicting_assignments=loss,states=dict(Counter(states)))
        assert models[mid]['n']%P==0 and P%13!=0 and P<400
        cell=48;columns=32;rows_n=math.ceil(P/columns)
        im=Image.new('RGB',(columns*cell+40,rows_n*71+155),'#172330');d=ImageDraw.Draw(im)
        text(d,(20,12),f'06 | {mid}, P={P} | REJECTED: {loss} contradictory assignments',25)
        text(d,(20,50),'R red-only | Y yellow-only | ? unobserved | ! conflicting red/yellow | residue labels are zero-based',20)
        for residue,(g,state) in enumerate(zip(groups,states)):
            x=20+(residue%columns)*cell;y=100+(residue//columns)*71
            d.rectangle((x,y,x+cell-3,y+39),fill=COL[state]);text(d,(x+14,y+4),state,21,fill='black',backed=False);text(d,(x+5,y+42),str(residue),16)
            allres.append(dict(model=mid,N=models[mid]['n'],P=P,residue=residue,status=state,red_observations=';'.join(r['observation_id'] for r in g if r['color']=='red'),yellow_observations=';'.join(r['observation_id'] for r in g if r['color']=='yellow'),observation_indices=';'.join(f'{r["observation_id"]}:{r["k"]}' for r in g),black_observations='',template_status='rejected diagnostic'))
        im.save(out/f'06-pattern-{mid}-P{P}.png')
        chosen=[i for i,s in enumerate(states) if s=='!'][:3]
        for residue in chosen:
            g=groups[residue]
            for color in ['red','yellow']:
                r=next(r for r in g if r['color']==color);x,y=r['x'],r['y'];box=(int(x)-65,int(y)-50,int(x)+65,int(y)+50)
                def mark(d,xy,w,h):
                    px,py=xy(x,y);ring(d,px,py,'#8aff76',17)
                    cx,cy=xy(*r['projected_center']);cross(d,cx,cy,'cyan',8)
                    text(d,(w+10,115),f'{color}: k={r["k"]}',20)
                    text(d,(w+10,145),f'{r["k"]} mod {P} = {residue}',20)
                name=f'06-conflict-{mid}-r{residue}-{color}.png'
                raw_pair(photo,box,f'{r["observation_id"]} | {color} | {mid}',f'Conflict residue {residue}: needs BOTH red and yellow; green = interior, cyan = model center',mark,out/name,scale=4)
                conflicts.append(dict(model=mid,P=P,residue=residue,observation_id=r['observation_id'],color=color,x=x,y=y,bead_index=r['k'],owns_representative=r['owns_representative'],patch_support=r['patch_support'],image=name))
    table(out/'pattern-residues.csv',allres);table(out/'conflict-witnesses.csv',conflicts)
    md=['# Every template residue and its observed evidence','', 'All templates below are rejected diagnostics. Empty support means unknown, never black.','']
    for mid in [PATTERN,PRIMARY]:
        md += [f'## {mid}', '', '| Residue | Status | Observations: bead_index (observed color) |','|---:|:---:|---|']
        for r in allres:
            if r['model']!=mid:continue
            g=[x for x in assigns[mid] if x['k']%r['P']==r['residue']]
            md.append(f"| {r['residue']} | {r['status']} | "+'; '.join(f"{x['observation_id']}: {x['k']} ({x['color']})" for x in g)+' |')
    (out/'PATTERN_RESIDUES.md').write_text('\n'.join(md)+'\n')
    save(out/'summary.json',dict(primary=PRIMARY,pattern_diagnostic=PATTERN,alternative=OTHER,photo_size=photo.size,observations=len(accepted),colors=dict(Counter(r['color'] for r in accepted)),cross_sections=sections,active_spline_image_length=arc[-1],candidate_to_active_nearest_curve_distance=dict(median=float(np.median(distance)),p95=float(np.percentile(distance,95)),maximum=float(max(distance)),interpretation='geometric separation, not accuracy or a confidence bound'),origin=anchor,patterns=patternstats,crop_boxes=SITES,full_photo_selected_labels=len(selected)))
    # Independent audit invariants across saved artifacts; no search/refit is called.
    for mid in MODELS:
        src=assigns[mid];m=models[mid]
        assert len(src)==310 and len({r['generator_index'] for r in src})==310
        assert {r['observation_id'] for r in src}==set(byaccepted)
        for r in src:
            a=byaccepted[r['observation_id']];assert r['color']==a['color'] and [r['x'],r['y']]==[a['x'],a['y']]
            t=triple(r['k'],m['n']);assert (t[0]+6*t[1]+7*t[2])%m['n']==r['k']
            assert (r['generator_index']-m['origin'])%m['n']==r['k']
    saved=csvread(SRC/'r254/residue-constraints.csv')
    for r in allres:
        old=next(x for x in saved if x['model_id']==r['model'] and int(x['P'])==r['P'] and int(x['residue'])==r['residue'])
        assert old['status']==r['status'] and old['red_observation_ids']==r['red_observations'] and old['yellow_observation_ids']==r['yellow_observations']
    for r in conflicts:assert r['bead_index']%r['P']==r['residue']
    for name in ['01-splines-whole.png','02-trusted-whole.png','04-triple-whole.png','05-index-whole.png']:assert Image.open(out/name).size==photo.size
    inputs.update([Path(__file__),ROOT/'photo2/tangent_circles.py',ROOT/'photo2/spline-provenance-r187.json',ROOT/'photo2/CENTERLINE_FIT_REVIEW.md'])
    save(out/'verification.json',dict(python=platform.python_version(),checks=['930 source identity/color/coordinate/index/triple rows checked','three one-to-one assignments preserved','719 residues independently reconstructed and exactly matched to R254','27 maker A/B chart weighted sums verified','all conflict witness residues checked','four whole overlays retain native 2540x3182 dimensions','all raw panels exactly equal nearest-neighbor crops of original pixels','historical edge source hash matches R175/R187 provenance'],source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name not in ['verification.json','INDEX.md','QUESTIONS.md']}))
    print(json.dumps(dict(patterns=patternstats,artifacts=len(list(out.iterdir())),ledger_rows=len(ledger),sections=sections),indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=SRC/'r255');args=parser.parse_args();render(args.output.resolve())

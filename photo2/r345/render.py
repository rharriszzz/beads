"""Deterministic R345 POV-Ray reconstruction. Run from any working directory."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math, re, struct, subprocess
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SIZE = np.array([2540, 3182])
N = 2704

def read(p):
    p=Path(p)
    return json.loads(gzip.open(p,'rt').read() if p.suffix=='.gz' else p.read_text())

def save(p,d):
    Path(p).write_text(json.dumps(d,indent=2,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else v.item(),allow_nan=False)+'\n')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unit(v): return v/np.linalg.norm(v,axis=-1,keepdims=True)
def vec(v): return '<'+','.join(f'{x:.17g}' for x in v)+'>'

def normalize_png(path):
    """Remove renderer dates without recompressing pixels or changing color tags."""
    path=Path(path);data=path.read_bytes();offset=8;chunks=[data[:8]]
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    while offset<len(data):
        count=struct.unpack('!I',data[offset:offset+4])[0];kind=data[offset+4:offset+8]
        payload=data[offset+8:offset+8+count]
        if kind!=b'tIME' and not (kind==b'tEXt' and payload.startswith(b'Comment\x00Render Date:')):
            chunks.append(data[offset:offset+count+12])
        offset+=count+12
    path.write_bytes(b''.join(chunks))

def fields(k,coef):
    f=np.asarray(k)/N
    out=np.zeros_like(f,dtype=float)+coef[0]
    for j in range(1,(len(coef)+1)//2):
        out+=coef[2*j-1]*np.sin(2*np.pi*j*f)+coef[2*j]*np.cos(2*np.pi*j*f)
    return out

class Model:
    def __init__(self,c):
        self.c=c;self.scale=c['pixels_per_unit'];e=np.radians(c['camera_elevation_deg'])
        self.right=np.array([1.,0,0]);self.down=np.array([0,-np.sin(e),-np.cos(e)])
        self.eye=np.cross(self.right,-self.down)
        self.r=c['bead_radius'];self.height=c['minor_radius']+self.r+.03
        image=np.array(read(ROOT/c['centerline'])['points']);image[-1]=image[0]
        self.image=image
        plane=self.inverse(image,self.height)
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
        # Saved dense spline, interpolated periodically; physical arc reintegrated.
        raw=CubicSpline(arc,plane,bc_type='periodic')
        fine=np.linspace(0,arc[-1],65537);q=raw(fine)
        true=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))]
        self.length=true[-1];self.table=true;self.parameters=fine;self.raw=raw
    def inverse(self,xy,z):
        xy=(np.asarray(xy)-(SIZE-1)/2)/self.scale
        return np.c_[xy[:,0],-(xy[:,1]+np.cos(np.radians(self.c['camera_elevation_deg']))*z)/np.sin(np.radians(self.c['camera_elevation_deg'])),np.full(len(xy),z)]
    def project(self,p):
        return np.c_[np.asarray(p)@self.right,np.asarray(p)@self.down]*self.scale+(SIZE-1)/2
    def geometry(self,k):
        k=np.atleast_1d(k).astype(float)
        fraction=(k/N+fields(k,self.c['station_fraction_coefficients']))%1
        u=np.interp(fraction*self.length,self.table,self.parameters)
        line=self.raw(u);t=unit(self.raw(u,1));normal=np.cross(np.array([0,0,1.]),t)
        phi=self.c['helicity']*2*np.pi*self.c['minor_turns']*k/N+fields(k,self.c['phase_radian_coefficients'])
        radial=np.sin(phi)[:,None]*normal+np.cos(phi)[:,None]*[0,0,1.]
        centers=line+self.c['minor_radius']*radial
        # Crochet holes are transported centerline tangent, not string-trajectory tangent.
        tilt=np.radians(self.c['hole_axis_tilt_deg'])
        circum=np.cos(phi)[:,None]*normal-np.sin(phi)[:,None]*[0,0,1.]
        axis=unit(np.cos(tilt)*t+np.sin(tilt)*circum)
        ex=unit(np.cross(axis,radial));ez=np.cross(ex,axis)
        return dict(k=k,line=line,tangent=t,normal=normal,radial=radial,phi=phi,centers=centers,axis=axis,ex=ex,ez=ez)
    def proxy(self,k):
        g=self.geometry(k)
        # Support is on glass, never assumed a physical center or calibrated highlight.
        return self.project(g['centers']+self.c['support_proxy_radius_fraction']*self.r*g['radial'])

def observations(c=None):
    d=read(ROOT/(c or {}).get('indexed_graph','photo2/r344/graph.json.gz'));o={r['id']:r for r in d['observations']}
    co=sorted(d['coordinates'],key=lambda r:r['id'])
    k=np.array([(7*r['ab'][0]+6*r['ab'][1])%N for r in co])
    xy=np.array([o[r['id']]['xy'] for r in co])
    return co,k,xy

def calibrate(c):
    """Geometry only: fixed count, spline, sequence and A identities. No color input."""
    co,k,xy=observations(c)
    # Origin from nearest axis station; clockwise source trace already agrees with +A.
    m=Model(c);_,ix=cKDTree(m.image).query(xy)
    origin=np.angle(np.mean(np.exp(2j*np.pi*(m.table[np.minimum(ix*8,len(m.table)-1)]/m.length-k/N))))/(2*np.pi)
    # Use the exact source chord arc for a reliable initialization.
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(m.image,axis=0),axis=1))]
    origin=np.angle(np.mean(np.exp(2j*np.pi*(arc[ix]/arc[-1]-k/N))))/(2*np.pi)
    stages=[]
    # Smooth periodic fields, shared by all beads; no per-bead offsets/centerline edits.
    for degree in [0,3,5]:
        count=1+2*degree
        sc=np.zeros(count);pc=np.zeros(count)
        sc[:min(count,len(c['station_fraction_coefficients']))]=c['station_fraction_coefficients'][:count]
        pc[:min(count,len(c['phase_radian_coefficients']))]=c['phase_radian_coefficients'][:count]
        if degree==0:sc[0]=origin;pc[0]=-.5
        v=np.r_[sc,pc]
        def residual(v):
            c['station_fraction_coefficients']=v[:count].tolist();c['phase_radian_coefficients']=v[count:].tolist()
            errors=(m.proxy(k)-xy).ravel()
            regular=np.r_[v[1:count]*6000,v[count+1:]*2]
            return np.r_[errors,regular]
        fit=least_squares(residual,v,max_nfev=120,loss='soft_l1',f_scale=10,
                          bounds=(np.r_[origin-.02,np.full(count-1,-.008),-np.pi,np.full(count-1,-3)],
                                  np.r_[origin+.02,np.full(count-1,.008),np.pi,np.full(count-1,3)]))
        residual(fit.x);err=np.linalg.norm(m.proxy(k)-xy,axis=1)
        stages.append(dict(harmonic_degree=degree,rms_px=float(np.sqrt(np.mean(err**2))),median_px=float(np.median(err)),p95_px=float(np.percentile(err,95)),nfev=fit.nfev,station=c['station_fraction_coefficients'],phase=c['phase_radian_coefficients']))
    c['calibration']=dict(policy='Robust fit to 1041 frozen bright-support coordinates, not centers; geometry only. Degree5 smooth periodic station/phase fields; no per-bead corrections.',stages=stages)
    return c

def sdf(local,c):
    r=c['bead_radius'];minor=.43*r;extra=.2*minor;rounding=.8*minor
    qr=np.abs(np.hypot(local[...,0],local[...,2])-.57*r)-extra
    qa=np.abs(local[...,1])/(c['height_ratio']/.43)-extra
    return np.hypot(np.maximum(qr,0),np.maximum(qa,0))+np.minimum(np.maximum(qr,qa),0)-rounding

def profile(c,steps=12,azimuths=48):
    r=c['bead_radius'];mi=.43*r;rr=.8*mi;extra=.2*mi;st=c['height_ratio']/.43
    q=np.linspace(0,2*np.pi,steps*4,endpoint=False)
    # Rounded rectangle in (radial, compressed axial), exact surface including bore.
    rho=.57*r+np.sign(np.cos(q))*extra+rr*np.cos(q)
    y=st*(np.sign(np.sin(q))*extra+rr*np.sin(q))
    az=np.linspace(0,2*np.pi,azimuths,endpoint=False)
    return np.stack([rho[:,None]*np.cos(az),np.broadcast_to(y[:,None],(len(q),len(az))),rho[:,None]*np.sin(az)],axis=-1).reshape(-1,3)

def validate(m,out):
    c=m.c;g=m.geometry(np.arange(N));end=m.geometry([0,N]);r=m.r
    frames=np.stack([g['ex'],g['axis'],g['ez']],axis=1)
    spacing={}
    for d in [1,6,7]:
        dist=np.linalg.norm(np.roll(g['centers'],-d,axis=0)-g['centers'],axis=1)
        spacing[str(d)]={name:float(v) for name,v in zip(['min','mean','max','cv'],[dist.min(),dist.mean(),dist.max(),dist.std()/dist.mean()])}
    # Filled rounded-bead support separations certify many pairs; sampled exact
    # surfaces inside the other's actual glass demonstrate penetration otherwise.
    surface=profile(c);bound=r*np.sqrt(1+c['height_ratio']**2)
    pairs=sorted(cKDTree(g['centers']).query_pairs(2*bound));rows=[];witnesses=[];certificates=[]
    for a,b in pairs:
        delta=g['centers'][b]-g['centers'][a];normal=unit(delta)
        def support(j):
            ax=abs(normal@g['axis'][j]);rad=np.sqrt(max(0,1-ax*ax));mi=.43*r
            return .57*r*rad+.2*mi*(rad+ax*c['height_ratio']/.43)+.8*mi*np.hypot(rad,ax*c['height_ratio']/.43)
        margin=np.linalg.norm(delta)-support(a)-support(b)
        if margin<=1e-6:
            # A plane need not be perpendicular to the center displacement.
            # Search a deterministic fan toward the average transported hole axis.
            axis=unit(g['axis'][a]+g['axis'][b]);axis*=np.sign(axis@delta)
            normals=unit(np.array([(1-v)*normal+v*axis for v in np.linspace(0,1,17)]))
            def supports(j):
                axial=abs(normals@g['axis'][j]);radial=np.sqrt(np.maximum(0,1-axial**2))
                mi=.43*r;st=c['height_ratio']/.43
                return .57*r*radial+.2*mi*(radial+st*axial)+.8*mi*np.hypot(radial,st*axial)
            margins=normals@delta-supports(a)-supports(b)
            best=margins.argmax()
            if margins[best]>margin:margin=float(margins[best]);normal=normals[best]
        if margin>1e-6:
            certificates.append(dict(a=a,b=b,normal=normal.tolist(),margin=float(margin)))
            continue
        worst=0.;point=None
        for i,j in [(a,b),(b,a)]:
            world=surface@frames[i]+g['centers'][i]
            local=(world-g['centers'][j])@frames[j].T
            values=sdf(local,c);jmin=values.argmin()
            if values[jmin]<worst:worst=float(values[jmin]);point=world[jmin].tolist()
        state='sampled-glass-penetration' if worst<-.005*r else 'unresolved-envelope-overlap'
        rows.append(dict(a=a,b=b,state=state,separating_center_plane_margin=float(margin),minimum_implicit_value=worst,point=point))
        if point is not None:witnesses.append(worst)
    # Gap brackets: a separating margin is a lower bound, while the distance
    # between two actual supporting glass points is a constructive upper bound.
    def supporting_point(i,n):
        local=frames[i]@n;transverse=np.hypot(local[0],local[2]);st=c['height_ratio']/.43
        denominator=np.hypot(transverse,st*local[1]);rho=.656*r+.344*r*transverse/denominator
        axial=np.sign(local[1])*(.086*r*st+.344*r*st*st*abs(local[1])/denominator)
        p=np.array([rho*local[0]/transverse,axial,rho*local[2]/transverse]) if transverse>1e-14 else np.array([rho,axial,0.])
        assert abs(sdf(p,c))<1e-8
        return p@frames[i]+g['centers'][i]
    for q in certificates:
        a,b=q['a'],q['b'];n=np.array(q['normal'])
        q['glass_gap_upper_bound']=float(np.linalg.norm(supporting_point(a,n)-supporting_point(b,-n)))
    gaps={}
    for step in [1,6,7]:
        group=[q for q in certificates if min((q['b']-q['a'])%N,(q['a']-q['b'])%N)==step]
        if group:gaps[str(step)]=dict(pairs=len(group),minimum_lower_bound=min(q['margin'] for q in group),median_upper_bound=float(np.median([q['glass_gap_upper_bound'] for q in group])),maximum_upper_bound=max(q['glass_gap_upper_bound'] for q in group))
    save(out/'contacts.json',dict(bound_candidates=len(pairs),certificates=certificates,nonseparated_pairs=rows,gap_brackets=gaps,policy='Positive separating-plane filled-profile support margin certifies separation; constructive glass-point distances bound gaps above. Negative exact hollow SDF on sampled surface demonstrates penetration. Other cases unresolved, never declared safe.'))
    co,k,xy=observations(c);err=np.linalg.norm(m.proxy(k)-xy,axis=1)
    with (out/'projected-support-errors.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['id','k','observed_x','observed_y','predicted_proxy_x','predicted_proxy_y','distance_px'])
        for rec,ki,q,p,e in zip(co,k,xy,m.proxy(k),err):w.writerow([rec['id'],ki,*q,*p,e])
    near=cKDTree(m.image).query(xy)[0]
    densek=np.linspace(0,N,50001);fraction=densek/N+fields(densek,c['station_fraction_coefficients']);phase=c['helicity']*2*np.pi*c['minor_turns']*densek/N+fields(densek,c['phase_radian_coefficients'])
    pattern_length=len(read(ROOT/c['pattern_file'])['provisional_sequence'])
    v=dict(physical_beads=N,pattern_length=pattern_length,repeats=N//pattern_length,minor_turns=c['minor_turns'],
        position_closure_error=float(np.linalg.norm(end['centers'][1]-end['centers'][0])),
        axis_closure_error=float(np.linalg.norm(end['axis'][1]-end['axis'][0])),
        phase_turns=float((end['phi'][1]-end['phi'][0])/(2*np.pi)),
        frame_orthogonality_error=float(np.max(abs(frames@frames.transpose(0,2,1)-np.eye(3)))),
        frame_determinant_error=float(np.max(abs(np.linalg.det(frames)-1))),
        minimum_station_derivative=float(np.min(np.diff(fraction)/np.diff(densek))),
        minimum_signed_phase_derivative=float(np.min(c['helicity']*np.diff(phase)/np.diff(densek))),
        spline_length=m.length,spline_position_closure=float(np.linalg.norm(m.raw(0)-m.raw(m.parameters[-1]))),
        spline_tangent_closure=float(np.linalg.norm(m.raw(0,1)-m.raw(m.parameters[-1],1))),
        centerline_height=m.height,conservative_bounding_sphere_height=float(np.min(g['centers'][:,2])-bound),
        spacing=spacing,glass_gap_brackets=gaps,bounding_neighbor_pairs=len(pairs),nonseparated_pairs=len(rows),
        demonstrated_penetrations=sum(x['state']=='sampled-glass-penetration' for x in rows),
        certified_separations=len(certificates),minimum_separating_plane_margin=min((x['margin'] for x in certificates),default=0.),
        maximum_sampled_implicit_depth=float(-min(witnesses,default=0)),
        last_to_first_center_distance=float(np.linalg.norm(g['centers'][-1]-g['centers'][0])),
        projected_support_proxy=dict(n=len(k),rms_px=float(np.sqrt(np.mean(err**2))),median_px=float(np.median(err)),p95_px=float(np.percentile(err,95)),maximum_px=float(err.max()),warning='Bright-support to approximate outer-glass proxy, not center/contour or independent camera error.'),
        reference_axis_to_bright_support_median_px=float(np.median(near)))
    # Exact lowest surface height (linear support), includes tilted holes.
    axial=np.abs(g['axis'][:,2]);radial=np.sqrt(1-axial**2);mi=.43*r;st=c['height_ratio']/.43
    support=.57*r*radial+.2*mi*(radial+st*axial)+.8*mi*np.hypot(radial,st*axial)
    v['minimum_glass_height']=float(np.min(g['centers'][:,2]-support))
    assert v['position_closure_error']<1e-8 and v['axis_closure_error']<1e-8
    assert v['frame_orthogonality_error']<1e-12 and v['minimum_station_derivative']>0 and v['minimum_signed_phase_derivative']>0
    assert v['minimum_glass_height']>=0
    save(out/'validation.json',v)
    return v

def generate(m,out):
    c=m.c;pattern=read(ROOT/c['pattern_file']);seq=pattern['provisional_sequence'];period=len(seq)
    assert N%period==0 and N/c['beads_per_minor_turn']==c['minor_turns']
    source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')].rstrip()+'\n'
    (out/'shape.inc').write_text('// Generated verbatim from beads.pov bead macro.\n'+macro)
    g=m.geometry(np.arange(N));lines=[];records=[]
    for k in range(N):
        mat={'R':0,'Y':1,'B':2}[seq[k%period]]
        matrix=np.r_[g['ex'][k],g['axis'][k],g['ez'][k],g['centers'][k]]
        lines.append(f'// physical k={k} residue={k%period} color={seq[k%period]}\nobject {{ GlassBeads[{mat}] matrix <'+','.join(f'{v:.12g}' for v in matrix)+'> }')
        records.append(dict(k=k,residue=k%period,color=seq[k%period],strict=pattern['strict_sequence'][k%period],tentative=pattern['entries'][k%period]['tentative'],center=g['centers'][k].tolist(),hole_axis=g['axis'][k].tolist(),matrix=matrix.tolist()))
    (out/'beads.inc').write_text('\n'.join(lines)+'\n');save(out/'beads.json',records)
    paper=m.inverse(np.array(c['paper_corners_image']),0)
    verts=np.r_[paper,paper[:1]]
    glass=c['glass']
    scene=f'''// R345; generated by render.py, world units are an arbitrary physical scale.
global_settings {{ assumed_gamma 1 max_trace_level 12 ambient_light rgb <.65,.68,.75> }}
#declare bead_radius={m.r:.14g};
#declare hole_size_per_bead_size={c['hole_radius_fraction']};
#include "shape.inc"
camera {{ orthographic location {vec(m.eye*10000)} direction {vec(-m.eye)}
 right {vec(m.right*SIZE[0]/m.scale)} up {vec(-m.down*SIZE[1]/m.scale)} }}
background {{ rgb <.45,.30,.37> }}
// Shared rounded glass geometry for every pigment; only optics change.
#macro Glass(C,F)
 material {{ texture {{ pigment {{ color srgbft <C.x,C.y,C.z,F,0> }}
 finish {{ ambient {glass['ambient']} diffuse {glass['diffuse']} specular {glass['specular']} roughness {glass['roughness']}
 reflection {{ {glass['reflection_min']},{glass['reflection_max']} fresnel on }} conserve_energy }} }}
 interior {{ ior {glass['ior']} fade_distance {glass['fade_distance']} fade_power 1 fade_color rgb C }} }}
#end
#declare GlassBeads=array[3];
#declare GlassBeads[0]=bead(Glass({vec(glass['colors']['R']['srgb'])},{glass['colors']['R']['filter']}),.8,{c['height_ratio']},1);
#declare GlassBeads[1]=bead(Glass({vec(glass['colors']['Y']['srgb'])},{glass['colors']['Y']['filter']}),.8,{c['height_ratio']},1);
#declare GlassBeads[2]=bead(Glass({vec(glass['colors']['B']['srgb'])},{glass['colors']['B']['filter']}),.8,{c['height_ratio']},1);
light_source {{ {vec(c['light_position'])} color rgb {c['light_intensity']}
 area_light <75,0,0>,<0,75,0>,5,5 adaptive 1 circular orient }}
light_source {{ <-250,150,500> color rgb .13 shadowless }}
// Paper is a finite geometric prism with a measured appearance, no image map.
prism {{ linear_sweep linear_spline -0.025,0,{len(verts)},
'''
    # POV prism height is y; rotate to world z using matrix x->x y->z z->-y.
    scene+=',\n'.join('<'+f'{v[0]:.12g},{-v[1]:.12g}'+ '>' for v in verts)
    scene+='\n matrix <1,0,0, 0,0,1, 0,-1,0, 0,0,0>\n'
    scene+=f' texture {{ pigment {{ color srgb {vec(c["paper_srgb"])} }} finish {{ ambient .22 diffuse .84 }} normal {{ bumps .10 scale .16 }} }} }}\n'
    scene+='#include "beads.inc"\n'
    (out/'scene.inc').write_text(scene)
    (out/'scene.pov').write_text('#version 3.7;\n#declare R345=1;\n#include "beads.pov"\n')
    inputs=['beads-photo-2.jpg',c['pattern_file'],c['indexed_graph'],c['centerline'],'photo2/spline-provenance-r187.json','beads.pov','photo2/r345/render.py','photo2/r345/verify.py','photo2/r345/replay.py']
    save(out/'provenance.json',dict(source_commit=c['source_commit'],source_files={p:sha(ROOT/p) for p in inputs},renderer=subprocess.run(['povray','-version'],capture_output=True,text=True).stderr,configuration=c,pattern_metadata=pattern,assumptions=['N2704, 13x208, 6.5 beads/turn and 416 minor turns selected, conditional','R282 sampled R175/R187 image-only centerline proxy; no subsequently accepted physical centerline','Paper boundaries outside photograph; finite oversize sheet','Orthographic elevation80deg is reconstruction approximation, not calibrated camera','Common annular glass geometry; no color-dependent scale or photographic image maps']))

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n=22):return ImageFont.truetype(FONT,n)
def panel(im,title,width=762):
    im=im.convert('RGB');h=round(im.height*width/im.width);im=im.resize((width,h),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(width,h+44),'#faf7f2');canvas.paste(im,(0,44));ImageDraw.Draw(canvas).text((12,10),title,font=font(18),fill='#202830');return canvas

def diagnostics(m,out):
    original=Image.open(ROOT/m.c['photograph']).convert('RGB');render=Image.open(out/'render.png').convert('RGB').resize(tuple(SIZE),Image.Resampling.LANCZOS)
    a=panel(original,f'Photograph — {SIZE[0]} × {SIZE[1]}');b=panel(render,f'POV-Ray — {N} beads, provisional R344')
    comp=Image.new('RGB',(a.width*2,a.height));comp.paste(a,(0,0));comp.paste(b,(a.width,0));comp.save(out/'comparison.jpg',quality=94)
    # Transparent sampled profile hulls, before occlusion. These are diagnostic
    # envelopes, not measured photographic contours or silhouettes of holes.
    layer=Image.new('RGBA',tuple(SIZE),(0,0,0,0));d=ImageDraw.Draw(layer);g=m.geometry(np.arange(N));surf=profile(m.c,steps=5,azimuths=24)
    for k in range(N):
        if g['radial'][k]@m.eye<.15:continue
        frame=np.stack([g['ex'][k],g['axis'][k],g['ez'][k]])
        xy=m.project(surf@frame+g['centers'][k]);# envelope hull used only for alignment overlay
        from scipy.spatial import ConvexHull
        hull=xy[ConvexHull(xy).vertices];d.line([tuple(p) for p in np.r_[hull,hull[:1]]],fill=(0,245,245,155),width=1)
    d.line([tuple(p) for p in m.image],fill=(255,255,255,220),width=2)
    layer.save(out/'geometry-transparent.png');Image.alpha_composite(original.convert('RGBA'),layer).convert('RGB').save(out/'geometry-overlay.jpg',quality=95)
    crops=m.c.get('comparison_crops',{'straight':(2080,1040,2320,1450),'bend':(1550,1380,1830,1810),'reference':(1190,220,1430,400),'lower-bend':(1130,2840,1540,3120)})
    for name,box in crops.items():
        ims=[panel(im.crop(box),title,560) for im,title in [(original,'Photograph'),(render,'POV-Ray'),(Image.alpha_composite(original.convert('RGBA'),layer),'Projected geometry envelope')]]
        canvas=Image.new('RGB',(sum(im.width for im in ims),max(im.height for im in ims)),'#faf7f2')
        for j,im in enumerate(ims):canvas.paste(im,(j*560,0))
        canvas.save(out/f'crop-{name}.jpg',quality=95)
    # Indices and winding shown on actual visible geometry near reference.
    diag=render.convert('RGBA');draw=ImageDraw.Draw(diag);xy=m.project(g['centers']);seq=read(ROOT/m.c['pattern_file']);period=len(seq['provisional_sequence'])
    for k in range(N):
        if seq['entries'][k%period]['tentative'] and g['radial'][k]@m.eye>.3:
            x,y=xy[k];draw.ellipse((x-12,y-12,x+12,y+12),outline='#4fe7ff',width=2)
    for k in range(0,N,period):
        x,y=m.project(g['line'][k:k+1])[0];draw.text((x+12,y),str(k),font=font(21),fill='white',stroke_width=2,stroke_fill='black')
    diag.convert('RGB').save(out/'indices-full.jpg',quality=95)
    box=(1180,210,1460,410);detail=render.crop(box).resize((1120,800));dd=ImageDraw.Draw(detail)
    def point(k):return tuple((xy[k]-box[:2])*4)
    for i,j,col in [(0,1,'#12ccfb'),(0,6,'#43f180'),(0,7,'#ff75ef')]:
        p,q=point(i),point(j);dd.line([p,q],fill=col,width=5);v=np.array(p)-q;v=unit(v);perp=np.array([-v[1],v[0]]);qq=np.array(q);dd.polygon([q,tuple(qq+v*18+perp*7),tuple(qq+v*18-perp*7)],fill=col)
    for k in range(0,14):
        if g['radial'][k]@m.eye>0:
            p=point(k);dd.text(p,str(k),font=font(24),fill='white',stroke_width=2,stroke_fill='black')
    detail=panel(detail,f'Projected centers: cyan +1 string winding; green +6; pink +7; helicity {m.c["helicity"]:+d}',1120);detail.save(out/'helicity-detail.png')

def render_pov(out,width=1270,height=1591,name='render',extra=None):
    cmd=['povray','+I'+str(out/'scene.pov'),'+O'+str(out/(name+'.png')),'+L'+str(ROOT),'+L'+str(out),f'+W{width}',f'+H{height}','+FN','-D','+A0.18','+AM2','+R2','-J','+WT4']+(extra or [])
    with (out/(name+'.log')).open('w') as log:
        p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    logfile=out/(name+'.log')
    logtext=re.sub(r'Rendered[^\r\n]*(?:[\r\n]|$)','',logfile.read_text())
    logfile.write_text('\n'.join(line.rstrip() for line in logtext.splitlines()).rstrip()+'\n')
    p.check_returncode();normalize_png(out/(name+'.png'));return cmd

def main():
    global N,SIZE
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=HERE/'config.json');ap.add_argument('--output',type=Path,default=HERE/'output');ap.add_argument('--calibrate',action='store_true');ap.add_argument('--generate-only',action='store_true');ap.add_argument('--width',type=int,default=2540);ap.add_argument('--height',type=int,default=3182);args=ap.parse_args()
    c=read(args.config);N=c['total_beads'];SIZE=np.array(c['image_size'])
    if args.calibrate:c=calibrate(c);save(args.config,c)
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);m=Model(c);generate(m,out);v=validate(m,out)
    print(json.dumps(v,indent=2),flush=True)
    if not args.generate_only:
        cmd=render_pov(out,args.width,args.height);diagnostics(m,out);save(out/'render-receipt.json',dict(command=cmd,render_sha256=sha(out/'render.png'),width=args.width,height=args.height,png_date_metadata_removed=True))

if __name__=='__main__': main()

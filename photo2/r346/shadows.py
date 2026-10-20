"""Whole-necklace paper-shadow metrology and one shared POV-Ray light."""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,os,re,subprocess,sys
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy import ndimage as ndi
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares
from PIL import Image,ImageDraw,ImageFont
from photo2.r345.render import Model,read,save as save_json,sha,vec,normalize_png
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=HERE/'output';OUT.mkdir(exist_ok=True)
BASE=ROOT/'photo2/r345/output';W,H=2540,3182
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def save(path,value):
    def clean(v):
        if isinstance(v,np.ndarray):return clean(v.tolist())
        if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)):return [clean(x) for x in v]
        if isinstance(v,(float,np.floating)) and not np.isfinite(v):return None
        return v
    value=clean(value)
    if Path(path).suffix=='.gz':
        text=json.dumps(value,indent=2,allow_nan=False)+'\n'
        Path(path).write_bytes(__import__('gzip').compress(text.encode(),mtime=0))
    else:save_json(path,value)
def font(n):return ImageFont.truetype(FONT,n)
def linear(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def rgb(path):return np.asarray(Image.open(path).convert('RGB'),float)/255

def stations(count=96):
    c=read(ROOT/'photo2/r345/config.json');m=Model(c);p=m.image;arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];p[-1]=p[0];s=CubicSpline(arc,p,bc_type='periodic');a=(np.arange(count)+.5)*arc[-1]/count;pts=s(a);t=s(a,1);t/=np.linalg.norm(t,axis=1)[:,None]
    return [dict(station=i,arc=float(aa),point=q.tolist(),tangent=tt.tolist(),normal=[-tt[1],tt[0]]) for i,(aa,q,tt) in enumerate(zip(a,pts,t))]

def sample(array,xy):
    xy=np.asarray(xy);return ndi.map_coordinates(array,[xy[...,1],xy[...,0]],order=1,mode='constant',cval=np.nan)

def measure():
    im=rgb(ROOT/'beads-photo-2.jpg');gray=im@np.array([.2126,.7152,.0722]);smooth=ndi.gaussian_filter(gray,1.1);gy,gx=np.gradient(smooth);edge=np.hypot(gx,gy)
    rows=[];lanes=np.arange(-18,19,3);radius=np.arange(15,151,dtype=float)
    for st in stations():
        for side in [-1,1]:
            q=np.array(st['point']);t=np.array(st['tangent']);n=side*np.array(st['normal']);xy=q+lanes[:,None,None]*t+radius[None,:,None]*n
            e=sample(edge,xy);bounds=[];valids=[]
            for threshold in [.026,.034,.044]:
                bb=[]
                for ee in e:
                    eligible=(radius>=24)&(radius<=68)&(ee>threshold)
                    # Last substantial steep edge, rather than the dark shadow toe.
                    run=ndi.binary_closing(eligible,iterations=1)
                    ids=np.flatnonzero(run)
                    if len(ids):bb.append(radius[ids[-1]])
                bounds.append(float(np.percentile(bb,75)) if bb else 70.)
                valids.append(len(bb))
            bound=bounds[1];unc=max(3.,np.ptp(bounds));eligible=bool(unc<=8 and valids[1]>=9 and bound<65)
            row=dict(st,side=side,outward=n.tolist(),edge_radius=bound,edge_alternatives=bounds,edge_uncertainty=unc,boundary_lanes=valids[1],eligible=eligible,id=f"S{st['station']:02d}{'p' if side==1 else 'm'}",split='validation' if st['station']%4==0 else 'fit')
            rows.append(row)
    save(OUT/'observations.json',dict(photo_sha256=sha(ROOT/'beads-photo-2.jpg'),policy='All96 uniform image-arclength stations, both sides. Boundary finding uses only grayscale steep-edge energy, never pigment labels/chroma. Grayscale boundaries uncertain; threshold sensitivity and all rejected profiles retained. Tangential lanes +/-18px, boundary75th percentile; paper starts beyond conservative edge+uncertainty+2px.',rows=rows))
    atlas(im,rows,OUT/'boundary-atlas.jpg')
    print('boundaries',len(rows),'eligible',sum(r['eligible'] for r in rows),flush=True)
    return rows

def atlas(im,rows,path):
    # One tile per station, all points and both side edges displayed on native pixels.
    tiles=[]
    for j in range(96):
        rs=rows[2*j:2*j+2];q=np.array(rs[0]['point']);x,y=np.rint(q).astype(int);box=(x-115,y-115,x+116,y+116);tile=Image.fromarray(np.uint8(np.clip(im,0,1)*255)).crop(box);d=ImageDraw.Draw(tile)
        for r in rs:
            p=q+r['edge_radius']*np.array(r['outward'])-[box[0],box[1]];t=np.array(r['tangent']);d.line([tuple(p-20*t),tuple(p+20*t)],fill='cyan' if r['eligible'] else 'orange',width=2)
            z=p+50*np.array(r['outward']);d.line([tuple(p),tuple(z)],fill='white',width=1)
        canvas=Image.new('RGB',(231,254),'white');canvas.paste(tile,(0,23));ImageDraw.Draw(canvas).text((5,3),f"{j:02d} edges {rs[0]['edge_radius']:.0f}/{rs[1]['edge_radius']:.0f}",font=font(14),fill='black');tiles.append(canvas)
    sheet=Image.new('RGB',(231*8,254*12),'white')
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%8)*231,(i//8)*254))
    sheet.save(path,quality=95)

def profile_metrics(distance,deficit):
    d=np.asarray(distance);v=np.asarray(deficit);ok=np.isfinite(v);d=d[ok];v=v[ok]
    if len(v)<15 or np.sum((d>=4)&(d<=100))<3:return dict(reliable=False)
    v=ndi.gaussian_filter1d(v,1.5);peak=float(np.max(v[(d>=4)&(d<=100)]));i=int(np.argmax(np.where((d>=4)&(d<=100),v,-np.inf)))
    # Trailing edge after near-edge peak; crossings are linearly interpolated.
    def crossing(level):
        z=np.flatnonzero((np.arange(len(v))>i)&(v<=level))
        if not len(z):return None
        j=int(z[0]);return float(np.interp(level,[v[j],v[j-1]],[d[j],d[j-1]]))
    ten=crossing(.1*peak) if peak>.04 else None;ninety=crossing(.9*peak) if peak>.04 else None
    absolute=crossing(.05) if peak>.05 else 0.
    near=v[(d>=12)&(d<=20)]
    return dict(reliable=bool(peak>.08 and ten is not None and ninety is not None),peak_darkness=peak,extent_5percent_px=absolute,penumbra_10_90_px=(ten-ninety) if ten is not None and ninety is not None else None,near_edge_darkness=float(np.median(near)) if len(near) else None,peak_distance_px=float(d[i]),extent_censored=bool(peak>.05 and absolute is None),extent_lower_bound_px=float(d[-1]) if peak>.05 and absolute is None else None,integrated_darkness_px=float(np.trapezoid(np.maximum(v,0),d)))

# Functions below deliberately use the union of all2704 bead objects; there is no
# bead-specific shadow target, pigment-dependent selection, or local light fit.
def scene(parameters,destination,mode='paper'):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    source=(BASE/'scene.inc').read_text();start=source.index('light_source {');end=source.index('// Paper is',start)
    camera=parameters.get('camera')
    if camera:
        location=camera['location'];distance=camera['distance'];scale=camera['scale']
        replacement=f'camera {{ perspective location {vec(location)} direction <0,0,{-distance}> right <{W/scale},0,0> up <0,{H/scale},0> }}'
        source=re.sub(r'camera \{[^}]+\}',replacement,source,count=1)
        start=source.index('light_source {');end=source.index('// Paper is',start)
    pos=parameters['position'];size=parameters['diameter'];intensity=parameters.get('intensity',1.05);fill=parameters.get('fill',.13);grid=parameters.get('grid',9)
    first=np.array([size,0,0.]);second=np.array([0,size,0.]);orient='orient'
    if parameters.get('fixed_plane'):
        direction=np.array(pos,dtype=float);direction/=np.linalg.norm(direction)
        first=np.cross([0,0,1.],direction);first/=np.linalg.norm(first);second=np.cross(direction,first);first*=size;second*=size;orient=''
    tint=np.array(parameters.get('fill_tint',[1.,1.,1.]))
    lights=f'''light_source {{ {vec(pos)} color rgb {intensity}
 area_light {vec(first)},{vec(second)},{grid},{grid} adaptive 2 circular {orient} }}
light_source {{ <0,-86.8240888,492.4038765> color rgb {vec(fill*tint)} shadowless }}
'''
    source=source[:start]+lights+source[end:]
    multiplier=parameters.get('ambient_multiplier',1.)
    source=source.replace('ambient_light rgb <.65,.68,.75>',f'ambient_light rgb {vec(np.array([.65,.68,.75])*multiplier*tint)}')
    # Baseline pass reproduces R345's original illumination exactly.
    if parameters.get('original'):
        source=(BASE/'scene.inc').read_text()
    if mode=='mask':
        start=source.index('// Shared rounded');end=source.index('// Paper is',start)
        shapes='\n'.join(f'#declare GlassBeads[{i}]=bead(M,.8,.55,1);' for i in range(3))
        source=source[:start]+'#declare M=material{texture{pigment{rgb 1} finish{ambient 1 diffuse 0}}};\n#declare GlassBeads=array[3];\n'+shapes+'\n'+source[end:]
        source=source.replace('ambient_light rgb <.65,.68,.75>','ambient_light rgb 1')
        source=re.sub(r'texture \{ pigment \{ color srgb <[^>]+> \} finish \{ ambient .22 diffuse .84 \} normal \{ bumps .10 scale .16 \} \}', 'texture{pigment{rgb 0} finish{ambient 0 diffuse 0}}',source)
    if mode=='clear':source=source.replace('#include "beads.inc"','')
    elif mode=='paper':
        # no_image removes camera material ONLY; shadow rays still meet every
        # original hollow glass bead. Actual full render is checked separately.
        beads=(BASE/'beads.inc').read_text();beads=beads.replace('> }','> no_image }')
        source=source.replace('#include "beads.inc"',beads)
    destination.write_text('#version 3.7;\n'+source.rstrip()+'\n')

def run_pov(path,width=635,height=796,aa=False,output_name=None):
    path=Path(path);png=path.parent/output_name if output_name else path.with_suffix('.png');log=path.with_suffix('.log')
    cmd=['povray','+I'+str(path),'+O'+str(png),'+L'+str(BASE),f'+W{width}',f'+H{height}','+FN','-D','-J','+WT4']+(['+A0.15','+AM2','+R2'] if aa else ['-A'])
    with log.open('w') as f:p=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text();log.write_text('\n'.join(s.rstrip() for s in re.sub(r'Rendered[^\r\n]*(?:[\r\n]|$)','',text).splitlines()).rstrip()+'\n')
    if p.returncode:raise RuntimeError(text[-3000:])
    normalize_png(png);return png

def pass_images(params,folder,width=635,height=796,full=False):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    for mode in ['paper','clear']+(['full'] if full else []):
        p=folder/(mode+'.pov');scene(params,p,mode);run_pov(p,width,height,aa=full)
    a=linear(rgb(folder/'paper.png'));b=linear(rgb(folder/'clear.png'));ratio=np.divide(a,b,out=np.ones_like(a),where=b>.001)
    return ratio

def design(xy):
    xy=np.asarray(xy);x=(xy[...,0]-1269.5)/1270;y=(xy[...,1]-1590.5)/1591
    return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],axis=-1)

def fit_background():
    image=linear(rgb(ROOT/'beads-photo-2.jpg'));curve=Model(read(ROOT/'photo2/r345/config.json')).image
    from scipy.spatial import cKDTree
    yy,xx=np.mgrid[6:H:12,6:W:12];xy=np.c_[xx.ravel(),yy.ravel()];dist=cKDTree(curve).query(xy)[0]
    keep=dist>260;xy=xy[keep];values=image[xy[:,1],xy[:,0]];A=design(xy);hold=((xy[:,0]//12+3*(xy[:,1]//12))%5)==0
    coefficients=[];diagnostics=[]
    for c in range(3):
        target=np.log(np.maximum(values[:,c],1e-5));fit=least_squares(lambda v:A[~hold]@v-target[~hold],np.linalg.lstsq(A[~hold],target[~hold],rcond=None)[0],loss='soft_l1',f_scale=.06,max_nfev=30)
        coefficients.append(fit.x.tolist());residual=A[hold]@fit.x-target[hold];diagnostics.append(dict(log_residual_rms=float(np.sqrt(np.mean(residual**2))),log_residual_median_absolute=float(np.median(abs(residual)))))
    result=dict(source_sha256=sha(ROOT/'beads-photo-2.jpg'),method='Robust global quadratic log-RGB background, all grid points at image-axis distance>260px; no hue/pigment or shadow-darkness selection. Every fifth geometric grid point held for residual diagnostics. No extrapolated narrow local reference band.',control_points=len(xy),coefficients=coefficients,validation=diagnostics)
    save(OUT/'background.json',result)
    im=Image.open(ROOT/'beads-photo-2.jpg').convert('RGB').resize((635,796));d=ImageDraw.Draw(im)
    for q in xy[::3]:d.point(tuple(q*[635/W,796/H]),fill='#00ffff')
    im.save(OUT/'background-controls.jpg',quality=95)
    return result

@lru_cache(maxsize=1)
def background_coefficients():return np.array(read(OUT/'background.json')['coefficients'])
def background_at(xy):return np.exp(design(xy)@background_coefficients().T)

def prepare_profiles():
    rows=read(OUT/'observations.json')['rows'];im=rgb(ROOT/'beads-photo-2.jpg');im=linear(im)
    # Native, exact whole-necklace model silhouette independent of illumination.
    if not (OUT/'mask.png').exists():
        scene(dict(position=[-300,350,850],diameter=75),OUT/'mask.pov','mask');run_pov(OUT/'mask.pov',W,H)
    mask=rgb(OUT/'mask.png')[:,:,0]>.5
    distance=np.arange(0,261,dtype=float);lanes=np.arange(-18,19,3);profiles=[]
    gray=rgb(ROOT/'beads-photo-2.jpg')@np.array([.2126,.7152,.0722]);gy,gx=np.gradient(ndi.gaussian_filter(gray,1.1));edge=np.hypot(gx,gy)
    for row in rows:
        q=np.array(row['point']);t=np.array(row['tangent']);n=np.array(row['outward']);rr=np.arange(15,75,dtype=float)
        xy=q+lanes[:,None,None]*t+rr[None,:,None]*n;e=sample(edge,xy);last=[]
        for ee in e:
            ids=np.flatnonzero((rr>=24)&(rr<=68)&(ee>.034))
            if len(ids):last.append(rr[ids[-1]])
        guard=max(12.,row['edge_uncertainty']+8,(max(last)-row['edge_radius']+8) if last else 25)
        # Profile samples are on paper outside a conservative contour band.
        radii=row['edge_radius']+distance
        pxy=q+lanes[:,None,None]*t+radii[None,:,None]*n
        backgrounds=background_at(pxy)
        channels=[];deficits=[]
        for channel in range(3):
            observed=sample(im[:,:,channel],pxy)
            deficit=1-np.nanmedian(observed/backgrounds[:,:,channel],axis=0)
            deficits.append(deficit)
            reference=q+132.5*n
            logs=np.log(background_at(np.array([reference,reference+t,reference+n])))[:,channel]
            channels.append([float(logs[0]),float(logs[1]-logs[0]),float(logs[2]-logs[0])])
        bg=np.nanmedian(backgrounds,axis=0).T
        lum=np.array([.2126,.7152,.0722]);deficit=(lum@(bg*np.array(deficits)))/(lum@bg)
        use=(distance>=guard)&np.isfinite(deficit)
        eligible=bool(row['eligible'] and use.sum()>60)
        # Render edge from a single fixed exact mask, not from rendered darkness.
        mr=np.arange(5,86,dtype=float);mxy=q+lanes[:,None,None]*t+mr[None,:,None]*n;mm=sample(mask.astype(float),mxy);mb=[]
        for lane in mm:
            ids=np.flatnonzero(lane>.5)
            if len(ids):mb.append(mr[ids[-1]])
        model_edge=float(np.percentile(mb,75)) if mb else 60.
        profiles.append(dict(row,distance=distance.tolist(),paper_guard=float(guard),eligible=eligible,photo_deficit=deficit.tolist(),photo_rgb_deficit=np.array(deficits).T.tolist(),background_log_planes=channels,model_edge_radius=model_edge,photo_metrics=profile_metrics(distance[use],deficit[use])))
    save(OUT/'profiles.json.gz',dict(policy='Grayscale-only silhouette eligibility; paper guard covers the last steep body edge across all13 lanes plus8px, threshold uncertainty plus8px, and minimum12px beyond nominal75th-percentile edge. Background from a robust global quadratic log-RGB illumination surface fitted only on a fixed grid farther than260px from the entire traced centerline. Border-clipped samples are null and extents can be censored. All profiles retained, no pigment selection. Model silhouette comes from exact all-bead POV-Ray mask. Metrics measured only beyond paper guard; 12..20px darkness is NOT under-body contact shadow.',profiles=profiles))
    print('profiles eligible',sum(r['eligible'] for r in profiles),flush=True)
    return profiles

@lru_cache(maxsize=1)
def paper_distance():
    mask=np.asarray(Image.open(OUT/'mask.png').convert('L'))>128
    return ndi.distance_transform_edt(~mask).astype(np.float32)

def rendered_profiles(ratio,profiles,mask_path=None):
    # Match material-relative shadow offsets without changing any scene geometry.
    sy,sx=ratio.shape[0]/H,ratio.shape[1]/W;result=[];lanes=np.arange(-18,19,3)
    alternate=None
    if mask_path:
        mask=np.asarray(Image.open(mask_path).convert('L'))>128
        maskscale=np.array([mask.shape[1]/W,mask.shape[0]/H]);alternate=ndi.distance_transform_edt(~mask).astype(np.float32)/maskscale.mean()
    for r in profiles:
        q=np.array(r['point']);t=np.array(r['tangent']);n=np.array(r['outward']);dist=np.array(r['distance']);xy=q+lanes[:,None,None]*t+(r['model_edge_radius']+dist)[None,:,None]*n
        if alternate is not None:
            mr=np.arange(0,110,dtype=float);mxy=q+lanes[:,None,None]*t+mr[None,:,None]*n;mm=sample(mask.astype(float),(mxy+.5)*maskscale-.5);mb=[]
            for lane in mm:
                ids=np.flatnonzero(lane>.5)
                if len(ids):mb.append(mr[ids[-1]])
            model_edge=float(np.percentile(mb,75)) if mb else 60.
            xy=q+lanes[:,None,None]*t+(model_edge+dist)[None,:,None]*n
            outside=sample(alternate,(xy+.5)*maskscale-.5)>=2
        else:outside=sample(paper_distance(),xy)>=2
        xy=(xy+.5)*[sx,sy]-.5
        # Convert each channel's clear-paper-normalized transmission to a common
        # linear-luminance ratio; photograph's own baseline supplies channel weights.
        weights=np.exp(np.array(r['background_log_planes'],dtype=float)[:,0])*[.2126,.7152,.0722];weights/=weights.sum()
        value=np.stack([np.nanmedian(np.where(outside,sample(ratio[:,:,c],xy),np.nan),axis=0) for c in range(3)])
        result.append(1-weights@value)
    return np.array(result)


def score(pred,profiles,fit_alpha=True):
    photo=np.array([r['photo_deficit'] for r in profiles],dtype=float);distance=np.arange(photo.shape[1])
    good=np.array([r['eligible'] for r in profiles]);guards=np.array([r['paper_guard'] for r in profiles]);mask=good[:,None]&(distance[None,:]>=guards[:,None])&(distance[None,:]<=200)&np.isfinite(photo)&np.isfinite(pred)
    split=np.array([r['split']=='fit' for r in profiles]);fit=mask&split[:,None]
    x=pred[fit];y=photo[fit];alpha=1.
    if fit_alpha:
        for _ in range(20):
            residual=alpha*x-y;weight=1/np.sqrt(1+(residual/.07)**2);alpha=float(np.clip(np.sum(weight*x*y)/max(1e-12,np.sum(weight*x*x)),.35,1.35))
    errors=alpha*pred-photo;out=dict(alpha=alpha)
    for name,use in [('fit',fit),('validation',mask&~split[:,None]),('all',mask)]:
        e=errors[use];out[name]=dict(points=int(use.sum()),profiles=int(np.any(use,axis=1).sum()),rms=float(np.sqrt(np.mean(e**2))),mae=float(np.mean(abs(e))),robust_loss=float(np.mean(.07**2*(np.sqrt(1+(e/.07)**2)-1))))
    return out

def optimize():
    profiles=read(OUT/'profiles.json.gz')['profiles'];work=Path('/tmp/r346-shadow-trials');work.mkdir(exist_ok=True)
    candidates=[dict(id='R345',position=[-300,350,850],diameter=75,original=True)]
    for x,y in [(-300,-400),(-500,-400),(-700,-400),(-300,-650),(-500,-650),(-700,-650),(-900,-650),(-500,-850),(-700,-850)]:
        candidates.append(dict(id=f'x{x}_y{y}_d350',position=[x,y,850],diameter=350))
    for diameter in [150,550,800]:candidates.append(dict(id=f'x-500_y-650_d{diameter}',position=[-500,-650,850],diameter=diameter))
    for z in [500,1500]:candidates.append(dict(id=f'height{z}',position=[-500*z/850,-650*z/850,z],diameter=350*z/850))
    ledger=[]
    for params in candidates:
        folder=work/params['id'];rp=folder/'ratio.npy'
        if rp.exists():ratio=np.load(rp)
        else:ratio=pass_images(params,folder);np.save(rp,ratio)
        pred=rendered_profiles(ratio,profiles);result=score(pred,profiles,fit_alpha=not params.get('original',False));row=dict(parameters=params,metrics=result);ledger.append(row)
        save(OUT/'optimization.json',dict(policy='Global physical key-light position/diameter grid with one fitted global shadow-contrast scale. Fit geography3/4; every fourth station reserved. Both sides, including no-shadow controls, use fixed grayscale eligibility. No per-section light or geometric changes.',trials=ledger))
        print(params['id'],result,flush=True)
    best=min(ledger[1:],key=lambda r:r['metrics']['fit']['robust_loss']);save(OUT/'selected-proxy.json',dict(stage='coarse grid only',accepted=False,superseded_by='photo2/r346/config.json',result=best))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['measure','background','profiles','trial','optimize']);ap.add_argument('--name',default='test');ap.add_argument('--position',type=float,nargs=3,default=[-500,-650,850]);ap.add_argument('--diameter',type=float,default=350);a=ap.parse_args()
    if a.stage=='measure':measure()
    elif a.stage=='background':fit_background()
    elif a.stage=='profiles':prepare_profiles()
    elif a.stage=='optimize':optimize()
    elif a.stage=='trial':pass_images(dict(position=a.position,diameter=a.diameter),OUT/a.name,1270,1591,True)

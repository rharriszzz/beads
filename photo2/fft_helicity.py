"""R243 bounded paired-channel Gaussian FFT experiment. See FFT_HELICITY.md.

Numerical FFT/window/peak machinery is reused from fft_explorer_core (pinned
upstream excerpts). New candidate qualification, tracking and hypothesis scoring
are experimental. Image observations are never full-string bead indices.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-fft-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from PIL import Image, ImageOps, ExifTags
from scipy.interpolate import splprep, splev
from scipy.ndimage import map_coordinates
from scipy.optimize import linear_sum_assignment
from photo2 import fft_explorer_core as core

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/'photo2/review/r243'
OUT = ROOT/'photo2/output/r243'
COLORS = ['#00bbff','#ff9900','#66cc55','#dd55cc','#ffee55','#aaaaaa']
PARAMS = dict(max_pairs=6, prominence_min=3., separation_resolution=1.5,
              lobe_resolution=1.25, angle_floor_deg=3., radius_floor_fraction=.08,
              matching_cap=4., unmatched=4., track_gate=3., track_gap=2,
              sigma_radius=1., low_d=1/3, high_d=2., d_uncertainty_fraction=.2,
              tangent_uncertainty_deg=5.)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def read(p): return json.loads(Path(p).read_text())
def wrap(a): return (np.asarray(a)+90)%180-90

def image_rgb(path):
    return np.asarray(ImageOps.exif_transpose(Image.open(path)).convert('RGB'), dtype=np.float32)/255

def prepare():
    """Raw-image-only sample/scale protocol; no FFTs in this stage."""
    BUNDLE.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    seed=read(ROOT/'photo2/spline-seed-r175.json'); pts=np.array(seed['points'])
    tck,_=splprep(pts.T,s=len(pts)*4,per=True,k=3)
    u=np.linspace(0,1,16001); line=np.array(splev(u,tck)).T
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
    src=ROOT.parent/'fft-image-explorer/beads-photo-2_splines.json'
    spline=read(src)
    # Distances to existing boundary polylines are diagnostic scale guides only.
    def nearest(q, poly):
        a=np.array(poly[:-1]); b=np.array(poly[1:]); v=b-a
        f=np.clip(np.sum((q-a)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1e-12),0,1)
        hits=a+f[:,None]*v; j=np.argmin(np.linalg.norm(hits-q,axis=1)); return hits[j]
    sites=[]
    for i in range(8):
        s=arc[-1]*i/8; ui=np.interp(s,arc,u); xy=np.array(splev(ui,tck)); t=np.array(splev(ui,tck,der=1));t/=np.linalg.norm(t)
        inn=nearest(xy,spline['inner_spline']); outer=nearest(xy,spline['outer_spline'])
        radius=(np.linalg.norm(inn-xy)+np.linalg.norm(outer-xy))/2
        sites.append(dict(id=f'W{i+1}',s=float(s),xy=xy.tolist(),tangent=t.tolist(),
                          tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))),radius=float(radius),
                          boundary_guide_endpoints=[inn.tolist(),outer.tolist()],
                          split='development' if i in (0,4) else 'reserved'))
    # d is set by raw-image scale review after the initial overview, before spectra.
    protocol=dict(request='R243',image='beads-photo-2.jpg',image_sha256=sha(ROOT/'beads-photo-2.jpg'),
        source_commit='2caf0707c2b63a0d7540e2cac447d2f1b883d8c1',spline_sha256=sha(src),
        seed_sha256=sha(ROOT/'photo2/spline-seed-r175.json'),sampling='equal image arc length; no moves',
        length=float(arc[-1]),sites=sites,parameters=PARAMS,
        radius_status='distance to existing approximate boundary guides, checked in raw crops; not measured 3D radius',
        no_spectra_inspected=True)
    if (BUNDLE/'sampling.json').exists():
        old=read(BUNDLE/'sampling.json')
        if all('diameter' in q for q in old['sites']):
            raise ValueError('Sampling already frozen; use the tracked protocol for reproduction, not prepare')
    save(BUNDLE/'sampling.json',protocol)
    np.savez(OUT/'curve.npz',u=u,line=line,arc=arc,tangent=np.array(splev(u,tck,der=1)).T)
    rgb=image_rgb(ROOT/'beads-photo-2.jpg')
    fig,ax=plt.subplots(figsize=(8,10));ax.imshow(rgb);ax.plot(*line.T,c='cyan',lw=.7)
    for q in sites:
        x,y=q['xy'];r=q['radius']; t=np.array(q['tangent'])
        ax.add_patch(Circle((x,y),r,fill=False,color='white',lw=1));ax.plot([x-2*r*t[0],x+2*r*t[0]],[y-2*r*t[1],y+2*r*t[1]],c='yellow')
        ax.text(x+30,y,q['id']+' '+q['split'],color='white',bbox=dict(facecolor='black',alpha=.7))
    ax.set_title('Raw sampling protocol: cyan approximate centerline; circles = Gaussian sigma\nEqual image arc length; yellow tangents; no spectral selection');fig.tight_layout();fig.savefig(BUNDLE/'locations.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(2,4,figsize=(16,9))
    for ax,q in zip(axes.flat,sites):
        x,y=q['xy'];r=q['radius'];ax.imshow(rgb);ax.set_xlim(x-2*r,x+2*r);ax.set_ylim(y+2*r,y-2*r)
        endpoints=np.array(q['boundary_guide_endpoints']);ax.plot(*endpoints.T,'c.-',lw=1)
        ax.set_title(f"{q['id']} {q['split']} R={r:.1f}px");ax.grid(alpha=.2)
    fig.suptitle('Raw crops before FFT inspection — cyan endpoints from existing boundary guides');fig.tight_layout();fig.savefig(BUNDLE/'raw-scale-review.png',dpi=150);plt.close(fig)
    exif=Image.open(ROOT/'beads-photo-2.jpg').getexif()
    save(BUNDLE/'exif.json',{str(ExifTags.TAGS.get(k,k)):str(v) for k,v in exif.items()})
    print(json.dumps(dict(length=arc[-1],sites=sites),indent=2))

def ensure_curve():
    """Regenerate routine curve cache from the tracked seed, without sibling files."""
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/'curve.npz'
    if not path.exists():
        pts=np.array(read(ROOT/'photo2/spline-seed-r175.json')['points'])
        tck,_=splprep(pts.T,s=len(pts)*4,per=True,k=3)
        u=np.linspace(0,1,16001);line=np.array(splev(u,tck)).T
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
        np.savez(path,u=u,line=line,arc=arc,tangent=np.array(splev(u,tck,der=1)).T)
    return np.load(path)

def sample(rgb,xy,sigma):
    half=int(np.ceil(3*sigma)); x,y=np.round(xy).astype(int); n=2*half+1
    if x-half<0 or y-half<0 or x+half>=rgb.shape[1] or y+half>=rgb.shape[0]:
        raise ValueError('Window extends outside image; do not silently pad')
    patch=rgb[y-half:y+half+1,x-half:x+half+1]
    # width=2*half and softness=sigma/half gives exact source Gaussian convention.
    g=core.make_mask((n,n),'Rectangle','Gaussian',half,half,2*half,2*half,0,sigma/half)
    return patch,g,[int(x-half),int(y-half)]

def inverse_pairs(f,peaks,lobes=False,resolution=1.):
    n=f.shape[0];c=n//2;yy,xx=np.mgrid[:n,:n]; mask=np.zeros((n,n),bool)
    for p in peaks:
        dx,dy=p['offset']; r=resolution if lobes else 0
        for sign in (-1,1):
            mask |= (xx-(c+sign*dx))**2+(yy-(c-sign*dy))**2<=r*r
    return np.fft.ifft2(np.fft.ifftshift(f*mask)).real

def analyze(rgb,q,channel,variant=None):
    v=variant or {};sigma=q['radius']*v.get('width',1);d=q['diameter'];t=np.array(q['tangent']);normal=np.array([-t[1],t[0]])
    xy=np.array(q['xy'])+d*(v.get('shift_t',0)*t+v.get('shift_n',0)*normal)
    patch,g,origin=sample(rgb,xy,sigma);bank=core.make_channel_bank(patch)
    x=bank.arrays['HSV V' if channel=='V' else 'Y luminance'].copy()
    if v.get('mean'):x-=np.sum(x*g)/np.sum(g)
    lo=PARAMS['low_d']/d*v.get('low',1); hi=min(.49,PARAMS['high_d']/d*v.get('high',1))
    # Source percent is measured relative to corner radius, n/sqrt(2).
    product=core.compute_fft_products(x,g,False,square_fft=False,
            fft_highpass_percent=lo*100*np.sqrt(2),fft_lowpass_percent=hi*100*np.sqrt(2))
    f=product[6].astype(complex);n=len(f); c=n//2
    yy,xx=np.mgrid[:n,:n];fx=(xx-c)/n;fy=(c-yy)/n;rr=np.hypot(fx,fy)
    if v.get('taper'):
        a=np.clip((rr-lo)/(.1*(hi-lo)),0,1);b=np.clip((hi-rr)/(.1*(hi-lo)),0,1)
        f*=np.sin(a*np.pi/2)**2*np.sin(b*np.pi/2)**2
    power=np.abs(f)**2;total=float(power.sum()); resolution=n/(2*np.pi*sigma)
    candidates=core.find_top_fft_peaks(np.log1p(np.abs(f)),top_k=40,min_distance=max(1,int(np.ceil(1.5*resolution))))
    peaks=[];used=[]
    for p in candidates:
        dx,dy=p['x'],p['y'];rad=p['distance']/n
        if not lo<rad<hi:continue
        if any(min(np.hypot(dx-a,dy-b),np.hypot(dx+a,dy+b))<PARAMS['separation_resolution']*resolution for a,b in used):continue
        # Merge antipodal lobe support, retaining actual physical sum |F|^2.
        dist=np.minimum(np.hypot(xx-c-dx,c-yy-dy),np.hypot(xx-c+dx,c-yy+dy))
        support=(dist<=PARAMS['lobe_resolution']*resolution)&(power>0)
        annulus=(dist>2*resolution)&(dist<4*resolution)&(power>0)
        baseline=float(np.median(power[annulus])) if annulus.any() else 0
        peakpower=float(power[int(c-dy),int(c+dx)])
        prominence=peakpower/max(baseline,1e-12)
        if prominence<PARAMS['prominence_min']:continue
        pairpower=float(power[support].sum());width=float(np.sqrt(np.sum(power[support]*dist[support]**2)/max(pairpower,1e-12)))
        angle=float(wrap(p['angle_deg']));rel=float(wrap(angle-q['tangent_deg']))
        uncertainty=max(PARAMS['angle_floor_deg'],float(np.degrees(np.arctan2(max(width,resolution),p['distance']))))
        peaks.append(dict(candidate=len(peaks)+1,offset=[int(dx),int(dy)],radius_bins=float(p['distance']),
            frequency=rad,fd=rad*d,diameter=d,angle=angle,relative_angle=rel,pair_power=pairpower,
            band_fraction=pairpower/max(total,1e-12),prominence=prominence,breadth_bins=width,
            angle_uncertainty=uncertainty,frequency_uncertainty=max(width,resolution)/n,
            legacy_log_power_sum=p['log_power_sum'],assignment='unassigned'))
        used.append((dx,dy))
        if len(peaks)==PARAMS['max_pairs']:break
    rec=dict(window=q['id'],channel=channel,xy=xy.tolist(),origin=origin,n=n,sigma=sigma,
        diameter=d,s=q.get('s',0),split=q.get('split','control'),tangent_deg=q['tangent_deg'],
        low=lo,high=hi,total_band_power=total,peaks=peaks,variant=v,
        resolution_bins=resolution)
    return rec,dict(patch=patch,g=g,x=x,f=f)

def predicted(tangent_deg,hand,elevation=85,roll=0,rho=6.1109157489,phase=0.,scale=1.):
    """Local visible-front unrolled reference tube -> reciprocal vectors.

    Global orthographic plane camera; perspective is tested separately in rendered
    controls, not silently claimed solved by this approximation. A=[v1 v6],
    reciprocal normals to rows 6,1,7 are b1,b2,b1-b2 respectively.
    """
    el=np.radians(elevation);az=np.radians(roll)
    # Image roll changes the foreshortening axis; world azimuth alone is a gauge
    # when the planar tangent is recovered from its image direction.
    r0=np.array([-1.,0.,0.]);u0=np.array([0.,np.sin(el),np.cos(el)])
    eye=np.array([0.,-np.cos(el),np.sin(el)])
    right=np.cos(az)*r0-np.sin(az)*u0
    up=np.sin(az)*r0+np.cos(az)*u0
    ta=np.radians(tangent_deg)
    t2=np.linalg.solve(np.array([right[:2],up[:2]]),[np.cos(ta),np.sin(ta)])
    t=np.r_[t2/np.linalg.norm(t2),0];normal=np.array([-t[1],t[0],0])
    phi=np.arctan2(eye@normal,eye[2])+np.radians(phase)
    circ=np.cos(phi)*normal-np.sin(phi)*np.array([0,0,1])
    j=np.array([[right@t,right@circ],[up@t,up@circ]])
    pitch=.443292307273487;delta=2*np.pi/6.5
    a=j@np.array([[pitch,6*pitch],[hand*rho*delta,hand*rho*(6*delta-2*np.pi)]])
    if abs(np.linalg.det(a))<1e-7:return None
    b=np.linalg.inv(a).T
    vectors=[b[:,1],b[:,0],b[:,0]-b[:,1]]
    diameter=4.221831497842732
    return [dict(family=label,relative_angle=float(wrap(np.degrees(np.arctan2(k[1],k[0]))-tangent_deg)),
                 fd=float(np.linalg.norm(k)*diameter/scale)) for label,k in zip([1,6,7],vectors)]

def score(peaks,model):
    if model is None:return dict(score=4.,matches=[],resolved=0)
    m=len(peaks);cost=np.full((3,m+3),PARAMS['unmatched'])
    for i,a in enumerate(model):
      for j,p in enumerate(peaks):
        da=float(wrap(p['relative_angle']-a['relative_angle']))
        au=np.hypot(p['angle_uncertainty'],PARAMS['tangent_uncertainty_deg'])
        fu=max(PARAMS['radius_floor_fraction']*p['fd'],p['frequency_uncertainty']*p.get('diameter',1))
        # d uncertainty explicitly limits radius precision; no absolute image gain score.
        fu=np.hypot(fu,PARAMS['d_uncertainty_fraction']*a['fd'])
        cost[i,j]=min(4.,np.hypot(da/au,(p['fd']-a['fd'])/fu))
    rows,cols=linear_sum_assignment(cost)
    matches=[dict(family=model[i]['family'],candidate=peaks[j]['candidate'],residual=float(cost[i,j]))
             for i,j in zip(rows,cols) if j<m and cost[i,j]<4]
    return dict(score=float(cost[rows,cols].mean()),matches=matches,
                resolved=sum(x['residual']<2 for x in matches))

def models_for(rec):
    # Same finite nuisance bank for each hand. Global camera settings must be shared
    # when aggregating windows. Local surface offset/radius are uncertainty variants.
    results=[]
    for el in (45,65,85):
      for az in (0,45,90,135):
       for rho in (4.,6.1109157489):
        for phase in (-25,0,25):
         for hand in (-1,1):
          model=predicted(rec['tangent_deg'],hand,el,az,rho,phase)
          fit=score(rec['peaks'],model)
          results.append(dict(hand=hand,elevation=el,roll=az,rho=rho,phase=phase,**fit))
    return results

def variants():
    return [('primary',{})]+[(f'width{x}',dict(width=x)) for x in (.75,1.25)]+[(f'{key}{x}',{key:x}) for key in ('low','high') for x in (.8,1.2)]+[(f'{key}{x}',{key:x}) for key in ('shift_t','shift_n') for x in (-.25,.25)]+[('mean',dict(mean=True)),('taper',dict(taper=True))]

def card(q,results,path):
    fig,axes=plt.subplots(2,5,figsize=(17,7),layout='constrained')
    vmax=max(np.log1p(np.abs(a['f'])).max() for _,a in results)
    for row,(rec,a) in enumerate(results):
        axes[row,0].imshow(a['patch']);axes[row,0].set_title(q['id']+' raw RGB' if row==0 else 'Same raw crop')
        axes[row,1].imshow(a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title(rec['channel']+' × Gaussian')
        n=rec['n'];f=a['f'];axes[row,2].imshow(np.log1p(np.abs(f)),cmap='magma',vmin=0,vmax=vmax,extent=[-.5,.5,-.5,.5],origin='upper')
        for p in rec['peaks']:
            x,y=np.array(p['offset'])/n
            for s in (-1,1):axes[row,2].plot(s*x,s*y,'o',mfc='none',mec=COLORS[p['candidate']-1],ms=8)
            axes[row,2].text(x,y,str(p['candidate']),color='white',fontsize=8)
        lim=rec['high']*1.1;axes[row,2].set_xlim(-lim,lim);axes[row,2].set_ylim(-lim,lim)
        axes[row,2].set_title(rec['channel']+' FFT; cycles/pixel')
        for col,picks,title in [(3,rec['peaks'][:1],'strongest pair'),(4,rec['peaks'][:3],'top three candidates')]:
            inv=inverse_pairs(f,picks);amp=max(abs(inv).max(),1e-12)
            axes[row,col].imshow(inv,cmap='gray',vmin=-amp,vmax=amp);axes[row,col].set_title(title+'\nphase preserved; unassigned')
        for col in (0,1,3,4):axes[row,col].axis('off')
    fig.suptitle(f"{q['id']} {q.get('split','control')}: sigma={q['radius']:.1f}px; d={q['diameter']:.1f}px; tangent={q['tangent_deg']:.1f}°")
    fig.savefig(path,dpi=140);plt.close(fig)

def track(records):
    """New uncertain short-gap angle/radius tracking; no smoothing or model labels."""
    active=[];nextid=1;links=[]
    for idx,r in enumerate(records):
        active=[a for a in active if idx-a['index']<=PARAMS['track_gap']+1]
        previous_active=active.copy()
        peaks=r['peaks'];cost=np.full((len(active),len(peaks)+len(active)),3.)
        for i,a in enumerate(active):
          for j,p in enumerate(peaks):
            da=float(wrap(p['relative_angle']-a['peak']['relative_angle']))
            au=max(5.,np.hypot(p['angle_uncertainty'],a['peak']['angle_uncertainty']))
            cost[i,j]=np.hypot(da/au,(p['fd']-a['peak']['fd'])/.2)
        chosen={}
        if active:
            ii,jj=linear_sum_assignment(cost)
            chosen={int(j):int(i) for i,j in zip(ii,jj) if j<len(peaks) and cost[i,j]<3}
        for j,p in enumerate(peaks):
            alternatives=[dict(track=a['track'],cost=float(cost[i,j])) for i,a in enumerate(previous_active) if cost[i,j]<3]
            if j in chosen:
                a=active[chosen[j]];tid=a['track'];prev=a['window'];gap=idx-a['index']
                a.update(index=idx,peak=p,window=r['window'])
                links.append(dict(window=r['window'],candidate=p['candidate'],track=tid,previous=prev,gap=gap,alternatives=alternatives))
            else:
                tid=nextid;nextid+=1;active.append(dict(track=tid,index=idx,peak=p,window=r['window']))
            p['track']=tid;p['track_ambiguous']=len(alternatives)>1
    return links

def photo(stage):
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=read(BUNDLE/'sampling.json');rgb=image_rgb(ROOT/cfg['image']);assert sha(ROOT/cfg['image'])==cfg['image_sha256']
    if not all('diameter' in q for q in cfg['sites']):raise ValueError('Raw scale review must be frozen first')
    selected=[q for q in cfg['sites'] if stage=='all' or q['split']=='development']
    records=[]
    for q in selected:
        primary=[]
        for name,v in variants():
          for ch in ('V','Y'):
            rec,a=analyze(rgb,q,ch,v);rec['variant_name']=name
            rec['fits']=models_for(rec);records.append(rec)
            if name=='primary':primary.append((rec,a))
        card(q,primary,BUNDLE/f"{q['id']}-comparison.png")
    save(OUT/f'{stage}-windows.json',records)
    if stage=='all':
        curve=ensure_curve();arc=curve['arc'];line=curve['line'];tang=curve['tangent']
        n=int(np.ceil(cfg['length']/(.5*np.median([q['radius'] for q in cfg['sites']]))))
        dense=[]
        for i,s in enumerate(np.linspace(0,cfg['length'],n,endpoint=False)):
            xy=[float(np.interp(s,arc,line[:,k])) for k in (0,1)]; t=np.array([np.interp(s,arc,tang[:,k]) for k in (0,1)]);t/=np.linalg.norm(t)
            ss=np.array([q['s'] for q in cfg['sites']]);r=np.interp(s,np.r_[ss,cfg['length']],np.r_[[q['radius'] for q in cfg['sites']],cfg['sites'][0]['radius']]);d=np.interp(s,np.r_[ss,cfg['length']],np.r_[[q['diameter'] for q in cfg['sites']],cfg['sites'][0]['diameter']])
            q=dict(id=f'T{i:03}',s=float(s),xy=xy,tangent=t.tolist(),tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))),radius=float(r),diameter=float(d),split='tracking')
            for ch in ('V','Y'):
                try:
                    rec,_=analyze(rgb,q,ch)
                except ValueError as exc:
                    rec=dict(window=q['id'],channel=ch,s=float(s),xy=xy,split='tracking',peaks=[],failure=str(exc),tangent_deg=q['tangent_deg'])
                # Geometric curvature uncertainty is kept independent of spectra.
                dist=np.minimum(abs(arc-s),cfg['length']-abs(arc-s))
                near=dist<=r
                angles=np.degrees(np.arctan2(-tang[near,1],tang[near,0]))
                rec['tangent_variation_sigma_deg']=float(np.ptp(wrap(angles-q['tangent_deg'])))
                dense.append(rec)
        links={ch:track([r for r in dense if r['channel']==ch]) for ch in ('V','Y')}
        save(OUT/'tracking.json',dict(windows=dense,links=links,step=cfg['length']/n,closure='track IDs do not impose loop closure'))
    print(stage,len(records),'paired-configuration records')

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','development','all']);args=p.parse_args()
    if args.stage=='prepare':prepare()
    else:photo(args.stage)
if __name__=='__main__':main()

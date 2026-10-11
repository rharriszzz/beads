"""R244: straight selection, long tangent windows and curve straightening.

Uses the pinned FFT explorer numerical functions. R243 measurements/code stay
unchanged. Coordinates are diagnostic approximate image-centerline coordinates,
not inferred bead centers. See FFT_CURVATURE.md for limitations and commands.
"""
from __future__ import annotations
import argparse,csv,json,os,hashlib
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-fft-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.interpolate import CubicSpline
from scipy.optimize import linear_sum_assignment
from photo2 import fft_helicity as base
from photo2 import fft_explorer_core as core
from photo2.fft_helicity_report import best_at
ROOT=base.ROOT; BUNDLE=ROOT/'photo2/review/r244';OUT=ROOT/'photo2/output/r244'
ARMS={'A':1.,'B':2.,'C':2.}
COLORS=base.COLORS

def save(p,d):base.save(p,d)
def read(p):return base.read(p)
def sha(p):return base.sha(p)

class Curve:
    def __init__(self,line):
        line=np.asarray(line,float)
        if np.linalg.norm(line[0]-line[-1])>1e-8:line=np.vstack([line,line[0]])
        s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
        keep=np.r_[True,np.diff(s)>1e-8];s=s[keep];line=line[keep]
        self.length=float(s[-1]);self.spline=CubicSpline(s,line,bc_type='periodic')
    def at(self,s):
        s=np.asarray(s)%self.length;xy=self.spline(s);t=self.spline(s,1);t=t/np.linalg.norm(t,axis=-1,keepdims=True)
        n=np.stack([-t[...,1],t[...,0]],axis=-1)
        return xy,t,n
    def metric(self,s,r,stretch=1):
        ds=np.linspace(-3*stretch*r,3*stretch*r,241);xy,t,n=self.at(s+ds);_,t0,_=self.at(s)
        angles=np.arctan2(t[:,1],t[:,0]);a0=np.arctan2(t0[1],t0[0]);da=np.arctan2(np.sin(angles-a0),np.cos(angles-a0))
        w=np.exp(-.5*(ds/(stretch*r))**2);rms=np.sqrt(np.sum(w*da*da)/w.sum())
        cross=np.gradient(t,ds,axis=0);k=np.sum(cross*n,axis=1)
        # Arc-normal map J=1-v*k: compression/inversion risk over visible rope.
        return dict(turn_rms_deg=float(np.degrees(rms)),turn_range_deg=float(np.degrees(np.ptp(da))),
                    jacobian_min_visible=float(1-r*np.max(abs(k))),
                    jacobian_min_3sigma=float(1-3*r*np.max(abs(k))),max_abs_curvature=float(np.max(abs(k))))

def photo_curve():return Curve(base.ensure_curve()['line'])

def protocol():
    if (BUNDLE/'protocol.json').exists():raise ValueError('Protocol already frozen; do not silently replace selections')
    BUNDLE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    cfg=read(base.BUNDLE/'sampling.json');curve=photo_curve();sites=cfg['sites'];ss=np.array([q['s'] for q in sites]);pool=[]
    for i,s in enumerate(np.linspace(0,curve.length,371,endpoint=False)):
        r=float(np.interp(s,np.r_[ss,curve.length],np.r_[[q['radius'] for q in sites],sites[0]['radius']]))
        d=float(np.interp(s,np.r_[ss,curve.length],np.r_[[q['diameter'] for q in sites],sites[0]['diameter']]))
        xy,t,n=curve.at(s)
        pool.append(dict(source=f'T{i:03}',s=float(s),xy=xy.tolist(),tangent=t.tolist(),tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))),radius=r,diameter=d,
                         **curve.metric(s,r),long_metric=curve.metric(s,r,2)))
    selected=[]
    for group,reverse in [('straight',False),('curved',True)]:
        chosen=[]
        for q in sorted(pool,key=lambda q:q['turn_rms_deg'],reverse=reverse):
            if any(min(abs(q['s']-a['s']),curve.length-abs(q['s']-a['s']))<6*(q['radius']+a['radius']) for a in selected):continue
            if any(np.linalg.norm(np.array(q['xy'])-a['xy'])<3*(q['radius']+a['radius']) for a in selected):continue
            chosen.append(dict(q,id=('S' if group=='straight' else 'C')+str(len(chosen)+1),group=group,split='geometry-selected diagnostic'))
            selected.append(chosen[-1])
            if len(chosen)==6:break
        if len(chosen)<6:raise ValueError(f'Only {len(chosen)} eligible {group} sites; inspect geometry before changing rule')
    cfg=dict(request='R244',selection='371 arc-spaced candidates ranked ONLY by Gaussian-weighted tangent-turn RMS. Six lowest first, then six highest remaining. Arc separation >=6*(Ri+Rj), Euclidean >=3*(Ri+Rj). Previously studied photo; not independent held-out evidence.',image=cfg['image'],image_sha256=cfg['image_sha256'],source_sampling_sha256=sha(base.BUNDLE/'sampling.json'),curve_seed_sha256=sha(ROOT/'photo2/spline-seed-r175.json'),sites=selected,
        arms=dict(A='naturally straight/curved selection; isotropic sigma=R in tangent frame',B='long tangent-frame Gaussian sigma_u=2R,sigma_v=R',C='same long Gaussian in arc-length/normal coordinates, no intensity Jacobian compensation'),
        constants=dict(prominence_min=3,max_pairs=6,separation_resolution=1.5,angle_floor_deg=3,score_margin=.5,uncertainty='anisotropic Gaussian frequency resolution; R243 d20% and tangent5deg retained; curvature reported separately'),
        variants=[dict(name='primary'),dict(name='width-',width=.8),dict(name='width+',width=1.2),dict(name='center-',shift=-.25),dict(name='center+',shift=.25),dict(name='low-',low=.8),dict(name='low+',low=1.2),dict(name='high-',high=.8),dict(name='high+',high=1.2)],
        safety='Reflect interpolation outside photograph only where Gaussian mass is negligible; reject if missing weighted mass exceeds0.1%. Reject straightening where J<=0 in |v|<=3*sigma_v; Gaussian tails beyond this are not certified.',
        controls='Reuse existing R243 e65 orthographic/perspective uniform/mixed, both hands: eight images x eight sites x V/Y x three arms. No new rendering parameters.',
        stop='Compare methods/curvature, retain failures. No segmentation, palette normalization, global fit/index/pattern work.')
    save(BUNDLE/'protocol.json',cfg);save(OUT/'geometry-candidates.json',pool)
    rgb=base.image_rgb(ROOT/cfg['image']);fig,ax=plt.subplots(figsize=(9,11),layout='constrained');ax.imshow(rgb)
    for q in selected:
        x,y=q['xy'];t=np.array(q['tangent']);r=q['radius'];color='#00ffff' if q['group']=='straight' else '#ffaa00'
        ax.plot([x-2*r*t[0],x+2*r*t[0]],[y-2*r*t[1],y+2*r*t[1]],c=color,lw=2)
        ax.text(x+12,y,q['id'],color=color,bbox=dict(facecolor='black',alpha=.7,pad=1))
    ax.set_title('Selection from centerline geometry before spectra\nCyan S: lowest turning; orange C: highest remaining turning');fig.savefig(BUNDLE/'locations.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(3,4,figsize=(16,12),layout='constrained')
    for ax,q in zip(axes.flat,selected):
        x,y=q['xy'];r=q['radius'];ds=np.linspace(-3*r,3*r,100);line=curve.at(q['s']+ds)[0]
        ax.imshow(rgb);ax.plot(*line.T,c='cyan',lw=1);ax.set_xlim(x-2*r,x+2*r);ax.set_ylim(y+2*r,y-2*r)
        ax.set_title(f"{q['id']} {q['source']} turn RMS={q['turn_rms_deg']:.1f}°\nlong-window RMS={q['long_metric']['turn_rms_deg']:.1f}°")
    fig.savefig(BUNDLE/'raw-crops.png',dpi=120);plt.close(fig)
    print([(q['id'],q['source'],round(q['turn_rms_deg'],2),round(q['long_metric']['turn_rms_deg'],2)) for q in selected])

def mapped_patch(rgb,q,curve,arm,variant=None):
    v=variant or {};r=q['radius']*v.get('width',1);stretch=ARMS[arm];su=r*stretch;sv=r
    s=q['s']+v.get('shift',0)*q['diameter'];xy,t,n=curve.at(s)
    # R245 user-requested tail check changes support only, not Gaussian sigma.
    half=int(np.ceil(v.get('extent',3)*su));size=2*half+1
    yy,xx=np.mgrid[-half:half+1,-half:half+1];u=xx.astype(float);z=yy.astype(float)
    if arm=='C':
        line,ts,ns=curve.at(s+u[0]);mx=line[None,:,0]+z*ns[None,:,0];my=line[None,:,1]+z*ns[None,:,1]
    else:
        mx=xy[0]+u*t[0]+z*n[0];my=xy[1]+u*t[1]+z*n[1]
    # No abrupt short-axis crop. Upstream crops negligible mask tails then pads
    # back to a square with edge propagation; metadata is retained for inverses.
    g=np.exp(-.5*((u/su)**2+(z/sv)**2)).astype('float32')
    outside=(mx<0)|(mx>rgb.shape[1]-1)|(my<0)|(my>rgb.shape[0]-1)
    lost=float(g[outside].sum()/g.sum())
    if lost>.001:raise ValueError(f'Outside weighted support {lost:.5f}>0.001')
    metric=curve.metric(s,r,stretch)
    if arm=='C' and metric['jacobian_min_3sigma']<=0:raise ValueError('Fold within three transverse Gaussian sigmas')
    patch=np.stack([map_coordinates(rgb[:,:,k],[my,mx],order=1,mode='reflect') for k in range(3)],axis=-1)
    return patch,g,dict(sigma_u=su,sigma_v=sv,missing_weight=lost,**metric,center_s=s,tangent_deg=float(np.degrees(np.arctan2(-t[1],t[0]))))

def analyze(rgb,q,curve,arm,ch,variant=None):
    v=variant or {};patch,g,geom=mapped_patch(rgb,q,curve,arm,v);bank=core.make_channel_bank(patch);x=bank.arrays['HSV V' if ch=='V' else 'Y luminance'];d=q['diameter']
    lo=(1/3)/d*v.get('low',1);hi=min(.49,2/d*v.get('high',1))
    product=core.compute_fft_products(x,g,False,square_fft=True,square_pad_mode='edge',fft_highpass_percent=100*np.sqrt(2)*lo,fft_lowpass_percent=100*np.sqrt(2)*hi)
    f=product[6].astype(complex);size=len(f);c=size//2;yy,xx=np.mgrid[:size,:size];power=abs(f)**2;total=float(power.sum())
    ru=size/(2*np.pi*geom['sigma_u']);rv=size/(2*np.pi*geom['sigma_v'])
    candidates=core.find_top_fft_peaks(np.log1p(abs(f)),top_k=40,min_distance=1);peaks=[];used=[]
    for p in candidates:
        dx,dy=p['x'],p['y'];rad=np.hypot(dx,dy);freq=rad/size
        if not lo<freq<hi:continue
        if any(min(np.hypot((dx-a)/ru,(dy-b)/rv),np.hypot((dx+a)/ru,(dy+b)/rv))<1.5 for a,b in used):continue
        dist=np.minimum(np.hypot((xx-c-dx)/ru,(c-yy-dy)/rv),np.hypot((xx-c+dx)/ru,(c-yy+dy)/rv))
        support=(dist<=1.25)&(power>0);ann=(dist>2)&(dist<4)&(power>0)
        peakpower=float(power[int(c-dy),int(c+dx)]);bg=float(np.median(power[ann])) if ann.any() else 0;prom=peakpower/max(bg,1e-12)
        if prom<3:continue
        pp=float(power[support].sum());angle=float(base.wrap(np.degrees(np.arctan2(dy,dx))))
        au=max(3.,float(np.degrees(np.arctan2(np.hypot(dy*ru,dx*rv)/rad,rad))))
        fu=float(np.hypot(dx*ru,dy*rv)/rad/size)
        peaks.append(dict(candidate=len(peaks)+1,offset=[int(dx),int(dy)],frequency=freq,fd=freq*d,diameter=d,
                          relative_angle=angle,angle=float(base.wrap(angle+geom['tangent_deg'])),angle_uncertainty=au,
                          frequency_uncertainty=fu,pair_power=pp,band_fraction=pp/max(total,1e-12),prominence=prom,
                          legacy_log_power_sum=p['log_power_sum']))
        used.append((dx,dy))
        if len(peaks)==6:break
    rec=dict(window=q['id'],group=q.get('group','control'),arm=arm,channel=ch,s=q['s'],diameter=d,xy=q['xy'],
             tangent_deg=geom['tangent_deg'],n=size,low=lo,high=hi,variant=v.get('name','primary'),geometry=geom,
             total_band_power=total,peaks=peaks,fft_reconstruction_metadata=product[7])
    return rec,dict(patch=patch,g=g,x=x,f=f)

def cards(q,records,path):
    fig,axes=plt.subplots(3,7,figsize=(22,10),layout='constrained')
    for row,arm in enumerate(ARMS):
        rec,a=records[arm]['V'];ry,ay=records[arm]['Y'];vmax=max(np.log1p(abs(a['f'])).max(),np.log1p(abs(ay['f'])).max())
        axes[row,0].imshow(a['patch']);axes[row,0].set_title(arm+' sampled RGB (u along rope)')
        axes[row,1].imshow(a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title('V × Gaussian')
        for col,r,b in [(2,rec,a),(3,ry,ay)]:
            axes[row,col].imshow(np.log1p(abs(b['f'])),cmap='magma',origin='upper',extent=[-.5,.5,-.5,.5],vmin=0,vmax=vmax)
            for p in r['peaks']:
                dx,dy=np.array(p['offset'])/r['n']
                for sign in (-1,1):axes[row,col].plot(sign*dx,sign*dy,'o',mfc='none',mec=COLORS[p['candidate']-1],ms=7)
                axes[row,col].text(dx,dy,str(p['candidate']),color='white',fontsize=7)
            lim=r['high']*1.1;axes[row,col].set_xlim(-lim,lim);axes[row,col].set_ylim(-lim,lim);axes[row,col].set_title(r['channel']+' FFT; cycles/pixel')
        inv=base.inverse_pairs(a['f'],rec['peaks'][:3]);amp=max(abs(inv).max(),1e-12);axes[row,4].imshow(inv,cmap='gray',vmin=-amp,vmax=amp);axes[row,4].set_title('V top3 inverse; unassigned')
        axes[row,5].imshow(ay['x']*ay['g'],cmap='gray',vmin=0,vmax=1);axes[row,5].set_title('Y × Gaussian')
        iy=base.inverse_pairs(ay['f'],ry['peaks'][:3]);amp=max(abs(iy).max(),1e-12)
        axes[row,6].imshow(iy,cmap='gray',vmin=-amp,vmax=amp);axes[row,6].set_title('Y top3 inverse; unassigned')
        for col in (0,1,4,5,6):axes[row,col].axis('off')
    fig.suptitle(q['id']+' — A isotropic tangent crop; B long tangent crop; C long arc-normal straightening\nAll input RGB bilinear sampled at one native pixel; no channel normalization or spectrum-dependent location selection')
    fig.savefig(path,dpi=115);plt.close(fig)

def run_photo():
    cfg=read(BUNDLE/'protocol.json');rgb=base.image_rgb(ROOT/cfg['image']);curve=photo_curve();rows=[]
    assert sha(ROOT/cfg['image'])==cfg['image_sha256']
    for q in cfg['sites']:
        display={a:{} for a in ARMS}
        for arm in ARMS:
          for v in cfg['variants']:
           for ch in ('V','Y'):
            try:
                r,a=analyze(rgb,q,curve,arm,ch,v);r['fits']=base.models_for(r);rows.append(r)
                if v['name']=='primary':display[arm][ch]=(r,a)
            except ValueError as exc:rows.append(dict(window=q['id'],group=q['group'],arm=arm,channel=ch,variant=v['name'],failure=str(exc),peaks=[]))
        if all(len(x)==2 for x in display.values()):cards(q,display,BUNDLE/(q['id']+'-comparison.png'))
        print('Measured',q['id'],flush=True)
    save(OUT/'photo-measurements.json',rows)

def control_curve(case):
    from photo2.fft_helicity_controls import setup
    rope,project,_,meta=setup(case['elevation'],case['perspective'])
    theta=np.linspace(0,2*np.pi,16001)
    xyz=np.column_stack((rope.chain_major*np.cos(theta),rope.chain_major*np.sin(theta),np.full(len(theta),meta['target'][2])))
    line=project(xyz);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
    return Curve(line),theta,s


def run_controls():
    manifest=read(base.BUNDLE/'controls-manifest.json');results=[]
    for case in manifest:
        if case['elevation']!=65:continue
        rgb=base.image_rgb(ROOT/case['image']);assert sha(ROOT/case['image'])==case['image_sha256']
        curve,theta,ss=control_curve(case)
        for orig in case['sites']:
            q=dict(orig,s=float(np.interp(np.radians(orig['theta']),theta,ss)),group='control')
            for arm in ['native',*ARMS]:
              for ch in ('V','Y'):
                r,_=base.analyze(rgb,q,ch) if arm=='native' else analyze(rgb,q,curve,arm,ch)
                fits=[]
                for hand in (-1,1):
                    fits.append(dict(hand=hand,**base.score(r['peaks'],base.predicted(r['tangent_deg'],hand,65,0,6.1109157489,0))))
                r.update(arm=arm,truth=case['hand'],case=case['id'],appearance=case['appearance'],perspective=case['perspective'],fits=fits)
                results.append(r)
        print('Control',case['id'],flush=True)
    save(OUT/'controls.json',results)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','photo','controls']);a=p.parse_args()
    {'prepare':protocol,'photo':run_photo,'controls':run_controls}[a.stage]()

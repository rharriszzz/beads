"""Curated phase, transform and selected contrast evidence for R244."""
from photo2.fft_curvature import *

def pair_sheet(rgb,q,curve,path):
    fig,axes=plt.subplots(6,8,figsize=(21,14),layout='constrained')
    for row,(arm,ch) in enumerate((a,c) for a in ARMS for c in ('V','Y')):
        r,b=analyze(rgb,q,curve,arm,ch);axes[row,0].imshow(b['patch']);axes[row,0].set_title(arm+' '+ch+' sampled')
        axes[row,1].imshow(b['x']*b['g'],cmap='gray',vmin=0,vmax=1);axes[row,1].set_title('Windowed '+ch)
        for i,p in enumerate(r['peaks']):
            inv=base.inverse_pairs(b['f'],[p]);amp=max(abs(inv).max(),1e-12)
            axes[row,i+2].imshow(inv,cmap='gray',vmin=-amp,vmax=amp)
            axes[row,i+2].set_title(f"{p['candidate']}: {p['relative_angle']:.1f}°\nf={p['frequency']:.4f}")
        for ax in axes[row]:ax.axis('off')
    fig.suptitle(q['id']+' — individual conjugate-pair inverse contributions, preserving complex phase\nUnassigned strength-ranked candidates. Contrast independently scaled for visibility; do not compare amplitudes by brightness.')
    fig.savefig(path,dpi=110);plt.close(fig)


def main():
    cfg=read(BUNDLE/'protocol.json');rgb=base.image_rgb(ROOT/cfg['image']);curve=photo_curve()
    # Retain a whole comparison card when one primary method is rejected.
    q=next(q for q in cfg['sites'] if q['id']=='C4')
    fig,axes=plt.subplots(3,4,figsize=(14,11),layout='constrained')
    for row,arm in enumerate(ARMS):
        for col,ch in enumerate(('V','Y')):
            try:
                rec,a=analyze(rgb,q,curve,arm,ch)
                axes[row,2*col].imshow(a['x']*a['g'],cmap='gray',vmin=0,vmax=1)
                axes[row,2*col].set_title(arm+' '+ch+' × Gaussian')
                axes[row,2*col+1].imshow(np.log1p(abs(a['f'])),cmap='magma')
                c=rec['n']//2
                for p in rec['peaks']:
                    dx,dy=p['offset']
                    for sign in (-1,1):axes[row,2*col+1].plot(c+sign*dx,c-sign*dy,'o',mfc='none',mec=COLORS[p['candidate']-1])
                axes[row,2*col+1].set_title(ch+' spectrum (individual display scale)')
            except ValueError as exc:
                axes[row,2*col].text(.5,.5,arm+' '+ch+' rejected\n'+str(exc),ha='center',va='center',wrap=True)
        for ax in axes[row]:ax.axis('off')
    fig.suptitle('C4: image-edge failure retained; B primary needs too much missing photograph\nA and C wider-window variants also fail. No replacement location or relaxed boundary rule.')
    fig.savefig(BUNDLE/'C4-comparison.png',dpi=125);plt.close(fig)
    for name in ('S1','C1'):
        q=next(q for q in cfg['sites'] if q['id']==name);pair_sheet(rgb,q,curve,BUNDLE/(name+'-individual-pairs.png'))
    q=next(q for q in cfg['sites'] if q['id']=='C1');s=q['s'];r=q['radius'];xy,t,n=curve.at(s);us=np.linspace(-6*r,6*r,121)
    fig,axes=plt.subplots(1,3,figsize=(17,7),layout='constrained')
    for ax,arm in zip(axes[:2],('B','C')):
        ax.imshow(rgb)
        for v in np.linspace(-3*r,3*r,7):
            if arm=='B':points=xy+us[:,None]*t+v*n
            else:
                line,_,norm=curve.at(s+us);points=line+v*norm
            ax.plot(*points.T,lw=.8,alpha=.8)
        for u in np.linspace(-6*r,6*r,13):
            vv=np.linspace(-3*r,3*r,61)
            if arm=='B':points=xy+u*t+vv[:,None]*n
            else:
                loc,_,nn=curve.at(s+u);points=loc+vv[:,None]*nn
            ax.plot(*points.T,c='cyan',lw=.5,alpha=.6)
        ax.set_xlim(xy[0]-7*r,xy[0]+7*r);ax.set_ylim(xy[1]+7*r,xy[1]-7*r);ax.set_title('C1 '+arm+' sampling grid ±3 Gaussian sigmas')
    patch,g,geom=mapped_patch(rgb,q,curve,'C');axes[2].imshow(patch);axes[2].contour(g,levels=[np.exp(-4.5),np.exp(-2),np.exp(-.5)],colors='cyan',linewidths=.7);axes[2].set_title(f"Straightened C1\nminimum Jacobian bound={geom['jacobian_min_3sigma']:.2f}")
    fig.suptitle('Straightening changes spatial coordinates, preserves image brightness\nThe approximate centerline is not a measured bead surface; compression affects off-center texture.')
    fig.savefig(BUNDLE/'straightening-map.png',dpi=135);plt.close(fig)
    # Select known-truth examples reproducibly, keeping improvement and failure.
    windows=read(BUNDLE/'control-windows.json');groups={}
    for rec in windows:groups.setdefault((rec['window'],rec['channel']),{})[rec['arm']]=rec
    contrasts=[]
    for key,rs in groups.items():
        contrasts.append(dict(window=key[0],channel=key[1],case=rs['C']['case'],delta=rs['C']['signed_margin']-rs['B']['signed_margin']))
    picks=[dict(max(contrasts,key=lambda p:p['delta']),reason='largest C-minus-B true-hand margin gain'),dict(min(contrasts,key=lambda p:p['delta']),reason='largest C-minus-B true-hand margin loss')]
    paired={}
    for r in windows:
        if r['arm']=='C':paired.setdefault(r['window'],{})[r['channel']]=r
    for ch in ('V','Y'):
        other='Y' if ch=='V' else 'V';q=max(paired.values(),key=lambda q:q[ch]['signed_margin']-q[other]['signed_margin'])
        picks.append(dict(window=q[ch]['window'],channel=ch,case=q[ch]['case'],delta=q[ch]['signed_margin']-q[other]['signed_margin'],reason=ch+' largest known-truth margin advantage within C'))
    manifest=read(base.BUNDLE/'controls-manifest.json')
    for i,pick in enumerate(picks):
        case=next(c for c in manifest if c['id']==pick['case']);cu,theta,ss=control_curve(case);raw=base.image_rgb(ROOT/case['image']);q=next(q for q in case['sites'] if q['id']==pick['window']);q=dict(q,s=float(np.interp(np.radians(q['theta']),theta,ss)),group='control')
        display={a:{ch:analyze(raw,q,cu,a,ch) for ch in ('V','Y')} for a in ARMS}
        pick['figure']=f'control-example-{i+1}.png';pick['truth']=case['hand'];pick['results']=[r for r in windows if r['window']==pick['window']]
        cards(q,display,BUNDLE/pick['figure'])
    save(BUNDLE/'selected-examples.json',picks)
    # Raw mathematical bent wave, same phantom as the geometry test.
    R=180.;y,x=np.mgrid[:769,:769];u=R*np.arctan2(y-384,x-384);v=R-np.hypot(x-384,y-384)
    raw=np.repeat((.5+.2*np.cos(2*np.pi*(u/20+v/32)+.61))[:,:,None],3,axis=2).astype('float32');theta=np.linspace(0,2*np.pi,8001)
    cu=Curve(np.column_stack((384+R*np.cos(theta),384+R*np.sin(theta))));q=dict(id='Bent phase signal (not bead appearance)',s=0.,xy=[564.,384.],radius=18.,diameter=20.)
    display={a:{ch:analyze(raw,q,cu,a,ch) for ch in ('V','Y')} for a in ARMS};cards(q,display,BUNDLE/'phase-phantom.png')
    print('Saved individual-pair, warp and selected control evidence')

if __name__=='__main__':main()

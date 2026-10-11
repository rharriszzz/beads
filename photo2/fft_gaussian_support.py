"""R245: finite support sensitivity for the circular Gaussian, sigma unchanged.

Added after R244 results in response to the maker's mask/crop question. Separate
from the frozen three-arm comparison; no favorable result replaces its baseline.
"""
from photo2.fft_curvature import *


def relative_band_change(q,a4,a3):
    # Same large FFT grid isolates added tails from a finer frequency-bin grid.
    x=a4['x'];g4=a4['g'];n=len(g4);half=n//2;y,xcoord=np.mgrid[-half:half+1,-half:half+1]
    h3=int(np.ceil(3*q['radius']));g3=g4*((abs(xcoord)<=h3)&(abs(y)<=h3))
    f4=np.fft.fftshift(np.fft.fft2(x*g4));f3=np.fft.fftshift(np.fft.fft2(x*g3))
    freq=np.hypot(xcoord,y)/n;band=(freq>1/(3*q['diameter']))&(freq<=2/q['diameter'])
    return float(np.linalg.norm((f4-f3)[band])/max(np.linalg.norm(f4[band]),1e-12))


def main():
    cfg=read(BUNDLE/'protocol.json');curve=photo_curve();rgb=base.image_rgb(ROOT/cfg['image']);baseline=read(OUT/'photo-measurements.json')
    cams=read(base.BUNDLE/'summary.json')['camera_choices_from_development'];rows=[];examples={}
    for q in cfg['sites']:
      for ch in ('V','Y'):
        r3=next(r for r in baseline if (r['window'],r['arm'],r['channel'],r['variant'])==(q['id'],'A',ch,'primary'))
        try:
            r4,a4=analyze(rgb,q,curve,'A',ch,dict(name='support4',extent=4));r4['fits']=base.models_for(r4)
            r3check,a3=analyze(rgb,q,curve,'A',ch)
            assert r3check['peaks']==r3['peaks']
            row=dict(window=q['id'],channel=ch,common_grid_relative_band_change=relative_band_change(q,a4,a3),n3=r3['n'],n4=r4['n'],peaks3=r3['peaks'],peaks4=r4['peaks'],
                     gap3=best_at(r3,-1,cams[f'{ch}/-1'])['score']-best_at(r3,1,cams[f'{ch}/1'])['score'],gap4=best_at(r4,-1,cams[f'{ch}/-1'])['score']-best_at(r4,1,cams[f'{ch}/1'])['score'])
            examples[(q['id'],ch)]=(a3,a4)
        except ValueError as exc:row=dict(window=q['id'],channel=ch,failure=str(exc))
        rows.append(row)
    baseline_controls=read(OUT/'controls.json');controls=[]
    for case in read(base.BUNDLE/'controls-manifest.json'):
        if case['elevation']!=65:continue
        cu,theta,ss=control_curve(case);raw=base.image_rgb(ROOT/case['image'])
        for orig in case['sites']:
          q=dict(orig,s=float(np.interp(np.radians(orig['theta']),theta,ss)))
          for ch in ('V','Y'):
            r4,_=analyze(raw,q,cu,'A',ch,dict(name='support4',extent=4))
            r3=next(r for r in baseline_controls if (r['window'],r['arm'],r['channel'])==(q['id'],'A',ch))
            fits=[base.score(r4['peaks'],base.predicted(r4['tangent_deg'],h,65,0,6.1109157489,0)) for h in (-1,1)]
            controls.append(dict(window=q['id'],channel=ch,truth=case['hand'],margin3=(r3['fits'][0]['score']-r3['fits'][1]['score'])*case['hand'],margin4=(fits[0]['score']-fits[1]['score'])*case['hand']))
    save(BUNDLE/'gaussian-support-results.json',dict(photo=rows,controls=controls,interpretation='Common-grid relative complex band change isolates added tails. Candidate/score changes also include finer FFT-bin sampling at 4 sigma. Small spectral changes may alter ambiguous peak ranking; no baseline replacement.'))
    # Mathematical weights on a common physical scale; preserve ellipse distinction.
    fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained');y,x=np.mgrid[-4:4:401j,-4:4:401j]
    for ax,title,su in zip(axes[:2],['A: circular Gaussian','B/C: elliptical Gaussian'],[1.,2.]):
        g=np.exp(-.5*((x/su)**2+y*y));ax.imshow(g,extent=[-4,4,-4,4],origin='lower',vmin=0,vmax=1,cmap='gray');ax.contour(x,y,g,levels=[np.exp(-4.5),np.exp(-2),np.exp(-.5)],colors=['cyan','yellow','orange']);ax.set_title(title);ax.set_xlabel('u / R');ax.set_ylabel('v / R');ax.set_aspect('equal')
    z=np.linspace(0,4,401);axes[2].semilogy(z,np.exp(-.5*z*z),label='center-to-edge profile')
    for extent in (3,4):axes[2].axvline(extent,c='gray',ls=':');axes[2].plot(extent,np.exp(-.5*extent**2),'o')
    axes[2].set_xlabel('Distance / sigma');axes[2].set_ylabel('Weight relative to center');axes[2].grid(alpha=.2);axes[2].set_title('3 sigma: 1.11%; 4 sigma: 0.0335%')
    fig.suptitle('Gaussian throughout the window: no flat rectangular center and no separate edge taper\nContours are 1, 2 and 3 normalized radii. B/C image crops extend farther along u than this mask illustration.')
    fig.savefig(BUNDLE/'gaussian-weights.png',dpi=140);plt.close(fig)
    # Fixed example plus largest observed spectral perturbation; selection disclosed.
    valid=[r for r in rows if not r.get('failure')];worst=max(valid,key=lambda r:r['common_grid_relative_band_change'])
    keys=[('S1','V'),(worst['window'],worst['channel'])];fig,axes=plt.subplots(2,6,figsize=(18,7),layout='constrained')
    for row,key in enumerate(keys):
        a3,a4=examples[key];r=next(r for r in rows if (r['window'],r['channel'])==key);vmax=max(np.log1p(abs(a['f'])).max() for a in (a3,a4))
        for i,a in enumerate((a3,a4)):
            axes[row,3*i].imshow(a['g'],cmap='gray',vmin=0,vmax=1);axes[row,3*i].set_title(f'{key[0]} {key[1]}: {3+i} sigma support')
            axes[row,3*i+1].imshow(a['x']*a['g'],cmap='gray',vmin=0,vmax=1);axes[row,3*i+1].set_title('Same sigma; weighted image')
            axes[row,3*i+2].imshow(np.log1p(abs(a['f'])),cmap='magma',vmin=0,vmax=vmax,extent=[-.5,.5,-.5,.5]);axes[row,3*i+2].set_xlim(-.07,.07);axes[row,3*i+2].set_ylim(-.07,.07);axes[row,3*i+2].set_title(f'FFT; band change {r["common_grid_relative_band_change"]:.2%}')
    fig.suptitle('Tail-support sensitivity: first site fixed; second is greatest common-grid complex spectral change\nBoth are circular Gaussians with the same sigma. FFT grids differ; display frequency coordinates are shared.')
    fig.savefig(BUNDLE/'gaussian-support-comparison.png',dpi=130);plt.close(fig)
    print('support',len(rows),'photo',len(controls),'controls; worst relative band change',worst['common_grid_relative_band_change'])

def angle_illustration():
    """Known waves: window covariance changes blur, not frequency coordinates."""
    n=401;y,x=np.mgrid[-200:201,-200:201];freqs=np.array([[12,4],[-5,15],[17,-11]],float)/257
    fig,axes=plt.subplots(4,3,figsize=(13,15),layout='constrained')
    for row,(su,sv,theta) in enumerate([(24,24,0),(48,24,0),(24,24,35),(48,24,35)]):
        t=np.radians(theta);u=np.cos(t)*x+np.sin(t)*(-y);v=-np.sin(t)*x+np.cos(t)*(-y)
        a=.5+sum(.12*np.cos(2*np.pi*(kx*u+ky*v)+.4) for kx,ky in freqs)
        g=np.exp(-.5*((u/su)**2+(v/sv)**2)).astype('float32')
        f=core.compute_fft_products(a.astype('float32'),g,False,square_fft=True,square_pad_mode='edge',fft_highpass_percent=100*np.sqrt(2)*.025,fft_lowpass_percent=100*np.sqrt(2)*.105)[6]
        shape='Circular' if su==sv else 'Elliptical'
        axes[row,0].imshow(g,cmap='gray',vmin=0,vmax=1);axes[row,0].set_title(f'{shape} weights, rotation {theta}°')
        axes[row,1].imshow(a*g,cmap='gray',vmin=0,vmax=1);axes[row,1].set_title('Same three waves; square pixels')
        ax=axes[row,2];ax.imshow(np.log1p(abs(f)),cmap='magma',extent=[-.5,.5,-.5,.5],vmin=0,vmax=6)
        rot=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
        for i,k in enumerate(freqs@rot.T):
            for sign in (-1,1):ax.plot(*(sign*k),'x',c='cyan',ms=10)
            ax.text(*(k+.003),str(i+1),c='white')
        ax.set_xlim(-.105,.105);ax.set_ylim(-.105,.105);ax.set_xlabel('fx (cycles/pixel)');ax.set_ylabel('fy, image-up (cycles/pixel)');ax.set_title('FFT; × exact input frequencies')
        axes[row,0].axis('off');axes[row,1].axis('off')
    fig.suptitle('Rotate the signal AND Gaussian together: frequency directions rotate by the same angle\nChanging Gaussian widths changes peak blur/strength, not the coordinate scale. Cyan crosses are known inputs, not fitted outputs.\nThe 35° examples are evaluated analytically on the pixel grid, without image interpolation.')
    fig.savefig(BUNDLE/'gaussian-angle-explanation.png',dpi=135);plt.close(fig)


def bandpass_illustration():
    cfg=read(BUNDLE/'protocol.json');q=cfg['sites'][0];curve=photo_curve();rgb=base.image_rgb(ROOT/cfg['image'])
    rec,a=analyze(rgb,q,curve,'A','V');full=core.compute_fft_products(a['x'],a['g'],False,square_fft=True,square_pad_mode='edge')[6]
    fig,axes=plt.subplots(2,3,figsize=(16,10),layout='constrained');z=np.linspace(0,2.7,1201)
    ax=axes[0,0];ax.plot(z,((z>1/3)&(z<=2)).astype(float),c='black',label='primary')
    for factor,col in [(.8,'#2266aa'),(1.2,'#cc6600')]:
        ax.axvline(factor/3,c=col,ls='--');ax.axvline(2*factor,c=col,ls='--',label=f'cutoff ×{factor}')
    ax.set_ylim(-.08,1.15);ax.set_xlabel('Radial frequency × approximate bead diameter (f*d)');ax.set_ylabel('Multiplier on complex FFT coefficients');ax.set_title('Hard circular annulus; no angular preference');ax.legend();ax.grid(alpha=.2)
    vmax=float(np.percentile(np.log1p(abs(full)),99.8))
    for ax,f,title in [(axes[0,1],full,'S1 V: before frequency filter'),(axes[0,2],a['f'],'S1 V: retained band')]:
        ax.imshow(np.log1p(abs(f)),cmap='magma',extent=[-.5,.5,-.5,.5],vmin=0,vmax=vmax)
        for radius,color in [(rec['low'],'cyan'),(rec['high'],'lime')]:ax.add_patch(plt.Circle((0,0),radius,fill=False,color=color,lw=1.5))
        ax.set_xlim(-.075,.075);ax.set_ylim(-.075,.075);ax.set_xlabel('fx (cycles/pixel)');ax.set_ylabel('fy (cycles/pixel)');ax.set_title(title)
    rows=read(OUT/'photo-measurements.json');cams=read(base.BUNDLE/'summary.json')['camera_choices_from_development'];variants=['primary','low-','low+','high-','high+']
    for ax,arm in zip(axes[1],ARMS):
        for site,color in [('S1','#2266aa'),('C1','#cc6600')]:
          for ch,style in [('V','o-'),('Y','s--')]:
            rs=[next(r for r in rows if (r['window'],r['arm'],r['channel'],r['variant'])==(site,arm,ch,v)) for v in variants]
            gaps=[best_at(r,-1,cams[f'{ch}/-1'])['score']-best_at(r,1,cams[f'{ch}/1'])['score'] for r in rs]
            ax.plot(range(5),gaps,style,c=color,label=site+' '+ch)
        ax.set_xticks(range(5),['primary','low ×.8','low ×1.2','high ×.8','high ×1.2'],rotation=15);ax.axhline(0,c='black',lw=.7);ax.set_ylim(-.6,.6);ax.set_title(arm+' existing cutoff sensitivity');ax.set_ylabel('Hand margin; + favors h+1');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('Band boundaries fixed from rough bead scale, then varied independently ±20%; no winning cutoff selected\nTop spectra share log-magnitude display scale (99.8th percentile clipping for visibility only). Bottom: fixed straight S1 and curved C1 examples.')
    fig.savefig(BUNDLE/'bandpass-explanation.png',dpi=135);plt.close(fig)


if __name__=='__main__':main();angle_illustration();bandpass_illustration()

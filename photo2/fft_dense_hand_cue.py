"""Conditional R250 hand cue from maker's near-zero and diagonal interpretation.

No extraction/track changes. Existing projected reciprocal model, fixed finite
nuisance bank. Family assignment remains a stated hypothesis, not ground truth.
"""
import csv,itertools
import numpy as np
from photo2.fft_dense import *
from photo2.fft_helicity import predicted


def main():
    d=load_measurements(2000);fits=read(BUNDLE/'angle-fits.json');ranges=fits['ranges'];sites=d['records'][::2]
    selected={ch:[] for ch in ('V','Y')}
    # 200 regularly spaced original measured windows, selected by index only.
    for r in d['records']:
        if r['index']%10:continue
        for label,k in [('negative',0),('near_zero',2),('positive',3)]:
            b=ranges[k];ps=[p for p in r['peaks'][:4] if not p['weak'] and not p['boundary_clipped'] and b['low']<=p['relative_angle']<b['high']]
            for p in ps:selected[r['channel']].append(dict(index=r['index'],tangent=r['tangent_deg'],category=label,angle=p['relative_angle'],weight=1/len(ps),observation=p['observation']))
    bank=[]
    for hand,el,roll,rho,phase in itertools.product((-1,1),(45,65,85,90),(0,45,90,135),(4.,6.1109157489),(-25,0,25)):
        models={}
        for i in range(0,2000,10):
            m=predicted(sites[i]['tangent_deg'],hand,el,roll,rho,phase)
            # Family1's row normal is near-zero. Other normals mapped by their sign.
            near=m[0]['relative_angle'];others=sorted([m[1]['relative_angle'],m[2]['relative_angle']])
            models[i]=dict(near_zero=near,negative=others[0],positive=others[1])
        for ch,rows in selected.items():
            residual=np.array([float(wrap(r['angle']-models[r['index']][r['category']])) for r in rows]);weights=np.array([r['weight'] for r in rows]);nz=np.array([r['category']=='near_zero' for r in rows])
            # Positive nuisance bias means measured angle exceeds modeled angle.
            # This is a sensitivity to systematic tangent/calibration error, not an estimated camera.
            bias=float(np.clip(np.average(residual,weights=weights),-5,5));nbias=float(np.clip(np.average(residual[nz],weights=weights[nz]),-5,5))
            bank.append(dict(channel=ch,hand=hand,elevation=el,roll=roll,rho=rho,phase=phase,rms=float(np.sqrt(np.average(residual**2,weights=weights))),near_zero_rms=float(np.sqrt(np.average(residual[nz]**2,weights=weights[nz]))),bias_within5=bias,rms_with_bias=float(np.sqrt(np.average((residual-bias)**2,weights=weights))),near_zero_bias=nbias,near_zero_rms_with_bias=float(np.sqrt(np.average((residual[nz]-nbias)**2,weights=weights[nz])))))
    best=[]
    for ch,hand,metric in itertools.product(('V','Y'),(-1,1),('rms','near_zero_rms','rms_with_bias','near_zero_rms_with_bias')):
        b=min((r for r in bank if r['channel']==ch and r['hand']==hand),key=lambda r:r[metric]);best.append(dict(metric=metric,**b))
    result=dict(interpretation='Conditional on maker-proposed mapping: near-zero reciprocal peak normal to family1; diagonal normals sorted by sign. Four angular categories are empirical; minus19 remains excluded/unresolved. No per-window selection or nuisance tuning.',model='Existing fft_helicity.predicted, visible-front unrolled local tube, shared camera/phase/radius per hand/channel. Orthographic finite bank, not calibrated photo pose or exhaustive camera uncertainty.',sample='200 equal-arc original windows, every tenth of the 2000-point master; original unsmoothed peaks and equal total category/window weights.',systematic_sensitivity='Common angle bias limited to +/-5deg is a diagnostic, not a measured correction; retained separately.',top_down={str(h):predicted(0,h,90,0) for h in (-1,1)},best=best,angle_offsets={ch:dict(negative_minus_minus45=fits['channels'][ch][0]['constant_angle']+45,near_zero=fits['channels'][ch][2]['constant_angle'],positive_minus_plus45=fits['channels'][ch][3]['constant_angle']-45) for ch in ('V','Y')})
    save(BUNDLE/'conditional-hand-cue.json',result);write_csv(BUNDLE/'conditional-hand-models.csv',bank)
    plot_cues(result,fits)
    print(json.dumps(result,indent=2))


def plot_cues(s,f):
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for ax,ch in zip(axes,('V','Y')):
        labels=['Negative diagonal','Near zero','Positive diagonal'];idx=[0,2,3];ref=np.array([-45,0,45]);xx=np.arange(3)
        vals=[f['channels'][ch][i]['constant_angle'] for i in idx];rms=[f['channels'][ch][i]['rms_residual'] for i in idx]
        ax.errorbar(xx,np.array(vals)-ref,yerr=rms,fmt='o',c='k',label='Observed LS mean ± residual RMS',capsize=4)
        for h,c in [(1,'#277da8'),(-1,'#e76f51')]:
            m=s['top_down'][str(h)];a=[min(m[1]['relative_angle'],m[2]['relative_angle']),m[0]['relative_angle'],max(m[1]['relative_angle'],m[2]['relative_angle'])]
            ax.plot(xx,np.array(a)-ref,'s--',c=c,label=f'Overhead model h{h:+}')
        ax.axhline(0,c='.5',lw=.8);ax.set_xticks(xx,labels);ax.set_ylabel('Offset from −45°, 0°, +45° (degrees)');ax.set_title(ch);ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('Three signed helicity cues, with intrinsic 6/7 asymmetry retained\nIllustrative overhead geometry; conditional projected-model scores are separate. RMS bars are not confidence intervals.')
    fig.savefig(BUNDLE/'helicity-angle-cues.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()

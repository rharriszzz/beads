"""R250 maker-requested four prevalent angle ranges and least-squares fits.

Exploratory categorization AFTER extraction/tracking; never retunes either.
Histogram smoothing locates ranges only. Fits use original unsmoothed observations.
"""
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from photo2.fft_dense import *


def fit(a,weights):
    return float(np.average(a,weights=weights))


def main():
    d=load_measurements(2000);length=d['length'];rows=[]
    for r in d['records']:
        ps=[p for p in r['peaks'][:4] if not p['weak'] and not p['boundary_clipped']]
        for p in ps:rows.append(dict(channel=r['channel'],index=r['index'],s=r['s'],observation=p['observation'],angle=p['relative_angle'],frequency=p['frequency'],weight=1/len(ps),broad=p['broad']))
    edges=np.arange(-90,91);centers=(edges[1:]+edges[:-1])/2
    hist={ch:np.histogram([p['angle'] for p in rows if p['channel']==ch],edges,weights=[p['weight'] for p in rows if p['channel']==ch])[0] for ch in ('V','Y')}
    pooled=sum(hist.values());smooth=gaussian_filter1d(pooled,3,mode='wrap')
    peaks,_=find_peaks(np.tile(smooth,3),distance=15,prominence=3)
    peaks=[int(i-180) for i in peaks if 180<=i<360]
    minima,_=find_peaks(-np.tile(smooth,3));minima=list(minima)
    # Rank local concentrations by mass within +/-10 degrees; no fixed model angles.
    ranked=sorted(peaks,key=lambda i:-sum(pooled[(i+j)%180] for j in range(-10,11)))[:4]
    ranges=[]
    for i in sorted(ranked):
        ii=i+180;l=max(j for j in minima if j<ii)-180;u=min(j for j in minima if j>ii)-180
        ranges.append(dict(mode=float(centers[i]),low=float(l-89.5),high=float(u-89.5),mass_within10=float(sum(pooled[(i+j)%180] for j in range(-10,11)))))
    result=dict(request='R250 user steering: least squares for each of four most prevalent angle ranges',selection='Brightest-four, not weak, not central-clipped. Broad observations retained and flagged. Equal total weight per channel/window. Periodic1deg histogram, sigma3deg display/mode smoothing, local maxima >=15deg apart; select four by mass within +/-10deg, bounds at neighboring pooled minima. Exploratory ranges; minor modes/tails remain unassigned. Fits use unsmoothed angles. Eight contiguous holdout blocks with 300px training embargo; ranges themselves are exploratory and fixed from the full photograph.',ranges=ranges,channels={},length=length,histogram=dict(centers=centers.tolist(),V=hist['V'].tolist(),Y=hist['Y'].tolist(),pooled_smoothed=smooth.tolist()))
    rng=np.random.default_rng(250);assignment=[]
    for ch in ('V','Y'):
        out=[]
        for k,b in enumerate(ranges):
            ps=[p for p in rows if p['channel']==ch and b['low']<=p['angle']<b['high']]
            a=np.array([p['angle'] for p in ps]);w=np.array([p['weight'] for p in ps]);s=np.array([p['s'] for p in ps]);f=np.array([p['frequency'] for p in ps]);mu=fit(a,w);res=a-mu
            X=np.column_stack([np.ones(len(s)),np.sin(2*np.pi*s/length),np.cos(2*np.pi*s/length)])
            beta=np.linalg.lstsq(X*np.sqrt(w[:,None]),a*np.sqrt(w),rcond=None)[0];harm_res=a-X@beta
            # 32 spatial blocks (~289px), fixed ranges; descriptive spatial-resampling interval.
            block=np.minimum((32*s/length).astype(int),31);boot=[]
            for _ in range(500):
                multiplicities=np.bincount(rng.integers(0,32,32),minlength=32);ww=w*multiplicities[block]
                if ww.sum():boot.append(fit(a,ww))
            constant_error=0.;harmonic_error=0.;test_weight=0.
            for fold in range(8):
                test=(8*s/length).astype(int)==fold
                # Remove training centers within 300px of the held-out arc: two 5sigma supports.
                center=(fold+.5)*length/8
                circular_distance=np.abs((s-center+length/2)%length-length/2)
                train=circular_distance>length/16+300
                if not test.any():continue
                cm=fit(a[train],w[train]);bb=np.linalg.lstsq(X[train]*np.sqrt(w[train,None]),a[train]*np.sqrt(w[train]),rcond=None)[0]
                constant_error+=float(np.sum(w[test]*(a[test]-cm)**2));harmonic_error+=float(np.sum(w[test]*(a[test]-X[test]@bb)**2));test_weight+=float(w[test].sum())
            unb=np.array([not p['broad'] for p in ps]);out.append(dict(range=k+1,observations=len(ps),window_coverage=len({p['index'] for p in ps})/2000,constant_angle=mu,rms_residual=float(np.sqrt(np.average(res**2,weights=w))),angle_p05_p95=np.percentile(a,[5,95]).tolist(),frequency_p05_p50_p95=np.percentile(f,[5,50,95]).tolist(),spatial_block_interval=np.percentile(boot,[2.5,97.5]).tolist(),excluding_broad_angle=fit(a[unb],w[unb]),harmonic_coefficients=beta.tolist(),harmonic_amplitude=float(np.hypot(*beta[1:])),harmonic_rms=float(np.sqrt(np.average(harm_res**2,weights=w))),blocked_cv_constant_rms=float(np.sqrt(constant_error/test_weight)),blocked_cv_harmonic_rms=float(np.sqrt(harmonic_error/test_weight))))
            for p in ps:assignment.append(dict(**p,range=k+1,constant_fit=mu,residual=p['angle']-mu))
        result['channels'][ch]=out
    write_csv(BUNDLE/'angle-range-observations.csv',assignment);save(BUNDLE/'angle-fits.json',result)
    print(json.dumps(dict(ranges=ranges,channels=result['channels']),indent=2))


if __name__=='__main__':main()

"""Post-fit descriptive diagnostics; no optimization or denominator modification."""
import csv,json
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from .common import *
from .experiment import *


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    inputs,_=load_evidence();rows=observations();models=read(BASE/'results/export-manifest.json')['models'];out=[];angular=[]
    for name in models:
        m=read(BASE/f'results/native-{name}.json.gz');rr=[r for r in m['records'] if r['trusted'] and r['exists']];res=np.array([r['centroid_residual'] for r in rr]);angle=np.radians([r['orientation_deg'] for r in rr]);phase=np.radians([r['phase_deg'] for r in rr]);patterns={}
        for label,aa in [('axis_orientation',angle),('minor_phase',phase)]:
            design=np.c_[np.ones(len(aa)),np.sin(aa),np.cos(aa),np.sin(2*aa),np.cos(2*aa)];coeff=np.linalg.lstsq(design,res,rcond=None)[0];pred=design@coeff;patterns[label]=dict(coefficients=coeff.tolist(),descriptive_r2=float(1-np.sum((res-pred)**2)/np.sum((res-res.mean(0))**2)))
        sectors=[]
        for sector in range(16):
            group=[r for r in rr if next(q for q in rows if q['id']==r['id'])['sector']==sector];v=np.array([r['centroid_residual'] for r in group]);sectors.append(dict(sector=sector,n=len(group),mean_vector=v.mean(0).tolist() if len(v) else None,mean_error=float(np.mean(np.linalg.norm(v,axis=1))) if len(v) else None))
        d=m['diagnosis'];finite=[r for r in d if r['implied_light_mismatch_deg'] is not None];width=[r['sigma_major_error_px'] for r in rr];best=[r['optimistic_alternative_peak_error_px'] for r in rr if r['optimistic_alternative_peak_error_px'] is not None]
        record=dict(model=name,mean_centroid_vector=res.mean(0).tolist(),orientation_patterns=patterns,sectors=sectors,assigned_surface_farther_than_5px=sum(r['distance_to_sampled_visible_surface_px'] is None or r['distance_to_sampled_visible_surface_px']>5 for r in d),first_hit_disagrees=sum(not r['first_hit_agrees_with_frozen_owner'] for r in d),median_implied_light_mismatch_deg=float(np.median([r['implied_light_mismatch_deg'] for r in finite])),optimistic_alternative_peak_median=float(np.median(best)),median_sigma_major_error=float(np.median(width)),missing_ids=[r['id'] for r in m['records'] if not r['exists']],meaning='Descriptive regressions and optimistic alternatives are diagnostics only; no fitting or reassignment follows.')
        out.append(record)
        if m['light']['kind']=='extended':
            s=Surface(m['parameters'],inputs);assign=read(BASE/f"evidence/ownership-{m['baseline']}.json")['assignments'];ix=list(range(0,len(rows),8));a=[assign[i] for i in ix];r=[rows[i] for i in ix];data=grids(s,[v['owner'] for v in a],.5);r5,_=evaluate(s,data,m['light'],r,a,.5,5);r9,_=evaluate(s,data,m['light'],r,a,.5,9)
            for aa,bb in zip(r5,r9):angular.append(dict(model=name,id=aa['id'],both_exist=aa['exists'] and bb['exists'],centroid_change=float(np.linalg.norm(np.array(aa['predicted']['centroid'])-bb['predicted']['centroid'])) if aa['exists'] and bb['exists'] else None,peak_change=float(np.linalg.norm(np.array(aa['predicted']['peak'])-bb['predicted']['peak'])) if aa['exists'] and bb['exists'] else None))
    save(BASE/'results/residual-diagnosis.json',out);save(BASE/'results/angular-convergence.json',angular)
    names=['fixed-0-directional','fixed-49-directional','joint-15'];fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for name in names:
        m=read(BASE/f'results/native-{name}.json.gz');r=[r for r in m['records'] if r['trusted'] and r['exists']];axes[0,0].scatter([q['station_fraction'] for q in r],[q['centroid_error_px'] for q in r],s=14,label=name);axes[0,1].scatter([q['orientation_deg'] for q in r],[q['centroid_error_px'] for q in r],s=14,label=name);err=np.sort([q['centroid_error_px'] for q in r]);axes[1,0].plot(err,np.arange(1,len(err)+1)/45,label=name)
    for ax in axes[0]:ax.axhline(3,color='gray',linestyle='--');ax.set_ylabel('Centroid error (native pixels)');ax.legend(fontsize=8)
    axes[0,0].set_xlabel('Conditional necklace station');axes[0,1].set_xlabel('Projected bead-axis angle (degrees)');axes[1,0].set_xlabel('Centroid error (native pixels)');axes[1,0].set_ylabel('Fraction of fixed trusted denominator (45)');axes[1,0].axvline(3,color='gray',linestyle='--');axes[1,0].axvline(5,color='gray',linestyle=':');axes[1,0].legend(fontsize=8)
    m=read(BASE/'results/native-joint-15.json.gz');r=[r for r in m['records'] if r['trusted'] and r['exists']];axes[1,1].scatter([q['centroid_residual'][0] for q in r],[q['centroid_residual'][1] for q in r],s=20);axes[1,1].axhline(0,color='gray');axes[1,1].axvline(0,color='gray');axes[1,1].set_xlabel('Horizontal residual (px)');axes[1,1].set_ylabel('Vertical residual (px)');axes[1,1].set_title('Bounded phase candidate, same frozen owners');fig.savefig(REVIEW/'error-plots.png',dpi=140);plt.close(fig)
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');draw=ImageDraw.Draw(im)
    for r in m['records']:
        p=r['observed_centroid'];draw.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),outline='#ffbb35',width=2)
        if r['exists']:
            q=(np.array(p)+4*np.array(r['centroid_residual'])).tolist();draw.line([tuple(p),tuple(q)],fill='#00e5c2',width=3)
        else:draw.text(tuple(p),'MISSING',fill='red')
    im.save(REVIEW/'whole-residuals.png');print('Descriptive diagnostics written; no fitting.')
if __name__=='__main__':main()

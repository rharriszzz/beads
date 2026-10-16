"""Analyze saved native predictions, never fit light/geometry or alter ownership.

The only least-squares operations here are descriptive residual regressions.
Geometric reconstruction is used solely to obtain local frames, pitch and seams.
"""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from scipy.stats import theilslopes, spearmanr
from photo2.r297.common import ROOT, read, save, sha, load_evidence
from photo2.r297.geometry import reference
from photo2.r298.geometry import Chain

BASE=ROOT/'photo2/r300'
PRINCIPAL=['fixed-0-directional','fixed-49-directional','joint-15','fixed-8-directional','fixed-29-directional','fixed-76-directional']
LABELS=['R297 closed −','R298 open −','R299 phase open −','R298 closed −','R298 open +','R298 closed +']


def frame(ref, arc, direction=1):
    arc=np.asarray(arc)%ref.length
    j=np.clip(np.searchsorted(ref.arc,arc,side='right')-1,0,len(ref.delta)-1)
    t=ref.delta[j]/ref.lengths[j,None]*direction
    return t,np.stack([-t[...,1],t[...,0]],axis=-1)


def slope(x,y):
    return float(np.linalg.lstsq(np.c_[np.ones(len(x)),x],y,rcond=None)[0][1]) if len(x)>2 and np.ptp(x)>0 else None


def trend(x,y,sector):
    x=np.asarray(x);y=np.asarray(y);sector=np.asarray(sector)
    if len(x)<4 or np.ptp(x)==0:return dict(n=len(x),slope=None)
    b=slope(x,y); pred=y.mean()+b*(x-x.mean());den=np.sum((y-y.mean())**2)
    groups=np.unique(sector);leave=[slope(x[sector!=g],y[sector!=g]) for g in groups];leave=[v for v in leave if v is not None]
    # Sampling sensitivity only: sectors are spatial blocks, not independent new images.
    rng=np.random.default_rng(300);boot=[]
    for _ in range(1000):
        ids=np.concatenate([np.flatnonzero(sector==g) for g in rng.choice(groups,len(groups),replace=True)])
        if np.ptp(x[ids])>0:boot.append(slope(x[ids],y[ids]))
    means=np.array([[x[sector==g].mean(),y[sector==g].mean()] for g in groups])
    return dict(n=len(x),slope=b,r2=float(1-np.sum((y-pred)**2)/den) if den else 0.,spearman=float(spearmanr(x,y).statistic) if np.ptp(y) else 0.,theil_sen=float(theilslopes(y,x)[0]),leave_sector_out_range=[min(leave),max(leave)] if leave else None,sector_bootstrap_95=np.quantile(boot,[.025,.975]).tolist(),equal_sector_slope=slope(means[:,0],means[:,1]),cyclic_origin_slope_range=[min(slope((x-a)%1,y) for a in np.arange(16)/16),max(slope((x-a)%1,y) for a in np.arange(16)/16)])


def regress(design,y,groups):
    coef=np.linalg.lstsq(design,y,rcond=None)[0];pred=design@coef
    den=np.sum((y-y.mean(axis=0))**2);err=0.;null=0.
    for g in np.unique(groups):
        train=groups!=g;test=~train
        c=np.linalg.lstsq(design[train],y[train],rcond=None)[0]
        err+=np.sum((y[test]-design[test]@c)**2);null+=np.sum((y[test]-y[train].mean(axis=0))**2)
    return dict(coefficients=coef.tolist(),in_sample_r2=float(1-np.sum((y-pred)**2)/den),leave_sector_out_skill=float(1-err/null))


def describe(rows,kind='centroid'):
    valid=[r for r in rows if r['exists']]
    result=dict(n=len(rows),predicted=len(valid),missing_ids=[r['id'] for r in rows if not r['exists']],ambiguous=sum(r['ownership_ambiguous'] for r in rows),distinct_owners=len({r['index'] for r in valid}))
    if len(valid)<4:return result
    x=np.array([r['fraction'] for r in valid]);g=(x*16).astype(int)
    v=np.array([r[kind+'_xy'] for r in valid]);tn=np.array([r[kind+'_tn'] for r in valid]);mag=np.linalg.norm(v,axis=1);dn=np.array([r[kind+'_diameters'] for r in valid]);eq=np.array([r[kind+'_index_equivalent'] for r in valid]);theta=np.array([r['angle'] for r in valid]);phi=np.radians([r['phase_deg'] for r in valid]);curv=np.array([r['bend_deg_96px'] for r in valid])
    one=np.ones(len(x));orient=np.c_[one,np.sin(theta),np.cos(theta),np.sin(2*theta),np.cos(2*theta)];ph=np.c_[one,np.sin(phi),np.cos(phi)]
    result.update(mean_xy=v.mean(0).tolist(),mean_tn=tn.mean(0).tolist(),rms=float(np.sqrt(np.mean(mag**2))),rms_after_global_translation=float(np.sqrt(np.mean(np.sum((v-v.mean(0))**2,axis=1)))),magnitude_quantiles=np.quantile(mag,[.5,.9,1]).tolist(),diameter_quantiles=np.quantile(dn,[.5,.9,1]).tolist(),parallel=trend(x,tn[:,0],g),normal=trend(x,tn[:,1],g),magnitude=trend(x,mag,g),index_equivalent=trend(x,eq,g),index_equivalent_range=[float(eq.min()),float(eq.max())],model_frame_parallel=trend(x,[r[kind+'_model_tn'][0] for r in valid],g),patterns={key:regress(X,v,g) for key,X in [('global_translation',one[:,None]),('progression',np.c_[one,x]),('orientation',orient),('orientation_and_progression',np.c_[orient,x]),('minor_phase',ph),('bend',np.c_[one,curv])]},regions=[])
    for sector in range(16):
        mask=g==sector
        result['regions'].append(dict(sector=sector,n=int(mask.sum()),mean_tn=tn[mask].mean(0).tolist() if mask.any() else None,mean_magnitude=float(mag[mask].mean()) if mask.any() else None,mean_index_equivalent=float(eq[mask].mean()) if mask.any() else None))
    order=np.argsort(x);xx=x[order];yy=tn[order,0];ee=eq[order]
    # Demeaned CUSUM is a regional-bias display, NOT cumulative count error.
    cusum=np.r_[0,np.cumsum(yy-yy.mean())]/len(yy)
    result['ordered']=dict(ids=[valid[i]['id'] for i in order],fraction=xx.tolist(),cusum_mean_parallel=cusum.tolist(),cusum_range=float(np.ptp(cusum)),local_index_increment=np.diff(ee).tolist(),net_index_displacement=(ee-ee[0]).tolist(),endpoint_index_change=float(ee[-1]-ee[0]),endpoint_parallel_change=float(yy[-1]-yy[0]),maximum_gap_fraction=float(np.diff(np.r_[xx,xx[0]+1]).max()))
    return result


def seam_stats(rows,seam,kind):
    rr=[r for r in rows if r['trusted'] and r['exists']];offset=np.array([((r['fraction']-seam+.5)%1)-.5 for r in rr]);out=[]
    for width in [.03,.06,.10]:
        before=[r for r,d in zip(rr,offset) if -width<=d<0];after=[r for r,d in zip(rr,offset) if 0<=d<=width]
        means=lambda a:np.mean([r[kind+'_tn'] for r in a],axis=0).tolist() if a else None
        bm,am=means(before),means(after)
        out.append(dict(width_fraction=width,before_ids=[r['id'] for r in before],after_ids=[r['id'] for r in after],before_mean_tn=bm,after_mean_tn=am,after_minus_before=(np.array(am)-bm).tolist() if bm is not None and am is not None else None))
    before=np.flatnonzero(offset<0);after=np.flatnonzero(offset>=0)
    return dict(fraction=seam,nearest_before_distance_fraction=float(-offset[before].max()) if len(before) else None,nearest_after_distance_fraction=float(offset[after].min()) if len(after) else None,windows=out,trend_from_seam=trend((np.array([r['fraction'] for r in rr])-seam)%1,[r[kind+'_tn'][0] for r in rr],[r['sector'] for r in rr]))


def analyze(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    inputs,_=load_evidence();ref=reference();manifest=read(ROOT/'photo2/r299/results/export-manifest.json');names=manifest['models'];models={};ledger=[];sources={}
    measurements=read(ROOT/'photo2/r298/evidence/measurements.json')
    for name in names:
        path=ROOT/f'photo2/r299/results/native-{name}.json.gz';m=read(path);sources[str(path.relative_to(ROOT))]=sha(path)
        scene=Chain(m['parameters'],inputs);p=m['parameters'];rows=[]
        for z in m['records']:
            arc=float(ref.project([z['observed_centroid']])['arc'][0]);fraction=float(((arc-inputs['arc0'])*inputs['direction']/ref.length)%1);t,n=frame(ref,[arc],inputs['direction']);t=t[0];n=n[0]
            k=z['ownership']['index'];owner=z['ownership']['owner'];line,_,_=scene.placement(np.array([k-.01,k+.01]));dline=np.diff(scene.project(line),axis=0)[0]/.02;pitch=float(np.linalg.norm(dline));mt=dline/pitch;mn=np.array([-mt[1],mt[0]])
            bt,_=frame(ref,[arc-48,arc+48],inputs['direction']);bend=float(np.degrees(np.arctan2(np.linalg.det(bt),bt[0]@bt[1])))
            r=dict(model=name,id=z['id'],color=z['color'],trusted=z['trusted'],split=z['split'],exists=z['exists'],missing_reason=z['missing_reason'],index=k,ownership_ambiguous=z['ownership']['ambiguous'],competing_indices=[a['index'] for a in z['ownership']['alternatives']],fraction=fraction,sector=int(fraction*16),observed_centroid=z['observed_centroid'],tangent=t.tolist(),normal=n.tolist(),model_tangent=mt.tolist(),pitch_px=pitch,diameter_px=z['apparent_diameter_px'],angle=float(np.arctan2(t[1],t[0])),bend_deg_96px=bend,phase_deg=z['phase_deg'],index_fraction=(k-scene.start)/scene.n)
            for kind in ['centroid','peak']:
                delta=np.array(z[kind+'_residual']) if z['exists'] else None
                r[kind+'_xy']=delta.tolist() if delta is not None else None
                r[kind+'_tn']=[float(delta@t),float(delta@n)] if delta is not None else None
                r[kind+'_model_tn']=[float(delta@mt),float(delta@mn)] if delta is not None else None
                r[kind+'_diameters']=z[kind+'_normalized_error']
                r[kind+'_index_equivalent']=float(delta@t/pitch) if delta is not None else None
            rows.append(r)
        seam_line,_,_=scene.placement(np.array([scene.start,scene.start+scene.n]));seam_xy=scene.project(seam_line);sa=ref.project(seam_xy)['arc'];sf=((sa-inputs['arc0'])*inputs['direction']/ref.length)%1;seam=float(sf[0]);rr=[r for r in rows if r['trusted']]
        groups={'trusted':rr,'all':rows,'unambiguous':[r for r in rr if not r['ownership_ambiguous']]}
        for color in ['black','red','yellow']:groups[color]=[r for r in rr if r['color']==color]
        model=dict(parameters=p,light=m['light'],groups={kind:{key:describe(value,kind) for key,value in groups.items()} for kind in ['centroid','peak']},seam={kind:seam_stats(rows,seam,kind) for kind in ['centroid','peak']},closure=scene.closure(),seam_xy=seam_xy.tolist(),seam_end_fractions=sf.tolist(),geometry_metrics=m['geometry']['metrics'],photographic={sp:{k:v for k,v in a.items() if k not in ['assignments','separators']} for sp,a in m['geometry']['photographic'].items()},physical={k:v for k,v in m['geometry']['physical'].items() if k not in ['witnesses','index_pairs','fallback']})
        # Signed native boundary errors on all preserved eligible transects.
        profiles=[]
        for obs,pred in zip(measurements['envelope'],m['geometry']['envelope']):
            err=np.array(pred)-obs['bounds'];f=float(((obs['arc']-inputs['arc0'])*inputs['direction']/ref.length)%1)
            profiles.append(dict(id=obs['id'],fraction=f,eligible=obs['eligible'],split=obs['split'],width_error=float(err[1]-err[0]),common_edge_error=float(err.mean()),edge_errors=err.tolist()))
        model['profiles']=profiles
        matches=[]
        for r in rr:
            if not r['exists']:continue
            eligible=[q for q in profiles if q['eligible']];dist=[abs((q['fraction']-r['fraction']+.5)%1-.5)*ref.length for q in eligible];j=int(np.argmin(dist));q=eligible[j]
            matches.append(dict(id=r['id'],profile=q['id'],distance_px=dist[j],normal_residual=r['centroid_tn'][1],common_edge_error=q['common_edge_error'],width_error=q['width_error'],within_96px=bool(dist[j]<=96)))
        close=[r for r in matches if r['within_96px']]
        model['boundary_association']=dict(matches=matches,n=len(close),distinct_profiles=len({r['profile'] for r in close}),correlation_normal_common=float(np.corrcoef([[r['normal_residual'] for r in close],[r['common_edge_error'] for r in close]])[0,1]),limits='Repeated profiles and approximate edge proxies; association does not identify a cause.')
        models[name]=model;ledger.extend(rows)
        print(name, 'slope',round(model['groups']['centroid']['trusted']['parallel']['slope'],2),flush=True)
    # Common finite subset across every principal family; no selective omission hidden.
    common=sorted(set.intersection(*[{r['id'] for r in ledger if r['model']==name and r['trusted'] and r['exists']} for name in PRINCIPAL]))
    for name in PRINCIPAL:models[name]['common_principal']=describe([r for r in ledger if r['model']==name and r['id'] in common])
    fft={}
    for ident in [0,8,29,49,76]:
        path=ROOT/f'photo2/r298/results/fft-{ident}.json';d=read(path);sources[str(path.relative_to(ROOT))]=sha(path)
        fft[str(ident)]=[dict(window=r['window'],channel=r['channel'],best=r['best'],best_fundamental=min(q['fundamental_best']['rms_resolution'] for q in r['predictions']),supported_trios=r['saved_supported_trios']) for r in d['records']]
    baseline=read(ROOT/'photo2/r298/results/model-0.json.gz');structural=[]
    for ident in [0,8,29,49,76]:
        m=read(ROOT/f'photo2/r298/results/model-{ident}.json.gz');neighbor=[]
        for row in m['neighbors']:
            for v in row['predictions']:neighbor.append(dict(id=row['id'],step=v['step'],indices=v['indices'],center_displacement=v['center_displacement'],projected_interval_gap=v['projected_interval_gap'],physical_center_distance=v['physical_center_distance']))
        structural.append(dict(id=ident,dimensions=m['dimensions'],neighbors=neighbor,closure=m['closure']))
    doc=dict(schema=1,reference_length_px=ref.length,anchor_arc=inputs['arc0'],direction=inputs['direction'],models=models,common_principal_ids=common,fft=fft,structure=structural,sources=sources,limits='Retrospective diagnostics conditional on frozen positive-interior owners. Bootstrap ranges describe sector resampling, not calibrated physical uncertainty. Finite, localized matching can hide integer slips and missing stretches. No observations, predictions, ownership, light, or geometry were fitted or changed.')
    save(output/'analysis.json',doc);save(output/'ledger.json',ledger)
    flat=[]
    for r in ledger:
        row={k:v for k,v in r.items() if not isinstance(v,(list,dict))}
        for kind in ['centroid','peak']:
            row[kind+'_parallel_px']=r[kind+'_tn'][0] if r['exists'] else None;row[kind+'_normal_px']=r[kind+'_tn'][1] if r['exists'] else None
        row['competing_indices']=';'.join(map(str,r['competing_indices']));flat.append(row)
    with (output/'residuals.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');w.writeheader();w.writerows(flat)
    return doc,ledger


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=BASE/'results');a=p.parse_args();analyze(a.output)

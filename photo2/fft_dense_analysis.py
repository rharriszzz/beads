"""R250 descriptive statistics and traceable dense-tracking exports."""
import itertools,json
import numpy as np
from scipy.stats import spearmanr
from photo2.fft_dense import *


def rho(a,b):
    if len(a)<3 or np.std(a)==0 or np.std(b)==0:return None
    return float(spearmanr(a,b).statistic)


def pct(a):
    return [float(x) for x in np.percentile(a,[5,50,95])] if len(a) else []


def track_detail(t,records,length):
    obs={p['observation']:dict(p,s=r['s'],curvature=r['curvature'],**{k:r[k] for k in ('red_proxy','yellow_proxy','dark_proxy','highlight_proxy')}) for r in records for p in r['peaks']}
    outgoing={e['source']:e['target'] for e in t['associations'] if e['accepted']};incoming=set(outgoing.values());details=[]
    for g in t['tracks']:
        ids=g['observations'];start=next((o for o in ids if o not in incoming),ids[0]);order=[start]
        while order[-1] in outgoing and outgoing[order[-1]]!=start:
            order.append(outgoing[order[-1]])
        ps=[obs[o] for o in order];ss=np.array([p['s'] for p in ps]);arc=np.r_[0,np.cumsum(np.diff(ss)%length)];angles=np.degrees(np.unwrap(2*np.radians([p['relative_angle'] for p in ps])))/2
        ff=np.array([p['frequency'] for p in ps]);pp=np.array([p['normalized_peak_power'] for p in ps]);short=sum(p['shortlisted'] for p in ps)/len(ps)
        detail=dict(track=g['track'],count=len(ps),span=g['measured_span'],wrap=g['wrap'],closed=g['closed'],start_s=ps[0]['s'],end_s=ps[-1]['s'],shortlist_fraction=short,rank_min=g['rank_min'],rank_max=g['rank_max'],weak_fraction=g['weak_count']/len(ps),angle_p05_p50_p95=pct(angles),frequency_p05_p50_p95=pct(ff),power_ratio_p95_p05=float(np.percentile(pp,95)/max(np.percentile(pp,5),1e-30)),broad_fraction=float(np.mean([p['broad'] for p in ps])),clipped_fraction=float(np.mean([p['boundary_clipped'] for p in ps])))
        if len(ps)>=3:
            coeff=np.polyfit(arc,angles,1);res=angles-np.polyval(coeff,arc)
            detail.update(angle_linear_slope_deg_per100=float(coeff[0]*100),angle_detrended_mad_deg=float(np.median(abs(res-np.median(res)))),frequency_slope_per100=float(np.polyfit(arc,ff,1)[0]*100),angle_increment_p05_p50_p95=pct(np.diff(angles)),frequency_increment_p05_p50_p95=pct(np.diff(ff)))
        details.append(detail)
    return details,obs


def summarize(records,t,length):
    details,obs=track_detail(t,records,length);edges=[e for e in t['associations'] if e['accepted']];supported=[bool(any(x['supported'] for x in r['trios'])) for r in records]
    curvature=np.abs([r['curvature'] for r in records]);q=np.quantile(curvature,[.25,.75]);low=curvature<=q[0];high=curvature>=q[1]
    principal=[d for d in details if d['span']>=150 and d['shortlist_fraction']>=.25]
    principal_ids={d['track'] for d in principal};principal_obs=[o for o in obs if t['assignment'][o] in principal_ids]
    # Within-fragment demeaned descriptive correlations; no independent-sample p values.
    residual={k:[] for k in ('logpower','frequency','abs_curvature','red_proxy','yellow_proxy','dark_proxy','highlight_proxy')}
    for d in principal:
        ps=[obs[o] for o in next(g for g in t['tracks'] if g['track']==d['track'])['observations']]
        arrays=dict(logpower=np.log10([p['normalized_peak_power'] for p in ps]),frequency=np.array([p['frequency'] for p in ps]),abs_curvature=np.abs([p['curvature'] for p in ps]))
        arrays.update({k:np.array([p[k] for p in ps]) for k in ('red_proxy','yellow_proxy','dark_proxy','highlight_proxy')})
        for k,a in arrays.items():residual[k].extend(a-np.mean(a))
    corr={k:rho(residual['logpower'],v) for k,v in residual.items() if k!='logpower'}
    dr=[float(wrap(obs[e['target']]['relative_angle']-obs[e['source']]['relative_angle'])) for e in edges]
    df=[obs[e['target']]['frequency']-obs[e['source']]['frequency'] for e in edges]
    # Continuation of a local supported reciprocal trio requires three accepted identities.
    out={e['source']:e['target'] for e in edges};pairs=[];trio_run=0;best=0
    for r in records:
        triples={tuple(sorted(r['peaks'][i-1]['observation'] for i in tr['candidates'])) for tr in r['trios'] if tr['supported']}
        pairs.append(triples)
    good=[]
    for i,triples in enumerate(pairs):
        nxt=pairs[(i+1)%len(pairs)]
        good.append(any(all(o in out for o in ids) and tuple(sorted(out[o] for o in ids)) in nxt for ids in triples))
    # Follow the SAME three identities, not a sequence of different passing trios.
    triple_edges=[]
    for i,triples in enumerate(pairs):
        for ids in triples:
            if all(o in out for o in ids):
                target=tuple(sorted(out[o] for o in ids))
                if target in pairs[(i+1)%len(pairs)]:triple_edges.append((ids,target))
    parent={ids:ids for triples in pairs for ids in triples}
    def root(ids):
        while parent[ids]!=ids:parent[ids]=parent[parent[ids]];ids=parent[ids]
        return ids
    for a,b in triple_edges:parent[root(b)]=root(a)
    counts={}
    for a,b in triple_edges:counts[root(a)]=counts.get(root(a),0)+1
    best=max(counts.values(),default=0)*length/len(records)
    summary=dict(locations=len(records),failures=sum('failure' in r for r in records),observations=len(obs),tracks=len(details),accepted_adjacent=len(edges),eligible_adjacent=sum(e['kind']=='adjacent' for e in t['associations']),ambiguous_observations=len(t['ambiguous']),tentative_gaps=sum(e['kind']=='tentative_gap' for e in t['associations']),unique_tentative_gaps=sum(e.get('unique_gap',False) for e in t['associations']),wrap_accepted=sum(e['wrap'] for e in edges),closed_tracks=sum(d['closed'] for d in details),persistent_fragments=len(principal),longest_span=max(d['span'] for d in details),top4_in_persistent_fraction=sum(obs[o]['shortlisted'] for o in principal_obs)/max(sum(p['shortlisted'] for p in obs.values()),1),rank_change_fraction=float(np.mean([obs[e['source']]['candidate']!=obs[e['target']]['candidate'] for e in edges])),rank1_changes=sum(obs[e['source']]['candidate']==1 and obs[e['target']]['candidate']!=1 for e in edges),angle_step_p05_p50_p95=pct(dr),frequency_step_p05_p50_p95=pct(df),supported_trio_fraction=float(np.mean(supported)),trio_continuation_fraction=float(np.mean(good)),longest_supported_trio_run=best,trio_fraction_low_curvature=float(np.mean(np.array(supported)[low])),trio_fraction_high_curvature=float(np.mean(np.array(supported)[high])),curvature_quartiles=q.tolist(),within_fragment_power_correlations=corr,within_fragment_frequency_curvature_rho=rho(residual['frequency'],residual['abs_curvature']),top_tracks=sorted(principal,key=lambda d:-d['span'])[:12])
    # Coarse nonoverlap-oriented descriptive check, no p-values or independence claim.
    dec=records[::max(1,int(np.ceil(120/(length/len(records)))))];summary['coarse_120px_trio_curvature_rho']=rho([abs(r['curvature']) for r in dec],[int(any(t['supported'] for t in r['trios'])) for r in dec]);summary['coarse_120px_count']=len(dec)
    return summary,details


def main():
    data=load_measurements(2000);length=data['length'];density=[];alltracks={};summary={};detailsall=[]
    for n in (200,500,1000,2000):
        alltracks[n]={}
        for ch in ('V','Y'):
            rs=[r for r in data['records'] if r['channel']==ch and r['index']%(2000//n)==0]
            t=associate(rs,length);alltracks[n][ch]=t;s,d=summarize(rs,t,length)
            density.append(dict(n=n,channel=ch,spacing=length/n,**{k:v for k,v in s.items() if k not in ('top_tracks','within_fragment_power_correlations')}))
            if n==2000:summary[ch]=s;detailsall.extend(d)
            print('Analyzed',n,ch,'longest',round(s['longest_span']),flush=True)
    comparisons=[]
    for coarse,fine in ((200,1000),(500,1000),(1000,2000)):
        for ch in ('V','Y'):
            a=alltracks[coarse][ch];b=alltracks[fine][ch];out={e['source']:e['target'] for e in b['associations'] if e['accepted']};edges=[e for e in a['associations'] if e['accepted']];same=0;changed=0;lost=0
            for e in edges:
                target=e['source']
                for _ in range(fine//coarse):target=out.get(target)
                if target==e['target']:same+=1
                elif target is None:lost+=1
                else:changed+=1
            comparisons.append(dict(coarse=coarse,fine=fine,channel=ch,accepted_coarse=len(edges),same_endpoints=same,different_endpoints=changed,fine_path_broken=lost))
    summary['density_comparison']=comparisons
    # V/Y mutual matches at identical locations, no fusion.
    cross=[]
    for i in range(2000):
        v,y=[next(r for r in data['records'][2*i:2*i+2] if r['channel']==ch) for ch in ('V','Y')]
        for e in match_edges(v['peaks'],y['peaks']):cross.append(dict(index=i,s=v['s'],**e))
    summary['cross_channel']=dict(accepted=sum(e['accepted'] for e in cross),eligible=len(cross))
    obs={p['observation']:p for r in data['records'] for p in r['peaks']}
    matched=[e for e in cross if e['accepted']]
    summary['cross_channel'].update(angle_difference_p05_p50_p95=pct([float(wrap(obs[e['target']]['relative_angle']-obs[e['source']]['relative_angle'])) for e in matched]),frequency_difference_p05_p50_p95=pct([obs[e['target']]['frequency']-obs[e['source']]['frequency'] for e in matched]),both_top4=sum(obs[e['source']]['shortlisted'] and obs[e['target']]['shortlisted'] for e in matched))
    for ch in ('V','Y'):
        ee=[e for e in alltracks[2000][ch]['associations'] if e['accepted']]
        out={e['source'] for e in ee}
        ends=[p for o,p in obs.items() if o.startswith(ch+':') and o not in out]
        summary[ch]['identical_fft_bin_fraction']=float(np.mean([obs[e['source']]['offset']==obs[e['target']]['offset'] for e in ee]))
        summary[ch]['accepted_edges_involving_weak']=sum(obs[e['source']]['weak'] or obs[e['target']]['weak'] for e in ee)
        summary[ch]['endpoint_rank5_to8_fraction']=float(np.mean([p['candidate']>=5 for p in ends]))
    # Tracking sensitivity: change association tolerance only; observations stay fixed.
    sensitivity=[]
    for gate,margin,frame in ((.8,.25,'relative_angle'),(1.2,.25,'relative_angle'),(1.,.1,'relative_angle'),(1.,.4,'relative_angle'),(1.,.25,'angle')):
        for ch in ('V','Y'):
            rs=[r for r in data['records'] if r['channel']==ch];tt=associate(rs,length,gate,margin,frame,gaps=False);base={(e['source'],e['target']) for e in alltracks[2000][ch]['associations'] if e['accepted']};alt={(e['source'],e['target']) for e in tt['associations'] if e['accepted']}
            sensitivity.append(dict(channel=ch,gate=gate,margin=margin,frame=frame,accepted=len(alt),base_accepted=len(base),same=len(base&alt),removed=len(base-alt),added=len(alt-base),longest_span=max(x['measured_span'] for x in tt['tracks'])))
    summary['tracking_sensitivity']=sensitivity;save(BUNDLE/'summary.json',summary);save(BUNDLE/'density.json',density);save(BUNDLE/'track-statistics.json',detailsall)
    save(BUNDLE/'tracks.json',alltracks[2000]);write_csv(BUNDLE/'cross-channel.csv',cross)
    candidates=[];windows=[];assoc=[];events=[]
    for r in data['records']:
        ch=r['channel'];t=alltracks[2000][ch];amb=set(t['ambiguous'])
        for p in r['peaks']:
            candidates.append(dict(observation=p['observation'],channel=ch,index=r['index'],s=r['s'],x=r['x'],y=r['y'],tangent_deg=r['tangent_deg'],curvature=r['curvature'],track=t['assignment'][p['observation']],ambiguous=p['observation'] in amb,**{k:p[k] for k in ('candidate','shortlisted','angle','relative_angle','radius_bins','frequency','wavelength','peak_bin_power','normalized_peak_power','relative_brightness','pair_power','band_fraction','prominence','weak','broad','broad_width','boundary_clipped','frequency_resolution','angle_uncertainty')},offset_x=p['offset'][0],offset_y=p['offset'][1]))
        windows.append(dict(channel=ch,index=r['index'],s=r['s'],x=r['x'],y=r['y'],tangent_deg=r['tangent_deg'],curvature=r['curvature'],failure=r.get('failure',''),candidates=len(r['peaks']),supported_trios=json.dumps([tr['candidates'] for tr in r['trios'] if tr['supported']]),**{k:r.get(k) for k in ('total_band_power','red_proxy','yellow_proxy','dark_proxy','highlight_proxy')}))
    for ch,t in alltracks[2000].items():
        for e in t['associations']:assoc.append(dict(channel=ch,**{k:e.get(k) for k in ('source','target','kind','accepted','cost','margin','wrap','arc_gap','unique_gap')}))
        inc={e['target'] for e in t['associations'] if e['accepted']};out={e['source'] for e in t['associations'] if e['accepted']};amb=set(t['ambiguous'])
        for r in (r for r in data['records'] if r['channel']==ch):
            for p in r['peaks']:
                o=p['observation']
                if o not in inc or o not in out:events.append(dict(channel=ch,index=r['index'],s=r['s'],observation=o,track=t['assignment'][o],rank=p['candidate'],appearance=o not in inc,disappearance=o not in out,ambiguous=o in amb,weak=p['weak'],clipped=p['boundary_clipped']))
    write_csv(BUNDLE/'candidates.csv',candidates);write_csv(BUNDLE/'windows.csv',windows);write_csv(BUNDLE/'associations.csv',assoc);write_csv(BUNDLE/'events.csv',events)
    print('Wrote all traceable exports',flush=True)


if __name__=='__main__':main()

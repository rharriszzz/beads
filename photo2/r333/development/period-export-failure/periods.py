"""Bounded periodic and structured-prior searches; no adopted sequence or shifts."""
import argparse,time,csv
from pathlib import Path
from .common import *
from photo2.r330.pattern import dataset as old_dataset,scan,viterbi
from photo2.r331.analyze import evaluate,motif_entries
from photo2.r329.common import canonical
PERIODS=[104]+list(range(200,400))

def occurrence_score(k,c,w,p):
    pred=np.zeros((len(k),3));base=np.zeros_like(pred)
    for occurrence in sorted(set((k//p).tolist())):
        tr=k//p!=occurrence;te=~tr;th,ba,_=fit_keys(k%p,c,w,tr);pred[te]=th[k[te]%p];base[te]=ba
    return dict(gain_nats=float(np.average(np.log(pred[np.arange(len(c)),c]/base[np.arange(len(c)),c]),weights=w)),agreement=float(np.mean(pred.argmax(1)==c)),occurrences=len(set((k//p).tolist())))

def run(out,null_trials=19):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=dataset();og,states,oldids,oldobs,ost,ob,oc,ow=old_dataset();lookup={o:i for i,o in enumerate(ids)};names=sorted(canonical(states['working']));ii=np.array([lookup[o] for o in names]);maps=[];rankings=[];full=[]
    for name,state in states.items():
        coord=canonical(state);present=np.array([o in coord for o in names]);aa=np.array([coord.get(o,(0,0)) for o in names])
        for fam,wt in [('A',[7,6]),('B',[6,7])]:
            k=aa@wt;N=int(np.dot(state['H'],wt));key=name+'-'+fam;maps.append((key,k,present,N));rankings.append(dict(map=key,H=state['H'],N=N,cohort=int(present.sum()),ranking=scan(k[present],c[ii][present],w[ii][present],b[ii][present],PERIODS)))
    # Main complete R332 cohort; geographic held-out exploration (historical
    # test sections are already exposed, and R332 additions remain unreviewed).
    predictions={}
    for fam,wt in [('A',[7,6]),('B',[6,7])]:
        k=ab@wt;N=int(np.dot(g['H'],wt))
        for p in PERIODS:
            r,pr,ba=evaluate(k,c,w,b,p,details=True);r.update(family=fam,N=N,cyclic=N%p==0,maker=(200<=p<=399 and p%13!=0),parent=None);full.append(r);predictions[fam,p,None]=pr
        r,pr,ba=evaluate(k,c,w,b,208,parent=104,details=True);r.update(family=fam,N=N,cyclic=N%208==0,maker=False);full.append(r);predictions[fam,208,104]=pr
    maker=sorted([r for r in full if r['maker']],key=lambda r:-r['penalized_gain']);short={(r['family'],r['period'],None) for r in maker[:8]}|{('A',104,None),('A',208,None),('A',208,104),('B',207,None),('B',299,None)}
    motifs=[];sens=[];joint=[]
    spatialkey,_=spatial_keys(ab);spatialpr,spatialba=cross_predict(spatialkey,c,w,b,guard=1)
    for fam,p,parent in sorted(short,key=str):
        k=ab@([7,6] if fam=='A' else [6,7]);N=int(np.dot(g['H'],[7,6] if fam=='A' else [6,7]));entries=motif_entries(ids,k,c,w,b,p)
        motifs.append(dict(family=fam,period=p,parent=parent,N=N,known=sum(e['color']!='?' for e in entries),unknown=sum(e['color']=='?' for e in entries),unobserved=sum(not e['observations'] for e in entries),entries=entries,distinct_occurrence_test=occurrence_score(k,c,w,p)))
        for guard in [0,1]:
            for blackweight in [.25,.55,1.]:
                ww=w.copy();ww[(c==2)&(w!=.25)]=blackweight;r=evaluate(k,c,ww,b,p,parent=parent,guard=guard);sens.append(dict(r,family=fam,black_weight=blackweight))
        # Structured prior as a diagnostic: period residuals have to explain
        # something BEYOND the independently trained spatial feature predictor.
        pr=np.zeros((len(c),3));base=np.zeros_like(pr)
        for block in range(12):
            tr=~np.isin(b,[(block-1)%12,block,(block+1)%12]);te=b==block;th,ba,cc=fit_keys(k%p,c,w,tr)
            sk,_,_=fit_keys(spatialkey,c,w,tr);prior=sk[spatialkey[te]];rr=k[te]%p;pr[te]=(cc[rr]+3*prior)/(cc[rr].sum(1)[:,None]+3);base[te]=prior
        joint.append(dict(family=fam,period=p,kind='period_counts_plus_spatial_prior',increment_over_spatial=score(pr,base,c,w,b),policy='Spatial prior varies within a residue. This is a joint predictor, not a recovered exact repeating sequence.'))
    # Same common original cohort for all saved maps, exact closure-compatible
    # periods fully evaluated; alternatives do not inherit R332 assignments.
    compatible=[]
    for key,k,present,N in maps:
        for p in PERIODS:
            if p%13 and N%p==0:
                r=evaluate(k,c[ii],w[ii],b[ii],p,present=present);compatible.append(dict(r,map=key,N=N,maker=True,cyclic=True))
    # Orientation/origin invariance checked on all periods of the R332 map.
    gauge=[]
    for fam,wt in [('A',[7,6]),('B',[6,7])]:
        k=ab@wt
        for p in PERIODS:
            a=evaluate(k,c,w,b,p)['gain_nats'];z=evaluate(-k+37,c,w,b,p)['gain_nats'];gauge.append(abs(a-z))
    rng=np.random.default_rng(33301);nulls=[]
    for kind in ['whole_section_translation13','phase_lane_rotation']:
        trials=[]
        for trial in range(null_trials):
            cp=c[ii].copy();wp=w[ii].copy();shifts=rng.integers(0,64,12)*13
            if kind=='phase_lane_rotation':
                for block in range(12):
                    for phase in range(13):
                        jj=np.flatnonzero((b[ii]==block)&((ab[ii]@[7,6])%13==phase));jj=jj[np.argsort(station[ii[jj]])]
                        if len(jj):
                            sh=int(rng.integers(len(jj)));cp[jj]=np.roll(cp[jj],sh);wp[jj]=np.roll(wp[jj],sh)
            best=None;bestmaker=None
            for key,k,present,N in maps:
                kk=k+shifts[b[ii]] if kind=='whole_section_translation13' else k
                rr=scan(kk[present],cp[present],wp[present],b[ii][present],PERIODS)
                r=dict(rr[0],map=key)
                mr=dict(next(x for x in rr if x['period']%13),map=key)
                if best is None or r['selection_score']>best['selection_score']:best=r
                if bestmaker is None or mr['selection_score']>bestmaker['selection_score']:bestmaker=mr
            trials.append(dict(trial=trial,best=best,best_maker=bestmaker))
        nulls.append(dict(kind=kind,trials=trials))
        print('period null',kind,round(time.perf_counter()-t,2),flush=True)
    # Existing saved G replays, not new graph search; all on their own maps.
    greplays=read(ROOT/'photo2/r330/photography/g-replays.json.gz')[-1]['candidates'];grows=[]
    for j,row in enumerate(greplays):
        state=row['state'];coord=canonical(state);present=np.array([o in coord for o in names]);aa=np.array([coord.get(o,(0,0)) for o in names])
        for fam,p,parent in [('A',208,104),('A',306,None),('B',207,None),('B',305,None)]:
            k=aa@([7,6] if fam=='A' else [6,7]);r=evaluate(k,c[ii],w[ii],b[ii],p,present=present,parent=parent);grows.append(dict(r,G=j,family=fam,N=int(np.dot(state['H'],[7,6] if fam=='A' else [6,7])),H=state['H'],changed=sum(coord.get(o)!=co[o] for o in names)))
    # Bounded piecewise shifts: fit on eight sections only; the four withheld
    # sections cannot select shifts. Offset translates a complete geographic bin,
    # so internal equations stay valid; ALL crossing-link violations counted.
    aligns=[];bins=np.minimum((station/station.max()*95).astype(int),95)
    for fam,p,parent in sorted(short,key=str):
        k=ab@([7,6] if fam=='A' else [6,7]);tr=~np.isin(b,[2,5,8,11]);th,ba,_=fit_keys(k%p,c,w,tr)
        for penalty in [6.,12.]:
            shifts,receipt=viterbi(k,c,w,station,th,tr,penalty);pr=th[(k+shifts)%p];unshift=th[k%p];ll=np.log(pr[np.arange(len(c)),c]/unshift[np.arange(len(c)),c]);shiftby=dict(zip(ids,shifts));bad=[dict(source=e['source'],target=e['target'],source_shift=int(shiftby[e['source']]),target_shift=int(shiftby[e['target']])) for e in g['edges'] if shiftby[e['source']]!=shiftby[e['target']]]
            aligns.append(dict(family=fam,period=p,parent=parent,**receipt,training_gain=float(np.average(ll[tr],weights=w[tr])),withheld_gain=float(np.average(ll[~tr],weights=w[~tr])),crossing_equations_violated=len(bad),violations=bad,offsets=[dict(id=o,shift=int(shifts[i])) for i,o in enumerate(ids) if shifts[i]],admissible_without_link_changes=not bool(bad)))
    cuts=[]
    for fam,p in [('A',208),('A',306),('B',207),('B',305),('B',299)]:
        k=ab@([7,6] if fam=='A' else [6,7]);N=int(np.dot(g['H'],[7,6] if fam=='A' else [6,7]))
        for cut in range(12):cuts.append(dict(family=fam,period=p,cut=cut,**evaluate((k-cut*N//12)%N,c,w,b,p)))
    # Geometric alias witnesses including new observations.
    occ={tuple(v):i for i,v in enumerate(ab)};pairs=[]
    for i,v in enumerate(ab):
        for delta in [(8,8),(16,16),(17,15)]:
            j=occ.get(tuple(v+delta))
            if j is not None:pairs.append(dict(source=ids[i],target=ids[j],delta_ab=delta,deltaA=int(np.dot(delta,[7,6])),deltaB=int(np.dot(delta,[6,7])),same_color=bool(c[i]==c[j])))
    result=dict(full_R332=full,common900_scans=rankings,compatible_saved_maps=sorted(compatible,key=lambda r:-r['gain_nats']),motifs=motifs,sensitivity=sens,joint_predictors=joint,nulls=nulls,G=grows,alignments=aligns,cyclic_cuts=cuts,alias_pairs=pairs,reversal_origin_max_delta=max(gauge),best_maker=maker[:16],seconds=time.perf_counter()-t,policy='All R333 cross-validation exploratory; original colors always evaluation targets. Hypothetical shifts are rejected if they violate retained links. R332 additions are not assumed independently reviewed; alternatives scored on common original cohort.')
    save(out/'periods.json.gz',result)
    with (out/'periods.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,['family','N','period','parent','maker','cyclic','gain_nats','gain_over_phase13','penalized_gain','agreement'],extrasaction='ignore');wr.writeheader();wr.writerows(full)
    save(out/'summary.json',dict(best_maker=maker[:8],compatible_saved_maps=result['compatible_saved_maps'][:8],reversal_origin_max_delta=max(gauge),seconds=result['seconds']))
    print('PERIODS',[(r['family'],r['period'],round(r['gain_nats'],4)) for r in maker[:5]],'seconds',result['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--null-trials',type=int,default=19);a=ap.parse_args();run(a.output,a.null_trials)

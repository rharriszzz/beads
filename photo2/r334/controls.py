"""Geographically separated label controls and unchanged-target auto feedback.

These historical labels are exposed and may themselves contain errors. No fresh
blind accuracy claim is made. Thresholds are frozen before this supplemental table.
"""
import argparse,time
from collections import Counter
from pathlib import Path
from .common import *
from photo2.r331.analyze import fit

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=reviewed_dataset('relocated');audit=read(artifact('classification/audit.json.gz'));rr={r['id']:r for r in audit['records']};maker={r['id'] for r in audit['maker_controls']};sections=[];rows=[]
    for block in range(12):
        use=[o for j,o in enumerate(ids) if b[j]==block and o not in maker]
        rows.extend(dict(id=o,section=block,label=obs[o]['color'],prediction=rr[o]['body_prediction'],black_test=rr[o]['black_test']['decision'],held_geographic_control=block in [2,5,8,11]) for o in use)
        counts=Counter((obs[o]['color'],rr[o]['body_prediction']) for o in use);sections.append(dict(section=block,observations=len(use),confusion=[dict(recorded=a,predicted=z,count=n) for (a,z),n in sorted(counts.items())]))
    proposed={r['id']:r['body_prediction'] for r in audit['ranked_color_candidates'] if r['strong_provisional'] and r['id'] in co};corrected=c.copy();lookup={o:i for i,o in enumerate(ids)}
    for o,col in proposed.items():corrected[lookup[o]]=COLORS.index(col)
    target=np.array([o not in proposed for o in ids]);feedback=[]
    for fam,p,parent in [('A',208,104),('A',208,None),('A',306,None),('B',305,None),('B',207,None)]:
        k=ab@([7,6] if fam=='A' else [6,7]);before=np.zeros((len(ids),3));after=np.zeros_like(before)
        for block in range(12):
            train=b!=block;test=(b==block)&target
            for labels,output in [(c,before),(corrected,after)]:theta,_=fit(k,labels,w,p,train,parent=parent);output[test]=theta[k[test]%p]
        jj=np.flatnonzero(target);delta=np.log(after[jj,c[jj]]/before[jj,c[jj]]);feedback.append(dict(family=fam,period=p,parent=parent,unchanged_targets=len(jj),proposed_training_labels=len(proposed),gain_nats=float(np.average(delta,weights=w[jj])),targets_are_unchanged_authoritative_labels=True))
    result=dict(geographic_sections=sections,rows=rows,held_sections=[2,5,8,11],held_observations=sum(r['held_geographic_control'] for r in rows),maker_geography=[dict(id=o,section=int(b[ids.index(o)]),classifier=rr[o]['body_prediction']) for o in sorted(maker)],automatic_training_feedback=feedback,seconds=time.perf_counter()-start,policy='Geographically separated computational controls; historical inventory labels and maker examples already exposed. No independent accuracy. Automatic predictions never become evaluation truth.')
    save(out/'controls.json.gz',result);save(out/'summary.json',{k:v for k,v in result.items() if k!='rows'});print('CONTROLS held',result['held_observations'],'feedback',feedback,flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)

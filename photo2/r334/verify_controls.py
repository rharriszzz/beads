"""Independent unchanged-target feedback calculation, without fitting imports."""
import argparse,time
from .common import ROOT,read,save
import numpy as np

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='photo2/r334');ap.add_argument('--output',default='photo2/r334/controls-verification.json');a=ap.parse_args();from pathlib import Path
    run=Path(a.run);start=time.perf_counter();data=read(run/'controls/controls.json.gz');g=read(run/'overlay/graph.json.gz');raw=read(ROOT/'photo2/r332/results/graph.json.gz');rr={r['id']:r for r in raw['observations']};obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']};ids=sorted(co);ix={o:j for j,o in enumerate(ids)};blocks={r['id']:r['section'] for r in data['rows']+data['maker_geography']};assert len(blocks)==1041;bb=np.array([blocks[o] for o in ids]);ab=np.array([co[o] for o in ids]);colors=['red','yellow','black'];c=np.array([colors.index(obs[o]['color']) for o in ids]);w=np.array([.25 if 'provisional' in str(rr[o]).lower() else .55 if rr[o]['color']=='black' else 1. for o in ids]);proposed={r['id']:r['body_prediction'] for r in read(run/'overlay/ranked-suspects.json.gz') if r['strong_provisional'] and r['id'] in co};after=c.copy()
    for o,col in proposed.items():after[ix[o]]=colors.index(col)
    targets=np.array([o not in proposed for o in ids]);maxdelta=0
    for row in data['automatic_training_feedback']:
        k=ab@([7,6] if row['family']=='A' else [6,7]);p=row['period'];parent=row['parent'];pred=[]
        for labels in [c,after]:
            values=np.zeros((len(ids),3))
            for block in range(12):
                train=np.flatnonzero(bb!=block);test=(bb==block)&targets;freq=np.ones(3);counts=np.zeros((p,3));parentcounts=np.zeros((parent or 1,3))
                for j in train:freq[labels[j]]+=w[j];counts[k[j]%p,labels[j]]+=w[j];parentcounts[k[j]%(parent or 1),labels[j]]+=w[j]
                freq/=freq.sum()
                if parent:
                    prior=(parentcounts+3*freq)/(parentcounts.sum(1)[:,None]+3);prior=prior[np.arange(p)%parent];theta=(counts+prior)/(counts.sum(1)[:,None]+1)
                else:theta=(counts+3*freq)/(counts.sum(1)[:,None]+3)
                values[test]=theta[k[test]%p]
            pred.append(values)
        jj=np.flatnonzero(targets);gain=float(np.average(np.log(pred[1][jj,c[jj]]/pred[0][jj,c[jj]]),weights=w[jj]));delta=abs(gain-row['gain_nats']);assert delta<1e-12;maxdelta=max(maxdelta,delta);assert row['unchanged_targets']==len(jj)==987;assert row['proposed_training_labels']==len(proposed)==54
    assert data['held_observations']==sum(r['section'] in [2,5,8,11] for r in data['rows'])==343
    save(a.output,dict(passed=True,independent_feedback_models=5,unchanged_authoritative_targets=987,proposed_training_labels=54,held_geographic_controls=343,max_score_delta=maxdelta,seconds=time.perf_counter()-start));print('PASS independent unchanged-target feedback',maxdelta)
if __name__=='__main__':main()

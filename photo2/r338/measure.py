"""Bounded black-first pigment audit, independent of pattern/color expectations."""
import argparse,time
from scipy.spatial import cKDTree
from photo2.r334.classify import BodyAudit
from photo2.r335.application import compact_test
from .common import *

def run(out):
    start=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False);g,obs,co=baseline();audit=BodyAudit(g,obs,co);historical={r['id']:r for r in read(ROOT/'photo2/r334/classification/audit.json.gz')['records']};targets={r['id']:obs[r['id']] for r in read(artifact('conflicts/responsibilities.json'))['records']}
    # This support was picked on the original visible body/reflection after
    # native inspection, not as a centroid of a prediction-seeded dark mask.
    targets['R338-N-1009-2826']=dict(id='R338-N-1009-2826',xy=[1009.,2826.],color='?',source='R338 native boundary inspection of unindexed body; fixed original-pixel support',body_boundary=[[999,2818],[1007,2816],[1015,2819],[1021,2826],[1017,2836],[1007,2838],[998,2831]],body_identity='requires separate native-body decision; intensity cannot establish identity')
    for rr in read(artifact('audit/audit.json.gz'))['ranked']:
        if rr['id'] in ['REC266-P143676','REC266-P055677']:targets[rr['id']]=dict(id=rr['id'],xy=rr['xy'],color='?',source=rr['source'])
    r=next(r for r in read(ROOT/'photo2/r332/results/graph.json.gz')['provisional_observations'] if r['id']=='R332-B-0098-0092');targets[r['id']]=dict(id=r['id'],xy=r['xy'],color='black',source='R336 maker-confirmed body; previously deferred indexing')
    # Independent geographic/color-balanced controls: every22nd current ID.
    for o in sorted(co)[::22]:targets.setdefault(o,obs[o])
    anchors=[o for o in co if obs[o]['color'] in ['red','yellow'] and historical.get(o,{}).get('samples',[{},{}])[1].get('common_body_count',0)>=35 and historical[o]['samples'][1].get('common_median_intensity',0)>.18];atree=cKDTree([obs[o]['xy'] for o in anchors]);records=[]
    for o,r in sorted(targets.items()):
        dd,jj=atree.query(r['xy'],k=10);refs=[anchors[int(j)] for d,j in zip(dd,jj) if d<220 and anchors[int(j)]!=o];light=float(np.median([historical[z]['samples'][1]['common_median_intensity'] for z in refs]));samples=[audit.sample(r['xy'],radius,o) for radius in [9,12,15]];broad=[]
        for s in samples:
            test=s.get('black_test',{});ratio=test.get('median_intensity',1)/max(light,.1);broad.append(dict(test,relative_to_adjacent_colored_body=ratio,positive=bool(test.get('raw_positive') and ratio<=.65),negative=bool(test.get('raw_negative'))))
        compact=[compact_test(audit.rgb,r['xy'],radius,audit.tree,audit.names,obs,o,light) for radius in [9,12,15]]
        def decision(tests):
            p=sum(t['positive'] for t in tests);n=sum(t['negative'] for t in tests);return 'black' if p>=2 and n==0 else 'not-black' if n>=2 and p==0 else 'unknown'
        bdec,cdec=decision(broad),decision(compact);result='black' if bdec==cdec=='black' else 'not-black' if bdec==cdec=='not-black' else 'unknown'
        records.append(dict(id=o,xy=r['xy'],recorded_color=r['color'],black_first=result,broad_decision=bdec,compact_decision=cdec,broad=broad,compact=compact,samples=samples,lighting=dict(intensity=light,ids=refs),hue_used_for_black=False,pigment='black' if result=='black' else '?',body_identity_established_by_classifier=False,new_observation=o.startswith('R338-') or o in ['REC266-P143676','REC266-P055677'],maker_confirmed_body=o=='R332-B-0098-0092',source=r.get('source'),body_boundary=r.get('body_boundary')))
    save(out/'pigment.json.gz',dict(records=records,policy='Same R334/R335 black-first two-extent procedure at unchanged support locations; no motif or expected color input. No automatic historical recoloring. Not-black targets retain their existing red/yellow classification; new targets abstain unless independently supported. Annuli do not establish bead identity.',seconds=time.perf_counter()-start));save(out/'summary.json',dict(targets=len(records),decisions=dict(Counter(r['black_first'] for r in records)),new_targets=[{k:r[k] for k in ['id','xy','black_first','broad_decision','compact_decision']} for r in records if r['new_observation'] or r['maker_confirmed_body']],seconds=time.perf_counter()-start));print('MEASURE',len(records),[(r['id'],r['black_first']) for r in records if r['new_observation'] or r['maker_confirmed_body']],time.perf_counter()-start,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)

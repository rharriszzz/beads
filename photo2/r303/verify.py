"""Exact selected-vector replay, witness checks, guard extension, preservation."""
import time
import numpy as np
from .core import *

def main():
    began=time.monotonic();seal=read(BASE/'results/fit-freeze.json');ss=read(BASE/'evidence/sections.json.gz');p=read(BASE/'evidence/protocol.json')
    for path,h in p['sources'].items():assert sha(ROOT/path)==h,path
    assert sha(BASE/'evidence/protocol.json')==seal['protocol_sha256']
    protected=read(BASE/'evidence/preservation.json.gz');bad=[path for path,h in protected.items() if not (ROOT/path).exists() or sha(ROOT/path)!=h];assert not bad,bad
    for s,original in zip(ss,read(ROOT/'photo2/r301/evidence/frozen.json.gz')['sections']):
        for key in ['observations','cues','profiles','bead_dimensions']:assert s[key]==original[key],(s['id'],key)
    replays=[];guards=[]
    for r in seal['selected']:
        s=next(s for s in ss if s['id']==r['section']);v=r['parameters'];expected=read(BASE/f'results/native-{r["name"]}.json.gz')['result']
        got=evaluate(v,s,r['hand'],r['mode'],True)
        for key in ['feasible','loss','contact']:
            assert got.get(key)==expected.get(key),(r['name'],key)
        if not got['feasible']:continue
        for key in ['train','predictions','secondary','indices','centers','polygons']:assert got[key]==expected[key],(r['name'],key)
        c=Scene(v,s,r['hand'],r['mode'])
        for w in got['contact']['witnesses']:
            a,b=w['pair'];n=np.array(w['normal']);gap=(c.centers[b]-c.centers[a])@n-c.support(n,c.g[old.AXES[0]][a])-c.support(n,c.g[old.AXES[0]][b])
            assert abs(gap-w['gap_units'])<1e-10 and gap>1e-6
        replays.append(dict(name=r['name'],positions=c.n,witnesses=got['contact']['pairs'],predictions=len(got['predictions']),loss=got['loss']))
        # A larger address span checks whether new end bodies affect retained
        # photographic predictions; it does not certify a complete necklace.
        extended=Scene(v,s,r['hand'],r['mode'],guards=96);cert=extended.certify(iterations=100,witnesses=True)
        pp,_=old.native(extended,s);a={q['index']:q for q in got['predictions']};b={q['index']:q for q in pp}
        common=set(a)&set(b);error=max([float(np.linalg.norm(np.array(a[k]['point'])-b[k]['point'])) for k in common],default=0)
        guards.append(dict(name=r['name'],positions=extended.n,physical=cert,missing=sorted(set(a)-set(b)),extra=sorted(set(b)-set(a)),max_common_error=error))
    assert seal['numerical_seconds']<=600
    save(BASE/'results/verification.json',dict(utc=utc(),seconds=time.monotonic()-began,protected_files=len(protected),changed=[],replays=replays,guard_extension=guards,evidence_unchanged=True,source_hashes_unchanged=True,numerical_seconds=seal['numerical_seconds']))
    print('Verified',len(protected),'historical files;',len(replays),'native models;',sum(x['witnesses'] for x in replays),'contact witnesses')
    print('Guard extension failures:',[g['name'] for g in guards if not g['physical']['certified'] or g['missing'] or g['extra'] or g['max_common_error']>1e-9])

if __name__=='__main__':main()

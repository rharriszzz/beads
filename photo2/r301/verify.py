"""Read-only delivery audits and deterministic native/scientific replays."""
import time
import numpy as np
from .evidence import BASE,ROOT,read,save,sha,utc
from .model import Local,NAMES,AXES
from .objective import evaluate
from .export import native_evaluate

def main():
    t0=time.monotonic();protected=read(BASE/'evidence/preservation.json.gz');changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    assert not changed,changed
    sections={s['id']:s for s in read(BASE/'evidence/frozen.json.gz')['sections']};records=read(BASE/'results/native-manifest.json.gz');positions=pairs=extended_pairs=0;replayed=[]
    for r in records:
        d=r['result']
        if d.get('baseline') or not d['feasible']:continue
        s=sections[r['section']];p=[d['parameters'][n] for n in NAMES];scene=Local(p,s,d['hand']);np.testing.assert_allclose(scene.centers,d['centers'],atol=1e-12);positions+=scene.n
        for w in d['contact']['witnesses']:
            a,b=w['pair'];normal=np.array(w['normal']);gap=(scene.centers[b]-scene.centers[a])@normal-scene.support(normal,scene.g[AXES[0]][a])-scene.support(normal,scene.g[AXES[0]][b]);assert gap>1e-6;assert abs(gap-w['gap_units'])<1e-10;pairs+=1
        ext=Local(p,s,d['hand'],guards=64)
        for w in d['guard_extension']['physical']['witnesses']:
            a,b=w['pair'];normal=np.array(w['normal']);gap=(ext.centers[b]-ext.centers[a])@normal-ext.support(normal,ext.g[AXES[0]][a])-ext.support(normal,ext.g[AXES[0]][b]);assert abs(gap-w['gap_units'])<1e-10;assert (gap>1e-6)==w['separated'];extended_pairs+=1
        # Complete native reflection and owner-assignment replay for all finals.
        e=native_evaluate(p,s,d['hand'])
        for split in ['train','withheld']:
            for a,b in zip(e[split]['records'],d[split]['records']):
                for key in ['id','owner','index','error','predicted','alternatives']:assert a[key]==b[key],(r['name'],key)
        replayed.append(r['name'])
    receipt=dict(utc=utc(),protected_files=len(protected),changed=changed,positions_replayed=positions,analytic_pair_witnesses_replayed=pairs,extended_pair_witnesses_replayed=extended_pairs,complete_native_replays=replayed,seconds=time.monotonic()-t0,photo_sha256=sha(ROOT/'beads-photo-2.jpg'),fit_seal_sha256=sha(BASE/'results/fit-freeze.json'))
    save(BASE/'results/verification.json',receipt);print(receipt)

if __name__=='__main__':main()

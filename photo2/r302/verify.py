"""Replay sealed selected vectors; audit preserved history and sources."""
import time
import numpy as np
from .core import *

def main():
    began=time.monotonic();s=read(BASE/'evidence/section.json.gz');seal=read(BASE/'results/fit-freeze.json')
    for path,digest in read(BASE/'evidence/protocol.json')['sources'].items():
        assert sha(ROOT/path)==digest,('fitting source changed',path)
    assert sha(BASE/'evidence/protocol.json')==seal['protocol_sha256']
    protected=read(BASE/'evidence/preservation.json.gz');bad=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    assert not bad,bad
    replay=[]
    for selected in seal['selected']:
        name=selected['name'];expected=read(BASE/f'results/native-{name}.json.gz')['result']
        got=evaluate(selected['parameters'],s,selected['hand'],True)
        assert abs(got['loss']-expected['loss'])<1e-10
        assert got['train']==expected['train'];assert got['predictions']==expected['predictions']
        assert got['contact']==expected['contact'];assert got['secondary']==expected['secondary']
        assert 15<=got['local_positions']<=30
        assert abs(2000*(6.5/selected['parameters'][5]-1))<=6.5+1e-9
        replay.append(dict(name=name,positions=len(got['indices']),witnesses=got['contact']['pairs'],loss=got['loss'],predictions=len(got['predictions'])))
    original=read(ROOT/'photo2/r301/evidence/frozen.json.gz')['sections'][0]
    for key in ['observations','cues','bead_dimensions','profiles']:assert original[key]==s[key]
    assert seal['numerical_seconds']<=600
    save(BASE/'results/verification.json',dict(utc=utc(),seconds=time.monotonic()-began,protected_files=len(protected),changed=[],replays=replay,original_observations_and_cues_unchanged=True,source_hashes_unchanged=True,numerical_seconds=seal['numerical_seconds']))
    print('Verified',len(protected),'historical files and',len(replay),'native selected models')

if __name__=='__main__':main()

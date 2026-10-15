"""Replay contact alternatives and actual penetrations using analytic surfaces."""
import numpy as np
from photo2.r279.geometry import sdf
from .common import *
from .geometry import Chain

def results(inputs):
    initial=read(OUT/'initial.json');alternatives=[]
    for i,c in enumerate(initial['candidates']):
        cert=Chain(c['parameters'],inputs).certify()
        alternatives.append(dict(candidate=i,parameters=c['parameters'],training_score=c['train']['score'],certificate=cert))
    model=read(OUT/'revised.json')['unconstrained_winner']
    scene=Chain(model['parameters'],inputs);surface=scene.surface_points();cert=scene.certify();pairs=[]
    for row in cert['witnesses']:
        if row['separated']:continue
        a,b=row['pair'];delta=surface[a]-scene.centers[b]
        q=np.c_[*[delta@scene.g[key][b] for key in ('surface_tangent','surface_normal','surface_binormal')]]
        pairs.append(dict(pair=[int(scene.indices[a]),int(scene.indices[b])],sampled_min_sdf=float(sdf(q).min())))
    return {'initial-contact-alternatives.json':dict(records=alternatives),
        'unconstrained-penetration.json':dict(sampled_penetrating_pairs=sum(r['sampled_min_sdf']<-.001 for r in pairs),
            unresolved_pairs=pairs,scope='Actual sampled source surface entering the other literal annulus; negative values show penetration at sampled points, not a complete volume audit.')}

def main():
    for name,data in results(read(EVIDENCE/'inputs.json.gz')).items():
        assert data==read(OUT/name),name
    print('Physical diagnostics reproduced: 15 initial contact alternatives; 93 sampled penetrating pairs in rejected revision')
if __name__=='__main__':main()

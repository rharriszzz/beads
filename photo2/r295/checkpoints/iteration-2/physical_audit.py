"""Independent support-witness and dense actual-annulus penetration audit.

No image observations enter this module. A positive certificate proves the filled
outer envelopes separate (floating point margin, not interval proof). Negative
sampled actual SDF proves an overlap; no negative sample is not a proof of safety.
"""
import numpy as np
from photo2.bead_placement import Rope,bead_surface_samples
from .common import *
from .geometry import Chain,AXES,R

def independent_support(n,t,r,axial):
    dot=np.sum(n*t,axis=-1);rad=np.sqrt(np.maximum(0,np.sum(n*n,axis=-1)-dot*dot));a=dot*axial
    return .656*r*rad+.14*r*np.abs(a)+r*np.sqrt((.344*rad)**2+(.56*a)**2)

def audit(p,inputs,dense=True):
    s=Chain(p,inputs);c=s.certify(iterations=200);checked=[];penetrations=[]
    # Independent surface sampler from literal rounded profile (not trace SDF).
    rope=Rope(2600,radius_convention='intended');local=(bead_surface_samples(rope,0,24 if dense else 8,96 if dense else 32)-rope.place(0)[0])[:,[1,0,2]]*s.dims
    for row in c['witnesses']:
        a,b=row['pair'];n=np.array(row['normal']);ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b]
        gap=float((s.centers[b]-s.centers[a])@n-independent_support(n,ta,s.radius,s.axial)-independent_support(n,tb,s.radius,s.axial))
        assert abs(gap-row['gap_units'])<1e-10
        checked.append(gap)
        # Audit all candidate pairs, including positive certificates, bidirectionally.
        mins=[]
        for j,k in ((a,b),(b,a)):
            xyz=s.centers[j]+sum(local[:,i,None]*s.g[key][j] for i,key in enumerate(AXES));delta=xyz-s.centers[k]
            q=np.c_[*[delta@s.g[key][k] for key in AXES]]/s.dims
            aa=np.abs(np.hypot(q[:,1],q[:,2])-.57*R)-.086*R;bb=np.abs(q[:,0])/(.7/.43)-.086*R
            distance=(np.hypot(np.maximum(aa,0),np.maximum(bb,0))+np.minimum(np.maximum(aa,bb),0)-.344*R)*min(s.dims)
            mins.append(float(distance.min()))
        if min(mins)<-.001:penetrations.append(dict(pair=[int(s.indices[a]),int(s.indices[b])],bidirectional_min_sdf=mins))
    return dict(certified=c['certified'],state='demonstrated-interpenetration' if penetrations else 'certified-nonintersection' if c['certified'] else 'unresolved',
        candidate_pairs=c['pairs'],positive_witnesses=sum(g>1e-6 for g in checked),minimum_recomputed_gap=min(checked),dense_points_per_surface=len(local),
        penetrating_pairs=len(penetrations),penetrations=penetrations,certificate=c,limits='Dense sampled nonpenetration alone is not certification; filled-envelope witness is sufficient, not necessary.')

def main():
    inputs=read(EVIDENCE/'inputs.json.gz')['r294'];screen=read(OUT/'screen.json')['candidates'];rows=[]
    # Every failed controlled screen is classified, not silently called a collision.
    for i,r in enumerate(screen):
        if not r['train']['feasible']:
            s=Chain(r['parameters'],inputs);cert=s.certify(iterations=200);pen=s.penetration(cert)
            rows.append(dict(candidate=i,family=r['family'],parameters=r['parameters'],certified=cert['certified'],unresolved_pairs=cert['unresolved_pairs'],sampled_penetrating_pairs=sum(q['penetrating'] for q in pen),witnesses=pen))
    save(OUT/'screen-contact-classification.json.gz',dict(records=rows))
    print('Classified',len(rows),'inconclusive screening results; penetrations',sum(bool(r['sampled_penetrating_pairs']) for r in rows))
if __name__=='__main__':main()

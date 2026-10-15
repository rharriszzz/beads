"""Conservative annular-volume subdivision for inconclusive filled envelopes.

The transformed implicit function is 1-Lipschitz or tighter. A positive value
larger than a box's half diagonal excludes that whole box. This can certify hollow
bodies disjoint even when filled envelopes overlap. Exhausting the node/depth
budget is unresolved, never a collision or a certificate.
"""
import numpy as np
from .geometry import AXES

def audit_pair(scene,a,b,max_depth=13,max_nodes=200000):
    frames=[np.stack([scene.g[k][j] for k in AXES]) for j in (a,b)]
    extent=np.array([.7*scene.radius*scene.axial,scene.radius,scene.radius])
    bounds=[np.abs(frame.T)@extent for frame in frames]
    lo=np.maximum(scene.centers[a]-bounds[0],scene.centers[b]-bounds[1]);hi=np.minimum(scene.centers[a]+bounds[0],scene.centers[b]+bounds[1])
    if np.any(lo>hi):return dict(state='certified-nonintersection',nodes=0,method='disjoint containing AABBs')
    center=(lo+hi)/2;half=(hi-lo)/2;centers=center[None];nodes=0
    offsets=np.array([[x,y,z] for x in (-1,1) for y in (-1,1) for z in (-1,1)])
    for depth in range(max_depth+1):
        nodes+=len(centers)
        values=np.stack([scene.local_sdf((centers-scene.centers[j])@frame.T) for j,frame in zip((a,b),frames)],axis=1)
        inside=np.all(values< -1e-7,axis=1)
        if inside.any():return dict(state='demonstrated-interpenetration',nodes=nodes,depth=depth,point=centers[np.flatnonzero(inside)[0]].tolist(),implicit_values=values[np.flatnonzero(inside)[0]].tolist())
        uncertain=~np.any(values>np.linalg.norm(half)+1e-7,axis=1);centers=centers[uncertain]
        if not len(centers):return dict(state='certified-nonintersection',nodes=nodes,depth=depth,method='Lipschitz exclusion of all overlapping annular-volume boxes, floating point with 1e-7 margin')
        if nodes+8*len(centers)>max_nodes:return dict(state='unresolved',nodes=nodes,depth=depth,remaining_boxes=len(centers))
        half=half/2;centers=(centers[:,None,:]+offsets[None,:,:]*half).reshape(-1,3)
    return dict(state='unresolved',nodes=nodes,depth=max_depth,remaining_boxes=len(centers))

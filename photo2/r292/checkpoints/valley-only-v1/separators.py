"""Follow measured dark valleys; distinguish exterior-connected and enclosed darkness.

A rotated sampling lattice supplies short normal profiles. Dynamic programming
tracks adjacent measured minima, not chords through five corridor samples. No
unsupported step is returned as a supported arc. Search geometry bounds computation
only. Peer-side constraints apply to observed exterior-connected valleys, not every
internal dark component or a global half-plane.
"""
import numpy as np
from scipy import ndimage as ndi

PARAMETERS=dict(profile_offsets=[3,5,7],normal_fraction=[.12,.88],tracking_step=2,
                maximum_tangent_extent=48,valley_ratio=.65,minimum_arc_pixels=5,
                peer_side_offsets=[0,1],external_clearance=2)

def sample(a,xy):return ndi.map_coordinates(a,[xy[...,1],xy[...,0]],order=1,mode='nearest')

def trace(m,seed,peers,initial):
    h,w=m['lum'].shape;sm=m['smooth'];out=[];enforced=np.zeros((h,w),bool)
    for p in peers:
        if not p['supported']:continue
        other=np.array(p['local_point'],float);delta=other-seed;dist=np.linalg.norm(delta);normal=delta/dist;tangent=np.array([-normal[1],normal[0]])
        u=np.arange(max(3,np.ceil(.12*dist)),min(dist-3,np.floor(.88*dist))+1)
        if len(u)<3:continue
        extent=min(48,int(np.hypot(h,w)/2));v=np.arange(-extent,extent+1);xy=np.asarray(seed)+v[:,None,None]*tangent+u[None,:,None]*normal
        inside=(xy[...,0]>=3)&(xy[...,0]<w-3)&(xy[...,1]>=3)&(xy[...,1]<h-3)
        center=sample(sm,xy);left=np.maximum.reduce([sample(sm,xy-off*normal) for off in (3,5,7)]);right=np.maximum.reduce([sample(sm,xy+off*normal) for off in (3,5,7)]);side=np.minimum(left,right)
        ratio=center/np.maximum(side,.008)
        field=np.maximum.reduce([sample(f[k],xy) for f in m['fields'] for k in ('A_dark_seam','B_multiscale','C_material')])
        valid=inside&(ratio<.65)&(side>.02)&(field>.12)
        cost=ratio+.12*(1-np.clip(field,0,1));cost=np.where(valid,cost,4.)
        anchor=np.array(p['troughs'][2]);anchor_u=np.dot(anchor-seed,normal);middle=extent
        candidates=np.flatnonzero(valid[middle]&(np.abs(u-anchor_u)<=3))
        if not len(candidates):continue
        j=int(candidates[np.argmin(cost[middle,candidates])]);indices=[(middle,j)]
        for sign in (-1,1):
            prev=np.full(len(u),np.inf);prev[j]=0.;backs=[];rows=[];best_prev=None
            for row in range(middle+sign,-1 if sign<0 else len(v),sign):
                shifts=np.arange(-2,3);matrix=np.full((5,len(u)),np.inf)
                for z,shift in enumerate(shifts):
                    src=np.arange(len(u))+shift;ok=(src>=0)&(src<len(u));matrix[z,ok]=prev[src[ok]]+.025*abs(shift)
                choice=np.argmin(matrix,axis=0);new=matrix[choice,np.arange(len(u))]+cost[row]
                if not np.isfinite(new).any():break
                k=int(np.argmin(new))
                if not valid[row,k]:break
                backs.append(np.arange(len(u))+shifts[choice]);rows.append(row);prev=new;best_prev=k
            branch=[]
            if rows:
                k=best_prev
                for row,back in zip(rows[::-1],backs[::-1]):branch.append((row,k));k=int(back[k])
                branch.reverse()
                # Do not retain a supported bridge over a locally unmeasured step.
                for row,k in branch:
                    if not valid[row,k]:break
                    indices.append((row,k))
        indices.sort();path=np.array([xy[row,k] for row,k in indices]);values=np.array([ratio[row,k] for row,k in indices])
        if len(path)<5:continue
        q=np.rint(path).astype(int);q[:,0]=np.clip(q[:,0],0,w-1);q[:,1]=np.clip(q[:,1],0,h-1)
        # A hole/shadow entirely enclosed by the current target has no affirmative
        # exterior connection. Do not promote it to an enforced bead separator.
        dark=sm<.65*min(p['reference_Y']);labels,n=ndi.label(dark,np.ones((3,3)))
        outer=~ndi.binary_dilation(initial,iterations=2);external_ids=np.unique(labels[outer&dark]);path_labels=labels[q[:,1],q[:,0]]
        external_fraction=float(np.mean(np.isin(path_labels,external_ids[external_ids>0])))
        external=external_fraction>=.6
        record=dict(feature_id=p['feature_id'],local_path=path.tolist(),normal=normal.tolist(),ratios=values.tolist(),supported=True,enforced=bool(external),external_connection_fraction=external_fraction,classification='External separator evidence' if external else 'Enclosed darkness: internal shadow/hole alternative',endings=[dict(point=path[0].tolist(),status='Unresolved beyond observed arc'),dict(point=path[-1].tolist(),status='Unresolved beyond observed arc')],interpretation='Bilateral valley + R291 coherent corridor + tracked local edges. Exterior connection supports separation but is not physical ownership truth.')
        out.append(record)
        if external:
            for offset in (0,1):
                z=np.rint(path+offset*normal).astype(int);ok=(z[:,0]>=1)&(z[:,0]<w-1)&(z[:,1]>=1)&(z[:,1]<h-1);z=z[ok];enforced[z[:,1],z[:,0]]=True
    return out,enforced

def crossing(mask,arcs):
    """Measure actual valley inclusion and foreground on both observed sides."""
    rows=[];h,w=mask.shape
    for arc in arcs:
        p=np.asarray(arc['local_path']);n=np.asarray(arc['normal']);points=[]
        for offset in (0,-2,2):
            q=np.rint(p+offset*n).astype(int);q[:,0]=np.clip(q[:,0],0,w-1);q[:,1]=np.clip(q[:,1],0,h-1);points.append(mask[q[:,1],q[:,0]])
        center,left,right=points;cross=center&left&right
        rows.append(dict(feature_id=arc['feature_id'],enforced=arc['enforced'],samples=len(p),valley_inside=int(center.sum()),straddled_samples=int(cross.sum()),peer_side_inside=int(right.sum()),target_side_inside=int(left.sum())))
    return rows

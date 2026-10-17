"""Scale-explicit numerical sensitivity, compact-field representability and camera invariants."""
from copy import deepcopy
import numpy as np
from scipy.optimize import lsq_linear
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r297.geometry import periodic_field
from photo2.r295.geometry import AXES
from .model import Chain,bump,refined_trace,subset
from .diagnose import OUT


def main():
    data=load()[0];p=read(ROOT/'photo2/r314/results/models/R306-2405.json.gz')['parameters'];s=Chain(p,data);target=np.flatnonzero((s.indices>=-20)&(s.indices<20));columns=[];arrays=[];pc=[];orient=[]
    defs=[('phase',.1),('s0',3),('translation_x',3),('translation_y',3),('minor',.2),('elevation',3),('roll',3),('axial',.1),('tilt',3),('trajectory_mix',.1),('scale',.2),('pitch',.1),('gap_steps',5),('perspective',.0001),('old_phase_cos',.15),('old_phase_sin',.15),('old_spacing_cos',.01),('old_spacing_sin',.01)]+[(f'compact_phase_{i}',.15) for i in range(3)]+[(f'compact_spacing_{i}',.005) for i in range(3)]
    def perturb(key,z):
        q=deepcopy(p)
        if key.startswith('translation_'):q['translation']=[z,0] if key.endswith('x') else [0,z]
        elif key.startswith('old_'):
            _,field,kind=key.split('_');k='local_'+field;wave=getattr(np,kind)(2*np.pi*np.arange(32)/32);q[k]=(np.array(q[k])+z*wave).tolist()
        elif key.startswith('compact_'):
            key,i=key.rsplit('_',1);q[key]=[0.,0.,0.];q[key][int(i)]=z
        else:q[key]=q.get(key,0)+z
        return q
    def vector(s):
        # Position and axes in pixel-equivalent units; dimensions included explicitly.
        return np.r_[s.pc[target].ravel(),(s.centers[target]*s.scale).ravel(),*[s.g[k][target].ravel()*s.radius*s.scale for k in AXES],s.dims*s.scale]
    for key,step in defs:
        lo=perturb(key,-step);hi=perturb(key,step)
        if key=='perspective':lo=deepcopy(p);step=.00005;hi=perturb(key,2*step)
        try:
            a,b=Chain(lo,data),Chain(hi,data);v=(vector(b)-vector(a))/2;arrays.append(v);pc.append((b.pc[target]-a.pc[target])/2);orient.append((b.g[AXES[0]][target]-a.g[AXES[0]][target])/2);columns.append(dict(name=key,half_step=step,projected_rms_px=float(np.sqrt(np.mean(np.sum(pc[-1]**2,axis=1)))),orientation_rms_rad=float(np.sqrt(np.mean(np.sum(orient[-1]**2,axis=1)))),state_norm=float(np.linalg.norm(v))))
        except ValueError as ex:columns.append(dict(name=key,excluded=str(ex)))
    included=[c for c in columns if 'excluded' not in c];J=np.array(arrays).T;u,sv,vh=np.linalg.svd(J,full_matrices=False);norm=np.linalg.norm(J,axis=0);jn=J/np.maximum(norm,1e-12);cor=jn.T@jn;coupled=[dict(a=included[i]['name'],b=included[j]['name'],cosine=float(cor[i,j])) for i in range(len(included)) for j in range(i+1,len(included)) if abs(cor[i,j])>.90]
    k=np.arange(-100,100);basis=np.array([periodic_field(np.eye(32)[j],k/s.n) for j in range(32)]).T;desired=.18*bump(k,0,20);fit=lsq_linear(basis,desired,bounds=(-.45,.45),tol=1e-12);res=basis@fit.x-desired
    # Verify pure camera geometry independently: ray point reprojects to its pixel.
    xy=s.pc[target];base=((xy-s.offset)/s.scale)@np.array([s.right,s.down]);ray=(s.eye-base/s.distance);ray/=np.linalg.norm(ray,axis=1)[:,None];reprojection=np.max(abs(s.project(base+5*ray)-xy));frame=np.array([s.right,s.down,s.eye]);frame_error=np.max(abs(frame@frame.T-np.eye(3)))
    z=subset(s,[int(target[20]),int(target[20])]);z.centers=np.array([s.centers[target[20]],s.centers[target[20]]+s.eye*4*s.bound]);z.indices=np.array([100,101]);z.n=2;z.distance=np.inf;z.pc=z.project(z.centers)
    from scipy.spatial import cKDTree
    z.tree=cKDTree(z.pc);q=z.project(z.centers[:1]+s.g[AXES[1]][target[20]]*.65*s.radius);hit=refined_trace(z,q);near_index=int(z.indices[hit['owner'][0]]) if hit['owner'][0]>=0 else None
    # Uniform relabeling cannot alter geometry; a physical integer shift changes placement.
    shifts=[]
    for n in range(-8,9):
        line,g,phase=s.placement(s.indices[target]+n);cent=line+s.p['minor']*g['radial'];shifts.append(dict(shift=n,projected_center_rms_px=float(np.sqrt(np.mean(np.sum((s.project(cent)-s.pc[target])**2,axis=1))))))
    np.savez_compressed(OUT/'sensitivity.npz',indices=s.indices[target],jacobian=J,projected=np.array(pc),orientation=np.array(orient),singular=sv,field_indices=k,desired=desired,old_basis_fit=basis@fit.x,compact_basis=np.array([bump(k,c,45) for c in [-35,0,35]]))
    save(OUT/'sensitivity.json',dict(columns=columns,singular_values=sv.tolist(),coupled=coupled,weak_directions=[dict(singular=float(sv[-i]),coefficients={c['name']:float(v) for c,v in zip(included,vh[-i]) if abs(v)>.15}) for i in range(1,5)],old_node_spacing=s.n/32,compact_representability=dict(amplitude=.18,halfwidth=20,old_node_bound=.45,rms_residual_rad=float(np.sqrt(np.mean(res**2))),max_residual_rad=float(abs(res).max()),max_coeff=float(abs(fit.x).max()),unconstrained_residual=float(np.linalg.norm(basis@np.linalg.lstsq(basis,desired,rcond=1e-10)[0]-desired))),camera=dict(frame_orthonormal_error=float(frame_error),frame_determinant=float(np.linalg.det(frame)),ray_reprojection_px=float(reprojection),near_fixture_owner=near_index,expected_near_owner=101,depth_convention='larger signed ray parameter is nearer the camera; physical fixture surfaces separated by four bounding radii'),integer_shifts=shifts,policy='SVD uses stated engineering step scales and pixel-equivalent state vector, not statistical information rank or confidence intervals. Uniform relabeling leaves rendering invariant; physical k shift changes both station and phase.'))
if __name__=='__main__':main()

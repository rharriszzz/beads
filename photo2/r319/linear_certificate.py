"""Supporting-hyperplane LP lower bounds for the measured convex local minimax.

These certify only the affine prediction in the stated numerical trust box,
never physical-model infeasibility or a nonlinear local optimum.
"""
import numpy as np
from scipy.optimize import linprog
from .common import *

def main():
    rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];out=[]
    for stem in ['full-minimax','wide-secant-minimax','geometry-constrained-minimax','small-constrained-minimax','narrow-patch-minimax','half-grid-minimax']:
        d=read(OUT/(stem+'.json.gz'));base=rows[d['parent']];J=np.array(d['jacobian']);e=positions(base)-np.array([r['observed'] for r in base['rows']]);sel=d.get('cohort',list(range(22)));vs=d['variables'];n=len(vs)
        for step in d['steps']:
            x=np.array(step['scaled_step'][:-1]);y=e+np.einsum('ijk,k->ij',J,x);u=y[sel]/np.linalg.norm(y[sel],axis=1)[:,None];D=np.einsum('ij,ijk->ik',u,J[sel]);a=np.sum(u*e[sel],axis=1);bounds=[]
            for v in vs:
                lo=-step['trust'];k=v['key']
                if isinstance(k,str) and k in ['perspective','light_inverse','light_width']:lo=max(lo,-base['parameters'].get(k,0)/v['scale'])
                bounds.append((lo,step['trust']))
            A=np.c_[D,-np.ones(len(sel))];b=-a
            sol=linprog(np.r_[np.zeros(n),1.],A_ub=A,b_ub=b,bounds=bounds+[(0,None)],method='highs')
            if not sol.success:raise RuntimeError(sol.message)
            # A dual lower bound independently recomputed from multipliers.
            lower=np.array([b[0] for b in bounds]+[0]);upper=np.array([b[1] for b in bounds]+[0]);dual=float(sol.ineqlin.marginals@b+sol.lower.marginals@lower+sol.upper.marginals@upper)
            assert abs(dual-sol.fun)<1e-7
            weights=-sol.ineqlin.marginals;active=[dict(index=base['rows'][sel[i]]['index'],observation=base['rows'][sel[i]]['id'],weight=float(w)) for i,w in enumerate(weights) if w>1e-6]
            limits=[dict(variable=v['key'],lower_multiplier=float(sol.lower.marginals[i]),upper_multiplier=float(sol.upper.marginals[i])) for i,v in enumerate(vs) if abs(sol.lower.marginals[i])+abs(sol.upper.marginals[i])>1e-5]
            out.append(dict(model=stem,trust=step['trust'],norm_solver_prediction=step['predicted_max'],certified_affine_lower_bound_px=float(sol.fun),dual_lower_bound_px=dual,target10_impossible_in_this_affine_box=bool(sol.fun>10+1e-7),active_reflections=active,active_parameter_bounds=limits,policy='Supporting-unit-vector inequalities lower-bound Euclidean norms. LP dual equality verified; photometric/geometric/contact constraints omitted, so this is a valid lower bound even with them. Applies only to saved measured Jacobian and trust box.'))
    save(OUT/'linear-target-certificates.json',out)
    print('CERTIFICATES',[(r['model'],r['trust'],round(r['certified_affine_lower_bound_px'],4),[(a['index'],round(a['weight'],2)) for a in r['active_reflections']]) for r in out],flush=True)
if __name__=='__main__':main()

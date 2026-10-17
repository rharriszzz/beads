"""Pure-bending identities and saved-model curvature diagnostics, never fitting."""
import numpy as np
from scipy.stats import spearmanr
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r295.geometry import AXES
from photo2.r297.geometry import reference
from .analysis import OUT,D,models,stats

def derivative(scene,k):
    p=scene.p;k=np.asarray(k,float);s=scene.station(k);u=scene.inverse((scene.a0+scene.direction*s)%scene.length);a=scene.spline(u,1);b=scene.spline(u,2);v=np.linalg.norm(a,axis=1);kappa=scene.direction*(a[:,0]*b[:,1]-a[:,1]*b[:,0])/v**3
    line,g,phase=scene.placement(k);t=g['axis_tangent'];normal=np.c_[-t[:,1],t[:,0],np.zeros(len(k))];z=np.tile([0.,0.,1.],(len(k),1));radial=np.sin(phase)[:,None]*normal+np.cos(phase)[:,None]*z;circum=np.cos(phase)[:,None]*normal-np.sin(phase)[:,None]*z
    rho=p['minor']*(1+p.get('minor_y',0)*(scene.project(line)[:,1]-1591)/1591)
    return line,g,phase,rho,kappa,t,radial,circum

def main():
    part=read(OUT/'partA-completion.json');assert part['completed_before_curvature'];allrows=[];summary=[];verification=[];scenes=[]
    for name,doc,scene,raster in models():
        if name.startswith('R297'):continue
        scenes.append((name,scene));k=scene.indices;line,g,phase,rho,kap,t,rad,circ=derivative(scene,k);h=1e-3
        l1,g1,p1,r1,_,_,rad1,_=derivative(scene,k+h);l0,g0,p0,r0,_,_,rad0,_=derivative(scene,k-h);ds=scene.station(k+h)-scene.station(k-h);phi_s=(p1-p0)/ds;rho_s=(r1-r0)/ds;analytic=(1-rho*kap*np.sin(phase))[:,None]*t+(rho*phi_s)[:,None]*circ+rho_s[:,None]*rad;numeric=((l1+r1[:,None]*rad1)-(l0+r0[:,None]*rad0))/ds[:,None]
        delta=np.linalg.norm(analytic-numeric,axis=1);frame=np.stack([g[x] for x in AXES],axis=1);orth=float(np.max(abs(frame@np.swapaxes(frame,1,2)-np.eye(3))));det=float(np.max(abs(np.linalg.det(frame)-1)))
        verify=dict(model=name,beads=len(k),maximum_center_derivative_error=float(delta.max()),p95_center_derivative_error=float(np.percentile(delta,95)),maximum_frame_orthogonality_error=orth,maximum_frame_determinant_error=det,centers_equal_saved=bool(np.allclose(scene.centers,[b['center'] for b in doc['positions']],atol=1e-9,rtol=0)),formula='dC/ds=(1-rho*kappa*sin(phi))*T+rho*phi_s*circum+rho_s*radial; R309 height law included',passed=bool(delta.max()<1e-3 and orth<1e-10 and det<1e-10));assert verify['passed'] and verify['centers_equal_saved'];verification.append(verify)
        A=read(OUT/f'{name}-partA.json.gz');origin=A['anchor']['index'];ref=reference();rows=[]
        for j,index in enumerate(k):
            xy=scene.project(line[j:j+1])[0];arc=ref.project([xy])['arc'][0];rel=(arc-read(ROOT/'photo2/r296/evidence/inputs.json.gz')['arc0'])*scene.direction;rel=float((rel+ref.length/2)%ref.length-ref.length/2)
            width=2*(rho[j]+scene.radius);R=1/abs(kap[j]) if abs(kap[j])>1e-12 else None;neighbors=[]
            for step in [1,6,7]:
                target=j+step
                if target>=scene.n:
                    if not scene.closed:continue
                    target%=scene.n
                vec=scene.centers[target]-scene.centers[j];image=scene.pc[target]-scene.pc[j];neighbors.append(dict(step=step,target=int(k[target]),vector_units=vec.tolist(),vector_px=image.tolist(),length_units=float(np.linalg.norm(vec)),length_D=float(np.linalg.norm(image)/D),tangent_component_units=float(vec@t[j]),radial_component_units=float(vec@rad[j])))
            supports=[r for r in A['supports'] if r['index']==index];rr=[r for r in A['reflections'] if r['index']==index and r['strong']]
            rows.append(dict(model=name,index=int(index),index_from_reference=int(index-origin),point=scene.pc[j].tolist(),axis_xy=xy.tolist(),photo_distance_px=rel,curvature_per_unit=float(kap[j]),turning_radius_units=float(R) if R else None,rope_width_units=float(width),radius_over_rope_width=float(R/width) if R else None,inside_signed_factor=float(rho[j]*kap[j]*np.sin(phase[j])),pure_bend_tangent_factor=float(1-rho[j]*kap[j]*np.sin(phase[j])),inside=bool(kap[j]*np.sin(phase[j])>0),foreshortening=float(np.linalg.norm(scene.project((line[j]+t[j])[None])[0]-xy)/scene.scale),neighbors=neighbors,coherence=float(np.mean([r['coherence'] for r in supports])) if supports else None,reflection=stats([r['error_px'] for r in rr]),supports=[r['id'] for r in supports]))
        allrows+=rows
        evidence_rows=[r for r in rows if r['coherence'] is not None];c=np.array([abs(r['curvature_per_unit'])*r['rope_width_units'] for r in evidence_rows]);e=np.array([1-r['coherence'] for r in evidence_rows]);quant=np.quantile(c,[0,.25,.5,.75,1]);bins=[]
        for lo,hi in zip(quant[:-1],quant[1:]):
            sel=[r for r in evidence_rows if lo<=abs(r['curvature_per_unit'])*r['rope_width_units']<=hi];bins.append(dict(curvature_width_range=[float(lo),float(hi)],n=len(sel),mean_coherence=float(np.mean([r['coherence'] for r in sel])),reflection=stats([r['error_px'] for r in A['reflections'] if r['strong'] and r['index'] in [x['index'] for x in sel]])))
        first=[]
        for sign,f in A['findings'].items():
            for what in ['first_suspected','first_demonstrated_material_inconsistency']:
                r=f[what]
                if r:
                    cr=next(q for q in rows if q['index']==r['index']);first.append(dict(direction=int(sign),kind=what,id=r['id'],index=r['index'],curvature_width=abs(cr['curvature_per_unit'])*cr['rope_width_units'],radius_over_width=cr['radius_over_rope_width'],curvature_percentile=float(np.mean(c<=abs(cr['curvature_per_unit'])*cr['rope_width_units'])*100),inside=cr['inside']))
        summary.append(dict(model=name,minimum_radius_over_width=min(r['radius_over_rope_width'] for r in rows if r['radius_over_rope_width'] is not None),minimum_pure_bend_tangent_factor=min(r['pure_bend_tangent_factor'] for r in rows),spearman_curvature_vs_ownership_error=float(spearmanr(c,e).statistic),quartiles=bins,first_failures=first,interpretation='Descriptive association, not a significance test. Conditional owners, projection, photograph quality and position confound curvature; all evidence historically exposed.'))
    # Fixed analytic circles test inner/outer compression as bend tightens. No fitted scene changes.
    circles=[];rho=4.;omega=.7;h=1e-5
    for radius in [40.,12.,6.]:
        for phi in [np.pi/2,0,-np.pi/2]:
            def c(s):
                angle=s/radius;t=np.array([np.cos(angle),np.sin(angle),0.]);n=np.array([-np.sin(angle),np.cos(angle),0.]);line=np.array([radius*np.sin(angle),radius*(1-np.cos(angle)),0.]);return line+rho*(np.sin(phi+omega*s)*n+np.cos(phi+omega*s)*np.array([0,0,1]))
            deriv=(c(h)-c(-h))/(2*h);analytic=np.array([1-rho/radius*np.sin(phi),rho*omega*np.cos(phi),-rho*omega*np.sin(phi)]);error=float(np.linalg.norm(deriv-analytic));assert error<1e-8;circles.append(dict(turning_radius=radius,minor_radius=rho,phase=phi,tangent_factor=1-rho/radius*np.sin(phi),error=error))
    a,b=scenes;u=np.linspace(0,reference().length,2049);la=np.c_[a[1].spline(u),np.zeros(len(u))];lb=np.c_[b[1].spline(u),np.zeros(len(u))];pa=a[1].project(la);pb=b[1].project(lb);dist=np.linalg.norm(pb-pa,axis=1);ta=np.gradient(pa,axis=0);tb=np.gradient(pb,axis=0);ta/=np.linalg.norm(ta,axis=1)[:,None];tb/=np.linalg.norm(tb,axis=1)[:,None];angle=np.degrees(np.arccos(np.clip(np.sum(ta*tb,axis=1),-1,1)))
    axis=dict(photo_parameter=u.tolist(),R306_xy=pa.tolist(),R309_xy=pb.tolist(),displacement=stats(dist.tolist()),displacement_px=dist.tolist(),tangent_difference_degrees=angle.tolist(),maximum_tangent_difference_degrees=float(angle.max()),policy='Model-to-model axis difference, not photographic error or physical truth.')
    result=dict(started_after_partA=part['utc'],completed_utc=utc(),summary=summary,positions=allrows,verification=verification,circle_tests=circles,axis_comparison=axis,fit_evaluations=0,formula_proposed_only='If new evidence establishes curvature-dependent packing, one shared coefficient could set delta_phi(s)=a*rho*kappa(s), with periodic smooth kappa and a bounded derivative; alternatively tilt(s)=tilt0+b*rho*kappa(s). Never independent bead repairs. Neither implemented nor tested as a fit.',physical_scope='Pure bending and all-body visibility/contact already respond to curvature. Spacing/phase fields are inherited prescribed functions, not mechanical equilibrium or curvature-dependent crochet relaxation.')
    save(OUT/'curvature.json.gz',result);print(summary,verification,flush=True)
if __name__=='__main__':main()

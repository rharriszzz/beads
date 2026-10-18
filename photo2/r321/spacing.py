"""Deterministic curvature-dependent stitch density on a closed major curve.

At signed curvature kappa, the local staircase metric is
  dc/ds = (1 - R*kappa*sin(phi))*t + R*dphi/ds*circ.
Use rho(s)=1-R*abs(kappa(s)) as the worst-side first-order density factor.
Uniform index in integrated rho allocates longer advance to tighter bends.
It is a construction hypothesis, not a finite-pair separation theorem.
"""
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import cumulative_simpson

def build(scene):
    s=np.linspace(0,scene.length,16385);u=scene.inverse(s);v=scene.spline(u,1);w=scene.spline(u,2)
    k=(v[:,0]*w[:,1]-v[:,1]*w[:,0])/np.linalg.norm(v,axis=1)**3
    density=1-scene.p['minor']*abs(k)
    if density.min()<=.1:raise ValueError('Curvature tube metric outside regular construction branch')
    mass=cumulative_simpson(density,x=s,initial=0);mass_of_s=PchipInterpolator(s,mass);s_of_mass=PchipInterpolator(mass,s)
    return mass_of_s,s_of_mass,float(mass[-1]),dict(minimum_density=float(density.min()),mean_density=float(mass[-1]/scene.length),maximum_density=float(density.max()))

def station(scene,k):
    if not hasattr(scene,'_density_map'):scene._density_map=build(scene)
    forward,inverse,total,summary=scene._density_map;k=np.asarray(k,float)
    # Bead0 stays at a0 + direction*s0; signed index winds exactly once.
    origin=(scene.a0+scene.direction*scene.p['s0']/scene.scale)%scene.length
    target=float(forward(origin))+scene.direction*k*total/scene.n
    cycles=np.floor(target/total);position=inverse(target-cycles*total)+cycles*scene.length
    return scene.p['s0']/scene.scale+scene.direction*(position-origin)

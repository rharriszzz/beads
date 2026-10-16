"""One S1 registration, a deterministic curve splice, then arclength transport."""
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r303.core import Scene, ROOT, read, NAMES
from photo2.r301.model import AXES, unit
from photo2.r293.geometry import Reference

BASE=ROOT/'photo2/r304'
REVIEW=ROOT/'photo2/review/r304'
FIRST,LAST=-20,329
FAMILIES={'primary':'joint-independent-h1-S1','hand-minus':'joint-independent-h-1-S1','calibrated':'joint-calibrated-h1-S1'}

def source(name):
    row=next(r for r in read(ROOT/'photo2/r303/results/fit-freeze.json')['selected'] if r['name']==FAMILIES[name])
    section=next(s for s in read(ROOT/'photo2/r303/evidence/sections.json.gz') if s['id']=='S1')
    return row,section

class Extended(Scene):
    def __init__(self,name='primary',guards=64):
        r,s=source(name);super().__init__(r['parameters'],s,r['hand'],r['mode'],guards=64)
        self.name=name;self.source=r;self.section=s
        ref=Reference();self.ref=ref
        matrix=np.array([self.right[:2],self.down[:2]])
        # Arc zero is the photographic projection of the fitted S1 axis origin.
        a0=float(ref.project([self.offset])['arc'][0]);self.photo_origin=a0
        world=np.linalg.solve(matrix,((ref.points-self.offset)/self.scale).T).T
        wa=np.r_[0,np.cumsum(np.linalg.norm(np.diff(world,axis=0),axis=1))]
        origin=float(np.interp(a0,ref.arc,wa));reference=CubicSpline(wa-origin,world)
        # Preserve the actual local circular axis for |s|<=4 radii, then use a
        # fixed quintic splice to the unmodified image curve by |s|=12 radii.
        # This is a construction rule, not a fit to any new photographic feature.
        u=np.arange(-80.,140.0001,.01)
        zero=int(np.flatnonzero(self.indices==0)[0]);z=np.array([0.,0.,1.])
        t=np.array(s['tangent']);angle=np.radians(self.p['angle'])
        t=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])@t
        tangent0=unit(np.r_[np.linalg.solve(matrix,t),0]);normal0=np.cross(z,tangent0)
        theta=self.p['curve']*u
        local=(u*np.sinc(theta/np.pi))[:,None]*tangent0[:2]+(.5*self.p['curve']*u*u*np.sinc(theta/(2*np.pi))**2)[:,None]*normal0[:2]
        q=np.clip((abs(u)-4)/8,0,1);blend=q**3*(10-15*q+6*q*q)
        curve=(1-blend[:,None])*local+blend[:,None]*reference(u)
        true_arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];true_arc-=np.interp(0,u,true_arc)
        spline=CubicSpline(true_arc,curve)
        self.indices=np.arange(FIRST-guards,LAST+guards+1);self.n=len(self.indices);k=self.indices.astype(float);p=self.p
        self.arc=p['pitch']*(k+p['spacing']*14*(np.logaddexp(k/14,-k/14)-np.log(2)))
        self.advance=p['pitch']*(1+p['spacing']*np.tanh(k/14))
        assert self.arc.min()>true_arc[0] and self.arc.max()<true_arc[-1]
        self.line=np.c_[spline(self.arc),np.zeros(self.n)]
        tangent=np.c_[unit(spline(self.arc,1)),np.zeros(self.n)];normal=np.cross(z,tangent)
        self.phase=p['phase']+self.hand*2*np.pi*k/p['turn']
        radial=np.sin(self.phase)[:,None]*normal+np.cos(self.phase)[:,None]*z
        circum=np.cos(self.phase)[:,None]*normal-np.sin(self.phase)[:,None]*z
        tilt=np.radians(p['tilt']);axis=np.cos(tilt)*tangent+np.sin(tilt)*circum
        other=unit(np.cross(radial,axis));third=np.cross(axis,other)
        self.g=dict(zip(AXES,(axis,other,third)),radial=radial)
        self.centers=self.line+p['minor']*radial;self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
        self.axis_xy=self.project(self.line);self.photo_arc=ref.project(self.axis_xy)['arc']-a0
        self.axis_tangent=unit(np.c_[tangent@self.right,tangent@self.down])
        self.axis_departure=ref.project(self.axis_xy)['signed']
        original=Scene(r['parameters'],s,r['hand'],r['mode'])
        overlap=np.arange(-16,17);a=np.searchsorted(self.indices,overlap);b=np.searchsorted(original.indices,overlap)
        self.registration=dict(source=r['name'],axis_origin_xy=self.offset.tolist(),reference_arc_origin=a0,
            preserved_circle_half_length_units=4.,splice_end_units=12.,phase_at_zero=p['phase'],
            maximum_S1_center_change_px=float(np.linalg.norm(self.pc[a]-original.pc[b],axis=1).max()),
            maximum_S1_world_center_change=float(np.linalg.norm(self.centers[a]-original.centers[b],axis=1).max()),
            method='R293/R282 saved photographic curve, planar deprojection with fixed R303 camera; exact local circle within 4 radius units, quintic blend to image curve at 12; true arclength resampling, one origin and phase. No additional registrations.')

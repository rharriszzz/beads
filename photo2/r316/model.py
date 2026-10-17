"""One shared rigid profile; compact, coherent orientation correction across turns."""
import numpy as np
from photo2.r315.model import Chain as Previous,bump
from photo2.r295.geometry import AXES

class Chain(Previous):
    def placement(self,k):
        line,g,phase=super().placement(k)
        a=sum(v*bump(k,c,self.p.get('orientation_halfwidth',18)) for c,v in zip(self.p.get('compact_centers',[-13,0,13]),self.p.get('compact_tilt',[0,0,0])))
        if np.max(np.abs(a))>20:raise ValueError('coherent orientation exceeds exploratory 20 degrees')
        if np.any(a):
            a=np.radians(a)[:,None];axis=g['radial'];co=np.cos(a);si=np.sin(a)
            for key in AXES:
                v=g[key];g[key]=co*v+si*np.cross(axis,v)+(1-co)*np.sum(axis*v,axis=1)[:,None]*axis
        return line,g,phase

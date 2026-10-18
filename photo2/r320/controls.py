"""Packing diagnosis and explicit winding-boundary controls; no new photo fit."""
from copy import copy
import numpy as np
from photo2.r297.common import ROOT,save
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES
from photo2.r314.geometry import contacts
from .model import parameters,Chain,derive
OUT=ROOT/'photo2/r320/results'
def straight(parent,rise_ratio,factor=1.):
 s=copy(parent);p=parent.p;H=1.4*s.radius*s.axial;P=H*rise_ratio;T=p['count']/p['winding'];R=s.radius/np.sin(np.pi/T)*factor
 k=np.arange(-20,21);phi=p['phase']+p['hand']*2*np.pi*k/T;s.n=len(k);s.indices=k
 t=np.tile([1.,0,0],(s.n,1));rad=np.c_[np.zeros(s.n),np.sin(phi),np.cos(phi)];circ=np.c_[np.zeros(s.n),np.cos(phi),-np.sin(phi)]
 alpha=-p['hand']*np.arctan(P/(2*np.pi*R));body=np.cos(alpha)*t+np.sin(alpha)*circ;other=np.cross(rad,body)
 s.centers=k[:,None]*P/T*t+R*rad;s.g=dict(zip(AXES,[body,other,np.cross(body,other)]),radial=rad,axis_tangent=t)
 return s

def main():
 data=load()[0];rows=[]
 for a in [.65,.85,1.05,1.25]:
  parent=Chain(parameters(2405,1.8,a),data)
  for ratio in [.95,1.,1.05,1.1,1.15,1.2,1.3]:
   for factor in [1.,1/.96]:
    s=straight(parent,ratio,factor);c=contacts(s,seconds=.2);c.pop('witnesses',None)
    rows.append(dict(axial=a,radius=1.8,rise_ratio=ratio,minor_factor=factor,contact=c))
 controls=[]
 for n in [2401,2402]:
  for r,a in [(1.35,1.25),(1.65,1.05),(1.95,.85)]:
   s,z=derive(parameters(n,r,a),data);controls.append(dict(parameters=s.p,packing=z))
 save(OUT/'packing-controls.json',dict(straight_controls=rows,winding_controls=controls,interpretation='Straight 41-body toys isolate local packing from major curvature; they are not closed bracelets or photographic fits. Every pair in their finite scene is checked. Closed winding controls preserve bead0 station/phase at the integer transition369->370.'))
 print('CONTROLS',len(rows),len(controls),flush=True)
if __name__=='__main__':main()

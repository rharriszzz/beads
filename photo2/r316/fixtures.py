"""Adversarial owner checks including a genuine regional depth-order cycle."""
import time
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES,Chain as Python
from photo2.r279.geometry import R
from photo2.r315.model import refined_trace,subset
from .model import Chain
from .renderer import Hybrid,RayLayers,plane_orders,sandwich
OUT=ROOT/'photo2/r316/results'


def arrange(s,centers,axes,radius=None,axial=None):
    s=subset(s,np.arange(len(centers)));s.indices=np.arange(len(centers));s.centers=np.asarray(centers,float);t=np.asarray(axes,float);t/=np.linalg.norm(t,axis=1)[:,None]
    v=np.cross(t,np.tile(s.right,(s.n,1)));bad=np.linalg.norm(v,axis=1)<.01;v[bad]=np.cross(t[bad],s.down);v/=np.linalg.norm(v,axis=1)[:,None];s.g.update(zip(AXES,[t,v,np.cross(t,v)]))
    if radius is not None:s.radius=radius
    if axial is not None:s.axial=axial
    s.dims=np.array([s.axial,1,1])*s.radius/R;s.bound=s.radius*np.sqrt(1+(.7*s.axial)**2);s.query_radius=s.bound*s.scale;s.pc=s.project(s.centers);s.tree=cKDTree(s.pc);return s


def main():
    p=read(ROOT/'photo2/r315/results/baseline-model.json.gz')['parameters'];p=deepcopy(p);p.update(perspective=0,exterior=True,edge=.344,face=.8);s=Chain(p,load()[0]);scenes=[]
    for n,t in [('face-hole',s.eye),('edge-on',s.right),('oblique',s.eye+s.right+.3*s.down)]:scenes.append((n,arrange(s,[[0,0,0]],[t])))
    scenes.append(('near-tangent',arrange(s,[np.zeros(3),s.right*(2*s.radius+1e-4)],[s.eye,s.eye])))
    scenes.append(('close-depth-contact',arrange(s,[np.zeros(3),s.eye*(1.4*s.radius*s.axial+1e-4)],[s.eye,s.eye])))
    # Three slender rigid bodies traverse a triangle, low at start/high at end.
    # At the three distinct overlaps 0>1, 1>2, 2>0. No global order exists.
    verts=np.array([[-3.,-2.],[3.,-2.],[0.,3.2]]);centers=[];axes=[];lens=[]
    for i in range(3):
        a=verts[i]@np.array([s.right,s.down])-1.6*s.eye;b=verts[(i+1)%3]@np.array([s.right,s.down])+1.6*s.eye
        centers.append((a+b)/2);axes.append(b-a);lens.append(np.linalg.norm(b-a))
    cyc=arrange(s,centers,axes,radius=.23,axial=max(lens)*1.28/(1.4*.23));cyc.face=.2;cyc.edge=.3;scenes.append(('regional-cycle',cyc))
    rows=[]
    for name,z in scenes:
        lo=np.floor(z.pc.min(0)-z.query_radius-2).astype(int);hi=np.ceil(z.pc.max(0)+z.query_radius+2).astype(int);yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.c_[xx.ravel(),yy.ravel()];oracle=refined_trace(z,xy);h=Hybrid();hy=h.trace(z,xy);ly=RayLayers().trace(z,xy);parts=[Python.trace(z,xy[i:i+3000]) for i in range(0,len(xy),3000)];py={k:np.concatenate([t[k] for t in parts]) for k in ['owner','unknown']};known=~py['unknown'];orders,proofs,_,_=plane_orders(z,np.arange(z.n))
        # Deliberately wrong global order control, using isolated masks only.
        wrong=np.full(len(xy),-1,int)
        for j in np.argsort(z.centers@z.eye):
            for jj,ix,mask,dep,un in ly['layers']:
                if jj==j:wrong[ix[mask]]=j
        directed=[(int(a),int(b)) for a,b in orders];cycle=all(x in directed for x in [(0,1),(1,2),(2,0)]) or all(x in directed for x in [(1,0),(2,1),(0,2)])
        row=dict(name=name,pixels=len(xy),hybrid_disagreements=int(np.sum(hy['owner']!=oracle['owner'])),layer_disagreements=int(np.sum(ly['owner']!=oracle['owner'])),python_known_disagreements=int(np.sum(py['owner'][known]!=oracle['owner'][known])),python_unknown=int(py['unknown'].sum()),oracle_unknown=int(oracle['unknown'].sum()),center_sort_disagreements=int(np.sum(wrong!=oracle['owner'])),cycle=cycle,orders=proofs,hybrid=hy['stats']);rows.append(row);np.savez_compressed(OUT/f'fixture-{name}.npz',xy=xy,oracle=oracle['owner'],hybrid=hy['owner'],layers=ly['owner'],center_sort=wrong,centers=z.centers,frames=np.stack([z.g[k] for k in AXES]),radius=z.radius,axial=z.axial,edge=z.edge,face=z.face);print(row,flush=True)
    save(OUT/'fixtures.json',dict(cases=rows,passed=all(r['hybrid_disagreements']==r['layer_disagreements']==r['python_known_disagreements']==r['oracle_unknown']==0 for r in rows),cycle_demonstrated=any(r['cycle'] and r['center_sort_disagreements'] for r in rows)))
if __name__=='__main__':main()

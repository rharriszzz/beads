"""Rounded hollow annuli, planar smooth axis, orthographic/pinhole first hits.

Dimension changes are affine transforms of the literal R279 implicit annulus.
The SDF step is scaled by the smallest singular value, a conservative distance
bound. No spheres replace bead surfaces; spheres only accelerate ray queries.
"""
from copy import deepcopy
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r279.geometry import R, PITCH, SURFACE, sdf
from photo2.r282.geometry import Scene, unit
from photo2.r293.geometry import Reference
from photo2.r280.contact import support as original_support
from .common import *
AXES=('surface_tangent','surface_normal','surface_binormal')
KNOTS=np.array([-30.,30.,90.,150.,210.])

def extend(p):
    p=deepcopy(p)
    for k,v in dict(radius=R,axial=1.,turn=6.5,minor=4.,yaw=0.,perspective=0.,phase_knots=[0.]*5).items():p.setdefault(k,v)
    return p

class Chain(Scene):
    def __init__(self,p,inputs,indices=None):
        p=self.p=extend(p);self.indices=np.arange(-45,251) if indices is None else np.asarray(indices)
        self.n=len(self.indices);self.radius=p['radius'];self.axial=p['axial']
        self.dims=np.array([self.axial,1.,1.])*self.radius/R
        self.bound=self.radius*np.sqrt(1+(.7*self.axial)**2);self.scale=p['scale']
        e,y=np.radians([p['elevation'],p['yaw']]);self.right=np.array([np.cos(y),np.sin(y),0.])
        self.down=np.array([-np.sin(y)*np.sin(e),np.cos(y)*np.sin(e),-np.cos(e)])
        self.eye=np.cross(self.right,self.down);self.distance=1/p['perspective'] if p['perspective'] else np.inf
        self.offset=np.array(inputs['anchor']['measured_photo_location'])
        ref=Reference();anchor_ref=np.array([np.interp(inputs['arc0'],ref.arc,ref.points[:,j]) for j in range(2)])
        image=(ref.points-anchor_ref)/self.scale
        base=image@np.array([self.right,self.down])
        if np.isfinite(self.distance):
            t=self.distance*self.eye[2]/(self.distance*self.eye[2]-base[:,2]);plane=(t[:,None]*base+(1-t[:,None])*self.distance*self.eye)[:,:2]*self.scale
        else:
            plane=(base-base[:,2,None]/self.eye[2]*self.eye)[:,:2]*self.scale
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
        a0=np.interp(inputs['arc0'],ref.arc,arc);spline=CubicSpline(arc,plane)
        origin=np.array([np.interp(a0,arc,plane[:,j]) for j in range(2)])
        k=self.indices.astype(float);fine=np.arange(-65.,276.,.25)
        rate=np.exp(np.interp(fine,KNOTS,p['strain']));integ=np.r_[0,np.cumsum((rate[1:]+rate[:-1])*.125)];integ-=np.interp(0.,fine,integ)
        station=p['s0']+PITCH*p['pitch']*self.scale*np.interp(k,fine,integ)
        aa=a0+inputs['direction']*station;xy=spline(aa);tt=unit(spline(aa,1))*inputs['direction']
        normal=np.c_[-tt[:,1],tt[:,0],np.zeros(self.n)];xy+=np.interp(k,KNOTS,p['bend'])[:,None]*normal[:,:2]
        if np.any(p['bend']):tt=unit(np.gradient(xy,axis=0))
        tangent=np.c_[tt,np.zeros(self.n)];normal=np.c_[-tt[:,1],tt[:,0],np.zeros(self.n)];z=np.tile([0.,0.,1.],(self.n,1))
        phase=p['phase']+p['hand']*2*np.pi*k/p['turn']+np.interp(k,KNOTS,p['phase_knots'])
        radial=np.sin(phase)[:,None]*normal+np.cos(phase)[:,None]*z
        self.line=np.c_[(xy-origin)/self.scale,np.zeros(self.n)];self.centers=self.line+p['minor']*radial
        self.g=dict(zip(AXES,(tangent,normal,z)),radial=radial);self.pc=self.project(self.centers);self.tree=cKDTree(self.pc);self.station_px=station
        self.query_radius=self.bound*self.scale
        if np.isfinite(self.distance):
            depth=self.centers@self.eye
            self.query_radius*=np.max((1+np.linalg.norm(self.centers,axis=1)/self.distance)/(1-(depth+self.bound)/self.distance)**2)

    def project(self,xyz):
        xyz=np.asarray(xyz);xy=np.c_[xyz@self.right,xyz@self.down]*self.scale
        if np.isfinite(self.distance):xy/=1-(xyz@self.eye)[:,None]/self.distance
        return xy+self.offset

    def local_sdf(self,q):return sdf(np.asarray(q)/self.dims)*min(self.dims)

    def surface_points(self):
        return self.centers[:,None,:]+sum((SURFACE*self.dims)[None,:,j,None]*self.g[key][:,None,:] for j,key in enumerate(AXES))

    def trace(self,xy,normals=False):
        xy=np.asarray(xy,float).reshape(-1,2)
        if len(xy)>4000:
            chunks=[self.trace(xy[i:i+4000],normals) for i in range(0,len(xy),4000)]
            out={k:np.concatenate([r[k] for r in chunks]) for k in ('owner','unknown','points','normal')};out['isolated_counts']=sum(r['isolated_counts'] for r in chunks);return out
        base=((xy-self.offset)/self.scale)@np.array([self.right,self.down])
        ray=unit(self.eye-base/self.distance) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1))
        near=self.tree.query_ball_point(xy,self.query_radius+1e-4)
        a=np.repeat(np.arange(len(xy)),[len(k) for k in near]);k=np.array([j for z in near for j in z],int)
        best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),bool);counts=np.zeros(self.n,int)
        if len(a):
            delta=base[a]-self.centers[k];mid=-(delta*ray[a]).sum(1);perp=(delta*delta).sum(1)-mid*mid;keep=perp<self.bound**2
            a,k,delta,mid,perp=[v[keep] for v in (a,k,delta,mid,perp)]
            axes=[self.g[key][k] for key in AXES];q=np.stack([(delta*v).sum(1) for v in axes],axis=1);v=np.stack([(z*ray[a]).sum(1) for z in axes],axis=1)
            half=np.sqrt(np.maximum(self.bound**2-perp,0));depth=mid+half;end=mid-half;active=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
            for _ in range(450):
                ix=np.flatnonzero(active)
                if not len(ix):break
                distance=self.local_sdf(q[ix]+depth[ix,None]*v[ix]);yes=distance<1e-5;hit[ix[yes]]=True;active[ix[yes]]=False;j=ix[~yes]
                depth[j]-=np.maximum(distance[~yes],1e-5);active[j[depth[j]<end[j]]]=False
            np.maximum.at(best,a[hit],depth[hit]);front=hit&(depth>=best[a]-1e-6);owner[a[front]]=k[front];unknown[a[active]]=True;owner[unknown]=-1;counts=np.bincount(k[hit],minlength=self.n)
        points=base+np.where(np.isfinite(best),best,0)[:,None]*ray;n=np.zeros_like(points)
        if normals:
            ok=owner>=0;k=owner[ok];delta=points[ok]-self.centers[k];axes=[self.g[key][k] for key in AXES];q=np.stack([(delta*v).sum(1) for v in axes],axis=1)
            gradient=np.stack([(self.local_sdf(q+np.eye(3)[j]*1e-4)-self.local_sdf(q-np.eye(3)[j]*1e-4))/2e-4 for j in range(3)],axis=1)
            n[ok]=unit(sum(gradient[:,j,None]*axes[j] for j in range(3)))
        return dict(owner=owner,unknown=unknown,points=points,normal=n,isolated_counts=counts)

    def support(self,n,t,gradient=False):
        transformed=n+(self.axial-1)*np.sum(n*t,axis=-1)[...,None]*t
        result=original_support(transformed,t,self.radius,gradient)
        if not gradient:return result
        h,g=result;return h,g+(self.axial-1)*np.sum(g*t,axis=-1)[...,None]*t

    def certify(self,iterations=100,witnesses=True):
        pairs=cKDTree(self.centers).query_pairs(2*self.bound+1e-8,output_type='ndarray')
        if not len(pairs):return dict(certified=True,pairs=0,witnesses=[],minimum_gap_units=None,unresolved_pairs=0)
        a,b=pairs.T;delta=self.centers[b]-self.centers[a];ta=self.g[AXES[0]][a];tb=self.g[AXES[0]][b];n=unit(delta);step=np.full(len(n),.25)
        for _ in range(iterations):
            ha,ga=self.support(n,ta,True);hb,gb=self.support(n,tb,True);gap=np.sum(delta*n,axis=1)-ha-hb;grad=delta-ga-gb;grad-=np.sum(grad*n,axis=1)[:,None]*n
            candidate=unit(n+step[:,None]*grad);nextgap=np.sum(delta*candidate,axis=1)-self.support(candidate,ta)-self.support(candidate,tb);good=nextgap>gap;n[good]=candidate[good];step[~good]*=.5;step[good]=np.minimum(.5,step[good]*1.1)
        gap=np.sum(delta*n,axis=1)-self.support(n,ta)-self.support(n,tb);ok=gap>1e-6
        out=dict(certified=bool(ok.all()),pairs=len(pairs),separated_pairs=int(ok.sum()),unresolved_pairs=int((~ok).sum()),minimum_gap_units=float(gap.min()),method='R280 analytic filled-envelope support, affinely transformed for axial thickness. Inconclusive is not collision.')
        if witnesses:out['witnesses']=[dict(pair=[int(x) for x in p],normal=v.tolist(),gap_units=float(g),separated=bool(k)) for p,v,g,k in zip(pairs,n,gap,ok)]
        return out

    def penetration(self,cert=None):
        cert=cert or self.certify();surface=self.surface_points();out=[]
        for row in cert['witnesses']:
            if row['separated']:continue
            a,b=row['pair'];minimum=0.
            for j,k in ((a,b),(b,a)):
                delta=surface[j]-self.centers[k];q=np.c_[*[delta@self.g[key][k] for key in AXES]];minimum=min(minimum,float(self.local_sdf(q).min()))
            out.append(dict(pair=[int(self.indices[a]),int(self.indices[b])],sampled_min_sdf=minimum,penetrating=minimum<-.001))
        return out

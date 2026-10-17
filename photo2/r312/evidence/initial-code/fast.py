"""Conservative accelerations of existing annuli; unchanged ray tolerances."""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r309.geometry import Chain as Previous
from photo2.r307.fast import kernel
from photo2.r295.geometry import AXES, unit


class Chain(Previous):
    def certify(self, iterations=100, witnesses=True):
        # A positive separating plane is already a complete certificate. Stop
        # refining that pair; no approximate distance or collision decision.
        pairs=cKDTree(self.centers).query_pairs(2*self.bound+1e-8,output_type='ndarray')
        if not len(pairs):
            return dict(certified=True,pairs=0,witnesses=[],minimum_gap_units=None,unresolved_pairs=0)
        a,b=pairs.T;delta=self.centers[b]-self.centers[a]
        ta=self.g[AXES[0]][a];tb=self.g[AXES[0]][b];normal=unit(delta)
        step=np.full(len(a),.25);gap=np.full(len(a),-np.inf)
        for _ in range(iterations):
            ix=np.flatnonzero(gap<=1e-6)
            if not len(ix):break
            n=normal[ix];ha,ga=self.support(n,ta[ix],True);hb,gb=self.support(n,tb[ix],True)
            g=np.sum(delta[ix]*n,axis=1)-ha-hb;gap[ix]=g
            active=g<=1e-6;ix=ix[active]
            if not len(ix):continue
            n=n[active];grad=(delta[ix]-ga[active]-gb[active]);grad-=np.sum(grad*n,axis=1)[:,None]*n
            candidate=unit(n+step[ix,None]*grad)
            new=np.sum(delta[ix]*candidate,axis=1)-self.support(candidate,ta[ix])-self.support(candidate,tb[ix])
            good=new>gap[ix];normal[ix[good]]=candidate[good];gap[ix[good]]=new[good]
            step[ix[~good]]*=.5;step[ix[good]]=np.minimum(.5,step[ix[good]]*1.1)
        ok=gap>1e-6
        out=dict(certified=bool(ok.all()),pairs=len(pairs),separated_pairs=int(ok.sum()),unresolved_pairs=int((~ok).sum()),minimum_gap_units=float(gap.min()),method='Exact analytic support; stop each pair after positive separating-plane witness')
        if witnesses:out['witnesses']=[dict(pair=p.tolist(),normal=n.tolist(),gap_units=float(g),separated=bool(z)) for p,n,g,z in zip(pairs,normal,gap,ok)]
        return out

    def blocked(self, points, direction, max_distance=np.inf):
        points=np.asarray(points);d=np.asarray(direction)
        blocked=np.zeros(len(points),bool);owner=np.full(len(points),-1,int)
        if not len(points):return blocked,owner,0
        if not hasattr(self,'_shadow_trees'):self._shadow_trees={}
        if d.ndim==1:
            key=('direction',*d)
            if key not in self._shadow_trees:
                axis=np.eye(3)[np.argmin(abs(d))];r=unit(np.cross(d,axis));s=np.cross(d,r)
                self._shadow_trees[key]=(cKDTree(np.c_[self.centers@r,self.centers@s]),r,s)
            tree,r,s=self._shadow_trees[key]
            near=tree.query_ball_point(np.c_[points@r,points@s],self.bound+1e-10)
        else:
            # All finite rays converge on one source. Query the bounding spheres'
            # angular caps on the unit sphere about that source. Chord radius
            # 2 sin(asin(bound/distance)/2) encloses each complete sphere.
            limits=np.asarray(max_distance)
            lights=points+d*limits[:,None]
            light=lights[0]
            spread=float(np.max(np.linalg.norm(lights-light,axis=1)))
            if spread>.00201:
                return super().blocked(points,d,max_distance)
            key=('finite',*np.round(light,7))
            if key not in self._shadow_trees:
                delta=self.centers-light;dist=np.linalg.norm(delta,axis=1)
                if dist.min()<=self.bound:return super().blocked(points,d,max_distance)
                self._shadow_trees[key]=(cKDTree(unit(delta)),float(dist.min()))
            tree,mindist=self._shadow_trees[key]
            radius=2*np.sin(np.arcsin(min(1.,(self.bound+spread)/mindist))/2)+1e-9
            near=tree.query_ball_point(-d,radius)
        a=np.repeat(np.arange(len(points)),[len(z) for z in near]);b=np.array([j for z in near for j in z],int)
        delta=points[a]-self.centers[b];v=d[a] if d.ndim==2 else np.broadcast_to(d,delta.shape)
        mid=-np.sum(delta*v,axis=1);perp=np.sum(delta*delta,axis=1)-mid*mid
        lim=np.asarray(max_distance)[a] if np.ndim(max_distance) else np.full(len(a),max_distance)
        keep=(perp<self.bound**2)&(mid+self.bound>0)&(mid-self.bound<lim)
        a,b,delta,v,mid,perp,lim=[z[keep] for z in (a,b,delta,v,mid,perp,lim)]
        half=np.sqrt(np.maximum(self.bound**2-perp,0));begin=np.maximum(0,mid-half);end=np.minimum(lim,mid+half)
        keep=end>=begin;a,b,delta,v,begin,end=[z[keep] for z in (a,b,delta,v,begin,end)]
        if not len(a):return blocked,owner,0
        axes=[self.g[k][b] for k in AXES]
        q=np.stack([np.sum(delta*z,axis=1) for z in axes],axis=1)
        vl=np.stack([np.sum(v*z,axis=1) for z in axes],axis=1)
        depth,state=kernel(q,vl,begin,end,self.dims,1);hit=state==1;unknown=state==2
        blocked[a[hit|unknown]]=True;first=np.full(len(points),np.inf)
        np.minimum.at(first,a[hit],depth[hit]);front=hit&(depth<=first[a]+1e-6)
        owner[a[front]]=b[front];owner[a[unknown]]=-2
        return blocked,owner,int(unknown.sum())

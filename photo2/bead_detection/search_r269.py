"""Isolated bounded alternative-path search; no detector imports this module.

Search radius is Euclidean, measured from the preserved R268 endpoint. All graph
paths are native 8-neighbor paths, with both diagonal corner routes checked.
Equal/downward steps are allowed above explicit fixed raw/mean floors.
"""
from dataclasses import dataclass
import heapq
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order
from .climb_r268 import N8

@dataclass(frozen=True)
class Policy:
    raw_drop: float = 12
    mean_drop: float = 2
    color: bool = True

POLICIES = {'radius-only': Policy(256, 256, False),
            'raw12-mean2': Policy(), 'raw24-mean2': Policy(24, 2),
            'raw24-mean6': Policy(24, 6)}
REASONS = {1:'confident-background', 2:'paper-context-uncertainty',
           4:'abrupt-hue>12deg', 8:'start-relative-hue>25deg',
           16:'saturation-step>.22', 32:'raw-floor', 64:'mean-floor'}

def hue(a,b):
    return np.abs((a-b+.5)%1-.5)*360

class Neighborhood:
    def __init__(self, value, hsv, paper, sums, side, anchor, reference_raw=None, max_radius=16):
        self.side=side; self.anchor=tuple(anchor); self.max_radius=max_radius
        x,y=anchor; h,w=value.shape
        self.x0=max(0,x-max_radius); self.y0=max(0,y-max_radius)
        self.x1=min(w,x+max_radius+1); self.y1=min(h,y+max_radius+1)
        cut=np.s_[self.y0:self.y1,self.x0:self.x1]
        self.shape=value[cut].shape; self.v=value[cut].astype(float).ravel()
        self.hs=hsv[cut].reshape(-1,3); self.paper=paper[cut].ravel()
        self.sums=sums[cut].ravel(); self.mean=self.sums/side**2
        yy,xx=np.indices(self.shape); self.xy=np.column_stack((xx.ravel()+self.x0,yy.ravel()+self.y0))
        self.dist2=((self.xy-np.array(anchor))**2).sum(axis=1)
        self.start=(y-self.y0)*self.shape[1]+x-self.x0
        self.reference_raw=float(self.v[self.start] if reference_raw is None else reference_raw)
        self.reference_mean=float(self.mean[self.start]); self.start_hsv=self.hs[self.start]
        ids=np.arange(len(self.v)).reshape(self.shape); src=[];dst=[];c1=[];c2=[]
        for dx,dy in N8:
            ys=slice(max(0,-dy),min(self.shape[0],self.shape[0]-dy))
            xs=slice(max(0,-dx),min(self.shape[1],self.shape[1]-dx))
            yd=slice(max(0,dy),min(self.shape[0],self.shape[0]+dy))
            xd=slice(max(0,dx),min(self.shape[1],self.shape[1]+dx))
            a=ids[ys,xs].ravel();b=ids[yd,xd].ravel()
            src.extend(a);dst.extend(b)
            c1.extend(ids[ys,xd].ravel() if dx and dy else a)
            c2.extend(ids[yd,xs].ravel() if dx and dy else b)
        self.a=np.array(src);self.b=np.array(dst);self.c=np.array(c1);self.d=np.array(c2)
        self.rawcap=np.minimum.reduce([self.v[z] for z in (self.a,self.b,self.c,self.d)])
        self.sumcap=np.minimum.reduce([self.sums[z] for z in (self.a,self.b,self.c,self.d)])
        self.meancap=self.sumcap/side**2
        self.colorbits=self.edge_bits(self.a,self.b)
        diagonal=(self.xy[self.a,0]!=self.xy[self.b,0]) & (self.xy[self.a,1]!=self.xy[self.b,1])
        for a,b in ((self.a,self.c),(self.c,self.b),(self.a,self.d),(self.d,self.b)):
            self.colorbits |= self.edge_bits(a,b)*diagonal
        self.validedge=np.logical_and.reduce([self.sums[z]>=0 for z in (self.a,self.b,self.c,self.d)])

    def edge_bits(self,a,b):
        q=self.hs[a];t=self.hs[b];bits=np.zeros(len(a),np.uint8)
        bits[self.paper[b]==1]|=1;bits[self.paper[b]==2]|=2
        reliable=lambda z:(z[...,1]>=.35)&(z[...,2]>=.2)&(z[...,1]*z[...,2]>=.08)
        bits[reliable(q)&reliable(t)&(hue(q[:,0],t[:,0])>12)]|=4
        bits[reliable(self.start_hsv)&reliable(t)&(hue(self.start_hsv[0],t[:,0])>25)]|=8
        bits[(np.maximum(q[:,2],t[:,2])>=.2)&(np.abs(q[:,1]-t[:,1])>.22)]|=16
        return bits

    def edge_masks(self,radius,policy):
        spatial=self.validedge.copy()
        for z in (self.a,self.b,self.c,self.d):spatial &= self.dist2[z]<=radius**2
        bits=self.colorbits.copy() if policy.color else np.zeros(len(self.a),np.uint8)
        bits[self.rawcap<self.reference_raw-policy.raw_drop]|=32
        bits[self.sumcap<self.sums[self.start]-policy.mean_drop*self.side**2]|=64
        return spatial,bits

    def search(self,radius,policy):
        spatial,bits=self.edge_masks(radius,policy);keep=spatial&(bits==0)
        start_blocked=bool(policy.color and self.paper[self.start])
        graph=csr_matrix((np.ones(int(keep.sum()),np.uint8),(self.a[keep],self.b[keep])),shape=(len(self.v),)*2)
        order,pred=breadth_first_order(graph,self.start,directed=True,return_predecessors=True)
        if start_blocked or self.sums[self.start]<0:order=np.array([self.start]);pred[:]=-9999
        reachable=np.zeros(len(self.v),bool);reachable[order]=True
        # Mean ranks the point; exact-score ties prefer least displacement, then y/x.
        end=min(order,key=lambda i:(-int(self.sums[i]),int(self.dist2[i]),int(self.xy[i,1]),int(self.xy[i,0])))
        rejected=np.flatnonzero(spatial&reachable[self.a]&~reachable[self.b]&(bits!=0))
        return dict(end=int(end),order=order,pred=pred,reachable=reachable,
                    frontier=[dict(from_xy=self.xy[self.a[i]].tolist(),to_xy=self.xy[self.b[i]].tolist(),
                                   raw_capacity=float(self.rawcap[i]),mean_capacity=float(self.meancap[i]),
                                   reasons=[s for b,s in REASONS.items() if bits[i]&b]) for i in rejected],
                    start_blocked=start_blocked)

    def widest(self,radius,policy,metric="raw"):
        """For all targets: greatest possible raw bottleneck with color/mean fixed.

        This evaluates alternative paths, independently of the shortest admissible
        route. Failure below the raw floor certifies *all* such paths fail.
        """
        spatial,bits=self.edge_masks(radius,policy)
        ignore=32 if metric=="raw" else 64
        keep=spatial&((bits&~np.uint8(ignore))==0)
        adjacency=[[] for _ in self.v]
        capacity=self.rawcap if metric=="raw" else self.meancap
        for a,b,c in zip(self.a[keep],self.b[keep],capacity[keep]):adjacency[a].append((int(b),float(c)))
        cap=np.full(len(self.v),-1.);pred=np.full(len(self.v),-9999,int)
        cap[self.start]=self.v[self.start] if metric=="raw" else self.mean[self.start];heap=[(-cap[self.start],self.start)]
        if policy.color and self.paper[self.start]:return cap,pred
        while heap:
            neg,a=heapq.heappop(heap)
            if -neg!=cap[a]:continue
            for b,c in adjacency[a]:
                trial=min(cap[a],c)
                if trial>cap[b]:cap[b]=trial;pred[b]=a;heapq.heappush(heap,(-trial,b))
        return cap,pred

    def path(self,pred,end):
        indices=[int(end)]
        while indices[-1]!=self.start:
            a=int(pred[indices[-1]])
            if a<0:return []
            indices.append(a)
            assert len(indices)<=len(self.v)
        return [dict(x=int(self.xy[i,0]),y=int(self.xy[i,1]),raw_v=int(self.v[i]),
                     mean=float(self.mean[i]),sum=int(self.sums[i]),
                     h_deg=float(self.hs[i,0]*360),s=float(self.hs[i,1])) for i in indices[::-1]]

    def index(self,xy):
        x,y=xy
        if self.x0<=x<self.x1 and self.y0<=y<self.y1:return (y-self.y0)*self.shape[1]+x-self.x0
        return None

    def audit(self,path,radius,policy):
        if not path:return 0
        assert (path[0]['x'],path[0]['y'])==self.anchor
        spatial,bits=self.edge_masks(radius,policy)
        edges={(int(a),int(b)) for a,b in zip(self.a[spatial&(bits==0)],self.b[spatial&(bits==0)])}
        for p in path:
            i=self.index((p['x'],p['y']));assert self.dist2[i]<=radius**2
            assert p['raw_v']==self.v[i] and p['sum']==self.sums[i]
        for a,b in zip(path,path[1:]):assert (self.index((a['x'],a['y'])),self.index((b['x'],b['y']))) in edges
        return len(path)-1

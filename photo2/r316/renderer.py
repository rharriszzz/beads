"""Conservative support sandwiches, local occlusion proofs, and exact fallback.

No center-depth sort. A plane separating convex envelopes proves pair order on
any common orthographic ray. Nonconvex occupancy, bore projection, and perspective
remain exact-ray work. Geometry arrays are hashed on every call: caches cannot
silently survive camera, profile, frame, translation or placement changes.
"""
import hashlib,time
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from matplotlib.path import Path
from photo2.r295.geometry import AXES
from photo2.r315.model import refined_trace,subset


def key(s,xy):
    h=hashlib.sha256()
    for a in [s.centers,s.indices,s.g[AXES[0]],s.g[AXES[1]],s.g[AXES[2]],s.right,s.down,s.eye,s.offset,s.dims,xy,
              [s.scale,s.distance,s.hole,s.rounding,s.exterior,s.edge,s.face,s.bore]]:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def sandwich(s,j,tolerance=.025):
    """Inner convex hull and outer support-line intersection. Measured Hausdorff bound.

    Exact convex geometry lies between them; outer vertices' distances to inner
    polygon bound the entire outer polygon by convexity of distance-to-convex-set.
    Tolerance is adaptive, not an assertion about a fixed angular mesh.
    """
    if np.isfinite(s.distance):raise ValueError('Perspective requires exact fallback')
    n=16
    while True:
        a=np.arange(n)*2*np.pi/n;u=np.c_[np.cos(a),np.sin(a)];w=u@np.array([s.right,s.down]);h,g=s.support(w,s.g[AXES[0]][j],True)
        inner=s.pc[j]+s.scale*(g@np.array([s.right,s.down]).T)
        rhs=s.pc[j]@u.T+s.scale*h
        outer=np.linalg.solve(np.stack([u,np.roll(u,-1,axis=0)],axis=1),np.stack([rhs,np.roll(rhs,-1)],axis=1)[...,None])[...,0]
        hull=ConvexHull(inner);inner=inner[hull.vertices];v=np.roll(inner,-1,axis=0)-inner
        d=outer[:,None,:]-inner[None,:,:];t=np.clip(np.sum(d*v,axis=-1)/np.sum(v*v,axis=-1),0,1)
        dist=np.linalg.norm(d-t[...,None]*v,axis=-1).min(axis=1);bound=float(dist.max())
        if bound<=tolerance or n>=512:break
        n*=2
    if bound>tolerance:raise ValueError('Unresolved silhouette tolerance')
    return dict(inner=inner,outer=outer,bound=bound,directions=n)


def plane_orders(s,js):
    """Spatial candidate pairs, refined separating normals, no global DAG required."""
    start=time.perf_counter();js=np.asarray(js,int);pairs=cKDTree(s.pc[js]).query_pairs(2*s.query_radius+1e-4,output_type='ndarray');pairs=js[pairs];discovery=time.perf_counter()-start
    start=time.perf_counter()
    if not len(pairs):return {},[],discovery,time.perf_counter()-start
    a,b=pairs.T;delta=s.centers[b]-s.centers[a];length=np.linalg.norm(delta,axis=1);n=delta/np.maximum(length[:,None],1e-30);n[length<1e-12]=s.right;step=np.full(len(n),.25)
    for _ in range(50):
        ha,ga=s.support(n,s.g[AXES[0]][a],True);hb,gb=s.support(-n,s.g[AXES[0]][b],True)
        gap=np.sum(delta*n,axis=1)-ha-hb;grad=delta-ga+gb;grad-=np.sum(grad*n,axis=1)[:,None]*n
        nn=n+step[:,None]*grad;nn/=np.linalg.norm(nn,axis=1)[:,None];ng=np.sum(delta*nn,axis=1)-s.support(nn,s.g[AXES[0]][a])-s.support(-nn,s.g[AXES[0]][b]);ok=ng>gap;n[ok]=nn[ok];step[~ok]*=.5;step[ok]=np.minimum(.5,step[ok]*1.1)
    gap=np.sum(delta*n,axis=1)-s.support(n,s.g[AXES[0]][a])-s.support(-n,s.g[AXES[0]][b]);cos=n@s.eye;orders={};rows=[]
    for aa,bb,gg,cc,normal in zip(a,b,gap,cos,n):
        front=None
        if gg>1e-5 and abs(cc)>1e-8 and not np.isfinite(s.distance):
            front=int(bb if cc>0 else aa);back=int(aa if cc>0 else bb);orders[front,back]=True
        rows.append(dict(pair=[int(s.indices[aa]),int(s.indices[bb])],array_pair=[int(aa),int(bb)],support_gap=float(gg),normal=normal.tolist(),eye_dot=float(cc),front=None if front is None else int(s.indices[front]),ray_depth_lower_bound=None if front is None else float(gg/abs(cc))))
    return orders,rows,discovery,time.perf_counter()-start


class Hybrid:
    def __init__(self,tolerance=.025):self.tolerance=tolerance;self.cache={};self.hits=0;self.silhouettes={}
    def trace(self,s,xy):
        xy=np.asarray(xy,float).reshape(-1,2);start=time.perf_counter();k=key(s,xy)
        if k in self.cache:
            self.hits+=1;r=self.cache[k];return dict(owner=r['owner'].copy(),unknown=r['unknown'].copy(),stats=dict(r['stats'],cache_hit=True,total_seconds=time.perf_counter()-start))
        if np.isfinite(s.distance):
            r=refined_trace(s,xy);r['stats']=dict(mode='perspective-exact-fallback',cache_hit=False,fallback_pixels=len(xy),certified_pixels=0,total_seconds=time.perf_counter()-start);self.cache={k:r};return r
        t=time.perf_counter();tree=cKDTree(xy);possible={};certain={};bounds=[];limit_fallbacks=0;shape_hits=0;raster_seconds=0.
        # Ray march hit tolerance transformed conservatively to image distance.
        f=.7*s.face/s.edge if s.exterior else 1.;guard=max(.002,4e-5*s.scale*max(s.dims)/min(s.dims)/min(1.,f))
        for j in range(s.n):
            ix=np.asarray(tree.query_ball_point(s.pc[j],s.query_radius+guard),int)
            if not len(ix):continue
            sk=tuple(np.r_[s.g[AXES[0]][j],s.right,s.down,s.dims,s.scale,s.radius,s.axial,s.hole,s.rounding,s.exterior,s.edge,s.face,self.tolerance])
            if sk in self.silhouettes:
                relative=self.silhouettes[sk];shape_hits+=1
                z=dict(relative,inner=relative['inner']+s.pc[j],outer=relative['outer']+s.pc[j]) if relative else None
            else:
                try:z=sandwich(s,j,self.tolerance)
                except ValueError:z=None
                self.silhouettes[sk]=dict(z,inner=z['inner']-s.pc[j],outer=z['outer']-s.pc[j]) if z else None
            if z is None:
                possible[j]=ix;certain[j]=np.empty(0,int);limit_fallbacks+=1;continue
            bounds.append(z['bound']);rt=time.perf_counter();p=Path(z['outer']).contains_points(xy[ix],radius=2*guard);ix=ix[p]
            if not len(ix):continue
            possible[j]=ix;inside=Path(z['inner']).contains_points(xy[ix],radius=-2*guard)
            if s.exterior:
                # Finite bore cylinder is enclosed in this projected capsule.
                axis=s.g[AXES[0]][j];end=.7*s.radius*s.axial*s.scale*(axis@np.array([s.right,s.down]).T)
                a=s.pc[j]-end;b=s.pc[j]+end;v=b-a;d=xy[ix]-a;tau=np.clip(d@v/max(v@v,1e-30),0,1);outside=np.linalg.norm(d-tau[:,None]*v,axis=1)>s.bore*s.radius*s.scale+guard
                certain[j]=ix[inside&outside]
            else:certain[j]=np.empty(0,int)
            raster_seconds+=time.perf_counter()-rt
        sil=time.perf_counter()-t;orders,rows,disc,order=plane_orders(s,list(possible));t=time.perf_counter();count=np.zeros(len(xy),int)
        for ix in possible.values():count[ix]+=1
        owner=np.full(len(xy),-1,int);resolved=count==0
        for j,ix in certain.items():
            if not len(ix):continue
            blocked=np.zeros(len(xy),bool)
            for kk,jj in [(r['array_pair'][1],r['array_pair'][0]) for r in rows if j==r['array_pair'][0]]+[(r['array_pair'][0],r['array_pair'][1]) for r in rows if j==r['array_pair'][1]]:
                if (j,kk) not in orders:blocked[possible[kk]]=True
            good=ix[~blocked[ix]];owner[good]=j;resolved[good]=True
        compose=time.perf_counter()-t;ix=np.flatnonzero(~resolved);t=time.perf_counter();unknown=np.zeros(len(xy),bool)
        if len(ix):r=refined_trace(s,xy[ix]);owner[ix]=r['owner'];unknown[ix]=r['unknown']
        fallback=time.perf_counter()-t
        stats=dict(mode='support-sandwich-hybrid',cache_hit=False,full_bodies=s.n,active_bodies=len(possible),silhouette_seconds=sil-raster_seconds,rasterization_seconds=raster_seconds,silhouette_cache_hits=shape_hits,silhouette_limit_fallbacks=limit_fallbacks,overlap_discovery_seconds=disc,ordering_seconds=order,composition_seconds=compose,fallback_seconds=fallback,fallback_pixels=len(ix),certified_pixels=int(resolved.sum()),empty_certified=int((count==0).sum()),occupied_certified=int((resolved&(owner>=0)).sum()),overlap_pixels=int((count>1).sum()),max_overlap=int(count.max(initial=0)),pair_count=len(rows),proved_pairs=len(orders),uncertain_pairs=len(rows)-len(orders),silhouette_bound_max=max(bounds,default=0),silhouette_bound_p95=float(np.percentile(bounds,95)) if bounds else 0.,guard_px=guard,total_seconds=time.perf_counter()-start)
        r=dict(owner=owner,unknown=unknown,stats=stats,orders=rows);self.cache={k:r};return r


class RayLayers:
    """Exact isolated occupied masks with depths. Independent arrays, no convex hull substitution.

    Reusable numerical layers on frozen coordinates; composition handles regional
    ordering reversals via per-pixel depth maxima. Cold construction is measured.
    """
    def __init__(self):self.cache={};self.bead_cache={}
    def trace(self,s,xy):
        start=time.perf_counter();xy=np.asarray(xy,float);k=key(s,xy);hit=k in self.cache;reused=0;rebuilt=0
        camera_key=hashlib.sha256(np.ascontiguousarray(xy).tobytes()+np.r_[s.right,s.down,s.eye,s.offset,s.dims,s.scale,s.distance,s.hole,s.rounding,s.exterior,s.edge,s.face,s.bore,s.query_radius].tobytes()).digest()
        if hit:layers=self.cache[k];generation=0.
        else:
            layers=[];tree=cKDTree(xy)
            for j in range(s.n):
                ix=np.asarray(tree.query_ball_point(s.pc[j],s.query_radius+1e-4),int)
                if len(ix):
                    bk=hashlib.sha256(camera_key+np.r_[s.centers[j],s.g[AXES[0]][j],s.g[AXES[1]][j],s.g[AXES[2]][j]].tobytes()).digest()
                    if bk in self.bead_cache:
                        oldix,mask,depth,un=self.bead_cache[bk];assert np.array_equal(ix,oldix);reused+=1
                    else:
                        tr=refined_trace(subset(s,[j]),xy[ix]);mask=tr['owner']>=0;depth=tr['depth'];un=tr['unknown'];self.bead_cache[bk]=(ix,mask,depth,un);rebuilt+=1
                    layers.append((j,ix,mask,depth,un))
            if len(self.bead_cache)>2048:self.bead_cache.clear()
            self.cache={k:layers};generation=time.perf_counter()-start
        t=time.perf_counter();dep=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),bool)
        for j,ix,mask,depth,un in layers:
            # Same tie tolerance and increasing body order as the numerical oracle.
            yes=mask&(depth>=dep[ix]-1e-6);owner[ix[yes]]=j;dep[ix[yes]]=np.maximum(dep[ix[yes]],depth[yes]);unknown[ix[un]]=True
        # Isolated unknowns do not expose remaining-depth bounds: resolve whole rays.
        if unknown.any():
            r=refined_trace(s,xy[unknown]);owner[unknown]=r['owner'];unknown[unknown]=r['unknown']
        return dict(owner=owner,unknown=unknown,depth=dep,layers=layers,stats=dict(cache_hit=hit,reused_beads=reused,rebuilt_beads=rebuilt,isolated_seconds=generation,composition_seconds=time.perf_counter()-t,total_seconds=time.perf_counter()-start,layer_count=len(layers),stored_pair_pixels=sum(len(z[1]) for z in layers),layer_array_bytes=sum(sum(a.nbytes for a in z[1:]) for z in layers),fallback_pixels=int(sum(z[4].sum() for z in layers))))

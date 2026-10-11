"""R257 local first-hit metrology on the source rounded annulus.

Coordinates are original pixel centers (integer x,y), world z is paper normal.
The compressed rounded-rectangle SDF is conservative, not Euclidean after stretch.
No sphere replaces a bead: spheres are ONLY acceleration bounds.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from .registry import load, model_version, RADIUS, ROOT, rays
from .generate import sha
from curved_surface_fit import sdf

EXTRA=.2*.43*RADIUS
ROUND=.8*.43*RADIUS
STRETCH=.7/.43
BOUND=RADIUS*np.sqrt(1+.7**2)
EPS=1e-5
VERSION='r257-surface-1'


def unit(v):
    v=np.asarray(v,float)
    return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-30)


def local_normal(p):
    """Analytic gradient: radial cylinders, axial planes, elliptical fillets/hole."""
    p=np.asarray(p);rho=np.linalg.norm(p[...,1:],axis=-1)
    qr=np.abs(rho-.57*RADIUS)-EXTRA;qa=np.abs(p[...,0])/STRETCH-EXTRA
    gr=np.maximum(qr,0);ga=np.maximum(qa,0)
    interior=(gr+ga)==0
    gr=np.where(interior&(qr>=qa),1,gr);ga=np.where(interior&(qa>qr),1,ga)
    radial=gr*np.sign(rho-.57*RADIUS)/np.maximum(rho,1e-30)
    return unit(np.stack([ga*np.sign(p[...,0])/STRETCH,radial*p[...,1],radial*p[...,2]],axis=-1))


def moments(xy,w):
    xy=np.asarray(xy);w=np.asarray(w);s=w.sum()
    if not len(xy) or s<=1e-12:return None
    c=np.sum(xy*w[:,None],axis=0)/s;q=xy-c;cov=(q*w[:,None]).T@q/s
    vals,vec=np.linalg.eigh(cov);axis=vec[:,-1]
    return dict(centroid=c.tolist(),covariance=cov.tolist(),sigma_major=float(np.sqrt(max(vals[-1],0))),
                sigma_minor=float(np.sqrt(max(vals[0],0))),orientation_deg=float(np.degrees(np.arctan2(axis[1],axis[0]))%180),weight=float(s))


class Scene:
    def __init__(self,mid):
        self.config,self.model=load(mid);self.g=self.model.geometry(np.arange(self.config['n']))
        self.mid=mid;self.version=model_version(mid)[0];self.centers=self.g['centers'];self.pc=self.model.view.project(self.centers)
        self.plane_z=-(4+RADIUS) # conservative shared support plane, source units
        self.shadow_trees={}
    def normals(self,points,owner):
        q=points-self.centers[owner];g=self.g
        local=np.c_[np.sum(q*g['tangent'][owner],axis=1),np.sum(q*g['normal'][owner],axis=1),q[:,2]]
        n=local_normal(local)
        return n[:,0,None]*g['tangent'][owner]+n[:,1,None]*g['normal'][owner]+n[:,2,None]*[0,0,1]
    def camera(self,xy):
        xy=np.asarray(xy,float);owner,depth,unknown=rays(self.model,xy,self.g)
        v=self.model.view.directions(xy);base=self.model.view.base(xy)
        points=base+np.where(np.isfinite(depth),depth,0)[:,None]*v
        normal=np.zeros_like(points);hit=(owner>=0)&(unknown==0)
        normal[hit]=self.normals(points[hit],owner[hit]);owner[unknown>0]=-1
        return dict(xy=xy,owner=owner,points=points,normal=normal,viewer=v,unknown=unknown)
    def blocked(self,points,direction,return_owner=False):
        """All-scene directional shadow rays, including self/hole occlusion.

        KD-tree is on the plane perpendicular to light; unlike image-space
        neighbors it includes distant beads capable of casting a shadow.
        Unfinished grazing rays are conservatively blocked and counted.
        """
        points=np.asarray(points);d=unit(direction);key=tuple(d)
        if key not in self.shadow_trees:
            if len(self.shadow_trees)>=64:self.shadow_trees.pop(next(iter(self.shadow_trees)))
            axis=np.eye(3)[np.argmin(np.abs(d))];r=unit(np.cross(d,axis));s=np.cross(d,r)
            self.shadow_trees[key]=(r,s,cKDTree(np.c_[self.centers@r,self.centers@s]))
        r,s,tree=self.shadow_trees[key];blocked=np.zeros(len(points),bool);owners=np.full(len(points),-1,int);unfinished=0
        for start in range(0,len(points),4000):
            p=points[start:start+4000];near=tree.query_ball_point(np.c_[p@r,p@s],BOUND)
            a=np.repeat(np.arange(len(p)),[len(x) for x in near]);b=np.array([k for x in near for k in x],int)
            if not len(a):continue
            delta=p[a]-self.centers[b];mid=-delta@d;perp=np.sum(delta**2,axis=1)-mid**2;half=np.sqrt(np.maximum(BOUND**2-perp,0))
            t=np.maximum(mid-half,0);end=mid+half;keep=end>=t
            a,b,delta,t,end=[x[keep] for x in (a,b,delta,t,end)]
            local=np.c_[np.sum(delta*self.g['tangent'][b],axis=1),np.sum(delta*self.g['normal'][b],axis=1),delta[:,2]]
            direct=np.c_[self.g['tangent'][b]@d,self.g['normal'][b]@d,np.full(len(b),d[2])]
            active=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
            for _ in range(800):
                ix=np.flatnonzero(active)
                if not len(ix):break
                dist=sdf(local[ix]+t[ix,None]*direct[ix]);yes=dist<EPS
                hit[ix[yes]]=True;active[ix[yes]]=False;move=ix[~yes]
                t[move]+=np.maximum(dist[~yes],EPS);active[move[t[move]>end[move]]]=False
            unfinished+=int(active.sum());blocked[start+a[hit|active]]=True
            front=np.full(len(p),np.inf);np.minimum.at(front,a[hit],t[hit]);first=hit&(t<=front[a]+EPS/2)
            owners[start+a[first]]=b[first];owners[start+a[active]]=-2
        return (blocked,unfinished,owners) if return_owner else (blocked,unfinished)
    def grid(self,box,step=1):
        x0,y0,x1,y1=box
        y,x=np.mgrid[int(np.ceil(y0/step))*step:y1:step,int(np.ceil(x0/step))*step:x1:step]
        return self.camera(np.c_[x.ravel(),y.ravel()])
    def box(self,indices,pad=3):
        pc=self.pc[indices];r=BOUND*self.model.view.scale+pad
        return [max(0,int(np.floor(pc[:,0].min()-r))),max(0,int(np.floor(pc[:,1].min()-r))),
                min(2540,int(np.ceil(pc[:,0].max()+r))+1),min(3182,int(np.ceil(pc[:,1].max()+r))+1)]
    def outward(self,gi):
        p=self.g['outward'][gi];xy=self.model.view.project(p[None])[0];hit=self.camera(xy[None]);dist=np.linalg.norm(hit['points'][0]-p)
        visible=hit['owner'][0]==gi and dist<.005
        return dict(xyz=p.tolist(),xy=xy.tolist(),visible=bool(visible),first_owner=int(hit['owner'][0]),front_distance_units=float(dist),
                    definition='midplane representative of outer cylindrical radial-extremum band',
                    extremum_axial_half_extent=EXTRA*STRETCH,radial_support=RADIUS)


def directions(light,order=3):
    """Uniform radiance rectangular distant source, finite angular extent.

    Directional limit is one sample. Angular size is inferred; no distance claim.
    Solid-angle quadrature includes the planar source's cos^3 Jacobian.
    """
    d=unit(light['direction']);width=light.get('width_deg',0);height=light.get('height_deg',width)
    if width==height==0:return [(d,1.)]
    r=unit(np.cross(d,np.eye(3)[np.argmin(np.abs(d))]));s=np.cross(d,r);a=np.radians(light.get('rotation_deg',0))
    r,s=np.cos(a)*r+np.sin(a)*s,-np.sin(a)*r+np.cos(a)*s
    nodes,weights=np.polynomial.legendre.leggauss(order);out=[]
    for x,wx in zip(nodes,weights):
        for y,wy in zip(nodes,weights):
            q=d+x*np.tan(np.radians(width)/2)*r+y*np.tan(np.radians(height)/2)*s
            out.append((unit(q),float(wx*wy/np.linalg.norm(q)**3)))
    total=sum(w for _,w in out);return [(d,w/total) for d,w in out]


def shade(scene,data,light,shadows=True,order=9):
    n=data['normal'];v=data['viewer'];p=data['points'];valid=data['owner']>=0
    spec=np.zeros(len(p));diff=np.zeros(len(p));shadow=np.zeros(len(p));self_shadow=np.zeros(len(p));self_cast=np.zeros(len(p));neighbor_cast=np.zeros(len(p));un=0
    alpha=np.radians(light.get('roughness_deg',6));exponent=max(1,2/max(alpha**2,1e-8)-2)
    for source in light.get('lights',[light]):
        for d,w in directions(source,order):
            weight=w*source.get('strength',1);nl=np.maximum(n@d,0);h=unit(v+d)
            # Shared Blinn half-vector lobe, relative exposure only.
            # Fresnel/masking are intentionally omitted from the position diagnostic.
            val=np.maximum(np.sum(n*h,axis=1),0)**exponent*nl
            block=np.zeros(len(p),bool)
            if shadows:
                ix=np.flatnonzero(valid&(nl>0));block[ix],uu,blocker=scene.blocked(p[ix]+n[ix]*1e-3,d,return_owner=True);un+=uu
                self_cast[ix]+=weight*(blocker==data['owner'][ix]);neighbor_cast[ix]+=weight*((blocker>=0)&(blocker!=data['owner'][ix]))
            spec+=weight*val*(~block);diff+=weight*nl*(~block)
            shadow+=weight*block;self_shadow+=weight*(nl<=0)
    spec[~valid]=0;diff[~valid]=0
    return dict(specular=spec,diffuse=diff,cast_shadow=shadow,back_facing=self_shadow,self_cast=self_cast,neighbor_cast=neighbor_cast,unfinished_shadow_pairs=un)


def highlight(xy,intensity):
    if len(intensity)==0 or intensity.max()<1e-4:return None
    peak=float(intensity.max());region=intensity>=max(.5*peak,1e-4)
    result=moments(xy[region],intensity[region]);result.update(peak_xy=xy[intensity.argmax()].tolist(),peak_intensity=peak,
                  area_px2=int(region.sum()),threshold_relative=.5,
                  region=np.c_[xy[region],intensity[region]].round(5).tolist())
    return result


def cache_key(scene,light,indices):
    payload=dict(surface=sha(Path(__file__)),geometry=scene.version,image=sha(ROOT/'beads-photo-2.jpg'),light=light,indices=list(map(int,indices)),step=1,adaptive=2)
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

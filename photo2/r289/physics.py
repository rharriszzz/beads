"""Known synthetic geometry only: analytic surface normals and shadow visibility."""
import numpy as np
from photo2.r279.geometry import R,INDICES,centers,frame,project,trace,sdf
from photo2.bead_debugger.surface import local_normal,RADIUS,unit,moments

def blocked(points,light,c):
    # SDF march toward known distant light through all 29 source annuli.
    p=points+light*.001;delta=p[:,None,:]-c[None,:,:];mid=-delta@light
    perp=(delta*delta).sum(2)-mid*mid;bound=R*np.sqrt(1+.7**2)
    a,b=np.where(perp<bound**2);half=np.sqrt(np.maximum(bound**2-perp[a,b],0));t=np.maximum(mid[a,b]-half,0);end=mid[a,b]+half
    live=end>=t;hit=np.zeros(len(a),bool)
    for _ in range(450):
        ix=np.flatnonzero(live)
        if not len(ix):break
        dist=sdf(delta[a[ix],b[ix]]+t[ix,None]*light);yes=dist<1e-5;hit[ix[yes]]=True;live[ix[yes]]=False
        mv=ix[~yes];t[mv]+=np.maximum(dist[~yes],1e-5);live[mv[t[mv]>end[mv]]]=False
    out=np.zeros(len(points),bool);out[a[hit|live]]=True
    return out,int(live.sum())

def forward(p,shape=(224,320)):
    yy,xx=np.indices(shape);xy=np.c_[xx.ravel(),yy.ravel()];owner,depth,unknown=trace(p,xy)
    r,d,e=frame(p['inclination'],p['roll']);c=centers(INDICES,p['hand'],p['phase'],p['pitch']);valid=owner!=-999
    pts=((xy[valid]-p['translation'])/p['scale'])@np.array([r,d])+depth[valid,None]*e
    local=pts-c[owner[valid]+14];n=local_normal(local*(RADIUS/R));l=unit(p['light']);h=unit(l+e)
    shadow,unfinished=blocked(pts,l,c)
    # Known half-vector alignment; maximum is independent of chosen lobe exponent.
    intensity=np.maximum(n@h,0)**(1/p['roughness']);intensity[(n@l)<=0]=0;intensity[shadow]=0
    field=np.zeros(len(xy));field[valid]=intensity
    return dict(owner=owner.reshape(shape),unknown=unknown.reshape(shape),specular=field.reshape(shape),shadow_unfinished=unfinished,centers=project(p,c))

def bright_truth(field,mask):
    y,x=np.where(mask)
    if not len(x):return None
    v=field[y,x];i=int(np.argmax(v))
    if v[i]<.01:return None
    keep=v>=.85*v[i];m=moments(np.c_[x[keep],y[keep]],v[keep])
    return dict(peak=[int(x[i]),int(y[i])],centroid=m['centroid'],maximum=float(v[i]))

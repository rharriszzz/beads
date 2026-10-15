"""Complementary A–E measurements of original photographic pixels.

Adapt R265 first-dark paths, R288 parallel separator profiles, and R290's
specular-tolerant chromatic direction. No prior masks, case IDs or judgments.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2hsv
from skimage.morphology import skeletonize
from photo2.bead_detection.brightness_r270 import linearize
from photo2.r290.detector import shifted

PARAMETERS=dict(scales=[.65,1.2,1.8],normal_offsets=[2,4],tangent_width=5,
                color_sigma_degrees=18.,diffuse_quantile=.6,illumination_fraction=.18,
                corridor_ratio=.55,corridor_offsets=[-5,-2.5,0,2.5,5],corridor_fraction=.8,
                direct_dark_ratio=.55)

def hue_distance(a,b):return np.abs((a-b+180)%360-180)

def measure(rgb,seed):
    lum=linearize(rgb.astype(float)/255.)@np.array([.2126,.7152,.0722])
    hsv=rgb2hsv(rgb/255.);hue=hsv[:,:,0]*360;sat=hsv[:,:,1];yy,xx=np.indices(lum.shape)
    ds=np.hypot(xx-seed[0],yy-seed[1]);local=(ds<=8)&(sat>.3)&(lum>.008)
    bins=np.arange(0,360,5);weights=np.exp(-ds**2/32)*sat
    scores=np.array([np.sum(weights[local]*np.exp(-.5*(hue_distance(hue[local],v)/18)**2)) for v in bins])
    material=float(bins[np.argmax(scores)]) if local.any() else None
    match=np.exp(-.5*(hue_distance(hue,material)/PARAMETERS['color_sigma_degrees'])**2) if material is not None else np.zeros_like(lum)
    pigment=(match>.6)&(sat>.3)
    samples=lum[local&(match>.6)]
    diffuse=float(np.quantile(samples,.6)) if len(samples) else float(np.median(lum[ds<=5]))
    floor=max(.004,.18*diffuse)
    reliable=np.clip((sat-.12)/.28,0,1)*np.clip(lum/.025,0,1)
    color_rgb=ndi.uniform_filter(rgb.astype(float),size=(3,3,1),mode='nearest')
    difference=color_rgb-color_rgb.min(2,keepdims=True);chroma=difference/np.maximum(difference.max(2,keepdims=True),1.)
    s=ndi.gaussian_filter(lum,.65);fields=[]
    for axis in (1,0):
        dy,dx=(0,1) if axis==1 else (1,0);tangent=0 if axis==1 else 1
        c=(s+shifted(s,dy,dx))/2
        profiles=[];darkness=[];valleys=[];steps=[]
        for off in (2,4):
            a=shifted(s,-off*dy,-off*dx);b=shifted(s,off*dy,off*dx)
            scale=np.maximum(np.maximum(a,b),.025)
            drop=np.clip((np.maximum(a,b)-c)/scale,0,1);recovery=np.clip((np.minimum(a,b)-c)/scale,0,1)
            dark=drop*np.maximum(np.clip(recovery/.25,0,1),np.clip((floor*1.5-np.minimum(a,b))/(floor*1.5),0,1))
            coherence=ndi.uniform_filter1d((dark>.2).astype(float),5,axis=tangent,mode='nearest')
            darkness.append(dark*coherence);valleys.append(recovery);steps.append(np.abs(a-b)/scale)
            profiles.append(np.stack([a,c,b]))
        A=np.maximum.reduce(darkness);recovery=np.maximum.reduce(valleys)
        # B: scale persistence and tangent tracking; no requirement of a dark floor.
        gradients=[]
        for sigma in PARAMETERS['scales']:
            sm=ndi.gaussian_filter(lum,sigma)
            a=shifted(sm,-2*dy,-2*dx);b=shifted(sm,2*dy,2*dx)
            signed=(b-a)/np.maximum(np.maximum(a,b),.025)
            gradients.append(signed)
        same_sign=(np.sign(gradients[0])==np.sign(gradients[1]))&(np.sign(gradients[0])==np.sign(gradients[2]))
        grad=np.minimum.reduce([abs(g) for g in gradients])*same_sign
        tracking=ndi.uniform_filter1d((grad>.16).astype(float),5,axis=tangent,mode='nearest')
        B=grad*tracking
        ca=shifted(chroma,-3*dy,-3*dx);cb=shifted(chroma,3*dy,3*dx)
        ra=shifted(reliable,-3*dy,-3*dx);rb=shifted(reliable,3*dy,3*dx)
        color=np.linalg.norm(ca-cb,axis=2)*np.minimum(ra,rb)
        C=np.clip(color,0,1)*ndi.uniform_filter1d((color>.16).astype(float),5,axis=tangent,mode='nearest')
        ma=shifted(match,-3*dy,-3*dx);mb=shifted(match,3*dy,3*dx)
        la=shifted(s,-3*dy,-3*dx);lb=shifted(s,3*dy,3*dx)
        # D is contradictory evidence, never a route-based cancellation of A.
        D=np.minimum(ma*ra,mb*rb)*np.clip(np.minimum(la,lb)/max(floor*2,.008),0,1)
        B_effective=B*(1-.65*D)
        fused=1-(1-np.clip(A*1.3,0,1))*(1-np.clip(B_effective,0,1))*(1-np.clip(C,0,1))
        fields.append(dict(A_dark_seam=A,B_multiscale=B,C_material=C,D_continuity=D,
                           recovery=recovery,tracking=tracking,combined=fused,
                           profile_near=profiles[0],profile_far=profiles[1]))
    ridge=np.maximum(fields[0]['A_dark_seam'],fields[1]['A_dark_seam'])
    edge=np.maximum.reduce([v[k] for v in fields for k in ('A_dark_seam','B_multiscale','C_material')])
    skeleton=skeletonize(edge>.3);degree=ndi.convolve(skeleton.astype(int),np.ones((3,3),int))-skeleton
    junction=skeleton&(degree>=3);termination=skeleton&(degree==1)
    # Edge junctions are supporting context, not proof of an occluder's identity.
    for f in fields:
        f['E_junction']=ndi.maximum_filter(junction.astype(float),5)
        f['E_termination']=ndi.maximum_filter(termination.astype(float),5)
    model=dict(material_hue_degrees=material,diffuse_Y=diffuse,floor_Y=floor,local_material_pixels=int(local.sum()),source='Target-local original pixels only; hue is not physical identity.')
    return dict(lum=lum,smooth=s,hsv=hsv,match=match,reliability=reliable,pigment=pigment,
                ridge=ridge,fields=fields,model=model)

def direct_access(m,seed):
    """Every pixel has its own native straight profile; detours cannot erase stops.

    This is source-relative evidence, not a shape constraint or final mask.
    Internal holes/shadows can interrupt it, so a separate alternative softens it.
    """
    lum=m['smooth'];h,w=lum.shape;yy,xx=np.indices(lum.shape);length=np.hypot(xx-seed[0],yy-seed[1]);blocked=np.zeros_like(lum,bool)
    steps=int(np.ceil(length.max()))+1
    for t in np.linspace(0,1,steps):
        x=seed[0]+t*(xx-seed[0]);y=seed[1]+t*(yy-seed[1])
        dark=ndi.map_coordinates(lum,[y,x],order=1,mode='nearest')
        ridge=ndi.map_coordinates(m['ridge'],[y,x],order=1,mode='nearest')
        blocked|=(t*length>3)&(ridge>.24)&(dark<.55*m['model']['diffuse_Y'])
    return ~blocked

def separators(m,seed,nearby):
    """R288-style five parallel actual-pixel profiles; endpoints remain unowned."""
    sm=m['smooth'];pg=m['pigment'];yy,xx=np.indices(sm.shape);rows=[]
    for q in nearby:
        p=np.array(seed,float);other=np.array(q['local_point'],float);delta=other-p;distance=float(np.linalg.norm(delta))
        if not 6<=distance<=55:continue
        refs=[];fractions=[]
        for v in (p,other):
            disk=(xx-v[0])**2+(yy-v[1])**2<=36;valid=disk&pg
            fractions.append(float(pg[disk].mean()));refs.append(float(np.quantile(sm[valid],.6)) if valid.any() else float(np.quantile(sm[disk],.6)))
        normal=np.array([-delta[1],delta[0]])/distance;t=np.linspace(0,1,max(31,int(distance*2)))
        profiles=[];ratios=[];positions=[];troughs=[]
        for off in PARAMETERS['corridor_offsets']:
            route=p+t[:,None]*delta+off*normal;v=ndi.uniform_filter1d(ndi.map_coordinates(sm,route[:,::-1].T,order=1,mode='nearest'),3)
            ids=np.flatnonzero((t>=.2)&(t<=.8));ix=ids[np.argmin(v[ids])]
            ratios.append(float(v[ix]/max(min(refs),.008)));positions.append(float(t[ix]));troughs.append(route[ix].tolist())
            profiles.append(dict(offset=off,Y=v.tolist(),route=route.tolist(),trough_index=int(ix)))
        coherence=float(np.mean(np.array(ratios)<.55));aligned=float(np.std(positions))
        supported=bool(ratios[2]<.55 and coherence>=.8 and aligned<.15 and min(refs)>.02 and min(fractions)>.35)
        rows.append(dict(feature_id=q['id'],point=q['point'],local_point=q['local_point'],distance=distance,reference_Y=refs,pigment_fractions=fractions,ratios=ratios,coherence=coherence,position_std=aligned,supported=supported,troughs=troughs,profiles=profiles,interpretation='Photographic separator evidence; an internal hole/shadow is a competing explanation, not certified distinct beads.'))
    return rows

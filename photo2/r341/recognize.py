"""One neighbor-oriented core, one fixed3x3 minimax; no pigment-dependent geometry."""
import numpy as np
THRESHOLD=73.5
CENTER=np.array([.248130237459968,-.0191702201531064]) # R340 geometry-only rectangle midpoint.

def sample(rgb,point,geometry,neighbors,kind):
 s=geometry['spacing'];center=np.array(point)+s*CENTER
 axis=np.array(geometry['J'])@np.array([1.,-1.]);axis/=np.linalg.norm(axis);perp=np.array([-axis[1],axis[0]])
 a,b=(.25,.25) if kind=='circle' else (.30,.20)
 x0,y0=np.floor(center-.31*s).astype(int);x1,y1=np.ceil(center+.31*s).astype(int)+1
 if min(x0,y0)<0 or x1>rgb.shape[1] or y1>rgb.shape[0]:return None
 yy,xx=np.mgrid[y0:y1,x0:x1];p=np.stack([xx-center[0],yy-center[1]],axis=-1);mask=((p@axis)/(a*s))**2+((p@perp)/(b*s))**2<=1
 # Keep one inset geometric Voronoi cell; nearby fixed bead identities own the other cells.
 for q in neighbors:
  shifted=np.array(q)+s*CENTER;mask&=(p*p).sum(2)+(.10*s)**2<((xx-shifted[0])**2+(yy-shifted[1])**2)
 valid=np.lib.stride_tricks.sliding_window_view(mask,(3,3)).all(axis=(-2,-1))
 if not valid.any():return None
 score=np.lib.stride_tricks.sliding_window_view(rgb[y0:y1,x0:x1].max(2),(3,3)).max(axis=(-2,-1)).astype(int);score[~valid]=256;j,i=np.unravel_index(score.argmin(),score.shape);x=int(x0+i);y=int(y0+j)
 return dict(score=int(score[j,i]),raw_decision='black' if score[j,i]<THRESHOLD else 'not-black',center=center.tolist(),axis=axis.tolist(),semiaxes=[a*s,b*s],region_pixels=np.c_[xx[mask],yy[mask]].tolist(),patch_box=[x,y,x+3,y+3],patch_RGB=rgb[y:y+3,x:x+3].tolist(),candidate_patches=int(valid.sum()))

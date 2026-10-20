"""Fixed pixels only; one region and one 3x3 maximum-RGB darkness measurement."""
import numpy as np
THRESHOLD=73.5

def sample(rgb,point,neighbors,kind):
 center=np.rint(point).astype(int)+([0,0] if kind=='at-support' else [6,0])
 x0,y0=center-4;yy,xx=np.mgrid[y0:y0+9,x0:x0+9];mask=np.ones((9,9),bool)
 if kind=='neighbor-clipped':
  for q in neighbors:
   shifted=np.rint(q).astype(int)+[6,0]
   mask&=(xx-center[0])**2+(yy-center[1])**2+4<(xx-shifted[0])**2+(yy-shifted[1])**2
 valid=np.lib.stride_tricks.sliding_window_view(mask,(3,3)).all(axis=(-2,-1))
 if not valid.any():return None
 values=np.lib.stride_tricks.sliding_window_view(rgb[y0:y0+9,x0:x0+9].max(2),(3,3)).max(axis=(-2,-1)).astype(int);values[~valid]=256
 j,i=np.unravel_index(values.argmin(),values.shape);x=int(x0+i);y=int(y0+j);s=int(values[j,i])
 return dict(score=s,decision='black' if s<THRESHOLD else 'not-black',region_pixels=np.c_[xx[mask],yy[mask]].tolist(),patch_box=[x,y,x+3,y+3],patch_RGB=rgb[y:y+3,x:x+3].tolist(),candidate_patches=int(valid.sum()),center=center.tolist())

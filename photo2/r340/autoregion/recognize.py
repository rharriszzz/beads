"""One geometric glass rectangle, one contiguous3x3 minimax, fixed73.5."""
import numpy as np

THRESHOLD=73.5

def fit_region(examples,spacing):
    bounds=[(np.array(r['absolute_material_box'])-np.tile(r['xy'],2))/spacing[r['id']] for r in examples]
    return np.median(bounds,axis=0).tolist()

def measure(photo,xy,spacing,bounds):
    x0,y0,x1,y1=np.rint(np.tile(xy,2)+spacing*np.array(bounds)).astype(int)
    if min(x0,y0)<0 or x1>photo.shape[1] or y1>photo.shape[0] or min(x1-x0,y1-y0)<3:return None
    v=photo[y0:y1,x0:x1].max(axis=2)
    patches=np.lib.stride_tricks.sliding_window_view(v,(3,3)).max(axis=(-2,-1))
    j,i=np.unravel_index(patches.argmin(),patches.shape);x=int(x0+i);y=int(y0+j)
    return dict(region_box=[int(x0),int(y0),int(x1),int(y1)],patch_box=[x,y,x+3,y+3],score=int(patches[j,i]),decision='black' if patches[j,i]<THRESHOLD else 'not-black',patch_RGB=photo[y:y+3,x:x+3].tolist())

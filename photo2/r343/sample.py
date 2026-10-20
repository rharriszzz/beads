"""Small colored-material sample with clearance, never a darkness extremum."""
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt

def inside_polygon(poly):
 p=np.array(poly);lo=p.min(0)-2;hi=p.max(0)+3;image=Image.new('1',tuple(hi-lo),0);ImageDraw.Draw(image).polygon([tuple(v-lo) for v in p],fill=1);mask=np.array(image,bool);yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];return mask,xx,yy

def interior_patch(poly):
 mask,xx,yy=inside_polygon(poly);clear=distance_transform_edt(mask);valid=np.lib.stride_tricks.sliding_window_view(mask,(3,3)).all((-2,-1));margin=np.lib.stride_tricks.sliding_window_view(clear,(3,3)).min((-2,-1));margin[~valid]=-1;j,i=np.unravel_index(margin.argmax(),margin.shape)
 if margin[j,i]<2:return None
 x=int(xx[j,i]);y=int(yy[j,i]);return dict(patch_box=[x,y,x+3,y+3],minimum_pixel_clearance=float(margin[j,i]),region_pixels=np.c_[xx[mask],yy[mask]].tolist(),method='Maximum clearance3x3 inside an inspected native glass core, minimum2pixels. Geometry only; no darkest-patch search.')

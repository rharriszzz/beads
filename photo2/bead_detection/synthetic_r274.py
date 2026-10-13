"""Known color interfaces, including equal-Y boundaries; truth only evaluates output."""
import numpy as np
from matplotlib.colors import hsv_to_rgb
from .brightness_r270 import linearize,encode

def scenes():
 yy,xx=np.mgrid[:128,:144]
 for pair in ((18,42),(0,60),(358,55),(18,18),(42,42)):
  for kind in ('equal-Y','shading','neutral-highlight','soft-boundary','dim','gap'):
   rgb=np.full((128,144,3),hsv_to_rgb([.83,.42,.78]));truth=np.zeros((128,144),np.uint8)
   centers=[(57,64),(91 if kind=='gap' else 81,64)]
   for i,((cx,cy),h) in enumerate(zip(centers,pair),1):
    rad=((xx-cx)/15)**2+((yy-cy)/17)**2;inside=rad<=1
    if kind!='gap':inside &= xx<69 if i==1 else xx>=69
    truth[inside]=i
    hue=np.full(rad.shape,h/360.);sat=np.full(rad.shape,.83)
    if kind=='soft-boundary' and pair[0]!=pair[1]:
     t=np.clip((xx-66)/6,0,1);delta=(pair[1]-pair[0]+180)%360-180;hue=((pair[0]+delta*t)%360)/360
    unit=linearize(hsv_to_rgb(np.stack([hue,sat,np.ones_like(rad)],axis=-1)))
    ybase=.15*(.92+.08*np.sqrt(np.maximum(0,1-rad)))
    if kind=='shading':ybase*=np.clip(.85+.55*(xx-cx)/15,.2,1.3)
    if kind=='dim':ybase*=.50
    glint=np.exp(-((xx-cx+3)**2+(yy-cy+3)**2)/10)
    ytarget=ybase+.05*glint
    linear=unit*ytarget[:,:,None]/(unit@np.array([.2126,.7152,.0722]))[:,:,None]
    if kind=='neutral-highlight':linear=linear*(1-.9*glint[:,:,None])+.75*.9*glint[:,:,None]
    rgb[inside]=encode(np.clip(linear,0,1))[inside]
   name=f'h{pair[0]}-h{pair[1]}-{kind}';colors={1:'red' if pair[0]<30 or pair[0]>330 else 'yellow',2:'red' if pair[1]<30 or pair[1]>330 else 'yellow'}
   yield name,np.rint(rgb*255).astype(np.uint8),truth,colors
 for h in (0,18,42,60,300):
  rgb=np.full((128,144,3),hsv_to_rgb([h/360,.40,.70]));rgb*= (1-.5*np.exp(-((xx-72)**2+(yy-64)**2)/500))[:,:,None]
  yield 'background-'+str(h),np.rint(rgb*255).astype(np.uint8),np.zeros((128,144),np.uint8),{}

"""Fixed automatic-location highlight/shading tests isolate region growth."""
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from PIL import Image
from .synthetic_r274 import scenes
from .hue_r274 import grow,SELECTED,color_surface,palette_from
from .interiors_r273 import colored_interior,SELECTED as OLD
from .coverage_r272 import detect as baseline
from .brightness_r270 import linearize
from .climb_r268 import background
from .experiment_r274 import OUT,save
from .review_r274 import panel
from .evaluate_coverage_r272 import metric

def main():
 data={n:(r,t,c) for n,r,t,c in scenes()};source=data['h18-h42-equal-Y'][0];base=baseline(source)[0];results=[]
 for condition in ('equal-Y','soft-boundary','shading','neutral-highlight','dim'):
  rgb,t,c=data['h18-h42-'+condition];hs=rgb_to_hsv(rgb/255.);l=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);m=ndi.uniform_filter(l,3);_,paper,_=background(rgb);surface=color_surface(hs);old=[colored_interior(r,rgb,rgb,hs,l,m,paper,OLD) for r in base];new=[grow(r,rgb,rgb,hs,l,m,paper,surface,palette_from(base),SELECTED) for r in base]
  stats={}
  for name,rows in [('r273',old),('r274',new)]:
   accepted=[r for r in rows if r['accepted']];met,_=metric(accepted,t,c);stats[name]=dict(metrics=met,regions=[dict(id=r['id'],accepted=r['accepted'],area=r.get('region',{}).get('pixel_count',0),reasons=r['reasons']) for r in rows])
  panel(Image.fromarray(rgb),[r for r in old if r['accepted']],[r for r in new if r['accepted']],[30,38,110,90],'synthetic-'+condition+'.png','Fixed automatic locations: '+condition,scale=4)
  results.append(dict(condition=condition,results=stats))
 save('component-evaluation.json',dict(scope='Region component only: locations and core colors automatically detected from the equal-Y input, then held fixed while only illumination/highlights change. Not end-to-end recall.',results=results))
if __name__=='__main__':main()

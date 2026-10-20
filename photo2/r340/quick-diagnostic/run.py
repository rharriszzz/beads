"""Nine maker-reviewed bodies; manually selected glass interiors; one 3x3 patch."""
from pathlib import Path
import json,time
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.ndimage import maximum_filter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
# Rectangles selected by inspecting native-selection.png before measurement.
BOXES=[[1053,2778,1061,2785],[2088,2609,2094,2617],[501,1595,507,1602],[314,1445,321,1451],[416,1571,423,1579],[1901,419,1907,426],[1701,1510,1711,1519],[1341,2979,1349,2988],[1305,312,1312,321]]
def run():
 start=time.monotonic();im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');rgb=np.asarray(im);rows=json.loads((OUT/'selection.json').read_text());overlay=Image.open(OUT/'native-selection.png');d=ImageDraw.Draw(overlay)
 for j,(r,box) in enumerate(zip(rows,BOXES)):
  x0,y0,x1,y1=box;v=rgb[y0:y1,x0:x1].max(2);patch=maximum_filter(v,size=3,mode='constant',cval=255)[1:-1,1:-1];y,x=np.unravel_index(patch.argmin(),patch.shape);x+=x0;y+=y0;r.update(glass_interior_box=box,dark_patch_box=[int(x),int(y),int(x+3),int(y+3)],dark_patch_brightness=int(patch.min()),brightness_definition='maximum RGB channel, then maximum across all9 contiguous3x3 pixels; select minimum such patch wholly inside manually approved glass rectangle',patch_RGB=rgb[y:y+3,x:x+3].tolist(),material_pixel_range=[int(v.min()),int(v.max())]);ox=j%3*300;oy=j//3*320+25;bx,by=r['bbox'][:2];d.rectangle((ox+(x0-bx)*6,oy+(y0-by)*6,ox+(x1-bx)*6,oy+(y1-by)*6),outline='lime',width=2);d.rectangle((ox+(x-bx)*6,oy+(y-by)*6,ox+(x+3-bx)*6,oy+(y+3-by)*6),outline='cyan',width=2)
 groups={c:[r['dark_patch_brightness'] for r in rows if r['color']==c] for c in ['black','red','yellow']};ranges={c:[min(v),max(v)] for c,v in groups.items()};b=max(groups['black']);c=min(groups['red']+groups['yellow']);threshold=(b+c)/2 if b<c else None;result=dict(records=rows,ranges=ranges,black_max=b,colored_min=c,overlap=b>=c,separating_threshold=threshold,exceptions=[r['id'] for r in rows if (r['color']=='black' and r['dark_patch_brightness']>=c) or (r['color']!='black' and r['dark_patch_brightness']<=b)],scope='Nine manually inspected maker-reviewed bodies only. No whole-photograph accuracy claim; material rectangles exclude visible reflections, boundaries and inter-bead shadows. No classifier redesign or inference from darkest unowned aperture pixels.',computation_seconds=time.monotonic()-start);(OUT/'measurements.json').write_text(json.dumps(result,indent=2)+'\n');overlay.save(OUT/'measured-native.png')
 fig,ax=plt.subplots(figsize=(11,4.5));colors={'black':'#20242b','red':'#d63c42','yellow':'#d6a200'}
 for i,name in enumerate(['black','red','yellow']):
  rr=[r for r in rows if r['color']==name];ax.plot(ranges[name],[i,i],lw=9,alpha=.2,color=colors[name]);ax.scatter([r['dark_patch_brightness'] for r in rr],[i]*len(rr),c=colors[name],s=65,zorder=3)
  for k,r in enumerate(rr):ax.annotate(r['id'],(r['dark_patch_brightness'],i),xytext=(0,13+13*k),textcoords='offset points',fontsize=8,ha='center')
 if threshold is not None:ax.axvline(threshold,color='#29846d',ls='--',label=f'Separating threshold {threshold:g}/255');ax.legend(loc='lower right')
 ax.set(xlim=(0,255),ylim=(-.4,2.9),yticks=[0,1,2],yticklabels=['Black','Red','Yellow'],xlabel='Darkest genuine-material 3×3 patch: brightest channel/pixel (0–255)',title='One shared brightness scale — seven maker-reviewed interiors + two visual red controls');ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(OUT/'brightness.png',dpi=150);plt.close(fig);print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':run()

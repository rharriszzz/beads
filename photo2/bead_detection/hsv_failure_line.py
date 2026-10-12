"""Post-search diagnostic: every native pixel on a line through the failed support."""
import csv
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from matplotlib.colors import rgb_to_hsv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .tunable_detect import ROOT,save


def main():
    out=ROOT/'photo2/review/r263'
    data=json.loads((ROOT/'photo2/output/search-r263/p40-b2/regions.json').read_text())
    r=next(r for r in data['regions'] if r['id']=='P126974')
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    y=r['location'][1];xs=np.arange(1690,1991);colors=rgb[y,xs];hsv=rgb_to_hsv(colors/255)
    h=hsv[:,0]*360;s=hsv[:,1];v=colors.max(axis=1)
    sx,sy=r['bright_patch']['peak'];seed=rgb_to_hsv(rgb[sy,sx]/255)
    delta=np.minimum(np.abs(h-seed[0]*360),360-np.abs(h-seed[0]*360))
    member={(x,yy) for yy,lo,hi in r['pixel_runs'] for x in range(lo,hi+1)}
    inside=np.array([(int(x),y) in member for x in xs])
    paper=np.array(data['background']['chromaticity'])
    pdist=np.linalg.norm(colors/np.maximum(v[:,None],1)-paper,axis=1)
    with (out/'hsv-line.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['x','y','red','green','blue','hue_degrees','saturation','value_dn','circular_hue_difference_from_seed_degrees','retained_by_failed_region','paper_chromaticity_distance'])
        for i,x in enumerate(xs):w.writerow([int(x),y,*map(int,colors[i]),float(h[i]),float(s[i]),int(v[i]),float(delta[i]),bool(inside[i]),float(pdist[i])])
    fig=plt.figure(figsize=(15,10));gs=fig.add_gridspec(5,2,width_ratios=(1,1.6),hspace=.35,wspace=.22)
    ax=fig.add_subplot(gs[:4,0]);x0,x1=1630,2060;y0,y1=y-180,y+180
    ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest')
    ax.plot(xs,np.full(len(xs),y),color='yellow',lw=1.5)
    ax.plot(r['location'][0],y,'x',color='white',ms=12,mew=2)
    for x,txt in [(xs[0],'A'),(xs[-1],'B')]:ax.text(x,y-14,txt,color='yellow',fontsize=15,bbox=dict(facecolor='black',alpha=.65,pad=2))
    ax.set_title(f'Line A–B: y={y}; x=1690…1990\nWhite × = displaced supported coordinate')
    ax.set_xlabel('Native photograph x');ax.set_ylabel('Native photograph y')
    hs=fig.add_subplot(gs[0,1]);hs.scatter(xs,h,s=5,c='purple');hs.set(ylabel='H (degrees)',ylim=(-5,365));hs.set_title('301 consecutive source pixels; no filtering or interpolation')
    dh=fig.add_subplot(gs[1,1],sharex=hs);dh.plot(xs,delta,color='purple',lw=1)
    for threshold,color in [(20,'orange'),(10,'green')]:dh.axhline(threshold,color=color,ls='--',label=f'{threshold}° hue limit')
    dh.set(ylabel='Circular ΔH\nfrom seed (°)');dh.legend(fontsize=8,loc='upper right')
    ss=fig.add_subplot(gs[2,1],sharex=hs);ss.plot(xs,s,color='darkorange');ss.axhline(.35,color='gray',ls='--',label='S≥0.35 hue reliability gate');ss.set(ylabel='S (0–1)',ylim=(0,1));ss.legend(fontsize=8)
    vv=fig.add_subplot(gs[3,1],sharex=hs);vv.plot(xs,v,color='black');vv.axhline(81,color='gray',ls='--',label='Dark threshold81');vv.set(ylabel='V (0–255)',ylim=(0,260));vv.legend(fontsize=8)
    strip=fig.add_subplot(gs[4,1],sharex=hs);strip.imshow(colors[None,:,:],extent=(xs[0]-.5,xs[-1]+.5,1,0),aspect='auto',interpolation='nearest')
    strip.scatter(xs[inside],np.full(inside.sum(),1.25),s=4,color='#009fa8');strip.set(ylim=(1.5,-.1),yticks=[.5,1.25],yticklabels=['Source RGB','In support'],xlabel='Native photograph x, along A → B')
    note=fig.add_subplot(gs[4,0]);note.axis('off');note.text(0,.95,'The line crosses the bracelet edge, shadowed paper,\nand lighter paper. It is a diagnostic cross-section,\nnot the actual priority-queue expansion route.\nHue changes are clues; matching hue is not bead proof.',va='top',fontsize=10)
    for axis in (hs,dh,ss,vv,strip):axis.grid(alpha=.18);axis.set_xlim(xs[0],xs[-1])
    fig.suptitle('Why a brightness-only allowance can follow the background shadow',fontsize=17)
    fig.subplots_adjust(top=.91,bottom=.065,left=.06,right=.98);fig.savefig(out/'hsv-line.png',dpi=155);plt.close(fig)
    summary=dict(region_id=r['id'],line_start=[int(xs[0]),y],line_end=[int(xs[-1]),y],native_samples=len(xs),source_interpolation=False,
        seed=[sx,sy],seed_hsv=[float(seed[0]*360),float(seed[1]),float(seed[2])],sampled_membership=int(inside.sum()),
        role='Post-hoc diagnostic straight line, not a growth predecessor path.',segments=[])
    for lo,hi in [(1690,1760),(1761,1840),(1841,1990)]:
        choose=(xs>=lo)&(xs<=hi);summary['segments'].append(dict(x_range=[lo,hi],value_range=[int(v[choose].min()),int(v[choose].max())],hue_range=[float(h[choose].min()),float(h[choose].max())],saturation_range=[float(s[choose].min()),float(s[choose].max())],paper_compatible_fraction=float(np.mean(pdist[choose]<data['background']['tolerance']))))
    save(out/'hsv-line.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':main()

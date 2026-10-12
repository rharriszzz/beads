"""Illustrate already-completed trials; no detector or parameter search runs."""
import json
import csv
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .tunable_detect import ROOT,save


def main():
    out=ROOT/'photo2/review/r263';rid='P126974'
    old=json.loads((ROOT/'photo2/output/detection-r262/regions.json').read_text())
    new=json.loads((ROOT/'photo2/output/search-r263/p40-b2/regions.json').read_text())
    a=next(r for r in old['regions'] if r['id']==rid);b=next(r for r in new['regions'] if r['id']==rid)
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    x0,y0,x1,y1=b['bbox'];x0-=45;y0-=45;x1+=45;y1+=45
    x0=max(0,x0);y0=max(0,y0);x1=min(rgb.shape[1],x1);y1=min(rgb.shape[0],y1)
    extent=(x0-.5,x1-.5,y1-.5,y0-.5)
    fig,axes=plt.subplots(1,3,figsize=(15,9.5),sharex=True,sharey=True)
    for ax in axes:
        ax.imshow(rgb[y0:y1,x0:x1],extent=extent,interpolation='nearest')
        ax.set_xlim(x0-.5,x1-.5);ax.set_ylim(y1-.5,y0-.5);ax.set_xlabel('Native photograph x')
    axes[0].set_ylabel('Native photograph y')
    axes[0].set_title('Original photograph',fontsize=15)
    for ax,r,title in [(axes[1],a,'Strict growth: 186 pixels'),(axes[2],b,'Two-level allowance: 17,095 pixels')]:
        overlay=np.zeros((y1-y0,x1-x0,4))
        for y,lo,hi in r['pixel_runs']:
            if y0<=y<y1:overlay[y-y0,max(lo,x0)-x0:min(hi+1,x1)-x0]=[0,1,1,.95]
        ax.imshow(overlay,extent=extent,interpolation='nearest')
        ax.set_title(title,fontsize=15)
    seed=a['bright_patch']['peak'];ca=a['centroid'];cb=b['centroid']
    for ax in axes:
        ax.plot(*seed,'o',ms=10,mfc='none',mec='#ffff00',mew=2)
        ax.annotate('Starting maximum',xy=seed,xytext=(x0+70,y1-70),color='#ffff00',fontsize=11,
                    arrowprops=dict(arrowstyle='->',color='#ffff00'),bbox=dict(facecolor='black',alpha=.7,pad=3))
    axes[1].plot(*ca,'+',ms=17,color='white',mew=2)
    axes[2].plot(*cb,'x',ms=17,color='white',mew=3)
    axes[2].annotate('Centroid moved 776 pixels',xy=cb,xytext=(x0+60,y0+115),color='white',fontsize=12,
                     arrowprops=dict(arrowstyle='->',color='white',lw=2),bbox=dict(facecolor='black',alpha=.75,pad=4))
    axes[2].annotate('',xy=cb,xytext=ca,arrowprops=dict(arrowstyle='->',color='#ffff00',lw=2.5))
    fig.suptitle('Biggest observed failure: growth spreads into paper and loses the bead coordinate',fontsize=17)
    fig.text(.5,.018,'Cyan = exact retained source pixels. Yellow arrow = centroid displacement. Same seed and photograph; no inferred bead positions.\n83% of the expanded support matches the learned paper appearance. Shadow involvement remains a hypothesis.',ha='center',fontsize=11)
    fig.tight_layout(rect=(0,.065,1,.94));fig.savefig(out/'biggest-problem.png',dpi=150);plt.close(fig)
    # Near the seed: exact native pixels displayed without image interpolation.
    sx,sy=seed;x0,y0,x1,y1=sx-35,sy-35,sx+36,sy+36
    fig,axes=plt.subplots(1,3,figsize=(13,4.6))
    for ax in axes:
        ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest');ax.set_xlim(x0-.5,x1-.5);ax.set_ylim(y1-.5,y0-.5)
    axes[0].set_title('Original native-pixel close-up')
    for ax,r,title in [(axes[1],a,'Strict growth'),(axes[2],b,'Two-level allowance')]:
        for curve in r['contours']:
            c=np.array(curve);ax.plot(c[:,0],c[:,1],color='cyan',lw=.7)
        ax.plot(*seed,'+',color='yellow',ms=10);ax.set_title(title)
    fig.tight_layout();fig.savefig(out/'biggest-problem-closeup.png',dpi=170);plt.close(fig)
    evidence=dict(id=rid,seed=seed,strict_pixels=a['pixel_count'],expanded_pixels=b['pixel_count'],
        strict_centroid=ca,expanded_centroid=cb,strict_supported_coordinate=a['location'],expanded_supported_coordinate=b['location'],
        centroid_displacement=float(np.linalg.norm(np.array(cb)-ca)),expanded_bbox=b['bbox'],
        interpretation='Background-compatible spread; background shadow possible, not established. Nonzero rise allowance rejected for recommendation.')
    save(out/'biggest-problem.json',evidence)
    oldpoints={(x,y) for y,lo,hi in a['pixel_runs'] for x in range(lo,hi+1)}
    with (out/'biggest-problem-pixels.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['x','y','r','g','b','value_dn','also_in_strict_support'])
        for y,lo,hi in b['pixel_runs']:
            for x in range(lo,hi+1):w.writerow([x,y,*map(int,rgb[y,x]),int(rgb[y,x].max()),int((x,y) in oldpoints)])
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()

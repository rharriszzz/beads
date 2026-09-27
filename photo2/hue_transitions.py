"""R100: raw HSV along the frozen T1/T2 routes; no edge classifier."""
import argparse
import csv
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
import numpy as np
from PIL import Image, ImageOps
from background_probe import ROOT, digest


def red_relative(h):
    return (360*h+180)%360-180


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r100')
    out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'beads-photo-2.jpg'; pathsource=ROOT/'photo2/review/r099/report.json'
    im=ImageOps.exif_transpose(Image.open(source)).convert('RGB');rgb=np.asarray(im)/255.
    paths=json.loads(pathsource.read_text())['paths'][:2]
    assert np.allclose(rgb_to_hsv(np.eye(3))[:,0],[0,1/3,2/3])
    assert np.allclose(red_relative(np.array([359/360,1/360])),[-1,1])
    assert rgb_to_hsv(np.array([[.2,.2,.2]]))[0,1]==0
    rows=[];summaries={}
    for path in paths:
        distances=np.arange(193);start=np.array(path['start']);direction=np.array(path['direction'])
        xy=start+distances[:,None]*direction
        colors=rgb[xy[:,1],xy[:,0]];hsv=rgb_to_hsv(colors);chroma=colors.max(1)-colors.min(1)
        hue=red_relative(hsv[:,0]);hue[chroma==0]=np.nan
        for i,(x,y) in enumerate(xy):
            rows.append(dict(path=path['id'],distance=i,x=int(x),y=int(y),
                             hue_degrees=float(hsv[i,0]*360) if chroma[i]>0 else '',
                             hue_from_red=float(hue[i]) if chroma[i]>0 else '',
                             saturation=float(hsv[i,1]),value=float(hsv[i,2]),chroma=float(chroma[i])))
        summaries[path['id']]=dict(minimum_value=float(hsv[:,2].min()),minimum_chroma=float(chroma.min()),
                                   achromatic_count=int((chroma==0).sum()),
                                   stops=[rows[-193+i] for i in (0,24,32,40,48,64,96,192)])
        fig=plt.figure(figsize=(12,10));gs=fig.add_gridspec(4,3,height_ratios=[1.4,.22,1,1])
        mid=start+96*direction;end=start+192*direction
        for col,title in enumerate(('Raw photo','Same P and Q as R099','Same sampling route; labeled stops')):
            ax=fig.add_subplot(gs[0,col]);ax.imshow(im)
            ax.set_xlim(mid[0]-170,mid[0]+170);ax.set_ylim(mid[1]+170,mid[1]-170)
            ax.set_axis_off();ax.set_title(title,fontsize=10)
            if col==1:
                for name,pt in [('P',start),('Q',end)]:
                    ax.plot(*pt,'o',mec='white',mfc='none',ms=7)
                    ax.annotate(name,pt,xytext=(5,8),textcoords='offset points',color='white')
            if col==2:
                ax.plot([start[0],end[0]],[start[1],end[1]],color='cyan',lw=1)
                for t in (0,32,64,96,192):
                    pt=start+t*direction;ax.plot(*pt,'+',color='white')
                    ax.annotate({0:'P',192:'Q'}.get(t,str(t)),pt,
                                xytext=(3,8 if t%64==0 else -15),textcoords='offset points',color='white',fontsize=9)
        ax=fig.add_subplot(gs[1,:]);ax.imshow(colors[None,:,:],extent=(-.5,192.5,0,1),aspect='auto')
        ax.set_yticks([]);ax.set_xlim(0,192);ax.set_title('Exact pixel colors along P → Q; one sample per pixel',fontsize=10)
        ax=fig.add_subplot(gs[2,:]);ax.plot(distances,hue,color='purple',lw=1.2,label='Raw hue, red at 0°')
        ax.axhline(0,color='gray',lw=.6);ax.set_ylim(-65,65);ax.set_xlim(0,192)
        ax.set_ylabel('Hue relative to red (degrees)');ax.set_xlabel('Distance from P (original pixels)')
        ax.set_title('Negative angles turn from red toward magenta; no 360° wrap jump')
        for t in (24,40,64):
            ax.plot(t,hue[t],'o',color='purple',ms=4)
            ax.annotate(f'{t}: {hue[t]:.1f}°',(t,hue[t]),xytext=(7,12 if t!=40 else -20),textcoords='offset points',fontsize=9)
        ax=fig.add_subplot(gs[3,:])
        for values,label in [(hsv[:,1],'Saturation S'),(hsv[:,2],'Value V'),(chroma,'RGB chroma = max − min')]:ax.plot(distances,values,label=label)
        ax.set_ylim(0,1.05);ax.set_xlim(0,192);ax.set_xlabel('Distance from P (original pixels)')
        ax.set_ylabel('0–1 JPEG units');ax.legend(ncol=3,fontsize=9)
        ax.set_title('Brightness and color strength: hue alone does not identify a surface')
        fig.suptitle(path['id']+': hue supplies a local clue despite overlapping color ranges\nRaw photo and frozen route; no hue threshold or bead edge selected',fontsize=12)
        fig.tight_layout(rect=(0,0,1,.94));fig.savefig(out/(path['id']+'-hue.png'),dpi=140);plt.close(fig)
    with (out/'samples.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    provenance=ROOT/'photo2/hsv-provenance-r100.json'
    report=dict(source_sha256=digest(source),script_sha256=digest(__file__),helper_sha256=digest(ROOT/'photo2/background_probe.py'),
                paths_source_sha256=digest(pathsource),provenance_sha256=digest(provenance),
                paths=paths,sampling='Original integer pixels, 0 through 192 inclusive; no smoothing or interpolation',
                hsv='matplotlib RGB-to-HSV on original JPEG RGB/255; H degrees, S/V 0–1',
                hue_plot='(H_degrees+180) mod 360 -180; achromatic hue undefined',
                checks=['primary hue conversion','red wrap handling','achromatic saturation'],
                summaries=summaries,rows=len(rows),versions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),
                artifacts={p.name:digest(p) for p in sorted(out.iterdir()) if p.suffix in ('.png','.csv')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(rows=len(rows),summaries=summaries),indent=2))


if __name__=='__main__':main()

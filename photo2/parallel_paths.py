"""R104: parallel-route hue/texture and paper-reference sensitivity."""
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
from matplotlib.patches import Circle
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import gaussian_filter
from background_probe import ROOT,digest
from background_transitions import Probe,crop,crossing,DISTANCES

METRICS=('detrended_rms_64','spatial_rms')


def circular_difference(a,b):
    """Signed b-a in hue turns, expressed in degrees, independent of hue zero."""
    return (360*(np.asarray(b)-np.asarray(a))+180)%360-180


def local_hue_steps(h,c,width):
    result=np.full(len(h),np.nan);concentration=np.full(len(h),np.nan)
    for i in range(width,len(h)-width):
        means=[];strength=[]
        for sl in (slice(i-width,i),slice(i+1,i+1+width)):
            weight=c[sl].sum()
            if weight<1e-12:break
            z=np.sum(c[sl]*np.exp(2j*np.pi*h[sl]))/weight
            if abs(z)<1e-6:break
            means.append(np.angle(z)/(2*np.pi));strength.append(abs(z))
        if len(means)==2:
            result[i]=circular_difference(*means);concentration[i]=min(strength)
    return result,concentration


def checks():
    h=np.linspace(.94,1.06,65)%1;c=np.linspace(.1,.9,65)
    a,_=local_hue_steps(h,c,8);b,_=local_hue_steps((h+.37)%1,c,8)
    assert np.allclose(a,b,equal_nan=True,atol=1e-10)
    assert abs(float(circular_difference(359/360,1/360))-2)<1e-10
    zero,_=local_hue_steps(np.full(65,.3),np.ones(65),8)
    assert np.nanmax(abs(zero))<1e-10
    absent,_=local_hue_steps(np.full(65,.3),np.zeros(65),8)
    assert np.isnan(absent).all()
    return ['hue-zero rotation invariance','red-wrap difference','constant hue','achromatic undefined']


def write_csv(path,rows):
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r104')
    out=parser.parse_args().output;out.mkdir(parents=True,exist_ok=True)
    configpath=ROOT/'photo2/parallel-paths-r104.json';basepath=ROOT/'photo2/review/r099/report.json'
    cfg=json.loads(configpath.read_text());base=json.loads(basepath.read_text());control=checks()
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    rgb=np.asarray(im)/255.;gray=rgb@np.array([.299,.587,.114]);spatial=gray-gaussian_filter(gray,4,mode='reflect')
    texture=[];huerows=[];huecurves={};paper=[];references={};curves={};routes=[];candidates=[]
    for sigma in cfg['sigmas_px']:
        probe=Probe(sigma)
        for ref in cfg['extra_paper']:
            x,y=ref['center'];values=probe.measure(crop(gray,x,y),crop(spatial,x,y))
            paper.append(dict(id=ref['id'],group=ref['group'],x=x,y=y,sigma=sigma,**{m:values[m] for m in METRICS}))
        old=base['references'][str(float(sigma))]
        references[sigma]={
            'original':{m:old[m] for m in METRICS},
            'plus_clear':{m:max(old[m],*(r[m] for r in paper if r['sigma']==sigma and r['group']=='clear')) for m in METRICS},
            'plus_shadow':{m:max(old[m],*(r[m] for r in paper if r['sigma']==sigma)) for m in METRICS},
            'new_clear_only':{m:max(r[m] for r in paper if r['sigma']==sigma and r['group']=='clear') for m in METRICS},
            'shadow_only':{m:max(r[m] for r in paper if r['sigma']==sigma and r['group']=='shadow') for m in METRICS}}
    for path in base['paths']:
        direction=np.array(path['direction']);normal=np.array([-direction[1],direction[0]])
        for offset in cfg['offsets_px']:
            start=np.array(path['start'])+offset*normal;key=f"{path['id']}/{offset:+d}"
            route=dict(id=path['id'],offset=offset,start=start.tolist(),end=(start+192*direction).tolist(),direction=direction.tolist())
            routes.append(route)
            xy=start+np.arange(193)[:,None]*direction
            colors=rgb[xy[:,1],xy[:,0]];hsv=rgb_to_hsv(colors);chroma=colors.max(1)-colors.min(1)
            step,strength=local_hue_steps(hsv[:,0],chroma,cfg['hue_halfwidth_px'])
            huecurves[key]=dict(hue=hsv[:,0],step=step,colors=colors)
            for i,(x,y) in enumerate(xy):
                huerows.append(dict(id=path['id'],offset=offset,distance=i,x=int(x),y=int(y),
                                    hue=float(hsv[i,0]) if chroma[i]>0 else '',chroma=float(chroma[i]),
                                    hue_step=float(step[i]) if np.isfinite(step[i]) else '',
                                    resultant=float(strength[i]) if np.isfinite(strength[i]) else ''))
            for sigma in cfg['sigmas_px']:
                probe=Probe(sigma);selected=[]
                for t in DISTANCES:
                    x,y=start+t*direction;values=probe.measure(crop(gray,x,y),crop(spatial,x,y))
                    row=dict(id=path['id'],offset=offset,distance=int(t),x=int(x),y=int(y),sigma=sigma,**{m:values[m] for m in METRICS})
                    texture.append(row);selected.append(row)
                curves[key,sigma]=selected
                for family,ref in references[sigma].items():
                    for metric in METRICS:
                        for mult in cfg['threshold_multipliers']:
                            threshold=mult*ref[metric]
                            candidates.append(dict(id=path['id'],offset=offset,sigma=sigma,family=family,metric=metric,multiplier=mult,
                                                   threshold=threshold,distance=crossing([r[metric] for r in selected],threshold)))
    write_csv(out/'texture.csv',texture);write_csv(out/'hue.csv',huerows);write_csv(out/'paper.csv',paper)
    summaries={}
    for path in base['paths']:
        ident=path['id'];deltas=[];summary={}
        for offset in cfg['offsets_px']:
            h=huecurves[f'{ident}/{offset:+d}']['hue'];lo,hi=cfg['hue_comparison_stops_px']
            deltas.append(float(circular_difference(h[lo],h[hi])))
        summary['hue_40_to_64_deg']=dict(zip(map(str,cfg['offsets_px']),deltas))
        summary['largest_hue_step']={}
        for offset in cfg['offsets_px']:
            step=huecurves[f'{ident}/{offset:+d}']['step'];t=int(np.nanargmax(abs(step)))
            summary['largest_hue_step'][str(offset)]=dict(distance=t,degrees=float(step[t]))
        for family in ('original','plus_clear','plus_shadow','new_clear_only','shadow_only'):
            cs=[c for c in candidates if c['id']==ident and c['family']==family]
            valid=[c['distance'] for c in cs if c['distance'] is not None]
            summary[family]=dict(crossing_range=[min(valid),max(valid)] if valid else None,unresolved=len(cs)-len(valid),total=len(cs))
        summaries[ident]=summary
        fig=plt.figure(figsize=(12,12));gs=fig.add_gridspec(5,3,height_ratios=[1.5,.35,1,1,1])
        start=np.array(path['start']);direction=np.array(path['direction']);mid=start+96*direction
        for col,title in enumerate(('Raw context','Shifted endpoints (unconfirmed)','Parallel sampling routes')):
            ax=fig.add_subplot(gs[0,col]);ax.imshow(im);ax.set_xlim(mid[0]-150,mid[0]+150);ax.set_ylim(mid[1]+150,mid[1]-150);ax.set_axis_off();ax.set_title(title,fontsize=10)
            if col:
                for i,offset in enumerate(cfg['offsets_px']):
                    route=next(r for r in routes if r['id']==ident and r['offset']==offset);a=np.array(route['start']);b=np.array(route['end']);color=plt.get_cmap('tab10')(i)
                    ax.plot([a[0],b[0]],[a[1],b[1]],'o',mfc='none',mec=color,ms=4)
                    if col==2:ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1,label=f'{offset:+d} px')
                ax.annotate('P',start,xytext=(-15,-18),textcoords='offset points',color='white',weight='bold')
                ax.annotate('Q',start+192*direction,xytext=(8,8),textcoords='offset points',color='white',weight='bold')
                if col==2:ax.legend(fontsize=8,loc='lower right')
        ax=fig.add_subplot(gs[1,:]);strip=np.stack([huecurves[f'{ident}/{o:+d}']['colors'] for o in cfg['offsets_px']])
        ax.imshow(strip,extent=(-.5,192.5,2.5,-.5),aspect='auto');ax.set_yticks(range(3),[str(o) for o in cfg['offsets_px']]);ax.set_ylabel('offset');ax.set_xlim(0,192);ax.set_title('Pixel colors along each shifted P → Q',fontsize=10)
        ax=fig.add_subplot(gs[2,:])
        for i,offset in enumerate(cfg['offsets_px']):ax.plot(np.arange(193),huecurves[f'{ident}/{offset:+d}']['step'],color=plt.get_cmap('tab10')(i),label=f'{offset:+d} px')
        ax.axhline(0,color='gray',lw=.5);ax.set_xlim(0,192);ax.set_ylabel('Signed local hue change (degrees)');ax.set_title('Chroma-weighted circular hue: eight pixels after versus eight before; center excluded');ax.legend(ncol=3,fontsize=8)
        for panel,metric in [(3,'detrended_rms_64'),(4,'spatial_rms')]:
            ax=fig.add_subplot(gs[panel,:]);sigma=12
            for i,offset in enumerate(cfg['offsets_px']):
                values=[r[metric] for r in curves[f'{ident}/{offset:+d}',sigma]]
                ax.plot(DISTANCES,values,color=plt.get_cmap('tab10')(i),label=f'{offset:+d} px')
            for family,style in [('original',':'),('new_clear_only','--'),('shadow_only','-.')]:ax.axhline(2*references[sigma][family][metric],ls=style,color='gray',label='2× '+family)
            ax.set_xlim(0,192);ax.set_ylabel('RMS, JPEG units');ax.set_xlabel('Distance from shifted P (original pixels)')
            ax.set_title(('Detrended FFT ≥1/64 cycles/pixel' if panel==3 else 'Spatial sigma-4 residual')+'; window sigma 12; reference thresholds shown separately')
            ax.legend(fontsize=7,ncol=3)
        fig.suptitle(ident+': sensitivity to an 8-pixel sideways move\nRoutes are diagnostic fixtures; no edge point selected',fontsize=12)
        fig.tight_layout(rect=(0,0,1,.94));fig.savefig(out/(ident+'-parallel.png'),dpi=135);plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,9))
    for row,path in enumerate(base['paths'][1:]):
        ident=path['id'];start=np.array(path['start']);direction=np.array(path['direction']);mid=start+64*direction
        for col in range(2):
            ax=axes[row,col];ax.imshow(im);ax.set_xlim(mid[0]-110,mid[0]+110);ax.set_ylim(mid[1]+110,mid[1]-110);ax.set_axis_off()
            ax.set_title(ident+(': raw pixels' if col==0 else ': three routes; white marks at 40 and 64 px'),fontsize=10)
            if col:
                for i,offset in enumerate(cfg['offsets_px']):
                    route=next(r for r in routes if r['id']==ident and r['offset']==offset);a=np.array(route['start']);b=a+144*direction;color=plt.get_cmap('tab10')(i)
                    ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1.2,label=f'{offset:+d} px')
                    ax.plot(*a,'o',mec=color,mfc='none',ms=4)
                for t in (40,64):
                    pt=start+t*direction;ax.plot(*pt,'+',color='white',ms=7)
                    label_offset=(10,0) if direction[1] else (5,-16 if t==40 else 8)
                    ax.annotate(str(t),pt,xytext=label_offset,textcoords='offset points',color='white',fontsize=9)
                ax.annotate('P',start,xytext=(-15,-16),textcoords='offset points',color='white');ax.legend(fontsize=8,loc='lower right')
    fig.suptitle('Small route changes expose different bead colors or highlights\nLines and white stops are sampling guides, not bead boundaries',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.94));fig.savefig(out/'review-crops.png',dpi=145);plt.close(fig)

    fig,axes=plt.subplots(2,4,figsize=(13,8));axes=axes.ravel()
    axes[0].imshow(im);axes[0].set_title('Additional reference centers');axes[0].set_axis_off()
    for ref in cfg['extra_paper']:
        x,y=ref['center'];axes[0].plot(x,y,'+',color='white');axes[0].text(x+15,y,ref['id'],color='white',fontsize=8)
    axes[1].axis('off');axes[1].text(0,.85,'C1–C4: proposed clear paper\nS1/S2: shadowed paper centers\n\nWhite circle: sigma 24 px\nFFT square extends ±144 px\n\nA paper center does not imply\na pure-paper window.\nNo maker labels assumed.',va='top')
    for ax,ref in zip(axes[2:],cfg['extra_paper']):
        x,y=ref['center'];ax.imshow(im);ax.set_xlim(x-90,x+90);ax.set_ylim(y+90,y-90);ax.add_patch(Circle((x,y),24,fill=False,color='white'));ax.plot(x,y,'+',color='white');ax.set_title(ref['id']+': '+ref['group']);ax.set_axis_off()
    fig.tight_layout();fig.savefig(out/'paper-controls.png',dpi=140);plt.close(fig)
    report=dict(config=cfg,source_sha256=digest(ROOT/'beads-photo-2.jpg'),config_sha256=digest(configpath),
                script_sha256=digest(__file__),base_sha256=digest(basepath),
                helpers={p:digest(ROOT/'photo2'/p) for p in ('background_probe.py','background_transitions.py')},
                routes=routes,references=references,candidates=candidates,summaries=summaries,
                counts=dict(texture=len(texture),hue=len(huerows),paper=len(paper),candidates=len(candidates)),
                checks=control,versions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),
                artifacts={p.name:digest(p) for p in sorted(out.iterdir()) if p.suffix in ('.png','.csv')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(counts=report['counts'],summaries=summaries,references=references),indent=2))


if __name__=='__main__':main()

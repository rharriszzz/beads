"""R132 raw evidence, constraint comparison and one neighbor-family question."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from local_surface_fit import ROOT,IDS,INDICES,polygons
from refine_surface_constraints import constraints
from check_placement import sha

COLORS=dict(zip(IDS,['cyan','lime','gold','orange','white','magenta','deepskyblue']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--question-only',action='store_true')
    args=parser.parse_args();out=ROOT/'photo2/output/r132';out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    image=ImageOps.exif_transpose(Image.open(ROOT/cfg['image']))
    xy,shape,masks=polygons(cfg);x0,y0,x1,y1=cfg['crop']
    unknown,data=constraints(xy,shape,masks,'G',[1364,278],6,3)
    fig,axes=plt.subplots(1,2,figsize=(10,5),layout='constrained')
    for ax in axes:
        ax.imshow(image);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw photo and existing observation IDs')
    axes[1].set_title('Interior constraints; G withheld\nDashed circles: diagnostic ignore radii 6 / 10 px')
    for k,poly in cfg['observations'].items():
        q=np.mean(poly,axis=0);axes[0].text(*q,k,color='white',bbox=dict(facecolor='black',alpha=.5,pad=1))
        if k!='G':
            axes[1].contourf(np.arange(x0,x1),np.arange(y0,y1),data[k]['core'],levels=[.5,1.5],colors=[COLORS[k]],alpha=.25)
            axes[1].contour(np.arange(x0,x1),np.arange(y0,y1),data[k]['core'],levels=[.5],colors=[COLORS[k]],linewidths=1)
        else:
            poly=np.array(poly);axes[1].plot(*np.vstack((poly,poly[0])).T,color='white',ls=':')
            axes[1].text(*q,'G: withheld',color='white',fontsize=8)
    for radius in [6,10]:axes[1].add_patch(Circle((1364,278),radius,fill=False,color='white',ls='--',lw=1))
    fig.savefig(out/'surface-evidence.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,5),layout='constrained')
    for ax in axes:
        ax.imshow(image);ax.set_xlim(1326,1394);ax.set_ylim(320,234)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw context')
    axes[1].set_title('B and C: which neighbor direction?\n1, 6/7, or not immediate / unclear')
    for k,point in [('B',(1360,256)),('C',(1348,280)),('E',(1382,280)),('G',(1373,303))]:
        axes[1].text(point[0]+2,point[1],k,color='white',bbox=dict(facecolor='black',alpha=.5,pad=1))
    axes[1].annotate('',xy=(1360,256),xytext=(1348,280),arrowprops=dict(arrowstyle='<->',color='cyan',lw=1.5))
    fig.savefig(out/'neighbor-question.png',dpi=180);plt.close(fig)
    if args.question_only:return
    report=json.loads((out/'report.json').read_text())
    selected=[c for c in report['cases'] if c['dataset']=='photo' and c['erosion_px']==3 and c['ignore_radius_px']==6]
    fig,axes=plt.subplots(2,3,figsize=(13,10),layout='constrained')
    for row,name in zip(axes,['H1','H2']):
        for ax in row:
            ax.imshow(image);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
            ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
        row[0].set_title(name+': raw photo (same evidence)')
        for ax,method in zip(row[1:],['masked_regions','cores']):
            case=next(c for c in selected if c['hypothesis']==name and c['method']==method)
            red=np.asarray(Image.open(out/(case['stem']+'.png')))[:,:,0]
            labels=np.full(red.shape,-999,int);yes=red>0;labels[yes]=INDICES[red[yes]-1]
            for k in IDS:
                ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==case['mapping'][k],levels=[.5],colors=[COLORS[k]],linewidths=1)
            ax.add_patch(Circle((1364,278),6,fill=False,color='white',ls='--'))
            ax.set_title(('Outline control, P region omitted' if method=='masked_regions' else 'Positive interiors only')
                +f"\nC interior {case['metrics']['C']['core_coverage']:.0%}; withheld G overlap {case['metrics']['G']['iou']:.0%}")
    fig.savefig(out/'fit-comparison.png',dpi=150);plt.close(fig)
    rows=[]
    for c in report['cases']:
        train=[k for k in IDS if k!='G'];m=c['metrics'];b=c['baseline_metrics']
        rows.append(dict(dataset=c['dataset'],hypothesis=c['hypothesis'],method=c['method'],radius=c['ignore_radius_px'],erosion=c['erosion_px'],
            training_core_coverage=float(np.mean([m[k]['core_coverage'] for k in train])),
            C_core=m['C']['core_coverage'],F_core=m['F']['core_coverage'],G_iou=m['G']['iou'],
            training_area_ratio=float(np.mean([m[k]['area_ratio'] for k in train])),
            C_iou=m['C']['iou'],C_area_ratio=m['C']['area_ratio'],
            baseline_C_core=b['C']['core_coverage'],baseline_G_iou=b['G']['iou'],
            capped_stages=sum(not s['success'] for s in c['optimizer']),ray_mismatches=c['ray_pov_mismatches']))
    summary=dict(rows=rows,question=dict(id='Q132.1',text='Are B and C immediate neighbors in direction 1, direction 6 or 7, or not immediate/unclear?',status='pending'),
        report_sha256=sha(out/'report.json'),review_code_sha256=sha(Path(__file__)),
        evaluation='Common 3px cores and 6px ignored radius for all variants; G excluded from fitting. Area/overlap comparisons use uncertain assistant polygons, not verified silhouettes.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    for r in rows:print(json.dumps(r))

if __name__=='__main__':main()

"""R135 evidence first, then independent rendered comparison."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Polygon,Rectangle
from local_surface_fit import ROOT,IDS,INDICES
from fit_boundary_arcs import arc_samples,support,losses
from refine_surface_constraints import cast
from check_placement import sha
from check_local_perspective import render as perspective_render
COLORS=dict(zip(IDS,['cyan','lime','gold','orange','white','magenta','deepskyblue']))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-only',action='store_true');ap.add_argument('--wider-context-only',action='store_true');args=ap.parse_args()
    out=ROOT/'photo2/output/r135';out.mkdir(parents=True,exist_ok=True)
    annotation=json.loads((ROOT/'photo2/boundary-arcs-r135.json').read_text())
    im=ImageOps.exif_transpose(Image.open(ROOT/annotation['source_image']))
    # R137: retain the whole photograph and raw wider crop beside the ID view.
    fig,axes=plt.subplots(1,3,figsize=(14,6),layout='constrained')
    for ax in axes:ax.imshow(im,interpolation='nearest');ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Whole photograph\nBox marks the wider crop')
    axes[0].add_patch(Rectangle((1180,130),360,390,fill=False,edgecolor='cyan',linewidth=1.5))
    for ax in axes[1:]:ax.set_xlim(1180,1540);ax.set_ylim(520,130)
    axes[1].set_title('Wider raw context\nNo added body labels')
    axes[2].set_title('Same context with B / C / G\nDots are existing interior observations')
    for k,point in [('B',(1360,256)),('C',(1348,280)),('G',(1373,303))]:
        axes[2].plot(*point,'o',color='cyan',ms=3)
        axes[2].annotate(k,xy=point,xytext=(point[0]+(45 if k!='C' else -45),point[1]+(0 if k!='G' else 18)),
            color='white',fontsize=12,ha='center',bbox=dict(facecolor='black',alpha=.7,pad=1),
            arrowprops=dict(arrowstyle='-',color='cyan',lw=.8))
    axes[2].add_patch(Rectangle((1325,235),60,72,fill=False,edgecolor='lime',linewidth=1))
    fig.savefig(out/'wider-context.png',dpi=170);plt.close(fig)
    if args.wider_context_only:return
    fig,axes=plt.subplots(1,3,figsize=(13,5),layout='constrained')
    for ax in axes:
        ax.imshow(im,interpolation='nearest');ax.set_xlim(1325,1385);ax.set_ylim(307,235)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw context: B above C\nNo highlight defines an edge')
    axes[1].set_title('Assistant boundary proposals\nSolid arc; shaded +/-3 px uncertainty')
    axes[2].set_title('Paired ownership samples\nInside: dot; outside: cross (not this bead)')
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    samples=arc_samples(annotation['arcs'],annotation['ignore_point_xy'],6,3,regions=cfg['observations'])
    for arc in annotation['arcs']:
        pts=np.array(arc['points']);color='cyan' if arc['body']=='B' else 'lime'
        for a,b in zip(pts[:-1],pts[1:]):
            v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*3
            axes[1].add_patch(Polygon([a+n,b+n,b-n,a-n],color=color,alpha=.2,linewidth=0))
        axes[1].plot(*pts.T,color=color,lw=1.5)
        axes[1].text(*pts[len(pts)//2],arc['id'],color='white',bbox=dict(facecolor='black',alpha=.7,pad=2))
    for sample in samples:
        color='cyan' if sample['body']=='B' else 'lime'
        a=np.array(sample['inside']);b=np.array(sample['outside'])
        axes[2].plot(*np.array([a,b]).T,color=color,lw=.5,alpha=.25)
        axes[2].plot(*a,'o',color=color,ms=2);axes[2].plot(*b,'x',color=color,ms=3)
    for ax in axes[1:]:ax.add_patch(Circle((1364,278),6,fill=False,color='white',ls='--'))
    fig.savefig(out/'arc-evidence.png',dpi=170);plt.close(fig)
    neighbor=json.loads((ROOT/'photo2/neighbor-review-r136.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(11,5),layout='constrained')
    points={'B':np.array([1360,256]),'C':np.array([1348,280]),'G':np.array([1373,303])}
    for ax in axes:
        ax.imshow(im,interpolation='nearest');ax.set_xlim(1325,1394);ax.set_ylim(328,236)
        ax.set_xlabel('source x');ax.set_ylabel('source y')
    axes[0].set_title('Raw context: B, C, G')
    for ax,alternative in zip(axes[1:],neighbor['coupled_family_alternatives']):
        for k,point in points.items():ax.text(*(point+[2,0]),k,color='white',bbox=dict(facecolor='black',alpha=.6,pad=1))
        for pair,color in [('BC','cyan'),('CG','gold')]:
            a,b=[points[k] for k in pair]
            ax.annotate('',xy=a,xytext=b,arrowprops=dict(arrowstyle='<->',color=color,lw=1.5))
            ax.text(*((a+b)/2+[-9,0]),str(alternative[pair])+'?',color=color,fontsize=11,bbox=dict(facecolor='black',alpha=.6,pad=1))
        ax.set_title(f"B-C family {alternative['BC']}; C-G family {alternative['CG']}\nSigns unresolved (R136)")
    fig.savefig(out/'neighbor-alternatives.png',dpi=170);plt.close(fig)
    if args.evidence_only:return
    report=json.loads((out/'report.json').read_text())
    extra=json.loads((out/'weight-report.json').read_text())
    cases=report['cases']+extra['cases']
    old=json.loads((ROOT/'photo2/review/r132/report.json').read_text())
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text());x0,y0,x1,y1=cfg['crop']
    controls={}
    fig,axes=plt.subplots(2,5,figsize=(18,9),layout='constrained')
    for row,chart in zip(axes,['H1','H2']):
      candidates=[None,next(c for c in old['cases'] if c['dataset']=='photo' and c['hypothesis']==chart and c['method']=='masked_regions'),
          next(c for c in cases if c['stem']==f'photo-{chart}-band3'),next(c for c in cases if c['stem']==f'photo-{chart}-band5'),next(c for c in cases if c['stem']==f'photo-{chart}-band3-weight3')]
      for ax,c,title in zip(row,candidates,[chart+': raw','R132 outline control','Interior + arcs, band 3','Interior + arcs, band 5','Band 3, boundary weight 3']):
        ax.imshow(im,interpolation='nearest');ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
        ax.set_xlabel('source x');ax.set_ylabel('source y')
        if c:
          if c.get('method')=='masked_regions':
            camera=c['camera']
            labels,provenance=perspective_render(c['parameters'],c['hand'],cfg['crop'],camera['focal_px'],np.array(camera['principal_xy']),out,'control-'+chart)
            controls[chart]=provenance
          else:
            red=np.array(Image.open(out/(c['stem']+'.png')))[:,:,0]
            labels=np.full(red.shape,-999,int);yes=red>0;labels[yes]=INDICES[red[yes]-1]
          for k in IDS:ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==c['mapping'][k],levels=[.5],colors=[COLORS[k]],linewidths=.9)
          m=c['metrics'];title+=f"\nC core {m['C']['core_coverage']:.0%}, C area {m['C']['area_ratio']:.2f}, G {m['G']['iou']:.0%}"
          ax.add_patch(Circle((1364,278),6,fill=False,color='white',ls='--'))
        ax.set_title(title,fontsize=10)
    fig.savefig(out/'arc-comparison.png',dpi=150);plt.close(fig)
    # Known synthetic contour supervision is diagnostic input, not photo truth.
    fig,axes=plt.subplots(1,3,figsize=(11,4.5),layout='constrained')
    red=np.array(Image.open(out/'synthetic-truth.png'))[:,:,0]
    actual=np.full(red.shape,-999,int);yes=red>0;actual[yes]=INDICES[red[yes]-1]
    ownership=np.ones((*red.shape,3))*.3
    from matplotlib.colors import to_rgb
    for k,index in report['synthetic_truth']['mapping'].items():ownership[actual==index]=to_rgb(COLORS[k])
    for ax in axes:
        ax.imshow(ownership,extent=(x0-.5,x1-.5,y1-.5,y0-.5));ax.set_xlabel('source x');ax.set_ylabel('source y')
    axes[0].set_title('Known POV ownership\nContours supplied for calibration')
    for ax,chart in zip(axes[1:],['H1','H2']):
        c=next(c for c in cases if c['stem']==f'synthetic-{chart}-band3')
        red=np.array(Image.open(out/(c['stem']+'.png')))[:,:,0]
        labels=np.full(red.shape,-999,int);yes=red>0;labels[yes]=INDICES[red[yes]-1]
        for k in IDS:ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==c['mapping'][k],levels=[.5],colors=[COLORS[k]],linewidths=1.5)
        ax.set_title(f"{chart} fitted, G {c['metrics']['G']['iou']:.0%}\n"+('Correct source chart' if chart=='H1' else 'Wrong source chart'))
    fig.savefig(out/'synthetic-arcs.png',dpi=150);plt.close(fig)
    rows=[]
    for c in cases:
      ecfg=report['synthetic_config'] if c['dataset']=='synthetic' else cfg
      points,core,pairs,_=support(ecfg,c['arcs'],halfwidth=3)
      common=losses(cast(np.array(c['parameters']),points,c,c['camera']),c['mapping'],core,pairs)
      m=c['metrics'];rows.append(dict(stem=c['stem'],core_miss=c['training']['core_miss'],bracket_miss=c['training']['bracket_miss'],
          common_python_bracket_miss=common['bracket_miss'],C_core=m['C']['core_coverage'],F_core=m['F']['core_coverage'],C_area=m['C']['area_ratio'],G_iou=m['G']['iou'],
          capped_stages=sum(not s['success'] for s in c['optimizer']),ray_mismatches=c['ray_pov_mismatches']))
    summary=dict(rows=rows,report_sha256=sha(out/'report.json'),weight_report_sha256=sha(out/'weight-report.json'),review_code_sha256=sha(ROOT/'photo2/review_boundary_arcs.py'),control_render_provenance=controls,question=annotation['question'],neighbor_review_sha256=sha(ROOT/'photo2/neighbor-review-r136.json'))
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    for row in rows:print(json.dumps(row))

if __name__=='__main__':main()

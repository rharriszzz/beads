"""Raw-context review and independent render checks for the R156 candidates."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from curved_surface_fit import trace,geometry,project,anchors
from check_curved_patch import parity,render
from check_placement import ROOT,sha

OUT=ROOT/'photo2/review/r156'
RAW=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')))


def panel(ax,crop,title,result=None,case=None,focus=None):
    x0,y0,x1,y1=crop
    ax.imshow(RAW[y0:y1,x0:x1],extent=[x0-.5,x1-.5,y1-.5,y0-.5])
    ax.set_xlim(x0,x1);ax.set_ylim(y1,y0);ax.set_title(title,fontsize=10)
    ax.set_xlabel('oriented source x');ax.set_ylabel('source y')
    if result is None:return
    p=np.array(result['parameters']);hand=case['hand'];focal=case['focal']
    yy,xx=np.mgrid[y0:y1,x0:x1];xy=np.column_stack((xx.ravel(),yy.ravel()))
    owner,_,_,_=trace(p,xy,hand,focal=focal);owner=owner.reshape(xx.shape)
    s=np.linspace(-45,35,400)
    line=geometry(p,s,hand)[3]
    line_xy=project(p,line,focal)
    ax.plot(line_xy[:,0],line_xy[:,1],':',color='white',lw=1,label='fitted centerline')
    for o in result['observations']:
        number=o['number']
        if focus is not None and number!=focus:continue
        mask=owner==o['relative_index']
        if mask.any():ax.contour(xx,yy,mask.astype(float),levels=[.5],colors=['cyan'],linewidths=.9)
        x,y=o['outward_xy']
        ax.plot(x,y,marker='D',ms=4,color='lime',mfc='lime' if o['outward_exposed'] else 'none')
        mx,my=o['point'];held=o['role']=='held-out'
        ax.plot(mx,my,'+',color='orange' if held else 'white',ms=6,mew=1)
        if focus is None:
            ax.text(mx+3,my-3,str(number),color='orange' if held else 'white',fontsize=7,
                    bbox=dict(facecolor='black',alpha=.5,pad=.3,edgecolor='none'))


def main():
    report=json.loads((OUT/'report.json').read_text())
    checks=[]
    for i,c in enumerate(report['cases']):
        if c['dataset']!='photo' or max(r['training_pass'] for r in c['retained'])<23:continue
        for j,r in enumerate(c['retained']):
            check,labels=parity(r['parameters'],c['hand'],[1180,210,1495,365],
                ROOT/'photo2/output/r156/review',f'photo-{i}-{j}',c['focal'])
            # Independent renderer's actual pixel ownership at rounded maker
            # locations, including held-out locations, is also evaluated.
            observed=[]
            for o in r['observations']:
                x,y=np.rint(o['point']).astype(int)
                observed.append(dict(number=o['number'],role=o['role'],
                    rounded_pixel=[int(x),int(y)],pov_owner=int(labels[y-210,x-1180]),
                    expected=o['relative_index'],pov_pass=bool(labels[y-210,x-1180]==o['relative_index'])))
            check['rounded_point_checks']=observed
            check.update(case=i,retained=j)
            checks.append(check)
    # Two wrong-handed synthetic inverse solutions share ordinary point evidence.
    for i,c in enumerate(report['cases']):
        if c['dataset']=='synthetic' and max(r['training_pass'] for r in c['retained'])==23:
            r=c['retained'][0]
            check,_=parity(r['parameters'],c['hand'],[1170,200,1510,385],
                ROOT/'photo2/output/r156/review',f'synthetic-{i}',c['focal'])
            check.update(case=i,retained=0);checks.append(check)
    cases=[c for c in report['cases'] if c['dataset']=='photo' and c['focal'] is None and c.get('q_fixed') is None and c['family'] in ['A','B'] and c['hand']==(1 if c['family']=='A' else -1)]
    # Selection is training rank only. Show A's additional distinct retained fit
    # explicitly: its held-out success is evidence, not a selection criterion.
    a,b=cases
    exact=[]
    # Rounded maker coordinates can cross a boundary. Independently put the
    # single POV pixel's center on each exact fractional observation instead.
    for name,c,r in [('A3',a,a['retained'][2]),('B1',b,b['retained'][0])]:
        pointchecks=[]
        for o in r['observations']:
            x,y=o['point']
            labels,provenance=render(r['parameters'],c['hand'],[x,y,x+1,y+1],
                ROOT/'photo2/output/r156/exact-points',f'{name}-{o["number"]}',c['focal'])
            pointchecks.append(dict(number=o['number'],point=o['point'],expected=o['relative_index'],
                owner=int(labels[0,0]),passed=bool(labels[0,0]==o['relative_index']),**provenance))
        exact.append(dict(candidate=name,points=pointchecks))
    (OUT/'fit-parity.json').write_text(json.dumps(dict(cases=checks,exact_fractional_points=exact,
        kernel_sha256=sha(ROOT/'photo2/curved_surface_fit.py'),
        checker_sha256=sha(ROOT/'photo2/check_curved_patch.py')),indent=2)+'\n')
    choices=[('A1',a,a['retained'][0]),('A2',a,a['retained'][1]),('B1',b,b['retained'][0])]
    crop=[1180,130,1540,520]
    fig,axs=plt.subplots(1,4,figsize=(16,6.2),constrained_layout=True)
    panel(axs[0],crop,'Raw wider context')
    for ax,(name,c,r) in zip(axs[1:],choices):
        panel(ax,crop,f'{name}: training {r["training_pass"]}/23; held-out {r["heldout_pass"]}/4',r,c)
    fig.suptitle('Proposals only: cyan body extent; green minor-outward point; orange withheld maker mark.\nCenterline is fitted; highlights are not measured outward anchors.',fontsize=11)
    fig.savefig(OUT/'wider-comparison.png',dpi=150);plt.close(fig)
    crop=[1250,265,1310,325];focus=11
    fig,axs=plt.subplots(1,4,figsize=(13,4),constrained_layout=True)
    panel(axs[0],crop,'Raw: maker bead 11')
    for ax,(name,c,r) in zip(axs[1:],choices):
        panel(ax,crop,name+' proposed bead 11',r,c,focus)
    fig.suptitle('Q156.1: which cyan outlines cross into paper or another bead?\nWhite + = maker mark; green diamond = predicted exposed outward point, not a measured highlight.',fontsize=11)
    fig.savefig(OUT/'q156-1.png',dpi=180);plt.close(fig)
    # Show the particular held-out failure without hiding passing alternatives.
    crop=[1350,270,1430,345];focus=25
    fig,axs=plt.subplots(1,4,figsize=(13,4),constrained_layout=True)
    panel(axs[0],crop,'Raw: withheld bead 25')
    for ax,(name,c,r) in zip(axs[1:],choices):panel(ax,crop,name+' proposed bead 25',r,c,focus)
    fig.suptitle('A1 misses bead 25; A2 and B1 pass. This does not reject family A.',fontsize=11)
    fig.savefig(OUT/'heldout-25.png',dpi=180);plt.close(fig)
    (OUT/'review-provenance.json').write_text(json.dumps(dict(
        reviewer_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),
        source_image_sha256=sha(ROOT/'beads-photo-2.jpg'),
        wider_crop=[1180,130,1540,520],question_crop=[1250,265,1310,325],question_number=11,
        choices=[dict(label=n,family=c['family'],hand=c['hand'],start_rank=r['start_rank']) for n,c,r in choices]),indent=2)+'\n')
    print(json.dumps(dict(parity_checks=len(checks),max_mismatch_fraction=max(c['mismatch_fraction'] for c in checks),
                         files=['wider-comparison.png','q156-1.png','heldout-25.png']),indent=2))


if __name__=='__main__':main()

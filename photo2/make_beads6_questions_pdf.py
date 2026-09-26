#!/usr/bin/env python3
"""Build the short R088 question PDF from frozen R087 image/path evidence."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'font.size':11})
INK='#203342'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(fig,x,y,value,size=12,bold=False,color=INK):
    return fig.text(x/8.5,y/11,value,fontsize=size,fontweight='bold' if bold else 'normal',
                    color=color,va='top',linespacing=1.45)


def base(page,title):
    fig=plt.figure(figsize=(8.5,11),facecolor='white')
    text(fig,.5,10.5,title,19,True)
    text(fig,.5,.43,'Beads6 • two pending questions • 25 September 2026',9)
    text(fig,7.55,.43,f'{page} / 3',9)
    return fig


def picture(fig,rgb,path,rect,marked=True,box=None):
    ends=np.array(path['ends'])
    center=ends.mean(axis=0)
    if box is None:
        box=[center[0]-20,center[1]-20,center[0]+20,center[1]+20]
    ax=fig.add_axes([rect[0]/8.5,rect[1]/11,rect[2]/8.5,rect[3]/11])
    ax.imshow(rgb,interpolation='nearest')
    ax.set(xlim=(box[0],box[2]),ylim=(box[3],box[1]))
    ax.axis('off')
    if marked:
        ax.plot(*ends.T,color='#ffed47',lw=1)
        for point,label,color,marker in zip(ends,['P','Q'],['#00e5ef','#ffb329'],['o','s']):
            ax.plot(*point,marker,ms=8,mfc='none',mec=color,mew=1.5)
            ax.annotate(label,point,xytext=(5,-13),textcoords='offset points',color=color,
                        weight='bold',fontsize=12,bbox=dict(facecolor='black',alpha=.7,pad=1,edgecolor='none'))
    return ax


def strip(fig,samples,path_id,rect):
    rows=samples[path_id]
    colors=np.array([[float(r[c]) for c in ['red','green','blue']] for r in rows])/255
    ax=fig.add_axes([rect[0]/8.5,rect[1]/11,rect[2]/8.5,rect[3]/11])
    ax.imshow(colors[None,:,:],aspect='auto',interpolation='nearest')
    ax.set_xticks([]);ax.set_yticks([])
    for spine in ax.spines.values():spine.set_color('#8a969e')


def save_page(pdf,fig):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    extent=fig.get_window_extent()
    for item in fig.texts:
        box=item.get_window_extent(renderer)
        assert box.x0>=0 and box.y0>=0 and box.x1<=extent.width and box.y1<=extent.height,item.get_text()
    pdf.savefig(fig);plt.close(fig)


def question(pdf,number,rgb,path,samples):
    title='Across the blue stripe' if number==1 else 'The neighboring blue areas'
    fig=base(number,f'Question {number} · {title}')
    text(fig,.5,9.99,'Look at the pictures first. A short answer is enough; “cannot tell” is useful.',11.5)
    text(fig,.5,9.55,'Do P and Q appear to be on two different beads?',15,True)
    text(fig,.64,9.08,'Unmarked image',12,True)
    text(fig,4.48,9.08,'Same image, with P and Q',12,True)
    picture(fig,rgb,path,[.5,5.6,3.6,3.3],False)
    picture(fig,rgb,path,[4.4,5.6,3.6,3.3],True)
    text(fig,.5,5.42,'P = blue circle. Q = orange square. The yellow line joins the two marks.',11)
    text(fig,.5,5.14,'It shows where I read the colors; it is not a proposed bead outline.',11)
    if number==1:
        reason='I put P beside the bright spot on the left, and Q on the blue area\nto the right of the dark stripe. I may be misreading either area.'
        lesson='Travelling from P to Q, the blue gets darker and then lighter.\nThat could be a gap between beads, but shading could do this too.'
    else:
        reason='I put P below the central bright spot, and Q below the bright spot\nto its right. I want to check whether those are two separate beads.'
        lesson='Again, the blue darkens and then brightens along the line.\nThis supports looking for a boundary, but does not prove one.'
    text(fig,.5,4.68,reason,12)
    text(fig,.5,3.88,'Colors encountered along the line, from P → Q',11,True)
    strip(fig,samples,path['id'],[.5,3.36,7.5,.29])
    text(fig,.5,3.18,lesson,12)
    fig.patches.append(Rectangle((.5/8.5,1.39/11),7.5/8.5,1.13/11,transform=fig.transFigure,
                                 facecolor='#eef3f6',edgecolor='none',zorder=-1))
    text(fig,.7,2.32,'Your answer (choose one)',12,True)
    for x,label in [( .73,'Two beads'),(3.05,'One bead'),(5.38,'Cannot tell')]:
        fig.patches.append(Rectangle((x/8.5,1.69/11),.16/8.5,.16/11,transform=fig.transFigure,
                                     facecolor='none',edgecolor=INK,lw=.8))
        text(fig,x+.27,1.9,label,12)
    text(fig,.5,1.14,'Optional: if a mark is badly placed, say “move P left,” for example.\nNo coordinates, bead counts, or decisions about tiny fragments are needed.',11)
    save_page(pdf,fig)


def supporting(pdf,rgb,paths,samples):
    fig=base(3,'Supporting examples · What can mislead us')
    text(fig,.5,9.99,'These explain the uncertainty. There are no extra questions on this page.',11.5)
    text(fig,.5,9.47,'A bright spot can change color within one bead',14,True)
    picture(fig,rgb,paths['H'],[.5,6.35,3.05,2.9])
    text(fig,3.83,9.02,'This looks like one red bead.\nThe line goes through its highlight.\n\nThe sampled colors go from red\nto almost white and back to red.\n\nLesson: a strong color change\ndoes not by itself mark a boundary.',12)
    text(fig,.5,6.2,'Along this line: red → white highlight → red',11,True)
    strip(fig,samples,'H',[.5,5.69,7.5,.28])
    text(fig,.5,5.16,'A badly placed starting point can mislead',14,True)
    picture(fig,rgb,paths['K'],[.5,2.04,3.05,2.9])
    text(fig,3.83,4.68,'This was my first attempt near\nQuestion 2. P was too close to\nthe shadow stripe being tested.\n\nThe darkest part comes almost\nimmediately after P. I rejected\nthis placement; Question 2 uses\nthe revised pair of points.',12)
    text(fig,.5,1.88,'Along the rejected line: the dark stripe is near the start',11,True)
    strip(fig,samples,'K',[.5,1.39,7.5,.28])
    text(fig,.5,1.11,'Only the wording and presentation have changed. These remain visual\nhypotheses; no bead boundaries or inventory entries have been changed.',10.5)
    save_page(pdf,fig)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    cfgpath=ROOT/'photo2/beads6-sv-paths-r087.json'
    cfg=json.loads(cfgpath.read_text());paths={p['id']:p for p in cfg['paths']}
    report=json.loads((ROOT/'photo2/review/r087/report.json').read_text())
    rgbpath=ROOT/cfg['image'];csvpath=ROOT/'photo2/review/r087/profiles.csv'
    assert sha(rgbpath)==report['sources'][cfg['image']]
    assert sha(cfgpath)==report['sources']['photo2/beads6-sv-paths-r087.json']
    assert sha(csvpath)==report['artifacts']['profiles.csv']
    samples={key:[] for key in ['A','B','H','K']}
    with csvpath.open() as f:
        for r in csv.DictReader(f):
            if r['path'] in samples and float(r['sigma_px'])==0 and float(r['offset_px'])==0:
                samples[r['path']].append(r)
    rgb=np.asarray(Image.open(rgbpath).convert('RGB'))
    pdfpath=args.output/'beads6-questions.pdf'
    date=datetime(2026,9,25,tzinfo=timezone.utc)
    with PdfPages(pdfpath,metadata={'Title':'Beads6: two illustrated questions',
                  'Author':'Beads reconstruction project','Subject':'Simplified R087 questions and supporting examples (R088)',
                  'CreationDate':date,'ModDate':date}) as pdf:
        for number,key in enumerate(['A','B'],1):question(pdf,number,rgb,paths[key],samples)
        supporting(pdf,rgb,paths,samples)
    sources=['beads6.jpg','photo2/beads6-sv-paths-r087.json','photo2/review/r087/profiles.csv',
             'photo2/review/r087/report.json','photo2/make_beads6_questions_pdf.py']
    manifest=dict(command=[sys.executable,*sys.argv],sources={p:sha(ROOT/p) for p in sources},
                  artifacts={pdfpath.name:sha(pdfpath)},page_count=3,
                  parameters={'paper':'US Letter, portrait','question_paths':['A','B'],'support_paths':['H','K'],
                              'rgb':'Unmodified beads6.jpg pixels; nearest-neighbor display',
                              'strips':'Saved R087 raw sigma=0, offset=0 samples in original order',
                              'crops':'40x40 source pixels centered at path endpoint midpoint',
                              'pdf_metadata_date':'2026-09-25T00:00:00Z'},
                  environment={'python':sys.version,'matplotlib':matplotlib.__version__,'numpy':np.__version__})
    (args.output/'report.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(pdfpath)


if __name__=='__main__':main()

"""Print the same canonical strip used by the interactive graph-paper view."""
from common import *
from graph_paper import X_SCALE,Y_SCALE,RX,RY
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='beads-r344-graph-paper'
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Polygon
from matplotlib.backends.backend_pdf import PdfPages

PALETTE={'red':'#d43b42','yellow':'#dfb915','black':'#252a31','?':'#eceff1'}


def draw_axis(ax,paper,kind,indices=False):
    points=paper['points'];lo,hi=paper['rows'];left,right=paper['x0']-1,paper['x0']+13
    xmin=min(r['x'] for r in points)-1;xmax=max(r['x'] for r in points)+1
    ax.add_patch(Rectangle((xmin*X_SCALE,(lo-.65)*Y_SCALE),(xmax-xmin)*X_SCALE,(hi-lo+1.3)*Y_SCALE,facecolor='#f2f4f6',edgecolor='none',zorder=0))
    interval=np.array([[paper['x0']-.5 if x==left else paper['x0']+12.5 if x==right else x,y] for x,y in paper['start_boundary']+list(reversed(paper['end_boundary']))])*[X_SCALE,Y_SCALE]
    ax.add_patch(Polygon(interval,facecolor='white',edgecolor='none',zorder=.5))
    for y in np.arange(lo-.5,hi+1,.5):ax.axhline(y*Y_SCALE,color='#e4e8ec',lw=.35,zorder=1)
    for x in range(xmin,xmax+1):ax.axvline(x*X_SCALE,color='#e4e8ec',lw=.35,zorder=1)
    for x in [paper['x0']-.5,paper['x0']+12.5]:ax.axvline(x*X_SCALE,color='#929ca5',lw=.5,ls=(0,(3,3)),zorder=2)
    for r in points:
        color=r[kind+'_color'];ax.add_patch(Ellipse((r['x']*X_SCALE,r['y']*Y_SCALE),2*RX,2*RY,facecolor=PALETTE[color],edgecolor='#246aab' if kind=='provisional' and r['tentative'] else '#67727b',linewidth=.8 if kind=='provisional' and r['tentative'] else .35,linestyle='--' if kind=='provisional' and r['tentative'] else '-',zorder=3))
        if color=='?':ax.text(r['x']*X_SCALE,r['y']*Y_SCALE,'?',fontsize=6,ha='center',va='center',zorder=4)
        elif indices:ax.text(r['x']*X_SCALE,r['y']*Y_SCALE,str(r['position']),fontsize=3.4,color='white' if color in ['red','black'] else '#151515',ha='center',va='center',zorder=4)
    for name,color,label in [('start_boundary','#006879',f"START · before {paper['start']}"),('end_boundary','#873c80',f"END · after {paper['start']+paper['length']-1}")]:
        xy=np.array(paper[name])*[X_SCALE,Y_SCALE];ax.plot(xy[:,0],xy[:,1],color=color,lw=.8,zorder=5)
        ax.text((xmax+.4)*X_SCALE,xy[-1,1],label,fontsize=5,color=color,ha='left',va='center',zorder=6)
    ax.set(xlim=((xmin-.5)*X_SCALE,(xmax+5.8)*X_SCALE),ylim=((lo-1)*Y_SCALE,(hi+1)*Y_SCALE),aspect='equal')
    ax.axis('off')


def main():
    paper=read(OUT/'graph-paper-layout.json')
    pattern=read(OUT/'pattern208.json');unknown=pattern['length']-pattern['supported']
    assert read(OUT/'graph-paper-verification.json')['passed']
    for indices,stem in [(False,'graph-paper'),(True,'graph-paper-numbered')]:
        fig,axes=plt.subplots(1,2,figsize=(16.54,11.69))
        for ax,kind,title in zip(axes,['strict','provisional'],[f"Strict · {pattern['supported']} colors, {unknown} unknown",f"Provisional · {unknown} tentative colors"]):
            draw_axis(ax,paper,kind,indices);ax.set_title(title,fontsize=9)
        fig.suptitle(f"6.5-bead graph paper · conditional {paper['length']}-position block",fontsize=11,y=.985)
        fig.text(.5,.956,'Every row: 7 left + 6 or 7 basic + 7 right. String +1 right; +6 up-left; +7 up-right.',ha='center',fontsize=8)
        fig.text(.5,.025,f"The thin lines enclose one block: {paper['start']}–{paper['start']+paper['length']-1}, once each. Periodic continuation before and after.",ha='center',fontsize=7)
        fig.text(.5,.01,'All ellipses have the same shape. Gray ? = strict unknown. Dashed blue = provisional. Display copies are not observations.',ha='center',fontsize=6.5)
        fig.subplots_adjust(top=.935,bottom=.05,left=.015,right=.99,wspace=.04)
        fig.savefig(OUT/(stem+'.png'),dpi=300)
        fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None})
        plt.close(fig)
        # Two readable A4 portrait pages, one color interpretation per page.
        with PdfPages(OUT/(stem+'.pdf'),metadata={'CreationDate':None,'ModDate':None}) as pdf:
            for kind in ['strict','provisional']:
                page,ax=plt.subplots(figsize=(8.27,11.69));draw_axis(ax,paper,kind,indices)
                page.suptitle(f"{kind.title()} · {paper['length']} positions · 7 extra beads on EACH side",fontsize=10,y=.985)
                page.text(.5,.954,'Dotted seams mark the basic strip; colored cuts mark the chosen repeat.',ha='center',fontsize=7)
                page.text(.5,.025,'Gray surroundings are display continuation, not additional observations.',ha='center',fontsize=7)
                page.text(.5,.01,'Indices, when shown, are pattern positions. Identical positions always retain identical colors.',ha='center',fontsize=6.5)
                page.subplots_adjust(top=.93,bottom=.05,left=.015,right=.99);pdf.savefig(page);plt.close(page)
        svg=OUT/(stem+'.svg');svg.write_text('\n'.join(s.rstrip() for s in svg.read_text().splitlines())+'\n')
    print('PRINT graph paper: two-page A4 PDFs, comparison SVGs and 4962x3507 PNGs; seven on BOTH sides')


if __name__=='__main__':
    main()

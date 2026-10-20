"""Print the same canonical strip used by the interactive graph-paper view."""
from common import *
from graph_paper import X_SCALE,Y_SCALE,RX,RY
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='beads-r344-graph-paper'
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Polygon

PALETTE={'red':'#d43b42','yellow':'#dfb915','black':'#252a31','?':'#eceff1'}


def draw_axis(ax,paper,kind,indices=False):
    points=[r for r in paper['points'] if r['lateral_copy']==0];lo,hi=paper['rows'];left,right=paper['x0']-1,paper['x0']+13
    ax.add_patch(Rectangle((left*X_SCALE,(lo-.65)*Y_SCALE),(right-left)*X_SCALE,(hi-lo+1.3)*Y_SCALE,facecolor='#f2f4f6',edgecolor='none',zorder=0))
    interval=np.array(paper['start_boundary']+list(reversed(paper['end_boundary'])))*[X_SCALE,Y_SCALE]
    ax.add_patch(Polygon(interval,facecolor='white',edgecolor='none',zorder=.5))
    for y in np.arange(lo-.5,hi+1,.5):ax.axhline(y*Y_SCALE,color='#e4e8ec',lw=.35,zorder=1)
    for x in range(left,right+1):ax.axvline(x*X_SCALE,color='#e4e8ec',lw=.35,zorder=1)
    for r in points:
        color=r[kind+'_color'];ax.add_patch(Ellipse((r['x']*X_SCALE,r['y']*Y_SCALE),2*RX,2*RY,facecolor=PALETTE[color],edgecolor='#246aab' if kind=='provisional' and r['tentative'] else '#67727b',linewidth=.8 if kind=='provisional' and r['tentative'] else .35,linestyle='--' if kind=='provisional' and r['tentative'] else '-',zorder=3))
        if color=='?':ax.text(r['x']*X_SCALE,r['y']*Y_SCALE,'?',fontsize=6,ha='center',va='center',zorder=4)
        elif indices:ax.text(r['x']*X_SCALE,r['y']*Y_SCALE,str(r['position']),fontsize=3.4,color='white' if color in ['red','black'] else '#151515',ha='center',va='center',zorder=4)
    for name,color,label in [('start_boundary','#006879',f"START · before {paper['start']}"),('end_boundary','#873c80',f"END · after {paper['start']+paper['length']-1}")]:
        xy=np.array(paper[name])*[X_SCALE,Y_SCALE];ax.plot(xy[:,0],xy[:,1],color=color,lw=.8,zorder=5)
        ax.text((right+.4)*X_SCALE,xy[-1,1],label,fontsize=5,color=color,ha='left',va='center',zorder=6)
    ax.set(xlim=((left-.5)*X_SCALE,(right+5.8)*X_SCALE),ylim=((lo-1)*Y_SCALE,(hi+1)*Y_SCALE),aspect='equal')
    ax.axis('off')


def main():
    paper=read(OUT/'graph-paper-layout.json')
    pattern=read(OUT/'pattern208.json');unknown=pattern['length']-pattern['supported']
    assert read(OUT/'graph-paper-verification.json')['passed']
    for indices,stem in [(False,'graph-paper'),(True,'graph-paper-numbered')]:
        fig,axes=plt.subplots(1,2,figsize=(8.27,11.69))
        for ax,kind,title in zip(axes,['strict','provisional'],[f"Strict · {pattern['supported']} colors, {unknown} unknown",f"Provisional · {unknown} tentative colors"]):
            draw_axis(ax,paper,kind,indices);ax.set_title(title,fontsize=9)
        fig.suptitle(f"6.5-bead graph paper · conditional {paper['length']}-position block",fontsize=11,y=.985)
        fig.text(.5,.956,'6 / 7 beads per row. String +1 right; +6 up-left; +7 up-right.',ha='center',fontsize=8)
        fig.text(.5,.025,f"The thin lines enclose one block: {paper['start']}–{paper['start']+paper['length']-1}, once each. Periodic continuation before and after.",ha='center',fontsize=7)
        fig.text(.5,.01,'All ellipses have the same shape. Gray ? = strict unknown. Dashed blue = provisional. Display copies are not observations.',ha='center',fontsize=6.5)
        fig.subplots_adjust(top=.935,bottom=.05,left=.015,right=.99,wspace=.04)
        fig.savefig(OUT/(stem+'.png'),dpi=300)
        fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None})
        fig.savefig(OUT/(stem+'.pdf'),metadata={'CreationDate':None,'ModDate':None})
        plt.close(fig)
        svg=OUT/(stem+'.svg');svg.write_text('\n'.join(s.rstrip() for s in svg.read_text().splitlines())+'\n')
    print('PRINT graph paper: two A4 vector PDFs/SVGs and 2481x3507 PNGs')


if __name__=='__main__':
    main()

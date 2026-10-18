"""Small static review: native photograph, vectors, supported segments and matrices."""
import csv,html
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from .common import *


def main():
    summary=read(OUT/'summary.json');base=read(OUT/'baseline.json.gz');best=read(OUT/'best-full.json.gz');small=read(OUT/'best-small.json.gz');epoch=read(OLD/'epoch2/epoch.json');ev=read(OUT/'evidence-policy.json');origin=np.array(ev['origin']);h,w=ev['shape'];x,y=origin;photo=np.array(Image.open(ROOT/'beads-photo-2.jpg'));crop=photo[y:y+h,x:x+w];Image.fromarray(crop).save(OUT/'raw-photo.png');extent=[x-.5,x+w-.5,y+h-.5,y-.5]
    models=[('baseline',base),('best-full',best),('best-small',small)]
    for boundaries in [False,True]:
        fig,axes=plt.subplots(3,1,figsize=(13,13),constrained_layout=True)
        for ax,(name,r) in zip(axes,models):
            ax.imshow(crop,extent=extent);a=np.load(OUT/(name+'-visible.npz'));m=read(OUT/(name+'-geometry.json'));owner=a['owner'];unknown=a['unknown'];bd=a['boundary'];pos=read(OUT/(name+'-positions.json.gz'));idx=np.array(pos['indices'])
            if boundaries:
                yy,xx=np.where(bd);ax.scatter(xx+x,yy+y,s=.3,c='#28d8ff',alpha=.8,label='predicted visible boundary')
                for z in m['seams']:
                    ax.plot(*z['xy'],'.',color='#ffe660',ms=2)
                for b in m['brackets']:ax.plot([b['material'][0],b['paper'][0]],[b['material'][1],b['paper'][1]],color='#ffe660',lw=1.4)
                oldmaps=np.load(ROOT/'photo2/r314/evidence/maps.npz');mx,my=origin-oldmaps['origin'];cores=oldmaps['core'][my:my+h,mx:mx+w];red=np.zeros_like(bd)
                for z in ev['cores']:red|=bd&ndi.binary_erosion(cores==z['label'],iterations=2)
                yy,xx=np.where(red);ax.scatter(xx+x,yy+y,s=4,c='#ff4164',label='boundary crosses pigment core')
            for row in r['rows']:
                o=np.array(row['observed']);p=np.array(row['predicted']);color='#ff4e4e' if row['error_px']>=r['emax_px']-.01 else '#39ffe0';ax.plot(*o,'o',ms=3,mfc='white',mec='black',mew=.4);ax.annotate('',xy=p,xytext=o,arrowprops=dict(arrowstyle='->',color=color,lw=1.2));ax.text(o[0]+1,o[1]-2,str(row['index']),fontsize=7,color='white',bbox=dict(facecolor='black',alpha=.45,pad=.3,edgecolor='none'))
            ax.set_title(f'{name}: Emax {r["emax_px"]:.3f}px; conditional indices; white observed → arrow predicted',fontsize=11);ax.set_xlim(extent[:2]);ax.set_ylim(extent[2:]);ax.set_xlabel('original photo x (px)');ax.set_ylabel('original photo y (px)')
        fig.suptitle('Cyan: actual visible boundaries; yellow: supported photo segments/brackets; red: core crossings' if boundaries else 'Reflection vectors only — unmeasured beads remain unknown',fontsize=11);fig.savefig(OUT/('geometry-overlay.png' if boundaries else 'reflection-vectors.png'),dpi=140);plt.close(fig)
    # Compact full 163-variable response heatmap. Row groups and exact CSV retain all values.
    a=read(OUT/'bilateral-sensitivity.json.gz');mat=[];labels=[]
    for r in a['records']:
        field=r.get('1.0',r.get('0.25'))
        if field is None:col=np.zeros((22,2))
        else:col=np.array(field['central'])
        mat.append(np.linalg.norm(col,axis=1));labels.append(str(r['key']))
    mat=np.array(mat).T;fig,ax=plt.subplots(figsize=(18,6),constrained_layout=True);im=ax.imshow(mat,aspect='auto',cmap='magma',vmin=0,vmax=np.percentile(mat,99));ax.set_yticks(range(22),[str(r['index']) for r in base['rows']]);ax.set_ylabel('conditional index');ticks=list(range(0,len(labels),5));ax.set_xticks(ticks,[labels[i] for i in ticks],rotation=80,fontsize=6);ax.set_title('All163 scaled bilateral responses (px per declared scale); zeros may mean local insensitivity');fig.colorbar(im,ax=ax,label='predicted reflection movement (px)');fig.savefig(OUT/'sensitivity.png',dpi=130);plt.close(fig)
    x=read(OUT/'wide-secant-minimax.json.gz');hg=read(OUT/'half-grid-minimax.json.gz');fig,axes=plt.subplots(1,2,figsize=(13,4),constrained_layout=True)
    for d,n in [(x,'native full-scale secants'),(hg,'half-pixel secants')]:axes[0].semilogy(d['singular_values'],'o-',ms=3,label=n)
    axes[0].set(xlabel='singular direction',ylabel='scaled singular value',title='Conditioning depends on measured derivative model');axes[0].legend(fontsize=8)
    states=[(0,base['emax_px'],max(base['rows'],key=lambda r:r['error_px'])['index'])]
    for z in read(OUT/'accepted-history.json'):
        r=read(OUT/'trials'/f'{z["selected"]:05}.json.gz');states.append((r['id'],r['emax_px'],max(r['rows'],key=lambda r:r['error_px'])['index']))
    axes[1].plot(range(len(states)),[s[1] for s in states],'o-')
    for i,(_,error,index) in enumerate(states):axes[1].annotate(str(index),(i,error),xytext=(0,6),textcoords='offset points',fontsize=8)
    axes[1].set(xlabel='accepted continuation state (baseline then four)',ylabel='Emax (px)',title='Worst conditional index annotated');fig.savefig(OUT/'conditioning-progress.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(11,7),constrained_layout=True);order=np.argsort([r['index'] for r in base['rows']]);inds=np.array([r['index'] for r in base['rows']])
    for name,r in models:axes[0].plot(inds[order],np.array([z['error_px'] for z in r['rows']])[order],'o-',label=name,ms=4)
    axes[0].axhline(10,c='black',ls='--',lw=.8,label='10px diagnostic');axes[0].legend(fontsize=8);axes[0].set(xlabel='conditional physical index',ylabel='reflection error (px)',title='All22 observations retained; gaps are unmeasured')
    for tid in [709,728,1010,1013]:
        r=read(OUT/'trials'/f'{tid:05}.json.gz');parent=read(OUT/'trials'/f'{r["meta"]["parent"]:05}.json.gz');p=np.array([z['error_px'] for z in parent['rows']]);pred=np.array(r['meta']['predicted_errors']);actual=np.array([z['error_px'] for z in r['rows']]);axes[1].scatter(p-pred,p-actual,label=f'trial{tid}'+(' accepted' if r['acceptance']['passed'] else ' rejected'),s=20)
    lim=axes[1].get_xlim();axes[1].plot(lim,lim,'k--',lw=.8);axes[1].set(xlabel='predicted error reduction (px)',ylabel='actual error reduction (px)',title='Every bead in representative coordinated steps; positive improves');axes[1].legend(fontsize=8);fig.savefig(OUT/'errors-and-predictions.png',dpi=150);plt.close(fig)
    steps=read(OUT/'step-comparison.json');lines=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R319 search-space diagnosis</title><style>body{max-width:1200px;margin:auto;padding:20px;font:16px system-ui;background:#fafafa;color:#222}img{width:100%;height:auto}table{border-collapse:collapse;font-size:13px}td,th{padding:5px;border-bottom:1px solid #ddd}section{overflow-x:auto}a{color:#135b9d}details{margin:16px 0}</style><h1>R319: why the reflection fit stalls</h1>',f'<p>All22: {base["emax_px"]:.3f} → {best["emax_px"]:.3f}px with geometry non-regression. No excellent reconstruction, no adoption. Small interval27–46: {summary["small_best_max"]:.3f}px on seven observations. Physical identities remain provisional.</p>','<p><a href="../../R319_REPORT.md">Report</a> · <a href="parameter-ranges.md">Actual R318 parameter ranges</a> · <a href="all-reflection-responses.csv">Every reflection response</a> · <a href="trial-ledger.csv">Every candidate outcome</a> · <a href="verification.json">Independent verification</a> · <a href="raw-photo.png">Unannotated original pixels</a></p>']
    for name,title in [('reflection-vectors.png','Reflection vectors only'),('geometry-overlay.png','Visible geometry and independently supported photo evidence'),('sensitivity.png','Parameter response matrix'),('conditioning-progress.png','Conditioning and accepted progress'),('errors-and-predictions.png','Individual errors and prediction accuracy')]:lines += [f'<details open><summary>{title}</summary><img src="{name}" alt="{title}"></details>']
    lines+=['<h2>Coordinated-step ledger</h2><section><table><tr><th>Trial</th><th>Model</th><th>Predicted max</th><th>Actual max</th><th>Outcome</th></tr>']
    for r in steps:lines.append(f'<tr><td>{r["trial"]}</td><td>{html.escape(r["stage"])}</td><td>{r["predicted_max"]:.3f}</td><td>{str(round(r["actual_max"],3)) if r["actual_max"] is not None else "unavailable"}</td><td>{html.escape(r["reason"] or "; ".join((r["acceptance"] or {}).get("failures",[])) or r["classification"])}</td></tr>')
    lines+=['</table></section><p>Static/offline review. No hidden model selection, color pattern, complete black outlines or inferred physical identity.</p></html>'];(OUT/'index.html').write_text('\n'.join(lines))
if __name__=='__main__':main()

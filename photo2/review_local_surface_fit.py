"""Curate local-fit review, independent final silhouettes and unresolved edges."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from local_surface_fit import ROOT,IDS,INDICES,RADIUS,polygons,trace,outward,centers,frame
from check_local_surface_fit import render
from check_placement import sha
from neighbor_coordinates import resolve_local

OUT=ROOT/'photo2/output/r126'
COLORS=dict(zip(IDS,['cyan','lime','gold','orange','white','magenta','deepskyblue']))


def measure(labels,masks,mapping,band):
    rows={}
    for k in IDS:
        pred=labels==mapping[k];obs=masks[k]
        di=distance_transform_edt(obs);do=distance_transform_edt(~obs)
        intersection=int((pred&obs).sum());union=int((pred|obs).sum())
        loss=float((np.maximum(di-band,0)*(~pred)+np.maximum(do-band,0)*pred).sum()/obs.sum())
        rows[k]=dict(iou=intersection/union,region_loss=loss,
            predicted_area=int(pred.sum()),observed_area=int(obs.sum()),
            core_coverage=float((pred&(di>band)).sum()/max(1,(di>band).sum())))
    return rows


def best_by_chart(fits):
    return [min((f for f in fits if f['hypothesis']==name),key=lambda f:f['region_loss']) for name in ['H1','H2']]


def main():
    cfg=json.loads((ROOT/'photo2/local-fit-r126.json').read_text())
    photo=best_by_chart(json.loads((OUT/'final/fits.json').read_text()))
    synth=best_by_chart(json.loads((OUT/'synthetic/final/fits.json').read_text()))
    xy,shape,masks=polygons(cfg);x0,y0,x1,y1=cfg['crop']
    image=ImageOps.exif_transpose(Image.open(ROOT/cfg['image']))
    results=[];labelmaps=[]
    for f in photo:
        p=np.array(f['parameters']);name=f['hypothesis']
        labels,provenance=render(p,f['hand'],cfg['crop'],OUT/'final',name+'-final')
        approx,_,unfinished=trace(p,xy,f['hand'])
        mismatch=int((approx.reshape(shape)!=labels).sum())
        assert mismatch/labels.size<.001,(name,mismatch)
        metrics=measure(labels,masks,f['mapping'],cfg['boundary_uncertainty_px'])
        train=[k for k in IDS if k!=cfg['held_out']]
        sensitivity={str(b):float(np.mean([v['region_loss'] for k,v in measure(labels,masks,f['mapping'],b).items() if k in train])) for b in [2,3,4]}
        edges=[(u,v,f['mapping'][v]-f['mapping'][u]) for j,u in enumerate(IDS) for v in IDS[j+1:]
               if abs(f['mapping'][v]-f['mapping'][u]) in [1,6,7]]
        chart=resolve_local(IDS,edges,'C')
        assert not chart['conflicts'] and not chart['distinct_observation_index_collisions']
        assert chart['derived_component_indices']==f['mapping']
        anchors=outward(p,[f['mapping'][k] for k in IDS],f['hand'])
        owners,depths,_=trace(p,anchors,f['hand'])
        targets=centers(p,[f['mapping'][k] for k in IDS],f['hand'])
        targets[:,1:]*=(4+RADIUS)/4
        target_depth=targets@frame(p)[2]
        results.append(dict(f,independent_pov_metrics=metrics,training_mean_iou=float(np.mean([metrics[k]['iou'] for k in train])),
            held_out_iou=metrics[cfg['held_out']]['iou'],
            training_region_loss_by_band=sensitivity,ray_pov_mismatches=mismatch,ray_pairs_unfinished=unfinished,
            tentative_edges=edges,direction_coordinates=chart,
            outward_anchor_predictions={k:dict(xy=pt.tolist(),ray_owner_index=int(owner),assigned_index=f['mapping'][k],
                ray_owner_matches=bool(owner==f['mapping'][k]),
                point_exposed=bool(owner==f['mapping'][k] and abs(hit-target)<1e-3),
                point_depth_error=float(abs(hit-target))) for k,pt,owner,hit,target in zip(IDS,anchors,owners,depths,target_depth)},
            render_provenance=provenance))
        labelmaps.append(labels)
    fig,axes=plt.subplots(1,3,figsize=(15,6),layout='constrained')
    for ax in axes:
        ax.imshow(image);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw photo; observation IDs only')
    for k,poly in cfg['observations'].items():
        q=np.mean(poly,axis=0);axes[0].text(*q,k,color='white',bbox=dict(facecolor='black',alpha=.6,pad=1))
    for ax,f,labels in zip(axes[1:],results,labelmaps):
        for k,poly in cfg['observations'].items():
            poly=np.array(poly);closed=np.vstack((poly,poly[0]))
            ax.plot(*closed.T,ls=':',color=COLORS[k],lw=1)
            ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==f['mapping'][k],levels=[.5],colors=[COLORS[k]],linewidths=1.2)
        ax.set_title(f"{f['hypothesis']}: solid = POV model, dotted = rough region\nG withheld; overlap {f['held_out_iou']:.0%}; both proposals remain tentative")
    fig.savefig(OUT/'fit-comparison.png',dpi=160);plt.close(fig)
    # A small specific question concerns ownership, not a demanded exact contour.
    point=np.array([1364,278])
    fig,axes=plt.subplots(1,2,figsize=(10,5),layout='constrained')
    for ax in axes:
        ax.imshow(image);ax.set_xlim(1326,1395);ax.set_ylim(326,250)
        ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
    axes[0].set_title('Raw C/E/G neighborhood')
    axes[1].set_title('Question: which bead owns dark patch P?\nC, E, another bead/gap, or unclear')
    for k in ['C','E','G']:
        q=np.mean(cfg['observations'][k],axis=0)
        axes[1].text(*q,k,color='white',bbox=dict(facecolor='black',alpha=.7,pad=1))
    axes[1].plot(*point,'o',ms=10,mfc='none',mec='cyan',mew=1.5)
    axes[1].annotate('P',point,xytext=(1358,268),color='cyan',arrowprops=dict(arrowstyle='-',color='cyan'))
    fig.savefig(OUT/'ownership-question.png',dpi=180);plt.close(fig)
    # Directly compare the independently generated known example with its fit.
    synthetic_cfg=json.loads((OUT/'synthetic/synthetic-config.json').read_text())
    sxy,sshape,smasks=polygons(synthetic_cfg)
    synthetic_results=[]
    for f in synth:
        pred,_,_=trace(np.array(f['parameters']),sxy,f['hand']);pred=pred.reshape(sshape)
        rows=measure(pred,smasks,f['mapping'],synthetic_cfg['boundary_uncertainty_px'])
        synthetic_results.append(dict(hypothesis=f['hypothesis'],hand=f['hand'],region_loss=f['region_loss'],
            held_out_iou=rows['G']['iou'],metrics=rows))
    assert synth[0]['region_loss']<synth[1]['region_loss']
    assert synthetic_results[0]['held_out_iou']>.9
    fig,axes=plt.subplots(1,3,figsize=(12,5),layout='constrained')
    for ax in axes:ax.set_aspect('equal');ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
    for k,mask in smasks.items():
        axes[0].contour(np.arange(x0,x1),np.arange(y0,y1),mask,levels=[.5],colors=['gray'])
    axes[0].set_title('Known POV geometry\nSupplied regions; G withheld')
    for ax,f in zip(axes[1:],synth):
        pred,_,_=trace(np.array(f['parameters']),sxy,f['hand']);pred=pred.reshape(sshape)
        for k,mask in smasks.items():
            ax.contour(np.arange(x0,x1),np.arange(y0,y1),mask,levels=[.5],colors=['gray'],linestyles=':')
            ax.contour(np.arange(x0,x1),np.arange(y0,y1),pred==f['mapping'][k],levels=[.5],colors=['red' if k=='G' else 'blue'],linewidths=1)
        ax.set_title(f"{f['hypothesis']} ({'correct' if f['hypothesis']=='H1' else 'wrong'} correspondence)\nG overlap {f['after']['G']['iou']:.1%}")
    fig.savefig(OUT/'synthetic-fit.png',dpi=150);plt.close(fig)
    report=dict(photo=results,synthetic=synthetic_results,
        provenance={name:sha(ROOT/name) for name in ['beads-photo-2.jpg','beads.pov','photo2/local-fit-r126.json',
            'photo2/local_surface_fit.py','photo2/check_local_surface_fit.py','photo2/review_local_surface_fit.py']},
        question=dict(point_xy=point.tolist(),text='Which bead owns dark patch P immediately to the right of C: C, E, another bead/gap, or unclear?',status='pending'),
        limitations=['Assistant-drawn diagnostic regions, no automatic detector or maker-confirmed boundaries.',
            'Both local hypotheses remain tentative; G is withheld from continuous fitting and chart scoring.',
            'Straight planar section and orthographic approximation; fixed 55-degree elevation is a camera/phase gauge, not measured global elevation.',
            'Numerical search is local and bounded, not proof of a global optimum.',
            'No full-string indices, exact N, recovered pigments, pattern or ring propagation.'])
    perspective_path=OUT/'perspective/report.json'
    if perspective_path.exists():
        perspective=json.loads(perspective_path.read_text())
        f=next(v for v in perspective['results'] if v['hypothesis']=='H2' and v['focal_ratio']==1.)
        red=np.asarray(Image.open(OUT/'perspective/H2-1.0.png'))[:,:,0]
        plabels=np.full(red.shape,-999,int);valid=red>0;plabels[valid]=INDICES[red[valid]-1]
        fig,axes=plt.subplots(1,3,figsize=(14,5),layout='constrained')
        for ax in axes:
            ax.imshow(image);ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
            ax.set_xlabel('source x (px)');ax.set_ylabel('source y (px)')
        axes[0].set_title('Raw photo')
        for ax,labels,title in [(axes[1],labelmaps[1],'H2 parallel-ray approximation'),
                                (axes[2],plabels,'H2 perspective, nominal metadata calibration')]:
            for k in IDS:
                ax.contour(np.arange(x0,x1),np.arange(y0,y1),labels==f['mapping'][k],levels=[.5],colors=[COLORS[k]],linewidths=1.2)
            ax.set_title(title+'\nC boundary mismatch remains; G withheld')
        fig.savefig(OUT/'perspective-comparison.png',dpi=160);plt.close(fig)
        report['perspective_report_sha256']=sha(perspective_path)
    (OUT/'review-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(photo=[{k:f[k] for k in ['hypothesis','training_mean_iou','held_out_iou','training_region_loss_by_band','ray_pov_mismatches']} for f in results],synthetic=synthetic_results),indent=2))

if __name__=='__main__':main()

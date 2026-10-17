"""Compact static photo comparisons and measured-only error propagation."""
import html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from PIL import Image,ImageDraw
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r315.review import card,overlay,FONT
from .model import Chain
from photo2.r316.renderer import RayLayers
from .search import OUT,SPLITS

def contour(m):return m&~ndi.binary_erosion(m)
def main():
    e=engine();data=load()[0];diag=read(OUT/'diagnostics.json.gz')['models'];names=['R316','hypothesis-A','hypothesis-B','hypothesis-C','joint-preserved'];dest=OUT/'review';extra=[]
    for fid,indices,title in [('R282-1459-0316',[-14,-15],'next-negative'),('R282-1537-0308',[11,12],'positive12')]:
        c=next(c for c in e.doc['regions'] if c['id']==fid);x,y=np.rint(c['point']).astype(int);x0=max(int(e.m['origin'][0]),int(x)-60);y0=max(int(e.m['origin'][1]),int(y)-60);yy,xx=np.mgrid[y0:y0+121,x0:x0+121];xy=np.c_[xx.ravel(),yy.ravel()];raw=e.m['native'][yy-e.m['origin'][1],xx-e.m['origin'][0]];core=e.m['core'][yy-e.m['origin'][1],xx-e.m['origin'][0]]==c['label'];canvas=Image.new('RGB',(1089,401*len(names)))
        for row,name in enumerate(names):
            s=Chain(read(OUT/f'{name}-model.json.gz')['parameters'],data);lay=RayLayers().trace(s,xy);pan=[card(raw,name+' / '+fid,3)]
            for idx in indices:
                j=int(np.flatnonzero(s.indices==idx)[0]);z=np.zeros(len(xy),bool)
                for jj,ix,mask,dep,un in lay['layers']:
                    if jj==j:z[ix]=mask
                iso=z.reshape(xx.shape);vis=(lay['owner']==j).reshape(xx.shape);im=raw.copy();im[contour(iso)]=[255,255,255];im[contour(vis)]=[0,240,255];hidden=iso&~vis&core;im[hidden]=[255,130,0];hole=ndi.binary_fill_holes(iso)&~iso;im[ndi.binary_dilation(hole)&iso]=[255,0,220]
                fi=float((iso&core).sum()/core.sum());fv=float((vis&core).sum()/core.sum());pan.append(card(im,f'Conditional {idx}: isolated {fi:.1%}, visible {fv:.1%}\nwhite isolated / cyan visible / orange hidden core',3))
                assert not (iso[0].any() or iso[-1].any() or iso[:,0].any() or iso[:,-1].any())
                path=f'review/{name}-{title}-{idx}-exact.npz';np.savez_compressed(OUT/path,xy=xy,isolated=iso,visible=vis,owner=lay['owner'],core=core)
                extra.append(dict(name=name,id=fid,index=idx,isolated=fi,visible=fv,arrays=path))
            for col,p in enumerate(pan):canvas.paste(p,(363*col,401*row))
        canvas.save(dest/f'alternatives-{title}.png')
    save(OUT/'alternative-cards.json',extra)
    # Fixed-R316 physical labels avoid moving the plot's x axis when correspondence changes.
    fig,axs=plt.subplots(3,2,figsize=(15,11),constrained_layout=True)
    for name in ['R306','R316','hypothesis-A','hypothesis-B','hypothesis-C','joint-preserved']:
        d=next(z for z in diag if z['name']==name)
        for col,xkey in enumerate(['fixed_R316_index','arc']):
            rr=sorted([r for r in d['regions'] if r[xkey] is not None],key=lambda z:z[xkey]);x=[z[xkey] for z in rr]
            axs[0,col].plot(x,[100*(1-z['modal']['modal_fraction']) for z in rr],'.-',label=name,alpha=.8)
            axs[1,col].plot(x,[100*(1-max([c['isolated'] for c in z['candidates']],default=0)) for z in rr],'.-',alpha=.8)
            axs[2,col].plot(x,[z['modal']['boundary']['p95_px'] for z in rr],'.-',alpha=.8)
            axs[2,col].set_xlabel('Conditional R316 physical index (fixed)' if col==0 else 'Frozen photographic arc from reference (px)')
    for i,label in enumerate(['Visible single-owner deficit (%)','Best isolated deficit (%; identity unresolved)','Supported boundary p95 (px)']):
        for ax in axs[i]:ax.set_ylabel(label);ax.grid(alpha=.25)
    axs[0,0].legend(fontsize=8);fig.suptitle('Measured cores only; lines guide the eye. Unmeasured physical addresses remain unknown.');fig.savefig(dest/'propagation.png',dpi=130);plt.close(fig)
    # Compact six-core before/after overview uses same photograph and exact full-scene contours.
    from photo2.r314.diagnostics import EARLY
    feature_ids=EARLY.copy();base=next(z for z in diag if z['name']=='R316')
    remote=[z for z in base['regions'] if abs(z['arc'])>80]
    for color in ['red','yellow']:
        rr=[z for z in remote if z['color']==color]
        if rr:feature_ids.extend([min(rr,key=lambda z:z['modal']['modal_fraction'])['id'],max(rr,key=lambda z:z['modal']['modal_fraction'])['id']])
    selected=read(OUT/'joint-preserved-model.json.gz')
    for part in SPLITS:
        feature_ids.append(max(selected[part]['owner_specific_cores'],key=lambda c:c['material_distance']['p95_px'])['id'])
    feature_ids=list(dict.fromkeys(feature_ids));manifest=[]
    for fid in feature_ids:
        c=next(c for c in e.doc['regions'] if c['id']==fid);x,y=np.rint(c['point']).astype(int);x0=int(np.clip(x-50,e.m['origin'][0],e.m['origin'][0]+e.shape[1]-101));y0=int(np.clip(y-50,e.m['origin'][1],e.m['origin'][1]+e.shape[0]-101));yy,xx=np.mgrid[y0:y0+101,x0:x0+101];raw=e.m['native'][yy-e.m['origin'][1],xx-e.m['origin'][0]];panels=[card(raw,fid+' / native original',3)]
        for name in ['R316','hypothesis-A','hypothesis-B','hypothesis-C','joint-preserved']:
            a=np.load(OUT/f'{name}-raster.npz');own=a['owner'].reshape(e.shape)[yy-e.m['origin'][1],xx-e.m['origin'][0]];im=overlay(raw,own.ravel());bd=np.zeros(own.shape,bool);bd[1:]|=own[1:]!=own[:-1];bd[:,1:]|=own[:,1:]!=own[:,:-1];im[bd]=[0,240,255];panels.append(card(im,name+' / visible boundaries',3))
        canvas=Image.new('RGB',(panels[0].width*len(panels),panels[0].height))
        for i,p in enumerate(panels):canvas.paste(p,(i*p.width,0))
        path=f'review/compact-{len(manifest)}.png';canvas.save(OUT/path);manifest.append(dict(id=fid,point=c['point'],crop_origin=[x0,y0],image=path))
    save(OUT/'compact-manifest.json',manifest)
    tables=[]
    for name in names:
        d=next(z for z in diag if z['name']==name)
        rows=''.join(f'<tr><td>{r["id"]}</td><td>{r["point"][0]:.1f}, {r["point"][1]:.1f}</td><td>{r["arc"]:.1f}</td><td>{r["modal"]["index"]}</td><td>{r["modal"]["modal_fraction"]:.1%}</td><td>{r["fixed_R316_index"]}: {r["fixed_R316_visible"]:.1%}</td></tr>' for r in sorted(d['regions'],key=lambda z:z['arc']))
        tables.append(f'<h2>{name}: measured error progression</h2><table><tr><th>Core</th><th>Photo x,y</th><th>Arc px</th><th>Conditional owner</th><th>Visible</th><th>Fixed R316 owner coverage</th></tr>{rows}</table>')
    page='<h2>Separate correspondence hypotheses</h2><p>White: isolated boundary. Cyan: visible boundary. Orange: candidate core hidden by other bodies. A matching isolated outline does not identify the real bead.</p><img src="review/alternatives-next-negative.png"><img src="review/alternatives-positive12.png"><h2>Error propagation</h2><img src="review/propagation.png"><h2>Compact original-photo comparisons</h2>'+''.join(f'<p>{x["id"]}</p><img src="{x["image"]}">' for x in manifest)+''.join(tables)
    path=OUT/'index.html';s=path.read_text().replace('</body>',page+'</body>');path.write_text(s)
if __name__=='__main__':main()

"""Small static ledger with real-photo crops and separate visibility layers."""
import html
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r295.geometry import AXES
from .model import Chain,refined_trace,subset
from .diagnose import OUT
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)

def edge_classes(s,xy,shape,tr):
    o=tr['owner'].reshape(shape);u=tr['unknown'].reshape(shape);ext=np.zeros(shape,bool);occ=ext.copy();bore=ext.copy()
    for axis in [0,1]:
        a=[slice(None)]*2;b=a.copy();a[axis]=slice(None,-1);b[axis]=slice(1,None);a,b=tuple(a),tuple(b);ok=~u[a]&~u[b];change=(o[a]!=o[b])&ok;occ[a]|=change&(o[a]>=0)&(o[b]>=0);ext[a]|=change&((o[a]<0)|(o[b]<0))
    for j in np.unique(o[o>=0]):
        t=refined_trace(subset(s,[j]),xy);mask=(t['owner']>=0).reshape(shape);hole=ndi.binary_fill_holes(mask)&~mask;near=ndi.binary_dilation(hole,iterations=2);bore|=ext&near&ndi.binary_dilation(o==j)
    ext&=~bore
    return ext,occ,bore

def overlay(raw,owners,classes=None):
    im=raw.copy();o=owners.reshape(raw.shape[:2]);valid=o>=0
    colors=np.stack([80+(o*73)%170,60+(o*117)%180,60+(o*41)%180],axis=-1);im[valid]=(.65*im[valid]+.35*colors[valid]).astype(np.uint8)
    if classes:
        for mask,col in zip(classes,[(255,255,255),(0,240,255),(255,30,210)]):im[mask]=col
    return im

def card(rgb,title,scale=3):
    im=Image.fromarray(rgb).resize((rgb.shape[1]*scale,rgb.shape[0]*scale),Image.Resampling.NEAREST);out=Image.new('RGB',(im.width,im.height+38),'white');out.paste(im,(0,38));ImageDraw.Draw(out).text((4,3),title,font=FONT,fill='black');return out

def main():
    dest=OUT/'review';dest.mkdir(exist_ok=True);e=engine();m=e.m;data=load()[0];ledger=read(OUT/'ledger.json.gz');rows=[];cache={};records=[]
    for z,r in enumerate(ledger):
        name=r['model']
        if name not in cache:cache[name]=Chain(read(OUT/'narrow-model.json.gz' if name=='R315-narrow' else ROOT/f'photo2/r314/results/models/{name}.json.gz')['parameters'],data)
        s=cache[name];x,y=np.rint(r['point']).astype(int);x0,y0=x-40,y-40;yy,xx=np.mgrid[y0:y+41,x0:x+41];xy=np.c_[xx.ravel(),yy.ravel()];raw=m['native'][y0-m['origin'][1]:y+41-m['origin'][1],x0-m['origin'][0]:x+41-m['origin'][0]];tr=refined_trace(s,xy);classes=edge_classes(s,xy,xx.shape,tr);panels=[card(raw,'Original photograph')]
        material=m['material'][yy-m['origin'][1],xx-m['origin'][0]];paper=m['paper'][yy-m['origin'][1],xx-m['origin'][0]];evi=raw.copy();evi[material]=(.5*evi[material]+.5*np.array([0,255,0])).astype(np.uint8);evi[paper]=(.5*evi[paper]+.5*np.array([50,100,255])).astype(np.uint8);panels.append(card(evi,'Frozen material / paper'))
        fullcard=card(overlay(raw,tr['owner'],classes),'Full necklace\nwhite exterior; cyan occlusion');draw=ImageDraw.Draw(fullcard)
        for jj in np.unique(tr['owner'][tr['owner']>=0]):
            pos=(s.pc[jj]-[x0,y0])*3
            if 0<=pos[0]<243 and 0<=pos[1]<243:draw.text((float(pos[0]),float(pos[1])+38),str(s.indices[jj]),font=FONT,fill='white',stroke_width=1,stroke_fill='black')
        panels.append(fullcard)
        numerical=dict(xy=xy,full_owner=np.where(tr['owner']>=0,s.indices[np.maximum(tr['owner'],0)],-32768),full_depth=tr['depth'],external=classes[0],occlusion=classes[1],bore=classes[2]);corexy=np.array(r['pixels']);ct=refined_trace(s,corexy);numerical.update(core_xy=corexy,core_owner=np.where(ct['owner']>=0,s.indices[np.maximum(ct['owner'],0)],-32768),core_depth=ct['depth'])
        for n,c in enumerate(r['candidates'][:2]):
            j=int(np.flatnonzero(s.indices==c['index'])[0]);it=refined_trace(subset(s,[j]),xy);mask=(it['owner']>=0).reshape(xx.shape);boundary=mask&~ndi.binary_erosion(mask);im=raw.copy();im[mask]=(.65*im[mask]+.35*np.array([30,255,80])).astype(np.uint8);im[boundary]=[255,255,255];panels.append(card(im,f"Isolated {c['index']}: {c['isolated_fraction']:.1%}\nvisible {c['visible_fraction']:.1%}"));numerical[f'isolated_{c["index"]}_depth']=refined_trace(subset(s,[j]),corexy)['depth']
        best=r['candidates'][0]
        if best['occluders']:
            oc=best['occluders'][0];cf=refined_trace(s,xy,remove=(oc['index'],));panels.append(card(overlay(raw,cf['owner']),f"Remove {oc['index']} (invalid geometry)\n{best['index']} visible {oc['removed_candidate_visible_fraction']:.1%}"));numerical['counterfactual_removed']=np.array(oc['index']);numerical['counterfactual_owner']=cf['owner']
        canvas=Image.new('RGB',(panels[0].width*3,panels[0].height*2),'#eeeeee')
        for i,im in enumerate(panels):canvas.paste(im,((i%3)*im.width,(i//3)*im.height))
        filename=f'feature-{z:02d}.png';canvas.save(dest/filename);np.savez_compressed(dest/f'feature-{z:02d}.npz',**numerical)
        links='; '.join(f"{c['index']}: isolated {c['isolated_fraction']:.1%}, visible {c['visible_fraction']:.1%}; hides behind "+','.join(str(o['index']) for o in c['occluders']) for c in r['candidates'][:3]);rows.append(f'<tr><td>{html.escape(name)}</td><td>{r["id"]}<br>{r["point"][0]:.2f}, {r["point"][1]:.2f}<br>arc {r["arc"]:.2f}</td><td>{html.escape(r["outcome"].replace('_',' '))}</td><td>{links}</td><td><a href="review/{filename}">photo layers</a> · <a href="review/feature-{z:02d}.npz">exact arrays</a></td></tr>');records.append(dict(model=name,id=r['id'],image='review/'+filename,numerical=f'review/feature-{z:02d}.npz'))
    save(OUT/'review-manifest.json',records)
    # Fixed observation catalog, including all black observations; no optical rematching.
    cat=read(ROOT/'photo2/r314/results/observation-catalog.json.gz');obs=cat['all_inherited_observations'];local=[]
    for r in obs:
        x,y=np.rint(r['point']).astype(int)-m['origin'];h,w=e.shape
        if 0<=x<w and 0<=y<h and m['roi'][y,x]:local.append(r)
    optical=[]
    for name,s in cache.items():
        tr=refined_trace(s,[r['point'] for r in local]);optical.append(dict(model=name,observations=[dict(original=r,first_hit_index=int(s.indices[j]) if j>=0 else None,unknown=bool(u),correspondence_verified=False) for r,j,u in zip(local,tr['owner'],tr['unknown'])]))
    save(OUT/'bright-placement.json.gz',dict(all_inherited=obs,local=optical,optical_fitting=False,connected_patch_source='../../r314/results/bright-epoch.json.gz',policy='Geometric ownership at unchanged observed bright-feature location, not a specular prediction or correspondence certificate.'))
    sensitivity=read(OUT/'sensitivity.json');a=np.load(OUT/'sensitivity.npz');fig,ax=plt.subplots(2,2,figsize=(12,8));names=[r['name'] for r in sensitivity['columns'] if 'excluded' not in r]
    for n in ['phase','s0','translation_x','translation_y','old_phase_cos','compact_phase_1','old_spacing_cos','compact_spacing_1']:
        j=names.index(n);ax[0,0].plot(a['indices'],np.linalg.norm(a['projected'][j],axis=1),label=n)
    ax[0,0].set(xlabel='physical index',ylabel='projected movement px / declared step');ax[0,0].legend(fontsize=7);ax[0,1].semilogy(a['singular'],'o-');ax[0,1].set(xlabel='direction',ylabel='scaled state singular value');ax[1,0].plot(a['field_indices'],a['desired'],label='bounded 40-address bump');ax[1,0].plot(a['field_indices'],a['old_basis_fit'],label='best bounded 32-node fit');ax[1,0].legend();ax[1,0].set(xlabel='physical index',ylabel='phase rad');ax[1,1].plot(a['field_indices'],a['compact_basis'].T);ax[1,1].set(xlabel='physical index',ylabel='new compact basis');fig.tight_layout();fig.savefig(dest/'sensitivity.png');plt.close(fig)
    c=read(OUT/'contacts.json.gz');fig,ax=plt.subplots(2,2,figsize=(12,8));rr=c['pairs']
    for off in [1,6,7]:
        z=[r for r in rr if r['offset']==off];ax[0,0].scatter([r['pair'][0] for r in z],[r['support_lower'] for r in z],s=8,label=f'+{off}');ax[0,1].scatter([r['pair'][0] for r in z],[r['solid_surface_upper'] for r in z],s=8,label=f'+{off}')
    ax[0,0].set(xlabel='physical index',ylabel='support gap lower bound (units)');ax[0,1].set(xlabel='physical index',ylabel='actual surface distance upper bound');ax[0,0].legend();z=c['local_paper'];ax[1,0].scatter([r['index'] for r in z],[r['clearance'] for r in z],s=8);ax[1,0].set(xlabel='physical index',ylabel='lowest glass minus support plane');z=[r for r in rr if r['refined']];ax[1,1].semilogy([r['support_lower'] for r in z],np.maximum([r['uncertainty_width'] for r in z],1e-12),'o');ax[1,1].set(xlabel='refined gap lower bound',ylabel='primal-dual width (units)');fig.tight_layout();fig.savefig(dest/'contacts.png');plt.close(fig)
    s=cache['R306-2405'];ix=np.flatnonzero((s.indices>=-16)&(s.indices<=20));fig,ax=plt.subplots(1,3,figsize=(15,5));axes=[s.pc,s.centers[:,[0,1]],s.centers[:,[0,2]]]
    for aa,pp,title in zip(ax,axes,['Image centers and conditional adjacency','Physical x/y','Physical x/z (paper support dashed)']):
        aa.scatter(pp[ix,0],pp[ix,1],c=s.indices[ix],cmap='turbo')
        for j in ix:
            aa.text(*pp[j],str(s.indices[j]),fontsize=7)
            for off,color in [(1,'#999999'),(6,'#dd6600'),(7,'#0077aa')]:
                if j+off in ix:aa.plot(pp[[j,j+off],0],pp[[j,j+off],1],c=color,alpha=.4,lw=.7)
        aa.set_title(title);aa.set_aspect('equal')
    ax[0].invert_yaxis();ax[2].axhline(c['paper']['plane_z'],ls='--');fig.tight_layout();fig.savefig(dest/'relative-positions.png');plt.close(fig)
    # Entire fixed geography before/after, and every fixed-core error versus index AND arc.
    extra=''
    if (OUT/'experiment.json.gz').exists():
        ex=read(OUT/'experiment.json.gz');fig,ax=plt.subplots(1,2,figsize=(12,4));old=read(ROOT/'photo2/r314/results/geometry-diagnostics.json.gz');arcs={r['id']:r['arc'] for r in old['models'][0]['regions']};ims=[]
        for name in ['baseline','translation','compact','narrow']:
            r=read(OUT/f'{name}-model.json.gz');o=np.load(OUT/f'{name}-raster.npz');cores=sum([r[key]['cores'] for key in ['development','comparison','buffer']],[]);ax[0].scatter([c['index'] for c in cores],[100*(1-c['modal_fraction']) for c in cores],s=14,label=name);ax[1].scatter([arcs[c['id']] for c in cores],[100*(1-c['modal_fraction']) for c in cores],s=14,label=name);im=overlay(m['native'],o['owner']);ims.append(card(im,name+' full fixed geography; conditional visible surfaces',1))
        for a,xlabel in zip(ax,['conditional modal physical index','fixed photographic arc px']):a.set(xlabel=xlabel,ylabel='core single-owner omission %');a.legend()
        fig.tight_layout();fig.savefig(dest/'propagation.png');plt.close(fig);canvas=Image.new('RGB',(ims[0].width,sum(i.height for i in ims)))
        y=0
        for im in ims:canvas.paste(im,(0,y));y+=im.height
        canvas.save(dest/'before-after.png');extra='<p><a href="experiment.json.gz">All experiment results</a> · <a href="review/before-after.png">Same-geography comparison</a> · <a href="review/propagation.png">Error propagation</a></p>'
        # finite boundary distributions, never substitute sentinel values
        fig,ax=plt.subplots(1,2,figsize=(12,4))
        for name in ['baseline','translation','compact','narrow']:
            bs=read(OUT/f'{name}-brackets.json.gz');x=np.array([b['displacement'] for b in bs if b['found']]);ax[0].plot(np.sort(x),np.arange(1,len(x)+1)/len(x),label=name);ax[1].plot([b['id'] for b in bs if b['found']],[b['displacement'] for b in bs if b['found']],'.',label=name,ms=3)
        ax[0].set(xlabel='finite bracket excess px',ylabel='empirical CDF');ax[1].set(xlabel='fixed bracket ID',ylabel='finite excess px');ax[0].legend();fig.tight_layout();fig.savefig(dest/'brackets.png');plt.close(fig)
    (OUT/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>R315 causal geometry ledger</title><style>body{font:16px system-ui;margin:24px;max-width:1400px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:8px;text-align:left}img{max-width:100%}a{color:#065ca0}@media(max-width:700px){table,tr,td{display:block;width:auto}table{font-size:14px}tr{margin-bottom:16px;border:1px solid #bbb}tr:first-child{display:none}td{padding:7px;border:0;overflow-wrap:anywhere}body{margin:16px}}</style></head><body><h1>R315 — causal geometry ledger</h1><p>No reconstruction adopted. Indices and alternative assignments remain conditional. Original photograph only; removed-occluder panels are diagnostic counterfactuals, never physical candidates. White = external silhouette, cyan = bead occlusion boundary, magenta = model bore boundary. Exact masks in NPZ files. Pixel uncertainty and incomplete silhouettes remain explicit.</p><p><a href="../../R315_REPORT.md">Report</a> · <a href="ledger.json.gz">Exact ledger JSON</a> · <a href="contacts.json.gz">Contact bounds</a> · <a href="sensitivity.json">Sensitivity details</a> · <a href="bright-placement.json.gz">All inherited bright observations</a></p>'+extra+'<table><tr><th>Model</th><th>Feature / original point</th><th>Outcome</th><th>Plausible modeled alternatives</th><th>Evidence</th></tr>'+''.join(rows)+'</table><p><a href="review/bracket-failures.png">Raw bracket-failure atlas</a> · <a href="review/brackets.png">Finite boundary errors</a> · <a href="search-coverage.json">Actual search coverage</a> · <a href="indexing-and-readiness.json">Indexing and acceptance</a> · <a href="review/relative-positions.png">Relative positions</a> · <a href="review/contacts.png">Packing and paper</a> · <a href="review/sensitivity.png">Sensitivity / phase and spacing</a></p><img src="review/sensitivity.png"><img src="review/contacts.png"></body></html>')
if __name__=='__main__':main()

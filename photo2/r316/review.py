"""Automatically generated measured-core occlusion ledger and pixel-exact photo cards."""
import html,time
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.diagnostics import EARLY
from photo2.r315.review import card,overlay,FONT
from photo2.r295.geometry import AXES
from .model import Chain
from .renderer import RayLayers,plane_orders
OUT=ROOT/'photo2/r316/results'


def contour(mask):return mask&~ndi.binary_erosion(mask)

def main():
    began=time.monotonic();e=engine();data=load()[0];ledger=[];manifest=[];dest=OUT/'review';dest.mkdir(exist_ok=True);htmlrows=[]
    for name in ['R306','focused3','narrow','negative-repair','positive-recovery','joint-recovery']:
        saved=read(OUT/f'{name}-model.json.gz');s=Chain(saved['parameters'],data);br=read(OUT/f'{name}-brackets.json.gz');witness={tuple(w['pair']):w for w in saved['physical']['witnesses']}
        for feature in e.doc['regions']:
            if feature['id'] not in EARLY:continue
            x,y=np.rint(feature['point']).astype(int);x0,y0=max(int(e.m['origin'][0]),x-60),max(int(e.m['origin'][1]),y-60);yy,xx=np.mgrid[y0:y0+121,x0:x0+121];xy=np.c_[xx.ravel(),yy.ravel()];shape=xx.shape;xxe=xx-e.m['origin'][0];yye=yy-e.m['origin'][1];assert yye.min()>=0 and xxe.min()>=0 and yye.max()<e.shape[0] and xxe.max()<e.shape[1];raw=e.m['native'][yye,xxe];core=(e.m['core'][yye,xxe]==feature['label']).ravel();layers=RayLayers().trace(s,xy);full=layers['owner'];dep=layers['depth'];cs=[];all_masks={};all_depths={}
            for j,ix,mask,depth,un in layers['layers']:
                z=np.zeros(len(xy),bool);z[ix]=mask;dd=np.full(len(xy),-np.inf);dd[ix]=depth;all_masks[j]=z;all_depths[j]=dd
            for j,z in all_masks.items():
                if not (z&core).any():continue
                hidden=z&(full!=j)&(full>=0);occ=[];overlaps=[]
                for k,zk in all_masks.items():
                    if j==k:continue
                    overlap=z&zk;front=overlap&(all_depths[k]>all_depths[j]+1e-6)
                    if not overlap.any():continue
                    delta=all_depths[k][overlap]-all_depths[j][overlap];overlaps.append(dict(index=int(s.indices[k]),overlap_pixels=int(overlap.sum()),foreground_pixels=int(front.sum()),depth_difference_min=float(delta.min()),depth_difference_max=float(delta.max()),ordering='uniform-front-sampled' if front[overlap].all() else ('uniform-back-sampled' if not front.any() else 'regional-reversal'),policy='Sampled occupied-ray depths, not continuous order proof'))
                    sel=hidden&(full==k)
                    if sel.any():occ.append(dict(index=int(s.indices[k]),pixels=int(sel.sum()),measured_core_pixels=int((sel&core).sum()),depth_margin_min=float((dep[sel]-all_depths[j][sel]).min()),depth_margin_p95=float(np.percentile(dep[sel]-all_depths[j][sel],95))))
                neighbors=[]
                for off in [1,6,7]:
                    matches=np.flatnonzero(s.indices==s.indices[j]+off)
                    if not len(matches):continue
                    k=int(matches[0]);pair=tuple(sorted([j,k]));w=witness.get(pair);normal=np.array(w['normal']) if w else s.centers[k]-s.centers[j];normal/=np.linalg.norm(normal)
                    if normal@(s.centers[k]-s.centers[j])<0:normal=-normal
                    ha,ga=s.support(normal,s.g[AXES[0]][j],True);hb,gb=s.support(-normal,s.g[AXES[0]][k],True);lo=float((s.centers[k]-s.centers[j])@normal-ha-hb);upper=float(np.linalg.norm(s.centers[k]+gb-s.centers[j]-ga))
                    neighbors.append(dict(offset=off,index=int(s.indices[k]),center=s.centers[k].tolist(),projected=s.pc[k].tolist(),support_clearance_lower=lo,support_witness_distance=upper,upper_policy='Envelope witness distance; not claimed actual-solid upper bound if a bore removes a witness'))
                cs.append(dict(index=int(s.indices[j]),array_index=j,isolated_fraction=float((z&core).sum()/core.sum()),visible_fraction=float(((full==j)&core).sum()/core.sum()),isolated_pixels=int(z.sum()),visible_pixels=int((full==j).sum()),occluders=sorted(occ,key=lambda a:-a['measured_core_pixels']),overlaps=overlaps,neighbors=neighbors,center=s.centers[j].tolist(),axis=s.g[AXES[0]][j].tolist()))
            cs.sort(key=lambda z:-z['isolated_fraction']);best=cs[0];j=best['array_index'];iso=all_masks[j].reshape(shape);vis=(full==j).reshape(shape);hidden=iso&~vis;panels=[card(raw,'Original photograph',3)];evi=raw.copy();mat=e.m['material'][yye,xxe];paper=e.m['paper'][yye,xxe];evi[mat]=(.5*evi[mat]+.5*np.array([0,255,0])).astype('uint8');evi[paper]=(.5*evi[paper]+.5*np.array([60,100,255])).astype('uint8');evi[contour(core.reshape(shape))]=[255,255,0];panels.append(card(evi,'Measured material / paper / core',3))
            im=raw.copy();im[iso]=(.65*im[iso]+.35*np.array([20,255,80])).astype('uint8');im[contour(iso)]=[255,255,255];hole=ndi.binary_fill_holes(iso)&~iso;im[ndi.binary_dilation(hole)&iso]=[255,0,220];panels.append(card(im,f"Isolated {best['index']}: {best['isolated_fraction']:.1%}\nwhite contour / magenta bore",3))
            fullim=overlay(raw,full);bound=np.zeros(shape,bool);oo=full.reshape(shape);bound[1:]|=oo[1:]!=oo[:-1];bound[:,1:]|=oo[:,1:]!=oo[:,:-1];fullim[bound]=[0,240,255];pan=card(fullim,'Full-scene visible contours',3);draw=ImageDraw.Draw(pan)
            for k in np.unique(full[full>=0]):
                pos=(s.pc[k]-[x0,y0])*3
                if 0<=pos[0]<363 and 0<=pos[1]<363:draw.text((float(pos[0]),float(pos[1])+38),str(s.indices[k]),font=FONT,fill='white',stroke_width=1,stroke_fill='black')
            panels.append(pan);im=overlay(raw,np.where(hidden.ravel(),full,-1));im[hidden&core.reshape(shape)]=[255,130,0];panels.append(card(im,'Occluders: hidden core in orange\nIndices/colors match full scene',3));im=raw.copy();im[contour(iso)]=[255,255,255];im[vis]=(.6*im[vis]+.4*np.array([0,230,255])).astype('uint8');im[contour(vis)]=[0,240,255];panels.append(card(im,f"Same candidate visible: {best['visible_fraction']:.1%}\nwhite isolated / cyan visible",3));canvas=Image.new('RGB',(1089,802),'#eeeeee')
            for n,pan in enumerate(panels):canvas.paste(pan,((n%3)*363,(n//3)*401))
            ident=f'{name}-{EARLY.index(feature["id"])}';canvas.save(dest/f'{ident}.png');np.savez_compressed(dest/f'{ident}.npz',xy=xy,full_owner=full,full_depth=dep,isolated=iso,visible=vis,hidden=hidden,core=core.reshape(shape),candidate_index=best['index'])
            nearby=[b for b in br if np.linalg.norm(np.array(b['material_endpoint'])-feature['point'])<45];record=dict(model=name,id=feature['id'],point=feature['point'],core_pixels=int(core.sum()),occupancy_count_scope='121x121 native crop; best isolated candidate checked against crop edges by verification',candidates=cs,local_brackets=nearby,layer_timing=layers['stats'],interpretation='Conditional isolated candidates, never physical identity. Hidden core pixels diagnose a candidate, not proof of the true foreground relation. Full necklace retained.');ledger.append(record);manifest.append(dict(model=name,id=feature['id'],image=f'review/{ident}.png',arrays=f'review/{ident}.npz',point=feature['point'],crop_origin=[int(x0),int(y0)]));oc=', '.join(f"{o['index']} ({o['measured_core_pixels']} core px)" for o in best['occluders'] if o['measured_core_pixels']);htmlrows.append(f'<tr><td>{name}</td><td>{feature["id"]}</td><td>{best["index"]}: isolated {best["isolated_fraction"]:.1%}; visible {best["visible_fraction"]:.1%}</td><td>{oc}</td><td><a href="review/{ident}.png">photographic layers</a> · <a href="review/{ident}.npz">arrays</a></td></tr>')
        print('ledger',name,flush=True)
    save(OUT/'ledger.json.gz',ledger);save(OUT/'review-manifest.json',manifest)
    # Native full geography, with every target-grid count retained in model JSON.
    ims=[]
    for name in ['R306','focused3','narrow','negative-repair','positive-recovery','joint-recovery']:
        a=np.load(OUT/f'{name}-raster.npz');ims.append(card(overlay(e.m['native'],a['owner']),name+' — same fixed photographic geography',1))
    canvas=Image.new('RGB',(ims[0].width,sum(im.height for im in ims)));y=0
    for im in ims:canvas.paste(im,(0,y));y+=im.height
    canvas.save(dest/'before-after.png')
    (OUT/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>R316 layered geometry</title><style>body{font:16px system-ui;max-width:1400px;margin:24px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:8px}img{max-width:100%}a{color:#065ca0}@media(max-width:700px){table,tr,td{display:block}th{display:none}tr{margin-bottom:16px}body{margin:12px}}</style></head><body><h1>R316 — layered rendering and joint geometry</h1><p>No reconstruction adopted. Isolated overlap is not identity. Cold polygon rendering is slower; cached layers accelerate local proposals by reusing unchanged bodies, and also accelerate repeated diagnostics. White isolated occupied contours, cyan visible contours, magenta enclosed bore, orange candidate core pixels hidden by neighbors.</p><p><a href="../../R316_REPORT.md">Report</a> · <a href="../../R316_REPRODUCE.md">Reproduce</a> · <a href="benchmarks.json">Timings and owner comparisons</a> · <a href="fixtures.json">Adversarial fixtures</a> · <a href="experiment.json">Controlled experiment / Pareto IDs</a> · <a href="ledger.json.gz">Complete occlusion ledger</a> · <a href="review/before-after.png">Same-geography before/after</a></p><table><tr><th>Model</th><th>Core</th><th>Best isolated candidate</th><th>Actual modeled occluders</th><th>Review</th></tr>'+''.join(htmlrows)+'</table><img src="review/before-after.png"></body></html>')
    save(OUT/'review-receipt.json',dict(seconds=time.monotonic()-began,rows=len(ledger),original_photo_panels=len(manifest)))
if __name__=='__main__':main()

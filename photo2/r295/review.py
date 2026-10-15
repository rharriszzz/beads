"""Native original-photo review, first-hit boundaries, support and competing hands."""
import html,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from .common import *
from .geometry import Chain
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COLORS={'R294':(255,180,45),'R295':(66,255,185),'hand-plus':(110,210,255)}
def text(im,xy,value,size=15,color='white'):
    ImageDraw.Draw(im).text(tuple(xy),value,font=ImageFont.truetype(FONT,size),fill=color,stroke_width=1,stroke_fill=(10,15,20))
def owner_image(name,box):
    z=np.load(OUT/(name+'-visibility.npz'));xy=z['xy'];o=z['owner'];x0,y0,x1,y1=box;keep=(xy[:,0]>=x0)&(xy[:,0]<x1)&(xy[:,1]>=y0)&(xy[:,1]<y1);p=xy[keep]-[x0,y0];a=np.full((y1-y0,x1-x0),-999,int);a[p[:,1],p[:,0]]=o[keep];return a

def edges(owner):
    e=np.zeros(owner.shape,bool)
    for shift in ((1,0),(-1,0),(0,1),(0,-1)):
        q=ndi.shift(owner,shift,order=0,mode='constant',cval=-999);e|=(owner>=-20)&(owner<=200)&(q!=owner)
    return e

def annotated(native,name,scene,box,scale=2,material=None,support_mode=False):
    x0,y0,x1,y1=box;a=native[y0:y1,x0:x1].copy();own=owner_image(name,box);edge=edges(own);a[edge]=COLORS[name]
    if support_mode:
        supported=[r['index'] for r in read(OUT/(name+'-positions.json.gz'))['records'] if r['meaningful_photographic_support']]
        a[edge&~np.isin(own,supported)]=[165,165,175]
    if material is not None:
        xy=pixels(material);q=xy-[x0,y0];good=(q[:,0]>=0)&(q[:,0]<x1-x0)&(q[:,1]>=0)&(q[:,1]<y1-y0);q=q[good];mask=np.zeros(own.shape,bool);mask[q[:,1],q[:,0]]=True;a[mask&~ndi.binary_erosion(mask)]=[255,255,255]
    im=Image.fromarray(a).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST)
    rows=read(OUT/(name+'-positions.json.gz'))['records'];by={r['index']:r for r in rows};d=ImageDraw.Draw(im)
    for j,k in enumerate(scene.indices):
        x,y=scene.pc[j]
        if not(-20<=k<=200 and x0<=x<x1 and y0<=y<y1):continue
        p=(scene.pc[j]-[x0,y0])*scale;color=COLORS[name]
        if support_mode:color=(80,255,160) if by[int(k)]['meaningful_photographic_support'] else (190,190,195)
        if scale>1 and (k%3==0 or k==0):text(im,p+[3,-12],str(k),13,color)
        elif k%10==0:text(im,p+[3,-12],str(k),14,color)
        d.ellipse((*tuple(p-2),*tuple(p+2)),outline=color)
        if k==0:d.ellipse((*tuple(p-10),*tuple(p+10)),outline='yellow',width=2);text(im,p+[10,7],'0',17,'yellow')
    return im

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();data=read(EVIDENCE/'inputs.json.gz');names=['R294','R295','hand-plus'];scenes={n:Chain(read(OUT/(n+'-evaluation.json'))['parameters'],data['r294']) for n in names};comparison=read(OUT/'comparison.json');changes=[r for r in comparison['changes'] if r['kind']=='region'];by={r['id']:r for r in data['rows'] if r['kind']=='region'}
    boxes=[]
    for k in (0,33,65,195):
        p=scenes['R294'].pc[k+45];box=[int(p[0]-100),int(p[1]-75),int(p[0]+100),int(p[1]+75)];boxes.append(dict(id='index-'+str(k),box=box,caption=f'Neighborhood of R294 conditional index {k}. Labels are model indices; hand+ changes correspondence. No verified physical identities.',record=None))
    for label,row in [('largest-gain',max(changes,key=lambda r:r['delta'])),('largest-regression',min(changes,key=lambda r:r['delta']))]:
        x,y=row['point'];boxes.append(dict(id=label,box=[int(x-85),int(y-65),int(x+85),int(y+65)],record=row['id'],caption=f"{row['id']} ({row['split']}): support containment {row['old_containment']:.1%} to {row['new_containment']:.1%}. White outline is a fallible historical automatic support, not accepted boundary truth."))
    primary=read(OUT/'R295-evaluation.json');reg=[r for r in primary['observations'] if r['kind']=='region'];success=max([r for r in reg if r['split']=='train'],key=lambda r:r['containment']);fail=min([r for r in reg if r['split']=='reserved'],key=lambda r:r['containment'])
    for label,row in [('successful-section',success),('reserved-failure',fail)]:
        x,y=row['point'];boxes.append(dict(id=label,box=[int(x-90),int(y-70),int(x+90),int(y+70)],record=row['id'],caption=f"{row['id']} ({row['split']}): R295 containment {row['containment']:.1%}; compatibility is not physical identity. Original photo is unobstructed at left."))
    for c in boxes:
        x0,y0,x1,y1=c['box'];raw=Image.fromarray(native[y0:y1,x0:x1]);raw.save(REVIEW/(c['id']+'-native.png'));panels=[raw.resize((raw.width*2,raw.height*2),Image.Resampling.NEAREST)]
        material=by[c['record']]['pixels'] if c['record'] else None
        for n in names:panels.append(annotated(native,n,scenes[n],c['box'],2,material))
        width=sum(im.width for im in panels);canvas=Image.new('RGB',(width,panels[0].height+95),(14,19,26));x=0
        for im,title in zip(panels,('Original photograph','R294 baseline','R295 selected hand−','R295 competing thin hand+')):
            canvas.paste(im,(x,30));text(canvas,(x+7,7),title,14);x+=im.width
        import textwrap
        for i,line in enumerate(textwrap.wrap(c['caption'],max(90,width//9))):text(canvas,(8,panels[0].height+40+i*19),line,13)
        canvas.save(REVIEW/(c['id']+'.png'));c['image']=c['id']+'.png';c['native']=c['id']+'-native.png'
    # Whole native photo keeps the complete necklace visible; only requested run is labeled.
    wholebox=[0,0,native.shape[1],native.shape[0]];Image.fromarray(native).save(REVIEW/'original-native.png')
    for n in names:
        im=annotated(native,n,scenes[n],wholebox,1,support_mode=(n=='R295'));im.save(REVIEW/(n+'-whole.png'));thumb=im.copy();thumb.thumbnail((1000,1250));thumb.save(REVIEW/(n+'-preview.png'))
    runbox=[1350,180,2220,810];parts=[annotated(native,n,scenes[n],runbox,1) for n in ('R294','R295')]
    sheet=Image.new('RGB',(parts[0].width*2,parts[0].height+30),(14,19,26))
    for i,(im,title) in enumerate(zip(parts,('R294: original conditional family','R295: selected conditional family'))):sheet.paste(im,(i*im.width,30));text(sheet,(i*im.width+8,6),title)
    sheet.save(REVIEW/'complete-run-side-by-side.png')
    # Native photo seam evidence vs model-only first hit: no invented observed contours.
    cues=np.load(EVIDENCE/'photographic-cues.npz');c=boxes[1];x0,y0,x1,y1=c['box'];im=Image.fromarray(native[y0:y1,x0:x1]).resize(((x1-x0)*3,(y1-y0)*3),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
    for pair,strength in zip(cues['pairs'],cues['edge']):
        p=cues['xy'][pair].mean(0)
        if strength>.8 and x0<=p[0]<x1 and y0<=p[1]<y1:
            p=(p-[x0,y0])*3;d.ellipse((*tuple(p-1),*tuple(p+1)),fill=(255,255,255))
    im.save(REVIEW/'photo-edge-evidence.png')
    save(REVIEW/'manifest.json',dict(crops=boxes,whole_models=names,native_dimensions=list(native.shape[1::-1]),colors=COLORS,edge_limits='White points: sampled observed gradient/dark-ridge evidence, not a certified complete ownership separator.'))
    metrics=[]
    for name in ('R294','local','global','geometry','R295','hand-plus','light'):
        r=read(OUT/(name+'-evaluation.json'));s=r['summary']['reserved'];metrics.append(f"<tr><td>{name}</td><td>{s['region']['compatible']}/{s['region']['n']}</td><td>{s['region']['mean_containment']:.1%}</td><td>{s['patch']['compatible']}/{s['patch']['n']}</td><td>{r['physical_audit']['state']}</td></tr>")
    crops=''.join(f'<article id="{c["id"]}"><h2>{html.escape(c["id"].replace("-"," "))}</h2><p>{html.escape(c["caption"])}</p><a href="{c["image"]}"><img loading="lazy" src="{c["image"]}" alt="{html.escape(c["caption"])}"></a><a href="{c["native"]}">Unmarked native crop</a></article>' for c in boxes)
    links=''.join(f'<li>{name}: <a href="../../r295/results/{name}-positions.csv">221 positions CSV</a> · <a href="../../r295/results/{name}-positions.json.gz">surfaces, correspondences, uncertainty</a> · <a href="../../r295/results/{name}-evaluation.json">evaluation and physical audit</a></li>' for name in ('R294','local','global','geometry','R295','hand-plus','light'))
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R295 — geometry and conditional correspondence</title><style>body{margin:0;background:#0d121b;color:#e5ecf4;font:16px/1.5 system-ui}main{max-width:1500px;margin:auto;padding:24px}h1{font-size:29px}a{color:#8ed9ff}button,select{padding:10px;background:#243246;color:white;border:1px solid #60748b;border-radius:5px}img{max-width:100%;height:auto}article{padding:22px 0;border-top:1px solid #445}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;border-bottom:1px solid #445;padding:7px}.scroll{overflow:auto}.view{overflow:auto;max-height:780px;background:#141c29}.view img{max-width:none;width:1000px}.note{border-left:4px solid #77dcb0;padding:12px;background:#182a2b}nav{display:flex;gap:15px;flex-wrap:wrap}label{display:inline-block;margin:8px}</style><main>
<h1>R295: physically feasible geometry, improved local compatibility, unresolved ownership</h1>
<p class="note">New reserved large regions: 0/5 → 2/5 compatible, but mean containment 69.3% → 68.6%. Reserved patches: 17/19 compatible in both. The gains coexist with clear regressions. All principal models are physically certified; no physical identities or repeating pattern are recovered.</p>
<nav><a href="../../R295_REPORT.md">Scientific report</a><a href="../../R295_REPRODUCE.md">Reproduce</a><a href="#index-33">Index 33</a><a href="#index-65">Index 65</a><a href="#index-195">Index 195</a><a href="#largest-regression">Regression</a><a href="#successful-section">Successful section</a></nav>
<h2>Bead 0 and complete conditional −20…200 run</h2><p>Yellow ring marks bead 0. Green center markers have compatible photographed support; gray markers are geometric predictions without compatible support. This does not establish distinct physical identities. Cyan/green/orange lines are predicted first-hit boundaries. Bead centers and highlights are different measurements. Hidden indices remain in every export.</p>
<label>View <select id="model"><option value="R295-whole.png">R295 selected</option><option value="R294-whole.png">R294 baseline</option><option value="hand-plus-whole.png">R295 thin hand+ alternative</option><option value="original-native.png">Original unmarked photo</option></select></label><label>Zoom <input id="zoom" type="range" min="600" max="2540" step="20" value="1000"></label><button id="toggle">Toggle original / model</button><p><a id="full" href="R295-whole.png">Open full native image</a></p><div class="view"><img id="whole" src="R295-whole.png" alt="Complete indexed reconstruction on the original photograph"></div>
<h2>Frozen independent regions</h2><p>Compatibility = at least 80% of native support owned by one visible surface, with at least 20 percentage points over its rival. These automatic regions are fallible and are not user-accepted contours. No accepted colored contour lies in this requested section. Training, development-validation, reserved, and buffer observations are retained separately.</p><div class="scroll"><table><thead><tr><th>Model</th><th>Reserved regions compatible</th><th>Mean containment</th><th>Reserved patches compatible</th><th>Physical audit</th></tr></thead><tbody>METRICS</tbody></table></div>
CROPS
<h2>Observed photographic edges</h2><p>White samples below show measured image gradient or dark-ridge evidence used by the objective. Some are illumination edges, not ownership seams. Compare with the unobstructed index-33 crop and model boundaries above.</p><img src="photo-edge-evidence.png" alt="Photographic edge evidence near index 33">
<h2>Packing, shape and competing correspondence</h2><p>The thin hand+ family is now physically possible: axial thickness and pitch change together. It improves selected large regions but drifts to different conditional indices and loses requested-run patch coverage. The joint training objective chooses the original hand− family. The tested legacy-radius controls penetrate neighbors. Failed envelope tests were distinguished from actual intersections; an annular-volume fallback located one shallow penetration missed by sampled surfaces.</p><p><a href="../../r295/results/screen-contact-classification.json.gz">Screening contact records</a> · <a href="../../r295/results/inconclusive-volume-audit.json">Independent shallow-overlap witness</a> · <a href="../../r295/results/sensitivity.json">Paired dimension/spacing and camera controls</a> · <a href="../../r295/results/joint.json">Integer assignment alternatives and search history</a></p>
<h2>Full scientific exports</h2><ul>LINKS</ul><p>All source Phase 1 pixels, positions, colors and historical experiments remain unchanged. Uncertainty is conditional parameter sensitivity, not a confidence interval. Reflections constrain candidate surface normals and lighting; they are never physical black-body centers.</p></main><script>const model=document.querySelector('#model'),whole=document.querySelector('#whole'),full=document.querySelector('#full');function show(v){whole.src=v;full.href=v}model.onchange=()=>show(model.value);document.querySelector('#zoom').oninput=e=>whole.style.width=e.target.value+'px';document.querySelector('#toggle').onclick=()=>show(whole.getAttribute('src')==='original-native.png'?model.value:'original-native.png');</script></html>'''
    page=page.replace('METRICS',''.join(metrics)).replace('CROPS','<h2>Complete run side by side</h2><a href="complete-run-side-by-side.png"><img src="complete-run-side-by-side.png" alt="R294 and R295 complete requested runs side by side"></a>'+crops).replace('LINKS',links);(REVIEW/'index.html').write_text(page)
    print('Review:',len(boxes),'native crop comparisons, 3 whole-model overlays')
if __name__=='__main__':main()

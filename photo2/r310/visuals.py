"""Native-coordinate ordered atlas and read-only click-to-recenter review."""
import base64,gzip,json
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save
from .analysis import OUT,BASE,D,MODELS,stats

def atlas():
    review=ROOT/'photo2/review/r310';review.mkdir(exist_ok=True);data=read(OUT/'viewer-data.json.gz');im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');im.save(review/'photo.png');cases=[];r306=data['models'][0];bs={b['index']:b for b in r306['positions']}
    for sign in [-1,1]:
        for n in [0,5,10,20,40,80,160,320]:cases.append(dict(id=f'{"negative" if sign<0 else "positive"}-{n:03d}',direction=sign,step=n,point=bs[sign*n]['axis_xy'],title=f'{"Negative" if sign<0 else "Positive"} sequence: R306 relative {sign*n:+d}'))
    # First failures and preceding good groups are added without replacing ordered views.
    for name in MODELS:
        d=read(OUT/f'{name}-partA.json.gz')
        for sign,f in d['findings'].items():
            for what in ['first_demonstrated_material_inconsistency','last_preceding_high_coverage']:
                r=f[what]
                if r and abs(r['distance_px'])<600:cases.append(dict(id=f'{name}-{sign}-{what}',direction=int(sign),step=r['index_from_reference'],point=r['point'],title=f'{name}: {what.replace("_"," ")} {r["id"]}'))
    for num,c in enumerate(cases):
        xy=np.array(c['point']);lo=np.maximum([0,0],np.round(xy-[155,100])).astype(int);hi=np.minimum(im.size,lo+[310,200]);crop=(*lo,*hi);raw=im.crop(crop);w,h=raw.size;canvas=Image.new('RGB',(w*4,h+56),'#14212c');draw=ImageDraw.Draw(canvas);canvas.paste(raw,(0,56));draw.text((4,3),c['title'],fill='white');draw.text((4,29),'Original, unchanged pixels',fill='white');nearest={}
        for j,m in enumerate(data['models'],1):
            img=raw.copy().convert('RGBA');over=Image.new('RGBA',img.size);od=ImageDraw.Draw(over)
            for s in data['supports']:
                if np.linalg.norm(np.array(s['point'])-xy)>220:continue
                for y,a,b in s['pixels']['runs']:od.line((a-lo[0],y-lo[1],b-lo[0],y-lo[1]),fill=(55,245,115,75))
            img=Image.alpha_composite(img,over);dd=ImageDraw.Draw(img);nearbeads=[b for b in m['positions'] if np.linalg.norm(np.array(b['projected_center'])-xy)<230];selected=min(m['positions'],key=lambda b:np.linalg.norm(np.array(b['projected_center'])-xy));nearest[m['name']]=selected['index']
            for b in nearbeads:
                for x,y,a,z in b['boundary_segments']:dd.line((x-lo[0],y-lo[1],a-lo[0],z-lo[1]),fill='#26e6f0',width=1)
                x,y=np.array(b['projected_center'])-lo
                if 0<x<w and 0<y<h:dd.text((x+2,y+2),str(b['index']),fill='white',stroke_width=1,stroke_fill='black')
            for r in m['reflections']:
                if not r['predicted'] or np.linalg.norm(np.array(r['observed'])-xy)>210:continue
                a=np.array(r['observed'])-lo;b=np.array(r['predicted'])-lo;dd.line((*a,*b),fill='#ff9349',width=1);dd.ellipse((*(a-2),*(a+2)),outline='#ffef5b');dd.line((b[0]-2,b[1],b[0]+2,b[1]),fill='white');dd.line((b[0],b[1]-2,b[0],b[1]+2),fill='white')
            lookup={b['index']:b for b in m['positions']}
            for k in [1,6,7]:
                b=lookup.get(selected['index']+k)
                if b:
                    a=np.array(selected['projected_center'])-lo;z=np.array(b['projected_center'])-lo;dd.line((*a,*z),fill=['#ee72ff','#94a4ff','#ff6590'][[1,6,7].index(k)],width=1);dd.text(tuple((a+z)/2),f'+{k}',fill='white',stroke_width=1,stroke_fill='black')
            canvas.paste(img.convert('RGB'),(j*w,56));draw.text((j*w+4,29),m['name']+' | conditional indices',fill='white')
        c.update(crop=list(map(int,crop)),nearest=nearest,image=f'atlas-{num:02d}.png',raw=f'raw-{num:02d}.png');canvas.save(review/c['image']);raw.save(review/c['raw'])
    save(OUT/'atlas.json',cases);return cases

def plots():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    review=ROOT/'photo2/review/r310'
    for name in MODELS:
        d=read(OUT/f'{name}-partA.json.gz')
        for sign in [-1,1]:
            q=[r for r in d['reflections'] if r['strong'] and sign*r['distance_px']>=0 and abs(r['distance_px'])<1250];f=d['findings'][str(sign)]
            for field in ['index_from_reference','distance_D']:
                fig,axs=plt.subplots(3,1,figsize=(11,8),sharex=True,layout='constrained')
                for r in q:
                    if r[field] is None or r['error_px'] is None:continue
                    x=sign*r[field];axs[0].scatter(x,r['error_px']/D,c='#b85227',s=16);axs[1].scatter(x,r['tangent_px']/D,c='#357ab4',s=12);axs[1].scatter(x,r['normal_px']/D,c='#ba4564',s=12)
                rows=[r for r in d['supports'] if sign*r['distance_px']>0 and abs(r['distance_px'])<1250]
                for r in rows:
                    x=sign*r[field];axs[2].scatter(x,r['coherence'],c='#25896c',s=16);axs[2].scatter(x, max(0,r['coherence']-(r['alternatives'][1]['fraction'] if len(r['alternatives'])>1 else 0)),c='#c99832',s=10)
                for key,col in [('first_suspected','#d29b12'),('first_demonstrated_material_inconsistency','#c22332')]:
                    r=f[key]
                    if r and abs(r['distance_px'])<1250:
                        for ax in axs:ax.axvline(sign*r[field],color=col,ls='--',label=key)
                axs[0].set_ylabel('Reflection magnitude / D');axs[1].set_ylabel('Tangent blue / normal red / D');axs[2].set_ylabel('Coverage green / rival margin gold');axs[2].set_xlabel('Outward conditional index difference' if field=='index_from_reference' else 'Outward photographic reference distance / D');axs[0].legend(fontsize=7);axs[2].set_ylim(0,1.05)
                for ax in axs:ax.grid(alpha=.2)
                fig.suptitle(f'{name}, direction {sign:+d}: all physical identities conditional; low error is not identity recovery');fig.savefig(review/f'{name}-{sign}-{field}.png',dpi=130);plt.close(fig)

def build():
    cases=atlas();plots();review=ROOT/'photo2/review/r310';data=read(OUT/'viewer-data.json.gz');data['atlas']=cases
    for m in data['models']:
        # Keep full model and all observations; avoid pixel arrays in the browser ledger.
        for r in m['supports']:r.pop('core_distances_px',None)
    payload=gzip.compress(json.dumps(data,separators=(',',':'),allow_nan=False).encode(),mtime=0);(review/'data.js').write_text('const PACKED='+json.dumps(base64.b64encode(payload).decode())+';\n')
    (review/'index.html').write_text(HTML)

HTML='''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R310 · first positioning discrepancy</title><style>body{font:15px system-ui;background:#12212c;color:#eef4f7;margin:18px}a{color:#8cd7ff}button,select,input{font:inherit;margin:4px;max-width:100%}canvas{width:100%;background:#253846;touch-action:none}.views{display:grid;grid-template-columns:1fr 1fr;gap:12px}.views>div{min-width:0}#info{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%}.atlas{margin:22px 0}#info{max-height:420px;overflow:auto}@media(max-width:720px){.views{grid-template-columns:1fr}}label{display:inline-block}</style><h1>R310 · outward from the red reference</h1><p>Diagnostic only: unchanged complete models. Physical identities are conditional. Yellow rings = observed reflections; white crosses = predicted reflections; orange vectors = Euclidean displacement. Cyan = native visible boundaries; green tint = observed positive interiors; magenta links = modeled +1/+6/+7, not verified photo neighbors. Bead centers are marked separately. D=36.878px.</p><p><a href="../../R310_REPORT.md">Report</a> · <a href="../../R310_REPRODUCE.md">Reproduce</a> · <a href="../../r310/results/partA.json.gz">Part A data</a> · <a href="../../r310/results/curvature.json.gz">Curvature data</a></p><div><select id="model"></select><button id="home">Reference</button><button data-step="-7">−7</button><button data-step="-6">−6</button><button data-step="-1">−1</button><input id="index" type="number" style="width:90px"><button data-step="1">+1</button><button data-step="6">+6</button><button data-step="7">+7</button><label>Zoom <input id="zoom" type="range" min="1" max="6" step=".25" value="2.5"></label><label><input id="boundaries" type="checkbox" checked>Boundaries</label><label><input id="interiors" type="checkbox" checked>Interiors</label><label><input id="vectors" type="checkbox" checked>Reflections</label><label><input id="neighbors" type="checkbox" checked>+1/+6/+7</label><label><input id="axes" type="checkbox">Photo / geometric axes</label></div><p id="status">Loading…</p><div class="views"><div>Original photograph<canvas id="raw" width="620" height="420"></canvas></div><div>Unchanged model at identical coordinates<canvas id="view" width="620" height="420"></canvas></div></div><p>Click either image to recenter at that photographic point and select the nearest projected model center (selection is not an ownership assertion). Changing model preserves photo coordinates and zoom.</p><div id="near"></div><pre id="info"></pre><h2>Ordered atlas: reference → negative, reference → positive</h2><div id="atlas"></div><h2>Signed errors and correspondence support</h2><div id="graphs"></div><script src="data.js"></script><script src="viewer.js"></script></html>'''
if __name__=='__main__':build()

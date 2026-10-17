"""Reuse R305 navigation, native owner picking, vectors, boundaries and plots."""
from pathlib import Path
import json,shutil,gzip,base64
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save
from photo2.r297.geometry import reference

def illustrations(out,models):
    review=out/'review';image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    image.save(review/'photo.png');primary=models[0];gallery=[];chosen=[]
    # Required geographic location plus predeclared performance quantiles.
    chosen.append(([1110.23,336.04],'R306 minus101 photographic location','Required location; current indices are conditional.'))
    dense=read(out/'metrics'/f"{primary['name']}.json.gz")
    supports=sorted([r for d in dense.values() for r in d['supports']],key=lambda r:r['fraction'])
    for quantile,label in [(.9,'good'),(.5,'mediocre'),(.1,'poor')]:
        r=supports[int(quantile*(len(supports)-1))];chosen.append((r['point'],label+' ownership quantile',f"Interior modal ownership {100*r['fraction']:.1f}% (not a full outline certificate)."))
    # Include the greatest measured ownership regression, even if numerically small.
    baseline=read(out/'metrics/R307-primary.json.gz');old={r['id']:r for d in baseline.values() for r in d['supports']}
    regression=min(supports,key=lambda r:r['fraction']-old[r['id']]['fraction'])
    chosen.append((regression['point'],'Largest ownership regression versus R307',f"Modal ownership change {100*(regression['fraction']-old[regression['id']]['fraction']):+.1f} percentage points; original support retained."))
    for c in read(out/'R305-problem-cohorts.json'):
        chosen.append((c['center'],f"R305 interval {c['historical_R305_interval'][0]}…{c['historical_R305_interval'][1]}",'Original geographic cohort; current index is independently assigned.'))
    for r in sorted([r for r in primary.get('guided_correspondences',primary['correspondences'])['records'] if r['strong'] and r['error_px'] is not None],key=lambda r:-r['error_px']):
        if all(np.linalg.norm(np.array(r['observed'])-p[0])>140 for p in chosen):
            chosen.append((r['observed'],r['id'],f"Strong reflection error {r['error_px']:.2f}px; {r['status']}."))
        if len(chosen)>=12:break
    for r in sorted([r for r in primary['supports'] if r['kind']=='region'],key=lambda r:r['fraction']):
        if all(np.linalg.norm(np.array(r['point'])-p[0])>140 for p in chosen):
            chosen.append((r['point'],r['id'],f"Independent interior: {100*r['fraction']:.1f}% on largest visible owner."))
        if len(chosen)>=16:break
    points=np.array([b['projected_center'] for b in primary['positions']])
    for number,(point,title,caption) in enumerate(chosen,1):
        center=np.array(point);lo=np.maximum([0,0],np.floor(center-110)).astype(int);hi=np.minimum(image.size,lo+220).astype(int)
        raw=image.crop((*lo,*hi));annotated=raw.copy();draw=ImageDraw.Draw(annotated)
        for b in primary['positions']:
            if np.linalg.norm(np.array(b['projected_center'])-center)>150:continue
            for a,c,d,e in b['boundary_segments']:draw.line((a-lo[0],c-lo[1],d-lo[0],e-lo[1]),fill='#32ddff',width=1)
        for r in primary.get('guided_correspondences',primary['correspondences'])['records']:
            if r['predicted'] and np.linalg.norm(np.array(r['observed'])-center)<155:
                a=np.array(r['observed'])-lo;b=np.array(r['predicted'])-lo
                draw.line((*a,*b),fill='#ff873c' if r['strong'] else '#bd84eb',width=2);draw.ellipse((* (a-2),*(a+2)),outline='#fff16b')
        combined=Image.new('RGB',(raw.width*2,raw.height+32),'#152430');combined.paste(raw,(0,32));combined.paste(annotated,(raw.width,32));d=ImageDraw.Draw(combined);d.text((8,8),'Original photograph',fill='white');d.text((raw.width+8,8),'Native boundaries + reflection vectors',fill='white')
        name=f'diagnostic-{number:02d}.png';rawname=f'raw-{number:02d}.png';combined.save(review/name);raw.save(review/rawname)
        j=int(np.linalg.norm(points-center,axis=1).argmin());gallery.append(dict(image=name,raw=rawname,title=title,caption=caption,index=primary['positions'][j]['index'],point=list(map(float,center))))
    overview=image.copy();d=ImageDraw.Draw(overview)
    for j,g in enumerate(gallery,1):
        x,y=g['point'];d.ellipse((x-30,y-30,x+30,y+30),outline='#38e8ff',width=5);d.text((x+30,y),str(j),fill='white',stroke_width=2,stroke_fill='black')
    overview.thumbnail((760,960));overview.save(review/'overview.png')
    (review/'gallery.js').write_text('const GALLERY='+json.dumps(gallery,separators=(',',':'))+';\n')
    return gallery

def plots(out,models):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for model in models:
        rows=[r for r in model.get('guided_correspondences',model['correspondences'])['records'] if r['strong'] and r['index'] is not None]
        fig,axes=plt.subplots(2,1,figsize=(12,6),sharex=True,layout='constrained')
        axes[0].scatter([r['index'] for r in rows],[r['error_px'] for r in rows],s=12,color='#bd622c');axes[0].set_ylabel('Magnitude (px)')
        for field,color in [('tangent_px','#b44732'),('normal_px','#227aa0')]:axes[1].scatter([r['index'] for r in rows],[r[field] for r in rows],s=12,label=field,color=color)
        axes[1].axhline(0,color='gray',lw=.6);axes[1].legend();axes[1].set_ylabel('Signed error (px)');axes[1].set_xlabel('Conditional bead index')
        fig.suptitle(model['name']+' · original observations, current one-to-one assignment')
        for a in axes:a.grid(alpha=.2)
        fig.savefig(out/'review'/f'{model["name"]}-errors.png',dpi=130)
        svg=out/'review'/f'{model["name"]}-errors.svg';fig.savefig(svg);plt.close(fig)
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig,axes=plt.subplots(2,1,figsize=(12,6),sharex=True,layout='constrained')
    for model in [models[0]]+[m for m in models if m['name'] in ['R297','R298-primary']]:
        r=model['regions'];axes[0].plot([x['section'] for x in r],[100*x['support_containment'] if x['support_containment'] is not None else np.nan for x in r],'.-',label=model['name'])
        axes[1].plot([x['section'] for x in r],[100*x['colored_omission'] if x['colored_omission'] is not None else np.nan for x in r],'.-',label=model['name'])
    axes[0].set_ylabel('Positive region containment (%)');axes[1].set_ylabel('Colored omission (%)');axes[1].set_xlabel('Common photographic circuit section')
    axes[0].legend();fig.savefig(out/'review'/'regional-material.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    for folder,label in [(out,'R309 guided trials')]:
        if not (folder/'checkpoint.json').exists():continue
        history=read(folder/'checkpoint.json')['history']
        ax.plot([r['id'] for r in history],[r.get('loss') for r in history],label=label,lw=1.3)
        if (folder/'native-progress.json.gz').exists():
            audits=read(folder/'native-progress.json.gz');ax.scatter([r['id'] for r in audits],[r['native']['loss'] for r in audits],s=30,marker='x',label=label+' · native audit')
    ax.set(xlabel='Proposal number within run',ylabel='Training objective',title='Search history · comparison outcomes excluded')
    ax.legend();ax.grid(alpha=.2);fig.savefig(out/'review'/'optimization-progress.png',dpi=140);plt.close(fig)

def build(out,models,m,obs):
    out=Path(out);review=out/'review';review.mkdir(exist_ok=True)
    prepare_guided_review(out,models)
    original=ROOT/'photo2/review/r305';html=(original/'index.html').read_text();js=(original/'viewer.js').read_text()
    html=html.replace('R305 · 1,041 bead inspection','R309 · whole-circuit reconstruction').replace('R305 · continuous inspection, −40 to +1000','R309 · whole-circuit reconstruction')
    html=html.replace('</style>','main,.panel,.views>div,.grid>div{min-width:0}#associated,#downloads,#redDetail{overflow-wrap:anywhere}.grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}@media(max-width:800px){.grid{grid-template-columns:minmax(0,1fr)}.bar{min-width:0}#slider{min-width:120px;width:100%}#plot{min-width:0}}</style>')
    html=html.replace('</style>','.bar label{max-width:100%}#model{max-width:calc(100vw - 110px)}</style>')
    html=html.replace('Fixed R304 registration and illumination · conditional indices · no fitting','One fitted geometric axis · hard physical feasibility · conditional identities')
    html=html.replace('../../R305_REPORT.md','../R309_REPORT.md').replace('../../R305_REPRODUCE.md','../../../../R309_REPRODUCE.md').replace('../r304/','../../../../review/r305/')
    html=html.replace('>R304</a>','>R305 historical review</a>')
    html=html.replace('<option value="primary">Primary · independent hand+</option><option value="hand-minus">Independent hand−</option><option value="calibrated">Calibrated hand+</option>',''.join(f'<option value="{r["name"]}">{r["name"]} · N{r["parameters"]["count"]} · hand {r["parameters"]["hand"]:+d} · {r["parameters"]["topology"]}</option>' for r in models))
    html=html.replace('>Axis</label>','>Geometric axis</label><label><input id="photoReference" type="checkbox">Original photographic reference</label>')
    html=html.replace('Unobstructed surface (four red cases)','Reserved layer').replace('Saved red interiors (uncertain)','Observed contours / red interiors')
    html=html.replace('S1 anchors and one globally ordered alignment are retained. Gap costs 12², 24² (selected), 48² px² and no-gap ordinal control are saved in downloads. Alternatives are diagnostic and do not replace the selected path.','No old index anchors are imposed. Global one-to-one spatial assignments use 12², 24² (selected), and 48² px² unmatched-observation costs. Strong reflections are paired first; uncertain candidates remain separate. The catalog is incomplete. Alternative assignments and fixed-owner controls are saved.')
    html=html.replace('Curated diagnosis · raw beside annotated','Automatically selected residual problems · raw beside annotated')
    html=html.replace('Questions retained for later review','Interpretation and limits').replace('No optimization, color-pattern inference, FFT constraints or Phase 3. Stop for maker review.','Fitting is complete. No color-pattern inference or Phase 3. Every body, unmatched observation and ambiguous assignment remains in the saved model.')
    html=html.replace('curvature, local signed slope, abrupt changes, sampling sensitivity, unassigned reflections, ambiguity and sparse evidence','regional material contradictions, reflection displacement, ambiguity and sparse evidence')
    html=html.replace('<div id="problems"></div>','<div id="problems"></div><p><a href="regional-material.png">Common-geography material comparison</a> · <a href="optimization-progress.png">Optimization history</a> · <a href="../comparison.json">Quantitative comparison</a> · <a href="../phase-diagnostics.json.gz">Conditional phase / owner controls</a></p>')
    html=html.replace('<script src="viewer.js"></script>', '<script>async function startReview(){const bytes=Uint8Array.from(atob(COMPRESSED_DATA),c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));window.DATA=JSON.parse(await new Response(stream).text());const script=document.createElement("script");script.src="viewer.js";document.body.append(script);}startReview().catch(e=>{document.getElementById("status").textContent="Load error: "+e;throw e;});</script>')
    js=js.replace('selected=-40','selected=0').replace('model.positions[k+40]','model.positions[k-model.positions[0].index]')
    js=js.replace('Math.max(-40,Math.min(1000,Math.round(Number(k))))','Math.max(model.positions[0].index,Math.min(model.positions.at(-1).index,Math.round(Number(k))))').replace('selected=-40','selected=0')
    js=js.replace('k>=-40&&k<=1000','k>=model.positions[0].index&&k<=model.positions.at(-1).index')
    js=js.replace('x=k=>60+(k+40)/1040*1115','x=k=>60+(k-model.positions[0].index)/(model.positions.length-1)*1115')
    js=js.replace('for(let k=-40;k<=1000;k+=80)','for(let k=model.positions[0].index;k<=model.positions.at(-1).index;k+=200)')
    js=js.replace(' · fraction ${(100*b.visible_fraction).toFixed(1)}%','')
    js=js.replace('model.positions.forEach((b,i)=>i?ctx.lineTo(...b.axis_xy):ctx.moveTo(...b.axis_xy));',
        '(model.geometric_axis_xy||model.positions.map(b=>b.axis_xy)).forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));')
    js=js.replace("'not applicable'","'not measured per bead; see sampled numerical audit'")
    js=js.replace("function tables(){", "function tables(){for(const id of ['index','slider']){$(id).min=model.positions[0].index;$(id).max=model.positions.at(-1).index;}")
    before="$('outsideCatalog').textContent=`${model.correspondences.unmatched_outside_model_geography.length} unmatched catalog observations lie beyond this model’s geographic extent; they are retained in correspondence downloads, outside the50-index group counts. Different families reach different photographic endpoints.`;"
    js=js.replace(before,"$('outsideCatalog').textContent=`${model.positions.length} physical bodies cover the whole circuit. Unmatched observations retain their measured locations; numbers in other families do not establish the same physical identity.`;")
    start=js.index(" $('downloads').innerHTML=");end=js.index(";$('physical').textContent",start)
    js=js[:start]+" $('downloads').innerHTML=`<a href=\"../exports/${model.name}.json.gz\">Complete model</a> · <a href=\"../exports/${model.name}${model.guided?'-guided':''}-errors.csv\">Error CSV</a> · <a href=\"../exports/${model.name}-regions.csv\">Regions CSV</a> · <a href=\"${model.name}-errors.png\">Error figure</a> · <a href=\"../numerical.json\">Primary sampled numerical audit</a>`"+js[end:]
    js=js.replace("'centerline','material'","'centerline','photoReference','material'")
    needle=" if(checked('centerline'))"
    reference_draw=" if(checked('photoReference')){ctx.strokeStyle='#f1be5b';ctx.lineWidth=1.4/zoom;ctx.setLineDash([5/zoom,4/zoom]);ctx.beginPath();DATA.reference.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);}\n if(checked('material'))for(const r of DATA.observedContours){ctx.strokeStyle='#ffb953';ctx.lineWidth=1/zoom;ctx.beginPath();r.polygon.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.stroke();}\n"
    js=js.replace(needle,reference_draw+needle)
    js=js.replace("selectBead(-40,true)","selectBead(0,true)").replace("'Ready · 1,041 positions in each of three models'","`Ready · ${DATA.models.length} complete-circuit models`")
    html=html.replace('</header>', '<p><a href="before-after.png">Required location: before/after</a> · <a href="../acceptance.json">Acceptance and regressions</a></p></header>')
    html=html.replace('<div id="redDetail"></div>', '<div id="redDetail"></div>')
    html=html.replace('</style>', '#overlapDetail{max-height:280px;overflow:auto;overflow-wrap:anywhere}</style>')
    html=html.replace('<label><input id="photoReference"', '<label><input id="overlap" type="checkbox">Observed interior / owner overlap</label><label><input id="photoReference"')
    html=html.replace('<details>', '<div id="overlapDetail"></div><details>',1)
    js=js.replace("'centerline','photoReference'","'centerline','overlap','photoReference'")
    js=js.replace(" if(checked('photoReference'))", OVERLAP_DRAW+" if(checked('photoReference'))")
    js=js.replace('function details(){', 'function details(){overlapDetails();')
    js=js.replace("$('model').onchange=()=>{model=DATA.models.find(m=>m.name===$('model').value);tables();selectBead(selected,true);};", "$('model').onchange=()=>{const point=[...viewCenter];model=DATA.models.find(m=>m.name===$('model').value);const nearest=model.positions.reduce((a,b)=>Math.hypot(a.projected_center[0]-point[0],a.projected_center[1]-point[1])<Math.hypot(b.projected_center[0]-point[0],b.projected_center[1]-point[1])?a:b);tables();selectBead(nearest.index,true);viewCenter=point;draw();details();};")
    js=js.replace("selectBead(0,true);$('status')", "selectBead(model.positions.reduce((a,b)=>Math.hypot(a.projected_center[0]-1110.23,a.projected_center[1]-336.04)<Math.hypot(b.projected_center[0]-1110.23,b.projected_center[1]-336.04)?a:b).index,true);$('status')")
    js+=OVERLAP_JS
    # All primary/alternative/historical datasets use the same native pixel format.
    owners={}
    for r in models:
        a=np.load(out/'exports'/f'{r["name"]}-raster.npz')['address'];flat=a.ravel();edges=np.r_[0,np.flatnonzero(np.diff(flat)!=0)+1,len(flat)]
        runs=[[int(i),int(j-i),int(flat[i])] for i,j in zip(edges,edges[1:]) if flat[i]!=-32768]
        owners[r['name']]=dict(width=a.shape[1],height=a.shape[0],runs=runs)
    public=[]
    for r in models:
        public.append({k:r[k] for k in ['name','parameters','positions','bounds','correspondences','closure']})
        public[-1]['guided']=bool(r.get('guided_correspondences'))
        public[-1]['supports']=r['supports']
        public[-1]['correspondences']=r.get('guided_correspondences',r['correspondences'])
        public[-1]['geometric_axis_xy']=r.get('geometric_axis_xy')
        public[-1]['physical']={k:v for k,v in r['physical'].items() if k not in ['witnesses','index_pairs']}
    problems=[];origin=reference_origin()
    for r in read(out/'diagnosis.json'):
        model=next(m for m in models if m['name']==r['model']);c=[b for b in model['positions'] if int(((b['photo_arc']-origin)%reference().length)/reference().length*32)==r['section']]
        if c:
            k=c[len(c)//2]['index'];problems.append(dict(model=r['model'],first=max(model['positions'][0]['index'],k-20),last=min(model['positions'][-1]['index'],k+20),score=r['priority'],summary=dict(n=r['metrics']['n'],demonstrated_penetrating_pairs=0)))
    data=dict(models=public,reference=reference().points.tolist(),observedContours=m['beads'],observations=obs,
        observedSupports=[dict(id=r['id'],point=r['point'],runs=r['pixels']['runs'],color=r['color'],accepted=r['accepted']) for r in read(ROOT/'photo2/r296/evidence/inputs.json.gz')['rows'] if r['kind']=='region' and not r['reflection']],red=read(out/'starting-red-diagnosis.json'),contour=[],problems=problems,
        questions=['The photographic reference (gold dashed) is unchanged; the fitted geometric axis is green. Physical nonintersection does not establish photographic correctness.',
                   'Observed interiors, uncertain contours, predicted visible surfaces, highlights and body centers are different objects. All index assignments are conditional.',
                   'The comparison bands use previously studied evidence. Errors, competing families, failed trials and numerical uncertainty remain available in the report.'])
    (review/'index.html').write_text(html);(review/'viewer.js').write_text(js)
    payload=gzip.compress(json.dumps(data,separators=(',',':'),allow_nan=False).encode(),mtime=0)
    (review/'data.js').write_text('const COMPRESSED_DATA='+json.dumps(base64.b64encode(payload).decode())+';\n')
    (review/'owners.js').write_text('const OWNERS='+json.dumps(owners,separators=(',',':'))+';\n')
    illustrations(out,models);plots(out,models)
    save(out/'review-manifest.json',dict(models=[r['name'] for r in models],viewer='R305 native navigation and plots adapted for variable whole-circuit counts; prior viewers unchanged.'))

def reference_origin():
    return read(ROOT/'photo2/r296/evidence/inputs.json.gz')['arc0']

OVERLAP_DRAW=""" if(checked('overlap'))for(const r of DATA.observedSupports){if(Math.hypot(r.point[0]-viewCenter[0],r.point[1]-viewCenter[1])>260/zoom+80)continue;const match=model.supports.find(s=>s.id===r.id),modal=match?match.index:null;const px=ownerPixels[model.name];for(const [y,a,b] of r.runs)for(let x=a;x<=b;x++){const ix=4*(y*2540+x),k=px[ix]+256*px[ix+1]-32768;ctx.fillStyle=k===-32768?'#ff304aaa':k===modal?'#35ed7899':'#ffad3299';ctx.fillRect(x-.5,y-.5,1,1);}}\n"""
OVERLAP_JS="""
function overlapDetails(){const out=$('overlapDetail');if(!out)return;out.replaceChildren();const note=document.createElement('p');note.textContent='Observed positive interiors: green = modal visible owner; orange = competing owner; red = no resolved modeled surface. Unknown photographic exterior stays unlabelled. Selection yellow is not bead color.';out.append(note);for(const r of DATA.observedSupports.filter(r=>Math.hypot(r.point[0]-viewCenter[0],r.point[1]-viewCenter[1])<85)){const s=model.supports.find(s=>s.id===r.id);if(!s)continue;const p=document.createElement('p');p.textContent=r.id+' · '+(r.accepted?'qualitatively accepted':'automatic, possible merged interior')+' · '+(100*s.fraction).toFixed(1)+'% modal · owners: ';for(const a of s.alternatives.slice(0,5)){const b=document.createElement('button');b.textContent=a.index+': '+(100*a.fraction).toFixed(1)+'%';b.onclick=()=>selectBead(a.index,true);p.append(b);}out.append(p);}}
"""


def prepare_guided_review(out,models):
    import csv
    from scipy.spatial import cKDTree
    from photo2.r306.evidence import load
    from photo2.r306.diagnose import red_checks
    from photo2.r309.delivery import model_scene
    data,_,_=load();red=[]
    for model in models:
        proxy=dict(model)
        if model.get('guided_correspondences'):
            g=model['guided_correspondences'];tree=cKDTree([b['projected_center'] for b in model['positions']])
            for group in g['groups']:group['examples']['unmatched_observed']=[]
            for r in g['records']:
                if r['index'] is None:
                    k=model['positions'][tree.query(r['observed'])[1]]['index']
                    next(x for x in g['groups'] if x['first']<=k<=x['last'])['examples']['unmatched_observed'].append(dict(index=k,id=r['id']))
            proxy['correspondences']=g
            with (out/'exports'/f"{model['name']}-guided-errors.csv").open('w') as f:
                writer=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in g['records']))),lineterminator='\n');writer.writeheader();writer.writerows(g['records'])
            save(out/'exports'/f"{model['name']}.json.gz",model)
        red+=red_checks(model_scene(model,data),proxy)
    save(out/'starting-red-diagnosis.json',red)

"""Post-seal evaluation and small adaptation of the existing R302 viewer."""
import csv
import json
import time
import numpy as np
from PIL import Image
from .core import *
from photo2.r302.experiment import clean
from photo2.r301.export import stats

REVIEW=ROOT/'photo2/review/r303'

def surface(c,s,name):
    yy,xx=np.mgrid[0:220,0:220];xy=np.c_[xx.ravel(),yy.ravel()]+np.array(s['center'])-110
    tr=c.camera(xy);ok=tr['owner']>=0;rgba=np.zeros((len(xy),4),np.uint8);tone=80+140*np.maximum(tr['normal']@c.eye,0)
    rgba[ok,:3]=np.c_[tone[ok]*.35,tone[ok]*.85,tone[ok]].astype(np.uint8);rgba[ok,3]=145;rgba[tr['unknown']]=[255,80,220,150]
    filename=f'surface-{name}.png';Image.fromarray(rgba.reshape(220,220,4)).save(REVIEW/filename);return filename

def main():
    seal=read(BASE/'results/fit-freeze.json');ss=read(BASE/'evidence/sections.json.gz');models=[];rows=[];began=time.monotonic()
    for r in seal['selected']:
        s=next(s for s in ss if s['id']==r['section']);v=r['parameters'];c=Scene(v,s,r['hand'],r['mode']);d=evaluate(v,s,r['hand'],r['mode'],True)
        if d['feasible']:
            d['withheld']=assignment(d['predictions'],[z for z in s['observations'] if z['split']=='withheld'],s,blocked=d['train']['used'])
            d['withheld_material']=structure(c,s,held=True);d['physical_accepted']=True;d['geometrically_accepted']=not d['flags']
            d['guard_extension']=dict(guards_each_side=64,positions=c.n,physical=d['contact'],scope='finite local section only')
            d['surface_image']=surface(c,s,r['name']);records=d['train']['records']+d['withheld']['records']
            d['summary']={g:stats([z for z in records if g=='all' or z['split']==g or z['color']==g],s,c.scale) for g in ['all','train','withheld','red','yellow','black']}
            d['construction']=dict(mode=r['mode'],c=c.coefficient,face_diameter_units=2.,axial_height_units=2*c.axial,per_bead_advance_units=c.p['pitch'],per_revolution_advance_units=c.p['pitch']*c.p['turn'],face_diameter_px=2*c.scale,axial_height_scaled_px=2*c.scale*c.axial,local_correction_percent=[float(100*(c.advance/c.p['pitch']-1).min()),float(100*(c.advance/c.p['pitch']-1).max())],string_length=None)
            z=d['secondary'];h=d['withheld_material']
            rows.append(dict(name=r['name'],stage=r['stage'],section=s['id'],mode=r['mode'],hand=r['hand'],c=c.coefficient,axial=c.axial,elevation=c.p['elevation'],face_px=2*c.scale,pitch=c.p['pitch'],loss=d['loss'],train_rms=d['summary']['train']['finite_rms'],held_rms=d['summary']['withheld']['finite_rms'],train_matched=d['summary']['train']['matched'],held_matched=d['summary']['withheld']['matched'],extent_mae=z['dimension_mae'] if z['dimensions'] else None,boundary_mae=z['boundary_mae'],envelope_mae=z['edge_mae'] if z['profiles'] else None,paper=z['paper'],omission=z['material_missing'],held_paper=h['paper'],held_omission=h['material_missing'],valley_mae=h['separator_mae'],positions=z['local_positions'],minimum_margin=d['contact']['minimum_gap_units'],flags=d['flags']))
        else:
            d['reason']=d.get('reason','Failed separating-plane certificate; not a demonstrated collision');d.update(parameters=dict(c.p),hand=r['hand'])
            rows.append(dict(name=r['name'],stage=r['stage'],section=s['id'],mode=r['mode'],hand=r['hand'],rejected=True))
        m=dict(name=r['name'],section=s['id'],kind='R303',stage=r['stage'],result=d);models.append(m);save(BASE/f'results/native-{r["name"]}.json.gz',clean(m))
    for rev in [301,302]:
        for m in read(ROOT/f'photo2/r{rev}/results/native-manifest.json.gz'):
            if rev==302 and m['kind']!='R302':continue
            m['result']['surface_image']=f'../r{rev}/'+m['result']['surface_image'];m['name']=f'R{rev}: '+m['name'];models.append(m)
    save(BASE/'results/native-manifest.json.gz',clean(models));save(BASE/'results/analysis.json',clean(dict(rows=rows,numerical_seconds=seal['numerical_seconds'])))
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (BASE/'results/comparison.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(clean(dict(sections=ss,models=models)),separators=(',',':'))+';\n')
    html=(ROOT/'photo2/review/r302/index.html').read_text().replace('R302 local geometry','R303 height-coupled geometry').replace('R302 · sensitivity-guided local geometry','R303 · height-constrained pitch and transfer').replace('../../R302_REPORT.md','../../R303_REPORT.md')
    html=html.replace('R302 uses native predictions and bounded stitch correction. Parameter and geometry flags are below. Older S1 results are retained unchanged.','R303 compares independent, source c=0.975, and calibrated pitch. Transfer keeps geometry, camera and light shared. Joint fits reopen shared parameters. No model is adopted. All earlier comparisons remain available.')
    html=html.replace('Observed B15 contour (uncertain)','Observed contour / envelope (uncertain)')
    html=html.replace('for(const b of section.bead_dimensions)path(c,b.polygon,true);','for(const b of section.bead_dimensions)path(c,b.polygon,true);for(const p of section.profiles){for(const v of p.bounds){const q=p.point.map((x,i)=>x+v*p.normal[i]);path(c,[-4,4].map(a=>q.map((x,i)=>x+a*p.tangent[i])));}}')
    html=html.replace('<a href="../r301/index.html">Original R301 debugger</a>','<a href="../r301/index.html">Original R301 debugger</a> · <a href="../r302/index.html">Original R302 debugger</a>')
    html=html.replace("document.querySelector('#details').textContent=", "document.querySelector('#metrics').insertAdjacentHTML('beforeend',`<table><tr><th>c</th><th>Bead extent / visible boundary px</th><th>Envelope px</th><th>Paper train / held %</th><th>Colored omission train / held %</th><th>Local positions</th></tr><tr><td>${fmt(r.construction?.c??null)}</td><td>${fmt(r.secondary.dimensions?r.secondary.dimension_mae:null)} / ${fmt(r.secondary.boundary_mae??null)}</td><td>${fmt(r.secondary.profiles?r.secondary.edge_mae:null)}</td><td>${fmt(100*r.secondary.paper)} / ${fmt(100*r.withheld_material.paper)}</td><td>${fmt(100*r.secondary.material_missing)} / ${fmt(100*r.withheld_material.material_missing)}</td><td>${r.local_positions??'historical full chain'}</td></tr></table>`);document.querySelector('#details').textContent=")
    (REVIEW/'index.html').write_text(html)
    launch=REVIEW/'launch.sh';launch.write_text('#!/bin/sh\nset -eu\ncd "$(dirname "$0")/../../.."\nexec .venv/bin/python -m photo2.r303.serve "$@"\n');launch.chmod(0o755)
    save(BASE/'results/export.json',dict(utc=utc(),seconds=time.monotonic()-began,models=len(models),fit_seal_sha256=sha(BASE/'results/fit-freeze.json')))
    for r in rows:print(r)

if __name__=='__main__':main()

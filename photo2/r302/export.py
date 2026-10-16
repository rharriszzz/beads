"""Read-only post-seal native comparison and minimal reuse of the R301 viewer."""
import json
import time
import numpy as np
from PIL import Image
from .core import *
from photo2.r301.export import stats

REVIEW=ROOT/'photo2/review/r302'

def surface(scene,s,name):
    yy,xx=np.mgrid[0:220,0:220];xy=np.c_[xx.ravel(),yy.ravel()]+np.array(s['center'])-110
    tr=scene.camera(xy);ok=tr['owner']>=0;rgba=np.zeros((len(xy),4),np.uint8)
    tone=80+140*np.maximum(tr['normal']@scene.eye,0)
    rgba[ok,:3]=np.c_[tone[ok]*.35,tone[ok]*.85,tone[ok]].astype(np.uint8);rgba[ok,3]=145;rgba[tr['unknown']]=[255,80,220,150]
    filename=f'surface-{name}.png';Image.fromarray(rgba.reshape(220,220,4)).save(REVIEW/filename);return filename

def main():
    seal=read(BASE/'results/fit-freeze.json');s=read(BASE/'evidence/section.json.gz');REVIEW.mkdir(parents=True,exist_ok=True);models=[];started=time.monotonic()
    for selected in seal['selected']:
        v=selected['parameters'];hand=selected['hand'];c=Scene(v,s,hand)
        d=evaluate(v,s,hand,True)
        if not d['feasible']:raise RuntimeError('Selected fit lost feasibility')
        d['withheld']=assignment(d['predictions'],[r for r in s['observations'] if r['split']=='withheld'],s,blocked=d['train']['used'])
        d['withheld_material']=structure(c,s,held=True)
        d['physical_accepted']=d['contact']['certified'];d['geometrically_accepted']=not d['flags']
        d['guard_extension']=dict(guards_each_side=64,positions=c.n,physical=d['contact'],scope='finite section only; not a complete necklace certificate')
        d['surface_image']=surface(c,s,selected['name']);records=d['train']['records']+d['withheld']['records']
        d['summary']={g:stats([z for z in records if g=='all' or z['split']==g or z['color']==g],s,c.scale) for g in ['all','train','withheld','red','yellow','black']}
        d['construction']=dict(conditional_count=2000,twist_bead_equivalents=2000*(6.5/c.p['turn']-1),local_extension_percent=[float(100*(c.advance/c.p['pitch']-1).min()),float(100*(c.advance/c.p['pitch']-1).max())],face_diameter_px=2*c.scale,axial_width_px=2*c.scale*c.axial)
        m=dict(name=selected['name'],section='S1',kind='R302',result=d);models.append(m);save(BASE/f'results/native-{selected["name"]}.json.gz',m)
    # Old scientific outputs are not rewritten or refitted; all S1 comparisons
    # remain available, including rejected and dimensionally worse hypotheses.
    for m in read(ROOT/'photo2/r301/results/native-manifest.json.gz'):
        if m['section']!='S1':continue
        m['result']['surface_image']='../r301/'+m['result']['surface_image']
        m['name']='R301-view: '+m['name'];models.append(m)
    save(BASE/'results/native-manifest.json.gz',models)
    (REVIEW/'data.js').write_text('const DATA='+json.dumps(dict(sections=[s],models=models),separators=(',',':'))+';\n')
    html=(ROOT/'photo2/review/r301/index.html').read_text()
    html=html.replace('R301 local geometry','R302 local geometry').replace('R301 · randomized local inverse geometry','R302 · sensitivity-guided local geometry').replace('../../R301_REPORT.md','../../R302_REPORT.md')
    html=html.replace("M.value='joint-h1-'+S.value;",'M.selectedIndex=0;')
    html=html.replace('<p><select id="section">','<p>R302 uses native predictions and bounded stitch correction. Parameter and geometry flags are below. Older S1 results are retained unchanged. <a href="../r301/index.html">Original R301 debugger</a></p><p><select id="section">')
    html=html.replace('parameters:r.parameters,physical:r.contact','parameters:r.parameters,contradiction_flags:r.flags,geometrically_accepted:r.geometrically_accepted,construction:r.construction,physical:r.contact')
    html=html.replace("'extended local certificate only'","'extended local certificate only; '+(r.flags?.join('; ')||'check structural evidence')")
    html=html.replace('<button id="previous">','<label><input id="observed" type="checkbox">Observed B15 contour (uncertain)</label><button id="previous">')
    html=html.replace("c.fillStyle='#35ff79';", "if(document.querySelector('#observed').checked){c.strokeStyle='#ffb84d';c.lineWidth=2;c.setLineDash([4,4]);for(const b of section.bead_dimensions)path(c,b.polygon,true);c.setLineDash([])}c.fillStyle='#35ff79';")
    html=html.replace("['surfaces','wire','alternatives','centers']", "['surfaces','wire','alternatives','centers','observed']")
    (REVIEW/'index.html').write_text(html)
    launch=REVIEW/'launch.sh';launch.write_text('#!/bin/sh\nset -eu\ncd "$(dirname "$0")/../../.."\nexec .venv/bin/python -m photo2.r302.serve "$@"\n');launch.chmod(0o755)
    save(BASE/'results/export.json',dict(utc=utc(),seconds=time.monotonic()-started,models=len(models),fit_seal_sha256=sha(BASE/'results/fit-freeze.json'),optimization=False))

if __name__=='__main__':main()

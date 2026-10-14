"""Shared distant-light diagnostic on frozen physical geometry and ownership."""
import argparse,gzip,json
import numpy as np
from .reconstruct_r278 import OUT,ROOT,observations,Evidence,Scene,grid,shade,bright_prediction,stats,save,sha


def fit_light(name):
    doc=json.loads((OUT/(name+'.json')).read_text())
    if doc['phase1_sha256']!=sha(OUT/'phase1-inventory.json.gz'):raise ValueError('Model belongs to a different frozen inventory')
    s=Scene(doc['base'],np.array(doc['p']));rows=observations();fixed=[]
    for split in ('train','holdout','buffer'):
        ev=Evidence([r for r in rows if r['split']==split],48);_,a=ev.evaluate(s)
        fixed.extend((r,int(k)) for r,k in zip(ev.rows,a['owners']) if r['specular_candidate'])
    data=s.camera(grid(s));owners={k for r,k in fixed if k>=0};take=np.isin(data['owner'],list(owners));data={k:v[take] for k,v in data.items()}
    foot={k:np.flatnonzero(data['owner']==k) for k in owners};trials=[]
    def evaluate(az,el):
        a,e=np.radians([az,el]);light=dict(direction=[float(np.cos(e)*np.cos(a)),float(np.cos(e)*np.sin(a)),float(np.sin(e))],roughness_deg=6.)
        response=shade(s,data,light);pred={k:bright_prediction(data['xy'][ix],response['specular'][ix],2) for k,ix in foot.items()};records=[]
        for r,k in fixed:
            h=pred.get(k);error=float(np.linalg.norm(np.array(h['centroid'])-r['bright_shape']['centroid'])) if h else 30.
            records.append(dict(id=r['id'],color=r['color'],split=r['split'],owner=k,error_px=error,missing=h is None,predicted=h['centroid'] if h else None))
        objective=float(np.mean([min(r['error_px'],30)**2 for r in records if r['color']=='yellow' and r['split']=='train']))
        trials.append(dict(azimuth=az,elevation=el,objective=objective,light=light))
        return objective,records,light
    best=None
    for az in (-150,-60,30,120):
        for el in (40,60,80):
            value,records,illum=evaluate(az,el)
            if best is None or value<best[0]:best=(value,records,illum,az,el)
    for delta in (12,6):
        az,el=best[3:]
        for da,de in ((delta,0),(-delta,0),(0,delta),(0,-delta)):
            aa,ee=az+da,float(np.clip(el+de,15,88));value,records,illum=evaluate(aa,ee)
            if value<best[0]:best=(value,records,illum,aa,ee)
    metrics={}
    for split in ('train','holdout'):
        for color in ('yellow','red','black'):
            rr=[r for r in best[1] if r['split']==split and r['color']==color]
            metrics[split+'/'+color]=dict(**stats([r['error_px'] for r in rr]),missing=sum(r['missing'] for r in rr))
    result=dict(model=name,light=best[2],trials=trials,records=best[1],metrics=metrics,
                protocol='20 equal-budget direction trials; train yellow only, fixed geometry and split-specific one-to-one positive-interior owners; shared light transfers to red/black; 30px explicit missing sentinel; no heldout tuning',
                limitations='2px raster, fixed 6 degree lobe, historical warm start; neither radiometric fit nor measured lamp position')
    save(OUT/(name+'-light.json'),result);pov(name,s,best[2]);print(name,metrics,flush=True)


def pov(name,s,illum):
    source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
    with gzip.open(OUT/(name+'-correspondence.json.gz'),'rt') as f:ledger=json.load(f)
    colors={b['candidate_index']:b['color'] if b['status']=='confident conditional match' else 'unknown' for b in ledger['beads']}
    palette={'red':[.55,.025,.045],'yellow':[.9,.55,.035],'black':[.012,.012,.016],'unknown':[.25,.30,.36]}
    vec=lambda x:'<'+','.join(f'{v:.12g}' for v in x)+'>'
    view=s.model.view;r,d,e=view.basis();width,height=2540,3182
    center=r*(width/2-view.tx)/view.scale+d*(height/2-view.ty)/view.scale
    text=['#version 3.7;','global_settings { assumed_gamma 1.0 }',f'#declare bead_radius={s.radius:.16g};','#declare hole_size_per_bead_size=.14;',macro]
    if view.focal:raise ValueError('POV exporter currently orthographic only; do not mislabel a perspective view')
    text.append('camera { orthographic location '+vec(center+e*1000)+' direction '+vec(-e*1000)+' right '+vec(r*width/view.scale)+' up '+vec(-d*height/view.scale)+' }')
    text.append('light_source { '+vec(np.array(illum['direction'])*10000)+' color rgb <1,1,1> parallel point_at <0,0,0> }')
    text.append('background { color rgb <.8,.8,.8> }')
    for c,v in palette.items():
        text.append(f'#declare mat_{c}=material {{ texture {{ pigment {{ color rgb {vec(v)} }} finish {{ ambient .12 diffuse .65 specular .6 roughness .035 }} }} }};')
        text.append(f'#declare bead_{c}=bead(mat_{c},.8,.7,1.0);')
    for k in range(len(s.centers)):
        matrix=np.r_[s.g['surface_normal'][k],s.g['surface_tangent'][k],-s.g['surface_binormal'][k],s.centers[k]]
        text.append('object { bead_'+colors[k]+' matrix '+vec(matrix)+' }')
    (OUT/(name+'.pov')).write_text('\n'.join(line.rstrip() for line in '\n'.join(text).splitlines()).rstrip()+'\n')
    save(OUT/(name+'-pov-provenance.json'),dict(source_sha256=sha(ROOT/'beads.pov'),geometry='literal source CSG macro with explicit intended radius and all saved 3D transforms',materials='illustrative shared materials; unknown indices gray',lighting=illum))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();fit_light(a.name)

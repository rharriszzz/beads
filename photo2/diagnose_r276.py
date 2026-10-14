"""R276 physical correction, empirical control, sensitivity and POV-Ray export."""
from __future__ import annotations
import argparse, copy, gzip, json
import numpy as np
from scipy.optimize import least_squares
from .reconstruct_r276 import *
from .bead_debugger.surface import EXTRA,ROUND,STRETCH
from curved_surface_fit import sdf


def correction():
    rows,_=observation_data(False);doc=json.loads((OUT/'joint_refined.json').read_text());base=doc['base'];base['uniform_material']=True
    p=np.array(doc['p']);ev=Evaluation(base,rows,step=3)
    save_model('uniform_before',base,p,dict(reason='Remove inherited +/-11% material-speed irregularity; no new fit parameters'))
    # Separate phase/material registration, bend, strain and twist remain bounded.
    q,log=pattern_fit(ev,p,list(range(22)),budget=177);save_model('uniform_joint',base,q,log)
    fine=Evaluation(base,rows,step=2);q,log=pattern_fit(fine,q,[0,1,2,3,12,13,14,15,19,20,21],budget=89)
    save_model('uniform_refined',base,q,log)


def collision_audit(s,ntheta=32,naz=16,include_flats=False):
    theta=np.linspace(0,2*np.pi,ntheta,endpoint=False);az=np.linspace(0,2*np.pi,naz,endpoint=False)
    radial=.57*RADIUS+EXTRA*np.sign(np.cos(theta))+ROUND*np.cos(theta)
    axial=(EXTRA*np.sign(np.sin(theta))+ROUND*np.sin(theta))*STRETCH
    if include_flats:
        flat=np.linspace(-EXTRA,EXTRA,max(3,ntheta//4))
        radial=np.r_[radial,.57*RADIUS+flat,.57*RADIUS+flat,np.full(len(flat),RADIUS),np.full(len(flat),.14*RADIUS)]
        axial=np.r_[axial,np.full(len(flat),(EXTRA+ROUND)*STRETCH),np.full(len(flat),-(EXTRA+ROUND)*STRETCH),flat*STRETCH,flat*STRETCH]
    aa,tt=np.meshgrid(az,np.arange(len(radial)));local=np.c_[axial[tt.ravel()],radial[tt.ravel()]*np.cos(aa.ravel()),radial[tt.ravel()]*np.sin(aa.ravel())]
    result={};g=s.g;n=len(s.centers)
    for delta in (1,6,7):
        mins=[]
        for start in range(0,n,64):
            ix=np.arange(start,min(start+64,n));other=(ix+delta)%n
            points=s.centers[ix,None,:]+local[None,:,0,None]*g['tangent'][ix,None,:]+local[None,:,1,None]*g['normal'][ix,None,:]+local[None,:,2,None]*np.array([0,0,1])
            q=points-s.centers[other,None,:];loc=np.stack([np.sum(q*g['tangent'][other,None,:],axis=2),np.sum(q*g['normal'][other,None,:],axis=2),q[:,:,2]],axis=2)
            mins.extend(sdf(loc.reshape(-1,3)).reshape(len(ix),-1).min(1).tolist())
        result[str(delta)]=dict(sampled_pairs=n,penetrating_pairs=sum(x<-.001 for x in mins),minimum_sdf_units=min(mins),pair_minimum_sdf=mins)
    return dict(method=f'{len(local)} exact rounded-profile surface samples per bead into +1,+6,+7 neighbor SDF; explicit flat-face sampling={include_flats}; one-sided sampled lower-bound detection, not exhaustive noninterpenetration proof',families=result)


def empirical(s,records):
    # Tangent and outward major-normal projected directions carry local orientation.
    # Coordinates normalized by literal bead diameter; no fixed image displacement.
    frames={};train=[];targets=[];records=copy.deepcopy(records)
    for r in records:
        if r['owner']<0 or r['observed_bright_centroid'] is None:continue
        k=r['owner'];c=s.centers[k];view=s.model.view
        T=(view.project((c+s.g['tangent'][k])[None])[0]-s.pc[k])*(2*.7*RADIUS)
        R=(view.project((c+s.g['radial'][k])[None])[0]-s.pc[k])*(2*RADIUS)
        F=np.stack([T,R],axis=1)
        if abs(np.linalg.det(F))<20:continue
        frames[r['id']]=F
        if r['color']=='yellow' and r['specular_candidate'] and r['split']=='train':
            targets.append(np.linalg.solve(F,np.array(r['observed_bright_centroid'])-s.pc[k]));train.append(r['id'])
    target=np.array(targets);coef=np.median(target,axis=0);out=[]
    for r in records:
        if r['id'] not in frames:continue
        pred=s.pc[r['owner']]+frames[r['id']]@coef
        out.append(dict(id=r['id'],color=r['color'],split=r['split'],specular_candidate=r['specular_candidate'],predicted=pred.tolist(),error=float(np.linalg.norm(pred-r['observed_bright_centroid']))))
    metrics={}
    for split in ('train','holdout'):
        for col in ('yellow','red','black'):
            metrics[split+'/'+col]=stats([r['error'] for r in out if r['split']==split and r['color']==col and r['specular_candidate']])
    predicted_owners=s.camera(np.array([r['predicted'] for r in out]))['owner'] if out else []
    by_id={r['id']:r for r in records}
    for r,k in zip(out,predicted_owners):r['predicted_inside_assigned_surface']=bool(k==by_id[r['id']]['owner'])
    excluded=[dict(id=r['id'],reason='No conditional owner or nearly singular projected tangent/radial frame') for r in records if r['id'] not in frames]
    return dict(excluded=excluded,normalized_offset=coef.tolist(),training_ids=train,training_scatter=np.cov(target.T).tolist(),metrics=metrics,records=out,
        limitation='Geometry-conditioned empirical control. Excludes singular projected local frames explicitly; compare only paired valid IDs. Not proof of light direction or full silhouette.')


def diagnostics(name):
    doc=json.loads((OUT/(name+'.json')).read_text());p=np.array(doc['p']);s=scene(doc['base'],p)
    with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
    save(OUT/(name+'-collisions.json'),collision_audit(s));emp=empirical(s,a['records'])
    # Paired physical score, so excluded empirical singularities cannot help its comparison.
    ids={r['id'] for r in emp['records']};paired={}
    for split in ('train','holdout'):
        for col in ('yellow','red','black'):
            paired[split+'/'+col]=stats([r['highlight_error'] for r in a['records'] if r['id'] in ids and r['split']==split and r['color']==col and r['specular_candidate']])
    emp['paired_physical_metrics']=paired;save(OUT/(name+'-empirical.json'),emp)
    rows,_=observation_data(False);ev=Evaluation(doc['base'],rows,step=2);sensitivity=[]
    for j,values in [(19,(-10,-5,0,5,10)),(20,(-10,-5,0,5,10)),(21,(-4,-2,0,2,4))]:
        for value in values:
            q=p.copy();q[j]=np.clip(q[j]+value,2 if j==21 else -360,18 if j==21 else 89 if j==20 else 360)
            sensitivity.append(dict(parameter=NAMES[j],delta=value,value=float(q[j]),train_objective=ev.evaluate(q)))
    save(OUT/(name+'-light-sensitivity.json'),sensitivity)
    # Material-normalized intensity and shape validation always includes failures.
    summary={}
    for split in ('train','holdout'):
        for col in ('yellow','red','black'):
            rr=[r for r in a['records'] if r['split']==split and r['color']==col and r['specular_candidate']]
            summary[split+'/'+col]=dict(n=len(rr),brightness_absolute_relative=stats([abs(r['relative_brightness_error']) for r in rr]),
                shape_sigma_px=stats([r['shape_sigma_error'] for r in rr if 'shape_sigma_error' in r]),
                shape_angle_deg=stats([r['shape_orientation_error_deg'] for r in rr if r.get('shape_orientation_reliable')]),
                missing=sum(r['missing_highlight'] for r in rr))
    save(OUT/(name+'-shape-brightness.json'),summary)
    export_pov(name,s,doc['light'],a['records'])


def export_pov(name,s,illum,records):
    source=(ROOT/'beads.pov').read_text();macro=source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
    # Same literal source CSG dimensions. Gray bodies lack confirmed model color.
    colors={};palette={'red':[.55,.025,.045],'yellow':[.9,.55,.035],'black':[.012,.012,.016],'unknown':[.25,.30,.36]}
    for r in records:
        if r['owner']>=0:colors.setdefault(r['owner'],set()).add(r['color'])
    vector=lambda x:'<'+','.join(f'{v:.10g}' for v in x)+'>'
    view=s.model.view;r,d,e=view.basis();width,height=2540,3182
    center=r*(width/2-view.tx)/view.scale+d*(height/2-view.ty)/view.scale
    text=['#version 3.7;','global_settings { assumed_gamma 1.0 }',f'#declare bead_radius={RADIUS:.14g};','#declare hole_size_per_bead_size=.14;',macro]
    text.append('camera { orthographic location '+vector(center+e*1000)+' direction '+vector(-e*1000)+' right '+vector(r*width/view.scale)+' up '+vector(-d*height/view.scale)+' }')
    text.append('light_source { '+vector(np.array(illum['direction'])*10000)+' color rgb <1,1,1> parallel point_at <0,0,0> }')
    text.append('background { color rgb <.8,.8,.8> }')
    for namecol,col in palette.items():
        # Appearance only: POV specular differs from positional Blinn diagnostic.
        text.append(f'#declare mat_{namecol}=material {{ texture {{ pigment {{ color rgb {vector(col)} }} finish {{ ambient .12 diffuse .65 specular .6 roughness .035 }} }} }};')
        text.append(f'#declare bead_{namecol}=bead(mat_{namecol},.8,.7,1.0);')
    for k in range(len(s.centers)):
        cs=colors.get(k,set());col=next(iter(cs)) if len(cs)==1 else 'unknown'
        # Source hole axis y maps to tangent; x maps to major normal, z unchanged.
        matrix=np.r_[s.g['normal'][k],s.g['tangent'][k],[0,0,1],s.centers[k]]
        text.append(f'object {{ bead_{col} matrix '+vector(matrix)+' }')
    (OUT/(name+'.pov')).write_text('\n'.join(line.rstrip() for line in '\n'.join(text).splitlines()).rstrip()+'\n')
    save(OUT/(name+'-pov-provenance.json'),dict(source_sha256=sha(ROOT/'beads.pov'),macro='literal #macro bead from source',
        geometry='all 3D centers and local hole axes from saved R276 fit',light='same single distant direction',
        materials='display assumptions; POV appearance is not the quantitative radiometric fit',colors='conditional observation ownership; unknown/conflicting bodies gray'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['correction','diagnostics','mixed','metric','packing','screens','checks','contact']);ap.add_argument('--name',default='joint_refined');args=ap.parse_args()
    if args.stage=='correction':correction()
    elif args.stage=='mixed':mixed_correction()
    elif args.stage=='metric':metric_fit()
    elif args.stage=='packing':packing_fits()
    elif args.stage=='screens':structural_screens()
    elif args.stage=='contact':contact_fit()
    elif args.stage=='checks':
        fixed_and_normals(args.name);convergence(args.name);color_transfer(args.name);ray_termination(args.name)
    else:diagnostics(args.name)



# Callable separately so an expensive fit is never relaunched by report generation.
def fixed_and_normals(name):
    doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']))
    with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
    reference='initial' if (doc['base']['n'],doc['base']['h'])==(2696,1) else f"packing_N{doc['base']['n']}_h{doc['base']['h']:+d}"
    reference_doc=json.loads((OUT/(reference+'.json')).read_text())
    assert (reference_doc['base']['n'],reference_doc['base']['h'])==(doc['base']['n'],doc['base']['h']), 'Cannot equate indices across count/hand hypotheses'
    with gzip.open(OUT/(reference+'-audit.json.gz'),'rt') as f:initial=json.load(f)
    frozen={r['id']:r['owner'] for r in initial['records']};data=np.load(OUT/(name+'-surfaces.npz'));rows=[]
    obs,_=observation_data(False);omap={r['id']:r for r in obs};native=s.camera(np.array([r['observed_peak'] for r in a['records']]))
    implied=[]
    for j,r in enumerate(a['records']):
        k=frozen[r['id']];ix=np.flatnonzero(data['owner']==k) if k>=0 else []
        ratio=doc['base'].get('yellow_diffuse_ratio',0) if r['color']=='yellow' else 0
        h=bright_prediction(data['xy'][ix],data['specular'][ix]+ratio*data['diffuse'][ix],2) if len(ix) else None
        error=float(np.linalg.norm(np.array(h['centroid'])-r['observed_bright_centroid'])) if h and r['observed_bright_centroid'] else 30.
        rows.append(dict(id=r['id'],color=r['color'],split=r['split'],specular_candidate=r['specular_candidate'],initial_owner=k,final_owner=r['owner'],owner_changed=k!=r['owner'],fixed_owner_highlight_error=error,missing=h is None))
        if r['specular_candidate']:
            normal=native['normal'][j];v=native['viewer'][j];ell=unit(2*np.dot(normal,v)*normal-v)
            valid=int(native['owner'][j])==r['owner'] and r['owner']>=0
            angle=float(np.degrees(np.arccos(np.clip(np.dot(ell,doc['light']['direction']),-1,1)))) if valid else None
            implied.append(dict(id=r['id'],color=r['color'],split=r['split'],valid_conditional_owner=valid,implied_light=ell.tolist() if valid else None,angular_disagreement_deg=angle,
                                reason='Mirror-normal diagnostic at observed brightest pixel, conditional on geometry; rough/diffuse peaks need not satisfy it'))
    metrics={}
    for split in ('train','holdout'):
        for col in ('yellow','red','black'):
            rr=[r for r in rows if r['split']==split and r['color']==col and r['specular_candidate']]
            metrics[split+'/'+col]=dict(highlight=stats([r['fixed_owner_highlight_error'] for r in rr]),changed=sum(r['owner_changed'] for r in rr),n=len(rr))
    save(OUT/(name+'-fixed-correspondence.json'),dict(reference_model=reference,metrics=metrics,records=rows));save(OUT/(name+'-implied-light.json'),implied)


def packing_fits():
    rows,_=observation_data(False);results=[]
    for n,h in [(2696,1),(1950,-1),(1950,1)]:
        base=initial_base(n,h);base.update(uniform_material=True,rope_radius=4.55,phase_harmonics=[0]*4,local=[])
        starts=[]
        for phase in np.linspace(-np.pi,np.pi,8,endpoint=False):
            b=copy.deepcopy(base);b['phase']=float(phase);ev=Evaluation(b,rows);starts.append((ev.evaluate(DEFAULT),b))
        score,base=min(starts,key=lambda z:z[0]);ev=Evaluation(base,rows);p,trials=fit_light(ev,DEFAULT,budget=35)
        p,log=pattern_fit(ev,p,[0,1,12,13,14,15,19,20],budget=49)
        name=f'packing_N{n}_h{h:+d}';save_model(name,base,p,dict(**log,light_starts=trials,phase_scores=[v for v,b in starts],scope='packing control: same screen budget, wider structural hypothesis, not adopted'))
        results.append(dict(id=name,objective=log['objective']));save(OUT/'packing-fit-summary.json',results)


def convergence(name):
    doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']))
    with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
    obs,_=observation_data(False);omap={r['id']:r for r in obs};selected=[]
    for sector in range(16):
        for col in ('yellow','red','black'):
            rr=sorted([r for r in a['records'] if r['color']==col and r['specular_candidate'] and omap[r['id']]['sector']==sector],key=lambda r:r['id'])
            if rr:selected.append(rr[0])
    out=[]
    for r in selected:
        k=r['owner']
        if k<0:out.append(dict(id=r['id'],owner=k,missing=True));continue
        grid=s.grid(s.box([k]),1);ix=grid['owner']==k;d={key:v[ix] for key,v in grid.items()}
        val=shade(s,d,doc['light']);ratio=doc['base'].get('yellow_diffuse_ratio',0) if r['color']=='yellow' else 0
        h=bright_prediction(d['xy'],val['specular']+ratio*val['diffuse'],1)
        delta=float(np.linalg.norm(np.array(h['centroid'])-r['predicted']['centroid'])) if h and r['predicted'] else None
        observed=r['observed_bright_centroid'];out.append(dict(id=r['id'],owner=k,color=r['color'],split=r['split'],native_prediction=h,
            coarse_prediction=r['predicted'],coarse_native_displacement=delta,native_photo_error=float(np.linalg.norm(np.array(h['centroid'])-observed)) if h else 30,
            native_outline_pixels=d['xy'].tolist(),missing=h is None))
    with gzip.open(OUT/(name+'-native-convergence.json.gz'),'wt') as f:json.dump(dict(records=out,centroid_grid_difference=stats([r['coarse_native_displacement'] for r in out if r.get('coarse_native_displacement') is not None]),
        missing=sum(r['missing'] for r in out),selection='first source ID per color in each of 16 geographic sectors, no residual selection'),f)


def material_control(name):
    """One shared diffuse/specular ratio for yellow; never a per-bead lamp/gain.

    Conditional owners and geometry are frozen. Optimize training peak-centroid
    scores only, evaluate heldout once. Tests diffuse contamination of yellow maxima.
    """
    from scipy.optimize import minimize_scalar
    doc=json.loads((OUT/(name+'.json')).read_text())
    with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
    data=np.load(OUT/(name+'-surfaces.npz'));rows=[r for r in a['records'] if r['color']=='yellow' and r['specular_candidate']]
    domains={r['id']:np.flatnonzero(data['owner']==r['owner']) if r['owner']>=0 else np.array([],int) for r in rows}
    def predict(r,ratio):
        ix=domains[r['id']];h=bright_prediction(data['xy'][ix],data['specular'][ix]+ratio*data['diffuse'][ix],2)
        return h,float(np.linalg.norm(np.array(h['centroid'])-r['observed_bright_centroid'])) if h else 30.
    def loss(ratio):return np.mean([min(predict(r,ratio)[1],30)**2 for r in rows if r['split']=='train'])
    control=[dict(ratio=v,train_mse=float(loss(v))) for v in (0,.05,.1,.25,.5,1.,2.,4.)]
    best=min(control,key=lambda v:v['train_mse']);fitted=minimize_scalar(loss,bounds=(max(0,best['ratio']/2),max(.1,best['ratio']*2)),method='bounded',options={'maxiter':20})
    ratio=float(fitted.x) if fitted.fun<best['train_mse'] else best['ratio'];out=[]
    for r in rows:
        h,error=predict(r,ratio);out.append(dict(id=r['id'],split=r['split'],ratio=ratio,error=error,pure_specular_error=r['highlight_error'],prediction=h))
    save(OUT/(name+'-diffuse-control.json'),dict(ratio=ratio,grid_controls=control,records=out,metrics={split:dict(mixed=stats([r['error'] for r in out if r['split']==split]),pure=stats([r['pure_specular_error'] for r in out if r['split']==split])) for split in ('train','holdout')},
         limitation='Shared yellow diffuse/specular mixture conditional on frozen geometry/light; not a reflectance measurement or a new light source'))


def mixed_correction():
    rows,_=observation_data(False);doc=json.loads((OUT/'uniform_refined.json').read_text());base=doc['base']
    # Ratio comes from training-only diffuse control at frozen light-only baseline.
    # Subsequent holdouts are exploratory because prior outcomes are already known.
    ratio=json.loads((OUT/'light_only-diffuse-control.json').read_text())['ratio']
    base.update(yellow_diffuse_ratio=ratio,black_reflection_weight=.5)
    ev=Evaluation(base,rows,step=3);p,trials=fit_light(ev,np.array(doc['p']),budget=45)
    save_model('mixed_light',base,p,dict(trials=trials,reason='Yellow brightness can be diffuse-dominated; black training reflections constrain the SAME lamp at half weight'))
    q,log=pattern_fit(ev,p,[0,1,2,3,4,5,8,9,12,13,14,15,19,20,21],budget=121)
    save_model('mixed_joint',base,q,log)


def metric_fit():
    rows,_=observation_data(False);doc=json.loads((OUT/'uniform_refined.json').read_text());base=copy.deepcopy(doc['base']);size=.85
    base['knots']=(np.array(base['knots'])/size).tolist();base['camera']['scale']*=size;base['rope_radius']=4/size
    base['metric_calibration']='Photographic bead-size sensitivity: same literal source bead; centerline/rope coordinates expanded by1/.85, camera scale reduced by.85; fixed length within this hypothesis'
    ev=Evaluation(base,rows,step=3);p=np.array(doc['p']);save_model('metric_before',base,p,dict(reason=base['metric_calibration']))
    q,trials=fit_light(ev,p,budget=45);q,log=pattern_fit(ev,q,list(range(22)),budget=133)
    save_model('metric_refined',base,q,dict(**log,light_trials=trials))


def color_transfer(name):
    doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']))
    with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
    rows,_=observation_data(False);rmap={r['id']:r for r in rows};training_colors={r['owner']:r['color'] for r in a['records'] if r['split']=='train' and r['owner']>=0}
    allpts=np.concatenate([pixels(rmap[r['id']]['region_runs']) for r in a['records']]);owners=s.camera(allpts)['owner'];offset=0;out=[]
    for r in a['records']:
        count=r['positive_pixels'];own=owners[offset:offset+count];offset+=count
        known=np.array([k in training_colors for k in own]);bad=np.array([k in training_colors and training_colors[k]!=r['color'] for k in own])
        out.append(dict(id=r['id'],split=r['split'],color=r['color'],native_pixels=count,training_color_known_pixels=int(known.sum()),contradicting_pixels=int(bad.sum())))
    save(OUT/(name+'-color-transfer.json'),dict(records=out,metrics={split:dict(native_pixels=sum(r['native_pixels'] for r in out if r['split']==split),training_color_known_pixels=sum(r['training_color_known_pixels'] for r in out if r['split']==split),contradicting_pixels=sum(r['contradicting_pixels'] for r in out if r['split']==split)) for split in ('train','holdout','buffer')},
        definition='Colors attached only by training positive-support correspondences. Heldout colors never paint their own prediction in this diagnostic. Unknown-colored predicted surfaces are not counted as correct.'))


def structural_screens():
    rows,_=observation_data(False);large=[];small=[];metric=[]
    for n in (2696,2500,2300,2100,2000,1950,1900):
        for radius in ((4,4.5,5,5.5) if n>=2100 else (4.55,)):
            base=initial_base(n,1);base.update(uniform_material=True,phase_harmonics=[0]*4,local=[],rope_radius=radius)
            a=collision_audit(scene(base,DEFAULT));record=dict(n=n,radius=radius,collisions={k:dict(pairs=v['penetrating_pairs'],min=v['minimum_sdf_units']) for k,v in a['families'].items()})
            (large if n>=2100 else small).append(record)
    save(OUT/'packing-structural-screen.json',large);save(OUT/'packing-lower-count-screen.json',small)
    for size in (1.,.95,.9,.85,.8):
        b=initial_base();b['uniform_material']=True;b['knots']=(np.array(b['knots'])/size).tolist();b['camera']['scale']*=size;b['rope_radius']=4/size;s=scene(b,DEFAULT)
        a=collision_audit(s);v={k:dict(pairs=z['penetrating_pairs'],min=z['minimum_sdf_units']) for k,z in a['families'].items()};score=Evaluation(b,rows).evaluate(DEFAULT)
        metric.append(dict(projected_size_factor=size,source_bead_geometry='unchanged literal dimensions',camera_scale=b['camera']['scale'],reference_length_units=s.model.length,objective=score,collisions=v))
    save(OUT/'metric-calibration-screen.json',metric)





def ray_termination(name):
    doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']));rows,_=observation_data(False)
    pts=np.concatenate([pixels(r['region_runs']) for r in rows]);ids=np.concatenate([np.full(r['area'],j,int) for j,r in enumerate(rows)])
    native=s.camera(pts);bad=np.flatnonzero(native['unknown']>0)
    peak=s.camera(np.array([r['xy'] for r in rows]));grid=np.load(OUT/(name+'-surfaces.npz'));sample=s.camera(grid['xy'])
    save(OUT/(name+'-unfinished-rays.json'),dict(native_positive_total=len(pts),native_unfinished=[dict(id=rows[ids[j]]['id'],xy=pts[j].tolist(),unfinished_candidates=int(native['unknown'][j])) for j in bad],
        brightest_unfinished=[rows[j]['id'] for j in np.flatnonzero(peak['unknown']>0)],
        surface_grid_total=len(grid['xy']),surface_grid_unfinished_xy=grid['xy'][sample['unknown']>0].tolist(),
        treatment='Any unfinished candidate camera ray makes pixel ownership unknown; never assigned as correct. Grazing-shadow unfinished rays treated blocked. No numerical full-convergence claim.'))




def contact_fit():
    rows,_=observation_data(False);doc=json.loads((OUT/'packing_N1950_h-1.json').read_text());base=copy.deepcopy(doc['base'])
    base.update(yellow_diffuse_ratio=json.loads((OUT/'light_only-diffuse-control.json').read_text())['ratio'],black_reflection_weight=.5)
    class ContactEvaluation(Evaluation):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.contact_cache={};self.rejected=0
        def evaluate(self,p,details=False):
            key=tuple(p[:19])
            if key not in self.contact_cache:
                s=self.surfaces(p)[0];a=collision_audit(s,64,32)
                self.contact_cache[key]=min(v['minimum_sdf_units'] for v in a['families'].values())
            clearance=self.contact_cache[key]
            if clearance<.002:
                self.rejected+=1
                return 1000.+max(0,.002-clearance)*1000
            return super().evaluate(p,details)
    ev=ContactEvaluation(base,rows,step=3);p=np.array(doc['p']);p,trials=fit_light(ev,p,budget=35)
    save_model('contact_light',base,p,dict(trials=trials,contact_margin_units=.002,contact_samples_per_bead=2048))
    q,log=pattern_fit(ev,p,[0,1,2,3,4,5,8,9,12,13,14,15,19,20,21],budget=91)
    save_model('contact_joint',base,q,dict(**log,contact_rejections=ev.rejected,contact_margin_units=.002,contact_samples_per_bead=2048,
        scope='Extra-budget physics-selected follow-up; not a fair count-ranking comparison to original screens'))
    a=collision_audit(scene(base,q),128,64);save(OUT/'contact_joint-dense-collisions.json',a)





def full_contact_check(name):
    from collections import Counter
    doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']));a=collision_audit(s,128,64,True)
    pairs=cKDTree(s.centers).query_pairs(2*RADIUS*np.sqrt(1+.7**2),output_type='ndarray');delta=pairs[:,1]-pairs[:,0];delta=np.minimum(delta,len(s.centers)-delta)
    a['all_bounding_sphere_neighbor_families']=dict(Counter(map(str,delta)));save(OUT/(name+'-full-profile-collisions.json'),a)


def confirmed_support():
    evidence=json.loads((ROOT/'photo2/review/r258/bead2-reviewed-support.json').read_text());points=np.array(evidence['patch']);out=[]
    for name in ('initial','light_only','mixed_joint','metric_refined','contact_joint'):
        doc=json.loads((OUT/(name+'.json')).read_text());s=scene(doc['base'],np.array(doc['p']));hit=s.camera(points)
        with gzip.open(OUT/(name+'-audit.json.gz'),'rt') as f:a=json.load(f)
        colors={r['owner']:r['color'] for r in a['records'] if r['split']=='train' and r['owner']>=0}
        out.append(dict(model=name,points=[dict(xy=p.tolist(),conditional_owner=int(k),training_assigned_color=colors.get(int(k),'unknown'),contradicts_confirmed_yellow=bool(k in colors and colors[k]!='yellow')) for p,k in zip(points,hit['owner'])]))
    save(OUT/'maker-B-positive-audit.json',dict(source='R258 maker-confirmed seven yellow B pixels; excluded A remains excluded',source_sha256=sha(ROOT/'photo2/review/r258/bead2-reviewed-support.json'),records=out,
         status='Independent retained confirmation diagnostic; no old-model index2 correspondence inserted into R276 fitting. Unknown model color is not confirmation.'))


if __name__=='__main__':main()

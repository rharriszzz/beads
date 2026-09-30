"""R171: diagnose angle-based neighbor failures without changing the detector.

Replay the pinned R169 program; vary only direction-histogram weights. Appearance
pixels enter detection, followed by every graph variant, before any maker/ID
evaluation. Coordinates in the review figures are diagnostic evidence only.
"""
import argparse,hashlib,json,os,subprocess,types
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_auto_labels import score

ROOT=Path(__file__).resolve().parents[1]
BASELINE='f42b488dfb1bb07782ee2caeb8de4f385d97ab62'
SOURCE_SHA='57855ac1c9c382a2fe03ef4c49e1eb5c181df4aa9cbdd62299116954c01dbbcd'
VARIANTS=[('baseline',None)]+[(f'distance-weight-{p}',f'(spacing/v[2])**{p}') for p in (1,2,4)]+[
    (f'short-mode-{cap}',f'v[2]<=spacing*{cap}') for cap in (1.25,1.5,1.75)]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def modules():
    source=subprocess.check_output(['git','show',BASELINE+':photo2/auto_label_beads.py'],cwd=ROOT).decode()
    assert hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA
    original="angles=np.array([v[5] for v in trial]);hist,_=np.histogram(angles,bins=180,range=(0,180))"
    local="np.histogram(angles[local],bins=180,range=(0,180))"
    assert source.count(original)==source.count(local)==1
    versions={}
    for name,expression in VARIANTS:
        code=source
        if expression:
            code=code.replace(original,"angles=np.array([v[5] for v in trial]);weights=np.array(["+expression+
                " for v in trial],float);hist,_=np.histogram(angles,bins=180,range=(0,180),weights=weights)")
            code=code.replace(local,"np.histogram(angles[local],bins=180,range=(0,180),weights=weights[local])")
        module=types.ModuleType('r171_'+name.replace('-','_'))
        module.__file__=str(ROOT/'photo2/auto_label_beads.py')
        exec(compile(code,module.__file__+'@'+BASELINE+'/'+name,'exec'),module.__dict__)
        versions[name]=module
    return versions


def pair_geometry(result,graph,i,j):
    a,b=result['points'][i],result['points'][j];length=len(result['axis']['xy'])
    ds=(b['station']-a['station']+length/2)%length-length/2;dt=b['cross']-a['cross']
    angle=float(np.degrees(np.arctan2(dt,ds))%180)
    modes={d:(graph['local_direction_modes_degrees'][i][d]+graph['local_direction_modes_degrees'][j][d])/2 for d in ('d1','d2','d3')}
    deviations={d:abs((angle-mode+90)%180-90) for d,mode in modes.items()}
    name=min(deviations,key=deviations.get)
    return dict(start=i,end=j,source_endpoints=[a['source_xy'],b['source_xy']],
        distance_analysis_pixels=float(np.hypot(b['x']-a['x'],b['y']-a['y'])),
        station_delta=float(ds),cross_delta=float(dt),angle_degrees=angle,
        pair_modes=modes,deviations=deviations,closest_family=name,
        passes_angle_gate=deviations[name]<=22,
        proposed=[e for e in graph['edges'] if {e['start'],e['end']}=={i,j}])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r171')
    parser.add_argument('--fixtures',type=Path,default=ROOT/'photo2/output/r167/calibration')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    versions=modules();baseline=versions['baseline']
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
    result=baseline.detect(np.array(image))
    graphs={name:module.adjacency(result) for name,module in versions.items()}
    # Detector and all seven variants are complete; maker evaluation begins here.
    manual=ROOT/'photo2/manual-labels-r169.json'
    doc=json.loads(manual.read_text())
    evaluations={name:baseline.evaluate(result,graph,manual,sha(ROOT/'beads-photo-2.jpg')) for name,graph in graphs.items()}
    mapping={q['number']:q['automatic_point'] for q in evaluations['baseline']['matches']}
    automatic=json.loads((ROOT/'photo2/output/r169/context-first/annotations.json').read_text())
    old=json.loads((ROOT/'photo2/review/r169/summary.json').read_text())
    old_report=ROOT/'photo2/output/r169/context-first/report.json'
    assert graphs['baseline']==json.loads(old_report.read_text())['adjacency']
    assert [p['source_xy'] for p in result['points']]==[[a['x'],a['y']] for a in automatic['annotations']]
    assert evaluations['baseline']==old['after_evaluation']
    assert len(graphs['baseline']['edges'])==old['after_inventory']['candidate_links']
    targets={}
    for number in (10,11,14,16,17):
        i=mapping[number];p=result['points'][i]
        targets[str(number)]=dict(automatic_point=i,source_xy=p['source_xy'],kind=p['kind'],
            automatic_id=automatic['annotations'][i]['id'],maker_id=next(a['id'] for a in doc['annotations'] if a['number']==number),
            ownership='R170 point ownership' if number==10 else 'inside R160-confirmed core' if number in (11,14,17) else 'proximity association; Q171.1 pending')
    cases=[]
    for stem in ['hand+1-palette0-shift0','hand-1-palette0-shift0','hand+1-palette1-shift2']:
        png=args.fixtures/(stem+'.png');ids=args.fixtures/(stem+'-ids.png')
        simulated=baseline.detect(np.array(Image.open(png).convert('RGB')))
        trial_graphs={name:module.adjacency(simulated) for name,module in versions.items()}
        # ID pixels and construction indices are read only after every graph.
        scores={name:score(simulated,graph,ids,312) for name,graph in trial_graphs.items()}
        compact={name:{k:s[k] for k in ('proposals','eligible_visible','eligible_located','on_paper','duplicate_points','adjacency_proposals','true_unsigned_neighbors','per_direction')} for name,s in scores.items()}
        expected=next(c for c in old['calibration_after'] if Path(c['appearance_command'][2][2:]).stem==stem)
        for key in ('proposals','eligible_located','on_paper','duplicate_points','adjacency_proposals','true_unsigned_neighbors'):
            assert compact['baseline'][key]==expected[key],(stem,key)
        cases.append(dict(name=stem,appearance_sha256=sha(png),id_sha256=sha(ids),variants=compact))
    photo={}
    for name,g in graphs.items():
        ev=evaluations[name]
        photo[name]=dict(links=len(g['edges']),forward_links_agree=ev['forward_links_agree'],
            pairs={f'{a}-{b}':pair_geometry(result,g,mapping[a],mapping[b]) for a,b in ((11,14),(14,16),(11,17))},
            supplied_relations=[q for q in ev['relations'] if 14 in (q['start'],q['end'])])
    # Raw plus sparse comparison: lines connect interior points, never boundaries.
    crop=(1225,235,1355,335)
    fig,axes=plt.subplots(1,3,figsize=(13,5),constrained_layout=True)
    for ax,title in zip(axes,['Raw context and maker numbers','Current: 11 to 17, missing 11 to 14','Shorter-pair weights: 11 to 14 restored']):
        ax.imshow(image);ax.set_xlim(crop[0],crop[2]);ax.set_ylim(crop[3],crop[1]);ax.axis('off');ax.set_title(title,fontsize=10)
        for number in (10,11,14,16,17):
            a=next(a for a in doc['annotations'] if a['number']==number)
            ax.text(a['x']+3,a['y']+4,str(number),color='white',fontsize=10,bbox=dict(facecolor='black',alpha=.7,pad=.2))
    for ax in axes[1:]:
        for number in (10,11,14,16,17):
            q=targets[str(number)];ax.plot(*q['source_xy'],'+',color='lime' if q['kind']=='chromatic' else 'cyan',ms=7)
    for ax,name,pairs in [(axes[1],'baseline',[(11,17),(14,16),(10,14),(14,17)]),
                          (axes[2],'distance-weight-2',[(11,14),(10,14),(14,17)])]:
        for a,b in pairs:
            ia,ib=mapping[a],mapping[b]
            accepted=any(e['start']==ia and e['end']==ib for e in graphs[name]['edges'])
            if not accepted:continue
            x,y=targets[str(a)]['source_xy'];xx,yy=targets[str(b)]['source_xy']
            color='orange' if (a,b)==(11,17) else 'deepskyblue' if (a,b)==(11,14) else 'white'
            ax.annotate('',(xx,yy),(x,y),arrowprops=dict(arrowstyle='->',color=color,lw=1.4,alpha=.8))
    x,y=targets['16']['source_xy']
    axes[0].annotate('S',(x,y),xytext=(x+18,y-4),color='cyan',fontsize=13,
        bbox=dict(facecolor='black',alpha=.75,pad=.4),arrowprops=dict(arrowstyle='->',color='cyan',lw=1.3))
    fig.savefig(args.output/'neighbor-comparison.png',dpi=170);plt.close(fig)
    # Show histogram evidence behind the broad d3 peak; no point-label input.
    points=result['points'];xy=np.array([[p['x'],p['y']] for p in points])
    distances,neighbors=baseline.cKDTree(xy).query(xy,k=12)
    spacing=float(np.median(distances[:,1]));length=len(result['axis']['xy']);station=points[mapping[11]]['station']
    angles=[];dsizes=[]
    for i in range(len(points)):
        offset=(points[i]['station']-station+length/2)%length-length/2
        if abs(offset)>=result['axis']['width']*3:continue
        for j,d in zip(neighbors[i,1:],distances[i,1:]):
            if d>spacing*2.3:continue
            ds=(points[j]['station']-points[i]['station']+length/2)%length-length/2
            dt=points[j]['cross']-points[i]['cross']
            if np.hypot(ds,dt)<spacing*.35:continue
            angles.append(np.degrees(np.arctan2(dt,ds))%180);dsizes.append(d)
    angles=np.array(angles);dsizes=np.array(dsizes)
    counts,_=np.histogram(angles,bins=180,range=(0,180))
    weighted,_=np.histogram(angles,bins=180,range=(0,180),weights=(spacing/dsizes)**2)
    fig,ax=plt.subplots(figsize=(9,3),constrained_layout=True)
    for hist,label in [(counts,'All candidate pairs equally weighted'),(weighted,'Weights proportional to inverse squared distance')]:
        smooth=baseline.ndi.gaussian_filter1d(hist.astype(float),5,mode='wrap')
        ax.plot(np.arange(180),smooth/smooth.max(),label=label)
    for pair,label,color in [('11-14','11 to 14','deepskyblue'),('14-16','14 to proposed16','red')]:
        ax.axvline(photo['baseline']['pairs'][pair]['angle_degrees'],color=color,ls='--',label=label)
    ax.set(xlabel='Strip connection angle modulo180 degrees',ylabel='Normalized local support',xlim=(0,180));ax.legend(fontsize=8)
    fig.savefig(args.output/'local-angle-support.png',dpi=160);plt.close(fig)
    summary=dict(request='R171',baseline_commit=BASELINE,detector_sha256=SOURCE_SHA,
        probe_sha256=sha(Path(__file__)),image_sha256=sha(ROOT/'beads-photo-2.jpg'),
        calibration_evaluator_sha256=sha(ROOT/'photo2/check_auto_labels.py'),
        beads_pov_sha256=sha(ROOT/'beads.pov'),annotation_sha256=sha(manual),annotation_revision=doc['revision'],
        r169_report_sha256=sha(old_report),r169_automatic_annotation_sha256=sha(ROOT/'photo2/output/r169/context-first/annotations.json'),
        confirmed_core_sha256=sha(ROOT/'photo2/review/r157/report.json'),
        r160_confirmation_sha256=sha(ROOT/'photo2/interior-confirmed-r160.json'),
        r170_confirmation_sha256=sha(ROOT/'photo2/reflection-confirmed-r170.json'),
        marker_S_maker_number=16,targets=targets,photo=photo,calibration=cases,
        variant_histogram_weights=dict(VARIANTS),analysis_parameters=dict(angle_gate_degrees=22,
            candidate_radius_spacing_factor=2.3,local_window_strip_halfwidth_factor=3,
            scale_xy=result['scale'].tolist(),nearest_spacing_analysis_pixels=spacing),
        conclusion='No variant adopted: recovering11-14 via shorter-pair histograms loses known-render true neighbors. Keep topology alternatives and point roles explicit.',
        limitation='S ownership pending; other associations and synthetic unsigned adjacency scores do not establish physical centers, exposed outward anchors, direction signs or helicity.',
        curated_image_sha256={p.name:sha(p) for p in sorted(args.output.glob('*.png'))})
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(photo={name:dict(links=v['links'],forward=v['forward_links_agree'],
        restored11_14=bool(v['pairs']['11-14']['proposed']),retained14_16=bool(v['pairs']['14-16']['proposed'])) for name,v in photo.items()},
        marker_S=targets['16']),indent=2))


if __name__=='__main__':main()

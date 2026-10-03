"""R208 parallel-path cue transfer and known-ownership evaluation, without fit."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-profile-mpl')
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D

import auto_label_beads as auto
from bead_profile_cues import local_profiles, parallel_cues
from distributed_colored_interiors import detect_distributed_interiors
from practice_centerline_profiles import periodic_route
from label_beads import atomic_json

ROOT=auto.ROOT
COLORS=['#386cb0','#20a060','cyan','#f29922','#993399']


def truth_at(coordinates, labels):
    """Nearest-pixel ownership and agreement of all bilinear contributing pixels."""
    xy=np.asarray(coordinates); height,width=labels.shape
    nearest=np.rint(xy).astype(int)
    valid=(xy[:,0]>=0)&(xy[:,1]>=0)&(xy[:,0]<=width-1)&(xy[:,1]<=height-1)
    owners=np.full(len(xy),-2,int); pure=np.zeros(len(xy),bool)
    for i in np.flatnonzero(valid):
        x,y=nearest[i]; owners[i]=labels[y,x]
        lo=np.floor(xy[i]).astype(int); hi=np.ceil(xy[i]).astype(int)
        values=labels[np.array([lo[1],hi[1]])[:,None],np.array([lo[0],hi[0]])]
        pure[i]=np.all(values==owners[i])
    return owners,pure


def evaluate_profiles(data, labels):
    """Expose in-body landmarks as well as nearby owner changes; no truth tuning."""
    tolerance=data['native_diameter']*.15
    counts={kind:Counter() for kind in ['V trough','hue change','neutral bright feature']}
    persistent={kind:Counter() for kind in counts}
    transitions=Counter(); coverage={kind:Counter() for kind in counts}
    witnesses=[]
    for row in data['records']:
        path=row['paths'][row['base_path_index']]
        owners,pure=truth_at(path['coordinates'],labels)
        boundaries=np.flatnonzero(owners[:-1]!=owners[1:])+.5
        events=path['events']
        for e in events:
            i=e['sample_index']; lo=max(0,int(np.ceil(i-tolerance))); hi=min(len(owners),int(np.floor(i+tolerance))+1)
            local=set(owners[lo:hi].tolist())
            bodies=sorted(n for n in local if n>=0)
            if -2 in local: disposition='outside image'
            elif len(bodies)>=2: disposition='near body transition'
            elif -1 in local and bodies: disposition='near paper transition'
            elif bodies: disposition='within one body'
            else: disposition='paper only'
            counts[e['kind']][disposition]+=1
            if e['matched_paths']>=3: persistent[e['kind']][disposition]+=1
            witnesses.append(dict(observation_number=row['observation_number'],kind=e['kind'],
                sample_index=i,xy=e['xy'],matched_paths=e['matched_paths'],
                disposition=disposition,owner_at_event=int(owners[i]),bilinear_single_owner=bool(pure[i]),
                nearby_owners=sorted(local)))
        for b in boundaries:
            i=int(b); a,c=int(owners[i]),int(owners[i+1])
            if a<0 or c<0: continue
            kind='same palette slot' if a%3==c%3 else 'different palette slots'
            transitions[kind]+=1
            for feature in counts:
                if any(e['kind']==feature and abs(e['sample_index']-b)<=tolerance for e in events):
                    coverage[feature][kind]+=1
    return dict(profiles=len(data['records']),event_counts={k:dict(v) for k,v in counts.items()},
        persistent_event_counts={k:dict(v) for k,v in persistent.items()},
        transition_exposures=dict(transitions),transition_exposures_with_event={k:dict(v) for k,v in coverage.items()},
        tolerance_pixels=tolerance,witnesses=witnesses,
        limits=['Repeated local windows can expose the same physical transition; these are not unique global boundary counts.',
            'Near-transition tolerance is0.15 apparent diameters, not exact edge agreement.',
            'Neutral bright features can occur on colored bodies; this cue never assigns black ownership.',
            'Palette-slot equality uses the known fixture construction owner%3 only after cue extraction.'])


def compact(data):
    rows=[]
    for row in data['records']:
        base=row['paths'][row['base_path_index']]
        rows.append({**{k:row[k] for k in ['observation_number','observation_id','source_xy','appearance_mode','route_fraction','tangent_xy','reference_role']},
            'events':base['events'], 'events_per_path':[len(p['events']) for p in row['paths']],
            'middle_hsv':base['hsv'][len(base['hsv'])//2]})
    groups=[]
    for b in range(20):
        subset=[r for r in rows if min(int(r['route_fraction']*20),19)==b]
        groups.append(dict(bin=b,profiles=len(subset),base_events=len([e for r in subset for e in r['events']]),
            persistent_events=len([e for r in subset for e in r['events'] if e['matched_paths']>=3])))
    return dict(records=rows,native_diameter=data['native_diameter'],offsets_pixels=data['offsets_pixels'],
        bins=groups,source_image_sha256=data['source_image_sha256'],
        role='Feature annex to frozen interior references; no identities, bead outlines or positional shifts inferred')


def plot_profile(image,row,output,title,marks=()):
    paths=row['paths']; base=paths[row['base_path_index']]
    xy=np.array(base['coordinates']); middle=len(xy)//2; distance=np.arange(len(xy))-middle
    origin=xy[middle]; direction=xy[-1]-xy[0]
    transform=Affine2D().rotate_around(*origin,-np.arctan2(direction[1],direction[0]))
    display=transform.transform(np.vstack([p['coordinates'] for p in paths]))
    lo=display.min(axis=0)-25; hi=display.max(axis=0)+25
    fig=plt.figure(figsize=(12,9),layout='constrained')
    axes=fig.subplot_mosaic([['raw','path'],['strip','strip'],['value','value'],['hue','hue'],['neutral','neutral']],
        height_ratios=[2,.6,1.2,1.2,1.2])
    for key in ['raw','path']:
        ax=axes[key]; ax.imshow(image,transform=transform+ax.transData)
        ax.set_xlim(lo[0],hi[0]); ax.set_ylim(hi[1],lo[1]); ax.axis('off')
        ax.set_title('Raw context' if key=='raw' else 'Parallel sampling paths; no bead boundaries')
    for p,color in zip(paths,COLORS):
        coords=transform.transform(p['coordinates']); axes['path'].plot(*coords.T,color=color,lw=.8)
        label=f"{p['offset_pixels']:+.1f}px"
        axes['value'].plot(distance,np.array(p['hsv'])[:,2],color=color,lw=.8,label=label)
        axes['hue'].plot(distance,p['hue_score'],color=color,lw=.8)
        axes['neutral'].plot(distance,p['neutral_score'],color=color,lw=.8)
    axes['strip'].imshow(np.array([p['rgb'] for p in paths]),extent=[distance[0],distance[-1],4.5,-.5],aspect='auto')
    axes['strip'].set_yticks(range(len(paths)),[f"{p['offset_pixels']:+.1f}" for p in paths],fontsize=7)
    axes['strip'].set_ylabel('offset px'); axes['strip'].set_title('RGB sampled on the five paths')
    for e in base['events']:
        key={'V trough':'value','hue change':'hue','neutral bright feature':'neutral'}[e['kind']]
        value={'V trough':e['value'],'hue change':e['hue_score'],'neutral bright feature':e['neutral_score']}[e['kind']]
        axes[key].scatter(e['distance_pixels'],value,s=24,facecolors='black' if e['matched_paths']>=3 else 'none',edgecolors='black')
    for letter,index in marks:
        point=transform.transform(xy[index])
        for key in ['raw','path']:
            axes[key].annotate(letter,point,xytext=(point[0],point[1]-20),color='white',fontsize=11,
                ha='center',bbox=dict(facecolor='black',alpha=.8,pad=2),arrowprops=dict(arrowstyle='->',color='cyan',lw=.8))
        for key in ['value','hue','neutral']: axes[key].axvline(index-middle,color='gray',ls=':',lw=.7)
    for tick in np.linspace(distance[0],distance[-1],5).astype(int):
        point=transform.transform(xy[tick+middle]); axes['path'].text(*point,str(tick),fontsize=7,color='white',
            bbox=dict(facecolor='black',alpha=.6,pad=1))
    axes['value'].set_ylabel('V (0–1)'); axes['hue'].set_ylabel('Weighted hue change')
    axes['neutral'].set_ylabel('V × (1−S)'); axes['neutral'].set_xlabel('Distance on cyan path, native pixels')
    axes['value'].legend(ncol=5,fontsize=8,loc='upper right')
    for key in ['value','hue','neutral']:
        axes[key].set_xlim(distance[0],distance[-1]); axes[key].grid(alpha=.2)
    fig.suptitle(title+'\nFilled dots persist on ≥3 paths; persistence does not establish a seam',fontsize=12)
    fig.savefig(output,dpi=130); plt.close(fig)


def confirmed_example(image,diameter):
    report=json.loads((ROOT/'photo2/review/r203/report.json').read_text())
    right=next(r for r in report['sections'] if r['name']=='right')
    _,xy,normal=periodic_route(json.loads((ROOT/'photo2/spline-seed-r175.json').read_text())['points'])
    indices=np.array(right['sample_indices']); offsets=np.array([-.4,-.2,0.,.2,.4])*diameter
    coordinates=xy[indices][None,:,:]+offsets[:,None,None]*normal[indices][None,:,:]
    result=parallel_cues(np.asarray(image,float)/255,coordinates,diameter,offsets,140)
    base=result['paths'][result['base_path_index']]
    np.testing.assert_allclose(base['coordinates'],right['coordinates'],atol=0,rtol=0)
    np.testing.assert_allclose(base['hsv'],right['hsv'],atol=0,rtol=0)
    measurements=[]
    for p in result['paths']:
        hsv=np.array(p['hsv']); interval=hsv[140:161]; k=int(np.argmin(interval[:,2]))
        measurements.append(dict(offset_pixels=p['offset_pixels'],
            minimum_value_distance_pixels=k,minimum_value=float(interval[k,2]),
            value_dip_fraction=float(1-interval[k,2]/min(interval[0,2],interval[-1,2])),
            endpoint_hue_change_degrees=float((interval[-1,0]*360-interval[0,0]*360+180)%360-180),
            transition_events=[e for e in p['events'] if 0<=e['distance_pixels']<=20],
            reflection_events=[e for e in p['events'] if abs(e['distance_pixels']-109)<=diameter*.15],
            endpoint_xy=[p['coordinates'][140],p['coordinates'][160]],
            endpoint_ownership='Only zero-offset S/Q points maker-confirmed; shifted points unresolved'))
    return result,dict(measurements=measurements,
        scope='Frozen maker S/Q distinction and R black reflection reused only for assisted diagnostic; no region/center/adjacency promotion')


def choose_question(data,modes):
    candidates=[]
    diameter=data['native_diameter']; far=round(diameter*.35)
    for row in data['records']:
        base=row['paths'][row['base_path_index']]; hsv=np.array(base['hsv'])
        for e in base['events']:
            i=e['sample_index']
            if e['kind']!='hue change' or e['matched_paths']<3 or not 8<=abs(e['distance_pixels'])<=diameter: continue
            a,b=i-far,i+far
            if not 0<=a<b<len(hsv): continue
            # Review selection only: same learned appearance family at endpoints,
            # with substantial color. Does not label them as same/different beads.
            ha,hb=hsv[[a,b],0]*360
            nearest=lambda h:int(np.argmin(abs((np.asarray(modes)-h+180)%360-180)))
            if nearest(ha)!=nearest(hb): continue
            if min(hsv[a,1]*hsv[a,2],hsv[b,1]*hsv[b,2])<.35: continue
            distance_hue=abs((hb-ha+180)%360-180)
            if not 6<=distance_hue<=25: continue
            candidates.append((e['matched_paths'],distance_hue,row,e,a,b))
    candidates.sort(key=lambda c:(-c[0],-c[1],c[2]['observation_number']))
    return candidates


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r208')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    protected_paths=json.loads((ROOT/'photo2/review/r201/summary.json').read_text())['protected_inputs']
    protected={p:auto.sha(ROOT/p) for p in protected_paths}
    photo=ROOT/'beads-photo-2.jpg'; image=ImageOps.exif_transpose(Image.open(photo)).convert('RGB')
    inventory=json.loads((ROOT/'photo2/review/r201/interiors.json').read_text())
    assert auto.sha(photo)==inventory['image_sha256']
    visual=json.loads((ROOT/'photo2/review/r201/visual-review.json').read_text())
    assert auto.sha(ROOT/visual['inventory'])==visual['inventory_sha256']
    answers=json.loads((ROOT/'photo2/profile-answers-r204-r205.json').read_text())
    for path,digest in [('report','report_sha256'),('supporting_image','supporting_image_sha256')]:
        assert auto.sha(ROOT/answers[path])==answers[digest]
    data=local_profiles(np.array(image),inventory)
    routine=ROOT/'photo2/output/r208'; routine.mkdir(parents=True,exist_ok=True)
    atomic_json(routine/'photo-profiles.json',data)
    print(json.dumps(dict(stage='photo',profiles=len(data['records']))),flush=True)
    pending=[]; fixture_dir=ROOT/'photo2/output/r167/calibration'
    for name in ['hand+1-palette0-shift0','hand-1-palette0-shift0','hand+1-palette1-shift2']:
        path=fixture_dir/(name+'.png'); rendered=np.array(Image.open(path).convert('RGB'))
        selected=detect_distributed_interiors(rendered,auto.sha(path))
        profiles=local_profiles(rendered,selected); atomic_json(routine/(name+'-profiles.json'),profiles)
        pending.append((name,path,profiles))
        print(json.dumps(dict(stage=name,profiles=len(profiles['records']))),flush=True)
    # Rendered ownership is loaded after all image-only cue extraction.
    calibration=[]
    for name,path,profiles in pending:
        ids=fixture_dir/(name+'-ids.png'); rgb=np.array(Image.open(ids).convert('RGB'),int)
        result=evaluate_profiles(profiles,rgb[:,:,0]+256*rgb[:,:,1]-1)
        calibration.append(dict(fixture=name,appearance_sha256=auto.sha(path),ids_sha256=auto.sha(ids),**result))
    atomic_json(args.output/'calibration.json',calibration)
    summary=compact(data); atomic_json(args.output/'reference-cues.json',summary)
    aggregate={}
    for kind in ['V trough','hue change','neutral bright feature']:
        all_counts=Counter(); persistent_counts=Counter()
        for c in calibration:
            all_counts.update(c['event_counts'][kind]); persistent_counts.update(c['persistent_event_counts'][kind])
        aggregate[kind]=dict(all=dict(all_counts),persistent=dict(persistent_counts),
            photo_base_events=sum(e['kind']==kind for r in summary['records'] for e in r['events']),
            photo_persistent_events=sum(e['kind']==kind and e['matched_paths']>=3 for r in summary['records'] for e in r['events']))
    neutral=[w for c in calibration for w in c['witnesses'] if w['kind']=='neutral bright feature']
    aggregate['neutral_owner_diagnostic']=dict(events=len(neutral),
        on_colored_slot=sum(w['owner_at_event']>=0 and w['owner_at_event']%3!=2 for w in neutral),
        persistent_events=sum(w['matched_paths']>=3 for w in neutral),
        persistent_on_colored_slot=sum(w['matched_paths']>=3 and w['owner_at_event']>=0 and w['owner_at_event']%3!=2 for w in neutral),
        role='Evaluation-only fixture palette slots; neutral brightness is not black ownership')
    atomic_json(args.output/'aggregate.json',aggregate)
    adverse=None
    for c,(name,path,profiles) in zip(calibration,pending):
        candidates=[w for w in c['witnesses'] if w['kind']=='V trough' and w['matched_paths']>=3
            and w['disposition']=='within one body' and w['owner_at_event']%3!=2 and w['bilinear_single_owner']]
        if not candidates: continue
        witness=candidates[0]; row=next(r for r in profiles['records'] if r['observation_number']==witness['observation_number'])
        plot_profile(Image.open(path).convert('RGB'),row,args.output/'adverse-trough.png',
            'Known render: persistent trough F lies within one colored body',[('F',witness['sample_index'])])
        adverse=dict(fixture=name,appearance_sha256=auto.sha(path),witness=witness,
            interpretation='A feature near neither ownership transition within the evaluation tolerance; cause unassigned')
        atomic_json(args.output/'adverse-trough.json',adverse)
        break
    diagnostic,measurements=confirmed_example(image,data['native_diameter'])
    atomic_json(args.output/'confirmed-example.json',measurements)
    atomic_json(routine/'confirmed-profiles.json',diagnostic)
    plot_profile(image,diagnostic,args.output/'confirmed-parallels.png','Confirmed S/Q and R; shifted-path ownership remains unknown',
        [('S',140),('Q',160),('R',249)])
    examples=[]
    for b in [0,5,10,15]:
        subset=[r for r in data['records'] if b<=r['route_fraction']*20<b+5]
        row=max(subset,key=lambda r:sum(e['matched_paths']>=3 for e in r['paths'][r['base_path_index']]['events']))
        name=f"sector-{b//5+1}-A{row['observation_number']}.png"
        plot_profile(image,row,args.output/name,f"A{row['observation_number']}: local strips through an existing interior reference")
        examples.append(dict(image=name,observation_number=row['observation_number']))
    candidates=choose_question(data,inventory['parameters']['inventory']['detector']['hue_modes_degrees'])
    atomic_json(routine/'question-candidates.json',[dict(observation_number=c[2]['observation_number'],
        matched_paths=c[0],endpoint_hue_difference_degrees=c[1],event=c[3],endpoint_indices=[c[4],c[5]]) for c in candidates])
    # First ranked candidate is a proposal to inspect, not an automatic fact.
    if candidates:
        _,_,row,event,a,b=candidates[0]
        plot_profile(image,row,args.output/'question-proposal.png',f"Automatic observation {row['observation_number']}: proposed same-family transition review",[('A',a),('B',b)])
        base=row['paths'][row['base_path_index']]
        question=dict(observation_number=row['observation_number'],observation_id=row['observation_id'],event=event,
            points=[dict(label=letter,sample_index=i,distance_pixels=i-len(base['hsv'])//2,
                xy=base['coordinates'][i],hsv=base['hsv'][i]) for letter,i in [('A',a),('B',b)]],
            status='Curator proposal; inspect raw image before asking maker')
        atomic_json(args.output/'question-proposal.json',question)
    atomic_json(args.output/'examples.json',examples)
    sources=['beads-photo-2.jpg','photo2/bead_profile_cues.py','photo2/review_profile_cues.py',
        'photo2/practice_centerline_profiles.py','photo2/distributed_colored_interiors.py','photo2/auto_label_beads.py',
        'photo2/review/r201/interiors.json','photo2/review/r203/report.json',
        'photo2/profile-answers-r204-r205.json','photo2/spline-seed-r175.json',
        'photo2/review/r201/visual-review.json','photo2/test_profile_cues.py']
    generated=['reference-cues.json','calibration.json','aggregate.json','confirmed-example.json','confirmed-parallels.png','examples.json']
    generated += [r['image'] for r in examples]
    if adverse: generated+=['adverse-trough.png','adverse-trough.json']
    if candidates: generated+=['question-proposal.png','question-proposal.json']
    assert protected=={p:auto.sha(ROOT/p) for p in protected}
    seal=dict(request='R208',source_sha256={p:auto.sha(ROOT/p) for p in sources},protected_inputs=protected,
        curated_sha256={p:auto.sha(args.output/p) for p in sorted(generated)},
        profiles=len(data['records']),bins=summary['bins'],
        calibration=[{k:v for k,v in c.items() if k!='witnesses'} for c in calibration],
        old_observations_unchanged=True,new_body_labels=False,fit_performed=False,
        reproduction='.venv/bin/python photo2/review_profile_cues.py')
    atomic_json(args.output/'summary.json',seal)
    print(json.dumps(dict(calibration=seal['calibration'],question_candidates=len(candidates))),flush=True)


if __name__=='__main__': main()

"""R192: trusted-fact ledger, whole-photo atlas and independent region audit.

Maker facts and synthetic ownership masks are evaluator-only. The inventory
must already exist before they are loaded. No model fitting is performed.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-evidence-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as Polygon
from matplotlib.colors import rgb_to_hsv
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage as ndi

import auto_label_beads as auto
from bead_evidence_inventory import inventory, encode_pixels
from label_beads import atomic_json


def pixels(record):
    return np.array([(x, y) for y, lo, hi in record['pixel_runs'] for x in range(lo, hi+1)])


def calibration(output):
    folder = auto.ROOT/'photo2/output/r167/calibration'
    pending = []
    for hand, palette, shift in [(1, 0, 0), (-1, 0, 0), (1, 1, 2)]:
        name = f'hand{hand:+d}-palette{palette}-shift{shift}'
        appearance = folder/(name+'.png')
        result = inventory(np.array(Image.open(appearance).convert('RGB')))
        pending.append((name, appearance, folder/(name+'-ids.png'), result))
        atomic_json(output/(name+'.json'), result)
    checks = []
    # All candidate decisions finish before loading exact rendered body ownership.
    for name, appearance, ids, result in pending:
        rgb = np.array(Image.open(ids).convert('RGB')).astype(int)
        labels = rgb[:, :, 0]+256*rgb[:, :, 1]-1
        regions = [r for r in result['records'] if r['status']=='region-proposal']
        owners = []; wrong_kind = 0; mixed = []; reflection_mismatch = []
        margins = []
        body_distances = {}
        for row in regions:
            xy = pixels(row['region']); body = np.unique(labels[xy[:, 1], xy[:, 0]])
            if len(body)!=1 or body[0]<0:
                owners.append(None); mixed.append(row['observation_number']); continue
            owner = int(body[0]); owners.append(owner)
            if (owner%3==2) != (row['kind']=='dark-reflection'):
                wrong_kind += 1
            if owner not in body_distances:
                body_distances[owner] = ndi.distance_transform_edt(labels==owner)
            margins.append(float(body_distances[owner][xy[:, 1], xy[:, 0]].min()))
            if row['reflection']:
                x, y = np.rint(row['reflection']['xy']).astype(int)
                if labels[y, x] != owner:reflection_mismatch.append(row['observation_number'])
        known = Counter(o for o in owners if o is not None)
        reflection_rows = [r for r in result['records'] if r.get('reflection')]
        reflection_owners = []
        for row in reflection_rows:
            x,y = np.rint(row['reflection']['xy']).astype(int)
            reflection_owners.append(int(labels[y,x]))
        black_with_reflection = {o for o in reflection_owners if o>=0 and o%3==2}
        # Eligibility is explicit: a substantial visible body supports an inset,
        # and its safest pixels lie away from the approximate search-band edge.
        detector = auto.detect(np.array(Image.open(appearance).convert('RGB')))
        band = detector['band']; band_distance = ndi.distance_transform_edt(band)
        eligible = []
        for owner in np.unique(labels):
            if owner<0:continue
            body = labels==owner
            inset = ndi.distance_transform_edt(body)>=3
            if np.sum(inset)>=12 and np.max(band_distance[inset], initial=0)>=detector['diameter']*.7:
                eligible.append(int(owner))
        checks.append(dict(fixture=name, appearance_sha256=auto.sha(appearance), ids_sha256=auto.sha(ids),
            region_proposals=len(regions), single_body_regions=len(regions)-len(mixed),
            mixed_or_background_regions=mixed, wrong_appearance_kind=wrong_kind,
            reflection_owner_mismatch=reflection_mismatch,
            duplicate_body_regions=sum(n-1 for n in known.values()),
            minimum_true_body_margin=min(margins, default=None),
            eligible_body_count=len(eligible), eligible_located=sum(o in known for o in eligible),
            eligible_colored=sum(o%3!=2 for o in eligible),
            located_colored=sum(o%3!=2 and o in known for o in eligible),
            eligible_black=sum(o%3==2 for o in eligible),
            located_black=sum(o%3==2 and o in known for o in eligible),
            eligible_black_with_reflection=sum(o in black_with_reflection for o in eligible if o%3==2),
            reflection_only_proposals=sum(r['status']=='reflection-only-proposal' for r in result['records']),
            reflection_positions_on_black=sum(o>=0 and o%3==2 for o in reflection_owners),
            reflection_positions_wrong_owner=sum(o<0 or o%3!=2 for o in reflection_owners),
            eligible_missed=[o for o in eligible if o not in known],
            limitation='Evaluator-only synthetic ownership/visibility threshold; not real-photo trust or completeness.'))
    return checks


def trusted_facts(image):
    cores = json.loads((auto.ROOT/'photo2/review/r157/report.json').read_text())
    confirmed = json.loads((auto.ROOT/'photo2/interior-confirmed-r160.json').read_text())
    regions = []
    for row in cores['results']:
        if row['number'] not in confirmed['accepted_numbers']:continue
        loop = np.array(row['loop_xy'])
        lo = np.floor(loop.min(axis=0)).astype(int); hi = np.ceil(loop.max(axis=0)).astype(int)+1
        yy, xx = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]
        mask = Polygon(loop).contains_points(np.column_stack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
        regions.append(dict(maker_number=row['number'], observation_id=row['observation_id'],
            appearance=confirmed['appearance_colors'][str(row['number'])],
            confirmation='maker-confirmed positive interior R160',
            region=dict(loop_xy=row['loop_xy'], pixel_runs=encode_pixels(mask, lo), pixels=int(mask.sum())),
            source='photo2/review/r157/report.json', limits='Positive interior only; no boundary/center/outward point.'))
    targets = json.loads((auto.ROOT/'photo2/review/r171/summary.json').read_text())['targets']
    reflections = [dict(maker_number=n, observation_id=targets[str(n)]['automatic_id'],
                        xy=targets[str(n)]['source_xy'],
                        confirmation='R170 maker point ownership' if n==10 else 'Point inside R160-confirmed black region',
                        limits='Image reflection locator with confirmed body ownership; not a body center or exact optical peak.')
                   for n in [10, 14, 17]]
    point = json.loads((auto.ROOT/'photo2/neighbor-confirmed-r172.json').read_text())
    three = json.loads((auto.ROOT/'photo2/review/r167/summary.json').read_text())['question_observations']
    distinct = [dict(historical_number=int(n), observation_id=v['stable_id'], xy=v['source_xy']) for n,v in three.items()]
    return dict(request='R192', image_sha256=auto.sha(auto.ROOT/'beads-photo-2.jpg'),
        region_facts=regions, black_reflection_point_facts=reflections,
        other_point_facts=[dict(maker_number=16, xy=point['source_xy'], observation_id=point['automatic_observation_id'],
                               confirmation='R172 point ownership only; no new region confirmation')],
        distinct_body_point_group=dict(confirmation='R168: three different beads', observations=distinct,
                                       limits='Distinct identities only; surrounding new region pixels remain unreviewed'),
        diagonal_group=json.loads((auto.ROOT/'photo2/diagonal-confirmed-r189.json').read_text()),
        unresolved_fact=json.loads((auto.ROOT/'photo2/colored-review-answers-r188.json').read_text()),
        complete=False, stage='Trusted existing facts only; automatic proposals cannot enter this ledger by threshold confidence alone.')


def draw(ax, image, records, crop, annotated=False, labels=True, dark=()):
    ax.imshow(image); ax.set_xlim(crop[0], crop[2]); ax.set_ylim(crop[3], crop[1]); ax.axis('off')
    if not annotated:return
    for row in records:
        x,y = row['seed_xy']
        if not crop[0]<=x<=crop[2] or not crop[1]<=y<=crop[3]:continue
        if row['status']=='region-proposal':
            loop = np.array(row['region']['loop_xy']); ax.plot(*loop.T, color='lime', lw=.7)
            if row['reflection']:
                ax.plot(*row['reflection']['xy'], '+', color='cyan', ms=4, mew=.7)
        else:
            ax.plot(x,y,'x',color='orange',ms=3,mew=.5)
            if row.get('reflection'):
                ax.plot(*row['reflection']['xy'],'+',color='cyan',ms=4,mew=.7)
        if labels:
            ax.text(x+5,y-5,str(row['observation_number']),color='white',fontsize=6,
                    bbox=dict(facecolor='black',alpha=.65,pad=.3))
    for row in dark:
        x,y=row['xy']
        if crop[0]<=x<=crop[2] and crop[1]<=y<=crop[3]:
            ax.plot(x,y,'o',color='orange',mfc='none',ms=5,mew=.6)


def comparison(image, records, crop, path, targets):
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    draw(axes[0],image,records,crop)
    draw(axes[1],image,records,crop,True,False)
    for ax in axes:
        for letter,row in zip('ABC',targets):
            xy=row['reflection']['xy'] if row['reflection'] else row['seed_xy']
            ax.annotate(letter,xy,xytext=np.array(xy)+[10,-18],color='white',fontsize=10,
                        bbox=dict(facecolor='black',alpha=.8,pad=1),
                        arrowprops=dict(arrowstyle='->',color='cyan',lw=.7))
    axes[0].set_title('Raw photo; arrows identify evidence under review')
    axes[1].set_title('Green: inset region; cyan +: reflection locator')
    fig.savefig(path,dpi=170);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,default=auto.ROOT/'photo2/output/r192/conservative')
    parser.add_argument('--output',type=Path,default=auto.ROOT/'photo2/review/r192')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    data=json.loads((args.run/'inventory.json').read_text());records=data['records']
    image=ImageOps.exif_transpose(Image.open(auto.ROOT/'beads-photo-2.jpg')).convert('RGB')
    assert data['image_sha256']==auto.sha(auto.ROOT/'beads-photo-2.jpg')
    calibration_dir=args.run/'calibration';calibration_dir.mkdir(exist_ok=True)
    checks=calibration(calibration_dir)
    facts=trusted_facts(image)
    # Existing confirmed positive regions can support exact contained subsets;
    # mere proximity/partial overlap cannot certify any new exterior pixels.
    photo_checks=[];derived=[]
    for fact in facts['region_facts']:
        parent=Polygon(fact['region']['loop_xy']);overlap=[];contained=[]
        for row in records:
            if row['status']!='region-proposal':continue
            xy=pixels(row['region']);inside=parent.contains_points(xy)
            if inside.any():overlap.append(row['observation_number'])
            if inside.all() and parent.contains_points(np.array(row['region']['loop_xy'])).all():
                contained.append(row['observation_number'])
                derived.append(dict(maker_number=fact['maker_number'],
                    observation_id=row['observation_id'], observation_number=row['observation_number'],
                    region=row['region'],reflection=row['reflection'],
                    confirmation='All recorded pixels and loop vertices inside an existing R160-confirmed positive region',
                    role='Derived subset of an already confirmed body; not a new distinct body or full coverage evidence'))
        photo_checks.append(dict(maker_number=fact['maker_number'],overlapping_observations=overlap,
                                 wholly_contained_observations=contained,
                                 limits='No overlap is not proof the whole bead is missed; partial overlap does not confirm the new whole region.'))
    facts['derived_confirmed_subsets']=derived
    atomic_json(args.output/'trusted-facts.json',facts)
    # Color naming is semantic assistance after all candidate decisions, not a
    # detection threshold: compare learned modes with already confirmed colors.
    colors={}
    native_hsv=rgb_to_hsv(np.array(image,float)/255)
    for fact in facts['region_facts']:
        if fact['appearance']=='black':continue
        xy=pixels(fact['region']);hue=native_hsv[xy[:,1],xy[:,0],0]*360
        reference=float(np.degrees(np.angle(np.mean(np.exp(1j*np.radians(hue)))))%360)
        modes=data['parameters']['detector']['hue_modes_degrees']
        mode=int(np.argmin([abs((h-reference+180)%360-180) for h in modes]))+1
        colors[str(mode)]=fact['appearance']
    proposals=[r for r in records if r['status']=='region-proposal']
    # A review pair is selected by coverage issues, never by a model position.
    added=[r for r in proposals if r['source']=='native unresolved-coverage search']
    if not added:raise ValueError('No native added candidate for this fixed-photo review')
    focus=added[0];center=np.array(focus['seed_xy'])
    near_colored=sorted((r for r in proposals if r['kind']=='chromatic'),key=lambda r:np.linalg.norm(np.array(r['seed_xy'])-center))
    other_mode=next(r for r in near_colored if r['appearance_mode']!=focus['appearance_mode'])
    same_mode=next(r for r in near_colored if r['appearance_mode']==focus['appearance_mode'] and r['observation_number']!=focus['observation_number'])
    colored=[focus,other_mode,same_mode]
    lo=np.min([r['seed_xy'] for r in colored],axis=0)-55;hi=np.max([r['seed_xy'] for r in colored],axis=0)+55
    comparison(image,records,[*lo,*hi],args.output/'colored-question.png',colored)
    # The black review uses three central reflection candidates far from the
    # historically confirmed patch, not those labels as detection seeds.
    black=sorted((r for r in proposals if r['kind']=='dark-reflection'),key=lambda r:np.linalg.norm(np.array(r['seed_xy'])-center))[:3]
    lo=np.min([r['seed_xy'] for r in black],axis=0)-55;hi=np.max([r['seed_xy'] for r in black],axis=0)+55
    comparison(image,records,[*lo,*hi],args.output/'black-question.png',black)
    fig,ax=plt.subplots(figsize=(10,12),layout='constrained')
    draw(ax,image,records,[0,0,*image.size],True,False,data['unmatched_dark_areas'])
    ax.set_title('Candidate interior evidence only; orange: unresolved/excluded/dark audit')
    fig.savefig(args.output/'whole-context.png',dpi=160);plt.close(fig)
    # All-around raw/proposal atlas remains routine output; curated questions and
    # full inventory are tracked separately. No server/browser needs to launch.
    atlas=args.run.parent/'atlas';atlas.mkdir(exist_ok=True)
    links=[];tiles=[]
    width,height=image.size
    for row in range(5):
        for col in range(4):
            crop=[col*width/4,row*height/5,(col+1)*width/4,(row+1)*height/5]
            members=[r for r in records if crop[0]<=r['seed_xy'][0]<crop[2] and crop[1]<=r['seed_xy'][1]<crop[3]]
            dark=[r for r in data['unmatched_dark_areas'] if crop[0]<=r['xy'][0]<crop[2] and crop[1]<=r['xy'][1]<crop[3]]
            if not members and not dark:continue
            padded=[max(0,crop[0]-20),max(0,crop[1]-20),min(width,crop[2]+20),min(height,crop[3]+20)]
            name=f'tile-{row+1}-{col+1}.png'
            fig,axes=plt.subplots(1,2,figsize=(12,6),layout='constrained')
            draw(axes[0],image,records,padded)
            draw(axes[1],image,records,padded,True,True,data['unmatched_dark_areas'])
            axes[0].set_title('Raw');axes[1].set_title('Candidate regions / observation IDs')
            fig.savefig(atlas/name,dpi=150);plt.close(fig)
            links.append(f'<h2>Tile {row+1},{col+1}</h2><a href="{name}"><img width="1200" src="{name}"></a>')
            tiles.append(dict(tile=[row+1,col+1],crop=crop,observations=[r['observation_number'] for r in members],unassociated_dark=len(dark)))
    atlas.joinpath('index.html').write_text('<!doctype html><meta charset="utf-8"><title>Bead evidence review</title><h1>Raw and candidate regions — not yet trusted</h1><p>Click images for full size. Green loops must stay inside one body. Cyan marks are reflections, not centers. Orange marks need review. Numbers name observations, not bead indices.</p>'+''.join(links))
    # Full candidate pixels are retained without conferring maker trust.
    atomic_json(args.output/'candidates.json',data)
    atomic_json(args.output/'coverage-tiles.json',tiles)
    protected=json.loads((args.run.parent/'preserved-inputs.json').read_text())
    assert all(auto.sha(auto.ROOT/p)==h for p,h in protected.items())
    sources=['beads-photo-2.jpg','photo2/bead_evidence_inventory.py','photo2/review_bead_evidence.py',
             'photo2/test_bead_evidence.py','photo2/auto_label_beads.py','photo2/review/r157/report.json',
             'photo2/interior-confirmed-r160.json','photo2/reflection-confirmed-r170.json',
             'photo2/neighbor-confirmed-r172.json','photo2/review/r171/summary.json',
             'photo2/review/r167/summary.json','photo2/diagonal-confirmed-r189.json','photo2/colored-review-answers-r188.json']
    sources.append('photo2/foundation-request-r192.json')
    atomic_json(args.output/'summary.json',dict(request='R192',counts=dict(
        statuses=dict(Counter(r['status'] for r in records)),regions_by_kind=dict(Counter(r['kind'] for r in proposals)),
        native_added=data['native_extra_seeds'],unassociated_dark=len(data['unmatched_dark_areas']),
        trusted_regions=len(facts['region_facts']),trusted_black_reflection_points=len(facts['black_reflection_point_facts'])),
        color_names=colors,color_name_role='Post-selection semantic naming from existing maker-confirmed color facts',
        question_colored=[dict(label=l,observation_number=r['observation_number'],seed_xy=r['seed_xy'],source=r['source']) for l,r in zip('ABC',colored)],
        question_black=[dict(label=l,observation_number=r['observation_number'],seed_xy=r['seed_xy'],reflection=r['reflection']) for l,r in zip('ABC',black)],
        calibration=checks,coverage='Coverage unverified. Full-photo tiles preserve every observation; dark areas are not bead counts.',
        confirmed_photo_region_checks=photo_checks,
        sources={p:auto.sha(auto.ROOT/p) for p in sources},preserved_inputs=protected,
        curated_sha256={p.name:auto.sha(p) for p in args.output.glob('*') if p.name!='summary.json'},
        stopping_point='Native region inventory and trusted-fact separation; two illustrated reviews before promoting new regions. No photo/model fit.'))
    print(json.dumps(dict(color_names=colors,calibration=[{k:c[k] for k in
        ['fixture','region_proposals','single_body_regions','wrong_appearance_kind','eligible_located',
         'eligible_body_count','eligible_black_with_reflection','reflection_positions_wrong_owner']} for c in checks]),indent=2),flush=True)


if __name__=='__main__':main()

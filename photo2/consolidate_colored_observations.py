"""R252 assisted consolidation. No detector, full-mask partition, or geometry fit.

Source-local IDs are namespaced; curator identity decisions are explicit input,
never inferred by distance or brightness. Profile valleys are measurements only.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-r252-mpl')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_saved_centers import coverage_stations
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'photo2/review/r252'
PHOTO = ROOT/'beads-photo-2.jpg'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads((ROOT/path).read_text())

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')

def region_point(runs):
    p=np.array([(x,y) for y,lo,hi in runs for x in range(lo,hi+1)],float)
    # Pick actual positive pixel nearest mean, never an out-of-mask centroid.
    return p[np.argmin(np.linalg.norm(p-p.mean(axis=0),axis=1))].tolist()

def import_sources():
    sources=[]; primary=[]; paths=set(); black=[]; constraints=[]
    def add(key,path,xy,color,raw,level='automatic_candidate',active=False,**extra):
        paths.add(path)
        r=dict(key=key,source_file=path,original_xy=xy,color=color,original=raw,
               original_evidence_level=level,**extra)
        sources.append(r)
        if active: primary.append(key)
        return r
    p='photo2/review/r201/interiors.json'
    for r in read(p)['records']:
        add(f"A{r['observation_number']}",p,r['source_xy'],{1:'yellow',2:'red'}[r['appearance_mode']],r,
            'curator_reviewed' if r['selected'] else 'automatic_candidate',r['selected'])
    p='photo2/review/r200/position-basis.json'
    for r in read(p)['records']:
        add(f"M{r['number']}",p,[r['x'],r['y']],r['appearance_label'],r,'maker_marked_reviewed',True)
    for exp in [235,239]:
        p=f'photo2/review/r{exp}/references.json'
        for r in read(p):
            key=r['observation_id']; color=r['color']
            if color=='black': black.append(dict(source_file=p,original=r));continue
            add(key,p,r['observed_patch']['interior_sample_xy'],color,r,
                'curator_reviewed' if r['eligibility']=='eligible' else 'ambiguous',r['eligibility']=='eligible')
    # Import every historical proposal, including automatic abstentions and known errors.
    baseline_by_identity={}
    p='photo2/review/r235/automatic.json'; adj=read('photo2/review/r235/adjudication.json')['candidates']
    paths.add('photo2/review/r235/adjudication.json')
    for section,rows in read(p)['sections'].items():
        for r in rows:
            a=adj.get(r['candidate_id'],{})
            baseline_by_identity[(section,r['source_id'],tuple(r['xy']))]=a
            add('R235:'+r['candidate_id'],p,r['xy'],r['color'],r,adjudication=a)
    p='photo2/review/r235/halo-audit.json'; paths.add('photo2/review/r235/evaluation-amendments.json')
    for i,r in enumerate(read(p)):
        a=r.get('association')
        a=dict(status='supported',**a) if a else dict(status='outside_scope')
        baseline_by_identity[(r['section'],r['source_id'],tuple(r['xy']))]=a
        add(f'R235:halo:{i}',p,r['xy'],r['color'],r,adjudication=a)
    adj238=read('photo2/review/r238/adjudication.json')['decisions'];paths.add('photo2/review/r238/adjudication.json')
    adj239=read('photo2/review/r239/transfer-adjudication.json')['decisions'];paths.add('photo2/review/r239/transfer-adjudication.json')
    for split in ['development','transfer']:
        p=f'photo2/review/r239/{split}/ownership.json'
        for result in read(p)['results']:
            for r in result['proposals']:
                if split=='transfer':a=adj239.get(r['candidate_id'],{})
                elif '-A' in r['candidate_id']:a=adj238.get(r['candidate_id'],{})
                else:a=baseline_by_identity.get((result['section'],r['source_id'],tuple(r['xy'])),{})
                add('R239:'+r['candidate_id'],p,r['xy'],r['color'],r,adjudication=a)
    # Archive R238 pools, preserving suppressed candidates and original reasons.
    for split in ['development','transfer']:
        p=f'photo2/review/r238/{split}/candidates.json'
        for result in read(p)['results']:
            for r in result['baseline']+result['additions']:
                a=(adj238.get(r['candidate_id'],{}) if '-A' in r['candidate_id'] else
                   baseline_by_identity.get((result['section'],r['source_id'],tuple(r['xy'])),{}))
                add('R238:'+r['candidate_id'],p,r['xy'],r['color'],r,adjudication=a)
    p='photo2/review/r196/trusted-facts.json'; facts=read(p)
    for i,r in enumerate(facts['region_facts']):
        if r['appearance']=='black':black.append(dict(source_file=p,original=r));continue
        add(f'F196-{i}',p,region_point(r['region']['pixel_runs']),r['appearance'],r,'maker_confirmed',True)
    for i,r in enumerate(facts['other_point_facts']):
        color=r.get('appearance','yellow') # R172 maker16 is yellow, verified below in raw review.
        if color=='black':black.append(dict(source_file=p,original=r));continue
        add(f'F196p-{i}',p,r['xy'],color,r,'maker_confirmed',True)
    for i,r in enumerate(facts['distinct_body_point_group']['observations']):
        add(f'F168-{i}',p,r['xy'],'black' if i==1 else 'yellow',r,'maker_confirmed',True)
    constraints.append(dict(relation='distinct',keys=['F168-0','F168-1','F168-2'],source='R168'))
    for i,r in enumerate(facts['diagonal_group']['observations']):
        add(f'F189-{i}',p,r['source_xy'],'yellow',r,'maker_confirmed',True)
    constraints.append(dict(relation='distinct',keys=['F189-0','F189-1','F189-2'],source='R189'))
    constraints.append(dict(relation='distinct',keys=['F196p-1','F196p-2'],source='R194'))
    black.extend(dict(source_file=p,original=r) for r in facts['black_reflection_point_facts'])
    p='photo2/profile-answers-r204-r205.json'; d=read(p)
    for r in d['answers']['Q203.1']['points']:
        add('F204-'+r['label'],p,r['xy'],'yellow',r,'maker_confirmed',True)
    constraints.append(dict(relation='distinct',keys=['F204-S','F204-Q'],source='R204'))
    black.append(dict(source_file=p,original=d['answers']['Q203.2']))
    p='photo2/profile-transfer-answer-r209.json'
    for r in read(p)['points']:add('F209-'+r['label'],p,r['xy'],'yellow',r,'maker_confirmed',True)
    constraints.append(dict(relation='distinct',keys=['F209-A','F209-B'],source='R209'))
    p='photo2/correspondence-answer-r211.json'
    for k,xy in read(p)['points'].items():add('F211-'+k,p,xy,'yellow',dict(answer=read(p)['answer'],label=k),'maker_confirmed',True)
    constraints.append(dict(relation='same',keys=['F211-M','F211-V','F211-O','M5'],source='R211'))
    p='photo2/review/r215/confirmed-pixel-facts.json'
    for r in read(p)['confirmed_colored_regions']:
        add('F216-'+r['letter'],p,region_point(r['retained_pixel_runs']), 'yellow' if r['letter']=='A' else 'red',r,'maker_confirmed',True)
    black.append(dict(source_file=p,original=read(p)['confirmed_reflection']))
    # Older local-pilot observations retain their original uncertain meanings.
    # R147 explicitly aliases C to maker20, already present as F196-4.
    p='photo2/local-pilot-r114.json'
    colors=dict(A='yellow',B='red',C='red',D='uncertain',E='black',F='black',
                G='red',H='black',I='red',J='black',K='yellow',L='uncertain')
    for r in read(p)['observations']:
        adjudication=({'status':'supported','observation_id':'F196-4',
            'reason':'Explicit R147 alias C = maker20, stable ID 2ed70a3c-43a7-4634-a212-3612b8f6bc43; R160 positive interior is F196-4.'}
            if r['id']=='C' else {})
        add('R114:'+r['id'],p,r['xy'],colors[r['id']],r,
            'ambiguous' if r['id'] in ['D','L'] else 'historical_curator_proposal',adjudication=adjudication)
    p='photo2/colored-review-answers-r188.json';r=read(p)
    add('R188:587',p,r['source_xy'],'uncertain',r,'ambiguous')
    paths.update(['beads-photo-2.jpg','photo2/spline-seed-r175.json','photo2/interior-confirmed-r160.json',
        'photo2/interiors-confirmed-r193.json','photo2/ownership-answers-r194-r195.json','photo2/seed-method-answer-r232.json',
        'photo2/colored-review-answers-r188.json','photo2/diagonal-confirmed-r189.json',
        'photo2/review/r201/visual-review.json','photo2/review/r239/lost-correct.json'])
    paths.update(['photo2/local-pilot-review-r115.json','photo2/label-series-answers-r144.json',
                  'photo2/review/r114/observations.csv'])
    return sources,primary,black,constraints,paths

def pair_profiles(rgb,a,b):
    a=np.array(a,float);b=np.array(b,float);delta=b-a;length=float(np.linalg.norm(delta))
    t=np.linspace(0,1,max(41,int(np.ceil(length*4))+1))
    n=np.array([-delta[1],delta[0]])/max(length,1e-10)
    profiles=[]
    for offset in [-2.,-1.,0.,1.,2.]:
        xy=a+t[:,None]*delta+offset*n
        # RGB interpolation precedes Value=max(R,G,B); HSV hue never interpolated.
        values=np.array([map_coordinates(rgb[:,:,c],[xy[:,1],xy[:,0]],order=1,mode='nearest') for c in range(3)]).max(axis=0)
        ends=[float(np.median(values[t<=.12])),float(np.median(values[t>=.88]))]
        middle=(t>=.15)&(t<=.85);vmin=float(values[middle].min()); ti=float(t[middle][np.argmin(values[middle])])
        depth=1-vmin/max(min(ends),1e-9)
        profiles.append(dict(offset_px=offset,value=values.tolist(),endpoint_medians=ends,
            minimum_value=vmin,minimum_fraction=ti,relative_dip=depth))
    return dict(length_px=length,t=t.tolist(),profiles=profiles,
                interpretation='Diagnostic only; a minimum does not infer bead count; dark pixels unassigned.')

def pair_sheet(image, pairs, rows, path):
    font=ImageFont.truetype(FONT,14); cells=[]
    for i,(a,b) in pairs:
        ra,rb=rows[a],rows[b];aa=np.array(ra['original_xy']);bb=np.array(rb['original_xy']);mid=(aa+bb)/2
        side=max(76,int(np.max(abs(aa-bb)))+44);x,y=np.rint(mid-side/2).astype(int)
        raw=image.crop((x,y,x+side,y+side)).resize((190,190),Image.Resampling.NEAREST)
        marked=raw.copy();d=ImageDraw.Draw(marked)
        for p,label,c in [(aa,'a','#00ffff'),(bb,'b','#88ff66')]:
            q=(p-[x,y])*190/side;d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),outline=c,width=2);d.text((q[0]+5,q[1]-17),label,fill=c,font=font,stroke_width=1,stroke_fill='black')
        cell=Image.new('RGB',(390,224),'white');cell.paste(raw,(0,30));cell.paste(marked,(196,30));dr=ImageDraw.Draw(cell);dr.text((2,0),f'{i}: {a} / {b}',fill='black',font=font);dr.text((2,15),f"{ra['color']}/{rb['color']}  raw | point identity review",fill='black',font=font);cells.append(cell)
    sheet=Image.new('RGB',(1170,224*int(np.ceil(len(cells)/3))),'white')
    for j,cell in enumerate(cells):sheet.paste(cell,((j%3)*390,(j//3)*224))
    sheet.save(path)

LEVEL_RANK={'maker_confirmed':0,'maker_marked_reviewed':1,'curator_reviewed':2,'automatic_candidate':3,'ambiguous':4}

class Identities:
    def __init__(self,keys):self.parent={k:k for k in keys}
    def find(self,k):
        while self.parent[k]!=k:k=self.parent[k]
        return k
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.parent[max(a,b)]=min(a,b)


def consolidate(data,decisions):
    rows={r['key']:dict(r) for r in data['sources']}
    overrides=decisions['observation_overrides']
    for k,v in overrides.items():
        if 'color' in v:rows[k]['color']=v['color']
    def level(k):
        return overrides.get(k,{}).get('evidence_level',rows[k]['original_evidence_level'])
    primary=data['primary']+decisions.get('additional_primary',[])
    ids=Identities(primary)
    for p in decisions['pairs']:
        if p['decision']=='same':
            if rows[p['keys'][0]]['color']!=rows[p['keys'][1]]['color']:raise ValueError('Conflicting color identity')
            ids.union(*p['keys'])
    for c in data['constraints']:
        roots=[ids.find(k) for k in c['keys']]
        if c['relation']=='distinct' and len(roots)!=len(set(roots)):raise ValueError('Maker distinctness conflict')
        if c['relation']=='same' and len(set(roots))!=1:raise ValueError('Maker sameness not respected')
    for p in decisions['pairs']:
        if p['decision']=='distinct' and ids.find(p['keys'][0])==ids.find(p['keys'][1]):
            raise ValueError(f"Conflicting transitive review {p['keys']}")
    groups=defaultdict(list)
    for k in primary:groups[ids.find(k)].append(k)
    entities=[];key_entity={}
    for root,keys in sorted(groups.items()):
        usable=[k for k in keys if overrides.get(k,{}).get('status') not in ['ambiguous','rejected','deferred_black','black_preserved']]
        representative=min(usable or keys,key=lambda k:(LEVEL_RANK.get(level(k),9),k))
        r=rows[representative]
        status='trusted' if usable and r['color'] in ['red','yellow'] else 'ambiguous'
        if r['color']=='black':status='black_preserved'
        entity=dict(observation_id='C252-'+root,short_id=root,color=r['color'],status=status,
            evidence_level=level(representative) if status=='trusted' else status,
            representative_source=representative,xy=r['original_xy'],source_keys=sorted(keys),
            point_role='Observed colored interior sample; neither visible-surface centroid nor physical bead center',
            bead_index=None,physical_center_xyz=None,visible_surface_centroid_xy=None,
            decision_reason=overrides.get(representative,{}).get('reason','Raw photographic interior and body-context review; explicit cross-source identity adjudication.'),
            evidence=[p['evidence'] for p in decisions['pairs'] if set(p['keys'])&set(keys)])
        entity['evidence']=sorted(set(entity['evidence']))
        entity['color_evidence']='Raw photograph reviewed; maker-confirmed level concerns only the explicitly recorded facts, not every alias or derived coordinate.'
        for k in keys:key_entity[k]=entity
        entities.append(entity)
    # Historical accepted proposal associations are curator facts, never maker facts.
    for k,r in rows.items():
        r['current_review_override']=overrides.get(k)
        if k in key_entity:
            e=key_entity[k];r['entity_id']=e['observation_id']
            r['disposition']='representative' if e['representative_source']==k else 'duplicate_alias'
            if e['status']!='trusted':r['disposition']=e['status']
            r['decision_reason']=overrides.get(k,{}).get('reason',e['decision_reason'])
            continue
        a=r.get('adjudication',{});target=a.get('observation_id')
        if a.get('status')=='supported' and target in key_entity and r['color']==key_entity[target]['color']:
            e=key_entity[target];r['entity_id']=e['observation_id'];e['source_keys'].append(k)
            r['disposition']='duplicate_alias' if e['status']=='trusted' else 'ambiguous'
            r['decision_reason']='Inherited explicit photographic association: '+a.get('reason','')
        elif a.get('status') in ['false_positive','incorrect_color']:
            r['disposition']='rejected';r['decision_reason']=a.get('reason','')
        elif a.get('status')=='unresolved' or r['original_evidence_level']=='ambiguous' or overrides.get(k,{}).get('status')=='ambiguous':
            r['disposition']='ambiguous';r['decision_reason']=overrides.get(k,{}).get('reason',a.get('reason',r['original'].get('note','Unresolved historical reference')))
        elif r['color']=='black':
            r['disposition']='black_preserved';r['decision_reason']='Outside colored consolidation; original evidence retained.'
        else:
            r['disposition']='provisional';r['decision_reason']='Automatic or historical context candidate; not independently certified in this bounded audit.'
        r.setdefault('entity_id',None)
    # Explicit UUID lineage is linked as source identity only (same extraction seed,
    # NOT guaranteed identical bead or footprint); no implicit trust propagation.
    lineage=defaultdict(list)
    for r in rows.values():
        u=r['original'].get('observation_id') or r['original'].get('id')
        if u:lineage[u].append(r['key'])
    for r in rows.values():
        u=r['original'].get('observation_id') or r['original'].get('id')
        r['same_original_uuid_keys']=sorted(set(lineage[u])-{r['key']}) if u else []
    return list(rows.values()),entities


def csv_write(path,rows,fields):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)


def marker(draw,xy,status,color,size=6):
    x,y=xy;c='#00ff9d' if status=='trusted' else {'ambiguous':'#00d8ff','provisional':'#ff9b20','rejected':'#bd63ff','duplicate_alias':'#bd63ff'}.get(status,'#888888')
    if status=='trusted':
        draw.ellipse((x-size,y-size,x+size,y+size),outline='black',width=4)
        draw.ellipse((x-size,y-size,x+size,y+size),outline=c,width=2)
        draw.ellipse((x-1,y-1,x+1,y+1),fill='#ff3c24' if color=='red' else '#ffff00')
    elif status=='ambiguous':draw.polygon([(x,y-size),(x+size,y),(x,y+size),(x-size,y)],outline=c,width=2)
    elif status=='provisional':draw.rectangle((x-2,y-2,x+2,y+2),outline=c,width=1)
    else:
        draw.line((x-size,y-size,x+size,y+size),fill=c,width=2);draw.line((x-size,y+size,x+size,y-size),fill=c,width=2)


def build(out):
    original,primary,black,constraints,paths=import_sources()
    data=dict(sources=original,primary=primary,black_preserved=black,constraints=constraints,
              source_hashes={p:sha(ROOT/p) for p in sorted(paths)})
    decisions=read('photo2/review/r252/decisions.json')
    for p,h in decisions['source_hashes'].items():
        if sha(ROOT/p)!=h:raise ValueError(f'Changed source requires new review: {p}')
    sources,entities=consolidate(data,decisions)
    # One unchanged periodic spline supplies approximate photographic coverage only.
    coords=np.array([e['xy'] for e in entities]);fr,dist,_,_,_,curve=coverage_stations(coords,read('photo2/spline-seed-r175.json')['points'])
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];length=float(arc[-1]);sectors=32
    for e,f,d in zip(entities,fr,dist):
        e.update(arc_fraction=float(f%1),sector=min(int(f*sectors),sectors-1)+1,centerline_distance_px=float(d))
        e['evidence'].append(f"sector-{e['sector']:02}.png")
    accepted=[e for e in entities if e['status']=='trusted']; accepted.sort(key=lambda e:e['arc_fraction'])
    gaps=[]
    for i,e in enumerate(accepted):
        nxt=accepted[(i+1)%len(accepted)];gap=(nxt['arc_fraction']-e['arc_fraction'])%1
        gaps.append(dict(from_id=e['observation_id'],to_id=nxt['observation_id'],from_xy=e['xy'],to_xy=nxt['xy'],
            from_fraction=e['arc_fraction'],to_fraction=nxt['arc_fraction'],gap_fraction=gap,gap_arc_px=gap*length))
    gaps.sort(key=lambda g:-g['gap_fraction'])
    sf,*_=coverage_stations([r['original_xy'] for r in sources],read('photo2/spline-seed-r175.json')['points'])
    for r,f in zip(sources,sf):r['sector']=min(int(f*sectors),sectors-1)+1
    coverage=[]
    for s in range(1,sectors+1):
        es=[e for e in entities if e['sector']==s];ss=[r for r in sources if r['sector']==s and r['color']!='black']
        coverage.append(dict(sector=s,arc_start_px=(s-1)*length/sectors,arc_end_px=s*length/sectors,
            trusted_red=sum(e['status']=='trusted' and e['color']=='red' for e in es),
            trusted_yellow=sum(e['status']=='trusted' and e['color']=='yellow' for e in es),
            ambiguous_entity_hypotheses=sum(e['status']=='ambiguous' for e in es),
            ambiguous_source_records=sum(r['disposition']=='ambiguous' for r in ss),
            provisional_source_records=sum(r['disposition']=='provisional' for r in ss)))
    counts=Counter(e['color'] for e in accepted);levels=Counter(e['evidence_level'] for e in accepted)
    accounting=[]
    for p in sorted(set(r['source_file'] for r in sources)):
        rr=[r for r in sources if r['source_file']==p and r['color']!='black'];disp=Counter(r['disposition'] for r in rr)
        linked={r['entity_id'] for r in rr if r['entity_id'] and r['disposition'] in ['representative','duplicate_alias']}
        accounting.append(dict(source_file=p,colored_records=len(rr),unique_trusted_entities_represented=len(linked),**{k:disp[k] for k in ['representative','duplicate_alias','ambiguous','provisional','rejected']}))
    summary=dict(trusted_total=len(accepted),trusted_by_color=dict(counts),evidence_levels=dict(levels),
        nontrusted_entity_hypotheses=dict(Counter(e['status'] for e in entities if e['status']!='trusted')),
        colored_source_dispositions=dict(Counter(r['disposition'] for r in sources if r['color']!='black')),
        sector_count=sectors,centerline_length_px=length,sectors_with_trusted=sum(c['trusted_red']+c['trusted_yellow']>0 for c in coverage),
        sectors_with_both_colors=sum(c['trusted_red']>0 and c['trusted_yellow']>0 for c in coverage),largest_gaps=gaps[:12])
    unresolved=defaultdict(list)
    for r in sources:
        if r['color']=='black' or r['disposition']!='ambiguous':continue
        target=r.get('adjudication',{}).get('observation_id')
        if r['entity_id']:case=r['entity_id']
        elif target:case='reference:'+target
        elif 'eligibility' in r['original'] and '-B' in r['key']:case='reference:'+r['key']
        elif r['original'].get('source_id'):
            case='measurement:'+r['original']['source_id']+':'+str(r['original_xy'])
        else:case='candidate:'+r['key']
        unresolved[case].append(r)
    unresolved_cases=[dict(case_id=k,source_keys=[r['key'] for r in rr],xy=rr[0]['original_xy'],
        sector=rr[0]['sector'],reasons=sorted({r['decision_reason'] for r in rr}),
        distinct_bead_count=None) for k,rr in sorted(unresolved.items())]
    summary['unresolved_case_groups']=len(unresolved_cases)
    summary['unresolved_count_meaning']='Cases/measurement hypotheses, not independently established distinct beads; original alternatives retained.'
    rejected=[r for r in sources if r['color']!='black' and r['disposition']=='rejected']
    summary['unique_rejected_measurements']=len({(r['original'].get('source_id'),tuple(r['original_xy'])) for r in rejected})
    inventory=dict(schema_version=1,request='R252',photo_sha256=sha(PHOTO),photo_size=[2540,3182],
        coordinate_convention='Native JPEG pixels, x right, y down; no EXIF transform needed (orientation 1).',
        measurement_role='One safe visible colored-interior representative per accepted photographic body hypothesis. No center inference.',
        curator_role='Assisted review, not a new image-only detector; no independent precision/recall estimate.',
        source_hashes=data['source_hashes'],sources=sources,observations=entities,identity_decisions=decisions,
        maker_identity_constraints=data['constraints'],black_evidence_preserved_separately=data['black_preserved'],
        historical_identity_facts={p:read(p) for p in ['photo2/local-pilot-review-r115.json',
            'photo2/label-series-answers-r144.json']},
        summary=summary,coverage=coverage,source_accounting=accounting,unresolved_cases=unresolved_cases,
        unassigned_dark_pixels='No dark seam or background pixels assigned to any bead.',
        favored_working_helicity=1,helicity_proven=False,helicities_to_test=[1,-1],fitting_performed=False)
    write(out/'inventory.json',inventory);write(out/'summary.json',summary)
    csv_write(out/'accepted.csv',[dict(observation_id=e['observation_id'],x=e['xy'][0],y=e['xy'][1],color=e['color'],
        evidence_level=e['evidence_level'],sector=e['sector'],arc_fraction=e['arc_fraction'],representative_source=e['representative_source'],source_keys=';'.join(e['source_keys'])) for e in accepted],
        ['observation_id','x','y','color','evidence_level','sector','arc_fraction','representative_source','source_keys'])
    csv_write(out/'coverage.csv',coverage,list(coverage[0]));csv_write(out/'source-accounting.csv',accounting,list(accounting[0]))
    csv_write(out/'unresolved.csv',[dict(case_id=r['case_id'],x=r['xy'][0],y=r['xy'][1],sector=r['sector'],
        source_keys=';'.join(r['source_keys']),reasons=' | '.join(r['reasons'])) for r in unresolved_cases],
        ['case_id','x','y','sector','source_keys','reasons'])
    image=Image.open(PHOTO).convert('RGB');font=ImageFont.truetype(FONT,15)
    for all_status,name in [(False,'whole-accepted.png'),(True,'whole-inventory.png')]:
        im=image.copy();d=ImageDraw.Draw(im)
        if all_status:
            for r in sources:
                if r['color']!='black' and r['disposition'] in ['provisional','ambiguous','rejected']:
                    marker(d,r['original_xy'],r['disposition'],r['color'],4)
        for e in entities:
            if e['status'] in ['trusted','ambiguous']:marker(d,e['xy'],e['status'],e['color'])
        for s in range(sectors):
            i=int(np.argmin(abs(arc-(s+.5)*length/sectors)));x,y=curve[i]
            d.text((x+35,y+35),str(s+1),font=font,fill='white',stroke_width=2,stroke_fill='black')
        d.rectangle((25,25,1550,100),fill='white');d.text((40,35),f'R252: {len(accepted)} trusted interiors ({counts["red"]} red, {counts["yellow"]} yellow); sectors 1-32',fill='black',font=font)
        d.text((40,62),'Green ring trusted | cyan diamond ambiguous | orange square provisional | purple X rejected. Points are not centers.',fill='black',font=font)
        im.save(out/name)
    # Raw sector coverage cards retain the original photograph, with identical
    # crop at left and annotation at right; no straightening or simulated pixels.
    for s in range(sectors):
        sel=curve[(arc>=(s)*length/sectors)&(arc<=(s+1)*length/sectors)]
        lo=np.floor(sel.min(axis=0)-70).astype(int);hi=np.ceil(sel.max(axis=0)+70).astype(int)
        box=tuple(np.r_[lo,hi]);raw=image.crop(box);marked=raw.copy();d=ImageDraw.Draw(marked)
        for e in entities:
            q=np.array(e['xy'])-lo
            if np.all(q>=0) and q[0]<raw.width and q[1]<raw.height and e['status'] in ['trusted','ambiguous']:
                marker(d,q,e['status'],e['color'],5)
        card=Image.new('RGB',(raw.width*2+8,raw.height+30),'white');card.paste(raw,(0,30));card.paste(marked,(raw.width+8,30))
        ImageDraw.Draw(card).text((4,5),f'Sector {s+1}: raw | reviewed points',font=ImageFont.truetype(FONT,12),fill='black');card.save(out/f'sector-{s+1:02}.png')
    print(json.dumps(summary,indent=2))


def illustrate(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    inventory=json.loads((out/'inventory.json').read_text());rows={r['key']:r for r in inventory['sources']}
    im=Image.open(PHOTO).convert('RGB');rgb=np.asarray(im,float)/255
    cases=[('yellow-area-failure','R239:D4-A02','R239:D4-P14','distinct',
            'D4 B30 / B27: two credible yellow interiors; shared oversized lobe is not identity.'),
           ('yellow-touching','F196p-1','F196p-2','distinct',
            'R194 maker-confirmed distinct yellow points: retain both; do not assign intervening pixels.'),
           ('yellow-shallow','F204-S','F204-Q','distinct',
            'R204 maker-confirmed distinct yellow points: shallow separation can still be useful.'),
           ('red-adjacent','D4-B19','D4-B22','distinct',
            'Separate red faces with dark intervening saddle and different local body context.'),
           ('red-duplicate','R239:D4-P10','R239:D4-A08','same',
            'Two samples on one red face: directional shading alone does not make a second bead.'),
           ('yellow-duplicate','F211-M','F211-O','same',
            'R211 maker-confirmed same bead: M / O differ in position and brightness, not identity.'),
           ('yellow-false-merge','R239:T2-A01','R239:T2-A06','distinct',
            'Different visible yellow faces: R239 shared-lobe suppression does not establish sameness.')]
    output=[]
    for name,ka,kb,decision,reason in cases:
        a=np.array(rows[ka]['original_xy']);b=np.array(rows[kb]['original_xy']);m=pair_profiles(rgb,a,b)
        record=dict(case=name,source_keys=[ka,kb],endpoints_xy=[a.tolist(),b.tolist()],
            endpoint_reason='Previously observed colored interiors, checked in raw photo; no endpoint selected from a brightness minimum.',
            decision=decision,reason=reason,measurement=m,dark_pixel_assignment=None)
        output.append(record)
        lo=np.floor(np.minimum(a,b)-32).astype(int);hi=np.ceil(np.maximum(a,b)+32).astype(int)
        crop=np.asarray(im.crop(tuple(np.r_[lo,hi])));fig,ax=plt.subplots(1,3,figsize=(13,4),gridspec_kw={'width_ratios':[1,1,1.5]})
        for j in [0,1]:ax[j].imshow(crop,interpolation='nearest');ax[j].axis('off')
        ax[0].set_title('Unmarked native photograph (enlarged)');ax[1].set_title('Endpoints + parallel sampling routes')
        delta=b-a;n=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
        for p in m['profiles']:
            offset=p['offset_px'];xy=np.stack([a,b])+offset*n-lo
            ax[1].plot(xy[:,0],xy[:,1],color='cyan',lw=.6,alpha=.7)
            ax[2].plot(np.array(m['t'])*m['length_px'],p['value'],label=f'{offset:+g}px',lw=1.3)
        for letter,q in [('a',a),('b',b)]:ax[1].text(*(q-lo),letter,color='white',bbox=dict(facecolor='black',alpha=.7,pad=1))
        ax[2].set(xlabel='Distance from a along connecting segment (native px)',ylabel='HSV Value after native RGB interpolation',ylim=(0,1.02));ax[2].legend(fontsize=8,ncol=3);ax[2].grid(alpha=.2)
        fig.suptitle(f'{name}: {decision.upper()} — {reason}',fontsize=10)
        fig.tight_layout();fig.savefig(out/f'profile-{name}.png',dpi=140);plt.close(fig)
    write(out/'dark-separation.json',output)
    # Complete numeric samples, including parallel offsets, remain machine-readable.
    profrows=[]
    for r in output:
        m=r['measurement']
        for p in m['profiles']:
            for t,v in zip(m['t'],p['value']):profrows.append(dict(case=r['case'],offset_px=p['offset_px'],distance_px=t*m['length_px'],value=v))
    csv_write(out/'dark-profiles.csv',profrows,list(profrows[0]))
    coverage=inventory['coverage'];s=[c['sector'] for c in coverage];red=np.array([c['trusted_red'] for c in coverage]);yellow=np.array([c['trusted_yellow'] for c in coverage])
    fig,ax=plt.subplots(figsize=(13,4));ax.bar(s,red,color='#d94542',label='Trusted red');ax.bar(s,yellow,bottom=red,color='#e4bb38',label='Trusted yellow');ax.set(xticks=s,xlabel='Equal image-arclength sector (approximate unchanged spline)',ylabel='Distinct trusted observations',title='R252 coverage: each sector matters; observations are not projected centers');ax.legend();fig.tight_layout();fig.savefig(out/'coverage.png',dpi=150);plt.close(fig)
    # Reproduce the curated identity sheets from explicit recorded decisions.
    by_sheet=defaultdict(list)
    for p in inventory['identity_decisions']['pairs']:
        by_sheet[p['evidence']].append((p['pair_number'],p['keys']))
    for name,pairs in by_sheet.items():pair_sheet(im,pairs,rows,out/name)
    pair_sheet(im,[(0,['M37','M37'])],rows,out/'isolated.png')
    choices=read('photo2/review/r252/gap-proposals.json')
    pair_sheet(im,[(i,[c['key'],c['gap']['from_id'].removeprefix('C252-')]) for i,c in enumerate(choices)],rows,out/'gap-proposals.png')
    # Keep raw rejected/ambiguous examples, including candidate-level historical errors.
    difficult=[r['key'] for r in inventory['sources'] if r['disposition']=='rejected' and r['color']!='black']
    difficult+=list(inventory['identity_decisions']['observation_overrides'])
    difficult=sorted({k for k in difficult if rows[k]['color']!='black' and rows[k]['disposition'] in ['ambiguous','rejected']})
    for start in range(0,len(difficult),15):
        pair_sheet(im,[(i,[k,k]) for i,k in enumerate(difficult[start:start+15],start)],rows,out/f'withheld-{start//15+1:02}.png')
    # Each source record can be reached through a canonical JSON ID; immutable
    # historical archives keep rejected detection traces without counting them as bodies.
    inventory['archived_detection_traces']={p:[dict(section=s['section'],traces=s['traces']) for s in read(p)['results']]
        for p in ['photo2/review/r238/development/candidates.json','photo2/review/r238/transfer/candidates.json']}
    write(out/'inventory.json',inventory)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['build'])
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    build(args.output);illustrate(args.output)

if __name__=='__main__':main()

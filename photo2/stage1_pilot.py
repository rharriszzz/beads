"""R235: frozen two-pass photo pilot, with separate provisional visual evaluation.

Candidate assembly reads no reference labels. Adjudication is explicit visual
evidence, never nearest-center truth. No production detector or geometry change.
"""
from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'photo2/review/r235'
COLORS = {'red': '#ff5050', 'yellow': '#ffe030', 'black': '#35e4ff', 'unknown': '#bbbbbb'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def contains(box, xy):
    return box[0] <= xy[0] < box[2] and box[1] <= xy[1] < box[3]


def assemble_candidates(protocol, root=ROOT):
    """Frozen automatic output only; no reference or adjudication argument."""
    for name, digest in protocol['sources'].items():
        if sha(root/name) != digest:
            raise ValueError(f'Changed frozen source: {name}')
    colored = read(root/'photo2/review/r231/points.json')
    black = read(root/'photo2/review/r192/candidates.json')
    modes = colored['parameters']['hue_modes_degrees']
    names = {}
    for i, hue in enumerate(modes, 1):
        # Semantic names for the maker-supplied photo palette, not segmentation bounds.
        names[i] = min({'red': 0, 'yellow': 45},
                       key=lambda name: abs((hue-{'red': 0, 'yellow': 45}[name]+180) % 360-180))
    all_points = []
    for p in next(m['points'] for m in colored['methods'] if m['key'] == 'M4'):
        all_points.append(dict(source_id=p['id'], xy=p['xy'], color=names[p['mode']],
                               role='colored interior proposal', reflection_xy=None))
    for p in black['records']:
        if p['kind'] == 'dark-reflection' and p.get('reflection'):
            all_points.append(dict(source_id=f"R192:{p['observation_number']}",
                                   xy=p['reflection']['xy'], color='black',
                                   role='reflection with native dark-surround support',
                                   reflection_xy=p['reflection']['xy'],
                                   inherited_status=p['status'],
                                   localization_sensitivity_px=p['reflection']['threshold_sensitivity_pixels']))
    sections = {}
    for section in protocol['sections']:
        points = sorted((dict(p) for p in all_points if contains(section['box'], p['xy'])),
                        key=lambda p: (p['xy'][1], p['xy'][0], p['source_id']))
        for i, p in enumerate(points, 1):
            p['candidate_id'] = f"{section['id']}-P{i:02d}"
        sections[section['id']] = points
    return dict(method=protocol['method'], full_photo_proposal_counts=dict(Counter(p['color'] for p in all_points)),
                sections=sections, reference_labels_used=False, model_predictions_used=False)


def reference_records(protocol, raw):
    rows = []
    for section in protocol['sections']:
        key = section['id']; x0, y0 = section['box'][:2]
        fw, fh = section['full_footprint_dimensions_px']
        for number, row in enumerate(raw[key], 1):
            x, y, color, w, h, status, rx, ry, note = row
            area = None
            if color in ('red', 'yellow') and w is not None and status != 'uncertain_identity':
                area = [round(min(1., .50*w*h/(1.05*fw*fh)), 3),
                        round(min(1., .85*w*h/(.65*fw*fh)), 3)]
            xy = [x0+x, y0+y]
            if not contains(section['box'], xy):
                raise ValueError('Reference representative outside section')
            rows.append(dict(observation_id=f'{key}-B{number:02d}', section=key, split=section['split'],
                             color=color, eligibility=status, reference_representative_xy=xy,
                             observed_patch=dict(interior_sample_xy=xy,
                                                 extent_dimensions_px=[w, h] if w is not None else None,
                                                 role='Agent visible-area estimate; not exact segmentation'),
                             visible_fraction_range=area,
                             visible_surface_centroid_xy=None, physical_center_xyz=None, bead_index=None,
                             reference_reflection_xy=[x0+rx, y0+ry] if rx is not None else None,
                             representative_uncertainty_px=3 if status == 'eligible' else 6,
                             uncertainty_meaning='Illustrative marking tolerance within visible support, not physical-center error or calibrated confidence interval',
                             confidence='clear provisional visual interpretation' if status == 'eligible' else 'unresolved reference interpretation',
                             provenance='Agent raw-photo review; not new maker confirmation', note=note))
    return rows


def evaluate(references, automatic, adjudications):
    refs = {r['observation_id']: r for r in references}
    candidates = {p['candidate_id']: p for pts in automatic['sections'].values() for p in pts}
    if set(adjudications) != set(candidates):
        raise ValueError('Every candidate must have an explicit adjudication, exactly once')
    correct = {key: [] for key in refs}
    outcomes = []
    for key, p in candidates.items():
        decision = adjudications[key]
        owner = decision.get('observation_id')
        if owner is not None:
            if owner not in refs or refs[owner]['section'] != key.split('-')[0]:
                raise ValueError('Unknown or cross-section owner')
        state = decision['status']
        if state == 'supported':
            if owner is None or refs[owner]['eligibility'] != 'eligible':
                raise ValueError('Supported candidates need a clear eligible reference')
            if refs[owner]['color'] == p['color']:
                correct[owner].append(key)
            else:
                state = 'incorrect_color'
        elif state not in ('false_positive', 'unresolved', 'outside_scope'):
            raise ValueError('Unrecognized adjudication')
        outcomes.append(dict(**p, status=state, observation_id=owner, reason=decision['reason']))
    observations = []
    for key, r in refs.items():
        matches = correct[key]
        first = candidates[matches[0]] if matches else None
        eligible = r['eligibility'] == 'eligible'
        observations.append(dict(**r, automatic_candidate_ids=matches,
                                 representative_xy=first['xy'] if first else r['reference_representative_xy'],
                                 representative_role=first['role'] if first else 'Agent-selected visible-surface sample',
                                 specular_reflection_xy=first['reflection_xy'] if first and first['reflection_xy'] else r['reference_reflection_xy'],
                                 detection_origin=('automatic proposal, visually associated' if matches else 'assisted addition') if eligible else 'unresolved reference',
                                 automatic_missed=eligible and not matches))
    summary = {}
    for section in automatic['sections']:
        rr = [r for r in observations if r['section'] == section]
        oo = [p for p in outcomes if p['candidate_id'].startswith(section+'-')]
        eligible = [r for r in rr if r['eligibility'] == 'eligible']
        summary[section] = dict(split=rr[0]['split'], eligible=len(eligible),
                                eligible_by_color=dict(Counter(r['color'] for r in eligible)),
                                correctly_detected=sum(bool(r['automatic_candidate_ids']) for r in eligible),
                                missed=sum(r['automatic_missed'] for r in eligible),
                                misses_by_color=dict(Counter(r['color'] for r in eligible if r['automatic_missed'])),
                                duplicate_proposals=sum(max(0, len(r['automatic_candidate_ids'])-1) for r in eligible),
                                false_positives=sum(p['status'] == 'false_positive' for p in oo),
                                incorrect_colors=sum(p['status'] == 'incorrect_color' for p in oo),
                                unresolved_candidates=sum(p['status'] == 'unresolved' for p in oo),
                                outside_scope_candidates=sum(p['status'] == 'outside_scope' for p in oo),
                                candidate_count=len(oo),
                                reference_uncertain=sum(r['eligibility'] not in ('eligible', 'deferred_black') for r in rr),
                                deferred_no_reflection=sum(r['eligibility'] == 'deferred_black' for r in rr),
                                assisted_additions=sum(r['automatic_missed'] for r in eligible))
        s = summary[section]
        s['automatic_local_gate_passed'] = not any(s[k] for k in (
            'missed', 'duplicate_proposals', 'false_positives', 'incorrect_colors',
            'unresolved_candidates', 'reference_uncertain'))
    return dict(summary=summary, observations=observations, candidate_adjudications=outcomes,
                reference_status='Provisional agent annotations; counts conditional on that interpretation',
                assisted_map_status='Reference-supported additions; not independent validation or automatic success',
                global_indexing_started=False)


def apply_evaluation_amendments(protocol, raw, automatic, amendments):
    """Preserve the frozen score; add disclosed reference and crop-boundary corrections."""
    amended_raw = copy.deepcopy(raw)
    for addition in amendments['reference_additions']:
        amended_raw[addition['section']].append(addition['row'])
    references = reference_records(protocol, amended_raw)
    for r in references:
        if 'Post-freeze' in r['note']:
            r['provenance'] = 'Agent post-overlay reference correction; see evaluation-amendments.json'
    expanded = copy.deepcopy(protocol)
    for s in expanded['sections']:
        x0,y0,x1,y1=s['box'];s['box']=[x0-30,y0-30,x1+30,y1+30]
    halo = assemble_candidates(expanded)
    result = copy.deepcopy(automatic)
    audit = []
    for s in protocol['sections']:
        for p in halo['sections'][s['id']]:
            if contains(s['box'],p['xy']):continue
            record = dict(p, section=s['id']);record.pop('candidate_id')
            matches = [a for a in amendments['halo_associations']
                       if a['candidate_id'].startswith(s['id']+'-') and a['source_id']==p['source_id']]
            record['association'] = matches[0] if matches else None
            audit.append(record)
            if matches:
                result['sections'][s['id']].append(dict(p,candidate_id=matches[0]['candidate_id'],
                                                       boundary_credit=True))
    if sum(a['association'] is not None for a in audit)!=len(amendments['halo_associations']):
        raise ValueError('Boundary association does not name an actual halo proposal')
    return references, result, audit


def figure(image, section, markers, path, title, colors=False):
    halo=30; scale=5; x0,y0,x1,y1=section['box']
    crop=image.crop((x0-halo,y0-halo,x1+halo,y1+halo))
    enlarged=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST)
    canvas=Image.new('RGB',(enlarged.width,enlarged.height+65),'white');canvas.paste(enlarged,(0,65))
    d=ImageDraw.Draw(canvas);font=ImageFont.truetype('DejaVuSans.ttf',17)
    d.text((10,8),title,fill='black',font=font)
    d.text((10,33),'Box = scored section. Halo = context. Positions are not physical centers.',fill='black',font=font)
    d.rectangle((halo*scale,65+halo*scale,(x1-x0+halo)*scale,65+(y1-y0+halo)*scale),outline='#bbbbbb',width=2)
    used=[]
    for m in markers:
        x=(m['xy'][0]-x0+halo)*scale;y=65+(m['xy'][1]-y0+halo)*scale
        color=COLORS.get(m.get('color'), '#ffffff') if colors else '#ffffff'
        label=m['label'];bbox=d.textbbox((0,0),label,font=font);w=bbox[2]+7;h=24
        options=[(x+dx,y+dy) for dx,dy in [(10,-26),(10,8),(-w-10,-26),(-w-10,8),(8,-48),(8,28),(-w-10,-48),(-w-10,28)]]
        def penalty(pos):
            a,b=pos;outside=a<0 or b<65 or a+w>canvas.width or b+h>canvas.height
            return 1000*outside+sum(max(0,min(a+w,c)-max(a,aa))*max(0,min(b+h,dd)-max(b,bb)) for aa,bb,c,dd in used)
        a,b=min(options,key=penalty);used.append((a,b,a+w,b+h))
        d.line((x,y,a+w/2,b+h/2),fill=color,width=1)
        if m.get('assisted'):
            d.polygon([(x,y-6),(x+6,y+5),(x-6,y+5)],outline=color,width=2)
        elif m.get('uncertain'):
            d.rectangle((x-5,y-5,x+5,y+5),outline='#aaaaaa',width=2)
        else:d.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2)
        d.rectangle((a,b,a+w,b+h),fill='#151515');d.text((a+3,b),label,font=font,fill=color)
    canvas.save(path)


def render(protocol, refs, auto, output, report=None):
    image=ImageOps.exif_transpose(Image.open(ROOT/protocol['source_image'])).convert('RGB')
    for s in protocol['sections']:
        key=s['id'];x0,y0,x1,y1=s['box']
        image.crop((x0-30,y0-30,x1+30,y1+30)).resize(((x1-x0+60)*5,(y1-y0+60)*5),Image.Resampling.NEAREST).save(output/f'{key}-raw.png')
        rr=[r for r in refs if r['section']==key]
        markers=[dict(xy=r['reference_representative_xy'],label=r['observation_id'].split('-')[1],
                      uncertain=r['eligibility']!='eligible') for r in rr]
        figure(image,s,markers,output/f'{key}-numbered.png',f'{key}: raw-photo reference IDs; squares = unresolved / deferred')
        markers=[dict(xy=p['xy'],label=p['candidate_id'].split('-')[1],color=p['color']) for p in auto['sections'][key]]
        figure(image,s,markers,output/f'{key}-automatic.png',f'{key}: frozen automatic proposals; red / yellow / cyan = black',True)
        if report:
            markers=[dict(xy=r['representative_xy'],label=r['observation_id'].split('-')[1],color=r['color'],
                          assisted=r['detection_origin']=='assisted addition',uncertain=r['eligibility']!='eligible')
                     for r in report['observations'] if r['section']==key]
            by_id={r['observation_id']:r for r in report['observations']}
            markers += [dict(xy=p['xy'],label=p['candidate_id'].split('-')[1],color=p['color'],uncertain=True)
                        for p in report['candidate_adjudications'] if p['candidate_id'].startswith(key+'-')
                        and p['status']=='unresolved' and (p['observation_id'] is None
                        or by_id[p['observation_id']]['eligibility']=='eligible')]
            figure(image,s,markers,output/f'{key}-reviewed.png',f'{key}: reviewed inventory; circles automatic, triangles assisted, squares unresolved',True)


def write_tables(report, output):
    columns=['observation_id','color','eligibility','representative_xy','reference_representative_xy',
             'visible_fraction_range','specular_reflection_xy','visible_surface_centroid_xy',
             'physical_center_xyz','representative_uncertainty_px','confidence','detection_origin','automatic_candidate_ids','note']
    with (output/'observations.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for r in report['observations']:
            writer.writerow({k:json.dumps(r[k]) if isinstance(r[k],(list,dict)) else r[k] for k in columns})
    for key in report['summary']:
        lines=[f'# {key} observation table — provisional visual interpretation','',
               'Color: R=red, Y=yellow, K=black, ?=unknown. A=automatic proposal with assisted ownership review; S=assisted addition; U=unresolved. Fractions are broad heuristic ranges, not measured masks. Coordinates are native x,y. All physical centers, visible centroids and string indices remain unknown.','',
               'Confidence: eligible rows are clear but provisional agent interpretations, not independently confirmed truth. Representative marking tolerance is approximately 3px for eligible rows and 6px for uncertain rows, not a physical-center error bound. Reflection coordinates and separate raw-reference locations are in observations.csv and report.json.','',
               '| ID | Color | Representative (x,y) | Visible fraction | Origin | Eligibility / uncertainty | Automatic IDs |',
               '| --- | --- | --- | --- | --- | --- | --- |']
        for r in report['observations']:
            if r['section']!=key:continue
            frac=r['visible_fraction_range'];fraction=f'{100*frac[0]:.0f}–{100*frac[1]:.0f}%' if frac else 'unknown'
            origin='A' if r['automatic_candidate_ids'] else 'S' if r['eligibility']=='eligible' else 'U'
            xy=', '.join(f'{v:.1f}' for v in r['representative_xy'])
            lines.append(f"| {r['observation_id']} | {dict(red='R',yellow='Y',black='K',unknown='?')[r['color']]} | {xy} | {fraction} | {origin} | {r['eligibility']}: {r['note']} | {', '.join(r['automatic_candidate_ids']) or '—'} |")
        (output/f'{key}-observations.md').write_text('\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['prepare','evaluate'])
    parser.add_argument('--output',type=Path,default=BUNDLE)
    args=parser.parse_args();output=args.output;output.mkdir(parents=True,exist_ok=True)
    protocol=read(BUNDLE/'protocol.json')
    if sha(ROOT/protocol['source_image'])!=protocol['image_sha256']:raise ValueError('Photo changed')
    raw=read(BUNDLE/'reference-input.json');refs=reference_records(protocol,raw)
    auto=assemble_candidates(protocol)
    seals=dict(protocol=sha(BUNDLE/'protocol.json'),reference=sha(BUNDLE/'reference-input.json'),
               image=protocol['image_sha256'],sources=protocol['sources'])
    if args.stage=='prepare':
        existing=BUNDLE/'reference-freeze.json'
        if existing.exists() and read(existing)!=seals:raise ValueError('Frozen reference/protocol changed; append an amendment instead')
        save(output/'reference-freeze.json',seals);save(output/'references.json',refs);save(output/'automatic.json',auto)
        render(protocol,refs,auto,output)
        print(json.dumps(dict(reference_counts=dict(Counter(r['section'] for r in refs)),
                              candidate_counts={k:len(v) for k,v in auto['sections'].items()})))
    else:
        if read(BUNDLE/'reference-freeze.json')!=seals:raise ValueError('Frozen inputs changed')
        if read(BUNDLE/'automatic.json')!=auto:raise ValueError('Automatic output changed after reference freeze')
        adjudication=read(BUNDLE/'adjudication.json')
        frozen_decisions={k:v for k,v in adjudication['candidates'].items() if '-P' in k}
        save(output/'frozen-score.json',evaluate(refs,auto,frozen_decisions)['summary'])
        amendments=read(BUNDLE/'evaluation-amendments.json')
        refs,auto,halo=apply_evaluation_amendments(protocol,raw,auto,amendments)
        save(output/'halo-audit.json',halo);save(output/'evaluation-automatic.json',auto)
        report=evaluate(refs,auto,adjudication['candidates'])
        save(output/'report.json',report);write_tables(report,output);render(protocol,refs,auto,output,report)
        summary=dict(inputs=seals,adjudication_sha256=sha(BUNDLE/'adjudication.json'),
                     evaluation_amendments_sha256=sha(BUNDLE/'evaluation-amendments.json'),
                     script_sha256=sha(Path(__file__)),summary=report['summary'],
                     image_processing='Frozen detector replay; native crop/nearest-neighbor review only',
                     reproduction='.venv/bin/python photo2/stage1_pilot.py evaluate',
                     outputs_sha256={p.name:sha(p) for p in sorted(output.iterdir()) if p.suffix in ('.png','.csv','.md')})
        save(output/'summary.json',summary);print(json.dumps(report['summary'],indent=2))


if __name__=='__main__':main()

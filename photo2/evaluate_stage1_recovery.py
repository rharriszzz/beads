"""Score frozen R238 output without changing detection or the R235 reference."""
from collections import Counter
from pathlib import Path
import argparse
import copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from photo2.stage1_pilot import ROOT,read,save,sha,contains,evaluate
from photo2.stage1_recovery import BUNDLE


def score(bundle=BUNDLE,output=None):
    output=Path(output or bundle);output.mkdir(parents=True,exist_ok=True)
    freeze=read(bundle/'freeze.json')
    if freeze['script_sha256']!=sha(ROOT/'photo2/stage1_recovery.py'):raise ValueError('Detector changed after freeze')
    if freeze['inputs_sha256']!=sha(bundle/'inputs.json'):raise ValueError('Inputs changed after freeze')
    original=read(ROOT/'photo2/review/r235/report.json')
    refs=original['observations'];owners={r['observation_id']:r for r in refs}
    baseline=read(ROOT/'photo2/review/r235/evaluation-automatic.json')
    base_decisions={p['candidate_id']:{k:p[k] for k in ['status','observation_id','reason']} for p in original['candidate_adjudications']}
    results=[]
    for split in ['development','transfer']:
        doc=read(bundle/split/'candidates.json')
        if doc['script_sha256']!=freeze['script_sha256'] or doc['rules']!=freeze['rules']:raise ValueError('Unfrozen output')
        results+=doc['results']
    decisions=read(bundle/'adjudication.json')['decisions']
    candidates=[p for r in results for p in r['additions']]
    if set(decisions)!={p['candidate_id'] for p in candidates}:raise ValueError('Incomplete addition audit')
    for r in results:
        for p in r['additions']:
            if decisions[p['candidate_id']]['status']=='outside_scope' and contains(r['box'],p['xy']):raise ValueError('Cannot discard an in-box proposal')
    arms={};reports={}
    baseline_covered={r['observation_id'] for r in refs if r['automatic_candidate_ids']}
    for arm in ['baseline','rejected','native']:
        auto=copy.deepcopy(baseline);adjud=copy.deepcopy(base_decisions)
        for r in results:
            for p in r['additions']:
                if arm=='baseline' or (arm=='rejected' and p['arm']=='native'):continue
                auto['sections'][r['section']].append(dict(p,role='reflection' if p['color']=='black' else 'colored surface sample',reflection_xy=p['xy'] if p['color']=='black' else None))
                decision=copy.deepcopy(decisions[p['candidate_id']])
                # Existing evaluator detects incorrect color from a supported owner.
                if decision['status']=='incorrect_color':decision['status']='supported'
                adjud[p['candidate_id']]=decision
        reference_fields=[{k:v for k,v in r.items() if k not in ('automatic_candidate_ids','representative_xy','representative_role','specular_reflection_xy','detection_origin','automatic_missed')} for r in refs]
        report=evaluate(reference_fields,auto,adjud);reports[arm]=report
        recovered=[r for r in report['observations'] if r['automatic_candidate_ids'] and r['observation_id'] not in baseline_covered]
        totals={key:sum(s[key] for s in report['summary'].values()) for key in ['eligible','correctly_detected','missed','duplicate_proposals','false_positives','incorrect_colors','unresolved_candidates','outside_scope_candidates','reference_uncertain','deferred_no_reflection']}
        totals['new_recoveries_by_color']=dict(Counter(r['color'] for r in recovered))
        totals['recovered_ids']=[r['observation_id'] for r in recovered]
        totals['baseline_retained']=sum(bool(r['automatic_candidate_ids']) for r in report['observations'] if r['observation_id'] in baseline_covered)
        arms[arm]=dict(total=totals,sections=report['summary'])
    final=arms['native']['total'];new=final['new_recoveries_by_color']
    criteria=dict(colored=new.get('red',0)+new.get('yellow',0)>=8,black=new.get('black',0)>=9,retention=final['baseline_retained']==76,
                  zero_confirmed_errors=not any(final[k] for k in ['duplicate_proposals','false_positives','incorrect_colors']))
    summary=dict(arms=arms,criteria=criteria,passed=all(criteria.values()),reference_sha256=sha(ROOT/'photo2/review/r235/report.json'),
                 reference_status='Unchanged R235 provisional agent judgments, not independent ground truth.',
                 decision_sha256=sha(bundle/'adjudication.json'),detector_sha256=freeze['script_sha256'])
    save(output/'summary.json',summary)
    save(output/'report.json',reports['native'])
    # Every original miss gets an explicit trace locator, including persistent misses.
    paths=[]
    for ref in refs:
        if not ref['automatic_missed']:continue
        r=next(r for r in results if r['section']==ref['section'])
        point=ref['reference_reflection_xy'] if ref['color']=='black' else ref['reference_representative_xy']
        near=sorted([p for p in r['traces'] if p['color']==ref['color']],key=lambda p:np.linalg.norm(np.asarray(p['xy'])-point))[:3]
        paths.append(dict(observation_id=ref['observation_id'],color=ref['color'],reference_xy=point,
                          recovered_in=[arm for arm in ['rejected','native'] if ref['observation_id'] in arms[arm]['total']['recovered_ids']],
                          nearby_traces=[dict(p,distance_to_reference_px=float(np.linalg.norm(np.asarray(p['xy'])-point))) for p in near],
                          caution='Distance locates evidence for review; not an ownership rule or automatic cause assignment.'))
    save(output/'original-miss-traces.json',paths)
    image=Image.open(ROOT/'beads-photo-2.jpg');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    for r in results:
        box=r['halo'];crop=image.crop(box);scale=4;pic=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST);d=ImageDraw.Draw(pic)
        x0,y0,x1,y1=r['box'];d.rectangle(((x0-box[0])*scale,(y0-box[1])*scale,(x1-box[0])*scale,(y1-box[1])*scale),outline='white')
        counts=Counter()
        lines=['# '+r['section']+' candidate audit','', 'Automatic proposals remain unchanged. Supported ownership can still reveal duplicates. U is unresolved; F is false positive; W is wrong color; C is halo context.','', '| Candidate | Arm | Native x,y | Result / owner | Reason |','| --- | --- | --- | --- | --- |']
        for p in r['additions']:
            a=decisions[p['candidate_id']];owner=a['observation_id'];state=a['status'];counts[state]+=1
            duplicate=state=='supported' and (owner in baseline_covered or any(q['candidate_id']!=p['candidate_id'] and q['candidate_id']<p['candidate_id'] and decisions[q['candidate_id']]['observation_id']==owner and decisions[q['candidate_id']]['status']=='supported' for q in r['additions']))
            label='D' if duplicate else {'supported':'+','unresolved':'U','false_positive':'F','incorrect_color':'W','outside_scope':'C'}[state]
            color={'D':'#ff9944','+':'#33ff66','U':'#dddddd','F':'#ff4444','W':'#ff44ff','C':'#66bbff'}[label]
            x,y=(np.array(p['xy'])-box[:2])*scale
            d.ellipse((x-6,y-6,x+6,y+6),outline=color,width=2);d.text((x+7,y-15),p['candidate_id'].split('-')[1]+':'+label,fill=color,font=font,stroke_width=2,stroke_fill='black')
            lines.append(f"| {p['candidate_id']} | {p['arm']} | {p['xy']} | {label} {owner or '—'} | {a['reason']} |")
        pic.save(output/f"{r['section']}-audit.png")
        (output/f"{r['section']}-audit.md").write_text('\n'.join(lines)+'\n')
    # Diagnostic coordinates below select illustrations AFTER detection/scoring.
    # They are not detector inputs and never promote or delete a proposal.
    cases=[('D3','pool:21','Colored recovery: profile failure'),
           ('D4','reflection_rejections:324','Black recovery: old context rejection'),
           ('H1','native:182:1099','Native reflection versus paper-rim proposal'),
           ('D4','pool:1934','Miss: colored basin merges different bodies'),
           ('H4','native:1559:3056','Miss: paper proposal suppresses actual reflection')]
    cards=[];measurements=[]
    for sec,source,title in cases:
        rr=next(r for r in results if r['section']==sec)
        p=next(p for p in rr['traces'] if p['source_id']==source)
        x,y=map(int,p['xy']);box=[x-28,y-24,x+29,y+25];zoom=6
        raw=image.crop(box).resize((57*zoom,49*zoom),Image.Resampling.NEAREST)
        annotated=raw.copy();draw=ImageDraw.Draw(annotated)
        radius=freeze['rules']['ring_outer_d'] if p['color']=='black' else freeze['rules']['color_radius_d']
        diameter=read(bundle/'inputs.json')['parameters']['native_diameter']
        cx,cy=28*zoom,24*zoom
        radii=[radius*diameter]
        if p['color']=='black':radii.append(freeze['rules']['ring_inner_d']*diameter)
        for radius_px in radii:
            rad=radius_px*zoom;draw.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline='#00ffff',width=2)
        draw.line((cx-5,cy,cx+5,cy),fill='white',width=2);draw.line((cx,cy-5,cx,cy+5),fill='white',width=2)
        for q in rr['additions']:
            if contains(box,q['xy']):
                qx,qy=(np.asarray(q['xy'])-box[:2])*zoom
                draw.text((qx+4,qy-12),q['candidate_id'].split('-')[1],font=font,fill='#ffff44',stroke_width=2,stroke_fill='black')
        card=Image.new('RGB',(684,raw.height+78),'white');card.paste(raw,(0,78));card.paste(annotated,(342,78));draw=ImageDraw.Draw(card)
        draw.text((6,5),f'{sec}: {title}',fill='black',font=font)
        draw.text((6,27),f'{source} at ({x},{y}); cyan sampling disk/ring, not bead outline',fill='black',font=font)
        draw.text((6,49),p['decision'],fill='black',font=font)
        cards.append(card);measurements.append(dict(section=sec,trace=p,sampling_radii_native_px=radii,crop=box))
    sheet=Image.new('RGB',(684,sum(c.height for c in cards)),'white');y=0
    for card in cards:sheet.paste(card,(0,y));y+=card.height
    sheet.save(output/'failure-paths.png');save(output/'failure-paths.json',measurements)
    print(__import__('json').dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();score(output=args.output)

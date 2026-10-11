"""R239 explicit visual ownership scoring and reproducible review figures."""
from collections import Counter
from pathlib import Path
import argparse
import copy
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from photo2.stage1_pilot import ROOT,read,save,sha,contains,evaluate
from photo2.stage1_ownership import BUNDLE
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def render(split,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rgb=Image.open(ROOT/'beads-photo-2.jpg');font=ImageFont.truetype(FONT,13)
    for s in read(BUNDLE/split/'ownership.json')['results']:
        box=s['halo'];raw=rgb.crop(box);scale=4
        raw=raw.resize((raw.width*scale,raw.height*scale),Image.Resampling.NEAREST)
        panels=[raw.copy() for _ in range(3)]
        for k,pic in enumerate(panels):
            dr=ImageDraw.Draw(pic);a,b,c,d=s['box'];dr.rectangle(((a-box[0])*scale,(b-box[1])*scale,(c-box[0])*scale,(d-box[1])*scale),outline='white')
            if k==0:continue
            for p in s['proposals']:
                x,y=(np.array(p['xy'])-box[:2])*scale
                keep=p['ownership_decision']=='retain';col=('#55ffff' if k==1 else '#55ff55' if keep else '#ff7777')
                dr.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2)
                dr.text((x+5,y-12),p['candidate_id'].split('-')[1],fill=col,font=font,stroke_width=2,stroke_fill='black')
        sheet=Image.new('RGB',(raw.width*3,raw.height+42),'white');dr=ImageDraw.Draw(sheet)
        for i,(pic,title) in enumerate(zip(panels,['Raw photo','R238 proposals','R239 green retained / red abstained'])):
            sheet.paste(pic,(i*raw.width,42));dr.text((i*raw.width+6,10),s['section']+' '+title,fill='black',font=font)
        sheet.save(out/f"{s['section']}-comparison.png")
        # Separate manageable one-panel audit for inspection.
        panels[1].save(out/f"{s['section']}-proposals.png")


def clean_refs(refs):
    omit={'automatic_candidate_ids','representative_xy','representative_role','specular_reflection_xy','detection_origin','automatic_missed'}
    return [{k:v for k,v in r.items() if k not in omit} for r in refs]


def score(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    freeze=read(BUNDLE/'freeze.json')
    for name,key in [('photo2/stage1_ownership.py','script_sha256'),('photo2/stage1_recovery.py','r238_script_sha256')]:
        if sha(ROOT/name)!=freeze[key]:raise ValueError('Changed detector')
    historical=read(ROOT/'photo2/review/r238/report.json')
    refs=clean_refs(historical['observations'])+read(BUNDLE/'references.json')
    decisions={p['candidate_id']:{k:p[k] for k in ['status','observation_id','reason']} for p in historical['candidate_adjudications']}
    decisions.update(read(BUNDLE/'transfer-adjudication.json')['decisions'])
    for d in decisions.values():
        if d['status']=='incorrect_color':d['status']='supported'
    sections=sum([read(BUNDLE/s/'ownership.json')['results'] for s in ['development','transfer']],[])
    reports={}
    for arm in ['r238','ownership']:
        auto={'sections':{}};adjud={}
        for s in sections:
            pp=[p for p in s['proposals'] if arm=='r238' or p['ownership_decision']=='retain']
            auto['sections'][s['section']]=[dict(p,role=p['point_role'],reflection_xy=p['xy'] if p['color']=='black' else None) for p in pp]
            for p in pp:
                adjud[p['candidate_id']]=decisions[p['candidate_id']]
                if contains(s['box'],p['xy']) and adjud[p['candidate_id']]['status']=='outside_scope':raise ValueError('In-box candidate excluded')
        reports[arm]=evaluate(refs,auto,adjud)
    summary={};before={r['observation_id'] for r in reports['r238']['observations'] if r['automatic_candidate_ids']}
    after={r['observation_id'] for r in reports['ownership']['observations'] if r['automatic_candidate_ids']}
    for split,ids in [('development',['D3','D4','H1','H4']),('fresh_transfer',['T1','T2'])]:
        summary[split]={}
        for arm,rep in reports.items():
            keys=['eligible','correctly_detected','missed','duplicate_proposals','false_positives','incorrect_colors','unresolved_candidates','outside_scope_candidates','reference_uncertain','deferred_no_reflection']
            summary[split][arm]={key:sum(rep['summary'][sec][key] for sec in ids) for key in keys}
        summary[split]['lost_correct_bodies']=sorted(x for x in before-after if x.split('-')[0] in ids)
        summary[split]['abstained_proposals']=sum(p['ownership_decision']=='abstain' and decisions[p['candidate_id']]['status']!='outside_scope' for s in sections if s['section'] in ids for p in s['proposals'])
    save(out/'summary.json',summary);save(out/'report.json',reports)
    lines=['# R239 complete candidate audit','','Coordinates identify image samples or reflections, never physical centers. Reference ownership is provisional visual interpretation.','','| Candidate | x,y / color | R238 visual audit / owner | R239 | Automatic reason |','| --- | --- | --- | --- | --- |']
    for s in sections:
        for p in s['proposals']:
            a=decisions[p['candidate_id']]
            lines.append(f"| {p['candidate_id']} | {p['xy']} {p['color']} | {a['status']} {a['observation_id'] or '—'} | {p['ownership_decision']} | {p['ownership_reason']} |")
    (out/'candidate-audit.md').write_text('\n'.join(lines)+'\n')
    print(__import__('json').dumps(summary,indent=2))
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['render','score']);ap.add_argument('--output');args=ap.parse_args()
    out=Path(args.output or BUNDLE)
    if args.command=='render':
        for split in ['development','transfer']:render(split,out)
    else:score(out)

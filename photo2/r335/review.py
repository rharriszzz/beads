"""Current problems only: measured photographs, numbered adjacency, exact keys.

Presentation reuses immutable R332-R334 computations and R335 pigment application.
No detection, classifier training, period search, geometric fit or graph edits.
"""
import argparse,copy,csv,html,json,time
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from photo2.r334.common import read,save,ROOT
from .application import MAKER

PRIMARY=[
 dict(id='K-1508-3038',kind='link',title='Two proposed neighbors cross an unindexed observation',
      critical=['E5-1499-3037','K-1473-3021','NEW-1487-3054'],category='association',
      belief='The lattice makes #1 a coordinate neighbor of #3 and #4, but neither link is accepted: unindexed #2 lies in both photographic corridors.',
      alternative='The marker at #2 may belong to one of the neighboring bodies, or it may record a distinct bead. A separate bead would challenge the current row continuation rather than require a color edit.',
      look='Compare the actual glass boundaries around #1 and #2, only about 11 native pixels apart, and follow the visible bodies toward #3 and #4. Use the raw body close-up; do not count individual glints as separate beads.',
      question='Do #1 and #2 mark the same bead body or two distinct bodies? If distinct, is either dashed connection visibly interrupted by #2?',
      rationale='One identity decision constrains two missing links and a local row continuation.'),
 dict(id='K-2225-1294',kind='link',title='Is the link blocker another observation of the same black body?',
      critical=['E7-2235-1306','K-2244-1307'],category='association',
      belief='The #1–#3 F1 coordinate relation is not an accepted link because unindexed #2 lies in its native corridor. #2 is now black after the global body check.',
      alternative='The three locations may sample two bodies with a duplicate marker, or #2 may represent a third, intervening body. Recoloring cannot choose between those associations.',
      look='Inspect the connected glass material surrounding #1, #2 and #3. Look for actual boundaries between bodies and their continuity next to the neighboring red/yellow beads, rather than using the number of reflections.',
      question='Which of #1, #2 and #3 are on the same physical bead, if any?',
      rationale='A confirmed duplicate would explain a rejected link without inventing an extra bead.'),
 dict(id='NEW-946-2684',kind='link',title='A black body sample blocks an F0 continuation',
      critical=['E5-0948-2669','K-0951-2652'],category='association',
      belief='The #1–#3 coordinate relation is omitted because unindexed #2 intersects its corridor. The global procedure has corrected #2 to black; its identity is still unresolved.',
      alternative='The recorded points could sample two bodies with a duplicate at #2, or three bodies requiring a different local association/row continuation.',
      look='Follow the outline of the black glass between #1 and #3, with the yellow bodies to its right and the red bodies to its left as references. Check whether #2 has a distinct body boundary.',
      question='Is #2 a separate bead between #1 and #3, or another location on one of those bodies?',
      rationale='Separates a solved pigment issue from an unresolved physical identity.'),
 dict(id='NEW-985-2766',kind='link',title='Another observed support interrupts a nominal F0 neighbor',
      critical=['E5-0986-2754','MAT25-K-0980-2735'],category='association',
      belief='The working lattice has a #1–#3 F0 coordinate relation, but its link is withheld because unindexed #2 lies in the corridor.',
      alternative='An unindexed distinct bead could expose a row/index error; an alias or misplaced support could explain the blockage without changing the row.',
      look='Inspect the body boundaries immediately above #1 and below #3. Distinguish the material at #2 from a highlight or shadow belonging to either endpoint.',
      question='Does #2 identify a distinct bead body, or belong to #1 or #3?',
      rationale='Completes review coverage of all five currently omitted coordinate-neighbor links.'),
 dict(id='R332-B-0196-0183',kind='candidate',title='Four-neighbor dark candidate close to an accepted black observation',
      critical=['K-0548-0636','C-0574-0602','C-0544-0606','R332-R-0197-0183'],category='association',
      belief='The measured dark material at #1 remains provisional. Four indexed neighbors and three local triangles support the proposed site P, but its material support is about 10px from that prediction. #2 is only about 15px away.',
      alternative='There may be a separate partly visible body at #1, or the sample may belong to #2 or a cast-shadow/edge region. P is a geometric proposal, not an observed bead center.',
      look='Use the neighboring colored bodies at #3–#5 to follow the same two diagonal families around #1 and #2. Look for a separate glass outline at #1, not just dark pixels.',
      question='Is there a distinct visible bead body at #1, separate from #2, or is #1 part of #2/shadow?',
      rationale='A visible identity decision tests a four-neighbor gap and possible duplicate simultaneously.'),
 dict(id='R332-B-0138-0130',kind='candidate',title='A possible body on the inward edge near an uncertain continuation',
      critical=['K-1740-1575','C-1717-1540','C-1721-1566'],category='association',
      belief='#1 is a provisional native material support with three indexed neighboring proposals, shown as dashed connections at site P. It has no accepted lattice association.',
      alternative='A partly visible distinct body could occupy P; alternatively the material may be the edge of another body or shadow. Local direction/row continuation remains conditional.',
      look='Trace the adjacent colored bodies at #3 and #4 toward #1 and compare with the accepted black support #2. Check the narrow visible material rather than the geometric diamond P.',
      question='Can you identify a distinct body at #1, and which of #2–#4 actually touch it in the two drawn diagonal directions?',
      rationale='Targets the inward continuation without re-running the winding search.'),
 dict(id='R332-B-0098-0092',kind='candidate',title='Native dark body: a separate bead or an alias of its neighbor?',
      critical=['D40-K-1036-2780','C-1058-2815','C-1033-2810'],category='association',
      belief='#1 has cached/native material evidence and three neighboring proposals but remains unassociated. The accepted black support #2 is about 21px away. The cache alias REC266-P134549 belongs to the same provisional group, not a second new bead.',
      alternative='#1 may be a separate partially occluded bead or another sample from #2. The proposed lattice site alone cannot settle physical identity.',
      look='Compare the black material connecting #1 and #2 with the neighboring yellow bodies at #3/#4. A second reflection is not sufficient to establish a second body.',
      question='Are #1 and #2 on distinct bead bodies, or the same one?',
      rationale='Could resolve an observed black group while preventing duplicate admission.'),
 dict(id='C-1979-2669',kind='candidate',title='A visible yellow observation still lacks a lattice association',
      critical=['NEW-1999-2655','R332-Y-0071-0067','C-1998-2685'],category='association',
      belief='#1 is already a recorded yellow observation but remains unindexed. Its proposed site P has three neighbors and two triangles; its support is too far from the saved local prediction for automatic association.',
      alternative='The measured support may be on the correct body but displaced from the predictor, or it may identify a neighboring body rather than the proposed site.',
      look='Follow the yellow body at #1 and its boundary against #2–#4. P marks a prediction only; compare the real visible continuation through the numbered colored bodies.',
      question='Which visible body does #1 measure, and does it sit between the three dashed proposed neighbors as shown?',
      rationale='Human inspection can settle a visible association; a motif prediction cannot.'),
 dict(id='REC266-P146299',kind='pattern',title='Recorded red body versus repeated yellow counterparts',
      critical=[],category='pattern',
      belief='The body calculation retains red at #1. Three distant occurrences of the same saved spatial feature are yellow. This is the remaining significant contradiction involving red/yellow rather than a red/black classification.',
      alternative='The support may belong to a red neighbor, or the repeated-feature alignment/spiral rule may be incomplete. Color disagreement alone does not justify a new index.',
      look='Inspect the glass body around #1 outside its reflection and compare with the numbered yellow neighbors and two distant examples below. Check whether the support sits on red glass, yellow glass, or their boundary.',
      question='Is #1 on a red bead body, a yellow bead body, or a boundary/neighboring body?',
      rationale='Distinguishes a remaining pigment/marker problem from an incomplete repeated rule.'),
 dict(id='NEW-1927-2829',kind='pattern',title='Black body supported by the procedure, but red in repeated counterparts',
      critical=[],category='pattern',
      belief='Both saved and compact intensity checks support black at #1, which stays black. Three distant copies are red. This is presented as an association/continuation question, not another automatic red/black request.',
      alternative='The black observation may belong to the wrong visible body or lattice row; if its association is correct, the repeated spiral rule needs a more complex explanation.',
      look='Check that the marked support really belongs to the body connected to the local numbered neighbors. Compare the same lattice directions in the two distant examples; do not infer body color from the reflection hue.',
      question='Is #1 associated with the correct visible body and neighboring row, or does its marker belong to a different body?',
      rationale='If the body association is correct, this becomes a computational pattern/topology problem.'),
]

def run(out,run_root=None):
    t=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False);assets=out/'assets';assets.mkdir()
    base=Path(run_root or ROOT/'photo2/r335');g=read(base/'results/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']}
    oldg=read(ROOT/'photo2/r332/results/graph.json.gz');app=read(base/'results/application.json.gz');appby={r['id']:r for r in app['records']}
    audit={r['id']:r for r in read(ROOT/'photo2/r334/classification/audit.json.gz')['records']}
    candidates={r['id']:r for r in oldg['provisional_observations']};allobs={r['id']:r for r in oldg['unrepresented_candidates']};allobs.update(candidates);allobs.update(obs)
    for o,r in allobs.items():
        if o in appby:r['color']=appby[o]['color']
    remain=read(base/'results/remaining.json.gz');pred={r['id']:r for r in remain['predictions']};traces=read(ROOT/'photo2/r334/analysis/relocated/staircases/staircases.json.gz')['traces']
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');panels={};crops=[]
    def panel(oid,name,critical=(),proposal=False):
        target=allobs[oid];x,y=target['xy'];box=[max(0,int(x)-105),max(0,int(y)-100),min(photo.width,int(x)+106),min(photo.height,int(y)+101)]
        rows=[oid]+[o for o in critical if o!=oid]
        local=[o for o in co if box[0]+7<=obs[o]['xy'][0]<box[2]-7 and box[1]+7<=obs[o]['xy'][1]<box[3]-7]
        rows+=sorted(set(local)-set(rows),key=lambda o:(obs[o]['xy'][1],obs[o]['xy'][0]))
        # Every numbered point is a recorded/native support. Predictions use P.
        key=[dict(number=j+1,id=o,color=allobs[o]['color'],xy=allobs[o]['xy'],ab=co.get(o),status='indexed' if o in co else 'unindexed recorded' if o in obs else 'provisional native support') for j,o in enumerate(rows)]
        for k in key:assert box[0]<=k['xy'][0]<box[2] and box[1]<=k['xy'][1]<box[3],(oid,k)
        cropfile=f'assets/{name}-native.png';photo.crop(box).save(out/cropfile);crops.append(dict(file=cropfile,bbox=box,kind='context',id=oid))
        b=[max(0,int(x)-32),max(0,int(y)-32),min(photo.width,int(x)+33),min(photo.height,int(y)+33)];bodyfile=f'assets/{name}-body.png';photo.crop(b).save(out/bodyfile);crops.append(dict(file=bodyfile,bbox=b,kind='body',id=oid))
        present=set(rows);edges=[e for e in g['edges'] if e['source'] in present and e['target'] in present]
        omitted=[e for e in oldg['coordinate_only_edges'] if e['source'] in present and e['target'] in present and oid in [e['source'],e['target']]]
        pr=candidates.get(oid) if proposal else None
        p=dict(name=name,id=oid,bbox=box,body_bbox=b,image=cropfile,body_image=bodyfile,key=key,edges=edges,omitted=omitted,
               proposal={k:pr.get(k) for k in ['cell','prediction','xy','neighbors','reasons','error','native','alternatives']} if pr else None,
               traces=[dict(palette=tr['palette'],ids=[o for o in tr['ids'] if o in present],pairs=[[a,z] for a,z in zip(tr['ids'],tr['ids'][1:]) if a in present and z in present]) for tr in traces if any(a in present and z in present for a,z in zip(tr['ids'],tr['ids'][1:]))],
               pixels=appby.get(oid,{}).get('scales',[None,None])[1],old_pixels=audit.get(oid,{}).get('samples',[None,None])[1])
        # Native material arrays are available in ledgers, not duplicated in JS.
        if p['proposal'] and p['proposal'].get('native'):p['proposal']['native']={k:v for k,v in p['proposal']['native'].items() if k!='pixels_xy'}
        if p['old_pixels']:p['old_pixels']={k:p['old_pixels'].get(k) for k in ['highlight_pixels','body_pixels']}
        panels[name]=p;return name
    cases=[]
    for j,recipe in enumerate(PRIMARY):
        case=copy.deepcopy(recipe);case['rank']=j+1;case['name']=f'problem-{j+1:02}';case['panel']=panel(case['id'],case['name'],case['critical'],case['kind']=='candidate');case['examples']=[]
        if case['kind']=='pattern':
            winner=pred[case['id']]['prediction'];ex=[e for e in pred[case['id']]['examples'] if e['color']==winner]
            for k,e in enumerate(ex[:2]):
                nm=panel(e['id'],f'{case["name"]}-example-{k+1}');case['examples'].append(dict(panel=nm,id=e['id'],translation=e['translation']))
        cases.append(case)
    primaryids={c['id'] for c in cases};extras=[]
    # All 65 provisional black groups and all 23 recorded unindexed supports are
    # accessible individually, but only selected visible cases are on the main list.
    extraids={r['id'] for r in oldg['provisional_observations'] if r['color']=='black'}|{o for o in obs if o not in co}
    protected=set(MAKER)|{r['id'] for r in read(ROOT/'photo2/r334/corrections/ledger.json')['ordinary_color_corrections']}|{'R332-R-0025-0023'}
    for oid in sorted(extraids-primaryids-protected):
        pr=candidates.get(oid);critical=[r['id'] for r in pr.get('neighbors',[])][:4] if pr else []
        name='extra-'+str(len(extras)+1).zfill(3);nm=panel(oid,name,critical,pr is not None)
        extras.append(dict(id=oid,name=name,panel=nm,kind='candidate',category='secondary',title='Additional native evidence — lower review priority',examples=[],
            belief='This is an existing native support without an accepted lattice association. Any proposed site and dashed links remain unaccepted.',
            alternative='It may be a distinct visible body, an alias/edge of another bead, or material too obscured to associate.',
            look='Inspect the numbered support and real surrounding glass boundaries; ignore P as evidence of visibility. Saved evidence may be insufficient.',
            question=None,rationale='Detailed access is retained; no maker decision is required unless the body is visibly identifiable.'))
    gaps=copy.deepcopy(read(ROOT/'photo2/r333/diagnosis/diagnosis.json.gz')['gaps'])
    for gap in gaps:
        gap['historical_R333_prediction']=gap.pop('prediction');gap['prediction_status']='historical diagnostic, not a current pigment/visibility fact'
        for r in gap['neighbors']+gap['examples']:
            if r['id'] in obs:r['color']=obs[r['id']]['color']
        for r in gap['proposals']:
            if r['id'] in appby:r['color']=appby[r['id']]['color']
    ledger=dict(primary=cases,additional=extras,all_provisional_groups=[dict(id=r['id'],xy=r['xy'],color=appby.get(r['id'],r)['color'],proposed_ab=r['cell'],neighbors=r['neighbors'],reasons=r['reasons'],native_pixel_count=r['native']['pixel_count'],alternatives=r.get('alternatives',[])) for r in oldg['provisional_observations']],
                all_unindexed=[dict(id=o,xy=obs[o]['xy'],color=obs[o]['color']) for o in sorted(obs) if o not in co],coordinate_only_links=oldg['coordinate_only_edges'],
                inherited_gap_ledger=gaps,current_fixed_disagreements=remain['breaks'],motif208=remain['motif208'],
                full_pigment_application='photo2/r335/results/application.json.gz',scope='All records accessible; a provisional group, unobserved motif entry or predicted site is not a demonstrated visible error.')
    save(out/'ledger.json.gz',ledger);save(out/'panels.json.gz',panels);save(out/'native-crops.json',crops)
    summary=read(base/'results/summary.json');data=dict(cases=cases,additional=extras,panels=panels,summary=summary,colors={'red':'#df383f','yellow':'#f5d54b','black':'#242a32'},motif208=remain['motif208'])
    (out/'data.js').write_text('window.R335='+json.dumps(data,separators=(',',':'))+';\n')
    for filename in ['viewer.js','style.css','index.html']:(out/filename).write_text(Path(__file__).with_name('review-'+filename).read_text())
    save(out/'generation.json',dict(seconds=time.perf_counter()-t,primary_cases=len(cases),additional_cases=len(extras),panels=len(panels),literal_crops=len(crops),provisional_black_groups=65,unindexed_observations=len(ledger['all_unindexed']),working_links_edited=0,scope='Current R335 pigment application; unchanged R334 geometry. No solved maker target is a review question.'))
    print('REVIEW',len(cases),'primary',len(extras),'additional',len(panels),'panels',len(crops),'native crops',time.perf_counter()-t)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--run');a=p.parse_args();run(a.output,a.run)

"""Exact native-data/replay audit and situation coverage; no scientific retuning."""
import argparse,subprocess,tempfile
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
from .common import *
from .run import hashes

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');args=p.parse_args();native,_,meta=photo();rows=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];oldhash=read(EVIDENCE/'historical-hashes.json.gz');feedback=read(EVIDENCE/'feedback-hashes.json')
    for path,digest in dict(oldhash,**feedback).items():assert sha(ROOT/path)==digest,path
    assert hashes()==read(OUT/'algorithm-frozen.json')['source_hashes']
    for r in rows:
        x0,y0,x1,y1=r['box'];np.testing.assert_array_equal(np.asarray(Image.open(OUT/'crops'/(r['case_id']+'.png'))),native[y0:y1,x0:x1]);assert sha(OUT/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
    replay={}
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='r292-replay-') as folder:
            for stage in ('development','reserved'):
                log=Path(folder)/(stage+'.log')
                with log.open('w') as f:subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r292.run',stage,'--output',folder],stdout=f,stderr=subprocess.STDOUT,check=True)
                digest=sha(Path(folder)/(stage+'.json.gz'));assert digest==sha(OUT/(stage+'.json.gz')),stage;replay[stage]=dict(byte_exact=True,sha256=digest)
            for r in rows:assert sha(Path(folder)/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
    coverage=[];comparison=read(OUT/'comparison.json');human=read(ROOT/'photo2/r291/evidence/completed-review-analysis.json');known={q['case_id']:q for q in human['cases']}
    for category in sorted({c for r in rows for c in r['categories']}):
        group=[r for r in rows if category in r['categories']];ids=[r['case_id'] for r in group];accepted=[cid for cid in ids if known.get(cid,{}).get('answer') in ('A','B')];coverage.append(dict(category=category,cases=ids,evidence_tests=[f'T{i}' for i in range(1,9)],development=sum(r['split']=='development' for r in group),reserved=sum(r['split']=='reserved' for r in group),tracked_arcs=sum(len(r['separator_arcs']) for r in group),crossings_before=sum(sum(q['straddled_samples'] for q in r['separator_comparison']['before'] if q['enforced']) for r in group),crossings_after=sum(sum(q['straddled_samples'] for q in r['separator_comparison']['after'] if q['enforced']) for r in group),remaining_bank_connections=sum(r['A']['evidence']['T4']['remaining_separator_bank_connections'] for r in group),accepted_r291_references=accepted,materially_changed_accepted=[cid for cid in accepted if comparison[cid]['materially_changed']],outcomes=dict(Counter(r['A']['status'] for r in group)),limits='R292 human correctness pending. Labels include selection proxies; exact holes, physical ownership, occluders and pixel truth not established.'))
    save(OUT/'coverage.json',dict(categories=coverage,missing='Only9 new targets:4 red-context/4 yellow-context/1 unknown-context. No fresh controlled coverage of historical holes, bright-near-boundary or certified occlusions; no exact physical-hole/ownership labels. All T1–T8 run on all candidates.'))
    lines=['# R292 photographic coverage and regression matrix','','All T1–T8 run for every A/B. These are diagnostics, not correctness rates.','', '| Situation | Real-photo cases | Exposed / new | Tracked arcs | Direct crossings before / after | Remaining paired banks | Accepted R291 references changed materially |','|---|---|---:|---:|---:|---:|---|']
    for c in coverage:lines.append(f"| {c['category']} | {', '.join(c['cases'])} | {c['development']} / {c['reserved']} | {c['tracked_arcs']} | {c['crossings_before']} / {c['crossings_after']} | {c['remaining_bank_connections']} | {', '.join(c['materially_changed_accepted']) or 'None'} |")
    lines+=['','Missing coverage: only nine fresh targets (four red-context, four yellow-context, one unknown); the second unknown slot was unavailable under frozen separation rules. No independently established physical-hole, occluder or ownership labels. Historical failures remain exposed regressions, not fresh validation. New target labels are selection proxies. No case is certified photographically insufficient by a method failing.','', 'All primary results retain explicit partial/unresolved status. Eight accepted R291 references are pixel-identical; five have immaterial boundary changes. Their historical acceptance is not a new R292 judgment. Counter samples may overlap between arcs and must not be interpreted as distinct beads or pixel precision.']
    (ROOT/'photo2/R292_COVERAGE.md').write_text('\n'.join(lines)+'\n')
    import html
    (REVIEW/'coverage.html').write_text('<!doctype html><meta charset="utf-8"><title>R292 situation coverage</title><a href="index.html">Review</a><pre style="white-space:pre-wrap">'+html.escape('\n'.join(lines))+'</pre>')
    prior=read(OUT/'audit.json') if (OUT/'audit.json').exists() else {}
    save(OUT/'audit.json',dict(original_photo=meta,native_crops=len(rows),historical_files_unchanged=len(oldhash),feedback_files_unchanged=len(feedback),frozen_sources_unchanged=True,replay=replay or prior.get('replay',{}),replay_native_PNGs=len(rows) if replay else prior.get('replay_native_PNGs'),synthetic_work=False))
    print('Audit:',len(rows),'native crops;',len(oldhash),'historical files and',len(feedback),'feedback files unchanged;',len(replay),'exact data replays')
if __name__=='__main__':main()

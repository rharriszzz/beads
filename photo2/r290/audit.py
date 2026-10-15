"""Exact real-photo replay, category denominators, and preservation receipt."""
import argparse
import collections
from html import escape
import shutil
import subprocess
import sys
import tempfile
import numpy as np
from .common import *

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');a=parser.parse_args()
    records=[q for s in ('development','reserved') for q in read(OUT/(s+'.json.gz'))['records']]
    manifest=read(REVIEW/'manifest.json');collection=read(EVIDENCE/'collection.json');old=read(EVIDENCE/'historical-hashes.json.gz')
    for path,digest in old.items():assert sha(ROOT/path)==digest,path
    replay=read(OUT/'audit.json').get('replay',{}) if (OUT/'audit.json').exists() else {}
    if a.replay:
        with tempfile.TemporaryDirectory(prefix='r290-replay-') as directory:
            for stage in ('development','reserved'):
                subprocess.run([sys.executable,'-m','photo2.r290.run',stage,'--output',directory],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
                p=__import__('pathlib').Path(directory)/(stage+'.json.gz');assert sha(p)==sha(OUT/p.name),stage;replay[stage]=dict(byte_exact=True,sha256=sha(p))
            for r in records:assert sha(__import__('pathlib').Path(directory)/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
            replay['native_crops_exact']=len(records)
    counts={stage:dict(collections.Counter(r['A']['status'] for r in records if r['split']==stage)) for stage in ('development','reserved')}
    categories={}
    by_id={r['case_id']:r for r in records}
    mechanisms=read(EVIDENCE/'historical-mechanisms.json')['cases']
    for tag,tests in collection['categories'].items():
        cases=[m for m in manifest['cases'] if tag in m['categories']]
        categories[tag]=dict(cases=[m['case_id'] for m in cases],applicable_tests=tests,tests_evaluated_on_every_candidate=list('T'+str(i) for i in range(1,9)),development=sum(m['split']=='development' for m in cases),reserved=sum(m['split']=='reserved' for m in cases),automatic_outcomes=dict(collections.Counter(m['status'] for m in cases)),human_correctness='pending',historical_mechanisms=[t for t in (tag if tag.startswith('historical-') else 'See per-case historical tags',)],missing_coverage='No reserved case in this category' if not any(m['split']=='reserved' for m in cases) else 'Category labels are unverified selection proxies except documented development observations')
        categories[tag]['historical_mechanisms']={m['case_id']:mechanisms[m['case_id']] for m in cases if m['case_id'] in mechanisms}
        if tag=='weak-illumination':categories[tag]['missing_coverage']+='; dark-context examples still start at accepted bright R289 patches. Subthreshold peaks and too-small/uninformative cores are not sampled.'
    summary=dict(cases=len(records),counts=counts,status_fractions={s:{k:v/sum(d.values()) for k,v in d.items()} for s,d in counts.items()},alternatives=sum(bool(r['B']) for r in records),historical_blobs_unchanged=len(old),native_crops=len(records),replay=replay,categories=categories,human_review=dict(accepted_correctness=None,neighbor_inclusion=None,target_exclusion=None,duplicate_ownership=None,centroid_accuracy=None,reason='No pixel-accurate human boundary or trustworthy centroid references. Historical masks are not truth.'),unsupported_closure_exported_as_visible_region=sum(r['A']['visible_region_centroid'] is not None and r['A']['status']!='Reliable boundary' for r in records),context_expansions={r['case_id']:r['search'] for r in records if len(r['search'])>1},source_mismatches=[dict(case_id=r['case_id'],feature_id=r['feature']['id'],distance=r['selection_anchor_distance_px'],anchor=r['selection_anchor']) for r in records if r['selection_anchor_distance_px']>8],missing_coverage=collection['missing_coverage']+read(EVIDENCE/'development-observations.json')['limitations'])
    save(OUT/'audit.json',summary);save(OUT/'coverage.json',categories)
    lines=['# R290 permanent photographic coverage matrix','','Situation labels identify selection strata and documented mechanisms, not verified boundary truth. All T1–T8 run for every A/B candidate. Human correctness is pending.','', '| Situation | Cases | Relevant tests | Dev / reserved | Automatic outcomes | Historical mechanisms | Missing coverage |','|---|---|---|---|---|---|---|']
    html=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R290 photographic coverage</title><style>body{font:16px system-ui;margin:24px;background:#f5f3ed}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:10px}a{color:#00666f}.scroll{overflow:auto}</style><h1>R290 permanent photographic coverage</h1><p>All T1–T8 are evaluated on every candidate. Situation tags are selection proxies or documented development observations. Human correctness and physical ownership await review.</p><a href="index.html">Return to batch review</a><div class="scroll"><table><tr><th>Situation</th><th>Cases</th><th>Relevant evidence</th><th>Dev / reserved</th><th>Automatic outcomes</th><th>Historical mechanisms</th><th>Coverage limits</th></tr>']
    for tag,d in categories.items():
        outcomes=', '.join(f'{k}: {v}' for k,v in d['automatic_outcomes'].items()) or 'Missing'
        mechanism_text='; '.join(f'{c}: {v}' for c,v in d['historical_mechanisms'].items()) or 'Fresh hash-selected features; no prior individual correctness reference.'
        lines.append(f"| {tag} | {', '.join(d['cases'])} | {', '.join(d['applicable_tests'])} | {d['development']} / {d['reserved']} | {outcomes}; user pending | {mechanism_text} | {d['missing_coverage']} |")
        links=', '.join(f'<a href="index.html#{escape(c)}">{escape(c)}</a>' for c in d['cases'])
        html.append(f"<tr><td>{tag}</td><td>{links}</td><td>{', '.join(d['applicable_tests'])}</td><td>{d['development']} / {d['reserved']}</td><td>{outcomes}; user pending</td><td>{escape(mechanism_text)}</td><td>{d['missing_coverage']}</td></tr>")
    html.append('</table></div><p>Physical hole identity, true occluder identity, exact boundary truth and trustworthy centroid references are missing. Historical merger, truncation, tail and missing-boundary examples are retained as permanent development regressions; fresh reserved confirmation for those specific mechanisms remains missing.</p>')
    (ROOT/'photo2/R290_COVERAGE.md').write_text('\n'.join(lines)+'\n');(REVIEW/'coverage.html').write_text('\n'.join(html))
    # Per-case general regressions: every earlier version survives, no method is
    # treated as truth and status/area changes are diagnostic rather than gains.
    versions={p.parent.name:read(p)['records'] for p in (ROOT/'photo2/r290/checkpoints').glob('*/development.json.gz')}
    save(OUT/'development-regressions.json',dict(cases=[dict(case_id=r['case_id'],final_status=r['A']['status'],final_pixels=r['A']['candidate_pixels']['pixel_count'],versions={name:dict(status=q['A']['status'],pixels=q['A']['candidate_pixels']['pixel_count']) for name,rows in versions.items() for q in rows if q['case_id']==r['case_id']}) for r in records if r['split']=='development'],interpretation='No automatic correctness claim. Revisions corrected two general measurement/objective defects, while all remaining truncations, mergers and abstentions remain for batch review.'))
    print('Audit:',len(old),'historical blobs unchanged;',len(records),'photo cases;',counts,'replay',replay)

if __name__=='__main__':main()

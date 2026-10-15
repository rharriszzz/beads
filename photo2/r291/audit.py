"""Original-photo replay, preservation and diagnostic comparison receipts."""
import argparse
from collections import Counter
from html import escape
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image
from .common import *
from .run import hashes

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');a=p.parse_args()
    assert hashes()==read(OUT/'algorithm-frozen.json')['source_hashes']
    rows=[r for s in ('development','retrospective','reserved') for r in read(OUT/(s+'.json.gz'))['records']]
    old=read(EVIDENCE/'historical-hashes.json.gz');feedback=read(EVIDENCE/'r290-feedback-hashes.json')
    for path,digest in dict(old,**feedback).items():assert sha(ROOT/path)==digest,path
    native,_,meta=photo()
    for r in rows:
        x0,y0,x1,y1=r['box'];im=np.asarray(Image.open(OUT/'crops'/(r['case_id']+'.png')));np.testing.assert_array_equal(im,native[y0:y1,x0:x1])
        assert sha(REVIEW/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
    replay=read(OUT/'audit.json').get('replay',{}) if (OUT/'audit.json').exists() else {}
    if a.replay:
        with tempfile.TemporaryDirectory(prefix='r291-replay-') as folder:
            for stage in ('development','reserved','retrospective'):
                subprocess.run([sys.executable,'-m','photo2.r291.run',stage,'--output',folder],cwd=ROOT,stdout=subprocess.DEVNULL,check=True)
                actual=Path(folder)/(stage+'.json.gz');assert sha(actual)==sha(OUT/actual.name),stage;replay[stage]=dict(byte_exact=True,sha256=sha(actual))
            for r in rows:assert sha(Path(folder)/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
            replay['exact_native_PNGs']=len(rows)
    comparison=read(OUT/'comparison.json');groups={}
    for stage in ('development','retrospective','reserved'):
        rs=[r for r in rows if r['split']==stage];cs=[comparison[r['case_id']] for r in rs if r['case_id'] in comparison]
        groups[stage]=dict(cases=len(rs),statuses=dict(Counter(r['A']['status'] for r in rs)),median_supported_fraction=float(np.median([r['A']['evidence']['T7']['supported_fraction'] for r in rs])),median_min_IoU=float(np.median([min(r['A']['evidence']['T8']['perturbation_IoU']) for r in rs])),median_agreement_fraction=float(np.median([r['A']['evidence']['T7']['mechanism_agreement_sides']/max(r['A']['evidence']['T7']['total_sides'],1) for r in rs])),
            new_locally_supported_sides=sum(c['new_supported_sides_away_from_old'] for c in cs),old_supported_sides_without_new_match=sum(c['old_supported_sides_without_new_match'] for c in cs),cases_with_removed_feature_inclusions=sum(bool(c['other_feature_inclusions_removed']) for c in cs),cases_with_added_feature_inclusions=sum(bool(c['other_feature_inclusions_added']) for c in cs),old_crossed_supported_separators=sum(len(c['old_crossed_supported_separators']) for c in cs),new_crossed_supported_separators=sum(len(c['new_crossed_supported_separators']) for c in cs))
        groups[stage]['supported_sides_by_mechanism']=dict(Counter('+'.join(k for k in 'ABC' if any(v.startswith(k+':') for v in s['methods'])) for r in rs for s in r['A']['segments'] if s['supported']))
        if not cs:
            for key in ['new_locally_supported_sides','old_supported_sides_without_new_match','cases_with_removed_feature_inclusions','cases_with_added_feature_inclusions','old_crossed_supported_separators','new_crossed_supported_separators']:groups[stage][key]=None
    categories={};alltags=sorted(set(read(ROOT/'photo2/r290/evidence/collection.json')['categories'])|{tag for r in rows for tag in r['categories']})
    for tag in alltags:
        rs=[r for r in rows if tag in r['categories']];oldtests=read(ROOT/'photo2/r290/evidence/collection.json')['categories'];applicable=oldtests.get(tag,list('T'+str(i) for i in range(1,9)))
        categories[tag]=dict(case_ids=[r['case_id'] for r in rs],applicable_tests=applicable,evaluated_tests=[f'T{i}' for i in range(1,9)],split_counts=dict(Counter(r['split'] for r in rs)),outcomes=dict(Counter(r['A']['status'] for r in rs)),new_supported_sides=sum(comparison.get(r['case_id'],{}).get('new_supported_sides_away_from_old',0) for r in rs),lost_old_supported_sides=sum(comparison.get(r['case_id'],{}).get('old_supported_sides_without_new_match',0) for r in rs),human_correctness=None,missing='No new reserved examples' if not any(r['split']=='reserved' for r in rs) else 'Situation labels and ownership remain unverified; new cases are one historically studied photograph.')
    summary=dict(photo=meta,cases=len(rows),alternatives=sum(bool(r['B']) for r in rows),groups=groups,historical_files_unchanged=len(old),r290_feedback_files_unchanged=len(feedback),native_crops_exact=len(rows),replay=replay,start_here=read(OUT/'start-here.json'),analysis_limit_cases=[r['case_id'] for r in rows if r['search'][-1]['contact']],human_accuracy=None,neighbor_pixel_precision=None,centroid_accuracy=None,limitations=['Support-location changes, feature inclusion and stability are diagnostics, not accuracy.','All primary contours remain partial; useful-looking contours still await human assessment.','Known mergers/truncations remain. Fresh-unknown-02 reaches the computational limit with a large stable false region; no post-holdout repair.','Old R290 reserved cases are retrospective, never fresh validation. New targets are >=100px apart, but larger contexts may overlap.','New cases still use accepted R289 bright features; truly subthreshold seeds and exact photographic boundary truth are missing.','E junction/termination measurements are context proxies, not physical occluder identities.','No automatic assertion of photographic insufficiency is made.'])
    save(OUT/'audit.json',summary);save(OUT/'coverage.json',categories)
    lines=['# R291 photographic coverage and regression matrix','','All T1–T8 run for every A/B. R290 reserved is retrospective; only ten new cases are reserved for R291. Changes in support are diagnostic, not verified correctness.','', '| Situation | Cases | Relevant tests | Dev / old reserved / new reserved | New / lost old supported sides | Human correctness / missing coverage |','|---|---|---|---|---|---|']
    html=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R291 coverage</title><style>body{font:16px system-ui;margin:24px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:9px}.scroll{overflow:auto}</style><h1>R291 photographic coverage</h1><a href="index.html">Start Here review</a><p>All T1–T8 are evaluated on every candidate. Scores are diagnostic. Old reserved cases are retrospective, not fresh confirmation. Human correctness is pending.</p><div class="scroll"><table><tr><th>Situation</th><th>Cases</th><th>Relevant tests</th><th>Development / retrospective / new reserved</th><th>New / lost supported sides</th><th>Coverage limits</th></tr>']
    for tag,d in categories.items():
        counts=' / '.join(str(d['split_counts'].get(s,0)) for s in ('development','retrospective','reserved'));changes=f"{d['new_supported_sides']} / {d['lost_old_supported_sides']}" if any(c in comparison for c in d['case_ids']) else 'N/A: no R290 baseline'
        lines.append(f"| {tag} | {', '.join(d['case_ids'])} | {', '.join(d['applicable_tests'])} | {counts} | {changes} | Pending; {d['missing']} |")
        links=', '.join(f'<a href="index.html#{escape(c)}">{escape(c)}</a>' for c in d['case_ids'])
        html.append(f"<tr><td>{tag}</td><td>{links}</td><td>{', '.join(d['applicable_tests'])}</td><td>{counts}</td><td>{changes}</td><td>{d['missing']}</td></tr>")
    html.append('</table></div><p>Historical mechanisms remain linked in the R290 permanent collection and R291 comparison. No prior mask is truth. New/lost supported sides use a1.5px matching tolerance and different local evidence definitions, so neither count measures accuracy.</p>')
    (ROOT/'photo2/R291_COVERAGE.md').write_text('\n'.join(lines)+'\n');(REVIEW/'coverage.html').write_text('\n'.join(html))
    print('Audit:',len(rows),'cases;',len(old),'historical files unchanged;',groups,'replay',replay)

if __name__=='__main__':main()

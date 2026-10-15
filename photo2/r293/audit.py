"""Real-photo preservation, exact replay and readable coverage receipts."""
import argparse,subprocess,tempfile,csv,html
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
from .common import *
from .run import hashes

def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');args=p.parse_args();native,_,meta=photo();rows=[r for stage in ('development','reserved') for r in read(OUT/(stage+'.json.gz'))['records']];historical=read(EVIDENCE/'historical-hashes.json.gz');feedback=read(EVIDENCE/'feedback-hashes.json')
    for path,h in dict(historical,**feedback).items():assert sha(ROOT/path)==h,path
    assert hashes()==read(OUT/'algorithm-frozen.json')['source_hashes']
    for r in rows:
        x0,y0,x1,y1=r['box'];np.testing.assert_array_equal(np.asarray(Image.open(OUT/'crops'/(r['case_id']+'.png'))),native[y0:y1,x0:x1]);assert sha(OUT/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
    replay={}
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='r293-replay-') as folder:
            for stage in ('development','reserved'):
                with open(Path(folder)/(stage+'.log'),'w') as f:subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r293.run',stage,'--output',folder],stdout=f,stderr=subprocess.STDOUT,check=True)
                digest=sha(Path(folder)/(stage+'.json.gz'));assert digest==sha(OUT/(stage+'.json.gz'));replay[stage]=dict(byte_exact=True,sha256=digest)
            for r in rows:assert sha(Path(folder)/'crops'/(r['case_id']+'.png'))==r['crop_sha256']
    strata={}
    for stage in ('development','reserved'):
        group=[r for r in rows if r['split']==stage];strata[stage]=dict(cases=len(group),source_contexts=dict(Counter(r['feature']['color'] for r in group)),reflection_flags=sum(r['A']['evidence']['T8']['reflection_edge_ambiguous'] for r in group),with_other_features=sum(bool(r['A']['evidence']['T4']['other_features_inside']) for r in group),paired_bank_flags=sum(bool(r['A']['evidence']['T4']['remaining_separator_bank_connections']) for r in group),median_min_IoU=float(np.median([min(r['A']['evidence']['T8']['perturbation_IoU']) for r in group])),minimum_IoU=min(min(r['A']['evidence']['T8']['perturbation_IoU']) for r in group),human_accuracy=None)
    save(OUT/'evaluation.json',dict(strata=strata,inference_changed=False,production_changed=False,interpretation='Balanced spatial/context sample, not population-proportional; context colors are not physical material identity. Automatic metrics do not establish accuracy. All T1–T8 retained. Older judgments are separate regression evidence.'))
    cov=read(OUT/'coverage.json');lines=['# R293 priority coverage and evaluation','','Source: original photograph and unregistered image-derived centerline. No physical bead quotas or indexing.','', '| Evidence category | Result | Limit |','|---|---:|---|',f"| Independent features / within26px / within40px | {cov['feature_count']} / {cov['near26']} / {cov['near40']} | Not physical bead counts |",f"| Well-observed proxy within26px | {cov['well_observed_near26']} | Illumination/contrast/resolution, not mask accuracy |",f"| Neutral/reflection-like patches within26px | {cov['reflection_like_near26']} | Not certified black owners |"]
    for k,v in cov['summary'].items():lines.append(f'| {k} | {v} | Windows/pairs/references; no completeness claim |')
    lines+=['','## New frozen population','', '| Split | Cases | Context strata | Other-feature inclusion flags | Bank flags | Median / worst parameter IoU | Human accuracy |','|---|---:|---|---:|---:|---|---|']
    for stage,q in strata.items():lines.append(f"| {stage} | {q['cases']} | {q['source_contexts']} | {q['with_other_features']} | {q['paired_bank_flags']} | {q['median_min_IoU']:.3f} / {q['minimum_IoU']:.3f} | Pending |")
    lines+=['','## Coverage limits','','All385 sampled photographic windows contain an illuminated feature. This is not evidence of complete bead coverage: multiple highlights, unrepresented surfaces and ownership remain unresolved. 28 old near-centerline locations have no accepted independent R289 feature within8px (22 black-context,6 red-context). These are historical location discrepancies, not28 verified missing beads. The initial narrow arc-window false gap is preserved in checkpoints; final windows use actual26px Euclidean footprints and a40px local arc guard.','', 'All T1–T8 run for every new candidate. Human-reviewed old central clear-photo failures remain separate from lower-priority weak/peripheral uncertainty. Difficult physical silhouettes are not required for photographic interiors/reflections. No fresh physical truth labels, calibrated localization/ownership precision, full photographic completeness or subthreshold-feature recall is established.']
    (ROOT/'photo2/R293_COVERAGE.md').write_text('\n'.join(lines)+'\n');(REVIEW/'coverage.html').write_text('<!doctype html><meta charset="utf-8"><title>R293 coverage</title><a href="index.html">Priority review</a><pre style="white-space:pre-wrap">'+html.escape('\n'.join(lines))+'</pre>')
    with (OUT/'stations.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['station_id','reference_arc_px','x','y','feature_count','well_observed_count','negative_side_features','positive_side_features','separator_supported_pairs','human_clear_failure_cases','physical_bead_count'])
        for s in cov['stations']:w.writerow([s['station_id'],s['arc_px'],*s['point'],len(s['near_feature_ids']),s['well_observed_features'],len(s['signed_sides']['negative']),len(s['signed_sides']['positive']),len(s['supported_opposite_side_pairs']),';'.join(s['human_clear_failures']),'unknown'])
    with (OUT/'case-evaluation.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['case_id','feature_id','split','source_color_context','x','y','centerline_distance','signed_offset','pixels','other_features_inside','bank_flags','minimum_parameter_IoU','human_correctness'])
        for r in rows:w.writerow([r['case_id'],r['feature']['id'],r['split'],r['feature']['color'],*r['feature']['point'],r['priority_evidence']['centerline']['distance'],r['priority_evidence']['centerline']['signed_offset'],r['A']['candidate_pixels']['pixel_count'],len(r['A']['evidence']['T4']['other_features_inside']),r['A']['evidence']['T4']['remaining_separator_bank_connections'],min(r['A']['evidence']['T8']['perturbation_IoU']),'pending'])
    previous=read(OUT/'audit.json') if (OUT/'audit.json').exists() else {};save(OUT/'audit.json',dict(original_photo=meta,source_hashes_match=True,historical_files_unchanged=len(historical),feedback_files_unchanged=len(feedback),native_new_crops=len(rows),unchanged_historical_candidates=77,full_native_overview=True,replay=replay or previous.get('replay',{}),replay_native_PNGs=len(rows) if replay else previous.get('replay_native_PNGs'),synthetic_work=False,physical_reconstruction=False))
    print('Audit:',len(rows),'new native crops;',len(historical),'historical and',len(feedback),'feedback files unchanged;',len(replay),'exact replays')
if __name__=='__main__':main()

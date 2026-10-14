"""Curated report and review index from saved R278 numerical evidence."""
import csv,gzip,json,os
from pathlib import Path
from collections import Counter
import numpy as np
os.environ.setdefault('MPLCONFIGDIR','/tmp/r278-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .reconstruct_r278 import OUT,ROOT
from .bead_debugger.generate import save,sha
from .reproduce_r278 import EXPORTED


def main():
    phase=json.loads((OUT/'phase1-summary.json').read_text());models=json.loads((OUT/'comparison.json').read_text())
    sep={r['model']:r for r in json.loads((OUT/'separation-summary.json').read_text())}
    table=[]
    for row in models:
        doc=json.loads((OUT/(row['id']+'.json')).read_text());b=doc['base'];m=row['metrics'];c=sep[row['id']]
        table.append(dict(model=row['id'],count=b['n'],helicity=b['h'],pitch=b['pitch_factor'],hole_tilt_deg=b.get('hole_tilt_deg',0),focal_px=b.get('focal',0),
                          evaluations=row['fit']['evaluations'],train_support=m['train']['mean_support'],heldout_support=m['holdout']['mean_support'],
                          separated_pairs=c['separated_pairs'],possible_pairs=c['pairs'],minimum_separation_units=c['minimum_gap_units']))
    with (OUT/'comparison.csv').open('w') as f:
        w=csv.DictWriter(f,list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
    # No interpolation between counts: each point is a separate conditional model.
    fig,ax=plt.subplots(figsize=(10,5));x=np.arange(len(table));ax.bar(x-.18,[r['train_support']*100 for r in table],.36,label='Training');ax.bar(x+.18,[r['heldout_support']*100 for r in table],.36,label='Withheld geography')
    ax.set_xticks(x,[f"{r['count']} / {r['helicity']:+d}\n"+('tilt' if r['hole_tilt_deg'] else 'persp' if r['focal_px'] else '') for r in table],rotation=45,ha='right');ax.set_ylabel('Mean assigned positive interior pixels (%)');ax.set_ylim(0,100);ax.legend();ax.set_title('All models have positive separating-plane witnesses; none establishes photo identity')
    fig.tight_layout();fig.savefig(OUT/'comparison.png',dpi=160);plt.close(fig)
    with gzip.open(OUT/'phase1-inventory.json.gz','rt') as f:inv=json.load(f)
    regions={b['id']:b for b in inv['beads']};ledger=[]
    for l in inv['locations']:
        b=regions.get(l['id']);p=l['point']
        ledger.append(dict(observation_id=l['id'],color=l['color'],brightness_max_x=p['x'],brightness_max_y=p['y'],bright_patch_centroid=l['bright_patch']['centroid'],
                           measured_interior_centroid=b['region']['centroid'] if b else None,measured_pixels=b['region']['pixel_count'] if b else 0,
                           estimated_physical_center=None,location_kind='photographic maximum with interior/reflection evidence',
                           uncertainty='Physical center offset unmeasured; exact pixel coordinates are not center estimates',source=l.get('source','R275 preserved')))
    with (OUT/'phase1-positions.csv').open('w') as f:
        w=csv.DictWriter(f,list(ledger[0]),lineterminator='\n');w.writeheader();w.writerows(ledger)
    phase_cases=json.loads((OUT/'phase1-review-cases.json').read_text())
    tables=['| N | Hand | Pitch / source | Tilt | Focal px | Evaluations | Train ownership | Withheld ownership | Min separating gap |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in table:tables.append(f"| {r['count']} | {r['helicity']:+d} | {r['pitch']:.2f} | {r['hole_tilt_deg']:g}° | {r['focal_px']:g} | {r['evaluations']} | {r['train_support']:.1%} | {r['heldout_support']:.1%} | {r['minimum_separation_units']:.4f} |")
    accounting={n:json.loads((OUT/(n+'-accounting.json')).read_text()) for n in EXPORTED}
    lights={n:json.loads((OUT/(n+'-light.json')).read_text()) for n in EXPORTED if (OUT/(n+'-light.json')).exists()}
    source=json.loads((OUT/'packing-screen.json').read_text());legacy=next(r for r in source if r['convention']=='legacy' and r['pitch_factor']==1);intended=next(r for r in source if r['convention']=='intended' and r['pitch_factor']==1)
    text=f'''# R278 — corrected construction, independent inventory and conditional correspondence

**The radius correction resolves the sampled ±1 collision failure, but does not by itself resolve ±6 packing or photographic indexing.** Fourteen new closed-loop candidates have separating-plane witnesses for every possible collision pair. None yet explains substantially every photographed bead. All historical inventories, models and the source photograph remain preserved.

[Whole-photo comparison](review/r278/intended_N2696_h+1_p1.300_f0_tilt-8-overlay.jpg) · [review and reproduction index](review/r278/README.md) · [physical-model table](review/r278/comparison.csv) · [image-only positions](review/r278/phase1-positions.csv)

## Phase 1: photograph only

The frozen inventory has **{phase['locations']} locations and {phase['interiors']} measured interiors**: all 810 R275 locations/807 masks unchanged, plus 90 outside-band proposals (63 black, 23 yellow, 4 red). The target remains 658 locations. No new centerline-target candidate passed the final identity checks. The 63 prior residual peak groups, 12 short station intervals, 24 small colored supports and band-edge cases remain explicitly reviewable; they are not a completeness denominator.

Compared multiscale LoG features, chromatic distance cores, dark enclosure and secondary-highlight continuity. The full-photo search measures 4,200 features and attempts 2,191 native proposals. A failed wide control admitted 425 additions including shadowed paper and weak color fragments. An enclosure-only control retained 117, including dim/transitional doubts. Both survive separately. Selected additions require intact broad colored enclosure with coherent learned hue, sufficient illumination/extent, or a strong neutral reflection with dark enclosure. Small inset-core rescues remain candidates, because their local color does not establish separate bead identity.

The expanded domain exposed an inherited fallback hazard: an upstream size rejection could be lost during a hue fallback. The R278 wrapper rechecks the 870-pixel native limit; old outputs and historical algorithms remain unchanged. These requirements are conservative engineering gates, not a claim of general photo completeness. No reviewed coordinates, physical spacing, predicted sites, model colors or string indices enter Phase 1. The reference centerline records target membership only. Brightness maxima, patch centroids, interior centroids and unknown physical centers remain separate in the position ledger.

All 87 known synthetic scenes ran with an empty trusted inventory and automatic palette learning. New recovery detects 98/156 known bodies: black 28/32, red 45/62, yellow 25/62; zero selected false/duplicate/wrong-color locations or background/other-body mask pixels. Low yellow recall is explicit. This tests the new recovery path, not end-to-end photographic correctness. Full-photo regeneration reproduces the inventory, candidate decisions and feature files byte-for-byte.

## Radius, spacing and physical clearance

`Rope(..., radius_convention="intended")` uses `.96*4*sin(pi/6.5)=1.784536980648071`; default `legacy` remains `2.110915748921366`. The choice propagates into circular placement, source row spacing, loop dimensions, annular surfaces, visibility bounds and contact calculations. The new spline construction sets physical loop length before camera registration. A normalized world-unit adapter reuses the legacy exact surface evaluator; it does not shrink a rendered image.

At N=2696, source row pitch and zero tilt, legacy has {legacy['families']['1']['penetrations']} sampled ±1 and {legacy['families']['6']['penetrations']} ±6 penetrations. Intended radius has {intended['families']['1']['penetrations']} ±1 and {intended['families']['6']['penetrations']} ±6 penetrations. Updating the radius-dependent pitch shortens the source loop, so the remaining axial packing cannot be diagnosed by shrinking bead silhouettes alone.

Tested coherent pitch multipliers and one shared hole-axis tilt. A −8° signed circumferential tilt trades ±6 against ±7 clearance and allows a 1.30 pitch factor at high count. Untilted candidates use 1.35–1.45. These **30–45% global pitch increases are exploratory structural hypotheses**, not maker-confirmed dimensions or "small strain." Local fitted strain remains separately bounded, arclength-zero-net, with fixed loop length and integer winding closure. The spline is noncircular, planar and smoothly adjustable. Its R258 warm start and camera have historical photographic information; phases, twist harmonics and local fields are reset before the new fits. No historical string identities are imported.

Contact auditing checks both directions against the exact annulus at 16,384 surface samples per bead for the exported models, across every bounding-sphere neighbor pair. More strongly, filling the annular hole gives a convex outer envelope with analytic support. Stored plane normals separate every possible pair by a positive margin; all other pairs are excluded by bounding spheres. This is a sufficient floating-point geometric certificate for the stated idealized shapes, with a 1e-6-unit safety threshold; it is not interval-arithmetic formal verification or proof that these are the photographed beads.

## Equal-budget geometry comparison

All rows use the same 24 full-circle phase starts and 136 objective evaluations (145 allowed), with train-only positive interiors and the same bounded parameter search. Assignments maximize native visible positive-pixel ownership one-to-one, with unmatched dummy assignments. Fit uses 12 deterministic pixels/interior; comparison uses up to 48; exported ledgers audit every native interior pixel. Training and withheld assignment are separate; final ledgers use a single global assignment and report disagreements. The cost uses whole observations equally, not pooled pixel count. No nearest-highlight-to-center loss is used.

'''+'\n'.join(tables)+'''

Held-out geographic sectors and buffers exclude R278 parameter updates, not the historical warm start. The later count/camera/tilt comparisons are exploratory after inspecting earlier results. A count grid plus bounded search does not establish a unique count or global optimum. The N2080 negative-hand fit slightly leads training ownership; its opposite hand does better on withheld ownership. The high-count positive-hand tilted fit is competitive. The historical R276 mixed/contact models are audited against the same current observations in `historical-comparison.json`; their different historical fit budgets are not disguised as equal-budget controls.

## Complete conditional prediction ledgers

Every generated bead has a model index, ±1/±6/±7 neighbors, 3D center, projected center, sampled visible support, visible centroid, associated observation if any, pixel-derived color and status. Four competing models have full exports. A 2px visibility grid may miss tiny slivers; zero samples is explicitly not proof of complete occlusion. Unknown/grazing rays are retained. Indices are conditional generator addresses with an arbitrary origin, not recovered physical string identities.

Color uses actual inset visible pixels and hue distributions learned from measured training interiors. Black requires reflection plus dark-body evidence. Geometry-assisted candidates additionally need an independent stable image feature and adequate visible support; they never become retrospective Phase 1 detections. Conflicting surface colors downgrade otherwise high-support correspondences. Unknown is retained for insufficient evidence. No repeating pattern is used.

| Model | Confident conditional matches | Ambiguous | Geometry-assisted candidates | Predicted unconfirmed | Independent unexplained* |
|---|---:|---:|---:|---:|---:|
'''
    for name,a in accounting.items():
        c=a['categories'];o=a['observations'];text+=f"| {name} | {c.get('confident conditional match',0)} | {c.get('ambiguous correspondence',0)} | {c.get('geometry-assisted image-supported candidate',0)} | {c.get('predicted but unconfirmed',0)} | {o.get('independent observation unexplained',0)+o.get('independent location without measured interior',0)} |\n"
    text+='''
*Includes the three preserved location-only observations, which have no invented interior. The categories are conditional evidence accounting, not a verified visible bead census. Large numbers of tiny predicted surfaces and unconfirmed bodies are a warning, not successful recovery.

## Shared lighting and discrepancies

Geometry and positive-support correspondences are frozen before each lighting diagnostic. Twenty identical direction trials fit yellow training reflections; a single distant direction and fixed 6° lobe transfer to red and black. Missing highlights retain an explicit 30px sentinel and count. These are brightness-patch predictions, not inferred physical centers.

| Model | Held-out yellow RMS px | Red RMS px | Black RMS px |
|---|---:|---:|---:|
'''
    for n,l in lights.items():text+='| '+n+' | '+' | '.join(f"{l['metrics']['holdout/'+c]['rms']:.2f}" for c in ('yellow','red','black'))+' |\n'
    text+='''
The high-count tilted model transfers shared lighting better than the lower-count candidate, but the positive-interior fit still leaves extensive ambiguity. The worst crops show clear black reflections with no plausible owner, large colored interiors split between candidate surfaces, and tiny visible predictions that cannot establish an independent body. Likely contributors are incorrect row pitch/count/phase, the assumed bead aspect ratio and hole-axis orientation, residual spline/camera bias, and uncertain ownership of small photographic patches. These are hypotheses to test, not adjudicated causes. The geometric clearance improvement does not compensate for photographic failures.

POV-Ray renders use the unchanged source bead macro with the explicit corrected radius and saved 3D transforms, one shared parallel light, and gray for uncertain model colors. Display materials are illustrative, not radiometric calibration.

## Validation and stopping point

50 scientific tests, plus 18 R275/local-surface regression checks, pass. The scientific tests cover both radius conventions, dimensional propagation, both helicities with fixed major traversal, closure, neighbor modulo indexing, positive-support assignment, legacy ray replay, unit-change invariance, tilted frames, perspective registration, exact surface samples and separation witnesses. The 87 image scenes, native measurement/ledger audit, byte-exact Phase 1 replay and byte-exact 31-file saved-model replay are separate checks. Original photograph, all 810 coordinates/807 masks and 4,721 prior tracked files are unchanged; the only shared-code edit is the explicit optional radius convention in `bead_placement.py`. All prior R276 alternatives survive.

This delivers significant progress in both phases, a physically separated family of candidates and reproducible complete conditional ledgers. **It does not complete reliable physical indexing or predict the verified identity of substantially every visible bead.** Next resolve the pitch/aspect-ratio/orientation ambiguity using geographically distributed exposed bodies and connected ±1/±6/±7 photographic ownership, keeping the frozen observations fixed. Do not begin repeating-pattern inference. Keep the current model/reasoning; no `/new` is required for reviewing these results.
'''
    (ROOT/'photo2/RECONSTRUCTION_R278.md').write_text(text)
    index='''# R278 evidence and reproduction

[Main report](../../RECONSTRUCTION_R278.md)

`phase1-inventory.json.gz` is the frozen independent inventory; `phase1-positions.csv` separates measured position types and unknown physical centers. `phase1-decisions.json.gz` and `phase1-features.json.gz` retain every attempted proposal and feature, including rejections. The original 295 R275 uncertain records remain in the inventory. `phase1-review-cases.json` indexes additions, unresolved peak groups, small supports, short intervals and band edges. Cyan marks preserved locations; green marks additions; the orange square is the review target, not a detection.

`failed-wide-control/` preserves the failed 425-addition control and illustrative paper failures. `enclosure-only-control/` preserves the 117-addition intermediate. `obsolete-prefreeze-fits/` contains interrupted/obsolete preliminary fits against earlier inventories; NEVER include these in final model comparisons. Routine full failed atlases can be regenerated; only representative failure images are curated.

`packing-screen.json`, `contact-screen.json`, `tilt-screen.json` retain failed packing alternatives. `comparison.json`/CSV contain all 14 fits, color/sector breakdowns and budgets. `MODEL.json` includes full spline/camera/phase parameters, frozen inventory hash and fit trace. `MODEL-separation.json` stores a separating-plane normal/gap for every possible collision pair. `MODEL-contact.json` is the denser sampled audit for exported models.

`MODEL-correspondence.json.gz` contains every generated bead and every independent observation, alternatives, statuses, raw-pixel colors and unknown rays. `MODEL-visible-support.json.gz` contains 2px first-hit support samples keyed by model index. `MODEL-beads.csv` is suitable for later indexing review; indices remain conditional. `MODEL-discrepancies.json` links worst native crops, black matches and geometry-assisted candidates. `MODEL-light.json` contains all 20 shared-light trials and every individual error. POV scenes preserve the literal source macro with the intended radius; uncertain colors are gray.

No external packages are required beyond the existing Python 3.12 environment. From repository root:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage phase1
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage screens
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage fit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage audit
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage export
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.reproduce_r278 --stage light
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 synthetic
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 native
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.validate_r278 preservation
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest photo2.test_reconstruct_r278 photo2.test_reconstruct_r276 photo2.bead_debugger.test_surface
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m photo2.report_r278
povray +Iphoto2/review/r278/intended_N2696_h+1_p1.300_f0_tilt-8.pov +Ophoto2/review/r278/intended_N2696_h+1_p1.300_f0_tilt-8-pov.png +W762 +H955 +FN -D +A0.2 +WT2
```

The fit stage reuses saved models only when the Phase 1 hash agrees. To rerun optimization from scratch, first archive its model JSON files separately. For a cheap deterministic replay, rerun export for a named saved model with `python -m photo2.reconstruct_r278 export --name MODEL`. Phase 1 can also reproduce the selected output from the preserved failed control with `python -m photo2.bead_detection.phase1_r278 --select-saved`.

## Photographic atlas

'''
    for name in sorted({c['atlas'] for c in phase_cases}):index+=f'- [{name}]({name})\n'
    index+='\n## Candidate overlays and ledgers\n\n'
    for name in EXPORTED:index+=f'- [{name}: overlay]({name}-overlay.jpg) · [per-bead CSV]({name}-beads.csv) · [accounting]({name}-accounting.json) · [discrepancies]({name}-discrepancies.json)\n'
    (OUT/'README.md').write_text(index)

if __name__=='__main__':main()

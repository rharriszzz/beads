from collections import Counter
from photo2.r297.common import *
import numpy as np
out=BASE/'results/pilot';summary=read(out/'summary.json');state=read(out/'checkpoint.json');ids=read(out/'exports/manifest.json')['ids']
evals=[read(out/f'exports/evaluation-{i}.json.gz') for i in ids];best=evals[0]
old=read(ROOT/'photo2/r296/results/pilot/exports/evaluation-188.json.gz')
local=read(ROOT/'photo2/r295/results/R295-evaluation.json');comparison=read(out/'exports/r295-comparison.json')['changes']
sections=read(out/'exports/sections.json');primary=[s for s in sections if s['model']==best['id']]
oldmap={r['id']:r for r in old['observations']};newmap={r['id']:r for r in best['observations']};localmap={r['id']:r for r in local['observations']}
rows=[read(out/'candidates'/f'{i:06d}.json.gz') for i in range(state['next_id'])]
status=dict(Counter(r['status'] for r in rows));physical=dict(Counter(r['reason'] for r in rows if r['status']=='physical-rejected'))
selected=read(out/'candidates'/f"{best['id']:06d}.json.gz")
p=best['parameters'];pct=lambda n:f'{100*n:.2f}%'
metrics=[]
for split in ['train','validation','reserved']:
 for kind in ['region','patch']:
  a=old['summary'][split][kind];b=best['summary'][split][kind]
  metrics.append(f"| {split} {kind} ({a['n']}) | {pct(a['mean_containment'])} / {a['compatible']} | {pct(b['mean_containment'])} / {b['compatible']} |")
changes=[]
for id in ['E5-1633-0278','C-1729-0337','C-2038-0658']:
 a,b,c=localmap[id],oldmap[id],newmap[id]
 changes.append(f"| {id} | {pct(a['containment'])} · {a['index']} | {pct(b['containment'])} · {b['index']} | {pct(c['containment'])} · {c['index']} |")
localmeans={k:dict(old=float(np.mean([r['old_containment'] for r in comparison if r['kind']==k])),new=float(np.mean([r['new_containment'] for r in comparison if r['kind']==k]))) for k in ['region','patch']}
family=[]
for e in evals:
 q=e['parameters'];family.append(f"| {e['id']} | {q['count']} | {q['hand']:+d} / {q['topology']} | {q['winding'] if q['topology']=='closed' else 'free: '+str(round(q['turn'],4))} | {q['scale']:.3f} / {q['elevation']:.2f}° | {q['radius']:.4f} / {q['axial']:.4f} | {pct(e['summary']['train']['region']['mean_containment'])} | {pct(e['summary']['validation']['region']['mean_containment'])} | {pct(e['summary']['reserved']['region']['mean_containment'])} |")
sectiontable=[]
for r in primary:
 d=r['r296_common_delta'];sectiontable.append(f"| {r['section']:02d} | {r['n']} / {r['r296_common_n']} | {pct(r['mean']) if r['mean'] is not None else 'no regions'} | {100*d:+.2f} pp | {r['supported_sites']}/{r['modeled_sites']} | {r['cut_pairs']}/{r['continuous_pairs']} | {r['paper_samples']}/{r['predicted_visible_samples']} |")
improved=[r for r in primary if r['r296_common_delta'] is not None and r['r296_common_delta']>.01]
regressed=[r for r in primary if r['r296_common_delta'] is not None and r['r296_common_delta']<-.01]
regions=[r for r in best['observations'] if r['kind']=='region' and r['id'] in oldmap]
rank=sorted(regions,key=lambda r:r['containment']-oldmap[r['id']]['containment'])
examples=[]
for label,rr in [('Largest regressions',rank[:5]),('Largest improvements',list(reversed(rank[-5:])))]:
 examples.append('**'+label+' on the same native support:** '+ '; '.join(f"{r['id']} ({r['split']}): {pct(oldmap[r['id']]['containment'])}→{pct(r['containment'])}" for r in rr)+'.')
seams=[]
for e in evals:
 c=read(out/f"exports/circuit-{e['id']}.json");q=e['parameters'];seams.append(f"- Model {e['id']} ({q['topology']}, cut {c['seam_fraction']:.3f}): axis endpoint gap {c['axis_endpoint_gap']:.6g} source units; radial/tangent residuals {c['radial_endpoint_gap']:.3g}/{c['tangent_endpoint_gap']:.3g}; station increments {c['minimum_station_increment']:.3f}–{c['maximum_station_increment']:.3f}px. Near the cut, {c['measured_seam_neighborhood']['colored_without_predicted_material']}/{c['measured_seam_neighborhood']['colored']} colored cue samples lack predicted material. This is photographic contradiction evidence, not proof of a physical gap or join.")
report=f'''# R297 — inspectable full-necklace optimization

[Open the clickable whole-photograph debugger](r297/results/pilot/review/debug.html)
· [Native overlays and exports](r297/results/pilot/review/index.html)
· [Single-command instructions](R297_REPRODUCE.md)
· [Controlled diagnosis and ablations](R297_DIAGNOSIS.md)

R297 improves the search system and restores much of the useful R295 section while
continuing full-loop refinement. It does **not** establish a convincing reconstruction
of every bead or a unique count, hand or physical closure. The final primary remains
a conditional {p['count']}-position, hand{p['hand']:+d}, {p['topology']} hypothesis.
It has {best['visibility']['unsupported']} model-only sites and
{best['visibility']['below_point_one']} sites below10% modeled visibility.
No reconstruction is adopted as production truth.

## Changes justified by diagnosis

The old local regression was driven mainly by full-path station normalization and
minor winding, not camera/shape changes alone. R296's stored pitch was initializer
metadata; changing total count changed the old section's effective spacing. Paired
native tests reproduce the old local fit inside feasible full-loop models at two
different total counts. Index195→182 is a changed conditional correspondence, not
a discovery that either number is the physical identity.

R297 adds compact physical station restoration with exterior compensation confined
to a transition, separately adjustable local phase, and partial phase transport
through that transition. All are shared smooth fields; no observation is moved and
no old integer assignment is locked. Aggressive phase transport demonstrates actual
collisions and is retained as a failed approach. The selected transport coefficient
is {p.get('phase_transport',0.):.4g}. Every candidate still passes the full spatial
contact gate before photographic selection.

The objective now directly scores geographically balanced substantial supports,
including difficult sections, alongside the bounded ownership beam and photometric
constraints. A soft preservation term compares prior large-support performance on
the same observations, allowing3 percentage points of loss before penalizing the
worst prior-fit regression. This tolerance is an engineering tradeoff, not a confidence
interval. Patch and boundary ablations, including their mixed outcomes, are reported
in the diagnosis. No new optimization method has demonstrated superiority here;
the resumable coordinate/population search is improved rather than replaced.

Initialization retains all R296 hand/topology families, transplanted R295 local fits,
cold camera/count/shape families and open cuts at three locations. Population
diversity includes local-preservation and seam alternatives. Paired local rate
changes limit propagation into distant sections; overlapping phase changes and
rotated coordinate schedules improve regional refinement. Count, winding, camera,
spacing, shape and discrete ownership remain jointly re-evaluated. Each proposal
has a durable record, including rejection, competing assignments and score terms.

## Native photographic comparison

Mean containment / number compatible below use the same original support pixels.
Compatibility is≥80% on one first-hit surface with≥20-point rival margin. It is
**not** verified ownership, an observed bead count, or measured occlusion accuracy.
Training and validation are development evidence. R296 reserved outcomes are
**retrospective**, re-evaluated only after the final model freeze. There is no
untouched final photographic information in this experiment.

| Fixed evidence | R296 selected | R297 selected |
|---|---:|---:|
{chr(10).join(metrics)}

On R295's exact36 large supports, its original mean is
{pct(localmeans['region']['old'])}; R296 gives63.11%; R297 gives
**{pct(localmeans['region']['new'])}**. The corresponding123 bright-patch means are
{pct(localmeans['patch']['old'])},86.27%, and{pct(localmeans['patch']['new'])}.
The old patch and region channels share pixels and cannot be treated as independent
statistical replicates. Whole-loop and local denominators are never interchanged.

| Earlier problematic support | R295 containment · index | R296 | R297 |
|---|---:|---:|---:|
{chr(10).join(changes)}

{chr(10).join(examples)}

The gains are changes in compatibility with unchanged photographic measurements,
not merely composite-score gains. They remain development/retrospective evidence
on one repeatedly studied photograph. No independent new-image improvement,
physical-identity recovery, or calibrated accuracy is claimed.

## All32 geographic sections

The debugger maps these stations around the whole original photograph, covering
bead0, the earlier33/65/195 neighborhoods, the right descent, both major bends,
lower arc, left return and the final approach to the proposed cut. The review also
shows the worst large support in each of eight full-circuit sectors beside raw
pixels. There are {len(improved)} sections improving by more than1 percentage point
and {len(regressed)} regressing by more than1 point on their **common** supports.
Every remaining section is also reported, including failures.

N lists all evaluated large supports / supports shared with the R296 export.
R297 mean uses all evaluated supports; delta uses only identical common supports.
Buffer observations newly exported here are retrospective diagnostics, not fresh
holdouts. Support/site counts are conditional compatibility, not recovered bodies.
Cuts and paper are fallible cached photographic proxies; their denominators are
shown. A photographed irregularity never by itself makes a bead impossible.

| Section | N / common | R297 mean | Δ common R296 | Supported / modeled sites | Cuts / continuity pairs | Paper / predicted samples |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(sectiontable)}

[Machine-readable section comparison](r297/results/pilot/exports/regions.csv),
[complete failure atlas](r297/results/pilot/exports/failure-atlas.json.gz).

## Competing families and the seam

| Candidate | Count | Hand / topology | Minor winding or open beads/turn | Scale / elevation | Radius / axial | Train large mean | Validation | Retrospective reserved |
|---|---:|---|---|---|---|---:|---:|---:|
{chr(10).join(family)}

Each family is retained on its development score, before retrospective reserved
inspection. Different local fits favor different hypotheses; the finite ranking
does not identify the true count, winding, camera or shape. The best opposite-hand,
open and different-count candidates remain available in the viewer. The same index
in another family need not denote the same body. No repeating color pattern is used.

{chr(10).join(seams)}

Closed candidates enforce integer winding, index uniqueness, tangent/frame/phase
closure and monotone spacing, with contact checks spanning the cut. Open candidates
have separate endpoints and no artificial closing edge; all spatially near surfaces
are nevertheless checked. The reference was periodic before fitting and **does not
establish physical closure**. Per-model circuit exports include33 boundary probes,
endpoint coordinates, cross-cut contact witnesses and measured cut-neighborhood
cues. The selected model's independently replayed minimum separating-plane margin
is {best['contact']['minimum_gap_units']:.6g} source units. This is a conservative
separation lower bound under the fitted shape, not an exact closest distance or a
certificate of photographic correctness. Numerical geometry is not interval arithmetic.

## Bounded experiments and reliability

Four128-proposal first-generation objective ablations are retained. A matched128
proposal preservation control,512-proposal medium search, paired native mechanism
controls and bounded transition probes led to the final program. The final pilot
completes{state['next_id']} proposals in{state['elapsed_seconds']:.1f}s cumulative
search and stops for{state['stop_reason']}. Native exports add separate overhead.
Its status counts are `{status}`; physical rejections are `{physical}`. Inconclusive
certificates are never relabeled as collisions or admitted to selection.

The complete histories, failed approaches, source versions and deterministic seeds
are retained. The final program received no scientific changes after this pilot
started, and final parameters were frozen before retrospective reserved/buffer
tracing. The prior medium search and earlier controls use their archived versions.

Twenty-eight contracts pass: unchanged R296 placement, full-path/local restoration,
seam families, aggressive-transport collision witnesses, material accounting,
source/evidence/seal guards, writer locking, actual SIGTERM and uninterrupted versus
35→42 restart equivalence through autonomous refinement, including post-write crash
recovery. Final native position/contact/ray/support replay, original-photo equality,
prior-science preservation and Chromium desktop/narrow/offline review receipts are
linked below. The source photograph, all Phase1 observations, R294–R296 results,
feedback and beads.pov are preserved. There is no Phase3 or production adoption.

## Using the result and deciding on more computation

Run `python3 photo2/phase2_autofit.py --preset medium --output photo2/output/r297-new`
without activating a virtual environment. The debugger works from a local file or
`--review-only --serve`; choose a location or section, inspect the raw photograph,
compare candidate surfaces, then read measured support and separate model evidence.
Filters expose weak ownership, split material, occlusion competition, nonnearest
surface assignments, conflicting colors, paper occupation, old-fit regressions and
family disagreement. Search-beam hypotheses remain distinct from native modal owners.
Downloadable full positions retain every unsupported site.

Additional computation can explore the documented family and improve these
compatibility measures; it cannot establish a unique reconstruction from the score.
Use the region table and remaining failures to decide whether a bounded longer run
is worthwhile. The delivered run is sealed; a subsequent run needs a new destination,
and all previously inspected evaluation data remain retrospective. No multi-hour
search is launched here. Stop for user review; no automatic R298.

[Reproduction and launch examples](R297_REPRODUCE.md),
[native/preservation verification](r297/results/verification.json),
[browser verification](r297/results/browser-check.json),
[delivery receipt](r297/results/delivery.json).
'''
(ROOT/'photo2/R297_REPORT.md').write_text(report)
save(BASE/'results/final-comparison.json',dict(primary=best['id'],status_counts=status,physical_rejections=physical,local=localmeans,improved_sections=[r['section'] for r in improved],regressed_sections=[r['section'] for r in regressed],protocol=summary['evaluation_protocol']))
print('Report generated:',len(report.split()),'words')

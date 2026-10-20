"""Render the report's numerical tables and complete sequences from frozen results."""
from common import *


def mdtable(headers,rows):
    return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])


def frac(r):
    return f"{r['agree']}/{r['n']} ({100*r['agree']/r['n']:.2f}%)"


def sequence(s):
    return '\n'.join(f'{i:03d}–{i+15:03d}  '+' '.join(s[i:i+16]) for i in range(0,208,16))


def main():
    effects=read(OUT/'correction-effects.json')['states']
    p=read(OUT/'pattern208.json');v=read(OUT/'evaluation.json');t=read(OUT/'training-agreement.json');g=v['heldout']['A208_geographic'];q=v['heldout']['A208_occurrence'];f=t['current1041']['provisional']
    replacements={
      'MAKER_EFFECTS':mdtable(['R343 cohort with applied judgments','Indexed n','Supported','Conflicting','Insufficient'],[['None' if not e['changed_ids'] else ' + '.join(e['changed_ids']),e['indexed'],e['supported'],e['conflicting'],e['insufficient']] for e in effects]),
      'STRICT_SEQUENCE':sequence(p['strict_sequence']), 'PROVISIONAL_SEQUENCE':sequence(p['provisional_sequence']),
      'COHORT_TABLE':mdtable(['Cohort / colors','Indexed n','Supported','Conflict','Insufficient'],[[k,r['n'],r['supported'],r['conflicting'],r['insufficient']] for k,r in v['strict_cohorts'].items()]),
      'COLOR_TABLE':mdtable(['Recorded color','Provisional fit','Guarded geography held-out','Whole-occurrence held-out'],[[c,frac(f['by_color'][c]),frac(g['by_color'][c]),frac(q['by_color'][c])] for c in ['black','red','yellow']]),
      'AUTHORITY_TABLE':mdtable(['Source authority stratum','Provisional fit','Geography held-out','Occurrence held-out'],[[c,frac(f['by_authority'][c]),frac(g['by_authority'][c]),frac(q['by_authority'][c])] for c in f['by_authority']]),
      'REGION_TABLE':mdtable(['Frozen geographic block','Provisional fit','Geography held-out','Occurrence held-out'],[[i,frac(f['by_region'][str(i)]),frac(g['by_region'][str(i)]),frac(q['by_region'][str(i)])] for i in range(12)]),
      'OCCURRENCE_TABLE':mdtable(['Conditional occurrence q','Provisional fit','Geography held-out','Occurrence held-out'],[[i,frac(f['by_occurrence'][str(i)]),frac(g['by_occurrence'][str(i)]),frac(q['by_occurrence'][str(i)])] for i in range(13)]),
      'MODEL_TABLE':mdtable(['Fixed predictor','Guarded geography','Whole occurrence','Geographic gain nats','Own closure'],[[m['model'],frac(v['heldout'][m['model']+'_geographic']),frac(v['heldout'][m['model']+'_occurrence']),f"{v['heldout'][m['model']+'_geographic']['gain_nats']:.4f}",'yes' if m['divides_own_total'] else 'no'] for m in v['model_closure']]),
      'MATCHED_TABLE':mdtable(['Fixed cohort / label epoch','Geographic all targets','Occurrence all targets','Geographic unchanged-color targets','Occurrence unchanged-color targets'],[[name,frac(r['geographic']['all_targets']),frac(r['occurrence']['all_targets']),frac(r['geographic']['unchanged_color_targets']),frac(r['occurrence']['unchanged_color_targets'])] for name,r in v['cohort_comparisons'].items() if not name.startswith('frozen_')]),
      'TENTATIVE_TABLE':mdtable(['Position','Prediction','Observed counts','Agreeing geographic blocks','Explicit pigment judgments','Shrinkage score','Actual sources'],[[e['residue'],e['provisional_color'],', '.join(c+':'+str(n) for c,n in e['counts'].items()),','.join(map(str,e['sections'])),e['explicit_pigment_records'],f"{e['smoothing_probability'][e['provisional_color']]:.3f}",'; '.join(e['ids'])] for e in p['entries'] if e['tentative']]),
      'MISMATCH_TABLE':mdtable(['Source ID','Position','Recorded / provisional','Native x,y','AB','A index / q / region'],[[r['id'],r['position'],r['color']+' / '+r['prediction'],', '.join(f'{x:.2f}' for x in r['xy']),','.join(map(str,r['ab'])),f"{r['index_A']} / {r['occurrence']} / {r['region']}"] for r in t['current1041']['mismatches']]),
      'DIVISOR_TABLE':mdtable(['Proper divisor','Strict witness positions','Strict colors'],[[d['period'],','.join(map(str,d['witness_positions'])),' / '.join(d['colors'])] for d in v['proper_divisor_obstructions']])}
    text='''# R344 — recovered graph-paper presentation, sequence and measured agreement

[Offline pattern and photographic review](r344/review/index.html) · [Reproduce](R344_REPRODUCE.md) · [All numerical results](r344/evaluation.json) · [Independent checks](r344/verification.json)

**199 of 208 positions now satisfy the unchanged strict support rule; two conflict and seven lack sufficient support.** Both new individual maker judgments are applied as yellow, with no identity, XY, lattice coordinate, link or winding changes. The provisional complete block matches **1,038/1,041 indexed photographic colors (99.71%)**. This is fitted agreement with recorded labels, not independently measured physical accuracy.

## The graph-paper presentation

![Alternating six/seven-bead graph paper, strict and provisional](r344/graph-paper.png)

The maker’s coordinate construction works exactly: x=a−b, y=a+b and 2k=x+13y. In the central strip −1≤x<12, even rows have six beads and odd rows seven. Moving right adds1, up-left adds6 and up-right adds7. The 208 chosen beads occupy sixteen row pairs, 0≤y<32, exactly once. Reading proceeds upward; the first row is indices0–5 and the next6–12.

Thin START and END lines lie immediately below the first included row and above the last: y=−0.5 and31.5. White background is the chosen block; gray continuation contains eight extra rows (52 indices) at either end. All colored beads are identical ellipses; strict unknowns retain ?. A separate provisional panel marks inferred entries with dashed blue outlines. No pigment or photographic evidence changes for the display.

The zero-index seam is (Δa,Δb)=(6,−7), hence (Δx,Δy)=(13,−1), not a same-height left/right wrap. Optional lateral strips in the interactive view repeat exactly the same k and color. The actual spatial recurrence (16,16) becomes (0,32) and adds208. Conditional H=(214,201) becomes (13,415)=13(0,32)+(13,−1), consistent with thirteen visual repeats plus the seam, without proving the physical winding.

The [interactive graph paper](r344/review/index.html) supports zoom, drag, optional indices/diagonal guides, seam copies and bidirectional highlighting with the one-dimensional sequence. Its selected position links to the same photographic IDs and current adjacency already used in the statistics. [Print A4 PDF](r344/graph-paper.pdf), [vector SVG](r344/graph-paper.svg), [numbered PDF](r344/graph-paper-numbered.pdf); PNG exports are2481×3507pixels at300dpi.

[The standalone general method](GRAPH_PAPER_6_5_BEADS.md) derives arbitrary-length intervals and stepped cuts. For L not divisible by13, the repeat need not be rectangular or purely vertical. An independent verifier checks936 current display sites,192 general length/origin/strip cases and24,544 boundary/ellipse tests. Selected-block membership remains208 unique indices; neither continuation nor lateral copies become new observations.

The previous R344 sequence/statistics delivery at37a23300 is retained under [pre-graph-paper-37a23300](r344/pre-graph-paper-37a23300/README.md); all thirteen sealed scientific products remain byte-identical. Its original scientific base remains R3436fa108f7. This extension changes presentation and its mathematical verification, not reconstruction results.

## The same block in string order

[Numbered one-dimensional strict/provisional graphic](r344/patterns.png).

These are string-order grids: left to right, then the next row; the 16-column layout is not a physical crochet-row claim. R=red, Y=yellow, B=black. Indices are **0–207**, with A=7a+6b, modulo2704. Index zero is the current reference C-1302-0316. Cyclic origin and positive direction are conventions, not a recovered original stringing start. The strict block has **62 red /60 yellow /77 black /9 unknown** entries; the best provisional block has **62 red /62 yellow /84 black**.

Authoritative strict sequence, `?` retained:

```text
STRICT_SEQUENCE
```

Separate best provisional complete sequence:

```text
PROVISIONAL_SEQUENCE
```

Download every individually numbered entry: [strict CSV](r344/strict-pattern.csv), [provisional CSV](r344/provisional-pattern.csv), [full provenance/confidence JSON](r344/pattern208.json). The offline review shows **13 rows of 208 addresses** and links each photographed occurrence to its native body, local numbered key and current adjacency. Solid circles are recorded colors, faint circles are predictions without indexed observations, blue dashed borders are tentative motif entries, and magenta borders mark mismatches. Only 1,041 of the conditional 2,704 addresses are photographically indexed; 1,663 lack an indexed observation. Some may be visible but unassociated, so this is not a count of physically unseen beads. Repeating the provisional block does not measure those missing beads.

## Exactly what changed

The reversible [correction ledger](r344/corrections.json) retains both original records and previous authority statements:

- P29 NEW-1519-2976, own photograph feature1: explicit **yellow**, superseding software red and general illustration approval. Its historical R343 metadata remains intact; a new explicit pigment record has precedence.
- P127 R332-R-0125-0118, own photograph feature1: explicit **yellow glass in shadow**, superseding software red.

P29 becomes five yellow observations in four blocks (5,6,7,8). P127 becomes three yellow observations in blocks**7,8,9**. Previously, its two yellow supporters spanned only8,9; the former red in7 now supplies the third *agreeing* block. Both conflicts therefore become strictly supported. Removing a disagreement alone would not have been sufficient if the third block were absent. No support threshold changes.

An independent one-at-a-time recount keeps all1,041 R343 observation IDs fixed:

MAKER_EFFECTS

[Full correction effects, color counts and geographic supporters](r344/correction-effects.json).

COHORT_TABLE

The original R3361039-ID set is retained without removals: R343196/4/8 becomes R344198/2/8 there. The two already-admitted extra records in the current1041 cohort explain its additional supported position62. Neither R344 improvement comes from adding or removing observations. The frozen710 cohort is unchanged and still cannot certify global indexing.

## Provisional entries and important alternatives

Strict support requires an uncontradicted color in at least three observations and three fixed geographic blocks. All208 residues have observations; no provisional entry here fills a completely unobserved residue. The seven insufficient entries have only software-derived black records: six have two observations;89 has three observations but two blocks. Their provisional black is useful but not strict. None of the nine tentative residues has an explicit individual maker pigment judgment.

TENTATIVE_TABLE

Scores are the existing fixed concentration3 shrinkage toward training color frequencies, **not calibrated confidence in physical truth**. Every tentative entry has a qualitative confidence statement and original photographic ID/XY/AB/authority in the JSON and clickable review. The provisional choices never overwrite photographic labels.

At83, yellow matches5/7 while red matches2/7; at189 yellow matches7/8 while red matches1/8. Keeping all seven insufficient entries black yields four important red/yellow completions: Y/Y has3 mismatches; R/Y has6; Y/R has9; R/R has12. The fit favors Y/Y, but this does not decide which native pigment or association is correct. Other colors at the insufficient positions would contradict their two or three current black labels; they are logically possible if those records are wrong, but have no positive color support.

## Inventory, fit and source authority

The selected active inventory contains **1,059 recorded observations**, of which**1,041 are indexed and18 unindexed**. This is not a physical bead census. Indexed colors are392 black,330 red,319 yellow; all active records include392 black,337 red,330 yellow. Historical excluded/phantom evidence stays preserved and excluded. All208 pattern positions have recorded support.

The provisional fit agrees with1,038/1,041 and disagrees with3/1,041. The strict block agrees with**1,011/1,011 evaluable observations**, disagrees with0 there and abstains on30/1,041 observations at its nine unresolved entries. Strict100% agreement follows its uncontradicted-entry definition; it is not an independent accuracy estimate. For the historical1039-ID cohort, the current provisional block agrees with1,036/1,039; strict1,009/1,009, abstaining30.

COLOR_TABLE

AUTHORITY_TABLE

Authority strata are derived from the retained source statements for this analysis: explicit individual pigment, approval of displayed labels, and native/software label. General approvals are retained as support and not promoted to individual pigment truth. The ledger contains123 entries:120 indexed/active and3 excluded; among the indexed records,37 are explicit individual pigments and83 are displayed-label approvals. All37 explicit indexed pigments agree with the provisional block and both held-out208 predictions. Those judgments were selected during earlier reviews and helped construct the current labels; they are not an independent random test set. No broad metadata reclassification occurs.

## Geography and all thirteen occurrences

Regions below are the same frozen12 photographic station blocks used in recent rounds; neither labels nor model scores choose new boundaries. Geographic held-out training removes the target block and both adjacent blocks, including cyclic adjacency0/11. Occurrence held-out removes the entire leading-A208-address occurrence. Every comparison uses the same target IDs.

[Native photograph with block overlay](r344/geography.png) — overlay colors denote blocks, not pigments.

REGION_TABLE

OCCURRENCE_TABLE

The occurrence numbers assume N2704/208/13 and the conventional origin. They are not independent proof of those assumptions. Full per-observation held-out probabilities and all mismatches are in [heldout-predictions.json.gz](r344/heldout-predictions.json.gz).

## Held-out models and unchanged cohorts

All models were fixed before comparison, using the same1,041 current observations, frozen folds and historical smoothing constants; this is a small hypothesis comparison, not a new length/winding scan. Flat208 geographic prediction gets**1,024/1,041 (98.37%)**; whole-occurrence gets**1,038/1,041 (99.71%)**. The existing104-parent hierarchy gets1,029/1,041 (98.85%) geographically and1,038/1,041 by occurrence. It is a predictor, not a different adopted pattern.

MODEL_TABLE

Frequency uses only training color frequencies; phase13 is a simple spatial/index-phase baseline. A104 tests half-length structure; A338 is the other200–399 divisor of conditional A2704. B207/B299 divide their own2691 total. A306 is a previously noted weak alias and does not close. Every occurrence comparison uses the same leading-A occurrence partition even for B, avoiding favorable alternative test sets. Gain is average log probability relative to the training-only frequency baseline, in natural-log units. A104's geographic log gain exceeds flat208 despite worse hard agreement because flat208 loses support in some folds; the hierarchy handles that sparsity better. Selecting only a favorable accuracy metric would miss this distinction.

For flat208 geography, **997/1,003** targets with at least one remaining same-position record are correct. Another38 targets have no same-position training record;27/38 succeed only through the black frequency fallback. Of17 geographic errors,11 are these cold positions and6 occur despite remaining support. Whole-occurrence testing retains same-position support for all1,041 targets. The all-black success therefore must not be interpreted as new measurement of every unresolved black residue.

MATCHED_TABLE

“Unchanged-color targets” excludes only the two R344 corrected IDs, holding both ID and target color fixed in the R343/R344 comparison. On the current cohort those1,039 unchanged targets improve geographically1,020→1,022 and by occurrence1,034→1,036; training still legitimately includes the corrected colors in other folds. On the fixed original1039 cohort, the matched unchanged subset has1,037 targets. No problematic observations are removed from the full evaluations.

Scoring the **same current provisional block** against the frozen original R336 labels gives1,006/1,039, versus1,036/1,039 with current corrected labels. This separates historical label corrections from observation selection. Neither cross-validation nor maker review of this same photograph is independent physical validation; previously choosing208 and targeting disagreements also creates selection dependence. No nominal binomial confidence interval is offered for these correlated observations.

## Exact remaining mismatches

MISMATCH_TABLE

All three are inherited software-red observations; none contradicts an explicit individual maker pigment. Their native body ownership/edge material remains difficult. R343 could not safely annotate their glass cores, and R344 does not fabricate new hue measurements or recolor them by the motif majority. The review provides actual native crops, current numbered neighborhoods and links. No bead is moved or reindexed to eliminate these residuals.

## What “shortest” can now mean

Every proper divisor of208 is contradicted by a pair of **strict** colors:

DIVISOR_TABLE

Any cyclic208-word with a smaller period has a proper divisor of208 as a period. These witnesses therefore prove that **every completion of this strict block has minimal cyclic period208**, under the current A indexing. They do not prove that this indexing, winding, N2704 or exact physical208 repetition is true. The three residual photographic contradictions still prevent that stronger claim. Broad alternative winding/global continuation tests are not repeated.

## One recommended next step

**Obtain targeted independent photographic reobservations of the three mismatching bodies at83/189, with their known neighboring beads visible.** The original image leaves those thin/edge glass regions unsafe, so another general classifier or majority vote has little value. These are the only contradictory recorded colors left; the other seven gaps are geographic-support shortages, and conditional208 minimality already has strict witnesses.

Cost: three localized closeups or equivalent direct maker inspection tied unambiguously to the native IDs/neighbors, followed by a bounded association/pigment check. Computational work is small: three local source/association checks and the fixed1,041-record evaluation, taking seconds for the existing numerical pipeline rather than a global search. The main cost is obtaining and inspecting unambiguous material evidence. No broad detector, rendering or winding campaign is needed. Success means independently established body identity and pigment for all three, preserving distinct physical beads. If they are yellow, strict support can reach201/0/7 without weakening the rule. If a red body is confirmed at its existing association, that is a substantive counterexample to the exact208 hypothesis and motivates a targeted indexing/design investigation. Either result is more informative than another high fitted score. Additional independent geographic support for seven black residues remains necessary afterward. **This next step has not begun.**

## Verification and stopping

The independent verifier preserves all1,059 original observation identities/XY,1,041 coordinates,2,290 links and H214,201; checks every primitive equation and distinct quotient/index; preserves maker pigments and old exclusions; rederives1,456 strict entries,18,738 held-out probability vectors and20 matched historical summaries without the producer prediction helpers; checks nine shortest-divisor witnesses and five literal native crops. Historical scientific hashes, the black implementation and all earlier results remain unchanged. Independent graph-paper math verifies directions, seam identity, nonrectangular cuts and copy colors without changing the scientific cohort. Fresh replay and actual offline/narrow browser interactions, including graph-to-string and string-to-graph highlighting, are recorded under r344. Native labels/identities and the physical closure remain hypotheses, not conclusions supplied by arithmetic verification.

STOP after scoped commit, push and remote verification; no automatic R345.
'''
    for key in sorted(replacements,key=len,reverse=True):text=text.replace(key,replacements[key])
    destination=OUT/'REPORT.generated.md' if OUT!=ROOT/'photo2/r344' else ROOT/'photo2/R344_REPORT.md'
    destination.write_text(text)
    print('REPORT',destination)


if __name__=='__main__':
    main()

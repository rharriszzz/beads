# R334 — maker corrections and an intensity-first black test

**The authoritative overlay now contains seven maker-confirmed red-to-black
corrections and one separate black-body reassociation.** Black classification
runs first, using only intensity immediately outside the measured reflection.
Hue cannot establish black. Only a clear not-black decision opens the red/yellow
body calculation; ambiguous black tests abstain.

The maker corrections resolve six of R333's original19 interruptions. Relearned
strong disagreements fall19→14, including one newly qualified disagreement.
Repeat-supported traces increase17→22 and201→255 observations. The partial208
tile gains four supported positions: **170 known,38 unknown**. This improves the
spatial reconstruction, but does not recover the actual maker-compatible shortest
stringing repeat. A new207 index-compression experiment illustrates the remaining
problem: it predicts well only by changing85–113 measured link equations and
collapsing34–48 occupied sites. It is rejected.

[Corrected native-photo/lattice viewer](r334/review/index.html) ·
[Exact maker mappings](r334/overlay/maker-corrections.csv) ·
[Ranked provisional suspects](r334/overlay/ranked-suspects.csv) ·
[Complete1600-support scan](r334/overlay/complete-classification.csv) ·
[Period results](r334/analysis/periods.csv) ·
[Reproduce](R334_REPRODUCE.md) · [Independent verification](r334/verification.json).

Baseline is R333 delivery `acd51b0bcd586e812e1979258de8b402094fb634`, branch
`photo-2-strategy-v3`. Original R330–R333 outputs, photographs, diagrams, expanded
keys and uncertainty remain intact. All revisions live under R334. There is no
new detector bank, physical fit, render campaign or adopted winding/count.

## Exact interpretation of the maker review

The actual R333 page was opened in Chromium. Its comparison photographs, diagrams
and expanded keys were inspected; screenshots and DOM evidence are retained under
`r334/development/`. Local numbers were resolved against their own photograph,
not treated as global indices. K-1904-2820 appears in two comparison panels with
identical keys; both references are preserved and identify the same observations.
MAT25 feature25 was mentioned twice and counts **once**.

| Named photograph | Panel / local feature | Stable observation | Original support(x,y) | Maker correction |
|---|---|---|---|---|
| E5-1616-2970 | case02 target /20 | E5-1616-2970 | (1616.857,2970.857) | red→black |
| NEW-1706-342 | case03 target /28 | NEW-1706-342 | (1705.088,343.122) | red→black |
| NEW-2207-1350 | case04 target /25 | NEW-2207-1350 | (2207.564,1350.534) | red→black |
| MAT25-K-2237-2196 | case05 comparison1 /25 | NEW-2237-2128 | (2236.232,2127.105) | red→black |
| K-1904-2820 | case05 comparison2; case10 comparison1 /36 | NEW-1942-2725 | (1942.281,2726.213) | red→black |
| K-1904-2820 | same comparisons /7 | C-1893-2771 | (1893.571,2772.429) | red→black |
| K-1904-2820 | same comparisons /33 | NEW-1828-2833 | (1826.528,2832.155) | red→black |
| R332-R-0025-0023 | case05 target /27 | R332-R-0025-0023 | (2069.407,831.655) | wrong-body location; see below |

All seven ordinary corrections preserve their measured location and lattice
association. They are accepted from maker review, regardless of any classifier
or periodicity score. The exact unrounded coordinates, original labels, lattice
coordinates, source assets and11 panel references are in the correction ledger.
No numbering ambiguity remains. C-1284-0332 was not named as a confirmed correction
and therefore keeps its recorded red label in the authoritative overlay.

## The misplaced marker is a different-body association

The original feature27 lies at the lower edge of a yellow body. That yellow body
already has a distinct recorded observation, **C-2058-0820=(2058.05,819.875)**,
which remains yellow and unindexed. It is shown as additional local marker31 in
the R334 close-up. The original R333 photograph/key remains unchanged beside it.
No yellow bead has been recolored into a black bead or silently removed.

The adjacent lower black body contains the cached colored reflection
REC266-P040667=(2067.2,843.9). That cache point is retained as an alias/evidence
hint, not another bead and not a physical center. Native inspection selects
**(2076,845)** as an actual dark-material representative on this black body,
14.89px from the old marker. The bounded component contains171 native material
pixels. The new representative is a sampled material location, not a measured
bead center, geometric prediction or reflection centroid.

The site remains(a,b)=(25,23); the same three working neighbors remain. All three
moved native corridors pass the original filled-foreground/intervening-observation
gates, and their integer equations remain exact. Raw threshold masks alone cross
bright reflections, so their lower raw fractions are preserved separately from
the original filled mask. No link is added/removed and no lattice coordinate moves.
There is no duplicate occupied site or duplicate accepted black observation.
The yellow observation's old provisional site remains a proposal; the viewer
never paints it onto the accepted lattice as if indexed.

## Black first, without hue

The implementation follows the maker's follow-up instruction explicitly:

1. Construct the **same** conservative geometry for every pigment: radii9/12/15
   around recorded supports, clipped by neighboring-support Voronoi guards. These
   are sampling regions, not fitted body outlines or special black-bead shapes.
2. Find bright reflection seeds using maximum-channel intensity and local bright
   contrast. Grow through the bright shoulder so reddish/yellowish halos are not
   mistaken for pigment. Reflection detection does not depend on highlight hue.
3. Select the measured reflection lobe nearest the support and inspect the annulus
   immediately outside it: dilation4 minus dilation1, within the common geometry,
   excluding every reflection region. No hue-based paper mask enters this test.
4. Establish black only with at least25 annular pixels, four angular sectors,
   median encoded luminance≤.15, luminance upper quartile≤.20, maximum-channel
   median≤.30, maximum-channel upper quartile≤.40 and≥70% of pixels with every
   channel≤.35. Annular median luminance must also be≤.65 of adjacent reliably
   colored-reference brightness. Require two of three scales and no contradictory
   clear not-black scale. These explicit thresholds are operational, not a
   radiometric calibration.
5. A clear not-black decision requires two sufficiently supported bright annuli.
   **Only then** run red/yellow classification on body pixels after reflection,
   neighbor, paper and sharp-boundary exclusions. RGB/chromaticity quantiles,
   local lighting normalization and15/31/51-neighbor votes are allowed here.
   Training excludes the entire target geographic section. A black-test unknown
   stops with abstention; it cannot be rescued by the highlight's hue.

The lighting references for the first test also use hue-free common-region
intensity. Chromatic paper rejection is confined to the later red/yellow step.
The independent verifier checks that black and unknown decisions have **zero
red/yellow inference votes**, demonstrating the actual execution order rather
than merely describing a preferred interpretation.

The page shows native colors, excluded reflections(cyan), the first-test
annulus(amber), later body samples(green), actual sampled/excluded color swatches,
and pixel distributions against nearby colored bodies with stable IDs.
Specular descriptors never become physical centers.

## Whole-inventory scan and its limits

The scan covers1600 unique supports: all1064 recorded observations,263 additional
provisional groups(including all65 provisional black groups), and273 other
unassociated native groups. It rechecks all red labels, R330's six hypotheses,
R333's interruption ledger and R332 additions. Expected pattern color is absent
from both pigment stages; it enters the **later ranking only**.

The intensity test gives605 black,647 not-black and348 unknown decisions. The
later red/yellow calculation abstains on98 more, giving446 total abstentions.
These are support-level decisions, not a census of physical beads. Of65 provisional
black groups,62 pass the intensity test and three remain unknown; none gains a
lattice association or accepted-bead status merely from darkness.

On the exposed maker batch, six black bodies pass automatically and two abstain:
C-1893-2771 and NEW-2237-2128. Both remain authoritatively black. In particular,
C-1893 has a reddish, moderately bright surrounding response and does not satisfy
the strict all-channel darkness test consistently. Hue is not used to force it.
This is a development/control result, **not independent accuracy** on examples
used to shape the method.

The scan ranks157 red-labeled possible black supports.105 meet the strict
intensity decision:46 recorded,38 provisional and21 unassociated-native supports.
All additional suggestions remain provisional;122 strict color-change flags span all scanned support types. The separate automatic experiment changes54 indexed black-label hypotheses, and promotes zero into the authoritative overlay. Eight recorded candidates combine
body evidence, at least two working links and a separately strong R333 spatial
expectation: NEW-2237-1522, REC266-P032517, C-1284-0332, NEW-2257-2004,
NEW-2060-796, NEW-2186-2343, NEW-2167-1179 and NEW-1920-531.
The remaining four unconfirmed R330 red-to-black hypotheses also pass the new
intensity-first screen; this is renewed support, not new maker confirmation.

Geographic control tables retain all12 sections and separately summarize the
fixed2/5/8/11 sections(343 unreviewed historical observations). Historical R161-associated controls give23 agreements,
two disagreements and eight abstentions among33 observations. One disagreement
is C-1284-0332, already an unconfirmed R333 black hypothesis conflicting with its
historical red association; the other is yellow C-1243-0349 predicted red in the
later calculation. Neither is changed in the authoritative overlay. The R161
labels/associations are exposed and potentially imperfect, so this is a transparent
regression/control comparison rather than a newly blinded accuracy measurement.
The safeguards prevent these automatic flags from becoming accepted opposite errors.

## Matched spiral comparison

The first comparison freezes all1041 IDs,2285 links, lattice coordinates, original
R333 weights and geographic folds. Only seven maker color labels change. The
second includes the separate moved-body association; image location changes,
but lattice geometry remains identical. Automatic hypotheses are a third,
explicitly unaccepted experiment.

| Layer | Relearned disagreements | Original19 resolved | Repeat-supported traces | Supported observations | Partial A208 known/unknown |
|---|---:|---:|---:|---:|---:|
| Original R333 | 19 | 0 | 17 | 201 | 166/42 |
| Seven ordinary colors only | 15 | 5 | 20 | 231 | 170/38 |
| Maker colors + distinct-body reassociation | 14 | 6 | 22 | 255 | 170/38 |
| Provisional automatic experiment | 12 | 14 | 24 | 266 | 178/30 |

The six resolved original interruptions are E5-1616-2970, NEW-1706-342,
NEW-2207-1350, C-1893-2771, NEW-1828-2833 and R332-R-0025-0023. Thirteen original
ones remain, and **REC266-P076585=(1699,1594)** newly qualifies after a distant
maker correction makes its three examples agree on black. A new disagreement is
a rule flag, not proof that its recorded red is wrong.

The learned local rules stay black–red3/3 and black–yellow2/2. Black–yellow's
continuation score rises.78194→.80211. The measured regular cover still contains
59 traces/592 distinct observations, maximum lengths16/15. **No original selected
regular trace becomes longer in the matched continuation comparison.** The gain
is stronger correspondence across repeated occurrences, not newly established
physical links or a closed full spiral. Flexible segmentation can redistribute
nodes, so its coverage is not a monotone accuracy measure.

Spatial(16,16) agreement rises698→703 of748 pairs(93.3→94.0%). Applying all
strict additional black hypotheses instead lowers it to691, despite eliminating more
of the old interruption flags. This is direct evidence against blanket automatic
recoloring. The automatic layer is not adopted, and its fitted label agreement
is never presented as photographic accuracy. Separate feedback scores evaluate
automatic training changes only on987 unchanged authoritative target labels: A208
hierarchical prediction worsens by.0121 nats, independently recomputed. This supports
keeping those54 indexed hypotheses provisional.

## Renewed shortest-pattern search

All200–399 lengths, including incompatible multiples of13 as diagnostics, plus104
are reevaluated under A=7a+6b and B=6a+7b. The185 maker-eligible lengths remain
explicit. All40 saved map/convention scans use their common original900-observation
cohort, with18 exact-divisor fits and176 own-map cached G comparisons. Nine whole-
section/phase-preserving controls repeat the full map/period selection. Black-weight
and adjacent-section exclusion controls are separate from the frozen-weight comparison.

| Predictor | R333 log gain | Maker overlay log gain | Maker overlay label agreement |
|---|---:|---:|---:|
| A208 flat | .5943 | .6100 | 90.3% |
| A208 hierarchical(104 parent) | .8073 | **.8327** | **93.0%** |
| A208 hierarchical, adjacent sections excluded | .6957 | .7279 | 87.3% |
| A306 / B305 flat alias | .1242 | .1260 | 51.6% |
| B207 flat | −.0561 | −.0597 | 35.2% |
| B299 flat | −.1354 | −.1329 | 31.7% |

Gains are natural-log units per weighted observation, not independent accuracy.
The authoritative208 consensus has170 known/38 unknown slots; A306 and B305 still
have44 known with262/261 unknown,87/86 wholly unobserved. B207 and B299 have14 known,
193/285 unknown. None of those unknowns is silently filled.

All18 maker-compatible exact-divisor fits on saved windings remain negative;
the best is saved-16-A/P302,−.0165. The maker-compatible shortest-repeat range is
therefore **not genuinely narrowed globally** by these color fixes. Current A's
count2704 permits208/338 in the range, both excluded by the non13 maker fact;
current B's2691 permits207/299, both poor predictors. The working H stays(214,201).

Two substantive structural diagnostics go beyond another flat period scan:

- Alternative global primitive-family conventions can expose a256-position
  spatial alias:7a+b gives.215 gain, but its own conditional N1699 does not close
  at256 and it changes which family is string-step1. Other conventions create
 34 or82 duplicate sequence indices. These diagnostics cannot override R161's
  established direction relationships or become physical counts.
- A repeat-derived **whole-stripe** transformation shifts all observations in a
  stripe coherently after each16-step spatial recurrence. Across16 possible cuts,
  it raises A207 gain to.533–.563 and suggests arithmetic N2691=13×207. However,
  each version changes85–113 existing boundary equations and creates34–48 duplicate
  lattice occupancies. All are rejected. A strong periodic fit obtained by
  collapsing real neighbor relationships is not a recovered design.

The specific unresolved structure is the transverse/row continuation connecting
these same-phase repeated features. Correct pigments strengthen the(16,16)/208
spatial tile, but supply no independently justified reconnection that turns it
into a non13 stringing repeat with whole-necklace closure. More color relabeling
alone cannot resolve that index/topology question.

## Verification, performance and delivery

The compact offline page preserves the exact R333 before panels and their local
number keys; after panels use identical native pixels, corrected overlays and
matched lattice diagrams. The relocated black support, old yellow marker and
separate yellow observation are annotated together. All1600 support IDs can be
inspected, including optional unassociated candidates; unindexed observations
are not plotted at fabricated accepted lattice sites. Before/after layer switches,
three directions, saved maps, A/B/reversal, zoom/pan/click/recenter and explicit
body/reflection/annular pixel switches are checked in the actual browser.

Independent code checks all11 panel references, eight unique maker corrections,
one moved image support,1041 unique sites/one component,2285 equations, three moved
native corridors,4800 native annular tests,399 hue-free lighting anchors,1624
matched period fits(max difference1.1×10⁻¹⁶),419 measured paths/4496 link incidences,
16 rejected stripe transformations and22 literal crops. R161 remains33/40
associations,25/25 interior,65/86 links,45/45 interior,zero wrong retained links;
the exposed extended check remains36/40 and74/86. All346 sealed historical inputs
remain exact. These numerical/pixel checks do not certify unreviewed body identities.

The [fresh replay receipt](r334/performance.json) records exact parsed scientific
equality, including all before/after layers, excluding measured time only.
It takes about104s end-to-end including parsing/comparison, with a2.71GiB peak.
Per-process times and peak memory are explicit; classifier inference after imports
is about9.45s, while serialization/comparison adds cost. Main analysis takes52.37s;
independent numerical verification19.54s. Supplemental controls and review generation
are separately timed. This is a bounded cache/native-pixel workload, not a detector
speedup or convergence estimate.

Earlier RGB-body and luminance-only experiments are preserved as superseded
approaches. The maker's follow-up selects intensity-first, all-channel darkness
with abstention before red/yellow inference. Development also caught an empty
material-component fallback, a duplicate CSV metadata keyword and a NumPy scalar
viewer export issue; sources/failures are retained. No failed epoch supplies
accepted corrections or a recovered design.

R334 stops after scoped commit/push and independent remote confirmation. The eight
maker corrections are authoritative in their overlay; all further automatic edits,
index transformations, repeats and counts remain unadopted. No automatic R335 or
model/session switch is authorized.

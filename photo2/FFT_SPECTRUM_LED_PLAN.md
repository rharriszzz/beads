# Spectrum-led FFT direction experiment — R247 proposal

**Proposal only; stop for user approval before implementation.** The photograph
is the primary problem. First establish reproducible directional structure;
helicity comparison must not influence location, width, band or peak selection.
User reviewed R244–R246 and requested this new bounded proposal and preservation
of the methodological clarifications. Documentation maintenance is authorized;
new experiment code, spectra, renders and measurements are not yet authorized.

## Maker's procedure and what remains unknown

The original interactive sequence, reaffirmed by the maker, is:

1. Increase the lower spatial-frequency cutoff until the bright central spike
   disappears.
2. Decrease the upper cutoff until the three opposite peak pairs associated
   with bead directions become distinguishable.
3. Inspect both the peaks and their reconstructed spatial patterns.

This is the **primary procedure to investigate**, not a retrospective description
of R243/R244. Those runs used reasonable bead-diameter-derived starting bands,
but did not reproduce the maker's spectrum-led selection. Their inconclusive
results do not settle whether this procedure can expose the three directions.

The original explorer's startup circle (diameter 200px, softness 0.20) implies
sigma about 20 native pixels; recent experiments used roughly 43–57px. Actual
interactive settings were not saved. Neither width range nor any numeric cutoff
is maker-established truth. Preserve [the source-settings audit](review/r244/explorer-settings-audit.json)
and [R244–R246 evidence](FFT_CURVATURE.md) as historical records.

## Three ways to investigate selection

| Method | Role in this proposal |
| --- | --- |
| Manual replay of the maker's sequence | Recommended primary: retain slider/cutoff states, visual reasons and individual reconstructions; no helicity display during selection |
| Radial-profile-assisted visual selection | Supporting diagnostic: show the central-lobe shoulder and candidate frequency radii alongside the 2D spectrum; radial averages alone cannot identify the directional pairs |
| Automated central-lobe/peak-band selection | Later possibility after the visual choices are understood and reproducible; do not introduce an unvalidated automatic rule in this first experiment |

The older fixed bands are historical comparisons, not a fourth primary method
or limits on the search. Circular Gaussians isolate width and cutoff effects.
The previously implemented elongated-window/straightening methods remain available
for other uses, but are not additional factors in this bounded calibration.

## Proposed experiment

1. **Choose three development locations from raw photographic context:** two
   relatively straight sections with different red/yellow/black mixtures and
   one gently curved section. Prefer complete support for the largest window;
   record centerline position, tangent, curvature and selection reasons before
   viewing new spectra. Predeclare six spatially separated transfer locations
   with varied orientations/appearance at the same time. No coordinates are
   selected or measured in this proposal. These are reserved for the new
   procedure on a previously studied photograph, not untouched blind data.

2. **Compare circular Gaussian sigma = 20, 30, 40 and 55 native pixels.** Use the
   original photo grid, without image stretching or straightening; express angles
   relative to the tangent afterward. Use the explorer's circular Gaussian with
   a 5-sigma support radius (negligible boundary weight), with square array storage.
   Keep sigma, support radius and diameter explicitly distinct. Compare V=maxRGB
   and Y=0.299R+0.587G+0.114B at identical locations and widths: 24 development
   channel/width cases before cutoff choices. No assumption that sigma20 or the
   recent larger widths are correct; no color normalization or channel fusion.

3. **Replay the cutoff sequence for each case.** Begin with the unfiltered
   spectrum and a fixed documented display scale; do not let moving cutoffs
   silently change contrast. Show a companion central-lobe view/profile if the
   brightest bins overwhelm the display. Raise the lower radius until the bright
   central lobe, not just the single DC bin, is excluded; preserve before/after
   views and any uncertainty about its extent. Hold that lower radius while
   reducing the upper radius to the first clearly interpretable directional
   group. Save the sequence and neighboring cutoff settings, not just a selected
   final image. If there is no clear band, or several plausible bands, retain that
   outcome. Do not stop solely because exactly three peaks remain.

   Use the same visual rules and exploration budget for V/Y. Cross-apply bands
   selected from either channel to the other, so a channel-specific choice is
   distinguishable from a channel advantage at matched cutoffs. Record all
   frequencies in cycles/native pixel and the explorer's percent convention.
   Gaussian width changes Fourier resolution; compare physical frequency axes
   and resolution estimates, not FFT-bin numbers or apparent sharpness alone.

4. **Inspect candidates and explain geometry before giving family names.** Reuse
   the source conjugate-pair finder and phase-preserving inverse machinery;
   exclude its forced origin and do not allow top-k fallback to manufacture
   resolved pairs. Show raw crop, Gaussian weights/weighted V/Y, unfiltered and
   filtered FFTs, every retained candidate pair, and each pair's individual
   inverse over the same photographic context. Record angles, radii, strengths,
   breadth/resolution and cutoff/width sensitivity. Extra candidates remain
   visible; fewer than three is a valid result.

   Check whether reconstructed bands follow visible bead-row structure rather
   than only highlights, color changes or the rope outline. A reciprocal vector
   is normal to its spatial constant-phase bands; its plotted angle is not
   automatically a bead-neighbor angle. For a proposed two-vector reciprocal
   basis, test whether a third candidate is consistent with a signed sum or
   difference within resolution and whether direct-basis inversion gives plausible
   row spacings/orientations. Retain sign, harmonic and permutation alternatives.
   Initially name observed families A/B/C; attach physical 1/6/7 labels only with
   explicit spatial and reciprocal-geometry evidence. A 6/7 ambiguity stays
   unresolved. Nominal unwrapped angles are not camera-projected photo angles.
   Do not use a best-fitting hand to choose the band, peaks or assignments.

5. **Freeze before transfer or hand comparisons.** Review development evidence
   with the user, then record one selected width or a small justified width set,
   the cutoff-selection rubric, display scaling, candidate/ambiguity rules,
   uncertainty conventions and bounded sensitivity checks. Freeze the adaptation
   procedure, not necessarily identical numeric cutoffs for every location:
   any local spectrum-led adjustment must obey the recorded rubric, have the
   same budget, and preserve its decision trail. If visual decisions cannot be
   stated reproducibly, remain in calibration rather than claiming a freeze.
   Hash the procedure/inputs and save decisions before applying it to the six
   additional sites. No helicity scores are computed or shown during selection.

6. **Evaluate directional transfer first.** At the six predeclared sites, retain
   failures and compare candidate frequencies and tangent-relative directions,
   uncertainty, nearby-center stability and neighboring cutoff/width choices.
   Report how often a supported three-direction interpretation survives, why
   each physical-family assignment is justified, and how often V/Y disagree.
   Camera projection can change relative angles along the necklace; do not
   demand identical angles or use a global hand fit to enforce consistency.
   Neighboring samples/channels are correlated, and consistent color/outline
   artifacts can also persist. Only after frozen extraction and review of this
   evidence would a separately identified helicity comparison be appropriate;
   it is not a gate or tuning objective for this experiment.

## Evidence, controls and stopping points

Use existing known-helicity synthetic examples to check coordinate signs,
conjugacy, frequency scaling, reciprocal-basis interpretation and inverse phase.
Keep both mirror hands available without favoring either during selection.
They check the mathematics; they do not replace photographic development or
supply a hand-dependent peak-selection score. Do not launch another broad render
sweep, segmentation project, complete bead inventory, indexing or global fit.
Exact seven-of-6/six-of-7 closure is not required.

The review packet should put raw/windowed images, marked spectra and individual
inverse contributions side by side for each development location/width/channel,
with a compact decision table and explicit ambiguous examples. A successful
calibration produces an understandable, repeatable selection procedure; successful
transfer additionally requires spatially credible, stable directional structure
at separated locations. Clean spectra, three strongest pairs, or a consistent
hand score alone are insufficient. No unique helicity is promised.

**Current stop:** approve or revise this proposal. No new experiment has run.
**First implementation milestone, if approved:** three-location width/band replay
and a small illustrated review before freezing transfer rules. Preserve raw and
curated evidence, source hashes and reproducible parameters. Follow standing
scoped documentation/commit/push/remote-status verification at bounded stops.
Recommend Astra/High for geometric interpretation without claiming current model
identity. No `/new` needed for proposal review; a fresh session is reasonable
before implementation, reading this plan and the current handoff first.

# R249 — provisional FFT transfer experiment

## Procedure frozen before transfer

User authorizes selecting a provisional method from D1–D3 and recorded R248
advice, then applying it unchanged to six previously reserved photographic
locations. This supersedes R248's review stop. Unanswered review questions remain
unanswered; numeric choices below are Codex decisions, not maker confirmations.

Three options considered: one fixed width; a primary width plus a fixed small
sensitivity panel; or local visual adaptation. Use the second. It exposes width
dependence while keeping the primary result and all comparison settings fixed.
Only D1–D3 spectra were consulted before the freeze. No R249 transfer FFTs were
computed before [freeze.json](review/r249/freeze.json) was saved and committed.

- Primary circular Gaussian **sigma30 native pixels**, support radius5sigma;
  native image grid, rounded center, no stretching, mean removal or normalization.
  Full-support failure is recorded, never padded or moved to a better location.
- **V and Y separately**, identical locations/weights/frequency limits. Y uses
  the explorer's .299R+.587G+.114B definition. No fusion or channel selection.
- Exclude radius **2/(2πsigma)** around DC: primary .01061 cycles/pixel, or1.50%
  in explorer units. This is a conservative, reproducible approximation to the
  visually chosen central cut in development, not a claim to have learned an
  exact central-spike boundary. Keep bright side lobes; flag residual skirts or
  clipped lobes. No upper cutoff.
- Reuse R248/source qualification: origin excluded; reject maxima created by
  cutting the spectrum; prominence≥3; separation1.5 window-resolution scales.
  Preserve up to8 qualified alternatives; shortlist at most the **brightest4**
  by peak-bin squared magnitude. Ranks1–3 are the first candidates; rank4 remains
  an alternative. Fewer pairs is a valid outcome. Never pull rank5–8 into the
  primary shortlist to rescue a failed interpretation.
- Freeze four diagnostic settings: sigma20/40 with the same two-resolution
  central exclusion (.01592/.00796); sigma30 with central radius1.5/2.5 resolution
  scales (.00796/.01326). These diagnose sensitivity; none replaces primary.

Sigma30 is a compromise between merged sigma20 lobes and extra sigma40/55
substructure in development. It does not win in every channel/site. The same
rule gives primary plausible trios in D1 V, D2 Y and D3 V/Y; D1 Y and D2 V remain
unresolved. [Development-only replay](review/r249/development.json). This limited
success justifies a transfer test, not a validated extractor.

### Interpretation rules also frozen

Within the brightest4 retain **every** triple satisfying signed reciprocal-vector
closure within √3δf, where δf=1/(2πsigma). A supported spectral candidate additionally
needs pairwise axial-angle separation≥25°, no lobe within1.25δf of the central
cut, and no member below10% of the brightest pair's peak-bin power. Near-parallel
harmonics therefore do not count as three independent directions. Thresholds are
provisional screens, not estimated statistical significance or maker answers.
Record failed conditions and multiple trios, not just a winning assignment.

Compare frequencies and directions in the centerline-tangent frame. A match is
an axial one-to-one vector match within two combined window-resolution scales
for each pair. Keep all passing permutations. This tolerance includes frequency
and angle differences; it is fairly loose and is not an accuracy bound. A
primary trio gets **stable spectral support** only if matched supported trios
occur in at least3/4 fixed diagnostic settings; otherwise call it fragile.
Compare against all supported primary D1–D3 trios as a separate descriptive
measure. Reference similarity cannot change extraction or rescue a failure.

Visual assessment follows measurement: compare raw/weighted photographs,
spectra and all shortlisted individual complex-coefficient inverses; describe
whether bands follow plausible rows, reflections, color changes or the outline.
Numerical support alone does not establish three physical1/6/7 families. Angles
are reciprocal-vector angles; spatial constant-phase bands are perpendicular.
The centerline lies in the paper plane but beads are3D: tangent correction
removes local image roll, not perspective or surface projection. Do not infer a
hand merely from agreement with unwrapped nominal angles.

The six coordinates remain exactly T1–T6 from R248. They belong to a historically
studied photograph; this is reserved evaluation of a new frozen procedure, not
untouched blind data. Source, development and input hashes are verified before
transfer extraction. No indexing, repeat recovery or global optimization.

## Results

Pending transfer execution. This section will report every site/channel and
the fixed sensitivity panel, then stop with a bounded next-step recommendation.

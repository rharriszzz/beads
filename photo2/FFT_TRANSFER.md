# R249 — provisional FFT transfer experiment

**Completed: similar candidate three-direction structure transfers to four of
six locations, with stable support in both channels at two.** Y is more stable
than V in this small test. T4/T5 remain unsupported or unstable, and T3 retains
competing interpretations. Physical1/6/7 assignments and helicity are unresolved.

[Raw six-site overview](review/r249/raw-sites.png) ·
[all paired photographic/FFT/inverse comparisons](review/r249/INDEX.md) ·
[tangent-frame vector comparison](review/r249/tangent-frame.png).

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

- Primary circular Gaussian **sigma 30 native pixels**, support radius 5 sigma;
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
  cutting the spectrum; prominence≥3; separation 1.5 window-resolution scales.
  Preserve up to8 qualified alternatives; shortlist at most the **brightest 4**
  by peak-bin squared magnitude. Ranks1–3 are the first candidates; rank4 remains
  an alternative. Fewer pairs is a valid outcome. Never pull rank5–8 into the
  primary shortlist to rescue a failed interpretation.
- Freeze four diagnostic settings: sigma 20/40 with the same two-resolution
  central exclusion (.01592/.00796); sigma 30 with central radius1.5/2.5 resolution
  scales (.00796/.01326). These diagnose sensitivity; none replaces primary.

Sigma30 is a compromise between merged sigma 20 lobes and extra sigma 40/55
substructure in development. It does not win in every channel/site. The same
rule gives primary plausible trios in D1 V, D2 Y and D3 V/Y; D1 Y and D2 V remain
unresolved. [Development-only replay](review/r249/development.json). This limited
success justifies a transfer test, not a validated extractor.

### Interpretation rules also frozen

Within the brightest 4 retain **every** triple satisfying signed reciprocal-vector
closure within √3δf, where δf=1/(2πsigma). A supported spectral candidate additionally
needs pairwise axial-angle separation≥25°, no lobe within 1.25δf of the central
cut, and no member below 10% of the brightest pair's peak-bin power. Near-parallel
harmonics therefore do not count as three independent directions. Thresholds are
provisional screens, not estimated statistical significance or maker answers.
Record failed conditions and multiple trios, not just a winning assignment.

Compare frequencies and directions in the centerline-tangent frame. A match is
an axial one-to-one vector match within two combined window-resolution scales
for each pair. Keep all passing permutations. This tolerance includes frequency
and angle differences; it is fairly loose and is not an accuracy bound. A
primary trio gets **stable spectral support** only if matched supported trios
occur in at least 3/4 fixed diagnostic settings; otherwise call it fragile.
Compare against all supported primary D1–D3 trios as a separate descriptive
measure. Reference similarity cannot change extraction or rescue a failure.

Visual assessment follows measurement: compare raw/weighted photographs,
spectra and all shortlisted individual complex-coefficient inverses; describe
whether bands follow plausible rows, reflections, color changes or the outline.
Numerical support alone does not establish three physical 1/6/7 families. Angles
are reciprocal-vector angles; spatial constant-phase bands are perpendicular.
The centerline lies in the paper plane but beads are 3D: tangent correction
removes local image roll, not perspective or surface projection. Do not infer a
hand merely from agreement with unwrapped nominal angles.

The six coordinates remain exactly T1–T6 from R248. They belong to a historically
studied photograph; this is reserved evaluation of a new frozen procedure, not
untouched blind data. Source, development and input hashes are verified before
transfer extraction. No indexing, repeat recovery or global optimization.

## Results

The freeze was committed as `ffc9f56` before transfer extraction. Its SHA256 is
`77eca4c58e36bbd7bf3d3a7c591094469ce31456b73b176255a191c347c768c9`.
The extraction module and hashed dependencies remained unchanged. Six locations
× two channels × five fixed settings = **60 cases**, all with complete source
support. Each has 8 qualified alternatives; 480 pairs are saved and 240 enter the
four-pair shortlists. Those counts do not mean eight physical directions were
found. Missing evidence here means an unsupported trio, not an empty spectrum.

| Site | V primary result | Y primary result | Interpretation |
| --- | --- | --- | --- |
| [T1](review/r249/T1-comparison.png) | Stable,4/4 checks | Stable,4/4 | Strongest transfer example; both channels recover the same three pair identities, with different brightness ordering |
| [T2](review/r249/T2-comparison.png) | Stable,3/4 | Stable,3/4 | Common trio in both; sigma 20 fails, so not width-invariant |
| [T3](review/r249/T3-comparison.png) | Fragile,2/4; two trios | Stable,4/4 for common trio; another survives 3/4 | Useful Y advantage, with genuine assignment ambiguity preserved |
| [T4](review/r249/T4-comparison.png) | Fragile,2/4 | No supported primary trio | V trio differs from development-like branch; Y has a clipped low-frequency competitor |
| [T5](review/r249/T5-comparison.png) | No supported primary trio | No supported primary trio | Some directional peaks remain, but none of the primary brightest 4 triples meets the frozen rule |
| [T6](review/r249/T6-comparison.png) | Fragile,1/4 | Stable,3/4 | V's brightest pair is a broad central-adjacent competitor; Y exposes the shared row-like trio more clearly |

Thus stable spectral support is **V 2/6, Y 4/6**, at least one channel 4/6, both
channels 2/6. These are outcomes under a provisional screening rule, not detection
accuracy or six independent confirmations of the lattice. V/Y and overlapping
Gaussian settings share image content. Three V cases are fragile and one has
no primary trio; Y has two unsupported cases. T3's two supported primary trios
remain in each channel. [All cases and alternatives](review/r249/assessment.json).

### Directions and frequencies after tangent correction

The common branch at the four promising sites has reciprocal angles roughly
−57..−43°, +2..+10°, and +37..+59° relative to the local tangent. These are observed
bands, not angular constraints used in peak extraction. Their camera-dependent
spread is preserved. Spatial constant-phase bands are rotated 90° from them;
the near-tangent reciprocal family therefore gives nearly transverse spatial
bands. No physical 1/6/7 names are attached.

The table shows Y's common branch at each promising site for a compact matched
comparison; V measurements, both T3 alternatives and all failed sites remain in
the [complete CSV](review/r249/peaks.csv) and [plot](review/r249/directions-frequency.png).

| Site | Negative-angle family: angle / frequency | Near-tangent family | Positive-angle family |
| --- | --- | --- | --- |
| T1 Y | −43.5° / .0342 | +6.6° / .0463 | +55.0° / .0284 |
| T2 Y | −56.6° / .0306 | +2.5° / .0420 | +37.2° / .0332 |
| T3 Y | −48.1° / .0334 | +7.6° / .0416 | +52.9° / .0347 |
| T6 Y | −49.5° / .0334 | +2.3° / .0433 | +59.3° / .0401 |

Frequencies are cycles/native pixel and unaffected by rotating into the tangent
frame. Angle resolution scales are about 6–11° for these primary peaks; δf=.00531
cycles/pixel. These are Gaussian blur scales, not confidence bounds on family
identity. T2's different positive angle and T6's larger positive-family radius
are retained; no frequency scaling, affine correction or camera fitting makes
them agree. The [common-frame plot](review/r249/tangent-frame.png) shows raw
tangent-rotated vectors against all four frozen development reference trios.
T1/T2/T3/T6 each have development-compatible primary trios in both channels,
though V stability can fail. T4 V does not; T4 Y/T5 have no supported primary trio.
The six separated sites do not establish continuous tracking around the necklace.

### What the photographs and inverses add

**T1 and T2:** paired diagonal contributions and a near-transverse family cross
several visible red/yellow bodies, with similar arrangements in V and Y. For
example, [T1 V individual pairs 1/2/3](review/r249/T1-V-individual.png) show these
three distinct stripe orientations over the raw crop. The agreement is more
persuasive than a single clean FFT. Some crests also follow specular reflections;
there is no independent bead-center ground truth.

**T3:** Y's 1/2/3 branch shows a coherent arrangement across the yellow/red/black
section. However,1/3/4 is also closure-compatible and survives 3/4 checks. V has
nearby competing peaks in one direction and fails both width checks. This is
ambiguity within a promising location, not a unique lattice recovered by Y.
[Individual Y reconstructions](review/r249/T3-Y-individual.png).

**T4:** the raw row orientations change through a bend. V's supported 1/3/4
combination includes reciprocal angle~90°, giving a nearly longitudinal spatial
band, rather than the common near-transverse family. It passes the loose closure
screen but fails both matched width checks and development similarity. Y puts a
strong clipped low-frequency contribution in the shortlist and produces no
supported trio. [V individual reconstructions](review/r249/T4-V-individual.png)
illustrate why plausible stripes alone cannot validate a family interpretation.

**T5:** Y retains two diagonal row-like contributions, but its other bright pair
differs from the common near-tangent reciprocal family. The photograph contains
strong yellow/black contrast, a prominent black reflection and changing rope
orientation. This can mix appearance, outline and packing frequencies; the
experiment does not isolate their causal contributions. Neither primary channel
supports a trio. Y sigma 20 succeeds numerically as a diagnostic, but the freeze
forbids replacing the failed primary with it.
[Y individual reconstructions](review/r249/T5-Y-individual.png).

**T6:** Y shows a near-transverse spatial contribution and two diagonals;
its fourth pair is close to a harmonic of its first (.0849 versus.0433 cycles/pixel).
V instead ranks a broad, central-adjacent contribution first and recovers the
common trio only at ranks 2/3/4, with much poorer sensitivity survival. The
[paired image](review/r249/T6-comparison.png) is the clearest channel contrast:
V's combined inverse carries a large broad structure; Y's is more regularly
row-like. The [individual Y crests](review/r249/T6-Y-individual.png) still strongly
emphasize highlights, so this is not proof of bead-center geometry.

The original saved geometry ranks T4/T5 among sharper bends: its radius-scale
tangent RMS changes are 11.6°/8.4°, compared with 0.2°/0.8° at T1/T2. T3/T6 are
1.7°/4.6°. Those are earlier radius-scale descriptors, not new sigma 30 tangent
uncertainties. Curvature is a plausible contributor to failures, not a proven
sole cause; projected surface shape, central-peak overlap and appearance also
vary. No straightening, center shift or retuning was attempted.

### Limits, helicity and the next bounded task

The test establishes useful transfer of **candidate directional structure** under
one fixed method. It does not prove a primitive reciprocal cell, nearest-neighbor
directions, a complete three-family interpretation at every site, or a unique
helicity. Signed reciprocal closure is necessary evidence for a proposed trio
but can also arise from harmonics or unrelated texture. Multiple passing trios,
reflections and the loose matching tolerance remain material limitations.

There is no photographic hand score in this experiment. Known-hand mathematical
controls still verify signs/phase/reciprocal geometry, but the unresolved physical
assignments and unknown projection prevent a defensible unique-hand claim.
Both helicities remain unexcluded; their probabilities have not been estimated.

**Recommended next task:** a small spatial-validation experiment at T1/T3 and
T4/T5: compare the already selected individual peak reconstructions with visible
bead-row alignments and matched known-helicity synthetic examples, preserving
both T3 trios and failed cases. Validate which peaks represent geometric rows
before using them for helicity. These transfer locations are now inspected and
cannot be called fresh reserved evidence for any revised method. No indexing,
repeat recovery, global optimization or further experiment starts automatically.

## Reproduction and checks

```bash
.venv/bin/python -m photo2.fft_transfer evaluate
.venv/bin/python -m photo2.fft_transfer_evidence
.venv/bin/python -m unittest photo2.test_fft_transfer photo2.test_fft_spectrum_led photo2.test_fft_helicity
```

`develop` and `freeze` refuse to overwrite frozen development/procedure records.
Evaluate verifies frozen extraction-source/input hashes first. The committed
freeze is the experiment definition, not a request for another user approval.
[Full index](review/r249/INDEX.md), [peak CSV](review/r249/peaks.csv),
[qualitative assessment](review/r249/visual-assessment.json), and
[verification](review/r249/verification.json) preserve provenance, exact numerical
replay and representative figure reproduction. Fifteen tests cover source parity,
phase, mirrors, reciprocal inversion, missing/duplicated pairs, collinear
harmonics and weak/clipped abstention. No source photograph, scene, earlier
measurement or frozen extraction code changed during transfer.

Stop after scoped documentation/commit/push and exact remote/clean verification.
Recommend Astra/High for the proposed geometric validation, without asserting
the active model. No `/new` needed for reviewing these results; a fresh session
is reasonable before a separately authorized implementation, reading this report
and the current handoff first.

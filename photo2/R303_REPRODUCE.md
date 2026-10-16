# R303 reproduction and review

Launch `photo2/review/r303/launch.sh` from the repository, or open
`photo2/review/r303/index.html` offline. The launcher uses the repository `.venv`
and the existing localhost/WSL browser dispatch, normally on port8303.
`--no-browser --port 0` uses an available port without opening a browser.
The existing R301/R302 viewers and all earlier scientific results are unchanged.

The experiment is single-use and sealed. Its commands were:

```sh
.venv/bin/python -m photo2.r303.experiment freeze
.venv/bin/python -m photo2.r303.experiment run
.venv/bin/python -m photo2.r303.export
.venv/bin/python -m photo2.r303.analyze
.venv/bin/python -m unittest photo2.r303.tests
.venv/bin/python -m photo2.r303.verify
.venv/bin/python -m photo2.r303.audit_review
.venv/bin/python -m photo2.r303.extended_audit
/home/rharris/.local/bin/beads-chromium-review photo2.r303.browser_check
```

Do not repeat fitting into the delivered directory. Histories record every
proposal, native objective, physical rejection, training contradiction count,
stage and elapsed time. Replay the selected vectors with `verify`; a clock-based
rerun on a different machine need not take the same proposal path. Starting
geometry comes from delivered R302 models with historical alternatives. This is
a warm-start bounded test, not a global optimum or independent reconstruction.

The numerical deadline is580 seconds with20 seconds reserved for the last call.
Six two-sided starting sensitivities are charged to it. S1 gets38 seconds per
family/hand, fixed-geometry S2/S3 transfer gets15 seconds per region/family/hand,
and shared three-region refinement gets13 seconds per family/hand. Remaining
time is used for final S1 sensitivity, never another fit. Reports distinguish
these extremely short transfer/refinement tests from converged solutions.
Native exports, physical replay and browser verification after sealing are
evaluation only. No synthetic campaign or whole-necklace fit is performed.

All families use radius1, so face diameter D=2 and axial height H=2*axial.
`scale` is pixels per radius; `2*scale*axial` is the scaled physical height,
not generally the foreshortened visible height. Independent `pitch` is
centerline arclength per address. Coupled vectors replace slot4 with c and use
`pitch=c*H/turn`. The source family fixes c=.975. A freely calibrated c is
mathematically equivalent to a free pitch at positive H and turn; its different
search coordinates may change finite-budget results but add no information.
The same physical pitch interval .035.. .4 applies to all families. The calibrated
c interval .1..16.3 contains the entire ratio range implied by the original
height/pitch/turn bounds, so it adds no effective restriction.

The local advance derivative is `pitch*(1+spacing*tanh(k/14))`. Its amplitude
is explored within±2% as an initial sensitivity scale. This is neither measured
pointwise compliance nor string strain. There is no modeled thread path, tension,
stitch slack or measured string length. Curved axes use true circular arclength.
The constant twist uses the R302 conditional N=2000 interval; no count is inferred.

No15–30-position rejection remains. All153 local addresses, including64 guards
per side, enter contact/visibility. Verification additionally evaluates217
addresses to expose truncation effects. Neither finite certificate proves a
complete necklace is physically possible.

The217-position audit exposes truncation in six dense source hand− exports.
Their original153-position scores and selection remain preserved and explicitly
warned. `extended_audit` adds six evaluation-only views with the same parameters
and217 addresses; it does not refit or replace the original experiment. For a
fresh export/review rebuild, run the post-seal commands in the order above.
Do not rerun `extended_audit` on an already augmented manifest; rebuild with
`export` first. No extra fitting budget was used to repair this failure.

`S1-freeze.json` precedes S2/S3 fitting. Transfer retains the twelve shared
shape/pitch/camera/light parameters exactly, and adjusts only local image offset,
axis angle/curvature, helix phase and small smooth advance correction. The final
joint stage may change the shared parameters, but uses one common vector across
all three regions. There are separate families for both hands.

All30 original reflection coordinates and splits, material/paper cues and
dimension/envelope records are preserved. S1 has one uncertain B15 contour;
S2/S3 have two envelope profiles each but no individual bead-height measurement.
These evidence types are reported separately, not treated as equally informative
bead identities. Comparison reflections, held material bands and dark valleys
are evaluated only after the final seal. They are retrospective, not fresh data.

Selection prefers fewer predeclared training contradiction flags, then the common
objective. All no-flag candidates outrank flagged candidates. The loss-only winner
is also retained in each history file. Flags are engineering checks:3px individual
extent,4px contour/envelope error,10% paper occupation,23% colored omission,
missing training reflections, or failed local contact certification. Crossing
these thresholds is not proof of photographic truth, and a reflection gain does
not excuse geometric regression. See the report for component-wise comparisons.

`evidence/protocol.json` records source hashes, bounds, scales and allocation;
`results/fit-freeze.json` seals selection. `native-manifest.json.gz`,
`comparison.csv`, and the viewer retain all stages and historical comparisons.
`verification.json`, `browser-check.json` and `delivery.json` record verification
and delivery. Stop for maker review; no adoption, further section, whole-loop
optimization, pattern recovery or Phase3 is authorized by this delivery.

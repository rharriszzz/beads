# R276 — integrated 3D reconstruction and one shared distant light

**Working full-photo reconstruction and quantitative fitting are implemented. A physically certified reconstruction is not established.** All R259–R275 observations, masks and prior model artifacts remain unchanged.

[Numerical comparison and reproduction](review/r276/README.md) · [individual residuals](review/r276/individual-residuals.csv) · [shared-light POV-Ray appearance](review/r276/mixed_joint-pov.png) · [contact-constrained alternative](review/r276/contact_joint-pov.png) · [source photograph](../beads-photo-2.jpg)

The literal rounded, hole-bearing source bead is ray-traced with all necklace beads available as occluders and directional-light blockers. Unknown model colors stay gray; colored renders show conditional ownership, not a recovered string sequence.

| Experiment | Yellow train RMS | Yellow held-out RMS | Red held-out RMS | Black held-out RMS | Yellow held-out maximum |
|---|---:|---:|---:|---:|---:|
| initial | 12.38 | 13.44 | 11.02 | 10.44 | 30.00 |
| light_only | 10.18 | 11.69 | 9.50 | 9.51 | 17.71 |
| interior_geometry | 9.61 | 11.33 | 9.80 | 10.10 | 18.26 |
| joint | 9.09 | 10.77 | 9.54 | 10.92 | 20.58 |
| joint_refined | 8.76 | 10.55 | 9.88 | 11.29 | 18.97 |
| uniform_before | 9.53 | 10.34 | 9.93 | 12.28 | 19.40 |
| uniform_refined | 8.79 | 10.62 | 10.24 | 12.49 | 17.44 |
| mixed_light | 8.61 | 9.92 | 10.32 | 11.62 | 15.84 |
| mixed_joint | 8.70 | 9.86 | 10.55 | 11.10 | 16.35 |
| metric_before | 8.95 | 10.42 | 9.59 | 12.12 | 18.71 |
| metric_refined | 9.26 | 9.85 | 10.14 | 11.24 | 17.19 |
| contact_light | 11.42 | 12.18 | 10.70 | 11.24 | 19.86 |
| contact_joint | 11.62 | 11.25 | 10.63 | 11.49 | 18.27 |

All values are native pixels. Fixed photographic denominators: 175 training/37 held-out yellow specular candidates, 54/20 red, 160/39 black. Missing predictions remain as explicit 30px reporting sentinels, separately counted; every valid residual is untrimmed in the ledger. These are candidate brightness peaks, not verified mirror highlights. Later correction holdouts are exploratory because earlier outcomes had already been inspected.

Four methods were considered before implementation: frozen geometry/shared light; positive-interior geometry; joint geometry/light; and a normalized tangent/radial-frame empirical control. The first shared-light fit improves held-out yellow and black agreement. Subsequent pure-specular joint fitting improves yellow but worsens black, so it is not accepted as a universal improvement. At frozen light_only geometry, the empirical control loses to the directional model on paired held-out subsets.

Yellow peaks remain strongly colored. A neutral-only gate produced no reliable yellow calibration cases; that failed control is saved. The final photographic gate also accepts strong yellow peaks substantially desaturated relative to their own interiors. A shared diffuse/specular mixture is tested separately, preserving the pure-specular prediction. No red/yellow/black-specific light directions, finite-distance source or extra lamp is introduced.

The contact-constrained N1950/h−1 follow-up improves its held-out yellow brightness RMS from 11.95 to 11.25 px. It has zero sampled penetrations after 16,384 surface samples per bead, including flat faces; a bounding-sphere scan finds only the checked ±1/6/7 pair families. Minimum sampled clearance is 0.00457 source units. This is a plausible contact-consistent alternative, not a certified count: total native interior ownership is 65.7%, versus 74.3% for the inherited geometry, and black held-out RMS is 11.49 px. The extra 91-evaluation follow-up was selected by contact feasibility; do not use its extra budget as a fair count-ranking advantage.

The most important new failure is physical packing: the inherited literal source placement intersects its neighbors extensively. Small phase/strain adjustments do not remove this. Larger rope-radius, lower-count and absolute metric-calibration controls are retained, with their photographic costs; they are sensitivity hypotheses, not newly confirmed construction facts. The 15% projected-size metric control reduces the high-count contact violations to 235 sampled ±6 pairs, but held-out yellow interior ownership falls to 57.2%. It is not adopted. The source bead dimensions and shape are unchanged in the metric control; the centerline and camera unit calibration change together before a fixed-length fit.

Bending uses periodic normal displacement; longitudinal redistribution integrates a smooth strain field against physical arclength with zero net integral; twist changes a separate periodic phase field. Each hypothesis fixes its centerline length and integer winding. The inherited R258 material chart has about −11.3%/+10.4% local speed variation. The uniform-material correction explicitly removes this inherited variation before allowing small new strain. No individual bead translations are fitted.

R275 interiors constrain positive surface ownership only. Their boundaries are **not** complete visible silhouettes; symmetric outline error and silhouette IoU remain unavailable. Native ownership is checked at every one of the 807 exact masks; the three location-only observations have no invented area or mask error. Possible detection corrections are not applied. Large mismatches remain diagnosis candidates, not permission to move photographic measurements.

Count, helicity and camera alternatives have matched phase-start/search budgets. Their local objectives do not establish a unique bead count or physical correspondence. The broad inherited registration is a warm start, not an independent recovery of every centerline span. Geographic holdouts are withheld from R276 optimization, not from all historical fitting that produced the initialization. Relative gains, roughness, diffuse mixture and illumination direction remain conditional, without radiometric camera calibration.

The mixed fit’s shared direction is (−0.25218,+0.41879,+0.87236), versus (−0.06330,+0.18177,+0.98130) for the contact alternative, in the saved source world frame. This geometry dependence prevents identifying a unique lamp direction. Fixing the initial correspondences gives 11.78 px held-out yellow RMS for joint_refined, compared with 10.55 px when rematched: some improvement is correspondence-dependent.

Validation: 38 scientific tests pass; 810 locations, 807 masks and 4,166 preexisting files are unchanged. A saved mixed-model numerical/array/render replay is exact. One historical R258 immutable-review test expects an older ignored user-review hash; that review is preserved and the stale check is reported separately. Camera grazing rays remain conservatively unknown (180 of 220,131 native positive pixels in mixed_joint), with their coordinates saved; directional-shadow nonconvergence is counted and treated blocked. Native 1px sampling checks bound grid error separately from photographic error.

See the evidence index for light sensitivity, native-grid convergence, fixed-correspondence controls, material-normalized brightness/shape errors, closure/contact diagnostics, worst native crops and all saved alternatives. The stopping point is a reproducible integrated experiment with explicit failures. Next: resolve absolute bead-to-rope scale and noninterpenetrating placement against the photograph before extending deformation freedom or recovering string indices. Keep the current model/reasoning; no `/new` is required for reviewing this evidence.

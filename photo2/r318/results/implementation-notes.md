# Implementation chronology and retained limitations

- Initial photo detector failed JSON serialization on a NumPy boolean before
  writing observations. Converted the flag and window coordinates to builtin
  scalar types, then reran the unchanged photo-only selection. No fitted cohort
  or scientific result existed before that correction.
- First epoch used a shared directional light and the original coupled fields.
  The source snapshot `initial-source.tar.gz` preserves that implementation.
- The second map uses automatic full-bead luminance-basin overlap, with a separate
  unchanged-geometry correspondence control. It never selects assignments by
  predicted optical distance. All 22 observations remain in both epochs.
- Followups add roll, global station, shared radius, local radial orientation
  and finite source distance to the same exact reflection objective. The initial
  fitted outputs are preserved as `initial-*`. No unrelated radial-tilt campaign
  or crochet-mechanics model was run.
- Shared finite-source and extended-source controls are separately serialized.
  Their geometry stays fixed. Any correspondence-only difference is labeled and
  excluded from geometric-gain claims.
- Added strict stored-epoch hash and one-to-one validation after the first fit;
  this changes only corruption rejection, not valid predictions or metrics.
- Detector library deprecation warnings are retained in the log. They do not
  change the frozen masks, measurements or arithmetic.
- The original distant-source/half-vector BRDF is a positional optical model,
  not a radiometrically calibrated glass-refraction model. Numerical verification
  is not physical identification. Half-pixel principal-lobe switching remains
  visible rather than being repaired by selective localization changes.

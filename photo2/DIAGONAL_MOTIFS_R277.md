# R277 — Automatic photo-derived motif probe (not yet a recovered pattern)

This is a **new, independent analysis of R275's real-photo detections**, added after R276. It does **not** assume the R276 physical model is correct.

## The user's essential correction

The exact original bead-string repeat is **considerably longer than the obvious small similarities**. The handmade pattern also contains **almost-repeated and reflected subsequences**.

Therefore a strong autocorrelation or short similar color sequence **must never be promoted to the exact pattern length**. A reversed local motif is not necessarily a reversal in the original string: photographed centerline ordering is not crochet string ordering.

## Problem 1 — Can we extract useful discrete color evidence without solving illumination?

**Yes.** R275 saves 433 heuristic along-centerline groups containing 658 individual accepted colored observations (218 red, 194 yellow, 246 black). Each observed color is assigned to one of the two sides of the image-traced centerline. Unknown opposite-side colors remain unknown; none are filled with a model.

Source: [R275 station groups](review/r275/stations.json), [image-derived positions and colors](review/r275/angular-locations.json). Each station may contain one or two observations. **These groups are not crochet stitch rows**, a central technical distinction.

## Problem 2 — Are there direct and reflected local similarities?

**Yes, demonstrably, but without assigning physical string indices.** A reproducible independent search compares 18, 24 and 30 consecutive groups in four modes: forward vs reversed station order, with/without exchange of visible sides.

Some of the strongest overlapping-18-group witnesses:

| First group | Second group | Relationship | Same/compared colors |
| ---: | ---: | --- | ---: |
| 1 | 399 | forward, same side | 23/24 |
| 88 | 155 | forward, same side | 21/21 |
| 350 | 384 | reversed, sides exchanged | 21/21 |
| 130 | 163 | forward, same side | 22/23 |
| 163 | 198 | forward, sides exchanged | 25/28 |

A 30-group search finds a forward match starting at groups **277 and 309**, agreeing on **31 of 32 jointly observed side colors**. These high match rates remain *local motifs*, not global repetitions. Omitted observations, nearby similar runs, and uncertain group boundaries prevent interpreting an apparently exact local match as a confirmed repeated physical substring.

On the 18-group scan the strongest standardized exploratory score is 6.448. In **40 eight-group block shuffles**, preserving local color runs and paired-side missingness, none exceeded it (finite-sample maximum-search estimate `p≤1/41≈0.0244`). This is a provisional sanity check **not** a formal physical repeat test; the null does not reconstruct crochet connections.

[Reproducible Node analysis](diagonal_motif_probe_r277.mjs), from the repository root:

```sh
node photo2/diagonal_motif_probe_r277.mjs > /tmp/r277-motif-scan.json
# optional stronger null, at additional CPU expense:
node photo2/diagonal_motif_probe_r277.mjs --permutations 100 > /tmp/r277-motif-scan-100.json
```

The code includes a synthetic self-check that identifies a reversed, sides-exchanged sequence correctly.

## Problem 3 — Does a shorter color-similarity interval recover the true repeating bead string?

**No.** In an exploratory same-side color correlation of the R275 positions, a broad local signal appeared around 350–370 image pixels and near twice that span. It is evidence of repeating motifs, **not a physical bead count or exact repeat length**. The apparent interval changes when several harmonics are weighted. The user's almost-repeats and reflections provide a concrete reason for such false short periods.

**Do not convert centerline pixels or station counts into bead-string indices using a nominal 6.5 multiplier.** Beads around a crocheted rope have ±1/±6/±7 physical-index neighbor families; projected ordering mixes these diagonals and visibility. A translation along the photograph is generally not the same physical-string shift as a repeat.

## Problem 4 — Can we certify the complete repeated color pattern yet?

**Not yet.** The missing operation is automatic **crochet-diagonal connectivity / physical stitch-index reconstruction**, including hidden beads and local ambiguity. A direct/reversed match of the photographic *station sequence* is insufficient for assigning the original string. Need to reconstruct a candidate integer-index graph from two-dimensional native bead locations and crochet topology, then test global repeat candidates against observed colors, including almost-repeats, reflections, unknown beads, whole-repeat closure and held-out photographic evidence. Avoid using guessed R276 3D owner identities as truth.

R276 also found that the inherited high-count model physically intersects neighboring beads, so its string-index assignments cannot be treated as certified. The contact-consistent N=1950 alternative fits observed positive interiors less well. Neither resolves the original string ordering.

## Status

**Solved:** recover and compare direct and reflected local photo-color motifs automatically, without changing any prior observations or assuming a short exact period.

**Not solved:** global physical string order and shortest exact repeating color pattern. No count, physical repeat length, reflection in string space, or hidden-bead color is claimed.

All prior R259–R276 models, masks and reports remain untouched. This module reads the preserved R275 observation files and does not depend on R276 lighting predictions.

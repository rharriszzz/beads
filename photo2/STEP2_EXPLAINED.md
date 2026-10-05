# How step 2 chooses its seeds — R230

The maker reports that roughly half the displayed seeds lie between beads and
half lie inside them. This rejects the displayed seed set as a trusted interior
basis. It is a visual estimate, not a measured error rate across the whole photo;
no particular seed numbers or pixel ownerships were supplied. The old assertion
that steps 1 and 2 looked good is superseded by this more direct seed review.

The purpose of step 2 is to find a reliable starting pixel inside each colored
bead. Its actual rules find prominent maxima inside a broad color-compatible
area. The missing foundation is an independent check that this area represents
the inside of a bead at the selected point.

Read the [actual implementation](refine_colored_masks.py#L24) alongside the
[unchanged raw/seed close-ups](review/r229/closeups.png). The latter can still be
opened at http://127.0.0.1:4001/step2.html with the existing server.

## 1. Construct an allowed area for each learned color

The previous extractor supplies a broad search band, a color-family assignment,
and a permissive colored-pixel mask. It uses hue, saturation, departure from the
learned paper appearance, and a weak brightness floor. Step 2 tightens this to
pixels within 18 degrees of a learned hue: 27 or 353 degrees in this photo.
Hue distance wraps around zero. Previously attached neutral reflection pixels
are also allowed, even if their own hue is unreliable.

This is an allowed search area, not a collection of verified bead interiors.
It can contain several neighboring beads, and can retain intervening pixels
when their measured color passes the same tests. A gap need not create a hole
in the mask. The resulting distance is therefore not distance from a bead edge.

## 2. Reduce highlights, then smooth brightness

V is the largest of the original RGB channels, divided by 255. It is an HSV
brightness measure, not a calibrated illumination measurement. At pixels marked
as reflections by the earlier detector, V is replaced with a local 5-by-5 median.
Other pixels retain their original V. The result is then blurred with a Gaussian
whose standard deviation is about 1.90 native pixels.

The aim is to favor the body rather than a small glint. However, smoothing uses
neighboring pixels on both sides of the allowed area's boundary. Bright paper
or a neighboring bead can influence the smoothed value. Reflection suppression
also depends on the earlier detector; it does not guarantee every glint is removed.

## 3. Give each allowed pixel a score

Let d be distance, in pixels, to the nearest pixel outside that color's allowed
area. Let D be the apparent bead diameter estimated from the image: 27.19 pixels.
The code uses:

```text
quality = smoothed V × min(d / (0.10 × D), 1)
```

For this photo, the denominator is 2.72 pixels. The distance term discourages
pixels at the edge of the allowed color area, but stops increasing beyond that
small distance. It does not continue rewarding the middle of a bead-sized area.

| Distance inside the allowed area | Brightness multiplier | Passes the later seed-inset test? |
|---|---:|---|
| 1 pixel | 0.37 | No |
| 2 pixels | 0.74 | Yes |
| 3 pixels | 1.00 | Yes |
| 10 pixels | 1.00 | Yes |

These are numerical examples of the formula, not assigned bead boundaries. If
an allowed bridge spans a gap, a point within that bridge can get the full score.

## 4. Find sufficiently prominent hills in that score

The code calls `h_maxima` on quality. The required prominence is 8% of the
90th-percentile smoothed V within the color's allowed area. This compares a
peak's height with the valleys separating it from other peaks. It is not a
requirement that a bead-shaped neighborhood be bright, nor a comparison between
the inside and outside of an established bead.

For each connected maximum, the code chooses one highest-scoring pixel. Equal
scores use the first pixel in array order; it does not compute a plateau center.
It then rejects that point only if d is below 1.63 pixels in this photo. Thus a
small, moderately bright feature in an allowed gap can meet these rules. There
is no additional raw-brightness or saturation test on a whole seed neighborhood.

## 5. Suppress nearby peaks, then add old fallback seeds

New points are processed from highest score to lowest. A point is discarded
if another retained point of the same color lies less than 9.52 pixels away.
Different color families are handled separately. This spacing discourages very
close duplicates; it does not guarantee one point per physical bead. Two bright
features more than 9.52 pixels apart can both survive within one visible bead.

An older automatic seed is added wherever no same-color point lies within
17.67 pixels. Those old seeds came from the previous color-distance/region
procedure and do not have to pass the new prominent-brightness test. There are
1,515 new cyan seeds and 51 orange fallback seeds in the displayed output.

## What the failure means

The rules combine color compatibility, smoothed brightness, a small support-edge
inset, and peak spacing. They do not establish a substantial patch definitely
inside one bead. In particular, “inside the allowed color area” was given more
weight than the evidence justified. A misplaced seed then becomes a starting
anchor for region growth, so this defect can contribute to the later intrusive
regions. It does not prove that every later defect has the same cause.

The broad mask, smoothing, capped distance term and fallback branch are possible
contributors. The maker's assessment establishes the seed failure; it does not
yet identify which computation misplaced a particular seed. No repair is chosen
or implemented during this explanation. The exact answer and frozen artifact
bindings are in [the assessment record](step2-seed-answer-r230.json), with
[parameters and source seals](review/r230/summary.json).

Stop at explaining step 2. Next inspect the allowed area, raw brightness,
smoothed brightness and score around one misplaced seed before choosing a
correction. Recommend gpt-6.1-sol / High; same conversation, no `/new` needed.

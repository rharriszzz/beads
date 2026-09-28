# Reusing the maker's Gaussian FFT experiments — R110

The maker reports that Gaussian-window 2D FFT worked well both for background,
including shadows, and for bead directions. Preserve this as **prior practical
experience**, not just an untried suggestion. This review inspected code; it did
not rerun the photograph or measure a new classification/direction accuracy.

Read-only source: `fft-image-explorer` main at
`2caf0707c2b63a0d7540e2cac447d2f1b883d8c1`. Its local `radial-sum` branch has the
same `map_from_fft.py` and `fft_image_explorer.py` contents. No branch switch,
sibling edits or GUI launch. Older README/notes mention
`scan_highpass_removed_map.py`; the inspected current scanner is `map_from_fft.py`.

## Background: clarify which power is measured

R110 says **low-pass power**; R097 described removing the central peak and
inspecting remaining power. These are different raw quantities but can be
complementary fractions when calculated on the same spectrum with complementary
hard masks. Do not silently replace either statement with a new filter.

Let `F = FFT(image_patch * spatial_Gaussian)`, `P = sum(abs(F)**2)`, and `L` be
the central disk. Define `P_low = sum_L(abs(F)**2)` and `P_high = P - P_low`.
For nonzero P and complementary masks:

- Low-pass retained fraction: `P_low / P`.
- High-pass retained fraction: `P_high / P = 1 - P_low / P`.
- Scanner **hp_removed**: `100 * (P - P_high) / P`, hence `100 * P_low / P`.
- Explorer **low-pass removed**: `100 * (P - P_low) / P`, hence the high-frequency
  fraction when the disk cutoff is the same.

The scanner name can therefore be misleading: its background metric really is
low-frequency retained **fraction**, expressed as a percentage. R110 does not
specify whether every earlier interactive trial used a fraction or absolute
power; do not infer those settings from this saved scanner alone. The explorer's
remaining-power percentage uses all enabled filters, including optional thresholding.

[Scanner source](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/map_from_fft.py)
uses the Gaussian-windowed luminance directly, with no weighted-plane subtraction.
Its hard disk radius is `highpass_percent / 100 * hypot(height/2, width/2)` in FFT
bins. For its square window, frequency in cycles/pixel is radius divided by window
size. Its Gaussian sigma in source pixels is `softness * size/2`, with softness0.2
in the scanner; window side length is not sigma. Edge padding is used at image
borders. Do not copy these cutoffs between different FFT grids without conversion.

[Saved metadata](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/beads-photo-2_map_metadata.json)
records metric hp_removed, window128, cutoff8%, stride8 and a3182×2540 map.
This corresponds to sigma12.8 pixels and cutoff about0.05657 cycles/pixel for the
inspected scanner. The near100/alpha0.25 setting is a display transform, not a
new spectral measurement. These are **one saved run's parameters**, not universal
settings or a new recommended Gaussian width. The file alone does not establish
which code revision originally produced the map; no map provenance/accuracy audit
was performed here.

Uniform multiplicative intensity scaling cancels in this power fraction for an
ideal nonzero patch. That helps explain why it can be useful in a uniformly darker
paper region. A spatially varying or sharp shadow changes spectral shape, and
noise/clipping break that simple invariance. Small total power needs an explicit
weak-signal condition; the scanner returns0 when P is at most1e-12, which is a
numerical convention, not evidence that a black patch is a bead.

**Priority:** reproduce this raw-window low-pass-fraction baseline before adding
plane detrending or replacing it with spatial texture. Compare against the current
beads probes on identical patches, storing numerator, denominator, mask, Gaussian
parameters and absolute power separately. The R099/R104 detrended high-band RMS
is a different statistic. Its successes/failures cannot by themselves validate
or reject this source baseline. Keep both empirical records.

## Directions: three opposite peak pairs in the bead-scale band

The maker's procedure is: Gaussian window at a centerline point; suppress low
and high frequencies outside anticipated bead spacings; look for **three pairs
of opposite noncentral peaks**; interpret those pairs as directions **1,6,7**.
Use direction1 relative to the local centerline tangent for the helicity cue.
This is the stated working association, to reproduce with the source explorer.

[Explorer source](https://github.com/rharriszzz/fft-image-explorer/blob/2caf0707c2b63a0d7540e2cac447d2f1b883d8c1/fft_image_explorer.py)
implements both radial filters. `find_top_fft_peaks` merges opposite offsets into
one entry, computes angles with y upward, and includes the origin in the selected
list. Default top_k7 therefore does **not** mean three pairs or seven independent
directions. Inspect three nonzero pair representatives for this task; do not count
the center, accept six unrelated maxima, or force the strongest three candidates
to be physical families when the evidence is poor.

The peak popup already reconstructs selected conjugate pairs using the original
complex coefficients and adjustable strengths. Reuse this display to connect each
pair to the image structure. Peak `log_power_sum` summarizes log-magnitude support;
it is not the physical sum(abs(F)**2) used for the background metric.

For real-valued input, conjugate pairs are expected; their existence alone does
not label the lattice families. Use the anticipated band, persistence under nearby
window changes, image reconstruction and known-helicity calibration to distinguish
bead families from harmonics/color-pattern peaks. Keep the maker's successful
three-pair interpretation as the target, without declaring any arbitrary three
pairs sufficient proof. Spectral-to-spatial direction and handedness conventions
remain as described in [the bead methods](../METHODS.md#b2--gaussian-fft-along-the-centerline).

## Reproduce the source inspection

```bash
git -C ../fft-image-explorer show 2caf070:map_from_fft.py
git -C ../fft-image-explorer show 2caf070:fft_image_explorer.py
git -C ../fft-image-explorer show 2caf070:beads-photo-2_map_metadata.json
git -C ../fft-image-explorer diff main radial-sum -- map_from_fft.py fft_image_explorer.py
```

SHA-256 of the pinned source blobs, verified against the clean working files:

| File | SHA-256 |
| --- | --- |
| `map_from_fft.py` | `7295aa5dac6810cfe4bb6137d02837bbae39689454473a720374ca77428858b4` |
| `fft_image_explorer.py` | `73ced947b1825e55ca0d1337fc508bbd4917e574cbea150ae660b61ee8013c24` |
| `beads-photo-2_map_metadata.json` | `a5e1d5fd6081dd517ad96a4abf411385e88bddf93ab2c70e4ee8af65741ccc54` |

# Checkpoint 3 — black reflection comparison

R1: sigma0.65 linear-Y field, 16% local peak contrast isophote; independent native
16% threshold support. R2: local Otsu threshold bounded below by R1 level;
independent native threshold support. R3: image-gradient snake initialized from
R1, alpha0.025/beta0.25/180 iterations, maximum2.5px departure guard, native
positive-contrast floor8%. No method grows into a dark body. Parameters are in
methods.py; sigma0.50/0.80 and contrast±0.02 perturbations retained per feature.

Upper reflection R283/A/R1/R2/R3 areas:78/67/41/32/17px. Relative to A, R1/R2/R3
centroid shifts0.53/0.74/1.08px; mean boundary gradients0.0823/0.0891/0.0687
versus A0.0468. R1 keeps the elongated intensity footprint with a smoother curve.
R2 is smoother but contracts toward the bright core. R3 contracts substantially
and its curve is less stable/faithful; preserve as a failed independent approach.
Smoothness alone is not the decision criterion. Native threshold masks and
subpixel curves differ and are explicitly saved separately.

Lower reflection remains a separate photographic feature for every method;
nearby reflections have unresolved physical ownership. Review says it is a
secondary, not another established bead. Next inspect the lower-feature curves,
automatically selected strong/weak examples, perturbations and neighbor overlap.
No reflection centroid is a physical bead center; black-body crossing stays null.

# Checkpoint 2 — tail comparison and informative failures

Pass 1: A baseline; T opens with disk round(0.70 × maximum thickness), without
regrowing a rim; E connected brightness flood (allowed renewed rise 7% peak);
W prominence watershed (9% peak); L 28-step gradient geodesic level set;
I local-background plus 18% contrast isophote. All masks remain native.

For reviewed yellow1/red2/yellow3, T removes 45/46/19 of 516/537/490 pixels,
shifting centroids 0.74/0.52/0.12px. It removes the two protrusions visually while
keeping all three observations and the red crossing. This is support correction,
not line smoothing. It can round away real material elsewhere: validation needed.
I removes the yellow lobe but retains only 200/537 red pixels (3.64px shift),
showing that a highlight-oriented intensity threshold is unsuitable as a universal
colored-interior rule. E/W/L expand the reviewed tails instead of resolving them.

Pass 1's two-pixel expansion of A constrains every brightness alternative to
inherit the original flat/clipped support in picture3. Save this entire pass
under results/pass01 before removing that restriction. Next use the shared
photographic material domain, retaining search-boundary contacts as uncertainty.
No method selected or adopted. The weak-case selector initially used the wrong
stored peak field (fallback tied by ID); its two dependent selections survive in
results/selection-control. Correct selector uses R283 illumination.peak.

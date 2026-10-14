# Checkpoint 4 — brightness-aware methods and domain ablation

Independent methods E (path-minimum brightness barrier), W (prominence watershed),
L (gradient geodesic level set), I (local-background isophote) are compared against
A/T. Pass1 restricted the domain to A dilated2px; archived all ten numerical
comparisons and exact method/runner source in results/pass01. Pass2 uses the
photographic pigment/neutral-highlight domain directly, preserving its18px
search limit. Results: picture3 E414/W545/L416/I350 versus A355 pixels. W creates
an upper-left branch into a neighbor; L retains a notch. I avoids that branch,
but its bottom reaches the search limit while the native brightness profile is
still substantial. Thus material/region bounds, not just smoothness, matter.

Add J, explicitly an I domain ablation (24px instead of18px), NOT an additional
independent method. This tests inherited clipping without altering the four
mathematical comparisons. No reviewed coordinate or desired mask enters J.
Over870-pixel proposals are retained as inadmissible diagnostic failures, never
accepted. All candidates remain experimental/unresolved with no calibrated
probabilities or physical assignments. Next inspect J and automatically selected
cases, report color-specific limitations and preserve overlaps/false partitions.

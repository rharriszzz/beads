# Checkpoint 1 — native diagnosis, before replacement algorithms

Executed `.venv/bin/python -m photo2.r284b.diagnose`; parameters and all seven
profiles/thickness maps are in results/diagnosis.json and *-diagnosis.png.
Original A yellow1/red2/right-yellow areas are 516/537/490 native pixels.
Pre-A maximum thickness radii are 10/10.05/10; opening is capped at four pixels.
Only 15/10/13 pixels are restored after opening; the corresponding centroid
changes are 0.158/0.122/0.023 pixels. Thus reconstruction is a contributor but
cannot explain the broad surviving lobes. A purely cosmetic contour fix would
leave the measurement error intact. Lower-left profiles show dark valleys and
renewed brighter material, which opening never examines. Lower-left quadrants
are diagnostic summaries only, never automatic cutting regions.

The upper reflection A mask contains 67 pixels, with 10th-percentile linear Y
0.0020 versus a peak about 0.324. Historical collars are therefore mixed into
what should now be a reflection measurement. The lower feature is weaker but
must remain a photographic feature; neither proximity nor intensity ratio
establishes physical ownership. Bad-magenta A retains 355/402 pre-A pixels;
after opening, material connectivity still does not establish ownership.

Next experiments: uncapped adaptive opening (potential truncation control),
brightness-barrier connected growth, competing watershed, gradient level set,
and local isophote. Reflection experiments separately compare smoothed-field
subpixel isophotes, adaptive intensity thresholds, and gradient-driven snakes.
All use photographic cues and pixels; reviewed coordinates select evaluation
figures only. Preserve every failed alternative and quantify actual native changes.

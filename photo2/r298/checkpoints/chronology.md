# R298 chronology and failures

1. Read current instructions, R294–R297 implementation/reports, R183–R184 width
   feedback, R243/R249 FFT conventions and source model. Protected prior files frozen.
2. Selected sixteen crop locations from old Phase1 regions, before model scoring.
   Analyst digitized exposed contours. Photo() returns two pixel arrays plus metadata;
   the first measurement attempt incorrectly treated its second result as a path.
   Source `measure-v1.py` preserves that technical failure.
3. Global paper/luminance and global-hue-only profiles visibly followed cast shadow.
   Both numerical datasets and inspection images remain. Local-side hue/saturation
   comparisons, threshold uncertainty and a separate pre-fit visual exclusion screen
   were frozen. Measurements are analyst/photo evidence, not calibrated truth.
4. Paired R297 controls; fixed-camera thinner fit feasible, free-elevation thicker
   fit near overhead collides. Axis-only improves common-mode error but not width.
   Four unconstrained joint fits all collide. No selected model uses these failures.
5. Physical penalty fits with no camera rotation; one final hand+ open still
   collides. All physical states retained. Exact gating is separate from penalties.
   `geometry-no-roll.py` and `calibrate-no-roll.py` preserve that stage's code.
6. Diagnose world yaw gauge versus actual image-plane camera rotation. New camera
   rotation makes the independent shape control feasible and lowers width residual.
   Four bounded physical joint fits from that control certify. All fit histories
   retain finite-difference probes, even when their geometries are infeasible.
7. Freeze32 raw separator profiles from old region-pair evidence. Final81 trials
   use dimensional loss plus material/separator contradictions; 78 certify and3
   demonstrate penetration. `selection.json` freezes four families, primary49.
8. Full native export and old-support comparisons show substantial regressions.
   No subsequent fitting. All four families and R297 remain available in the review.
9. Figures' first JSON receipt failed on NumPy int64 crop bounds; display/export
   serialization repaired, source retained. Native/model data were unaffected.
10. First browser launch could not bind localhost in the sandbox. Rerun through the
    approved Chromium wrapper outside the sandbox passes. Windows GUI opening is
    mocked, while the actual WSL shell launcher and HTTP server are exercised.

No old experiment, feedback file, Phase1 observation, photograph, production launcher
or beads.pov changed. No external site is published; this is a local scientific
review under the Sites skill's local-only workflow. No agent delegation.

11. Staged whitespace check flagged default CSV CRLF line endings. Exporter now uses
    LF; every CSV parsed value is verified identical to full model exports. No fit
    or native visibility change. csv-verification.json records all rows and hashes.

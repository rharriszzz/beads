# R346 — whole-necklace cast shadow on the paper

[Final POV-Ray image](r346/output/render.png) · [Original / R345 / R346 comparison](r346/output/comparison.jpg) · [Paper-only shadow fields](r346/output/shadow-fields.png) · [Whole-loop profile comparisons](r346/output/shadow-profiles.png) · [Crop locations](r346/output/crop-locations.jpg) · [Reproduce](R346_REPRODUCE.md)

![Whole photograph and both lighting models](r346/output/comparison.jpg)

**One shared lighting arrangement now produces a longer, softer, warmer whole-necklace shadow.** The final 2540×3182 image is an actual POV-Ray render. R345's camera, all 2,704 bead transforms, geometry, provisional 208-color pattern, helicity, glass materials and paper remain unchanged. There are no individual-bead shadow targets, section-specific lights, local bead corrections, camera adjustments or photographic textures on the paper.

The native-image paper-profile RMS loss error changes from **20.4% to 6.8%**; every-fourth-station comparison error changes from **20.0% to 6.4%**. These are percentage-point errors in normalized linear-light paper brightness, not physical accuracy percentages. Actual image-coordinate paper samples also improve, rather than only silhouettes being re-aligned for plotting.

## Full-loop evidence and silhouette exclusion

The photograph has a dark near-necklace component and a much broader extended shadow. Its apparent reach changes with local outline direction: most extension is on right-facing outlines, while top, bottom, straight and curved segments have different normal components. The source shadow often remains detectable 100–200 native pixels beyond a silhouette estimate. Some tails reach the image border before their endpoint can be observed. R345's source gives a comparatively short, sharp-edged shadow and misses much of this paper darkening.

The analysis samples **96 evenly spaced image-arclength stations on both sides: 192 contours**. It uses grayscale steep-edge energy to estimate material boundaries and rejects threshold-sensitive or poorly supported edges. **142 contours** supply the quantitative profile denominator; all 192, including failures, remain in [observations](r346/output/observations.json), [frozen profiles](r346/output/profiles.json.gz), the [boundary atlas](r346/output/boundary-atlas.jpg), and the 576-row [measurement CSV](r346/output/shadow-measurements.csv). Bead pigments, motif labels and individual bead brightness are never observation-selection criteria.

Photographic samples start at least 12 pixels beyond the nominal silhouette, beyond the last substantial grayscale material edge across 13 tangential lanes plus 8 pixels, and beyond threshold uncertainty plus 8 pixels. This deliberately excludes ambiguous glass rims and most hidden contact regions. Exact POV-Ray all-necklace silhouette masks independently exclude modeled material. The image-coordinate comparison uses only pixels outside **both** the photographic exclusion band and the model's projected silhouette, with a 4 pixel model guard. Dark portions of the necklace are not counted as cast shadow.

The cyan atlas edges are estimated material boundaries, not shadow toes. Orange edges are excluded. White segments indicate outward sampling normals, not light directions or measured shadow boundaries. A sparse automatic contour cannot certify every photographic glass margin; the guard bands, full atlas, failed edges and sensitivity checks make that uncertainty inspectable. Neither hue nor bead class defines an edge. The body-colored reconstruction is used only for visual comparison; shadow metrology uses paper pixels.

## Paper illumination reference and measurement reliability

Extended shadow can look like gradual illumination change. A narrow local 115–150 pixel reference band proved contaminated by shadow and was rejected; its data and controls remain explicitly labeled under [development](r346/development/README.md). It is not an accepted measurement epoch.

The final background reference is a robust quadratic surface in log-RGB, fitted to **23,312 fixed-grid paper points farther than 260 pixels from the entire traced necklace**. Every fifth control-grid point checks the fit. [Reference controls](r346/output/background-controls.jpg) and [coefficients/residuals](r346/output/background.json) show the data. Held-out single-pixel log-RGB RMS residuals are approximately 5.0%, 9.1%, 6.0%; these include paper grain, spatial reference error and any residual contamination. Tangential medians reduce grain, but this is not a calibrated radiometric reference.

Shadow darkness is `1 − linear_RGB / estimated_unshadowed_RGB`, combined with linear-luminance weights. The primary profiles retain R345's encoded-RGB/sRGB-transfer approximation. An [embedded-ICC sensitivity check](r346/output/color-profile-sensitivity.json) converts the source's Apple Wide Color Sharing profile to sRGB and refits the same paper-reference basis without changing lighting or eligibility; held-station R346 RMS changes by 0.31 percentage points and still improves over R345. These remain relative photographic measurements, not calibrated radiometry. The 10% absolute paper-loss toe is the primary displacement measure; a 5% toe is provided as a more background-sensitive diagnostic. Penumbra width is a sustained 90–10% falloff of the **observed whole-necklace shadow peak** outside the guard, not a bead-specific optical PSF. The darker contact component under the necklace is mostly hidden and is not assigned invented measurements. The 12–20 pixel band measures the nearest safely sampled paper, not under-body contact darkness.

The following medians use the same **42 strong photographic profiles**: peak loss at least 30%, an observed 10% endpoint, and an observed 90–10% falloff. Missing modeled penumbras remain missing and their denominator is shown. Distances are original-photo pixels.

| Quantity | Photograph | R345 | R346 |
|---|---:|---:|---:|
|Shadow reach to10% paper loss|125.5; n=42|27.4; n=42|123.2; n=42|
|Faint toe to5% paper loss|158.2; n=40|28.4; n=42|142.8; n=35|
|90–10% outer falloff|117.3; n=42|7.5; n=24|120.9; n=41|
|Paper loss12–20px outside edge|78.0%; n=42|75.1%; n=42|75.1%; n=42|

There are 0 eligible photographic profiles whose 10% endpoint is clipped/censored; their lower bounds and null endpoints are retained. [Per-profile JSON](r346/output/shadow-measurements.json) includes background±3% sensitivity for every feature. Low-contrast toes and background-sensitive widths should not be read as precise physical dimensions.

## Representative locations around the loop

The table and [profile figure](r346/output/shadow-profiles.png) use fixed geographic positions, with both sides retained in the full dataset. Each cell gives 10%-loss reach / 90–10% falloff in native pixels. Excluded boundaries are displayed for inspection but never enter the fit or numerical summary.

| Location | Image x/y | Photo reach / width | R345 reach / width | R346 reach / width |
|---|---|---:|---:|---:|
|S05m|2272/2131|175.2 / 127.0|40.2 / 7.1|215.5 / —|
|S18p|1501/3023|134.8 / 165.9|0.0 / —|78.4 / 112.0|
|S26p|949/2576|205.7 / 178.2|0.0 / —|218.3 / 181.9|
|S36p|1573/1999|63.6 / 72.2|46.3 / 8.2|77.8 / 72.0|
|S48m|1141/1529|28.3 / 36.7|36.7 / 7.2|56.1 / 54.6|
|S58m (excluded)|262/1404|0.0 / —|0.0 / —|0.0 / —|
|S74p|1117/340|73.5 / 79.3|26.6 / 7.1|62.2 / 62.5|
|S85m (excluded)|2026/630|228.9 / 179.9|0.0 / —|202.5 / 174.9|

Enlarged comparisons show the silhouettes and surrounding paper directly:

- [Right straight section](r346/output/crop-right-straight.jpg) and [right middle](r346/output/crop-right-middle.jpg), including border-limited extended shadow.
- [Top section](r346/output/crop-top.jpg) and [bottom bend](r346/output/crop-bottom-bend.jpg).
- [Left outer curve](r346/output/crop-left-outer.jpg) and [lower-left bend](r346/output/crop-lower-left-bend.jpg).
- [Interior bend](r346/output/crop-inner-bend.jpg) and [inside straight section](r346/output/crop-inside-straight.jpg).

Gray in the shadow-field figure marks excluded material/boundary bands. The photographic field is relative to an estimated smooth-paper reference; it is not a ground-truth shadow segmentation. Actual camera-visible bead darkness is excluded from all rendered-paper comparisons.

## One global lighting model

[Configuration](r346/config.json) records the accepted parameters:

| Parameter | R345 | R346 |
|---|---|---|
| Key position, original world units |(−300,350,850)|(-5500, -700, 4000)|
| Emitter diameter |75|6000|
| Angular diameter at scene origin |about4.4°|47.38°|
| Key intensity, arbitrary units |1.05|1.776244|
| Uniform room-fill source intensity |0.13|0.038773, shared tint|
| Ambient-room multiplier |1|0.298251, same shared tint|
| Fill tint, linear RGB multipliers |neutral|(2.646,0.575,0.358)|
| Camera |R345 orthographic80°|unchanged|

The key is one **fixed tilted circular planar diffuser**, normal toward the scene. Its lowest emitting point is 1567.1units above the paper; the source never crosses the paper plane. The weak warm room contribution is shared globally, represented by an ambient term and one shadowless fill source. It approximates diffuse room/interreflection illumination, rather than another hard shadow. No light position, source size, intensity, fill or tint varies by necklace section.

The broader angular source accounts for the extended gradual falloff; the more lateral key produces the longer rightward cast. Warm fill improves the paper-shadow color without changing any bead material. The source's physical distance, absolute power, room bounce spectrum and glass absorption are not uniquely recoverable from this one photograph. World units retain R345's arbitrary scale, so the coordinates are not measured lamp distances in meters. The setup is a plausible reconstruction, not a recovered lighting calibration.

POV-Ray's [area-light implementation](https://www.povray.org/documentation/view/3.7.1/313/) is used for soft shadow sampling. Individual bead specular highlights do not enter the fit. The fitted photograph background is an analysis reference only; the scene still renders the original procedural R345 paper, with no photographic background paste or local illumination texture.

The broad global search and its refinements are saved in [coarse results](r346/output/optimization.json), [refinement](r346/output/refinement.json), [wide-source controls](r346/output/wide-refinement.json), and [final grid](r346/output/final-refinement.json). Camera alternatives remain in [camera controls](r346/output/camera-light-controls.json) and were rejected. The final choice retains R345's camera exactly. Global RGB room/direct balance is calibrated from paper profiles; a separate global unshadowed-paper brightness fit sets intensity. Three quarters of geographic stations fit lighting; every fourth is reserved for comparison. All geography is retrospective on the same photograph, so this is not independent physical validation.

## Brightness, color and spatial agreement

| Paper-shadow comparison | R345 RMS | R346 RMS |
|---|---:|---:|
| Contour-relative profiles, all eligible contours |20.4%|6.8%|
| Contour-relative profiles, held geographic stations |20.0%|6.4%|
| Same image-coordinate paper pixels, all |19.9%|8.2%|
| Same image-coordinate paper pixels, held stations |19.8%|8.1%|
| Same pixels with photographic guard enlarged 4 px, held stations |19.5%|8.0%|

The held same-coordinate comparison contains 84,320 background samples. This evaluates the cast shadow's actual image position outside both silhouettes, rather than obtaining improvement by translating shadow profiles. Contour-relative profiles separately describe the relationship of the shadow to its own necklace silhouette. Both measures improve.

The following matched-paper RGB losses use the nearest safe 12–20 pixel band at strong-shadow locations. They describe the paper's color change, not bead pigment:

| Linear channel loss | Photograph | R345 | R346 |
|---|---:|---:|---:|
|red channel|71.2%|72.2%|69.8%|
|green channel|80.8%|73.2%|81.4%|
|blue channel|85.9%|72.3%|82.8%|

The same global fill tint is used everywhere. Unshadowed-paper luminance has a median relative error of 0.0% and spatial RMS of 7.6% against the smooth photographic reference. The unchanged paper/material and simple room model retain an unshadowed blue-channel bias of -10.8%. Remaining local color differences can also reflect approximate glass transmission and absorption; the fit does not establish a unique room illuminant.

## Validation, provenance and remaining discrepancies

[Independent verification](r346/output/verification.json) checks unchanged scene components, all 162 sealed R344/R345 files, 2704 exact pattern assignments, both sides at all 96 stations, rendered-paper samples, independent RMS calculations, analytic falloff/censoring controls and the physical emitter bounds. It never substitutes per-bead shadow observations.

Increasing area-light sampling from 17×17 to 33×33 changes the selected paper profiles by **0.1% RMS**, with95th-percentile difference 0.4%. [Sampling receipt](r346/output/sampling-convergence.json) holds all geometry and lighting parameters fixed. The native final render uses 17×17 adaptive sampling and antialiasing. [Renderer receipt](r346/output/render-receipt.json), [log](r346/output/scene.log), [scene](r346/output/scene.pov), [provenance](r346/output/provenance.json), [input seal](r346/output/input-seal.json) and [raw rendered profiles](r346/output/rendered-profiles.npz) make the result reviewable.

The broad spatial shadow relationship is much closer, but local agreement is incomplete. R345's idealized fixed bead packing, silhouette/height approximation and paper-contact geometry remain unchanged; therefore some dark near-edge bands and bends still differ. Paper grain and gradual illumination are approximate, faint endpoints depend on the background model, and the frame truncates some tails. The conservative body guard prevents independent measurement of most true contact shadow. No additional local correction is introduced to hide those discrepancies.

The R344 sequence/ledger and R345 reconstruction inputs remain byte-preserved. Stopped unrelated R340 work is untouched. This delivery stops after the scoped commit, push and remote verification; no automatic R347 or pattern/geometry campaign is started.

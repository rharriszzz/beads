# R250 evidence and data

[Scientific report](../../FFT_DENSE_TRACKING.md) · [protocol](protocol.json) ·
[summary](summary.json) · [verification](verification.json).

| Figure | Purpose |
| --- | --- |
| [Four-angle distribution](angle-distribution.png) | Four prevalent ranges and V/Y least-squares means |
| [Four angle fits versus arc length](four-angle-fits.png) | Original unsmoothed angles, constant fits and periodic alternatives |
| [Frequency by angular category](four-range-frequencies.png) | Includes multiple frequency bands in the unresolved −19° category |
| [V tracks](V-tracks.png) / [Y tracks](Y-tracks.png) | Measured angle, frequency, relative intensity, gaps and curvature |
| [Entire necklace](centerline.png) | All 2000 sampled centers, arc distance and indexing seam |
| [Events/context](events-context.png) | Fragment endpoints, trio support, tentative reappearances, appearance and curvature |
| [Helicity angle cues](helicity-angle-cues.png) | Signed offsets and intrinsically asymmetric 6/7 model; conditional interpretation |
| [Darkness/discontinuities](darkness-discontinuities.png) | Maker's black-bead hypothesis tested with an explicitly limited image proxy |

The curves join actual adjacent observations only; missing/ambiguous links are
not interpolated. Constant/periodic fit lines are labeled models. Ranks in FFT
cards are brightness ranks, not track IDs. Opposite FFT marks are one axial pair.

| Photographic / weighted / FFT / inverse example | Explanation |
| --- | --- |
| [1: s≈4170](transition-1.png) | An accepted V branch changes angular category through a bend |
| [2: s≈7619](transition-2.png) | Y frequency migration and broad V competition |
| [3: s≈1810](transition-3.png) | Actual adjacent rank inversion with accepted identity |
| [4: s≈480](transition-4.png) | Competing V association left unresolved |
| [5: s≈9162→9189](transition-5.png) | Tentative Y reappearance, original endpoints and intervening crop |
| [6: s≈3957](transition-6.png) | Maximum spline curvature, changing rows/reflections |

[Example coordinates and edge IDs](examples.json).

- [Candidates CSV](candidates.csv): 32,000 original observations, radii/angles/power/rank/flags/track ID.
- [Window CSV](windows.csv): geometry, failures, appearance proxies, supported primary trios.
- [Association CSV](associations.csv): eligible adjacent links, acceptance/cost/margin, tentative gaps and seam flags.
- [Events CSV](events.csv): measured appearances/disappearances and unresolved identities.
- [Full measurements](measurements-2000.json.gz): compressed JSON, including rejections and all candidate flags.
- [Tracks](tracks.json) and [track statistics](track-statistics.json): every measured fragment, not only highlighted ones.
- [Density comparison](density.json) and [initial timing records](initial-timings.json).
- [Cross-channel matches](cross-channel.csv): separate V/Y observations, no fusion.
- [Angle fits](angle-fits.json) and [fitted observation CSV](angle-range-observations.csv).
- [Conditional hand comparison](conditional-hand-cue.json) and [all model scores](conditional-hand-models.csv).
- [Darkness analysis](darkness-analysis.json) and [arc-bin data](darkness-bins.csv).
- [Full source-photograph replay](measurement-replay.json).
- [Source at initial protocol](source-at-protocol.txt): hash-verified initial implementation, preserved separately from final cache/diagnostic refinements.

The 200/1000 measurement archives are nested subsets; final analysis uses 2000.
All scripts and reproduction commands are linked in the scientific report.

# R298 reproduction and review

Launch from WSL2, with no virtual-environment activation or remembered URL:

```sh
photo2/review/r298/launch.sh
```

The script selects the existing repository `.venv`, starts a localhost server and
opens the Windows default browser using PowerShell when available. Otherwise it
uses wslview or the platform browser. An occupied port falls back to a free port.
Ctrl+C stops the server. `--no-browser --port 0` is available for testing. The
review also works by opening `photo2/review/r298/index.html` offline.

The delivered scientific artifacts are frozen. Do not overwrite them to replay.
Use an isolated copy/worktree of this commit, with the existing Python 3.12
NumPy/SciPy/Pillow/scikit-image environment. No new dependencies are needed.

Measurement chronology: measure-v1 had a photo() return-type error; v2's global
hue/luminance paper test followed shadows; v3's hue-only global test also failed.
The final local-side paper comparison and pre-fit analyst screen are preserved.
`measure.py` refuses to replace the final measurements. `visual-screen.json`
excludes specified visibly ambiguous profiles; these are analyst judgments, not
maker labels. Sixteen bead contour annotations are frozen inside measure.py.

The scientific sequence is:

1. `measure.py`: photo-only bead contours, raw profile pixels and uncertainties.
2. `calibrate.py --stage controls`: R297 paired sensitivities, shape/camera and axis
   controls; the saved no-roll checkpoint is the source for the original controls.
   The fixed-camera dimensions control calls `fit(..., 'dimensions')`.
3. Original `calibrate.py --stage joint`: unconstrained diagnostic fits, all colliding.
4. `physical_fit.py`, using the saved no-roll geometry/calibration checkpoint: fits
   with an analytic separation penalty, followed by actual full-chain certification.
5. `fit(..., 'shape')` with current camera-roll geometry gives the camera-rotation
   control. `roll_fit.py` performs the four bounded joint structural fits.
6. `photometry.py`: freezes existing region-pair raw separator profiles.
7. `refine.py`: bounded physically gated shared nuisance/dimension controls; no
   repeating pattern or individual displacement. `selection.json` ends fitting.
8. `export.py`: full native first-hit surfaces and unchanged supports, all positions,
   exact contact witnesses, native profile errors and independent saved FFT checks.

No later evaluation is used for another fit. All geography is retrospective.
Solver evaluation histories retain parameters and losses, including finite-difference
probes; only fully certified final candidates can enter the selected review.

Run checks:

```sh
.venv/bin/python -m unittest photo2.r298.tests
.venv/bin/python -m photo2.r298.verify
/home/rharris/.local/bin/beads-chromium-review photo2.r298.browser_check
git diff --check
```

The verification replays geometry, full-chain contacts, native rays, source support
accounting, raw measurement pixels and protected file hashes. Browser tests use the
actual launch.sh from another working directory, check raw/overlay separation,
model/region selection, native zoom, all links, narrow layout and offline operation.
Windows browser dispatch is mocked; the agent does not open a separate Windows GUI.

"""Write an offline pixel audit and concise diagnostic report; no classification edits."""
from pathlib import Path
import json,html,datetime
from PIL import Image,ImageOps,ImageDraw
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def main():
 d=json.loads((OUT/'measurements.json').read_text());rows=d['records'];photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
 cards=[]
 for r in rows:
  n=r['number'];name=html.escape(r['id']);box=r['absolute_material_box'];patch=r['patch_box']
  cards.append(f'<article id="bead-{n}"><h2>{n}. {name} — {r["color"]}, {r["score"]}/255</h2><p>{html.escape(r["authority"])}</p><div class="pair"><figure><img src="native-{n:02d}.png"><figcaption>Unaltered native RGB crop, enlarged nearest-neighbor.</figcaption></figure><figure><img src="measured-{n:02d}.png"><figcaption>Green: visually approved glass; cyan: selected 3×3 patch.</figcaption></figure></div><p>Native crop {r["bbox"]}; material {box}; patch {patch}. Coordinates use end-exclusive bounds.</p><details><summary>All nine original RGB pixels</summary><pre>{html.escape(json.dumps(r["patch_RGB"],indent=1))}</pre></details></article>')
 for n in [2,31]:
  r=rows[n-1];x,y=map(round,r['xy']);box=[x-60,y-60,x+61,y+61];photo.crop(box).save(OUT/f'context-{n:02d}.png');im=photo.crop(box).resize((605,605),Image.Resampling.NEAREST);draw=ImageDraw.Draw(im);a,b,c,e=r['absolute_material_box'];draw.rectangle(((a-box[0])*5,(b-box[1])*5,(c-box[0])*5-1,(e-box[1])*5-1),outline='lime',width=2);im.save(OUT/f'context-marked-{n:02d}.png')
 (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Genuine glass darkness — 48 maker-confirmed beads</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:0 1em;background:#fafafa;color:#222}img{max-width:100%;image-rendering:pixelated}.plot{image-rendering:auto}article{border-top:1px solid #aaa;margin-top:2em}.pair{display:flex;flex-wrap:wrap;gap:1em}figure{margin:0;width:328px}figure img{width:328px}h2{font-size:18px}pre{overflow:auto}</style><h1>Genuine glass darkness: 48 maker-confirmed bodies</h1><p>Diagnostic only. No bead identities, colors, lattice links or pattern positions changed.</p><p>Black21–57; red107–199; yellow190–233. No black/colored overlap; earlier threshold73.5 has zero errors. Red and yellow ranges overlap190–199.</p><img class="plot" src="brightness.png" alt="Shared brightness plot"><p>Each score is the smallest maximum RGB value among complete3×3 patches inside the visually approved glass rectangle. No averages, aperture voting or color-pattern information. Green rectangles were chosen from native body appearance before measurement. This tests supplied body interiors; it does not solve automatic material ownership.</p><p><a href="REPORT.md">Report</a> · <a href="measurements.json">Exact measurements and RGB</a> · <a href="../../../beads-photo-2.jpg">Full original photograph</a></p><h2>Closest black and red: broader native contexts</h2>'+''.join(f'<p>{rows[n-1]["id"]}: <a href="context-{n:02d}.png">unaltered121×121 crop</a></p><img src="context-marked-{n:02d}.png" width="484">' for n in [2,31])+''.join(cards))
 red_overlap=[r['id'] for r in rows if r['color']=='red' and r['score']>=190];yellow_overlap=[r['id'] for r in rows if r['color']=='yellow' and r['score']<=199]
 report=f'''# Material-darkness diagnostic: ten-minute continuation

![Shared brightness plot](brightness.png)

The maker's proposed distinction holds for all **48 maker-confirmed bodies tested**: **24 black21–57;12 red107–199;12 yellow190–233**, on the0–255 maximum-channel scale. The earlier **73.5** threshold separates them unchanged, with **zero false positives, zero false negatives and no measurement abstentions**. Any threshold t satisfying57≤t<107 separates these particular measurements using black≤t. No threshold was adjusted after seeing this expanded sample.

There are **no black-versus-colored exceptions**. Closest are **C-1893-2771, black57**, and **R332-R-0167-0155, red107**. These have broader unaltered121×121 native context crops in the [offline review](index.html). Red and yellow ranges overlap190–199; this does not affect black recognition. Red observations inside that overlap: {', '.join(red_overlap)}. Yellow: {', '.join(yellow_overlap)}.

Even the darkest *individual* pixel anywhere in the approved red material rectangles has maxRGB90; the yellow minimum is173. Both exceed the brightest selected black3×3 material-patch score57. This directly supports the proposed material distinction in these inspected regions, without averaging dark material with reflections.

## Selection and measurement

The reference labels come from R339's explicit authoritative-label ledger plus the six latest maker black decisions. Earlier displayed-panel acceptances are identified as such, distinct from individually requested recolorings. All48 IDs, exact authority text and original native coordinates are retained in [selection.json](selection.json). Selection prioritizes prior difficult black cases, all six new confirmations, then geographic diversity; no brightness score or repeating-pattern color selects the IDs. The sample contains reflection-free black bodies R332-B-0098-0092 and REC266-P073002, strong/weak white glints, colored reflected illumination, and beads across the photograph. Two earlier visually selected red controls were **not** promoted to maker confirmations.

Three IDs overlap the preceding nine-body diagnostic (R332-B-0098-0092, D40-K-2081-2611, C-0412-1572). **45 bodies are additional tests of its already fixed threshold**, all correctly separated. This is an expanded retrospective test with manually supplied body ownership, not an estimate of automatic whole-photograph accuracy.

1. Inspect original native RGB crops with a local pixel grid. Choose one rectangle safely in visible glass, away from the glint, outer rim and neighboring bodies; all48 explicit choices are in [manual-regions.json](manual-regions.json) and as literal constants in measure.py. Support locations are inherited and never recentered.
2. For each complete contiguous3×3 patch inside that rectangle, compute the maximum of its27 RGB values. Take the smallest such maximum. Thus **all nine pixels and all channels** of the selected patch must be dark. There is no mean, darker-half statistic, hue test, multiple aperture, morphology or repeating-pattern input.
3. Save original patch RGB and both absolute/local coordinates; inspect green material boxes and cyan selected patches against unaltered crops. All48 overlays were inspected; no region was adjusted after its score was seen.

This uses one fixed patch size,3×3 native pixels. Hand-approved material rectangles vary with the visible body; they are explicit photographic ownership annotations, not multiple-aperture votes. The scalar computation itself is simply `sliding_window_view(material.max(axis=2),(3,3)).max(axis=(-2,-1)).min()`.

## Checks, scope and reproduction

All48 vectorized scores were independently recomputed by explicit nested loops; saved native RGB maxima agree exactly. The original photograph SHA256 is in [measurements.json](measurements.json), alongside all measurements and exceptions (empty). The [review](index.html) supplies raw and annotated pixels for every stable ID; the full original photograph is linked. The original seven-maker-plus-two-visual-control diagnostic and its reported60-second overrun remain unchanged.

No classifier was redesigned or applied globally. No recorded colors, identity, geometry, exclusions, pattern or graph changed. E5-2272-1815's new maker-black decision is preserved as a diagnostic reference label; applying it to the reconstruction remains part of the paused broader task. Material ownership is supplied by manual visual inspection here; an automatic method must still avoid inter-bead darkness and boundary contamination. These results support a very simple darkness threshold **once genuine material has been identified**.

Run from repository root:

```
.venv/bin/python photo2/r340/material-diagnostic/select.py
MPLCONFIGDIR=/tmp/beads-material-mpl .venv/bin/python photo2/r340/material-diagnostic/measure.py
.venv/bin/python photo2/r340/material-diagnostic/review.py
```

The reference selection, photograph and manual regions are frozen. Timing: continuation began2026-10-20T01:35:33Z, ten-minute deadline01:45:33Z; expanded measurements completed01:39:15Z (about3m43s after start; numerical computation0.22s). Delivery timing is recorded separately. Stop after scoped add/commit/push; no next analysis step.
'''
 (OUT/'REPORT.md').write_text(report)
 print('Review/report written',datetime.datetime.now(datetime.timezone.utc).isoformat())
if __name__=='__main__':main()

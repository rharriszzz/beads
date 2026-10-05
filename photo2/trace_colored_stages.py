"""R224: observe frozen colored-mask stages without changing their decisions.

Diagnostic crops and points are selected only after whole-photo extraction.
The fresh watershed is captured by a wrapper that returns its result unchanged.
Every reconstructed guard/rim is checked against the original stored masks.
"""
import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage as ndi
from skimage.morphology import convex_hull_image

import refine_colored_masks as refinement
from auto_label_beads import ROOT, sha
from trim_colored_masks import PARAMETERS, connected_to_seed, diffuse_fields, trim_region


SOURCES = ["beads-photo-2.jpg", "photo2/segment_colored_beads.py",
           "photo2/refine_colored_masks.py", "photo2/trim_colored_masks.py"]
STAGES = [
    ("raw", "Raw photo", "No proposed body pixels."),
    ("watershed", "3: watershed", "The seed's share of the allowed color pixels; not a bead outline."),
    ("early_floor", "4a: brightness", "Keep diffuse brightness at least 32% of this share's Q90."),
    ("radius", "4b: seed radius", "Also keep pixels within 0.85 estimated diameters of the seed."),
    ("connected", "4c: connection", "Keep only the component containing the seed; this is the stored candidate."),
    ("old_rim", "5a: earlier rim", "Inset and remove the lowest 10% rim scores: the R218 reviewed mask."),
    ("extra_brightness", "Later brightness tests", "Show the R220 raw floor and two-of-three votes on the earlier mask, before its rim test."),
    ("final", "5b: current result", "Combine all R220 tests and keep the seed-connected component: the stored R220 mask."),
]
TESTS = [
    ("early_floor", "4: 32% brightness"),
    ("radius_test", "4: radius <= 0.85D"),
    ("late_floor", "Later: 45% brightness"),
    ("votes_test", "Later: at least 2 votes"),
    ("late_inset", "5: minimum inset"),
    ("late_rank", "5: omit weakest 15%"),
]
FLAG_NAMES = ["watershed", "early_floor", "radius_test", "connected", "old_rim",
              "late_floor", "vote_0", "vote_1", "vote_2", "votes_test",
              "late_inset", "late_rank", "final"]


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def raw_watershed(image, digest, routine, reuse):
    fingerprint = {p: sha(ROOT / p) for p in SOURCES}
    if reuse:
        saved = json.loads((routine / "capture.json").read_text())
        assert saved["source_sha256"] == fingerprint, "Trace source changed"
        assert sha(routine / "watershed.npz") == saved["watershed_archive_sha256"]
        archive = np.load(routine / "watershed.npz")
        report = json.loads((ROOT / "photo2/review/r218/regions.json").read_text())
        arrays = dict(np.load(ROOT / "photo2/output/r218/pixel-masks.npz"))
        return report, arrays, archive["watershed"], archive["markers"], saved
    captured = np.zeros(image.shape[:2], np.int32)
    markers = np.zeros_like(captured)
    original = refinement.watershed

    def observe(elevation, seeds, **kwargs):
        result = original(elevation, seeds, **kwargs)
        captured[result > 0] = result[result > 0]
        markers[seeds > 0] = seeds[seeds > 0]
        return result

    refinement.watershed = observe
    try:
        report, arrays = refinement.refine(image, digest)
    finally:
        refinement.watershed = original
    frozen = dict(np.load(ROOT / "photo2/output/r218/pixel-masks.npz"))
    assert frozen.keys() == arrays.keys()
    assert all(np.array_equal(v, frozen[k]) for k, v in arrays.items()), "Baseline did not repeat"
    np.savez_compressed(routine / "watershed.npz", watershed=captured, markers=markers)
    saved = dict(source_sha256=fingerprint, watershed_archive_sha256=sha(routine / "watershed.npz"),
                 fresh_baseline_arrays_repeat=True, wrapper_returns_original_result_unchanged=True)
    save_json(routine / "capture.json", saved)
    return report, arrays, captured, markers, saved


def mask_overlay(rgb, mask, rejected=None):
    pixels = rgb.astype(float).copy()
    if rejected is not None:
        pixels[rejected] = .72 * pixels[rejected] + .28 * np.array([255, 135, 25])
    pixels[mask] = .78 * pixels[mask] + .22 * np.array([35, 255, 90])
    edge = mask & ~ndi.binary_erosion(mask)
    pixels[edge] = .2 * pixels[edge] + .8 * np.array([35, 255, 90])
    return Image.fromarray(np.uint8(np.clip(pixels, 0, 255)))


def mark(panel, xy, label, color=(0, 230, 255), seed=False):
    draw = ImageDraw.Draw(panel)
    x, y = xy
    if seed:
        draw.line((x-5, y-5, x+5, y+5), fill=(0, 0, 0), width=4)
        draw.line((x-5, y+5, x+5, y-5), fill=(0, 0, 0), width=4)
        draw.line((x-5, y-5, x+5, y+5), fill=(255, 70, 235), width=2)
        draw.line((x-5, y+5, x+5, y-5), fill=(255, 70, 235), width=2)
    else:
        font = ImageFont.truetype("DejaVuSans.ttf", 20)
        end = (x+30, y-26)
        draw.line((x+3, y-3, *end), fill="black", width=4)
        draw.line((x+3, y-3, *end), fill=color, width=2)
        draw.ellipse((x-3, y-3, x+3, y+3), outline=color, width=2)
        draw.text((end[0]+2, end[1]-12), label, fill=color, font=font, stroke_width=2, stroke_fill="black")


def filmstrip(case, rgb, masks, out):
    width, height = rgb.shape[1] * 3, rgb.shape[0] * 3
    header = 72
    canvas = Image.new("RGB", (width * 4, (height + header) * 2 + 45), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("DejaVuSans.ttf", 18)
    small = ImageFont.truetype("DejaVuSans.ttf", 16)
    previous = None
    for i, (key, title, _) in enumerate(STAGES):
        mask = masks[key]
        removed = None if previous is None else previous & ~mask
        if key == "raw":
            panel = Image.fromarray(rgb)
        else:
            panel = mask_overlay(rgb, mask, removed)
        panel = panel.resize((width, height), Image.Resampling.NEAREST)
        mark(panel, tuple(v * 3 + 1 for v in case["seed_crop_xy"]), "", seed=True)
        mark(panel, tuple(v * 3 + 1 for v in case["point_crop_xy"]), "P")
        x, y = (i % 4) * width, (i // 4) * (height + header)
        canvas.paste(panel, (x, y + header))
        draw.text((x+6, y+6), title, fill="black", font=font)
        count = "" if key == "raw" else f"{case['counts'][key]} pixels"
        draw.text((x+6, y+33), f"{case['letter']} / auto {case['region_number']}    {count}", fill="black", font=small)
        if key != "raw":
            previous = mask
    draw.text((7, canvas.height-34), "Green: current pixels. Orange: removed since preceding panel. Pink X: seed. P: unreviewed diagnostic point.", fill="black", font=small)
    canvas.save(out / f"sequence-{case['letter'].lower()}.png")


def tests_figure(case, rgb, masks, out):
    width, height, header = rgb.shape[1] * 3, rgb.shape[0] * 3, 70
    canvas = Image.new("RGB", (width * 3, (height+header) * 2 + 42), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("DejaVuSans.ttf", 18)
    small = ImageFont.truetype("DejaVuSans.ttf", 16)
    for i, (key, title) in enumerate(TESTS):
        support = masks["watershed"]
        keep = masks[key] & support
        panel = mask_overlay(rgb, keep, support & ~keep).resize((width, height), Image.Resampling.NEAREST)
        mark(panel, tuple(v * 3 + 1 for v in case["point_crop_xy"]), "P")
        x, y = (i % 3) * width, (i // 3) * (height + header)
        canvas.paste(panel, (x, y+header))
        draw.text((x+6, y+7), title, fill="black", font=font)
        draw.text((x+6, y+34), f"P: {'PASS' if masks[key][tuple(case['point_crop_xy'][::-1])] else 'FAIL'}", fill="black", font=small)
    draw.text((7, canvas.height-32), "Each test shown alone on step 3 pixels. Green passes; orange fails. Final output requires their combined tests.", fill="black", font=small)
    canvas.save(out / f"tests-{case['letter'].lower()}.png")


def partition_figure(case, image, baseline, raw, markers, out):
    from matplotlib.colors import hsv_to_rgb
    x0,y0,x1,y1 = case["crop"]
    sl = (slice(y0,y1),slice(x0,x1))
    rgb = image[sl]
    mode = int(baseline["family"][round(case["seed_xy"][1]),round(case["seed_xy"][0])])
    support = baseline["domain"][sl] & (baseline["family"][sl]==mode)
    terrain = rgb.astype(float)*.25
    darkness = baseline["valley"][sl]
    terrain[support] = (255*(1-np.clip(darkness[support]/.8,0,1)))[:,None]
    partition = rgb.astype(float)*.3
    labels = raw[sl]
    for ident in np.unique(labels[support]):
        if not ident:
            continue
        color = 255*hsv_to_rgb([((int(ident)*.61803398875)%1),.65,.95])
        partition[support & (labels==ident)] = color
    displays = [(Image.fromarray(rgb),"Raw photo"),
                (mask_overlay(rgb,support),"Allowed yellow-family pixels"),
                (Image.fromarray(np.uint8(terrain)),"Watershed surface: dark = high cost"),
                (Image.fromarray(np.uint8(partition)),"Step 3: competing seeds' shares")]
    width,height,header = (x1-x0)*3,(y1-y0)*3,65
    canvas = Image.new("RGB",(width*4,height+header+45),"white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("DejaVuSans.ttf",17)
    small = ImageFont.truetype("DejaVuSans.ttf",14)
    for j,(panel,title) in enumerate(displays):
        panel = panel.resize((width,height),Image.Resampling.NEAREST)
        if j in (2,3):
            pd = ImageDraw.Draw(panel)
            for y,x in np.argwhere((markers[sl]>0)&support):
                ident = int(markers[sl][y,x]); color = "cyan" if ident==case["region_number"] else "white"
                pd.ellipse((x*3-2,y*3-2,x*3+4,y*3+4),fill=color)
                pd.text((x*3+5,y*3-5),str(ident),font=small,fill=color,stroke_width=1,stroke_fill="black")
        canvas.paste(panel,(j*width,header))
        draw.text((j*width+5,10),title,font=font,fill="black")
    draw.text((7,canvas.height-32),"White/cyan dots are automatic seeds. Higher darkness delays flooding; it is not a stop rule. Colored shares are proposals, not bead identities.",font=small,fill="black")
    canvas.save(out/"partition-b.png")


def png_data(pixels):
    buf = io.BytesIO()
    Image.fromarray(pixels).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def make_case(row, box, letter, image, baseline, final, raw, markers, diffuse, smooth, diameter, out):
    ident = row["region_number"]
    marker_xy = tuple(round(v) for v in row["seed_xy"])[::-1]
    assert markers[marker_xy] == ident, "Seed/observation label mismatch"
    ys, xs = np.nonzero(raw == ident)
    sl = (slice(int(ys.min()), int(ys.max())+1), slice(int(xs.min()), int(xs.max())+1))
    seed_x, seed_y = row["seed_xy"]
    local = (round(seed_y)-sl[0].start, round(seed_x)-sl[1].start)
    share = raw[sl] == ident
    q90_early = float(np.quantile(diffuse[sl][share], .90))
    early_floor = share & (diffuse[sl] >= .32*q90_early)
    yy, xx = np.mgrid[sl[0], sl[1]]
    seed_radius = np.hypot(xx-seed_x, yy-seed_y)
    radius_test = seed_radius <= .85*diameter
    radius = early_floor & radius_test
    candidate = connected_to_seed(radius, local)
    assert np.array_equal(candidate, baseline["candidate"][sl] == ident), "Step 4 trace mismatch"
    distance = ndi.distance_transform_edt(np.pad(candidate, 1))[1:-1, 1:-1]
    q90_late = float(np.quantile(diffuse[sl][candidate], .90))
    valley = baseline["valley"][sl]
    confidence_early = distance + .25*diffuse[sl]/max((.32*q90_early)/.32, .02) - .25*valley
    threshold_early = float(np.quantile(confidence_early[candidate], .10))
    min_inset = max(.5, .018*diameter)
    old = candidate & (distance >= min_inset) & (confidence_early >= threshold_early)
    assert np.array_equal(old, baseline["retained"][sl] == ident), "Earlier rim mismatch"
    votes = np.zeros(share.shape, np.uint8)
    vote_masks = []
    references = []
    for values in smooth:
        reference = float(np.quantile(values[sl][candidate], .90))
        references.append(reference)
        keep = connected_to_seed(candidate & (values[sl] >= .45*reference), local)
        vote_masks.append(keep)
        votes += keep
    late_floor = diffuse[sl] >= .45*q90_late
    votes_test = votes >= 2
    confidence = distance + .25*diffuse[sl]/max(q90_late, .02) - .25*valley
    threshold_late = float(np.quantile(confidence[candidate], .15))
    late_inset = distance >= min_inset
    late_rank = confidence >= threshold_late
    extra = old & late_floor & votes_test
    combined = extra & late_inset & late_rank
    current = connected_to_seed(combined, local)
    stored = final["retained"][sl] == ident
    assert np.array_equal(current, stored), "Current result mismatch"
    # Also call the real function in its exact, smaller stored-candidate box.
    cy, cx = np.nonzero(candidate)
    small = (slice(cy.min(), cy.max()+1), slice(cx.min(), cx.max()+1))
    smaller_seed = (local[0]-small[0].start, local[1]-small[1].start)
    expected = trim_region(candidate[small], old[small], diffuse[sl][small],
                           [v[sl][small] for v in smooth], smaller_seed, diameter,
                           "stable", valley=valley[small])
    assert np.array_equal(expected, stored[small]), "Direct production-function mismatch"
    local_masks = dict(raw=np.zeros_like(share), watershed=share, early_floor=early_floor,
                       radius_test=radius_test, radius=radius, connected=candidate, old_rim=old,
                       extra_brightness=extra, late_floor=late_floor, votes_test=votes_test,
                       late_inset=late_inset, late_rank=late_rank, final=current,
                       **{f"vote_{i}":v for i,v in enumerate(vote_masks)})
    x0,y0,x1,y1 = box
    crop = (slice(y0,y1), slice(x0,x1))
    def in_crop(values):
        result = np.zeros((y1-y0,x1-x0), values.dtype)
        lo_y,hi_y = max(y0,sl[0].start),min(y1,sl[0].stop)
        lo_x,hi_x = max(x0,sl[1].start),min(x1,sl[1].stop)
        result[lo_y-y0:hi_y-y0,lo_x-x0:hi_x-x0] = values[lo_y-sl[0].start:hi_y-sl[0].start,lo_x-sl[1].start:hi_x-sl[1].start]
        return result
    masks = {k: in_crop(v) for k,v in local_masks.items()}
    # A conspicuous off-seed interior pixel is a question, not contamination truth.
    qualified = current & (distance >= 2)
    if not qualified.any():
        qualified = current
    py,px = np.unravel_index(np.where(qualified, seed_radius, -1).argmax(), current.shape)
    point = [int(px+sl[1].start), int(py+sl[0].start)]
    assert x0 <= point[0] < x1 and y0 <= point[1] < y1
    flags = np.zeros(share.shape, np.uint16)
    for bit,name in enumerate(FLAG_NAMES):
        flags |= local_masks[name].astype(np.uint16) << bit
    points = np.column_stack(np.nonzero(share))
    detail = []
    for y,x in points:
        index = int((y+sl[0].start-y0)*(x1-x0) + x+sl[1].start-x0)
        if not 0 <= x+sl[1].start-x0 < x1-x0 or not 0 <= y+sl[0].start-y0 < y1-y0:
            continue
        detail.append([index, int(flags[y,x]), float(diffuse[sl][y,x]), float(valley[y,x]),
                       float(distance[y,x]), float(confidence[y,x]), float(seed_radius[y,x]),
                       int(votes[y,x]), *[float(v[sl][y,x]) for v in smooth]])
    point_index = (point[1]-y0)*(x1-x0)+point[0]-x0
    witness = next(p for p in detail if p[0] == point_index)
    case = dict(letter=letter, region_number=ident, seed_xy=row["seed_xy"],
                source_observation_id=row["observation_id"], crop=box,
                seed_crop_xy=[round(seed_x)-x0,round(seed_y)-y0], point_xy=point,
                point_crop_xy=[point[0]-x0,point[1]-y0], point_ownership="unreviewed",
                point_selection="Farthest retained pixel from the seed with >=2px candidate inset; diagnostic only",
                counts={key:int(value.sum()) for key,value in local_masks.items() if key in dict((s[0],s[1]) for s in STAGES)},
                parameters=dict(diameter=diameter,seed_radius_limit=.85*diameter,
                    early_reference=q90_early,early_floor=.32*q90_early,late_reference=q90_late,
                    late_floor=.45*q90_late,smoothing_references=references,
                    smoothing_floors=[.45*v for v in references],minimum_inset=min_inset,
                    early_rim_threshold=threshold_early,late_rim_threshold=threshold_late),
                witness=witness, flags=FLAG_NAMES, data_fields=["crop_index","flags","diffuse_V","valley",
                    "candidate_inset_pixels","late_score","seed_distance_pixels","votes",
                    "smooth_V_0","smooth_V_1","smooth_V_2"], pixels=detail,
                trace_matches_stored_candidate_and_both_retained_masks=True)
    case["watershed_darkness"] = dict(zero_pixels=int((valley[share]==0).sum()),
                                      maximum=float(valley[share].max()),
                                      percentile_95=float(np.quantile(valley[share],.95)))
    rgb = image[crop]
    filmstrip(case,rgb,masks,out)
    tests_figure(case,rgb,masks,out)
    case["raw_png"] = png_data(rgb)
    Image.fromarray(rgb).save(out/f"raw-{letter.lower()}.png")
    mask_overlay(rgb,masks["final"]).save(out/f"final-{letter.lower()}.png")
    case["layers"] = {key:base64.b64encode(masks[key].astype(np.uint8).tobytes()).decode() for key,_,_ in STAGES}
    if letter == "B":
        partition_figure(case,image,baseline,raw,markers,out)
    return case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"photo2/review/r224")
    parser.add_argument("--reuse-trace", action="store_true", help="Rebuild presentation from the sealed diagnostic capture")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    routine = ROOT/"photo2/output/r224"
    routine.mkdir(parents=True, exist_ok=True)
    protected = json.loads((ROOT/"photo2/review/r220/summary.json").read_text())
    prior = json.loads((ROOT/"photo2/review/r218/summary.json").read_text())
    assert sha(ROOT/"photo2/output/r218/pixel-masks.npz") == prior["mask_archive_sha256"]
    assert sha(ROOT/"photo2/review/r218/regions.json") == prior["curated_sha256"]["regions.json"]
    assert sha(ROOT/"photo2/output/r220/pixel-masks.npz") == protected["mask_archive_sha256"]
    for group in ("source_sha256", "protected_inputs"):
        assert all(sha(ROOT/p)==v for p,v in protected[group].items())
    assert all(sha(ROOT/"photo2/review/r220"/p)==v for p,v in protected["curated_sha256"].items())
    photo = ROOT/"beads-photo-2.jpg"
    image = np.asarray(ImageOps.exif_transpose(Image.open(photo)).convert("RGB"))
    print("Capturing the unchanged whole-photo watershed...", flush=True)
    report,baseline,raw,markers,capture = raw_watershed(image,sha(photo),routine,args.reuse_trace)
    final = dict(np.load(ROOT/"photo2/output/r220/pixel-masks.npz"))
    diameter = report["parameters"]["native_diameter"]
    diffuse,smooth = diffuse_fields(image,baseline,diameter)
    locations = json.loads((ROOT/"photo2/review/r218/review-locations.json").read_text())
    rows = {r["region_number"]:r for r in report["records"]}
    cases = [make_case(rows[loc["region_number"]],loc["crop"],loc["letter"],image,baseline,final,
                       raw,markers,diffuse,smooth,diameter,args.output) for loc in locations["question_regions"]]
    # Post-extraction demonstration of a non-round mask in an earlier automatic context.
    box = locations["automatic_contexts"][1]["crop"]
    options = []
    for row in report["records"]:
        x,y = row["seed_xy"]
        if not (box[0]<x<box[2] and box[1]<y<box[3] and row["central_candidate"]):
            continue
        yy,xx = np.nonzero(final["retained"]==row["region_number"])
        if len(yy)<300:
            continue
        if (row["region_number"] in [c["region_number"] for c in cases]
                or xx.min()<box[0] or xx.max()>=box[2] or yy.min()<box[1] or yy.max()>=box[3]):
            continue
        mask = final["retained"][yy.min():yy.max()+1,xx.min():xx.max()+1]==row["region_number"]
        options.append((1-mask.sum()/convex_hull_image(mask).sum(),row))
    assert options
    chosen = max(options,key=lambda p:p[0])[1]
    yy,xx = np.nonzero(raw==chosen["region_number"])
    # Preserve the earlier context and widen it enough to show the whole share.
    box = [max(0,min(box[0],int(xx.min())-15)), max(0,min(box[1],int(yy.min())-15)),
           min(image.shape[1],max(box[2],int(xx.max())+16)),min(image.shape[0],max(box[3],int(yy.max())+16))]
    cases.append(make_case(chosen,box,"C",image,baseline,final,raw,markers,diffuse,smooth,diameter,args.output))
    data = dict(request="R224",photo_sha256=sha(photo),pixel_coordinates="EXIF-oriented native image; x right, y down; zero based",
                method="Unchanged R215 appearance / R218 refinement / R220 stable trimming",
                capture=capture,stages=STAGES,flag_names=FLAG_NAMES,cases=cases,
                limitation="Neither P nor the current masks have maker ownership confirmation; no roundness rule is applied")
    save_json(args.output/"trace.json",{**data,"cases":[{k:v for k,v in c.items() if k not in ("raw_png","layers","pixels")} for c in cases]})
    template = (ROOT/"photo2/mask_stage_viewer.html").read_text()
    payload = json.dumps(data,separators=(",",":"),allow_nan=False).replace("<","\\u003c")
    (args.output/"index.html").write_text(template.replace("__TRACE_DATA__",payload))
    sources = {p:sha(ROOT/p) for p in SOURCES+["photo2/trace_colored_stages.py","photo2/mask_stage_viewer.html"]}
    payloads = ["trace.json","index.html","partition-b.png"]+[f"{kind}-{c['letter'].lower()}.png" for kind in ("sequence","tests","raw","final") for c in cases]
    save_json(args.output/"summary.json",dict(request="R224",source_sha256=sources,
        curated_sha256={p:sha(args.output/p) for p in payloads},prior_review_summary_sha256=sha(ROOT/"photo2/review/r220/summary.json"),
        baseline_mask_archive_sha256=prior["mask_archive_sha256"],final_mask_archive_sha256=protected["mask_archive_sha256"],
        protected_inputs_unchanged=True,baseline_repeats=True,selected_case_trace_matches=True,
        segmentation_changed=False,roundness_rule_added=False,manual_labels_read=False,
        reconstruction_fit_performed=False,reproduction=[".venv/bin/python photo2/trace_colored_stages.py",
        ".venv/bin/python photo2/trace_colored_stages.py --reuse-trace"]))
    print(json.dumps({"cases":[{k:c[k] for k in ("letter","region_number","point_xy","counts")} for c in cases]},indent=2),flush=True)


if __name__ == "__main__":
    main()

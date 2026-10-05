"""Verify R224 stage illustrations, viewer coordinates and frozen question data."""
import ast
import base64
import importlib.metadata
import io
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from auto_label_beads import ROOT, sha


def main():
    out = ROOT / "photo2/review/r224"
    current = json.loads((out / "summary.json").read_text())
    for path, digest in current["source_sha256"].items():
        assert sha(ROOT / path) == digest, path
    for path, digest in current["curated_sha256"].items():
        assert sha(out / path) == digest, path
    previous = json.loads((ROOT / "photo2/review/r220/summary.json").read_text())
    preserved = 0
    for group in ("source_sha256", "protected_inputs"):
        for path, digest in previous[group].items():
            assert sha(ROOT / path) == digest, path
            preserved += 1
    for path, digest in previous["curated_sha256"].items():
        assert sha(ROOT / "photo2/review/r220" / path) == digest, path
        preserved += 1
    assert sha(ROOT / "photo2/output/r218/pixel-masks.npz") == current["baseline_mask_archive_sha256"]
    assert sha(ROOT / "photo2/output/r220/pixel-masks.npz") == current["final_mask_archive_sha256"]
    html = (out / "index.html").read_text()
    payload = re.search(r'<script id="trace-data" type="application/json">(.*?)</script>', html, re.S)
    data = json.loads(payload.group(1))
    cases = data["cases"]
    photo = np.asarray(ImageOps.exif_transpose(Image.open(ROOT / "beads-photo-2.jpg")).convert("RGB"))
    original = dict(np.load(ROOT / "photo2/output/r218/pixel-masks.npz"))
    final = dict(np.load(ROOT / "photo2/output/r220/pixel-masks.npz"))
    capture = ROOT / "photo2/output/r224/watershed.npz"
    assert sha(capture) == data["capture"]["watershed_archive_sha256"]
    raw = np.load(capture)["watershed"]
    rows = []
    for case in cases:
        ident = case["region_number"]
        x0,y0,x1,y1 = case["crop"]
        sl = (slice(y0,y1),slice(x0,x1))
        shape = (y1-y0,x1-x0)
        decoded = np.asarray(Image.open(io.BytesIO(base64.b64decode(case["raw_png"]))))
        assert np.array_equal(decoded, photo[sl])
        assert np.array_equal(np.asarray(Image.open(out / f"raw-{case['letter'].lower()}.png")), decoded)
        layers = {key:np.frombuffer(base64.b64decode(value),np.uint8).reshape(shape)
                  for key,value in case["layers"].items()}
        for key, expected in (("watershed", raw[sl] == ident),
                              ("connected", original["candidate"][sl] == ident),
                              ("old_rim", original["retained"][sl] == ident),
                              ("final", final["retained"][sl] == ident)):
            assert np.array_equal(layers[key],expected), (case["letter"],key)
        assert all(int(mask.sum())==case["counts"][key] for key,mask in layers.items())
        indices = set()
        for pixel in case["pixels"]:
            index,flags = pixel[:2]
            assert 0 <= index < np.prod(shape) and index not in indices
            indices.add(index)
            for bit,key in ((0,"watershed"),(3,"connected"),(4,"old_rim"),(12,"final")):
                assert bool(flags & (1<<bit)) == bool(layers[key].ravel()[index])
        assert len(indices) == case["counts"]["watershed"]
        px,py = case["point_xy"]
        assert final["retained"][py,px] == ident
        assert case["point_ownership"] == "unreviewed"
        rows.append(dict(letter=case["letter"],region_number=ident,
                         pixels=case["counts"]["final"],exact_native_layers=True,
                         inspector_records=len(indices),point_xy=case["point_xy"]))
    question_path = ROOT / "photo2/stage-diagnostic-questions-r224.json"
    questions = json.loads(question_path.read_text())
    for case in questions["cases"]:
        assert sha(ROOT / case["sequence_image"]) == case["sequence_sha256"]
        ident = case["automatic_region_number"]
        decoded = np.zeros(photo.shape[:2],bool)
        for y,lo,hi in case["final_pixel_runs"]:
            decoded[y,lo:hi+1] = True
        assert np.array_equal(decoded,final["retained"]==ident)
    assert questions["questions"][0]["status"] == "pending"
    repair_path = ROOT / "photo2/review/r226/viewer-startup-fix.json"
    repair = json.loads(repair_path.read_text())
    assert sha(ROOT / repair["source_filename"]) == repair["source_sha256"]
    assert sha(ROOT / repair["curated_screenshot"]) == repair["curated_sha256"]
    expected_crop = Image.open(ROOT / repair["source_filename"]).crop(repair["crop"])
    assert np.array_equal(np.asarray(expected_crop),np.asarray(Image.open(ROOT / repair["curated_screenshot"])))
    scripts = re.findall(r'<script(?![^>]*application/json)[^>]*>(.*?)</script>',html,re.S)
    for index,script in enumerate(scripts):
        path = Path(f"/tmp/beads-mask-stage-check-{index}.js")
        path.write_text(script)
        subprocess.run(["node","--check",str(path)],check=True,capture_output=True,text=True)
    js = subprocess.run(["node",str(ROOT / "photo2/test_mask_stage_viewer.cjs")],
                        check=True,capture_output=True,text=True)
    for path in ("photo2/trace_colored_stages.py","photo2/check_stage_diagnostics.py"):
        ast.parse((ROOT / path).read_text(),filename=path)
    old_log = subprocess.run(["git","show","HEAD:REQUEST_LOG.md"],cwd=ROOT,
                             check=True,capture_output=True).stdout
    assert (ROOT / "REQUEST_LOG.md").read_bytes().startswith(old_log)
    checked_links = 0
    for path in ("photo2/MASK_STAGE_DIAGNOSTICS.md",):
        md = ROOT / path
        for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
            if target.startswith(("http:","https:","#")):
                continue
            assert (md.parent / target.split("#")[0]).exists(),target
            checked_links += 1
    subprocess.run(["git","diff","--check"],cwd=ROOT,check=True,capture_output=True)
    report = dict(request="R224–R228",source_and_curated_hashes_match=True,
                  prior_protected_entries_checked=preserved,native_case_checks=rows,
                  original_question_images_and_extents_preserved=True,ownership_question_pending=True,
                  supplied_screenshot_unchanged_and_curated_crop_exact=True,
                  viewer_repair_record_sha256=sha(repair_path),
                  javascript_syntax=True,viewer_harness=js.stdout.strip(),browser_paint_exercised=False,
                  append_only_log_prefix=True,local_review_links_checked=checked_links,
                  versions={p:importlib.metadata.version(p) for p in ("numpy","scipy","Pillow","scikit-image")},
                  verifier_sha256=sha(ROOT / "photo2/check_stage_diagnostics.py"),
                  viewer_test_sha256=sha(ROOT / "photo2/test_mask_stage_viewer.cjs"),
                  reproduction=".venv/bin/python photo2/check_stage_diagnostics.py")
    (out / "verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(preserved=preserved,cases=rows,viewer=js.stdout.strip()),indent=2))


if __name__ == "__main__":
    main()

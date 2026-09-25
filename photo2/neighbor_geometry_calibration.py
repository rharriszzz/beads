#!/usr/bin/env python3
"""R075: calibrate local mask-centroid and outline proxies near beads3 warnings.

This is image-only. It compares provisional color-constrained masks with
marker positions; it does not produce physical bead centers or bead indices.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent/"output/matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import Ellipse
from scipy.spatial.distance import cdist
from skimage.measure import find_contours

import blind_generated as bg

ROOT = Path(__file__).resolve().parents[1]
R071 = ROOT / "photo2/review/r071"
CONFIG = ROOT / "photo2/black-region-review-r073.json"
PARAMETERS = {"max_reference_distance_px": 58.0, "max_references": 12,
              "minimum_references": 5, "same_color_only": True,
              "outline_mahalanobis_radius": 2.0}


def moments(mask: np.ndarray) -> dict:
    y, x = np.nonzero(mask)
    if len(x) < 5:
        raise ValueError("Mask has too few pixels for a contour proxy")
    points = np.column_stack((x, y)).astype(float)
    center = points.mean(axis=0)
    cov = np.cov(points.T)
    values, vectors = np.linalg.eigh(cov)
    values = np.maximum(values, 1e-8)
    return {"centroid": center, "covariance": cov,
            "eigenvalues": values, "eigenvectors": vectors,
            "area": int(len(x)), "bbox": [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)]}


def boundary(mask: np.ndarray) -> np.ndarray:
    curves = find_contours(mask.astype(float), .5)
    if not curves:
        return np.empty((0, 2))
    curve = max(curves, key=len)
    return curve[:, ::-1]


def ellipse_points(center: np.ndarray, covariance: np.ndarray, count=180) -> np.ndarray:
    # A uniform filled ellipse has covariance R^2/4. This is explicitly a proxy.
    values, vectors = np.linalg.eigh(covariance)
    theta = np.linspace(0, 2*np.pi, count, endpoint=False)
    circle = np.stack((np.cos(theta), np.sin(theta)))
    return center + (vectors @ (2*np.sqrt(np.maximum(values, 1e-8))[:, None] * circle)).T


def nearest_error(a: np.ndarray, b: np.ndarray) -> dict:
    if not len(a) or not len(b):
        return {"median_px": None, "p90_px": None, "symmetric_mean_px": None}
    d = cdist(a, b)
    da, db = d.min(axis=1), d.min(axis=0)
    return {"median_px": float(np.median(np.r_[da, db])),
            "p90_px": float(np.percentile(np.r_[da, db], 90)),
            "symmetric_mean_px": float((da.mean()+db.mean())/2)}


def robust_cov(mats: list[np.ndarray]) -> np.ndarray:
    # Elementwise median is robust to partial-mask elongation; symmetrize after.
    cov = np.median(np.stack(mats), axis=0)
    return (cov + cov.T) / 2


def fit_region(name: str, case: dict, rows: dict, labels: np.ndarray) -> dict:
    target = int(name)
    row = rows[target]
    xy = np.asarray(row["marker_xy"], float)
    candidates = []
    for ident, other in rows.items():
        if ident == target or not other.get("selection", {}).get("active", False):
            continue
        if other["selection"].get("warnings"):
            continue
        if PARAMETERS["same_color_only"] and other["color"] != row["color"]:
            continue
        distance = float(np.linalg.norm(np.asarray(other["marker_xy"], float)-xy))
        if distance <= PARAMETERS["max_reference_distance_px"]:
            candidates.append((distance, ident))
    candidates.sort()
    refs = [ident for _, ident in candidates[:PARAMETERS["max_references"]]]
    if len(refs) < PARAMETERS["minimum_references"]:
        raise ValueError(f"Region {name}: only {len(refs)} local controls")
    measurements = {ident: moments(labels == ident) for ident in refs}
    offsets = {ident: measurements[ident]["centroid"] - np.asarray(rows[ident]["marker_xy"], float) for ident in refs}
    loo = []
    for ident in refs:
        train = [j for j in refs if j != ident]
        predicted_offset = np.median(np.stack([offsets[j] for j in train]), axis=0)
        actual_center = measurements[ident]["centroid"]
        predicted_center = np.asarray(rows[ident]["marker_xy"], float) + predicted_offset
        cov = robust_cov([measurements[j]["covariance"] for j in train])
        actual_boundary = boundary(labels == ident)
        predicted_boundary = ellipse_points(predicted_center, cov, count=360)
        loo.append({"id": ident, "prediction_xy": predicted_center.tolist(),
                    "mask_centroid_xy": actual_center.tolist(),
                    "centroid_error_px": float(np.linalg.norm(predicted_center-actual_center)),
                    "mask_marker_offset_xy": offsets[ident].tolist(),
                    "contour_error": nearest_error(predicted_boundary, actual_boundary),
                    "training_ids": train})
    offset = np.median(np.stack(list(offsets.values())), axis=0)
    covariance = robust_cov([m["covariance"] for m in measurements.values()])
    predicted_center = xy + offset
    target_mask = labels == target
    target_contour = boundary(target_mask)
    predicted_contour = ellipse_points(predicted_center, covariance, count=360)
    return {"target_id": target, "target_color": row["color"],
            "reference_ids": refs, "reference_distances_px": {str(i): round(float(np.linalg.norm(np.asarray(rows[i]["marker_xy"])-xy)), 3) for i in refs},
            "target_marker_xy": xy.tolist(),
            "predicted_mask_centroid_xy": predicted_center.tolist(),
            "predicted_center_offset_from_marker_xy": offset.tolist(),
            "target_mask_area_px": int(target_mask.sum()),
            "target_ellipse_proxy_covariance_px2": covariance.tolist(),
            "target_ellipse_proxy_contour_error": nearest_error(predicted_contour, target_contour),
            "leave_one_out": loo,
            "leave_one_out_centroid_error_summary_px": {
                "median": float(np.median([x["centroid_error_px"] for x in loo])),
                "p90": float(np.percentile([x["centroid_error_px"] for x in loo], 90)),
                "maximum": float(max(x["centroid_error_px"] for x in loo))},
            "leave_one_out_contour_error_summary_px": {
                "median_symmetric_mean": float(np.median([x["contour_error"]["symmetric_mean_px"] for x in loo if x["contour_error"]["symmetric_mean_px"] is not None])),
                "p90_symmetric_mean": float(np.percentile([x["contour_error"]["symmetric_mean_px"] for x in loo if x["contour_error"]["symmetric_mean_px"] is not None], 90))},
            "measurements": {str(i): {"mask_centroid_xy": measurements[i]["centroid"].tolist(),
                                      "marker_xy": rows[i]["marker_xy"],
                                      "offset_xy": offsets[i].tolist(), "area_px": measurements[i]["area"],
                                      "bbox_xyxy": measurements[i]["bbox"]} for i in refs},
            "status": "calibrated_against_provisional_masks_only"}


def plot_region(name: str, case: dict, rows: dict, labels: np.ndarray,
                rgb: np.ndarray, result: dict, path: Path) -> None:
    x0,y0,x1,y1 = case["crop"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), layout="constrained")
    for ax in axes:
        ax.imshow(rgb)
        ax.set_xlim(x0,x1); ax.set_ylim(y1,y0); ax.set_aspect("equal")
        ax.set_xlabel("image x (pixels)"); ax.set_ylabel("image y (pixels)")
    ax=axes[0]; ax.set_title(f"Region {name}: nearby same-color controls")
    for ident in result["reference_ids"]:
        m=labels==ident
        curve=boundary(m)
        if len(curve): ax.plot(curve[:,0],curve[:,1],color="lime",lw=.8)
        px,py=rows[ident]["marker_xy"];cx,cy=result["measurements"][str(ident)]["mask_centroid_xy"]
        ax.plot(px,py,"+",color="cyan",ms=6); ax.plot(cx,cy,".",color="yellow",ms=5)
        ax.text(px+1,py,str(ident),color="cyan",fontsize=7)
    tx,ty=result["target_marker_xy"];px,py=result["predicted_mask_centroid_xy"]
    ax.plot(tx,ty,"+",color="magenta",ms=10); ax.plot(px,py,"x",color="orange",ms=9)
    ax.text(tx+1,ty,str(name),color="magenta",fontsize=8)
    ax=axes[1]; ax.set_title("Target mask and transferred ellipse proxy")
    target=labels==int(name); curve=boundary(target)
    if len(curve): ax.plot(curve[:,0],curve[:,1],color="lime",lw=1.2,label="provisional target mask")
    center=np.asarray(result["predicted_mask_centroid_xy"])
    contour=ellipse_points(center,np.asarray(result["target_ellipse_proxy_covariance_px2"]),360)
    ax.plot(contour[:,0],contour[:,1],color="orange",lw=1.2,label="neighbor-calibrated proxy")
    ax.plot(*center,"x",color="orange"); ax.legend(fontsize=8)
    loo=result["leave_one_out_centroid_error_summary_px"]
    fig.suptitle(f"Leave-one-out mask-centroid error: median {loo['median']:.2f}px; p90 {loo['p90']:.2f}px; mask-only calibration",fontsize=12)
    fig.savefig(path,dpi=150); plt.close(fig)


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--labels",type=Path,default=ROOT/"photo2/output/beads3-final/labels.npy")
    ap.add_argument("--review-bundle",type=Path,required=True)
    args=ap.parse_args(); args.review_bundle.mkdir(parents=True,exist_ok=True)
    source_report=json.loads((R071/"report.json").read_text())
    for p,expected in [(ROOT/"beads3.jpg",source_report["sources"]["beads3.jpg"]),
                       (R071/"inventory.json",source_report["artifacts"]["inventory.json"]),
                       (args.labels,source_report["bulk_artifacts"]["labels.npy"])]:
        if bg.digest(p)!=expected: raise ValueError("Source binding mismatch: "+str(p))
    config=json.loads(CONFIG.read_text())
    all_rows=json.loads((R071/"inventory.json").read_text())
    rows={r["id"]:r for r in all_rows["active_observations"]+all_rows["excluded_observations"]}
    labels=np.load(args.labels); rgb=np.asarray(Image.open(ROOT/"beads3.jpg").convert("RGB"))
    results={}
    for name,case in config["cases"].items():
        result=fit_region(name,case,rows,labels); results[name]=result
        plot_region(name,case,rows,labels,rgb,result,args.review_bundle/f"{name}-calibration.png")
    bg.write_json(args.review_bundle/"calibration.json",{"parameters":PARAMETERS,"results":results,
        "limitations":["Labels and marker coordinates come from the provisional R071 image-only inventory.",
                        "A mask centroid is not a recovered physical center; color watershed boundaries can be clipped or shadow-contaminated.",
                        "Leave-one-out scores validate transfer among nearby masks only, not an underlying 3D bead shape or indexing model.",
                        "Warning targets are compared with their own uncertain masks for visualization only; they were excluded from training.",
                        "No missing-bead count, region split, bead index, POV-Ray source, or physical pattern was consulted or inferred."],
        "inventory_changed":False})
    paths=[Path(__file__).resolve(),CONFIG,R071/"inventory.json",R071/"report.json",ROOT/"beads3.jpg",ROOT/"photo2/requirements.txt",ROOT/"photo2/blind_generated.py",args.labels]
    report={"command":[str(Path(sys.argv[0])),*sys.argv[1:]],"parameters":PARAMETERS,
            "sources":{str(p.relative_to(ROOT)):bg.digest(p) for p in paths},
            "artifacts":{p.name:bg.digest(p) for p in sorted(args.review_bundle.iterdir()) if p.name!="report.json"},
            "inventory_changed":False}
    bg.write_json(args.review_bundle/"report.json",report)
    print(json.dumps({k:{"reference_ids":v["reference_ids"],"centroid_loo":v["leave_one_out_centroid_error_summary_px"],"contour_loo":v["leave_one_out_contour_error_summary_px"],"target_contour":v["target_ellipse_proxy_contour_error"]} for k,v in results.items()},indent=2))


if __name__=="__main__":
    main()

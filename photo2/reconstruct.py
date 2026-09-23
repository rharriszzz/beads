#!/usr/bin/env python3
"""Deterministic photo-2 forward model and explicitly provisional inverse analysis.

Coordinates are original image pixels (x right, y down), with z above the paper.
Only the POV export flips y. There is no physical length calibration in the photo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import scipy
from PIL import Image, ImageDraw
from scipy.interpolate import splprep, splev
from scipy.ndimage import gaussian_filter1d, map_coordinates
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NAMES = ["near-black", "red", "yellow-orange"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ClosedPath:
    """Periodic cubic spline evaluated by arc length, including the closing span."""

    def __init__(self, points):
        points = np.asarray(points, dtype=float)
        if points.ndim != 2 or points.shape[1] != 2 or len(points) < 4:
            raise ValueError("Need at least four 2D spline points")
        if not np.isfinite(points).all():
            raise ValueError("Nonfinite spline coordinates")
        if not np.allclose(points[0], points[-1]):
            points = np.vstack([points, points[0]])
        if np.any(np.linalg.norm(np.diff(points, axis=0), axis=1) < 1e-8):
            raise ValueError("Consecutive duplicate spline points")
        self.tck, _ = splprep(points.T, per=True, s=len(points) * 4)
        self.u = np.linspace(0, 1, 20001)
        xy = np.array(splev(self.u, self.tck)).T
        self.arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
        self.length = float(self.arc[-1])

    def evaluate(self, distance):
        u = np.interp(np.asarray(distance) % self.length, self.arc, self.u)
        xy = np.array(splev(u, self.tck)).T
        tangent = np.array(splev(u, self.tck, der=1)).T
        tangent /= np.linalg.norm(tangent, axis=-1, keepdims=True)
        normal = np.stack([-tangent[..., 1], tangent[..., 0]], axis=-1)
        return xy, tangent, normal


def sample_rgb(rgb, xy):
    return np.stack([map_coordinates(rgb[..., c].astype(float),
                     [xy[..., 1], xy[..., 0]], order=1, mode="nearest")
                     for c in range(3)], axis=-1)


def classify(rgb):
    """Photo-specific conservative color boxes; -1 means paper/highlight/uncertain.

    RGB inequalities preserve red/yellow separation without treating magenta
    shadows as black beads. These are starting thresholds, not a learned palette.
    """
    r, g, b = np.moveaxis(np.asarray(rgb, dtype=float) / 255, -1, 0)
    labels = np.full(r.shape, -1, dtype=int)
    labels[(np.maximum.reduce([r, g, b]) < .30)] = 0
    labels[(r > .28) & (r > g * 1.65) & (r > b * 1.65)] = 1
    labels[(r > .42) & (g > r * .40) & (g < r * .92) & (b < g * .55)] = 2
    return labels


def layout(path, settings, handedness=None):
    turns = int(np.floor(path.length / settings["turn_pitch_px"] + .5))
    count = int(np.floor(turns * settings["beads_per_turn"] + .5))
    index = np.arange(count)
    xy, tangent, normal = path.evaluate(index * path.length / count)
    hand = settings["handedness"] if handedness is None else handedness
    theta = hand * 2 * np.pi * turns * index / count + np.deg2rad(settings["phase_degrees"])
    radius = settings["rope_radius_px"]
    xy = xy + radius * np.sin(theta)[:, None] * normal
    # z clearance is conservative for the rounded bead profile in every rotation.
    z = radius + settings["bead_radius_px"] + radius * np.cos(theta)
    return xy, z, tangent, theta, turns


def observations(rgb, xy, theta, radius):
    # Five interior samples suppress single-pixel glints; edges/back are not evidence.
    samples = [classify(sample_rgb(rgb, xy + np.array(offset) * radius * .25))
               for offset in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]]
    votes = np.stack([(np.array(samples) == c).sum(axis=0) for c in range(3)], axis=1)
    labels = votes.argmax(axis=1)
    weights = votes.max(axis=1) / len(samples)
    visible = np.cos(theta) > .25
    weights[~visible | (weights < .6)] = 0
    labels[weights == 0] = -1
    return labels, weights


def period_candidates(labels, weights, minimum=200, maximum=400):
    """Rank by held-out contiguous arc blocks, preserving every hidden bead index.

    Numeric color IDs are categorical, never scalar autocorrelation amplitudes.
    Unknown residues stay -1. Block holdout prevents each bead voting for itself.
    Scores are conditional on geometry; they are not proof of a recovered repeat.
    """
    labels, weights = np.asarray(labels), np.asarray(weights)
    index = np.arange(len(labels))
    valid = (labels >= 0) & (weights > 0)
    if valid.sum() < 2:
        return []
    blocks = np.minimum(index * 5 // len(index), 4)
    candidates = []
    baseline = max(np.sum(weights[labels == c]) for c in range(3)) / weights[valid].sum()
    for period in range(minimum, min(maximum, len(labels) // 2) + 1):
        residue = index % period
        correct, evaluated, possible = 0., 0., float(weights[valid].sum())
        for fold in range(5):
            train = valid & (blocks != fold)
            test = valid & (blocks == fold)
            votes = np.zeros((period, 3))
            np.add.at(votes, (residue[train], labels[train]), weights[train])
            supported = votes.sum(axis=1) > 0
            test &= supported[residue]
            tied = np.isclose(votes, votes.max(axis=1, keepdims=True), rtol=0, atol=1e-12)
            # Average over tied winners so arbitrary palette numbering cannot
            # change scores (argmax would always favor the lowest color ID).
            credit = tied[residue[test], labels[test]] / tied[residue[test]].sum(axis=1)
            correct += np.sum(weights[test] * credit)
            evaluated += weights[test].sum()
        votes = np.zeros((period, 3))
        np.add.at(votes, (residue[valid], labels[valid]), weights[valid])
        support = votes.sum(axis=1)
        pattern = votes.argmax(axis=1)
        ambiguous = np.isclose(votes, votes.max(axis=1, keepdims=True), rtol=0, atol=1e-12).sum(axis=1) > 1
        pattern[(support == 0) | ambiguous] = -1
        confidence = votes.max(axis=1) / np.maximum(support, 1e-12)
        candidates.append({"period": period, "held_out_accuracy": float(correct / evaluated) if evaluated else 0.,
                           "held_out_coverage": float(evaluated / possible),
                           "majority_baseline": float(baseline),
                           "supported_fraction": float(np.mean(support > 0)),
                           "pattern": pattern.tolist(), "confidence": confidence.tolist(),
                           "support": support.tolist()})
    return sorted(candidates, key=lambda c: (-c["held_out_accuracy"] * c["held_out_coverage"], c["period"]))


def diagnostics(rgb, path, output):
    distances = np.arange(0, path.length, 2.)
    xy, _, normal = path.evaluate(distances)
    offsets = np.arange(-65, 66)
    strip = sample_rgb(rgb, xy[None] + offsets[:, None, None] * normal[None])
    Image.fromarray(np.uint8(np.clip(strip, 0, 255))).save(output / "unwrap.png")
    # Save five readable sections, keeping x measured in true arc length.
    sections = np.array_split(strip, 5, axis=1)
    canvas = Image.new("RGB", (max(s.shape[1] for s in sections), 5 * 153), "white")
    draw = ImageDraw.Draw(canvas)
    for i, section in enumerate(sections):
        canvas.paste(Image.fromarray(np.uint8(section)), (0, i * 153 + 20))
        draw.text((4, i * 153 + 3), f"Arc section {i + 1}/5; x = 2 source pixels per pixel; normal -65 to +65", fill="black")
    canvas.save(output / "unwrap-sections.png")
    overlay = Image.fromarray(rgb)
    draw = ImageDraw.Draw(overlay)
    draw.line([tuple(v) for v in xy] + [tuple(xy[0])], fill="cyan", width=3)
    draw.ellipse(tuple(np.r_[xy[0] - 12, xy[0] + 12]), fill="white")
    overlay.thumbnail((1000, 1253))
    overlay.save(output / "centerline-overlay.png")
    signal = strip[45:85].mean(axis=2)
    signal -= gaussian_filter1d(signal, 25, axis=1, mode="wrap")
    power = np.mean(abs(np.fft.rfft(signal, axis=1)) ** 2, axis=0)
    frequency = np.fft.rfftfreq(signal.shape[1], 2)
    peaks, _ = find_peaks(gaussian_filter1d(power, 3))
    peaks = peaks[(frequency[peaks] > 1 / 28) & (frequency[peaks] < 1 / 16)]
    peaks = peaks[np.argsort(power[peaks])[::-1]][:5]
    return {"longitudinal_texture_peak_px": (1 / frequency[peaks]).tolist(),
            "warning": "Texture peaks can be harmonics or color motifs, not necessarily the turn pitch."}


def vector(values):
    return "<" + ",".join(f"{v:.7f}" for v in values) + ">"


def write_scene(output, rgb, path, settings, colors):
    xy, z, tangent, theta, turns = layout(path, settings)
    h, w = rgb.shape[:2]
    lines = ["// Generated by photo2/reconstruct.py; coordinates in image pixels.",
             f"#declare PhotoWidth = {w};", f"#declare PhotoHeight = {h};",
             f"#declare bead_radius = {settings['bead_radius_px']};",
             "#declare hole_size_per_bead_size = 0.14;",
             f"#declare PhotoHeightRatio = {settings['bead_height_ratio']};",
             f"#declare PhotoPaper = {vector(settings['paper_srgb'])};",
             f"#declare PhotoLight = {vector(settings['light_position_px'])};"]
    for key, name in [("light_size_px", "PhotoLightSize"), ("light_strength", "PhotoLightStrength"),
                      ("fill_strength", "PhotoFill"), ("paper_bump", "PhotoPaperBump"),
                      ("material_specular", "PhotoSpecular"), ("material_roughness", "PhotoRoughness")]:
        lines.append(f"#declare {name} = {settings[key]};")
    lines.append("#declare PhotoPalette = array[3]{" + ",".join(map(vector, settings["palette_srgb"])) + "};")
    lines += [f"#declare PhotoCount = {len(xy)};", "#declare PhotoPositions = array[PhotoCount]{"]
    lines.append(",\n".join(vector([p[0] - w / 2, h / 2 - p[1], zz]) for p, zz in zip(xy, z)) + "};")
    # A bead's hole axis follows the rope tangent. Local y is the hole axis.
    angles = np.rad2deg(np.arctan2(-tangent[:, 0], -tangent[:, 1]))
    lines += ["#declare PhotoAngles = array[PhotoCount]{" + ",".join(f"{a:.6f}" for a in angles) + "};",
              "#declare PhotoColors = array[PhotoCount]{" + ",".join(map(str, colors)) + "};"]
    (output / "scene-data.inc").write_text("\n".join(lines) + "\n")
    return {"count": len(xy), "turns": turns, "exact_beads_per_turn": len(xy) / turns,
            "arc_length_px": path.length, "actual_pitch_px": path.length / turns,
            "minimum_center_height_px": float(z.min()), "all_finite": bool(np.isfinite(xy).all())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=ROOT / "beads-photo-2.jpg")
    parser.add_argument("--settings", type=Path, default=HERE / "settings.json")
    parser.add_argument("--output", type=Path, default=HERE / "output")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--period", type=int, help="Render this provisional repeat instead of observed colors")
    parser.add_argument("--handedness", type=int, choices=[-1, 1])
    args = parser.parse_args()
    settings = json.loads(args.settings.read_text())
    if args.handedness is not None:
        settings["handedness"] = args.handedness
    for key in ["beads_per_turn", "turn_pitch_px", "rope_radius_px", "bead_radius_px", "bead_height_ratio"]:
        if not np.isfinite(settings[key]) or settings[key] <= 0:
            parser.error(f"{key} must be finite and positive")
    if settings["handedness"] not in (-1, 1) or args.width < 32:
        parser.error("Invalid handedness or render width")
    if not 1 <= settings["min_period"] <= settings["max_period"]:
        parser.error("Invalid period range")
    source = json.loads((HERE / "centerline.json").read_text())
    if digest(args.image) != source["image_sha256"]:
        parser.error("Image does not match the source image for the saved spline")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rgb = np.array(Image.open(args.image).convert("RGB"))
    path = ClosedPath(source["points"])
    report = {"status": "provisional; repeat and helicity unresolved", "settings": settings,
              "image_sha256": digest(args.image), "centerline_sha256": digest(HERE / "centerline.json"),
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in
                                [Path(__file__), HERE / "scene.inc", ROOT / "beads.pov", ROOT / "bead-shape.inc"]},
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "spectral": diagnostics(rgb, path, output), "hypotheses": {}}
    selected = None
    for hand in [-1, 1]:
        xy, z, tangent, theta, turns = layout(path, settings, hand)
        labels, weights = observations(rgb, xy, theta, settings["bead_radius_px"])
        ranked = period_candidates(labels, weights, settings["min_period"], settings["max_period"])
        report["hypotheses"][str(hand)] = {"visible_classified": int((weights > 0).sum()), "top_candidates": ranked[:10]}
        if hand == settings["handedness"]:
            selected = labels, weights, ranked, xy
    labels, weights, ranked, xy = selected
    # Observation mode is a forward-model appearance check, not a recovered repeat.
    colors = labels.copy()
    if args.period is not None:
        all_candidates = period_candidates(labels, weights, settings["min_period"], settings["max_period"])
        candidate = next((c for c in all_candidates if c["period"] == args.period), None)
        if candidate is None:
            parser.error("Requested period lies outside the supported search range")
        colors = np.array(candidate["pattern"])[np.arange(len(labels)) % args.period]
    # For observation preview only, classify edge samples as well; hidden colors
    # remain arbitrary. None of these filled entries are used as inverse evidence.
    if args.period is None:
        edge_labels = classify(sample_rgb(rgb, xy))
        colors[colors < 0] = edge_labels[colors < 0]
    report["preview_unknown_filled_black"] = int((colors < 0).sum())
    colors[colors < 0] = 0
    report["render_color_mode"] = "photo samples (not a pattern)" if args.period is None else f"candidate repeat {args.period}"
    report["geometry"] = write_scene(output, rgb, path, settings, colors)
    np.savez_compressed(output / "observations.npz", index=np.arange(len(labels)), labels=labels, weights=weights, xy=xy)
    (output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"geometry": report["geometry"], "mode": report["render_color_mode"],
                      "top_periods": {h: [(c["period"], round(c["held_out_accuracy"], 3)) for c in v["top_candidates"][:3]]
                                      for h, v in report["hypotheses"].items()}}, indent=2), flush=True)
    if args.render:
        command = ["povray", "+Ibeads.pov", f"+O{output / 'render.png'}", f"+L{output}",
                   "Declare=Photo2=1", f"+W{args.width}", f"+H{round(args.width * rgb.shape[0] / rgb.shape[1])}",
                   "+FN", "-D", "+A0.2", "+AM2", "+R2", "+WT4"]
        (output / "render-command.json").write_text(json.dumps(command, indent=2) + "\n")
        with (output / "render.log").open("w") as log:
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        photo = Image.fromarray(rgb).resize((args.width, round(args.width * rgb.shape[0] / rgb.shape[1])))
        render = Image.open(output / "render.png").convert("RGB")
        comparison = Image.new("RGB", (args.width * 2, photo.height + 24), "white")
        comparison.paste(photo, (0, 24))
        comparison.paste(render, (args.width, 24))
        draw = ImageDraw.Draw(comparison)
        draw.text((8, 6), "Reference photograph", fill="black")
        draw.text((args.width + 8, 6), report["render_color_mode"] + "; geometry provisional", fill="black")
        comparison.save(output / "comparison.png")
        reference_mask = classify(np.array(photo)) >= 0
        rendered_mask = classify(np.array(render)) >= 0
        def iou(a, b):
            return float(np.sum(a & b) / max(1, np.sum(a | b)))
        report["render_check"] = {"foreground_color_mask_iou": iou(reference_mask, rendered_mask),
                                  "mirrored_mask_iou": iou(reference_mask, rendered_mask[:, ::-1]),
                                  "note": "Color-mask overlap is a coarse alignment check, not bead recovery accuracy."}
        (output / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

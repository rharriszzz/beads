#!/usr/bin/env python3
"""Plot the saved photo-2 centerline on its matching photograph, without refitting."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/centerline-view')
    args = parser.parse_args()
    source = ROOT/'photo2/centerline.json'
    photo = ROOT/'beads-photo-2.jpg'
    saved = json.loads(source.read_text())
    if digest(photo) != saved['image_sha256']:
        raise ValueError('Photograph does not match the saved centerline')
    points = [tuple(p) for p in saved['points']]
    if len(points) < 4 or points[0] != points[-1]:
        raise ValueError('Expected the saved closed centerline')
    with Image.open(photo) as image:
        original = image.convert('RGB')
    if list(original.size) != saved['image_size']:
        raise ValueError('Image dimensions do not match the saved coordinates')
    if any(len(p) != 2 or not all(math.isfinite(v) for v in p) or
           not (0 <= p[0] < original.width and 0 <= p[1] < original.height) for p in points):
        raise ValueError('Invalid centerline coordinates')
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    overlay = original.copy()
    draw = ImageDraw.Draw(overlay)
    draw.line(points, fill=(0, 0, 0), width=10, joint='curve')
    draw.line(points, fill=(0, 255, 255), width=6, joint='curve')
    overlay.save(output/'photo2-centerline.png')
    preview = overlay.copy()
    preview.thumbnail((1000, 1253), Image.Resampling.LANCZOS)
    preview.save(output/'photo2-centerline-preview.png')
    report = dict(command=[sys.executable, *sys.argv],
                  sources={str(p.relative_to(ROOT)): digest(p) for p in [Path(__file__).resolve(), source, photo]},
                  image_size=list(original.size), points=len(points),
                  rendering='Polyline through saved sample points in source pixels; no refit or new inference',
                  style=dict(line_rgb=[0,255,255],line_width_px=6,halo_rgb=[0,0,0],halo_width_px=10),
                  artifacts={name:digest(output/name) for name in ['photo2-centerline.png','photo2-centerline-preview.png']})
    (output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(output/'photo2-centerline.png')


if __name__ == '__main__':
    main()

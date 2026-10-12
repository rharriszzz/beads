"""Archive existing R263 production data and compare native pixels; no detection."""
import csv
import gzip
import json
import shutil
import tarfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

from .bounded_detect import ROOT, save, sha


def points(region):
    return {(x, y) for y, start, end in region['pixel_runs'] for x in range(start, end + 1)}


def main():
    work = ROOT / 'photo2/output/detection-r263-bounded'
    out = ROOT / 'photo2/review/r263/bounded'
    out.mkdir(exist_ok=True)
    data = json.loads((work / 'regions.json').read_text())
    for name in ('labels.npz', 'coordinates.csv', 'rank-size.csv', 'size-distribution.png', 'summary.json'):
        shutil.copy2(work / name, out / name)
        if name.endswith('.csv'):
            (out / name).write_text((out / name).read_text())
    with gzip.GzipFile(filename=str(out / 'regions.json.gz'), mode='wb', mtime=0) as f:
        f.write((work / 'regions.json').read_bytes())
    with tarfile.open(out / 'growth-traces.tar', 'w') as tar:
        for path in sorted((work / 'traces').glob('*.gz')):
            info = tar.gettarinfo(str(path), arcname='traces/' + path.name)
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ''
            with path.open('rb') as f:
                tar.addfile(info, f)
    save(out / 'overgrowth-candidates.json', [r for r in data['rejected'] if r['size_limited']])
    with gzip.open(out.parent / 'bounded-hue20/regions.json.gz', 'rt') as f:
        before = json.load(f)
    a = {r['id']: r for r in before['regions']}
    b = {r['id']: r for r in data['regions']}
    changes = []
    for key in sorted(a.keys() & b.keys()):
        pa, pb = points(a[key]), points(b[key])
        changes.append(dict(id=key, pixels20=len(pa), pixels10=len(pb),
                            centroid20=a[key]['centroid'], centroid10=b[key]['centroid'],
                            centroid_shift_px=float(np.linalg.norm(np.array(a[key]['centroid']) - b[key]['centroid'])),
                            added_pixels=len(pb-pa), removed_pixels=len(pa-pb)))
    save(out / 'hue20-to10.json', dict(before_generation=before['generation_id'],
         after_generation=data['generation_id'], added_ids=sorted(b.keys()-a.keys()),
         lost_ids=sorted(a.keys()-b.keys()), common_regions=changes))
    with gzip.open(ROOT / 'photo2/review/r260/regions.json.gz', 'rt') as f:
        r260 = json.load(f)
    old = {r['id']: r for r in r260['regions']}
    rgb = np.asarray(ImageOps.exif_transpose(Image.open(ROOT / 'beads-photo-2.jpg')).convert('RGB'))
    comparisons = []
    cases = [('pair-32240-32353', (450, 640, 515, 701))]
    for rid in ('R01307', 'R00956', 'R01284'):
        r = old[rid]
        x, y = map(round, r['centroid'])
        cases.append((rid, (x-40, y-40, x+41, y+41)))
        p = points(r)
        overlaps = []
        for nr in data['regions']:
            npix = points(nr)
            if p & npix:
                overlaps.append(dict(id=nr['id'], shared_pixels=len(p & npix), pixels=nr['pixel_count'],
                                     centroid=nr['centroid'], supported_coordinate=nr['location']))
        comparisons.append(dict(r260_id=rid, r260_pixels=len(p), r260_centroid=r['centroid'],
                                overlapping_supports=overlaps, correspondence='intersection only; no bead identity assignment'))
    save(out / 'r260-comparisons.json', comparisons)
    datasets = {'R260': r260, 'R263 hue20 cap870': before, 'R263 hue10 cap870': data}
    for name, (x0, y0, x1, y1) in cases:
        fig, axes = plt.subplots(1, 4, figsize=(14, 4))
        for ax in axes:
            ax.imshow(rgb[y0:y1, x0:x1], extent=(x0-.5, x1-.5, y1-.5, y0-.5), interpolation='nearest')
            ax.set_xlim(x0-.5, x1-.5)
            ax.set_ylim(y1-.5, y0-.5)
        axes[0].set_title('Original native pixels')
        native = {}
        for ax, (label, ds) in zip(axes[1:], datasets.items()):
            members = {}
            for r in ds['regions']:
                subset = {(x, y) for x, y in points(r) if x0 <= x < x1 and y0 <= y < y1}
                if not subset:
                    continue
                for xy in subset:
                    members.setdefault(xy, []).append(r['id'])
                for c in r['contours']:
                    curve = np.asarray(c)
                    ax.plot(curve[:, 0], curve[:, 1], color='cyan', lw=.8)
                ax.plot(*r['centroid'], '+', color='white', ms=5)
            native[label] = members
            ax.set_title(label)
        fig.tight_layout()
        fig.savefig(out / (name + '-native.png'), dpi=160)
        plt.close(fig)
        with (out / (name + '-native.csv')).open('w', newline='') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(['x', 'y', 'r', 'g', 'b', 'value_dn', *datasets])
            for y in range(y0, y1):
                for x in range(x0, x1):
                    writer.writerow([x, y, *map(int, rgb[y, x]), int(rgb[y, x].max()),
                                     *[';'.join(native[n].get((x, y), [])) for n in datasets]])
    save(out.parent / 'manifest.json', {str(p.relative_to(out.parent)): sha(p)
         for p in sorted(out.parent.rglob('*')) if p.is_file() and p.name != 'manifest.json'})
    print(json.dumps(dict(regions=len(b), added=len(b.keys()-a.keys()), lost=len(a.keys()-b.keys()), comparisons=comparisons), indent=2))


if __name__ == '__main__':
    main()

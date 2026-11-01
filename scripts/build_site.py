"""Build only the explicit publication allowlist; never inspect the research tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from beadwork.graph_paper import pattern_layout

DIST = ROOT / "dist/beads"
LIMIT = 20 * 1024 * 1024
START, END = "<!-- PATTERN_VIEWER -->", "<!-- /PATTERN_VIEWER -->"


def catalog():
    paths = json.loads((ROOT / "scripts/publication.json").read_text())
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate publication entry")
    for name in paths:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or any(p.startswith(".") for p in path.parts):
            raise ValueError(f"Unsafe publication path: {name}")
        source = ROOT / path
        if not source.is_file() or source.resolve() != source.absolute():
            raise ValueError(f"Missing or symlinked publication input: {name}")
    return paths


def provenance_check():
    manifest = json.loads((ROOT / "docs/photo2/provenance.json").read_text())
    for record in manifest['files']:
        if record['mode'] not in ['existing', 'verbatim']:
            continue
        path = ROOT / record['destination']
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f"Copied evidence changed: {path}")


def candidate_data():
    data = json.loads((ROOT / "docs/photo2/data/candidate.json").read_text())
    if len(data['candidate']) != 208:
        raise ValueError("Invalid candidate length")
    if set(data['candidate']) != set('RBY'):
        raise ValueError("Invalid candidate colors")
    for name, values in [('r344', (199, 2, 7, 1038, 1041)), ('r347', (201, 0, 7, 1040, 1040))]:
        epoch = data['epochs'][name]
        s = epoch['statuses']
        if tuple(s[k] for k in ['supported', 'conflicting', 'insufficient']) + (epoch['agreements'], epoch['observations']) != values:
            raise ValueError("Evidence epochs changed")
        if [e['position'] for e in epoch['entries']] != list(range(208)):
            raise ValueError("Invalid position order")
        for i, entry in enumerate(epoch['entries']):
            expected = data['candidate'][i] if entry['status'] == 'supported' else '?'
            if epoch['strict'][i] != expected:
                raise ValueError("Unknown mask disagrees with saved status")
    return data


def graph_svg(data):
    """Presentation from the maintained Python geometry; browser does no math."""
    paper = pattern_layout(data['epochs']['r347']['strict'], data['candidate'])
    lo, hi = paper['rows']
    minx = min(r['x'] for r in paper['points'])
    maxx = max(r['x'] for r in paper['points'])
    width, height = (maxx - minx) * 24 + 150, (hi - lo) * 32 + 110
    def xy(x, y):
        return (x - minx) * 24 + 40, (hi - y) * 32 + 55
    def line(points):
        return ' '.join(f'{x:g},{y:g}' for x, y in [xy(*p) for p in points])
    sides = paper['side_boundaries']
    outline = sides['left'] + sides['right'][::-1]
    block = paper['start_boundary'] + paper['end_boundary'][::-1]
    parts = [f'<svg id="graph-paper" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="group" aria-labelledby="paper-title paper-description">',
             '<title id="paper-title">208-position candidate on 6.5-bead graph paper</title>',
             '<desc id="paper-description">Mathematical y increases upward. Six and seven basic beads alternate, with seven continuation beads on each side. Teal START and purple END enclose exactly 208 canonical members. Gray question marks are strict unknowns. Display copies add no observations.</desc>',
             f'<rect width="{width}" height="{height}" fill="#eeeee7"/>',
             f'<defs><clipPath id="strip-clip"><polygon points="{line(outline)}"/></clipPath></defs>',
             f'<polygon points="{line(block)}" fill="#fff" clip-path="url(#strip-clip)"/>']
    for r in paper['points']:
        x, y = xy(r['x'], r['y'])
        code = data['epochs']['r347']['strict'][r['position']]
        color = {'R': '#ce3d49', 'Y': '#e0bb18', 'B': '#252d33', '?': '#e9edeb'}[code]
        title = f"Position {r['position']}, string k={r['k']}, {'unknown' if code == '?' else code}, {r['side']} display"
        keyboard = f' tabindex="0" role="button" aria-label="{escape(title, quote=True)}"' if r['in_chosen_interval'] else ''
        parts.extend([
            f'<g class="bead" data-position="{r["position"]}" data-k="{r["k"]}" data-side="{r["side"]}" data-row="{r["y"]}" data-chosen="{str(r["in_chosen_interval"]).lower()}" transform="translate({x:g} {y:g})"{keyboard}>',
            f'<title>{escape(title)}</title><ellipse rx="18" ry="14" fill="{color}" stroke="#788380" stroke-width=".6"/>',
            f'<text class="unknown" text-anchor="middle" y="5" font-size="14" fill="#243c3c" style="display:{"block" if code == "?" else "none"}">?</text>',
            f'<text class="position-label" text-anchor="middle" y="4" font-size="10" fill="{"#fff" if code == "B" else "#243c3c"}">{r["position"]}</text></g>',
        ])
    for name, path in sides.items():
        parts.append(f'<polyline data-boundary="{name}" points="{line(path)}" fill="none" stroke="#4e5956" stroke-width="1" vector-effect="non-scaling-stroke"/>')
    for name, key, color in [('START', 'start_boundary', '#17666b'), ('END', 'end_boundary', '#863f8f')]:
        path = paper[key]
        parts.append(f'<polyline data-boundary="{name}" points="{line(path)}" clip-path="url(#strip-clip)" fill="none" stroke="{color}" stroke-width="1.5" vector-effect="non-scaling-stroke"/>')
        x, y = xy(maxx + 1.4, path[-1][1])
        parts.append(f'<text x="{x:g}" y="{y+4:g}" fill="{color}" font-size="12">{name}</text>')
    parts.append('</svg>')
    return '\n'.join(parts)


def index_html():
    template = (ROOT / 'index.html').read_text()
    data = candidate_data()
    payload = json.dumps(data, separators=(',', ':')).replace('<', '\\u003c')
    svg = graph_svg(data) + f'\n<script type="application/json" id="pattern-data">{payload}</script>'
    prefix, rest = template.split(START)
    _, suffix = rest.split(END)
    return prefix + svg + suffix


def expected_files():
    files = {}
    for name in catalog():
        if name == 'index.html':
            files[name] = index_html().encode()
        elif name == 'simulated-beads.html':
            # Original file stays byte-exact in Git. The missing movie was never
            # tracked on master; publication routes that dead link to a notice.
            text = (ROOT / name).read_text().replace('href="beads.mp4"', 'href="legacy-movie.html"')
            files[name] = text.encode()
        else:
            files[name] = (ROOT / name).read_bytes()
    files['.nojekyll'] = b''
    return files


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def check_links(directory):
    for page in directory.rglob('*.html'):
        doc = Document(page.read_text())
        ids = [attrs['id'] for _, attrs in doc.elements if 'id' in attrs]
        if len(ids) != len(set(ids)):
            raise ValueError(f'Duplicate HTML IDs: {page}')
        for tag, attrs in doc.elements:
            for key in ['src', 'href']:
                url = attrs.get(key, '')
                parsed = urlsplit(url)
                if not url or parsed.scheme or parsed.netloc:
                    continue
                if parsed.path.startswith('/'):
                    raise ValueError(f'Base-path-unsafe local URL: {url}')
                target = page.parent / unquote(parsed.path) if parsed.path else page
                if not target.is_file():
                    raise ValueError(f'Missing local target: {page.name}: {url}')
                if parsed.fragment and target.suffix == '.html':
                    target_ids = [a.get('id') for _, a in Document(target.read_text()).elements]
                    if unquote(parsed.fragment) not in target_ids:
                        raise ValueError(f'Missing anchor: {url}')
            if page.name == 'index.html' and tag == 'img':
                if not attrs.get('alt') or not attrs.get('width') or not attrs.get('height'):
                    raise ValueError('Missing image accessibility/dimensions')


def check(directory=DIST):
    provenance_check()
    expected = expected_files()
    if any(p.is_symlink() for p in directory.rglob('*')):
        raise ValueError('Symlink in publication output')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    if actual != set(expected):
        raise ValueError(f'Publication inventory differs: {actual ^ set(expected)}')
    for name, content in expected.items():
        path = directory / name
        if path.is_symlink() or path.read_bytes() != content:
            raise ValueError(f'Stale or unsafe output: {name}')
    total = sum(len(b) for b in expected.values())
    if total > LIMIT:
        raise ValueError(f'Publication exceeds {LIMIT} byte budget')
    check_links(directory)
    return len(expected), total


def build(directory=DIST):
    provenance_check()
    expected = expected_files()
    # Only the owned output folder may be replaced. Never clean the checkout.
    directory = Path(directory)
    if directory.is_symlink() or directory.resolve() in [ROOT, ROOT.parent]:
        raise ValueError('Unsafe build destination')
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    for name, content in expected.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return check(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check existing output without modifying it')
    args = parser.parse_args()
    count, size = check() if args.check else build()
    print(f'PASS {count} allowlisted files, {size:,} bytes ({size/1024/1024:.2f} MiB)')


if __name__ == '__main__':
    main()

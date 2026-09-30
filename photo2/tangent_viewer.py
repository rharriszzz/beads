"""Local count/helicity slider with full-photo zoom, pan and saved choices."""
from __future__ import annotations

import argparse
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timezone
import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs, urlsplit

import numpy as np
from PIL import Image, ImageOps
from tangent_circles import ROOT, load_model, visible_anchors, sha
from label_beads import atomic_json, open_browser

ASSETS = Path(__file__).with_name('tangent_viewer')
COUNT_LIMITS = (100, 10000)
DEFAULT_PORT = 8766


def validate_selection(count, hand):
    if type(count) is not int or not COUNT_LIMITS[0] <= count <= COUNT_LIMITS[1]:
        raise ValueError(f'Count must be a whole number between {COUNT_LIMITS[0]} and {COUNT_LIMITS[1]}.')
    if type(hand) is not int or hand not in [-1, 1]:
        raise ValueError('Helicity must be +1 or -1.')
    return count, hand


def validate_view(value):
    if not isinstance(value, dict):
        raise ValueError('A saved view needs x, y and scale.')
    clean = {}
    for key in ['x', 'y', 'scale']:
        v = value.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v):
            raise ValueError('Saved view coordinates must be finite numbers.')
        clean[key] = float(v)
    if not .025 <= clean['scale'] <= 32 or max(abs(clean['x']), abs(clean['y'])) > 1e6:
        raise ValueError('Saved view is outside the supported zoom/pan range.')
    return clean


class ViewerStore:
    def __init__(self, save_path, min_count=2000, max_count=3600, count=None, hand=None):
        validate_selection(min_count, 1); validate_selection(max_count, 1)
        if min_count >= max_count:
            raise ValueError('Minimum count must be smaller than maximum count.')
        self.path = Path(save_path).resolve()
        self.lock = threading.Lock()
        self.cache = OrderedDict()
        self.seeds = {h: json.loads((ROOT / f"photo2/review/r179/{'plus' if h > 0 else 'minus'}-2698/parameters.json").read_text())
                      for h in [1, -1]}
        self.source = dict(filename='beads-photo-2.jpg', sha256=sha(ROOT / 'beads-photo-2.jpg'),
                           oriented_size=[2540, 3182])
        if self.path in [ROOT / 'beads-photo-2.jpg', ROOT / 'beads.pov'] or self.path.suffix != '.json':
            raise ValueError('Use a separate .json file to save the viewer choice.')
        with Image.open(ROOT / 'beads-photo-2.jpg') as im:
            oriented = ImageOps.exif_transpose(im).convert('RGB')
            assert list(oriented.size) == self.source['oriented_size']
            buffer = BytesIO(); oriented.save(buffer, format='PNG'); self.png = buffer.getvalue()
        saved = self.read_choice()
        self.initial_count = count if count is not None else saved['parameters']['nbeads'] if saved else 2698
        self.initial_hand = hand if hand is not None else saved['parameters']['hand'] if saved else -1
        validate_selection(self.initial_count, self.initial_hand)
        self.minimum = min(min_count, self.initial_count)
        self.maximum = max(max_count, self.initial_count)
        self.initial_view = saved.get('viewer_choice', {}).get('view') if saved else None

    def read_choice(self):
        if not self.path.exists():
            return None
        doc = json.loads(self.path.read_text())
        choice = doc.get('viewer_choice', {}) if isinstance(doc, dict) else {}
        if choice.get('schema_version') != 1 or choice.get('source') != self.source:
            raise ValueError('The save file is not this viewer\'s choice for this photo; use another --save path.')
        validate_selection(doc['parameters']['nbeads'], doc['parameters']['hand'])
        if choice.get('view') is not None:
            validate_view(choice['view'])
        return doc

    def configuration(self, count, hand):
        validate_selection(count, hand)
        config = deepcopy(self.seeds[hand])
        config['parameters']['nbeads'] = count
        return config

    def frame(self, count, hand):
        validate_selection(count, hand)
        key = count, hand
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            started = time.perf_counter()
            config = self.configuration(count, hand)
            model = load_model(config, config['parameters'])
            g = model.geometry(np.arange(count)); visibility = visible_anchors(model, g)
            keep = visibility['exposed']
            center = visibility['xy'][keep]
            right, down, _ = model.view.basis()
            a = g['tangent'][keep] * config['circle_radius']
            b = np.cross(g['radial'][keep], g['tangent'][keep]) * config['circle_radius']
            # Each projected circle is exactly center + a*cos(t) + b*sin(t).
            axes_a = np.column_stack((a @ right, a @ down)) * model.view.scale
            axes_b = np.column_stack((b @ right, b @ down)) * model.view.scale
            result = dict(count=count, hand=hand, circles=np.column_stack((center, axes_a, axes_b)).tolist(),
                visible_anchors=int(keep.sum()), excluded_anchors=int((~keep).sum()),
                unfinished_rays=int(np.sum(visibility['unfinished_pairs_per_ray'] > 0)),
                parameters=config, nrows=model.source.nrows, scale_pixels_per_unit=model.view.scale,
                calculation_ms=round(1000*(time.perf_counter()-started), 1))
            self.cache[key] = result
            while len(self.cache) > 12:
                self.cache.popitem(last=False)
            return result

    def config(self):
        return dict(source=self.source, image_url='/image.png', initial_count=self.initial_count,
            initial_hand=self.initial_hand, initial_view=self.initial_view,
            min_count=self.minimum, max_count=self.maximum, allowed_range=COUNT_LIMITS,
            save_path=str(self.path), starting_patch=[1210, 210, 1450, 365])

    def save(self, payload):
        if not isinstance(payload, dict):
            raise ValueError('A choice must include count and helicity.')
        count, hand = validate_selection(payload.get('count'), payload.get('hand'))
        view = validate_view(payload.get('view'))
        doc = self.configuration(count, hand)
        doc['viewer_choice'] = dict(schema_version=1, source=self.source, view=view,
            saved_at=datetime.now(timezone.utc).isoformat(),
            source_sha256={str(p.relative_to(ROOT)): sha(p) for p in [
                Path(__file__), ROOT/'beads.pov', ROOT/'photo2/tangent_circles.py',
                ROOT/'photo2/bead_placement.py', ROOT/'photo2/curved_surface_fit.py',
                ROOT/'photo2/local_surface_fit.py', ROOT/'photo2/spline-seed-r175.json',
                ASSETS/'app.mjs', ASSETS/'viewport.mjs', ASSETS/'index.html', ASSETS/'style.css']},
            status='User-selected diagnostic model parameters; no recovered N or helicity is implied.')
        with self.lock:
            previous = self.read_choice()
            if previous is not None:
                atomic_json(self.path.with_name(self.path.stem + '.previous.json'), previous)
            atomic_json(self.path, doc)
        return dict(path=str(self.path), document=doc)


def make_server(store, port=DEFAULT_PORT):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, code, body, content_type='application/json; charset=utf-8'):
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def json_response(self, code, value):
            self.respond(code, json.dumps(value, allow_nan=False).encode())

        def do_GET(self):
            url = urlsplit(self.path)
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.mjs': ('app.mjs', 'text/javascript; charset=utf-8'),
                      '/viewport.mjs': ('viewport.mjs', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            try:
                if url.path in assets:
                    filename, kind = assets[url.path]
                    self.respond(200, (ASSETS / filename).read_bytes(), kind)
                elif url.path == '/image.png':
                    self.respond(200, store.png, 'image/png')
                elif url.path == '/api/config':
                    self.json_response(200, store.config())
                elif url.path == '/api/frame':
                    query = parse_qs(url.query)
                    if set(query) != {'count', 'hand'} or any(len(v) != 1 for v in query.values()):
                        raise ValueError('Specify one count and one helicity.')
                    self.json_response(200, store.frame(int(query['count'][0]), int(query['hand'][0])))
                else:
                    self.json_response(404, dict(error='Not found.'))
            except (ValueError, KeyError) as exc:
                self.json_response(400, dict(error=str(exc)))
            except Exception as exc:
                self.json_response(500, dict(error=f'Could not calculate this view: {exc}'))

        def do_POST(self):
            if urlsplit(self.path).path != '/api/choice':
                self.json_response(404, dict(error='Not found.')); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 10000:
                    raise ValueError('Invalid choice size.')
                result = store.save(json.loads(self.rfile.read(length)))
                self.json_response(200, result)
            except (ValueError, KeyError, TypeError) as exc:
                self.json_response(400, dict(error=str(exc)))
            except OSError as exc:
                self.json_response(500, dict(error=f'Could not save: {exc}'))

        def log_message(self, *_):
            pass

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, help='Initial bead count (default: saved choice or 2698)')
    parser.add_argument('--hand', type=int, choices=[-1, 1], help='Initial helicity (default: saved choice or -1)')
    parser.add_argument('--min-count', type=int, default=2000)
    parser.add_argument('--max-count', type=int, default=3600)
    parser.add_argument('--save', type=Path, default=ROOT / 'photo2/output/tangent-viewer/choice.json')
    parser.add_argument('--port', type=int, help='Default 8766, automatic fallback when busy; 0 selects a free port')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if args.port is not None and not 0 <= args.port <= 65535:
        parser.error('--port must be between 0 and 65535.')
    try:
        store = ViewerStore(args.save, args.min_count, args.max_count, args.count, args.hand)
        try:
            server = make_server(store, DEFAULT_PORT if args.port is None else args.port)
        except OSError as exc:
            if args.port is not None or exc.errno != errno.EADDRINUSE:
                raise
            server = make_server(store, 0)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Tangent-circle viewer: {url}\nSave choice: {store.path}\nCtrl+C stops the server.', flush=True)
    try:
        if not args.no_browser and not open_browser(url):
            print(f'Open this URL in your browser: {url}', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

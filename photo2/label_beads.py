"""Show a raw bead-photo crop and save manual point annotations locally."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import errno
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import urlsplit
import webbrowser

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).with_name('labeler')
DEFAULT_IMAGE = ROOT / 'beads-photo-2.jpg'
DEFAULT_CROP = (1180, 130, 1540, 520)
DEFAULT_PORT = 8765
DIRECTIONS = {
    'd1': 'plus or minus 1 direction',
    'd2': 'up to down while proceeding clockwise around the bracelet (according to the major diameter of the torus)',
    'd3': 'down to up while proceeding clockwise; equivalently up to down counterclockwise',
}


class AnnotationError(ValueError):
    pass


class SaveConflict(AnnotationError):
    pass


def validate_annotations(value, size):
    if not isinstance(value, list) or len(value) > 10000:
        raise AnnotationError('Annotations must be a list of at most 10,000 markers.')
    clean = []
    ids = set()
    numbers = set()
    for item in value:
        if not isinstance(item, dict):
            raise AnnotationError('Each marker must be an object.')
        marker_id = item.get('id')
        if not isinstance(marker_id, str) or not marker_id or len(marker_id) > 128 or marker_id in ids:
            raise AnnotationError('Each marker needs a unique, nonempty ID.')
        ids.add(marker_id)
        number = item.get('number')
        if type(number) is not int or abs(number) > 9007199254740991 or number in numbers:
            raise AnnotationError('Each bead needs a unique integer number within JavaScript safe limits.')
        numbers.add(number)
        point = {}
        for axis, upper in zip(('x', 'y'), size):
            v = item.get(axis)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v < upper or not math.isfinite(v):
                raise AnnotationError('Marker positions must lie within the oriented source image.')
            point[axis] = float(v)
        for axis, default in [('label_dx', 6), ('label_dy', -6)]:
            v = item.get(axis, default)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or abs(v) > 10000 or not math.isfinite(v):
                raise AnnotationError('Label offsets must be finite image-pixel distances.')
            point[axis] = float(v)
        clean.append(dict(id=marker_id, number=number, **point))
    return clean


def validate_series(value, annotations):
    if not isinstance(value, list) or len(value) > 10000:
        raise AnnotationError('Series must be a list of at most 10,000 entries.')
    marker_ids = {a['id'] for a in annotations}
    clean, ids, active = [], set(), 0
    for item in value:
        if not isinstance(item, dict):
            raise AnnotationError('Each series must be an object.')
        sid = item.get('id')
        if not isinstance(sid, str) or not sid or len(sid) > 128 or sid in ids:
            raise AnnotationError('Each series needs a unique, nonempty ID.')
        ids.add(sid)
        direction, state, members = item.get('direction'), item.get('status'), item.get('bead_ids')
        if not isinstance(direction, str) or direction not in DIRECTIONS or state not in ('active', 'complete'):
            raise AnnotationError('Series need a d1/d2/d3 direction and active/complete status.')
        if not isinstance(members, list) or len(members) > 10000 or any(
                not isinstance(mid, str) or mid not in marker_ids for mid in members):
            raise AnnotationError('Series must reference existing bead IDs in click order.')
        if any(a == b for a, b in zip(members, members[1:])):
            raise AnnotationError('Consecutive series entries must be different beads.')
        if state == 'complete' and len(members) < 2:
            raise AnnotationError('End a series after selecting at least two beads.')
        active += state == 'active'
        clean.append(dict(id=sid, direction=direction, status=state, bead_ids=list(members)))
    if active > 1:
        raise AnnotationError('Only one series may be active at a time.')
    return clean


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', suffix='.tmp', delete=False) as f:
            name = f.name
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        name = None
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


class LabelStore:
    def __init__(self, image_path, crop, annotations_path):
        self.image_path = Path(image_path).resolve()
        self.path = Path(annotations_path).resolve()
        self.lock = threading.Lock()
        if self.path == self.image_path or self.path.with_name(self.path.stem + '.previous.json') == self.image_path:
            raise AnnotationError('Annotation and backup files must differ from the source image.')
        with Image.open(self.image_path) as im:
            oriented = ImageOps.exif_transpose(im).convert('RGB')
            self.size = oriented.size
            self.crop = tuple(crop) if crop is not None else (0, 0, *self.size)
            x0, y0, x1, y1 = self.crop
            if not (0 <= x0 < x1 <= self.size[0] and 0 <= y0 < y1 <= self.size[1]):
                raise AnnotationError('Crop must be within the EXIF-oriented source image.')
            buf = BytesIO()
            oriented.crop(self.crop).save(buf, format='PNG')
            self.png = buf.getvalue()
        self.source = dict(filename=self.image_path.name,
                           sha256=hashlib.sha256(self.image_path.read_bytes()).hexdigest(),
                           oriented_size=list(self.size), coordinates='source pixels after EXIF orientation; x right, y down')
        # Validate existing work before starting; never replace a mismatched file.
        self._read()

    def _read(self):
        if not self.path.exists():
            return dict(schema_version=2, source=self.source, revision=0, annotations=[], series=[])
        try:
            doc = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise AnnotationError(f'Cannot read saved annotations: {exc}') from exc
        if not isinstance(doc, dict) or doc.get('schema_version') != 2:
            raise AnnotationError('Saved annotations use an unsupported format.')
        source = doc.get('source', {})
        if not isinstance(source, dict) or any(source.get(k) != self.source[k] for k in ('sha256', 'oriented_size', 'coordinates')):
            raise AnnotationError('Saved annotations belong to a different source image. Choose another --annotations file.')
        revision = doc.get('revision')
        if type(revision) is not int or revision < 0:
            raise AnnotationError('Saved annotations have an invalid revision.')
        doc['annotations'] = validate_annotations(doc.get('annotations'), self.size)
        doc['series'] = validate_series(doc.get('series', []), doc['annotations'])
        return doc

    def read(self):
        with self.lock:
            return self._read()

    def save(self, payload):
        if not isinstance(payload, dict) or type(payload.get('revision')) is not int:
            raise AnnotationError('A save requires its current revision.')
        annotations = validate_annotations(payload.get('annotations'), self.size)
        series = validate_series(payload.get('series', []), annotations)
        with self.lock:
            previous = self._read()
            if payload['revision'] != previous['revision']:
                raise SaveConflict('Another copy saved changes. Download your draft before reloading.')
            now = datetime.now(timezone.utc).isoformat()
            doc = dict(schema_version=2, source=self.source, view_crop=list(self.crop),
                       revision=previous['revision'] + 1, annotation_kind='manual numbered bead locations and ordered direction series',
                       created_at=previous.get('created_at', now), updated_at=now, annotations=annotations, series=series,
                       direction_definitions=DIRECTIONS)
            if previous.get('automatic_proposals') is True:
                # Editing one proposal does not confirm the remaining inventory.
                # Preserve the origin and uncertainty across subsequent saves.
                doc['automatic_proposals'] = True
                doc['automatic_origin'] = previous.get('automatic_origin', {})
                doc['annotation_kind'] = 'automatic bead/adjacency proposals with manual edits; confirmation is not implied'
            if self.path.exists():
                atomic_json(self.path.with_name(self.path.stem + '.previous.json'), previous)
            atomic_json(self.path, doc)
            return doc

    def config(self):
        return dict(source=self.source, crop=list(self.crop), image_url='/image.png',
                    annotations_path=str(self.path), directions=DIRECTIONS, document=self.read())


def make_server(store, host='127.0.0.1', port=8765):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, body, content_type='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def json_response(self, status, value):
            self.respond(status, json.dumps(value, ensure_ascii=False, allow_nan=False).encode())

        def do_GET(self):
            path = urlsplit(self.path).path
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.mjs': ('app.mjs', 'text/javascript; charset=utf-8'),
                      '/model.mjs': ('model.mjs', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if path in assets:
                name, mime = assets[path]
                self.respond(200, (ASSETS / name).read_bytes(), mime)
            elif path == '/image.png':
                self.respond(200, store.png, 'image/png')
            elif path in ('/api/config', '/api/annotations'):
                try:
                    self.json_response(200, store.config() if path == '/api/config' else store.read())
                except AnnotationError as exc:
                    self.json_response(409, dict(error=str(exc)))
            else:
                self.json_response(404, dict(error='Not found.'))

        def do_POST(self):
            if urlsplit(self.path).path != '/api/annotations':
                self.json_response(404, dict(error='Not found.'))
                return
            origin = self.headers.get('Origin')
            if origin and urlsplit(origin).netloc != self.headers.get('Host'):
                self.json_response(403, dict(error='Save from the labeler window.'))
                return
            if self.headers.get_content_type() != 'application/json':
                self.json_response(415, dict(error='Send JSON annotations.'))
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 2_000_000:
                    self.json_response(413, dict(error='Save size is invalid or too large.'))
                    return
                payload = json.loads(self.rfile.read(length))
                self.json_response(200, store.save(payload))
            except SaveConflict as exc:
                self.json_response(409, dict(error=str(exc)))
            except (AnnotationError, ValueError) as exc:
                self.json_response(400, dict(error=str(exc)))
            except OSError as exc:
                self.json_response(500, dict(error=f'Could not save: {exc}'))

        def log_message(self, format, *args):
            if len(args) > 1 and str(args[1]).startswith(('4', '5')):
                super().log_message(format, *args)

    return ThreadingHTTPServer((host, port), Handler)


def start_server(store, port=None):
    """Honor explicit ports; let the OS find a free port if the default is busy."""
    try:
        return make_server(store, port=DEFAULT_PORT if port is None else port)
    except OSError as exc:
        if port is not None or exc.errno != errno.EADDRINUSE:
            raise
        return make_server(store, port=0)


def open_browser(url):
    """Use Windows' default browser on WSL, avoiding headless xdg-open noise."""
    if sys.platform.startswith('linux'):
        if 'microsoft' in platform.release().lower():
            launcher = shutil.which('wslview')
            powershell = shutil.which('powershell.exe')
            commands = []
            if launcher:
                commands.append([launcher, url])
            if powershell:
                commands.append([powershell, '-NoProfile', '-NonInteractive',
                                 '-Command', 'Start-Process', url])
            for command in commands:
                try:
                    result = subprocess.run(command, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL, timeout=5, check=False)
                    if result.returncode == 0:
                        return True
                except (OSError, subprocess.TimeoutExpired):
                    continue
            return False
        browsers = ('firefox', 'chromium', 'chromium-browser', 'google-chrome',
                    'google-chrome-stable', 'brave-browser', 'microsoft-edge')
        if not os.environ.get('BROWSER') and not any(shutil.which(name) for name in browsers):
            return False
    try:
        return webbrowser.open(url)
    except (OSError, webbrowser.Error):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=DEFAULT_IMAGE)
    parser.add_argument('--crop', nargs=4, type=int, metavar=('X0', 'Y0', 'X1', 'Y1'))
    parser.add_argument('--full-image', action='store_true')
    parser.add_argument('--annotations', type=Path, default=ROOT / 'photo2/output/labeler/annotations.json')
    parser.add_argument('--port', type=int, help='Listen on this port; 0 chooses a free port. Default: 8765, with automatic fallback if busy.')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if args.port is not None and not 0 <= args.port <= 65535:
        parser.error('Port must be between 0 and 65535.')
    if args.full_image and args.crop:
        parser.error('Choose --full-image or --crop.')
    crop = args.crop
    if crop is None and not args.full_image and args.image.resolve() == DEFAULT_IMAGE.resolve():
        crop = DEFAULT_CROP
    try:
        store = LabelStore(args.image, crop, args.annotations)
        if store.path == store.image_path:
            parser.error('The annotations file must differ from the source image.')
        server = start_server(store, port=args.port)
    except (AnnotationError, OSError) as exc:
        if isinstance(exc, OSError) and exc.errno == errno.EADDRINUSE:
            parser.error(f'Port {args.port} is already in use. Choose another --port or use --port 0.')
        parser.error(str(exc))
    url = f'http://127.0.0.1:{server.server_port}/'
    if args.port is None and server.server_port != DEFAULT_PORT:
        print(f'Port {DEFAULT_PORT} is busy; using an available port instead.', flush=True)
    print(f'Bead labeler: {url}\nAnnotations: {store.path}\nCtrl+C stops the server.', flush=True)
    try:
        if not args.no_browser and not open_browser(url):
            print(f'Open this URL in your browser manually: {url}', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

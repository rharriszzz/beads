"""Launch the simple, read-only photographic region viewer."""
from __future__ import annotations
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .pixel_detect import ROOT, generate, sha

STATIC=Path(__file__).parent/'static'


def prepare(work, image, regenerate=False):
    path=work/'regions.json'
    stale=not path.exists()
    if not stale:
        data=json.loads(path.read_text())
        stale=data.get('image_sha256')!=sha(image) or data.get('detector_sha256')!=sha(Path(__file__).parent/'pixel_detect.py')
        stale |= not (work/'photo.png').exists()
    if stale or regenerate:generate(image,work)


def make_server(work, host='127.0.0.1', port=8767):
    work=Path(work).resolve()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path=urlsplit(self.path).path
            files={'/':STATIC/'index.html','/app.js':STATIC/'app.js','/style.css':STATIC/'style.css',
                   '/regions.json':work/'regions.json','/photo.png':work/'photo.png',
                   '/size-distribution.png':work/'size-distribution.png','/rank-size.csv':work/'rank-size.csv',
                   '/coordinates.csv':work/'coordinates.csv'}
            file=files.get(path)
            import re
            if re.fullmatch(r'/traces/P[0-9]{6}\.json',path):
                import gzip
                packed=work/'traces'/(Path(path).name+'.gz')
                if not packed.is_file():self.send_error(404);return
                with gzip.open(packed,'rb') as f:body=f.read()
                self.send_response(200);self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
            if file is None or not file.is_file():self.send_error(404);return
            self.send_response(200)
            self.send_header('Content-Type',self.guess_type(str(file)))
            self.send_header('Content-Length',str(file.stat().st_size))
            self.send_header('Cache-Control','no-cache')
            self.end_headers()
            with file.open('rb') as source:
                import shutil
                shutil.copyfileobj(source,self.wfile)
        def log_message(self,*args):pass
    return ThreadingHTTPServer((host,port),Handler)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port',type=int,default=8767)
    ap.add_argument('--work',type=Path,default=ROOT/'photo2/output/detection-r261')
    ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    ap.add_argument('--regenerate',action='store_true')
    args=ap.parse_args();prepare(args.work,args.image,args.regenerate)
    server=make_server(args.work,port=args.port)
    print(f'Automatic region viewer: http://localhost:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':main()

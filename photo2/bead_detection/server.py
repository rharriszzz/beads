"""Launch the simple, read-only photographic region viewer."""
from __future__ import annotations
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .repaired_detect import ROOT, generate, sha

STATIC=Path(__file__).parent/'static'


def prepare(work, image, regenerate=False):
    path=work/'regions.json'
    stale=not path.exists()
    generator=generate;parameters=None
    if not stale:
        data=json.loads(path.read_text())
        detector=Path(__file__).parent/'repaired_detect.py'
        if data.get('version','').startswith('r263-tunable'):
            from .tunable_detect import generate as tuned_generate, Parameters
            detector=Path(__file__).parent/'tunable_detect.py'
            generator=tuned_generate;parameters=Parameters(**data['parameters'])
        elif data.get('version','').startswith('r262-'):
            from .monotone_detect import generate as old_generate, Parameters
            detector=Path(__file__).parent/'monotone_detect.py'
            generator=old_generate;parameters=Parameters(**data['parameters'])
        elif data.get('version','').startswith('r261-'):
            from .pixel_detect import generate as pixel_generate, Parameters
            detector=Path(__file__).parent/'pixel_detect.py'
            generator=pixel_generate;parameters=Parameters(**data['parameters'])
        elif data.get('version')=='r265-straight-native-v1':
            from .straight_detect_r265 import Parameters, generate as straight_generate
            detector=Path(__file__).parent/'straight_detect_r265.py'
            generator=straight_generate;parameters=Parameters(**data['parameters'])
        elif data.get('version','').startswith('r265-'):
            from .repaired_detect import Parameters
            parameters=Parameters(**data['parameters'])
        elif data.get('version','').startswith('r263-bounded'):
            from .bounded_detect import Parameters, generate as bounded_generate
            detector=Path(__file__).parent/'bounded_detect.py'
            generator=bounded_generate
            parameters=Parameters(**data['parameters'])
        else:
            raise ValueError('Unknown detector version; use its archived viewer instead of regenerating it here')
        stale=data.get('image_sha256')!=sha(image) or data.get('detector_sha256')!=sha(detector)
        stale |= not (work/'photo.png').exists()
    if stale or regenerate:
        if parameters is None:generator(image,work)
        else:generator(image,work,parameters)


def make_server(work, host='127.0.0.1', port=8767):
    work=Path(work).resolve()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path=urlsplit(self.path).path
            import re
            import gzip
            review=ROOT/'photo2/review/r264'
            if path=='/hue-comparison':path='/hue.html'
            files={'/':STATIC/'index.html','/app.js':STATIC/'app.js','/style.css':STATIC/'style.css',
                   '/hue.html':STATIC/'hue.html','/hue.js':STATIC/'hue.js',
                   '/hue-comparison.json':review/'comparison.json',
                   '/r264-hsv.png':review/'hsv-routes.png',
                   '/r264-review.png':review/'visual-review.png',
                   '/r264-leaf.png':review/'leaf-coordinate-control.png',
                   '/regions.json':work/'regions.json','/photo.png':work/'photo.png',
                   '/size-distribution.png':work/'size-distribution.png','/rank-size.csv':work/'rank-size.csv',
                   '/coordinates.csv':work/'coordinates.csv'}
            file=files.get(path)
            match=re.fullmatch(r'/hue-data/(5|8|10|12|15|20)/(regions.json|coordinates.csv|traces/P[0-9]{6}\.json)',path)
            if match:
                hue,name=match.groups()
                if not (review/hue/'regions.json.gz').is_file():self.send_error(404);return
                if name=='regions.json':
                    with gzip.open(review/hue/'regions.json.gz','rb') as f:body=f.read()
                elif name=='coordinates.csv':body=(review/hue/name).read_bytes()
                else:
                    import tarfile
                    with tarfile.open(review/hue/'traces.tar') as tar:
                        try:
                            with tar.extractfile(name+'.gz') as f:body=gzip.decompress(f.read())
                        except KeyError:self.send_error(404);return
                self.send_response(200);self.send_header('Content-Type','text/csv' if name.endswith('.csv') else 'application/json')
                self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
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
    ap.add_argument('--work',type=Path,default=ROOT/'photo2/output/r265-first-dark/joint')
    ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    ap.add_argument('--regenerate',action='store_true')
    args=ap.parse_args();prepare(args.work,args.image,args.regenerate)
    server=make_server(args.work,port=args.port)
    print(f'Automatic region viewer: http://localhost:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


if __name__=='__main__':main()

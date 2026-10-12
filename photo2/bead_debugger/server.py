"""Local-only, buildless reconstruction debugger. Run with --help."""
from __future__ import annotations
import argparse, io, json, mimetypes, sys, threading, zipfile
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from PIL import Image,ImageOps
import numpy as np
from .generate import ROOT,generate,sha
from . import registry as models
from .store import ReviewStore, Conflict
from .detail import DetailService

STATIC=Path(__file__).parent/'static'
class App:
    def __init__(self,work,regenerate=False):
        self.work=Path(work);self.generated=self.work/'generated';self.model_lock=threading.RLock()
        path=self.generated/'manifest.json'
        stale=not path.exists()
        if not stale:
            manifest=json.loads(path.read_text());stale=manifest['image_sha256']!=sha(ROOT/'beads-photo-2.jpg') or any(not (ROOT/p).exists() or sha(ROOT/p)!=h for p,h in manifest['sources'].items())
            stale |= any(not (self.generated/p).exists() or sha(self.generated/p)!=h for p,h in manifest['artifacts'].items())
        if regenerate or stale:
            print('Regenerating photo-only splines and interior candidates…',flush=True);generate(ROOT/'beads-photo-2.jpg',self.generated)
        self.manifest=json.loads(path.read_text());self.inventory=json.loads((self.generated/'observations.json').read_text());self.splines=json.loads((self.generated/'splines.json').read_text())
        annotation=ROOT/'photo2/review/r258/bead2-reviewed-support.json'
        self.reviewed_evidence=json.loads(annotation.read_text()) if annotation.exists() else None
        self.obs={r['id']:r for r in self.inventory['observations']};self.cache={};self.fft=None
        self.details=DetailService(self.work)
        self.reviews=ReviewStore(self.work/'reviews',self.manifest['image_sha256'])
        self.photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');b=io.BytesIO();self.photo.save(b,format='PNG',icc_profile=None);self.png=b.getvalue()
    def model(self,mid):
        with self.model_lock:
            if mid not in self.cache:
                print('Preparing diagnostic geometry',mid,flush=True)
                self.cache[mid]=models.prepare(mid,self.inventory,self.manifest['generation_id'],self.work/'models')
            return self.cache[mid]
    def validate_record(self,record,origin=False):
        m=self.model(record.get('model_id'));gi=record.get('generator_index')
        if record.get('model_version')!=m['version'] or record.get('generation_id')!=self.manifest['generation_id']: raise ValueError('Model/detector version mismatch; reload before saving')
        if type(gi) is not int or not 0<=gi<m['n']: raise ValueError('Generator index out of range')
        oid=record.get('observation_id')
        if oid is not None and oid not in self.obs: raise ValueError('Unknown fresh observation ID')
        if origin and not oid: raise ValueError('Select a fresh photographic observation for the new origin')
        polygon=record.get('region_polygon',[])
        if not isinstance(polygon,list) or len(polygon)>2000 or 0<len(polygon)<3:raise ValueError('Invalid region polygon')
        for p in polygon:
            if not isinstance(p,list) or len(p)!=2 or not all(type(x) in [int,float] and np.isfinite(x) for x in p) or not 0<=p[0]<self.photo.width or not 0<=p[1]<self.photo.height:raise ValueError('Invalid region vertex')
        for name in ['source_position','clicked_position']:
            p=record.get(name)
            if p is not None and (not isinstance(p,list) or len(p)!=2 or any(type(x) not in [int,float] for x in p) or not 0<=p[0]<self.photo.width or not 0<=p[1]<self.photo.height): raise ValueError('Image position outside original photograph')
    def debug_zip(self,record):
        self.validate_record(record);m=self.model(record['model_id']);b=m['beads'][record['generator_index']];oid=record.get('observation_id')
        x,y=record['source_position'];r=100;box=[max(0,int(x)-r),max(0,int(y)-r),min(self.photo.width,int(x)+r),min(self.photo.height,int(y)+r)]
        detail=self.details.result(record['model_id'],record['generator_index'],record.get('lighting_id',self.details.lighting()['selected']))
        doc=dict(**record,surface_diagnostics=detail,image_sha256=self.manifest['image_sha256'],native_image_size=list(self.photo.size),crop_box=box,
                 detector_provenance=self.manifest,model_provenance={k:v for k,v in m.items() if k not in ['beads','correspondences','patterns','centerline']},
                 bead=b,observation=self.obs.get(oid),correspondence=m['correspondences'].get(oid),
                 split_evidence=[self.inventory['split_pairs'][i] for i in self.obs.get(oid,{}).get('split_evidence',[])],
                 saved_reviews=[r for r in self.reviews.read()['reviews'] if r['model_version']==m['version'] and r['generator_index']==b['generator_index']])
        buf=io.BytesIO();crop=io.BytesIO();self.photo.crop(box).save(crop,format='PNG',icc_profile=None)
        with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('debug-record.json',json.dumps(doc,indent=2,allow_nan=False));z.writestr('original-crop.png',crop.getvalue())
        return buf.getvalue()

def make_server(app,host='127.0.0.1',port=8767):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):
            if args and str(args[1] if len(args)>1 else '') not in ['200','304']: super().log_message(fmt,*args)
        def send(self,data,kind='application/json',status=200,filename=None):
            if not isinstance(data,bytes):data=json.dumps(data,allow_nan=False,separators=(',',':')).encode()
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            try:
                parsed=urlsplit(self.path);path=parsed.path;q=parse_qs(parsed.query)
                if path=='/api/bootstrap':return self.send(dict(manifest=app.manifest,inventory=app.inventory,splines=app.splines,model_ids=models.IDS,reviewed_evidence=app.reviewed_evidence,reviews=app.reviews.read()))
                if path=='/api/lighting':return self.send(app.details.lighting())
                if path=='/api/surface':
                    key,future=app.details.submit(q['id'][0],int(q['gi'][0]),q['light'][0])
                    return self.send(dict(status='ready',result=future.result()) if future.done() else dict(status='working',key=key))
                if path=='/api/model':return self.send(app.model(q.get('id',[models.IDS[0]])[0]))
                if path=='/api/reviews':return self.send(app.reviews.read())
                if path=='/api/backup':return self.send(app.reviews.read(),filename='bead-reviews-backup.json')
                if path=='/api/legacy':return self.send(models.legacy())
                if path=='/api/fft':
                    if app.fft is None:app.fft=models.fft_data()
                    return self.send(app.fft)
                if path=='/api/legacy-splines':return self.send((ROOT/'photo2/review/r255/historical-splines.json').read_bytes())
                if path=='/original.jpg':return self.send((ROOT/'beads-photo-2.jpg').read_bytes(),'image/jpeg',filename='beads-photo-2.jpg')
                if path=='/photo.png':return self.send(app.png,'image/png')
                if path=='/api/crop':
                    x=float(q['x'][0]);y=float(q['y'][0]);r=min(256,max(24,int(q.get('r',['100'])[0])))
                    if not np.isfinite([x,y]).all():raise ValueError('Invalid crop')
                    box=(max(0,int(x)-r),max(0,int(y)-r),min(app.photo.width,int(x)+r),min(app.photo.height,int(y)+r))
                    b=io.BytesIO();app.photo.crop(box).save(b,format='PNG',icc_profile=None);return self.send(b.getvalue(),'image/png')
                if path=='/viewport.mjs':return self.send((ROOT/'photo2/tangent_viewer/viewport.mjs').read_bytes(),'text/javascript')
                if path.startswith('/reference/'):
                    rel=path[len('/reference/'):];target=(ROOT/'photo2/review'/rel).resolve();base=(ROOT/'photo2/review').resolve()
                    if not target.is_relative_to(base) or target.suffix not in ['.png','.json','.csv','.md','.gz']:raise ValueError('Invalid reference path')
                    return self.send(target.read_bytes(),mimetypes.guess_type(target)[0] or 'application/octet-stream')
                names={'/':'index.html','/app.mjs':'app.mjs','/logic.mjs':'logic.mjs','/style.css':'style.css'}
                if path in names:
                    target=STATIC/names[path];return self.send(target.read_bytes(),'text/javascript' if target.suffix=='.mjs' else mimetypes.guess_type(target)[0])
                self.send(dict(error='Not found'),status=404)
            except (ValueError,KeyError,FileNotFoundError) as e:self.send(dict(error=str(e)),status=400)
            except Exception as e:
                import traceback;traceback.print_exc();self.send(dict(error=str(e)),status=500)
        def do_POST(self):
            try:
                # Browser POSTs must be same-origin JSON; no permissive CORS or form writes.
                origin=self.headers.get('Origin')
                if origin and urlsplit(origin).netloc!=self.headers.get('Host'):return self.send(dict(error='Cross-origin write rejected'),status=403)
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('JSON required')
                size=int(self.headers.get('Content-Length',0))
                if not 0<size<=20_000_000:raise ValueError('Request size limit')
                body=json.loads(self.rfile.read(size));path=urlsplit(self.path).path
                if path=='/api/debug-export':return self.send(app.debug_zip(body),'application/zip',filename='bead-debug-record.zip')
                kind={'/api/review':'review','/api/origin':'origin','/api/session':'session','/api/import':'import'}.get(path)
                if kind is None:raise ValueError('Unknown action')
                if kind in ['review','origin']:app.validate_record(body['payload'],kind=='origin')
                return self.send(app.reviews.update(body['revision'],kind,body['payload']))
            except Conflict as e:self.send(dict(error=str(e)),status=409)
            except (ValueError,KeyError,TypeError) as e:self.send(dict(error=str(e)),status=400)
    return ThreadingHTTPServer((host,port),Handler)

def main():
    # R259: the familiar launch command now opens only photographic detection.
    # Keep the complete historical application available explicitly, unchanged.
    if '--legacy' not in sys.argv and '--prepare-only' not in sys.argv:
        from photo2.bead_detection.server import main as detection_main
        return detection_main()
    if '--legacy' in sys.argv:sys.argv.remove('--legacy')
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--port',type=int,default=8767);ap.add_argument('--work',type=Path,default=ROOT/'photo2/output/debugger');ap.add_argument('--regenerate',action='store_true');ap.add_argument('--prepare-only',action='store_true')
    a=ap.parse_args();app=App(a.work,a.regenerate)
    for mid in models.legacy_models.IDS:app.model(mid) # New fits load lazily; reviews untouched.
    if a.prepare_only:return
    server=make_server(app,port=a.port);print(f'Bead debugger: http://localhost:{server.server_port}\nReviews: {app.work / "reviews"}\nCtrl+C stops the server; saved reviews remain.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()

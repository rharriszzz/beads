"""Local batch review and append-only, fsynced versioned feedback."""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .common import ROOT, REVIEW, read, sha

ANSWERS={'A','B','neither','insufficient','not-sure',None}
OWNERSHIP={'same','different','insufficient','not-sure'}

class Store:
    def __init__(self,folder,review=REVIEW):
        self.folder=Path(folder);self.review=Path(review);self.folder.mkdir(parents=True,exist_ok=True)
        self.log=self.folder/'judgments.jsonl';self.lock=threading.Lock()
        self.manifest=read(self.review/'manifest.json');self.cases={q['case_id']:q for q in self.manifest['cases']}
    def events(self):
        if not self.log.exists():return []
        return [json.loads(line) for line in self.log.read_text().splitlines() if line.strip()]
    def state(self):
        result={}
        for event in self.events():result[event['case_id']]={k:event[k] for k in ('revision','payload','logical_parent_revision')}
        return result
    def record(self,request):
        with self.lock:
            name=request['case_id'];entry=self.cases[name]
            if request.get('candidate_digest')!=entry['candidate_digest']:raise ValueError('Displayed candidate version differs; reload before saving.')
            candidate_path=self.review/'data'/(name+'.json')
            if sha(candidate_path)!=entry['candidate_digest']:raise ValueError('Candidate file changed')
            candidate=read(candidate_path);history=[e for e in self.events() if e['case_id']==name]
            latest=history[-1] if history else None;revision=latest['revision'] if latest else 0
            if request.get('expected_revision',0)!=revision:raise ValueError('A newer answer exists; reload to avoid overwriting it.')
            previous=latest['payload'] if latest else dict(answer=None,ownership={})
            if request.get('action')=='undo':
                target=latest['logical_parent_revision'] if latest else 0
                e=next((e for e in history if e['revision']==target),None)
                payload=e['payload'] if e else dict(answer=None,ownership={});parent=e['logical_parent_revision'] if e else 0
            else:
                payload=request['payload'];parent=revision
            if payload.get('answer') not in ANSWERS:raise ValueError('Unknown answer')
            if payload.get('answer')=='B' and not candidate['B']:raise ValueError('No alternative B exists')
            neighbor_ids={q['feature_id'] for q in candidate['neighboring_features']}
            if any(k not in neighbor_ids or v not in OWNERSHIP for k,v in payload.get('ownership',{}).items()):raise ValueError('Invalid ownership judgment')
            # Snapshot immutable displayed bytes as well as exact masks/contours in
            # each event. Revisions never remove or mutate earlier answers.
            snapshot=self.folder/'snapshots'/entry['candidate_digest'];snapshot.mkdir(parents=True,exist_ok=True)
            for source,dest in [(candidate_path,snapshot/'candidate.json'),(self.review/'crops'/(name+'.png'),snapshot/'crop.png')]:
                if not dest.exists():shutil.copy2(source,dest)
            if sha(snapshot/'crop.png')!=candidate['crop_sha256']:raise ValueError('Native crop hash mismatch')
            if sha(snapshot/'candidate.json')!=entry['candidate_digest']:raise ValueError('Saved candidate snapshot hash mismatch')
            event=dict(schema='R290-review-v1',case_id=name,feature_id=candidate['feature']['id'],feature_point=candidate['feature']['point'],image_sha256=candidate['photo']['photo_sha256'],algorithm=candidate['algorithm'],parameters=candidate['parameters'],candidate_digest=entry['candidate_digest'],crop_sha256=candidate['crop_sha256'],displayed_candidates={k:candidate[k] for k in ('A','B')},neighboring_features=candidate['neighboring_features'],revision=revision+1,logical_parent_revision=parent,previous_payload=previous,payload=payload,action=request.get('action','answer'),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            with self.log.open('a') as f:f.write(json.dumps(event,separators=(',',':'),allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
            return {k:event[k] for k in ('revision','payload','logical_parent_revision')}

def server(port=0,feedback=None,review=REVIEW):
    store=Store(feedback or ROOT/'photo2/r290/feedback',review)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(review),**kwargs)
        def log_message(self,*args):pass
        def json(self,obj,status=200):
            data=(json.dumps(obj,allow_nan=False)+'\n').encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path=='/api/state':return self.json(store.state())
            if self.path=='/api/export':return self.json(dict(schema='R290-feedback-export-v1',manifest=store.manifest,events=store.events()))
            return super().do_GET()
        def do_POST(self):
            if self.path!='/api/judgment':return self.json(dict(error='Not found'),404)
            try:
                if self.headers.get('Origin') not in (None,f'http://{self.headers.get("Host")}'):raise ValueError('Use the local review origin')
                size=int(self.headers.get('Content-Length','0'))
                if size>100000:raise ValueError('Request too large')
                request=json.loads(self.rfile.read(size));return self.json(store.record(request))
            except (ValueError,KeyError,TypeError) as e:return self.json(dict(error=str(e)),409)
    httpd=ThreadingHTTPServer(('127.0.0.1',port),Handler);httpd.store=store
    return httpd

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8290);parser.add_argument('--feedback',type=Path);a=parser.parse_args()
    httpd=server(a.port,a.feedback)
    print(f'R290 batch review: http://127.0.0.1:{httpd.server_port}/',flush=True)
    print(f'Answers and full revision history: {httpd.store.log}',flush=True)
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass
    finally:httpd.server_close()

if __name__=='__main__':main()

"""R290 append-only feedback design, separately versioned for R291 questions."""
import argparse
import datetime
import json
import os
import shutil
import threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .common import ROOT,REVIEW,read,sha

ANSWERS={None,'A','B','partial','wrong-clear','insufficient','not-sure'}
DIAGNOSTICS={'neighbor','missing-material','internal-edge','missed-dark','other'}
OWNERSHIP={'same','different','insufficient','not-sure'}

def pair_id(a,b):return '|'.join(sorted([a,b]))

class Store:
    def __init__(self,folder,review=REVIEW):
        self.folder=Path(folder);self.review=Path(review);self.folder.mkdir(parents=True,exist_ok=True)
        self.log=self.folder/'judgments.jsonl';self.lock=threading.RLock()
        self.manifest=read(self.review/'manifest.json');self.cases={c['case_id']:c for c in self.manifest['cases']}

    def events(self):
        with self.lock:
            return [json.loads(s) for s in self.log.read_text().splitlines() if s.strip()] if self.log.exists() else []

    def state(self):
        cases={};ownership={}
        for e in self.events():
            cases[e['case_id']]={k:e[k] for k in ('revision','payload','logical_parent_revision')}
            for key,value in e['ownership_changes'].items():
                if value is None:ownership.pop(key,None)
                else:ownership[key]=dict(value=value,case_id=e['case_id'],revision=e['revision'],utc=e['utc'])
        return dict(cases=cases,ownership=ownership)

    def history(self):
        return [{k:e[k] for k in ('case_id','revision','payload','action','utc')} for e in self.events()]

    def record(self,request):
        with self.lock:
            name=request['case_id'];entry=self.cases[name];path=self.review/'data'/(name+'.json')
            if request.get('candidate_digest')!=entry['candidate_digest'] or sha(path)!=entry['candidate_digest']:raise ValueError('Candidate version differs; reload before saving.')
            candidate=read(path);history=[e for e in self.events() if e['case_id']==name];latest=history[-1] if history else None
            revision=latest['revision'] if latest else 0
            if request.get('expected_revision',0)!=revision:raise ValueError('A newer answer exists; reload before saving.')
            previous=latest['payload'] if latest else dict(answer=None,diagnostics=[],ownership={})
            if request.get('action')=='undo':
                target=latest['logical_parent_revision'] if latest else 0
                e=next((e for e in history if e['revision']==target),None)
                payload=e['payload'] if e else dict(answer=None,diagnostics=[],ownership={});parent=e['logical_parent_revision'] if e else 0
            else:payload=request['payload'];parent=revision
            if payload.get('answer') not in ANSWERS:raise ValueError('Unknown assessment')
            if payload.get('answer')=='B' and candidate['B'] is None:raise ValueError('No alternative B exists')
            if not isinstance(payload.get('diagnostics',[]),list) or not set(payload.get('diagnostics',[]))<=DIAGNOSTICS:raise ValueError('Unknown optional diagnostic')
            peers={q['feature_id'] for q in candidate['neighboring_features']}
            if any(k not in peers or v not in OWNERSHIP for k,v in payload.get('ownership',{}).items()):raise ValueError('Invalid ownership assessment')
            before_owners=self.state()['ownership'];changes={};prior={}
            old=previous.get('ownership',{});new=payload.get('ownership',{})
            for peer in set(old)|set(new):
                if old.get(peer)==new.get(peer):continue
                key=pair_id(candidate['feature']['id'],peer);value=new.get(peer)
                prior[key]=before_owners.get(key,{}).get('value')
                if request.get('action')=='undo' and latest and key in latest['ownership_previous']:value=latest['ownership_previous'][key]
                changes[key]=value
            snapshot=self.folder/'snapshots'/entry['candidate_digest'];snapshot.mkdir(parents=True,exist_ok=True)
            for source,dest in [(path,snapshot/'candidate.json'),(self.review/'crops'/(name+'.png'),snapshot/'crop.png')]:
                if not dest.exists():shutil.copy2(source,dest)
            if sha(snapshot/'candidate.json')!=entry['candidate_digest'] or sha(snapshot/'crop.png')!=candidate['crop_sha256']:raise ValueError('Snapshot hash mismatch')
            event=dict(schema='R291-review-v1',case_id=name,feature_id=candidate['feature']['id'],feature_point=candidate['feature']['point'],image_sha256=candidate['photo']['photo_sha256'],algorithm=candidate['algorithm'],parameters=candidate['parameters'],candidate_digest=entry['candidate_digest'],crop_sha256=candidate['crop_sha256'],displayed_candidates={k:candidate[k] for k in ('A','B')},revision=revision+1,logical_parent_revision=parent,previous_payload=previous,payload=payload,ownership_changes=changes,ownership_previous=prior,action=request.get('action','assessment'),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            with self.log.open('a') as f:f.write(json.dumps(event,separators=(',',':'),allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
            return self.state()

def server(port=0,feedback=None,review=REVIEW):
    store=Store(feedback or ROOT/'photo2/r291/feedback',review)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw):super().__init__(*a,directory=str(review),**kw)
        def log_message(self,*a):pass
        def json(self,obj,status=200):
            b=(json.dumps(obj,allow_nan=False)+'\n').encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
        def do_GET(self):
            if self.path=='/api/state':return self.json(store.state())
            if self.path=='/api/history':return self.json(store.history())
            if self.path=='/api/export':return self.json(dict(schema='R291-feedback-export-v1',manifest=store.manifest,events=store.events()))
            return super().do_GET()
        def do_POST(self):
            if self.path!='/api/judgment':return self.json(dict(error='Not found'),404)
            try:
                if self.headers.get('Origin') not in (None,f'http://{self.headers.get("Host")}'):raise ValueError('Use the local review origin')
                length=int(self.headers.get('Content-Length',0))
                if length>100000:raise ValueError('Request too large')
                return self.json(store.record(json.loads(self.rfile.read(length))))
            except (ValueError,KeyError,TypeError) as e:return self.json(dict(error=str(e)),409)
    httpd=ThreadingHTTPServer(('127.0.0.1',port),Handler);httpd.store=store;return httpd

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8291);p.add_argument('--feedback',type=Path);a=p.parse_args();httpd=server(a.port,a.feedback)
    print(f'R291 Start Here: http://127.0.0.1:{httpd.server_port}/',flush=True);print('Feedback:',httpd.store.log,flush=True)
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass
    finally:httpd.server_close()

if __name__=='__main__':main()

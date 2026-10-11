"""Revisioned append-only reviews, atomic snapshots and optimistic concurrency."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import json, math, os, threading, uuid
from pathlib import Path

ACTIONS=['looks-correct','location-incorrect','index-neighbor-incorrect','color-incorrect-or-uncertain',
         'duplicate-or-merged','detector-missed','cannot-determine','visible-centroid-incorrect',
         'predicted-reflection-incorrect','observed-reflection-incorrect-or-missing','lighting-mismatch']
class Conflict(ValueError): pass

def atomic(path,doc):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with tmp.open('w') as f:
        json.dump(doc,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)

def finite_point(p):
    return isinstance(p,list) and len(p)==2 and all(type(x) in (int,float) and math.isfinite(x) and 0<=x<=100000 for x in p)

class ReviewStore:
    def __init__(self,directory,image_hash):
        self.path=Path(directory);self.image_hash=image_hash;self.lock=threading.RLock();self.path.mkdir(parents=True,exist_ok=True)
        self.doc=dict(schema=1,image_sha256=image_hash,revision=0,reviews=[],origins=[],session={})
        latest=self.path/'latest.json'
        if latest.exists():
            self.doc=json.loads(latest.read_text());self.validate(self.doc)
        # A damaged latest is never silently reset. Revision snapshots remain available.
    def validate(self,doc):
        if not isinstance(doc,dict) or doc.get('schema')!=1 or doc.get('image_sha256')!=self.image_hash: raise ValueError('Backup belongs to another image/schema')
        if type(doc.get('revision')) is not int or doc['revision']<0: raise ValueError('Invalid revision')
        if not isinstance(doc.get('reviews'),list) or not isinstance(doc.get('origins'),list) or not isinstance(doc.get('session'),dict): raise ValueError('Invalid backup structure')
        for r in doc['reviews']:
            if r.get('action') not in ACTIONS or not all(isinstance(r.get(k),str) and r[k] for k in ['id','model_id','model_version','generation_id']): raise ValueError('Invalid review identity/action')
            if type(r.get('generator_index')) is not int or r['generator_index']<0 or not finite_point(r.get('source_position')): raise ValueError('Invalid review position/index')
            if not isinstance(r.get('note',''),str) or len(r.get('note',''))>20000: raise ValueError('Invalid review note')
        for r in doc['origins']:
            if not all(isinstance(r.get(k),str) and r[k] for k in ['id','model_id','model_version','generation_id','observation_id']): raise ValueError('Invalid origin identity')
            if type(r.get('generator_index')) is not int or r['generator_index']<0 or not finite_point(r.get('source_position')): raise ValueError('Invalid origin position')
        session=doc['session']
        if session.get('view') is not None:
            v=session['view']
            if not isinstance(v,dict) or any(type(v.get(k)) not in [int,float] or not math.isfinite(v[k]) for k in ['x','y','scale']) or not .025<=v['scale']<=32: raise ValueError('Invalid saved viewport')
        if 'gi' in session and (type(session['gi']) is not int or session['gi']<0): raise ValueError('Invalid saved selection')
        if 'layers' in session and (not isinstance(session['layers'],dict) or any(type(v) is not bool for v in session['layers'].values())): raise ValueError('Invalid layers')
        if 'drafts' in session and (not isinstance(session['drafts'],list) or any(not isinstance(d,list) or len(d)!=2 or not isinstance(d[0],str) or not isinstance(d[1],dict) for d in session['drafts'])): raise ValueError('Invalid drafts')
        json.dumps(doc,allow_nan=False)
    def read(self):
        with self.lock: return deepcopy(self.doc)
    def update(self,revision,kind,payload):
        with self.lock:
            if revision!=self.doc['revision']: raise Conflict('Another tab changed the review file. Reload current state; your draft is retained locally.')
            doc=deepcopy(self.doc)
            if kind=='session': doc['session']=payload
            elif kind in ['review','origin']:
                record=deepcopy(payload);record['id']=uuid.uuid4().hex;record['saved_at']=datetime.now(timezone.utc).isoformat()
                doc['reviews' if kind=='review' else 'origins'].append(record)
            elif kind=='import':
                self.validate(payload)
                for name in ['reviews','origins']:
                    ids={r['id']:r for r in doc[name]}
                    if any(r['id'] in ids and r!=ids[r['id']] for r in payload[name]): raise ValueError('Conflicting content for the same saved record ID')
                    doc[name].extend(r for r in payload[name] if r['id'] not in ids)
                doc['session']=payload['session']
            else: raise ValueError('Unknown mutation')
            doc['revision']+=1;self.validate(doc)
            # Immutable revision first. A crash can leave an extra snapshot, never a truncated latest.
            dest=self.path/f'revision-{doc["revision"]:08d}-{uuid.uuid4().hex[:8]}.json'
            atomic(dest,doc);atomic(self.path/'latest.json',doc);self.doc=doc
            return deepcopy(doc)

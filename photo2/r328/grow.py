"""One connected seed, local photographic patches, bounded reversible search.

No old selected graph, global optimizer, expected winding, or reference labels.
"""
import argparse, gzip, hashlib, json, time
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from scipy.spatial import cKDTree
from photo2.r325.tracker import preprocess

ROOT=Path(__file__).resolve().parents[2]
BANK=ROOT/'photo2/r327/results/graph.json.gz'
STEPS={(1,0):'F0',(0,1):'F1',(1,-1):'difference'}
SEED='C-0986-0371'

def read(path):
    with (gzip.open(path,'rt') if str(path).endswith('.gz') else open(path)) as f:return json.load(f)
def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with (gzip.open(path,'wt') if str(path).endswith('.gz') else open(path,'w')) as f:json.dump(data,f,indent=None if str(path).endswith('.gz') else 2,allow_nan=False)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def minus(a,b):return (a[0]-b[0],a[1]-b[1])

def prepare(bank):
    started=time.perf_counter();obs=bank['observations'];op={o['id']:o for o in obs};xy=np.array([o['xy'] for o in obs]);tree=cKDTree(xy)
    im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');data=preprocess(im);fg_field=data['fg'].astype(np.float32);checks={};patches=[]
    def check(a,b):
        k=tuple(sorted((a,b)))
        if k in checks:return checks[k]
        p,q=map(lambda o:np.array(op[o]['xy']),k);v=q-p;d=float(v@v);near=[]
        if d<1e-8:return dict(allowed=False,foreground_fraction=0.,intervening_observations=[])
        for oi in tree.query_ball_point((p+q)/2,np.sqrt(d)/2+7):
            o=obs[oi]
            if o['id'] in k:continue
            z=xy[oi]-p;f=float(z@v/d)
            if .2<f<.8 and np.linalg.norm(z-f*v)<7:near.append(o['id'])
        pts=np.linspace(p,q,31)
        # Bilinear foreground, identical sampling convention to R325.
        from scipy.ndimage import map_coordinates
        fg=float(map_coordinates(fg_field,[pts[:,1],pts[:,0]],order=1,mode='nearest').mean())
        checks[k]=dict(allowed=not near and fg>.95,foreground_fraction=fg,intervening_observations=near)
        return checks[k]
    # Keep the foreground conversion outside the pair loop.
    for wi,w in enumerate(bank['windows']):
        local=[]
        for hi,h in enumerate(w['hypotheses']):
            aa={o:tuple(v['ab']) for o,v in h['assignments'].items()};cells={v:o for o,v in aa.items()};adj=defaultdict(set);edges=[]
            for a,ab in aa.items():
                for d in STEPS:
                    b=cells.get(plus(ab,d))
                    if b and check(a,b)['allowed']:
                        adj[a].add(b);adj[b].add(a);edges.append((a,b,d))
            seen=set();ev=h['r327_evidence'];rows={r['observation']:r for r in ev['rows']}
            for root in sorted(adj):
                if root in seen:continue
                stack=[root];group=set()
                while stack:
                    o=stack.pop()
                    if o in group:continue
                    group.add(o);stack.extend(adj[o]-group)
                seen|=group
                if len(group)<3:continue
                sub={o:aa[o] for o in sorted(group)};ee=[e for e in edges if e[0] in group and e[1] in group]
                # Same photographic terms as R327, one local sum, no global factors.
                support=sum(rows[o]['utility'] for o in group if o in rows)
                seq=sum(r['reward'] for r in ev['runs'] if set(r['observations'])<=group)
                fraction=len(group)/len(aa);discovery=.35*h['photo_score']*fraction
                shape=h['r327_shared_shape']['penalty']*fraction
                score=support+.35*seq+discovery-shape
                local.append(dict(window=wi,hypothesis=hi,assignments=sub,edges=ee,score=score,score_terms=dict(support=support,sequence=.35*seq,discovery=discovery,shape_penalty=shape),parent_omitted=sorted(set(aa)-group)))
        # Identical relative topology has identical growth consequences; keep best
        # score, but record all equivalent evidence witnesses.
        unique={}
        for p in local:
            origin=next(iter(p['assignments'].values()));sig=tuple((o,*minus(v,origin)) for o,v in p['assignments'].items())
            if sig not in unique:unique[sig]=p;p['equivalent_witnesses']=[]
            elif p['score']>unique[sig]['score']:
                old=unique[sig];p['equivalent_witnesses']=old['equivalent_witnesses']+[[old['window'],old['hypothesis']]];unique[sig]=p
            else:unique[sig]['equivalent_witnesses'].append([p['window'],p['hypothesis']])
        patches.append(sorted(unique.values(),key=lambda p:(-p['score'],p['hypothesis'])))
    return patches,checks,dict(seconds=time.perf_counter()-started,candidate_patches=sum(map(len,patches)),checked_pairs=len(checks))


def lifted(p,arc,stations,period):
    return {(o,int(round((arc-stations[o])/period))):tuple(ab) for o,ab in p['assignments'].items()}


def extend(state,p,local,first=False):
    """Attach one connected patch; reject bookkeeping conflicts, not photo claims."""
    coords=state['coords'];common=coords.keys()&local.keys()
    if len(common)<(1 if first else 2):return None,'insufficient frontier overlap'
    offsets={minus(coords[o],local[o]) for o in common}
    if len(offsets)!=1:return None,'shared-coordinate disagreement'
    offset=next(iter(offsets));new={o:plus(ab,offset) for o,ab in local.items()};merged=dict(coords);occupied={v:k for k,v in coords.items()}
    for o,v in new.items():
        if v in occupied and occupied[v]!=o:return None,'two observed supports assigned one lattice site'
        occupied[v]=o;merged[o]=v
    # The same physical observation at another geographic turn must differ by
    # one common H. No value or magnitude of H is imposed.
    byid=defaultdict(list)
    for (o,k),v in merged.items():byid[o].append((k,v))
    H=state['H'];returns=[]
    for o,versions in byid.items():
        if len(versions)<2:continue
        versions.sort();k,a=versions[0]
        for l,b in versions[1:]:
            dk=l-k;d=minus(b,a)
            if any(v%dk for v in d):return None,'nonintegral return translation'
            value=tuple(v//dk for v in d)
            if H is not None and value!=H:return None,'inconsistent return translation'
            H=value;returns.append(o)
    rec=dict(window=p['window'],hypothesis=p['hypothesis'],patch=p['patch'],offset=list(offset),attached_to=[list(o) for o in sorted(common)],added=[list(o) for o in sorted(new.keys()-coords.keys())],score=p['score'],component_count=1)
    return dict(coords=merged,H=H,returns=sorted(set(returns)),score=state['score']+p['score'],path=state['path']+[rec],skips=0),'attached'


def search(bank,patches,width=32,budget=600):
    start=time.perf_counter();period=bank['period_px'];stations=bank['stations_px'];ws=bank['windows'];n=len(ws)
    for pp in patches:
        for i,p in enumerate(pp):p['patch']=i
    remaining_ids=[set() for _ in range(n+2)]
    for j in range(n,-1,-1):
        remaining_ids[j]=remaining_ids[j+1]|{o for p in patches[j%n] for o in p['assignments']}
    seedturn=int(round((ws[0]['arc_px']-stations[SEED])/period))
    states=[dict(coords={(SEED,seedturn):(0,0)},H=None,returns=[],score=0.,path=[],skips=0)]
    trace=[];failures=Counter();completed=False;checkpoints={};rollbacks=[];retried=set();step=0;active_width=width
    # Repeat start window at +period to demand an actual photographed return.
    while step<=n:
        checkpoints[step]=states;previous_best=states[0]
        wi=step%n;arc=ws[wi]['arc_px']+(period if step==n else 0);batch=[];counts=Counter()
        for s in states:
            for p in patches[wi]:
                t,reason=extend(s,p,lifted(p,arc,stations,period),first=step==0)
                if step==n and t is not None and (t['H'] is None or len(t['returns'])<3):
                    t=None;reason='insufficient photographed return overlap'
                counts[reason]+=1
                if t is not None:batch.append(t)
            if step not in (0,n) and s['skips']<3:
                t=dict(s,skips=s['skips']+1,path=s['path']+[dict(window=wi,skipped=True,component_count=1)]);batch.append(t)
        failures.update(counts)
        if not batch:
            trace.append(dict(step=step,window=wi,failed=True,reasons=dict(counts)))
            if step not in retried and step>0 and time.perf_counter()-start<budget:
                retried.add(step);back=max(0,step-5);active_width=min(active_width*4,512)
                rollbacks.append(dict(failed_step=step,reopen_from=back,width=active_width,reason='No compatible connected continuation; reopen five recent windows'))
                states=checkpoints[back];step=back;continue
            break
        # Equivalent active frontier states share future outcomes. Preserve absolute
        # coordinates and H so different windings are not merged.
        future=remaining_ids[step+1]
        unique={}
        for s in sorted(batch,key=lambda s:-s['score']):
            sig=(tuple(sorted((k,v) for k,v in s['coords'].items() if k[0] in future)),s['H'],s['skips'])
            if sig not in unique:unique[sig]=s
            if len(unique)>=active_width:break
        states=list(unique.values())
        revisions=[]
        for age,(old,new) in enumerate(zip(previous_best['path'],states[0]['path'])):
            if (old.get('hypothesis'),old.get('patch'),old.get('skipped'))!=(new.get('hypothesis'),new.get('patch'),new.get('skipped')):
                revisions.append(dict(window=old['window'],steps_back=step-age,previous_hypothesis=old.get('hypothesis'),new_hypothesis=new.get('hypothesis')))
        trace.append(dict(revisions=revisions,step=step,window=wi,candidates=len(batch),retained=len(states),best_score=states[0]['score'],best_nodes=len(states[0]['coords']),best_H=states[0]['H'],reasons=dict(counts),seconds=time.perf_counter()-start))
        if step%25==0:print('growth',width,step,'states',len(states),'nodes',len(states[0]['coords']),'seconds',round(time.perf_counter()-start,2),flush=True)
        if step==n:completed=True
        if time.perf_counter()-start>budget:break
        step+=1
    states.sort(key=lambda s:-s['score'])
    winding_best={}
    for s in states:
        winding_best.setdefault(s['H'],s)
    saved=states[:8]+[s for s in winding_best.values() if s not in states[:8]]
    def serialize(s):return dict(s,coords=[dict(observation=k[0],turn=k[1],ab=list(v)) for k,v in sorted(s['coords'].items())])
    return dict(width=width,seconds=time.perf_counter()-start,completed=completed,rollbacks=rollbacks,trace=trace,failures=dict(failures),states=[serialize(s) for s in saved])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--width',type=int,default=32);ap.add_argument('--budget',type=float,default=600);ap.add_argument('--prepared');args=ap.parse_args();out=Path(args.output)
    if out.exists():raise RuntimeError('Use a new output directory to preserve trials')
    bank=read(BANK)
    if args.prepared:
        cache=read(args.prepared);patches,checks,prep=cache['patches'],cache['checks'],cache['preparation']
    else:
        patches,checks,prep=prepare(bank);checks=[dict(source=a,target=b,**v) for (a,b),v in checks.items()]
    save(out/'prepared.json.gz',dict(patches=patches,checks=checks,preparation=prep,bank_sha256=sha(BANK)))
    result=search(bank,patches,args.width,args.budget);save(out/'search.json.gz',result)
    save(out/'receipt.json',dict(preparation=prep,seconds=result['seconds'],completed=result['completed'],width=args.width,bank_sha256=sha(BANK),source_sha256=sha(__file__),last_step=result['trace'][-1],best=dict(score=result['states'][0]['score'],nodes=len(result['states'][0]['coords']),H=result['states'][0]['H'])))
    print(json.dumps(read(out/'receipt.json')),flush=True)
if __name__=='__main__':main()

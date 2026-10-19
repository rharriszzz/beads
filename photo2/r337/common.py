import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r337-mpl')
import math,json,gzip
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from photo2.r328.grow import ROOT,read,save,sha
COLORS=['red','yellow','black']
BASE='a6e16d54eb692f78a725de6fb56414d4f3e98843'

def data():
    g=read(ROOT/'photo2/r336/results/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:tuple(r['ab']) for r in g['coordinates']};ids=sorted(co)
    ctrl=read(ROOT/'photo2/r334/controls/controls.json.gz');blocks={r['id']:r['section'] for r in ctrl['rows']+ctrl['maker_geography']}
    core=set(read(ROOT/'photo2/r336/analysis/diagnostics.json.gz')['fixed_core_ids'])
    return g,obs,co,ids,np.array([co[o] for o in ids]),np.array([COLORS.index(obs[o]['color']) for o in ids]),np.array([blocks[o] for o in ids]),core

def quotient(v,H):
    a,b=map(int,v);x,y=map(int,H);t=a//x
    return a-t*x,b-t*y

def keys_for(rows):
    _,k=np.unique(np.asarray(rows),axis=0,return_inverse=True);return k

def spatial(ab,v=(16,16)):
    a,b=v;t=ab[:,0]//a
    return keys_for(ab-t[:,None]*np.array(v))

def hnf(ab,p,q,r):
    t=ab[:,1]//q
    return (ab[:,0]-r*t)%p+p*(ab[:,1]%q)

def conflicts(keys,c,ids):
    groups=defaultdict(list)
    for i,key in enumerate(keys):groups[int(key)].append(i)
    witnesses=[];minimum=0
    for key,ii in sorted(groups.items()):
        ct=Counter(int(c[i]) for i in ii);minimum+=len(ii)-max(ct.values())
        if len(ct)>1:
            witnesses.append(dict(cell=key,counts={COLORS[k]:v for k,v in ct.items()},ids=[ids[i] for i in ii],pair=next([ids[i],ids[j]] for i in ii for j in ii if c[i]!=c[j])))
    return dict(minimum_record_disagreements=minimum,conflicting_cells=len(witnesses),witnesses=witnesses)

def predict(keys,c,blocks,guard=1,parent=None,occ=None):
    n=len(c);size=int(max(keys))+1;pred=np.zeros((n,3));base=np.zeros_like(pred);details=[]
    tests=range(12) if occ is None else sorted(set(map(int,occ)))
    for b in tests:
        te=blocks==b if occ is None else occ==b
        tr=~np.isin(blocks,[(b+d)%12 for d in range(-guard,guard+1)]) if occ is None else ~te
        prior=(np.bincount(c[tr],minlength=3)+1).astype(float);prior/=prior.sum()
        cc=np.bincount(keys[tr]*3+c[tr],minlength=size*3).reshape(size,3)
        th=(cc+3*prior)/(cc.sum(1)[:,None]+3)
        if parent is not None:
            ps=int(max(parent))+1;pc=np.bincount(parent[tr]*3+c[tr],minlength=ps*3).reshape(ps,3);pt=(pc+3*prior)/(pc.sum(1)[:,None]+3)
            mapping=np.zeros(size,int)
            for x,y in zip(keys,parent):mapping[x]=y
            th=(cc+pt[mapping])/(cc.sum(1)[:,None]+1)
        pred[te]=th[keys[te]];base[te]=prior
    ll=np.log(pred[np.arange(n),c]/base[np.arange(n),c])
    per=[dict(section=b,n=int((blocks==b).sum()),gain=float(ll[blocks==b].mean())) for b in range(12) if (blocks==b).any()]
    return dict(gain_nats=float(ll.mean()),agreement=float((pred.argmax(1)==c).mean()),per_section=per,per_color={COLORS[j]:dict(n=int((c==j).sum()),gain=float(ll[c==j].mean()),agreement=float((pred.argmax(1)[c==j]==j).mean())) for j in range(3)}),pred,base

def motif(keys,c,blocks,ids,size):
    result=[]
    for r in range(size):
        ii=np.flatnonzero(keys==r);ct=Counter(int(c[i]) for i in ii);win,n=ct.most_common(1)[0] if ct else (-1,0);sections=sorted({int(blocks[i]) for i in ii if c[i]==win});strong=n>=3 and len(sections)>=3 and n/max(len(ii),1)>=.8
        status='conflict' if len(ct)>1 else 'strong' if strong else 'observed' if len(ii) else 'unknown'
        result.append(dict(residue=r,color=COLORS[win] if strong else '?',observed_color=COLORS[win] if len(ct)==1 else '?',status=status,counts={COLORS[k]:v for k,v in ct.items()},sections=sections,ids=[ids[i] for i in ii]))
    return result

# Scientific exports normalize NumPy scalar types without changing values.
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    def default(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    with (gzip.open(path,'wt') if str(path).endswith('.gz') else open(path,'w')) as f:
        json.dump(value,f,default=default,allow_nan=False,indent=None if str(path).endswith('.gz') else 2)

def maker_constraints(g,co):
    """Exact earlier displayed/reviewed links, not a whole-photo certification."""
    import ast
    from photo2.r329.common import canonical
    old=canonical(read(ROOT/'photo2/r328/development/final256/search.json.gz')['states'][0]);sets={};tree=ast.parse((ROOT/'photo2/r331/review.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ['gids','eids','fids','blackids']:sets[target.id]=ast.literal_eval(node.value)
    pairs=defaultdict(list);current={frozenset((e['source'],e['target'])) for e in g['edges']}
    for name,names in sets.items():
        for a in names:
            for z in names:
                if a in old and z in old and tuple(np.array(old[z])-old[a]) in [(1,0),(0,1)]:
                    key=frozenset((a,z))
                    if key in current:pairs[key].append('R332 maker review of R331 '+name)
    established=read(ROOT/'photo2/r328/results/established-subset.json')
    for e in established['links']+established['peripheral_links']:
        if e.get('source') and e.get('target') and e.get('recovered'):
            key=frozenset((e['source'],e['target']))
            if key in current:pairs[key].append('R161 recorded reference')
    for panel in read(ROOT/'photo2/r336/review/panels.json').values():
        for e in panel['edges']:pairs[frozenset((e['source'],e['target']))].append('R337 maker approval of R336 '+panel['key'][0]['id'])
    for e in g['edges']:
        if e.get('origin')=='R336':pairs[frozenset((e['source'],e['target']))].append('R336 repaired relationship retained by R337 instruction')
    return pairs

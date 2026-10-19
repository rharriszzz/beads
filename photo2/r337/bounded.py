"""Two bounded photographic patch substitutions with hard reviewed-edge pruning."""
import argparse,time
from .common import *
from photo2.r329.common import inputs,replay,canonical,serialize,lifted,extend
from .search import extension

def run(out,width=32):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();g,obs,co,ids,ab,c,b,core=data();_,bank,prep,ss=inputs();primary=ss[0];_,_,cp=replay(bank,prep,primary['path']);protected=maker_constraints(g,co);pe=[e for e in g['edges'] if frozenset((e['source'],e['target'])) in protected];output=[];trials=[]
    # These corridors are not the two maker-approved R336 gap illustrations.
    # Recombine only existing native-tested connected patches, no new bodies.
    for begin,end,label in [(177,181,'upper-left return approach'),(78,83,'lower bend')]:
        states=[cp[begin]];trace=[];failures=Counter();complete=[]
        for wi in range(begin,end+1):
            batch=[]
            for s in states:
                for p in prep['patches'][wi]:
                    t,why=extend(s,p,lifted(p,bank['windows'][wi]['arc_px'],bank['stations_px'],bank['period_px']))
                    if t is None:failures[why]+=1;continue
                    # Reviewed links whose endpoints share a lifted geographic
                    # turn have exact signed differences, even before H exists.
                    bad=False
                    for e in pe:
                        for turn in [-1,0,1]:
                            aa=t['coords'].get((e['source'],turn));zz=t['coords'].get((e['target'],turn))
                            if aa is not None and zz is not None and tuple(np.array(zz)-aa)!=tuple(e['delta_ab']):bad=True;break
                        if bad:break
                    if bad:failures['maker-reviewed equation changed']+=1;continue
                    batch.append(t)
            unique={}
            for s in sorted(batch,key=lambda s:-s['score']):
                sig=tuple(sorted(s['coords'].items()))
                if sig not in unique:unique[sig]=s
                if len(unique)>=width:break
            states=list(unique.values());returns=0
            for s in states:
                full,receipt,_=replay(bank,prep,primary['path'],checkpoint=s,start=wi+1)
                if full is None:failures['suffix '+receipt['reason']]+=1;continue
                returns+=1;serialized=serialize(full);alt0=canonical(serialized);alt={o:tuple(np.array(v)+co[g['reference']]) for o,v in alt0.items() if o in co};ext,coords=extension(g,co,alt,serialized['H'],core,protected);eligible=[dict(family=f,N=int(np.dot(serialized['H'],w)),L=L) for f,w in [('A',[7,6]),('B',[6,7])] for L in range(200,400) if int(np.dot(serialized['H'],w))%L==0]
                complete.append(dict(last_replaced=wi,state=serialized,receipt=receipt,eligible=eligible,maker_changes=ext['maker_violations'],link_changes=len(ext['violated_edges']),new_boundary_changes=ext['new_support_boundary_violations'],duplicate_sites=ext['duplicate_sites']))
            trace.append(dict(window=wi,attempted=len(batch),retained=len(states),complete_returns=returns))
            if not states:break
            if time.perf_counter()-started>60:raise RuntimeError('Bounded60s limit reached; preserve output before any extension')
        distinct={}
        for r in complete:
            sig=(tuple(r['state']['H']),tuple(sorted(canonical(r['state']).items())))
            distinct.setdefault(sig,r)
        rows=list(distinct.values());output.extend(rows);trials.append(dict(corridor=label,begin=begin,end=end,width=width,trace=trace,failures=dict(failures),complete_paths=len(complete),distinct_maps=len(rows),eligible_maker_preserving=sum(bool(r['eligible']) and not r['maker_changes'] and not r['duplicate_sites'] for r in rows)))
    distinct={}
    for r in output:distinct.setdefault((tuple(r['state']['H']),tuple(sorted(canonical(r['state']).items()))),r)
    save(out/'states.json.gz',dict(candidates=list(distinct.values()),trials=trials,seconds=time.perf_counter()-started,policy='Photographic score orders a maximum32 states per window, with hard reviewed-equation pruning; no color ranking until complete return and exact count divisibility. Beam is bounded and not exhaustive. New R332 boundary contradictions and identity collisions still reject adoption.'))
    save(out/'summary.json',dict(trials=trials,distinct_complete_maps=len(distinct),seconds=time.perf_counter()-started));print('BOUNDED',[(r['corridor'],r['distinct_maps'],r['eligible_maker_preserving']) for r in trials],time.perf_counter()-started,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--width',type=int,default=32);a=p.parse_args();run(a.output,a.width)

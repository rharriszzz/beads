"""Contingent native minimax simplex refinement after broad Stage 2 discovery.

Runs only if the initial full-necklace native gain is below 5%. Existing
parameters/maps/guards, at most 600 extra wall seconds, no new photographic data.
Atomic evaluations are cached across interrupted deterministic simplex replay.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r312-mpl')
from pathlib import Path
from copy import deepcopy
from collections import Counter
import argparse,signal,time,resource
import numpy as np
from scipy.optimize import minimize
from photo2.r297.common import ROOT,read,save,sha,digest,utc,environment,run_lock
from .search import sources
from .model import canonical,validate,distance
from .objective import Engine,guard,violation
from .delivery import source_bundle
from .profiling import Sampler

class BlockDone(Exception):pass
class Paused(Exception):pass

BLOCKS=[(['light_az','light_el','roughness','light_inverse'],[3.,2.,.7,.0001]),
        (['phase','s0','elevation','roll','scale','minor','axial','perspective'],[.04,1.5,.6,2.,.06,.06,.03,.00002]),
        (['phase','s0','axis_cos','axis_sin','phase_cos','spacing_cos'],[.025,.75,1.,1.,.025,.0005])]

def move(base,keys,scale,u):
    p=deepcopy(base)
    for key,width,x in zip(keys,scale,u):
        if key in ['axis_cos','axis_sin','phase_cos','spacing_cos']:
            field='axis_nodes' if key.startswith('axis') else 'local_phase' if key.startswith('phase') else 'local_spacing'
            t=np.arange(len(p[field]))/len(p[field]);wave=np.sin(2*np.pi*t) if key.endswith('sin') else np.cos(2*np.pi*t)
            p[field]=(np.array(p[field])+width*x*wave).tolist()
        else:p[key]=p.get(key,0.)+width*x
    return canonical(p)

class Refine:
    def __init__(self,root,seconds=600,resume=False):
        self.root=Path(root);self.out=self.root/'stage2/local';self.out.mkdir(parents=True,exist_ok=True)
        self.seconds=seconds;self.start=time.monotonic();self.cpu_start=time.process_time();self.stop=False
        self.initial=read(self.root/'stage2/selection.json');self.parent=read(self.root/'stage2/checkpoint.json');assert self.parent['sealed']
        self.engine=Engine(2);self.original=[read(p) for p in sorted((self.root/'stage2/trials').glob('*.gz'))]
        self.rows=[read(p) for p in sorted((self.out/'trials').glob('*.gz'))]
        self.cache={r['key']:r for r in self.original+self.rows}
        manifest=sources();manifest['photo2/r312/local_refine.py']=sha(Path(__file__))
        inputs={p:sha(self.root/'stage2'/p) for p in ['selection.json','checkpoint.json']}
        if resume:
            self.state=read(self.out/'checkpoint.json');assert not self.state['sealed']
            assert self.state['sources']==manifest and self.state['environment']==environment() and self.state['inputs']==inputs
        else:
            assert not (self.out/'checkpoint.json').exists(),'Use --resume or a new output'
            candidates=self.initial['models'][:3]
            self.state=dict(started=utc(),sources=manifest,environment=environment(),inputs=inputs,elapsed=0.,cpu_seconds=0.,block=0,pending=None,seeds=candidates,sealed=False,cache_hits=0)
            source_bundle(self.out/'fitting-source',manifest)
        self.prior=max([self.state['elapsed']]+[r['local_elapsed'] for r in self.rows]);self.prior_cpu=self.state['cpu_seconds']
        self.base_wall=read(self.root/'stage2/summary.json')['elapsed'];self.base_cpu=read(self.root/'stage2/summary.json')['cpu_seconds']
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,lambda *_:setattr(self,'stop',True))
    def elapsed(self):return self.prior+time.monotonic()-self.start
    def checkpoint(self):
        self.state.update(elapsed=self.elapsed(),cpu_seconds=self.prior_cpu+time.process_time()-self.cpu_start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
        save(self.out/'checkpoint.json',self.state)
    def key(self,p,family):
        return digest(dict(parameters=p,step=1.,family=family,mapping_sha256=digest(self.parent['mappings'][family])))
    def full_chain_calibration(self):
        """New before/after epoch; reassignment-only changes are never fitting gains."""
        old=deepcopy(self.parent);docs={};families=['R306-2405']+[f for f in old['baselines'] if f!='R306-2405']
        for family in families:
            path=self.out/'calibration'/f'{family}.json.gz'
            if path.exists():doc=read(path)
            else:
                if self.stop:raise Paused()
                before=read(self.root/'stage2/calibration'/f'{family}.json.gz');p=before['parameters']
                result=self.engine.evaluate(p,None,step=1.);assert result['feasible']
                changed=[dict(id=k,before=v,after=result['mapping'].get(k)) for k,v in old['mappings'][family].items() if v!=result['mapping'].get(k)]
                doc=dict(parameters=p,result=result,old_metrics=before['result']['metrics'],old_mapping=old['mappings'][family],changed_owners=changed,
                    policy='Full-necklace before/after epoch, all269 observations. Assignment-only score changes are controls, not geometry improvements. These maps are frozen throughout subsequent refinement.')
                save(path,doc)
                print('full-chain calibration',family,'before',round(doc['old_metrics']['maximum_px'],3),'after',round(result['metrics']['maximum_px'],3),'changed',len(changed),flush=True)
            docs[family]=doc
        self.parent['mappings']={f:d['result']['mapping'] for f,d in docs.items()}
        self.parent['baselines']={f:d['result'] for f,d in docs.items()}
        common=self.parent['baselines']['R306-2405'];self.controls=[]
        for i,(family,doc) in enumerate(docs.items()):
            r=doc['result'];v=violation(r,common);obj=r['metrics']['objective_px']
            self.controls.append(dict(id=2000000+i,key=self.key(doc['parameters'],family),parameters=doc['parameters'],family=family,step=1.,kind='full-chain-initialization',result=r,feasible=True,status='certified',objective_px=obj,violation=v,acquisition=obj+50*v,passes_safeguards=guard(r,common),correspondence_control=True,accepted_improvement=False))
        self.cache={self.key(r['parameters'],r['family']):r for r in self.original+self.rows if r['family'] in self.parent['mappings'] and r.get('result',{}).get('mapping')==self.parent['mappings'][r['family']]}
        self.cache.update({r['key']:r for r in self.controls})
        if not self.state.get('calibration_complete'):
            chosen=[]
            for row in sorted(self.controls,key=lambda r:r['acquisition']):
                if all(distance(row['parameters'],q['parameters'])>.035 for q in chosen):chosen.append(row)
                if len(chosen)==3:break
            self.state.update(seeds=chosen,calibration_complete=True,mapping_hashes={f:digest(d['result']['mapping']) for f,d in docs.items()},calibration_files={f:sha(self.out/'calibration'/f'{f}.json.gz') for f in docs})
            self.checkpoint()
        else:
            for f,h in self.state['calibration_files'].items():assert sha(self.out/'calibration'/f'{f}.json.gz')==h
        save(self.out/'correspondence-control.json',dict(families={f:dict(old_metrics=d['old_metrics'],full_chain_metrics=d['result']['metrics'],changed_owners=d['changed_owners']) for f,d in docs.items()},new_observations=0,geometry_changes=0,not_fitting_improvement=True))
    def objective(self,u):
        st=self.state
        if self.stop or self.elapsed()>=self.seconds:raise Paused()
        if self.elapsed()>=st['pending']['deadline']:raise BlockDone()
        block=st['pending'];p=move(block['parameters'],block['keys'],block['scales'],u)
        key=self.key(p,block['family'])
        if key in self.cache:
            st['cache_hits']+=1;return self.cache[key].get('acquisition',1e7)
        began=time.monotonic();cpu=time.process_time();ident=1000000+len(self.rows)
        row=dict(id=ident,key=key,parameters=p,step=1.,family=block['family'],kind='native-simplex',block=st['block'],seed=block['seed'],feasible=False)
        rejection=validate(p)
        try:
            if rejection:row.update(status='numerical-bound',reason=rejection)
            else:
                r=self.engine.evaluate(p,self.parent['mappings'][row['family']],step=1.)
                row.update(result=r,feasible=r['feasible'],status='certified' if r['feasible'] else 'unresolved-contact')
                if r['feasible']:
                    base=self.parent['baselines'][row['family']];common=self.parent['baselines']['R306-2405']
                    good=guard(r,base) and guard(r,common);v=max(violation(r,base),violation(r,common));obj=r['metrics']['objective_px']
                    previous=min(z['objective_px'] for z in self.controls+self.rows if z.get('passes_safeguards'))
                    row.update(objective_px=obj,passes_safeguards=good,passes_family_safeguards=guard(r,base),passes_common_safeguards=guard(r,common),violation=v,acquisition=obj+50*v,accepted_improvement=good and obj<previous)
        except (ValueError,FloatingPointError,OverflowError) as error:row.update(status='numerical-rejected',reason=str(error))
        row.update(seconds=time.monotonic()-began,cpu_seconds=time.process_time()-cpu,local_elapsed=self.elapsed(),elapsed=self.base_wall+self.elapsed())
        save(self.out/'trials'/f'{ident:07d}.json.gz',row);self.rows.append(row);self.cache[key]=row;self.checkpoint()
        if len(self.rows)%10==0 or row.get('accepted_improvement'):print('simplex',ident,row['family'],block['keys'],round(row.get('objective_px',-1),4),row.get('passes_safeguards'),'elapsed',round(self.elapsed(),1),flush=True)
        return row.get('acquisition',1e7)
    def run(self):
        st=self.state;baseline=self.parent['baselines']['R306-2405']['metrics']['objective_px']
        initial=min(r['objective_px'] for r in self.initial['models'])
        skip=initial<=.95*baseline
        save(self.out/'decision.json',dict(skipped=skip,reason='Initial native gain reaches5%; calibration control only' if skip else 'Less than5% native minimax gain; standard simplex refinement after full-chain initialization',seconds=self.seconds,baseline=baseline,initial=initial,new_photographic_evidence=False))
        self.checkpoint()
        try:self.full_chain_calibration()
        except Paused:self.checkpoint();return
        if skip:
            st['sealed']=True;self.checkpoint();save(self.out/'summary.json',dict(evaluations=0,calibration_controls=len(self.controls),calibration_control_seconds=sum(r['result']['seconds'] for r in self.controls),elapsed=st['elapsed'],cpu_seconds=st['cpu_seconds'],peak_rss_mib=st['peak_rss_mib'],accepted_improvements=0,statuses={},stop_reason='initial5percent gain; only calibration control'));return
        if 'slot_seconds' not in st:st['slot_seconds']=max(1.,self.seconds-self.elapsed())/max(1,len(st['seeds'])*len(BLOCKS))
        slot=st['slot_seconds'];self.checkpoint()
        try:
            while st['block']<len(st['seeds'])*len(BLOCKS) and self.elapsed()<self.seconds and not self.stop:
                seed=st['seeds'][st['block']//len(BLOCKS)];keys,scale=BLOCKS[st['block']%len(BLOCKS)]
                if st['pending'] is None:
                    pool=[seed]+[r for r in self.rows if r.get('feasible') and r['seed']==seed['id']]
                    parent=min(pool,key=lambda r:r['acquisition'])
                    st['pending']=dict(parameters=parent['parameters'],family=seed['family'],seed=seed['id'],keys=keys,scales=scale,deadline=min(self.seconds,self.elapsed()+slot));self.checkpoint()
                try:
                    n=len(keys);simplex=np.vstack([np.zeros(n),np.eye(n)])
                    result=minimize(self.objective,np.zeros(n),method='Nelder-Mead',options=dict(initial_simplex=simplex,maxfev=400,xatol=.002,fatol=.0005))
                    save(self.out/f'block-{st["block"]:02d}.json',dict(message=str(result.message),function_calls=int(result.nfev),best_u=result.x.tolist(),acquisition=float(result.fun)))
                except BlockDone:pass
                st['block']+=1;st['pending']=None;self.checkpoint()
        except Paused:pass
        self.checkpoint();st['stop_reason']='signal' if self.stop else 'allowance or block completion'
        summary=dict(evaluations=len(self.rows),calibration_controls=len(self.controls),calibration_control_seconds=sum(r['result']['seconds'] for r in self.controls),elapsed=st['elapsed'],cpu_seconds=st['cpu_seconds'],peak_rss_mib=st['peak_rss_mib'],accepted_improvements=sum(r.get('accepted_improvement',False) for r in self.rows),statuses=dict(Counter(r['status'] for r in self.rows)),stop_reason=st['stop_reason'],correspondence_epoch='full-chain')
        save(self.out/'summary.json',summary)
        if not self.stop:
            pool=sorted([r for r in self.controls+self.rows if r.get('passes_safeguards') and r['step']==1.],key=lambda r:r['objective_px']);selected=[]
            for row in pool:
                if all(row['family']!=q['family'] or distance(row['parameters'],q['parameters'])>.035 for q in selected):selected.append(row)
                if len(selected)==8:break
            trade=[]
            for row in sorted([r for r in self.controls+self.rows if r.get('feasible') and not r.get('passes_safeguards') and r['step']==1.],key=lambda r:r['objective_px']):
                if all(row['family']!=q['family'] or distance(row['parameters'],q['parameters'])>.04 for q in trade):trade.append(row)
                if len(trade)==2:break
            st['sealed']=True;self.checkpoint()
            save(self.root/'stage2/final-selection.json',dict(sealed=True,utc=utc(),models=selected,tradeoffs=trade,correspondence_epoch='full-chain',initial_selection_sha256=sha(self.root/'stage2/selection.json'),local_source_sha256=sha(Path(__file__)),no_comparison_or_new_data_exposure=True))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'photo2/r312/results/campaign');parser.add_argument('--seconds',type=float,default=600.);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    with run_lock(args.output):
        with Sampler(.01) as sampler:Refine(args.output,args.seconds,args.resume).run()
        save(args.output/'stage2/local'/f'sampling-{time.time_ns()}.json',sampler.result())
if __name__=='__main__':main()

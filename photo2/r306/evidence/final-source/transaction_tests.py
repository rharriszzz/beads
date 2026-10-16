"""Actual CLI interruption/resume and post-result crash recovery."""
import os,subprocess,time,tempfile
from pathlib import Path
from photo2.r297.common import ROOT,read,save

def main():
    root=Path(tempfile.mkdtemp(prefix='r306-transactions-',dir='/tmp'))
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
    base=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_global_fit.py'),'--seconds','1000','--no-review']
    def run(path,n,resume=False):
        with (root/(path.name+f'-{n}.log')).open('w') as log:
            subprocess.run(base+['--output',str(path),'--max-evaluations',str(n)]+(['--resume'] if resume else []),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    # Interrupt during real rendering, then wait for the atomic transaction.
    split=root/'split';log=(root/'signal.log').open('w')
    proc=subprocess.Popen(base+['--output',str(split)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    deadline=time.monotonic()+120
    while not (split/'candidates/000001.json.gz').exists():
        if proc.poll() is not None:raise RuntimeError('Child exited before interruption')
        if time.monotonic()>deadline:proc.kill();raise TimeoutError('No child progress')
        time.sleep(.2)
    proc.terminate();proc.wait(timeout=60);log.close()
    interrupted=read(split/'checkpoint.json');assert interrupted['stop_reason']=='signal'
    run(split,43,True)
    # Simulate the documented after-result/before-checkpoint crash by restoring
    # a pre-transaction checkpoint while retaining its immutable result file.
    crash=root/'crash';run(crash,42);before=read(crash/'checkpoint.json');run(crash,43,True)
    after=read(crash/'checkpoint.json');save(crash/'checkpoint.json',before);run(crash,43,True)
    a=read(split/'checkpoint.json');b=read(crash/'checkpoint.json')
    assert a['next_id']==b['next_id']==43
    for key in ['pool','rng','last_improvement','step_scale','seen']:assert a[key]==b[key],key
    assert b['pool']==after['pool']
    for i in range(43):
        x=read(split/'candidates'/f'{i:06d}.json.gz');y=read(crash/'candidates'/f'{i:06d}.json.gz')
        x.pop('seconds');y.pop('seconds');assert x==y,i
    save(ROOT/'photo2/r306/results/transaction-tests.json',dict(passed=True,real_sigterm=True,resume_proposals=43,
        post_write_crash_recovery=True,exact_scientific_records=True,temporary_artifacts=str(root)))
    print('R306 transaction tests passed',root)

if __name__=='__main__':main()

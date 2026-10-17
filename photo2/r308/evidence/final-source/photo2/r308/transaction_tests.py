"""Signal, cache replay and post-publication recovery on isolated outputs."""
import subprocess,time,os,signal
from pathlib import Path
from photo2.r297.common import ROOT,read,save,sha

def run():
    directory=Path('/tmp/beads-r308-transactions')/str(time.time_ns());directory.mkdir(parents=True)
    cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_hierarchical_fit.py'),'--output',str(directory),'--seconds','120','--no-review']
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r308-mpl')
    with (directory/'signal.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env);deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if (directory/'checkpoint.json').exists() and read(directory/'checkpoint.json')['next_id']>=1:break
            if proc.poll() is not None:raise RuntimeError('Exited before checkpoint')
            time.sleep(.1)
        proc.send_signal(signal.SIGTERM);proc.wait(timeout=30)
    first=read(directory/'checkpoint.json');assert first['stop_reason']=='signal';n=first['next_id'];old={p.name:sha(p) for p in (directory/'trials').glob('*.gz')}
    subprocess.run(cmd+['--resume','--max-evaluations',str(n+1)],env=env,stdout=subprocess.DEVNULL,check=True,timeout=60)
    second=read(directory/'checkpoint.json');assert second['next_id']==n+1 and second['elapsed']>=first['elapsed']
    for name,h in old.items():assert sha(directory/'trials'/name)==h
    extra=directory/'trials'/f"{second['next_id']:06d}.json.gz";save(extra,dict(incomplete_post_publication_fixture=True))
    subprocess.run(cmd+['--resume','--max-evaluations',str(n+2)],env=env,stdout=subprocess.DEVNULL,check=True,timeout=60)
    assert 'incomplete_post_publication_fixture' not in read(extra)
    final=read(directory/'checkpoint.json');result=dict(passed=True,actual_SIGTERM=True,committed_trials_byte_preserved=len(old),resume_added_trials=final['next_id']-n,published_uncommitted_fixture_recomputed=True,output=str(directory),policy='Cached committed trials replay without recomputation; interrupted deterministic stage repeats its decisions from committed records. Actual restart time charged. No claim of bitwise equality for budget-cutoff timing.')
    save(ROOT/'photo2/r308/results/transaction-tests.json',result);print(result,flush=True)
if __name__=='__main__':run()

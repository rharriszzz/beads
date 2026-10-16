"""Real signal/resume and post-publication crash contracts in isolated outputs."""
from pathlib import Path
import subprocess,time,os,signal,shutil
from photo2.r297.common import ROOT,read,save,sha

def run():
    output=Path('/tmp/beads-r307-transactions');output.mkdir(exist_ok=True)
    # Each invocation gets a fresh directory. Existing test evidence is retained.
    directory=output/str(time.time_ns());directory.mkdir()
    shutil.copyfile(ROOT/'photo2/r307/results/campaign/benchmark.json',directory/'benchmark.json')
    cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_guided_fit.py'),'--output',str(directory),'--seconds','90','--no-review']
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r307-mpl')
    with (directory/'signal.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if (directory/'checkpoint.json').exists() and read(directory/'checkpoint.json')['next_id']>=2:break
            if proc.poll() is not None:raise RuntimeError('Process exited before checkpoint')
            time.sleep(.1)
        proc.send_signal(signal.SIGTERM);proc.wait(timeout=30)
    first=read(directory/'checkpoint.json');assert first['stop_reason']=='signal';n=first['next_id'];old={p.name:sha(p) for p in (directory/'trials').glob('*.gz')}
    subprocess.run(cmd+['--resume','--max-evaluations',str(n+2)],env=env,stdout=subprocess.DEVNULL,check=True,timeout=60)
    second=read(directory/'checkpoint.json');assert second['next_id']==n+2 and second['elapsed']>=first['elapsed']
    for name,h in old.items():assert sha(directory/'trials'/name)==h
    # Published extra trial (e.g. crash after atomic result before checkpoint) is
    # recomputed from the committed incumbent; no trial is silently promoted.
    before=read(directory/'checkpoint.json');extra=directory/'trials'/f'{before["next_id"]:06d}.json.gz';save(extra,dict(incomplete_post_publication_fixture=True))
    subprocess.run(cmd+['--resume','--max-evaluations',str(before['next_id']+1)],env=env,stdout=subprocess.DEVNULL,check=True,timeout=60)
    assert 'incomplete_post_publication_fixture' not in read(extra)
    final=read(directory/'checkpoint.json')
    result=dict(passed=True,actual_SIGTERM=True,committed_trials_preserved=len(old),resume_added_trials=final['next_id']-n,post_publication_fixture_recomputed=True,output=str(directory),policy='Resume restarts an interrupted numerical block from the committed incumbent; it preserves published committed trials and charges actual additional work. Wall-time paths are not claimed bitwise identical to uninterrupted runs.')
    save(ROOT/'photo2/r307/results/transaction-tests.json',result);print(result,flush=True)
if __name__=='__main__':run()

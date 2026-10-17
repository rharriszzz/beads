"""Small real SIGTERM/resume and explicit orphan-publication fixture."""
from pathlib import Path
import os,signal,subprocess,tempfile,time
from photo2.r297.common import ROOT,read,save,sha,utc

def run():
    out=Path(tempfile.mkdtemp(prefix='beads-r312-recovery-'));log=out/'process.log'
    command=[str(ROOT/'.venv/bin/python'),str(ROOT/'photo2/phase2_minimax.py'),'--output',str(out),'--stage','1','--seconds','9']
    with log.open('w') as stream:
        process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        deadline=time.monotonic()+25
        while time.monotonic()<deadline and not list((out/'stage1/trials').glob('*.gz')) and process.poll() is None:time.sleep(.05)
        process.send_signal(signal.SIGTERM);process.wait(timeout=30)
        assert process.returncode==0,log.read_text()
        checkpoint=out/'stage1/checkpoint.json';state=read(checkpoint)
        assert state['stop_reason']=='signal' and not state['sealed']
        first_elapsed=state['elapsed'];files=sorted((out/'stage1/trials').glob('*.gz'));last=files[-1];row=read(last);before=sha(last)
        # Explicitly reproduce the state before publication was checkpointed.
        # This is a rollback fixture, not a claim of a real crash at that instant.
        state['next_id']=row['id'];state['pending']=dict(family=row['family'],parameters=row['parameters'],kind=row['kind'],step=row['step'])
        state['cache'].pop(row['key'],None);save(checkpoint,state)
        resumed=subprocess.run(command+['--resume'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=35)
        assert resumed.returncode==0,log.read_text()
    after=read(checkpoint);assert after['sealed'] and after['elapsed']>=first_elapsed
    assert sha(last)==before,'Published orphan trial was changed'
    keys=[read(p)['key'] for p in (out/'stage1/trials').glob('*.gz')];assert len(keys)==len(set(keys))
    result=dict(passed=True,utc=utc(),real_SIGTERM_clean_checkpoint=True,resume_preserves_cumulative_time=True,explicit_orphan_rollback_reused_without_changes=True,fixture_directory=str(out),first_elapsed=first_elapsed,final_elapsed=after['elapsed'],unique_trials=len(keys))
    dest=ROOT/'photo2/r312/evidence/implementation-checks';save(dest/'recovery.json',result);(dest/'recovery.log').write_text(log.read_text())
    print(result)

if __name__=='__main__':run()

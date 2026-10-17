"""Numerical scope and real process-recovery contracts for R311."""
import os,sys,tempfile,subprocess,time,signal,unittest
from pathlib import Path
from copy import deepcopy,copy
import numpy as np
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from .model import starts,scene,canonical,VARIABLES
from .search import broad_plan,physical

class Contracts(unittest.TestCase):
    def test_fields_and_discrete_hypotheses_are_frozen(self):
        seeds={s['name']:s for s in starts()}
        plan=broad_plan();self.assertEqual(len([p for p in plan if p['kind']=='sobol']),192)
        for job in plan:
            original=seeds[job['family']]['parameters']
            for key,value in job['parameters'].items():
                if key not in VARIABLES:self.assertEqual(value,original[key],(job['family'],key))
        self.assertEqual({p['family'] for p in plan if p['kind']=='map'},set(list(seeds)[:3]))
    def test_periodic_map_does_not_duplicate_endpoints(self):
        plan=broad_plan()
        for seed in starts()[:3]:
            values=sorted({p['parameters']['phase'] for p in plan if p.get('pair')==['phase','s0'] and p['family']==seed['name']})
            self.assertEqual(len(values),7)
            np.testing.assert_allclose(np.diff(np.r_[values,values[0]+2*np.pi]),2*np.pi/7,atol=1e-12)
    def test_R297_is_not_converted_to_R306(self):
        data,_,_=load();seed=starts()[0];s=scene(seed['parameters'],data,seed['implementation'])
        old=read(ROOT/seed['source']);np.testing.assert_allclose(s.centers,[b['center'] for b in old['positions']],atol=1e-11)
        p=deepcopy(seed['parameters']);p['phase']+=4*np.pi;q=canonical(p)
        self.assertAlmostEqual(q['phase'],seed['parameters']['phase'])
        for key,value in p.items():
            if key!='phase':self.assertEqual(value,q[key])
    def test_full_contact_rejection_has_a_solid_witness(self):
        data,_,_=load();seed=starts()[1];s=scene(seed['parameters'],data,seed['implementation'])
        # Two original annuli deliberately overlap; all other bodies removed
        # only inside this isolated contact-unit fixture.
        s.n=2;s.centers=s.centers[:2].copy();s.indices=s.indices[:2];s.g={k:v[:2].copy() for k,v in s.g.items()}
        for k in s.g:s.g[k][1]=s.g[k][0]
        s.centers[1]=s.centers[0]+np.array([.3,0,0])
        result=physical(s);self.assertFalse(result['certified']);self.assertEqual(result['state'],'witnessed-penetration')

class Transactions(unittest.TestCase):
    def test_SIGTERM_resume_and_trial_before_checkpoint_recovery(self):
        began=time.monotonic();receipts=[]
        with tempfile.TemporaryDirectory(prefix='beads-r311-recovery-') as temp:
            out=Path(temp)/'signal';log=Path(temp)/'signal.log'
            command=[sys.executable,str(ROOT/'photo2/phase2_basin_search.py'),'--output',str(out),'--seconds','120','--max-evaluations','3','--no-review']
            with log.open('w') as stream:
                process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=stream)
                for _ in range(1200):
                    if (out/'checkpoint.json').exists() and read(out/'checkpoint.json')['next_id']>=1:break
                    if process.poll() is not None:self.fail(log.read_text())
                    time.sleep(.1)
                process.send_signal(signal.SIGTERM);self.assertEqual(process.wait(timeout=40),0)
            state=read(out/'checkpoint.json');self.assertEqual(state['stop_reason'],'signal')
            before={p.name:sha(p) for p in (out/'trials').glob('*.gz')}
            result=subprocess.run(command+['--resume'],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(read(out/'checkpoint.json')['next_id'],3)
            for name,h in before.items():self.assertEqual(sha(out/'trials'/name),h)
            receipts.append(dict(SIGTERM=True,resume=True,completed_trials_unchanged=len(before)))
            orphan=Path(temp)/'orphan'
            code='''import os,sys
from pathlib import Path
from photo2.r311 import search
old=search.save
def crash(path,value):
    old(path,value)
    if Path(path).parent.name=='trials':os._exit(19)
search.save=crash
search.Runner(Path(sys.argv[1]),120,False,1).run()
'''
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r311-mpl')
            killed=subprocess.run([sys.executable,'-c',code,str(orphan)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
            self.assertEqual(killed.returncode,19,killed.stdout+killed.stderr)
            self.assertEqual(read(orphan/'checkpoint.json')['next_id'],0)
            trial=orphan/'trials/000000.json.gz';h=sha(trial)
            result=subprocess.run([sys.executable,str(ROOT/'photo2/phase2_basin_search.py'),'--output',str(orphan),'--seconds','120','--max-evaluations','1','--resume','--no-review'],cwd=ROOT,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(read(orphan/'checkpoint.json')['next_id'],1);self.assertEqual(sha(trial),h)
            receipts.append(dict(actual_process_exit_before_checkpoint=True,orphan_trial_recovered=True,duplicate_native_evaluations=0))
        save(ROOT/'photo2/r311/evidence/transaction-tests.json',dict(passed=True,receipts=receipts,seconds=time.monotonic()-began,scope='Original historical baseline replays only; separate preflight/recovery overhead, no new scientific proposals.'))

if __name__=='__main__':unittest.main()

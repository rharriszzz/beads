"""Reproduce R275 from frozen image-only upstream artifacts and the reference curve."""
import os,subprocess,sys,time,json
from .centerline_r275 import OUT,save

def main():
 resume=next((s.split('=',1)[1] for s in sys.argv if s.startswith('--from=')),None);active=resume is None
 start=time.time();env=dict(os.environ,MPLCONFIGDIR='/tmp/beads-r275-mpl');steps=[]
 for module,args in [('centerline',[]),('recover',[]),('black',['--refresh']),('pale',['--refresh']),('ownership',['--refresh']),('material',['--refresh']),('connected',['--refresh']),('core',['--refresh']),('dominance',['--refresh']),('reclassify',['--refresh']),('homogeneous',['--refresh']),('reflection',['--refresh']),('finalownership',['--refresh']),('dim',['--refresh']),('spacing',[]),('groups',[]),('residual',[]),('audit',[]),('review',[])]:
  if module==resume:active=True
  if not active:continue
  cmd=[sys.executable,'-m',f'photo2.bead_detection.{module}_r275',*args];t=time.time();print('start',module,flush=True)
  with (OUT/(module+'-run.log')).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,env=env)
  steps.append(dict(module=module,seconds=time.time()-t));print('finished',module,round(time.time()-t,2),flush=True)
 save('run.json',dict(resumed_from=resume,steps=steps,seconds=time.time()-start,commands='python -m photo2.bead_detection.run_r275'))
if __name__=='__main__':main()

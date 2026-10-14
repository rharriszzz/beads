"""Reproduce the scientific final round in a fresh output directory."""
import os,subprocess,sys
from .common import OUT,save,sha

def run(module,*args,**env):
    subprocess.run([sys.executable,'-m','photo2.r283.'+module,*args],check=True,env={**os.environ,**env})

def main():
    assert not (OUT/'phase1.json.gz').exists(),'Preserve completed experiments; choose a fresh R283_OUTPUT'
    run('ownership');run('coverage')
    run('benchmark',R283_SYNTHETIC_SEED='283501',R283_SYNTHETIC_SPLIT='synthetic')
    run('benchmark')
    for name in ('local','local-confirmation'):
        for action in ('select','fit','evaluate'):run('local',action,R283_LOCAL_NAME=name)
        run('controls',R283_LOCAL_NAME=name);run('render',R283_LOCAL_NAME=name)
    run('integrated')
    save(OUT/'pipeline-complete.json',dict(phase1_sha256=sha(OUT/'phase1.json.gz'),
        independent_confirmation=True,accepted_physical_identity=False,accepted_pattern=False))

if __name__=='__main__':main()

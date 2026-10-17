#!/usr/bin/env python3
"""R312 restartable two-stage minimax reconstruction and performance audit."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r312-mpl')
if Path(sys.prefix).resolve()!=ROOT/'.venv':
    os.execv(str(ROOT/'.venv/bin/python'),[str(ROOT/'.venv/bin/python'),str(Path(__file__).resolve()),*sys.argv[1:]])
sys.path.insert(0,str(ROOT))

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'photo2/r312/results/campaign')
    p.add_argument('--profile-only',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--stage',type=int,choices=[1,2],default=1);p.add_argument('--seconds',type=float,default=1800.)
    p.add_argument('--native-only',action='store_true',help='Use the exact native 1px lattice throughout Stage 2')
    p.add_argument('--finalize',action='store_true');p.add_argument('--verify',action='store_true')
    a=p.parse_args()
    from photo2.r297.common import run_lock
    with run_lock(a.output):
        if a.profile_only:
            from photo2.r312.benchmark import run
            run(a.output/'profiling');return
        if a.finalize:
            from photo2.r312.delivery import finalize
            finalize(a.output);return
        if a.verify:
            from photo2.r312.verify import run
            run(a.output);return
        from photo2.r312.search import Runner
        runner=Runner(a.output,a.stage,a.seconds,a.resume)
        if a.native_only:runner.state['native_only']=True
        runner.run()
if __name__=='__main__':main()

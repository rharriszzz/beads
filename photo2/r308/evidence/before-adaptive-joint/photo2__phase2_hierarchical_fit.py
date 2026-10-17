#!/usr/bin/env python3
"""R308 native global discovery, small corrections, diagnosis and verification."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r308-mpl')
if Path(sys.prefix).resolve()!=ROOT/'.venv':os.execv(str(ROOT/'.venv/bin/python'),[str(ROOT/'.venv/bin/python'),str(Path(__file__).resolve()),*sys.argv[1:]])
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'photo2/r308/results/campaign');p.add_argument('--seconds',type=float,default=1200);p.add_argument('--resume',action='store_true');p.add_argument('--review-only',action='store_true');p.add_argument('--no-review',action='store_true');p.add_argument('--max-evaluations',type=int,default=100000)
    a=p.parse_args();assert a.seconds>0
    from photo2.r297.common import run_lock
    with run_lock(a.output):
        if not a.review_only:
            from photo2.r308.search import Runner
            s=Runner(a.output,a.seconds,a.resume,a.max_evaluations).run()
            if s.get('stop_reason')=='signal':return
        if not a.no_review:
            from photo2.r308.delivery import finalize
            finalize(a.output)
if __name__=='__main__':main()

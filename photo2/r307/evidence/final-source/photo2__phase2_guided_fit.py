#!/usr/bin/env python3
"""R307: bounded fitting, diagnosis, verification, and offline native review."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r307-mpl')
if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():
    os.execv(str(ROOT/'.venv/bin/python'),[str(ROOT/'.venv/bin/python'),str(Path(__file__).resolve()),*sys.argv[1:]])
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'photo2/r307/results/campaign');ap.add_argument('--seconds',type=float,default=1140);ap.add_argument('--resume',action='store_true');ap.add_argument('--benchmark-only',action='store_true');ap.add_argument('--review-only',action='store_true');ap.add_argument('--no-review',action='store_true');ap.add_argument('--max-evaluations',type=int,default=100000)
    a=ap.parse_args()
    if a.seconds<=0:ap.error('seconds must be positive')
    from photo2.r297.common import run_lock
    with run_lock(a.output):
        from photo2.r307.search import Runner,benchmark
        if not a.review_only:
            if not (a.output/'benchmark.json').exists():benchmark(a.output)
            if a.benchmark_only:return
            state=Runner(a.output,a.seconds,a.resume,a.max_evaluations).run()
            if state['stop_reason']=='signal':return
        if not a.no_review:
            from photo2.r307.delivery import finalize
            finalize(a.output)
if __name__=='__main__':main()

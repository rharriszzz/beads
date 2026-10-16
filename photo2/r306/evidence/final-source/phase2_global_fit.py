#!/usr/bin/env python3
"""R306 automated full-circuit geometry, search, diagnosis and native review."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():
    python=ROOT/'.venv/bin/python'
    if not python.exists():raise SystemExit(f'Repository Python missing: {python}')
    os.execv(str(python),[str(python),str(Path(__file__).resolve()),*sys.argv[1:]])
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'photo2/r306/results/campaign')
    ap.add_argument('--seconds',type=float,default=3600.,help='Cumulative fitting budget; export/verification separate')
    ap.add_argument('--seed',type=int,default=306)
    ap.add_argument('--max-evaluations',type=int,default=100000)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--initialize-from',type=Path,help='New run: reevaluate a prior checkpoint population under this run; preserve the source run')
    ap.add_argument('--review-only',action='store_true')
    ap.add_argument('--no-review',action='store_true')
    ap.add_argument('--native-seconds',type=float,default=0.,help='Additional final training-only native refinement budget, before selection is sealed')
    ap.add_argument('--serve',action='store_true');ap.add_argument('--port',type=int,default=8306)
    args=ap.parse_args()
    if args.seconds<=0 or args.max_evaluations<1:ap.error('Budgets must be positive')
    if args.resume and args.initialize_from:ap.error('Use --resume or --initialize-from, not both')
    from photo2.r297.common import run_lock
    with run_lock(args.output):
        from photo2.r306.pack import restore
        if args.resume or args.review_only:restore(args.output)
        if args.initialize_from:restore(args.initialize_from)
        if not args.review_only:
            from photo2.r306.search import Runner
            state=Runner(args.output,args.seconds,args.seed,args.resume,args.max_evaluations,args.initialize_from).run()
            if state['stop_reason']=='signal':return
        if not args.no_review:
            from photo2.r306.export import finalize
            finalize(args.output,args.native_seconds)
    if args.serve:
        from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
        from functools import partial
        print(f'Open http://127.0.0.1:{args.port}/review/',flush=True)
        ThreadingHTTPServer(('127.0.0.1',args.port),partial(SimpleHTTPRequestHandler,directory=str(args.output))).serve_forever()

if __name__=='__main__':main()

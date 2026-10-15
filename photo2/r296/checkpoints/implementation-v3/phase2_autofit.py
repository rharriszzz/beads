#!/usr/bin/env python3
"""One-command launcher: automatically use this repository's Python environment."""
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
PYTHON=ROOT/'.venv/bin/python'
if Path(sys.prefix).resolve() != (ROOT/'.venv').resolve():
    if not PYTHON.exists():
        raise SystemExit(f'Repository environment missing: {PYTHON}')
    os.execv(str(PYTHON),[str(PYTHON),str(Path(__file__).resolve()),*sys.argv[1:]])
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def main():
    import argparse
    from photo2.r296.common import read
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preset',choices=['smoke','medium','long'],default='medium')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/phase2-autofit')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--hours',type=float)
    parser.add_argument('--seconds',type=float)
    parser.add_argument('--max-evaluations',type=int)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--population',type=int)
    parser.add_argument('--patience',type=int)
    parser.add_argument('--min-delta',type=float)
    parser.add_argument('--count-min',type=int)
    parser.add_argument('--count-max',type=int)
    parser.add_argument('--seal',action='store_true',help='Freeze finalists, expose reserved cases, and disallow further resume')
    parser.add_argument('--review-only',action='store_true',help='Regenerate review from existing checkpoint; no optimization')
    parser.add_argument('--no-review',action='store_true',help='Skip export/review (useful for deterministic tests)')
    parser.add_argument('--serve',action='store_true',help='Serve output/review after generating it, on localhost')
    parser.add_argument('--port',type=int,default=8296)
    args=parser.parse_args()
    if args.hours is not None and args.seconds is not None:parser.error('Use --hours or --seconds, not both')
    if args.population is not None and args.population<4:parser.error('Population must be at least four to preserve hand/topology families')
    presets={'smoke':(120,8),'medium':(1800,600),'long':(14400,100000)}
    seconds,evaluations=presets[args.preset]
    settings=dict(seed=args.seed,population=args.population,patience=args.patience,min_delta=args.min_delta,
        count_min=args.count_min,count_max=args.count_max,
        seconds=args.seconds if args.seconds is not None else args.hours*3600 if args.hours is not None else seconds,
        max_evaluations=args.max_evaluations if args.max_evaluations is not None else evaluations)
    if not args.resume:
        defaults=dict(seed=296,population=8,patience=256,min_delta=.0005)
        for k,v in defaults.items():
            if settings[k] is None:settings[k]=v
    for k in ('seconds','max_evaluations','patience','min_delta'):
        if settings[k] is not None and settings[k]<=0:parser.error(k+' must be positive')
    if args.seal and args.no_review:parser.error('--seal requires review/export')
    if args.resume and (args.count_min is not None or args.count_max is not None):parser.error('Count bounds are frozen at run creation')
    if not args.review_only:
        from photo2.r296.search import Runner
        runner=Runner(args.output,settings,resume=args.resume);state=runner.run()
        print(f"Stopped: {state['stop_reason']}; {state['next_id']} proposals; {state['elapsed_seconds']:.1f}s cumulative search",flush=True)
        if state['stop_reason']=='signal':
            print('Interrupted safely; checkpoint saved. Resume later or use --review-only.',flush=True)
            return
    if not args.no_review:
        from photo2.r296.review import finalize
        finalize(args.output,seal=args.seal)
        print('Review: '+str(args.output.resolve()/'review/index.html'),flush=True)
    elif args.seal:parser.error('--seal requires review/export')
    if args.serve:
        from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
        from functools import partial
        print(f'Open http://127.0.0.1:{args.port}/review/',flush=True)
        ThreadingHTTPServer(('127.0.0.1',args.port),partial(SimpleHTTPRequestHandler,directory=str(args.output))).serve_forever()

if __name__=='__main__':main()

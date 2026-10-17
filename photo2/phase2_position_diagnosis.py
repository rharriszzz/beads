#!/usr/bin/env python3
"""R310 autonomous diagnostic pipeline; no optimization entry or parameter changes."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
venv=ROOT/'.venv/bin/python'
if Path(sys.prefix)!=ROOT/'.venv':os.execv(str(venv),[str(venv),str(Path(__file__).resolve()),*sys.argv[1:]])
sys.path.insert(0,str(ROOT))
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r310-mpl')
import argparse,time
from photo2.r297.common import save
from photo2.r310.analysis import OUT
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['all','partA','curvature','review','verify'],default='all');a=p.parse_args();timings={}
def run(label,fn):
    t=time.monotonic();fn();timings[label]=time.monotonic()-t;print(label,timings[label],flush=True)
if a.stage in ['all','partA']:
    from photo2.r310.analysis import analyze
    from photo2.r310.controls import controls
    run('partA',analyze);run('partA_controls',controls)
if a.stage in ['all','curvature']:
    from photo2.r310.curvature import main
    run('curvature_after_partA',main)
if a.stage in ['all','review']:
    from photo2.r310.report import main as report
    from photo2.r310.visuals import build
    from photo2.r310.plots import main as plots
    run('report',report);run('atlas_viewer',build);run('plots',plots)
if a.stage in ['all','verify']:
    from photo2.r310.verify import verify
    run('verify',verify)
save(OUT/f'workflow-{a.stage}.json',dict(seconds=timings,fit_evaluations=0,geometry_mutations=0))

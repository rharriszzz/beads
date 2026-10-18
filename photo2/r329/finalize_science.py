from .common import *
from .closed_checks import periods
from datetime import datetime,timezone

def main():
 g=read(ROOT/'photo2/r328/results/graph.json.gz');novel=read(OUT/'novel-windings.json.gz')['alternatives'];paths=sorted((OUT/'traversals').glob('*.json.gz'))+[OUT/'novel-windings.json.gz'];save(OUT/'final-photographic-freeze.json',dict(utc=datetime.now(timezone.utc).isoformat(),hashes={str(p.relative_to(ROOT)):sha(p) for p in paths},policy='All completed and failed growth outputs frozen before period checks on newly retained windings. No further search authorized automatically.'))
 t=time.perf_counter();rows=[]
 for z in novel:rows.extend(periods(z['state'],g,'new-H-'+str(z['H'])))
 save(OUT/'novel-periods.json.gz',dict(results=rows,seconds=time.perf_counter()-t,policy='Same post-freeze rules as periods.json.gz; no color input to inference.'))
 save(OUT/'science-seal.json',dict(utc=datetime.now(timezone.utc).isoformat(),sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r329').glob('*.py')) if p.name not in ['verify.py','browser_check.py']},inputs={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads-photo-2.jpg',ROOT/'beads.pov',ROOT/'photo2/r328/results/graph.json.gz',ROOT/'photo2/r328/results/alternatives.json.gz',ROOT/'photo2/r328/results/alternative-consequences.json.gz',ROOT/'photo2/r328/development/final256/prepared.json.gz',ROOT/'photo2/r327/results/graph.json.gz']},policy='Search and inference stop here; verification and documentation may add outputs. Historical science stays unchanged.'))
 print('SCIENCE SEALED',datetime.now(timezone.utc).isoformat(),flush=True)
if __name__=='__main__':main()

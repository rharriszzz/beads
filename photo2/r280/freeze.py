"""Freeze after development; never select rules using held-out data."""
from datetime import datetime,timezone
from .common import OUT,ROOT,read,save,sha
from .evaluate import summary
from .detector import DEFAULT

def main():
 if (OUT/'freeze.json').exists():raise RuntimeError('Existing freeze must not be overwritten')
 records=read(OUT/'dev-evaluation.json.gz')['records'];curves={}
 for method in 'ABC':
  curves[method]=[]
  for threshold in (.55,.60,.65,.70,.75,.80,.85,.90,.95,1.01):
   selected=[r for r in records if r['method']==method and r['tier']=='easy' and (r['test']=='A1' or r['false'] and r['kind']!='unanchored-neighbor')]
   curves[method].append(dict(threshold=threshold,**summary(selected,threshold)))
 chosen=.65
 easy=summary([r for r in records if r['method']=='C' and r['tier']=='easy' and r['test']=='A1'],chosen)
 assert easy['precision']>=.90 and easy['recall']>=.60
 paths=[p for p in (ROOT/'photo2/r280').glob('*.py') if p.name not in ('review.py','analysis.py')]+[ROOT/'photo2/r280/PROTOCOL.md']
 save(OUT/'freeze.json',dict(time_utc=datetime.now(timezone.utc).isoformat(),thresholds=DEFAULT,principal='C',curves=curves,easy_gate=easy,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths},selection='Development easy A1 plus contextual false alternatives: .65 retains >=98% precision with .10 margin above lowest tested qualifying threshold .55. Strong needs >=40 measured pixels; tiny fragments remain partial. A2/A3 and identity-permutation failures do not justify growth. No high-precision claim for arbitrary wrong geometry.',heldout='Not rendered or evaluated before freeze.',initial_control='development-v1 contains original .80/8px detector and every output. Empty initial easy stratum retained separately.'))
 print(easy)
if __name__=='__main__':main()

"""Explicitly authorize recorded final-joint adaptation after the initial run."""
from pathlib import Path
import json,gzip,hashlib,shutil
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3];out=ROOT/'photo2/r308/results/campaign';archive=ROOT/'photo2/r308/evidence/before-adaptive-joint'
state=json.loads((out/'checkpoint.json').read_text())
assert state['stop_reason']=='four complete joint blocks without improvement',state.get('stop_reason')
assert state['elapsed']<1150 and not state['sealed']
archive.mkdir(exist_ok=False)
for name,h in state['sources'].items():
 p=ROOT/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
 shutil.copyfile(p,archive/name.replace('/','__'))
shutil.copyfile(out/'checkpoint.json',archive/'checkpoint.json')
shutil.copyfile(ROOT/'photo2/r308/results/campaign.log',archive/'campaign.log')
shutil.copyfile(ROOT/'photo2/R308_SPECIFICATION.md',archive/'R308_SPECIFICATION.md')
p=ROOT/'photo2/r308/search.py';s=p.read_text().replace("files=[BASE/'search.py',BASE/'objective.py',ROOT/'photo2/phase2_hierarchical_fit.py']", "files=[BASE/'search.py',BASE/'objective.py',BASE/'native_refine.py',ROOT/'photo2/phase2_hierarchical_fit.py']");p.write_text(s)
p=ROOT/'photo2/phase2_hierarchical_fit.py';s=p.read_text().replace("if s.get('stop_reason')=='signal':return", "if s.get('stop_reason')=='signal':return\n            if all(k in s['stages'] for k in ['global','distributed','joint']) and s['elapsed']<a.seconds-3:\n                from photo2.r308.native_refine import run\n                s=run(a.output,a.seconds,a.max_evaluations)\n                if s.get('stop_reason')=='signal':return")
p.write_text(s)
new=dict(state['sources'])
for name in ['photo2/r308/search.py','photo2/r308/native_refine.py','photo2/phase2_hierarchical_fit.py']:new[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
transition=dict(utc=datetime.now(timezone.utc).isoformat(),elapsed=state['elapsed'],first_new_trial=state['next_id'],archive=str(archive.relative_to(ROOT)),old_sources=state['sources'],new_sources=new,reason='Pre-comparison adaptive final joint step sizes after failed large-scale linear predictions; same1200s cumulative budget. Objective, evidence, geometry, owners and acceptance guards unchanged.',protocol='photo2/r308/evidence/adaptive-protocol.md')
state['sources']=new;state['source_transitions']=[transition]
(out/'checkpoint.json').write_text(json.dumps(state,separators=(',',':'))+'\n')
(ROOT/'photo2/r308/evidence/adaptive-transition.json').write_text(json.dumps(transition,indent=2)+'\n')
print('Source transition recorded at',state['elapsed'],'seconds; next trial',state['next_id'])

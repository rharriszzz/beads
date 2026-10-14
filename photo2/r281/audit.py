"""Source provenance, historical preservation and independent output audits."""
import platform,subprocess
from pathlib import Path
import numpy as np
from .common import ROOT,OUT,read,save,sha

def main():
 changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines();allowed={'AGENTS.md','SESSION_HANDOFF.md','PLAN.md','REQUEST_LOG.md','METHODS.md'}
 assert all(p in allowed or p.startswith(('photo2/r281/','photo2/review/r281/')) or p=='photo2/R281_PRESENCE.md' for p in changed),changed
 sources=['beads-photo-2.jpg','beads.pov','photo2/review/r278/phase1-inventory.json.gz','photo2/review/r278/phase1-positions.csv','photo2/r279/geometry.py','photo2/bead_placement.py','photo2/r280/detector.py','photo2/r280/contact.py','photo2/r280/geometry.py','photo2/r280/synthetic.py','photo2/r280/evaluate.py']
 old=[p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines() if p not in allowed and not p.startswith(('photo2/r281/','photo2/review/r281/')) and p!='photo2/R281_PRESENCE.md'];assert not set(old)&set(changed)
 scenes=[]
 for split in ('dev','heldout'):
  for f in sorted((OUT/split).glob('scene-*')):
   d=read(f/'truth.json');assert d['certificate']['certified'];targets=read(f/'evaluation-targets.json')['targets'];records=read(f/'inference.json.gz');assert len(records)==15*len(targets)
   for row in records:
    if row['kind']=='removed' and row['level']==0:
     present=next(r for r in records if r['query_target']==row['query_target'] and r['kind']=='present' and r['level']==0);assert row['hypothesis']==present['hypothesis']
   scenes.append(dict(split=split,scene=f.name,targets=len(targets),minimum_gap=d['certificate']['minimum_gap_units'],projection=d['projection_check']))
 save(OUT/'audit.json',dict(base_commit='f180991af5843362ebd948bcf9af4d2f6bf7219a',historical_files_unchanged=len(old),source_hashes={p:sha(ROOT/p) for p in sources},r281_source_hashes={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'photo2/r281').glob('*.py')},scene_audits=scenes,python=platform.python_version(),platform=platform.platform(),phase1_anchor_provenance={'C-0585-1605':'image-only R273','C-0541-1602':'image-only R273','C-0565-1588':'image-only R273','E5-0562-1620':'R275 automatic band recovery'},excluded_inputs=['manual neighbor answers','numbered construction charts','maker-confirmed physical identities','historical poses','global centerline fits','color patterns']))
 print('historical unchanged',len(old),'scenes',len(scenes))
if __name__=='__main__':main()

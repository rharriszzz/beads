"""Final preservation and source/evidence provenance, no scientific mutation."""
import subprocess
from photo2.r297.common import ROOT,read,save,sha,utc
from .analysis import BASE,OUT,MODELS

def main():
    old=read(BASE/'evidence/preservation.json.gz');head=read(BASE/'evidence/start.json')['head'];additive=[]
    for p,h in old.items():
        if sha(ROOT/p)!=h:
            assert p in ['AGENTS.md','METHODS.md','PLAN.md','REQUEST_LOG.md'],p
            before=subprocess.check_output(['git','show',head+':'+p]);assert before in (ROOT/p).read_bytes(),p;additive.append(p)
    src=list(BASE.glob('*.py'))+[ROOT/'photo2/phase2_position_diagnosis.py']+list((ROOT/'photo2/review/r310').glob('*.js'))+[ROOT/'photo2/review/r310/serve.py',ROOT/'photo2/review/r310/launch.sh']
    save(OUT/'source-manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in src})
    inputs={}
    for name,(folder,stem) in MODELS.items():
        for suffix in ['.json.gz','-raster.npz']:
            p=ROOT/folder/f'{stem}{suffix}';inputs[str(p.relative_to(ROOT))]=sha(p)
    for p in ['beads-photo-2.jpg','photo2/r296/evidence/inputs.json.gz','photo2/r283/results/phase1.json.gz','photo2/r306/evidence.py','photo2/r306/geometry.py','photo2/r309/geometry.py','photo2/r307/kernel.cpp','photo2/r297/geometry.py','photo2/r298/geometry.py','photo2/r299/forward.py','photo2/r294/evidence/inputs.json.gz','photo2/r298/evidence/measurements.json','photo2/r299/evidence/measurements.json.gz']:inputs[p]=sha(ROOT/p)
    save(OUT/'input-manifest.json',inputs)
    for name in ['verification','browser-check']:assert read(OUT/f'{name}.json')['passed']
    for rel in read(OUT/'summary.json')['links'].values():assert (OUT/rel).exists(),rel
    result=dict(passed=True,utc=utc(),preserved_files=len(old),byte_identical=len(old)-len(additive),additive_handoffs=additive,historical_science_changed=[],fit_evaluations=0,models_unchanged=True,source_files=len(src),input_files=len(inputs),summary_links=True)
    save(OUT/'final-integrity.json',result);print(result)
if __name__=='__main__':main()

"""Replay frozen experiment into a new R281_OUTPUT directory."""
import os,shutil
from .common import ROOT,OUT,read,save
from . import synthetic,run,analyze,real_select,real_fit,real_evaluate

def main():
 original=ROOT/'photo2/r281/results'
 assert 'R281_OUTPUT' in os.environ and OUT.resolve()!=original.resolve(),'Set R281_OUTPUT to a new output directory'
 assert not OUT.exists() or not any(OUT.iterdir()),'Replay directory must be empty'
 OUT.mkdir(parents=True,exist_ok=True)
 for name in ('freeze.json','benchmark-amendment.json'):shutil.copyfile(original/name,OUT/name)
 for split in ('dev','heldout'):
  synthetic.generate(split);run.main(split,'all');analyze.main(split)
 real_select.main();real_fit.main();real_evaluate.main()
 checks={}
 for name in ('dev-frozen-summary.json','heldout-frozen-summary.json','real/prediction-freeze.json','real/measurements.json'):
  checks[name]=read(OUT/name)==read(original/name)
 save(OUT/'replay-check.json',checks);assert all(checks.values()),checks;print(checks)
if __name__=='__main__':main()

"""Fresh full render and exact comparison of reproducible R345 artifacts."""
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ARTIFACTS=['scene.pov','scene.inc','shape.inc','beads.inc','beads.json','contacts.json','validation.json','projected-support-errors.csv','provenance.json','render.png','comparison.jpg','geometry-transparent.png','geometry-overlay.jpg','indices-full.jpg','helicity-detail.png']+[f'crop-{name}.jpg' for name in ['straight','bend','reference','lower-bend']]

def compare(fresh):
    rows=[]
    for name in ARTIFACTS:
        a=(HERE/'output'/name).read_bytes();b=(fresh/name).read_bytes()
        if a!=b:raise AssertionError('Fresh replay differs: '+name)
        rows.append(dict(path=name,sha256=hashlib.sha256(a).hexdigest(),bytes=len(a)))
    result=dict(fresh_directory=str(fresh),exact_artifacts=len(rows),artifacts=rows,all_passed=True,exclusions='Runtime logs and command receipts contain time/path information; separate verification scenes are not pipeline outputs.')
    (HERE/'output/replay-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--existing',type=Path);a=ap.parse_args()
    if a.existing:compare(a.existing.resolve());return
    with tempfile.TemporaryDirectory(prefix='r345-replay-') as temp:
        out=Path(temp);env=dict(os.environ,OPENBLAS_NUM_THREADS='1')
        subprocess.run([sys.executable,str(HERE/'render.py'),'--output',str(out)],check=True,env=env)
        compare(out)
if __name__=='__main__':main()

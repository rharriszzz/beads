"""Independent output directory: exact inference, baseline and one fresh POV replay."""
from pathlib import Path
from .common import *

def main():
    temp=Path('/tmp/beads-r289-replay');temp.mkdir(exist_ok=True)
    from . import detect_photo,baseline,synthetic
    detect_photo.OUT=temp;detect_photo.main();baseline.OUT=temp;baseline.main()
    for name in ('photo-landmarks.json.gz','historical-replay.json'):
        assert sha(temp/name)==sha(OUT/name),name
    plan=read(OUT/'synthetic-plan.json');plan['scenes']=plan['scenes'][:1];save(temp/'synthetic-plan.json',plan);synthetic.OUT=temp;synthetic.run()
    names=('on-inference.json.gz','off-inference.json.gz','photo.png','diffuse.png','specular.png','identity.png','evaluation.json')
    for name in names:assert sha(temp/'synthetic/scene-00'/name)==sha(OUT/'synthetic/scene-00'/name),name
    save(OUT/'replay.json',dict(exact=['photo-landmarks.json.gz','historical-replay.json']+['synthetic/scene-00/'+n for n in names],temporary_directory=str(temp),meaning='Second independent full-image inference, historical recalculation and fresh rendering of one synthetic scene; not twelve new scenes.'))
    print('Nine exact replay files')
if __name__=='__main__':main()

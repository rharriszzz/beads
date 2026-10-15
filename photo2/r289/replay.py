"""Independent output directory: exact inference, baseline and one fresh POV replay."""
from pathlib import Path
from .common import *

def main(recompute=True):
    temp=Path('/tmp/beads-r289-replay');temp.mkdir(exist_ok=True)
    from . import detect_photo,baseline,synthetic
    if recompute:
        detect_photo.OUT=temp;detect_photo.main();baseline.OUT=temp;baseline.main()
    for name in ('photo-landmarks.json.gz','historical-replay.json'):
        assert sha(temp/name)==sha(OUT/name),name
    plan=read(OUT/'synthetic-plan.json');plan['scenes']=plan['scenes'][:1];save(temp/'synthetic-plan.json',plan);synthetic.OUT=temp
    if recompute:synthetic.run()
    names=('on-inference.json.gz','off-inference.json.gz','evaluation.json')
    from PIL import Image
    images=('photo.png','diffuse.png','specular.png','identity.png')
    for name in images:np.testing.assert_array_equal(np.asarray(Image.open(temp/'synthetic/scene-00'/name)),np.asarray(Image.open(OUT/'synthetic/scene-00'/name)))
    for name in names:assert sha(temp/'synthetic/scene-00'/name)==sha(OUT/'synthetic/scene-00'/name),name
    save(OUT/'replay.json',dict(exact=['photo-landmarks.json.gz','historical-replay.json']+['synthetic/scene-00/'+n for n in names],exact_rasters=list(images),png_metadata='Render Date differs; four decoded native pixel arrays match exactly.',temporary_directory=str(temp),meaning='Second independent full-image inference, historical recalculation and fresh rendering of one synthetic scene; not twelve new scenes.'))
    print('Five byte-exact files and four exact raster arrays')
if __name__=='__main__':
    import sys
    main('--verify-only' not in sys.argv)

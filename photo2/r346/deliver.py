"""Render the selected R346 lighting with the sealed R345 necklace unchanged."""
from .shadows import *
from concurrent.futures import ThreadPoolExecutor
from .analysis import analyze
from .report import main as write_report
from .color_profile_check import main as check_color_profile

def render_all(destination,width=W,height=H):
    destination=Path(destination);destination.mkdir(exist_ok=True,parents=True)
    params=read(HERE/'config.json')['parameters']
    for path,digest in read(OUT/'input-seal.json').items():assert sha(ROOT/path)==digest,path
    scene(params,destination/'scene.pov','full')
    scene(params,destination/'clear.pov','clear')
    scene(dict(original=True,position=[-300,350,850],diameter=75),destination/'R345-clear.pov','clear')
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(run_pov,destination/'scene.pov',width,height,True,'render.png'),pool.submit(run_pov,destination/'clear.pov',width,height,True),pool.submit(run_pov,destination/'R345-clear.pov',width,height,True)]
        for job in jobs:job.result()
    save(destination/'render-receipt.json',dict(parameters=params,width=width,height=height,source_commit=read(OUT/'measurement-freeze.json')['source_commit'],render_sha256=sha(destination/'render.png'),scene_sha256=sha(destination/'scene.pov'),bead_transforms_sha256=sha(BASE/'beads.inc'),shape_sha256=sha(BASE/'shape.inc'),camera_unchanged=True,png_date_metadata_removed=True))
    return destination

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);ap.add_argument('--size',type=int,nargs=2,default=[W,H]);ap.add_argument('--analyze-only',action='store_true');args=ap.parse_args()
    if not args.analyze_only:render_all(args.output,*args.size)
    analyze(args.output)
    if args.output.resolve()==OUT.resolve():
        check_color_profile()
        write_report()
if __name__=='__main__':main()

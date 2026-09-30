"""Independent source-macro/POV visibility check of an adjustable spline pose."""
import argparse,json
from pathlib import Path
from tangent_circles import ROOT,load_model,render_model,sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parameters',type=Path,default=ROOT/'photo2/output/r175/fit/parameters.json')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r175/fit-check')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    config=json.loads(args.parameters.read_text());model=load_model(config,config['parameters'])
    check=render_model(model,args.output,name='registered',circle_radius=config['circle_radius'])
    report=dict(parameters_sha256=sha(args.parameters),checker_sha256=sha(Path(__file__)),
        kernel_sha256=sha(ROOT/'photo2/tangent_circles.py'),source_scene_sha256=sha(ROOT/'beads.pov'),
        parameters=config['parameters'],check=check,
        meaning='Independent forward model/point-visibility agreement only; not validation of photo bead identities or N/camera/helicity.')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(visible_anchors=check['visible_anchors'],same_ray_check=check['independent_same_ray_check']),indent=2))


if __name__=='__main__':main()

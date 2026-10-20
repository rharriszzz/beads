"""Reproduce the global lighting candidate grid; cached renders are optional."""
from .shadows import *

def candidates(stage):
    if stage=='coarse':
        rows=[dict(id='R345',position=[-300,350,850],diameter=75,original=True)]
        rows += [dict(id=f'x{x}_y{y}_d350',position=[x,y,850],diameter=350) for x,y in [(-300,-400),(-500,-400),(-700,-400),(-300,-650),(-500,-650),(-700,-650),(-900,-650),(-500,-850),(-700,-850)]]
        rows += [dict(id=f'x-500_y-650_d{d}',position=[-500,-650,850],diameter=d) for d in [150,550,800]]
        rows += [dict(id=f'height{z}',position=[-500*z/850,-650*z/850,z],diameter=350*z/850) for z in [500,1500]]
        return rows
    if stage=='refine':
        return ([dict(id=f'refine_x{x}',position=[x,-700,4000],diameter=2400) for x in [-2500,-3750,-6250]]+
                [dict(id=f'refine_y{y}',position=[-3750,y,4000],diameter=2400) for y in [-200,-1200]]+
                [dict(id=f'refine_x{x}_d{d}',position=[x,-700,4000],diameter=d) for x in [-2500,-3750,-5000] for d in [4000,6000]])
    if stage=='wide':return [dict(id=f'wide_x{x}_d{d}',position=[x,-700,4000],diameter=d) for x,d in [(-5000,8000),(-5000,9500),(-7500,6000),(-7500,8000),(-10000,6000),(-10000,8000)]]
    if stage=='final':return [dict(id=f'final_x{x}_y{y}_d{d}',position=[x,y,4000],diameter=d) for x,y,d in [(-5000,-1700,6000),(-5000,-2700,6000),(-5000,300,6000),(-4500,-700,6000),(-5500,-700,6000),(-5000,-700,5000),(-5000,-700,7000)]]
    raise ValueError(stage)

def sweep(stage):
    profiles=read(OUT/'profiles.json.gz')['profiles'];work=Path('/tmp/r346-shadow-trials');work.mkdir(exist_ok=True);rows=[]
    for params in candidates(stage):
        folder=work/params['id'];cache=folder/'ratio.npy'
        ratio=np.load(cache) if cache.exists() else pass_images(params,folder)
        if not cache.exists():np.save(cache,ratio)
        pred=rendered_profiles(ratio,profiles);metrics=score(pred,profiles,fit_alpha=not params.get('original',False))
        feature_rows=[]
        for r,v in zip(profiles,pred):
            if r['eligible'] and r['photo_metrics']['reliable']:
                d=np.array(r['distance']);use=d>=r['paper_guard'];feature_rows.append(profile_metrics(d[use],v[use]*metrics['alpha']))
        metrics['feature_medians']={k:float(np.median([r[k] for r in feature_rows if r.get(k) is not None])) for k in ['extent_5percent_px','penumbra_10_90_px','near_edge_darkness']}
        rows.append(dict(parameters=params,metrics=metrics));print(params['id'],metrics['fit']['robust_loss'],flush=True)
    file={'coarse':'optimization.json','refine':'refinement.json','wide':'wide-refinement.json','final':'final-refinement.json'}[stage]
    if stage=='coarse':save(OUT/file,dict(policy='One global key source/diameter and one global contrast proxy; three quarters geographic stations fit, every fourth reserved. Both sides and unshadowed controls retained. No pigment-based observation selection.',trials=rows))
    else:save(OUT/file,rows)
    return rows
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['coarse','refine','wide','final','all']);args=ap.parse_args()
    for stage in (['coarse','refine','wide','final'] if args.stage=='all' else [args.stage]):sweep(stage)

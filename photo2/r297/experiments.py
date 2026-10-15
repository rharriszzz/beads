"""Equal-budget objective ablations and native development comparisons."""
import argparse
import shutil
from .common import *
from .search import Runner
from .geometry import Chain
from .review import native_observations,summarize


def settings(n,mode='balanced'):
    return dict(seed=297,population=8,patience=512,min_delta=.0005,count_min=None,count_max=None,seconds=1800,max_evaluations=n,objective=mode)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=128);args=ap.parse_args()
    archive=BASE/'checkpoints/development-v1';archive.mkdir(parents=True,exist_ok=True)
    for p in BASE.glob('*.py'):shutil.copyfile(p,archive/p.name)
    shutil.copyfile(ROOT/'photo2/phase2_autofit.py',archive/'phase2_autofit.py')
    outcomes=[]
    for mode in ['legacy','balanced','no-patches','no-boundaries']:
        out=BASE/'results'/('ablation-'+mode)
        runner=Runner(out,settings(args.trials,mode));state=runner.run()
        best=read(out/'candidates'/f"{state['pool'][0]:06d}.json.gz")
        obs=native_observations(Chain(best['parameters'],runner.data),runner.data,['train','validation'])
        localids={r['id'] for r in read(ROOT/'photo2/r295/results/R295-evaluation.json')['observations']}
        result=dict(mode=mode,budget=args.trials,id=best['id'],parameters=best['parameters'],
            selected_metrics={s:best[s] for s in ['train','validation']},native=obs,
            summary={s:{k:summarize([r for r in obs if r['split']==s and r['kind']==k]) for k in ['region','patch']} for s in ['train','validation']},
            historical_regions=summarize([r for r in obs if r['id'] in localids and r['kind']=='region']))
        save(out/'development.json.gz',result);outcomes.append(result)
        print('ABLATION',mode,result['summary'],result['historical_regions'],flush=True)
    save(BASE/'results/ablations.json.gz',outcomes)

if __name__=='__main__':main()

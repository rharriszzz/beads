"""Profile actual photo objectives, not synthetic training scenes."""
import cProfile
import pstats
import time
from .common import *
from .geometry import Chain,full_parameters,contact
from .objective import Objective


def main():
    data=read(EVIDENCE/'inputs.json.gz');p=full_parameters(read(ROOT/'photo2/r295/results/hand-plus-evaluation.json')['parameters'],2709)
    rows=[]
    for tier in ('coarse','fine'):
        obj=Objective(data,tier=tier);pr=cProfile.Profile();pr.enable();start=time.perf_counter()
        for _ in range(4):
            scene=Chain(p,data);cert=contact(scene);result=obj.assess(scene,discrete=tier!='coarse')
        elapsed=time.perf_counter()-start;pr.disable()
        with (BASE/'checkpoints'/f'full-{tier}-profile.txt').open('w') as f:pstats.Stats(pr,stream=f).sort_stats('cumtime').print_stats(30)
        rows.append(dict(tier=tier,calls=4,seconds=elapsed,seconds_per_candidate=elapsed/4,rays_per_candidate=len(obj.xy),score=result['score'],contact=cert['state']))
    save(BASE/'results/full-profile.json',dict(records=rows,old=read(BASE/'results/r295-profile.json'),
        approach='Cached reference/camera splines and photo arrays, cKDTree spatial bounds, sampled supports; inherited vectorized first hits. Serial transactional search; no unmeasured parallel speedup claim.'))
    print(rows)

if __name__=='__main__':main()

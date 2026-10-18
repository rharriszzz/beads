"""Shared finite-source controls on fixed Stage 1 geometry and assignments."""
from copy import deepcopy
from photo2.r297.common import read,save,utc
from .detect import OUT
from .optics import Engine,objective
from .search import compact

def main():
    for folder in [OUT,OUT/'epoch2']:
        trials=[read(p) for p in (folder/'trials').glob('*.gz')];base=min(trials,key=lambda r:r['objective_px']);epoch=read(folder/'epoch.json');engine=Engine(epoch);rows=[]
        for inv in [0.,.0003,.001,.003,.01]:
            for da in [-20.,0.,20.]:
                for de in [-10.,0.,10.]:
                    p=deepcopy(base['parameters']);p.update(light_inverse=inv,light_az=p['light_az']+da,light_el=p['light_el']+de)
                    r=compact(engine.evaluate(p));r.update(parameters=p,parent=base['id'],utc=utc(),objective_px=objective(r));rows.append(r)
        best=min(rows,key=lambda r:r['objective_px']);save(folder/'finite-light-controls.json.gz',dict(parent=base['id'],geometry_held_fixed=True,rows=rows,best=best,base_emax=base['emax_px']))
        save(folder/'light-seed.json.gz',best)
        print(folder.name,'FINITE',base['emax_px'],'->',best['emax_px'],'inverse',best['parameters']['light_inverse'],flush=True)

if __name__=='__main__':main()

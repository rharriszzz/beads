"""One common extended source; fixed-geometry exact-max controls."""
from copy import deepcopy
from photo2.r297.common import read,save,utc
from .detect import OUT
from .optics import Engine,objective
from .search import compact

def main():
    for folder in [OUT,OUT/'epoch2']:
        trials=[read(p) for p in (folder/'trials').glob('*.gz')];base=min(trials,key=lambda r:r['objective_px']);engine=Engine(read(folder/'epoch.json'));rows=[]
        for width in [5.,15.,30.]:
            for da in [-10.,0.,10.]:
                for de in [-5.,0.,5.]:
                    p=deepcopy(base['parameters']);p.update(light_inverse=0.,light_width=width,light_az=p['light_az']+da,light_el=p['light_el']+de)
                    r=compact(engine.evaluate(p));r.update(parameters=p,parent=base['id'],utc=utc(),objective_px=objective(r));rows.append(r)
        best=min(rows,key=lambda r:r['objective_px']);save(folder/'extended-light-controls.json.gz',dict(parent=base['id'],geometry_held_fixed=True,rows=rows,best=best,base_emax=base['emax_px']))
        save(folder/'extended-seed.json.gz',best)
        print(folder.name,'EXTENDED',base['emax_px'],'->',best['emax_px'],'width',best['parameters']['light_width'],flush=True)

if __name__=='__main__':main()

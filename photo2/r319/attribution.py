"""Frozen-map geometry/light factorial controls at delivered parameter settings."""
from copy import deepcopy
from photo2.r318 import optics
from photo2.r318.search import compact
from .common import *
from .evidence import Evidence,gate

def main():
    epoch=read(OLD/'epoch2/epoch.json');b=read(OUT/'baseline.json.gz');f=read(OUT/'best-full.json.gz');eng=optics.Engine(epoch);ev=Evidence(epoch);rows=[]
    for geometry in [False,True]:
        for light in [False,True]:
            p=deepcopy(f['parameters'] if geometry else b['parameters'])
            for k in optics.LIGHT_KEYS:
                source=f['parameters'] if light else b['parameters']
                if k in source:p[k]=source[k]
                else:p.pop(k,None)
            r,s,a=eng.evaluate(p,True);r=compact(r);r['geometry']=ev.measure(s);r['acceptance']=gate(r['geometry'],b['geometry']);rows.append(dict(final_geometry=geometry,final_light=light,parameters=p,result=r))
    save(OUT/'geometry-light-factorial.json.gz',rows);print([(r['final_geometry'],r['final_light'],r['result']['emax_px']) for r in rows],flush=True)
if __name__=='__main__':main()

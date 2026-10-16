"""Post-seal diagnostics only: no selection or optimization."""
from copy import deepcopy
import numpy as np
from .evidence import BASE,ROOT,read,save
from .model import Local,NAMES,AXES
from .objective import secondary
from photo2.r299.forward import Surface
from photo2.r298.geometry import outlines
from photo2.r297.common import load_evidence

def main():
    records=read(BASE/'results/native-manifest.json.gz');sections={s['id']:s for s in read(BASE/'evidence/frozen.json.gz')['sections']};inputs,_=load_evidence()
    for r in records:
        d=r['result'];s=sections[r['section']]
        if d.get('baseline'):
            scene=Surface(d['parameters'],inputs);scene.polygons=lambda:outlines(scene);ss=deepcopy(s);ss['cues']={k:[x for x,h in zip(v,s['cues']['withheld']) if h] for k,v in s['cues'].items() if k!='withheld'};ss['profiles']=[];ss['bead_dimensions']=[];ss['separators']=next(x['records'] for x in read(BASE/'evidence/withheld-separators.json')['sections'] if x['section']==s['id']);d['withheld_material']=secondary(scene,ss,2)
        else:
            ext=d['guard_extension'];d['physical_accepted']=ext['physical']['certified'];ext['failed_pair_surface_audits']=[]
            if not d['physical_accepted']:
                scene=Local([d['parameters'][n] for n in NAMES],s,d['hand'],guards=64);points,_=scene.samples(1)
                for w in ext['physical']['witnesses']:
                    if w['separated']:continue
                    a,b=w['pair'];mn=0
                    for j,k in [(a,b),(b,a)]:
                        delta=points[j]-scene.centers[k];q=np.stack([delta@scene.g[key][k] for key in AXES],axis=1);mn=min(mn,float(scene.local_sdf(q).min()))
                    ext['failed_pair_surface_audits'].append(dict(indices=[int(scene.indices[a]),int(scene.indices[b])],minimum_sampled_signed_distance=mn,demonstrated_penetration=mn<-.0001))
        save(BASE/f'results/native-{r["name"]}.json.gz',r)
    save(BASE/'results/native-manifest.json.gz',records)

if __name__=='__main__':main()

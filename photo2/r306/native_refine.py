"""Small final training-only correction stage using exact native predictions."""
from pathlib import Path
from copy import deepcopy
import time
import numpy as np
from photo2.r297.common import read,save,utc,sha
from photo2.r297.geometry import reference
from .geometry import Chain,valid
from .objective import Objective,predict,contour_samples

def refine(out,start,data,m,obs,seconds):
    from .export import native_envelope,native_assess
    directory=Path(out)/'native-refinement';directory.mkdir(exist_ok=True)
    progress=directory/'checkpoint.json';obj=Objective(data,m,obs);obj.contour_samples=contour_samples([m['beads'][i] for i in obj.bi],1.)
    state=read(progress) if progress.exists() else dict(start_id=start['id'],best=start,base=start,next_id=0,elapsed_seconds=0.,history=[],complete=False,
        source_sha256=sha(__file__),created=utc(),budget_seconds=seconds)
    if state['source_sha256']!=sha(__file__):raise ValueError('Native refinement source changed')
    if state['complete']:return state['best']
    before=state['elapsed_seconds'];t=time.monotonic()
    while before+time.monotonic()-t<max(0,seconds-15):
        i=state['next_id'];path=directory/f'candidate-{i:03d}.json.gz'
        if i%2==0:state['base']=state['best']
        base=state['base'];p=deepcopy(base['parameters']);sign=-1 if i%2==0 else 1;group=(i//2)%6
        scene=Chain(p,data)
        if group in (0,1,4,5):
            informative=sorted([r for r in base['train']['sections'] if r['n']>=4],key=lambda r:r['containment'])
            section=informative[(i//12)%min(4,len(informative))]['section']
            rows=[r for r in obj.photo.rows if int(r['station']/data['length']*32)%32==section]
            point=np.mean([r['point'] for r in rows],axis=0)
            key='local_phase' if group in (0,4) else 'axis_nodes';delta=sign*(.025 if key=='local_phase' else .5)
            if key=='axis_nodes':k=int(round(reference().project([point])['arc'][0]/reference().length*32))%32
            else:k=int(round((scene.indices[scene.tree.query(point)[1]]/scene.n+.5)%1*32))%32
            for off,w in [(-1,.35),(0,1.),(1,.35)]:p[key][(k+off)%32]+=delta*w
            operation=f'{key}[{k}] {delta:+g}, region {section}'
        else:
            key='axial' if group==2 else 'light_az';delta=sign*(.012 if key=='axial' else 2.);p[key]+=delta;operation=f'{key} {delta:+g}'
        if path.exists():row=read(path)
        else:
            t0=time.monotonic();row=dict(id=f'native-{i}',source=str(path.relative_to(out)),parameters=p,parent=base['id'],operation=operation,status='bounds-rejected',loss=None)
            if valid(p):
                try:
                    s=Chain(p,data);cert=s.certify(iterations=100,witnesses=True);row['contact']=cert
                    if cert['certified']:
                        pred,meta=predict(s,1.,obj.obs);en=native_envelope(s,m);result=native_assess(s,obj,pred,en)
                        row.update(status='eligible',loss=result['loss'],train=result,numerics=meta)
                    else:row.update(status='physical-rejected',penetration=s.penetration(cert))
                except ValueError as error:row.update(status='numerical-rejected',error=str(error))
            row['seconds']=time.monotonic()-t0;save(path,row)
        if row['status']=='eligible' and row['loss']<state['best']['loss']:state['best']=row
        state['history'].append(dict(id=row['id'],status=row['status'],loss=row['loss'],seconds=row['seconds'],best=state['best']['loss']))
        state['next_id']=i+1;state['elapsed_seconds']=before+time.monotonic()-t;save(progress,state)
        print('native refinement',i,operation,row['status'],row['loss'],'best',state['best']['loss'],flush=True)
    state['elapsed_seconds']=before+time.monotonic()-t;state['complete']=True;save(progress,state)
    return state['best']

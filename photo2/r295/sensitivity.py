"""Training-only paired factor controls and optional common-light refinement."""
from copy import deepcopy
import numpy as np
from photo2.r282.geometry import unit
from .common import *
from .geometry import Chain,extend,R
from .fit import Objective,refine

def mirror(scene,data,split='train'):
    rows=[r for r in data['rows'] if r['kind']=='patch' and r['reflection'] and r['split']==split]
    if not rows:return dict(n=0,mean_cosine=0.,median_angle=None,evidence=[])
    xy=np.array([r['point'] for r in rows]);d=scene.trace(xy,True);o=d['owner'];keep=o>=0;normal=d['normal'][keep]
    eye=unit(scene.eye-(d['points'][keep]/scene.distance)) if np.isfinite(scene.distance) else np.tile(scene.eye,(keep.sum(),1))
    v=unit(2*np.sum(normal*eye,axis=1)[:,None]*normal-eye)
    # One contribution per owner: multiple highlights do not create repeated votes.
    owners=np.unique(o[keep]);directions=np.array([unit(v[o[keep]==k].mean(0)) for k in owners]);light=unit(np.median(directions,axis=0))
    angles=np.degrees(np.arccos(np.clip(v@light,-1,1)))
    return dict(n=len(v),owners=len(owners),direction=light.tolist(),mean_cosine=float(np.mean(directions@light)),median_angle=float(np.median(angles)),evidence=[dict(id=r['id'],index=int(scene.indices[k]),direction=q.tolist(),angle=float(a)) for r,k,q,a in zip(np.array(rows,dtype=object)[keep],o[keep],v,angles)],limits='Conditional mirror-direction dispersion; flags can include diffuse maxima, illumination may be extended, no calibrated BRDF or black-body centers.')

class LightObjective(Objective):
    def assess(self,p,physical=True,details=False):
        r=super().assess(p,physical,details)
        if r['feasible']:
            light=mirror(Chain(p,self.inputs),self.data);r['photographic_score_without_light']=r['score'];r['light']=light;r['score']+=.035*light['mean_cosine']
        return r

def main():
    data=read(EVIDENCE/'inputs.json.gz');p=read(OUT/'revision.json')['selected']['parameters'];base=extend(read(ROOT/'photo2/r294/results/revised.json')['selected']['parameters']);obj=Objective(version=2);controls=[]
    changes=[('fixed R294',{}),('thickness alone',dict(axial=.85)),('spacing alone',dict(pitch=1.12)),('paired thickness spacing',dict(axial=.85,pitch=1.12)),
        ('legacy radius alone',dict(radius=2.1109157489)),('legacy paired spacing scale',dict(radius=2.1109157489,pitch=1.50,scale=8.3*1.26/1.50)),
        ('legacy expanded rope',dict(radius=2.1109157489,pitch=1.50,scale=8.3*1.26/1.50,minor=4.3,turn=6.35))]
    for name,changeset in changes:
        q=deepcopy(base);q.update(changeset);controls.append(dict(name=name,parameters=q,train=obj.assess(q)))
    # Sensitivities change one physical factor at a time around the selected fit.
    for key,d in [('radius',.04),('axial',.04),('pitch',.025),('turn',.025),('minor',.15),('elevation',4.),('yaw',8.),('perspective',.001),('phase',.12)]:
        for sign in (-1,1):
            q=deepcopy(p);q[key]+=sign*d
            if key=='perspective' and q[key]<0:continue
            controls.append(dict(name=f'{key} {sign*d:+g}',parameters=q,train=obj.assess(q)))
    light=LightObjective(version=2);result=refine(light,p,[('phase',.06),('s0',1.),('elevation',2.),('axial',.02)],steps=(1.,.5))
    save(OUT/'sensitivity.json',dict(controls=controls,source_hashes=source_hashes(),training_only=True))
    save(OUT/'light-alternative.json',dict(selected=result,source_hashes=source_hashes(),training_only=True,
        selection='Diagnostic alternative only; common mirror-direction assumption is not sufficiently established to override material/boundary selection.'))
    print('light alternative',result['train']['light']['median_angle'],'photo score',result['train']['photographic_score_without_light'])
if __name__=='__main__':main()

"""Frozen-artifact audit and local identifiability, without synthetic truth."""
from pathlib import Path
import platform,subprocess
import numpy as np
import scipy,skimage,PIL
from .run import OUT,ROOT,read,save,sha
from .geometry import centers,project,contact,R,PITCH

def vector(p):return np.array([*p['translation'],p['roll'],np.log(p['scale']),p['phase'],p['inclination'],p['pitch']])
def unpack(x,p):return {**p,'translation':x[:2].tolist(),'roll':x[2],'scale':np.exp(x[3]),'phase':x[4],'inclination':x[5],'pitch':x[6]}

def main():
    results=[];count=0;fourths=0
    for folder in [OUT/'real']+sorted(OUT.glob('scene-*')):
        if not (folder/'pairs.json.gz').exists():continue
        for pair in read(folder/'pairs.json.gz'):
            f=folder/pair['before_C'];d=read(f);s=read(folder/pair['after_C']);assert sha(f)==s['frozen_sha256'];count+=1
            for h in d['hypotheses']:
                p=h['parameters'];x=vector(p);eps=np.array([.001,.001,.001,.00001,.00001,.001,.00001]);cols=[]
                for j,step in enumerate(eps):
                    lo=x.copy();hi=x.copy();lo[j]-=step;hi[j]+=step
                    def fun(z):
                        pp=unpack(z,p);return project(pp,centers([0,h['delta']],pp['hand'],pp['phase'],pp['pitch'])).ravel()
                    cols.append((fun(hi)-fun(lo))/(2*step))
                J=np.array(cols).T;_,sv,vh=np.linalg.svd(J,full_matrices=True);rank=int(np.sum(sv>1e-6))
                norm=J/np.maximum(np.linalg.norm(J,axis=0),1e-12);cor=norm.T@norm
                results.append(dict(folder=folder.name,pair=f.name,hand=h['hand'],delta=h['delta'],rank=h['rank'],AB_jacobian_rank=rank,continuous_parameters=7,AB_nullity=7-rank,singular_values=sv.tolist(),null_vectors=vh[rank:].tolist(),parameter_order=['tx','ty','roll_degrees','logscale','phase_radians','inclination_degrees','pitch_factor'],column_cosines=cor.tolist()))
            for df in pair['before_D']:
                ds=read(folder/df.replace('-before-D.json.gz','-after-D.json'));assert sha(folder/df)==ds['frozen_sha256'];fourths+=1
    save(OUT/'identifiability.json.gz',results)
    obs=read(OUT/'real/observations.json.gz');assert all(o['physical_center'] is None for o in obs);assert all(10<=len(o['pixels'])<=870 for o in obs)
    projection=read(OUT/'synthetic-scenes/projection-check.json')
    save(OUT/'audit.json',dict(C_freezes_verified=count,D_freezes_verified=fourths,real_native_masks=len(obs),real_physical_centers_invented=0,AB_rank_counts={str(r):sum(x['AB_jacobian_rank']==r for x in results) for r in range(5)},intended_radius=R,source_step=PITCH,contact={str(x):contact(x) for x in (.95,1.,1.05,1.10)},projection_rays=sum(x['rays'] for x in projection),projection_unknown=sum(x['unknown'] for x in projection),projection_resolved_agreement=min(x['agreement'] for x in projection)))
    save(OUT/'environment.json',dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__,pillow=PIL.__version__,povray=subprocess.run(['povray','--version'],capture_output=True,text=True).stderr[:2500],platform=platform.platform()))
if __name__=='__main__':main()

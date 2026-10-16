"""Saved R249 reciprocal vectors versus local physical lattice derivatives.

Absolute axes are x-right/y-up as in R249 offsets (FFT array row = center-dy).
No extracted peak, family assignment, count or hand is imposed by this diagnostic.
"""
import itertools
import numpy as np
from .calibrate import BASE
from .geometry import AXES,unit
from photo2.r297.common import ROOT,read,sha

def diagnostic(scene):
    records=read(ROOT/'photo2/review/r249/transfer.json')['records'];out=[]
    axis=scene.project(scene.line)
    for rec in records:
        if rec['variant']!='primary':continue
        i=int(np.argmin(np.linalg.norm(axis-rec['xy'],axis=1)));k=scene.indices[i]
        line,g,ph=scene.placement(np.array([k-.05,k,k+.05]));t=g[AXES[0]][1];normal=g[AXES[1]][1];z=np.array([0,0,1.]);advance=np.linalg.norm(line[2]-line[0])/.1;angular=(ph[2]-ph[0])/.1
        front=np.arctan2(scene.eye@normal,scene.eye@z);pred=[]
        for rho in [scene.p['minor'],scene.p['minor']+scene.radius]:
            for off in [-20,0,20]:
                theta=front+np.radians(off);circ=np.cos(theta)*normal-np.sin(theta)*z;origin=line[1]+rho*(np.sin(theta)*normal+np.cos(theta)*z)
                world=np.column_stack([advance*t+rho*angular*circ,6*advance*t+rho*(6*angular-scene.p['hand']*2*np.pi)*circ])
                eps=1e-4;center=scene.project(origin[None])[0];a=np.column_stack([(scene.project((origin+eps*world[:,j])[None])[0]-center)/eps for j in range(2)]);a[1]*=-1
                if abs(np.linalg.det(a))<1e-6:continue
                b=np.linalg.inv(a).T;vectors=np.array([b[:,1],b[:,0],b[:,0]-b[:,1]])
                direct=np.array([a[:,0],a[:,1],a[:,0]+a[:,1]])
                ps=rec['peaks'][:4];observed=np.array([p['frequency']*np.array([np.cos(np.radians(p['angle'])),np.sin(np.radians(p['angle']))]) for p in ps]);matches=[]
                for perm in itertools.permutations(range(len(ps)),3):
                    for harmonic in [1.,.5,2.]:
                        errors=[min(np.linalg.norm(harmonic*v-observed[j]),np.linalg.norm(harmonic*v+observed[j]))/ps[j]['frequency_resolution'] for v,j in zip(vectors,perm)]
                        matches.append(dict(candidates=[ps[j]['candidate'] for j in perm],harmonic=harmonic,rms_resolution=float(np.sqrt(np.mean(np.square(errors)))),maximum_resolution=float(max(errors))))
                matches.sort(key=lambda x:x['rms_resolution'])
                pred.append(dict(radius=rho,front_offset_deg=off,direct_vectors_px=direct.tolist(),reciprocal_vectors_cycles_px=vectors.tolist(),best=matches[0],fundamental_best=min((r for r in matches if r['harmonic']==1),key=lambda r:r['rms_resolution']),passing=[r for r in matches if r['maximum_resolution']<=2]))
        out.append(dict(window=rec['window'],channel=rec['channel'],xy=rec['xy'],saved_tangent_deg=rec['tangent_deg'],observed=rec['peaks'][:4],saved_supported_trios=rec.get('trios',[]),predictions=pred,best=min((p['best']['rms_resolution'] for p in pred),default=None)))
    return dict(source='photo2/review/r249/transfer.json',source_sha256=sha(ROOT/'photo2/review/r249/transfer.json'),records=out,convention='A=[v1 v6]; B=A^-T; normals of rows1/6/7 = b2,b1,b1-b2. x right,y up. ± reciprocal signs equivalent. Harmonic .5/1/2 alternatives explicit.',limits='Local unrolled tangent approximation, curvature and exposed surface latitude uncertain. Optimistic matching of unassigned peaks, not hand/count evidence or validation accuracy.')

"""Local interruption alternatives evaluated against both sides of their new edge."""
import numpy as np
from scipy import ndimage as ndi

def select(m,strict,soft):
    added=soft&~strict;labels,n=ndi.label(added,np.ones((3,3)));relax=np.zeros_like(strict);records=[]
    for i in range(1,n+1):
        comp=labels==i;old=[];new=[]
        for axis,f in enumerate(m['fields']):
            if axis==0:
                cut=(strict[:,:-1]&comp[:,1:])|(comp[:,:-1]&strict[:,1:]);outer=(comp[:,:-1]&~soft[:,1:])|(~soft[:,:-1]&comp[:,1:])
            else:
                cut=(strict[:-1,:]&comp[1:,:])|(comp[:-1,:]&strict[1:,:]);outer=(comp[:-1,:]&~soft[1:,:])|(~soft[:-1,:]&comp[1:,:])
            for result,sel in ((old,cut),(new,outer)):
                y,x=np.where(sel);A=f['A_dark_seam'][y,x];B=f['B_multiscale'][y,x];C=f['C_material'][y,x];D=f['D_continuity'][y,x]
                conflict=(D>.6)&(A<.22)&(C<.18);support=((A>=.22)|(B>=.22)|(C>=.18))&~conflict
                result.extend(zip(support.tolist(),conflict.tolist()))
        old_support=sum(v[0] for v in old);new_support=sum(v[0] for v in new);old_conflict=sum(v[1] for v in old)
        # A local hypothesis replaces a continuity-conflicted cut only when its
        # alternative edge does not increase unresolved evidence. No area/shape gate.
        allow=bool(old and new and old_conflict>=len(old)/2 and len(new)-new_support<=len(old)-old_support and new_support>=old_support)
        if allow:relax|=comp
        records.append(dict(pixels=int(comp.sum()),old_cut_sides=len(old),old_supported=old_support,old_continuity_conflicts=old_conflict,new_outer_sides=len(new),new_supported=new_support,locally_relaxed=allow,reason='Continuity-conflicted interruption; replacement adds no unresolved sides' if allow else 'Alternative creates additional unresolved edge or cuts supported material'))
    return relax,records

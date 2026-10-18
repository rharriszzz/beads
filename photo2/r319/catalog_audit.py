"""Replay the complete detected-component audit of conditional interval27..46."""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r306.evidence import load
from photo2.r318.optics import Chain
from photo2.r315.model import refined_trace
from .common import *

def main():
    p=read(OLD/'epoch2/best.json.gz')['parameters'];s=Chain(p,load()[0]);js=np.flatnonzero((s.indices>=27)&(s.indices<=46));tree=cKDTree(s.pc[js]);epoch=read(OLD/'epoch2/epoch.json');doc=read(OLD/'observations.json.gz');rows=[]
    for o in doc['observations']:
        if tree.query(o['point'])[0]>s.query_radius+19:continue
        xy=np.array(o['component']['pixels']);tr=refined_trace(s,xy);owners,ns=np.unique(tr['owner'][tr['owner']>=0],return_counts=True);alts=[dict(index=int(s.indices[j]),fraction=float(n/len(xy))) for j,n in zip(owners,ns)];support=sum(a['fraction'] for a in alts if 27<=a['index']<=46)
        rows.append(dict(id=o['id'],eligible=o['eligible'],point=o['point'],color=o['color'],reasons=o['exclusion_reasons'],in_primary=o['id'] in epoch['mapping'],primary_index=epoch['mapping'].get(o['id']),alternatives=alts,interval_support=support))
    result=dict(interval=[27,46],records=rows,policy='Every detected component whose center lies within a conservative projected sphere plus19px window of any interval body checked against full-scene visible component support. Eligibility is inherited photo-only reliability; identity is still provisional.')
    path=OUT/'small-complete-catalog-audit.json'
    if path.exists():assert result==read(path),'Saved catalog audit changed'
    save(path,result)
if __name__=='__main__':main()

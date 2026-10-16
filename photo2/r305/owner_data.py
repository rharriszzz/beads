"""Offline-safe native owner data; no canvas readback of file:// images required."""
import json
import numpy as np
from .model import *

def main():
    data={}
    for name in FAMILIES:
        doc=np.load(BASE/f'results/{name}-raster.npz');a=doc['address'];flat=a.ravel();edges=np.r_[0,np.flatnonzero(np.diff(flat)!=0)+1,len(flat)];runs=[[int(i),int(j-i),int(flat[i])] for i,j in zip(edges,edges[1:]) if flat[i]!=-32768]
        decoded=np.full(flat.shape,-32768,np.int16)
        for i,n,k in runs:decoded[i:i+n]=k
        np.testing.assert_array_equal(decoded,flat);data[name]=dict(width=a.shape[1],height=a.shape[0],runs=runs)
    (REVIEW/'owners.js').write_text('const OWNERS='+json.dumps(data,separators=(',',':'))+';\n')
if __name__=='__main__':main()

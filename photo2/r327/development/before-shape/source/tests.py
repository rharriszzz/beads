"""Meaningful controls: target leakage, curvature, sequence dependence, faint RGB."""
import numpy as np
from .evidence import predict,evaluate,maps

def main():
    ab=np.array([(a,b) for a in range(5) for b in range(3)],float);xy=ab@np.array([[30.,8.],[12.,-24.]])+[80,140];train=np.arange(1,len(ab));p=predict(ab,xy,0,train)
    assert np.linalg.norm(p-xy[0])<1e-8
    corrupt=xy.copy();corrupt[0]+=[100,200];assert np.allclose(p,predict(ab,corrupt,0,train))
    curved=xy.copy();curved[:,1]+=1.5*(ab[:,0]-2)**2
    linear_error=np.linalg.norm(predict(ab,curved,7,np.delete(np.arange(len(ab)),7))-curved[7]);curved_error=np.linalg.norm(predict(ab,curved,7,np.delete(np.arange(len(ab)),7),True)-curved[7]);assert curved_error<linear_error
    rgb=np.zeros((300,300,3));op={};assign={}
    for i,(a,pt) in enumerate(zip(ab,xy)):
        o=str(i);op[o]=dict(xy=pt.tolist(),color='black' if i==7 else 'red');assign[o]=dict(ab=a.astype(int).tolist());x,y=np.rint(pt).astype(int);rgb[y-1:y+2,x-1:x+2]=[.08,.08,.08] if i==7 else [.8,.1,.1]
    h=dict(assignments=assign);ev=evaluate(h,op,maps(rgb));row=next(r for r in ev['rows'] if r['observation']=='7');assert row['anchor_kind']=='colored supports only' and '7' not in row['anchor_ids'];assert row['observed_native_response']>0
    assert ev['sequence']>0
    bad={o:dict(v) for o,v in op.items()};bad['7']['xy']=(xy[7]+[15,15]).tolist();worse=evaluate(h,bad,maps(rgb));assert worse['score']<ev['score']
    from .compatibility import cycle_audit
    # A long shared prefix is not part of the inconsistent triangle.
    links=[(0,1,np.array([0,0]),0),(1,2,np.array([0,0]),0),(2,3,np.array([0,0]),0),(3,4,np.array([0,0]),0),(2,4,np.array([1,0]),0)]
    bad,audit=cycle_audit(set(range(5)),links);assert bad and all(0 not in c and 1 not in c for c in bad)
    import unittest
    from photo2.r326 import tests as inherited
    from . import compatibility as current
    for name in ('reconsider','compatible_subset','relations','cycle_audit'):setattr(inherited,name,getattr(current,name))
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(inherited.Contracts));assert result.wasSuccessful()
    print('PASS target exclusion, shared curved geometry, colored-only black prediction, faint native response, sequence corruption')
if __name__=='__main__':main()

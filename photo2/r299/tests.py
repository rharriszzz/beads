import unittest
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
from .common import *
from .forward import *
from photo2.r279.geometry import SURFACE

def isolated(axial=.83,perspective=0.):
    s=Surface.__new__(Surface);s.n=1;s.centers=np.zeros((1,3));s.radius=R;s.axial=axial;s.dims=np.array([axial,1,1]);s.bound=R*np.sqrt(1+(.7*axial)**2);s.scale=18.;s.offset=np.array([50.,50.]);s.right=np.array([1.,0,0]);s.down=np.array([0,1.,0]);s.eye=np.array([0,0,1.]);s.distance=1/perspective if perspective else np.inf;s.g=dict(zip(AXES,[np.array([[1.,0,0]]),np.array([[0.,1,0]]),np.array([[0.,0,1]])]));s.indices=np.array([0]);s.pc=s.project(s.centers);s.tree=cKDTree(s.pc);s.query_radius=s.bound*s.scale*1.4;return s

class ForwardTests(unittest.TestCase):
    def test_affine_normals(self):
        for axial in [.55,.83,1.12]:
            s=isolated(axial);q=SURFACE*s.dims
            fd=np.stack([(s.local_sdf(q+np.eye(3)[j]*1e-6)-s.local_sdf(q-np.eye(3)[j]*1e-6))/2e-6 for j in range(3)],axis=1)
            np.testing.assert_allclose(normal_local(q,s.dims),unit(fd),atol=2e-6)
    def test_normal_transform_and_perspective(self):
        data,_=load_evidence();p=read(ROOT/'photo2/r298/results/model-49.json.gz')['parameters'];p=deepcopy(p);p['perspective']=.001
        s=Surface(p,data);xy=s.pc[:40];a=s.camera(xy);b=s.trace(xy,normals=True);ok=a['owner']>=0
        np.testing.assert_allclose(a['normal'][ok],b['normal'][ok],atol=2e-5)
        np.testing.assert_allclose(s.project(a['points'][ok]),xy[ok],atol=1e-9)
        self.assertTrue(np.all(np.sum(a['normal'][ok]*a['viewer'][ok],axis=1)>0))
    def test_hole_and_flat_face(self):
        s=isolated();s.right=np.array([0.,1.,0]);s.down=np.array([0.,0.,1.]);s.eye=np.array([1.,0,0]);s.pc=s.project(s.centers);s.tree=cKDTree(s.pc)
        tr=s.camera([[50,50],[50+R*.57*s.scale,50]])
        self.assertEqual(tr['owner'][0],-1);self.assertEqual(tr['owner'][1],0)
        np.testing.assert_allclose(tr['normal'][1],[1,0,0],atol=1e-6)
    def test_shadow_segment_and_neighbors(self):
        s=isolated();points=np.array([[0.,R*.57,3.]])
        self.assertTrue(s.blocked(points,np.array([0.,0.,-1.]))[0][0])
        self.assertFalse(s.blocked(points,np.array([[0.,0.,-1.]]),np.array([.1]))[0][0])
        self.assertFalse(s.blocked(points,np.array([0.,0.,1.]))[0][0])
        p=np.array([[3.,0,0]]);self.assertFalse(s.blocked(p,np.array([-1.,0,0]))[0][0])
    def test_known_light_reflection_law(self):
        s=isolated();yy,xx=np.mgrid[10:91:.5,10:91:.5];tr=s.camera(np.c_[xx.ravel(),yy.ravel()]);light=light_params([90,65,4.],'directional',np.zeros(3));val=shade(s,tr,light)['intensity'];i=val.argmax();n=tr['normal'][i];v=tr['viewer'][i];l=np.array(light['direction']);reflection=2*np.dot(n,l)*n-l
        self.assertLess(np.degrees(np.arccos(np.clip(np.dot(reflection,v),-1,1))),5)
        self.assertIsNotNone(highlight(tr['xy'],val,.5))
    def test_synthetic_light_recovery(self):
        s=isolated();yy,xx=np.mgrid[15:86:1,15:86:1];tr=s.camera(np.c_[xx.ravel(),yy.ravel()]);truth=[68.,61.,9.];target=shade(s,tr,light_params(truth,'directional',np.zeros(3)),shadows=False)['intensity']
        def fun(v):return shade(s,tr,light_params(v,'directional',np.zeros(3)),shadows=False)['intensity']-target
        result=least_squares(fun,[75,55,11],bounds=([-180,10,2],[180,89,20]),max_nfev=35)
        np.testing.assert_allclose(result.x,truth,atol=1e-4)
    def test_finite_infinity_limit(self):
        s=isolated(perspective=.001);yy,xx=np.mgrid[20:81:2,20:81:2];tr=s.camera(np.c_[xx.ravel(),yy.ravel()]);a=shade(s,tr,light_params([70,60,8],'directional',np.zeros(3)))['intensity'];b=shade(s,tr,light_params([70,60,8,1e8],'finite',np.zeros(3)))['intensity'];np.testing.assert_allclose(a,b,atol=2e-7)
    def test_extended_zero_limit(self):
        s=isolated();tr=grids(s,[0],2);a=shade(s,tr,light_params([80,65,8],'directional',np.zeros(3)))['intensity'];b=shade(s,tr,light_params([80,65,8,0],'extended',np.zeros(3)))['intensity'];np.testing.assert_array_equal(a,b)
    def test_self_and_neighbor_shadow_ids(self):
        s=isolated();p=np.array([[0.,0.,R+.001]])
        self.assertEqual(s.blocked(p,np.array([0.,0.,-1.]))[1][0],0)
        self.assertFalse(s.blocked(p,np.array([0.,0.,1.]))[0][0])
        s.centers=np.array([[0.,0.,0.],[0.,0.,4.]])
        s.g={key:np.repeat(value,2,axis=0) for key,value in s.g.items()};s.n=2
        blocked,owner,unknown=s.blocked(p,np.array([0.,0.,1.]))
        self.assertTrue(blocked[0]);self.assertEqual(owner[0],1);self.assertEqual(unknown,0)
    def test_missing_denominator_and_quantiles(self):
        from .experiment import summary
        rows=[dict(exists=i==0,peak_error_px=1. if i==0 else None,centroid_error_px=1. if i==0 else None,trusted=True,color='black',split='comparison',ownership=dict(ambiguous=False)) for i in range(3)]
        r=summary(rows)['trusted'];self.assertEqual(r['n'],3);self.assertEqual(r['missing'],2);self.assertIsNone(r['peak']['median']);self.assertIsNone(r['centroid']['p90']);self.assertEqual(r['peak']['within']['3'],1)
    def test_frozen_ownership_and_budgets(self):
        from .experiment import observations
        rows=observations();self.assertEqual(len(rows),52);self.assertEqual(sum(r['trusted'] for r in rows),45)
        fixed=read(BASE/'results/fixed-complete.json');self.assertEqual(len(fixed['models']),15)
        for name in fixed['models']:
            r=read(BASE/f'results/{name}.json.gz');self.assertLessEqual(len(r['fit']['history']),24)
        hist=read(BASE/'results/joint-history.json.gz');self.assertLessEqual(len(hist),96);owners=read(BASE/'evidence/ownership-49.json')['assignments']
        for r in hist:
            if r['fit']:self.assertEqual([x['ownership'] for x in r['records']],owners)
if __name__=='__main__':unittest.main()

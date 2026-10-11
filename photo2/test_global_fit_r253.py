"""Geometry and inference safeguards for the bounded R253 experiment."""
import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from global_fit_r253 import Model, correction, harmonics, assign, data, first_hits, RADIUS, ANCHOR

class GlobalGeometry(unittest.TestCase):
    def setUp(self):self.p=np.array([.31,.15,2.,-3.,84.,25.]+[0.]*8)
    def test_closed_position_and_frame_both_hands_with_deformation(self):
        self.p[6:]=[.002,-.003,.002,.001,.03,-.02,.01,.02]
        for h in [-1,1]:
            m=Model(2679,h,self.p);g=m.geometry([0,2679])
            for key in ['centers','tangent','normal','radial']:np.testing.assert_allclose(g[key][0],g[key][1],atol=1e-10)
            self.assertLess(abs(2679/m.source.nrows-6.5),.01)
    def test_separate_stretch_twist_zero_integral(self):
        t=np.arange(10000)/10000;p=self.p.copy();p[6]=.005
        ds,tw=correction(t,p);self.assertEqual(float(tw.max()),0)
        self.assertAlmostEqual(float((harmonics(t)@p[6:10]).mean()),0)
        p=self.p.copy();p[10]=.05;ds,tw=correction(t,p)
        self.assertEqual(float(abs(ds).max()),0);self.assertAlmostEqual(float(tw.mean()),0)
    def test_index_chart_neighbors_and_closure(self):
        for k in range(-30,30):
            for family,weights in [('A',(1,7)),('B',(-1,6))]:
                u,v=k,0
                for delta,expected in [((1,0),weights[0]),((0,1),weights[1]),((-1,1),weights[1]-weights[0])]:
                    before=weights[0]*u+weights[1]*v
                    after=weights[0]*(u+delta[0])+weights[1]*(v+delta[1])
                    self.assertEqual(after-before,expected)
    def test_split_and_origin(self):
        rr=data();self.assertEqual(len(rr),310);self.assertEqual(sum(r['color']=='red' for r in rr),151)
        self.assertEqual(len({r['sector'] for r in rr if r['split']=='test'}),8)
        self.assertTrue(any(r['observation_id']==ANCHOR and r['evidence_level']=='maker_confirmed' for r in rr))
    def test_known_center_count_and_assignment_both_hands(self):
        for h in [-1,1]:
            m=Model(2698,h,self.p);g=m.geometry(np.arange(2698));eye=m.view.basis()[2]
            ix=np.flatnonzero(g['radial']@eye>.8)[::12]
            xy=m.view.project(g['centers'][ix]);rows=[dict(x=x,y=y,sector=1+i%8) for i,(x,y) in enumerate(xy)]
            ids,c,*_=assign(m,rows);np.testing.assert_array_equal(ids,ix);self.assertLess(max(c),1e-15)
            for n in [2650,2750,3500]:
                _,wrong,*_=assign(Model(n,h,self.p),rows);self.assertGreater(np.mean(wrong),.01)
            self.assertEqual(len(ids),len(set(ids)))
    def test_known_exposed_surface_is_owned_and_hidden_is_not(self):
        for h in [-1,1]:
            m=Model(2698,h,self.p);g=m.geometry(np.arange(2698));eye=m.view.basis()[2]
            front=np.flatnonzero(g['radial']@eye>.98)[::20]
            xy=m.view.project(g['outward'][front]);own,_,unk=first_hits(m,xy,g)
            np.testing.assert_array_equal(own,front);self.assertFalse(unk.any())
            back=np.flatnonzero(g['radial']@eye<-.98)[::20]
            own,_,_=first_hits(m,m.view.project(g['outward'][back]),g)
            self.assertTrue(np.all(own!=back))
    def test_translation_is_rigid_in_image(self):
        q=self.p.copy();q[2:4]+=np.array([3,-5]);a=Model(2698,1,self.p);b=Model(2698,1,q)
        delta=b.view.project(b.geometry([0,111,2000])['centers'])-a.view.project(a.geometry([0,111,2000])['centers'])
        np.testing.assert_allclose(delta,np.tile([3,-5],(3,1)),atol=1e-10)

if __name__=='__main__':unittest.main()

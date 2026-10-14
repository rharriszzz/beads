"""Scientific and leakage regression tests, independent of historical reviews."""
import ast,copy,json,unittest
from pathlib import Path
import numpy as np
from . import geometry as g
from .photographic import detect,select,neighbors
from .predict import predict_pair

class Checks(unittest.TestCase):
    def test_radius(self):self.assertAlmostEqual(g.R,.96*4*np.sin(np.pi/6.5),14)
    def test_hand_changes_only_minor_winding(self):
        k=np.arange(-9,10);a=g.centers(k,1,0);b=g.centers(k,-1,0)
        np.testing.assert_allclose(a[:,0],b[:,0]);np.testing.assert_allclose(a[:,1],-b[:,1]);np.testing.assert_allclose(a[:,2],b[:,2])
    def test_triangle_both_hands(self):
        for h in (-1,1):
            c=g.centers([0,1,7],h,.47);np.testing.assert_allclose(c[1]-c[0]+c[2]-c[1],c[2]-c[0])
    def test_existing_surface_samples_on_implicit(self):self.assertLess(abs(g.sdf(g.SURFACE)).max(),1e-10)
    def test_hole_not_filled(self):self.assertGreater(g.sdf([[0,0,0]])[0],0)
    def test_pitch_collision_is_real_in_all_allowed_controls(self):
        for p in (.95,1.,1.05,1.1):self.assertLess(g.contact(p)['6'],-.001)
    def test_source_dimensions(self):self.assertAlmostEqual(6.5*g.PITCH,1.05*.65*2*g.R)
    def test_ray_occlusion(self):
        p=dict(hand=1,phase=0,pitch=1,inclination=0,roll=0,scale=10,translation=[100,100]);xy=np.array([[105.,110.],[110.,110.]])
        o,z,u=g.trace(p,xy);self.assertTrue(np.isfinite(z).all());self.assertFalse(u.any());self.assertTrue((o!=-999).all())
    def test_inference_import_allowlist(self):
        base=Path(__file__).parent
        for name in ('photographic','predict','geometry'):
            tree=ast.parse((base/(name+'.py')).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertIn(node.module,('numpy','scipy','scipy.spatial','scipy.optimize','scipy.cluster.vq','skimage.color','skimage.segmentation','geometry','photo2.bead_placement'))
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):self.assertNotIn(node.func.id,('open','read','load'))
    def test_geometry_input_cannot_include_hidden_observations(self):
        import inspect
        self.assertEqual(list(inspect.signature(predict_pair).parameters),['a','b','tangent'])
    def test_deterministic_image_observations(self):
        a=np.zeros((100,140,3),np.uint8);a[:]=[130,85,120]
        yy,xx=np.mgrid[:100,:140]
        for x,col in ((40,[220,25,5]),(80,[240,190,10])):
            q=(xx-x)**2+(yy-50)**2<100;a[q]=col
            a[(xx-x)**2+(yy-50)**2<9]=[250,150,40]
        o,s=detect(a);o2,s2=detect(a);self.assertEqual(o,o2);self.assertEqual(select(o),select(o2));self.assertGreaterEqual(len(o),2)
    def test_enclosed_paper_stays_background(self):
        a=np.empty((100,100,3),np.uint8);a[:]=[130,85,120]
        yy,xx=np.mgrid[:100,:100];rr=(xx-50)**2+(yy-50)**2
        a[(rr>25**2)&(rr<35**2)]=[230,35,10]
        _,state=detect(a);self.assertTrue(state['known_background'][50,50])
    def test_saved_prediction_budget_and_triangle(self):
        from .run import OUT,read,sha
        for folder in [OUT/'real']+sorted(OUT.glob('scene-*')):
            for pair in read(folder/'pairs.json.gz'):
                p=read(folder/pair['before_C']);score=read(folder/pair['after_C'])
                self.assertEqual(sha(folder/pair['before_C']),score['frozen_sha256'])
                self.assertEqual(p['evaluations_per_hand'],360)
                self.assertEqual(sum(h['hand']==-1 for h in p['hypotheses']),sum(h['hand']==1 for h in p['hypotheses']))
                for h in p['hypotheses']:
                    self.assertEqual(h['triangle'],[0,h['delta'],h['target']])
                    self.assertEqual(h['fit_uses'],[pair['A']['id'],pair['B']['id']])
                    self.assertFalse(h['physical_valid'])
                for name in pair['before_D']:
                    d=read(folder/name);sc=read(folder/name.replace('-before-D.json.gz','-after-D.json'))
                    self.assertEqual(sha(folder/name),sc['frozen_sha256'])
                    self.assertEqual(len(d['fit_uses']),3)
                    self.assertNotIn(sc['score']['match'],d['fit_uses'])
    def test_pov_projection_saved(self):
        path=Path(__file__).resolve().parents[1]/'review/r279/synthetic-scenes/projection-check.json'
        if not path.exists():self.skipTest('generate independent POV scenes first')
        for r in json.loads(path.read_text()):self.assertGreater(r['agreement'],.995)
if __name__=='__main__':unittest.main()

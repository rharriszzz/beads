"""Peak association changes must preserve native masks and uncertain alternatives."""
import unittest
import numpy as np
from matplotlib.colors import rgb_to_hsv,hsv_to_rgb
from . import test_annular as existing
from . import refine_r266 as r
from . import annular_detect as d
from .stress_r266 import stress_scenes
from .experiment_r266 import truth_metrics


class RefineTests(unittest.TestCase):
    def test_gradual_yellow_shading_and_inferior_rim(self):
        y,x=np.mgrid[:17,:25];hsv=np.full((17,25,3),[.1,.75,.9]);hsv[:,:,0]=(.07+.05*x/24);v=np.full((17,25),230,np.uint8);v[8,7]=255;v[8,14]=250;v[:,3:6]=180
        rs=existing.AnnularTests().records(v,[(7,8),(14,8)],hsv)
        kept,suppressed,e=r.associate(rs,v,hsv)
        self.assertEqual(len(kept),1);self.assertEqual(kept[0]['bright_patch']['peak'],[14,8])
        self.assertEqual(len(suppressed),1);self.assertTrue(e[0]['shallow_broad_bridge'])

    def test_abrupt_color_boundary_preserves_both(self):
        hsv=np.full((17,25,3),[.1,.75,.9]);hsv[:,12:,0]=.17;v=np.full((17,25),230,np.uint8)
        kept,suppressed,_=r.associate(existing.AnnularTests().records(v,[(7,8),(16,8)],hsv),v,hsv)
        self.assertEqual(len(kept),2);self.assertFalse(suppressed)

    def test_neighbor_valley_and_gray_uncertainty(self):
        v=np.full((17,25),220,np.uint8);hsv=np.full((17,25,3),[.1,.75,.9]);v[:,12]=70
        kept,suppressed,_=r.associate(existing.AnnularTests().records(v,[(7,8),(16,8)],hsv),v,hsv)
        self.assertEqual(len(kept),2)

    def test_synthetic_truth_and_mask_immutability(self):
        for name,rgb,truth,centers,conditions in stress_scenes():
            if int(name[-3:])>=24:break
            data,_,_=d.detect(rgb,d.Parameters(method='annular',recover_peaks=True,peak_selection=True,background_guard=True));data['generation_id']='test'
            before={q['id']:q['pixel_runs'] for k in ('regions','suppressed','deferred','rejected') for q in data[k]}
            after=r.refine(data,rgb)
            self.assertEqual(before,{q['id']:q['pixel_runs'] for k in ('regions','suppressed','deferred','rejected') for q in after[k]})
            self.assertEqual(truth_metrics(after,truth,centers)['false_suppression_cross_body'],0)
            self.assertEqual(truth_metrics(after,truth,centers)['missing'],0)

if __name__=='__main__':unittest.main()

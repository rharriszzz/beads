"""Local-fit failure modes: capture, blank evidence, helicity ties, seed aliasing."""
import unittest
import numpy as np
from scipy import ndimage as ndi

from local_patch import (assess, displace, fit, image_evidence, inverse_grid,
                         retained_hypotheses, warp)


class LocalPatchTests(unittest.TestCase):
    def test_inverse_smooth_warp(self):
        c = [3.,-2.,1.,-4.,8.,2.]
        yy,xx = inverse_grid((90,110),c)
        recovered = displace(np.stack([xx,yy],axis=-1),c,90)
        target_y,target_x = np.indices((90,110))
        np.testing.assert_allclose(recovered[...,0],target_x,atol=1e-8)
        np.testing.assert_allclose(recovered[...,1],target_y,atol=1e-8)

    def test_integer_translation_preserves_labels_and_missing(self):
        labels=np.zeros((50,60),np.int32);labels[20:30,20:30]=71
        shifted=warp(labels,[4.,-3.,0.,0.,0.,0.])
        self.assertEqual(set(np.unique(shifted)),{0,71})
        np.testing.assert_array_equal(shifted[17:27,24:34],np.full((10,10),71))

    def test_capture_translation_from_contours(self):
        from local_patch import contour_points
        labels=np.zeros((120,120),np.int32)
        labels[20:45,25:60]=1;labels[57:88,61:97]=2;labels[91:112,20:49]=3
        shifted=warp(labels,[8.,-6.,0.,0.,0.,0.])
        edge=np.zeros(labels.shape,bool)
        p=contour_points(shifted);edge[p[:,1],p[:,0]]=True
        distance=ndi.distance_transform_edt(~edge)
        result=fit(labels,distance,'translation')
        np.testing.assert_allclose(result['coefficients'][:2],[8,-6],atol=.2)
        self.assertLess(result['holdout_mean'],.3)

    def test_blank_black_has_no_supported_contours(self):
        rgb=np.zeros((100,100,3),np.uint8)
        edge,distance=image_evidence(rgb)
        self.assertFalse(edge.any())
        labels=np.zeros((100,100),np.int32);labels[25:75,25:75]=30
        result=assess(labels,distance,[(40,40)]*4,'black',rgb)
        self.assertFalse(result['anchor_ok'])
        self.assertFalse(result['objects'][0]['supported'])
        self.assertIsNone(result['objects'][0]['relative_index'])

    def test_all_three_families_required_and_duplicate_click_rejected(self):
        labels=np.zeros((140,140),np.int32)
        for x,y,label in [(20,20,100),(75,20,101),(20,75,106),(75,75,107)]:
            labels[y:y+40,x:x+40]=label
        anchors=[(40,40),(95,40),(40,95),(95,95)]
        rgb=np.full((140,140,3),100,np.uint8)
        good=assess(labels,np.zeros(labels.shape),anchors,'gray',rgb)
        self.assertTrue(good['anchor_ok'])
        self.assertEqual(good['anchor_families'],[1,6,7])
        self.assertEqual([o['relative_index'] for o in good['objects']],[0,1,6,7])
        bad=assess(labels,np.zeros(labels.shape),[anchors[1],*anchors[1:]],'gray',rgb)
        self.assertFalse(bad['anchor_ok'])
        self.assertTrue(all(o['relative_index'] is None for o in bad['objects']))

    def test_retain_both_helicities_on_tie_and_ignore_holdout_for_selection(self):
        options=[dict(name='plus',fit=dict(train_mean=2.,holdout_mean=9.),assessment=dict(anchor_ok=True)),
                 dict(name='minus',fit=dict(train_mean=2.3,holdout_mean=0.),assessment=dict(anchor_ok=True)),
                 dict(name='invalid',fit=dict(train_mean=0.),assessment=dict(anchor_ok=False))]
        self.assertEqual(retained_hypotheses(options),['plus','minus'])
        options[1]['fit']['train_mean']=3.
        self.assertEqual(retained_hypotheses(options),['plus'])

    def test_hue_wrap_not_an_sv_boundary(self):
        from skimage.color import hsv2rgb
        hsv=np.ones((50,50,3),float);hsv[:,:25,0]=.999;hsv[:,25:,0]=.001
        rgb=hsv2rgb(hsv)
        edge,_=image_evidence(rgb)
        self.assertFalse(edge.any())

if __name__=='__main__':unittest.main()

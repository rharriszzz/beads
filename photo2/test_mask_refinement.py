"""Adverse diffuse-core controls: real valleys versus multiple bright reflections."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-segmentation-mpl')
import unittest
import numpy as np
from matplotlib.colors import hsv_to_rgb
from refine_colored_masks import diffuse_cores


class DiffuseCoreTests(unittest.TestCase):
    def fixture(self,centers,hue=350):
        yy,xx=np.indices((91,111));hsv=np.zeros((91,111,3),np.float32)
        hsv[...,0]=hue/360;hsv[...,1]=.8;hsv[...,2]=.12
        for x,y in centers:
            hsv[...,2]=np.maximum(hsv[...,2],.14+.7*np.exp(-((xx-x)**2+(yy-y)**2)/130))
        support=hsv[...,2]>.18
        arrays=dict(domain=support,family=np.ones(support.shape,np.uint8),reflections=np.zeros(support.shape,np.int32))
        report=dict(parameters=dict(native_diameter=24,detector=dict(hue_modes_degrees=[hue])))
        return hsv,arrays,report,xx,yy

    def test_two_same_color_bodies_with_dark_valley_have_two_cores(self):
        centers=[[38,45],[68,45]];hsv,arrays,report,xx,yy=self.fixture(centers)
        image=(hsv_to_rgb(hsv)*255).astype(np.uint8)
        points,*_=diffuse_cores(image,report,arrays)
        self.assertEqual(len(points),2)
        for center in centers:
            self.assertLess(min(np.linalg.norm(np.asarray(p['xy'])-center) for p in points),2)

    def test_two_reflections_on_one_diffuse_body_do_not_make_two_cores(self):
        for hue in [350,27,210]:
            with self.subTest(hue=hue):
                hsv,arrays,report,xx,yy=self.fixture([[53,45]],hue)
                for ident,(x,y) in enumerate([(48,45),(58,45)],1):
                    spot=(xx-x)**2+(yy-y)**2<=4
                    hsv[spot,0]=0;hsv[spot,1]=.03;hsv[spot,2]=1
                    arrays['reflections'][spot]=ident
                image=(hsv_to_rgb(hsv)*255).astype(np.uint8)
                points,*_=diffuse_cores(image,report,arrays)
                self.assertEqual(len(points),1)
                self.assertLess(np.linalg.norm(np.asarray(points[0]['xy'])-[53,45]),3)


if __name__=='__main__':unittest.main()

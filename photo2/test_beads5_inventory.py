"""Controls for neutral highlights and shared-support bead segmentation."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from beads5_inventory import color_support, segment, envelope_mask


class Beads5Tests(unittest.TestCase):
    def test_purple_glint_repaired_but_neutral_body_preserved(self):
        rgb=np.full((90,120,3),(160,70,170),np.uint8)
        rgb[15:25,15:25]=255  # 100px exceeds the previous palette's 64px cutoff.
        rgb[30:60,60:90]=220  # A full white body must survive.
        _,_,channels=color_support(rgb,np.ones((90,120),bool))
        self.assertEqual(channels[20,20],1)
        self.assertEqual(channels[45,75],2)

    def test_gray_highlight_and_white_shadow_share_support(self):
        rgb=np.full((40,60,3),70,np.uint8);rgb[10:30,10:30]=240
        rgb[0:5]=20
        _,mask,channels=color_support(rgb,np.ones((40,60),bool))
        self.assertEqual(channels[20,20],channels[35,40])
        self.assertEqual(channels[20,20],2)
        self.assertFalse(mask[0].any())

    def test_neutral_labels_compete_without_brightness_class_cut(self):
        rgb=np.full((90,100,3),75,np.uint8);rgb[10:50,45:80]=220
        channels=np.zeros((90,100),np.uint8);channels[10:50,10:80]=2
        channels[60:64,20:24]=2
        rows=[dict(id=1,marker_xy=[25,30],color='gray'),dict(id=2,marker_xy=[60,30],color='white')]
        labels=segment(rgb,channels,rows)
        self.assertEqual(labels[30,25],1);self.assertEqual(labels[30,60],2)
        self.assertEqual(int((labels>0).sum()),40*70)
        self.assertFalse(labels[60:64].any())
        for row in rows:self.assertEqual(ndi.label(labels==row['id'])[1],1)

    def test_envelope_repairs_gap_without_filling_main_opening(self):
        base=np.zeros((180,220),bool);base[20:160,20:200]=True
        base[50:130,50:170]=False;base[20:50,90:102]=False
        mask=envelope_mask(base)
        self.assertTrue(mask[35,95]);self.assertFalse(mask[90,110]);self.assertFalse(mask[0,0])


if __name__=='__main__':unittest.main()

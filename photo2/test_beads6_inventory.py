"""Controls for beads6 chromatic highlights, white support and region separation."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from beads6_inventory import color_support, segment, envelope_mask


class Beads6Tests(unittest.TestCase):
    def test_chromatic_glints_repaired_without_swallowing_white_body(self):
        for color,index in [((220,15,15),1),((90,155,170),2)]:
            with self.subTest(color=color):
                rgb=np.full((90,120,3),color,np.uint8)
                rgb[15:25,15:25]=255
                rgb[30:60,60:90]=220
                _,_,channels=color_support(rgb,np.ones((90,120),bool))
                self.assertEqual(channels[20,20],index)
                self.assertEqual(channels[45,75],3)

    def test_white_shadow_threshold_and_envelope(self):
        rgb=np.full((40,60,3),180,np.uint8);rgb[:5]=70
        envelope=np.ones((40,60),bool);envelope[:,50:]=False
        _,mask,channels=color_support(rgb,envelope)
        self.assertEqual(channels[20,20],3)
        self.assertFalse(mask[:5].any());self.assertFalse(mask[:,50:].any())

    def test_three_classes_separate_and_detached_islands_unassigned(self):
        rgb=np.full((80,110,3),180,np.uint8)
        channels=np.zeros((80,110),np.uint8)
        for index in (1,2,3):channels[10:50,index*25-15:index*25+10]=index
        channels[60:64,10:14]=1
        rows=[dict(id=i,marker_xy=[i*25,30],color=c) for i,c in enumerate(['red','blue-gray','white'],1)]
        labels=segment(rgb,channels,rows)
        for row in rows:
            region=labels==row['id']
            self.assertEqual(ndi.label(region)[1],1)
            self.assertTrue(np.all(channels[region]==row['id']))
            self.assertEqual(region.sum(),1000)
        self.assertFalse(labels[60:].any())

    def test_envelope_repairs_gap_preserves_main_opening(self):
        base=np.zeros((180,220),bool);base[20:160,20:200]=True
        base[50:130,50:170]=False;base[20:50,90:102]=False
        mask=envelope_mask(base)
        self.assertTrue(mask[35,95]);self.assertFalse(mask[90,110]);self.assertFalse(mask[0,0])


if __name__=='__main__':unittest.main()

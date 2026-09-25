"""Controls for beads7 chromatic/dark glints and shared neutral segmentation."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from beads7_inventory import color_support, segment, envelope_mask, restore_reviewed_glints


class Beads7Tests(unittest.TestCase):
    def test_enclosed_glints_preserve_large_pale_bodies(self):
        for color,index in [((220,15,15),1),((45,180,65),2),((10,10,10),3)]:
            with self.subTest(color=color):
                rgb=np.full((90,120,3),color,np.uint8)
                rgb[15:27,15:27]=255;rgb[30:60,60:90]=220
                _,_,channels=color_support(rgb,np.ones((90,120),bool))
                self.assertEqual(channels[20,20],index)
                self.assertEqual(channels[45,75],4)

    def test_neutral_glints_and_shadows_share_support(self):
        rgb=np.full((40,60,3),180,np.uint8);rgb[:10]=[150,160,161];rgb[10:20]=255
        envelope=np.ones((40,60),bool);envelope[:,50:]=False
        _,mask,channels=color_support(rgb,envelope)
        self.assertTrue(np.all(channels[:,:50]==4))
        self.assertFalse(mask[:,50:].any())

    def test_reviewed_glint_preserves_background_and_chromatic_cores(self):
        channels=np.full((30,30),4,np.uint8)
        channels[12,12]=1;channels[13,13]=2;channels[14,14]=0
        restored=restore_reviewed_glints(channels,[dict(xy=[15,15],radius=5)])
        self.assertEqual(restored[15,15],3)
        for y,x in [(12,12),(13,13),(14,14),(0,0)]:
            self.assertEqual(restored[y,x],channels[y,x])
        self.assertEqual(channels[15,15],4)

    def test_classes_separate_and_neutral_labels_share_support(self):
        rgb=np.full((80,160,3),180,np.uint8);channels=np.zeros((80,160),np.uint8)
        for index in range(1,5):channels[10:50,index*30-20:index*30+5]=index
        channels[60:64,10:14]=1
        rows=[dict(id=i,marker_xy=[i*30-8,30],color=c) for i,c in enumerate(['red','green','black','silver'],1)]
        rows.append(dict(id=5,marker_xy=[120,30],color='white'))
        labels=segment(rgb,channels,rows)
        for row in rows:
            region=labels==row['id'];self.assertEqual(ndi.label(region)[1],1)
            self.assertTrue(np.all(channels[region]==min(row['id'],4)))
        self.assertFalse(labels[60:].any())
        self.assertEqual(int((labels>0).sum()),4000)

    def test_envelope_repairs_gap_preserves_main_opening(self):
        base=np.zeros((180,220),bool);base[20:160,20:200]=True
        base[50:130,50:170]=False;base[20:50,90:102]=False
        mask=envelope_mask(base)
        self.assertTrue(mask[35,95]);self.assertFalse(mask[90,110]);self.assertFalse(mask[0,0])


if __name__=='__main__':unittest.main()

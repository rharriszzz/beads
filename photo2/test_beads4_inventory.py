"""Palette and segmentation controls for the beads4 JPEG review."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from beads4_inventory import color_support, envelope_mask, segment


class Beads4Tests(unittest.TestCase):
    def test_five_colors_white_body_and_enclosed_glint(self):
        rgb=np.full((80,170,3),250,np.uint8)
        env=np.zeros((80,170),bool);env[10:70,10:160]=True
        for i,c in enumerate([(210,10,10),(195,190,10),(10,200,20),(10,140,195),(220,220,220)]):
            rgb[10:70,10+i*30:40+i*30]=c
        rgb[30:35,20:25]=255
        _,_,channels=color_support(rgb,env)
        self.assertEqual(channels[32,22],1)
        self.assertEqual(channels[40,145],5)
        self.assertEqual([channels[40,25+i*30] for i in range(5)],[1,2,3,4,5])
        self.assertFalse(channels[0].any())

    def test_dark_neutral_shadow_is_not_white(self):
        rgb=np.full((50,70,3),60,np.uint8);rgb[10:35,10:30]=230
        _,mask,channels=color_support(rgb,np.ones((50,70),bool))
        self.assertFalse(mask[40,40]);self.assertEqual(channels[20,20],5)

    def test_envelope_restores_white_gap_and_preserves_opening(self):
        base=np.zeros((180,220),bool);base[20:160,20:200]=True;base[50:130,50:170]=False
        base[20:50,90:102]=False
        mask=envelope_mask(base)
        self.assertTrue(mask[35,95]);self.assertFalse(mask[90,110]);self.assertFalse(mask[0,0])

    def test_adjacent_white_bodies_and_detached_island(self):
        rgb=np.full((100,110,3),240,np.uint8);rgb[10:45,40:70]=165
        channels=np.zeros((100,110),np.uint8);channels[10:45,10:70]=5
        channels[55:60,20:25]=5
        rows=[dict(id=1,marker_xy=[25,25],color='white'),dict(id=2,marker_xy=[55,25],color='white')]
        labels=segment(rgb,channels,rows)
        self.assertGreater(rows[0]['region_pixels'],500);self.assertGreater(rows[1]['region_pixels'],500)
        self.assertEqual(labels[25,55],2);self.assertFalse(labels[55:60].any())
        for row in rows:self.assertEqual(ndi.label(labels==row['id'])[1],1)


if __name__=='__main__':unittest.main()

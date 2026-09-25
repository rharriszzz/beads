"""Controls for neutral bodies, glints and connected regions in beads3."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from beads3_inventory import envelope_mask, color_support, segment


class Beads3Tests(unittest.TestCase):
    def test_foreground_repairs_white_gap_without_filling_main_opening(self):
        base=np.zeros((180,220),bool);base[20:160,20:200]=True;base[50:130,50:170]=False
        base[20:50,90:102]=False
        mask=envelope_mask(base)
        self.assertTrue(mask[35,95]);self.assertFalse(mask[90,110]);self.assertFalse(mask[0,0])

    def test_white_glint_inside_black_is_not_a_white_bead(self):
        rgb=np.full((80,120,3),245,np.uint8);env=np.zeros((80,120),bool);env[10:70,10:110]=True
        rgb[10:70,10:55]=10;rgb[25:30,25:30]=255;rgb[10:70,55:80]=[220,0,0]
        _,_,channels=color_support(rgb,env)
        self.assertEqual(channels[27,27],2);self.assertEqual(channels[30,60],1);self.assertEqual(channels[30,95],3)
        self.assertEqual(channels[0,0],0)

    def test_neutral_shadow_outside_envelope_not_assigned(self):
        rgb=np.full((70,110,3),245,np.uint8);rgb[10:60,10:40]=10;rgb[10:60,40:70]=220;rgb[10:60,75:100]=70
        env=np.zeros(rgb.shape[:2],bool);env[10:60,10:70]=True
        _,_,channels=color_support(rgb,env)
        rows=[dict(id=1,marker_xy=[25,35],color='black'),dict(id=2,marker_xy=[55,35],color='white')]
        labels=segment(rgb,channels,rows)
        self.assertFalse(labels[:,75:].any());self.assertEqual(labels[35,25],1);self.assertEqual(labels[35,55],2)
        for row in rows:self.assertEqual(ndi.label(labels==row['id'])[1],1)

    def test_adjacent_white_bodies_both_keep_substantial_regions(self):
        rgb=np.full((60,90,3),245,np.uint8);rgb[10:50,10:40]=245;rgb[10:50,40:70]=170
        channels=np.zeros((60,90),np.uint8);channels[10:50,10:70]=3
        rows=[dict(id=1,marker_xy=[25,30],color='white'),dict(id=2,marker_xy=[55,30],color='white')]
        labels=segment(rgb,channels,rows)
        self.assertGreater(rows[0]['region_pixels'],500);self.assertGreater(rows[1]['region_pixels'],500)
        self.assertEqual(labels[30,55],2)

    def test_distance_clipping_does_not_leave_disconnected_label_islands(self):
        rgb=np.zeros((90,90,3),np.uint8);channels=np.zeros((90,90),np.uint8)
        # Two nearby lobes connected only by a path outside the assignment radius.
        channels[20:30,20:30]=2;channels[40:50,20:30]=2;channels[20:50,65:70]=2
        channels[20:25,20:70]=2;channels[45:50,20:70]=2
        rows=[dict(id=7,marker_xy=[25,25],color='black')]
        labels=segment(rgb,channels,rows)
        self.assertEqual(ndi.label(labels==7)[1],1)
        self.assertGreater(rows[0]['detached_pixels_left_unassigned'],0)
        self.assertFalse(labels[40:50,20:30].any())


if __name__=='__main__':unittest.main()

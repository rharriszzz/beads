"""Controls for palette-constrained support and explicit unresolved regions."""
import unittest
import numpy as np
from beads1_inventory import color_support, segment, coverage


class InventoryTests(unittest.TestCase):
    def test_neutral_shadow_excluded_and_small_highlight_filled(self):
        rgb=np.full((60,80,3),245,np.uint8)
        rgb[10:45,10:40]=[220,0,0]
        rgb[20:23,20:23]=[255,255,255]
        rgb[10:45,45:60]=[90,90,90]
        core,mask,color=color_support(rgb)
        self.assertFalse(core[21,21]);self.assertTrue(mask[21,21]);self.assertEqual(color[21,21],1)
        self.assertFalse(mask[25,50]);self.assertFalse(mask[0,0])

    def test_large_opening_is_not_filled(self):
        rgb=np.full((60,60,3),255,np.uint8);rgb[5:55,5:55]=[0,200,0];rgb[15:45,15:45]=255
        _,mask,color=color_support(rgb)
        self.assertFalse(mask[25,25]);self.assertEqual(color[25,25],0)

    def test_instances_cannot_cross_color_and_seedless_patch_remains_unknown(self):
        rgb=np.full((70,100,3),245,np.uint8)
        rgb[10:40,10:40]=[220,0,0];rgb[10:40,40:70]=[0,220,0];rgb[50:60,80:90]=[0,0,220]
        _,mask,color=color_support(rgb)
        records=[dict(id=10,marker_xy=[25,25],color='red'),dict(id=20,marker_xy=[55,25],color='green')]
        labels=segment(rgb,color,records)
        self.assertTrue(np.all(color[labels==10]==1));self.assertTrue(np.all(color[labels==20]==2))
        self.assertTrue(np.all(labels[50:60,80:90]==0))
        unassigned,regions=coverage(mask,labels)
        self.assertEqual(unassigned.sum(),100);self.assertEqual(len(regions),1)
        self.assertEqual(regions[0]['pixels'],100)

    def test_duplicate_and_unsupported_seed_are_explicit(self):
        rgb=np.full((50,50,3),245,np.uint8);rgb[10:30,10:30]=[220,0,0]
        _,_,color=color_support(rgb)
        records=[dict(id=1,marker_xy=[15,15],color='red'),dict(id=2,marker_xy=[15,15],color='red'),dict(id=3,marker_xy=[45,45],color='red')]
        labels=segment(rgb,color,records)
        self.assertEqual(records[1]['mask_status'],'coincident_seed_unresolved')
        self.assertEqual(records[2]['mask_status'],'no_nearby_color_support')
        self.assertEqual(records[1]['region_pixels'],0);self.assertEqual(records[2]['region_pixels'],0)
        self.assertTrue(set(np.unique(labels))<={0,1})

    def test_tiny_unassigned_pixels_retained_without_bead_count(self):
        mask=np.zeros((10,20),bool);mask[1,1]=True;mask[4:6,10:14]=True
        unassigned,regions=coverage(mask,np.zeros_like(mask,dtype=int))
        self.assertEqual(unassigned.sum(),9);self.assertEqual(len(regions),1)
        self.assertEqual(regions[0]['pixels'],8)
        self.assertEqual(regions[0]['status'],'unassigned_colored_region_not_a_bead_count')


if __name__=='__main__':unittest.main()

"""Controls for pale beads, hue-separated masks and per-image exclusions."""
import unittest
import numpy as np
from beads2_inventory import color_support, segment, SELECTION
from inventory_selection import select_records


class Beads2Tests(unittest.TestCase):
    def test_four_palette_classes_and_neutral_shadow(self):
        rgb=np.full((50,150,3),245,np.uint8)
        for x,color in zip([5,30,55,80,105],[[220,120,15],[205,200,8],[110,3,205],[195,169,196],[90,90,90]]):
            rgb[10:40,x:x+20]=color
        _,mask,channels=color_support(rgb)
        for x,index in [(15,1),(40,2),(65,3),(90,4),(115,0)]:self.assertEqual(channels[25,x],index)
        self.assertFalse(mask[25,115]);self.assertFalse(mask[0,0])

    def test_highlight_filled_but_opening_and_other_hues_excluded(self):
        rgb=np.full((80,120,3),245,np.uint8)
        rgb[5:70,5:70]=[195,169,196];rgb[20:50,20:50]=245
        rgb[10:13,10:13]=255;rgb[20:50,85:110]=[0,210,0]
        core,mask,channels=color_support(rgb)
        self.assertFalse(core[11,11]);self.assertTrue(mask[11,11]);self.assertEqual(channels[11,11],4)
        self.assertFalse(mask[30,30]);self.assertFalse(mask[30,90])

    def test_regions_stay_in_palette_and_seedless_body_is_unassigned(self):
        rgb=np.full((70,100,3),245,np.uint8)
        rgb[10:40,10:40]=[195,169,196];rgb[10:40,40:70]=[110,3,205];rgb[50:60,80:90]=[220,120,15]
        _,_,channels=color_support(rgb)
        records=[dict(id=8,marker_xy=[25,25],color='lavender'),dict(id=9,marker_xy=[55,25],color='violet')]
        labels=segment(rgb,channels,records)
        self.assertTrue(np.all(channels[labels==8]==4));self.assertTrue(np.all(channels[labels==9]==3))
        self.assertTrue(np.all(labels[50:60,80:90]==0))

    def test_beads1_marker_exclusion_does_not_leak_into_beads2(self):
        rows=[dict(id=i,marker_xy=[10+3*j,10],status='reviewed_body',region_pixels=100) for j,i in enumerate([207,208,209,210,211,212])]
        active,excluded=select_records(rows,np.full((40,40),20.),SELECTION)
        self.assertIn(211,[r['id'] for r in active]);self.assertFalse(excluded)


if __name__=='__main__':unittest.main()

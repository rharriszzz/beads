import unittest
import numpy as np
from matplotlib.colors import hsv_to_rgb
from .trusted_r271 import detect
from .brightness_r270 import encode,linearize
from .inventory_r272 import inventory,measure,component,learn_palette,classify,outline

def scene(color='yellow',offset=0):
    yy,xx=np.mgrid[:90,:110];x=50+offset;y=45;rr=(xx-x)**2+(yy-y)**2;body=rr<=16**2
    rgb=np.full((90,110,3),[175,90,160],np.uint8)
    if color=='black':
        lin=.008+.8*np.exp(-rr/24);c=np.repeat(encode(lin)[...,None],3,axis=2)
    else:
        hue={'yellow':60,'red':0,'blue':220}[color];base=hsv_to_rgb(np.array([hue/360,.45,1.]));c=base*(.20+.75*np.exp(-rr/72))[...,None]
    rgb[body]=np.clip(np.rint(c[body]*255),0,255).astype(np.uint8)
    return rgb,body

def run(color,offset=0):
    rgb,truth=scene(color,offset);locations,_,_,_,paper=detect(rgb);beads,rejected,summary=inventory(rgb,rgb,locations,paper);return beads,rejected,summary,rgb,truth

class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cases={k:run(k) for k in ('yellow','red','black','blue')}
    def test_yellow_and_red(self):
        for color in ('yellow','red'):
            beads,*_=self.cases[color];self.assertEqual(len(beads),1);self.assertEqual(beads[0]['color'],color)
    def test_black_reflection_small(self):
        beads,_,_,_,truth=self.cases['black'];self.assertEqual(len(beads),1);self.assertEqual(beads[0]['color'],'black');self.assertLess(beads[0]['region']['pixel_count'],truth.sum()/3)
    def test_unsupported_color_not_fabricated(self):
        beads,records,*_=self.cases['blue'];self.assertFalse(beads);self.assertTrue(any(r['reasons'] for r in records))
    def test_known_ownership(self):
        for beads,_,_,_,truth in self.cases.values():
            for b in beads:
                for y,a,z in b['region']['runs']:self.assertTrue(truth[y,a:z+1].all())
    def test_counts_centroids_and_peak(self):
        for beads,_,_,rgb,_ in self.cases.values():
            for b in beads:
                for key in ('region','bright_patch'):
                    pts=np.array([(x,y) for y,a,z in b[key]['runs'] for x in range(a,z+1)]);self.assertEqual(len(pts),b[key]['pixel_count']);np.testing.assert_allclose(pts.mean(axis=0),b[key]['centroid'])
                self.assertEqual(b['brightest']['rgb_native'],rgb[b['brightest']['y'],b['brightest']['x']].tolist())
    def test_local_brightest_not_replaced_by_dimmer_sample(self):
        for beads,_,_,rgb,_ in self.cases.values():
            lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722])
            for b in beads:
                x,y=b['anchor'];self.assertEqual(b['brightest']['luminance'],float(lum[y-4:y+5,x-4:x+5].max()))
    def test_display_smoothing_does_not_change_mask(self):
        mask=np.zeros((12,12),bool);mask[2:10,3:9]=True;before=mask.copy();o=outline(mask,(20,30));np.testing.assert_array_equal(mask,before);self.assertEqual(o['smooth'][0],o['smooth'][-1]);self.assertLess(o['maximum_vertex_displacement'],1)
    def test_no_diagonal_ownership_bridge(self):
        m=np.eye(5,dtype=bool);self.assertEqual(component(m,(0,0)).sum(),1)
    def test_id_stable_and_number_not_index(self):
        first=self.cases['yellow'][0][0];second=run('yellow')[0][0];self.assertEqual(first['id'],second['id']);self.assertEqual(first['inventory_number'],1)
    def test_translation(self):
        b=run('yellow',5)[0][0];a=self.cases['yellow'][0][0];self.assertEqual(b['brightest']['x']-a['brightest']['x'],5);self.assertEqual(b['region']['pixel_count'],a['region']['pixel_count'])
    def test_unknown_neutral_not_automatically_black(self):
        f=dict(neutral_core_fraction=1.,dark_neutral_ring_fraction=0.,colored_core_fraction=0.,color_samples=0,hue=None,hue_deviation90=None);self.assertIsNone(classify(f,[])[0])
    def test_centroid_reference_mask(self):
        a=np.zeros((3,4),bool);a[0,0]=a[1,0]=a[1,1]=True;r=measure(a,(10,20));self.assertEqual(r['pixel_count'],3);np.testing.assert_allclose(r['centroid'],[10+1/3,20+2/3])
if __name__=='__main__':unittest.main()

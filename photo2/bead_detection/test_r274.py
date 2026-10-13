"""R274 hue interfaces, highlight handling, frozen locations and native masks."""
import unittest
from dataclasses import replace
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from .synthetic_r274 import scenes
from .hue_r274 import SELECTED,VARIANTS,refine,grow,color_surface,palette_from
from .coverage_r272 import detect as baseline
from .interiors_r273 import refine as old_refine,pixels,mask_local
from .brightness_r270 import linearize
from .climb_r268 import background
from .inventory_r272 import hue_distance
from .evaluate_coverage_r272 import metric

class HueTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.examples={n:(rgb,t,c) for n,rgb,t,c in scenes()};cls.rgb,cls.truth,cls.colors=cls.examples['h18-h42-equal-Y'];cls.base=baseline(cls.rgb)[0];cls.old=old_refine(cls.rgb,cls.rgb,cls.base)[1]
 def test_equal_brightness_hue_interface_owned(self):
  b,loc,rows,s=refine(self.rgb,self.rgb,self.base,self.old);self.assertEqual(len(b),2);m,_=metric(b,self.truth,self.colors);self.assertEqual(sum(v['background_pixels']+v['other_body_pixels'] for v in m.values()),0)
  l=linearize(self.rgb/255.)@np.array([.2126,.7152,.0722]);hs=rgb_to_hsv(self.rgb/255.);self.assertLess(abs(l[64,68]-l[64,69]),.005);self.assertGreater(hue_distance(hs[64,68,0]*360,hs[64,69,0]*360),20);self.assertTrue(any(r.get('stops',{}).get('rival-hue',0)>0 for r in rows))
 def test_dim_same_color_still_expands(self):
  rgb,t,c=self.examples['h18-h42-dim'];base=baseline(rgb)[0];b,_,_,_=refine(rgb,rgb,base);self.assertEqual(len(b),2);self.assertTrue(all(r['region']['pixel_count']>300 for r in b))
 def test_circular_hue_wrap(self):
  self.assertEqual(float(hue_distance(359,1)),2);rgb,t,c=self.examples['h358-h55-equal-Y'];b,*_=refine(rgb,rgb,baseline(rgb)[0]);self.assertEqual(len(b),2);m,_=metric(b,t,c);self.assertEqual(sum(v['other_body_pixels'] for v in m.values()),0)
 def test_location_survives_rejected_interior(self):
  b,loc,rows,_=refine(self.rgb,self.rgb,self.base,self.old,replace(SELECTED,hue_limit=.01));old={r['id']:r for r in self.old if r['accepted']};self.assertTrue(old);self.assertTrue(any(r['interior_status']=='uncertain' for r in loc));self.assertTrue(set(old)<=set(r['id'] for r in loc))
  for r in loc:
   if r['id'] in old:self.assertEqual(r['point'],old[r['id']]['brightest'])
 def test_mask_measurements_and_no_overlap(self):
  b,*_=refine(self.rgb,self.rgb,self.base,self.old);seen=set()
  for r in b:
   pts=pixels(r);self.assertFalse(pts&seen);seen|=pts;self.assertEqual(len(pts),r['region']['pixel_count']);np.testing.assert_allclose(np.array(list(pts)).mean(axis=0),r['region']['centroid']);self.assertEqual(ndi.label(mask_local(r['region']))[1],1);self.assertTrue(pts<=pixels(r,'supported_region'));self.assertTrue(pixels(r,'bright_patch')<=pts)
 def test_low_saturation_highlight_does_not_invent_hue_barrier(self):
  # Component test: freeze automatically found equal-Y locations, then add
  # neutral glints. This isolates growth from the older candidate filter.
  rgb,t,c=self.examples['h18-h42-neutral-highlight'];hs=rgb_to_hsv(rgb/255.);l=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);_,paper,_=background(rgb);surface=color_surface(hs);results=[grow(r,rgb,rgb,hs,l,ndi.uniform_filter(l,3),paper,surface,palette_from(self.base),SELECTED) for r in self.base];self.assertTrue(all(r.get('region',{}).get('pixel_count',0)>100 for r in results));self.assertFalse(any('interior-peak-lost' in r['reasons'] for r in results))
 def test_smooth_equal_y_color_transition_stops_without_brightness_valley(self):
  rgb,t,c=self.examples['h18-h42-soft-boundary'];hs=rgb_to_hsv(rgb/255.);l=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);_,paper,_=background(rgb);surface=color_surface(hs);rows=[grow(r,rgb,rgb,hs,l,ndi.uniform_filter(l,3),paper,surface,palette_from(self.base),SELECTED) for r in self.base];accepted=[r for r in rows if r['accepted']];self.assertEqual(len(accepted),2);m,_=metric(accepted,t,c);self.assertEqual(sum(v['other_body_pixels'] for v in m.values()),0);self.assertTrue(all(r['stops'].get('rival-hue',0)>0 for r in rows));self.assertLess(abs(l[64,67]-l[64,70]),.005)
 def test_no_review_coordinates_in_runtime(self):
  import inspect
  from . import hue_r274
  source=inspect.getsource(hue_r274)
  for token in ('R00956','R01284','inventory.json','contact-cases'):self.assertNotIn(token,source)
 def test_deterministic(self):self.assertEqual(refine(self.rgb,self.rgb,self.base,self.old),refine(self.rgb,self.rgb,self.base,self.old))
if __name__=='__main__':unittest.main()

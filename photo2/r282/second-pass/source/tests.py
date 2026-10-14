"""Scientific and phase-boundary contracts relevant to the real reconstruction."""
import ast
import copy
import unittest
import numpy as np
from .common import ROOT,record,support,pixels,validate
from .phase1 import component,shape_metrics,attempts,image_features
from .geometry import Scene,cold_parameters,R
from .phase2 import assignment,measure_color
from .phase3 import periods,consensus,search


class Contracts(unittest.TestCase):
    def test_shared_record_centroid_and_provenance(self):
        row=record('obs','phase1');row['measured_support']=support([[2,3],[3,3],[3,4]])
        row['measured_photo_location']=pixels(row['measured_support']).mean(0).tolist();validate(row)
        bad=copy.deepcopy(row);bad['physical_model_index']=2
        with self.assertRaises(AssertionError):validate(bad)

    def test_native_runs_roundtrip(self):
        xy=np.array([[1,2],[2,2],[5,2],[2,3]])
        np.testing.assert_array_equal(pixels(support(xy)),xy)

    def test_component_never_jumps_to_neighbor(self):
        mask=np.zeros((30,30),bool);mask[5:15,5:15]=True;mask[5:15,18:28]=True
        chosen=component(mask,[10,10]);self.assertEqual(chosen.sum(),100);self.assertFalse(chosen[:,18:].any())

    def test_neck_diagnostic_exposes_joined_lobes(self):
        y,x=np.indices((51,51));mask=((x-15)**2+(y-25)**2<8**2)|((x-35)**2+(y-25)**2<8**2)
        mask[25,15:36]=True
        metrics=shape_metrics(mask);self.assertEqual(metrics['components'],1);self.assertLess(metrics['neck_retention'],.6)

    def test_blank_paper_is_not_a_high_black_bead(self):
        rgb=np.full((80,80,3),[150,80,130],np.uint8);f=image_features(rgb)
        self.assertTrue(all(r['quality']!='high' for r in attempts(f,[40,40])))

    def test_black_requires_body_and_reflection(self):
        rgb=np.full((80,80,3),[150,80,130],np.uint8);yy,xx=np.indices((80,80))
        rgb[(xx-40)**2+(yy-40)**2<12**2]=[20,20,22]
        rgb[(xx-40)**2+(yy-40)**2<3**2]=[210,210,210]
        a=attempts(image_features(rgb),[40,40]);c=a[2]
        self.assertEqual(c['color'],'black');self.assertGreater(c['dark_fraction'],.5);self.assertGreater(c['region']['pixel_count'],40)
        self.assertLess(c['region']['pixel_count'],870)

    def test_palette_does_not_learn_tinted_paper_as_yellow(self):
        from skimage.color import hsv2rgb
        hs=np.empty((180,180,3));hs[:]=[312/360,.5,.65]
        hs[25:155,25:155]=[338/360,.5,.65]
        hs[45:85,45:85]=[357/360,.8,.8]
        hs[95:135,95:135]=[38/360,.8,.8]
        palette=image_features(np.rint(hsv2rgb(hs)*255).astype(np.uint8))['palette']
        from .common import circular_distance
        self.assertLess(circular_distance(palette['red'],357),3)
        self.assertLess(circular_distance(palette['yellow'],38),3)

    def test_phase1_has_no_model_or_pattern_import(self):
        tree=ast.parse((ROOT/'photo2/r282/phase1.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any(any(k in (m or '') for k in ('geometry','phase2','phase3','r281','reconstruct')) for m in imports))

    def scene(self,hand=1):
        a=np.arange(1024)*2*np.pi/1024;curve=np.c_[300+180*np.cos(a),300+150*np.sin(a)]
        return Scene(curve,cold_parameters(260,hand,75,1.45))

    def test_source_radius_and_closed_planar_curve(self):
        self.assertAlmostEqual(R,.96*4*np.sin(np.pi/6.5),14)
        for hand in (-1,1):
            s=self.scene(hand);self.assertTrue(np.all(s.line[:,2]==0));self.assertEqual(s.turns,40)
            self.assertLess(np.linalg.norm(s.line[0]-s.line[-1]),s.length/260*1.01)

    def test_first_hits_belong_to_literal_annuli(self):
        from photo2.r279.geometry import sdf
        s=self.scene();data=s.trace(s.pc[::5],normals=True);ok=data['owner']>=0;k=data['owner'][ok]
        self.assertGreater(len(k),10);delta=data['points'][ok]-s.centers[k]
        q=np.stack([(delta*s.g[key][k]).sum(1) for key in ('surface_tangent','surface_normal','surface_binormal')],axis=1)
        self.assertLess(np.max(np.abs(sdf(q))),2e-5)

    def test_assignments_are_one_to_one_and_allow_missing(self):
        owners,fractions=assignment([{1:1.},{1:.9},{2:.8},{}],4)
        self.assertEqual(len(set(k for k in owners if k>=0)),2)
        self.assertEqual(sum(owners<0),2)

    def test_visibility_counts_bound_observed_pixels(self):
        s=self.scene();xy=np.array([[x,y] for x in range(100,510,6) for y in range(100,510,6)])
        data=s.trace(xy);visible=np.bincount(data['owner'][data['owner']>=0],minlength=s.n)
        self.assertTrue(np.all(visible<=data['isolated_counts']))

    def test_invisible_color_unknown(self):
        c,reliability,info,xy=measure_color(None,None,np.empty((0,2),int))
        self.assertEqual(c,'unknown');self.assertEqual(reliability,0)

    def test_repeat_rule_and_maker_constraint(self):
        self.assertEqual(periods(40,False),[1,2,4,5,8,10])
        self.assertNotIn(13,periods(104));self.assertIn(13,periods(104,False))
        for n in (40,104,1950):self.assertTrue(all(n%p==0 and n//p>=4 for p in periods(n)))

    def test_low_weight_conflict_cannot_overrule_strong_color(self):
        result=consensus([(0,0,1.),(3,0,1.),(6,1,.05)],3)
        self.assertEqual(result['sequence'][0],'red');self.assertEqual(result['sequence'][1],'unknown')

    def test_exact_known_pattern_and_uncertain_slots(self):
        records=[]
        for k in range(60):
            row=record(str(k),'phase2');row.update(physical_model_index=k,visibility=1.,color=('red','yellow','black')[k%3],
                color_reliability=1.,phase2_identity_reliability=1.,phase1_reliability=1.)
            records.append(row)
        before=copy.deepcopy(records);result=search(records,60)
        self.assertEqual(result[0]['period'],3);self.assertEqual(result[0]['unknown_slots'],0);self.assertEqual(records,before)
        for r in records:
            if r['physical_model_index']%3==1:r['color']='unknown'
        p=next(r for r in search(records,60) if r['period']==3);self.assertEqual(p['sequence'][1],'unknown')


if __name__=='__main__':unittest.main()

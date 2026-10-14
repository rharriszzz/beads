"""Radius, physical units, handedness, closure, visibility and identity failures."""
import copy,json,unittest
import numpy as np
from photo2.construction_r278 import *
from photo2.reconstruct_r278 import assign,Evidence
from photo2.reconstruct_r276 import scene as legacy_scene
from photo2.bead_detection.phase1_r278 import confidence_gate


class ConstructionTests(unittest.TestCase):
    def test_maker_formula_and_legacy_default(self):
        self.assertAlmostEqual(Rope(2600).bead_radius,2.110915748921366)
        self.assertAlmostEqual(Rope(2600,radius_convention='intended').bead_radius,1.784536980648071)
        self.assertRaises(ValueError,Rope,2600,radius_convention='silent')

    def test_radius_propagates_to_source_length_height_and_samples(self):
        old=Rope(2600);new=Rope(2600,radius_convention='intended');ratio=new.bead_radius/old.bead_radius
        self.assertAlmostEqual(new.chain_major/old.chain_major,ratio)
        a=old.place([0,100])[0];b=new.place([0,100])[0]
        np.testing.assert_allclose(b[:,2]-a[:,2],2*(new.bead_radius-old.bead_radius))
        p=surface_samples(new.bead_radius)
        np.testing.assert_allclose(sdf(p,new.bead_radius),0,atol=2e-15)
        self.assertAlmostEqual(abs(p[:,0]).max(),.7*new.bead_radius)
        self.assertGreater(sdf([[0,0,0]],new.bead_radius)[0],0) # hole remains empty

    def test_source_helicity_keeps_major_traversal(self):
        a=Rope(2600,helicity=1,radius_convention='intended');b=Rope(2600,helicity=-1,radius_convention='intended')
        i=np.arange(100)
        np.testing.assert_array_equal(a.coordinates(i)[0],b.coordinates(i)[0])
        np.testing.assert_array_equal(a.coordinates(i)[1],-b.coordinates(i)[1])
        self.assertGreater(np.linalg.norm(a.place(i)[0]-b.place(i)[0]),10)

    def test_both_hands_closure_and_neighbor_modulo(self):
        for n in (1950,2300,2696):
            for h in (-1,1):
                s=Scene(base_model(n,h),DEFAULT);g=s.model.geometry([0,n])
                np.testing.assert_allclose(g['centers'][0],g['centers'][1],atol=2e-10)
                for d in (-7,-6,-1,1,6,7):self.assertEqual(((n-1+d)%n-d)%n,n-1)
                self.assertAlmostEqual(s.model.length,s.model.source.nrows*.65*2*s.radius*1.05,places=8)

    def test_normalized_scene_exact_legacy_replay(self):
        b=initial_base();b.update(bead_radius=RADIUS,rope_radius=4.)
        a=legacy_scene(b,DEFAULT);b=Scene(b,DEFAULT);xy=a.pc[::9]
        da=a.camera(xy);db=b.camera(xy)
        for key in ('owner','points','normal','unknown'):np.testing.assert_array_equal(da[key],db[key])

    def test_change_world_units_preserves_projection_and_visibility(self):
        b=base_model(2300,-1,pitch_factor=1.4);s=Scene(b,DEFAULT);xy=s.pc[::5];a=s.camera(xy)
        scale=1.7;c=copy.deepcopy(b);c['knots']=(np.array(c['knots'])*scale).tolist();c['bead_radius']*=scale;c['rope_radius']*=scale;c['camera']['scale']/=scale
        t=Scene(c,DEFAULT);d=t.camera(xy)
        np.testing.assert_array_equal(a['owner'],d['owner']);np.testing.assert_allclose(a['points']*scale,d['points'],atol=2e-10)
        np.testing.assert_allclose(a['normal'],d['normal'],atol=1e-9)
        np.testing.assert_array_equal(s.blocked(a['points'],[0,0,1])[0],t.blocked(d['points'],[0,0,1])[0])

    def test_radius_correction_changes_rope_projection_not_just_image_size(self):
        a=Scene(base_model(2600,1,'legacy'),DEFAULT);b=Scene(base_model(2600,1,'intended'),DEFAULT)
        np.testing.assert_allclose(a.model.view.project(a.g['line']),b.model.view.project(b.g['line']),atol=1e-8)
        self.assertGreater(np.max(np.linalg.norm(a.pc-b.pc,axis=1)),1)

    def test_source_collision_correction_is_partial(self):
        a=contact_audit(Scene(base_model(2600,1,'legacy'),DEFAULT),8,8)
        b=contact_audit(Scene(base_model(2600,1,'intended'),DEFAULT),8,8)
        self.assertGreater(a['families']['1']['penetrations'],2000)
        self.assertEqual(b['families']['1']['penetrations'],0)
        self.assertGreater(b['families']['6']['penetrations'],0)

    def test_one_to_one_and_missing_owner(self):
        owners,support=assign([{2:.9,3:.1},{2:.8,3:.2},{}],5)
        self.assertEqual(len(set(owners[owners>=0])),sum(owners>=0));self.assertEqual(owners[-1],-1)
        self.assertEqual(support[-1],0)

    def test_failed_upstream_cap_never_promoted(self):
        r=dict(accepted=True,color='red',recovery_method='r274-broad',confidence={'pre_retreat_pixels':871},region={'pixel_count':100},reasons=[])
        confidence_gate(r);self.assertFalse(r['accepted']);self.assertIn('native-size-cap',r['reasons'])

    def test_small_core_does_not_establish_physical_identity(self):
        r=dict(accepted=True,color='red',recovery_method='stable-peak-supported-rounded-core',confidence={},region={'pixel_count':100},reasons=[])
        confidence_gate(r);self.assertFalse(r['accepted'])

    def test_synthetic_visible_truth_discriminates_both_hands(self):
        # Known surfaces create positive pixels, never guessed center labels.
        for h in (-1,1):
            b=base_model(130,h,pitch_factor=1.5);b['knots']=(np.array(b['knots'])*8).tolist();b['camera']['scale']/=8
            truth=Scene(b,DEFAULT);xy=truth.pc;good=truth.camera(xy)['owner']
            keep=good>=0;correct=truth.camera(xy[keep])['owner'];other=copy.deepcopy(b);other['h']=-h
            wrong=Scene(other,DEFAULT).camera(xy[keep])['owner']
            self.assertTrue(len(correct)>20);self.assertGreater(np.mean(correct!=wrong),.3)

    def test_analytic_envelope_bounds_complete_surface(self):
        from photo2.contact_r278 import support
        r=radius();p=surface_samples(r,128,128);rng=np.random.default_rng(278)
        directions=unit(rng.normal(size=(60,3)))
        expected=support(directions,np.broadcast_to([1,0,0],directions.shape),r)
        sampled=np.max(p@directions.T,axis=0)
        self.assertTrue(np.all(sampled<=expected+1e-12))
        self.assertLess(np.max(expected-sampled),.002)

    def test_separation_witness_distinguishes_overlap(self):
        from photo2.contact_r278 import certificate
        a=Scene(base_model(2600,1,pitch_factor=1.),DEFAULT)
        self.assertFalse(certificate(a,40)['certified'])
        b=Scene(base_model(2600,1,pitch_factor=1.4),DEFAULT)
        self.assertTrue(certificate(b)['certified'])

    def test_general_frame_rays_match_axisymmetric_legacy(self):
        from photo2.surface_r278 import camera,blocked
        s=Scene(base_model(2080,-1,pitch_factor=1.4),DEFAULT);xy=s.pc[::5]
        a=s.camera(xy);b=camera(s,xy)
        np.testing.assert_array_equal(a['owner'],b['owner'])
        np.testing.assert_allclose(a['normal'],b['normal'],atol=1e-8)
        p=a['points'][a['owner']>=0]+a['normal'][a['owner']>=0]*.001
        np.testing.assert_array_equal(s.blocked(p,[.1,.2,1])[0],blocked(s,p,[.1,.2,1])[0])

    def test_tilted_frame_and_perspective_keep_centerline_convention(self):
        a=base_model(2696,1);b=base_model(2696,1,focal=9598.)
        sa=Scene(a,DEFAULT);sb=Scene(b,DEFAULT)
        np.testing.assert_allclose(sa.model.view.project(np.array(a['knots'])),sb.model.view.project(np.array(b['knots'])),atol=1e-9)
        b['hole_tilt_deg']=-8;s=Scene(b,DEFAULT)
        t,n,z=[s.g[k] for k in ('surface_tangent','surface_normal','surface_binormal')]
        np.testing.assert_allclose(np.sum(t*n,axis=1),0,atol=1e-14)
        np.testing.assert_allclose(np.sum(t*z,axis=1),0,atol=1e-14)
        self.assertTrue(np.isfinite(s.camera(s.pc[::10])['normal']).all())

    def test_geometry_assisted_color_abstains_on_paper_transition(self):
        from photo2.reconstruct_r278 import classify_pixels
        hsv=np.zeros((4,5,3));hsv[:]=[339/360,.5,.4];xy=np.array([(x,y) for y in range(4) for x in range(5)])
        color,_=classify_pixels(xy,hsv,{'red':352/360,'yellow':35/360})
        self.assertEqual(color,'unknown')

    def test_geometry_assisted_black_requires_reflection_and_body(self):
        from photo2.reconstruct_r278 import classify_pixels
        hsv=np.zeros((4,5,3));hsv[:]=[0,0,.06];xy=np.array([(x,y) for y in range(4) for x in range(5)]);proto={'red':352/360,'yellow':35/360}
        self.assertEqual(classify_pixels(xy,hsv,proto)[0],'unknown')
        hsv[0,:2]=[0,0,.9]
        self.assertEqual(classify_pixels(xy,hsv,proto)[0],'black')


if __name__=='__main__':unittest.main()

"""Independent invariants and failure controls for R276."""
import copy, json, unittest
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import least_squares
from photo2.reconstruct_r276 import (Model,DEFAULT,initial_base,physical,basis,integral_strain,
    scene,light,bright_prediction,stats,Evaluation)
from photo2.bead_debugger.refit import BeadCurve
from photo2.bead_debugger.surface import unit,shade
from photo2.bead_debugger.test_surface import synthetic

class ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.base=initial_base()
    def test_zero_parameter_exact_inherited_geometry(self):
        old=BeadCurve(self.base);new=Model(self.base,DEFAULT);ii=np.arange(self.base['n'])
        for key in ('centers','tangent','radial','line'):
            np.testing.assert_allclose(new.geometry(ii)[key],old.geometry(ii)[key],atol=2e-9)
    def test_fixed_length_bending(self):
        p=DEFAULT.copy();p[:4]=[5,-4,3,2];m=Model(self.base,p);d=physical(m)
        self.assertLess(abs(d['length_error_units']),1e-9);self.assertEqual(d['closure_position_units'],0)
        self.assertEqual(d['closure_tangent_units'],0);self.assertGreater(d['material_jacobian_min'],0)
    def test_zero_strain_uses_physical_arclength_nonuniform_chart(self):
        # Deliberately unequal physical speed: angular averaging would be wrong.
        t=np.linspace(0,1,100001);speed=1+.65*np.cos(2*np.pi*t)
        s=np.r_[0,cumulative_trapezoid(speed,t)];a=np.array([.003,.004,-.001,.002])
        epsilon=basis(s/s[-1])@a
        self.assertLess(abs(np.trapezoid(epsilon,s)),1e-10)
        self.assertGreater(abs(np.trapezoid(basis(t)@a,s)),.001)
        self.assertLess(abs(integral_strain(1.,a)),1e-15)
    def test_material_order_and_integer_closure(self):
        p=DEFAULT.copy();p[4:8]=[.005,-.005,.005,.005];p[8:12]=[.05,-.06,.02,.03]
        m=Model(self.base,p);d=physical(m);self.assertGreater(d['material_jacobian_min'],.98)
        self.assertLess(abs(d['strain_integral_units']),1e-6);self.assertLess(abs(d['phase_closure_error_rad']),1e-12)
        g=m.geometry([0,self.base['n']]);np.testing.assert_allclose(g['centers'][0],g['centers'][1],atol=1e-9)
    def test_twist_does_not_move_centerline(self):
        a=Model(self.base,DEFAULT);p=DEFAULT.copy();p[8]=.06;b=Model(self.base,p);ii=np.arange(0,2696,7)
        np.testing.assert_allclose(a.geometry(ii)['line'],b.geometry(ii)['line'])
        self.assertGreater(np.max(np.linalg.norm(a.geometry(ii)['centers']-b.geometry(ii)['centers'],axis=1)),.1)
    def test_strain_does_not_change_curve_or_material_phase(self):
        p=DEFAULT.copy();p[4]=.004;a=Model(self.base,DEFAULT);b=Model(self.base,p);ii=np.arange(2696)
        np.testing.assert_allclose(a.curve(a.q),b.curve(b.q))
        ga=a.geometry(ii);gb=b.geometry(ii)
        np.testing.assert_allclose(ga['radial'][:,2],gb['radial'][:,2],atol=1e-12)
        self.assertGreater(np.max(np.linalg.norm(ga['line']-gb['line'],axis=1)),.5)
    def test_hole_axes_tangent_and_normals_orthogonal(self):
        g=Model(self.base,DEFAULT).geometry(np.arange(2696))
        np.testing.assert_allclose(np.sum(g['tangent']*g['normal'],axis=1),0,atol=1e-12)
        np.testing.assert_allclose(np.sum(g['tangent']*g['radial'],axis=1),0,atol=1e-12)
    def test_both_hands_all_counts_close(self):
        for n in (2674,2681,2696,2700):
            for h in (-1,1):
                m=Model(initial_base(n,h),DEFAULT);g=m.geometry([0,n])
                np.testing.assert_allclose(g['centers'][0],g['centers'][1],atol=1e-9)
    def test_uniform_material_correction(self):
        base=copy.deepcopy(self.base);base['uniform_material']=True
        p=DEFAULT.copy();p[4:8]=[.003,-.002,.001,.001]
        d=physical(Model(base,p));speed=d['total_material_speed_relative_to_uniform']
        self.assertGreater(speed['min'],.99);self.assertLess(speed['max'],1.01)
        self.assertLess(abs(d['strain_integral_units']),1e-6)
    def test_failed_prediction_not_dropped(self):
        self.assertIsNone(bright_prediction(np.array([[0,0]]),np.array([0.])))
        self.assertEqual(stats([1,30])['n'],2)
    def test_metric_hypothesis_preserves_projected_centers(self):
        b=copy.deepcopy(self.base);size=.85
        b['knots']=(np.array(b['knots'])/size).tolist();b['camera']['scale']*=size;b['rope_radius']=4/size
        a=Model(self.base,DEFAULT);m=Model(b,DEFAULT);ii=np.arange(0,2696,9)
        np.testing.assert_allclose(a.view.project(a.geometry(ii)['centers']),m.view.project(m.geometry(ii)['centers']),atol=1e-8)
        self.assertAlmostEqual(m.length,a.length/size,places=8)
    def test_empty_yellow_and_holdout_fit_rejected(self):
        from types import SimpleNamespace
        from photo2.reconstruct_r276 import fit_light
        for rows in ([dict(split='train',color='black',specular_candidate=True)], [dict(split='holdout',color='yellow',specular_candidate=True)]):
            with self.assertRaises(ValueError):fit_light(SimpleNamespace(rows=rows),DEFAULT)
    def test_collision_audit_catches_inherited_penetration(self):
        from photo2.diagnose_r276 import collision_audit
        d=collision_audit(scene(self.base,DEFAULT))
        self.assertGreater(d['families']['1']['penetrating_pairs'],2500)
        self.assertLess(d['families']['6']['minimum_sdf_units'],-.1)
    def test_fixed_correspondences_stay_in_same_count_and_hand(self):
        root=Path('photo2/review/r276');frozen=json.loads((root/'contact_joint-fixed-correspondence.json').read_text())
        current=json.loads((root/'contact_joint.json').read_text())['base']
        reference=json.loads((root/(frozen['reference_model']+'.json')).read_text())['base']
        self.assertEqual((current['n'],current['h']),(reference['n'],reference['h']))
        self.assertEqual(frozen['reference_model'],'packing_N1950_h-1')
    def test_untrimmed_max_retained(self):
        r=stats([1,2,100]);self.assertEqual(r['maximum'],100);self.assertGreater(r['rms'],57)
    def test_bright_patch_connected_peak(self):
        y,x=np.mgrid[:4,:12];xy=np.c_[x.ravel(),y.ravel()];v=np.zeros(len(xy));v[(x.ravel()<3)]=1;v[(x.ravel()>8)]=.9
        h=bright_prediction(xy,v);self.assertLess(h['centroid'][0],3);self.assertEqual(h['competing_high_pixels'],12)
    def test_light_shared_direction_not_projected_offset(self):
        s=synthetic([[0,0,0],[5,0,0]]);d=s.grid([20,20,130,80],1);p=DEFAULT.copy();p[19:21]=[-120,60]
        a=shade(s,d,light(p));self.assertTrue(np.isfinite(a['specular']).all());self.assertGreater(a['specular'].max(),0)
    def test_synthetic_inverse_direction_from_independent_half_normals(self):
        # Independent analytic half-vector observations, no renderer-generated target.
        truth=unit([-.3,.2,.93]);view=unit(np.array([[.1,0,1],[-.1,.2,1],[.2,-.3,1],[0,0,1]]))
        normals=unit(view+truth)
        def residual(v):return (unit(view+unit(v))-normals).ravel()
        fit=least_squares(residual,[.1,-.1,1]);self.assertLess(np.linalg.norm(unit(fit.x)-truth),1e-6)
    def test_holdout_never_enters_training_rows(self):
        rows=[dict(strong=True,split='holdout'),dict(strong=False,split='train')]
        # Empty construction requires no observation coordinates; inspect filter
        # through a nonempty data fixture instead.
        allrows=json.loads(Path('photo2/review/r276/observations.json').read_text())['observations']
        e=Evaluation(self.base,allrows);self.assertTrue(e.rows);self.assertTrue(all(r['split']=='train' and r['strong'] for r in e.rows))
    def test_saved_observations_equal_original_coordinates_masks(self):
        source=json.loads(Path('photo2/review/r275/inventory.json').read_text());loc={r['id']:r for r in source['locations']};bead={r['id']:r for r in source['beads']}
        rows=json.loads(Path('photo2/review/r276/observations.json').read_text())['observations'];self.assertEqual(len(rows),810)
        for r in rows:
            self.assertEqual(r['brightest'],loc[r['id']]['point']);self.assertEqual(r['bright_patch'],loc[r['id']]['bright_patch'])
            self.assertEqual(r['region_runs'],bead[r['id']]['region']['runs'] if r['id'] in bead else [])

if __name__=='__main__':unittest.main()

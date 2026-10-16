"""Independent algebra, fixed-owner controls, full-circuit coverage and trend contracts."""
import unittest
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,load_evidence
from photo2.r297.geometry import reference
from photo2.r298.geometry import Chain
from .analyze import trend,PRINCIPAL
BASE=ROOT/'photo2/r300'

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=read(BASE/'results/analysis.json');cls.rows=read(BASE/'results/ledger.json');cls.controls=read(BASE/'results/crossed-controls.json')['controls']

    def test_frozen_measurements_and_owners_all_988(self):
        for name in self.d['models']:
            old=read(ROOT/f'photo2/r299/results/native-{name}.json.gz');rr=[r for r in self.rows if r['model']==name]
            self.assertEqual(len(rr),52);self.assertEqual(sum(r['trusted'] for r in rr),45)
            for r,z in zip(rr,old['records']):
                self.assertEqual(r['id'],z['id']);self.assertEqual(r['index'],z['ownership']['index']);self.assertEqual(r['observed_centroid'],z['observed_centroid']);self.assertEqual(r['exists'],z['exists'])
                for kind in ['peak','centroid']:self.assertEqual(r[kind+'_xy'],z[kind+'_residual'])

    def test_residual_components_and_units(self):
        for r in self.rows:
            t=np.array(r['tangent']);n=np.array(r['normal']);self.assertAlmostEqual(t@t,1);self.assertAlmostEqual(n@t,0)
            for kind in ['peak','centroid']:
                if not r['exists']:self.assertIsNone(r[kind+'_tn']);continue
                v=np.array(r[kind+'_xy']);a,b=r[kind+'_tn'];np.testing.assert_allclose(a*t+b*n,v,atol=1e-12)
                self.assertAlmostEqual(np.hypot(a,b)/r['diameter_px'],r[kind+'_diameters']);self.assertAlmostEqual(a/r['pitch_px'],r[kind+'_index_equivalent'])

    def test_accumulation_is_difference_not_sum(self):
        for name in PRINCIPAL:
            ordered=self.d['models'][name]['groups']['centroid']['trusted']['ordered'];diff=ordered['local_index_increment'];net=ordered['net_index_displacement']
            np.testing.assert_allclose(np.r_[0,np.cumsum(diff)],net,atol=1e-12);self.assertAlmostEqual(sum(diff),ordered['endpoint_index_change'])
            self.assertAlmostEqual(ordered['cusum_mean_parallel'][-1],0)

    def test_trend_known_ramp_and_constant(self):
        x=(np.arange(48)+.5)/48;sectors=(x*16).astype(int)
        a=trend(x,3+12*x,sectors);self.assertAlmostEqual(a['slope'],12);self.assertAlmostEqual(a['r2'],1)
        b=trend(x,np.full(48,10.),sectors);self.assertAlmostEqual(b['slope'],0);self.assertAlmostEqual(b['r2'],0)

    def test_actual_seams_not_bead_zero(self):
        for name in PRINCIPAL:
            s=self.d['models'][name]['seam']['centroid'];self.assertTrue(.48<s['fraction']<.50)
        s=self.d['models']['joint-15']['seam']['centroid'];self.assertEqual(s['windows'][0]['after_ids'],[]);self.assertGreater(s['nearest_after_distance_fraction'],.05)

    def test_crossed_controls_no_geometry_or_owner_changes(self):
        for control in self.controls:
            old=read(ROOT/f'photo2/r299/results/native-{control["geometry"]}.json.gz');source=read(ROOT/f'photo2/r299/results/native-{control["light_source"]}.json.gz')
            self.assertEqual(control['parameters'],old['parameters']);self.assertEqual(control['light'],source['light']);self.assertEqual(control['light']['direction'],old['light']['direction']);self.assertEqual(control['geometry_checks'],old['geometry']['metrics']);self.assertTrue(control['physical']['certified']);self.assertEqual(control['physical']['pairs'],7262)
            for a,b in zip(control['records'],old['records']):self.assertEqual(a['ownership'],b['ownership']);self.assertEqual(a['observed_peak'],b['observed_peak']);self.assertEqual(a['observed_centroid'],b['observed_centroid'])

    def test_source_geometry_positions_and_pitch(self):
        inputs,_=load_evidence()
        for name in PRINCIPAL:
            old=read(ROOT/f'photo2/r299/results/native-{name}.json.gz');s=Chain(old['parameters'],inputs);np.testing.assert_allclose(s.pc,old['positions'],atol=1e-10,rtol=0)
            for r in [r for r in self.rows if r['model']==name]:
                k=r['index'];line,_,_=s.placement(np.array([k-.005,k+.005]));diff=np.diff(s.project(line),axis=0)[0]/.01
                self.assertLess(abs(np.linalg.norm(diff)-r['pitch_px']),.005)

    def test_complete_denominators_and_common_subset(self):
        self.assertEqual(len(self.d['models']),19);self.assertEqual(len(self.rows),988);self.assertEqual(len(self.d['common_principal_ids']),42)
        for name,m in self.d['models'].items():
            a=m['groups']['centroid']['trusted'];self.assertEqual(a['n'],45);self.assertEqual(a['predicted']+len(a['missing_ids']),45);self.assertEqual(sum(r['n'] for r in a['regions']),a['predicted']);self.assertEqual(len(a['regions']),16)

if __name__=='__main__':unittest.main()

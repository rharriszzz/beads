"""Targeted construction, predictor and delivered-science contracts."""
import unittest
import numpy as np
from .core import *
from photo2.r301.export import full_predict

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=read(BASE/'evidence/section.json.gz')
        cls.v=np.array(read(BASE/'evidence/protocol.json')['starts'][0]['parameters'])

    def test_cumulative_twist_not_fixed_interval(self):
        widths=[]
        for count in [2000,2709,6000,12000]:
            lo,hi=twist_bounds(count);widths.append(hi-lo)
            self.assertAlmostEqual(count*(6.5/lo-1),6.5,places=10)
            self.assertAlmostEqual(count*(6.5/hi-1),-6.5,places=10)
        self.assertTrue(all(a>b for a,b in zip(widths,widths[1:])))
        with self.assertRaises(ValueError):twist_bounds(1999)

    def test_bending_preserves_arclength_and_extension_is_bounded(self):
        for strain in [-.02,.02]:
            v=self.v.copy();v[17]=strain;v[15]=.015
            c=Scene(v,self.s,-1,guards=96)
            self.assertLessEqual(np.max(abs(c.advance/v[4]-1)),.020000001)
            delta=np.diff(c.arc);chord=np.linalg.norm(np.diff(c.line,axis=0),axis=1)
            np.testing.assert_allclose(chord,delta*np.sinc(v[15]*delta/(2*np.pi)),atol=1e-12)
            # A nonsymmetric interval can have nonzero net effective extension.
            k=np.searchsorted(c.indices,[0,12]);self.assertGreater(abs(np.diff(c.arc[k])[0]/(12*v[4])-1),.001)
            np.testing.assert_allclose(np.diff(c.phase),-2*np.pi/v[5],atol=1e-12)

    def test_native_replacement_matches_old_complete_grid(self):
        c=Scene(self.v,self.s,-1)
        a,_=native(c,self.s)
        b,_=full_predict(c,self.s,light_params([self.v[10],self.v[11],10.],'directional',c.centers.mean(0)))
        a={r['index']:r for r in a};b={r['index']:r for r in b}
        self.assertEqual(set(a),set(b))
        for k in a:np.testing.assert_allclose(a[k]['point'],b[k]['point'],atol=1e-12)

    def test_withheld_excluded_from_training_and_sensitivity(self):
        a=evaluate(self.v,self.s,-1)
        s=deepcopy(self.s)
        for r in s['observations']:
            if r['split']=='withheld':r['point']=[0.,0.]
        s['diagnostic_separators']=[]
        for i,h in enumerate(s['cues']['withheld']):
            if h:s['cues']['xy'][i]=[0.,0.];s['cues']['color'][i]=9;s['cues']['paper'][i]=True
        b=evaluate(self.v,s,-1)
        self.assertEqual(a['loss'],b['loss'])
        held={r['id'] for r in self.s['observations'] if r['split']=='withheld'}
        for d in read(BASE/'results/diagnosis.json.gz')['sensitivity']:
            self.assertFalse(held&{x[0] for x in d['anchors']['reflection']})
            self.assertEqual(sum(g=='prediction_only' for g in d['groups']),28)

    def test_density_guard_rejects_extra_position_strategy(self):
        v=self.v.copy();v[0]=.08;v[4]=.15
        r=evaluate(v,self.s,-1)
        self.assertFalse(r['feasible'])
        self.assertGreater(r['loss'],1000)

    def test_delivered_budget_and_physical_witnesses(self):
        path=BASE/'results/fit-freeze.json'
        if not path.exists():self.skipTest('Fit not sealed yet')
        seal=read(path);self.assertLessEqual(seal['numerical_seconds'],600)
        self.assertEqual(len(seal['selected']),8)
        for r in seal['selected']:
            c=Scene(r['parameters'],self.s,r['hand']);cert=c.certify(iterations=100)
            self.assertTrue(cert['certified'])
            for w in cert['witnesses']:
                a,b=w['pair'];n=np.array(w['normal'])
                gap=(c.centers[b]-c.centers[a])@n-c.support(n,c.g[AXES[0]][a])-c.support(n,c.g[AXES[0]][b])
                self.assertAlmostEqual(gap,w['gap_units'],places=10)
                self.assertGreater(gap,1e-6)

if __name__=='__main__':unittest.main()

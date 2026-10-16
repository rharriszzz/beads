"""Scientific contracts for coupling, sharing, evidence and native equivalence."""
import unittest
import numpy as np
from .core import *

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ss=read(BASE/'evidence/sections.json.gz');cls.v=np.array(read(BASE/'evidence/protocol.json')['starts'][0]['parameters'])

    def test_source_units_and_invertible_calibration(self):
        from photo2.bead_placement import Rope
        r=Rope(2000);D=2*r.bead_radius;H=.70*D;row=2*np.pi*r.chain_major/r.nrows
        self.assertAlmostEqual(row/H,.975)
        self.assertAlmostEqual(2*np.pi*r.chain_major/r.nbeads,row/r.exact_beads_per_row)
        for axial in [.08,.7,.95]:
            for pitch in [.035,.23,.4]:
                v=self.v.copy();v[0]=axial;v[4]=pitch
                np.testing.assert_allclose(physical(encode(v,'calibrated'),'calibrated'),v,atol=1e-15)
                c=encode(v,'calibrated')[4];self.assertTrue(bounds('calibrated')[4,0]<=c<=bounds('calibrated')[4,1])

    def test_native_independent_calibrated_equivalence(self):
        a=evaluate(self.v,self.ss[0],-1,'independent',True)
        b=evaluate(encode(self.v,'calibrated'),self.ss[0],-1,'calibrated',True)
        self.assertTrue(a['feasible']);self.assertAlmostEqual(a['loss'],b['loss'],places=10)
        for x,y in zip(a['predictions'],b['predictions']):np.testing.assert_allclose(x['point'],y['point'],atol=1e-10)

    def test_source_coupling_and_smooth_correction(self):
        v=encode(self.v,'source');v[17]=.02;c=Scene(v,self.ss[0],-1,'source')
        self.assertAlmostEqual(c.p['pitch']*c.p['turn']/(2*c.axial),.975)
        np.testing.assert_allclose(c.advance,.975*2*c.axial/c.p['turn']*(1+.02*np.tanh(c.indices/14)))
        self.assertLessEqual(np.max(abs(c.advance/c.p['pitch']-1)),.020000001)
        delta=np.diff(c.arc);np.testing.assert_allclose(np.linalg.norm(np.diff(c.line,axis=0),axis=1),delta*np.sinc(c.p['curve']*delta/(2*np.pi)),atol=1e-12)

    def test_withheld_has_no_effect_on_training(self):
        for s in self.ss:
            v=self.v.copy();a=evaluate(v,s,-1,'independent');q=deepcopy(s)
            for r in q['observations']:
                if r['split']=='withheld':r['point']=[0,0]
            for i,h in enumerate(q['cues']['withheld']):
                if h:q['cues']['xy'][i]=[0,0];q['cues']['paper'][i]=True;q['cues']['color'][i]=9
            q['diagnostic_separators']=[];b=evaluate(v,q,-1,'independent');self.assertEqual(a['loss'],b['loss'])

    def test_shared_transfer_and_joint_parameters(self):
        seal=read(BASE/'results/fit-freeze.json');r=seal['selected']
        for mode in MODES:
            for hand in [-1,1]:
                rows=[x for x in r if x['mode']==mode and x['hand']==hand]
                frozen=[x for x in rows if x['stage']!='joint'];joint=[x for x in rows if x['stage']=='joint']
                for group in [frozen,joint]:
                    self.assertEqual(len(group),3)
                    for x in group:np.testing.assert_array_equal(x['parameters'][:12],group[0]['parameters'][:12])
                if mode=='source':self.assertTrue(all(x['parameters'][4]==.975 for x in rows))
        self.assertLessEqual(seal['numerical_seconds'],600)

    def test_no_density_rejection(self):
        seal=read(BASE/'results/fit-freeze.json');dense=[]
        for r in seal['selected']:
            d=read(BASE/f'results/native-{r["name"]}.json.gz')['result']
            if d['feasible'] and d['local_positions']>30:dense.append(r['name'])
        self.assertTrue(dense,'Must retain physically certified candidates over30, if predicted')

if __name__=='__main__':unittest.main()

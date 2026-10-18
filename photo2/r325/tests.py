"""Small independent contracts: exhaustive cyclic search and nonzero winding."""
import itertools,unittest
import numpy as np
from .global_solver import solve,objective
from .consistency import synchronize

class Contracts(unittest.TestCase):
    def fixture(self,n=6):
        rng=np.random.default_rng(19);ws=[]
        for i in range(n):
            hh=[]
            for k in range(2):
                ab=np.array([[0,0],[1,0],[0,1],[1,1],[2,1]])
                if k:ab[-1]=[2,0]
                hh.append(dict(score=float(rng.uniform()),assignments={str(j):dict(ab=(q+[i,0]).tolist()) for j,q in enumerate(ab)}))
            ws.append(dict(hypotheses=hh))
        return ws
    def test_exhaustive_cyclic_and_marginals(self):
        ws=self.fixture();sol=solve(ws);scores=[(objective(ws,p),p) for p in itertools.product(range(2),repeat=len(ws))];best=max(s for s,p in scores)
        self.assertAlmostEqual(best,sol['score']);self.assertAlmostEqual(objective(ws,sol['choices']),best)
        for i in range(len(ws)):
            for h in range(2):
                expected=best-max(s for s,p in scores if p[i]==h);self.assertAlmostEqual(expected,sol['max_marginal_gaps'][i][h])
    def test_shifted_origin(self):
        ws=self.fixture();base=solve(ws)
        for shift in [1,3,5]:
            sol=solve(ws[shift:]+ws[:shift]);self.assertAlmostEqual(sol['score'],base['score']);np.testing.assert_allclose(sol['max_marginal_gaps'],base['max_marginal_gaps'][shift:]+base['max_marginal_gaps'][:shift],atol=1e-10)
    def test_closing_factor_changes_early_choice(self):
        ws=self.fixture()
        for w in ws:w['hypotheses'][0]['score']=0.;w['hypotheses'][1]['score']=-20.
        ws[0]['hypotheses'][1]['score']=8.
        open_sol=solve(ws,cyclic=False);closed_sol=solve(ws)
        # The endpoint bonus beats two open overlap penalties but not four cyclic
        # ones: closing evidence must actually revise the early assignment.
        self.assertEqual(open_sol['choices'][0],1)
        self.assertEqual(closed_sol['choices'][0],0)
        self.assertAlmostEqual(objective(ws,closed_sol['choices']),closed_sol['score'])
    def test_nonzero_periodic_closure(self):
        edges=[dict(source=str(i),target=str((i+1)%6),delta_ab=[1,0],supporting_windows=2,consensus=1.,reasons=[]) for i in range(6)]
        accepted,conflicts,coords,components,c=synchronize(edges,[],{str(i):i for i in range(6)},6.)
        self.assertEqual(len(accepted),6);self.assertFalse(conflicts);self.assertTrue(c['identified']);self.assertEqual(c['holonomy_ab'],[6,0]);self.assertEqual(c['count_candidates'],{'A':42,'B':36})
    def test_unidentifiable_open_arc(self):
        edges=[dict(source=str(i),target=str(i+1),delta_ab=[1,0],supporting_windows=2,consensus=1.,reasons=[]) for i in range(4)]
        _,_,_,_,c=synchronize(edges,[],{str(i):i for i in range(5)},6.)
        self.assertFalse(c['identified']);self.assertIsNone(c['count_candidates'])

if __name__=='__main__':unittest.main()

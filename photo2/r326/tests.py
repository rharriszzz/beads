"""Independent small contracts for the new compatibility representation."""
import itertools,unittest
import numpy as np
from .compatibility import reconsider,compatible_subset,relations,cycle_audit
from .contexts import rescore

class Contracts(unittest.TestCase):
    def fixture(self):
        # Windows0 and3 share observations: outside the cyclic factor radius.
        windows=[]
        for i in range(6):
            ids=['a','b','c'] if i in [0,3] else [f'{i}a',f'{i}b',f'{i}c']
            hs=[]
            for k in range(2):
                ab=[[0,0],[1,0],[0,1]] if k==0 else [[0,0],[0,1],[1,0]]
                hs.append(dict(score=3.,assignments={o:dict(ab=q) for o,q in zip(ids,ab)}))
            windows.append(dict(id=i,arc_px=i,observation_ids=ids,hypotheses=hs))
        return windows
    def test_joint_reconsideration_and_bruteforce(self):
        ws=self.fixture();sol=dict(choices=[0,0,0,1,0,0],max_marginal_gaps=[[0,2],[0,2],[0,2],[1,0],[0,2],[0,2]])
        selected,audit=reconsider(ws,sol,{},6.)
        self.assertTrue(audit['cycle_audit']['compatible']);self.assertEqual(len(audit['selected_windows']),6)
        self.assertEqual(selected[0],selected[3]);best=-1e9
        for choices in itertools.product([None,0,1],repeat=6):
            active,conflicts,links=relations(ws,choices,{},6.)
            if conflicts or cycle_audit(set(active),links)[0]:continue
            score=sum(20-sol['max_marginal_gaps'][i][k] for i,k in enumerate(choices) if k is not None);best=max(best,score)
        actual=sum(20-sol['max_marginal_gaps'][i][ss[0]] for i,ss in enumerate(selected) if ss)
        self.assertAlmostEqual(actual,best)
    def test_marginal_pool_not_one_solution(self):
        ws=self.fixture();sol=dict(choices=[0,0,0,1,0,0]);selected,audit=compatible_subset(ws,sol,{},6.)
        self.assertEqual(len(audit['selected_windows']),5)
        self.assertFalse(selected[0] and selected[3])
    def test_nonzero_winding_and_inconsistent_cycle(self):
        links=[(0,1,np.array([1,0]),0),(1,2,np.array([1,0]),0),(2,0,np.array([1,0]),1)]
        bad,audit=cycle_audit({0,1,2},links);self.assertFalse(bad);self.assertEqual(audit['possible_holonomies'],[[3,0]])
        links[-1]=(2,0,np.array([1,0]),0)
        self.assertTrue(cycle_audit({0,1,2},links)[0])
    def test_correlated_context_duplicates_do_not_multiply_penalty(self):
        ws=self.fixture();ctx=dict(parent=0,id='a',hypotheses=[dict(score=3.,assignments={'a':dict(ab=[0,0]),'b':dict(ab=[0,1]),'c':dict(ab=[1,0])})])
        rescore(ws,[ctx]);first=ws[0]['hypotheses'][0]['context_penalty']
        rescore(ws,[ctx,dict(ctx,id='b')]);self.assertEqual(first,ws[0]['hypotheses'][0]['context_penalty'])
    def test_missing_observation_does_not_imply_relation(self):
        ws=self.fixture();ws[3]['hypotheses'][0]['assignments']={'a':dict(ab=[0,0])}
        active,conflicts,links=relations(ws,[0]*6,{},6.);self.assertFalse(conflicts)

if __name__=='__main__':unittest.main()

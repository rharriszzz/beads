"""Independent geometry controls for experimental neighbor proposals."""
import unittest
import numpy as np

from infer_neighbors import infer
from inference_audit import mask_features, evaluate
from inference_controls import brick_ring


class InferredNeighborsChecks(unittest.TestCase):
    def test_clean_brick_ring_pairs_labels_and_indices(self):
        xy,cov,truth,n=brick_ring()
        for moments in (None,cov):
            output=infer(xy,moments)
            result=evaluate(truth,n,output['variants'][0])
            summary=result['summary']
            self.assertGreater(summary['proposed_edges'],len(xy))
            self.assertEqual(summary['true_neighbor_pairs'],summary['proposed_edges'])
            self.assertEqual(summary['signed_correct_by_global_reversal'][1],summary['proposed_edges'])
            self.assertEqual(summary['consistent_wrong_nonseed_up_to_reversal'],0)
            self.assertEqual(summary['inconsistent_nontrivial_components'],0)

    def test_relabel_and_rigid_motion_invariance(self):
        xy,cov,_,_=brick_ring()
        base=infer(xy,cov)
        permutation=np.random.Generator(np.random.PCG64(43)).permutation(len(xy))
        angle=.731
        rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        moved=infer(xy[permutation]@rotation.T+[723,-40],
                    rotation@cov[permutation]@rotation.T)
        for a,b in zip(base['variants'],moved['variants']):
            def canonical(edges,mapping):
                return sorted((min(mapping[u],mapping[v]),max(mapping[u],mapping[v]),
                               d if mapping[u]<mapping[v] else -d) for u,v,d in edges)
            self.assertEqual(canonical(a['edges'],np.arange(len(xy))),canonical(b['edges'],permutation))

    def test_empty_and_degenerate_inputs_rejected(self):
        for xy in ([],[[0,0]]*4,[[0,0],[1,0],[2,0],[3,0]],[[0,0],[1,0],[0,1],[np.nan,1]]):
            with self.assertRaises(ValueError):
                infer(xy)

    def test_mask_moments_rectangle_and_missing_mask(self):
        ids=np.zeros((10,12),int); ids[2:6,3:11]=1
        size,xy,cov=mask_features(ids,2)
        np.testing.assert_array_equal(size,[32,0])
        np.testing.assert_allclose(xy[0],[6.5,3.5])
        np.testing.assert_allclose(cov[0],[[5.25,0],[0,1.25]])
        self.assertTrue(np.isfinite(cov).all())

    def test_both_conventions_and_reciprocity_are_retained(self):
        xy,cov,_,_=brick_ring()
        result=infer(xy,cov)
        self.assertEqual([v['convention'] for v in result['variants']],[1,-1])
        for v in result['variants']:
            selected={(i,d):entries[0][0] for i,d,entries in v['candidates']
                      if not any(a==i and b==d for a,b,_ in v['ambiguous'])}
            for i,j,d in v['edges']:
                self.assertEqual(selected[i,d],j)
                self.assertEqual(selected[j,-d],i)

    def test_missing_detection_does_not_certify_wrong_bridge(self):
        xy,cov,truth,n=brick_ring()
        keep=np.ones(len(xy),bool); keep[[47,52,57]]=False
        result=evaluate(truth[keep],n,infer(xy[keep],cov[keep])['variants'][0])
        # This deliberately exposes the baseline's failure, not a passing recovery.
        self.assertGreater(result['summary']['proposed_edges'],result['summary']['true_neighbor_pairs'])
        self.assertFalse(result['propagation']['consistent'])
        self.assertEqual(result['index_status'],'diagnostic_only_unvalidated_edges')

    def test_crossing_keeps_label_conventions_symmetric(self):
        xy,cov,_,_=brick_ring()
        points=np.vstack([xy,xy+[1.1*np.max(xy[:,0]),13.]])
        output=infer(points,np.concatenate([cov,cov]))
        a,b=output['variants']
        self.assertEqual({(u,v) for u,v,_ in a['edges']},{(u,v) for u,v,_ in b['edges']})
        for u,v,d in a['edges']:
            other = -d if abs(d)==1 else (1 if d>0 else -1)*(13-abs(d))
            self.assertIn([u,v,other],b['edges'])


if __name__=='__main__':
    unittest.main()

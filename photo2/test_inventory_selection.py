import unittest
import numpy as np
from inventory_selection import PARAMETERS, select_records, filter_labels, silhouette_distance

class SelectionTests(unittest.TestCase):
    def records(self):
        rows=[dict(id=i+1,marker_xy=[20+i*4,30],region_pixels=100,status='reviewed_body',color='red') for i in range(8)]
        return rows

    def test_known_fragment_and_211_excluded_even_if_large(self):
        rows=self.records()+[dict(id=211,marker_xy=[30,30],region_pixels=100,status='reviewed_body',color='red'),dict(id=300,marker_xy=[31,30],region_pixels=200,status='fragment_identity_unresolved',color='red')]
        active,excluded=select_records(rows,np.full((80,80),20.))
        self.assertEqual({r['id'] for r in excluded},{211,300})
        self.assertEqual(len(active),8)

    def test_small_edge_region_excluded_normal_edge_region_retained(self):
        rows=self.records();rows[0]['region_pixels']=30
        active,excluded=select_records(rows,np.full((80,80),2.))
        self.assertEqual([r['id'] for r in excluded],[1])
        self.assertIn('small_local_area_near_edge',excluded[0]['selection']['reasons'])
        self.assertTrue(all(r['selection']['near_edge'] for r in active))

    def test_sparse_reference_does_not_invent_area(self):
        active,excluded=select_records(self.records()[:2],np.full((80,80),20.))
        self.assertEqual(len(active),2);self.assertFalse(excluded)
        self.assertIsNone(active[0]['selection']['area_ratio'])
        self.assertIn('insufficient_local_reference',active[0]['selection']['warnings'])

    def test_large_body_warned_not_silently_removed(self):
        rows=self.records();rows[0]['region_pixels']=250
        active,excluded=select_records(rows,np.full((80,80),20.))
        self.assertFalse(excluded)
        self.assertIn('large_local_area_possible_merge',active[0]['selection']['warnings'])

    def test_exclusions_do_not_reassign_pixels_or_change_ids(self):
        labels=np.array([[0,1,1,2],[3,3,2,2]],np.int32)
        result=filter_labels(labels,[dict(id=1),dict(id=3)])
        np.testing.assert_array_equal(result,[[0,1,1,0],[3,3,0,0]])
        self.assertEqual(labels[0,3],2)

    def test_reference_is_frozen_and_does_not_include_fragments(self):
        rows=self.records();rows[0]['region_pixels']=30
        rows.append(dict(id=300,marker_xy=[24,31],region_pixels=10000,status='fragment_identity_unresolved',color='red'))
        active,excluded=select_records(rows,np.full((80,80),20.))
        all_rows=active+excluded
        self.assertTrue(all(300 not in r['selection']['local_reference_ids'] for r in all_rows))
        self.assertIn(1,next(r for r in active if r['id']==2)['selection']['local_reference_ids'])

    def test_silhouette_retains_large_central_opening(self):
        mask=np.zeros((100,100),bool);mask[10:90,10:90]=True;mask[30:70,30:70]=False
        distance=silhouette_distance(mask)
        self.assertEqual(distance[50,50],0);self.assertGreater(distance[20,20],0)

if __name__=='__main__':unittest.main()

"""Side selection remains provisional, circular stations/gaps remain explicit."""
import unittest
import numpy as np

from colored_centerline_evidence import colored_subset,rim_candidates,diagonal_chains


class ColoredEvidenceTests(unittest.TestCase):
    def test_subset_keeps_missing_black_slots_and_remaps_only_existing_links(self):
        result=dict(points=[dict(kind='chromatic',source_xy=[1,2]),dict(kind='dark-reflection',source_xy=[3,4]),
                            dict(kind='chromatic',source_xy=[5,6])])
        graph=dict(edges=[dict(start=0,end=1,direction='d2'),dict(start=1,end=2,direction='d2'),dict(start=0,end=2,direction='d3')])
        points,filtered=colored_subset(result,graph)
        self.assertEqual([p['original_proposal_number'] for p in points],[1,3])
        self.assertEqual(filtered['edges'],[dict(start=0,end=1,direction='d3')])
        self.assertEqual(diagonal_chains(points,filtered['edges']),[])
        self.assertEqual(len(result['points']),3)

    def test_side_candidates_use_periodic_local_support_not_saved_curve(self):
        points=[dict(observation_number=i+1,station=(990+i*2)%1000,cross=float(x),source_xy=[i,i],support_area=40)
                for i,x in enumerate(np.linspace(-10,10,10))]
        sides=rim_candidates(points,1000,5)
        self.assertEqual({p['side'] for p in sides},{'outer-side','inner-side'})
        self.assertTrue(all(p['local_support']==10 for p in sides))
        for p in points:p['cross']=0.
        self.assertEqual(rim_candidates(points,1000,5),[])

    def test_diagonal_cycles_not_promoted_to_closed_series(self):
        points=[dict(source_xy=[i,0]) for i in range(6)]
        edges=[dict(start=i,end=i+1,direction='d2') for i in [0,1]]
        edges += [dict(start=3,end=4,direction='d3'),dict(start=4,end=5,direction='d3'),dict(start=5,end=3,direction='d3')]
        chains=diagonal_chains(points,edges)
        self.assertEqual(chains[0]['observation_numbers'],[1,2,3])
        self.assertEqual(chains[1]['unresolved_component_numbers'],[4,5,6])
        self.assertNotIn('observation_numbers',chains[1])


if __name__=='__main__':unittest.main()

"""R252 identity/provenance and native-profile regression tests."""
import copy
import json
import unittest
import numpy as np
from photo2.consolidate_colored_observations import (ROOT, OUT, import_sources,
    consolidate, pair_profiles, region_point, sha, read)


class ConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources,primary,black,constraints,paths=import_sources()
        cls.data=dict(sources=sources,primary=primary,black_preserved=black,constraints=constraints)
        cls.decisions=read('photo2/review/r252/decisions.json')
        cls.sources,cls.entities=consolidate(cls.data,cls.decisions)
        cls.rows={r['key']:r for r in cls.sources}

    def test_original_sources_immutable_and_namespaced(self):
        self.assertEqual(len(self.rows),len(self.sources))
        for r in self.data['sources']:
            self.assertEqual(r['original'],self.rows[r['key']]['original'])
            self.assertEqual(r['original_xy'],self.rows[r['key']]['original_xy'])
        # A real reused P number must not inherit another experiment's owner.
        old=self.rows['R235:D3-P04'];new=self.rows['R238:D3-P04']
        self.assertNotEqual(old['original']['source_id'],new['original']['source_id'])
        self.assertNotEqual(old.get('adjudication'),new.get('adjudication'))

    def test_provenance_seals(self):
        for p,h in self.decisions['source_hashes'].items():self.assertEqual(sha(ROOT/p),h,p)

    def test_maker_same_and_distinct_constraints(self):
        for c in self.data['constraints']:
            ids=[self.rows[k]['entity_id'] for k in c['keys']]
            self.assertEqual(len(set(ids)),1 if c['relation']=='same' else len(ids),c)

    def test_harmful_yellow_mask_merge_is_not_adopted(self):
        a=self.rows['R239:D4-A02'];b=self.rows['R239:D4-P14']
        self.assertEqual(a['original']['ownership_decision'],'abstain')
        self.assertEqual(b['original']['ownership_decision'],'abstain')
        self.assertNotEqual(a['entity_id'],b['entity_id'])
        self.assertEqual(a['disposition'],'duplicate_alias')
        self.assertEqual(b['disposition'],'duplicate_alias')

    def test_red_duplicate_is_not_counted_twice(self):
        self.assertEqual(self.rows['R239:D4-P10']['entity_id'],self.rows['R239:D4-A08']['entity_id'])
        self.assertEqual(self.rows['R239:T1-P15']['entity_id'],self.rows['R239:T1-A08']['entity_id'])
        self.assertEqual(self.rows['R114:C']['entity_id'],self.rows['F196-4']['entity_id'])
        self.assertEqual(self.rows['R114:D']['disposition'],'ambiguous')
        self.assertEqual(self.rows['R188:587']['disposition'],'ambiguous')

    def test_conflicting_transitive_identity_rejected(self):
        d=copy.deepcopy(self.decisions)
        d['pairs'].append(dict(keys=['F204-S','F204-Q'],decision='same',evidence='bad-test'))
        with self.assertRaises(ValueError):consolidate(self.data,d)

    def test_closeness_and_valley_do_not_decide_identity(self):
        # Same coordinates alone do not merge independent observations.
        data=copy.deepcopy(self.data)
        for r in data['sources']:
            if r['key'] in ['F204-S','F204-Q']:r['original_xy']=[100.,100.]
        rows,_=consolidate(data,self.decisions);rr={r['key']:r for r in rows}
        self.assertNotEqual(rr['F204-S']['entity_id'],rr['F204-Q']['entity_id'])
        # A one-body dark stripe can produce a very strong valley: diagnostic,
        # explicitly not a classifier or reason to override maker identity.
        rgb=np.ones((30,50,3))*.9;rgb[:,22:28,:]=.2
        p=pair_profiles(rgb,[10,15],[40,15])
        self.assertTrue(all(q['relative_dip']>.7 for q in p['profiles']))
        self.assertNotIn('decision',p)

    def test_native_rgb_before_value_interpolation(self):
        rgb=np.zeros((4,4,3));rgb[:,:,0]=np.arange(4)[None,:]/3
        p=pair_profiles(rgb,[1,1],[2,1]);center=p['profiles'][2]
        np.testing.assert_allclose(center['value'],(1+np.array(p['t']))/3,atol=1e-12)
        reverse=pair_profiles(rgb,[2,1],[1,1]);np.testing.assert_allclose(center['value'],reverse['profiles'][2]['value'][::-1])

    def test_region_point_is_positive_not_arbitrary_centroid(self):
        runs=[[0,0,1],[0,8,9]];self.assertIn(region_point(runs),[[0.,0.],[1.,0.],[8.,0.],[9.,0.]])

    def test_accounting_and_no_automatic_trust_promotion(self):
        accepted=[e for e in self.entities if e['status']=='trusted']
        self.assertEqual(len({e['observation_id'] for e in accepted}),len(accepted))
        self.assertTrue(all(e['evidence_level']!='automatic_candidate' for e in accepted))
        for e in accepted:
            self.assertIsNone(e['bead_index']);self.assertIsNone(e['physical_center_xyz'])
            self.assertTrue(e['source_keys'])
        self.assertEqual(self.rows['A75']['disposition'],'ambiguous')
        self.assertEqual(self.rows['A267']['original_evidence_level'],'automatic_candidate')
        self.assertEqual(self.rows['F168-1']['color'],'black')
        self.assertTrue(all(self.rows[f'F189-{i}']['color']=='yellow' for i in range(3)))

    def test_inventory_coverage_and_representatives(self):
        d=json.loads((OUT/'inventory.json').read_text());a=[e for e in d['observations'] if e['status']=='trusted']
        self.assertEqual(len(a),sum(c['trusted_red']+c['trusted_yellow'] for c in d['coverage']))
        self.assertTrue(all(c['trusted_red']>0 and c['trusted_yellow']>0 for c in d['coverage']))
        self.assertEqual(len(a),len(set(e['representative_source'] for e in a)))
        for e in a:
            self.assertEqual(e['xy'],self.rows[e['representative_source']]['original_xy'])
        self.assertEqual(d['helicities_to_test'],[1,-1]);self.assertFalse(d['fitting_performed'])


if __name__=='__main__':unittest.main()

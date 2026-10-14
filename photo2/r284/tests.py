"""Mechanism and scientific invariants, with independent adversarial masks."""
import unittest
import numpy as np
from scipy import ndimage as ndi
from photo2.r282.common import pixels,support,read
from photo2.r282.phase1 import image_features
from .methods import prune,radial,route,cues,infer,cut_features
from .run import OUT


class Mechanisms(unittest.TestCase):
    def test_pruning_cannot_invent_material(self):
        yy,xx=np.indices((49,49));m=(xx-24)**2+(yy-24)**2<=100;m[23:26,30:46]=True
        p=prune(m,[24,24]);self.assertFalse((p&~m).any());self.assertFalse(p[:,42:].any());self.assertGreater(p.sum(),200)

    def test_pruning_does_not_jump_to_disconnected_neighbor(self):
        m=np.zeros((49,49),bool);m[20:29,20:29]=True;m[10:19,34:43]=True
        p=prune(m,[24,24]);self.assertEqual(ndi.label(p)[1],1);self.assertFalse(p[:,34:].any())

    def test_straight_route_retains_endpoint_order(self):
        p=route([31,8],[10,29]);np.testing.assert_array_equal(p[0],[31,8]);np.testing.assert_array_equal(p[-1],[10,29])
        self.assertTrue(np.all(np.diff(p[:,0])<=0));self.assertEqual(len(p),len(set(map(tuple,p))))

    def test_rays_cannot_cross_material_barrier(self):
        m=np.ones((49,49),bool);m[:,30]=False;lum=np.ones((49,49))*.2
        p=radial(m,lum,.2);self.assertFalse(p[:,30:].any());self.assertTrue(p[24,24])

    def test_rays_cannot_reenter_neighbor_after_dark_trough(self):
        yy,xx=np.indices((49,49));m=np.hypot(xx-24,yy-24)<18
        lum=.5-.01*np.hypot(xx-24,yy-24);lum[:,29:32]=.08;lum[:,32:]=.4
        p=radial(m,lum,.5);self.assertFalse(p[:,32:].any())

    def test_native_support_roundtrip(self):
        p=np.array([[3,5],[4,5],[9,8],[9,9]]);np.testing.assert_array_equal(pixels(support(p)),p)

    def test_competition_order_invariance_and_single_owner(self):
        im=np.full((100,110,3),[170,90,155],np.uint8);yy,xx=np.indices(im.shape[:2])
        for x in (45,65):
            m=((xx-x)/14)**2+((yy-50)/18)**2<1;im[m]=[200,80,20]
            q=(xx-x)**2+(yy-50)**2<16;im[q]=[255,190,65]
        f=image_features(im)
        bank=[dict(id='left',xy=[45,50],color='yellow',sources=['synthetic']),dict(id='right',xy=[65,50],color='yellow',sources=['synthetic'])]
        a,_=infer(f,bank,'B');b,_=infer(f,list(reversed(bank)),'B')
        aa={r['record_id']:set(map(tuple,pixels(r['measured_support']))) for r in a};bb={r['record_id']:set(map(tuple,pixels(r['measured_support']))) for r in b}
        self.assertEqual(aa,bb);self.assertFalse(aa['left']&aa['right']);self.assertTrue(aa['left']);self.assertTrue(aa['right'])


class SavedEvidence(unittest.TestCase):
    def test_cases_and_required_roles(self):
        cases=read(OUT/'cases.json');self.assertEqual(len(cases),8)
        self.assertEqual([c['name'] for c in cases[:3]],['two-sided','duplicate','abstention'])
        for i,c in enumerate(cases):
            for d in cases[i+1:]:self.assertGreater(np.linalg.norm(np.array(c['center'])-d['center']),128)

    def test_all_masks_native_connected_and_centroids_exact(self):
        for c in read(OUT/'cases.json'):
            result=read(OUT/(c['name']+'.json.gz'))
            for m in 'ABC':
                for r in result['methods'][m]['records']:
                    p=pixels(r['measured_support'])
                    if len(p):
                        np.testing.assert_allclose(p.mean(0),r['measured_photo_location'],atol=1e-12)
                        self.assertEqual(r['metrics']['components'],1)
                    if r['status']=='high':self.assertTrue(30<=len(p)<=870)
                    if r['secondary_of']:self.assertNotEqual(r['status'],'high')

    def test_competitive_masks_never_share_a_native_pixel(self):
        for c in read(OUT/'cases.json'):
            rows=read(OUT/(c['name']+'.json.gz'))['methods']['B']['records'];seen=set()
            for r in rows:
                p=set(map(tuple,pixels(r['measured_support'])));self.assertFalse(seen&p);seen|=p

    def test_all_cues_have_auditable_disposition(self):
        for c in read(OUT/'cases.json'):
            cues=read(OUT/(c['name']+'-cues.json'));ids={r['id'] for r in cues['bank']}
            self.assertTrue(all(r['representative'] in ids and r['reason'] for r in cues['ledger']))

    def test_no_certified_real_recall_or_physical_ids(self):
        for c in read(OUT/'cases.json'):
            result=read(OUT/(c['name']+'.json.gz'))
            for m in 'ABC':
                self.assertIsNone(result['methods'][m]['summary']['real_distinct_body_count'])
                self.assertIsNone(result['methods'][m]['summary']['real_recall'])
                for r in result['methods'][m]['records']:self.assertNotIn('physical_model_index',r)

if __name__=='__main__':unittest.main()

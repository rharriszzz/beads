"""Scientific contracts independent of rendering presentation."""
import csv,json,unittest
import numpy as np
from PIL import Image
from .model import *

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models={n:read(BASE/f'results/{n}.json.gz') for n in FAMILIES};cls.corr={n:read(BASE/f'results/{n}-correspondences.json') for n in FAMILIES}
    def test_complete_continuous_interval(self):
        for n,m in self.models.items():
            core=[b for b in m['positions'] if b['displayed']];self.assertEqual([b['index'] for b in core],list(range(-40,1001)));self.assertEqual(len(m['positions']),1169)
            np.testing.assert_allclose(np.diff([b['phase'] for b in core]),m['source']['hand']*2*np.pi/m['parameters']['turn'],atol=1e-10)
            self.assertTrue(np.all(np.diff([b['photo_arc'] for b in core])>0))
    def test_pairing_and_original_coordinates(self):
        obs={r['id']:r for r in read(BASE/'evidence/observations.json')['observations']}
        for n,c in self.corr.items():
            assigned=[r['index'] for r in c['records'] if r['index'] is not None];self.assertEqual(len(assigned),len(set(assigned)))
            for r in c['records']:
                self.assertEqual(r['observed'],obs[r['observation']]['point'])
                if r['index'] is None:self.assertIsNone(r['error_px']);self.assertIsNone(r['predicted'])
                else:self.assertAlmostEqual(r['error_px'],np.linalg.norm(np.array(r['predicted'])-r['observed']),places=12)
            for penalty,path in c['paths'].items():
                for lo,hi in [(-40,-13),(13,1000)]:
                    indices=[r['index'] for r in path if r['operation']=='pair' and lo<=r['index']<=hi];self.assertEqual(indices,sorted(indices))
        old=read(ROOT/'photo2/r304/results/primary-correspondences.json')['records'];new={r['observation']:r for r in self.corr['primary']['records']}
        for r in old:self.assertEqual(r['index'],new[r['observation']]['index'])
    def test_group_counts_and_exports(self):
        for n,c in self.corr.items():
            gs=c['groups'];self.assertEqual(sum(g['modeled'] for g in gs),1041);self.assertEqual(sum(g['n'] for g in gs),c['summary_strong']['n'])
            self.assertEqual(sum(g['ambiguous'] for g in gs),sum(r['status']=='ambiguous' for r in c['records']))
            self.assertEqual(sum(g['unmatched_observations'] for g in gs)+len(c['unmatched_outside_model_geography']),sum(r['index'] is None for r in c['records']))
            rows=list(csv.DictReader((BASE/f'results/{n}-errors.csv').read_text().splitlines()));self.assertEqual(len(rows),len(c['records']))
            for r in rows:
                if not r['index']:self.assertEqual(r['error_px'],'')
    def test_every_boundary_segment_separates_owners(self):
        for n,m in self.models.items():
            a=np.load(BASE/f'results/{n}-raster.npz')['address'];x0,y0=m['bounds'][:2]
            for b in m['positions']:
                for x1,y1,x2,y2 in b['boundary_segments']:
                    x=(x1+x2)/2-x0;y=(y1+y2)/2-y0
                    if y1==y2:p=(int(np.floor(y)),int(np.floor(x+.5)));q=(p[0]+1,p[1])
                    else:p=(int(np.floor(y+.5)),int(np.floor(x)));q=(p[0],p[1]+1)
                    values=[a[v] if 0<=v[0]<a.shape[0] and 0<=v[1]<a.shape[1] else -32768 for v in [p,q]]
                    self.assertNotEqual(values[0]==b['index'],values[1]==b['index'])
    def test_native_gallery_pixels(self):
        raw=Image.open(REVIEW/'photo.png');gallery=read(BASE/'results/gallery.json');self.assertTrue(12<=len(gallery)<=20)
        for g in gallery:
            crop=np.asarray(raw.crop(g['box']));np.testing.assert_array_equal(crop,np.asarray(Image.open(REVIEW/g['raw'])))
            annotated=Image.open(REVIEW/g['image']);expected=Image.fromarray(crop).resize((crop.shape[1]*g['scale'],crop.shape[0]*g['scale']),Image.Resampling.NEAREST)
            np.testing.assert_array_equal(np.asarray(expected),np.asarray(annotated.crop((8,72,8+expected.width,72+expected.height))))
    def test_material_partition_and_contact_scope(self):
        for r in read(BASE/'results/starting-red-diagnosis.json'):
            self.assertAlmostEqual(r['assigned_fraction']+r['other_fraction']+r['outside_fraction'],1)
            self.assertLessEqual(r['occluded_assigned_fraction'],r['other_fraction'])
        for n,m in self.models.items():
            p=m['physical'];self.assertEqual(p['pairs'],len(p['witnesses']));self.assertEqual(p['unresolved_pairs'],len(p['penetration_checks']))
            self.assertEqual(p['demonstrated_penetrating_pairs'],sum(q['demonstrated_penetration'] for q in p['penetration_checks']))
        self.assertTrue(self.models['hand-minus']['physical']['certified']);self.assertFalse(self.models['primary']['physical']['certified'])
    def test_output_isolation_and_guard_invariance(self):
        self.assertEqual(REVIEW,ROOT/'photo2/review/r305');self.assertEqual(BASE,ROOT/'photo2/r305')
        for n in FAMILIES:
            v=read(BASE/f'results/{n}-numerical.json');self.assertEqual(v['guard']['core_owner_changes'],0);self.assertEqual(v['guard']['core_maximum_intensity_change'],0);self.assertEqual(v['old_interval']['centers_projected_max_change_px'],0)

if __name__=='__main__':unittest.main()
